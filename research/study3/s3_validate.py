"""Study 3 validation (v1; before the lock; no per-key level on real text). Writes outputs/study3_v0.1/VALIDATION.json.
(a) the token caches: every calibration array against the manifest; the evaluation and calibration plan reproduced from the units
    metadata (Study 2's draws, the scan, disjointness); Study 2's manifest bound; the seal's digests current;
(b) fixtures on synthetic scores with validation randomness: the order indices; conformal and tolerance on exchangeable continuous scores
    (exact Beta law and the tolerance guarantee) and on discrete scores (conservative); the empirical multiplier's and the pooled
    threshold's defining properties and maximality; counts_below against brute force; the predictor against the exact Beta law and
    Monte Carlo; cross_cov and rho_bar against brute force and Study 1's estimator; the across-key covariance of two sets' mean z with
    validation keys against the identity;
(c) the key policy; (d) the lock schema (a canonical lock accepted, its variants refused); (e) the runner's reuse refusals;
(f) the analyzer's refusals and the acceptance of the complete pilot inventory; the REP decision function;
(g) the timed validation run (synthetic cells, validation keys), the pilot inputs and the analyzer in pilot mode (status and counts);
(h) the cost probe: one production-sized pass-1 and pass-2 unit at h = 0 and h = 2 on synthetic Zipf tokens at V = 128,256 with
    K = 1,000 (+ 1,000 fitting) validation keys, and the projection over every production unit from the key-free sizes in INPUTS.json;
(i) the eligibility (T1) and materiality (T2) counts from the key-free inputs.
Usage: PYTHONHASHSEED=0 .venv/bin/python -u research/study3/s3_validate.py
"""
import hashlib, json, pathlib, resource, shutil, sys, tempfile, time
import numpy as np
from scipy.stats import norm, binom
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study2")); sys.path.insert(0, str(ROOT / "research/study1")); sys.path.insert(0, str(ROOT / "tools"))
import s3_core as T
import s3_data as SD
import s3_run as R
import s3_analyze as A
import s3_inputs as I
import s2_core as S
import s1_core as C
from s3_keys import check_keys, KeyPolicyError

GRID_PATH = R.GRID_CANON; GRID = json.loads((ROOT / GRID_PATH).read_text()); VK = GRID["validation_key_seed_start"]
OUTD = ROOT / R.OUT; STAMP = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()); T0 = time.time()
rep = {"study": R.STUDY, "run": STAMP, "note": "no per-key level on real text; validation keys and synthetic tokens only; real chains read for key-free sizes", "fixtures": {}}


def log(m):
    print(f"[{time.time() - T0:6.0f}s] {m}", flush=True)


def vrng(*salt):
    return np.random.default_rng([99261014, *salt])


# ---------------- (a) token caches ----------------
man = json.loads((ROOT / R.TOKENS_MANIFEST).read_text()); s2m = json.loads((ROOT / R.S2_TOKENS_MANIFEST).read_text())
a_ok = {"study2_manifest_bound": man["study2_manifest_sha256"] == R.sha(ROOT / R.S2_TOKENS_MANIFEST)}
plan = SD.plan_sets(s2m); a_ok["plan_reproduced"] = all(plan[t]["cal_ids_sha256"] == man["cells"][t]["cal_ids_sha256"] and plan[t]["eval_ids_sha256"] == man["cells"][t]["eval_ids_sha256"] and plan[t]["cal_positions"] == man["cells"][t]["cal_positions"] for t in GRID["cells"])
arr_ok = True
for t in GRID["cells"]:
    for tok in GRID["tokenizers"]:
        X = SD.load_cal(t, tok, man); e = man["cells"][t]["tokenizers"][tok]
        arr_ok &= (int(X.min()) == e["min_id"] and int(X.max()) == e["max_id"] and int(X.max()) < GRID["tokenizers"][tok]["V"] and X.shape == (GRID["N_cal_set"], GRID["L"]))
        XE = SD.load_eval(t, tok, man); arr_ok &= XE.shape == ((GRID["N_eval_gutenberg"] if t == "gutenberg_en_1024" else GRID["N_eval"]), GRID["L"])
a_ok["arrays"] = bool(arr_ok)
sys.path.insert(0, str(ROOT / "tools")); from corpora_access import Access
acc = Access(str(SD.D.UNITS_DIR), SD.D.UNITS_VERSION)
a_ok["seal_current"] = man["seal"]["partition_sha256"] == acc.partition_sha256 and man["seal"]["units_sha256"] == acc.units_sha256
a_ok["all_ok"] = all(a_ok.values()); rep["token_cache"] = a_ok | {"cal_positions": {t: man["cells"][t]["cal_positions"] for t in GRID["cells"]}, "cal_skipped": {t: man["cells"][t]["cal_skipped"] for t in GRID["cells"]}}
log(f"(a) token caches {a_ok}")

# ---------------- (b) fixtures ----------------
fx = {}
fx["order_indices"] = {f"{n}|{a}": {"j_conformal": T.j_conformal(n, a), "j_tolerance": T.j_tolerance(n, a, GRID["delta"])} for n in GRID["N_cal"] for a in GRID["alpha"]}
tol_ok = True
for n in GRID["N_cal"]:
    for a in GRID["alpha"]:
        j = T.j_tolerance(n, a, GRID["delta"])
        if j > 0:
            tol_ok &= binom.cdf(j - 1, n, a) <= GRID["delta"] and (j == n or binom.cdf(j, n, a) > GRID["delta"])
        else:
            tol_ok &= binom.cdf(0, n, a) > GRID["delta"]
fx["tolerance_index_maximal"] = bool(tol_ok)
# i.i.d. continuous scores (uniform p): the realised level of a threshold t is t itself
rng = vrng(1); Rr = 20000; cont = {}
for n, a in ((1000, 0.01), (5000, 0.01), (2000, 0.05), (5000, 0.001)):
    jc, jt = T.j_conformal(n, a), T.j_tolerance(n, a, GRID["delta"])
    P = rng.random((n, Rr)) if n <= 2000 else None
    lc, lt = [], []
    for c0 in range(0, Rr, 2000):
        Pp = P[:, c0:c0 + 2000] if P is not None else rng.random((n, 2000))
        lc.append(T.kth_smallest(Pp, jc)); lt.append(T.kth_smallest(Pp, jt))
    lc = np.concatenate(lc); lt = np.concatenate(lt)
    ex_m = jc / (n + 1); ex_sd = np.sqrt(jc * (n + 1 - jc) / ((n + 1) ** 2 * (n + 2))); ex_tail = float(binom.cdf(jt - 1, n, a)) if jt > 0 else 0.0
    cont[f"{n}|{a}"] = {"conformal_mean": float(lc.mean()), "exact_mean": ex_m, "conformal_sd": float(lc.std()), "exact_sd": float(ex_sd), "tolerance_share_above_alpha": float(np.mean(lt > a)), "exact_tail": ex_tail,
                        "ok": bool(abs(lc.mean() - ex_m) < 4 * ex_sd / np.sqrt(Rr) and abs(lc.std() / ex_sd - 1) < 0.03 and np.mean(lt > a) <= ex_tail + 4 * np.sqrt(ex_tail * (1 - ex_tail) / Rr) + 1e-12)}
