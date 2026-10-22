"""Labelled side computation (2026-10-18; from checkpoint R09 round 3, finding F18; NOT pre-registered; no locked output changed;
not pinned by any lock; written before the paper reads the secondary SEs it concerns).

What it concerns. Studies 1 and 2 report a SECONDARY population target: the balanced two-way decomposition v = s_K^2 - MS_E/N of the
per-key rejection table (texts x keys, 0/1) with "a two-way bootstrap SE" from the locked s1_core.twoway_bootstrap (B = 100 resamples
of texts AND keys with replacement, the crossed scheme), used descriptively only (Study 1 §5 and Table 5's note; Study 2 Table 15b:
the "within 2 bootstrap SEs" counts). R09 round 3 (Codex, 2026-10-16, F18) showed, for Study 4's protocol, that the crossed resample of
v is centred at a s_K^2 with a = (K - 1)/K, not at v, and that its spread carries a text-duplication channel; Study 4 adopted a
key-only bootstrap (D17). This script quantifies what that means for the committed Study 1 and Study 2 records, in three parts.
 (1) STORED FIELDS, every live cell and alpha of both studies: the exact centring displacement d = a s_K^2 - v = MS_E/N - s_K^2/K,
     relative to |v| and to the stored crossed SE; the identity check z = (stored bootstrap mean - a s_K^2) / (SE / sqrt(B)); a key-only
     bootstrap SE of s_K^2 from the stored per-key levels (B_KEY resamples of the K keys; the MS_E/N term held fixed, an approximation
     whose accuracy part (2) measures); the normal-theory SE s_K^2 sqrt(2/(K - 1)); and the reports' "within 2 SE" counts recomputed
     with the key-only SE in place of the crossed one.
 (2) REGENERATION on a subset of Study 1 cells: the rejection table rebuilt with the locked code (the same law, chain seed, production
     keys and colouring), the stored population block reproduced through the locked cell_statistics (the regeneration check), and on
     that table the crossed bootstrap (the locked function; a fresh seed; B = 100 and B = 2,000), the exact key-only bootstrap of v
     (keys resampled, MS_E recomputed), the a_k-only approximation of part (1), and a text-only bootstrap (the text channel alone).
 (3) A SYNTHETIC TRUTH CHECK at the studies' sizes (K, N) = (500, 4000) and (1000, 10000): two-way Bernoulli tables from models whose
     population key component v_K is known (a Beta-Bernoulli key effect; a logistic key-by-text model), R replicates each: the empirical
     sampling SD of v against the mean crossed SE (the locked function at the production B = 100) and the mean key-only SE, and the
     coverage of v +- 1.96 SE for v_K under each SE.
Writes (side files only): outputs/study1_v0.3/report/twoway_se_check.json, outputs/study2_v0.1/report/twoway_se_check.json,
        outputs/study1_v0.3/report/twoway_se_check_synthetic.json and the generated memo research/study1/TWOWAY_SE_CHECK_2026-10-18.md
        (every number in the memo is written by this script; none is typed).
Usage: .venv/bin/python research/study1/twoway_se_check.py [--stored-only] [--no-synthetic] [--no-regen] [--replicates-small R] [--replicates-large R]
"""
import hashlib, json, os, pathlib, sys, time, datetime
import numpy as np
from scipy.stats import norm, beta as beta_dist

HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "tools"))
import s1_core as C                      # the locked Study 1 core (read-only use; nothing is written to the record)
import s1_run as R1                      # the locked runner's helpers (make_law, law_name, text_seed_for); its main is not called

S1_CELLS = ROOT / "outputs/study1_v0.3/cells"; S1_RES = ROOT / "outputs/study1_v0.3/results.json"; S1_OUT = ROOT / "outputs/study1_v0.3/report"
S2_CELLS = ROOT / "outputs/study2_v0.1/cells"; S2_RES = ROOT / "outputs/study2_v0.1/results.json"; S2_OUT = ROOT / "outputs/study2_v0.1/report"
MEMO = HERE / "TWOWAY_SE_CHECK_2026-10-18.md"
B_STORED = C.BOOT_TWOWAY          # the locked crossed bootstrap's resample count (100)
B_KEY = 2000                      # key-only resamples in parts (1) and (2)
SALT = 20261018


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def q(x, ps=(0.05, 0.5, 0.95)):
    x = np.asarray(x, dtype=np.float64); x = x[np.isfinite(x)]
    return {str(p): float(np.quantile(x, p)) for p in ps} | {"n": int(len(x)), "min": float(x.min()) if len(x) else None, "max": float(x.max()) if len(x) else None}


