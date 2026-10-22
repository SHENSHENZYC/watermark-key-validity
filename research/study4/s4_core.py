"""Study 4 core (v1): the analysis-side functions of the power study, on top of the LOCKED cores of Studies 1-3 (imported unchanged):
(a) scoring of generated token arrays with the locked detector code (s2_core.build_chain on the generated tokens alone; s1_core uniforms;
    s3_core p-values) for a list of keys, both rules, several lengths by truncation (prefix-stable retention masks);
(b) the per-key realised power at a threshold (strict p < t), the paired cost against the nominal threshold, and the across-key dispersion
    of power with the binomial noise removed (Study 1's known-noise form: the observed variance minus the mean p(1-p)/(n-1));
(c) the threshold-shift predictor of the cost from a pooled pilot law (the empirical law of the watermarked z on validation keys):
    Delta_hat_k = F_bar(z(t_k)) - F_bar(z_alpha) (a key-homogeneous watermark effect; the simplest model);
(d) the model-null block: Study 3's evaluation-unit computation (sorted p-values, strict counts below every committed threshold) on the
    unwatermarked generations for all 1,000 evaluation keys, and the key-free predictor inputs of Study 3 for the generated null set
    against every calibration prefix (s3_core.set_weights / rho_bar / cross_cov / set_moments / predict_per_key / predict_fixed);
(e) the rule classifications (bands, predicted sides) and the key bootstrap with the protocol's seed convention (sha256 of the row name
    with a salt), paired through shared key indices.
Pure NumPy/SciPy; deterministic given the seeds.
"""
import hashlib, pathlib, sys
import numpy as np
from scipy.stats import norm
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
for p in ("research/study1", "research/study2", "research/study3"):
    sys.path.insert(0, str(ROOT / p))
import s1_core as C   # Study 1's locked core, unchanged
import s2_core as S   # Study 2's locked core, unchanged
import s3_core as T   # Study 3's locked core, unchanged

BOOT_B = 200
BOOT_SALT = 20261019          # the analyzer's key bootstraps: sha256 of the row name, with this salt (protocol section 8)


# ---------------- (a) scoring ----------------
def score_set(X, V, h, keys, gamma, rules, lengths, families=("kgw",), chunk=8):
    """p-values of every text of X (N x L_max int32) under every key, for each (family, rule, L): {(family, rule, L): N x len(keys)} and the
    retained counts M per (rule, L). Every text must retain a tuple at every (rule, L) (an explicit error otherwise)."""
    X = np.ascontiguousarray(X, dtype=np.int32); chain = S.build_chain(X, V, "s4", h); g = C.green_fraction(gamma, V)
    if g != gamma:
        raise RuntimeError(f"g = {g} differs from gamma = {gamma} at V = {V}")
    inc = {}; M = {}
    for r in rules:
        for L in lengths:
            if L > X.shape[1] or L <= h:
                raise ValueError(f"length {L} outside (h, L_max]")
            inc[(r, L)] = chain.incidence(L, r); M[(r, L)] = np.asarray(inc[(r, L)].sum(axis=1)).ravel()
            if (M[(r, L)] <= 0).any():
                raise RuntimeError(f"a text retains no tuple under rule {r} at L = {L}")
    N = X.shape[0]; K = len(keys); P = {(f, r, L): np.empty((N, K), dtype=np.float64) for f in families for r in rules for L in lengths}
    for c0 in range(0, K, chunk):
        U = S.uniforms_chunk(keys[c0:c0 + chunk], chain.D); col = (U < g).astype(np.float64); Sg = S.gumbel_scores(U) if "gumbel" in families else None; del U
        for r in rules:
            for L in lengths:
                if "kgw" in families:
                    P[("kgw", r, L)][:, c0:c0 + chunk] = T.pvalues_kgw(np.asarray(inc[(r, L)] @ col), M[(r, L)], gamma)
                if "gumbel" in families:
                    P[("gumbel", r, L)][:, c0:c0 + chunk] = T.pvalues_gumbel(np.asarray(inc[(r, L)] @ Sg), M[(r, L)])
    info = {"n_tuples": int(len(chain.D)), "mean_M": {f"{r}@{L}": float(M[(r, L)].mean()) for r in rules for L in lengths}}
    return P, M, info, chain