fx["continuous_iid"] = cont
# discrete (KGW-like) scores: conformal is conservative
rng = vrng(2); M = 250; g = 0.25; Rr = 4000; n = 1000; a = 0.01; jc = T.j_conformal(n, a)
pop = T.pvalues_kgw(rng.binomial(M, g, size=(200000, 1)).astype(float), np.full(200000, M), g).ravel(); pop_s = np.sort(pop)
lv = []
for r_ in range(Rr):
    t = T.kth_smallest(rng.choice(pop, size=(n, 1)), jc)[0]; lv.append(np.searchsorted(pop_s, t, side="left") / len(pop_s))
fx["discrete_conformal"] = {"mean_level": float(np.mean(lv)), "bound": jc / (n + 1), "ok": bool(np.mean(lv) <= jc / (n + 1) + 3 * np.std(lv) / np.sqrt(Rr))}
# scheme-level thresholds: defining properties and maximality
rng = vrng(3); ok = True
for trial in range(20):
    Nn, Kf = int(rng.integers(200, 2000)), int(rng.integers(50, 400)); Pf = rng.random((Nn, Kf)) ** rng.uniform(0.7, 1.5, size=Kf)[None, :]
    for a in GRID["alpha"]:
        t_emp, kap, det = T.empirical_multiplier_threshold(Pf, a, GRID["beta"]); m = T.m_floor(a, Nn); b = T.m_floor(GRID["beta"], Kf)
        cnt = (Pf < t_emp).sum(axis=0); ok &= int((cnt > m).sum()) <= b and t_emp <= a + 1e-15
        if det["unclipped"] < a:   # maximal: the next larger p-value would push b + 1 keys above alpha
            nxt = np.min(Pf[Pf > det["unclipped"]]) + 1e-15; ok &= int(((Pf < nxt).sum(axis=0) > m).sum()) > b
        tp = T.pooled_threshold(Pf, a); mt = T.m_floor(a, Nn * Kf); ok &= int((Pf < tp).sum()) <= mt
        nxt = np.min(Pf[Pf > tp]) + 1e-15 if (Pf > tp).any() else None; ok &= (nxt is None) or int((Pf < nxt).sum()) > mt
fx["scheme_thresholds_properties"] = bool(ok)
rng = vrng(4); Pt = rng.random((500, 30)); Pt[rng.random(Pt.shape) < 0.2] = 0.5; Ts = rng.random((7, 30)); brute = np.stack([(Pt < Ts[v][None, :]).sum(axis=0) for v in range(7)])
fx["counts_below_brute_force"] = bool(np.array_equal(T.counts_below(T.sort_columns(Pt), Ts), brute))
# the predictor
pb = []
for n, a in ((1000, 0.01), (5000, 0.01), (2000, 0.05), (5000, 0.001)):
    j = T.j_conformal(n, a); p = T.predict_per_key(0.01, 0.01, 0.01, 0.99, 0.99, n, j, 10 ** 12, a)
    ex_m = j / (n + 1); ex_sd = np.sqrt(j * (n + 1 - j) / ((n + 1) ** 2 * (n + 2)))
    pb.append({"n": n, "alpha": a, "rel_err_mean": abs(p["mean_level"] / ex_m - 1), "rel_err_sd": abs(p["sd_pop"] / ex_sd - 1)})
rng = vrng(5); mc = []
for rC, rE, rCE, s2C, s2E, n, a in ((0.02, 0.03, 0.005, 0.95, 1.1, 1000, 0.01), (0.2, 0.15, 0.17, 0.8, 0.85, 5000, 0.01), (0.05, 0.05, 0.0, 1.0, 1.0, 1000, 0.05)):
    j = T.j_conformal(n, a); p = T.predict_per_key(rC, rE, rCE, s2C, s2E, n, j, 10 ** 12, a); nn = 400000
    D = rng.multivariate_normal([0, 0], [[rC, rCE], [rCE, rE]], size=nn); U = rng.beta(n + 1 - j, j, size=nn)
    l = norm.sf((D[:, 0] - D[:, 1] + np.sqrt(s2C) * norm.ppf(U)) / np.sqrt(s2E))
    mc.append({"pred_mean": p["mean_level"], "mc_mean": float(l.mean()), "pred_sd": p["sd_pop"], "mc_sd": float(l.std()), "pred_share": p["share_above_alpha_pop"], "mc_share": float(np.mean(l > a)),
               "ok": bool(abs(p["sd_pop"] / l.std() - 1) < 0.01 and abs(p["mean_level"] / l.mean() - 1) < 0.01 and abs(p["share_above_alpha_pop"] - np.mean(l > a)) < 0.005)})
fx["predictor"] = {"exact_beta": pb, "exact_beta_ok": all(x["rel_err_mean"] < 1e-5 and x["rel_err_sd"] < 1e-3 for x in pb), "monte_carlo": mc, "monte_carlo_ok": all(x["ok"] for x in mc)}
# the finite-evaluation exceedance shares (R07 F5, F9): (i) within a law (v = 0, equal scales) the population level is Beta(j, N + 1 - j) and the
# count on N_E independent texts is Beta-binomial (acceptance 1e-5); (ii) a fixed threshold at rho_E = 0 gives a constant level and a binomial
# count (1e-9); (iii) with a positive shift variance, convergence of the production Q = 1,000 midpoint rule against a four-fold finer rule on
# settings taken from the frozen inputs (the largest and smallest positive v, the largest and smallest residual-scale ratio, both evaluation
# sizes, every level, both per-key methods, plus a seeded random sample; acceptance 1e-4), and the fixed thresholds' Q = 4,000 rule against
# Q = 16,000 (1e-5); (iv) Monte Carlo (400,000 draws of U, X and the binomial count) at the reviewer's two per-key examples and one fixed
# threshold (acceptance 4 SE + 1e-4)
from scipy.stats import betabinom, beta as beta_dist_
fs = []
for n, j, NE, a in ((5000, 50, 10000, 0.01), (5000, 39, 10000, 0.01), (5000, 50, 7122, 0.01), (1000, 10, 10000, 0.01), (2000, 100, 10000, 0.05)):
    p = T.predict_per_key(0.003, 0.003, 0.003, 1.0, 1.0, n, j, NE, a); row = {"N_cal": n, "j": j, "N_E": NE, "alpha": a}
    for mult, nm in ((1, "alpha"), (2, "2alpha"), (5, "5alpha")):
        ex = float(betabinom.sf(T.m_floor(mult * a, NE), NE, j, n + 1 - j)); row[f"finite_{nm}"] = p[f"share_above_{nm}_finite"]; row[f"exact_{nm}"] = ex
    row["pop_alpha"] = p["share_above_alpha_pop"]; row["exact_pop_alpha"] = float(beta_dist_.sf(a, j, n + 1 - j))
    row["ok"] = all(abs(row[f"finite_{nm}"] - row[f"exact_{nm}"]) < 1e-5 for nm in ("alpha", "2alpha", "5alpha")) and abs(row["pop_alpha"] - row["exact_pop_alpha"]) < 1e-3
    fs.append(row)
