"""Study 4 design pilot (validation on inputs; VALIDATION KEYS ONLY, >= 1,000,000; pilot prompts only; no committed threshold is read).
Generates watermarked and unwatermarked continuations from the pinned model under a few settings, scores them with the LOCKED detector
code (s2_core.build_chain on the generated tokens alone; s1_core uniforms; s3_core p-values) at several lengths, and summarises the
nominal power at alpha, the z distribution, and quality diagnostics (the model's log-probability of its own tokens against the human
continuation's, rep-4, EOS mass). Its purpose is to choose the watermark strength and the sizes before the protocol; nothing here is an outcome.
Outputs: outputs/study4_v0.1/pilot/gen/*.npz (token arrays; git-ignored) and outputs/study4_v0.1/pilot/pilot_summary_<utc>.json (tracked)."""
import datetime, json, pathlib, resource, sys, time
import numpy as np
from scipy.stats import norm, gamma as gamma_dist
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
for p in ("research/study1", "research/study2", "research/study3", "tools"):
    sys.path.insert(0, str(ROOT / p))
sys.path.insert(0, str(HERE))
import s1_core as C, s2_core as S, s3_core as T
import s4_gen as G, s4_data as SD
from key_policy import check_keys

KEYS = [1_000_311, 1_000_312]
GAMMA = 0.25; ALPHAS = (0.01, 0.001); LENGTHS = (32, 64, 128, 256); RULES = ("raw", "distinct")


def score_texts(X, V, h, family, key):
    """Per-text p-values and z at every length for both rules under the LOCKED chain code (the generated text alone)."""
    chain = S.build_chain(np.ascontiguousarray(X, dtype=np.int32), V, "pilot", h); g = C.green_fraction(GAMMA, V)
    U = S.uniforms_chunk([key], chain.D)[:, 0]; col = (U < g).astype(np.float64); sg = S.gumbel_scores(U)
    out = {}
    for r in RULES:
        for L in LENGTHS:
            inc = chain.incidence(L, r); M = np.asarray(inc.sum(axis=1)).ravel()
            ok = M > 0
            if family == "kgw":
                Gc = np.asarray(inc @ col).ravel(); z = np.full(len(M), np.nan); z[ok] = (Gc[ok] - GAMMA * M[ok]) / np.sqrt(M[ok] * GAMMA * (1 - GAMMA)); p = norm.sf(z)
            else:
                Sg = np.asarray(inc @ sg).ravel(); p = np.full(len(M), np.nan); p[ok] = gamma_dist.sf(Sg[ok], M[ok]); z = norm.isf(np.clip(p, 1e-300, 1.0))
            out[(r, L)] = {"z": z, "p": p, "M": M}
    return out


def summarise(sc):
    res = {}
    for (r, L), d in sc.items():
        z = d["z"][np.isfinite(d["z"])]; p = d["p"]
        res[f"{r}@{L}"] = {"n": int(len(p)), "M_mean": float(d["M"].mean()), "z_mean": float(z.mean()), "z_sd": float(z.std(ddof=1)) if len(z) > 1 else None,
                           "z_q10": float(np.quantile(z, 0.1)), "z_q50": float(np.quantile(z, 0.5)), "z_q90": float(np.quantile(z, 0.9)),
                           **{f"power@{a}": float(np.mean(p < a)) for a in ALPHAS}}
    return res