def detector_green_flags(chain, key, gamma, V):
    """The locked detector's green indicator at every position of the chain's texts (False where invalid, t < h): the body contract compares
    it with the hook's stored flags on every scored position."""
    col = C.colour_independent(chain, [key], gamma, V)[:, 0].astype(bool)
    out = np.zeros(chain.X.shape, dtype=bool); valid = chain.col >= 0; out[valid] = col[chain.col[valid]]
    return out, valid


# ---------------- (b) power, cost, dispersion ----------------
def power(p, t):
    """The realised power: the share of texts with p < t (strict); p: N (one key); t: a scalar threshold (0 never rejects)."""
    return float(np.mean(p < t))


def power_count(p, t):
    return int(np.sum(p < t))


def between_key_sd(pi, n):
    """pi: K realised powers, each a share over n texts. Returns the noise-corrected between-key SD (0 when the raw estimate is negative),
    the raw corrected variance, the observed variance and the mean binomial variance p(1-p)/(n-1)."""
    pi = np.asarray(pi, dtype=np.float64); K = len(pi)
    var_obs = float(pi.var(ddof=1)) if K > 1 else float("nan"); noise = float(np.mean(pi * (1 - pi) / (n - 1))) if n > 1 else float("nan")
    raw = var_obs - noise
    return {"sd_between": float(np.sqrt(max(raw, 0.0))), "var_between_raw": raw, "var_obs": var_obs, "mean_binomial_var": noise, "K": int(K), "n": int(n)}


def rng_for(name, salt=BOOT_SALT):
    return np.random.default_rng([int(hashlib.sha256(str(name).encode()).hexdigest()[:8], 16), int(salt)])


def boot_indices(K, rng, B=BOOT_B):
    return rng.integers(0, K, size=(B, K))


def quantiles(x):
    x = np.asarray(x, dtype=np.float64)
    return float(np.quantile(x, 0.025)), float(np.quantile(x, 0.975))


# ---------------- (c) the threshold-shift predictor of the cost ----------------
class PooledLaw:
    """The empirical law of the watermarked per-text p-values over a pilot set (texts x validation keys), pooled, on the p scale: the
    power at a threshold t is the share of pilot p-values strictly below t, the detector's own rule (p < t), so a tie at a lattice
    value counts as the detector counts it. A zero threshold never rejects."""
    def __init__(self, p):
        p = np.asarray(p, dtype=np.float64).ravel(); self.p = np.sort(p[np.isfinite(p)]); self.n = int(len(self.p))
        if self.n == 0:
            raise ValueError("empty pilot law")
    def power_at(self, t):
        """P(p < t) under the law (strict; searchsorted left counts the values strictly below t); t <= 0 gives 0."""
        t = np.asarray(t, dtype=np.float64)
        return np.where(t > 0, np.searchsorted(self.p, t, side="left") / self.n, 0.0)
    def predicted_cost(self, t_keys, alpha):
        """Delta_hat_k = power(nominal) - power(t_k) under the pooled law."""
        return self.power_at(np.full(len(t_keys), float(alpha))) - self.power_at(np.asarray(t_keys))


def between_key_sd_twoway(Y):
    """Y: K x n binary rejection table (keys x the shared prompts). The estimate of the POPULATION between-key variance of the key's expected
    rejection probability over the prompt law, keys and prompts both random (the key component v_K of the crossed two-way decomposition;
    D16), by the balanced two-way decomposition of Study 1's locked core (s1_core.twoway_population_variance on the texts x keys table):
    s_K^2 - MS_E/n, with MS_E the residual mean square after the key and prompt main effects; under the two-way random model
    E[s_K^2] = v_K + v_e/n and E[MS_E] = v_e (v_e the interaction-plus-noise component), so the raw value is unbiased for v_K, and a prompt
    main effect shared by every key is not charged to the keys. It is NOT the variance of a fixed table's key means (R09 F13: for a fixed
    probability table it subtracts the key-by-prompt interaction too); its expectation given the realised prompts (the fixed-prompt key-mean
    variance less 1/n of the within-sample interaction variance) is the prompt-conditioned functional that Study 4's W2 targets (D18).
    Floored at 0 with the raw value recorded; the prompt component (s_P^2 - MS_E/K) beside it."""
    Y = np.asarray(Y, dtype=np.float64); K, n = Y.shape
    s_k2, ms_e, raw = C.twoway_population_variance(Y.T)
    s_p2 = float(Y.mean(axis=0).var(ddof=1)) if n > 1 else float("nan")
    return {"sd_between": float(np.sqrt(max(raw, 0.0))), "var_between_raw": float(raw), "var_obs": float(s_k2), "ms_resid": float(ms_e), "var_prompt_raw": float(s_p2 - ms_e / K), "K": int(K), "n": int(n)}