f0 = T.predict_fixed(0.0, 1.0, 0.01, 10000, 0.01); fx_fixed = {"finite": f0["share_above_alpha_finite"], "exact": float(binom.sf(100, 10000, 0.01)), "ok": abs(f0["share_above_alpha_finite"] - binom.sf(100, 10000, 0.01)) < 1e-9}
inp_fx = json.loads((ROOT / R.INPUTS).read_text()); cand = []
for bk, blk in inp_fx["blocks"].items():
    for pk, pr in blk["pairs"].items():
        src, dst = pk.split("->"); mE = blk["sets"][f"{dst}|E"]
        for n, per in pr["per_key"].items():
            mC = blk["sets"][f"{src}|C{n}"]
            for a, d in per.items():
                for meth in ("conformal", "tolerance"):
                    q = d[meth]
                    if q.get("j", 0) > 0 and q.get("v", 0) > 0 and not q.get("flags"):
                        cand.append({"block": bk, "pair": pk, "N_cal": int(n), "alpha": float(a), "method": meth, "v": q["v"], "sC2": mC["sigma2"], "sE2": mE["sigma2"], "j": q["j"], "N_E": mE["n"], "ratio": mC["sigma2"] / mE["sigma2"]})
pick = {}
if cand:
    pick["max_v"] = max(cand, key=lambda c: c["v"]); pick["min_v"] = min(cand, key=lambda c: c["v"]); pick["max_ratio"] = max(cand, key=lambda c: c["ratio"]); pick["min_ratio"] = min(cand, key=lambda c: c["ratio"])
    gut = [c for c in cand if c["N_E"] != GRID["N_eval"]]
    if gut:
        pick["gutenberg_E_max_v"] = max(gut, key=lambda c: c["v"])
    rs = np.random.default_rng(99261015); idx = rs.choice(len(cand), size=min(40, len(cand)), replace=False)
    for i_, k_ in enumerate(idx):
        pick[f"random_{i_}"] = cand[int(k_)]
conv = []
for nm_, c in pick.items():
    r1 = T.finite_share_perkey(np.sqrt(c["sC2"]), np.sqrt(c["sE2"]), c["v"], c["N_cal"], c["j"], c["N_E"], c["alpha"], Q=T.SHARE_Q)
    r4 = T.finite_share_perkey(np.sqrt(c["sC2"]), np.sqrt(c["sE2"]), c["v"], c["N_cal"], c["j"], c["N_E"], c["alpha"], Q=4 * T.SHARE_Q)
    d_ = max(abs(r1[k] - r4[k]) for k in r1); conv.append({"name": nm_, **{k: c[k] for k in ("block", "pair", "N_cal", "alpha", "method", "v", "ratio", "N_E", "j")}, "max_abs_diff_Q_vs_4Q": d_, "shares_Q": r1, "ok": d_ < 1e-4})
convf = []
if cand:
    sets_ = [(bk, k, m) for bk, blk in inp_fx["blocks"].items() for k, m in blk["sets"].items() if k.endswith("|E")]
    rs2 = np.random.default_rng(99261016); sel = [sets_[int(i)] for i in rs2.choice(len(sets_), size=min(20, len(sets_)), replace=False)]
    for bk, k, m in sel:
        for a in GRID["alpha"]:
            for tp_name, tp in (("nominal", a), ("multiplier20", a * GRID["beta"])):
                tz = float(norm.isf(tp)); r1 = T.finite_share_fixed(max(m["rho"], 0.0), np.sqrt(max(m["sigma2"], 0.0)), tz, m["n"], a, Q=T.SHARE_Q_FIXED); r4 = T.finite_share_fixed(max(m["rho"], 0.0), np.sqrt(max(m["sigma2"], 0.0)), tz, m["n"], a, Q=4 * T.SHARE_Q_FIXED)
                d_ = max(abs(r1[x] - r4[x]) for x in r1); convf.append({"block": bk, "set": k, "alpha": a, "method": tp_name, "rho": m["rho"], "max_abs_diff": d_, "ok": d_ < 1e-5})
mc_rows = []
rngm = np.random.default_rng(99261017); NMC = 400000
def mc_perkey(c, mult):
    U = rngm.beta(c["N_cal"] + 1 - c["j"], c["j"], NMC); X = rngm.normal(0, np.sqrt(c["v"]), NMC); ell = norm.sf((np.sqrt(c["sC2"]) * norm.ppf(U) + X) / np.sqrt(c["sE2"]))
    cnt = rngm.binomial(c["N_E"], np.clip(ell, 0, 1)); sh = float(np.mean(cnt > T.m_floor(mult * c["alpha"], c["N_E"]))); return sh, float(np.sqrt(max(sh * (1 - sh), 1e-12) / NMC))
targets = [("llama|wikipedia_en_1024->llama|wikipedia_zh_256", "5000", "0.01", "conformal", "h0|raw"), ("llama|gutenberg_en_1024->llama|wikipedia_ja_256", "5000", "0.01", "conformal", "h0|raw")]
for pk, n, a, meth, bk in targets:
    blk = inp_fx["blocks"].get(bk, {}); pr = (blk.get("pairs") or {}).get(pk)
    if pr is None:
        continue
    q = pr["per_key"][n][a][meth]; src, dst = pk.split("->"); mC = blk["sets"][f"{src}|C{n}"]; mE = blk["sets"][f"{dst}|E"]
    c = {"N_cal": int(n), "j": q["j"], "v": q["v"], "sC2": mC["sigma2"], "sE2": mE["sigma2"], "N_E": mE["n"], "alpha": float(a)}
    for mult, nm in ((1, "alpha"), (2, "2alpha")):
        sh, se = mc_perkey(c, mult); pred = q[f"share_above_{nm}_finite"]
        mc_rows.append({"pair": pk, "N_cal": int(n), "alpha": float(a), "method": meth, "level": nm, "pred": pred, "mc": sh, "mc_se": se, "ok": abs(pred - sh) < 4 * se + 1e-4})
blk = inp_fx["blocks"].get("h0|raw", {}); mE = (blk.get("sets") or {}).get("llama|news_en_256|E")
if mE:
    for a_ in (0.01,):
        nom = mE["pred_fixed"][str(a_)]["nominal"]; D = rngm.normal(0, np.sqrt(max(mE["rho"], 0.0)), NMC); ell = norm.sf((norm.isf(a_) - D) / np.sqrt(mE["sigma2"])); cnt = rngm.binomial(mE["n"], np.clip(ell, 0, 1))
        for mult, nm in ((2, "2alpha"), (5, "5alpha")):
            sh = float(np.mean(cnt > T.m_floor(mult * a_, mE["n"]))); se = float(np.sqrt(max(sh * (1 - sh), 1e-12) / NMC)); pred = nom[f"share_above_{nm}_finite"]
            mc_rows.append({"set": "llama|news_en_256|E", "alpha": a_, "method": "nominal", "level": nm, "pred": pred, "mc": sh, "mc_se": se, "ok": abs(pred - sh) < 4 * se + 1e-4})
