"""Study 2 core (v1): real-text chains built from cached token arrays with Study 1's locked code (research/study1/s1_core.py,
imported unchanged: context and tuple ids, the three retention rules, the two colouring models, the exact identities, the
common-factor and pairwise Gaussian predictors, the KL bound and the known-mean variance estimator), plus what Study 2 adds:
(a) the Gumbel-max score family (s_k(u) = -ln(1 - U(key, tuple)) ~ Exp(1) under the ideal null; the per-text statistic is the
    sum over the retained positions; the exact Gamma(M, 1) threshold per text; identities with Var s = 1 in place of g(1-g);
    the pairwise Gaussian predictor with per-text thresholds; the known-mean variance estimator with the Exp(1) fourth cumulant 6);
(b) the common-factor model with per-text thresholds: in closed form for a Gaussian shift (Owen's T over the distinct thresholds;
    s1_core.mixture_predictor's closed form for one threshold, which is checked; exact at sigma = 0) and, for a DISCRETE shift sample,
    by direct averaging over the sample (mixture_general; its Gaussian-node use was retired at R05 F6 because a fixed quadrature
    cannot integrate the indicator at sigma = 0);
(c) the simulated-shift predictor (a diagnostic): the across-key law of the mean shift simulated exactly from the realised
    document-averaged weights for the heaviest tuples plus a Gaussian remainder with the exact residual variance, moment-matched
    to rho_bar; it keeps the Gaussian residual and tests the shift's non-Gaussianity (discreteness and skew), the hypothesis left
    open by Study 1's h = 0 cells;
(d) the crossed key-by-document bootstrap of the deployer's view (per-key level quantiles, shares above 2 alpha and 5 alpha and
    the sampled maximum), gate constraint 12.
Pure NumPy/SciPy; deterministic given the seeds.
"""
import pathlib, sys
import numpy as np
import scipy.sparse as sp
from scipy.stats import norm, gamma as gamma_dist
from numpy.polynomial.hermite_e import hermegauss
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/study1"))
import s1_core as C   # Study 1's locked core, unchanged (its digest is pinned by Study 1's lock and by this study's lock)

SIM_SHIFT_B = 20000       # simulated-shift predictor: number of simulated colourings of the heavy tuples
SIM_SHIFT_T = 2000        # ... number of heaviest tuples simulated exactly (the remainder is Gaussian with its exact variance)
GH_NODES = 200            # Gauss-Hermite nodes for the Gaussian-shift quadrature of the general predictor
BOOT_CROSSED = 200        # crossed key-by-document bootstrap resamples (deployer's view)
EXP_KAPPA4 = 6.0          # fourth cumulant of Exp(1)


# ---------------- real-text chains ----------------
class FixedTexts:
    """A law-like wrapper so that s1_core.Chain can be built on cached real token arrays (X: N x L_max int32)."""
    def __init__(self, X, V, name):
        self.X = np.ascontiguousarray(X, dtype=np.int32); self.V = int(V); self.name = name
        if self.X.min() < 0 or self.X.max() >= self.V:
            raise ValueError("token ids outside [0, V)")
    def sample(self, N, L, rng):
        if N != self.X.shape[0] or L != self.X.shape[1]:
            raise ValueError("FixedTexts.sample: shape mismatch")
        return self.X
    def collision_h(self, h):
        return None


def build_chain(X, V, name, h):
    """One (cell, tokenizer, h) chain over the cached texts (prefix-stable retention masks for every L <= L_max)."""
    return C.Chain(FixedTexts(X, V, name), h, X.shape[0], X.shape[1], seed=0)


# ---------------- scores per key chunk ----------------
def uniforms_chunk(keys, D):
    """|D| x k float64 uniforms U(key, tuple id) for a chunk of keys (s1_core.uniforms per key)."""
    out = np.empty((len(D), len(keys)), dtype=np.float64)
    for j, k in enumerate(keys):
        out[:, j] = C.uniforms(k, D)
    return out


def gumbel_scores(U):
    """s = -ln(1 - U) ~ Exp(1) under the ideal null; U in [0, 1 - 2^-53] so the log is finite."""
    return -np.log1p(-U)


def gamma_threshold_z(alpha, M):
    """The exact Gamma(M, 1) upper-alpha quantile of the sum of M i.i.d. Exp(1) scores, in z-units (S - M)/sqrt(M) (per text)."""
    M = np.asarray(M, dtype=np.float64)
    return (gamma_dist.isf(alpha, M) - M) / np.sqrt(M)


# ---------------- identities and population estimates for a score with variance var_s (Gumbel: 1) ----------------
def identity_score(w, var_s=1.0):
    """Exact across-key variance of sum_u w(u) s_K(u) for independent scores of variance var_s: var_s * A, with A = sum w^2
    (no context term: a Gumbel score has no fixed-size constraint); A4 for the fourth-moment SE."""
    A = float((w ** 2).sum()); A4 = float((w ** 4).sum())
    return {"A": A, "A4": A4, "var": float(var_s * A), "structural_zero": bool(A == 0.0)}


