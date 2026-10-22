"""Study 1 core (v6, after R03 round 4): synthetic text laws, (h+1)-tuple retention rules, the two colouring models at a
common green probability g = floor(gamma V)/V, the red-green z-test centred at the requested gamma, the exact across-key
identities for any tuple weights, the first-order (normal-mixture) predictor of the across-key dispersion of the level,
and the per-cell statistics: (a) the primary target conditional on the realised texts (the observed across-key SD of the
per-key level against the predictor, with key-bootstrap intervals), (b) the population diagnostic (the balanced two-way
variance components with a two-way bootstrap), (c) the population mean-shift variance estimated without the finite-text
floor (the average pairwise across-key covariance of two texts' scores), with text-bootstrap errors, (d) the pairwise
Gaussian predictor on a text subsample (the full covariance structure; a diagnostic for the common-factor assumption),
(e) the KL-Chernoff bound for the simulator check R2 and the known-mean variance estimator for R3.
The predictor in (a) is a moment-matched common-factor approximation: across keys one Gaussian shift common to all texts,
residuals independent across texts with one variance; its inputs are exact second moments from the identities, its
structure is an assumption (protocol v0.3 section 3). Pure NumPy/SciPy; deterministic given the seeds.
"""
import numpy as np
import scipy.sparse as sp
from scipy.special import owens_t
from scipy.stats import norm, binom

MASK = np.uint64(0xFFFFFFFFFFFFFFFF)
C1, C2, C3 = np.uint64(0x9E3779B97F4A7C15), np.uint64(0xBF58476D1CE4E5B9), np.uint64(0x94D049BB133111EB)
BOOT_KEYS, BOOT_TWOWAY, BOOT_TEXTS = 200, 100, 30
PAIR_SUBSAMPLE = 300          # texts in the pairwise Gaussian predictor's subsample
R2_PBOUND = 1e-6              # per-check KL-Chernoff bound below which R2 raises the audit flag
R3_GROSS_SE = 6.0             # R3: a known-mean variance estimate beyond this many SEs of its exact value is a gross failure
ZERO_REL = 1e-9               # scale-aware tolerance for structural zeros (relative to the natural scale of the quantity)


def mix64(x):
    with np.errstate(over="ignore"):
        x = np.asarray(x, dtype=np.uint64)
        x = (x ^ (x >> np.uint64(30))) * C2
        x = (x ^ (x >> np.uint64(27))) * C3
        return x ^ (x >> np.uint64(31))


def uniforms(key, ids):
    """U(0,1) deterministic in (key, id): a splitmix64 mix of the id with a mixed key (an ideal-randomness surrogate; the
    protocol states that a hash supplies computational, not statistical, independence)."""
    with np.errstate(over="ignore"):
        k = mix64(np.uint64(key) * C1 + C2)
        x = mix64(np.asarray(ids, dtype=np.uint64) * C3 + k)
    return (x >> np.uint64(11)).astype(np.float64) / float(1 << 53)


def green_fraction(gamma, V):
    """The realised green fraction g = floor(gamma V)/V shared by both colouring models."""
    return float(np.floor(gamma * V) / V)


def degenerate(gamma, V):
    m = int(np.floor(gamma * V))
    return (m == 0 or m == V), m


# ---------------- text laws ----------------
class ZipfIID:
    def __init__(self, V, s):
        self.V, self.s = V, s
        p = (np.arange(1, V + 1, dtype=np.float64)) ** (-s); self.p = p / p.sum()
        self.name = f"zipf_V{V}_s{s}"
        self.collision_unigram = float((self.p ** 2).sum())   # C_0; the (h+1)-tuple collision is C_0^(h+1) for an i.i.d. law
    def sample(self, N, L, rng):
        return rng.choice(self.V, size=(N, L), p=self.p).astype(np.int32)
    def collision_h(self, h):
        return self.collision_unigram ** (h + 1)


class SupportUniform:
    """Control law for T1's saturation: uniform over the first s tokens of a V-token vocabulary (the colouring is over all
    V tokens; the texts use s of them). Analytic limits at h = 0 under the all-distinct-token rule once every text covers
    the support: fixed-size g(1-g)(V-s)/(s(V-1)); independent g(1-g)/s (gate v0.3, residual-gap item 3)."""
    def __init__(self, V, s_support):
        self.V, self.s_support = V, s_support; self.name = f"support_V{V}_s{s_support}"
    def sample(self, N, L, rng):
        return rng.integers(0, self.s_support, size=(N, L)).astype(np.int32)
    def collision_h(self, h):
        return (1.0 / self.s_support) ** (h + 1)


