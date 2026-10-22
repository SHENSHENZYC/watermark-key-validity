"""Study 3 key-free inputs (v1; before the lock; touches no key). For every tokenizer, width h and retention rule at L = 256:
(a) the set moments of every evaluation set E (Study 2's texts) and of every calibration prefix C_n (n in the grid's N_cal) of every cell:
    the document-averaged z-weights' collision A = <w, w>, rho_bar (Study 1's unbiased average pairwise across-key covariance of two
    texts' z), mean V_i, sigma^2 = mean V_i - rho_bar, mean M, the number of tuples;
(b) the cross-set shift covariances rho_CE = <w_C, w_E> (the mean over cross pairs of Cov_K(z_i, z_j); exact for independent colours
    or unit-variance scores, the hash being a function of the integer tuple ids alone) for every calibration prefix of every cell under
    each tokenizer against every evaluation set under the same tokenizer and, secondarily, under the other tokenizer;
(c) the calibrated-threshold predictor (s3_core.predict_per_key) for the per-key conformal and tolerance thresholds at every N_cal and
    alpha, and the fixed-threshold predictions (nominal, the 1/beta multiplier20, and the model-implied empirical-multiplier and pooled
    thresholds) for every (calibration cell, evaluation cell) pair; the predictions are family-independent (both families share the
    model's inputs; the predictor treats p as Phi_bar of the standardised statistic);
(d) a consistency check of (a) on the evaluation sets against Study 2's pinned INPUTS.json (rho_bar and sigma^2 at L = 256 for the KGW
    family at gamma = 0.25; Gutenberg excluded because its evaluation set is the first 7,122 of Study 2's 10,000 texts).
No key, no per-key level. Writes outputs/study3_v0.1/INPUTS.json (pinned by the lock).
Usage: .venv/bin/python -u research/study3/s3_inputs.py --grid research/study3/grid_v0.1.json
"""
import datetime, hashlib, json, pathlib, resource, sys, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study2")); sys.path.insert(0, str(ROOT / "research/study1"))
import s3_core as T
import s3_data as SD
import s2_core as S

OUT = ROOT / "outputs/study3_v0.1"


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def utc():
    return f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}"


def r8(x):
    return float(f"{x:.9g}") if isinstance(x, float) and np.isfinite(x) else x


def clean(d):
    if isinstance(d, dict):
        return {k: clean(v) for k, v in d.items()}
    if isinstance(d, (list, tuple)):
        return [clean(v) for v in d]
    if isinstance(d, (np.floating,)):
        return r8(float(d))
    if isinstance(d, float):
        return r8(d)
    if isinstance(d, (np.integer,)):
        return int(d)
    return d


def set_weights_for(X, V, h, rule, n_list=None):
    """Weights of a text set (all rows) or of each prefix in n_list."""
    chain = S.build_chain(X, V, "set", h)
    if n_list is None:
        return {"all": T.set_weights(chain, X.shape[1], rule)}
    return {n: T.set_weights(chain, X.shape[1], rule, rows=np.arange(n)) for n in n_list}


def predictions(mC, mE, rho_CE, N_E, grid):
    """Every variant's prediction for one (calibration prefix C_n, evaluation set E) pair."""
    out = {}
    for a in grid["alpha"]:
        A = str(a); out[A] = {}
        n = mC["n"]
        out[A]["conformal"] = T.predict_per_key(mC["rho"], mE["rho"], rho_CE, mC["sigma2"], mE["sigma2"], n, T.j_conformal(n, a), N_E, a)
        out[A]["tolerance"] = T.predict_per_key(mC["rho"], mE["rho"], rho_CE, mC["sigma2"], mE["sigma2"], n, T.j_tolerance(n, a, grid["delta"]), N_E, a)
    return out


def fixed_predictions(mC_full, mE, N_E, grid):
    out = {}
    for a in grid["alpha"]:
        A = str(a); mt = T.model_thresholds(mC_full["rho"], mC_full["sigma2"], a, grid["beta"])
        out[A] = {"empirical": T.predict_fixed(mE["rho"], mE["sigma2"], mt["t_emp"], N_E, a) | {"kappa_model": mt["kappa_emp"]},
                  "pooled": T.predict_fixed(mE["rho"], mE["sigma2"], mt["t_pool"], N_E, a)}
    return out


