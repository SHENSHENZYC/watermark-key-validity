"""Study 1 input validation (v5, after R03 round 4; before the lock; no study cell is computed). Writes
outputs/study1_v0.3/VALIDATION.json and runs the validation grid into a FRESH directory outputs/study1_v0.3/validation_<utc>/
(retained on disk as a pilot, git-ignored; its per-cell statistics are not study outcomes and are not read here beyond the
execution status, the counts and the cost records; the pilot analysis file is written OUTSIDE the cell inventory).
Sections: (a) laws; (b) the fixed-size sampler and the exact identities with validation keys (a non-integer gamma V case, a
degenerate case, a decomposition of the variance ratio over keys); (c) the two-token variances; (d) the population estimators
against analytic values; (e) the mixture quadrature against Monte Carlo and the exact sigma = 0 limit, and the bivariate normal
against SciPy; (e2) the heterogeneous-overlap (two-block) case: the common-factor predictor fails, the pairwise Gaussian
predictor does not; (f) the exact binomial marginal with 20,000 keys and the calibration of R2 (the KL rule's exact
false-audit probability in the covered-support regime; the normal check as a diagnostic); (f2) the calibration of R3's
known-mean estimator over disjoint 500-key subsamples; (g) the predictor on a light-overlap i.i.d. cell; (h) the two-way
population estimator; (i) colour packing; (j) the M = 0 convention; (k) the key policy; (l) the lock schema: canonical
identity refusals and acceptance under a copied root; (m) cell provenance and slot; (n) the analyzer's inventory refusals
(missing, extra, uniformly stale, a same-provenance wrong-cell copy, a marker mismatch); (o) the support law's analytic limit;
(p) the timed validation run and the pilot execution of the analyzer; (q) the cost table and the projection against the budget.
Usage: .venv/bin/python -u research/study1/s1_validate.py
"""
import datetime, hashlib, json, pathlib, resource, shutil, subprocess, sys, tempfile, time
import numpy as np
from scipy.stats import norm, binom, multivariate_normal
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "tools"))
import s1_core as C
import s1_run as R
import s1_analyze as A
from key_policy import check_keys, KeyPolicyError

GRID_PATH = R.GRID_CANON
GRID = json.loads(pathlib.Path(GRID_PATH).read_text())
OUT = R.OUT; OUT.mkdir(parents=True, exist_ok=True)
STAMP = f"{datetime.datetime.now(datetime.timezone.utc):%Y%m%dT%H%M%SZ}"
VAL_DIR = OUT / f"validation_{STAMP}"
VK = GRID["validation_key_seed_start"]
rep = {"study": R.STUDY, "date_utc": STAMP, "grid": GRID_PATH, "grid_sha256": R.sha(GRID_PATH), "validation_dir": str(VAL_DIR), "checks": {}, "fixtures": {}, "timing": {}, "projection": {},
       "retained_pilot_note": "the validation cells and cost records stay on disk under validation_dir (git-ignored) and the pilot analysis file beside it; the conductor reads only the execution status, the counts and the cost records; the pilots of protocol v0.1 (outputs/study1_v0.1/validation/, production keys 0-499) and v0.2 (outputs/study1_v0.2/) remain on disk as records; validation uses outcome statistics on validation laws, seeds and keys to test the implementation and calibrate the audit rules, and is disclosed as such"}
rng = np.random.default_rng(20261011)
T0 = time.time()


def vkeys(n, offset=0):
    ks = list(range(VK + offset, VK + offset + n)); check_keys(ks, "validation"); return ks


# (a) laws
for spec in GRID["laws"]:
    law = R.make_law(spec); X = law.sample(200, 256, np.random.default_rng(1))
    rep["checks"][f"law_{law.name}"] = {"V": law.V, "sample_shape": list(X.shape), "min": int(X.min()), "max": int(X.max()), "distinct_tokens_in_sample": int(len(np.unique(X))), "top_token_share": float(np.mean(X == 0))}
# (b) fixed sampler exact count; identities with validation keys; non-integer gamma V; decomposition; degenerate
law = C.ZipfIID(V=6, s=0.5); ch = C.Chain(law, h=1, N=400, L_max=64, seed=1)
cols = C.colour_fixed(ch, vkeys(300), 0.5, 6)
per = np.zeros((ch.n_ctx, 300)); np.add.at(per, ch.D_ctx, cols.astype(float)); j = np.bincount(ch.D_ctx, minlength=ch.n_ctx)
rep["checks"]["fixed_sampler_exact_count"] = {"contexts_fully_queried": int((j == 6).sum()), "all_equal_m": bool((per[j == 6] == 3).all()), "marginal_green": float(cols.mean())}
def identity_check(V, gamma, h, N, L, seed, K):
    law = C.ZipfIID(V=V, s=1.0); ch = C.Chain(law, h=h, N=N, L_max=L, seed=seed); inc = ch.incidence(L, "distinct")
    pe = C.population_estimates(inc, ch, gamma, V, "independent", rng); idq = pe["identity_q"]; keep = pe["keep"]; M = pe["M"]; out = {"g": idq["g"], "m": idq["m"], "degenerate": idq["degenerate"], "K": K}
    for name, fn in (("fixed", lambda ks: C.colour_fixed(ch, ks, gamma, V)), ("indep", lambda ks: C.colour_independent(ch, ks, gamma, V))):
        c = fn(vkeys(K)); counts = np.asarray(inc @ c.astype(float)); q = (counts[keep] / M[keep][:, None]).mean(axis=0)
        out[name] = {"observed_var": float(q.var(ddof=1)), "identity": idq["var_" + name], "ratio": float(q.var(ddof=1) / idq["var_" + name]) if idq["var_" + name] > 0 else None, "marginal_green": float(c.mean())}
    out["observed_ratio_fixed_over_indep"] = out["fixed"]["observed_var"] / out["indep"]["observed_var"] if out["indep"]["observed_var"] > 0 else None; out["exact_ratio_formula"] = idq["exact_ratio_formula"]
    return out
