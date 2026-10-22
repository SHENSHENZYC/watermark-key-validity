"""Study 2 input validation (v1; before the lock; no study cell is computed; no per-key level on real text exists). Writes
outputs/study2_v0.1/VALIDATION.json and runs the SYNTHETIC validation grid into a FRESH directory outputs/study2_v0.1/validation_<utc>/
(retained on disk as a pilot, git-ignored; synthetic tokens from a Zipf law at the Llama vocabulary size; validation keys).
Sections: (a) the token cache: every array against its manifest digest, shape and id range; the pools and draws recomputed from the
units metadata (ids digests); the seal's digests against the current partition, units and manifest; (b) fixtures with validation keys
on synthetic chains: the Study 1 code path reproduced field for field; the general predictor against the closed form; the exact Gamma
threshold by simulation; the Gumbel and KGW identities (independent; fixed at h = 0 at the real V) with 2,000-20,000 validation keys and
the fourth-moment SE's calibration; the simulated-shift predictor's scaling, Gaussian limit and a heavy-tuple case against observed
levels; the crossed bootstrap's coverage on key-independent tables; (c) the key policy; (d) the lock schema (acceptance under a copied
root; refusals); (e) provenance and slot; (f) the analyzer's inventory refusals; (g) the timed validation run and the pilot analyzer;
(h) the cost model (rates from the validation run and a real-sized synthetic chain) and the projection of every production chain
from the key-free sizes in INPUTS.json; (i) the power analysis from INPUTS.json (eligibility by theory share at each candidate N; the
key-count resolution).
Usage: .venv/bin/python -u research/study2/s2_validate.py [--skip-run]
"""
import copy, datetime, hashlib, json, pathlib, resource, shutil, subprocess, sys, tempfile, time
import numpy as np
from scipy.stats import norm
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study1")); sys.path.insert(0, str(ROOT / "tools"))
import s2_core as S
import s2_data as D
import s2_run as R
import s2_analyze as A
import s1_core as C
from s2_keys import check_keys, KeyPolicyError

GRID_PATH = R.GRID_CANON; GRID = json.loads((ROOT / GRID_PATH).read_text())
OUT = ROOT / R.OUT; OUT.mkdir(parents=True, exist_ok=True)
STAMP = f"{datetime.datetime.now(datetime.timezone.utc):%Y%m%dT%H%M%SZ}"; VAL_DIR = OUT / f"validation_{STAMP}"
VK = GRID["validation_key_seed_start"]; SKIP_RUN = "--skip-run" in sys.argv
rep = {"study": R.STUDY, "date_utc": STAMP, "grid": GRID_PATH, "grid_sha256": R.sha(ROOT / GRID_PATH), "validation_dir": str(VAL_DIR.relative_to(ROOT)), "checks": {}, "fixtures": {}, "timing": {}, "projection": {}, "power": {},
       "retained_pilot_note": "the validation cells and cost records stay on disk under validation_dir (git-ignored) with the pilot analysis file beside the directory; they are computed on SYNTHETIC tokens with validation keys; no per-key level on any real text is computed before the lock; the conductor reads the execution status, the counts, the sizes and the cost records"}
T0 = time.time()


def vkeys(n, offset=0):
    ks = list(range(VK + offset, VK + offset + n)); check_keys(ks, "validation"); return ks


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def syn(obs, exact, tol_rel=0.05):
    return {"observed": float(obs), "exact": float(exact), "ratio": float(obs / exact) if exact else None, "ok": bool(abs(obs - exact) <= tol_rel * abs(exact)) if exact else None}


# ---------------- (a) the token cache against its manifest and the metadata ----------------
man_path = ROOT / R.TOKENS_MANIFEST
if man_path.exists():
    man = json.loads(man_path.read_text()); a = {"manifest_sha256": R.sha(man_path), "N": man["N"], "cells": {}}
    df = D.load_units_meta()
    for cell in D.CELLS:
        tag = D.cell_tag(cell); e = man["cells"][tag]; pool, counts = D.eligible_pool(df, cell)
        seed = int(man["seed_base"]) + int(hashlib.sha256(D.cell_str(cell).encode()).hexdigest()[:8], 16); ids = D.draw(pool, man["N"], seed)
        rec = {"pool_size_recomputed": len(pool), "pool_size_manifest": e["pool_size"], "pool_sha256_matches": D.ids_digest(pool) == e["pool_sha256"], "seed_matches": seed == e["seed"], "ids_sha256_matches": D.ids_digest(ids) == e["ids_sha256"], "pool_counts": counts, "tokenizers": {}}
        for tok, te in e["tokenizers"].items():
            p = ROOT / te["file"]; ok = p.exists() and R.sha(p) == te["sha256"]; X = np.load(p) if ok else None
            rec["tokenizers"][tok] = {"digest_matches": bool(ok), "shape": list(X.shape) if ok else None, "shape_matches": (list(X.shape) == te["shape"]) if ok else False, "dtype": str(X.dtype) if ok else None,
                                      "ids_in_range": bool(X.min() >= 0 and X.max() < GRID["tokenizers"][tok]["V"]) if ok else False, "distinct_ids": int(len(np.unique(X))) if ok else None}
        a["cells"][tag] = rec
    acc_seal = man.get("seal", {})
    from corpora_access import Access
    acc = Access(str(D.UNITS_DIR), D.UNITS_VERSION)
    a["seal_digests_match_current"] = {"partition": acc.partition_sha256 == acc_seal.get("partition_sha256"), "units": acc.units_sha256 == acc_seal.get("units_sha256"), "manifest": R.sha(acc.manifest) == acc_seal.get("manifest_sha256")}
    cj = json.loads((D.UNITS_DIR / "counts.json").read_text())["tokenizer_provenance"]
    a["tokenizer_provenance_matches_counts_json"] = {t: man["tokenizers"][t]["files_sha256"] == cj[t]["files_sha256"] and man["tokenizers"][t]["revision"] == cj[t]["revision"] for t in man["tokenizers"]}
    a["all_ok"] = bool(all(r["pool_sha256_matches"] and r["seed_matches"] and r["ids_sha256_matches"] and all(t["digest_matches"] and t["shape_matches"] and t["ids_in_range"] for t in r["tokenizers"].values()) for r in a["cells"].values())
                       and all(a["seal_digests_match_current"].values()) and all(a["tokenizer_provenance_matches_counts_json"].values()))
    rep["checks"]["token_cache"] = a
else:
    rep["checks"]["token_cache"] = {"all_ok": False, "note": "tokens manifest missing"}
print(f"[{time.time()-T0:6.0f}s] (a) token cache: {rep['checks']['token_cache'].get('all_ok')}", flush=True)

# ---------------- (b) fixtures on synthetic chains ----------------
V = GRID["validation"]["law"]["V"]; law = C.ZipfIID(V, 1.0); rng0 = np.random.default_rng(20261013)
X = law.sample(600, 256, rng0); ch0 = S.build_chain(X, V, "fx", 0); ch1 = S.build_chain(X, V, "fx", 1)
# (b1) Study 1 code path reproduced field for field, and the general predictor against the closed form
inc = ch1.incidence(256, "distinct"); U = S.uniforms_chunk(vkeys(300), ch1.D); counts = np.asarray(inc @ (U < 0.25).astype(np.float64))
a1 = C.cell_statistics(inc, counts, ch1, 0.25, GRID["alpha"], V, "independent", np.random.default_rng(1)); b1 = S.kgw_cell_statistics(inc, counts, ch1, 0.25, GRID["alpha"], V, "independent", np.random.default_rng(1), deployer=True, B_text=30)
def _eq(x, y):
    return json.dumps(x, sort_keys=True, default=float) == json.dumps(y, sort_keys=True, default=float)
same_levels = all(_eq(a1["levels"][k][f], b1["levels"][k][f]) for k in a1["levels"] for f in a1["levels"][k] if f != "level_values")
same_top = (all(_eq(a1[f], b1[f]) for f in a1 if f not in ("levels", "zbar", "population", "q_hat")) and all(_eq(a1["zbar"][f], b1["zbar"][f]) for f in a1["zbar"] if f != "values")
            and all(_eq(a1["q_hat"][f], b1["q_hat"][f]) for f in a1["q_hat"] if f != "values") and all(round(x, 6) == y for x, y in zip(a1["q_hat"]["values"], b1["q_hat"]["values"]))
            and all(_eq(a1["population"][f], b1["population"][f]) for f in a1["population"]))   # the compacted per-key arrays (q_hat values to 6 decimals; zbar values dropped) are the only intended differences