fx["finite_shares"] = {"within_law": fs, "fixed_rho0": fx_fixed, "convergence_perkey": conv, "convergence_fixed": convf, "monte_carlo": mc_rows,
                       "n_candidates_positive_v": len(cand), "acceptance": {"within_law_abs": 1e-5, "within_law_population_share_abs": 1e-3, "fixed_rho0_abs": 1e-9, "convergence_perkey_abs": 1e-4, "convergence_fixed_abs": 1e-5, "monte_carlo": "4 SE + 1e-4", "monte_carlo_se_guard": "sqrt(max(p(1 - p), 1e-12) / 400000)"},
                       "ok": all(r["ok"] for r in fs) and fx_fixed["ok"] and bool(conv) and all(r["ok"] for r in conv) and bool(convf) and all(r["ok"] for r in convf) and bool(mc_rows) and all(r["ok"] for r in mc_rows)}
# cross_cov, rho_bar against brute force and Study 1's estimator; the across-key covariance of two sets' mean z
rng = vrng(6); law = C.ZipfIID(2000, 1.2); XA = law.sample(150, 64, rng).astype(np.int32); XB = law.sample(120, 64, rng).astype(np.int32)
cc_ok = True; ident = []
for h in (0, 1):
    for rule in ("raw", "distinct"):
        chA = S.build_chain(XA, 2000, "A", h); chB = S.build_chain(XB, 2000, "B", h)
        wa = T.set_weights(chA, 64, rule); wb = T.set_weights(chB, 64, rule); cc, _ = T.cross_cov(wa, wb)
        iA = chA.incidence(64, rule).toarray(); iB = chB.incidence(64, rule).toarray(); MA = iA.sum(1); MB = iB.sum(1)
        # brute force over cross pairs, on the union of tuple ids
        ids = np.union1d(chA.D, chB.D); FA = np.zeros((150, len(ids))); FB = np.zeros((120, len(ids)))
        FA[:, np.searchsorted(ids, chA.D)] = iA; FB[:, np.searchsorted(ids, chB.D)] = iB
        brute = float(((FA / np.sqrt(MA)[:, None]) @ (FB / np.sqrt(MB)[:, None]).T).mean())
        cc_ok &= abs(cc - brute) < 1e-12 * max(1, abs(brute))
        pe = C.population_estimates(chA.incidence(64, rule), chA, 0.25, 2000, "independent", np.random.default_rng(0), B=0); mA = T.set_moments(wa); mB = T.set_moments(wb)
        cc_ok &= abs(pe["rho_bar"] - mA["rho"]) < 1e-12 * max(1, abs(pe["rho_bar"])) and abs(pe["sigma_model2"] - mA["sigma2"]) < 1e-10
        # the algebraic floor of v: v_raw + tau_v = ||w_A - w_B||^2 exactly
        wA_full = (FA / np.sqrt(MA)[:, None]).mean(axis=0); wB_full = (FB / np.sqrt(MB)[:, None]).mean(axis=0); norm2 = float(((wA_full - wB_full) ** 2).sum())
        v_raw = mA["rho"] + mB["rho"] - 2 * cc; tau_v = mA["sigma2"] / mA["n"] + mB["sigma2"] / mB["n"]
        cc_ok &= abs(v_raw + tau_v - norm2) < 1e-12 * max(1.0, norm2)
        pv = T.predict_per_key(mA["rho"], mB["rho"], cc, mA["sigma2"], mB["sigma2"], mA["n"], T.j_conformal(mA["n"], 0.01), mB["n"], 0.01)
        cc_ok &= abs(pv["tau_v"] - tau_v) < 1e-15 and not pv["flags"]
        # a value below the floor is flagged
        pv2 = T.predict_per_key(mA["rho"], mB["rho"], cc + tau_v, mA["sigma2"], mB["sigma2"], mA["n"], T.j_conformal(mA["n"], 0.01), mB["n"], 0.01)
        cc_ok &= "v_below_algebraic_floor" in pv2["flags"]
        # across keys (validation keys): Cov_K(mean z over A, mean z over B) against <w_A, w_B> (independent colours at g = 0.25 of V = 2000)
        keys = list(range(VK + 7000, VK + 7000 + 4000)); g = 0.25
        UA = S.uniforms_chunk(keys, chA.D); UB = S.uniforms_chunk(keys, chB.D)
        zA = ((iA @ (UA < g)) - g * MA[:, None]) / np.sqrt(MA[:, None] * g * (1 - g)); zB = ((iB @ (UB < g)) - g * MB[:, None]) / np.sqrt(MB[:, None] * g * (1 - g))
        cov = float(np.cov(zA.mean(0), zB.mean(0))[0, 1]); se = float(np.sqrt((zA.mean(0).var() * zB.mean(0).var() + cov ** 2) / len(keys)))
        ident.append({"h": h, "rule": rule, "identity": cc, "observed": cov, "z": (cov - cc) / se})
fx["cross_cov"] = {"brute_and_study1_equal": bool(cc_ok), "across_keys": ident, "across_keys_ok": all(abs(x["z"]) < 4 for x in ident)}
rep["fixtures"]["b"] = fx
log(f"(b2) finite shares: within-law {all(r['ok'] for r in fs)}; per-key convergence over {len(conv)} frozen-input settings, max |Q - 4Q| {max((r['max_abs_diff_Q_vs_4Q'] for r in conv), default=None)}; fixed over {len(convf)}, max {max((r['max_abs_diff'] for r in convf), default=None)}; MC {[(round(r['pred'], 4), round(r['mc'], 4)) for r in mc_rows]}")
log(f"(b) fixtures: tolerance maximal {fx['tolerance_index_maximal']}; iid {all(v['ok'] for v in cont.values())}; discrete {fx['discrete_conformal']['ok']}; scheme {fx['scheme_thresholds_properties']}; counts {fx['counts_below_brute_force']}; predictor {fx['predictor']['exact_beta_ok']}/{fx['predictor']['monte_carlo_ok']}; finite shares {fx['finite_shares']['ok']}; cross_cov {fx['cross_cov']['brute_and_study1_equal']}/{fx['cross_cov']['across_keys_ok']}")

# ---------------- (c) key policy ----------------
kp = {}
for name, keys, purpose, expect in (("eval_ok", range(23000, 24000), "study3_eval", True), ("fit_ok", range(24000, 25000), "study3_fit", True), ("validation_ok", range(VK, VK + 10), "validation", True),
                                    ("reserved", range(30000, 30010), "study3_eval", False), ("study2_range", range(22990, 23010), "study3_eval", False), ("study1_range", range(20000, 20010), "validation", False),
                                    ("eval_as_fit", range(23000, 23010), "study3_fit", False), ("fit_as_eval", range(24000, 24010), "study3_eval", False), ("below_validation", range(999990, 1000010), "validation", False), ("audit_dev", range(0, 10), "study3_eval", False)):
    try:
        check_keys(keys, purpose); kp[name] = expect is True
    except KeyPolicyError:
        kp[name] = expect is False
rep["fixtures"]["key_policy"] = kp | {"all_ok": all(kp.values())}

# ---------------- (d) lock schema ----------------
def make_root(tmp):
    for f in R.PINNED + (R.RESOLUTION,):
        src = ROOT / f; dst = tmp / f; dst.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            shutil.copy(src, dst)
        else:
            dst.write_text(f"placeholder for {f} (validation fixture)\n")