rep["checks"]["identity_V4_gamma0.5"] = identity_check(4, 0.5, 0, 200, 8, 2, 20000)
rep["checks"]["identity_V10_gamma0.25_noninteger"] = identity_check(10, 0.25, 1, 300, 32, 11, 20000)     # m = 2, g = 0.2 (F2)
law = C.ZipfIID(V=10, s=1.0); ch10 = C.Chain(law, h=1, N=300, L_max=32, seed=11); inc10 = ch10.incidence(32, "distinct")
pe10 = C.population_estimates(inc10, ch10, 0.25, 10, "independent", rng); w = pe10["wq"]; ident = 0.2 * 0.8 * float((w ** 2).sum()); dec = {}
for name, keys in (("validation_20000", vkeys(20000)), ("validation_200000", vkeys(200000)), ("random_20000", [int(x) for x in np.random.default_rng(5).integers(VK, 2 ** 62, 20000)])):
    cols = C.colour_independent(ch10, keys, 0.25, 10).astype(float); q = (np.asarray(inc10 @ cols)[pe10["keep"]] / pe10["M"][pe10["keep"]][:, None]).mean(axis=0); Cc = np.cov(cols)
    dec[name] = {"var_ratio": float(q.var(ddof=1) / ident), "diagonal_part": float((w ** 2 * np.diag(Cc)).sum() / ident), "off_diagonal_part": float((w @ Cc @ w - (w ** 2 * np.diag(Cc)).sum()) / ident), "K": len(keys)}
ids = ch10.D[:2]; U = np.stack([C.uniforms(int(k), ids) for k in range(VK, VK + 200000)]); G = (U < 0.25).astype(float)
dec["hash_pair_200000_keys"] = {"green_fractions": [float(x) for x in G.mean(axis=0)], "correlation": float(np.corrcoef(G.T)[0, 1]), "se_of_correlation": float(1 / np.sqrt(200000))}
rep["checks"]["identity_ratio_decomposition_V10"] = dec
law = C.TwoToken(0.9); ch = C.Chain(law, 0, N=200, L_max=16, seed=1); inc = ch.incidence(16, "raw"); pe = C.population_estimates(inc, ch, 0.25, 2, "fixed", rng)
rep["checks"]["degenerate_V2_gamma0.25"] = {"degenerate_flag": pe["identity_q"]["degenerate"], "m": pe["identity_q"]["m"], "var_fixed": pe["identity_q"]["var_fixed"]}
# (c) two-token variances (reviewer's 0 and 0.08 are population values; the realised-weight values carry a finite-text term)
for h in (0, 1):
    ch = C.Chain(law, h, N=2000, L_max=400, seed=3); inc = ch.incidence(400, "raw"); pe = C.population_estimates(inc, ch, 0.5, 2, "fixed", rng)
    rep["checks"][f"twotoken_h{h}_var_fixed_realised"] = pe["identity_q"]["var_fixed"]
# (d) population estimators against analytic values
law = C.ZipfIID(V=1000, s=1.0); ch0 = C.Chain(law, h=0, N=2000, L_max=256, seed=5); ch1 = C.Chain(law, h=1, N=2000, L_max=256, seed=5)
d = {}
for L in (64, 256):
    inc = ch0.incidence(L, "raw"); pe = C.population_estimates(inc, ch0, 0.5, 1000, "independent", rng)
    d[f"h0_L{L}"] = {"rho_bar": pe["rho_bar"], "se": pe["rho_bar_boot_se"], "population": L * 0.25 * law.collision_unigram / 0.25, "A_between": pe["A_q_between"], "A_between_se": pe["A_q_between_boot_se"], "C_0": law.collision_unigram, "realised_var_zbar": pe["identity_z"]["var_indep"], "floor_removed": pe["mean_var_text_z"] / pe["N_eff"]}
inc = ch1.incidence(256, "raw"); pe = C.population_estimates(inc, ch1, 0.5, 1000, "independent", rng)
d["h1_L256"] = {"A_between": pe["A_q_between"], "A_between_se": pe["A_q_between_boot_se"], "C_1": law.collision_h(1), "rho_bar": pe["rho_bar"], "se": pe["rho_bar_boot_se"], "population": 255 * law.collision_h(1)}
rep["checks"]["population_estimators"] = d
# (e) the closed-form mixture moments against Monte Carlo (3 million draws), against an independent adaptive quadrature at ordinary variances,
#     and against the exact sigma = 0 limit; the flags on invalid sigma2
from scipy.integrate import quad as _quad
def quad_mixture(mu, var, alpha, N_eff, sig2):
    z_a = norm.isf(alpha); sd = np.sqrt(var); sg = np.sqrt(sig2); lo, hi = mu - 12 * sd, mu + 12 * sd
    pts = [z_a + k * sg for k in (-8, -4, -2, 0, 2, 4, 8) if lo < z_a + k * sg < hi]
    m1 = _quad(lambda d: norm.sf((z_a - d) / sg) * norm.pdf((d - mu) / sd) / sd, lo, hi, points=pts or None, limit=800, epsabs=1e-15, epsrel=1e-11)[0]
    m2 = _quad(lambda d: norm.sf((z_a - d) / sg) ** 2 * norm.pdf((d - mu) / sd) / sd, lo, hi, points=pts or None, limit=800, epsabs=1e-15, epsrel=1e-11)[0]
    return {"mean": m1, "sd_pop": float(np.sqrt(max(m2 - m1 ** 2, 0))), "floor": (m1 - m2) / N_eff}
qq = {}
for mu, var, sig2 in ((0.0, 1.0, 0.0), (0.0, 1.0, 1e-8), (0.0, 1.0, 1e-6), (0.0, 1.0, 1e-3), (0.0, 0.25, 1.0), (-0.8, 1.0, 0.85), (0.0, 0.01, 0.6), (0.3, 0.0, 1.0)):
    p = C.mixture_predictor(mu, var, 0.01, 4000, sig2); dl = mu + np.sqrt(var) * rng.standard_normal(3_000_000)
    lv = norm.sf((norm.isf(0.01) - dl) / np.sqrt(sig2)) if sig2 > 0 else (dl > norm.isf(0.01)).astype(float)
    e = {"closed_form": {"mean": p["mean_level"], "sd_pop": p["sd_pop"], "floor": p["floor"], "flags": p["flags"]}, "monte_carlo": {"mean": float(lv.mean()), "sd_pop": float(lv.std()), "floor": float((lv * (1 - lv)).mean() / 4000)}}
    if var > 0 and sig2 >= 1e-3:
        e["independent_quadrature"] = quad_mixture(mu, var, 0.01, 4000, sig2)
    qq[f"mu{mu}_var{var}_sig2{sig2}"] = e