# ---------------------------------------------------------------- the resampling algebra (own code; checked against the locked function)
def weighted_twoway(Y, a, b):
    """s_K^2 - MS_E/N of the table Y (texts x keys, 0/1) under text weights a (length N) and key weights b (length K): the locked
    twoway_bootstrap's inner algebra, reused for arbitrary weights (a = b = 1 gives the plain estimate)."""
    N, K = Y.shape
    colsum = a @ Y; rowsum = Y @ b; tot = float(colsum @ b)
    c = colsum / N; r = rowsum / K; m = tot / (N * K)
    ss_e = tot - K * float(a @ (r ** 2)) - N * float(b @ (c ** 2)) + N * K * m * m
    ms_e = ss_e / ((N - 1) * (K - 1)); s_k2 = float(b @ ((c - m) ** 2)) / (K - 1)
    return s_k2, ms_e, s_k2 - ms_e / N


def key_only_bootstrap(Y, rng, B):
    """Keys resampled with replacement, texts fixed; v recomputed exactly (MS_E included)."""
    N, K = Y.shape; ones = np.ones(N); out = np.empty(B)
    for i in range(B):
        b = np.bincount(rng.integers(0, K, size=K), minlength=K).astype(np.float64)
        out[i] = weighted_twoway(Y, ones, b)[2]
    return out


def text_only_bootstrap(Y, rng, B):
    N, K = Y.shape; ones = np.ones(K); out = np.empty(B)
    for i in range(B):
        a = np.bincount(rng.integers(0, N, size=N), minlength=N).astype(np.float64)
        out[i] = weighted_twoway(Y, a, ones)[2]
    return out


def key_only_from_levels(a_k, rng, B):
    """The a_k-only approximation: s_K^2 of resampled per-key levels (MS_E/N held fixed)."""
    K = len(a_k); idx = rng.integers(0, K, size=(B, K))
    return a_k[idx].var(axis=1, ddof=1)


# ---------------------------------------------------------------- part 1: the stored fields
def live_cells(cells_dir):
    for f in sorted(cells_dir.glob("*.json")):
        if f.name.startswith("costs__"):
            continue
        d = json.loads(f.read_text())
        if d.get("degenerate") or "levels" not in d or not d["levels"] or d.get("N_eff", 0) == 0:
            continue
        yield f.name, d


def stored_part(study, cells_dir):
    rows = []
    for name, d in live_cells(cells_dir):
        K = int(d["K"]); N = int(d["N_eff"])
        for alpha, lv in d["levels"].items():
            pe = lv.get("population_est")
            if pe is None:
                continue
            s_k2, ms_e, v, se, bm = (float(pe[k]) for k in ("s_K2", "MS_E", "var_pop_signed", "var_pop_boot_se", "var_pop_boot_mean"))
            if "level_values" in lv:
                a_k = np.asarray(lv["level_values"], dtype=np.float64)
            else:
                a_k = np.asarray(lv["level_counts"], dtype=np.float64) / N
            if len(a_k) != K:
                raise SystemExit(f"{study} {name} {alpha}: {len(a_k)} per-key levels against K = {K}")
            s_k2_re = float(a_k.var(ddof=1))
            if abs(s_k2_re - s_k2) > 1e-9 * max(abs(s_k2), 1e-300) + 1e-18:
                raise SystemExit(f"{study} {name} {alpha}: the per-key levels do not reproduce s_K2 ({s_k2_re} against {s_k2})")
            if abs((s_k2 - ms_e / N) - v) > 1e-12 * max(abs(v), 1e-300) + 1e-18:
                raise SystemExit(f"{study} {name} {alpha}: v != s_K2 - MS_E/N")
            a = (K - 1) / K; centre = a * s_k2; disp = centre - v
            rng = np.random.default_rng([int(hashlib.sha256(f"{study}|{name}|{alpha}".encode()).hexdigest()[:8], 16), SALT])
            vk = key_only_from_levels(a_k, rng, B_KEY); se_key = float(vk.std(ddof=1)); mean_key = float(vk.mean())
            se_normal = s_k2 * np.sqrt(2.0 / (K - 1))
            rows.append({"cell": name, "alpha": alpha, "K": K, "N_eff": N, "s_K2": s_k2, "MS_E": ms_e, "v": v, "se_crossed_stored": se, "boot_mean_stored": bm,
                         "centre_predicted": centre, "displacement": disp, "disp_over_abs_v": (disp / abs(v)) if v != 0 else None, "disp_over_se": (disp / se) if se > 0 else None,
                         "identity_z": ((bm - centre) / (se / np.sqrt(B_STORED))) if se > 0 else None,
                         "se_key_only": se_key, "mean_key_only_over_a_sK2": (mean_key / centre) if centre > 0 else None, "se_normal": se_normal,
                         "se_crossed_over_key": (se / se_key) if se_key > 0 else None, "se_key_over_normal": (se_key / se_normal) if se_normal > 0 else None,
                         "keys_at_zero": int((a_k == 0).sum()), "ms_e_over_N_over_v": (ms_e / N / v) if v > 0 else None})
    return rows