def canonical_lock(tmp):
    return {"study": R.STUDY, "date": "2026-10-14", "approved_by": "Yichen", "before_outcomes": True, "final": False, "grid": R.GRID_CANON, "protocol": R.PROTOCOL, "validation": R.VALIDATION, "inputs": R.INPUTS, "tokens_manifest": R.TOKENS_MANIFEST,
            "hashes": {f: R.sha(tmp / f) for f in R.PINNED}, "review": {"checkpoint": R.CHECKPOINT, "resolution": R.RESOLUTION, "sha256": R.sha(tmp / R.RESOLUTION)},
            "keys": {"eval_start": GRID["key_eval_start"], "K": GRID["K"], "fit_start": GRID["key_fit_start"], "K_fit": GRID["K_fit"]}}


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
                "non_iso_date": dict(base, date="14/10/2026"), "early_date": dict(base, date="2026-10-12"), "wrong_study": dict(base, study="study2_v0.1"), "protocol_is_grid": dict(base, protocol=R.GRID_CANON),
                "validation_noncanonical": dict(base, validation="outputs/study2_v0.1/VALIDATION.json"), "inputs_noncanonical": dict(base, inputs="outputs/study2_v0.1/INPUTS.json"), "tokens_noncanonical": dict(base, tokens_manifest=R.S2_TOKENS_MANIFEST),
                "checkpoint_R05": dict(base, review=dict(base["review"], checkpoint="R05")), "resolution_R06": dict(base, review=dict(base["review"], resolution="research/reviews/R06_study2-report/RESOLUTION.md")),
                "tampered_digest": dict(base, hashes=dict(base["hashes"], **{"research/study3/s3_core.py": "0" * 64})), "non_hex_digest": dict(base, hashes=dict(base["hashes"], **{"research/study3/s3_core.py": "zz"})),
                "missing_code_digest": dict(base, hashes={k: v for k, v in base["hashes"].items() if k != "research/study3/s3_analyze.py"}), "extra_digest": dict(base, hashes=dict(base["hashes"], **{"research/study2/s2_run.py": "0" * 64})),
                "missing_study2_manifest_digest": dict(base, hashes={k: v for k, v in base["hashes"].items() if k != R.S2_TOKENS_MANIFEST}),
                "key_record_mismatch": dict(base, keys=dict(base["keys"], K=GRID["K"] + 1)), "fit_start_mismatch": dict(base, keys=dict(base["keys"], fit_start=23000)), "review_digest_wrong": dict(base, review=dict(base["review"], sha256="1" * 64))}
    for name, lk in variants.items():
        try_lock(name, lk)
    try_lock("noncanonical_grid_argument", base, grid_arg="research/study2/grid_v0.1.json")
n_lock_variants = len(variants) + 1
rep["fixtures"]["lock"] = lock_fx | {"n_variants": n_lock_variants, "ok": lock_fx["accepted"] == ["complete_canonical"] and len(lock_fx["refused"]) == n_lock_variants}
log(f"(c)(d) key policy {rep['fixtures']['key_policy']['all_ok']}; lock accepted {lock_fx['accepted']} refused {len(lock_fx['refused'])} of {n_lock_variants}")

# ---------------- (g) the timed validation run, the pilot inputs and the analyzer in pilot mode ----------------
vdir = OUTD / f"validation_{STAMP}"; cells_v = vdir / "cells"; t1 = time.time()
R.main(GRID_PATH, None, True, out_dir=str(cells_v)); run_s = time.time() - t1
sp_v = R.spec_of(GRID, True); syn = R.synthetic_sets(GRID)
blocks, _ = I.compute(GRID, sp_v, lambda tok, tag: syn[tag][0], lambda tok, tag: syn[tag][1], log=lambda m: None)
pilot_inputs = {"blocks": blocks}; (vdir / "pilot_inputs.json").write_text(json.dumps(I.clean(pilot_inputs)))
pil = A.analyze(GRID, cells_v, pilot_inputs, "validation", validation=True)
rep["validation_run"] = {"dir": str(vdir.relative_to(ROOT)), "seconds": round(run_s, 1), "n_units": len(list(cells_v.glob("*.json"))), "pilot_status": "analyzed",
                         "pilot_counts": {"T1_rows": pil["T1"]["n_rows"], "T1_eligible": pil["T1"]["n_eligible"], "T2_rows": pil["T2"]["n_rows"], "T2_material": pil["T2"]["n_eligible"], "descriptive_rows": len(pil["descriptive_rows"])}}
log(f"(g) validation run {rep['validation_run']}")

# ---------------- (e) reuse refusals; (f) analyzer refusals ----------------
ef = {}
u0 = R.expected_units(GRID, True)[0]; n0 = R.unit_name(u0["kind"], u0["tokenizer"], u0["tag"], u0["h"]); rec0 = json.loads((cells_v / f"{n0}.json").read_text())
pv = dict(rec0["provenance"]); pv.pop("written_utc", None)
ef["matching_reusable"] = R.unit_reusable(cells_v / f"{n0}.json", pv) is True
for name, mut in (("foreign_grid", dict(pv, grid_sha256="0" * 64)), ("other_unit", dict(pv, unit=dict(pv["unit"], h=99))), ("other_mode", dict(pv, mode="study"))):
    try:
        R.unit_reusable(cells_v / f"{n0}.json", mut); ef[name] = False
    except R.ProvenanceError:
        ef[name] = True
ue = [u for u in R.expected_units(GRID, True) if u["kind"] == "eval"][0]; ne = R.unit_name("eval", ue["tokenizer"], ue["tag"], ue["h"])
with tempfile.TemporaryDirectory() as td:
    t = pathlib.Path(td) / "cells"; shutil.copytree(cells_v, t); p = t / f"{ne}.npz"; z = dict(np.load(p)); k0 = list(z)[0]; z[k0] = z[k0].copy(); z[k0].flat[0] += 1; np.savez_compressed(p, **z)
    pv_e = dict(json.loads((t / f"{ne}.json").read_text())["provenance"]); pv_e.pop("written_utc", None)
    try:
        R.unit_reusable(t / f"{ne}.json", pv_e); ef["tampered_npz"] = False
    except R.ProvenanceError:
        ef["tampered_npz"] = True
rep["fixtures"]["reuse"] = ef | {"all_ok": all(ef.values())}
af = {}
def try_inv(name, mutate, expect_refusal=True):
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td) / "cells"; shutil.copytree(cells_v, t); mutate(t)
        try:
            A.analyze(GRID, t, pilot_inputs, "validation", validation=True); af[name] = not expect_refusal
        except (A.InventoryError, A.BodyError, KeyError) as e:
            af[name] = expect_refusal; af[name + "_reason"] = str(e)[:120]
def edit_npz(t, fn):
    p = t / f"{ne}.npz"; z = {k: v.copy() for k, v in np.load(p).items()}; fn(z); np.savez_compressed(p, **z)
    j = json.loads((t / f"{ne}.json").read_text()); j["npz_sha256"] = R.sha(p); (t / f"{ne}.json").write_text(json.dumps(j))
def edit_json(t, fn, name=ne):
    j = json.loads((t / f"{name}.json").read_text()); fn(j); (t / f"{name}.json").write_text(json.dumps(j))
