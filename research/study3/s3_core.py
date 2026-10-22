"""Study 3 core (v1): per-key and scheme-level calibration of key-randomised detection tests on real null text, their transfer across
text laws, and the calibrated-threshold predictor. Imports Study 1's and Study 2's locked cores unchanged (s1_core: context and tuple
ids, the retention rules, the hash, bvn_upper, mixture_predictor; s2_core: real-text chains, uniforms per key chunk, Gumbel scores).

Every method is a threshold t on the per-text p-value p_k(x) of the published test and rejects iff p_k(x) < t (strict):
- KGW (red-green, independent colouring at g = gamma): p = Phi_bar(z), z = (G - gamma M)/sqrt(M gamma (1 - gamma)) (the published z-test;
  p < alpha iff z > z_alpha); Gumbel-max: p = P(Gamma(M, 1) > S), the exact sum-of-Exp(1) tail (p < alpha iff S exceeds Study 2's exact
  Gamma threshold).
- nominal: t = alpha. multiplier20 (AutoMark's 1/beta multiplier; Gloaguen, Staab, Vechev 2026, Proposition 1): t = alpha * beta. Its
  guarantee (soundness given a key) presupposes per-text p-values that are sound over the key (their Equation (2)): exact for the
  distinct-rule Gumbel test under the hash's ideal-randomness assumption, asymptotic for the distinct-rule KGW z-test, and not for the
  raw rule, whose repeated tuples break per-text validity; here it is a numerical arm, not a guarantee.
- empirical multiplier (scheme level; a plug-in analogue of AutoMark's App. C "smallest passing multiplier"; it runs neither their Algorithm 2
  nor Algorithm 3 and inherits no test-level guarantee): on the
  calibration set C of law P', with the FITTING keys, t*_k = the (floor(alpha N_C) + 1)-th smallest p of key k (the largest threshold with
  realised calibration level <= alpha), and t_emp = min(alpha, the (floor(beta K_fit) + 1)-th smallest t*_k): at most floor(beta K_fit)
  fitting keys exceed alpha on C at t_emp; kappa_hat = alpha / t_emp >= 1.
- pooled (scheme level; key-agnostic null calibration): t_pool = the (floor(alpha N_C K_fit) + 1)-th smallest of all fitting-key p-values on
  C (the largest threshold whose key-averaged realised level on C is <= alpha); not capped at alpha.
- per-key conformal: t_k = the j-th smallest of key k's p-values on the first N_cal calibration texts, j = floor(alpha (N_cal + 1));
  j = 0 never rejects. Under exchangeability the rank argument gives marginal validity only (a fresh text of the same law rejects with
  probability at most j/(N_cal + 1), averaged over the calibration draw); when the calibration texts are i.i.d. draws from the fixed
  key's continuous score law, the population level given the calibration set is Beta(j, N_cal + 1 - j) exactly (Vovk 2012, p.2), the
  reference law the predictor adopts as a model.
- per-key tolerance (Vovk 2012, Prop. 2b): t_k = the j_delta-th smallest, j_delta = max{j >= 1 : P(Bin(N_cal, alpha) <= j - 1) <= delta}
  (a numerical binomial CDF; the conformal and floor indices are exact rational arithmetic), so that under the same i.i.d. continuous-score
  condition P(population level > alpha) <= delta over repeated calibration draws for a fixed key; this is not a statement that at most a
  delta share of keys fail on the one frozen calibration set C of this study; no such j: never rejects (abstains).
Discrete (KGW) scores make both per-key methods conservative under those conditions (ties at the order statistic are not rejected).
Sampling without replacement from a finite pool is not i.i.d. sampling; the finite-pool and shared-C qualifications are stated in the protocol.

The calibrated-threshold predictor (key-free; the common-factor model of Study 1 extended to a threshold set on another text set):
in z-units, for a key, z_i = D^S + e_i on a text set S (D^S the key's mean shift, e_i i.i.d. N(0, sigma_S^2) across texts and keys).
For a per-key method with order index j on N calibration texts C and evaluation texts E: the threshold is t = D^C + sigma_C Phi^-1(U),
U ~ Beta(N + 1 - j, j) (the coverage), so the population level on E is l = Phi_bar((X + sigma_C Phi^-1(U))/sigma_E) with X = D^C - D^E ~
N(0, v), v = rho_C + rho_E - 2 rho_CE (rho_CE = mean over cross pairs of Cov_K(z_i, z_j) = <w_C, w_E> with w the document-averaged
z-weights n_iu/sqrt(M_i): an exact identity for the mean over pairs under independent colours or scores; the estimate satisfies
v_raw = ||w_C - w_E||^2 - tau_v >= -tau_v with tau_v = sigma_C^2/N_cal + sigma_E^2/N_E, so a negative estimate within the floor is
noise around a non-negative population quantity and is set to 0, and one below the floor is impossible and flagged). Given U the Gaussian
integral over X is closed (Phi_bar of the convolution; Owen's T for the second moment); the U integral is a fine midpoint rule on
the probability scale (smooth integrand). The finite-evaluation-text term is E[l(1 - l)]/N_E. Within the same law (C and E disjoint
samples of one law) v estimates 0 and the level is Beta(j, N + 1 - j) exactly when sigma_C = sigma_E. Scheme-level thresholds are
predicted at their model-implied values: t_emp = sigma_C z_alpha + sqrt(rho_C) z_beta (capped at z_alpha's p-value), t_pool = z_alpha
sqrt(rho_C + sigma_C^2); nominal and multiplier20 at alpha and alpha*beta; each through Study 1's closed-form mixture_predictor on E.
The predictor's inputs are exact second moments; its structure (one Gaussian shift, one residual variance, Gaussian residuals) is an
assumption whose adequacy Study 2 measured (a median under-prediction of about a fifth at gamma = 0.25, alpha = 0.01).
"""
import pathlib, sys
from fractions import Fraction
import numpy as np
from scipy.stats import norm, binom, beta as beta_dist, gamma as gamma_dist
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/study1")); sys.path.insert(0, str(ROOT / "research/study2"))
import s1_core as C   # Study 1's locked core, unchanged
import s2_core as S   # Study 2's locked core, unchanged

