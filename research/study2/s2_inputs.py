"""Study 2 key-free inputs (v1; before the lock; touches no key). For every production chain (corpus cell x tokenizer x h) built on
the cached texts, and for every (rule, L) of the grid: the retention sizes (mean M, N_eff, |D|, contexts, nnz), the exact identities
at the realised document-averaged weights (A, B, C_cond, the fixed-size reduction (1/C_cond - 1)/(V - 1) and ratio), rho_bar, sigma^2,
mu_delta, and the common-factor predictor's SD of the level, population variance, finite-text floor and theory share at every alpha,
for the KGW family at each gamma and for the Gumbel family, at N = the grid's N and at the smaller candidate N (the prefix of the same
draw). These are inputs: deterministic functions of the fixed texts, computable without any key; they feed the power analysis
(eligibility by theory share at each candidate N), the compute projection (sizes) and the protocol's §11. No per-key level exists.
Writes outputs/study2_v0.1/INPUTS.json (pinned by the lock).
Usage: .venv/bin/python -u research/study2/s2_inputs.py --grid research/study2/grid_v0.1.json [--N-candidates 4000,10000] [--only-cell <tag>]
"""
import datetime, json, pathlib, resource, sys, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study1"))
import s2_core as S
import s2_data as D
import s1_core as C
from s2_run import TOKENS_MANIFEST, INPUTS, sha, utc


def chain_inputs(X, V, name, h, grid):
    t0 = time.time(); chain = S.build_chain(X, V, name, h); build = time.time() - t0
    out = {"N": int(X.shape[0]), "L_max": int(X.shape[1]), "V": V, "h": h, "n_tuples": int(len(chain.D)), "n_contexts": int(chain.n_ctx), "build_seconds": round(build, 2), "cells": {}}
    rng = np.random.default_rng(0)
    for L in grid["L_list"]:
        for rule in grid["rules"]:
            inc = chain.incidence(L, rule); rec = {"nnz": int(inc.nnz), "L": L, "rule": rule, "kgw": {}, "gumbel": None}
            for g in grid["families"]["kgw"]["gamma"]:
                pe = C.population_estimates(inc, chain, g, V, "independent", rng, B=0)
                if pe is None:
                    rec["kgw"][str(g)] = {"N_eff": 0}; continue
                idq, idz = pe["identity_q"], pe["identity_z"]; Mk = pe["M"][pe["keep"]]
                r = {"N_eff": pe["N_eff"], "mean_M": float(Mk.mean()), "min_M": int(Mk.min()), "A_q": idq["A"], "B_q": idq["B"], "C_cond": idq["C_cond"], "reduction_fixed_vs_indep": (1.0 / idq["C_cond"] - 1.0) / (V - 1) if idq["C_cond"] > 0 else None,
                     "exact_ratio_fixed_over_indep": idq["exact_ratio_formula"], "var_q_indep": idq["var_indep"], "var_q_fixed": idq["var_fixed"], "rho_bar": pe["rho_bar"], "sigma_model2": pe["sigma_model2"], "mu_delta": pe["mu_delta"],
                     "var_zbar_exact_indep": idz["var_indep"], "mean_var_text_z": pe["mean_var_text_z"], "A_q_between": pe["A_q_between"], "coverage_distinct_tuples": int((inc.getnnz(axis=0) > 0).sum()), "pred": {}}
                for a in grid["alpha"]:
                    p = C.mixture_predictor(pe["mu_delta"], pe["rho_bar"], a, pe["N_eff"], pe["sigma_model2"], tol=pe["sigma_tol"])
                    r["pred"][str(a)] = {k: p[k] for k in ("mean_level", "sd_pop", "floor", "sd_cond", "theory_share", "flags")}
                    r["pred"][str(a)]["exact_binomial_key_mean_if_distinct"] = C.exact_marginal_level_distinct_independent(pe["M"], C.green_fraction(g, V), g, a)
                rec["kgw"][str(g)] = r
            pg = S.population_estimates_score(inc, chain, rng, 1.0, B=0)
            if pg is not None:
                Mk = pg["M"][pg["keep"]]; r = {"N_eff": pg["N_eff"], "mean_M": float(Mk.mean()), "A_q": pg["identity_q"]["A"], "rho_bar": pg["rho_bar"], "sigma_model2": pg["sigma_model2"], "mean_var_text_z": pg["mean_var_text_z"], "pred": {}}
                for a in grid["alpha"]:
                    p = S.mixture_gaussian_closed(0.0, max(pg["rho_bar"], 0.0), S.gamma_threshold_z(a, Mk), pg["sigma_model2"], pg["N_eff"], tol=pg["sigma_tol"])   # the per-text closed form (R05 F6)
                    r["pred"][str(a)] = {k: p[k] for k in ("mean_level", "sd_pop", "floor", "sd_cond", "theory_share", "flags", "method")}
                rec["gumbel"] = r
            else:
                rec["gumbel"] = {"N_eff": 0}
            out["cells"][f"L{L}__{rule}"] = rec
    out["seconds"] = round(time.time() - t0, 1)
    return out


def main(a):
    grid = json.loads(pathlib.Path(a[a.index("--grid") + 1]).read_text()); man = json.loads(pathlib.Path(TOKENS_MANIFEST).read_text())
    Ns = [int(x) for x in (a[a.index("--N-candidates") + 1] if "--N-candidates" in a else f"4000,{grid['N']}").split(",")]
    only = a[a.index("--only-cell") + 1] if "--only-cell" in a else None
    res = {"study": grid["study"], "written_utc": utc(), "grid_sha256": sha(a[a.index("--grid") + 1]), "tokens_manifest_sha256": sha(TOKENS_MANIFEST), "N_candidates": Ns, "note": "key-free inputs: identities and predictor values at the realised texts; no key, no per-key level", "chains": {}}
    T0 = time.time()
    for spec in grid["cells"]:
        if only and spec["tag"] != only:
            continue
        for tok, tinfo in grid["tokenizers"].items():
            X_full = D.load_tokens(man, spec["tag"], tok, N=max(Ns), root=ROOT)
            for N in Ns:
                X = X_full[:N]
                for h in grid["h"]:
                    name = f"{spec['tag']}__{tok}__h{h}__N{N}"; g2 = dict(grid, L_list=spec["L"])
                    res["chains"][name] = chain_inputs(X, int(tinfo["V"]), name, h, g2)
                    print(f"[{time.time() - T0:7.1f}s] {name}: |D|={res['chains'][name]['n_tuples']} build {res['chains'][name]['build_seconds']}s total {res['chains'][name]['seconds']}s rss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**30:.2f} GB", flush=True)
            del X_full
    res["seconds"] = round(time.time() - T0, 1); res["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30, 2)
    pathlib.Path(INPUTS).write_text(json.dumps(res, indent=1, default=float)); print("DONE", INPUTS, flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