pz = norm.sf(norm.isf(0.01)); qq["sigma0_analytic_limit"] = {"mean": float(pz), "sd_pop": float(np.sqrt(pz * (1 - pz))), "floor": 0.0}
qq["negative_sigma2_flagged"] = C.mixture_predictor(0.0, 1.0, 0.01, 4000, -0.5, tol=1e-9)["flags"]; qq["nonfinite_sigma2_flagged"] = C.mixture_predictor(0.0, 1.0, 0.01, 4000, float("nan"))["flags"]
rep["checks"]["mixture_moments"] = qq
a = rng.normal(0, 2, 300); b = rng.normal(0, 2, 300); r = np.concatenate([rng.uniform(-0.999, 0.999, 292), [0.9999, -0.9999, 0.0, 0.5, 0.95, -0.95, 0.999999, 0.3]])
ref = np.array([multivariate_normal.cdf([-x, -y], mean=[0, 0], cov=[[1, rr], [rr, 1]], allow_singular=True) for x, y, rr in zip(a, b, r)])
rep["checks"]["bivariate_normal"] = {"max_abs_error_vs_scipy_300_cases": float(np.abs(C.bvn_upper(a, b, r) - ref).max()), "rho_plus1": [float(C.bvn_upper(1.0, 2.0, 1.0)), float(norm.sf(2.0))], "rho_minus1": [float(C.bvn_upper(-1.0, -1.0, -1.0)), float(1 - 2 * norm.cdf(-1.0))]}
# (e2) the heterogeneous-overlap case: two blocks of texts on disjoint supports (the reviewer's two-factor structure)
class TwoBlock:
    def __init__(self, V, s):
        self.V, self.s, self.name = V, s, "twoblock"
    def sample(self, N, L, rng_):
        X = rng_.integers(0, self.s, size=(N, L)).astype(np.int32); X[N // 2:] += 500; return X
    def collision_h(self, h):
        return None
chb = C.Chain(TwoBlock(1000, 200), 0, N=400, L_max=2000, seed=3); incb = chb.incidence(2000, "distinct")
peb = C.population_estimates(incb, chb, 0.5, 1000, "independent", rng)
pair = C.pairwise_gaussian_predictor(peb, chb, 0.5, 1000, "independent", (0.01,), rng); mix = C.mixture_predictor(peb["mu_delta"], peb["rho_bar"], 0.01, peb["N_eff"], peb["sigma_model2"], peb["sigma_tol"])
colsb = C.colour_independent(chb, vkeys(20000), 0.5, 1000); zb = C.z_scores(np.asarray(incb @ colsb.astype(float)), peb["M"], 0.5); akb = (zb > norm.isf(0.01)).mean(axis=0)
rep["checks"]["two_block_heterogeneous_overlap"] = {"observed_sd_20000_keys": float(akb.std(ddof=1)), "common_factor_sd": mix["sd_cond"], "pairwise_gaussian_sd": pair["by_alpha"]["0.01"]["sd_cond"],
                                                     "ratio_obs_over_common_factor": float(akb.std(ddof=1) / mix["sd_cond"]), "ratio_obs_over_pairwise": float(akb.std(ddof=1) / pair["by_alpha"]["0.01"]["sd_cond"]), "pairwise_replicate_sd": pair["by_alpha"]["0.01"]["sd_cond_replicate"], "pairwise_subsample_sd_difference": pair["by_alpha"]["0.01"]["subsample_sd_difference"],
                                                     "rho_bar": peb["rho_bar"], "sigma2_model": peb["sigma_model2"], "theory_share_common_factor": mix["theory_share"], "heterogeneity": pair["heterogeneity"],
                                                     "exact_bernoulli_sd_if_normal": float(np.sqrt(0.01 * 0.99 / 2))}
# (f) exact binomial marginal with 20,000 keys; the R2 KL rule's calibration; the normal check as a diagnostic
law = C.ZipfIID(200, 1.0); ch = C.Chain(law, 0, N=1000, L_max=32, seed=99261017); inc = ch.incidence(32, "distinct"); M = np.asarray(inc.sum(axis=1)).ravel()
f = {}
for gamma in (0.25, 0.5):
    cols = C.colour_independent(ch, vkeys(20000), gamma, 200); counts = np.asarray(inc @ cols.astype(float)); g = C.green_fraction(gamma, 200)
    for alpha in (0.05, 0.01, 0.001):
        a_k = (C.z_scores(counts, M, gamma) > norm.isf(alpha)).mean(axis=0); ex = C.exact_marginal_level_distinct_independent(M, g, gamma, alpha)
        se = a_k.std(ddof=1) / np.sqrt(len(a_k)); f3 = f5 = fkl = 0; S = 400
        for _ in range(S):
            sub = a_k[rng.choice(len(a_k), 500, replace=False)]; dse = abs(sub.mean() - ex) / (sub.std(ddof=1) / np.sqrt(500)); f3 += dse > 3; f5 += dse > 5
            fkl += C.kl_chernoff_pbound(float(sub.mean()), ex, 500) < C.R2_PBOUND
        f[f"gamma{gamma}_alpha{alpha}"] = {"key_mean_20000_keys": float(a_k.mean()), "exact": ex, "dev_over_se": float((a_k.mean() - ex) / se), "skew_of_per_key_level": float(((a_k - a_k.mean()) ** 3).mean() / a_k.std() ** 3),
                                           "normal_check_chance_failure_3se_K500": f3 / S, "normal_check_chance_failure_5se_K500": f5 / S, "kl_rule_chance_flag_K500": fkl / S}
i = int(np.argmax(M)); G = counts[i]
f["per_text_binomial_gamma0.5"] = {"M": int(M[i]), "mean_G": float(G.mean()), "M_g": float(M[i] * 0.5), "var_G": float(G.var()), "M_g_1mg": float(M[i] * 0.25)}
# the covered-support regime (every text the same 50 tokens, so the per-key level is Bernoulli(p)): the KL rule's exact false-audit probability by enumeration
cov = {}
for gamma in (0.5, 0.25):
    thr = gamma * 50 + norm.isf(0.01) * np.sqrt(50 * gamma * (1 - gamma)); p = float(binom.sf(np.floor(thr), 50, C.green_fraction(gamma, 1000)))
    for K in (500, 2000):
        x = np.arange(K + 1); pm = binom.pmf(x, K, p); flagged = np.array([C.kl_chernoff_pbound(float(k / K), p, K) < C.R2_PBOUND for k in x])
        cov[f"gamma{gamma}_K{K}"] = {"p_per_key": p, "exact_false_audit_probability_kl_rule": float(pm[flagged].sum()), "P_no_rejecting_key": float((1 - p) ** K),
                                     "flag_region": [int(x[flagged].min()) if flagged.any() else None, int(x[flagged & (x < K * p)].max()) if (flagged & (x < K * p)).any() else None]}
f["covered_support_regime"] = cov
# the reviewer's round-3 counterexample: Bernoulli levels at the mean where the one-sided bound was tight on the lower tail; the two-sided rule must give <= 1e-6
K = 500; mu_ce = 1 - (0.999e-6) ** (1 / K); x = np.arange(K + 1); pm = binom.pmf(x, K, mu_ce); flagged = np.array([C.kl_chernoff_pbound(float(k / K), mu_ce, K) < C.R2_PBOUND for k in x])
f["two_sided_counterexample_K500"] = {"mu": float(mu_ce), "lower_tail_flagged_probability": float(pm[flagged & (x < K * mu_ce)].sum()), "upper_tail_flagged_probability": float(pm[flagged & (x > K * mu_ce)].sum()), "total": float(pm[flagged].sum()), "bound": C.R2_PBOUND}
# power of the KL rule: the smallest flagged over-rejection and the largest flagged under-rejection of the key-mean, by exact key-mean and K
# (None: no deviation on that side can be flagged at that K, because even a key-mean of 0 has the two-sided bound 2 (1 - mu)^K above the threshold; R03 round 4, F21)
pw = {}
for mu in (0.05, 0.01, 0.001):
    for K in (500, 2000):
        ks = np.linspace(0, 0.5, 50001); pb = np.array([C.kl_chernoff_pbound(float(k), mu, K) for k in ks])
        up = (ks > mu) & (pb < C.R2_PBOUND); dn = (ks < mu) & (pb < C.R2_PBOUND)
        pw[f"mu{mu}_K{K}"] = {"flagged_above": float(ks[up].min()) if up.any() else None, "flagged_below": float(ks[dn].max()) if dn.any() else None, "two_sided_bound_at_zero": C.kl_chernoff_pbound(0.0, mu, K),
                              "dead_detector_flaggable": bool(C.kl_chernoff_pbound(0.0, mu, K) < C.R2_PBOUND)}
# the smallest exact key-mean at which a dead detector (key-mean 0) is flagged: 2 (1 - mu)^K < 1e-6
f["dead_detector_min_mu"] = {f"K{K}": float(1 - (C.R2_PBOUND / 2) ** (1.0 / K)) for K in (500, 2000)}
f["kl_rule_power"] = pw
rep["checks"]["binomial_marginal_and_R2_calibration"] = f
# (f2) R3's known-mean estimator over 400 disjoint 500-key subsamples (V = 10, h = 1, both colourings): standardised deviations and the 95% coverage diagnostic
f2 = {}
for colouring, fn in (("independent", lambda ks: C.colour_independent(ch10, ks, 0.25, 10)), ("fixed", lambda ks: C.colour_fixed(ch10, ks, 0.25, 10))):
    allk = vkeys(200000); devs = []; covers = 0
    for s_ in range(400):
        ks_ = allk[s_ * 500:(s_ + 1) * 500]; cols = fn(ks_); counts = np.asarray(inc10 @ cols.astype(float))
        st = C.cell_statistics(inc10, counts, ch10, 0.25, (0.05,), 10, colouring, np.random.default_rng(s_))
        q = st["q_hat"]; devs.append((q["var_known_mean"] - q["exact_var_own_colouring"]) / q["var_known_mean_se"]); covers += q["var_boot_ci95"][0] <= q["exact_var_own_colouring"] <= q["var_boot_ci95"][1]
    devs = np.array(devs)
    f2[colouring] = {"n_subsamples": 400, "K": 500, "max_abs_dev_over_se": float(np.abs(devs).max()), "share_beyond_3": float((np.abs(devs) > 3).mean()), "share_beyond_4": float((np.abs(devs) > 4).mean()), "share_beyond_6": float((np.abs(devs) > 6).mean()),
                     "mean_dev": float(devs.mean()), "sd_dev": float(devs.std(ddof=1)), "coverage_of_nominal_95_interval": covers / 400, "se_method": st["q_hat"]["se_method"]}
# the full-coverage fixed-colouring structural zero (V = 10, four identical retained sets) and the two-token constant-estimate case
law = C.ZipfIID(V=10, s=0.0); chf = C.Chain(law, 0, N=4, L_max=400, seed=2); incf = chf.incidence(400, "distinct")
colsf = C.colour_fixed(chf, vkeys(300), 0.5, 10); stf = C.cell_statistics(incf, np.asarray(incf @ colsf.astype(float)), chf, 0.5, (0.01,), 10, "fixed", rng)
f2["full_coverage_fixed_V10"] = {"structural_zero": stf["q_hat"]["structural_zero"], "exact": stf["q_hat"]["exact_var_own_colouring"], "observed_var_known_mean": stf["q_hat"]["var_known_mean"], "sigma2_used": stf["levels"]["0.01"]["pred_first_order"]["sigma2"], "pred_flags": stf["levels"]["0.01"]["pred_first_order"]["flags"]}
cht = C.Chain(C.TwoToken(0.9), 0, N=300, L_max=64, seed=4); inct = cht.incidence(64, "raw"); colst = C.colour_fixed(cht, vkeys(200), 0.5, 2); stt = C.cell_statistics(inct, np.asarray(inct @ colst.astype(float)), cht, 0.5, (0.01,), 2, "fixed", rng)
stt["g"] = 0.5; f2["two_token_h0_fixed_constant_estimate"] = {"observed_var_known_mean": stt["q_hat"]["var_known_mean"], "exact": stt["q_hat"]["exact_var_own_colouring"], "se": stt["q_hat"]["var_known_mean_se"], "se_method": stt["q_hat"]["se_method"], "observed_sample_constancy": stt["q_hat"]["observed_sample_constancy"], "r3_decision_gross": A.r3_check(stt)["gross"]}
# the reviewer's round-4 illustration (K = 4, four all-red independent-colour realisations, outside the grid): the exact fourth-moment SE must NOT be overridden by observed constancy
cha = C.Chain(C.ZipfIID(4, 0.0), 0, N=4, L_max=4, seed=5); inca = cha.incidence(4, "raw")
sta = C.cell_statistics(inca, np.zeros((4, 4)), cha, 0.25, (0.01,), 4, "independent", np.random.default_rng(0)); sta["g"] = C.green_fraction(0.25, 4)
f2["reviewer_round4_F22_all_red_K4"] = {"observed_sample_constancy": sta["q_hat"]["observed_sample_constancy"], "se": sta["q_hat"]["var_known_mean_se"], "se_method": sta["q_hat"]["se_method"], "observed": sta["q_hat"]["var_known_mean"], "exact": sta["q_hat"]["exact_var_own_colouring"], "gross": A.r3_check(sta)["gross"]}
# the reviewer's round-3 F17 fixture through the full path (N = 20, L = 64, seed 3, 2,000 validation keys, rng 9), then the analyzer's actual decision
chr_ = C.Chain(C.TwoToken(0.9), 0, N=20, L_max=64, seed=3); incr = chr_.incidence(64, "raw"); colsr = C.colour_fixed(chr_, vkeys(2000), 0.5, 2)
str_ = C.cell_statistics(incr, np.asarray(incr @ colsr.astype(float)), chr_, 0.5, (0.01,), 2, "fixed", np.random.default_rng(9)); str_["g"] = 0.5; er = A.r3_check(str_)
f2["reviewer_round3_F17_fixture"] = {"abs_diff": er["abs_diff"], "se": er["se"], "se_method": er["se_method"], "tolerance": er["tolerance"], "observed_sample_constancy": er["observed_sample_constancy"], "gross": er["gross"]}
# the analyzer's R3 decision on synthetic cells: an exactly-zero SE with equal values; a roundoff-sized positive SE with a roundoff-sized difference; 5 and 7 SE deviations; structural zeros
def syn(obs, exact, se, sz=False, tol=1e-10):
    return {"q_hat": {"var_known_mean": obs, "var_known_mean_se": se, "se_method": "synthetic", "exact_var_own_colouring": exact, "structural_zero": sz, "var_boot_ci95": [0.0, 1.0], "r3_tolerance": tol, "observed_sample_constancy": se == 0.0}, "g": 0.5, "identity_q": {"A": 1.0}}
f2["r3_decision_fixtures"] = {"zero_se_equal": A.r3_check(syn(1e-4, 1e-4, 0.0))["gross"], "tiny_se_roundoff_diff": A.r3_check(syn(1e-4 + 3e-17, 1e-4, 3.6e-20))["gross"], "five_se": A.r3_check(syn(1e-4 + 5e-6, 1e-4, 1e-6))["gross"],
                               "seven_se": A.r3_check(syn(1e-4 + 7e-6, 1e-4, 1e-6))["gross"], "structural_zero_negligible": A.r3_check(syn(1e-18, 0.0, 0.0, True))["gross"], "structural_zero_material": A.r3_check(syn(1e-6, 0.0, 0.0, True))["gross"],
                               "expected": {"zero_se_equal": False, "tiny_se_roundoff_diff": False, "five_se": False, "seven_se": True, "structural_zero_negligible": False, "structural_zero_material": True}}
rep["checks"]["R3_calibration"] = f2
# (g) the predictor on a light-overlap i.i.d. cell (independent, distinct, Zipf V = 5,000, h = 1), 3,000 validation keys
law = C.ZipfIID(V=5000, s=1.0); ch = C.Chain(law, h=1, N=1500, L_max=400, seed=6); inc = ch.incidence(400, "distinct")
cols = C.colour_independent(ch, vkeys(3000), 0.5, 5000); counts = np.asarray(inc @ cols.astype(float))
st = C.cell_statistics(inc, counts, ch, 0.5, (0.01, 0.05), 5000, "independent", np.random.default_rng(1))
rep["checks"]["predictor_light_overlap_cell"] = {a: {"sd_obs": st["levels"][a]["sd_obs_conditional"], "sd_obs_ci95": st["levels"][a]["sd_obs_boot_ci95"], "sd_pred_common_factor": st["levels"][a]["pred_first_order"]["sd_cond"], "theory_share": st["levels"][a]["pred_first_order"]["theory_share"],
                                                     "ratio": st["levels"][a]["ratio_obs_over_pred"], "ratio_ci95": st["levels"][a]["ratio_boot_ci95"], "sd_pred_unit_sigma": st["levels"][a]["pred_unit_sigma"]["sd_cond"], "sd_linear_pop": st["levels"][a]["pred_first_order"]["sd_linear_pop"],
                                                     "sd_pred_pairwise": st["levels"][a]["pred_pairwise_gaussian"]["sd_cond"], "sd_pred_pairwise_replicate": st["levels"][a]["pred_pairwise_gaussian"]["sd_cond_replicate"], "key_mean": st["levels"][a]["key_mean_level"], "pred_mean": st["levels"][a]["pred_first_order"]["mean_level"], "exact_binomial_mean": st["levels"][a]["exact_marginal_if_indep_distinct"],
                                                     "var_pop_twoway": st["levels"][a]["population_est"]["var_pop_signed"], "var_pop_twoway_se": st["levels"][a]["population_est"]["var_pop_boot_se"], "var_pop_mixture": st["levels"][a]["pred_first_order"]["var_pop"]} for a in ("0.01", "0.05")}
rep["checks"]["predictor_light_overlap_cell"].update({"sigma2_model": st["population"]["sigma_model2"], "sigma2_observed": st["z_var_within_key"]["mean_over_keys"], "mean_M": st["mean_M"], "heterogeneity": st["covariance_heterogeneity"]})
# (h) two-way population estimator
p_k = np.clip(0.02 + 0.01 * np.random.default_rng(2).standard_normal(300), 0.001, 0.2); Y = (np.random.default_rng(3).random((2000, 300)) < p_k[None, :]).astype(float)
s_k2, ms_e, v = C.twoway_population_variance(Y); vb = C.twoway_bootstrap(Y, np.random.default_rng(4))
Y0 = np.zeros((100, 50)); Y0[:10, :] = 1.0
rep["checks"]["twoway_estimator"] = {"synthetic": {"var_pop": v, "true_var_pk": float(p_k.var(ddof=1)), "naive_s_K2": s_k2, "boot_se": float(vb.std(ddof=1)), "boot_mean": float(vb.mean())}, "key_independent_table": list(C.twoway_population_variance(Y0))}
# (i) colour packing
law = C.ZipfIID(V=50, s=1.0); ch = C.Chain(law, h=1, N=100, L_max=32, seed=9); pk = {}
try:
    C.PackedColours(ch, vkeys(60), 0.5, "independent", 50, chunk=50); pk["chunk50"] = "accepted (WRONG)"
except ValueError as e:
    pk["chunk50"] = f"refused: {e}"
for colouring, fn in (("independent", C.colour_independent), ("fixed", C.colour_fixed)):
    P = C.PackedColours(ch, vkeys(60), 0.5, colouring, 50, chunk=48); direct = fn(ch, vkeys(60), 0.5, 50)
    pk[f"chunk48_{colouring}_identical_K60"] = bool(all((P.chunk_cols(c0) == direct[:, c0:c0 + 48]).all() for c0 in range(0, 60, 48)))
rep["fixtures"]["packing"] = pk
# (j) M = 0 convention
ch = C.Chain(C.ZipfIID(100, 1.0), h=1, N=50, L_max=4, seed=3); inc = ch.incidence(1, "raw")
st0 = C.cell_statistics(inc, np.zeros((50, 8)), ch, 0.5, (0.01,), 100, "independent", rng)
inc = ch.incidence(4, "raw"); cols = C.colour_independent(ch, vkeys(8), 0.5, 100); st1 = C.cell_statistics(inc, np.asarray(inc @ cols.astype(float)), ch, 0.5, (0.01,), 100, "independent", rng)
rep["fixtures"]["M0_convention"] = {"all_M0_flag": st0.get("flag"), "all_M0_N_eff": st0["N_eff"], "normal_cell_unconditional_equals_keymean_times_share": bool(abs(st1["levels"]["0.01"]["unconditional_rate"] - st1["levels"]["0.01"]["key_mean_level"] * st1["N_eff"] / st1["N"]) < 1e-12)}
# (k) key policy
kp = {}
for name, ks, purpose in (("reserved_touch", range(29990, 30010), "study1"), ("study1_ok", range(20000, 22000), "study1"), ("study1_outside", range(0, 500), "study1"), ("validation_low", range(0, 10), "validation"), ("validation_ok", range(1_000_000, 1_020_000), "validation")):
    try:
        check_keys(ks, purpose); kp[name] = "accepted"
    except KeyPolicyError as e:
        kp[name] = f"refused: {e}"
rep["fixtures"]["key_policy"] = kp
# (l) lock schema under a copied root with the canonical relative paths (the real code and grid copied; stand-ins for the protocol, the validation record and the resolution memo)
tmp = pathlib.Path(tempfile.mkdtemp(prefix="s1lock_")); lk = {}
for f_ in R.CODE_FILES + (R.GRID_CANON,):
    (tmp / f_).parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(f_, tmp / f_)
for f_, text in ((R.PROTOCOL, "fixture protocol v0.3\n"), (R.VALIDATION, "{}\n"), (R.RESOLUTION, "AGREE (fixture)\n")):
    (tmp / f_).parent.mkdir(parents=True, exist_ok=True); (tmp / f_).write_text(text)
full = {"study": R.STUDY, "date": "2026-10-10", "approved_by": "Yichen", "before_outcomes": True, "final": False, "grid": R.GRID_CANON, "protocol": R.PROTOCOL, "validation": R.VALIDATION,
        "hashes": {f_: R.sha(tmp / f_) for f_ in R.PINNED}, "review": {"checkpoint": R.CHECKPOINT, "resolution": R.RESOLUTION, "sha256": R.sha(tmp / R.RESOLUTION)},
        "keys": {"production_start": GRID["key_seed_start"], "K": GRID["K"], "K_fixed_core": GRID["K_fixed_core"]}}
def try_lock(name, lock, grid_path=R.GRID_CANON):
    p = tmp / f"{name}.json"; p.write_text(json.dumps(lock))
    try:
        R.verify_lock(p, grid_path, root=tmp); lk[name] = "accepted"
    except R.LockError as e:
        lk[name] = f"refused: {e}"
try_lock("complete_canonical", full)
try_lock("reviewer_round2_fixture_protocol_is_grid_review_is_R02_date_junk", dict(full, date="not-an-ISO-date", protocol=R.GRID_CANON, validation=R.GRID_CANON, hashes={k: v for k, v in full["hashes"].items() if k in R.CODE_FILES + (R.GRID_CANON,)}, review={"checkpoint": "R02", "resolution": "research/reviews/R02_data-verdict/RESOLUTION.md", "sha256": R.sha("research/reviews/R02_data-verdict/RESOLUTION.md")}))
try_lock("grid_only", {"hashes": {R.GRID_CANON: full["hashes"][R.GRID_CANON]}, "grid": R.GRID_CANON, "before_outcomes": True, "final": False})
try_lock("missing_approved_by", {k: v for k, v in full.items() if k != "approved_by"})
try_lock("final_true", dict(full, final=True))
try_lock("date_not_iso", dict(full, date="not-an-ISO-date"))
try_lock("date_before_protocol", dict(full, date="2026-10-01"))
try_lock("protocol_path_is_grid", dict(full, protocol=R.GRID_CANON))
try_lock("validation_path_noncanonical", dict(full, validation="outputs/study1_v0.2/VALIDATION.json"))
try_lock("review_checkpoint_R02", dict(full, review=dict(full["review"], checkpoint="R02")))
try_lock("review_resolution_R02_path", dict(full, review={"checkpoint": "R03", "resolution": "research/reviews/R02_data-verdict/RESOLUTION.md", "sha256": R.sha("research/reviews/R02_data-verdict/RESOLUTION.md")}))
try_lock("tampered_hash", dict(full, hashes=dict(full["hashes"], **{"research/study1/s1_core.py": "0" * 64})))
try_lock("digest_not_hex", dict(full, hashes=dict(full["hashes"], **{"research/study1/s1_core.py": "0" * 63 + "g"})))
try_lock("missing_code_digest", dict(full, hashes={k: v for k, v in full["hashes"].items() if k != "tools/key_policy.py"}))
try_lock("extra_hash_entry", dict(full, hashes=dict(full["hashes"], **{"research/study1/grid_v0.2.json": "0" * 64})))
try_lock("wrong_study", dict(full, study="study1_v0.2"))
try_lock("wrong_grid_argument", full, grid_path="research/study1/grid_v0.2.json")
try_lock("keys_mismatch", dict(full, keys=dict(full["keys"], K=300)))
rep["fixtures"]["lock_schema"] = lk
# (m) cell provenance and slot
cells_exp = R.expected_cells(GRID, GRID["validation_laws"]); c0 = cells_exp[0]; c1 = [c for c in cells_exp if c["name"] == c0["name"] and c["K"] == c0["K"] and c["file"] != c0["file"]][0]
prov = R.provenance("validation", None, GRID_PATH, R.text_seed_for(c0["name"], GRID["validation_seed_base"]), VK, c0["K"], GRID["validation_seed_base"], R.slot_of(c0))
body = {"provenance": dict(prov, written_utc="x"), "law": c0["law"], "h": c0["h"], "L": c0["L"], "rule": c0["rule"], "colouring": c0["colouring"], "gamma": c0["gamma"], "K": c0["K"], "N": GRID["N"]}
cp = tmp / "cell.json"; cp.write_text(json.dumps(body)); pv = {"matching_reusable": R.cell_reusable(cp, prov), "absent_reusable": R.cell_reusable(tmp / "none.json", prov)}
for name, prov2, body2 in (("foreign_provenance", dict(prov, grid_sha256="0" * 64), body), ("same_provenance_other_slot", R.provenance("validation", None, GRID_PATH, prov["text_seed"], VK, c1["K"], GRID["validation_seed_base"], R.slot_of(c1)), body),
                           ("body_disagrees_with_slot", prov, dict(body, h=c0["h"] + 1)), ("role_only_mutation", prov, dict(body, law=dict(c0["law"], role="illustration" if c0["law"].get("role", "core") == "core" else "core")))):
    cp2 = tmp / f"{name}.json"; cp2.write_text(json.dumps(body2))
    try:
        R.cell_reusable(cp2, prov2); pv[name] = "reused (WRONG)"
    except R.ProvenanceError as e:
        pv[name] = f"refused: {e}"
rep["fixtures"]["provenance"] = pv
# (n) analyzer inventory refusals: missing, extra, uniformly stale (the reviewer's round-2 fixture, in pilot mode), and after the run a same-provenance copy and a marker mismatch
tiny = dict(GRID); tiny["laws"] = [GRID["laws"][0]]; tiny["validation_laws"] = [GRID["laws"][0]]
exp = R.expected_cells(tiny); inv = tmp / "inv"; inv.mkdir(); iv = {}
for c in exp[1:]:
    (inv / c["file"]).write_text("{}")
try:
    A.load_inventory(inv, tiny, True); iv["missing_one"] = "accepted (WRONG)"
except A.InventoryError as e:
    iv["missing_one"] = f"refused: {e}"
(inv / exp[0]["file"]).write_text("{}"); (inv / "extra_cell.json").write_text("{}")
try:
    A.load_inventory(inv, tiny, True); iv["extra_file"] = "accepted (WRONG)"
except A.InventoryError as e:
    iv["extra_file"] = f"refused: {e}"
(inv / "extra_cell.json").unlink()
stale = {"study": "wrong-study", "mode": "validation", "lock_sha256": "not-a-digest", "grid_sha256": "stale", "core_sha256": "stale", "run_sha256": "stale", "text_seed_base": 0, "text_seed": 1, "key_start": 1000000}
for c in exp:
    dd = {"provenance": dict(stale, K=c["K"], slot=R.slot_of(c)), "K": c["K"], "N": GRID["N"], "law": c["law"], "h": c["h"], "L": c["L"], "rule": c["rule"], "colouring": c["colouring"], "gamma": c["gamma"], "levels": {}, "N_eff": 0, "flag": "x"}
    (inv / c["file"]).write_text(json.dumps(dd))
try:
    A.load_inventory(inv, tiny, True); iv["uniformly_stale_complete_inventory"] = "accepted (WRONG)"
except A.InventoryError as e:
    iv["uniformly_stale_complete_inventory"] = f"refused: {e}"
rep["fixtures"]["analyzer_inventory"] = iv; rep["fixtures"]["expected_cells_full_grid"] = len(R.expected_cells(GRID)); rep["fixtures"]["expected_cells_validation_grid"] = len(cells_exp)
# (o) support law limit
law = C.SupportUniform(1000, 50); ch = C.Chain(law, 0, N=1000, L_max=1024, seed=7); lim = C.support_limits(1000, 50, 0.5); so = {"limits": lim}
for L in (64, 1024):
    inc = ch.incidence(L, "distinct"); pe = C.population_estimates(inc, ch, 0.5, 1000, "fixed", rng); pei = C.population_estimates(inc, ch, 0.5, 1000, "independent", rng)
    so[f"L{L}"] = {"mean_M": float(pe["M"][pe["keep"]].mean()), "fixed_q_identity": pe["identity_q"]["var_fixed"], "indep_q_identity": pe["identity_q"]["var_indep"], "rho_bar_fixed": pe["rho_bar"], "rho_bar_indep": pei["rho_bar"]}
rep["checks"]["support_law_limits"] = so
rep["timing"]["checks_seconds"] = round(time.time() - T0, 1)
# (p) timed validation run into a fresh directory; pilot execution of the analyzer (output outside the inventory)
t0 = time.time()
r = subprocess.run([sys.executable, "-u", str(HERE / "s1_run.py"), "--grid", GRID_PATH, "--validation", "--out-dir", str(VAL_DIR)], capture_output=True, text=True)
rep["timing"]["validation_run_seconds"] = round(time.time() - t0, 1); rep["timing"]["returncode"] = r.returncode; rep["timing"]["stderr_tail"] = r.stderr[-1500:]
costs = [json.loads(f_.read_text()) for f_ in sorted(VAL_DIR.glob("costs__*.json"))]
rep["timing"]["chains"] = [{"tag": c["tag"], "n_tuples": c["n_tuples"], "build_seconds": c["build_seconds"], "colourings": c["colourings"], "n_cells": len(c["cells"]), "cells_seconds": round(sum(x["seconds"] for x in c["cells"]), 1), "chain_seconds": c["chain_seconds"]} for c in costs]
rep["timing"]["n_cells_written"] = len([f_ for f_ in VAL_DIR.glob("*.json") if not f_.name.startswith("costs__")])
rep["timing"]["peak_rss_gb_this_process"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9, 2); rep["timing"]["peak_rss_gb_children"] = round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1e9, 2)
pilot_out = OUT / f"results_pilot_{STAMP}.json"; t0 = time.time()
r2 = subprocess.run([sys.executable, str(HERE / "s1_analyze.py"), "--grid", GRID_PATH, "--cells", str(VAL_DIR), "--out", str(pilot_out), "--pilot"], capture_output=True, text=True)
pilot = {"executed": r2.returncode == 0, "seconds": round(time.time() - t0, 1), "stderr_tail": r2.stderr[-800:], "results_file_outside_inventory": str(pilot_out)}
if r2.returncode == 0:
    pr = json.loads(pilot_out.read_text())
    pilot["counts_only"] = {"n_cells": pr["n_cells"], "n_live": pr["n_live"], "n_degenerate_markers": pr["n_degenerate_markers"], "R1_n_eligible": pr["rules"]["R1"]["n_eligible"], "R1_n_resolved": pr["rules"]["R1"]["n_resolved"],
                            "R2_n_checks": pr["rules"]["R2"]["n_checks"], "R3_n_checks": pr["rules"]["R3"]["n_checks"], "R4_n_chains": pr["rules"]["R4"]["n_chains"], "R5_n_chains": pr["rules"]["R5"]["n_chains"]}
    # a second identical analysis must see the same inventory (the results file lives outside it)
    r3 = subprocess.run([sys.executable, str(HERE / "s1_analyze.py"), "--grid", GRID_PATH, "--cells", str(VAL_DIR), "--out", str(OUT / f"results_pilot_{STAMP}_rerun.json"), "--pilot"], capture_output=True, text=True)
    pilot["second_analysis_executed"] = r3.returncode == 0; (OUT / f"results_pilot_{STAMP}_rerun.json").unlink(missing_ok=True)
    # the same-provenance wrong-cell copy and the marker mismatch on a copy of the real pilot inventory
    inv2 = tmp / "inv2"; shutil.copytree(VAL_DIR, inv2); live_files = [c for c in cells_exp if not c["degenerate"]]; mk = [c for c in cells_exp if c["degenerate"]]
    src = next(c for c in live_files if c["name"] == live_files[0]["name"] and c["K"] == live_files[0]["K"] and c["file"] != live_files[0]["file"])
    shutil.copyfile(inv2 / src["file"], inv2 / live_files[0]["file"])
    try:
        A.load_inventory(inv2, GRID, True); iv["same_provenance_wrong_cell_copy"] = "accepted (WRONG)"
    except A.InventoryError as e:
        iv["same_provenance_wrong_cell_copy"] = f"refused: {e}"
    shutil.copyfile(VAL_DIR / live_files[0]["file"], inv2 / live_files[0]["file"])
    if mk:
        # the marker guard itself: the marker's own content (provenance, slot and body intact) given a "levels" key, so only the marker status differs
        md = json.loads((inv2 / mk[0]["file"]).read_text()); md["levels"] = {}; (inv2 / mk[0]["file"]).write_text(json.dumps(md))
        try:
            A.load_inventory(inv2, GRID, True); iv["marker_status_mismatch_only"] = "accepted (WRONG)"
        except A.InventoryError as e:
            iv["marker_status_mismatch_only"] = f"refused: {e}"
        shutil.copyfile(VAL_DIR / mk[0]["file"], inv2 / mk[0]["file"])
    # the role-only mutation of one live cell's law specification (provenance block untouched): the body check must refuse it
    rd = json.loads((inv2 / live_files[0]["file"]).read_text()); rd["law"] = dict(rd["law"], role="illustration" if rd["law"].get("role", "core") == "core" else "core"); (inv2 / live_files[0]["file"]).write_text(json.dumps(rd))
    try:
        A.load_inventory(inv2, GRID, True); iv["role_only_mutation"] = "accepted (WRONG)"
    except A.InventoryError as e:
        iv["role_only_mutation"] = f"refused: {e}"
    shutil.copyfile(VAL_DIR / live_files[0]["file"], inv2 / live_files[0]["file"])
    # the no-lock guard itself: a complete inventory (the validation laws as the grid's laws) in study mode without a lock
    gl = dict(GRID); gl["laws"] = GRID["validation_laws"]
    try:
        A.load_inventory(VAL_DIR, gl, False, lock_path=None); iv["study_mode_without_lock"] = "accepted (WRONG)"
    except A.InventoryError as e:
        iv["study_mode_without_lock"] = f"refused: {e}"
