"""Study 4 pre-lock inputs (v1; before the lock; VALIDATION KEYS and pilot prompts only; no evaluation key is generated with):
(a) the pilot law of every arm: the watermarked z of the locked detector on continuations generated under validation keys from the pilot
    prompts of the grid's first cell (n_keys x n_prompts texts per arm), at both rules and every length; W1's threshold-shift predictor
    reads the arm's pooled law at (rule, L) from here (s4_core.PooledLaw);
(b) the human reference: the model's log-probability of the human continuations (192 tokens after the 64-token prompt) of the first
    n_ref production prompts of every cell, the quality reference the report compares the generations' log-probabilities with;
(c) the digests of every input the analyzer binds to (the prompts manifest, the pilot prompts manifest, the model manifest, the grid).
Writes outputs/study4_v0.1/INPUTS.json (pinned by the lock) and the pilot-law token arrays beside it (git-ignored; digests recorded).
Usage: .venv/bin/python -u research/study4/s4_inputs.py --grid research/study4/grid_v0.1.json
"""
import datetime, hashlib, json, pathlib, resource, sys, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import s4_core as T4, s4_gen as G, s4_data as SD, s4_keys as K4, s4_wm as W

OUT = ROOT / "outputs/study4_v0.1"
N_REF = 1000


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def utc():
    return f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}"


def pilot_law_arm(model, info, grid, arm, keys, Xp, cell, V, pl, pdir):
    """One arm's pilot law on one cell's pilot prompts: generation under the validation keys, the locked detector's p-values per text under
    the text's own key at both rules and every length, the hook flags checked against the detector, the arrays saved with their digest."""
    import hashlib, time
    from scipy.stats import norm
    t0 = time.time(); toks = []; flags = []; lp = []; B = grid["generation"]["batch_watermarked"]; n_new = grid["generation"]["n_new"]; g = W.C.green_fraction(grid["gamma"], V)
    for k in keys:
        cache = W.HookCache(V, max_entries=512, g=g)
        for i in range(0, len(Xp), B):
            seed = int(hashlib.sha256(f"pilot_law|{arm['name']}|{cell}|{k}|{i}".encode()).hexdigest()[:8], 16) ^ pl["salt"]
            r = G.generate_batch(model, info, Xp[i:i + B], n_new, "kgw", key=k, h=arm["h"], delta=arm["delta"], gamma=grid["gamma"], seed=seed, cache=cache)
            toks.append(r["tokens"]); flags.append(r["flag"]); lp.append(r["logp"])
    X = np.concatenate(toks).astype(np.int32); F = np.concatenate(flags).astype(np.uint8); LP = np.concatenate(lp).astype(np.float32); key_of_text = np.repeat(keys, len(Xp))
    pv = {}; flag_ok = True
    for ki, k in enumerate(keys):
        rows = slice(ki * len(Xp), (ki + 1) * len(Xp))
        Pk, M, _, chain = T4.score_set(X[rows], V, arm["h"], [k], grid["gamma"], grid["rules"], grid["lengths"], families=("kgw",))
        det, valid = T4.detector_green_flags(chain, k, grid["gamma"], V)
        if not np.array_equal(det[valid], F[rows][valid].astype(bool)):
            flag_ok = False
        for (f, r, L), pp in Pk.items():
            pv.setdefault(f"{r}@{L}", []).append(pp[:, 0])
    pv = {k: np.concatenate(v) for k, v in pv.items()}; z = {k: np.clip(norm.isf(np.clip(v, 1e-300, 1.0)), -50, 50) for k, v in pv.items()}
    f = pdir / f"{arm['name']}__{cell}.npz"; np.savez_compressed(f, tokens=X, flag=F, logp=LP, key=key_of_text, **{f"p_{k.replace('@', '_')}": v for k, v in pv.items()})
    rep = G.rep_n(X)
    return {"arm": arm, "cell": cell, "n_texts": int(X.shape[0]), "file": str(f.relative_to(ROOT)), "sha256": sha(f), "hook_flags_equal_detector": bool(flag_ok), "green_share": float(F.mean()), "mean_logp": float(LP.mean()), "ppl": float(np.exp(-LP.mean())),
            "rep4_mean": float(rep.mean()), "loop_share": float((rep > grid["integrity"]["loop_bar_rep4"]).mean()), "seconds": round(time.time() - t0, 1),
            "z": {k: {"n": int(len(v)), "mean": float(v.mean()), "sd": float(v.std(ddof=1)), "q05": float(np.quantile(v, 0.05)), "q50": float(np.quantile(v, 0.5)), "q95": float(np.quantile(v, 0.95)),
                      "power_nominal_0.01": float(np.mean(pv[k] < 0.01)), "per_key_mean": [float(v[key_of_text == k_]. mean()) for k_ in keys]} for k, v in z.items()},
            "p_values": {k: [float(x) for x in np.sort(v)] for k, v in pv.items()}, "key_of_text_order": "keys in order, each block of n_prompts texts in prompt order (the npz 'key' array)"}