same = same_levels and same_top
diffs = {k: b1["levels"][k]["pred_per_text_vs_closed_form_abs_diff_sd"] for k in b1["levels"]}
b5 = S.kgw_cell_statistics(inc, counts, ch1, 0.25, GRID["alpha"], V, "independent", np.random.default_rng(1), deployer=False, B_text=GRID["text_bootstrap_B"])
rep["fixtures"]["study1_fields_identical"] = {"ok": bool(same), "at_B_text": 30, "levels_identical": bool(same_levels), "other_fields_identical": bool(same_top),
                                              "level_counts_equal_values": bool(all(b1["levels"][k]["level_counts"][j] == round(a1["levels"][k]["level_values"][j] * a1["N_eff"]) for k in a1["levels"] for j in range(a1["levels"][k]["level_values"].__len__()))),
                                              "production_B_text": GRID["text_bootstrap_B"], "production_B_preserves_deterministic_quantities": bool(b5["population"]["rho_bar"] == a1["population"]["rho_bar"] and b5["population"]["sigma_model2"] == a1["population"]["sigma_model2"] and _eq(b5["identity_q"], a1["identity_q"]) and all(_eq(b5["levels"][k]["sd_obs_conditional"], a1["levels"][k]["sd_obs_conditional"]) and _eq(b5["levels"][k]["pred_first_order"], a1["levels"][k]["pred_first_order"]) and b5["levels"][k]["level_counts"] == [round(x * a1["N_eff"]) for x in a1["levels"][k]["level_values"]] for k in a1["levels"])),
                                              "production_B_changes_monte_carlo_realisations": {"sd_obs_boot_ci95_B30": a1["levels"]["0.01"]["sd_obs_boot_ci95"], "sd_obs_boot_ci95_B5": b5["levels"]["0.01"]["sd_obs_boot_ci95"], "note": "the text bootstrap consumes the cell's stream before the key bootstrap, the pairwise subsample and the two-way bootstrap, so their draws differ between B = 30 and B = 5 (R05 F5); the estimands do not"},
                                              "rho_bar_boot_se_B30_vs_B5": [a1["population"]["rho_bar_boot_se"], b5["population"]["rho_bar_boot_se"]], "chain": "N = 600, L = 256 synthetic chain at V = 128,256 (not a production-sized chain)"}
rep["fixtures"]["per_text_closed_form_vs_study1_closed_form"] = {"abs_diff_sd_by_alpha": diffs, "ok": bool(max(diffs.values()) < 1e-9), "chain": "N = 600, L = 256, h = 1, synthetic Zipf at V = 128,256 (not a production-sized chain)"}
# (b1b) the per-text closed form (R05 F6): equals Study 1's closed form at sigma2 in {0, 1e-6, 1e-3, 0.5, 1} for one threshold; equals the discrete-node quadrature at an ordinary
# sigma2 with varying Gamma thresholds; and matches Monte Carlo at sigma2 -> 0 with varying thresholds (where a fixed Gaussian quadrature failed)
z01 = norm.isf(0.01); f6 = {"vs_study1_closed_form": {}, "vs_quadrature_ordinary_sigma": None, "vs_monte_carlo_tiny_sigma": None}
for s2_ in (0.0, 1e-6, 1e-3, 0.5, 1.0):
    cf = C.mixture_predictor(0.0, 1.0, 0.01, 10000, s2_); cl = S.mixture_gaussian_closed(0.0, 1.0, np.full(10000, z01), s2_, 10000)
    f6["vs_study1_closed_form"][str(s2_)] = {"abs_diff_mean": abs(cf["mean_level"] - cl["mean_level"]), "abs_diff_sd": abs(cf["sd_cond"] - cl["sd_cond"])}
Mv = np.random.default_rng(0).integers(100, 900, size=5000); tv = S.gamma_threshold_z(0.01, Mv)
nq, wq = S.gaussian_shift_nodes(0.0, 0.04); qd = S.mixture_general(nq, wq, tv, 0.9, 5000); cl = S.mixture_gaussian_closed(0.0, 0.04, tv, 0.9, 5000)
f6["vs_quadrature_ordinary_sigma"] = {"abs_diff_sd": abs(qd["sd_cond"] - cl["sd_cond"]), "abs_diff_mean": abs(qd["mean_level"] - cl["mean_level"]), "n_distinct_thresholds": cl["n_distinct_thresholds"]}
rmc = np.random.default_rng(1); Bmc = 400000; dmc = rmc.normal(0, 1.0, Bmc); sub = tv[:200]
for s2_ in (1e-6, 1e-3):
    pim = norm.sf((sub[None, :] - dmc[:, None]) / np.sqrt(s2_)); am = pim.mean(axis=1); clm = S.mixture_gaussian_closed(0.0, 1.0, sub, s2_, 5000)
    f6["vs_monte_carlo_tiny_sigma"] = (f6["vs_monte_carlo_tiny_sigma"] or {}) | {str(s2_): {"mc_mean": float(am.mean()), "closed_mean": clm["mean_level"], "mc_sd_pop": float(am.std()), "closed_sd_pop": clm["sd_pop"], "mc_draws": Bmc}}
f6["ok"] = bool(max(x["abs_diff_sd"] for x in f6["vs_study1_closed_form"].values()) < 1e-12 and f6["vs_quadrature_ordinary_sigma"]["abs_diff_sd"] < 1e-9
                and all(abs(x["mc_sd_pop"] - x["closed_sd_pop"]) < 3 * x["closed_sd_pop"] / np.sqrt(2 * Bmc) * 10 for x in f6["vs_monte_carlo_tiny_sigma"].values()))
rep["fixtures"]["closed_form_per_text_thresholds"] = f6
# (b2) the exact Gamma threshold by simulation
gt = {}
for M in (64, 250, 1000):
    sim = np.random.default_rng(3).exponential(1.0, size=(200000, M)).sum(axis=1)
    for al in (0.01, 0.05):
        lvl = float(np.mean((sim - M) / np.sqrt(M) > S.gamma_threshold_z(al, M))); gt[f"M{M}_a{al}"] = {"empirical": lvl, "target": al, "within_3se": bool(abs(lvl - al) <= 3 * np.sqrt(al * (1 - al) / 200000))}
rep["fixtures"]["gamma_threshold_exact"] = {"cases": gt, "ok": bool(all(v["within_3se"] for v in gt.values()))}
# (b3) identities with many validation keys: Gumbel (var_s = 1) and KGW independent and fixed at h = 0 at the real V
inc0 = ch0.incidence(256, "distinct"); K_id = 20000
pg = S.population_estimates_score(inc0, ch0, np.random.default_rng(2), 1.0, B=0); M0 = pg["M"]; keep0 = pg["keep"]
sbar = np.empty(K_id); qh = np.empty(K_id)
for c0 in range(0, K_id, 500):
    U0 = S.uniforms_chunk(vkeys(500, 1000 + c0), ch0.D); sums = np.asarray(inc0 @ S.gumbel_scores(U0)); cnt = np.asarray(inc0 @ (U0 < 0.25).astype(np.float64))
    sbar[c0:c0 + 500] = (sums[keep0] / M0[keep0][:, None]).mean(axis=0); qh[c0:c0 + 500] = (cnt[keep0] / M0[keep0][:, None]).mean(axis=0)