def summarise_rows(rows):
    fin = [r for r in rows if r["se_crossed_stored"] > 0 and r["v"] != 0]
    return {"n_rows": len(rows), "n_with_positive_se_and_nonzero_v": len(fin),
            "n_v_negative": int(sum(1 for r in rows if r["v"] < 0)), "n_se_zero": int(sum(1 for r in rows if r["se_crossed_stored"] == 0)),
            "disp_over_abs_v": q([r["disp_over_abs_v"] for r in fin], (0.05, 0.5, 0.95, 0.99)),
            "disp_over_se": q([r["disp_over_se"] for r in fin], (0.05, 0.5, 0.95, 0.99)),
            "identity_z": q([r["identity_z"] for r in fin], (0.01, 0.05, 0.5, 0.95, 0.99)) | {"sd": float(np.std([r["identity_z"] for r in fin], ddof=1)), "share_abs_above_3": float(np.mean([abs(r["identity_z"]) > 3 for r in fin]))},
            "se_crossed_over_key": q([r["se_crossed_over_key"] for r in fin], (0.01, 0.05, 0.5, 0.95, 0.99)),
            "se_key_over_normal": q([r["se_key_over_normal"] for r in fin], (0.05, 0.5, 0.95)),
            "ms_e_over_N_over_v": q([r["ms_e_over_N_over_v"] for r in fin if r["ms_e_over_N_over_v"] is not None], (0.05, 0.5, 0.95, 0.99))}


def recount_study1(rows):
    """The report's population diagnostic: the 360 cells of results.json (alpha = 0.01) against the mixture's Var(alpha_k)."""
    res = json.loads(S1_RES.read_text()); pdg = res["rules"]["population_diagnostic"]
    by = {(r["cell"], r["alpha"]): r for r in rows}
    out = {"n": len(pdg), "within2_crossed_stored_in_results": 0, "within2_crossed_recomputed": 0, "within2_key_only": 0, "within2_normal": 0, "n_positive_mixture": 0, "mismatch_se": 0}
    for x in pdg:
        r = by[(x["cell"], "0.01")]; vm = x["var_pop_mixture"]
        if abs(r["se_crossed_stored"] - x["se"]) > 1e-12 * max(x["se"], 1e-300) or abs(r["v"] - x["var_pop_twoway"]) > 1e-12 * max(abs(x["var_pop_twoway"]), 1e-300):
            out["mismatch_se"] += 1
        if vm > 0:
            out["n_positive_mixture"] += 1
            out["within2_crossed_stored_in_results"] += int(abs(x["var_pop_twoway"] - vm) <= 2 * x["se"])
            out["within2_crossed_recomputed"] += int(abs(r["v"] - vm) <= 2 * r["se_crossed_stored"])
            out["within2_key_only"] += int(abs(r["v"] - vm) <= 2 * r["se_key_only"])
            out["within2_normal"] += int(abs(r["v"] - vm) <= 2 * r["se_normal"])
    return out


def recount_study2(rows):
    """The report's Table 15b statement: the eligible primary S1 cells at alpha = 0.01 against the predictor's Var(alpha_k)."""
    res = json.loads(S2_RES.read_text()); s1 = res["rules"]["S1_adequacy"]
    elig = {r["file"] for r in s1["rows"] if r["status"] != "ineligible"}
    by = {(r["cell"], r["alpha"]): r for r in rows}
    out = {"n_eligible": len(elig), "n_positive_mixture": 0, "within2_crossed": 0, "within2_key_only": 0, "within2_normal": 0, "n_negative_twoway": 0}
    for f in sorted(elig):
        d = json.loads((S2_CELLS / f).read_text()); lv = d["levels"]["0.01"]; vm = float(lv["pred_first_order"]["var_pop"]); r = by[(f, "0.01")]
        out["n_negative_twoway"] += int(r["v"] < 0)
        if vm > 0:
            out["n_positive_mixture"] += 1
            out["within2_crossed"] += int(abs(r["v"] - vm) <= 2 * r["se_crossed_stored"])
            out["within2_key_only"] += int(abs(r["v"] - vm) <= 2 * r["se_key_only"])
            out["within2_normal"] += int(abs(r["v"] - vm) <= 2 * r["se_normal"])
    return out