class MarkovZipf:
    """First-order chain: from token c, with probability 1 - eps the next token is drawn from c's support (S tokens with
    Zipf(s) weights over support rank; supports are a seeded draw of S distinct tokens from the global Zipf law),
    otherwise from the global Zipf law. Started from the global law and burnt in for `burn` steps, which are dropped;
    the chain is then close to, not exactly at, stationarity (stated in the protocol)."""
    def __init__(self, V, S, eps, s, support_seed=20261010, burn=64):
        self.V, self.S, self.eps, self.s, self.burn = V, S, eps, s, burn
        p = (np.arange(1, V + 1, dtype=np.float64)) ** (-s); self.p = p / p.sum()
        r = np.random.default_rng(support_seed)
        self.support = np.stack([r.choice(V, size=S, replace=False, p=self.p) for _ in range(V)]).astype(np.int32)
        w = (np.arange(1, S + 1, dtype=np.float64)) ** (-s); self.wcdf = np.cumsum(w / w.sum())
        self.name = f"markov_V{V}_S{S}_eps{eps}_s{s}"
    def sample(self, N, L, rng):
        T = L + self.burn; X = np.empty((N, T), dtype=np.int32)
        X[:, 0] = rng.choice(self.V, size=N, p=self.p)
        for t in range(1, T):
            u = rng.random(N); glob = rng.random(N) < self.eps
            rank = np.searchsorted(self.wcdf, u)
            nxt = self.support[X[:, t - 1], np.minimum(rank, self.S - 1)]
            nxt[glob] = rng.choice(self.V, size=int(glob.sum()), p=self.p)
            X[:, t] = nxt
        return X[:, self.burn:]
    def collision_h(self, h):
        return None   # no closed form used


class TwoToken:
    def __init__(self, p_stay):
        self.V, self.p_stay = 2, p_stay; self.name = f"twotoken_p{p_stay}"
    def sample(self, N, L, rng):
        X = np.empty((N, L), dtype=np.int32); X[:, 0] = rng.integers(0, 2, size=N)
        for t in range(1, L):
            flip = rng.random(N) >= self.p_stay; X[:, t] = np.where(flip, 1 - X[:, t - 1], X[:, t - 1])
        return X
    def collision_h(self, h):
        return None


# ---------------- tuples and retention ----------------
def context_ids(X, h):
    N, L = X.shape
    if h == 0:
        return np.zeros((N, L), dtype=np.uint64)
    cid = np.zeros((N, L), dtype=np.uint64)
    with np.errstate(over="ignore"):
        for j in range(1, h + 1):
            tok = np.zeros((N, L), dtype=np.uint64); tok[:, j:] = X[:, :-j].astype(np.uint64) + np.uint64(1)
            cid = mix64(cid * C1 + tok * C2 + np.uint64(j))
    return cid


def tuple_ids(cid, X):
    with np.errstate(over="ignore"):
        return mix64(cid * C2 + (X.astype(np.uint64) + np.uint64(1)) * C1)


class Chain:
    """One (law, h) chain: N texts of length L_max, the tuple dictionary, context classes, and prefix-stable retention
    masks (the first occurrence of a tuple or a context among positions < L is its first occurrence overall whenever it
    lies before L, so every L is a column prefix of the L_max mask). The texts are a deterministic function of (law, seed),
    so chains of one law at different widths share their texts when given the same seed."""
    def __init__(self, law, h, N, L_max, seed):
        self.law, self.h, self.N, self.L_max = law, h, N, L_max
        rng = np.random.default_rng(seed)
        self.X = law.sample(N, L_max, rng)
        self.cid = context_ids(self.X, h); self.tid = tuple_ids(self.cid, self.X)
        valid = np.zeros((N, L_max), dtype=bool); valid[:, h:] = True
        self.valid = valid
        self.D, inv = np.unique(self.tid[valid], return_inverse=True)
        self.col = np.full((N, L_max), -1, dtype=np.int64); self.col[valid] = inv
        self.D_cid = np.empty(len(self.D), dtype=np.uint64); self.D_tok = np.empty(len(self.D), dtype=np.int32)
        self.D_cid[inv] = self.cid[valid]; self.D_tok[inv] = self.X[valid]
        self.ctx, self.D_ctx = np.unique(self.D_cid, return_inverse=True); self.n_ctx = len(self.ctx)
        self.mask = {"raw": valid.copy()}
        L = L_max
        rows = np.repeat(np.arange(N), L)[valid.ravel()]; cols_all = np.tile(np.arange(L), N)[valid.ravel()]; c = self.col[valid]
        for rule, key in (("distinct", rows.astype(np.int64) * len(self.D) + c), ("first", rows.astype(np.int64) * self.n_ctx + self.D_ctx[c])):
            order = np.lexsort((cols_all, key)); ks = key[order]; first = np.r_[True, ks[1:] != ks[:-1]]
            m = np.zeros((N, L), dtype=bool); m[rows[order[first]], cols_all[order[first]]] = True; self.mask[rule] = m
        self._P = None

    def incidence(self, L, rule):
        N = self.N; m = self.mask[rule][:, :L]
        rows = np.repeat(np.arange(N), L)[m.ravel()]; c = self.col[:, :L][m]
        return sp.csr_matrix((np.ones(len(c), dtype=np.float64), (rows, c)), shape=(N, len(self.D)))

    def context_indicator(self):
        """|D| x n_ctx sparse 0/1 matrix mapping each tuple to its context class."""
        if self._P is None:
            self._P = sp.csr_matrix((np.ones(len(self.D)), (np.arange(len(self.D)), self.D_ctx)), shape=(len(self.D), self.n_ctx))
        return self._P