pe0 = C.population_estimates(inc0, ch0, 0.25, V, "independent", np.random.default_rng(2), B=0)
rep["fixtures"]["identity_gumbel_20000_keys"] = syn(sbar.var(ddof=1), pg["identity_q"]["var"], 0.03) | {"mean_sbar": float(sbar.mean()), "exact_mean": 1.0}
rep["fixtures"]["identity_kgw_indep_20000_keys"] = syn(qh.var(ddof=1), pe0["identity_q"]["var_indep"], 0.03) | {"mean_q": float(qh.mean()), "exact_mean": 0.25 * float(pe0["wq"].sum())}
# fourth-moment SE calibration of the known-mean estimator (Gumbel) over 200 disjoint 100-key subsamples
terms = (sbar - 1.0) ** 2; se_exact = np.sqrt(max(pg["identity_q"]["A4"] * S.EXP_KAPPA4 + 3 * pg["identity_q"]["var"] ** 2 - pg["identity_q"]["var"] ** 2, 0.0) / 100)
std_dev = (terms.reshape(200, 100).mean(axis=1) - pg["identity_q"]["var"]) / se_exact
rep["fixtures"]["gumbel_known_mean_se_calibration"] = {"subsamples": 200, "K_each": 100, "sd_of_standardised_deviation": float(std_dev.std(ddof=1)), "max_abs": float(np.abs(std_dev).max()), "share_abs_gt3": float(np.mean(np.abs(std_dev) > 3)), "ok": bool(0.7 < std_dev.std(ddof=1) < 1.4)}
# fixed colouring at h = 0 at the real V: 2,000 validation keys; observed fixed/indep variance ratio against the exact formula
kf = vkeys(2000, 50000); colf = C.colour_fixed(ch0, kf, 0.25, V).astype(np.float64); coli = C.colour_independent(ch0, kf, 0.25, V).astype(np.float64)
qf = (np.asarray(inc0 @ colf)[keep0] / M0[keep0][:, None]).mean(axis=0); qi = (np.asarray(inc0 @ coli)[keep0] / M0[keep0][:, None]).mean(axis=0)
rep["fixtures"]["fixed_h0_real_V"] = {"V": V, "queried_tokens": int(len(ch0.D)), "marginal_green_fixed": float(colf.mean()), "marginal_green_indep": float(coli.mean()), "g": C.green_fraction(0.25, V),
                                     "var_fixed_obs": float(qf.var(ddof=1)), "var_fixed_exact": pe0["identity_q"]["var_fixed"], "var_indep_obs": float(qi.var(ddof=1)), "var_indep_exact": pe0["identity_q"]["var_indep"],
                                     "observed_ratio": float(qf.var(ddof=1) / qi.var(ddof=1)), "exact_ratio": pe0["identity_q"]["exact_ratio_formula"], "reduction": (1 / pe0["identity_q"]["C_cond"] - 1) / (V - 1),
                                     "ok": bool(abs(qf.var(ddof=1) / pe0["identity_q"]["var_fixed"] - 1) < 0.1 and abs(qi.var(ddof=1) / pe0["identity_q"]["var_indep"] - 1) < 0.1)}
# (b4) the simulated-shift predictor: scaling to rho_bar; the Gaussian limit on uniform weights; a heavy-tuple case against observed levels
d_sim, info = S.simulated_shift(pe0["wz"], max(pe0["rho_bar"], 0.0), "kgw", 0.25, np.random.default_rng(7))
wu = np.full(5000, 1.0 / np.sqrt(5000)); d_u, info_u = S.simulated_shift(wu, 1.0, "kgw", 0.5, np.random.default_rng(8))
rep["fixtures"]["simulated_shift"] = {"var_matches_rho_bar": syn(d_sim.var(), pe0["rho_bar"], 0.03), "heavy_share": info["var_heavy_share"], "skew": info["sample_skew"],
                                      "uniform_weights_gaussian_limit": {"skew": info_u["sample_skew"], "excess_kurtosis": info_u["sample_kurtosis_excess"], "var": float(d_u.var()), "ok": bool(abs(info_u["sample_skew"]) < 0.1 and abs(info_u["sample_kurtosis_excess"]) < 0.2)}}
# heavy-tuple chain: a support law (50 tokens of V) so that a few tuples carry the weight; observed SD over 3,000 validation keys against both predictors
lawH = C.SupportUniform(V, 50); XH = lawH.sample(2000, 64, np.random.default_rng(11)); chH = S.build_chain(XH, V, "heavy", 0); incH = chH.incidence(64, "raw")
UH = S.uniforms_chunk(vkeys(3000, 60000), chH.D); cH = np.asarray(incH @ (UH < 0.5).astype(np.float64)); stH = S.kgw_cell_statistics(incH, cH, chH, 0.5, [0.01, 0.05], V, "independent", np.random.default_rng(12))
rep["fixtures"]["heavy_tuple_cell_h0_raw_support50"] = {a_: {"sd_obs": stH["levels"][a_]["sd_obs_conditional"], "pred_gaussian_shift": stH["levels"][a_]["pred_first_order"]["sd_cond"], "pred_simulated_shift": stH["levels"][a_]["pred_simulated_shift"]["sd_cond"],
                                                             "ratio_gaussian": stH["levels"][a_]["ratio_obs_over_pred"], "ratio_simulated": stH["levels"][a_]["ratio_obs_over_pred_simulated_shift"], "shift_skew": stH["simulated_shift"]["sample_skew"]} for a_ in ("0.01", "0.05")}
# (b5) the crossed bootstrap's coverage on key-independent tables (per-key level Binomial(N, alpha)/N; the median key's level has expectation about alpha)
cov = []; rngc = np.random.default_rng(13)
for _ in range(40):
    Rt = rngc.random((2000, 200)) < 0.01; cb = S.crossed_bootstrap(Rt, 0.01, rngc, B=120); lo, hi = cb["q0.5"]["ci95"]; cov.append(lo <= 0.01 <= hi)
rep["fixtures"]["crossed_bootstrap_median_coverage_null"] = {"replicates": 40, "coverage_of_alpha_by_median_interval": float(np.mean(cov)), "note": "a 95% percentile interval of the median key level on key-independent tables; expected coverage about 0.95 (40 replicates: a sanity check, not a calibration)"}
print(f"[{time.time()-T0:6.0f}s] (b) fixtures done", flush=True)

# (b6) the S2 thresholds (the two-sided KL rule's power at the grid's K and at 500), by root-finding on the bound
from scipy.optimize import brentq
def s2_thresholds(mu, K, p=C.R2_PBOUND):
    f = lambda a_: 2 * np.exp(-K * C.kl_bernoulli(a_, mu)) - p
    up = brentq(f, mu, 1 - 1e-12); lo = brentq(f, 1e-15, mu) if 2 * (1 - mu) ** K < p else None
    return {"flag_above": float(up), "flag_below": (float(lo) if lo is not None else "none"), "bound_at_zero": float(min(1.0, 2 * (1 - mu) ** K))}
rep["fixtures"]["s2_thresholds"] = {str(K): {"dead_detector_flaggable_iff_mu_above": float(1 - np.exp(np.log(C.R2_PBOUND / 2) / K)), **{f"mu_{mu}": s2_thresholds(mu, K) for mu in (0.05, 0.01, 0.001)}} for K in sorted({500, 1000, GRID["K"]})}
rep["fixtures"]["s2_check_count"] = {"distinct_rule_cells": len([c for c in R.expected_cells(GRID) if c["rule"] == "distinct" and (c["family"] == "gumbel" or c["colouring"] == "independent")]), "alphas": len(GRID["alpha"])}
rep["fixtures"]["s2_check_count"]["union_bound_if_all_live"] = rep["fixtures"]["s2_check_count"]["distinct_rule_cells"] * rep["fixtures"]["s2_check_count"]["alphas"] * C.R2_PBOUND

# ---------------- (c) key policy ----------------
kp = {}
for name, ks, purpose, expect in (("study2_range", range(22000, 23000), "study2", True), ("study2_below", range(21990, 22010), "study2", False), ("study2_reserved", range(30000, 30010), "study2", False), ("validation_ok", range(1000000, 1000010), "validation", True),
                                   ("validation_low", range(5000, 5010), "validation", False), ("study2_zero_range", range(0, 500), "study2", False), ("study2_study1_range", range(20000, 20100), "study2", False)):
    try:
        check_keys(ks, purpose); got = True
    except KeyPolicyError:
        got = False
    kp[name] = {"accepted": got, "expected": expect, "ok": got == expect}
rep["fixtures"]["key_policy"] = kp | {"all_ok": all(v["ok"] for v in kp.values())}