def population_estimates_score(inc, chain, rng, var_s=1.0, B=C.BOOT_TEXTS):
    """The score analogue of s1_core.population_estimates: z-weights n_iu/sqrt(M_i) (the statistic (S_i - M_i)/sqrt(M_i)),
    q-weights n_iu/M_i (the mean score), the identities at the document-averaged weights, rho_bar (the average pairwise across-key
    covariance of two texts' z: unbiased for the across-key variance of the population mean shift), A_between, text-bootstrap SEs,
    the per-text across-key variances V_i = var_s * sum_u n_iu^2 / M_i, and sigma_model2 = mean_i V_i - rho_bar (mu_i = 0 exactly:
    E s = 1 so E[(S_i - M_i)] = 0 for every text)."""
    M = np.asarray(inc.sum(axis=1)).ravel(); keep = M > 0; N = inc.shape[0]; N_eff = int(keep.sum())
    if N_eff == 0:
        return None
    s2 = np.asarray(inc.multiply(inc).sum(axis=1)).ravel()
    Vi = np.where(keep, var_s * s2 / np.maximum(M, 1), 0.0); Aq = np.where(keep, s2 / np.maximum(M, 1) ** 2, 0.0)
    Wz = sp.diags(np.where(keep, 1.0 / np.sqrt(np.maximum(M, 1)), 0.0)) @ inc
    Wq = sp.diags(np.where(keep, 1.0 / np.maximum(M, 1), 0.0)) @ inc

    def est(a):
        n = float(a[keep].sum())
        wz = np.asarray(Wz.T @ a).ravel() / n; wq = np.asarray(Wq.T @ a).ravel() / n
        idz = identity_score(wz, var_s); idq = identity_score(wq, var_s)
        meanV = float(a @ Vi) / n; meanAq = float(a @ Aq) / n
        rho = n / (n - 1) * (idz["var"] - meanV / n) if n > 1 else float("nan")
        Ab = n / (n - 1) * (idq["A"] - meanAq / n) if n > 1 else float("nan")
        return wz, wq, idz, idq, meanV, meanAq, rho, Ab
    a0 = keep.astype(np.float64)
    wz, wq, idz, idq, meanV, meanAq, rho, Ab = est(a0)
    idx = np.flatnonzero(keep); boots = []
    if len(idx) > 1:
        for _ in range(B):
            a = np.bincount(rng.choice(idx, size=len(idx), replace=True), minlength=N).astype(np.float64)
            r = est(a); boots.append((r[6], r[7], r[2]["var"], r[3]["A"]))
    bt = np.array(boots) if boots else np.full((2, 4), np.nan)
    return {"wz": wz, "wq": wq, "identity_z": idz, "identity_q": idq, "N_eff": N_eff, "M": M, "keep": keep, "mean_var_text_z": meanV, "mean_A_q_text": meanAq,
            "rho_bar": float(rho), "A_q_between": float(Ab), "rho_bar_boot_se": float(np.nanstd(bt[:, 0], ddof=1)), "A_q_between_boot_se": float(np.nanstd(bt[:, 1], ddof=1)),
            "var_zbar_exact_boot_se": float(np.nanstd(bt[:, 2], ddof=1)), "A_q_realised_boot_se": float(np.nanstd(bt[:, 3], ddof=1)), "mu_delta": 0.0,
            "sigma_model2": float(meanV - rho) if np.isfinite(rho) else float("nan"), "sigma_tol": float(C.ZERO_REL * max(meanV, 1e-300)),
            "Vi": Vi, "Wz": Wz, "mu_i": np.zeros(N), "var_s": var_s}


# ---------------- the general mixture predictor (any shift law, per-text thresholds) ----------------
def gaussian_shift_nodes(mu, var, Q=GH_NODES):
    """Gauss-Hermite nodes and weights for E_delta[f(delta)], delta ~ N(mu, var) (var <= 0: a point mass at mu)."""
    if var <= 0.0:
        return np.array([mu]), np.array([1.0])
    x, w = hermegauss(Q); return mu + np.sqrt(var) * x, w / w.sum()


def mixture_general(delta_nodes, delta_weights, tau, sigma2, N_eff, tol=0.0):
    """The common-factor model integrated over an arbitrary shift law: given the shift delta, text i rejects with probability
    pi_i(delta) = Phi_bar((tau_i - delta)/sigma), independently of the other texts; tau_i is the text's effective threshold (its
    z-threshold minus its own across-key mean offset). Returns E[alpha_k], Var_delta(alpha(delta)) (the population variance),
    the finite-text floor E_delta[mean_i pi_i (1 - pi_i)]/N_eff, sd_cond = sqrt(var_pop + floor), the theory share, and the
    shift's SD. tau is reduced to its unique values with multiplicities, so the cost is O(nodes x distinct thresholds).
    sigma = 0 gives pi_i = 1{delta > tau_i}. A materially negative or non-finite sigma2 is flagged, not replaced (Study 1, F13)."""
    flags = []
    if not np.isfinite(sigma2):
        flags.append("sigma2_nonfinite"); sigma2 = 0.0
    elif sigma2 < -abs(tol):
        flags.append("sigma2_negative"); sigma2 = 0.0
    elif sigma2 < abs(tol):
        sigma2 = 0.0
    tau_u, cnt = np.unique(np.asarray(tau, dtype=np.float64), return_counts=True); frac = cnt / cnt.sum()
    d = np.asarray(delta_nodes, dtype=np.float64)[:, None]; w = np.asarray(delta_weights, dtype=np.float64)
    if sigma2 > 0:
        pi = norm.sf((tau_u[None, :] - d) / np.sqrt(sigma2))
    else:
        pi = (d > tau_u[None, :]).astype(np.float64)
    a = pi @ frac                                   # alpha(delta) per node
    mean = float(w @ a); var_pop = max(float(w @ (a ** 2)) - mean ** 2, 0.0)
    floor = float(w @ ((pi * (1 - pi)) @ frac)) / N_eff
    return {"mean_level": mean, "var_pop": var_pop, "sd_pop": float(np.sqrt(var_pop)), "floor": floor, "sd_cond": float(np.sqrt(var_pop + floor)),
            "theory_share": float(var_pop / (var_pop + floor)) if var_pop + floor > 0 else 0.0, "sigma2": float(sigma2), "flags": flags,
            "shift_sd": float(np.sqrt(max(float(w @ (d.ravel() ** 2)) - float(w @ d.ravel()) ** 2, 0.0))), "n_distinct_thresholds": int(len(tau_u))}