# ---------------- colourings ----------------
def colour_independent(chain, keys, gamma, V):
    """|D| x K uint8: green iff U(key, tuple id) < g, with g = floor(gamma V)/V (the same marginal as the fixed model)."""
    g = green_fraction(gamma, V)
    out = np.empty((len(chain.D), len(keys)), dtype=np.uint8)
    for j, k in enumerate(keys):
        out[:, j] = uniforms(k, chain.D) < g
    return out


def colour_fixed(chain, keys, gamma, V):
    """|D| x K uint8 under the fixed-size model: per context class with j queried tokens the number of greens is
    Hypergeometric(V, m, j) and the green ones are the j tokens with the smallest U(key, id). The hypergeometric draws are
    seeded by (key, 20261010) and consumed in the chain's context traversal order, so a key's draw for a context is
    paired across lengths and rules within a chain but is not the same across chains (stated in the protocol)."""
    m = int(np.floor(gamma * V))
    D_ctx = chain.D_ctx; n_ctx = chain.n_ctx
    j_per_ctx = np.bincount(D_ctx, minlength=n_ctx); starts = np.r_[0, np.cumsum(j_per_ctx)[:-1]]
    out = np.empty((len(chain.D), len(keys)), dtype=np.uint8)
    for jx, k in enumerate(keys):
        rng = np.random.default_rng([int(k), 20261010])
        if 0 < m < V:
            g = rng.hypergeometric(m, V - m, j_per_ctx)
        else:
            g = j_per_ctx.copy() if m == V else np.zeros(n_ctx, dtype=np.int64)
        u = uniforms(k, chain.D); o = np.lexsort((u, D_ctx))
        rank = np.arange(len(o)) - np.repeat(starts, j_per_ctx)
        green = np.empty(len(o), dtype=np.uint8); green[o] = (rank < np.repeat(g, j_per_ctx)).astype(np.uint8)
        out[:, jx] = green
    return out