# ---------------- (d) the lock schema under a copied root ----------------
def make_root(tmp):
    """A copy of the repository's pinned paths (placeholders for files that do not exist yet) and the canonical resolution memo."""
    for f in R.PINNED + (R.RESOLUTION,):
        src = ROOT / f; dst = tmp / f; dst.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            shutil.copy(src, dst)
        else:
            dst.write_text(f"placeholder for {f} (validation fixture)\n")
    # the manifest in the fixture must be consistent with the grid (N, seed base, cells, V)
    mp = tmp / R.TOKENS_MANIFEST
    if not (ROOT / R.TOKENS_MANIFEST).exists():
        mp.write_text(json.dumps({"N": GRID["N"], "seed_base": GRID["text_seed_base"], "tokenizers": {t: {"V": GRID["tokenizers"][t]["V"]} for t in GRID["tokenizers"]}, "cells": {c["tag"]: {"tokenizers": {t: {"sha256": "0" * 64} for t in GRID["tokenizers"]}} for c in GRID["cells"]}}))


def canonical_lock(tmp):
    return {"study": R.STUDY, "date": "2026-10-12", "approved_by": "Yichen", "before_outcomes": True, "final": False, "grid": R.GRID_CANON, "protocol": R.PROTOCOL, "validation": R.VALIDATION, "inputs": R.INPUTS, "tokens_manifest": R.TOKENS_MANIFEST,
            "hashes": {f: R.sha(tmp / f) for f in R.PINNED}, "review": {"checkpoint": R.CHECKPOINT, "resolution": R.RESOLUTION, "sha256": R.sha(tmp / R.RESOLUTION)}, "keys": {"production_start": GRID["key_seed_start"], "K": GRID["K"], "K_fixed_h0": GRID["K_fixed_h0"]}}


lock_fx = {"accepted": [], "refused": {}, "unexpected_accept": []}
with tempfile.TemporaryDirectory() as td:
    tmp = pathlib.Path(td); make_root(tmp); base = canonical_lock(tmp)
    def try_lock(name, lock, grid_arg=R.GRID_CANON):
        p = tmp / f"lock_{name}.json"; p.write_text(json.dumps(lock))
        try:
            R.verify_lock(p, grid_arg, root=tmp); lock_fx["accepted"].append(name)
            if name != "complete_canonical":
                lock_fx["unexpected_accept"].append(name)
        except R.LockError as e:
            lock_fx["refused"][name] = str(e)[:140]
        except KeyPolicyError as e:
            lock_fx["refused"][name] = "key policy: " + str(e)[:120]
    try_lock("complete_canonical", base)
    variants = {"missing_approved_by": {k: v for k, v in base.items() if k != "approved_by"}, "final_true": dict(base, final=True), "before_outcomes_false": dict(base, before_outcomes=False), "approved_by_other": dict(base, approved_by="conductor"),
                "non_iso_date": dict(base, date="12/10/2026"), "early_date": dict(base, date="2026-10-01"), "wrong_study": dict(base, study="study1_v0.3"), "protocol_is_grid": dict(base, protocol=R.GRID_CANON),
                "validation_noncanonical": dict(base, validation="outputs/study2_v0.1/VALIDATION_old.json"), "inputs_noncanonical": dict(base, inputs="outputs/study2_v0.1/inputs.json"), "tokens_noncanonical": dict(base, tokens_manifest="outputs/study2_v0.1/tokens.json"),
                "checkpoint_R03": dict(base, review=dict(base["review"], checkpoint="R03")), "resolution_R04": dict(base, review=dict(base["review"], resolution="research/reviews/R04_study1-report/RESOLUTION.md")),
                "tampered_digest": dict(base, hashes=dict(base["hashes"], **{"research/study2/s2_core.py": "0" * 64})), "non_hex_digest": dict(base, hashes=dict(base["hashes"], **{"research/study2/s2_core.py": "zz"})),
                "missing_code_digest": dict(base, hashes={k: v for k, v in base["hashes"].items() if k != "research/study2/s2_analyze.py"}), "extra_digest": dict(base, hashes=dict(base["hashes"], **{"research/study1/s1_run.py": "0" * 64})),
                "key_record_mismatch": dict(base, keys=dict(base["keys"], K=GRID["K"] + 1)), "key_start_reserved": dict(base, keys=dict(base["keys"], production_start=30000)), "review_digest_wrong": dict(base, review=dict(base["review"], sha256="1" * 64))}
    for name, lk in variants.items():
        try_lock(name, lk)
    try_lock("noncanonical_grid_argument", base, grid_arg="research/study2/grid_v0.2.json")
    # a manifest with N below the grid's
    mp = tmp / R.TOKENS_MANIFEST; mj = json.loads(mp.read_text()); mj_small = dict(mj, N=GRID["N"] - 1); mp.write_text(json.dumps(mj_small)); base2 = canonical_lock(tmp); try_lock("manifest_N_too_small", base2); mp.write_text(json.dumps(mj))
rep["fixtures"]["lock"] = lock_fx | {"ok": lock_fx["accepted"] == ["complete_canonical"] and len(lock_fx["refused"]) == 22}
print(f"[{time.time()-T0:6.0f}s] (c)(d) key policy {rep['fixtures']['key_policy']['all_ok']}; lock accepted {lock_fx['accepted']} refused {len(lock_fx['refused'])}", flush=True)

# ---------------- (e) provenance and slot ----------------
cells_v = R.expected_cells(GRID, validation=True); c0 = cells_v[0]; c1 = cells_v[1]
with tempfile.TemporaryDirectory() as td:
    tmp = pathlib.Path(td); prov = R.provenance("validation", None, ROOT / GRID_PATH, "synthetic", VK, c0["K"], c0["N"], R.slot_of(c0), None)
    body = dict(R.slot_of(c0), N_eff=1, levels={}, provenance=prov); (tmp / c0["file"]).write_text(json.dumps(body))
    pv = {"matching_reusable": R.cell_reusable(tmp / c0["file"], prov), "absent_false": R.cell_reusable(tmp / "nope.json", prov) is False}
    for name, p2, b2 in (("foreign_provenance", dict(prov, lock_sha256="0" * 64), None), ("same_provenance_other_slot", dict(prov, slot=R.slot_of(c1)), None), ("body_disagrees", prov, dict(body, L=9999))):
        if b2 is not None:
            (tmp / c0["file"]).write_text(json.dumps(b2))
        try:
            R.cell_reusable(tmp / c0["file"], p2); pv[name] = "ACCEPTED (unexpected)"
        except R.ProvenanceError as e:
            pv[name] = "refused"
        (tmp / c0["file"]).write_text(json.dumps(body))
rep["fixtures"]["provenance_slot"] = pv | {"ok": pv["matching_reusable"] is True and pv["absent_false"] and all(v == "refused" for k, v in pv.items() if k not in ("matching_reusable", "absent_false"))}