def mixture_gaussian_closed(mu, var, tau, sigma2, N_eff, tol=0.0):
    """The common-factor model with a GAUSSIAN shift delta ~ N(mu, var) and per-text effective thresholds tau_i, in closed form (R05 F6):
    text i rejects iff delta + sigma*eps_i > tau_i, so with Z_i = delta + sigma*eps_i ~ N(mu, var + sigma^2), E[alpha_k] = mean_i Phi_bar(a_i),
    a_i = (tau_i - mu)/sqrt(var + sigma^2); E[alpha_k^2] = mean_{i,j} P(Z_i > tau_i, Z_j > tau_j), a bivariate normal orthant probability
    with correlation r = var/(var + sigma^2) (Owen's T; r = 1 when sigma = 0, where the level is the indicator mean_i 1{delta > tau_i} and
    the finite-text floor vanishes); the floor is E[mean_i pi_i(1 - pi_i)]/N_eff = (E[alpha] - mean_i P(Z_i > tau_i, Z_i' > tau_i))/N_eff
    for two texts with the same threshold sharing the shift. For one threshold it is s1_core.mixture_predictor's closed form exactly;
    for the Gumbel family the thresholds vary with M_i. Exact for every sigma2 >= 0 (no quadrature). Flags as in mixture_predictor."""
    flags = []
    if not np.isfinite(sigma2):
        flags.append("sigma2_nonfinite"); sigma2 = 0.0
    elif sigma2 < -abs(tol):
        flags.append("sigma2_negative"); sigma2 = 0.0
    elif sigma2 < abs(tol):
        sigma2 = 0.0
    var = max(float(var), 0.0); sigma2 = float(sigma2); tot = var + sigma2
    tau_u, cnt = np.unique(np.asarray(tau, dtype=np.float64), return_counts=True); f = cnt / cnt.sum()
    if tot <= 0.0:
        pi = (mu > tau_u).astype(np.float64); mean = float(f @ pi); e2 = float(f @ pi) ; same = float(f @ pi)   # deterministic: every text rejects iff mu > tau_i
        var_pop = max(float((f[:, None] * f[None, :] * np.minimum(pi[:, None], pi[None, :])).sum()) - mean ** 2, 0.0)
        return {"mean_level": mean, "var_pop": var_pop, "sd_pop": float(np.sqrt(var_pop)), "floor": 0.0, "sd_cond": float(np.sqrt(var_pop)), "theory_share": 1.0 if var_pop > 0 else 0.0, "sigma2": sigma2, "flags": flags, "shift_sd": 0.0, "n_distinct_thresholds": int(len(tau_u)), "method": "closed form (degenerate)"}
    a = (tau_u - mu) / np.sqrt(tot); r = var / tot
    pi = norm.sf(a); mean = float(f @ pi)
    both = C.bvn_upper(a[:, None], a[None, :], r)                       # P(Z_s > tau_s, Z_t > tau_t) for two texts sharing the shift
    e2 = float((f[:, None] * f[None, :] * both).sum()); same = float(f @ np.diag(both))
    var_pop = max(e2 - mean ** 2, 0.0); floor = max(mean - same, 0.0) / N_eff
    return {"mean_level": mean, "var_pop": var_pop, "sd_pop": float(np.sqrt(var_pop)), "floor": float(floor), "sd_cond": float(np.sqrt(var_pop + floor)),
            "theory_share": float(var_pop / (var_pop + floor)) if var_pop + floor > 0 else 0.0, "sigma2": sigma2, "flags": flags, "shift_sd": float(np.sqrt(var)),
            "n_distinct_thresholds": int(len(tau_u)), "method": "closed form (Owen's T over distinct thresholds)"}