def compute(grid, sp, get_E, get_C, s2_inputs=None, log=print):
    """The blocks for every (h, rule): get_E(tok, tag) and get_C(tok, tag) return the evaluation and calibration token arrays; sp is
    s3_run.spec_of(grid, validation) (cells, tokenizers, h, N_cal). Returns (blocks, study2_consistency)."""
    toks = list(sp["toks"]); Ncals = sp["N_cal"]; blocks = {}; cons = []
    for h in sp["h"]:
        for rule in grid["rules"]:
            t0 = time.time(); W = {}
            for tok in toks:
                V = int(sp["toks"][tok]["V"])
                for tag in sp["cells"]:
                    XE = get_E(tok, tag); XC = get_C(tok, tag)
                    W[(tok, tag, "E")] = set_weights_for(XE, V, h, rule)["all"]
                    for n, ws in set_weights_for(XC, V, h, rule, Ncals).items():
                        W[(tok, tag, "C", n)] = ws
                    del XE, XC
            mom = {k: T.set_moments(v) for k, v in W.items()}
            blk = {"h": h, "rule": rule, "sets": {}, "pairs": {}}
            for tok in toks:
                for tag in sp["cells"]:
                    blk["sets"][f"{tok}|{tag}|E"] = mom[(tok, tag, "E")]
                    for n in Ncals:
                        blk["sets"][f"{tok}|{tag}|C{n}"] = mom[(tok, tag, "C", n)]
            for tokE in toks:
                for tagE in sp["cells"]:
                    mE = mom[(tokE, tagE, "E")]; N_E = mE["n"]
                    for tokC in toks:
                        if tokC != tokE and not grid["cross_tokenizer"]:
                            continue
                        for tagC in sp["cells"]:
                            pr = {"cross": {}, "per_key": {}, "fixed": fixed_predictions(mom[(tokC, tagC, "C", max(Ncals))], mE, N_E, grid)}
                            for n in Ncals:
                                cc, nshared = T.cross_cov(W[(tokC, tagC, "C", n)], W[(tokE, tagE, "E")])
                                pr["cross"][str(n)] = {"rho_CE": cc, "n_shared_tuples": nshared}
                                pr["per_key"][str(n)] = predictions(mom[(tokC, tagC, "C", n)], mE, cc, N_E, grid)
                            blk["pairs"][f"{tokC}|{tagC}->{tokE}|{tagE}"] = pr
                    nom = {}
                    for al in grid["alpha"]:
                        nom[str(al)] = {"nominal": T.predict_fixed(mE["rho"], mE["sigma2"], al, N_E, al), "multiplier20": T.predict_fixed(mE["rho"], mE["sigma2"], al * grid["beta"], N_E, al)}
                    blk["sets"][f"{tokE}|{tagE}|E"]["pred_fixed"] = nom
                    if s2_inputs is not None and tagE != "gutenberg_en_1024":
                        ch = s2_inputs["chains"].get(f"{tagE}__{tokE}__h{h}__N10000")
                        rec = ch["cells"].get(f"L256__{rule}", {}).get("kgw", {}).get("0.25") if ch else None
                        if rec and "rho_bar" in rec:
                            cons.append({"set": f"{tokE}|{tagE}", "h": h, "rule": rule, "rho_s3": mE["rho"], "rho_s2": rec["rho_bar"], "sigma2_s3": mE["sigma2"], "sigma2_s2": rec["sigma_model2"],
                                         "abs_diff_rho": abs(mE["rho"] - rec["rho_bar"]), "abs_diff_sigma2": abs(mE["sigma2"] - rec["sigma_model2"])})
            blk["seconds"] = round(time.time() - t0, 1); blk["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30, 2)
            blocks[f"h{h}|{rule}"] = blk
            log(f"{utc()} h={h} rule={rule}: {len(blk['pairs'])} pairs in {blk['seconds']}s (peak RSS {blk['peak_rss_gb']} GB)")
            del W, mom
    return blocks, cons


def v_summary(blocks):
    """How many (pair, N_cal) conformal predictions at every alpha have a negative point estimate of v, how many lie below the algebraic floor
    (flagged), and the most negative relative value."""
    n = neg = flagged = 0; rel_min = 0.0
    for blk in blocks.values():
        for pk, pr in blk["pairs"].items():
            src, dst = pk.split("->")
            for nc, per in pr["per_key"].items():
                for a, d in per.items():
                    p = d["conformal"]; n += 1
                    if p.get("v_raw", 0.0) < 0:
                        neg += 1; mC = blk["sets"][f"{src}|C{nc}"]; mE = blk["sets"][f"{dst}|E"]
                        rel_min = min(rel_min, p["v_raw"] / max(mC["rho"] + mE["rho"], 1e-300))
                    if "v_below_algebraic_floor" in p.get("flags", []):
                        flagged += 1
    return {"n_predictions": n, "n_negative_raw": neg, "n_flagged_below_floor": flagged, "min_relative_v_raw": rel_min}


def main(a):
    import s3_run as R
    grid_path = a[a.index("--grid") + 1]; grid = json.loads(pathlib.Path(grid_path).read_text())
    man = json.loads((ROOT / grid["tokens_manifest"]).read_text())
    s2_inputs = json.loads((ROOT / "outputs/study2_v0.1/INPUTS.json").read_text())
    res = {"study": grid["study"], "written_utc": utc(), "grid_sha256": sha(grid_path), "tokens_manifest_sha256": sha(ROOT / grid["tokens_manifest"]),
           "study2_inputs_sha256": sha(ROOT / "outputs/study2_v0.1/INPUTS.json"), "s3_core_sha256": sha(HERE / "s3_core.py"), "s3_inputs_sha256": sha(HERE / "s3_inputs.py"),
           "note": "key-free inputs: set moments, cross-set shift covariances and the calibrated-threshold predictor at the realised texts; no key, no per-key level; predictions family-independent"}
    T0 = time.time()
    blocks, cons = compute(grid, R.spec_of(grid, False), lambda tok, tag: SD.load_eval(tag, tok, man), lambda tok, tag: SD.load_cal(tag, tok, man), s2_inputs, log=lambda m: print(m, flush=True))
    res["blocks"] = blocks; res["study2_consistency"] = cons; res["v_summary"] = v_summary(blocks)
    s2m = json.loads((ROOT / SD.S2_MANIFEST).read_text()); plan = SD.plan_sets(s2m)
    res["english_eval_overlap"] = len(set(plan["wikipedia_en_256"]["eval_ids"]) & set(plan["wikipedia_en_1024"]["eval_ids"]))
    res["study2_consistency_summary"] = {"n": len(cons), "max_abs_diff_rho": max((x["abs_diff_rho"] for x in cons), default=None), "max_abs_diff_sigma2": max((x["abs_diff_sigma2"] for x in cons), default=None)}
    res["seconds"] = round(time.time() - T0, 1)
    (OUT / "INPUTS.json").write_text(json.dumps(clean(res), indent=0, separators=(",", ":")))
    print("DONE", res["study2_consistency_summary"], res["v_summary"], "english eval overlap", res["english_eval_overlap"], res["seconds"], flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