rep["timing"]["pilot_analyzer"] = pilot
# (q) cost table and projection: size-weighted rates from the validation family's cost records; chain sizes from validation-seed builds of every production chain
ind = [(c["seconds"], ch_["n_tuples"] * c["K"]) for ch_ in costs for c in ch_["colourings"] if c["colouring"] == "independent"]
fix = [(c["seconds"], ch_["n_tuples"] * np.log2(max(ch_["n_tuples"], 2)) * c["K"]) for ch_ in costs for c in ch_["colourings"] if c["colouring"] == "fixed"]
cells_v = [(x["nnz"] * x["K"], ch_["n_tuples"], x["seconds"]) for ch_ in costs for x in ch_["cells"]]
Xc = np.array([[1.0, a_ / 1e9, b_ / 1e6] for a_, b_, _ in cells_v]); yc = np.array([s_ for *_, s_ in cells_v])
coef, *_ = np.linalg.lstsq(Xc, yc, rcond=None); coef = np.maximum(coef, 0.0)
rates = {"independent_colouring_s_per_tuple_key": float(sum(a_ for a_, _ in ind) / sum(b_ for _, b_ in ind)) if ind else None, "fixed_colouring_s_per_tuple_log_key": float(sum(a_ for a_, _ in fix) / sum(b_ for _, b_ in fix)) if fix else None,
         "cell_seconds_model": {"c0": float(coef[0]), "per_1e9_nnz_keys": float(coef[1]), "per_1e6_tuples": float(coef[2])}, "n_fit_cells": len(cells_v)}