# ---------------- (g) the timed validation run and the pilot analyzer (before (f), which mutates a copy of it) ----------------
if not SKIP_RUN:
    VAL_DIR.mkdir(parents=True, exist_ok=True); t0 = time.time()
    r = subprocess.run([sys.executable, "-u", str(HERE / "s2_run.py"), "--grid", GRID_PATH, "--validation", "--out-dir", str(VAL_DIR / "cells")], cwd=ROOT, capture_output=True, text=True)
    run_s = time.time() - t0; cells_dir = VAL_DIR / "cells"; n_cells = len([f for f in cells_dir.glob("*.json") if not f.name.startswith("costs__")])
    pil = VAL_DIR.parent / f"results_pilot_{STAMP}.json"
    r2 = subprocess.run([sys.executable, str(HERE / "s2_analyze.py"), "--grid", GRID_PATH, "--pilot", "--cells", str(cells_dir), "--out", str(pil)], cwd=ROOT, capture_output=True, text=True)
    pres = json.loads(pil.read_text()) if pil.exists() else {}
    sizes = [f.stat().st_size for f in cells_dir.glob("*.json") if not f.name.startswith("costs__")]
    rep["timing"]["validation_run"] = {"seconds": round(run_s, 1), "returncode": r.returncode, "stderr_tail": r.stderr[-400:], "n_cells": n_cells, "expected_cells": len(cells_v), "cell_file_kb_mean": round(float(np.mean(sizes)) / 1024, 1) if sizes else None, "K_validation": GRID["validation"]["K"],
                                      "analyzer_returncode": r2.returncode, "analyzer_stdout": r2.stdout[-500:], "analyzer_stderr_tail": r2.stderr[-300:],
                                      "pilot_counts_only": {"S1_counts": pres.get("rules", {}).get("S1_adequacy", {}).get("counts"), "S2": {k: pres.get("rules", {}).get("S2_key_mean_audit", {}).get(k) for k in ("n_checks", "n_flagged")}, "S3": {k: pres.get("rules", {}).get("S3_identities", {}).get(k) for k in ("n_checks", "n_gross", "coverage_nominal95")}}}
    print(f"[{time.time()-T0:6.0f}s] (g) validation run {run_s:.0f}s rc={r.returncode} cells={n_cells}; analyzer rc={r2.returncode}", flush=True)
    # ---------------- (f) the analyzer's inventory refusals on a mutated copy ----------------
    inv = {}
    def try_inventory(name, mutate):
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td) / "cells"; shutil.copytree(cells_dir, tmp); mutate(tmp)
            try:
                A.load_inventory(tmp, GRID, pilot=True); inv[name] = "ACCEPTED (unexpected)"
            except A.InventoryError as e:
                inv[name] = "refused: " + str(e)[:110]
    files = sorted(f for f in cells_dir.glob("*.json") if not f.name.startswith("costs__"))
    def edit_cell(t, i, fn):
        p_ = t / files[i].name; d_ = json.loads(p_.read_text()); fn(d_); p_.write_text(json.dumps(d_))
    try_inventory("one_missing", lambda t: (t / files[0].name).unlink())
    try_inventory("one_extra", lambda t: (t / "extra__cell.json").write_text("{}"))
    try_inventory("stale_provenance", lambda t: edit_cell(t, 0, lambda d: d["provenance"].update(core_sha256="0" * 64)))
    try_inventory("same_provenance_wrong_cell_copy", lambda t: shutil.copy(t / files[0].name, t / files[1].name))
    try_inventory("missing_alpha", lambda t: edit_cell(t, 0, lambda d: d["levels"].pop("0.001")))
    try_inventory("level_counts_not_K", lambda t: edit_cell(t, 0, lambda d: d["levels"]["0.01"].update(level_counts=d["levels"]["0.01"]["level_counts"][:-1])))
    # R05 F1: a missing or zero N_eff, a marker at a live slot
    try_inventory("missing_N_eff", lambda t: edit_cell(t, 0, lambda d: d.pop("N_eff")))
    try_inventory("zero_N_eff", lambda t: edit_cell(t, 0, lambda d: d.update(N_eff=0)))
    try_inventory("marker_at_live_slot", lambda t: edit_cell(t, 0, lambda d: d.pop("levels")))
    # R05 F2: malformed counts, a contradictory summary, a nesting violation with consistent summaries
    try_inventory("counts_negative", lambda t: edit_cell(t, 1, lambda d: d["levels"]["0.01"].update(level_counts=[-1] * len(d["levels"]["0.01"]["level_counts"]))))
    try_inventory("counts_fractional", lambda t: edit_cell(t, 1, lambda d: d["levels"]["0.01"].update(level_counts=[0.5] * len(d["levels"]["0.01"]["level_counts"]))))
    try_inventory("counts_above_N_eff", lambda t: edit_cell(t, 1, lambda d: d["levels"]["0.01"].update(level_counts=[d["N_eff"] + 1] * len(d["levels"]["0.01"]["level_counts"]))))
    try_inventory("counts_contradict_summary", lambda t: edit_cell(t, 1, lambda d: d["levels"]["0.01"].update(level_counts=[0] * len(d["levels"]["0.01"]["level_counts"]))))
    def nesting_violation(d):
        k = d["levels"]["0.001"]["level_counts"]; k[0] = d["N_eff"]; lev = np.array(k) / d["N_eff"]; lv = d["levels"]["0.001"]
        lv.update(key_mean_level=float(lev.mean()), sd_obs_conditional=float(lev.std(ddof=1)), max_key=float(lev.max()), min_key=float(lev.min()), share_keys_above_2alpha=float(np.mean(lev > 0.002)), share_keys_above_5alpha=float(np.mean(lev > 0.005)),
                  se_conditional_on_texts=float(lev.std(ddof=1) / np.sqrt(len(k))), quantiles={q: float(np.quantile(lev, float(q))) for q in lv["quantiles"]},
                  r2_kl_pbound=C.kl_chernoff_pbound(float(lev.mean()), float(lv.get("exact_marginal_if_indep_distinct", lv.get("exact_marginal_if_distinct"))), len(k)))
    try_inventory("nesting_violation_consistent_summaries", lambda t: edit_cell(t, 1, nesting_violation))
    # R05 F9: non-finite or contradictory decision values; a false structural-zero flag; a reversed interval; a NaN SE; an out-of-range exact mean
    gum_i = next(i for i, f in enumerate(files) if "__gumbel__" in f.name and "__distinct" in f.name)
    try_inventory("kl_bound_nan", lambda t: edit_cell(t, gum_i, lambda d: d["levels"]["0.01"].update(r2_kl_pbound=float("nan"))))
    try_inventory("structural_zero_flag_false", lambda t: edit_cell(t, gum_i, lambda d: d["levels"]["0.01"].update(structural_zero=True)))
    try_inventory("ratio_interval_reversed", lambda t: edit_cell(t, gum_i, lambda d: d["levels"]["0.01"].update(ratio_boot_ci95=[1.4, 0.8])))
    try_inventory("sd_interval_reversed", lambda t: edit_cell(t, gum_i, lambda d: d["levels"]["0.01"].update(sd_obs_boot_ci95=list(reversed(d["levels"]["0.01"]["sd_obs_boot_ci95"])))))
    try_inventory("sd_boot_se_nan", lambda t: edit_cell(t, gum_i, lambda d: d["levels"]["0.01"].update(sd_obs_boot_se=float("nan"))))
    try_inventory("exact_mean_out_of_range", lambda t: edit_cell(t, gum_i, lambda d: d["levels"]["0.01"].update(exact_marginal_if_distinct=1.5)))
    try_inventory("quantiles_empty", lambda t: edit_cell(t, gum_i, lambda d: d["levels"]["0.01"].update(quantiles={})))
    try_inventory("quantile_nan", lambda t: edit_cell(t, gum_i, lambda d: d["levels"]["0.01"]["quantiles"].update({"0.5": float("nan")})))
    # R05 F10: the deployer flag against the grid; null crossed values; a wrong resample count
    dep_i = next(i for i, f in enumerate(files) if json.loads(f.read_text()).get("deployer_subset"))
    try_inventory("deployer_flag_false", lambda t: edit_cell(t, dep_i, lambda d: d.update(deployer_subset=False)))
    try_inventory("deployer_flag_missing", lambda t: edit_cell(t, dep_i, lambda d: d.pop("deployer_subset")))
    try_inventory("crossed_values_null", lambda t: edit_cell(t, dep_i, lambda d: d["levels"]["0.01"].update(deployer_crossed={k: None for k in d["levels"]["0.01"]["deployer_crossed"]})))
    try_inventory("crossed_B_wrong", lambda t: edit_cell(t, dep_i, lambda d: d["levels"]["0.01"]["deployer_crossed"].update(B=100)))
    # the registered exceptions must still be ACCEPTED: a valid structural zero (counts 0, exact mean 0, bound 1) and a flagged zero prediction with the non-finite ratio
    def valid_structural_zero(d):
        for a_ in ("0.01", "0.05", "0.001"):
            lv = d["levels"][a_]; Kc = len(lv["level_counts"]); lv["level_counts"] = [0] * Kc
            lv.update(key_mean_level=0.0, sd_obs_conditional=0.0, max_key=0.0, min_key=0.0, share_keys_above_2alpha=0.0, share_keys_above_5alpha=0.0, se_conditional_on_texts=0.0, quantiles={q: 0.0 for q in lv["quantiles"]}, structural_zero=True, sd_obs_boot_se=0.0, sd_obs_boot_ci95=[0.0, 0.0])
            key_ = "exact_marginal_if_indep_distinct" if "exact_marginal_if_indep_distinct" in lv else "exact_marginal_if_distinct"; lv[key_] = 0.0; lv["r2_kl_pbound"] = C.kl_chernoff_pbound(0.0, 0.0, Kc)
            if lv["pred_first_order"]["sd_cond"] > 0:
                lv["ratio_obs_over_pred"] = 0.0; lv["ratio_boot_ci95"] = [0.0, 0.0]
    def flagged_zero_prediction(d):
        for a_ in ("0.01", "0.05", "0.001"):
            lv = d["levels"][a_]; lv["pred_first_order"] = dict(lv["pred_first_order"], sd_cond=0.0, flags=["sigma2_nonfinite"]); lv["ratio_obs_over_pred"] = float("nan"); lv["ratio_boot_ci95"] = [float("nan"), float("nan")]
    for nm, fn_ in (("valid_structural_zero_accepted", valid_structural_zero), ("flagged_zero_prediction_accepted", flagged_zero_prediction)):
        with tempfile.TemporaryDirectory() as td:
            t = pathlib.Path(td) / "cells"; shutil.copytree(cells_dir, t); edit_cell(t, gum_i, fn_)
            try:
                A.load_inventory(t, GRID, pilot=True); inv[nm] = "accepted"
            except A.InventoryError as e:
                inv[nm] = "REFUSED (unexpected): " + str(e)[:110]
    # R05 F4: a deployer-subset cell without its crossed block
    dep_i = next(i for i, f in enumerate(files) if json.loads(f.read_text()).get("deployer_subset"))
    try_inventory("deployer_cell_without_crossed_block", lambda t: edit_cell(t, dep_i, lambda d: d["levels"]["0.01"].pop("deployer_crossed")))
    try:
        A.load_inventory(cells_dir, GRID, pilot=False, lock_path=None); inv["study_mode_without_lock"] = "ACCEPTED (unexpected)"
    except A.InventoryError as e:
        inv["study_mode_without_lock"] = "refused: " + str(e)[:110]
    try:
        A.load_inventory(cells_dir, GRID, pilot=True); inv["complete_pilot_inventory"] = "accepted"
    except A.InventoryError as e:
        inv["complete_pilot_inventory"] = "REFUSED (unexpected): " + str(e)[:110]
    inv["study_mode_without_lock_reaches_lock_branch"] = inv["study_mode_without_lock"].startswith("refused: study mode requires --lock")
    # R05 F3: the language-disparity cases and the explicit six-cell selection
    Ld = A.language_disparity; six = ["a", "b", "c", "d", "e", "f"]
    lang_fx = {"identical_positive": Ld(np.full((6, 50), 0.01), six, {}), "all_zero": Ld(np.zeros((6, 50)), six, {}), "one_zero_language": Ld(np.where(np.arange(50)[None, :] < 10, np.array([0.0, 0.01, 0.01, 0.01, 0.01, 0.01])[:, None], 0.01), six, {}),
               "production_selection": [sp["tag"] for sp in GRID["cells"] if sp.get("source") == "wikipedia" and sp.get("L_cell") == 256]}
    lang_fx["ok"] = bool(lang_fx["identical_positive"]["share_all_positive_keys_ratio_gt2"] == 0.0 and lang_fx["identical_positive"]["n_keys_all_positive"] == 50 and lang_fx["all_zero"]["n_keys_all_zero"] == 50 and lang_fx["all_zero"]["share_all_positive_keys_ratio_gt2"] is None
                         and lang_fx["one_zero_language"]["n_keys_some_zero"] == 10 and lang_fx["one_zero_language"]["n_keys_all_positive"] == 40 and len(lang_fx["production_selection"]) == 6 and "wikipedia_en_1024" not in lang_fx["production_selection"])
    rep["fixtures"]["language_disparity_cases"] = {k: ({kk: vv for kk, vv in val.items() if kk.startswith(("n_keys", "share", "median"))} if isinstance(val, dict) else val) for k, val in lang_fx.items()}
    vcells_ = R.expected_cells(GRID, validation=True); n_dep_expected = sum(1 for c_ in vcells_ if R.in_deployer_subset(c_, GRID, GRID["validation"]["L"])) * len(GRID["alpha"])
    rep["fixtures"]["pilot_rule_paths_exercised"] = {"deployer_rows_expected_from_grid": n_dep_expected, "deployer_rows_equal_expected": len(pres.get("descriptive", {}).get("deployer_view", [])) == n_dep_expected, "S4_chains": pres.get("rules", {}).get("S4_H_length_raw", {}).get("n_chains"), "S5_chains": pres.get("rules", {}).get("S5_H_width", {}).get("n_chains"), "S1_candidates": (pres.get("rules", {}).get("S1_adequacy", {}).get("counts") or {}).get("candidate"),
                                                     "deployer_rows": len(pres.get("descriptive", {}).get("deployer_view", [])), "S2_checks": (pres.get("rules", {}).get("S2_key_mean_audit", {}) or {}).get("n_checks"), "language_blocks": len(pres.get("descriptive", {}).get("correlations", {}).get("language_disparity", [])), "note": "the synthetic pilot has one corpus cell and one tokenizer, so the between-cell and language blocks are empty by construction; S1, S4, S5 and the deployer paths execute"}
    accept_keys = ("complete_pilot_inventory", "valid_structural_zero_accepted", "flagged_zero_prediction_accepted")
    rep["fixtures"]["analyzer_inventory"] = inv | {"ok": all(inv.get(k) == "accepted" for k in accept_keys) and inv["study_mode_without_lock_reaches_lock_branch"] is True and all(str(v).startswith("refused") for k, v in inv.items() if k not in accept_keys + ("study_mode_without_lock_reaches_lock_branch",))}
    print(f"[{time.time()-T0:6.0f}s] (f) inventory fixtures: {rep['fixtures']['analyzer_inventory']['ok']}", flush=True)
    # ---------------- (h) the cost model ----------------
    costs = [json.loads(f.read_text()) for f in cells_dir.glob("costs__*.json")]
    rows = [(c["key_loop"]["nnz_total"] * c["key_loop"]["K"], c["n_tuples"] * c["key_loop"]["K"], c["key_loop"]["seconds"]) for c in costs]
    cellrows = [(x["seconds"], c["N"] * x["K"], x.get("deployer", False)) for c in costs for x in c["cells"]]
    rep["timing"]["validation_cost_records"] = {"n_chains": len(costs), "key_loop": rows, "cell_seconds_mean": float(np.mean([r[0] for r in cellrows])), "cell_seconds_mean_deployer": float(np.mean([r[0] for r in cellrows if r[2]])) if any(r[2] for r in cellrows) else None,
                                                "cell_seconds_mean_nondeployer": float(np.mean([r[0] for r in cellrows if not r[2]])), "peak_rss_gb": max(c["peak_rss_gb"] for c in costs)}