BETA_QUAD = 20000          # midpoint nodes on the probability scale for the Beta integral of the calibrated-threshold predictor
SHARE_Q = 1000             # midpoint nodes per Beta variable (U and W) for the finite-evaluation exceedance shares of the per-key methods (R07 F9)
SHARE_Q_FIXED = 4000       # midpoint nodes in W for the finite-evaluation shares of a fixed threshold
SCREEN_GAMMA = 0.01        # AutoMark's single screening level (Algorithm 3): a key screens positive when its count is significant at 1%
BOOT_KEYS = 200            # key-bootstrap resamples (analyzer)
V_NEG_TOL = 1e-9           # relative slack on the algebraic floor of v: v_raw = ||w_C - w_E||^2 - tau_v >= -tau_v exactly (tau_v = sigma_C^2/N_cal + sigma_E^2/N_E)


# ---------------- order-statistic indices (exact rational arithmetic) ----------------
def _frac(x):
    return Fraction(str(x))


def j_conformal(N, alpha):
    """floor(alpha (N + 1)) computed exactly (alpha read as its decimal string)."""
    return int((_frac(alpha) * (int(N) + 1)).__floor__())


def j_tolerance(N, alpha, delta):
    """max{j >= 1 : P(Bin(N, alpha) <= j - 1) <= delta}; 0 when even j = 1 fails ((1 - alpha)^N > delta)."""
    N = int(N); j = 0
    cdf = binom.cdf(np.arange(0, N + 1), N, alpha)
    ok = np.flatnonzero(cdf <= delta)          # cdf[j - 1] <= delta  <=>  j - 1 in ok
    if len(ok):
        j = int(ok.max()) + 1
    return min(j, N)


def m_floor(alpha, n):
    return int((_frac(alpha) * int(n)).__floor__())


# ---------------- per-text p-values ----------------
def pvalues_kgw(counts, M, gamma):
    """counts: N x k green counts; M: N retained positions (all > 0). p = Phi_bar(z) of the published z-test."""
    z = (counts - gamma * M[:, None]) / np.sqrt(M[:, None] * gamma * (1 - gamma))
    return norm.sf(z)


def pvalues_gumbel(sums, M):
    """sums: N x k Gumbel score sums; p = P(Gamma(M, 1) > S) (exact upper tail of the sum of M Exp(1) scores)."""
    return gamma_dist.sf(sums, M[:, None])