try_inv("complete_accepted", lambda t: None, expect_refusal=False)
try_inv("missing_unit", lambda t: (t / f"{ne}.json").unlink())
try_inv("extra_unit", lambda t: shutil.copy(t / f"{ne}.json", t / "eval__x__y__h9.json"))
try_inv("npz_digest_mismatch", lambda t: np.savez_compressed(t / f"{ne}.npz", dummy=np.zeros(1)))
try_inv("wrong_mode", lambda t: edit_json(t, lambda j: j["provenance"].__setitem__("mode", "study")))
try_inv("wrong_unit_identity", lambda t: edit_json(t, lambda j: j["provenance"].__setitem__("unit", dict(j["provenance"]["unit"], h=7))))
try_inv("threshold_digest_mismatch", lambda t: edit_json(t, lambda j: j.__setitem__("threshold_digests", {k: "0" * 64 for k in j["threshold_digests"]})))
try_inv("count_above_N", lambda t: edit_npz(t, lambda z: z["kgw|raw|fixed"].__setitem__((0, 0, 0), 60000)))
try_inv("not_nested_alpha", lambda t: edit_npz(t, lambda z: z["kgw|raw|same"].__setitem__((0, 0, GRID["alpha"].index(0.001), 0), z["kgw|raw|same"][0, 0, GRID["alpha"].index(0.05), 0] + 1)))
try_inv("wrong_shape", lambda t: edit_npz(t, lambda z: z.__setitem__("kgw|raw|same", z["kgw|raw|same"][:, :-1])))
try_inv("wrong_dtype", lambda t: edit_npz(t, lambda z: z.__setitem__("kgw|raw|fixed", z["kgw|raw|fixed"].astype(np.int32))))
try_inv("missing_crossed_variant", lambda t: edit_json(t, lambda j: j["crossed"]["kgw|raw"].pop("nominal")))
try_inv("crossed_wrong_B", lambda t: edit_json(t, lambda j: j["crossed"]["kgw|raw"]["nominal"].__setitem__("B", 7)))
try_inv("crossed_unpopulated", lambda t: edit_json(t, lambda j: j["crossed"]["kgw|raw"]["nominal"]["max"].__setitem__("ci95", [float("nan"), 1.0])))
try_inv("cal_boot_wrong_B", lambda t: edit_json(t, lambda j: j["cal_boot"]["kgw|raw"][sp_v["cells"][0]][f"conformal@1000"].__setitem__("sd", [0.0])))
try_inv("screen_constant_wrong", lambda t: edit_json(t, lambda j: j["screen"]["0.01"].__setitem__("c", 1)))
# R07 F1: the provenance gate, the threshold map and the committed thresholds record
nc = R.unit_name("cal", ue["tokenizer"], ue["tag"], ue["h"])
for fld, bad in (("grid_sha256", "0" * 64), ("core_sha256", "0" * 64), ("run_sha256", "0" * 64), ("tokens_manifest_sha256", "0" * 64), ("tokens_sha256", "0" * 64), ("key_eval_start", 23000), ("K", 7), ("key_fit_start", 24000), ("K_fit", 7), ("N", 1), ("lock_sha256", "x"), ("mode", "study"), ("study", "study2_v0.1")):
    try_inv(f"provenance_{fld}", lambda t, fld=fld, bad=bad: edit_json(t, lambda j: j["provenance"].__setitem__(fld, bad)))
try_inv("cal_provenance_tokens_sha", lambda t: edit_json(t, lambda j: j["provenance"].__setitem__("tokens_sha256", "0" * 64), name=nc))
try_inv("threshold_map_empty", lambda t: edit_json(t, lambda j: j.__setitem__("threshold_digests", {})))
try_inv("threshold_map_one_source_missing", lambda t: edit_json(t, lambda j: j["threshold_digests"].pop(list(j["threshold_digests"])[0])))
try_inv("threshold_map_foreign_digest", lambda t: edit_json(t, lambda j: j["threshold_digests"][list(j["threshold_digests"])[0]].__setitem__("thresholds", "0" * 64)))
try_inv("threshold_map_copy_mismatch", lambda t: edit_json(t, lambda j: j["provenance"]["threshold_digests"][list(j["threshold_digests"])[0]].__setitem__("boot", "0" * 64)))
try_inv("committed_thresholds_missing", lambda t: (t / f"{nc}__thresholds.npz").unlink())
def tamper_thresholds(t):
    p = t / f"{nc}__thresholds.npz"; z = {k: v.copy() for k, v in np.load(p).items()}; k0 = sorted(z)[0]; z[k0] = z[k0] * 0.5; np.savez_compressed(p, **z)
try_inv("committed_thresholds_tampered", tamper_thresholds)
try_inv("cal_summary_missing", lambda t: edit_json(t, lambda j: j.pop("summary"), name=nc))
try_inv("cal_N_C_wrong", lambda t: edit_json(t, lambda j: j.__setitem__("N_C", j["N_C"] + 1), name=nc))
try_inv("cal_alphas_reversed", lambda t: edit_json(t, lambda j: j.__setitem__("alphas", list(reversed(j["alphas"]))), name=nc))
def edit_cal_npz(t, fn):
    """Mutate the calibration thresholds file and re-record its digest everywhere, so the body contract (not the digest check) decides."""
    p = t / f"{nc}__thresholds.npz"; z = {k: v.copy() for k, v in np.load(p).items()}; fn(z); np.savez_compressed(p, **z); dig = R.sha(p)
    edit_json(t, lambda j: j.__setitem__("thresholds_sha256", dig), name=nc)
    src = f"{ue['tokenizer']}|{ue['tag']}"
    for u_ in R.expected_units(GRID, True):
        if u_["kind"] == "eval" and u_["h"] == ue["h"]:
            edit_json(t, lambda j: (j["threshold_digests"][src].__setitem__("thresholds", dig), j["provenance"]["threshold_digests"][src].__setitem__("thresholds", dig)), name=R.unit_name("eval", u_["tokenizer"], u_["tag"], u_["h"]))