def simulated_shift(wz, scale_to_var, family, g, rng, T=SIM_SHIFT_T, B=SIM_SHIFT_B):
    """B simulated values of the mean shift delta = sum_u wz(u) (score_u - E score) across FRESH ideal colourings/scores: the T
    heaviest tuples (by |wz|) are simulated exactly (Bernoulli(g) - g for the red-green family; Exp(1) - 1 for Gumbel), the
    remainder enters as a Gaussian with its exact variance, and the sample is rescaled to variance scale_to_var (rho_bar, the
    population shift variance the common-factor predictor uses; the realised-weight identity carries the finite-text part too).
    Independent colouring only (the fixed-size correction is not simulated). Returns the samples and the shares of variance."""
    wz = np.asarray(wz, dtype=np.float64); order = np.argsort(-np.abs(wz)); heavy = order[:T]; light = order[T:]
    var_unit = g * (1 - g) if family == "kgw" else 1.0
    v_heavy = var_unit * float((wz[heavy] ** 2).sum()); v_light = var_unit * float((wz[light] ** 2).sum()); v_id = v_heavy + v_light
    wh = wz[heavy]
    if family == "kgw":
        draws = (rng.random((B, len(wh))) < g).astype(np.float64) - g
    else:
        draws = rng.exponential(1.0, size=(B, len(wh))) - 1.0
    delta = draws @ wh + (rng.standard_normal(B) * np.sqrt(v_light) if v_light > 0 else 0.0)
    scale = float(np.sqrt(scale_to_var / v_id)) if (v_id > 0 and scale_to_var > 0) else 0.0
    delta = delta * scale
    return delta, {"T": int(len(wh)), "B": int(B), "var_heavy_share": float(v_heavy / v_id) if v_id > 0 else float("nan"), "var_identity_realised": v_id, "scale": scale,
                   "sample_skew": float(((delta - delta.mean()) ** 3).mean() / max(delta.std(), 1e-300) ** 3), "sample_kurtosis_excess": float(((delta - delta.mean()) ** 4).mean() / max(delta.std(), 1e-300) ** 4 - 3.0)}


# ---------------- Gumbel pairwise Gaussian predictor (per-text thresholds; Var s = 1) ----------------
def pairwise_gaussian_gumbel(pe, alphas, rng, n_s=C.PAIR_SUBSAMPLE):
    keep = pe["keep"]; idx = np.flatnonzero(keep); N_eff = len(idx)
    if N_eff < 3:
        return None
    perm = rng.permutation(idx); n1 = min(n_s, N_eff); subs = [np.sort(perm[:n1])] + ([np.sort(perm[n1:2 * n1])] if N_eff >= 2 * n1 >= 6 else [])
    results = [_pairwise_one_gumbel(pe, alphas, sub, N_eff) for sub in subs]
    out = {"heterogeneity": results[0]["heterogeneity"], "by_alpha": {}}
    for a in alphas:
        d = dict(results[0]["by_alpha"][str(a)])
        if len(results) > 1:
            d["sd_cond_replicate"] = results[1]["by_alpha"][str(a)]["sd_cond"]; d["subsample_sd_difference"] = abs(d["sd_cond"] - d["sd_cond_replicate"])
        else:
            d["sd_cond_replicate"] = None; d["subsample_sd_difference"] = None
        out["by_alpha"][str(a)] = d
    out["heterogeneity"]["replicate"] = results[1]["heterogeneity"] if len(results) > 1 else None
    return out


def _pairwise_one_gumbel(pe, alphas, sub, N_eff):
    n = len(sub); W = pe["Wz"][sub]; Cov = pe["var_s"] * np.asarray((W @ W.T).todense())
    Vi = np.clip(np.diag(Cov), 0.0, None); sd = np.sqrt(Vi); ok = sd > 0; M = pe["M"][sub]
    corr = np.zeros_like(Cov); corr[np.ix_(ok, ok)] = Cov[np.ix_(ok, ok)] / np.outer(sd[ok], sd[ok]); corr = np.clip(corr, -1.0, 1.0)
    iu = np.triu_indices(n, 1); c_off = Cov[iu]; r_off = corr[iu]
    het = {"n_subsample": int(n), "pair_cov_mean": float(c_off.mean()), "pair_cov_cv": float(c_off.std() / c_off.mean()) if c_off.mean() > 0 else float("nan"),
           "pair_corr_quantiles": {q: float(np.quantile(r_off, float(q))) for q in ("0.5", "0.9", "0.99")}, "pair_corr_max": float(r_off.max()), "share_zero_variance_texts": float(1 - ok.mean())}
    out = {}
    for alpha in alphas:
        t_i = gamma_threshold_z(alpha, M)                                  # per-text exact Gamma threshold in z-units
        t = np.where(ok, t_i / np.where(ok, sd, 1.0), np.inf); pi = np.where(ok, norm.sf(t), 0.0)
        both = C.bvn_upper(t[iu[0]], t[iu[1]], r_off); zero_pairs = ~(ok[iu[0]] & ok[iu[1]])
        if zero_pairs.any():
            both[zero_pairs] = (pi[iu[0]] * pi[iu[1]])[zero_pairs]
        cov_ind = both - pi[iu[0]] * pi[iu[1]]
        var = float((pi * (1 - pi)).mean() / N_eff + (1 - 1.0 / N_eff) * cov_ind.mean())
        out[str(alpha)] = {"sd_cond": float(np.sqrt(max(var, 0.0))), "var_signed": var, "mean_level": float(pi.mean()), "floor_part": float((pi * (1 - pi)).mean() / N_eff), "offdiag_part": float((1 - 1.0 / N_eff) * cov_ind.mean())}
    return {"heterogeneity": het, "by_alpha": out}


# ---------------- the crossed key-by-document bootstrap (deployer's view) ----------------
def deployer_view(a_k, alpha):
    return {"quantiles": {q: float(np.quantile(a_k, float(q))) for q in ("0.01", "0.05", "0.5", "0.95", "0.99")}, "max_key": float(a_k.max()), "min_key": float(a_k.min()),
            "share_keys_above_2alpha": float(np.mean(a_k > 2 * alpha)), "share_keys_above_5alpha": float(np.mean(a_k > 5 * alpha))}