# ---------------------------------------------------------------- part 2: regeneration on a Study 1 subset
SUBSET = [  # (law name, h, gamma, L, rule): cheap chains spanning the regimes (h = 0 raw and distinct, h = 1 raw and distinct, h = 2)
    ("zipf_V1000_s1.0", 0, 0.5, 64, "raw"), ("zipf_V1000_s1.0", 1, 0.5, 256, "raw"), ("zipf_V1000_s1.0", 1, 0.5, 256, "distinct"),
    ("zipf_V10000_s1.0", 0, 0.5, 2048, "distinct"), ("zipf_V10000_s1.0", 1, 0.5, 2048, "raw"), ("zipf_V10000_s1.2", 1, 0.5, 1024, "distinct"),
    ("markov_V1000_S50_eps0.1_s1.0", 2, 0.5, 2048, "distinct")]


def regen_part():
    grid = json.loads((HERE / "grid_v0.3.json").read_text()); specs = {R1.law_name(s): s for s in grid["laws"]}
    N = grid["N"]; L_max = max(grid["L"]); keys = list(range(grid["key_seed_start"], grid["key_seed_start"] + grid["K"]))
    out = []; chains = {}; packed = {}
    for name, h, gamma, L, rule in SUBSET:
        t0 = time.time(); spec = specs[name]; law = R1.make_law(spec); seed = R1.text_seed_for(law.name, grid["text_seed_base"])
        if (name, h) not in chains:
            chains[(name, h)] = C.Chain(law, h, N, L_max, seed=seed)
        chain = chains[(name, h)]
        if (name, h, gamma) not in packed:
            packed[(name, h, gamma)] = C.PackedColours(chain, keys, gamma, "independent", law.V, chunk=grid["key_chunk"])
        pk = packed[(name, h, gamma)]
        inc = chain.incidence(L, rule); K = len(keys)
        counts = np.zeros((N, K), dtype=np.float64)
        for c0 in range(0, K, grid["key_chunk"]):
            cols = pk.chunk_cols(c0); counts[:, c0:c0 + cols.shape[1]] = np.asarray(inc @ cols.astype(np.float64))
        fname = f"{name}__h{h}__independent__g{gamma}__L{L}__{rule}.json"; stored = json.loads((S1_CELLS / fname).read_text())
        # the regeneration check through the LOCKED cell_statistics with the runner's own rng seed for this cell
        rng = np.random.default_rng([int(hashlib.sha256(fname.encode()).hexdigest()[:8], 16), 20261011])
        stats = C.cell_statistics(inc, counts, chain, gamma, grid["alpha"], law.V, "independent", rng)
        rec = {"cell": fname, "regen_seconds": round(time.time() - t0, 1), "alphas": {}}
        for alpha in grid["alpha"]:
            a_s = str(alpha); pe_new = stats["levels"][a_s]["population_est"]; pe_old = stored["levels"][a_s]["population_est"]
            maxrel = max(abs(float(pe_new[k]) - float(pe_old[k])) / max(abs(float(pe_old[k])), 1e-300) for k in ("s_K2", "MS_E", "var_pop_signed", "var_pop_boot_se", "var_pop_boot_mean"))
            exact = all(float(pe_new[k]) == float(pe_old[k]) for k in ("s_K2", "MS_E", "var_pop_signed", "var_pop_boot_se", "var_pop_boot_mean"))
            # the table itself, as cell_statistics forms it
            M, keep, _, _, _ = C.per_text_terms(inc, chain, gamma); Mk = M[keep]
            z = C.z_scores(counts[keep], Mk, gamma); rej = (z > norm.isf(alpha)).astype(np.float64)
            s_k2, ms_e, v = C.twoway_population_variance(rej)
            own = weighted_twoway(rej, np.ones(rej.shape[0]), np.ones(rej.shape[1]))
            table_ok = (abs(s_k2 - pe_old["s_K2"]) <= 1e-12 * max(abs(pe_old["s_K2"]), 1e-300)) and (abs(ms_e - pe_old["MS_E"]) <= 1e-12 * max(abs(pe_old["MS_E"]), 1e-300))
            algebra_ok = all(abs(x - y) <= 1e-12 * max(abs(y), 1e-300) for x, y in zip(own, (s_k2, ms_e, v)))
            r2 = np.random.default_rng([int(hashlib.sha256(fname.encode()).hexdigest()[:8], 16), SALT, int(round(alpha * 1e6))])
            cr100 = C.twoway_bootstrap(rej, r2, B=B_STORED); cr2000 = C.twoway_bootstrap(rej, r2, B=2000)
            ko = key_only_bootstrap(rej, r2, B_KEY); ak = key_only_from_levels(rej.mean(axis=0), r2, B_KEY); to = text_only_bootstrap(rej, r2, 500)
            Kk = rej.shape[1]; Nn = rej.shape[0]; a = (Kk - 1) / Kk
            rec["alphas"][a_s] = {"stored_population_est_reproduced_exactly": bool(exact), "max_relative_difference": maxrel, "table_reproduces_stored_sK2_and_MSE": bool(table_ok), "own_algebra_equals_locked": bool(algebra_ok),
                                  "K": Kk, "N_eff": Nn, "s_K2": s_k2, "MS_E": ms_e, "v": v, "a_sK2": a * s_k2, "displacement": a * s_k2 - v,
                                  "se_crossed_stored": float(pe_old["var_pop_boot_se"]), "se_crossed_fresh_B100": float(cr100.std(ddof=1)), "se_crossed_fresh_B2000": float(cr2000.std(ddof=1)),
                                  "mean_crossed_fresh_B2000_over_a_sK2": float(cr2000.mean() / (a * s_k2)) if s_k2 > 0 else None,
                                  "se_key_only_exact": float(ko.std(ddof=1)), "mean_key_only_exact_over_a_v": float(ko.mean() / (a * v)) if v != 0 else None,
                                  "se_key_only_levels_approx": float(ak.std(ddof=1)), "se_text_only": float(to.std(ddof=1)), "se_normal": s_k2 * np.sqrt(2.0 / (Kk - 1)),
                                  "se_crossed_B2000_over_key_exact": float(cr2000.std(ddof=1) / ko.std(ddof=1)) if ko.std(ddof=1) > 0 else None,
                                  "se_levels_approx_over_key_exact": float(ak.std(ddof=1) / ko.std(ddof=1)) if ko.std(ddof=1) > 0 else None}
        out.append(rec); print("regen", fname, rec["regen_seconds"], "s", flush=True)
    return out