# ---------------- thresholds ----------------
def kth_smallest(P, j):
    """Column-wise j-th smallest (1-based) of P (n x K); j = 0 returns zeros (a threshold that never rejects)."""
    if j <= 0:
        return np.zeros(P.shape[1])
    return np.partition(P, j - 1, axis=0)[j - 1].copy()


def per_key_thresholds(Pcal, alpha, n_cals, delta):
    """Pcal: N_C x K calibration p-values (rows in calibration order). For each N_cal (a prefix) the conformal and tolerance thresholds."""
    out = {}
    for n in n_cals:
        jc, jt = j_conformal(n, alpha), j_tolerance(n, alpha, delta)
        sub = Pcal[:n]
        out[("conformal", n)] = (kth_smallest(sub, jc), jc)
        out[("tolerance", n)] = (kth_smallest(sub, jt), jt)
    return out


def empirical_multiplier_threshold(Pfit, alpha, beta):
    """Pfit: N_C x K_fit fitting-key p-values on the full calibration set. Returns (t_emp, kappa_hat, detail)."""
    N, K = Pfit.shape; m = m_floor(alpha, N); b = m_floor(beta, K)
    tstar = kth_smallest(Pfit, m + 1)                        # per fitting key: the largest threshold with calibration level <= alpha
    t = float(np.sort(tstar)[b])                             # the (b + 1)-th smallest: at most b fitting keys have t*_k < t
    t_emp = min(float(alpha), t)
    return t_emp, float(alpha / t_emp) if t_emp > 0 else float("inf"), {"m": m, "b": b, "tstar_median": float(np.median(tstar)), "unclipped": t}


def pooled_threshold(Pfit, alpha):
    """The largest threshold whose key-averaged realised level on the calibration set is <= alpha (fitting keys)."""
    N, K = Pfit.shape; m = m_floor(alpha, N * K)
    flat = Pfit.ravel()
    return float(np.partition(flat, m)[m])


# ---------------- evaluation ----------------
def sort_columns(P):
    return np.sort(P, axis=0)


def counts_below(Psorted, T):
    """Psorted: N x K (each column sorted ascending); T: n_var x K thresholds (or n_var scalars broadcast). Returns n_var x K integer
    counts #{i : P[i, k] < T[v, k]} (strict)."""
    N, K = Psorted.shape; T = np.atleast_2d(np.asarray(T, dtype=np.float64))
    if T.shape[1] == 1 and K > 1:
        T = np.repeat(T, K, axis=1)
    out = np.empty(T.shape, dtype=np.int64)
    for k in range(K):
        out[:, k] = np.searchsorted(Psorted[:, k], T[:, k], side="left")
    return out


def screening(counts, N_E, alpha, beta, gamma_s=SCREEN_GAMMA):
    """AutoMark's screen (Algorithm 3, lines 9-11) on one evaluation set: c = the smallest count significant at gamma_s for a key at
    level alpha; the number of keys screening positive B; the null screening bound b = beta + (1 - beta) r. With a shared evaluation
    set the keys' screens are dependent through the texts, so B is a descriptive count, not their test."""
    c = int(np.argmax(binom.sf(np.arange(N_E + 2) - 1, N_E, alpha) <= gamma_s)); r = float(binom.sf(c - 1, N_E, alpha))
    return {"c": c, "r": r, "b": float(beta + (1 - beta) * r), "B": int((np.asarray(counts) >= c).sum()), "K": int(len(counts))}


def level_summary(counts, N_E, alpha):
    a = np.asarray(counts, dtype=np.float64) / N_E
    q = {x: float(np.quantile(a, float(x))) for x in ("0.01", "0.05", "0.5", "0.95", "0.99")}
    return {"key_mean": float(a.mean()), "sd": float(a.std(ddof=1)), "quantiles": q, "max": float(a.max()), "min": float(a.min()),
            "share_above_alpha": float(np.mean(a > alpha)), "share_above_2alpha": float(np.mean(a > 2 * alpha)), "share_above_5alpha": float(np.mean(a > 5 * alpha)),
            "n_zero": int((a == 0).sum()), "n_distinct": int(len(np.unique(a)))}


# ---------------- the calibrated-threshold predictor ----------------
def _beta_nodes(N, j, Q=BETA_QUAD):
    """Midpoint nodes of U ~ Beta(N + 1 - j, j) on the probability scale (equal weights 1/Q)."""
    u = (np.arange(Q) + 0.5) / Q
    return beta_dist.ppf(u, N + 1 - j, j)