def crossed_bootstrap(R, alpha, rng, B=BOOT_CROSSED):
    """R: N_eff x K rejection table (bool). B resamples of BOTH the texts (multinomial weights) and the keys (with replacement);
    for each, the per-key levels over the resampled texts and the deployer's summaries; percentile 95% intervals. The interval
    of the maximum is the interval of the SAMPLED maximum under resampling, never a population extreme (gate constraint 12)."""
    N, K = R.shape; Rf = R.astype(np.float32)
    A = np.stack([np.bincount(rng.integers(0, N, size=N), minlength=N) for _ in range(B)]).astype(np.float32)   # B x N text weights
    lev = (A @ Rf) / N                                                                                              # B x K levels over resampled texts
    stats = {"q0.01": [], "q0.05": [], "q0.5": [], "q0.95": [], "q0.99": [], "max": [], "share2": [], "share5": []}
    for b in range(B):
        kk = rng.integers(0, K, size=K); a = lev[b, kk]
        stats["q0.01"].append(np.quantile(a, 0.01)); stats["q0.05"].append(np.quantile(a, 0.05)); stats["q0.5"].append(np.quantile(a, 0.5)); stats["q0.95"].append(np.quantile(a, 0.95)); stats["q0.99"].append(np.quantile(a, 0.99))
        stats["max"].append(a.max()); stats["share2"].append(np.mean(a > 2 * alpha)); stats["share5"].append(np.mean(a > 5 * alpha))
    return {k: {"ci95": [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))], "boot_se": float(np.std(v, ddof=1))} for k, v in stats.items()} | {"B": int(B), "note": "crossed key-by-document bootstrap (texts and keys resampled); the max row is the sampled maximum's interval"}


def compact_levels(out):
    """Per-key storage: the per-key level values (k/N_eff) are stored as the INTEGER counts of rejecting texts (exact; the analyzer
    divides by N_eff), the per-key mean-score values to 6 decimals, and the per-key zbar values are dropped (derivable statistics only)."""
    N_eff = out.get("N_eff", 0)
    for lv in out.get("levels", {}).values():
        if "level_values" in lv:
            lv["level_counts"] = [int(round(x * N_eff)) for x in lv.pop("level_values")]
    for blk in ("q_hat", "s_bar"):
        if blk in out and "values" in out[blk]:
            out[blk]["values"] = [round(float(x), 6) for x in out[blk]["values"]]
    if "zbar" in out and "values" in out["zbar"]:
        out["zbar"].pop("values")
    return out


# ---------------- cell statistics ----------------
TEXT_BOOT_PROD = 5        # text-bootstrap resamples in production (the SEs of rho_bar, A_between and the realised identities are descriptive in Study 2;
                          # Study 1 used 30; with B_text = 30 kgw_cell_statistics reproduces s1_core.cell_statistics field for field, which the validation checks)