# ---------------------------------------------------------------- part 3: the synthetic truth check
def gh_nodes(n=120):
    x, w = np.polynomial.hermite_e.hermegauss(n); return x, w / w.sum()


def model_truth(model):
    if model["kind"] == "beta":
        m, s = model["mean"], model["sd"]; c = m * (1 - m) / s ** 2 - 1; a, b = m * c, (1 - m) * c
        v_e = m - (s ** 2 + m ** 2)
        return {"v_K": s ** 2, "v_e": v_e, "beta_a": a, "beta_b": b, "mean": m}
    # logistic key-by-text: logit p = theta_k + tau_i, theta ~ N(mu, sk^2), tau ~ N(0, st^2); v_K = Var_theta E_tau p
    mu, sk, st = model["mu"], model["sigma_key"], model["sigma_text"]; xt, wt = gh_nodes(200); xk, wk = gh_nodes(200)
    th = mu + sk * xk; mtheta = np.array([(wt * (1 / (1 + np.exp(-(t + st * xt))))).sum() for t in th])
    mbar = float((wk * mtheta).sum()); v_K = float((wk * (mtheta - mbar) ** 2).sum())
    return {"v_K": v_K, "mean": mbar}


def draw_table(model, K, N, rng):
    if model["kind"] == "beta":
        p = rng.beta(model["beta_a"], model["beta_b"], size=K)
        return (rng.random((N, K)) < p[None, :]).astype(np.float64)
    th = model["mu"] + model["sigma_key"] * rng.standard_normal(K); ta = model["sigma_text"] * rng.standard_normal(N)
    p = 1 / (1 + np.exp(-(th[None, :] + ta[:, None])))
    return (rng.random((N, K)) < p).astype(np.float64)


MODELS = [{"name": "beta_mean0.0115_sd0.0044 (Study 2's distinct h = 1 nominal scale)", "kind": "beta", "mean": 0.0115, "sd": 0.0044},
          {"name": "beta_mean0.030_sd0.0136 (Study 2's raw h = 1 nominal scale)", "kind": "beta", "mean": 0.030, "sd": 0.0136},
          {"name": "logistic key-by-text (mu = logit 0.012, sigma_key 0.35, sigma_text 0.8)", "kind": "logistic", "mu": float(np.log(0.012 / 0.988)), "sigma_key": 0.35, "sigma_text": 0.8}]
SIZES = [(500, 4000), (1000, 10000)]