def main(B=16, n_prompts=64, n_new=256, model_name="qwen"):
    check_keys(KEYS, "validation")
    man = json.loads((ROOT / "outputs/study4_v0.1/pilot/prompts_manifest.json").read_text()); P = man["P"]; Lh = man["L"]
    gdir = ROOT / "outputs/study4_v0.1/pilot/gen"; gdir.mkdir(parents=True, exist_ok=True)
    model, tok, info = G.load_model(model_name); info = G.prepare_info(model, tok, info); V = info["V"]
    configs = [("news_en_256", "none", 0, 0.0, None)]
    for d in (0.5, 1.0, 1.5, 2.0, 3.0):
        for k in KEYS:
            configs.append(("news_en_256", "kgw", 1, d, k))
    for d in (1.0, 2.0):
        for k in KEYS:
            configs.append(("news_en_256", "kgw", 2, d, k))
    for k in KEYS:
        configs.append(("news_en_256", "kgw", 0, 2.0, k))
    for h in (0, 1, 2):
        for k in KEYS:
            configs.append(("news_en_256", "gumbel", h, 0.0, k))
    configs += [("wikipedia_zh_256", "none", 0, 0.0, None), ("wikipedia_zh_256", "kgw", 1, 2.0, KEYS[0]), ("wikipedia_zh_256", "gumbel", 2, 0.0, KEYS[0])]
    rec = {"utc": f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}", "model": {k: v for k, v in info.items() if not k.startswith("_")}, "B": B, "n_prompts": n_prompts, "n_new": n_new, "P": P,
           "keys": KEYS, "gamma": GAMMA, "alphas": ALPHAS, "lengths": LENGTHS, "configs": [], "human_reference": {}}
    human_lp = {}
    for cell in sorted(set(c[0] for c in configs)):
        X = SD.load_prompts(man, cell, "pilot")[:n_prompts]
        lp = G.score_logp_of_text(model, info, X, sub=4)   # n x (P+Lh-1), scored in sub-batches of 4
        hl = lp[:, P - 1:]                                                                                        # the human continuation's tokens
        human_lp[cell] = hl; rec["human_reference"][cell] = {"n": int(len(X)), "L_human": int(hl.shape[1]), "mean_logp": float(hl.mean()), "ppl": float(np.exp(-hl.mean())), "rep4_mean": float(G.rep_n(X[:, P:]).mean())}
        print("human", cell, rec["human_reference"][cell], flush=True)
    t_all = time.time()
    for (cell, mode, h, delta, key) in configs:
        X = SD.load_prompts(man, cell, "pilot")[:n_prompts]; n = len(X); cache = G.W.HookCache(V)
        toks = np.zeros((n, n_new), dtype=np.int32); logp = np.zeros((n, n_new), dtype=np.float32); flag = np.zeros((n, n_new), dtype=np.float32); eosm = np.zeros((n, n_new), dtype=np.float32); sec = 0.0
        for i in range(0, n, B):
            r = G.generate_batch(model, info, X[i:i + B, :P], n_new, mode, key=key, h=h, delta=delta, seed=1000 * (key or 0) + 7 * h + int(delta * 10) + i, cache=cache)
            toks[i:i + B] = r["tokens"]; logp[i:i + B] = r["logp"]; flag[i:i + B] = r["flag"]; eosm[i:i + B] = r["eos_mass"]; sec += r["seconds"]
        name = f"{cell}__{mode}_h{h}_d{delta}_k{key}"
        np.savez_compressed(gdir / f"{name}.npz", tokens=toks, logp=logp, flag=flag, eos_mass=eosm)
        entry = {"cell": cell, "mode": mode, "h": h, "delta": delta, "key": key, "n": n, "seconds": round(sec, 1), "tok_per_s": round(n * n_new / sec, 1), "mean_logp": float(logp.mean()), "ppl": float(np.exp(-logp.mean())),
                 "mean_logp_first_human_L": float(logp[:, :Lh - 0].mean()), "rep4_mean": float(G.rep_n(toks).mean()), "rep4_share_gt_0.5": float((G.rep_n(toks) > 0.5).mean()), "eos_mass_mean": float(eosm.mean()),
                 "green_share_hook": float(flag.mean()) if mode == "kgw" else None, "sample": tok.decode(toks[0][:80]), "scores": {}}
        fams = ("kgw", "gumbel") if mode == "none" else (mode,)
        keys_score = KEYS if mode == "none" else [key]
        for fam in fams:
            for k in keys_score:
                hh = h if mode != "none" else 1
                entry["scores"][f"{fam}|h{hh}|k{k}"] = summarise(score_texts(toks, V, hh, fam, k))
        rec["configs"].append(entry)
        s = entry["scores"][next(iter(entry["scores"]))]
        print(json.dumps({k: entry[k] for k in ("cell", "mode", "h", "delta", "key", "tok_per_s", "ppl", "rep4_mean", "green_share_hook")}), {kk: round(s[kk]["power@0.01"], 3) for kk in ("raw@64", "distinct@64", "raw@256", "distinct@256")}, flush=True)
    rec["seconds_total"] = round(time.time() - t_all, 1); rec["rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9, 2)
    out = ROOT / f"outputs/study4_v0.1/pilot/pilot_summary_{rec['utc'].replace(':', '').replace('-', '')}.json"; out.write_text(json.dumps(rec, indent=1, ensure_ascii=False)); print("wrote", out)


if __name__ == "__main__":
    a = sys.argv[1:]
    B = int(a[a.index("--B") + 1]) if "--B" in a else 16
    main(B=B)