def kgw_cell_statistics(inc, counts, chain, gamma, alphas, V, colouring, rng, deployer=False, sim_shift=True, B_text=TEXT_BOOT_PROD):
    """A faithful copy of s1_core.cell_statistics (v6; the same formulas, calling the same Study 1 helpers, the same random-stream
    order) with two changes: the population estimates are computed ONCE with B_text text-bootstrap resamples (Study 1: 30; here a
    parameter, 5 in production) and shared with Study 2's additions, which never change Study 1's fields: per alpha the general
    predictor's quadrature cross-check of the closed form, the simulated-shift predictor (independent colouring) and, on the deployer
    subset, the crossed key-by-document bootstrap. With B_text = 30 the Study 1 fields equal s1_core.cell_statistics' exactly."""
    g = C.green_fraction(gamma, V); deg, m = C.degenerate(gamma, V)
    pe = C.population_estimates(inc, chain, gamma, V, colouring, rng, B=B_text)
    N = inc.shape[0]
    out = {"g": g, "m": m, "degenerate": bool(deg), "N": int(N), "levels": {}}
    if pe is None:
        out.update({"N_eff": 0, "frac_M0": 1.0, "flag": "no text has a retained tuple: no detection possible (M = 0 everywhere)"}); return out
    M, keep, N_eff = pe["M"], pe["keep"], pe["N_eff"]; K = counts.shape[1]
    Mk = M[keep]
    out.update({"N_eff": N_eff, "frac_M0": float(1 - keep.mean()), "mean_M": float(Mk.mean()), "min_M": int(Mk.min()), "max_M": int(Mk.max()),
                "M_quantiles": {q: float(np.quantile(Mk, float(q))) for q in ("0.05", "0.5", "0.95")},
                "coverage": {"distinct_retained_tuples": int((inc.getnnz(axis=0) > 0).sum()), "share_of_V_if_h0": float((inc.getnnz(axis=0) > 0).sum() / V) if chain.h == 0 else None}})
    frac = counts[keep] / Mk[:, None]; z = C.z_scores(counts[keep], Mk, gamma)
    q_hat = frac.mean(axis=0); zbar = z.mean(axis=0)
    kb = rng.integers(0, K, size=(C.BOOT_KEYS, K))
    idq = pe["identity_q"]; Eq = g * float(pe["wq"].sum()); terms = (q_hat - Eq) ** 2; s0 = float(terms.mean())
    own_q = idq["var_fixed"] if colouring == "fixed" else idq["var_indep"]
    r3_tol = float(C.ZERO_REL * max(g * (1 - g) * idq["A"], 1e-300))
    observed_sample_constancy = bool(float(terms.max() - terms.min()) <= r3_tol)
    if colouring == "fixed":
        s0_se = float((terms[kb]).mean(axis=1).std(ddof=1)); s0_method = "key bootstrap (empirical)"
    else:
        k4 = g * (1 - g) * (1 - 6 * g * (1 - g)); mu4 = idq["A4"] * k4 + 3 * own_q ** 2
        s0_se = float(np.sqrt(max(mu4 - own_q ** 2, 0.0) / K)); s0_method = "exact fourth moment"
    out["q_hat"] = {"mean": float(q_hat.mean()), "exact_mean": Eq, "var_across_keys": float(q_hat.var(ddof=1)), "var_boot_ci95": [float(x) for x in np.quantile(q_hat[kb].var(axis=1, ddof=1), [0.025, 0.975])],
                    "var_known_mean": s0, "var_known_mean_se": s0_se, "se_method": s0_method, "exact_var_own_colouring": own_q, "r3_tolerance": r3_tol, "observed_sample_constancy": observed_sample_constancy,
                    "structural_zero": bool(idq["structural_zero_fixed"] if colouring == "fixed" else idq["structural_zero_indep"]),
                    "values": [round(float(x), 7) for x in q_hat]}
    out["zbar"] = {"mean": float(zbar.mean()), "var_across_keys": float(zbar.var(ddof=1)), "var_boot_ci95": [float(x) for x in np.quantile(zbar[kb].var(axis=1, ddof=1), [0.025, 0.975])], "values": [round(float(x), 6) for x in zbar]}
    zv = z.var(axis=0, ddof=1) if N_eff > 1 else np.full(K, np.nan)
    out["z_var_within_key"] = {"mean_over_keys": float(np.nanmean(zv)), "min": float(np.nanmin(zv)), "max": float(np.nanmax(zv))}
    own = "var_fixed" if colouring == "fixed" else "var_indep"
    out["identity_q"] = pe["identity_q"]; out["identity_z"] = pe["identity_z"]
    out["population"] = {k: pe[k] for k in ("rho_bar", "rho_bar_boot_se", "A_q_between", "A_q_between_boot_se", "var_zbar_exact_boot_se", "A_q_realised_boot_se", "mean_var_text_z", "mean_A_q_text", "mu_delta", "sigma_model2")}
    out["population"].update({"var_zbar_exact": pe["identity_z"][own], "A_q_realised": pe["identity_q"]["A"], "sd_zshift_pop": float(np.sqrt(max(pe["rho_bar"], 0.0))) if np.isfinite(pe["rho_bar"]) else float("nan"),
                              "collision_h_analytic": chain.law.collision_h(chain.h) if hasattr(chain.law, "collision_h") else None, "sigma_tol": pe["sigma_tol"], "text_bootstrap_B": int(B_text)})
    pair = C.pairwise_gaussian_predictor(pe, chain, gamma, V, colouring, alphas, rng)
    out["covariance_heterogeneity"] = pair["heterogeneity"] if pair else None
    for alpha in alphas:
        z_a = norm.isf(alpha); rej = (z > z_a)
        a_k = rej.mean(axis=0)
        sd_obs = float(a_k.std(ddof=1)); boots = a_k[kb].std(axis=1, ddof=1)
        pred = C.mixture_predictor(pe["mu_delta"], pe["rho_bar"], alpha, N_eff, pe["sigma_model2"], tol=pe["sigma_tol"])
        pred_unit = C.mixture_predictor(pe["mu_delta"], pe["rho_bar"], alpha, N_eff, 1.0)
        sd_pred = pred["sd_cond"]
        ratio_boot = boots / sd_pred if sd_pred > 0 else np.full(C.BOOT_KEYS, np.nan)
        s_k2, ms_e, v_pop = C.twoway_population_variance(rej.astype(np.float64))
        vb = C.twoway_bootstrap(rej.astype(np.float64), rng)
        ex = C.exact_marginal_level_distinct_independent(M, g, gamma, alpha)
        lv = {"key_mean_level": float(a_k.mean()), "unconditional_rate": float(a_k.mean() * N_eff / N),
              "se_conditional_on_texts": float(sd_obs / np.sqrt(K)),
              "r2_kl_pbound": C.kl_chernoff_pbound(float(a_k.mean()), ex, K),
              "pred_pairwise_gaussian": pair["by_alpha"][str(alpha)] if pair else None,
              "sd_obs_conditional": sd_obs, "sd_obs_boot_ci95": [float(x) for x in np.quantile(boots, [0.025, 0.975])], "sd_obs_boot_se": float(boots.std(ddof=1)),
              "pred_first_order": pred, "pred_unit_sigma": pred_unit,
              "ratio_obs_over_pred": float(sd_obs / sd_pred) if sd_pred > 0 else float("nan"),
              "ratio_boot_ci95": [float(x) for x in np.nanquantile(ratio_boot, [0.025, 0.975])] if sd_pred > 0 else [float("nan")] * 2,
              "ratio_boot_se": float(np.nanstd(ratio_boot, ddof=1)) if sd_pred > 0 else float("nan"),
              "population_est": {"s_K2": s_k2, "MS_E": ms_e, "var_pop_signed": v_pop, "sd_pop": float(np.sqrt(max(v_pop, 0.0))), "var_pop_boot_se": float(vb.std(ddof=1)), "var_pop_boot_mean": float(vb.mean()),
                                 "var_pop_ci95_normal": [float(v_pop - 1.96 * vb.std(ddof=1)), float(v_pop + 1.96 * vb.std(ddof=1))]},
              "quantiles": {q: float(np.quantile(a_k, float(q))) for q in ("0.01", "0.05", "0.5", "0.95", "0.99")}, "max_key": float(a_k.max()), "min_key": float(a_k.min()),
              "share_keys_above_2alpha": float(np.mean(a_k > 2 * alpha)), "share_keys_above_5alpha": float(np.mean(a_k > 5 * alpha)),
              "exact_marginal_if_indep_distinct": ex, "structural_zero": bool(a_k.max() == 0.0 and ex == 0.0),
              "level_values": [round(float(x), 7) for x in a_k]}
        out["levels"][str(alpha)] = lv
    # ---- Study 2's additions (after Study 1's fields are complete; they read pe and the rejection tables only) ----
    sims = None
    if sim_shift and colouring == "independent":
        sims, sim_info = simulated_shift(pe["wz"], max(pe["rho_bar"], 0.0), "kgw", g, np.random.default_rng(rng.integers(0, 2 ** 31)))
        out["simulated_shift"] = sim_info
    for alpha in alphas:
        z_a = norm.isf(alpha); lv = out["levels"][str(alpha)]
        tau = z_a - pe["mu_i"][keep]
        gen = mixture_gaussian_closed(pe["mu_delta"], max(pe["rho_bar"], 0.0), tau, pe["sigma_model2"], N_eff, tol=pe["sigma_tol"])
        lv["pred_gaussian_shift_per_text"] = gen                                     # the per-text-threshold closed form; equals Study 1's closed form when tau is constant
        lv["pred_per_text_vs_closed_form_abs_diff_sd"] = float(abs(gen["sd_cond"] - lv["pred_first_order"]["sd_cond"]))
        if sims is not None:
            ps = mixture_general(sims, np.full(len(sims), 1.0 / len(sims)), tau, pe["sigma_model2"], N_eff, tol=pe["sigma_tol"])
            lv["pred_simulated_shift"] = ps
            lv["ratio_obs_over_pred_simulated_shift"] = float(lv["sd_obs_conditional"] / ps["sd_cond"]) if ps["sd_cond"] > 0 else float("nan")
        if deployer:
            lv["deployer_crossed"] = crossed_bootstrap(z > z_a, alpha, np.random.default_rng(rng.integers(0, 2 ** 31)))
    return compact_levels(out)