try_inv("cal_threshold_above_one", lambda t: edit_cal_npz(t, lambda z: z["kgw|raw|conformal@1000|0.05"].__setitem__(0, 1.5)))
try_inv("cal_threshold_nonfinite", lambda t: edit_cal_npz(t, lambda z: z["kgw|raw|conformal@1000|0.05"].__setitem__(0, float("nan"))))
try_inv("cal_threshold_wrong_shape", lambda t: edit_cal_npz(t, lambda z: z.__setitem__("kgw|raw|conformal@1000|0.05", z["kgw|raw|conformal@1000|0.05"][:-1])))
try_inv("cal_threshold_extra_key", lambda t: edit_cal_npz(t, lambda z: z.__setitem__("kgw|raw|extra|0.05", z["kgw|raw|conformal@1000|0.05"])))
try_inv("cal_threshold_not_nested", lambda t: edit_cal_npz(t, lambda z: z.__setitem__("kgw|raw|conformal@1000|0.001", z["kgw|raw|conformal@1000|0.05"] + 1e-6)))
try_inv("cal_abstention_violated", lambda t: edit_cal_npz(t, lambda z: z["kgw|raw|conformal@100|0.001"].__setitem__(0, 1e-12)))
try_inv("cal_empirical_above_alpha", lambda t: edit_cal_npz(t, lambda z: z["kgw|raw|empirical|0.01"].__setitem__(0, 0.02)))
# R07 F10: the calibration summaries must equal their recomputation from the committed arrays
try_inv("cal_z_summary_emptied", lambda t: edit_json(t, lambda j: j["summary"]["kgw|raw"]["per_key_z"]["conformal@1000|0.01"].__setitem__("z", {}), name=nc))
try_inv("cal_abstaining_z_removed", lambda t: edit_json(t, lambda j: j["summary"]["kgw|raw"]["per_key_z"]["conformal@100|0.001"].pop("z"), name=nc))
try_inv("cal_cost_mean_wrong", lambda t: edit_json(t, lambda j: j["summary"]["kgw|raw"]["per_key_z"]["conformal@1000|0.01"]["z"].__setitem__("cost_mean", 12345), name=nc))
try_inv("cal_n_abstain_wrong", lambda t: edit_json(t, lambda j: j["summary"]["kgw|raw"]["per_key_z"]["conformal@1000|0.01"]["z"].__setitem__("n_abstain", 3), name=nc))
try_inv("cal_cost_field_missing", lambda t: edit_json(t, lambda j: j["summary"]["kgw|raw"]["per_key_z"]["conformal@1000|0.01"]["z"].pop("cost_q50"), name=nc))
try_inv("cal_kappa_wrong", lambda t: edit_json(t, lambda j: j["summary"]["kgw|raw"]["scheme"]["0.01"].__setitem__("kappa_emp", -4), name=nc))
try_inv("cal_z_emp_wrong", lambda t: edit_json(t, lambda j: j["summary"]["kgw|raw"]["scheme"]["0.01"].__setitem__("z_emp", 1.0), name=nc))
try_inv("cal_emp_detail_wrong", lambda t: edit_json(t, lambda j: j["summary"]["kgw|raw"]["scheme"]["0.01"]["emp_detail"].__setitem__("m", 999), name=nc))
# R07 F12: the zero-threshold boundary of the empirical multiplier (kappa = inf is the only admissible value)
def zero_emp(t, kappa):
    edit_cal_npz(t, lambda z: z.__setitem__("kgw|raw|empirical|0.001", np.array([0.0])))
    def fix(j):
        sc = j["summary"]["kgw|raw"]["scheme"]["0.001"]; sc["t_emp"] = 0.0; sc["z_emp"] = None; sc["emp_detail"]["unclipped"] = 0.0; sc["kappa_emp"] = kappa
    edit_json(t, fix, name=nc)
try_inv("cal_zero_threshold_kappa_inf_accepted", lambda t: zero_emp(t, float("inf")), expect_refusal=False)
try_inv("cal_zero_threshold_kappa_finite", lambda t: zero_emp(t, -4.0))
try_inv("cal_zero_threshold_kappa_one", lambda t: zero_emp(t, 1.0))
# R07 F2: the evaluation body contract
def recompute_screen(j, N):
    for a_ in GRID["alpha"]:
        s_ = T.screening(np.zeros(1), N, a_, GRID["beta"]); j["screen"][str(a_)] = {k: s_[k] for k in ("c", "r", "b")}
try_inv("N_E_wrong_screen_recomputed", lambda t: edit_json(t, lambda j: (j.__setitem__("N_E", 2 * j["N_E"]), recompute_screen(j, 2 * j["N_E"]))))
try_inv("alphas_reversed", lambda t: edit_json(t, lambda j: j.__setitem__("alphas", list(reversed(j["alphas"])))))
try_inv("variants_same_reversed", lambda t: edit_json(t, lambda j: j.__setitem__("variants_same", list(reversed(j["variants_same"])))))
try_inv("variants_cross_wrong", lambda t: edit_json(t, lambda j: j.__setitem__("variants_cross", j["variants_cross"][:-1])))
try_inv("cal_sources_reversed", lambda t: edit_json(t, lambda j: j.__setitem__("cal_sources", list(reversed(j["cal_sources"])))))
try_inv("fixed_variants_wrong", lambda t: edit_json(t, lambda j: j.__setitem__("fixed_variants", ["nominal", "guaranteed"])))
try_inv("cross_tokenizer_fabricated", lambda t: (edit_json(t, lambda j: j.__setitem__("cross_tokenizers", ["x"])), edit_npz(t, lambda z: z.__setitem__("kgw|raw|cross", np.zeros((1, len(sp_v["cells"]), len(R.cross_variant_names(GRID)), sp_v["K"]), dtype=np.uint16)))))
try_inv("extra_array_key", lambda t: edit_npz(t, lambda z: z.__setitem__("kgw|raw|extra", z["kgw|raw|fixed"])))
try_inv("missing_array_key", lambda t: edit_npz(t, lambda z: z.pop("gumbel|distinct|same")))
try_inv("cal_boot_nan", lambda t: edit_json(t, lambda j: j["cal_boot"]["kgw|raw"][sp_v["cells"][0]]["conformal@1000"]["sd"].__setitem__(0, float("nan"))))
try_inv("cal_boot_negative", lambda t: edit_json(t, lambda j: j["cal_boot"]["kgw|raw"][sp_v["cells"][0]]["conformal@1000"]["key_mean"].__setitem__(0, -1.0)))
try_inv("cal_boot_above_one", lambda t: edit_json(t, lambda j: j["cal_boot"]["kgw|raw"][sp_v["cells"][0]]["tolerance@1000"]["q99"].__setitem__(0, 1.5)))
try_inv("screen_r_nan", lambda t: edit_json(t, lambda j: j["screen"]["0.01"].__setitem__("r", float("nan"))))
try_inv("screen_b_wrong", lambda t: edit_json(t, lambda j: j["screen"]["0.01"].__setitem__("b", 0.5)))
try_inv("crossed_se_nan", lambda t: edit_json(t, lambda j: j["crossed"]["kgw|raw"]["nominal"]["max"].__setitem__("boot_se", float("nan"))))
nf = len([k for k in af if not k.endswith("_reason")])
rep["fixtures"]["analyzer"] = af | {"all_ok": all(v for k, v in af.items() if not k.endswith("_reason")), "n": nf}
# the REP decision function on constructed values (exactly equal; within noise; gross)
def rep_decide(sd3, se3, sd2, se2):
    return bool(abs(sd3 - sd2) > GRID["rep"]["gross_se"] * np.sqrt(se3 ** 2 + se2 ** 2) + A.REP_TOL)   # a Python bool (a NumPy bool is never `is False`)
rep["fixtures"]["rep_decision"] = {"equal": rep_decide(0.005, 1e-4, 0.005, 1e-4) is False, "noise": rep_decide(0.0052, 1e-4, 0.005, 1e-4) is False, "gross": rep_decide(0.008, 1e-4, 0.005, 1e-4) is True, "zero_se_equal": rep_decide(0.0, 0.0, 0.0, 0.0) is False}
log(f"(e) reuse {rep['fixtures']['reuse']['all_ok']}; (f) analyzer {rep['fixtures']['analyzer']['all_ok']} over {nf}; REP decision {rep['fixtures']['rep_decision']}")