exp_all = R.expected_cells(GRID); proj = []; t_build = time.time()
for spec in GRID["laws"]:
    law = R.make_law(spec); role = spec.get("role", "core"); L_max = max(GRID["L"] if role == "core" else GRID["L_illustration"]); hs = GRID["h"] if role == "core" else GRID["h_illustration"]
    for h in hs:
        t0 = time.time(); ch = C.Chain(law, h, GRID["N"], L_max, seed=GRID["validation_seed_base"] + 7919 + h); build = time.time() - t0
        cells_h = [c for c in exp_all if c["name"] == law.name and c["h"] == h and not c["degenerate"]]
        col_s = 0.0; seen = set()
        for c in cells_h:
            key = (c["colouring"], c["gamma"], c["K"])
            if key in seen:
                continue
            seen.add(key); n = len(ch.D)
            col_s += (rates["independent_colouring_s_per_tuple_key"] or 0) * n * c["K"] if c["colouring"] == "independent" else (rates["fixed_colouring_s_per_tuple_log_key"] or 0) * n * np.log2(max(n, 2)) * c["K"]
        cell_s = 0.0
        for c in cells_h:
            nnz = int(ch.mask[c["rule"]][:, :c["L"]].sum()); cell_s += coef[0] + coef[1] * nnz * c["K"] / 1e9 + coef[2] * len(ch.D) / 1e6
        proj.append({"chain": f"{law.name}__h{h}", "n_tuples": int(len(ch.D)), "build_seconds_measured": round(build, 1), "colouring_seconds_projected": round(col_s, 1), "cells": len(cells_h), "cell_seconds_projected": round(cell_s, 1), "chain_seconds_projected": round(build + col_s + cell_s, 1)})
        del ch