def synthetic_part(R_small, R_large):
    out = []
    for (K, N) in SIZES:
        R = R_small if K == 500 else R_large
        for mi, model in enumerate(MODELS):
            truth = model_truth(model); m = dict(model); m.update(truth)
            rng = np.random.default_rng([SALT, K, N, mi]); t0 = time.time()
            vs, se_c, se_k, se_a, se_n, msen = [], [], [], [], [], []
            for r in range(R):
                Y = draw_table(m, K, N, rng); s_k2, ms_e, v = C.twoway_population_variance(Y)
                cr = C.twoway_bootstrap(Y, rng, B=B_STORED); ko = key_only_bootstrap(Y, rng, 200); ak = key_only_from_levels(Y.mean(axis=0), rng, 200)
                vs.append(v); se_c.append(cr.std(ddof=1)); se_k.append(ko.std(ddof=1)); se_a.append(ak.std(ddof=1)); se_n.append(s_k2 * np.sqrt(2 / (K - 1))); msen.append(ms_e / N)
            vs, se_c, se_k, se_a, se_n, msen = map(np.asarray, (vs, se_c, se_k, se_a, se_n, msen)); vK = truth["v_K"]; sd_emp = float(vs.std(ddof=1))
            cov = lambda se: float(np.mean(np.abs(vs - vK) <= 1.96 * se))
            out.append({"model": model["name"], "K": K, "N": N, "replicates": R, "v_K": vK, "mean_v": float(vs.mean()), "bias_over_sd_emp": float((vs.mean() - vK) / sd_emp), "sd_emp_v": sd_emp,
                        "ms_e_over_N_over_vK": float(msen.mean() / vK), "mean_se_crossed_B100": float(se_c.mean()), "mean_se_key_only_exact": float(se_k.mean()), "mean_se_key_only_levels": float(se_a.mean()), "mean_se_normal": float(se_n.mean()),
                        "ratio_crossed_over_emp": float(se_c.mean() / sd_emp), "ratio_key_over_emp": float(se_k.mean() / sd_emp), "ratio_normal_over_emp": float(se_n.mean() / sd_emp),
                        "coverage95_crossed": cov(se_c), "coverage95_key_only": cov(se_k), "coverage95_key_levels": cov(se_a), "coverage95_normal": cov(se_n), "seconds": round(time.time() - t0, 1)})
            print("synthetic", K, N, model["name"], round(time.time() - t0, 1), "s", flush=True)
    return out


# ---------------------------------------------------------------- the memo (generated)
def f3(x):
    return "—" if x is None or not np.isfinite(x) else f"{x:.3f}"


def f2(x):
    return "—" if x is None or not np.isfinite(x) else f"{x:.2f}"