def cluster_bootstrap_se(p_sorted_by_key, keys, n_prompts, t_keys, alpha, B=2000, seed=927):
    """The SE of the predicted key-median cost over the pilot's own sampling: the pilot's texts are n_keys clusters (keys) crossed with
    n_prompts shared prompts; resample the key clusters and the prompt columns independently (a two-way cluster bootstrap), recompute the
    pooled law and the predicted key-median cost for the fixed thresholds t_keys. A sensitivity diagnostic, not a coverage guarantee."""
    rng = np.random.default_rng(seed); nk = len(keys); P = np.asarray(p_sorted_by_key).reshape(nk, n_prompts); meds = []
    for _ in range(B):
        ki = rng.integers(0, nk, size=nk); pi_ = rng.integers(0, n_prompts, size=n_prompts); sub = P[ki][:, pi_].ravel()
        law = T4.PooledLaw(sub); meds.append(float(np.median(law.predicted_cost(t_keys, alpha))))
    meds = np.array(meds)
    return {"se_pp": float(100 * meds.std(ddof=1)), "q025_pp": float(100 * np.quantile(meds, 0.025)), "q975_pp": float(100 * np.quantile(meds, 0.975)), "B": B, "seed": seed}


def main(grid_path):
    import s4_record as RC
    grid = json.loads(pathlib.Path(grid_path).read_text()); pl = grid["W1"]["pilot_law"]
    keys = list(range(pl["keys_start"], pl["keys_start"] + pl["n_keys"])); K4.check_keys(keys, "validation")
    pil_man = json.loads((ROOT / grid["prompts"]["pilot_manifest"]).read_text()); pm = json.loads((ROOT / grid["prompts"]["manifest"]).read_text())
    P = grid["prompts"]["P"]; V = grid["model"]["V"]; law_cells = grid["cells"] if pl.get("cells", "first") == "each" else [grid["cells"][0]]
    model, tok, info = G.load_model(grid["model"]["name"], device=grid["model"]["device"], dtype=grid["model"]["dtype"]); info = G.prepare_info(model, tok, info)
    if info["V"] != V:
        raise RuntimeError("model vocabulary differs from the grid")
    res = {"study": grid["study"], "written_utc": utc(), "grid_sha256": sha(grid_path), "prompts_manifest_sha256": sha(ROOT / grid["prompts"]["manifest"]), "pilot_manifest_sha256": sha(ROOT / grid["prompts"]["pilot_manifest"]),
           "model_manifest_sha256": sha(ROOT / grid["model"]["weights_manifest"]), "s4_core_sha256": sha(HERE / "s4_core.py"), "s4_gen_sha256": sha(HERE / "s4_gen.py"), "s4_wm_sha256": sha(HERE / "s4_wm.py"),
           "note": "pre-lock inputs on validation keys and pilot prompts only: the pilot law of each arm (per prompt cell) for W1's threshold-shift predictor as sorted p-values; W1's tolerance per cell from the cluster-bootstrap SE; the human reference under the admissible law; no evaluation key generated with",
           "pilot_law": {"cells": law_cells, "keys": keys, "n_prompts": int(pl["n_prompts"]), "n_new": grid["generation"]["n_new"], "arms": {}}, "W1_tolerance": {}, "human_reference": {}}
    pdir = OUT / "pilot_law"; pdir.mkdir(exist_ok=True); t_all = time.time()
    for arm in grid["arms"]:
        res["pilot_law"]["arms"][arm["name"]] = {"arm": arm, "by_cell": {}}
        for cell in law_cells:
            Xp = SD.load_prompts(pil_man, cell, "pilot")[:pl["n_prompts"], :P]
            rec = pilot_law_arm(model, info, grid, arm, keys, Xp, cell, V, pl, pdir); res["pilot_law"]["arms"][arm["name"]]["by_cell"][cell] = rec
            print(f"{utc()} pilot law {arm['name']} on {cell}: {rec['n_texts']} texts in {rec['seconds']}s; flags ok {rec['hook_flags_equal_detector']}; power@0.01 raw@256 {rec['z']['raw@256']['power_nominal_0.01']:.3f}", flush=True)
        a0 = res["pilot_law"]["arms"][arm["name"]]["by_cell"][law_cells[0]]
        res["pilot_law"]["arms"][arm["name"]].update({k: a0[k] for k in ("n_texts", "hook_flags_equal_detector", "green_share", "ppl", "loop_share", "z", "p_values")})   # the first cell's law also at the arm level (older readers)
    # W1's tolerance per cell: max(tolerance_pp, 2 x the cluster-bootstrap SE of the predicted key-median), from the primary arm's law on that cell and the power keys' committed diagonal thresholds (the record's committed thresholds are inputs, not outcomes)
    w = grid["W1"]; Rrec = RC.Record(verify_files=False); idx = np.array(grid["keys"]["power_keys"]) - 23000; h1 = next(a["h"] for a in grid["arms"] if a["name"] == w["arm"])
    for cell in grid["cells"]:
        law_cell = cell if cell in law_cells else law_cells[0]; rec = res["pilot_law"]["arms"][w["arm"]]["by_cell"][law_cell]
        d = np.load(ROOT / rec["file"]); p_by_key = d[f"p_{w['rule']}_{w['length']}"]   # in key order, each block in prompt order
        t_keys = Rrec.cal(grid["model"]["tokenizer"], cell, h1).threshold("kgw", w["rule"], w["method"], float(w["alpha"]), w["N_cal"])[idx]
        cb = cluster_bootstrap_se(p_by_key, keys, pl["n_prompts"], t_keys, float(w["alpha"]))
        law = T4.PooledLaw(p_by_key); pred = law.predicted_cost(t_keys, float(w["alpha"]))
        res["W1_tolerance"][cell] = {"pilot_law_cell": law_cell, "predicted_median_pp": float(100 * np.median(pred)), "predicted_mean_pp": float(100 * pred.mean()), "cluster_bootstrap": cb, "tolerance_pp": float(max(w["tolerance_pp"], 2 * cb["se_pp"])),
                                    "rule": "max(grid tolerance_pp, 2 x the key-and-prompt cluster-bootstrap SE of the predicted key-median)", "n_abstaining_keys": int((t_keys <= 0).sum())}
        print(f"{utc()} W1 tolerance {cell}: predicted median {res['W1_tolerance'][cell]['predicted_median_pp']:.2f} pp; cluster SE {cb['se_pp']:.2f} pp; tolerance {res['W1_tolerance'][cell]['tolerance_pp']:.2f} pp", flush=True)
    # the human reference under the admissible law (the same normalisation as the generations' logp), on the current production cache
    for tag in grid["cells"]:
        t0 = time.time(); Xh = SD.load_prompts(pm, tag, "prod")[:N_REF]
        lp = G.score_logp_of_text(model, info, Xh, sub=4)[:, P - 1:]           # the 192 human continuation tokens
        fin = np.isfinite(lp); res["human_reference"][tag] = {"n": int(Xh.shape[0]), "L_human": int(lp.shape[1]), "mean_logp": float(lp[fin].mean()), "ppl": float(np.exp(-lp[fin].mean())), "n_tokens_excluded_ids": int((~fin).sum()),
                                                              "per_text_mean_logp_q": [float(q) for q in np.quantile(np.where(fin, lp, np.nan).mean(axis=1) if fin.all() else np.nanmean(np.where(fin, lp, np.nan), axis=1), [0.05, 0.5, 0.95])],
                                                              "rep4_mean": float(G.rep_n(Xh[:, P:]).mean()), "normalisation": "admissible law (special and padding ids excluded), as the generations' logp", "seconds": round(time.time() - t0, 1)}
        print(f"{utc()} human reference {tag}: ppl {res['human_reference'][tag]['ppl']:.2f} ({res['human_reference'][tag]['n_tokens_excluded_ids']} tokens were excluded ids)", flush=True)
    res["seconds"] = round(time.time() - t_all, 1); res["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30, 2)
    (OUT / "INPUTS.json").write_text(json.dumps(res, indent=0)); print("DONE", res["seconds"], "s; peak RSS", res["peak_rss_gb"], flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]; main(a[a.index("--grid") + 1] if "--grid" in a else "research/study4/grid_v0.1.json")