def gumbel_cell_statistics(inc, sums, chain, alphas, rng, deployer=False, sim_shift=True, B_text=TEXT_BOOT_PROD):
    """All per-cell outputs for the Gumbel-max family. sums: N x K sums of the retained positions' scores. The per-text test is the
    exact Gamma(M_i, 1) upper tail at level alpha (reject iff S_i exceeds the Gamma quantile); in z-units (S - M)/sqrt(M) the
    threshold is per text. Fields mirror the red-green cells where the quantities correspond."""
    pe = population_estimates_score(inc, chain, rng, 1.0, B=B_text)
    N = inc.shape[0]; out = {"family": "gumbel", "N": int(N), "levels": {}}
    if pe is None:
        out.update({"N_eff": 0, "frac_M0": 1.0, "flag": "no text has a retained tuple: no detection possible (M = 0 everywhere)"}); return out
    M, keep, N_eff = pe["M"], pe["keep"], pe["N_eff"]; K = sums.shape[1]; Mk = M[keep]
    out.update({"N_eff": N_eff, "frac_M0": float(1 - keep.mean()), "mean_M": float(Mk.mean()), "min_M": int(Mk.min()), "max_M": int(Mk.max()),
                "M_quantiles": {q: float(np.quantile(Mk, float(q))) for q in ("0.05", "0.5", "0.95")},
                "coverage": {"distinct_retained_tuples": int((inc.getnnz(axis=0) > 0).sum())}})
    z = (sums[keep] - Mk[:, None]) / np.sqrt(Mk)[:, None]
    sbar = (sums[keep] / Mk[:, None]).mean(axis=0)                         # per-key mean score over texts (E = 1 exactly)
    zbar = z.mean(axis=0)
    kb = rng.integers(0, K, size=(C.BOOT_KEYS, K))
    idq = pe["identity_q"]; terms = (sbar - 1.0) ** 2; s0 = float(terms.mean())
    mu4 = idq["A4"] * EXP_KAPPA4 + 3 * idq["var"] ** 2; s0_se = float(np.sqrt(max(mu4 - idq["var"] ** 2, 0.0) / K))
    r3_tol = float(C.ZERO_REL * max(idq["A"], 1e-300))
    out["s_bar"] = {"mean": float(sbar.mean()), "exact_mean": 1.0, "var_across_keys": float(sbar.var(ddof=1)), "var_boot_ci95": [float(x) for x in np.quantile(sbar[kb].var(axis=1, ddof=1), [0.025, 0.975])],
                    "var_known_mean": s0, "var_known_mean_se": s0_se, "se_method": "exact fourth moment (Exp(1) cumulant 6)", "exact_var_own_colouring": idq["var"], "r3_tolerance": r3_tol,
                    "observed_sample_constancy": bool(float(terms.max() - terms.min()) <= r3_tol), "structural_zero": bool(idq["structural_zero"]), "values": [round(float(x), 7) for x in sbar]}
    out["zbar"] = {"mean": float(zbar.mean()), "var_across_keys": float(zbar.var(ddof=1)), "var_boot_ci95": [float(x) for x in np.quantile(zbar[kb].var(axis=1, ddof=1), [0.025, 0.975])], "values": [round(float(x), 6) for x in zbar]}
    zv = z.var(axis=0, ddof=1) if N_eff > 1 else np.full(K, np.nan)
    out["z_var_within_key"] = {"mean_over_keys": float(np.nanmean(zv)), "min": float(np.nanmin(zv)), "max": float(np.nanmax(zv))}
    out["identity_q"] = pe["identity_q"]; out["identity_z"] = pe["identity_z"]
    out["population"] = {k: pe[k] for k in ("rho_bar", "rho_bar_boot_se", "A_q_between", "A_q_between_boot_se", "var_zbar_exact_boot_se", "A_q_realised_boot_se", "mean_var_text_z", "mean_A_q_text", "mu_delta", "sigma_model2", "sigma_tol")}
    out["population"].update({"text_bootstrap_B": int(B_text), "var_zbar_exact": pe["identity_z"]["var"], "A_q_realised": pe["identity_q"]["A"], "sd_zshift_pop": float(np.sqrt(max(pe["rho_bar"], 0.0))) if np.isfinite(pe["rho_bar"]) else float("nan")})
    pair = pairwise_gaussian_gumbel(pe, alphas, rng)
    out["covariance_heterogeneity"] = pair["heterogeneity"] if pair else None
    sims = None
    if sim_shift:
        sims, sim_info = simulated_shift(pe["wz"], max(pe["rho_bar"], 0.0), "gumbel", None, np.random.default_rng(rng.integers(0, 2 ** 31))); out["simulated_shift"] = sim_info
    for alpha in alphas:
        t_i = gamma_threshold_z(alpha, Mk); rej = z > t_i[:, None]; a_k = rej.mean(axis=0)
        sd_obs = float(a_k.std(ddof=1)); boots = a_k[kb].std(axis=1, ddof=1)
        pred = mixture_gaussian_closed(0.0, max(pe["rho_bar"], 0.0), t_i, pe["sigma_model2"], N_eff, tol=pe["sigma_tol"]); pred_unit = mixture_gaussian_closed(0.0, max(pe["rho_bar"], 0.0), t_i, 1.0, N_eff)
        sd_pred = pred["sd_cond"]; ratio_boot = boots / sd_pred if sd_pred > 0 else np.full(C.BOOT_KEYS, np.nan)
        s_k2, ms_e, v_pop = C.twoway_population_variance(rej.astype(np.float64)); vb = C.twoway_bootstrap(rej.astype(np.float64), rng)
        lv = {"key_mean_level": float(a_k.mean()), "unconditional_rate": float(a_k.mean() * N_eff / N), "se_conditional_on_texts": float(sd_obs / np.sqrt(K)),
              "r2_kl_pbound": C.kl_chernoff_pbound(float(a_k.mean()), float(alpha), K),      # exact given the texts under the distinct rule: continuous scores give level alpha for every text
              "pred_pairwise_gaussian": pair["by_alpha"][str(alpha)] if pair else None,
              "sd_obs_conditional": sd_obs, "sd_obs_boot_ci95": [float(x) for x in np.quantile(boots, [0.025, 0.975])], "sd_obs_boot_se": float(boots.std(ddof=1)),
              "pred_first_order": pred, "pred_unit_sigma": pred_unit, "ratio_obs_over_pred": float(sd_obs / sd_pred) if sd_pred > 0 else float("nan"),
              "ratio_boot_ci95": [float(x) for x in np.nanquantile(ratio_boot, [0.025, 0.975])] if sd_pred > 0 else [float("nan")] * 2, "ratio_boot_se": float(np.nanstd(ratio_boot, ddof=1)) if sd_pred > 0 else float("nan"),
              "population_est": {"s_K2": s_k2, "MS_E": ms_e, "var_pop_signed": v_pop, "sd_pop": float(np.sqrt(max(v_pop, 0.0))), "var_pop_boot_se": float(vb.std(ddof=1)), "var_pop_boot_mean": float(vb.mean()),
                                 "var_pop_ci95_normal": [float(v_pop - 1.96 * vb.std(ddof=1)), float(v_pop + 1.96 * vb.std(ddof=1))]},
              "exact_marginal_if_distinct": float(alpha), "structural_zero": False, "threshold_z_mean": float(t_i.mean()), "threshold_z_min": float(t_i.min()), "threshold_z_max": float(t_i.max()),
              "level_values": [round(float(x), 7) for x in a_k]}
        lv.update(deployer_view(a_k, alpha))
        if sims is not None:
            ps = mixture_general(sims, np.full(len(sims), 1.0 / len(sims)), t_i, pe["sigma_model2"], N_eff, tol=pe["sigma_tol"]); lv["pred_simulated_shift"] = ps
            lv["ratio_obs_over_pred_simulated_shift"] = float(sd_obs / ps["sd_cond"]) if ps["sd_cond"] > 0 else float("nan")
        if deployer:
            lv["deployer_crossed"] = crossed_bootstrap(rej, alpha, np.random.default_rng(rng.integers(0, 2 ** 31)))
        out["levels"][str(alpha)] = lv
    return compact_levels(out)