CAL_MOMENT_REL = 1e-8   # the recomputed calibration-prefix moments against Study 3's pinned INPUTS.json, which stores nine significant digits


def cal_moment_ok(recomputed, stored, rel=CAL_MOMENT_REL):
    """|recomputed - stored| <= rel * max(1, |stored|): the pinned record's own precision (nine significant digits), not an identity check."""
    return abs(float(recomputed) - float(stored)) <= rel * max(1.0, abs(float(stored)))


# ---------------- (d) the model-null block ----------------
def null_counts(P_fam_rule, cal_unit, family, rule, alphas, variants, sources_units, beta):
    """P_fam_rule: N x K p-values of the null texts for all K keys of the record (in the record's key order). Returns counts (strict p < t):
    fixed (2 x nA x K: nominal, multiplier20) and same (n_sources x n_variants x nA x K) over the calibration units `sources_units`
    (an ordered list of CalUnit objects at the same h), exactly as Study 3's evaluation units store them."""
    Ps = T.sort_columns(P_fam_rule); K = P_fam_rule.shape[1]
    fixed = np.empty((2, len(alphas), K), dtype=np.uint16)
    for ia, a in enumerate(alphas):
        fixed[:, ia, :] = T.counts_below(Ps, np.array([[a], [a * beta]]))
    same = np.empty((len(sources_units), len(variants), len(alphas), K), dtype=np.uint16)
    for ic, cu in enumerate(sources_units):
        for ia, a in enumerate(alphas):
            Tm = np.stack([np.broadcast_to(cu.arrays[f"{family}|{rule}|{v}|{a}"], (K,)) for v in variants])
            same[ic, :, ia, :] = T.counts_below(Ps, Tm)
    return fixed, same


def null_predictor_inputs(chain_E, L_E, rule, cal_chain, N_cals, L_C=256):
    """Study 3's key-free inputs for (a calibration prefix C_n of a cell, the generated null set E): the set moments of E at (rule, L_E),
    the moments of every calibration prefix at L_C, and the cross-set shift covariance rho_CE per prefix."""
    wE = T.set_weights(chain_E, L_E, rule); mE = T.set_moments(wE); out = {"E": mE, "C": {}, "rho_CE": {}}
    for n in N_cals:
        wC = T.set_weights(cal_chain, L_C, rule, rows=np.arange(n)); out["C"][n] = T.set_moments(wC)
        cc, nsh = T.cross_cov(wC, wE); out["rho_CE"][n] = {"rho_CE": cc, "n_shared_tuples": nsh}
    return out


def null_predictions(inp, N_E, alphas, N_cals, delta_tol, beta):
    """The predictor's values for the per-key methods at every N_cal and alpha, and for the fixed and scheme-level methods."""
    mE = inp["E"]; out = {"per_key": {}, "fixed": {}}
    for n in N_cals:
        mC = inp["C"][n]; cc = inp["rho_CE"][n]["rho_CE"]; out["per_key"][str(n)] = {}
        for a in alphas:
            out["per_key"][str(n)][str(a)] = {"conformal": T.predict_per_key(mC["rho"], mE["rho"], cc, mC["sigma2"], mE["sigma2"], n, T.j_conformal(n, a), N_E, a),
                                              "tolerance": T.predict_per_key(mC["rho"], mE["rho"], cc, mC["sigma2"], mE["sigma2"], n, T.j_tolerance(n, a, delta_tol), N_E, a)}
    mCf = inp["C"][max(N_cals)]
    for a in alphas:
        mt = T.model_thresholds(mCf["rho"], mCf["sigma2"], a, beta)
        out["fixed"][str(a)] = {"nominal": T.predict_fixed(mE["rho"], mE["sigma2"], a, N_E, a), "multiplier20": T.predict_fixed(mE["rho"], mE["sigma2"], a * beta, N_E, a),
                                "empirical": T.predict_fixed(mE["rho"], mE["sigma2"], mt["t_emp"], N_E, a), "pooled": T.predict_fixed(mE["rho"], mE["sigma2"], mt["t_pool"], N_E, a)}
    return out