# ---------------- (h) the cost probe and the projection ----------------
probe = {}
law = C.ZipfIID(128256, 1.1)
with tempfile.TemporaryDirectory() as td:
    tmp = pathlib.Path(td); (tmp / "cells").mkdir(); (tmp / "thr").mkdir()
    sp_p = {"cells": [f"probe_{i}" for i in range(len(GRID["cells"]))], "toks": {"probe": {"V": 128256}, "probe2": {"V": 128256}}, "h": [0, 2], "K": GRID["K"], "K_fit": GRID["K_fit"], "N_cal": GRID["N_cal"], "N_cal_set": GRID["N_cal_set"], "N_eval": GRID["N_eval"]}
    ke = list(range(VK + 100000, VK + 100000 + GRID["K"])); kf = list(range(VK + 200000, VK + 200000 + GRID["K_fit"]))
    XC = law.sample(GRID["N_cal_set"], GRID["L"], vrng(7)).astype(np.int32); XE = law.sample(GRID["N_eval"], GRID["L"], vrng(8)).astype(np.int32)
    for h in (0, 2):
        with open(tmp / "probe.log", "a") as tl:
            t0 = time.time(); prov = {"unit": {"kind": "cal", "tokenizer": "probe", "tag": "probe_0", "h": h}}
            thr = R.run_cal_unit(XC, 128256, h, "probe", "probe_0", GRID, sp_p, "probe", tmp / "cells", tmp / "thr", ke, kf, prov, tl); tc = time.time() - t0
            thr_all = {(tk, c): thr for tk in sp_p["toks"] for c in sp_p["cells"]}
            t0 = time.time(); prov = {"unit": {"kind": "eval", "tokenizer": "probe", "tag": "probe_0", "h": h}}
            R.run_eval_unit(XE, 128256, h, "probe", "probe_0", GRID, sp_p, "probe", tmp / "cells", thr_all, ke, prov, tl); te = time.time() - t0
        nC = len(S.build_chain(XC, 128256, "c", h).D); nE = len(S.build_chain(XE, 128256, "e", h).D)
        probe[f"h{h}"] = {"cal_seconds": round(tc, 1), "eval_seconds": round(te, 1), "n_tuples_cal": nC, "n_tuples_eval": nE}
        log(f"(h) probe h={h}: pass 1 {tc:.1f}s (|D| {nC}), pass 2 {te:.1f}s (|D| {nE})")
probe["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30, 2)
# projection: per pass, seconds = a + b |D| from the two probe points; every production unit's |D| from INPUTS (the raw rule's tuple count of the set)
inputs = json.loads((ROOT / R.INPUTS).read_text())
def lin(x0, y0, x1, y1):
    b = (y1 - y0) / (x1 - x0); return y0 - b * x0, b
ac, bc = lin(probe["h0"]["n_tuples_cal"], probe["h0"]["cal_seconds"], probe["h2"]["n_tuples_cal"], probe["h2"]["cal_seconds"])
ae, be = lin(probe["h0"]["n_tuples_eval"], probe["h0"]["eval_seconds"], probe["h2"]["n_tuples_eval"], probe["h2"]["eval_seconds"])
tot = 0.0; per = {}
for h in GRID["h"]:
    blk = inputs["blocks"][f"h{h}|raw"]["sets"]
    for tok in GRID["tokenizers"]:
        for tag in GRID["cells"]:
            nc = blk[f"{tok}|{tag}|C{max(GRID['N_cal'])}"]["n_tuples"]; ne_ = blk[f"{tok}|{tag}|E"]["n_tuples"]
            s = max(ac + bc * nc, 0.5 * probe["h0"]["cal_seconds"]) + max(ae + be * ne_, 0.5 * probe["h0"]["eval_seconds"]); per[f"{tok}|{tag}|h{h}"] = round(s, 1); tot += s
probe["projection_hours"] = round(tot / 3600, 2); probe["per_unit_pair_seconds"] = per; probe["model"] = {"cal": [ac, bc], "eval": [ae, be], "note": "seconds = a + b |D| per pass, from the two probe points; an extrapolation, not a guarantee"}
rep["cost"] = probe
log(f"(h) projection {probe['projection_hours']} h (budget {GRID['budget_hours']} h); peak RSS {probe['peak_rss_gb']} GB")

# ---------------- (i) eligibility and materiality from the key-free inputs ----------------
pr = GRID["primary"]; elig = {"T1": {}, "T2": {}}; n1 = n2 = 0; signs = {"help": 0, "harm": 0}
for h in pr["h"]:
    for rule in pr["rules"]:
        blk = inputs["blocks"][f"h{h}|{rule}"]
        for tok in pr["tokenizers"]:
            for tagE in GRID["cells"]:
                pnom = blk["sets"][f"{tok}|{tagE}|E"]["pred_fixed"][pr["alpha"]]["nominal"]
                for tagC in GRID["cells"]:
                    cls = A.pair_class(tagC, tagE, GRID); pk = blk["pairs"][f"{tok}|{tagC}->{tok}|{tagE}"]
                    for nc in pr["N_cal"]:
                        p = pk["per_key"][str(nc)][pr["alpha"]][pr["method"]]; key = f"h{h}|{rule}|{tok}|N{nc}|{cls}"
                        e1 = p["theory_share"] >= pr["min_theory_share"] and not p["flags"] and p["sd_cond"] > 0
                        Rp = p["sd_cond"] / pnom["sd_cond"]; e2 = Rp < pr["T2_material_band"][0] or Rp > pr["T2_material_band"][1]
                        elig["T1"][key] = elig["T1"].get(key, 0) + int(e1); elig["T2"][key] = elig["T2"].get(key, 0) + int(e2); n1 += e1; n2 += e2
                        if e2:
                            signs["harm" if Rp > 1 else "help"] += 1
rep["eligibility"] = {"T1_eligible": int(n1), "T2_material": int(n2), "T2_predicted_signs": signs, "by_block": elig, "n_primary_rows": len(pr["h"]) * len(pr["rules"]) * len(pr["tokenizers"]) * len(GRID["cells"]) ** 2 * len(pr["N_cal"])}
rep["inputs_consistency_with_study2"] = inputs.get("study2_consistency_summary")
log(f"(i) T1 eligible {n1}, T2 material {n2} {signs} of {rep['eligibility']['n_primary_rows']}")

rep["all_ok"] = bool(a_ok["all_ok"] and fx["tolerance_index_maximal"] and all(v["ok"] for v in cont.values()) and fx["discrete_conformal"]["ok"] and fx["scheme_thresholds_properties"] and fx["counts_below_brute_force"]
                     and fx["predictor"]["exact_beta_ok"] and fx["predictor"]["monte_carlo_ok"] and fx["finite_shares"]["ok"] and fx["cross_cov"]["brute_and_study1_equal"] and fx["cross_cov"]["across_keys_ok"] and rep["fixtures"]["key_policy"]["all_ok"]
                     and rep["fixtures"]["lock"]["ok"] and rep["fixtures"]["reuse"]["all_ok"] and rep["fixtures"]["analyzer"]["all_ok"] and all(rep["fixtures"]["rep_decision"].values()))
rep["seconds"] = round(time.time() - T0, 1)
(OUTD / "VALIDATION.json").write_text(json.dumps(rep, indent=1, default=float))
log(f"DONE all_ok = {rep['all_ok']}")