# a real-sized synthetic chain (N = grid N, L = 1024, h = 4) at K = 100: the per-key hash and product rates at production scale, and the peak memory
tN = GRID["N"]; XL = C.ZipfIID(V, 1.0).sample(tN, 1024, np.random.default_rng(21)); t0 = time.time(); chL = S.build_chain(XL, V, "big", 4); build_s = time.time() - t0
incs = {("raw", 1024): chL.incidence(1024, "raw"), ("distinct", 1024): chL.incidence(1024, "distinct"), ("first", 1024): chL.incidence(1024, "first")}
Kt = 100; keys_t = vkeys(Kt, 70000); t1 = time.time(); hash_s = 0.0; prod_s = 0.0
for c0_ in range(0, Kt, GRID["key_chunk"]):
    ta = time.time(); U = S.uniforms_chunk(keys_t[c0_:c0_ + GRID["key_chunk"]], chL.D); cols = {g: (U < C.green_fraction(g, V)).astype(np.float32) for g in (0.25, 0.5)}; Sg = S.gumbel_scores(U).astype(np.float32); del U; hash_s += time.time() - ta
    tb = time.time()
    for m in incs.values():
        for g in cols:
            _ = np.asarray(m @ cols[g])
        _ = np.asarray(m @ Sg)
    prod_s += time.time() - tb