# ---------------- (e) classifications ----------------
def classify_band(lo, hi, band):
    if band[0] <= lo and hi <= band[1]:
        return "consistent"
    if hi < band[0] or lo > band[1]:
        return "inconsistent"
    return "unresolved"


def classify_side(lo, hi, side, band=None):
    """W2: side 'below_1' agrees when hi < 1 and disagrees when lo > 1; 'inside_band' agrees when [lo, hi] lies inside the band and
    disagrees when it is disjoint from it; unresolved otherwise."""
    if side == "below_1":
        if hi < 1:
            return "agree"
        if lo > 1:
            return "disagree"
        return "unresolved"
    if side == "inside_band":
        c = classify_band(lo, hi, band)
        return {"consistent": "agree", "inconsistent": "disagree", "unresolved": "unresolved"}[c]
    raise ValueError(side)


def w1_classify(lo, hi, pred_median, tol):
    """W1: the realised key-median cost's interval against [pred - tol, pred + tol]: consistent when inside, inconsistent when disjoint."""
    return classify_band(lo, hi, (pred_median - tol, pred_median + tol))


# ---------------- self-tests on synthetic data ----------------
if __name__ == "__main__":
    rng = np.random.default_rng(99261016); ok = True
    # (a) null p-values of random texts are uniform: the share below 0.05 over 40 validation keys x 300 texts
    V = 5000; X = rng.integers(0, V, size=(300, 128)).astype(np.int32); keys = [1_000_900 + i for i in range(40)]
    P, M, info, chain = score_set(X, V, 1, keys, 0.25, ("raw", "distinct"), (64, 128), families=("kgw", "gumbel"))
    for k, p in P.items():
        sh = float((p < 0.05).mean()); se = np.sqrt(0.05 * 0.95 / p.size)
        if abs(sh - 0.05) > 5 * se + 0.004:
            ok = False; print("FAIL uniformity", k, sh)
    print("(a) null shares below 0.05:", {f"{f}|{r}@{L}": round(float((p < 0.05).mean()), 4) for (f, r, L), p in P.items()})
    # (a') the detector flags of a chain equal s4_wm's hook flags on random choices (the hook module's own check covers it; here the shape)
    fl, valid = detector_green_flags(chain, keys[0], 0.25, V); assert fl.shape == X.shape and valid[:, 1:].all() and not valid[:, 0].any()
    # (b) the noise-corrected between-key SD recovers a planted dispersion
    K, n = 4000, 50; ptrue = np.clip(rng.normal(0.6, 0.10, size=K), 0.01, 0.99); pi = rng.binomial(n, ptrue) / n
    b = between_key_sd(pi, n); print("(b) planted between-key SD 0.10 (clipped normal); estimated", round(b["sd_between"], 4), "naive", round(np.sqrt(b["var_obs"]), 4))
    if abs(b["sd_between"] - ptrue.std(ddof=1)) > 0.01:
        ok = False; print("FAIL between_key_sd")
    # (c) the pooled-law cost predictor on the p scale: the strict rule at ties (the reviewer's fixture) and the analytic normal
    law3 = PooledLaw(np.array([0.01, 0.01, 0.001])); pw3 = law3.power_at(np.array([0.01, 0.001, 0.0]))
    if not (pw3[0] == 1 / 3 and pw3[1] == 0.0 and pw3[2] == 0.0):
        ok = False; print("FAIL PooledLaw ties/abstention", pw3)
    mu = 2.0; pz = norm.sf(rng.normal(mu, 1.0, size=200_000)); law = PooledLaw(pz); za = norm.isf(0.01); shifts = np.array([0.0, 0.3, 0.6, 1.0]); t = norm.sf(za + shifts)
    pred = law.predicted_cost(t, 0.01); exact = norm.sf(za - mu) - norm.sf(za + shifts - mu)
    print("(c) predicted costs", np.round(pred, 4), "exact", np.round(exact, 4), "| ties: power at a tied threshold", pw3[0])
    if np.abs(pred - exact).max() > 0.004:
        ok = False; print("FAIL PooledLaw normal")
    # (c') the two-way between-key SD under shared prompts: a prompt main effect of +-0.3 shared by every key, keys with SD 0.04
    Kk, nn = 200, 50; pm_ = np.array([-0.3] * 25 + [0.3] * 25); est_tw = []; est_bin = []
    for _ in range(100):
        km = rng.normal(0.5, 0.04, size=Kk); Pm = np.clip(km[:, None] + pm_[None, :], 0.01, 0.99); Y = rng.binomial(1, Pm)
        est_tw.append(between_key_sd_twoway(Y)["var_between_raw"]); est_bin.append(between_key_sd(Y.mean(axis=1), nn)["var_between_raw"])
    print("(c') planted between-key variance 0.0016; two-way estimate (mean over 100 tables)", round(float(np.mean(est_tw)), 5), "; binomial proxy", round(float(np.mean(est_bin)), 5))
    if abs(float(np.mean(est_tw)) - 0.0016) > 0.0003:
        ok = False; print("FAIL between_key_sd_twoway")
    # (c'') the calibration-moment allowance: nine-significant-digit rounding accepted, a changed moment refused
    if not cal_moment_ok(2.0565777947567527, 2.05657779) or cal_moment_ok(2.0565777947567527, 2.0565779):
        ok = False; print("FAIL cal_moment_ok")
    # (e) classifications
    assert classify_band(0.8, 1.2, (2/3, 1.5)) == "consistent" and classify_band(1.6, 1.9, (2/3, 1.5)) == "inconsistent" and classify_band(1.2, 1.7, (2/3, 1.5)) == "unresolved"
    assert classify_side(0.6, 0.9, "below_1") == "agree" and classify_side(1.1, 1.3, "below_1") == "disagree" and classify_side(0.9, 1.1, "below_1") == "unresolved"
    assert classify_side(0.8, 1.2, "inside_band", (2/3, 1.5)) == "agree" and classify_side(1.6, 2.0, "inside_band", (2/3, 1.5)) == "disagree"
    assert w1_classify(0.10, 0.14, 0.12, 0.05) == "consistent" and w1_classify(0.30, 0.34, 0.12, 0.05) == "inconsistent" and w1_classify(0.05, 0.20, 0.12, 0.05) == "unresolved"
    # (d) the null block's counts and predictor inputs on random tokens against the real record's calibration units (read-only)
    sys.path.insert(0, str(HERE)); import s4_record as RC, s3_data as SD3, json
    R = RC.Record(verify_files=False); cu = [R.cal("qwen", tag, 1) for tag in ("news_en_256", "wikipedia_en_256")]
    Vq = 151936; X0 = rng.integers(0, Vq, size=(120, 256)).astype(np.int32); keys_all = list(R.keys)
    P0, M0, _, chE = score_set(X0, Vq, 1, keys_all, 0.25, ("raw", "distinct"), (256,), families=("kgw",), chunk=50)
    fixed, same = null_counts(P0[("kgw", "raw", 256)], None, "kgw", "raw", R.alphas, ["empirical", "pooled", "conformal@5000", "tolerance@5000"], cu, R.beta)
    print("(d) null counts shapes", fixed.shape, same.shape, "nominal key-mean level on random tokens", round(float(fixed[0, 0].mean() / 120), 4))
    man3 = json.loads((ROOT / "outputs/study3_v0.1/tokens_manifest.json").read_text()); XC = SD3.load_cal("news_en_256", "qwen", man3); chC = S.build_chain(XC, Vq, "cal", 1)
    inp = null_predictor_inputs(chE, 256, "distinct", chC, [1000, 5000]); pr = null_predictions(inp, 120, [0.01], [1000, 5000], 0.05, 0.05)
    s3in = json.loads((ROOT / "outputs/study3_v0.1/INPUTS.json").read_text()); mC_s3 = s3in["blocks"]["h1|distinct"]["sets"]["qwen|news_en_256|C5000"]
    print("(d) calibration prefix moments recomputed vs Study 3's INPUTS (rho, sigma2):", (round(inp["C"][5000]["rho"], 8), round(inp["C"][5000]["sigma2"], 8)), "vs", (mC_s3["rho"], mC_s3["sigma2"]))
    if abs(inp["C"][5000]["rho"] - mC_s3["rho"]) > 1e-9 or abs(inp["C"][5000]["sigma2"] - mC_s3["sigma2"]) > 1e-9:
        ok = False; print("FAIL calibration moments differ from Study 3's pinned inputs")
    print("(d) predicted conformal@5000 SD on the random set:", pr["per_key"]["5000"]["0.01"]["conformal"].get("sd_cond"), "theory share", pr["per_key"]["5000"]["0.01"]["conformal"].get("theory_share"))
    print("ALL OK" if ok else "SOME CHECKS FAILED")