def _share_names():
    return ["share_above_alpha_pop", "share_above_2alpha_pop", "share_above_5alpha_pop", "share_above_alpha_finite", "share_above_2alpha_finite", "share_above_5alpha_finite"]


def _beta_mid(a, b, Q):
    """Midpoint nodes (equal weights) of a Beta(a, b) variable on the probability scale."""
    return beta_dist.ppf((np.arange(Q) + 0.5) / Q, a, b)


def finite_share_perkey(sC, sE, v, N_cal, j, N_E, alpha, Q=SHARE_Q):
    """The finite-evaluation estimand of 'the share of keys above a level' for a per-key threshold under the working model, for a in
    (alpha, 2 alpha, 5 alpha): P(count > m) with m = floor(a N_E), the count binomial given the key's population level ell. Through the
    identity BinomSF(m; N_E, ell) = P(W < ell), W ~ Beta(m + 1, N_E - m), and ell = Phi_bar((sigma_C Phi^-1(U) + X)/sigma_E) with
    U ~ Beta(N_cal + 1 - j, j) and X ~ N(0, v) independent, the share is P(X < sigma_E Phi_bar^-1(W) - sigma_C Phi^-1(U)) =
    E_{U,W}[Phi((sigma_E Phi_bar^-1(W) - sigma_C Phi^-1(U))/sqrt(v))]: a smooth integrand on the probability scales of U and W, integrated
    by a Q x Q midpoint rule (the fixed Gauss-Hermite rule in X of the first version missed the binomial tail's narrow transition; R07 F9).
    At v = 0 the X integral is an indicator, and the share is E_U[BinomSF(m; N_E, ell(U))] on Q midpoint nodes of U (exact to the rule's
    error; equal to the Beta-binomial law within a law). sigma_E = 0 makes ell an indicator of sigma_C Phi^-1(U) + X < 0."""
    out = {}; U = _beta_mid(N_cal + 1 - j, j, Q); bU = sC * norm.ppf(U)
    for mult, nm in ((1, "alpha"), (2, "2alpha"), (5, "5alpha")):
        a = mult * alpha; m = m_floor(a, N_E)
        if sE <= 0:
            val = float(np.mean(norm.cdf(-bU / np.sqrt(v)))) if v > 0 else float(np.mean(bU < 0))
        elif v > 0:
            W = _beta_mid(m + 1, N_E - m, Q); aW = sE * norm.isf(W)                       # Phi_bar^-1(W) = isf(W)
            val = float(np.mean(norm.cdf((aW[:, None] - bU[None, :]) / np.sqrt(v))))
        else:
            ell = norm.sf(bU / sE); val = float(np.mean(binom.sf(m, N_E, np.clip(ell, 0.0, 1.0))))
        out[f"share_above_{nm}_finite"] = val
    return out


def finite_share_fixed(rho, sE, tz, N_E, alpha, Q=SHARE_Q_FIXED):
    """The same estimand for a fixed threshold at z = tz with the shift D ~ N(0, rho): ell = Phi_bar((tz - D)/sigma_E), so the share is
    P(D > tz - sigma_E Phi_bar^-1(W)) = E_W[Phi_bar((tz - sigma_E Phi_bar^-1(W))/sqrt(rho))] on Q midpoint nodes of W (rho = 0: the
    binomial tail at the constant level)."""
    out = {}
    for mult, nm in ((1, "alpha"), (2, "2alpha"), (5, "5alpha")):
        a = mult * alpha; m = m_floor(a, N_E)
        if rho > 0:
            W = _beta_mid(m + 1, N_E - m, Q)
            val = float(np.mean(norm.sf((tz - sE * norm.isf(W)) / np.sqrt(rho)))) if sE > 0 else float(np.mean(norm.sf(tz / np.sqrt(rho)) * np.ones(1)))
        else:
            ell = float(norm.sf(tz / sE)) if sE > 0 else float(tz < 0); val = float(binom.sf(m, N_E, ell))
        out[f"share_above_{nm}_finite"] = val
    return out