def memo(s1, s2, regen, syn, rc1, rc2):
    L = [f"# Two-way bootstrap SE check (a labelled side computation; R09 F18) — generated {utc()}", "",
         "Generated by `research/study1/twoway_se_check.py` from the committed cells of Studies 1 and 2 and the locked `s1_core` functions (read-only). **Not pre-registered; no rule used the quantity it checks; no locked output, record file or verdict is changed.** It concerns the SECONDARY population target of Studies 1 and 2 (the two-way estimate v = s_K² − MS_E/N with 'a two-way bootstrap SE' from the locked crossed resampling of texts and keys, B = 100) that the reports use descriptively ('within 2 bootstrap SEs' counts). R09 round 3, F18 (Codex, 2026-10-16) showed that the crossed resample centres at a·s_K² with a = (K − 1)/K, not at v, and that its spread carries a text-duplication channel. This memo quantifies both for the committed records.", "",
         "## 1. The stored fields of every live cell and α", "",
         "The exact centring displacement d = a·s_K² − v = MS_E/N − s_K²/K (positive: the crossed resample's mean sits above the estimate by the duplicate-text term), the identity check z = (stored bootstrap mean − a·s_K²)/(SE/√100) (about standard normal if the stored means obey the identity), the ratio of the stored crossed SE to a key-only bootstrap SE of s_K² computed from the stored per-key levels (2,000 resamples; MS_E/N held fixed; part 2 measures that approximation), and the ratio of the key-only SE to the normal-theory SE s_K²√(2/(K − 1)).", "",
         "| Study | (cell, α) rows | Negative v | d/\\|v\\|: 5% / median / 95% / 99% | d/SE: median / 95% / 99% / max | identity z: SD, 1%, 99%, share \\|z\\| > 3 | SE_crossed / SE_key: 1% / 5% / median / 95% / 99% | SE_key / SE_normal: 5% / median / 95% | (MS_E/N)/v (v > 0): median / 95% / 99% |", "|---|---|---|---|---|---|---|---|---|"]
    for name, s in (("Study 1", s1), ("Study 2", s2)):
        a, b, z, r, k, m = s["disp_over_abs_v"], s["disp_over_se"], s["identity_z"], s["se_crossed_over_key"], s["se_key_over_normal"], s["ms_e_over_N_over_v"]
        L.append(f"| {name} | {s['n_with_positive_se_and_nonzero_v']} of {s['n_rows']} | {s['n_v_negative']} | {f3(a['0.05'])} / {f3(a['0.5'])} / {f3(a['0.95'])} / {f3(a['0.99'])} | {f3(b['0.5'])} / {f3(b['0.95'])} / {f3(b['0.99'])} / {f3(b['max'])} | {f2(z['sd'])}, {f2(z['0.01'])}, {f2(z['0.99'])}, {100 * z['share_abs_above_3']:.1f}% | {f3(r['0.01'])} / {f3(r['0.05'])} / {f3(r['0.5'])} / {f3(r['0.95'])} / {f3(r['0.99'])} | {f3(k['0.05'])} / {f3(k['0.5'])} / {f3(k['0.95'])} | {f3(m['0.5'])} / {f3(m['0.95'])} / {f3(m['0.99'])} |")
    L += ["", "(d/\\|v\\| is unbounded where v is near zero; the JSON files carry every row. The 'SE_crossed / SE_key' ratio compares a B = 100 crossed SE, whose own Monte Carlo relative error is about 7%, with a 2,000-resample key-only SE.)"]
    L += ["", "The reports' 'within 2 SE' counts, recomputed: Study 1's population diagnostic (the 360 cells of `results.json`, α = 0.01, against the mixture's Var(α_k)) and Study 2's Table 15b (the eligible primary S1 cells at α = 0.01 against the predictor's Var(α_k)).", "",
          "| Study | Cells | With a positive mixture variance | Within 2 crossed SEs (the report) | Within 2 key-only SEs | Within 2 normal-theory SEs |", "|---|---|---|---|---|---|",
          f"| Study 1 | {rc1['n']} | {rc1['n_positive_mixture']} | {rc1['within2_crossed_stored_in_results']} (recomputed from the cells: {rc1['within2_crossed_recomputed']}; SE or v mismatches between `results.json` and the cells: {rc1['mismatch_se']}) | {rc1['within2_key_only']} | {rc1['within2_normal']} |",
          f"| Study 2 | {rc2['n_eligible']} | {rc2['n_positive_mixture']} | {rc2['within2_crossed']} | {rc2['within2_key_only']} | {rc2['within2_normal']} |", ""]
    if regen:
        L += ["## 2. Regeneration on a Study 1 subset (the locked code; the production keys and seeds)", "",
              "Each cell's rejection table was rebuilt from the locked chain, colouring and incidence code, and the stored population block was re-derived through the locked `cell_statistics` with the runner's own per-cell seed (the regeneration check). On the rebuilt table (α = 0.01): the stored crossed SE, a fresh crossed bootstrap (the locked function; B = 100 and B = 2,000), the exact key-only bootstrap of v (keys resampled, MS_E recomputed; 2,000 resamples), the a_k-only approximation used in part 1, a text-only bootstrap (500 resamples) and the normal-theory SE.", "",
              "| Cell | Stored block reproduced exactly (max rel. diff.) | K / N_eff | v | d = a·s_K² − v | SE crossed: stored / fresh B100 / fresh B2000 | mean crossed B2000 ÷ a·s_K² | SE key-only exact | mean key-only ÷ a·v | SE a_k-only | SE text-only | SE normal | SE_crossed(B2000)/SE_key | SE_a_k/SE_key |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for rec in regen:
            x = rec["alphas"]["0.01"]
            L.append(f"| `{rec['cell']}` | {'yes' if x['stored_population_est_reproduced_exactly'] else 'no'} ({x['max_relative_difference']:.1e}); table {'ok' if x['table_reproduces_stored_sK2_and_MSE'] else 'DIFFERS'}; algebra {'ok' if x['own_algebra_equals_locked'] else 'DIFFERS'} | {x['K']} / {x['N_eff']} | {x['v']:.3e} | {x['displacement']:.2e} | {x['se_crossed_stored']:.2e} / {x['se_crossed_fresh_B100']:.2e} / {x['se_crossed_fresh_B2000']:.2e} | {f3(x['mean_crossed_fresh_B2000_over_a_sK2'])} | {x['se_key_only_exact']:.2e} | {f3(x['mean_key_only_exact_over_a_v'])} | {x['se_key_only_levels_approx']:.2e} | {x['se_text_only']:.2e} | {x['se_normal']:.2e} | {f3(x['se_crossed_B2000_over_key_exact'])} | {f3(x['se_levels_approx_over_key_exact'])} |")
        tk = [100 * r["alphas"]["0.01"]["se_text_only"] / r["alphas"]["0.01"]["se_key_only_exact"] for r in regen]; ak = [r["alphas"]["0.01"]["se_levels_approx_over_key_exact"] for r in regen]
        ck = [r["alphas"]["0.01"]["se_crossed_B2000_over_key_exact"] for r in regen]; n_exact = sum(1 for r in regen for a in r["alphas"].values() if a["stored_population_est_reproduced_exactly"]); n_all = sum(len(r["alphas"]) for r in regen)
        L.append(f"\nOver the {len(regen)} cells at α = 0.01 (SE ratios, this subset only): the text-only SE is {min(tk):.1f}% to {max(tk):.1f}% of the exact key-only SE; the a_k-only approximation is {min(ak):.3f} to {max(ak):.3f} of the exact key-only SE; the fresh crossed SE (B = 2,000) is {min(ck):.3f} to {max(ck):.3f} of it. The stored population block was reproduced exactly in {n_exact} of {n_all} (cell, α) blocks.")
        L.append("")
    if syn:
        L += ["## 3. The synthetic truth check at the studies' sizes", "",
              "Two-way Bernoulli tables from models whose population key component v_K is known; per replicate the estimate v, the crossed SE (the locked function at the production B = 100), the exact key-only SE (200 resamples), the a_k-only SE and the normal-theory SE; across replicates the empirical sampling SD of v (the quantity an SE should estimate) and the coverage of v ± 1.96·SE for v_K.", "",
              "| Model | K × N | Replicates | v_K | bias of v ÷ SD_emp | (MS_E/N)/v_K | SD_emp(v) | mean SE: crossed / key-only / a_k-only / normal | SE ÷ SD_emp: crossed / key-only / normal | coverage of v_K at 95%: crossed / key-only / a_k-only / normal |", "|---|---|---|---|---|---|---|---|---|---|"]
        for s in syn:
            L.append(f"| {s['model']} | {s['K']} × {s['N']} | {s['replicates']} | {s['v_K']:.3e} | {f2(s['bias_over_sd_emp'])} | {f3(s['ms_e_over_N_over_vK'])} | {s['sd_emp_v']:.2e} | {s['mean_se_crossed_B100']:.2e} / {s['mean_se_key_only_exact']:.2e} / {s['mean_se_key_only_levels']:.2e} / {s['mean_se_normal']:.2e} | {f2(s['ratio_crossed_over_emp'])} / {f2(s['ratio_key_over_emp'])} / {f2(s['ratio_normal_over_emp'])} | {f2(s['coverage95_crossed'])} / {f2(s['coverage95_key_only'])} / {f2(s['coverage95_key_levels'])} / {f2(s['coverage95_normal'])} |")
        L.append("")
    L += ["## 4. Reading (the conductor's; judgement, not evidence)", "",
          "Written into the decision log and the claim gate from the tables above; this file carries the generated numbers only.", ""]
    return "\n".join(L)


def main(argv):
    stored_only = "--stored-only" in argv; no_syn = "--no-synthetic" in argv or stored_only; no_regen = "--no-regen" in argv or stored_only
    Rs = int(argv[argv.index("--replicates-small") + 1]) if "--replicates-small" in argv else 200
    Rl = int(argv[argv.index("--replicates-large") + 1]) if "--replicates-large" in argv else 100
    t0 = time.time()
    head = {"written_utc": utc(), "note": "labelled side computation (R09 F18); not pre-registered; no locked output changed; the committed cells read only", "B_crossed_stored": B_STORED, "B_key_only": B_KEY,
            "s1_core_sha256": sha(HERE / "s1_core.py"), "script_sha256": sha(__file__)}
    if "--synthetic-only" in argv:      # re-run part (3) alone (more replicates); parts (1) and (2) are read back from their files for the memo
        no_regen = True; no_syn = False
        j1 = json.loads((S1_OUT / "twoway_se_check.json").read_text()); j2 = json.loads((S2_OUT / "twoway_se_check.json").read_text())
        s1, s2, rc1, rc2 = j1["summary"], j2["summary"], j1["recount_population_diagnostic"], j2["recount_table15b"]
    else:
        rows1 = stored_part("study1", S1_CELLS); rows2 = stored_part("study2", S2_CELLS)
        s1, s2 = summarise_rows(rows1), summarise_rows(rows2); rc1, rc2 = recount_study1(rows1), recount_study2(rows2)
        print("stored part", len(rows1), len(rows2), round(time.time() - t0, 1), "s", flush=True)
        (S1_OUT / "twoway_se_check.json").write_text(json.dumps(head | {"summary": s1, "recount_population_diagnostic": rc1, "rows": rows1}, indent=1))
        (S2_OUT / "twoway_se_check.json").write_text(json.dumps(head | {"summary": s2, "recount_table15b": rc2, "rows": rows2}, indent=1))
    regen = None if no_regen else regen_part()
    if regen is not None:
        (S1_OUT / "twoway_se_check_regen.json").write_text(json.dumps(head | {"subset": regen}, indent=1))
    syn = None if no_syn else synthetic_part(Rs, Rl)
    if syn is not None:
        (S1_OUT / "twoway_se_check_synthetic.json").write_text(json.dumps(head | {"models": MODELS, "sizes": SIZES, "results": syn}, indent=1))
    else:
        p = S1_OUT / "twoway_se_check_synthetic.json"
        syn = json.loads(p.read_text())["results"] if p.exists() else None
    if regen is None:
        p = S1_OUT / "twoway_se_check_regen.json"
        regen = json.loads(p.read_text())["subset"] if p.exists() else None
    MEMO.write_text(memo(s1, s2, regen, syn, rc1, rc2))
    print("DONE", round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