nnz_tot = sum(m.nnz for m in incs.values())
# the per-cell statistics cost: timed at four (nnz, N*K) points per family (L in {1024, 128}; K in {100, 400}) and fitted as seconds = a*nnz + b*N*K + c
stat_points = {"kgw": [], "gumbel": []}
for Kp in (100, 400):
    kp_ = vkeys(Kp, 80000); incPs = {Lp: chL.incidence(Lp, "distinct") for Lp in (1024, 128)}
    cnt = {Lp: np.zeros((tN, Kp), dtype=np.float64) for Lp in incPs}; sm = {Lp: np.zeros((tN, Kp), dtype=np.float64) for Lp in incPs}
    for c0_ in range(0, Kp, GRID["key_chunk"]):            # key chunks, as the runner does: never a |D| x K array (10M tuples x 400 keys would be 32 GB)
        U = S.uniforms_chunk(kp_[c0_:c0_ + GRID["key_chunk"]], chL.D); G = (U < 0.25).astype(np.float32); Sg = S.gumbel_scores(U).astype(np.float32); del U
        for Lp, incP in incPs.items():
            cnt[Lp][:, c0_:c0_ + GRID["key_chunk"]] = np.asarray(incP @ G); sm[Lp][:, c0_:c0_ + GRID["key_chunk"]] = np.asarray(incP @ Sg)
        del G, Sg
    for Lp, incP in incPs.items():
        tc = time.time(); S.kgw_cell_statistics(incP, cnt[Lp], chL, 0.25, GRID["alpha"], V, "independent", np.random.default_rng(1), deployer=(Lp == 1024), B_text=GRID["text_bootstrap_B"]); tk = time.time() - tc
        tc = time.time(); S.gumbel_cell_statistics(incP, sm[Lp], chL, GRID["alpha"], np.random.default_rng(2), deployer=(Lp == 1024), B_text=GRID["text_bootstrap_B"]); tg = time.time() - tc
        stat_points["kgw"].append({"L": Lp, "K": Kp, "nnz": int(incP.nnz), "NK": int(tN * Kp), "seconds": round(tk, 2), "deployer": Lp == 1024}); stat_points["gumbel"].append({"L": Lp, "K": Kp, "nnz": int(incP.nnz), "NK": int(tN * Kp), "seconds": round(tg, 2), "deployer": Lp == 1024})
    del cnt, sm, incPs
def fit_cost(points):
    A_ = np.array([[p_["nnz"], p_["NK"], 1.0] for p_ in points]); y_ = np.array([p_["seconds"] for p_ in points])
    coef, *_ = np.linalg.lstsq(A_, y_, rcond=None); pred_ = A_ @ coef
    return {"a_per_nnz": float(coef[0]), "b_per_NK": float(coef[1]), "c": float(coef[2]), "max_rel_residual": float(np.max(np.abs(pred_ - y_) / y_))}