total = sum(p_["chain_seconds_projected"] for p_ in proj)
rep["projection"] = {"rates": rates, "chains": proj, "total_projected_hours": round(total / 3600, 2), "budget_hours": GRID["budget_hours"], "within_budget": total / 3600 <= GRID["budget_hours"], "chain_builds_seconds": round(time.time() - t_build, 1),
                     "n_cells_total": len(exp_all), "n_degenerate_markers": sum(1 for c in exp_all if c["degenerate"]), "note": "chain sizes from validation-seed builds (the production text seeds are not used before the lock); size-weighted rates from the timed validation family; the colouring and cell models are linear in |D| and nnz x K; an extrapolation with margin, not a guarantee"}
rep["timing"]["peak_rss_gb_this_process_after_builds"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9, 2)
rep["timing"]["total_seconds"] = round(time.time() - T0, 1)
(OUT / "VALIDATION.json").write_text(json.dumps(rep, indent=1, default=float))
shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps({"checks": rep["checks"], "fixtures": rep["fixtures"]}, indent=1, default=float))
print("timing:", json.dumps({k: v for k, v in rep["timing"].items() if k not in ("stderr_tail", "chains")}, indent=1, default=float))
print("projection:", json.dumps({k: v for k, v in rep["projection"].items() if k != "chains"}, indent=1, default=float))
print("DONE validation")