class PackedColours:
    """All K colourings of a chain packed to bits, computed once per (chain, colouring, gamma); chunk must be a multiple of 8."""
    def __init__(self, chain, keys, gamma, colouring, V, chunk=48):
        if chunk % 8:
            raise ValueError("PackedColours: chunk must be a multiple of 8 (byte alignment)")
        self.K = len(keys); self.chunk = chunk
        self.packed = np.zeros((len(chain.D), (self.K + 7) // 8), dtype=np.uint8)
        for c0 in range(0, self.K, chunk):
            ks = keys[c0:c0 + chunk]
            cols = colour_fixed(chain, ks, gamma, V) if colouring == "fixed" else colour_independent(chain, ks, gamma, V)
            bits = np.packbits(cols, axis=1, bitorder="little")
            self.packed[:, c0 // 8:c0 // 8 + bits.shape[1]] = bits
    def chunk_cols(self, c0):
        ks = min(self.chunk, self.K - c0)
        return np.unpackbits(self.packed[:, c0 // 8:(c0 + ks + 7) // 8], axis=1, bitorder="little")[:, :ks]


# ---------------- identities, weights, population estimates ----------------
def identity_for_weights(w, D_ctx, n_ctx, V, gamma):
    """Exact across-key variance of sum_u w(u) G_K(u) for ANY real weights w: fixed-size g(1-g)/(V-1)(V A - B) and
    independent g(1-g) A, with A = sum w^2 and B = sum_c w(c)^2; the ratio (V - 1/C_cond)/(V - 1), C_cond = A/B."""
    g = green_fraction(gamma, V); deg, m = degenerate(gamma, V)
    A = float((w ** 2).sum()); wc = np.bincount(D_ctx, weights=w, minlength=n_ctx); B = float((wc ** 2).sum()); A4 = float((w ** 4).sum())
    # structural zero of the fixed-size variance: V A - B vanishes exactly when every context class is fully and evenly weighted
    # (for example a fully covered vocabulary at h = 0 with uniform weights); floating cancellation then leaves +-1e-17, so a
    # scale-aware tolerance recognises it (R03 round 2, F15)
    VA_B = V * A - B; sz_fixed = bool(A == 0.0 or VA_B <= ZERO_REL * V * A)
    var_fixed = 0.0 if (sz_fixed or V <= 1) else g * (1 - g) / (V - 1) * VA_B
    var_indep = g * (1 - g) * A
    C_cond = A / B if B > 0 else float("nan")
    return {"g": g, "m": m, "A": A, "B": B, "A4": A4, "C_cond": C_cond, "var_fixed": float(var_fixed), "var_indep": float(var_indep),
            "ratio_fixed_over_indep": float(var_fixed / var_indep) if var_indep > 0 else float("nan"),
            "exact_ratio_formula": float((V - 1.0 / C_cond) / (V - 1)) if (V > 1 and np.isfinite(C_cond) and C_cond > 0) else float("nan"),
            "degenerate": bool(deg or A == 0.0), "structural_zero_fixed": sz_fixed, "structural_zero_indep": bool(A == 0.0)}


def per_text_terms(inc, chain, gamma):
    """Per text: M_i, the z-weight collision A_i^z = sum_u n_iu^2/(M_i gamma(1-gamma)), its context term B_i^z, and the
    q-weight collision A_i^q = sum_u (n_iu/M_i)^2 (zeros where M_i = 0)."""
    M = np.asarray(inc.sum(axis=1)).ravel(); keep = M > 0
    s2 = np.asarray(inc.multiply(inc).sum(axis=1)).ravel()
    inc_ctx = inc @ chain.context_indicator(); s2c = np.asarray(inc_ctx.multiply(inc_ctx).sum(axis=1)).ravel()
    denom = np.where(keep, M * gamma * (1 - gamma), 1.0)
    return M, keep, np.where(keep, s2 / denom, 0.0), np.where(keep, s2c / denom, 0.0), np.where(keep, s2 / np.maximum(M, 1) ** 2, 0.0)


def var_text_z(Az, Bz, V, gamma, colouring):
    """Exact across-key variance of one text's z under the cell's colouring (identity at the text's own z-weights)."""
    g = green_fraction(gamma, V)
    if colouring == "fixed":
        return g * (1 - g) / (V - 1) * (V * Az - Bz) if V > 1 else np.zeros_like(Az)
    return g * (1 - g) * Az


def population_estimates(inc, chain, gamma, V, colouring, rng, B=BOOT_TEXTS):
    """Document-averaged weights (q: n_iu/M_i; z: n_iu/sqrt(M_i gamma(1-gamma))) over texts with M > 0, the exact identities
    at those realised weights, and the POPULATION estimates that remove the finite-text floor: rho_bar, the average
    pairwise across-key covariance of two texts' z (an unbiased estimate of the across-key variance of the population mean
    shift E_X[z | key]), and A_between, the same construction for the q-weight collision (unbiased for the population
    collision sum_u p(u)^2 of the retained-tuple law under i.i.d. texts). Text-bootstrap SEs of both (B resamples).
    Also mu_delta = (g - gamma) sum_u w_z(u), the exact across-key mean of the z-shift (zero when gamma V is an integer)."""
    M, keep, Az, Bz, Aq = per_text_terms(inc, chain, gamma); N_eff = int(keep.sum()); N = inc.shape[0]
    if N_eff == 0:
        return None
    Wz = sp.diags(np.where(keep, 1.0 / np.sqrt(np.maximum(M, 1) * gamma * (1 - gamma)), 0.0)) @ inc
    Wq = sp.diags(np.where(keep, 1.0 / np.maximum(M, 1), 0.0)) @ inc
    Vi = var_text_z(Az, Bz, V, gamma, colouring); own = "var_fixed" if colouring == "fixed" else "var_indep"
    g = green_fraction(gamma, V)

    def est(a):
        n = float(a[keep].sum())
        wz = np.asarray(Wz.T @ a).ravel() / n; wq = np.asarray(Wq.T @ a).ravel() / n
        idz = identity_for_weights(wz, chain.D_ctx, chain.n_ctx, V, gamma); idq = identity_for_weights(wq, chain.D_ctx, chain.n_ctx, V, gamma)
        meanV = float(a @ Vi) / n; meanAq = float(a @ Aq) / n
        rho = n / (n - 1) * (idz[own] - meanV / n) if n > 1 else float("nan")
        Ab = n / (n - 1) * (idq["A"] - meanAq / n) if n > 1 else float("nan")
        return wz, wq, idz, idq, meanV, meanAq, rho, Ab
    a0 = keep.astype(np.float64)
    wz, wq, idz, idq, meanV, meanAq, rho, Ab = est(a0)
    mu_i = np.where(keep, (g - gamma) * np.sqrt(np.maximum(M, 1) / (gamma * (1 - gamma))), 0.0)   # per-text across-key mean of z
    idx = np.flatnonzero(keep); boots = []
    if len(idx) > 1:
        for _ in range(B):
            a = np.bincount(rng.choice(idx, size=len(idx), replace=True), minlength=N).astype(np.float64)
            r = est(a); boots.append((r[6], r[7], r[2][own], r[3]["A"]))
    bt = np.array(boots) if boots else np.full((2, 4), np.nan)
    return {"wz": wz, "wq": wq, "identity_z": idz, "identity_q": idq, "N_eff": N_eff, "M": M, "keep": keep,
            "mean_var_text_z": meanV, "mean_A_q_text": meanAq, "rho_bar": float(rho), "A_q_between": float(Ab),
            "rho_bar_boot_se": float(np.nanstd(bt[:, 0], ddof=1)), "A_q_between_boot_se": float(np.nanstd(bt[:, 1], ddof=1)),
            "var_zbar_exact_boot_se": float(np.nanstd(bt[:, 2], ddof=1)), "A_q_realised_boot_se": float(np.nanstd(bt[:, 3], ddof=1)),
            "mu_delta": float((g - gamma) * wz.sum()),
            # the key-averaged within-key sample variance (ddof = 1) across the fixed texts is exactly
            # mean_i V_i - rho_bar + N/(N-1) mean_i (mu_i - mu_bar)^2 (R03 round 2, F12), mu_i = (g - gamma) sum_u w_i(u) = mean_i-average mu_bar = mu_delta
            "sigma_model2": float(meanV - rho + N_eff / (N_eff - 1) * float(a0 @ ((mu_i - (g - gamma) * wz.sum()) ** 2)) / N_eff) if (np.isfinite(rho) and N_eff > 1) else float("nan"),
            "sigma_tol": float(ZERO_REL * max(meanV, 1e-300)),
            "Az_text": Az, "Vi": Vi, "Wz": Wz, "mu_i": mu_i}


def mixture_predictor(mu, var, alpha, N_eff, sigma2=1.0, tol=0.0):
    """The common-factor approximation's prediction of the across-key dispersion of the level, in closed form (R03 round 3, F19):
    per key alpha_k = Phi_bar((z_a - delta_k)/sigma) with delta_k ~ N(mu, var) across keys (var <= 0 taken as no dispersion). With
    Z = delta + sigma eps ~ N(mu, var + sigma^2): E[alpha_k] = Phi_bar(t), t = (z_a - mu)/sqrt(var + sigma^2) (the convolution), and
    E[alpha_k^2] = P(Z_1 > z_a, Z_2 > z_a) for two texts sharing delta, a bivariate normal orthant probability with correlation
    r = var/(var + sigma^2) (Owen's T); var_pop = E[alpha^2] - E[alpha]^2; the conditional-on-texts variance adds the finite-text term
    E[alpha_k (1-alpha_k)]/N_eff (texts independent given the key). sigma = 0 gives r = 1 (alpha_k a 0/1 indicator; finite-text term 0);
    var = 0 gives r = 0. sd_linear is the delta-method limit phi((z_a-mu)/sigma) sqrt(var)/sigma. A materially negative or non-finite
    sigma2 is flagged, not replaced (F13)."""
    z_a = norm.isf(alpha); flags = []
    if not np.isfinite(sigma2):
        flags.append("sigma2_nonfinite"); sigma2 = 0.0
    elif sigma2 < -abs(tol):
        flags.append("sigma2_negative"); sigma2 = 0.0
    elif sigma2 < abs(tol):
        sigma2 = 0.0
    var = max(float(var), 0.0); sigma2 = float(sigma2); tot = var + sigma2
    if tot <= 0.0:
        mean = float(mu > z_a); e2 = mean; sd_lin = float("nan")
    else:
        t = (z_a - mu) / np.sqrt(tot); r = var / tot
        mean = float(norm.sf(t)); e2 = float(bvn_upper(t, t, r))
        sd_lin = float(norm.pdf((z_a - mu) / np.sqrt(sigma2)) * np.sqrt(var) / np.sqrt(sigma2)) if sigma2 > 0 else float("nan")
    var_pop = max(float(e2 - mean ** 2), 0.0); floor = max(float(mean - e2), 0.0) / N_eff
    return {"mean_level": float(mean), "var_pop": var_pop, "sd_pop": float(np.sqrt(var_pop)), "floor": float(floor), "sd_cond": float(np.sqrt(var_pop + floor)),
            "theory_share": float(var_pop / (var_pop + floor)) if var_pop + floor > 0 else 0.0, "sd_linear_pop": sd_lin, "sigma2": sigma2, "flags": flags}


def bvn_upper(a, b, rho):
    """P(X > a, Y > b) for a standard bivariate normal pair with correlation rho (vectorised; Owen's T function). rho = +-1 handled."""
    a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64); rho = np.clip(np.asarray(rho, dtype=np.float64), -1.0, 1.0)
    out = np.empty(np.broadcast(a, b, rho).shape); a, b, rho = np.broadcast_arrays(a, b, rho)
    one = rho >= 1 - 1e-12; mone = rho <= -1 + 1e-12; mid = ~(one | mone)
    out[one] = norm.sf(np.maximum(a, b))[one]
    out[mone] = np.maximum(0.0, 1.0 - norm.cdf(a) - norm.cdf(b))[mone]            # Y = -X: X > a and -X > b
    if mid.any():
        h = np.where(a[mid] == 0, 1e-12, a[mid]); k = np.where(b[mid] == 0, 1e-12, b[mid]); r = rho[mid]; q = np.sqrt(1 - r * r)
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            ah = (k - r * h) / (h * q); ak = (h - r * k) / (k * q)
        beta = np.where((h * k > 0) | ((h * k == 0) & (h + k >= 0)), 0.0, 0.5)
        cdf2 = 0.5 * (norm.cdf(h) + norm.cdf(k)) - owens_t(h, ah) - owens_t(k, ak) - beta       # P(X <= h, Y <= k)
        out[mid] = np.clip(1.0 - norm.cdf(h) - norm.cdf(k) + cdf2, 0.0, 1.0)
    return out


def pairwise_gaussian_predictor(pe, chain, gamma, V, colouring, alphas, rng, n_s=PAIR_SUBSAMPLE):
    """On a random subsample of n_s texts: the exact across-key covariance matrix of their scores from the identities (the
    bilinear form of the cell's colouring), the per-text means mu_i, and under a Gaussian model with THAT covariance the
    variance of the empirical rejection fraction, Var = mean_i pi_i(1-pi_i)/N_eff + (1 - 1/N_eff) mean_{i != j} [P(both reject) -
    pi_i pi_j]; the bivariate orthant probabilities through Owen's T. No common-factor or homogeneity assumption (R03 round 2, F12).
    Also the covariance heterogeneity diagnostics (coefficient of variation of the pairwise covariances; the correlation quantiles)."""
    g = green_fraction(gamma, V); keep = pe["keep"]; idx = np.flatnonzero(keep); N_eff = len(idx)
    if N_eff < 3:
        return None
    # two disjoint subsamples where the texts allow (R03 round 3): the second is a replicate whose difference from the first measures the subsampling error
    perm = rng.permutation(idx); n1 = min(n_s, N_eff); subs = [np.sort(perm[:n1])] + ([np.sort(perm[n1:2 * n1])] if N_eff >= 2 * n1 >= 6 else [])
    results = [_pairwise_one(pe, chain, gamma, V, colouring, alphas, sub, N_eff, g) for sub in subs]
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


def _pairwise_one(pe, chain, gamma, V, colouring, alphas, sub, N_eff, g):
    n = len(sub)
    W = pe["Wz"][sub]                                                   # n x |D| sparse z-weight rows
    G = np.asarray((W @ W.T).todense())
    if colouring == "fixed":
        Wc = W @ chain.context_indicator(); Gc = np.asarray((Wc @ Wc.T).todense()); Cov = g * (1 - g) / (V - 1) * (V * G - Gc) if V > 1 else np.zeros_like(G)
    else:
        Cov = g * (1 - g) * G
    Vi = np.clip(np.diag(Cov), 0.0, None); mu = pe["mu_i"][sub]
    sd = np.sqrt(Vi); ok = sd > 0
    corr = np.zeros_like(Cov); corr[np.ix_(ok, ok)] = Cov[np.ix_(ok, ok)] / np.outer(sd[ok], sd[ok]); corr = np.clip(corr, -1.0, 1.0)
    iu = np.triu_indices(n, 1); c_off = Cov[iu]; r_off = corr[iu]
    het = {"n_subsample": int(n), "pair_cov_mean": float(c_off.mean()), "pair_cov_cv": float(c_off.std() / c_off.mean()) if c_off.mean() > 0 else float("nan"),
           "pair_corr_quantiles": {q: float(np.quantile(r_off, float(q))) for q in ("0.5", "0.9", "0.99")}, "pair_corr_max": float(r_off.max()),
           "share_zero_variance_texts": float(1 - ok.mean())}
    out = {}
    for alpha in alphas:
        z_a = norm.isf(alpha)
        t = np.where(ok, (z_a - mu) / np.where(ok, sd, 1.0), np.inf); pi = np.where(ok, norm.sf(t), (mu > z_a).astype(float))
        both = bvn_upper(t[iu[0]], t[iu[1]], r_off)
        zero_pairs = ~(ok[iu[0]] & ok[iu[1]])
        if zero_pairs.any():
            both[zero_pairs] = (pi[iu[0]] * pi[iu[1]])[zero_pairs]       # a degenerate text's indicator is deterministic: independent of the rest
        cov_ind = both - pi[iu[0]] * pi[iu[1]]
        var = float((pi * (1 - pi)).mean() / N_eff + (1 - 1.0 / N_eff) * cov_ind.mean())
        out[str(alpha)] = {"sd_cond": float(np.sqrt(max(var, 0.0))), "var_signed": var, "mean_level": float(pi.mean()), "floor_part": float((pi * (1 - pi)).mean() / N_eff), "offdiag_part": float((1 - 1.0 / N_eff) * cov_ind.mean())}
    return {"heterogeneity": het, "by_alpha": out}


def kl_bernoulli(a, m):
    """KL(a || m) for Bernoulli parameters, with the 0 log 0 = 0 conventions; inf when m is 0 or 1 and a differs."""
    if m <= 0.0:
        return 0.0 if a <= 0.0 else float("inf")
    if m >= 1.0:
        return 0.0 if a >= 1.0 else float("inf")
    t1 = a * np.log(a / m) if a > 0 else 0.0; t2 = (1 - a) * np.log((1 - a) / (1 - m)) if a < 1 else 0.0
    return float(t1 + t2)


def kl_chernoff_pbound(abar, mu, K):
    """Hoeffding (1963, Theorem 1): for i.i.d. X_k in [0, 1] with mean mu, P(X_bar >= mu + t) <= exp(-K KL(mu + t || mu)), and the mirror
    bound for the lower tail. Because the side is chosen after seeing the deviation, the TWO-SIDED bound is returned: min(1, 2 exp(-K KL)),
    so that flagging below a threshold p gives a per-check false-audit probability of at most p (R03 round 3, F18)."""
    if abar == mu:
        return 1.0
    return float(min(1.0, 2.0 * np.exp(-K * kl_bernoulli(abar, mu))))


# ---------------- detector and statistics ----------------
def z_scores(counts, M, gamma):
    with np.errstate(divide="ignore", invalid="ignore"):
        return (counts - gamma * M[:, None]) / np.sqrt(M[:, None] * gamma * (1 - gamma))


def exact_marginal_level_distinct_independent(M, g, gamma, alpha):
    """Independent colours at g and distinct retained tuples: G | text ~ Binomial(M, g); the key-mean level of a text is
    P(G > gamma M + z_a sqrt(M gamma (1-gamma))). Returns the mean over texts with M > 0 (exact given the texts)."""
    z_a = norm.isf(alpha); keep = M > 0; Mk = M[keep]
    thr = gamma * Mk + z_a * np.sqrt(Mk * gamma * (1 - gamma))
    return float(np.mean(binom.sf(np.floor(thr), Mk, g)))


def twoway_population_variance(Y):
    """Balanced two-way decomposition of the rejection table Y (texts x keys, 0/1): s_K^2 of the per-key means and the
    residual mean square MS_E; the population across-key variance estimate is s_K^2 - MS_E / N (E[s_K^2] = v_K + v_E/N)."""
    N, K = Y.shape
    rowm = Y.mean(axis=1, keepdims=True); colm = Y.mean(axis=0, keepdims=True); gm = Y.mean()
    res = Y - rowm - colm + gm
    ms_e = float((res ** 2).sum() / ((N - 1) * (K - 1))) if N > 1 and K > 1 else float("nan")
    s_k2 = float(colm.ravel().var(ddof=1)) if K > 1 else float("nan")
    return s_k2, ms_e, s_k2 - ms_e / N


def twoway_bootstrap(Y, rng, B=BOOT_TWOWAY):
    """Two-way bootstrap (texts and keys resampled with replacement) of s_K^2 - MS_E/N, through weighted sums (no table copies)."""
    N, K = Y.shape; out = []
    for _ in range(B):
        a = np.bincount(rng.integers(0, N, size=N), minlength=N).astype(np.float64); b = np.bincount(rng.integers(0, K, size=K), minlength=K).astype(np.float64)
        colsum = a @ Y; rowsum = Y @ b; tot = float(colsum @ b)
        c = colsum / N; r = rowsum / K; m = tot / (N * K)
        ss_e = tot - K * float(a @ (r ** 2)) - N * float(b @ (c ** 2)) + N * K * m * m    # Y is 0/1 so sum Y^2 = tot
        ms_e = ss_e / ((N - 1) * (K - 1)); s_k2 = float(b @ ((c - m) ** 2)) / (K - 1)
        out.append(s_k2 - ms_e / N)
    return np.array(out)


def cell_statistics(inc, counts, chain, gamma, alphas, V, colouring, rng):
    """All per-cell outputs. counts: N x K green counts under the cell's colouring (keys independent draws)."""
    g = green_fraction(gamma, V); deg, m = degenerate(gamma, V)
    pe = population_estimates(inc, chain, gamma, V, colouring, rng)
    N = inc.shape[0]
    out = {"g": g, "m": m, "degenerate": bool(deg), "N": int(N), "levels": {}}
    if pe is None:
        out.update({"N_eff": 0, "frac_M0": 1.0, "flag": "no text has a retained tuple: no detection possible (M = 0 everywhere)"}); return out
    M, keep, N_eff = pe["M"], pe["keep"], pe["N_eff"]; K = counts.shape[1]
    Mk = M[keep]
    out.update({"N_eff": N_eff, "frac_M0": float(1 - keep.mean()), "mean_M": float(Mk.mean()), "min_M": int(Mk.min()), "max_M": int(Mk.max()),
                "M_quantiles": {q: float(np.quantile(Mk, float(q))) for q in ("0.05", "0.5", "0.95")},
                "coverage": {"distinct_retained_tuples": int((inc.getnnz(axis=0) > 0).sum()), "share_of_V_if_h0": float((inc.getnnz(axis=0) > 0).sum() / V) if chain.h == 0 else None}})
    frac = counts[keep] / Mk[:, None]; z = z_scores(counts[keep], Mk, gamma)
    q_hat = frac.mean(axis=0); zbar = z.mean(axis=0)
    kb = rng.integers(0, K, size=(BOOT_KEYS, K))
    # R3's estimator: the known-mean variance s0^2 = mean_k (q_hat_k - E q_hat)^2 with E q_hat = g sum_u w_q(u) exactly; its SE is exact for the
    # independent colouring (fourth central moment of a weighted sum of independent Bernoullis) and a key bootstrap for the fixed colouring
    idq = pe["identity_q"]; Eq = g * float(pe["wq"].sum()); terms = (q_hat - Eq) ** 2; s0 = float(terms.mean())
    own_q = idq["var_fixed"] if colouring == "fixed" else idq["var_indep"]
    r3_tol = float(ZERO_REL * max(g * (1 - g) * idq["A"], 1e-300))      # the scale-aware tolerance R3 applies to differences and to structural zeros
    # observed sample constancy of (q_hat_k - E q_hat)^2 over the keys is RECORDED, never used to override an SE (R03 round 4, F22): a constant
    # sample is a possible draw under either colouring; the SE stays the exact fourth-moment value (independent) or the empirical key bootstrap
    # (fixed), and R3's tolerance-inclusive rule (|diff| <= 6 SE + tol) decides the genuinely constant cases such as the two-token chain at h = 0
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
    out["z_var_within_key"] = {"mean_over_keys": float(np.nanmean(zv)), "min": float(np.nanmin(zv)), "max": float(np.nanmax(zv))}   # sigma_k^2 diagnostic (1 under the first-order model)
    own = "var_fixed" if colouring == "fixed" else "var_indep"
    out["identity_q"] = pe["identity_q"]; out["identity_z"] = pe["identity_z"]
    out["population"] = {k: pe[k] for k in ("rho_bar", "rho_bar_boot_se", "A_q_between", "A_q_between_boot_se", "var_zbar_exact_boot_se", "A_q_realised_boot_se", "mean_var_text_z", "mean_A_q_text", "mu_delta", "sigma_model2")}
    out["population"].update({"var_zbar_exact": pe["identity_z"][own], "A_q_realised": pe["identity_q"]["A"], "sd_zshift_pop": float(np.sqrt(max(pe["rho_bar"], 0.0))) if np.isfinite(pe["rho_bar"]) else float("nan"),
                              "collision_h_analytic": chain.law.collision_h(chain.h) if hasattr(chain.law, "collision_h") else None, "sigma_tol": pe["sigma_tol"]})
    pair = pairwise_gaussian_predictor(pe, chain, gamma, V, colouring, alphas, rng)
    out["covariance_heterogeneity"] = pair["heterogeneity"] if pair else None
    for alpha in alphas:
        z_a = norm.isf(alpha); rej = (z > z_a)
        a_k = rej.mean(axis=0)
        sd_obs = float(a_k.std(ddof=1)); boots = a_k[kb].std(axis=1, ddof=1)
        pred = mixture_predictor(pe["mu_delta"], pe["rho_bar"], alpha, N_eff, pe["sigma_model2"], tol=pe["sigma_tol"])   # the common-factor predictor (sigma from the identities; flags on a zero or negative sigma^2)
        pred_unit = mixture_predictor(pe["mu_delta"], pe["rho_bar"], alpha, N_eff, 1.0)                                  # the unit-variance variant (diagnostic)
        sd_pred = pred["sd_cond"]
        ratio_boot = boots / sd_pred if sd_pred > 0 else np.full(BOOT_KEYS, np.nan)
        s_k2, ms_e, v_pop = twoway_population_variance(rej.astype(np.float64))
        vb = twoway_bootstrap(rej.astype(np.float64), rng)
        ex = exact_marginal_level_distinct_independent(M, g, gamma, alpha)
        lv = {"key_mean_level": float(a_k.mean()), "unconditional_rate": float(a_k.mean() * N_eff / N),
              "se_conditional_on_texts": float(sd_obs / np.sqrt(K)),
              "r2_kl_pbound": kl_chernoff_pbound(float(a_k.mean()), ex, K),           # R2: Hoeffding's KL bound on this deviation of the key-mean (exact for any K)
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
    return out


def support_limits(V, s_support, gamma):
    """Analytic limits for the support law under the all-distinct-token rule at h = 0 once every text covers the support:
    the q-weight variances (gate item 3) and the z-shift variances they imply with M = s_support (rho = s * var_q / (gamma (1-gamma)))."""
    g = green_fraction(gamma, V); vf = g * (1 - g) * (V - s_support) / (s_support * (V - 1)); vi = g * (1 - g) / s_support
    return {"fixed_h0_distinct_limit_var": vf, "indep_h0_distinct_limit_var": vi,
            "fixed_h0_distinct_limit_rho": s_support * vf / (gamma * (1 - gamma)), "indep_h0_distinct_limit_rho": s_support * vi / (gamma * (1 - gamma))}