cost_fit = {fam: fit_cost(pts) for fam, pts in stat_points.items()}
rep["timing"]["real_sized_synthetic_chain"] = {"N": tN, "L": 1024, "h": 4, "V": V, "n_tuples": int(len(chL.D)), "build_seconds": round(build_s, 1), "K": Kt, "hash_seconds": round(hash_s, 2), "hash_seconds_per_tuple_key": hash_s / (len(chL.D) * Kt),
                                               "product_seconds": round(prod_s, 2), "product_seconds_per_nnz_key_scoring": prod_s / (nnz_tot * Kt * 3), "nnz_three_rules_L1024": int(nnz_tot),
                                               "cell_statistics_points": stat_points, "cell_statistics_fit": cost_fit, "peak_rss_gb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30, 2)}
del chL, incs, XL
print(f"[{time.time()-T0:6.0f}s] (h) real-sized chain: |D|={rep['timing']['real_sized_synthetic_chain']['n_tuples']} hash {hash_s:.1f}s products {prod_s:.1f}s; cell statistics points {[(q['L'], q['K'], q['seconds']) for q in stat_points['kgw']]} (kgw) {[(q['L'], q['K'], q['seconds']) for q in stat_points['gumbel']]} (gumbel); fit {cost_fit}", flush=True)

# (h2) the runner itself on a production-sized synthetic chain (R05, compute): run_chain with the production K and the full (rule, L) set of a @1024 cell,
# h = 4, into a fresh scratch directory; its peak RSS and seconds are the runner's, not the validator's, and are compared with the projection of that chain type
if not SKIP_RUN:
    import s2_run as RR
    with tempfile.TemporaryDirectory() as td:
        tdir = pathlib.Path(td) / "probe"; tdir.mkdir(); XL2 = C.ZipfIID(V, 1.0).sample(GRID["N"], 1024, np.random.default_rng(21))
        spec_p = {"tag": "probe_zipf_V128256", "L": [64, 128, 256, 512, 1024]}; grid_p = copy.deepcopy(GRID); grid_p["validation"] = dict(GRID["validation"], tag=spec_p["tag"], L=spec_p["L"], h=[4], K=GRID["K"], K_fixed_h0=GRID["K_fixed_h0"], N=GRID["N"])
        cells_p = RR.expected_cells(grid_p, validation=True); cells_p = [c for c in cells_p if c["h"] == 4]
        rss0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30; t0 = time.time()
        with (tdir / "probe_run.log").open("a") as lg:
            RR.run_chain(spec_p, GRID["validation"]["tokenizer_label"], V, 4, cells_p, grid_p, tdir, "validation", None, GRID_PATH, VK + 90000, lg, None, None, XL2)
        probe_s = time.time() - t0; cost_p = json.loads(next(tdir.glob("costs__*.json")).read_text())
        rep["timing"]["production_scale_runner_probe"] = {"N": GRID["N"], "K": GRID["K"], "L": spec_p["L"], "h": 4, "n_cells": len(cells_p), "seconds": round(probe_s, 1), "n_tuples": cost_p["n_tuples"], "key_loop_seconds": cost_p["key_loop"]["seconds"], "nnz_total": cost_p["key_loop"]["nnz_total"],
                                                          "cell_seconds_sum": round(sum(x["seconds"] for x in cost_p["cells"]), 1), "peak_rss_gb_process": cost_p["peak_rss_gb"], "peak_rss_gb_before_probe": round(rss0, 2), "cell_file_kb_mean": round(float(np.mean([f.stat().st_size for f in tdir.glob("*.json") if not f.name.startswith("costs__")])) / 1024, 1),
                                                          "note": "the runner's own code path at production N and K on a synthetic chain of the largest type; the process peak includes the validator's earlier sections, so the probe's own peak is at most the difference-inclusive value reported"}
        del XL2
    print(f"[{time.time()-T0:6.0f}s] (h2) runner probe: {rep['timing']['production_scale_runner_probe']['seconds']} s, peak RSS {rep['timing']['production_scale_runner_probe']['peak_rss_gb_process']} GB, {rep['timing']['production_scale_runner_probe']['n_cells']} cells", flush=True)

# ---------------- projection and power from INPUTS.json ----------------
inp_path = ROOT / R.INPUTS
if inp_path.exists():
    inp = json.loads(inp_path.read_text()); rep["projection"]["inputs_sha256"] = R.sha(inp_path)
    rt = rep["timing"]["real_sized_synthetic_chain"]; r_hash = rt["hash_seconds_per_tuple_key"]; r_prod = rt["product_seconds_per_nnz_key_scoring"]; cf = rt["cell_statistics_fit"]
    def stat_seconds(fam, nnz, N, K):
        return max(cf[fam]["a_per_nnz"] * nnz + cf[fam]["b_per_NK"] * N * K + cf[fam]["c"], 0.5)
    def project(N, K):
        tot = 0.0; per_chain = {}
        for name, chn in inp["chains"].items():
            if not name.endswith(f"__N{N}"):
                continue
            nnz = sum(c["nnz"] for c in chn["cells"].values())
            hash_t = r_hash * chn["n_tuples"] * K; prod_t = r_prod * nnz * K * 3
            # cell statistics per (rule, L): 2 KGW gammas (independent) + 1 Gumbel, plus the fixed colouring at h = 0 (2 gammas; its colouring is one hypergeometric draw per key)
            stat_t = sum(2 * stat_seconds("kgw", c["nnz"], N, K) + stat_seconds("gumbel", c["nnz"], N, K) + (2 * stat_seconds("kgw", c["nnz"], N, K) if chn["h"] == 0 else 0.0) for c in chn["cells"].values())
            t = chn["build_seconds"] + hash_t + prod_t + stat_t; per_chain[name] = round(t, 1); tot += t
        return tot, per_chain
    rep["projection"]["rates"] = {"hash_seconds_per_tuple_key": r_hash, "product_seconds_per_nnz_key_scoring": r_prod, "cell_statistics_fit": cf, "note": "seconds per cell = a*nnz + b*N*K + c per family, fitted on four timed points of the real-sized synthetic chain (deployer cells at L = 1024 carry the crossed bootstrap)"}
    for N in inp["N_candidates"]:
        for K in (500, 1000):
            tot, per = project(N, K); rep["projection"][f"N{N}_K{K}"] = {"hours": round(tot / 3600, 2), "n_chains": len(per), "largest_chains": sorted(per.items(), key=lambda x: -x[1])[:5], "budget_hours": GRID["budget_hours"], "within_budget": tot / 3600 <= GRID["budget_hours"]}
    # ---------------- (i) power: eligibility by theory share at each candidate N; key-count resolution ----------------
    P = GRID["primary"]; pw = {"note": "a cell is eligible for S1 when mean M >= 30 and the predictor's theory share >= 0.75 at alpha 0.01; the counts below are from the key-free inputs at the realised texts (no key, no level)", "by_N": {}}
    for N in inp["N_candidates"]:
        rows = []
        for name, chn in inp["chains"].items():
            if not name.endswith(f"__N{N}"):
                continue
            tag, tok, hh, _ = name.split("__"); h = int(hh[1:])
            for key, c in chn["cells"].items():
                for g, kg in c["kgw"].items():
                    if kg.get("N_eff", 0) == 0:
                        continue
                    pr = kg["pred"]["0.01"]; rows.append({"tag": tag, "tok": tok, "h": h, "L": c["L"], "rule": c["rule"], "family": "kgw", "gamma": float(g), "mean_M": kg["mean_M"], "sd_pred_pp": 100 * pr["sd_cond"], "theory_share": pr["theory_share"], "sigma_delta": float(np.sqrt(max(kg["rho_bar"], 0))), "reduction": kg["reduction_fixed_vs_indep"],
                                                         "eligible": bool(kg["mean_M"] >= P["min_mean_M"] and pr["theory_share"] >= P["min_theory_share"] and not pr["flags"])})
                gm = c["gumbel"]
                if gm and gm.get("N_eff", 0) > 0:
                    pr = gm["pred"]["0.01"]; rows.append({"tag": tag, "tok": tok, "h": h, "L": c["L"], "rule": c["rule"], "family": "gumbel", "gamma": "na", "mean_M": gm["mean_M"], "sd_pred_pp": 100 * pr["sd_cond"], "theory_share": pr["theory_share"], "sigma_delta": float(np.sqrt(max(gm["rho_bar"], 0))), "reduction": None,
                                                         "eligible": bool(gm["mean_M"] >= P["min_mean_M"] and pr["theory_share"] >= P["min_theory_share"] and not pr["flags"])})
        prim = [r_ for r_ in rows if r_["family"] == "kgw" and r_["gamma"] == P["gamma"] and r_["rule"] in P["rules"] and r_["h"] in P["h"]]
        pw["by_N"][str(N)] = {"primary_candidates": len(prim), "primary_eligible": sum(r_["eligible"] for r_ in prim),
                              "primary_eligible_by_h": {str(h): sum(r_["eligible"] for r_ in prim if r_["h"] == h) for h in P["h"]}, "primary_candidates_by_h": {str(h): sum(1 for r_ in prim if r_["h"] == h) for h in P["h"]},
                              "primary_eligible_by_rule": {ru: sum(r_["eligible"] for r_ in prim if r_["rule"] == ru) for ru in P["rules"]}, "primary_eligible_by_tokenizer": {t: sum(r_["eligible"] for r_ in prim if r_["tok"] == t) for t in GRID["tokenizers"]},
                              "primary_eligible_by_cell": {sp["tag"]: sum(r_["eligible"] for r_ in prim if r_["tag"] == sp["tag"]) for sp in GRID["cells"]},
                              "h0_kgw_g0.25_eligible": sum(r_["eligible"] for r_ in rows if r_["family"] == "kgw" and r_["gamma"] == P["gamma"] and r_["h"] == 0 and r_["rule"] in ("raw", "distinct")),
                              "gumbel_raw_distinct_eligible": sum(r_["eligible"] for r_ in rows if r_["family"] == "gumbel" and r_["rule"] in ("raw", "distinct")), "gumbel_raw_distinct_candidates": sum(1 for r_ in rows if r_["family"] == "gumbel" and r_["rule"] in ("raw", "distinct")),
                              "predicted_sd_pp_primary_eligible_range": [float(min(r_["sd_pred_pp"] for r_ in prim if r_["eligible"])), float(max(r_["sd_pred_pp"] for r_ in prim if r_["eligible"]))] if any(r_["eligible"] for r_ in prim) else None,
                              "theory_share_primary_quantiles": {q: float(np.quantile([r_["theory_share"] for r_ in prim], q)) for q in (0.1, 0.5, 0.9)} if prim else None,
                              "rows": rows}
    dd = {}
    for N in inp["N_candidates"]:
        thr = 1 - np.exp(np.log(C.R2_PBOUND / 2) / GRID["K"]); c_k = c_g = n_k = n_g = 0
        for name, chn in inp["chains"].items():
            if not name.endswith(f"__N{N}"):
                continue
            for c in chn["cells"].values():
                if c["rule"] != "distinct":
                    continue
                for g_, kg in c["kgw"].items():
                    if kg.get("N_eff", 0) > 0:
                        n_k += 1; c_k += int(kg["pred"]["0.01"]["exact_binomial_key_mean_if_distinct"] > thr)
                if c["gumbel"] and c["gumbel"].get("N_eff", 0) > 0:
                    n_g += 1; c_g += int(0.01 > thr)
        dd[str(N)] = {"K": GRID["K"], "mu_threshold": float(thr), "kgw_distinct_cells_flaggable_dead_at_alpha_0.01": c_k, "kgw_distinct_cells": n_k, "gumbel_distinct_cells_flaggable_dead_at_alpha_0.01": c_g, "gumbel_distinct_cells": n_g}
    pw["dead_detector_flaggable_cells"] = dd
    if "production_scale_runner_probe" in rep["timing"]:
        pr_ = rep["timing"]["production_scale_runner_probe"]; proj_big = [t for n, t in project(GRID["N"], GRID["K"])[1].items() if n.endswith("_1024__llama__h4__N%d" % GRID["N"])]
        rep["projection"]["runner_probe_vs_projection"] = {"probe_seconds": pr_["seconds"], "projected_seconds_largest_chain_type": proj_big, "ratio_probe_over_projection": [round(pr_["seconds"] / t, 3) for t in proj_big]}
    pw["key_count"] = {str(K): {"relative_se_of_sd_normal_benchmark": 1 / np.sqrt(2 * (K - 1)), "ratio_interval_halfwidth_approx": 1.96 / np.sqrt(2 * (K - 1)),
                                "ratios_resolvable_inside_band_approx": [P["band"][0] / (1 - 1.96 / np.sqrt(2 * (K - 1))), P["band"][1] / (1 + 1.96 / np.sqrt(2 * (K - 1)))],
                                "S4_S5_tolerance_relative_approx": 4 / np.sqrt(2 * (K - 1)), "quantile_0.99_rank": f"between the {ordinal(int(np.floor(0.01 * K)))} and {ordinal(int(np.floor(0.01 * K)) + 1)} worst key"} for K in (300, 500, 1000)}
    rep["power"] = pw
    print(f"[{time.time()-T0:6.0f}s] (i) power: " + "; ".join(f"N={N}: {v['primary_eligible']}/{v['primary_candidates']} primary eligible" for N, v in pw["by_N"].items()), flush=True)
    print("     projection: " + "; ".join(f"{k}: {v['hours']} h" for k, v in rep["projection"].items() if k.startswith("N")), flush=True)
else:
    rep["projection"]["note"] = "INPUTS.json missing: run s2_inputs.py first"; rep["power"]["note"] = "INPUTS.json missing"

rep["seconds"] = round(time.time() - T0, 1); rep["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30, 2)
rep["summary_ok"] = {k: v.get("ok", v.get("all_ok")) for k, v in list(rep["fixtures"].items()) + [("token_cache", rep["checks"]["token_cache"])] if isinstance(v, dict) and ("ok" in v or "all_ok" in v)}
(ROOT / R.VALIDATION).write_text(json.dumps(rep, indent=1, default=float))
print(f"[{time.time()-T0:6.0f}s] written {R.VALIDATION}; summary {rep['summary_ok']}", flush=True)