def predict_per_key(rho_C, rho_E, rho_CE, sig2_C, sig2_E, N_cal, j, N_E, alpha, Q=BETA_QUAD):
    """The across-key law of the realised level on E of a per-key threshold with order index j on N_cal texts of C (module docstring).
    Returns the mean, the population variance, the finite-text floor, the conditional SD, the theory share, and the predicted shares of
    keys above alpha, 2 alpha and 5 alpha as two estimands each (population and finite-evaluation; `finite_shares`)."""
    flags = []; zero_shares = {k: 0.0 for k in _share_names()}
    if j <= 0:
        return {"mean_level": 0.0, "var_pop": 0.0, "sd_pop": 0.0, "floor": 0.0, "sd_cond": 0.0, "theory_share": 0.0, **zero_shares,
                "v": float("nan"), "flags": ["never_rejects"], "j": int(j)}
    v_raw = rho_C + rho_E - 2 * rho_CE; v = v_raw
    # the algebraic floor: rho_bar = A - sigma^2/n exactly (set_moments), so v_raw = A_C + A_E - 2 <w_C, w_E> - tau_v = ||w_C - w_E||^2 - tau_v >= -tau_v;
    # a negative estimate within the floor is sampling noise around a non-negative population quantity (0 on the diagonal) and is set to 0,
    # recorded and unflagged; a value below the floor is impossible and is flagged (an integrity failure; the pair ineligible)
    tau_v = (max(float(sig2_C), 0.0) / N_cal + max(float(sig2_E), 0.0) / N_E) if (N_cal > 0 and N_E > 0) else 0.0
    if not np.isfinite(v_raw):
        flags.append("v_nonfinite"); v = 0.0
    elif v_raw < 0:
        if v_raw < -tau_v * (1 + V_NEG_TOL) - 1e-300:
            flags.append("v_below_algebraic_floor")
        v = 0.0
    for nm, s2 in (("sigma2_C", sig2_C), ("sigma2_E", sig2_E)):
        if not (np.isfinite(s2) and s2 > 0):
            flags.append(f"{nm}_nonpositive")
    sC = np.sqrt(max(sig2_C, 0.0)); sE = np.sqrt(max(sig2_E, 0.0))
    U = _beta_nodes(N_cal, j, Q); a = sC * norm.ppf(U)                  # the threshold's offset from the key's calibration shift, in z
    s = np.sqrt(sE ** 2 + v)
    if s <= 0:
        flags.append("degenerate_scale")
        m = (a < 0).astype(np.float64); e2 = m.copy()
    else:
        m = norm.sf(a / s)
        r = v / (sE ** 2 + v)
        e2 = C.bvn_upper(a / s, a / s, r) if v > 0 else m ** 2
    mean = float(m.mean()); var_within = float(np.mean(np.maximum(e2 - m ** 2, 0.0))); var_between = float(np.mean((m - mean) ** 2))
    var_pop = var_within + var_between; e2m = float(e2.mean())
    floor = max(mean - e2m, 0.0) / N_E
    shares = finite_share_perkey(sC, sE, v, N_cal, j, N_E, alpha)
    # the population shares in closed form on the full U grid: level > x  <=>  X < sigma_E z_x - a
    for mult, nm in ((1, "alpha"), (2, "2alpha"), (5, "5alpha")):
        zx = norm.isf(mult * alpha)
        shares[f"share_above_{nm}_pop"] = float(np.mean(norm.cdf((sE * zx - a) / np.sqrt(v)))) if v > 0 else float(np.mean(a < sE * zx))
    return {"mean_level": mean, "var_pop": var_pop, "sd_pop": float(np.sqrt(var_pop)), "floor": float(floor), "sd_cond": float(np.sqrt(var_pop + floor)),
            "theory_share": float(var_pop / (var_pop + floor)) if var_pop + floor > 0 else 0.0, **shares,
            "v": float(v), "v_raw": float(v_raw), "tau_v": float(tau_v), "flags": flags, "j": int(j)}


def predict_fixed(rho_E, sig2_E, t_p, N_E, alpha):
    """A fixed threshold t_p (a p-value) for every key, through Study 1's closed form on E; plus the predicted shares of keys above alpha,
    2 alpha and 5 alpha as two estimands each (population and finite-evaluation; `finite_shares`), from Gauss-Hermite nodes of the shift
    D ~ N(0, rho_E): the population level ell = Phi_bar((z(t_p) - D)/sigma_E)."""
    if t_p <= 0:
        return {"mean_level": 0.0, "var_pop": 0.0, "sd_pop": 0.0, "floor": 0.0, "sd_cond": 0.0, "theory_share": 0.0, **{k: 0.0 for k in _share_names()}, "flags": ["never_rejects"], "t_p": float(t_p)}
    r = C.mixture_predictor(0.0, rho_E, float(t_p), N_E, sigma2=sig2_E)
    tz = norm.isf(t_p); sE = np.sqrt(max(sig2_E, 0.0)); sd = np.sqrt(max(rho_E, 0.0))
    # the population shares in closed form: level > x  <=>  (tz - D)/sigma_E < z_x  <=>  D > tz - sigma_E z_x
    pop = {f"share_above_{nm}_pop": (float(norm.sf((tz - sE * norm.isf(mult * alpha)) / sd)) if sd > 0 else float(tz - sE * norm.isf(mult * alpha) < 0)) for mult, nm in ((1, "alpha"), (2, "2alpha"), (5, "5alpha"))}
    return {k: r[k] for k in ("mean_level", "var_pop", "sd_pop", "floor", "sd_cond", "theory_share")} | pop | finite_share_fixed(max(rho_E, 0.0), sE, tz, N_E, alpha) | {"flags": r["flags"], "t_p": float(t_p)}


def model_thresholds(rho_C, sig2_C, alpha, beta):
    """Model-implied scheme-level thresholds (p-values) fitted on C: the empirical multiplier's and the pooled one."""
    sC = np.sqrt(max(sig2_C, 0.0)); rC = max(rho_C, 0.0)
    t_emp_z = sC * norm.isf(alpha) + np.sqrt(rC) * norm.isf(beta)
    t_emp = min(float(alpha), float(norm.sf(t_emp_z)))
    t_pool = float(norm.sf(norm.isf(alpha) * np.sqrt(rC + sC ** 2)))
    return {"t_emp": t_emp, "kappa_emp": float(alpha / t_emp) if t_emp > 0 else float("inf"), "t_pool": t_pool}


# ---------------- key-free set moments (identities) ----------------
def set_weights(chain, L, rule, rows=None):
    """Document-averaged z-weights w(u) = mean_i n_iu / sqrt(M_i) over the texts `rows` (all if None), on the chain's sorted tuple ids,
    the per-text exact across-key variances V_i = sum_u n_iu^2 / M_i (independent colours at g = gamma, or unit-variance scores), and
    the sizes. Every text must retain at least one tuple (asserted by the caller through M > 0)."""
    import scipy.sparse as sp
    inc = chain.incidence(L, rule)
    if rows is not None:
        inc = inc[rows]
    M = np.asarray(inc.sum(axis=1)).ravel()
    if (M <= 0).any():
        raise RuntimeError("a text retains no tuple")
    s2 = np.asarray(inc.multiply(inc).sum(axis=1)).ravel(); Vi = s2 / M
    W = sp.diags(1.0 / np.sqrt(M)) @ inc
    w = np.asarray(W.sum(axis=0)).ravel() / inc.shape[0]
    nz = np.flatnonzero(w)
    return {"ids": chain.D[nz], "w": w[nz], "n": int(inc.shape[0]), "meanV": float(Vi.mean()), "mean_M": float(M.mean()), "M": M}


def rho_bar(ws):
    """Study 1's unbiased average pairwise across-key covariance of two texts' z (excluding i = j): n/(n-1) (<w, w> - meanV/n)."""
    n = ws["n"]; A = float(ws["w"] @ ws["w"])
    return n / (n - 1) * (A - ws["meanV"] / n), A


def cross_cov(wa, wb):
    """Mean over cross pairs (a text of set a, a text of set b; disjoint sets) of Cov_K(z_i, z_j) = <w_a, w_b> over the shared tuple ids."""
    ia, ib = wa["ids"], wb["ids"]
    if len(ia) > len(ib):
        wa, wb = wb, wa; ia, ib = ib, ia
    pos = np.searchsorted(ib, ia); pos = np.minimum(pos, len(ib) - 1); hit = ib[pos] == ia
    return float(wa["w"][hit] @ wb["w"][pos[hit]]), int(hit.sum())


def set_moments(ws):
    rho, A = rho_bar(ws)
    return {"rho": float(rho), "A": A, "meanV": ws["meanV"], "sigma2": float(ws["meanV"] - rho), "n": ws["n"], "mean_M": ws["mean_M"], "n_tuples": int(len(ws["ids"]))}
