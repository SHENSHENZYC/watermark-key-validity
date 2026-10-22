"""Study 4 report builder (protocol v0.1): every table, figure and number in research/STUDY4_REPORT_v0.1.md comes from the locked outputs
(outputs/study4_v0.1/results.json and results_arrays.npz, RUN_MANIFEST.json, the pinned INPUTS.json, Study 3's committed record), never
typed by hand (rule A4.1 of the research-project-guide).

Before writing anything the builder RE-COMPUTES, with its own code (not s4_analyze's functions), from the analyzer's per-key arrays:
  - every descriptive row: the key-mean power, the observed SD, the two-way between-key component (s_K^2 - MS_E/n on the indicator table
    of the per-text p-values against the key's committed threshold, read from Study 3's record), the binomial proxy, the quantiles, the
    cost statistics and the abstention counts;
  - W1 (the realised key-median cost with its key-bootstrap interval under the protocol's seed convention, the predicted median from the
    pilot law and the thresholds, the class), W2 (both two-way components, the ratio, the paired key bootstrap, the decision) and W3 (the
    observed SD of the model-null levels, its ratio to the predictor's SD, the key bootstrap, eligibility, the class) and the three verdicts;
  - every null row's level statistics from the stored counts;
and asserts that all of these equal results.json (every mismatch is collected and reported before raising). It then computes the builder's
own blocks the protocol lists (section 7): the per-key operating points against Study 3's stored null levels and the model-null levels, the
mechanism diagnostic, the design-remedy contrasts, the per-prompt pairing, the length curves and the transfer-source summaries, labelled as
its own; and writes <report dir>/: tables.md, the supplements, descriptive_rows_full.csv.gz, null_rows_full.csv.gz, prose_values.json,
checks.json and fig1..fig6 (.png, .svg); then assembles the report from research/study4/report_prose_v0.1.md by filling <<TABLE:name>>,
<<FIG:name>> and [[name]] and refusing any unresolved placeholder (registered-but-unused names are listed).
Usage: .venv/bin/python research/study4/s4_report.py                    (study mode: verifies the lock; writes outputs/study4_v0.1/report/ and research/STUDY4_REPORT_v0.1.md)
       .venv/bin/python research/study4/s4_report.py --fixture --results <results.json of a FIXTURE inventory> --out-dir <dir outside the repository>
       (fixture mode: the results file must carry the FIXTURE marker; the output is labelled FIXTURE and can never be the canonical report or report directory)
Not pinned by the lock.
"""
import gzip, hashlib, json, pathlib, re, sys, time
import numpy as np
from scipy.stats import norm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study3")); sys.path.insert(0, str(ROOT / "research/study2")); sys.path.insert(0, str(ROOT / "research/study1"))
from s4_run import OUT, STUDY, GRID_CANON, verify_lock, expected_units, unit_name, arm_spec   # noqa: E402  (pinned; read only)
import s4_record as RC   # noqa: E402  (pinned; read only: Study 3's committed thresholds and null counts)

T_START = time.time(); ARGV = sys.argv[1:]; FIXTURE = "--fixture" in ARGV; REAL = not FIXTURE
PROSE = HERE / "report_prose_v0.1.md"
if FIXTURE:
    RES = pathlib.Path(ARGV[ARGV.index("--results") + 1]).resolve(); OUTDIR = pathlib.Path(ARGV[ARGV.index("--out-dir") + 1]).resolve()
    for p in (RES, OUTDIR):
        if ROOT.resolve() in p.parents or p == ROOT.resolve():
            raise SystemExit(f"fixture mode reads and writes outside the repository only ({p})")
    REPORT = OUTDIR / "STUDY4_REPORT_fixture.md"; MANIFEST = None
else:
    if ARGV:
        raise SystemExit("study mode takes no arguments (canonical paths only)")
    RES = OUT / "results.json"; OUTDIR = OUT / "report"; REPORT = ROOT / "research/STUDY4_REPORT_v0.1.md"; MANIFEST = OUT / "RUN_MANIFEST.json"
    if not MANIFEST.exists():
        raise SystemExit("study mode needs outputs/study4_v0.1/RUN_MANIFEST.json (run s4_manifest.py first)")
OUTDIR.mkdir(parents=True, exist_ok=True)
BOOT_B, BOOT_SALT, BUILDER_SALT, TOL = 200, 20261019, 20261030, 1e-9
# dataviz palette (the Study 3 builder's validated set; the rules are slots 1/2, a third slot for a third series; the methods by marker)
COL = {"raw": "#2a78d6", "distinct": "#eb6834", "third": "#1baf7a", "ink": "#0b0b0b", "muted": "#898781", "grid": "#e1e0d9", "surface": "#fcfcfb", "accent": "#e34948"}
SEQ6 = ["#104281", "#2a78d6", "#86b6ef", "#eb6834", "#1baf7a", "#898781"]
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": COL["ink"], "xtick.color": COL["muted"], "ytick.color": COL["muted"], "axes.grid": True,
                     "grid.color": COL["grid"], "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "figure.facecolor": COL["surface"],
                     "axes.facecolor": COL["surface"], "savefig.facecolor": COL["surface"], "lines.linewidth": 1.6, "lines.markersize": 4.0, "svg.hashsalt": "study4_v0.1"})


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


# ------------------------------------------------------------------ loading
grid = json.loads((ROOT / GRID_CANON).read_text()); lock, _, Rrec = verify_lock(OUT / "PRE_RUN_LOCK.json", ROOT / GRID_CANON); LOCK_SHA = sha(OUT / "PRE_RUN_LOCK.json")
if RES.exists():
    RES_BYTES = RES.read_bytes()
elif REAL and (OUT / "results.json.gz").exists():
    RES_BYTES = gzip.decompress((OUT / "results.json.gz").read_bytes())
else:
    raise SystemExit(f"no results file at {RES}")
RES_SHA = hashlib.sha256(RES_BYTES).hexdigest(); res = json.loads(RES_BYTES); del RES_BYTES
if res.get("study") != STUDY or res.get("mode") != "study":
    raise SystemExit(f"the results file is not a study-mode analysis of {STUDY}")
if FIXTURE and "FIXTURE" not in res:
    raise SystemExit("fixture mode: the results file carries no FIXTURE marker")
if REAL and "FIXTURE" in res:
    raise SystemExit("study mode: the results file carries a FIXTURE marker")
if res["inventory"]["lock_sha256"] != LOCK_SHA:
    raise SystemExit("the results file was produced under another lock")
ARR_PATH = RES.with_name(RES.stem + "_arrays.npz")
if sha(ARR_PATH) != res["arrays_sha256"]:
    raise SystemExit("results_arrays.npz differs from the digest recorded in results.json")
Z = np.load(ARR_PATH); ARR = {k: Z[k] for k in Z.files}
manifest = json.loads(MANIFEST.read_text()) if MANIFEST else None
if REAL:
    if manifest["lock"]["sha256"] != LOCK_SHA or manifest["inventory"]["inventory_sha256"] != res["inventory"]["inventory_sha256"]:
        raise SystemExit("RUN_MANIFEST.json names another lock or another inventory than results.json")
    if manifest.get("analysis_output", {}).get("sha256") not in (None, RES_SHA):
        raise SystemExit("results.json differs from the digest recorded in RUN_MANIFEST.json")
inputs = json.loads((OUT / "INPUTS.json").read_text())
if lock["hashes"]["outputs/study4_v0.1/INPUTS.json"] != sha(OUT / "INPUTS.json") or res["inputs_sha256"] != sha(OUT / "INPUTS.json"):
    raise SystemExit("INPUTS.json is not the pinned pre-lock inputs this analysis read")
AX = res["axes"]; RULES = AX["rules"]; LENGTHS = AX["lengths"]; SOURCES = AX["sources"]; VARIANTS = AX["variants"]; ALPHAS = [float(a) for a in AX["alphas"]]; VS3 = AX["null_variants"]; VFIX = AX["null_fixed_variants"]
CELLS = list(grid["cells"]); ARMS = [a["name"] for a in grid["arms"]]; PRIMARY = grid["primary_arm"]; L_PRIM = grid["primary_length"]; A_PRIM = float(grid["primary_alpha"]); N_TX = grid["prompts"]["n_watermarked"]
BETA = grid["beta"]; NCALS = grid["N_cal"]; POWER_KEYS = list(grid["keys"]["power_keys"]); K4 = len(POWER_KEYS); TOK = grid["model"]["tokenizer"]
METH_LABEL = {"nominal": "nominal", "multiplier20": "multiplier20 (α/20)", "empirical": "empirical multiplier", "pooled": "pooled", "conformal": "per-key conformal", "tolerance": "per-key tolerance"}
CELL_LABEL = {c: f"{c.rsplit('_', 2)[0]}/{c.rsplit('_', 2)[1]}@{c.rsplit('_', 2)[2]}" for c in SOURCES}
ARM_LABEL = {a["name"]: f"h = {a['h']}, δ = {a['delta']}" for a in grid["arms"]}
CHECKS = {"mismatches": [], "verified": {}}; VALUES = {}; USED = set()


def reg(name, value):
    VALUES[name] = value; return value


def fnum(x, d=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return f"{x:.{d}f}"


def pp(x, d=1):
    return "—" if x is None or not np.isfinite(x) else f"{100 * x:.{d}f}"


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        if len(r) != len(header):
            raise RuntimeError(f"a table row has {len(r)} cells against {len(header)} header cells: {r[:3]}")
        out.append("| " + " | ".join(str(x).replace("|", "\\|") for x in r) + " |")
    return "\n".join(out)


def rng_for(name, salt=BOOT_SALT):
    return np.random.default_rng([int(hashlib.sha256(str(name).encode()).hexdigest()[:8], 16), int(salt)])


def boot_idx(K, name, salt=BOOT_SALT, B=BOOT_B):
    return rng_for(name, salt).integers(0, K, size=(B, K))


def quant(x):
    return float(np.quantile(x, 0.025)), float(np.quantile(x, 0.975))


def twoway_own(Y):
    """s_K^2 - MS_E/n on a K x n indicator table (the builder's own code)."""
    Y = np.asarray(Y, dtype=np.float64); K, n = Y.shape; rowm = Y.mean(axis=1); colm = Y.mean(axis=0); gm = Y.mean()
    resid = Y - rowm[:, None] - colm[None, :] + gm; ms_e = float((resid ** 2).sum() / ((K - 1) * (n - 1))); s_k2 = float(rowm.var(ddof=1)); raw = s_k2 - ms_e / n
    return {"sd": float(np.sqrt(max(raw, 0.0))), "raw": float(raw), "s_k2": s_k2, "ms_e": ms_e, "prompt_raw": float(colm.var(ddof=1) - ms_e / K)}


def proxy_own(pi, n):
    pi = np.asarray(pi, dtype=np.float64); var_obs = float(pi.var(ddof=1)); noise = float(np.mean(pi * (1 - pi) / (n - 1))); raw = var_obs - noise
    return {"sd": float(np.sqrt(max(raw, 0.0))), "raw": raw, "noise": noise, "var_obs": var_obs}


def close(a, b, what, tol=TOL):
    if a is None and b is None:
        return
    if a is None or b is None or (isinstance(a, float) and isinstance(b, float) and (np.isnan(a) != np.isnan(b))):
        CHECKS["mismatches"].append({"what": what, "own": a, "file": b}); return
    if isinstance(a, float) and isinstance(b, float) and np.isnan(a) and np.isnan(b):
        return
    if isinstance(a, str) or isinstance(b, str) or isinstance(a, bool):
        if a != b:
            CHECKS["mismatches"].append({"what": what, "own": a, "file": b})
        return
    if abs(float(a) - float(b)) > tol * max(1.0, abs(float(b))):
        CHECKS["mismatches"].append({"what": what, "own": float(a), "file": float(b)})


def variant_parts(v):
    if "@" in v:
        m, n = v.split("@"); return m, int(n)
    return v, None


CAL = {}
def cal_unit(src, h):
    if (src, h) not in CAL:
        CAL[(src, h)] = Rrec.cal(TOK, src, h)
    return CAL[(src, h)]


def thr_vec(src, h, rule, variant, alpha, keys):
    m, nc = variant_parts(variant)
    if m == "nominal":
        return np.full(len(keys), alpha)
    if m == "multiplier20":
        return np.full(len(keys), alpha * BETA)
    t = cal_unit(src, h).threshold("kgw", rule, m, alpha, nc)
    return np.array([t[k - 23000] for k in keys]) if m in ("conformal", "tolerance") else np.full(len(keys), float(t[0]))


def classify_band(lo, hi, band):
    if band[0] <= lo and hi <= band[1]:
        return "consistent"
    if hi < band[0] or lo > band[1]:
        return "inconsistent"
    return "unresolved"


def classify_side(lo, hi, side, band):
    if side == "below_1":
        return "agree" if hi < 1 else ("disagree" if lo > 1 else "unresolved")
    return {"consistent": "agree", "inconsistent": "disagree", "unresolved": "unresolved"}[classify_band(lo, hi, band)]


# ------------------------------------------------------------------ the per-key data of the generation units
GEN = {}   # (cell, arm) -> dict(keys, ok, counts, pv, green)
for cell in CELLS:
    for arm in ARMS:
        k = f"{cell}|{arm}"
        if f"counts|{k}" not in ARR:
            continue
        GEN[(cell, arm)] = {"keys": [int(x) for x in ARR[f"keys|{k}"]], "ok": ARR[f"contract_ok|{k}"].astype(bool), "counts": ARR[f"counts|{k}"].astype(np.int64), "pv": ARR[f"pvalues|{k}"], "green": ARR[f"green_share|{k}"]}
        if GEN[(cell, arm)]["keys"] != POWER_KEYS:
            raise SystemExit(f"{k}: the arrays' key order differs from the grid's power keys")
n_gen_units = sum(1 for u in expected_units(grid, False) if u["kind"] == "gen"); n_fail = len(res["integrity"]["contract_failures"])
close(n_fail / n_gen_units, res["integrity"]["contract_failure_share"], "integrity.contract_failure_share"); close(bool(n_fail / n_gen_units > grid["integrity"]["max_contract_failure_share"]), res["integrity"]["run_void"], "integrity.run_void")
if res["integrity"]["run_void"]:
    raise SystemExit("the run is void (section 9 rule 1): no report is built from it")

# ---- every descriptive row recomputed
t0 = time.time(); desc_file = {(r["cell"], r["arm"], r["rule"], r["L"], r["source"], r["variant"], r["alpha"]): r for r in res["descriptive_rows"]}; n_desc = 0
for (cell, arm), G in GEN.items():
    h = arm_spec(grid, arm)["h"]; ok = G["ok"]; keys_ok = [k for k, o in zip(G["keys"], ok) if o]
    if ok.sum() < 2:
        continue
    iv_nom = VARIANTS.index("nominal")
    for ir, rule in enumerate(RULES):
        for il, L in enumerate(LENGTHS):
            for isrc, src in enumerate(SOURCES):
                for iv, v in enumerate(VARIANTS):
                    if v in VFIX and isrc > 0:
                        continue
                    for ia, a in enumerate(ALPHAS):
                        r = desc_file.get((cell, arm, rule, L, (None if v in VFIX else src), v, a))
                        if r is None:
                            CHECKS["mismatches"].append({"what": f"descriptive row missing in file: {cell} {arm} {rule} {L} {src} {v} {a}"}); continue
                        pi = G["counts"][ok, ir, il, isrc, iv, ia] / N_TX; pnom = G["counts"][ok, ir, il, isrc, iv_nom, ia] / N_TX; cost = pnom - pi
                        thr = thr_vec(src, h, rule, v, a, keys_ok); Yv = (G["pv"][ok, :, ir, il] < thr[:, None]).astype(np.float64); tw = twoway_own(Yv); bp = proxy_own(pi, N_TX)
                        m, nc = variant_parts(v); abst = int((thr <= 0).sum()) if m in ("conformal", "tolerance") else 0
                        for what, own, fil in (("power_mean", float(pi.mean()), r["power_mean"]), ("power_sd_observed", float(pi.std(ddof=1)), r["power_sd_observed"]), ("power_sd_between_twoway", tw["sd"], r["power_sd_between_twoway"]),
                                               ("power_var_between_raw_twoway", tw["raw"], r["power_var_between_raw_twoway"]), ("ms_resid_twoway", tw["ms_e"], r["ms_resid_twoway"]), ("power_sd_between_binomial_proxy", bp["sd"], r["power_sd_between_binomial_proxy"]),
                                               ("power_var_between_raw_binomial_proxy", bp["raw"], r["power_var_between_raw_binomial_proxy"]), ("mean_binomial_var", bp["noise"], r["mean_binomial_var"]),
                                               ("power_q05", float(np.quantile(pi, 0.05)), r["power_q05"]), ("power_q50", float(np.quantile(pi, 0.5)), r["power_q50"]), ("power_q95", float(np.quantile(pi, 0.95)), r["power_q95"]),
                                               ("cost_mean", float(cost.mean()), r["cost_mean"]), ("cost_q50", float(np.quantile(cost, 0.5)), r["cost_q50"]), ("cost_q05", float(np.quantile(cost, 0.05)), r["cost_q05"]), ("cost_q95", float(np.quantile(cost, 0.95)), r["cost_q95"]),
                                               ("keys_abstaining", float(abst), float(r["keys_abstaining"])), ("K", float(ok.sum()), float(r["K"]))):
                            close(own, fil, f"desc {cell} {arm} {rule} {L} {src} {v} {a} {what}")
                        n_desc += 1
CHECKS["verified"]["descriptive_rows"] = n_desc; close(float(n_desc), float(len(res["descriptive_rows"])), "descriptive rows count")

# ---- W1 recomputed
w1 = res["W1"]["setting"]; ir1, il1, ia1 = RULES.index(w1["rule"]), LENGTHS.index(w1["length"]), ALPHAS.index(float(w1["alpha"])); iv_c1, iv_n1 = VARIANTS.index(f"{w1['method']}@{w1['N_cal']}"), VARIANTS.index("nominal")
W1_OWN = {}
for row in res["W1"]["rows"]:
    cell = row["cell"]; G = GEN[(cell, w1["arm"])]; ok = G["ok"]; keys_ok = [k for k, o in zip(G["keys"], ok) if o]; isrc = SOURCES.index(cell); h1 = arm_spec(grid, w1["arm"])["h"]
    real = (G["counts"][ok, ir1, il1, isrc, iv_n1, ia1] - G["counts"][ok, ir1, il1, isrc, iv_c1, ia1]) / N_TX
    law = np.sort(np.array(inputs["pilot_law"]["arms"][w1["arm"]]["by_cell"][cell]["p_values"][f"{w1['rule']}@{w1['length']}"], dtype=np.float64)); nl = len(law)
    t_keys = thr_vec(cell, h1, w1["rule"], f"{w1['method']}@{w1['N_cal']}", float(w1["alpha"]), keys_ok)
    G_at = lambda t: np.where(np.asarray(t) > 0, np.searchsorted(law, np.asarray(t), side="left") / nl, 0.0)
    pred = G_at(np.full(len(keys_ok), float(w1["alpha"]))) - G_at(t_keys); tol = float(inputs["W1_tolerance"][cell]["tolerance_pp"]) / 100
    idx = boot_idx(len(real), f"W1|{cell}"); med_b = np.median(real[idx], axis=1); lo, hi = quant(med_b); pm = float(np.median(pred)); cls = classify_band(lo, hi, (pm - tol, pm + tol))
    W1_OWN[cell] = {"real": real, "pred": pred, "lo": lo, "hi": hi, "median": float(np.median(real)), "pred_median": pm, "tol": tol, "class": cls, "nominal_power": G["counts"][ok, ir1, il1, isrc, iv_n1, ia1] / N_TX}
    for what, own, fil in (("realised_median", float(np.median(real)), row["realised_median"]), ("realised_mean", float(real.mean()), row["realised_mean"]), ("ci_lo", lo, row["ci_lo"]), ("ci_hi", hi, row["ci_hi"]), ("predicted_median", pm, row["predicted_median"]),
                           ("predicted_mean", float(pred.mean()), row["predicted_mean"]), ("tolerance", tol, row["tolerance"]), ("class", cls, row["class"]), ("share_keys_within_tol", float(np.mean(np.abs(real - pred) <= tol)), row["share_keys_within_tol"]),
                           ("corr_real_pred", (float(np.corrcoef(real, pred)[0, 1]) if real.std() > 0 and pred.std() > 0 else None), row["corr_real_pred"]), ("pilot_law_n", float(nl), float(row["pilot_law_n"]))):
        close(own, fil, f"W1 {cell} {what}")
n_c = sum(1 for c in W1_OWN.values() if c["class"] == "consistent"); n_i = sum(1 for c in W1_OWN.values() if c["class"] == "inconsistent")
close(bool(n_c >= w1["min_consistent_cells"] and n_i <= w1["max_inconsistent_cells"]), res["W1"]["pass"], "W1 pass"); CHECKS["verified"]["W1_rows"] = len(W1_OWN)

# ---- W2 recomputed
w2 = res["W2"]["setting"]; il2, ia2 = LENGTHS.index(w2["length"]), ALPHAS.index(float(w2["alpha"])); W2_OWN = {}
for row in res["W2"]["rows"]:
    cell, rule = row["cell"], row["rule"]; G = GEN[(cell, w2["arm"])]; ok = G["ok"]; keys_ok = [k for k, o in zip(G["keys"], ok) if o]; ir = RULES.index(rule); h2 = arm_spec(grid, w2["arm"])["h"]
    P = G["pv"][ok, :, ir, il2]; t_c = thr_vec(cell, h2, rule, f"{w2['method']}@{w2['N_cal']}", float(w2["alpha"]), keys_ok)
    Yn = (P < float(w2["alpha"])).astype(np.float64); Yc = (P < t_c[:, None]).astype(np.float64); bn, bc = twoway_own(Yn), twoway_own(Yc); K = Yn.shape[0]
    R_obs = bc["sd"] / bn["sd"] if bn["sd"] > 0 else float("nan"); idx = boot_idx(K, f"W2|{cell}|{rule}"); Rb = []
    for ki in idx:
        vn = twoway_own(Yn[ki])["sd"]; vc = twoway_own(Yc[ki])["sd"]; Rb.append(vc / vn if vn > 0 else np.nan)
    Rb = np.array(Rb); fin = np.isfinite(Rb); side = w2["predicted_side"][rule]
    if fin.mean() < w2["min_finite_resample_share"] or not np.isfinite(R_obs):
        lo = hi = float("nan"); cls = "unresolved"
    else:
        lo, hi = quant(Rb[fin]); cls = classify_side(lo, hi, side, tuple(w2["band"]))
    W2_OWN[(cell, rule)] = {"R": R_obs, "lo": lo, "hi": hi, "class": cls, "sd_n": bn["sd"], "sd_c": bc["sd"], "side": side, "n_fin": int(fin.sum()), "obs_n": float(np.sqrt(bn["s_k2"])), "obs_c": float(np.sqrt(bc["s_k2"]))}
    bpn, bpc = proxy_own(Yn.mean(axis=1), N_TX), proxy_own(Yc.mean(axis=1), N_TX)
    for what, own, fil in (("sd_between_nominal", bn["sd"], row["sd_between_nominal"]), ("sd_between_method", bc["sd"], row["sd_between_method"]), ("var_between_raw_nominal", bn["raw"], row["var_between_raw_nominal"]), ("var_between_raw_method", bc["raw"], row["var_between_raw_method"]),
                           ("ms_resid_nominal", bn["ms_e"], row["ms_resid_nominal"]), ("ms_resid_method", bc["ms_e"], row["ms_resid_method"]), ("var_prompt_raw_nominal", bn["prompt_raw"], row["var_prompt_raw_nominal"]), ("sd_observed_nominal", float(np.sqrt(bn["s_k2"])), row["sd_observed_nominal"]),
                           ("proxy sd nominal", bpn["sd"], row["binomial_proxy"]["sd_between_nominal"]), ("proxy sd method", bpc["sd"], row["binomial_proxy"]["sd_between_method"]), ("R_pow", R_obs, row["R_pow"]), ("ci_lo", lo, row["ci_lo"]), ("ci_hi", hi, row["ci_hi"]),
                           ("finite_resamples", float(fin.sum()), float(row["finite_resamples"])), ("class", cls, row["class"]), ("power_mean_nominal", float(Yn.mean()), row["power_mean_nominal"]), ("power_mean_method", float(Yc.mean()), row["power_mean_method"])):
        close(own, fil, f"W2 {cell} {rule} {what}")
n_a = sum(1 for c in W2_OWN.values() if c["class"] == "agree"); n_d = sum(1 for c in W2_OWN.values() if c["class"] == "disagree")
close(bool(n_a >= w2["min_agree_rows"] and n_d <= w2["max_disagree_rows"]), res["W2"]["pass"], "W2 pass"); CHECKS["verified"]["W2_rows"] = len(W2_OWN)

# ---- every null row's statistics and W3 recomputed
w3 = res["W3"]["setting"]; null_file = {(r["cell"], r["h"], r["family"], r["rule"], r["L"], r["source"], r["variant"], r["alpha"]): r for r in res["null_rows"]}; n_null = 0; W3_OWN = {}
for key_, r in null_file.items():
    cell, h, fam, rule, L, src, v, a = key_; N_E = r["N_E"]; ia = ALPHAS.index(float(a))
    if src is None:
        lv = ARR[f"null|{cell}|h{h}|{fam}|{rule}|L{L}|fixed"][VFIX.index(v), ia].astype(np.float64) / N_E
    else:
        lv = ARR[f"null|{cell}|h{h}|{fam}|{rule}|L{L}|same"][SOURCES.index(src), VS3.index(v), ia].astype(np.float64) / N_E
    for what, own, fil in (("level_mean", float(lv.mean()), r["level_mean"]), ("level_sd", float(lv.std(ddof=1)), r["level_sd"]), ("share_above_alpha", float((lv > a).mean()), r["share_above_alpha"]), ("q99", float(np.quantile(lv, 0.99)), r["q99"])):
        close(own, fil, f"null {key_} {what}")
    if src is not None:
        close(float((lv == 0).sum()), float(r["keys_at_zero"]), f"null {key_} keys_at_zero")
    n_null += 1
    if "w3_class" in r:
        pr_sd = r["pred_sd"]; flags = r.get("flags") or []; eligible = (r.get("theory_share") is not None and r["theory_share"] >= w3["theory_share_min"] and not flags and pr_sd > 0)
        name = f"W3|{cell}|h{h}|{rule}|{src}|{v}"; idx = boot_idx(len(lv), name); sd_b = lv[idx].std(axis=1, ddof=1)
        ratio = float(lv.std(ddof=1) / pr_sd) if pr_sd > 0 else float("nan"); lo, hi = (float(np.quantile(sd_b, 0.025) / pr_sd), float(np.quantile(sd_b, 0.975) / pr_sd)) if pr_sd > 0 else (float("nan"),) * 2
        cls = classify_band(lo, hi, tuple(w3["band"])) if eligible else "ineligible"
        W3_OWN[key_] = {"ratio": ratio, "lo": lo, "hi": hi, "class": cls, "eligible": bool(eligible)}
        for what, own, fil in (("w3_ratio", ratio, r["w3_ratio"]), ("w3_ci_lo", lo, r["w3_ci_lo"]), ("w3_ci_hi", hi, r["w3_ci_hi"]), ("w3_class", cls, r["w3_class"]), ("w3_eligible", bool(eligible), r["w3_eligible"])):
            close(own, fil, f"W3 {key_} {what}")
n_el = sum(1 for x in W3_OWN.values() if x["eligible"]); n_res = sum(1 for x in W3_OWN.values() if x["class"] in ("consistent", "inconsistent")); n_con = sum(1 for x in W3_OWN.values() if x["class"] == "consistent")
for what, own, fil in (("n_candidate", float(len(W3_OWN)), float(res["W3"]["n_candidate"])), ("n_eligible", float(n_el), float(res["W3"]["n_eligible"])), ("n_resolved", float(n_res), float(res["W3"]["n_resolved"])), ("n_consistent", float(n_con), float(res["W3"]["n_consistent"])),
                       ("pass", bool(n_res >= w3["min_resolved"] and n_con >= w3["min_consistent_share"] * n_res) if W3_OWN else None, res["W3"]["pass"])):
    close(own, fil, f"W3 {what}")
CHECKS["verified"]["null_rows"] = n_null; CHECKS["verified"]["W3_rows"] = len(W3_OWN); SECONDS_RECOMPUTE = round(time.time() - t0, 1)   # printed, never written (checks.json stays byte-reproducible)
if CHECKS["mismatches"]:
    (OUTDIR / "checks.json").write_text(json.dumps(CHECKS, indent=1, default=float)); raise SystemExit(f"{len(CHECKS['mismatches'])} mismatches between the builder's re-computation and results.json (see checks.json): {CHECKS['mismatches'][:5]}")
print(f"re-computation equal to results.json: {n_desc} descriptive rows, {len(W1_OWN)} W1 rows, {len(W2_OWN)} W2 rows, {n_null} null rows, {len(W3_OWN)} W3 rows ({SECONDS_RECOMPUTE} s)", flush=True)

# ------------------------------------------------------------------ registered values and tables
TABLES = {}; FIGS = {}
reg("conductor", "Claude (Fable 5.1, in Claude Code)"); reg("reviewer", "Codex"); reg("mode_label", "FIXTURE (a synthetic inventory; every number planted; not the study)" if FIXTURE else "STUDY")
reg("lock_sha12", LOCK_SHA[:12]); reg("results_sha12", RES_SHA[:12]); reg("inventory_sha12", res["inventory"]["inventory_sha256"][:12]); reg("n_units", res["inventory"]["n_files"] // 2); reg("n_files", res["inventory"]["n_files"])
reg("K4", K4); reg("n_tx", N_TX); reg("n_cells", len(CELLS)); reg("n_arms", len(ARMS)); reg("N0", res["quality"][f"{CELLS[0]}|none"]["N"]); reg("analyzer_seconds", res["seconds"]); reg("analyzer_peak_rss_gb", res["peak_rss_gb"])
reg("n_desc_rows", len(res["descriptive_rows"])); reg("n_null_rows", len(res["null_rows"])); reg("n_contract_failures", n_fail); reg("contract_failure_share_pct", pp(n_fail / n_gen_units, 2)); reg("n_gen_units", n_gen_units)
reg("tolerance_rule", "max(5 pp, 2 × the key-and-prompt cluster-bootstrap SE of the predicted key-median)")
# the run (study mode: from the manifest; fixture mode: a note)
if REAL:
    rr = manifest["run"]; reg("run_start", rr["start_utc"]); reg("run_end", rr["end_utc"]); reg("run_hours", fnum(rr["duration_hours"], 3)); reg("run_projected_hours", fnum(rr["projected_hours"], 2)); reg("run_restarts", rr["n_start_lines"] - 1)
    reg("run_reused", len(rr["reused_units_on_resume"])); reg("run_peak_rss_gb", fnum(rr["peak_rss_gb_max"], 2)); reg("head_at_launch", (manifest["git"].get("launch") or {}).get("head_at_launch", "")[:7])
    swap_used = lambda s: (re.search(r"used = ([\d.]+)M", s).group(1) if re.search(r"used = ([\d.]+)M", s) else "—")
    TABLES["timing"] = md_table(["phase", "start (UTC)", "end (UTC)", "hours", "swap used at the phase start (MB)"], [[p["phase"].split(" | ")[0], p["start_utc"], p.get("end_utc", "—"), fnum(p.get("hours"), 3), swap_used(p["phase"])] for p in rr["phases"]]) + "\n\n" + md_table(["arm", "units", "mean wall s per unit", "projected s per unit"],
                                [[a, d["n_units"], fnum(d["mean_wall_seconds"], 1), fnum(d.get("projected_wall_seconds_per_unit"), 1)] for a, d in rr["by_arm"].items()])
else:
    for k in ("run_start", "run_end", "run_hours", "run_projected_hours", "run_restarts", "run_reused", "run_peak_rss_gb", "head_at_launch"):
        reg(k, "FIXTURE")
    TABLES["timing"] = md_table(["phase", "start (UTC)", "end (UTC)", "hours"], [["FIXTURE: no run", "—", "—", "—"]])
# Table 1: the rules
verd = lambda p: "PASS" if p else ("FAIL" if p is not None else "not read")
reg("w1_verdict", verd(res["W1"]["pass"])); reg("w2_verdict", verd(res["W2"]["pass"])); reg("w3_verdict", verd(res["W3"]["pass"]))
reg("w1_n_consistent", res["W1"]["n_consistent"]); reg("w1_n_inconsistent", res["W1"]["n_inconsistent"]); reg("w1_n_unresolved", res["W1"]["n_unresolved"]); reg("w1_n_rows", res["W1"]["n_rows"])
reg("w2_n_agree", res["W2"]["n_agree"]); reg("w2_n_disagree", res["W2"]["n_disagree"]); reg("w2_n_unresolved", res["W2"]["n_unresolved"]); reg("w2_n_rows", res["W2"]["n_rows"])
for k in ("n_candidate", "n_eligible", "n_resolved", "n_consistent", "n_inconsistent", "n_unresolved"):
    reg(f"w3_{k}", res["W3"][k])
reg("w3_consistent_share_of_resolved", pp(res["W3"]["n_consistent"] / res["W3"]["n_resolved"] if res["W3"]["n_resolved"] else float("nan")))
TABLES["rules"] = md_table(["rule", "pre-registered pass condition (protocol §6, §9)", "observed", "verdict"], [
    ["W1 (the cost is the threshold shift alone)", "at least 2 of 3 cells consistent and none inconsistent (the key-median cost's 95% key-bootstrap interval inside the predicted median ± the cell's tolerance)", f"{res['W1']['n_consistent']} consistent, {res['W1']['n_inconsistent']} inconsistent, {res['W1']['n_unresolved']} unresolved of {res['W1']['n_rows']}", VALUES["w1_verdict"]],
    ["W2 (the dispersion of power changes in the predicted direction)", "at least 5 of 6 rows agree and none disagrees (raw: the ratio's interval below 1; distinct: inside [2/3, 3/2]; the prompt-conditioned target)", f"{res['W2']['n_agree']} agree, {res['W2']['n_disagree']} disagree, {res['W2']['n_unresolved']} unresolved of {res['W2']['n_rows']}", VALUES["w2_verdict"]],
    ["W3 (Study 3's predictor out of sample on the model's null law)", "at least 30 resolved rows and at least 80% of the resolved consistent (the ratio's interval inside [2/3, 3/2])", f"{res['W3']['n_candidate']} candidate, {res['W3']['n_eligible']} eligible, {res['W3']['n_resolved']} resolved, {res['W3']['n_consistent']} consistent, {res['W3']['n_inconsistent']} inconsistent, {res['W3']['n_unresolved']} unresolved", VALUES["w3_verdict"]]])
# Table 2: W1 rows
rows = []
for r in res["W1"]["rows"]:
    c = r["cell"]; wt = inputs["W1_tolerance"][c]
    rows.append([CELL_LABEL[c], r["K"], pp(r["realised_median"]), f"[{pp(r['ci_lo'])}, {pp(r['ci_hi'])}]", pp(r["realised_mean"]), pp(r["predicted_median"]), pp(r["predicted_mean"]), fnum(wt["cluster_bootstrap"]["se_pp"], 2), f"[{pp(wt['cluster_bootstrap']['q025_pp'] / 100)}, {pp(wt['cluster_bootstrap']['q975_pp'] / 100)}]", pp(r["tolerance"]), r["class"], pp(r["share_keys_within_tol"]), fnum(r["corr_real_pred"], 2), pp(r["nominal_power_median"]), r["pilot_law_n"]])
TABLES["w1_rows"] = md_table(["prompt cell", "K", "realised median cost (pp)", "95% key-bootstrap interval", "realised key-mean cost (pp)", "predicted median (pp)", "predicted key-mean (pp)", "predicted-median SE (pp; pre-lock key-and-prompt cluster bootstrap)", "the prediction's own 95% cluster-bootstrap interval (pre-lock)", "tolerance c (pp)", "class", "share of keys within c of their prediction (%)", "corr(realised, predicted) across keys", "median nominal power (pp)", "pilot texts"], rows)
# Table 3: W2 rows
rows = []
for r in res["W2"]["rows"]:
    rows.append([CELL_LABEL[r["cell"]], r["rule"], r["K"], pp(r["sd_between_nominal"], 2), pp(r["sd_between_method"], 2), pp(r["sd_observed_nominal"], 2), pp(r["sd_observed_method"], 2), pp(r["binomial_proxy"]["sd_between_nominal"], 2), pp(r["binomial_proxy"]["sd_between_method"], 2),
                 fnum(r["R_pow"], 3), f"[{fnum(r['ci_lo'], 3)}, {fnum(r['ci_hi'], 3)}]", r["finite_resamples"], r["predicted_side"], r["class"], pp(r["power_mean_nominal"]), pp(r["power_mean_method"])])
TABLES["w2_rows"] = md_table(["prompt cell", "rule", "K", "SD_b nominal (two-way, pp)", "SD_b conformal@5000 (pp)", "observed SD nominal (pp)", "observed SD conformal (pp)", "proxy SD nominal (pp)", "proxy SD conformal (pp)", "R_pow", "95% key-bootstrap interval", "finite resamples", "predicted side", "class", "key-mean power nominal (pp)", "key-mean power conformal (pp)"], rows)
# Table 3b: W2 components
rows = [[CELL_LABEL[r["cell"]], r["rule"], f"{r['var_between_raw_nominal']:.2e}", f"{r['var_between_raw_method']:.2e}", f"{r['var_obs_nominal']:.2e}", f"{r['var_obs_method']:.2e}", f"{r['ms_resid_nominal']:.3f}", f"{r['ms_resid_method']:.3f}", f"{r['var_prompt_raw_nominal']:.2e}", f"{r['var_prompt_raw_method']:.2e}", f"{r['binomial_proxy']['mean_binomial_var_nominal']:.2e}", f"{r['binomial_proxy']['mean_binomial_var_method']:.2e}", f"{r['binomial_proxy']['var_between_raw_nominal']:.2e}", f"{r['binomial_proxy']['var_between_raw_method']:.2e}"] for r in res["W2"]["rows"]]
TABLES["w2_components"] = md_table(["prompt cell", "rule", "raw two-way component nominal", "raw two-way component conformal", "observed variance nominal", "observed variance conformal", "MS_E nominal", "MS_E conformal", "prompt component nominal", "prompt component conformal", "mean binomial variance nominal", "mean binomial variance conformal", "proxy raw corrected variance nominal (observed − mean binomial)", "proxy raw corrected variance conformal"], rows)
# Table 4: W3 by block; Table 5: the non-consistent rows
def w3_counts(sel):
    sel = list(sel); return [len(sel), sum(1 for r in sel if r["w3_eligible"]), sum(1 for r in sel if r["w3_class"] in ("consistent", "inconsistent")), sum(1 for r in sel if r["w3_class"] == "consistent"), sum(1 for r in sel if r["w3_class"] == "inconsistent"), sum(1 for r in sel if r["w3_class"] == "unresolved")]
w3rows = res["W3"]["rows"]; blocks = []
for lab, fn in (("by cell", lambda r: CELL_LABEL[r["cell"]]), ("by width", lambda r: f"h = {r['h']}"), ("by rule", lambda r: r["rule"]), ("by source class", lambda r: r["class"]), ("by N_cal", lambda r: variant_parts(r["variant"])[1])):
    for val in sorted({fn(r) for r in w3rows}, key=str):
        blocks.append([lab, val] + w3_counts(r for r in w3rows if fn(r) == val))
blocks.append(["all", "", *w3_counts(w3rows)])
TABLES["w3_by_block"] = md_table(["block", "value", "candidate", "eligible", "resolved", "consistent", "inconsistent", "unresolved"], blocks)
bad = [r for r in w3rows if r["w3_class"] in ("inconsistent", "unresolved")]
TABLES["w3_failures"] = md_table(["prompt cell", "h", "rule", "source", "N_cal", "observed SD (pp)", "predicted SD (pp)", "ratio", "95% interval", "class", "theory share", "v", "v_raw", "ρ̄_E", "σ_E²", "ρ̄_C", "σ_C²", "ρ_CE", "shared tuples", "j", "mean level (pp)", "predicted mean (pp)", "predicted finite-evaluation share above α (%)", "predicted population share above α (%)"],
                                  [[CELL_LABEL[r["cell"]], r["h"], r["rule"], CELL_LABEL[r["source"]], variant_parts(r["variant"])[1], pp(r["level_sd"], 3), pp(r["pred_sd"], 3), fnum(r["w3_ratio"], 3), f"[{fnum(r['w3_ci_lo'], 3)}, {fnum(r['w3_ci_hi'], 3)}]", r["w3_class"], fnum(r.get("theory_share"), 3), (f"{r['v']:.2e}" if r.get("v") is not None else "—"), (f"{r['v_raw']:.2e}" if r.get("v_raw") is not None else "—"), fnum(r.get("rho_E"), 4), (f"{r['sigma2_E']:.3e}" if r.get("sigma2_E") is not None else "—"), fnum(r.get("rho_C"), 4), (f"{r['sigma2_C']:.3e}" if r.get("sigma2_C") is not None else "—"), fnum(r.get("rho_CE"), 4), r.get("n_shared_tuples", "—"), r.get("j", "—"), pp(r["level_mean"], 3), pp(r["pred_mean"], 3), pp(r.get("pred_share_above_alpha_finite")), pp(r.get("pred_share_above_alpha_pop"))] for r in bad] or [["none"] + ["—"] * 23])
reg("w3_fail_n", len(bad))
# Table 6: the power table at the primary settings
METHODS_MAIN = ["nominal", "multiplier20", "empirical", "pooled", f"conformal@{NCALS[-1]}", f"tolerance@{NCALS[-1]}"] + [f"conformal@{n}" for n in NCALS[:-1]]
def drow(cell, arm, rule, L, src, v, a):
    return desc_file.get((cell, arm, rule, L, (None if v in VFIX else src), v, a))
rows = []
for cell in CELLS:
    for arm in ARMS:
        for rule in RULES:
            for v in METHODS_MAIN:
                r = drow(cell, arm, rule, L_PRIM, cell, v, A_PRIM)
                if r:
                    rows.append([CELL_LABEL[cell], ARM_LABEL[arm], rule, v, r["K"], pp(r["power_mean"]), pp(r["power_q05"]), pp(r["power_q50"]), pp(r["power_q95"]), pp(r["power_sd_observed"], 2), pp(r["power_sd_between_twoway"], 2), pp(r["power_sd_between_binomial_proxy"], 2), pp(r["cost_mean"]), pp(r["cost_q50"]), pp(r["cost_q05"]), pp(r["cost_q95"]), r["keys_abstaining"]])
TABLES["power_primary"] = md_table(["prompt cell", "arm", "rule", "method", "K", "key-mean power (pp)", "5%", "median", "95%", "observed SD (pp)", "two-way SD_b (pp)", "proxy SD (pp)", "mean cost (pp)", "median cost", "5%", "95%", "abstaining keys"], rows)
# the per-key operating points (builder): Study 3's stored null level and the model-null level per key against the power, at the primary setting (raw rule)
OP = {}
for cell in CELLS:
    G = GEN[(cell, PRIMARY)]; ok = G["ok"]; keys_ok = [k for k, o in zip(G["keys"], ok) if o]; h = arm_spec(grid, PRIMARY)["h"]; ev = Rrec.eval(TOK, cell, h); isrc = SOURCES.index(cell); ir = RULES.index("raw"); il = LENGTHS.index(L_PRIM); ia = ALPHAS.index(A_PRIM)
    for v in METHODS_MAIN[:6]:
        m, nc = variant_parts(v); iv = VARIANTS.index(v); pi = G["counts"][ok, ir, il, isrc, iv, ia] / N_TX
        l3 = ev.null_level("kgw", "raw", m, A_PRIM, nc, cal_source=cell)[[k - 23000 for k in keys_ok]]
        if v in VFIX:
            l0 = ARR[f"null|{cell}|h{h}|kgw|raw|L{L_PRIM}|fixed"][VFIX.index(v), ia].astype(np.float64)[[k - 23000 for k in keys_ok]] / VALUES["N0"]
        else:
            l0 = ARR[f"null|{cell}|h{h}|kgw|raw|L{L_PRIM}|same"][isrc, VS3.index(v), ia].astype(np.float64)[[k - 23000 for k in keys_ok]] / VALUES["N0"]
        OP[(cell, v)] = {"pi": pi, "l3": l3, "l0": l0, "green": G["green"][ok]}
rows = []
for (cell, v), d in OP.items():
    above = d["l3"] > A_PRIM; above0 = d["l0"] > A_PRIM
    rows.append([CELL_LABEL[cell], v, len(d["pi"]), pp(d["l3"].mean(), 2), pp(above.mean()), pp(d["pi"][above].mean()) if above.any() else "—", pp(d["pi"][~above].mean()) if (~above).any() else "—", fnum(np.corrcoef(d["l3"], d["pi"])[0, 1], 2) if d["l3"].std() > 0 and d["pi"].std() > 0 else "—",
                 pp(d["l0"].mean(), 2), pp(above0.mean()), fnum(np.corrcoef(d["l0"], d["pi"])[0, 1], 2) if d["l0"].std() > 0 and d["pi"].std() > 0 else "—"])
TABLES["operating_points"] = md_table(["prompt cell", "method", "K", "key-mean stored null level ℓ_k (Study 3, pp)", "share of keys with ℓ_k > α", "their mean power (pp)", "the others' mean power (pp)", "corr(ℓ_k, π_k)", "key-mean model-null level ℓ̃_k (pp)", "share with ℓ̃_k > α", "corr(ℓ̃_k, π_k)"], rows)
# the mechanism diagnostic (builder): correlations across keys between the stored nominal null level, the nominal power and the hook's green share
MECH = {}
rows = []
for cell in CELLS:
    for arm in ARMS:
        G = GEN[(cell, arm)]; ok = G["ok"]; keys_ok = [k for k, o in zip(G["keys"], ok) if o]; h = arm_spec(grid, arm)["h"]; ev = Rrec.eval(TOK, cell, h); isrc = SOURCES.index(cell); iv = VARIANTS.index("nominal"); ia = ALPHAS.index(A_PRIM)
        for rule in RULES:
            ir = RULES.index(rule); l3 = ev.null_level("kgw", rule, "nominal", A_PRIM, cal_source=cell)[[k - 23000 for k in keys_ok]]; gsh = G["green"][ok]
            for L in LENGTHS:
                pi = G["counts"][ok, ir, LENGTHS.index(L), isrc, iv, ia] / N_TX
                c1 = float(np.corrcoef(l3, pi)[0, 1]) if l3.std() > 0 and pi.std() > 0 else float("nan"); c2 = float(np.corrcoef(l3, gsh)[0, 1]) if l3.std() > 0 and gsh.std() > 0 else float("nan")
                MECH[(cell, arm, rule, L)] = (c1, c2, float(gsh.std(ddof=1))); rows.append([CELL_LABEL[cell], ARM_LABEL[arm], rule, L, len(pi), fnum(c1, 2), fnum(c2, 2), fnum(c1 ** 2, 2), pp(gsh.mean(), 2), pp(gsh.std(ddof=1), 2)])
TABLES["mechanism"] = md_table(["prompt cell", "arm", "rule", "L", "K", "corr(stored null level, nominal power)", "corr(stored null level, green share)", "R² of nominal power on the stored null level", "key-mean green share (pp; the hook's share over all 256 generated tokens, the same at every L)", "SD of the green share across keys (pp)"], rows)
# the length curves (primary arm, raw and distinct; the shorter lengths are not calibrated operating points)
rows = []
for cell in CELLS:
    for rule in RULES:
        for v in METHODS_MAIN[:6]:
            rr_ = [drow(cell, PRIMARY, rule, L, cell, v, A_PRIM) for L in LENGTHS]
            rows.append([CELL_LABEL[cell], rule, v] + [pp(r["power_mean"]) if r else "—" for r in rr_] + [pp(r["power_sd_between_twoway"], 2) if r else "—" for r in rr_])
TABLES["length"] = md_table(["prompt cell", "rule", "method"] + [f"key-mean power at L = {L} (pp)" for L in LENGTHS] + [f"two-way SD_b at L = {L} (pp)" for L in LENGTHS], rows)
# the design remedy (builder): paired contrasts per key at the primary settings
def paired(cell, arm_a, arm_b, rule_a, rule_b, v):
    Ga, Gb = GEN[(cell, arm_a)], GEN[(cell, arm_b)]; ok = Ga["ok"] & Gb["ok"]; isrc = SOURCES.index(cell); il = LENGTHS.index(L_PRIM); ia = ALPHAS.index(A_PRIM); iv = VARIANTS.index(v)
    d = Ga["counts"][ok, RULES.index(rule_a), il, isrc, iv, ia] / N_TX - Gb["counts"][ok, RULES.index(rule_b), il, isrc, iv, ia] / N_TX
    idx = boot_idx(len(d), f"remedy|{cell}|{arm_a}|{arm_b}|{rule_a}|{rule_b}|{v}", BUILDER_SALT); lo, hi = quant(d[idx].mean(axis=1)); return float(d.mean()), lo, hi, int(ok.sum())
rows = []
for cell in CELLS:
    for v in METHODS_MAIN[:6]:
        for lab, (aa, ab, ra, rb) in (("h = 2 minus h = 1 (δ = 0.5), raw", ("kgw_h2_d0.5", "kgw_h1_d0.5", "raw", "raw")), ("h = 2 minus h = 1 (δ = 0.5), distinct", ("kgw_h2_d0.5", "kgw_h1_d0.5", "distinct", "distinct")), ("distinct minus raw (h = 1, δ = 0.5)", ("kgw_h1_d0.5", "kgw_h1_d0.5", "distinct", "raw")),
                             ("δ = 2.0 minus δ = 0.5 (h = 1), raw", ("kgw_h1_d2.0", "kgw_h1_d0.5", "raw", "raw"))):
            m, lo, hi, kk = paired(cell, aa, ab, ra, rb, v); rows.append([CELL_LABEL[cell], v, lab, kk, pp(m), f"[{pp(lo)}, {pp(hi)}]"])
TABLES["remedy"] = md_table(["prompt cell", "method", "contrast (key-mean power difference, paired on the same keys and prompts)", "K", "mean difference (pp)", "95% key-bootstrap interval (the builder's salt)"], rows)
# the transfer sources: the conformal@5000 power and the model-null level under every source (primary arm, L = 256, alpha = 0.01)
rows = []
for cell in CELLS:
    for rule in RULES:
        for src in SOURCES:
            r = drow(cell, PRIMARY, rule, L_PRIM, src, f"conformal@{NCALS[-1]}", A_PRIM); nr = null_file.get((cell, arm_spec(grid, PRIMARY)["h"], "kgw", rule, L_PRIM, src, f"conformal@{NCALS[-1]}", A_PRIM))
            rows.append([CELL_LABEL[cell], rule, CELL_LABEL[src], "diagonal" if src == cell else "transfer", pp(r["power_mean"]) if r else "—", pp(r["cost_mean"]) if r else "—", pp(r["power_sd_between_twoway"], 2) if r else "—", r["keys_abstaining"] if r else "—", pp(nr["level_mean"], 3) if nr else "—", pp(nr["level_sd"], 3) if nr else "—", pp(nr["share_above_alpha"]) if nr else "—"])
TABLES["transfer"] = md_table(["prompt cell", "rule", "calibration source", "class", "key-mean power conformal@5000 (pp)", "mean cost (pp)", "two-way SD_b (pp)", "abstaining keys", "model-null level: key-mean (pp)", "SD (pp)", "share of keys above α"], rows)
# the model-null block summary (L = 256, alpha = 0.01; the nominal and the diagonal conformal@5000 rows)
rows = []
for cell in CELLS:
    for h in grid["null_arm"]["widths"]:
        for fam in grid["null_arm"]["families"]:
            for rule in RULES:
                rn = null_file.get((cell, h, fam, rule, L_PRIM, None, "nominal", A_PRIM)); rc_ = null_file.get((cell, h, fam, rule, L_PRIM, cell, f"conformal@{NCALS[-1]}", A_PRIM))
                rows.append([CELL_LABEL[cell], h, fam, rule, pp(rn["level_mean"], 3), pp(rn["level_sd"], 3), pp(rn["share_above_alpha"]), pp(rn["q99"], 2), pp(rn["pred_sd"], 3) if rn.get("pred_sd") is not None else "—",
                             pp(rc_["level_mean"], 3), pp(rc_["level_sd"], 3), pp(rc_["share_above_alpha"]), pp(rc_["pred_sd"], 3) if rc_.get("pred_sd") is not None else "—", fnum(rc_.get("theory_share"), 2), rc_.get("w3_class", "—")])
TABLES["model_null"] = md_table(["prompt cell", "h", "family", "rule", "nominal: key-mean level (pp)", "SD (pp)", "share above α", "99% key quantile (pp)", "predicted SD (pp)", "conformal@5000 (diagonal): key-mean (pp)", "SD (pp)", "share above α", "predicted SD (pp)", "theory share", "W3 class"], rows)
# the quality table
rows = []
for cell in CELLS:
    for arm in ARMS + ["none"]:
        q = res["quality"].get(f"{cell}|{arm}")
        if not q or "ppl" not in q:
            continue
        rows.append([CELL_LABEL[cell], ARM_LABEL.get(arm, "unwatermarked"), q.get("n_units_in_tables", q.get("n_units")), fnum(q["ppl"]["mean"], 2), fnum(q["mean_logp_first_192"]["mean"], 3), fnum(q["rep4"]["mean"], 3), pp(q["loop"]["mean"], 2), pp(q["green"]["mean"], 1) if "green" in q else "—", fnum(q["eos"]["mean"], 4)])
hr = inputs["human_reference"]
for cell in CELLS:
    rows.append([CELL_LABEL[cell], "human continuation (reference, 192 tokens)", hr[cell]["n"], fnum(hr[cell]["ppl"], 2), fnum(hr[cell]["mean_logp"], 3), fnum(hr[cell]["rep4_mean"], 3), "—", "—", "—"])
TABLES["quality"] = md_table(["prompt cell", "arm", "units (generation arms: key-batches of 50 texts; unwatermarked: chunks of 500 texts; human: single continuations)", "perplexity of the model's own tokens (admissible law; generation and unwatermarked rows: the mean over units of exp(−mean log-probability) over the 256 generated tokens; the human reference: exp(−pooled mean log-probability) over its 1,000 × 192 continuation tokens)", "mean log-probability, first 192 tokens (the matched window)", "rep-4", "loop share (rep-4 > 0.5, %)", "green share (pp)", "EOS mass"], rows)
# the per-prompt pairing (builder): the watermark's effect per prompt averaged over the power keys
PAIR = {}
for cell in CELLS:
    for arm in ARMS:
        h = arm_spec(grid, arm)["h"]
        for rule in RULES:
            k0 = f"null_pvalues_first_prompts|{cell}|h{h}|kgw|{rule}|L{L_PRIM}"
            if k0 not in ARR:
                continue
            G = GEN[(cell, arm)]; ok = G["ok"]; pw = G["pv"][ok, :, RULES.index(rule), LENGTHS.index(L_PRIM)]; p0 = ARR[k0][:, ok].T   # keys x prompts
            zw = norm.isf(np.clip(pw, 1e-300, 1 - 1e-16)); z0 = norm.isf(np.clip(p0, 1e-300, 1 - 1e-16)); eff = (zw - z0).mean(axis=0); PAIR[(cell, arm, rule)] = eff
rows = []
for (cell, arm, rule), eff in PAIR.items():
    rows.append([CELL_LABEL[cell], ARM_LABEL[arm], rule, len(eff), fnum(eff.mean(), 2), fnum(np.quantile(eff, 0.05), 2), fnum(np.quantile(eff, 0.5), 2), fnum(np.quantile(eff, 0.95), 2), fnum(eff.std(ddof=1), 2)])
TABLES["pairing"] = md_table(["prompt cell", "arm", "rule", "prompts", "mean effect (z)", "5%", "median", "95%", "SD across prompts (z)"], rows)
# the null-block abstentions (builder): every same-tokenizer threshold setting of the model-null block read from the committed record, with its kind and order index;
# a setting is one (source, width, family, rule, method, N_cal, alpha) threshold vector, entering one model-null row per cell and length
NULL_ABST = []; K_NULL = len(cal_unit(SOURCES[0], grid["null_arm"]["widths"][0]).keys)
for src in SOURCES:
    for h in grid["null_arm"]["widths"]:
        cu = cal_unit(src, h)
        for fam in grid["null_arm"]["families"]:
            for rule in RULES:
                for v in VS3:
                    m, nc = variant_parts(v)
                    for a in ALPHAS:
                        t_ = cu.threshold(fam, rule, m, a, nc); n0 = int((t_ <= 0).sum())
                        if n0:
                            j = cu.order_index(fam, rule, m, a, nc) if m in ("conformal", "tolerance") else None
                            NULL_ABST.append({"source": src, "h": h, "family": fam, "rule": rule, "variant": v, "alpha": a, "n_keys": n0, "j": j, "kind": "structural" if j == 0 else "positive_index", "keys": [int(k) for k, z in zip(cu.keys, t_ <= 0) if z] if n0 <= 5 else None})
n_entered = len(CELLS) * len(LENGTHS); n_checked = 0
for r_ in NULL_ABST:   # a structural setting abstains for every key: every entered model-null row must have every count at 0
    if r_["kind"] == "structural":
        for cell in CELLS:
            for L in LENGTHS:
                nr_ = null_file[(cell, r_["h"], r_["family"], r_["rule"], L, r_["source"], r_["variant"], r_["alpha"])]
                if nr_["keys_at_zero"] != nr_["K"] or nr_["level_mean"] != 0 or nr_["level_sd"] != 0:
                    raise SystemExit(f"null abstention {r_}: the entered row {cell} L{L} is not all-zero")
                n_checked += 1
CHECKS["verified"]["null_abstention_rows_all_zero"] = n_checked
grp = {}
for r_ in NULL_ABST:
    k_ = (r_["family"], r_["rule"], r_["variant"], r_["alpha"], r_["kind"], r_["j"]); g = grp.setdefault(k_, {"settings": 0, "sources": [], "widths": [], "keys_min": 10 ** 9, "keys_max": 0, "ids": []})
    g["settings"] += 1; g["sources"].append(r_["source"]); g["widths"].append(r_["h"]); g["keys_min"] = min(g["keys_min"], r_["n_keys"]); g["keys_max"] = max(g["keys_max"], r_["n_keys"])
    if r_["keys"]:
        g["ids"].append(f"{CELL_LABEL[r_['source']]}, h = {r_['h']}: key {', '.join(str(k) for k in r_['keys'])}")
rows = [[fam, rule, v, a, kind, ("—" if j is None else j), g["settings"], f"{len(set(g['sources']))} source{'s' if len(set(g['sources'])) != 1 else ''} × {len(set(g['widths']))} width{'s' if len(set(g['widths'])) != 1 else ''}", (f"{g['keys_min']}" if g["keys_min"] == g["keys_max"] else f"{g['keys_min']}–{g['keys_max']}") + f" of {K_NULL}", g["settings"] * n_entered, "; ".join(g["ids"]) or "—"]
        for (fam, rule, v, a, kind, j), g in sorted(grp.items(), key=str)]
TABLES["null_abstentions"] = md_table(["family", "rule", "method", "α", "kind", "order index j", "settings", "span (sources × widths)", "keys abstaining per setting", f"model-null rows entered ({len(CELLS)} cells × {len(LENGTHS)} lengths per setting)", "key identity (positive-index settings)"], rows)
n_struct = sum(1 for r_ in NULL_ABST if r_["kind"] == "structural"); n_pos = sum(1 for r_ in NULL_ABST if r_["kind"] == "positive_index")
pos_desc = "; ".join(f"{CELL_LABEL[r_['source']]}, h = {r_['h']}, {r_['family']}, {r_['rule']} rule, {r_['variant']}, α = {r_['alpha']}, j = {r_['j']}, key {', '.join(str(k) for k in (r_['keys'] or []))}, {r_['n_keys']} of {K_NULL} keys" for r_ in NULL_ABST if r_["kind"] == "positive_index") or "none"
reg("n_null_abst_settings", len(NULL_ABST)); abst_alphas = ", ".join(str(a) for a in sorted(set(r_["alpha"] for r_ in NULL_ABST))); abst_methods = ", ".join(sorted(set(r_["variant"] for r_ in NULL_ABST if r_["kind"] == "structural")))
reg("null_abst_summary", f"{n_struct} structural settings (j = 0; every one of the {K_NULL} keys; α = {abst_alphas}; {abst_methods}) entering {n_struct * n_entered} model-null rows, every count 0, and {n_pos} positive-index setting{'s' if n_pos != 1 else ''} ({pos_desc}) entering {n_pos * n_entered} rows")
# the integrity record
abst_rows = [r for r in res["descriptive_rows"] if r["keys_abstaining"]]; abst = {}
for r in abst_rows:
    k_ = (r["source"], variant_parts(r["variant"])[0], r["abstention_kind"]); d_ = abst.setdefault(k_, {"settings": 0, "max_keys": 0, "alphas": set()}); d_["settings"] += 1; d_["max_keys"] = max(d_["max_keys"], r["keys_abstaining"]); d_["alphas"].add(r["alpha"])
TABLES["integrity"] = md_table(["item", "value"], [["inventory digest", res["inventory"]["inventory_sha256"]], ["lock digest", LOCK_SHA], ["results digest", RES_SHA], ["arrays digest", res["arrays_sha256"]], ["generation units", n_gen_units], ["contract failures", f"{n_fail} ({VALUES['contract_failure_share_pct']}%): " + ("; ".join(f"{f['unit']} ({f['mismatched_positions']} of {f['scored_positions']} scored positions)" for f in res["integrity"]["contract_failures"]) or "none")],
                                                    ["run void", str(res["integrity"]["run_void"])], ["settings with abstaining keys, by source, method and kind (settings; most keys abstaining; the α values)", "; ".join(f"{CELL_LABEL[s]}/{m}/{kd}: {d_['settings']} settings, up to {d_['max_keys']} keys, α = {', '.join(str(a_) for a_ in sorted(d_['alphas']))}" for (s, m, kd), d_ in sorted(abst.items(), key=str)) or "none"],
                                                    ["null-block threshold settings with abstaining keys (the builder's, read from the committed thresholds; a setting is one (source, width, family, rule, method, N_cal, α) threshold vector, entering one model-null row per cell and length; Table 18)", VALUES["null_abst_summary"] + "; never repaired"],
                                                    ["calibration-prefix moments against Study 3's pinned inputs", f"{res['null_inputs_consistency_summary']['n']} prefixes; max |Δρ̄| {res['null_inputs_consistency_summary']['max_abs_diff_rho']:.1e}, max |Δσ²| {res['null_inputs_consistency_summary']['max_abs_diff_sigma2']:.1e} (allowance 10⁻⁸ × max(1, |ref|))"]])
reg("n_abstaining_settings", len(abst_rows))
# the protocol's section 7 checklist: every promised output, its estimand and denominator, and where it is reported (the counts generated)
n_w3_fail = len(bad); n_null_src = sum(1 for r_ in res["null_rows"] if r_["source"]); n_null_fixed = sum(1 for r_ in res["null_rows"] if not r_["source"]); n_gumbel = sum(1 for r_ in res["null_rows"] if r_["family"] == "gumbel")
TABLES["checklist"] = md_table(["promised output (protocol §7)", "estimand and denominator", "where it is reported", "entries"], [
    ["the power table: per cell × arm × rule × L × source × method (and N_cal) × α: the key-mean, the observed SD, the two-way between-key component with its raw variance and residual mean square, the binomial proxy, the 5/50/95% quantiles of π_k, the cost's mean, median and 5/95% quantiles, the abstaining keys with their kind", f"over the K₄ = {K4} keys (contract failures excluded; K stated), each π_k over n = {N_TX} texts", "Table 8 (L = 256, α = 0.01, the diagonal source, every arm, rule and method); every row in `descriptive_rows_full.csv.gz` (fields `power_mean`, `power_sd_observed`, `power_sd_between_twoway`, `power_var_between_raw_twoway`, `ms_resid_twoway`, `power_sd_between_binomial_proxy`, `power_var_between_raw_binomial_proxy`, `mean_binomial_var`, `power_q05/q50/q95`, `cost_mean/q50/q05/q95`, `keys_abstaining`, `abstention_kind`)", f"{len(res['descriptive_rows'])} rows"],
    ["the per-key operating points: (ℓ_k, π_k) with Study 3's stored null level and (ℓ̃_k, π_k) with the model-null level, per method; the share of keys with ℓ_k > α and their power", f"per key over the {K4} power keys; the stored level over N_E = 10,000 corpus texts (Study 3); the model-null level over N₀ = {VALUES['N0']} generated texts", "Table 9 and Figure 4 (the builder's block; the primary arm, raw rule, L = 256, α = 0.01)", f"{len(OP)} cell × method rows"],
    ["the mechanism diagnostic: the Pearson correlations across keys of the stored null level with the nominal power and with the green share under the hook; the squared correlation", f"over the {K4} keys, per cell, arm, rule and L", "Table 10 (the builder's block; the green share over all 256 generated tokens)", f"{len(MECH)} rows"],
    ["the length curves: π_k(m) at L ∈ {64, 128, 256} for every method (the shorter lengths are not calibrated operating points)", "as the power table", "Table 11 and Figure 5 (the builder's summary of the descriptive rows at the primary arm; every method, source and α in `descriptive_rows_full.csv.gz`)", f"{len(CELLS) * len(RULES) * len(METHODS_MAIN[:6])} rows × {len(LENGTHS)} lengths"],
    ["the transfer sources: every method's power and the model-null level under the nine transfer sources beside the diagonal", "as above; the model-null level over the 1,000 evaluation keys × N₀ texts", "Table 13 (the builder's summary for conformal@5000 at the primary arm, L = 256, α = 0.01; every method in `descriptive_rows_full.csv.gz` and `null_rows_full.csv.gz`)", f"{len(CELLS) * len(RULES) * len(SOURCES)} rows"],
    ["the design remedy: the paired contrasts h = 2 against h = 1 (δ = 0.5) and distinct against raw, per method; the strength contrast", f"paired on the same {N_TX} prompts and {K4} keys", "Table 12 (the builder's block; the builder's bootstrap salt)", f"{len(CELLS) * len(METHODS_MAIN[:6]) * 4} rows"],
    ["the model-null block: per cell × h × family × rule × L × source × method × α: the key-mean, SD, share above α, 99% key quantile of ℓ̃_k, the predictor's mean and SD and the theory share; the Gumbel family here only; the fixed thresholds' rows", f"over the 1,000 evaluation keys on N₀ = {VALUES['N0']} texts", "Table 14 (L = 256, α = 0.01; the nominal and the diagonal conformal@5000 rows); every row in `null_rows_full.csv.gz`", f"{len(res['null_rows'])} rows ({n_null_src} with a calibration source, {n_null_fixed} fixed-threshold rows; {n_gumbel} Gumbel rows)"],
    ["the quality diagnostics: per cell and arm, the mean perplexity of the model's own tokens under the admissible law, the mean log-probability over the first 192 tokens, rep-4, the loop share, the green share, the EOS mass; the unwatermarked arm's; the human reference per cell", "per unit, summarised over units (the key-batches of 50 texts, the null chunks of 500, the 1,000 human continuations)", "Table 15 (from `results.json` `quality` and the pre-lock `INPUTS.json` `human_reference`; the unit-level values are derived from the unit arrays by the analyzer)", f"{len(CELLS) * (len(ARMS) + 1)} cell × arm rows and {len(CELLS)} human-reference rows"],
    ["the per-prompt pairing: the watermark's effect per prompt, averaged over the K₄ keys, at the arms' widths, both rules, L = 256", f"per prompt ({N_TX}), over the {K4} keys", "Table 16 and Figure 6 (the builder's block)", f"{len(PAIR)} cell × arm × rule series of {N_TX} prompts"],
    ["W1's predicted-cost uncertainty: the key-and-prompt cluster-bootstrap SE and 95% interval of the predicted key-median, and the cell's tolerance c", "over the pilot's 8 key clusters and 64 prompt columns (pre-lock, `INPUTS.json`)", "Table 3 (the SE, the interval and c beside every W1 row)", f"{len(res['W1']['rows'])} rows"],
    ["the integrity record: the inventory digest; the hook-flag contract per unit; abstentions by setting with their kind and order index; the run-void share; the calibration-moment consistency per prefix", "protocol §9", "Table 17 (the power-table settings and the null-block settings) and Table 18 (the null-block settings by family, rule, method, α, kind and j)", f"{VALUES['n_abstaining_settings']} power-table settings; {VALUES['n_null_abst_settings']} null-block settings"],
    ["W2's components: the two-way between-key variance (raw and floored), the observed variance of the per-key means, the residual mean square, the prompt component, for the nominal and the method; the binomial proxy's variance, raw corrected variance and mean binomial variance for both", "per W2 row", "Tables 4 and 5", f"{len(res['W2']['rows'])} rows"],
    ["W3's diagnostics per row: ρ̄_E, σ_E², ρ̄_C, σ_C², ρ_CE and the shared-tuple count, v and v_raw, the order index j, the predicted finite-evaluation and population shares above α; the fixed and Gumbel null rows labelled with the predictor used or 'not applicable'", "per null row", "Table 7 (the unresolved and inconsistent rows); every row in `null_rows_full.csv.gz` (fields `rho_E`, `sigma2_E`, `rho_C`, `sigma2_C`, `rho_CE`, `n_shared_tuples`, `v`, `v_raw`, `j`, `pred_share_above_alpha_finite`, `pred_share_above_alpha_pop`, `predictor`)", f"{n_w3_fail} rows in Table 7; {len(res['W3']['rows'])} W3 rows and {len(res['null_rows'])} null rows in the supplement"]])
# ------------------------------------------------------------------ figures
def save(fig, name):
    fig.savefig(OUTDIR / f"{name}.png", dpi=160, bbox_inches="tight", metadata={"Software": None}); fig.savefig(OUTDIR / f"{name}.svg", bbox_inches="tight", metadata={"Date": None, "Creator": None}); plt.close(fig); FIGS[name] = f"{name}.png"
# fig1: the operating points
fig, axes = plt.subplots(2, len(CELLS), figsize=(3.6 * len(CELLS), 6.6), sharey=True)
for j, cell in enumerate(CELLS):
    for i, (lab, key_l) in enumerate((("Study 3's stored null level ℓ_k on corpus text (pp)", "l3"), ("model-null level ℓ̃_k on unwatermarked generations (pp)", "l0"))):
        ax = axes[i, j]
        for v, col, mk in zip(METHODS_MAIN[:6], SEQ6, "osD^vP"):
            d = OP[(cell, v)]; ax.scatter(100 * d[key_l], 100 * d["pi"], s=12, c=col, marker=mk, label=v, alpha=0.8, linewidths=0)
        ax.axvline(100 * A_PRIM, color=COL["muted"], lw=0.8, ls="--"); ax.set_title(CELL_LABEL[cell] if i == 0 else "", fontsize=9)
        if j == 1:
            ax.set_xlabel(lab)
        if j == 0:
            ax.set_ylabel("realised power π_k (pp)")
h_, l_ = axes[0, 0].get_legend_handles_labels(); fig.legend(h_, l_, loc="lower center", ncol=6, fontsize=7, title="method (the dashed line marks α)", bbox_to_anchor=(0.5, -0.02))
fig.suptitle(f"Per-key operating points at the primary setting ({ARM_LABEL[PRIMARY]}, raw rule, L = {L_PRIM}, α = {A_PRIM}); {VALUES['mode_label'].split(' ')[0]}", fontsize=9); fig.tight_layout(rect=(0, 0.04, 1, 0.97)); save(fig, "fig1_operating_points")
# fig2: the per-key costs against the prediction (W1)
fig, axes = plt.subplots(1, len(CELLS), figsize=(3.4 * len(CELLS), 3.4), sharey=True)
for j, cell in enumerate(CELLS):
    ax = axes[j]; d = W1_OWN[cell]; x = np.argsort(d["pred"]); ax.scatter(100 * d["pred"][x], 100 * d["real"][x], s=12, c=COL["raw"], linewidths=0, label="keys")
    ax.axhspan(100 * (d["pred_median"] - d["tol"]), 100 * (d["pred_median"] + d["tol"]), color=COL["grid"], alpha=0.8, label="predicted median ± c"); ax.axhline(100 * d["median"], color=COL["accent"], lw=1.2, label="realised median")
    ax.axhspan(100 * d["lo"], 100 * d["hi"], color=COL["accent"], alpha=0.15, label="its 95% interval"); lim = [0, 100 * max(d["pred"].max(), d["real"].max(), 0.05) * 1.05]; ax.plot(lim, lim, color=COL["muted"], lw=0.8, ls=":")
    ax.set_title(f"{CELL_LABEL[cell]}: {d['class']}", fontsize=9); ax.set_xlabel("predicted cost Δ̂_k (pp)")
axes[0].set_ylabel("realised cost Δ_k (pp)"); axes[0].legend(fontsize=7); fig.suptitle(f"W1: the realised cost per key against the threshold-shift prediction (raw rule, conformal@{w1['N_cal']}, L = {w1['length']}, α = {w1['alpha']})", fontsize=9); save(fig, "fig2_w1_costs")
# fig3: W2 ratios and components
fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.4))
ax = axes[0]; y = 0; ticks = []
for (cell, rule), d in W2_OWN.items():
    col = COL[rule]; ax.plot([d["lo"], d["hi"]], [y, y], color=col, lw=2); ax.plot([d["R"]], [y], "o", color=col); ticks.append((y, f"{CELL_LABEL[cell]}, {rule}: {d['class']}")); y += 1
ax.axvline(1, color=COL["muted"], lw=0.8, ls="--"); ax.axvspan(w2["band"][0], w2["band"][1], color=COL["grid"], alpha=0.6); ax.set_yticks([t[0] for t in ticks]); ax.set_yticklabels([t[1] for t in ticks], fontsize=7); ax.set_xlabel("R_pow = SD_b(conformal)/SD_b(nominal), with its 95% key-bootstrap interval"); ax.set_title("W2 rows (the band [2/3, 3/2] shaded)", fontsize=9)
ax = axes[1]; xs = np.arange(len(W2_OWN)); w = 0.2
for i, (lab, key_, off, col) in enumerate((("two-way SD_b nominal", "sd_n", -1.5, COL["raw"]), ("two-way SD_b conformal", "sd_c", -0.5, COL["distinct"]), ("observed SD nominal", "obs_n", 0.5, "#86b6ef"), ("observed SD conformal", "obs_c", 1.5, "#f5a988"))):
    ax.bar(xs + off * w, [100 * d[key_] for d in W2_OWN.values()], w, color=col, label=lab)
ax.set_xticks(xs); ax.set_xticklabels([f"{c.split('_')[0][:5]}\n{r[:4]}" for c, r in W2_OWN], fontsize=7); ax.set_ylabel("SD across keys (pp)"); ax.legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2); ax.set_title("the components", fontsize=9); fig.tight_layout(); save(fig, "fig3_w2")
# fig4: the length curves
fig, axes = plt.subplots(len(RULES), len(CELLS), figsize=(3.4 * len(CELLS), 2.9 * len(RULES)), sharey=True, sharex=True)
for i, rule in enumerate(RULES):
    for j, cell in enumerate(CELLS):
        ax = axes[i, j]
        for v, col, mk in zip(METHODS_MAIN[:6], SEQ6, "osD^vP"):
            ys = [drow(cell, PRIMARY, rule, L, cell, v, A_PRIM)["power_mean"] for L in LENGTHS]; ax.plot(LENGTHS, [100 * y_ for y_ in ys], marker=mk, color=col, label=v)
        ax.set_title(f"{CELL_LABEL[cell]}, {rule}", fontsize=9); ax.set_xticks(LENGTHS)
        if i == len(RULES) - 1 and j == 1:
            ax.set_xlabel("length L (tokens; only L = 256 is a calibrated operating point)")
        if j == 0:
            ax.set_ylabel("key-mean power (pp)")
axes[0, 0].legend(fontsize=7); fig.suptitle(f"Power against length at the primary arm ({ARM_LABEL[PRIMARY]}), α = {A_PRIM}, diagonal source", fontsize=9); fig.tight_layout(rect=(0, 0, 1, 0.97)); save(fig, "fig4_length")
# fig5: W3 observed against predicted SD
fig, ax = plt.subplots(figsize=(5.2, 4.2)); cls_col = {"consistent": COL["raw"], "inconsistent": COL["accent"], "unresolved": COL["distinct"], "ineligible": COL["muted"]}
for cls_ in ("consistent", "unresolved", "inconsistent", "ineligible"):
    sel = [r for r in w3rows if r["w3_class"] == cls_]
    if sel:
        ax.scatter([100 * r["pred_sd"] for r in sel], [100 * r["level_sd"] for r in sel], s=14, c=cls_col[cls_], label=f"{cls_} ({len(sel)})", linewidths=0, alpha=0.8)
mx = max([100 * r["level_sd"] for r in w3rows] + [100 * r["pred_sd"] for r in w3rows if r["pred_sd"]] + [0.01]); ax.plot([0, mx], [0, mx], color=COL["muted"], lw=0.8, ls=":"); ax.plot([0, mx], [0, 1.5 * mx], color=COL["grid"], lw=0.8); ax.plot([0, mx], [0, mx / 1.5], color=COL["grid"], lw=0.8)
ax.set_xlabel("predicted SD of the model-null level across keys (pp)"); ax.set_ylabel("observed SD (pp)"); ax.legend(fontsize=7); ax.set_title(f"W3: {len(w3rows)} rows (KGW, h ∈ {{1, 2}}, both rules, conformal at N_cal ∈ {{1000, 5000}}, every source)", fontsize=9); save(fig, "fig5_w3")
# fig6: the per-prompt watermark effect
fig, axes = plt.subplots(1, len(CELLS), figsize=(3.4 * len(CELLS), 3.2), sharey=True)
for j, cell in enumerate(CELLS):
    ax = axes[j]
    for arm, col in zip(ARMS, (COL["raw"], COL["third"], COL["distinct"])):
        for rule, ls in zip(RULES, ("-", ":")):
            if (cell, arm, rule) in PAIR:
                e = PAIR[(cell, arm, rule)]; ax.plot(np.sort(e), ls=ls, color=col, label=f"{ARM_LABEL[arm]}, {rule}")
    ax.set_title(CELL_LABEL[cell], fontsize=9); ax.set_xlabel("prompts, sorted by effect")
axes[0].set_ylabel("watermark effect per prompt, mean over keys (z)"); axes[0].legend(fontsize=6); fig.suptitle("The per-prompt pairing: Φ̄⁻¹(p_wm) − Φ̄⁻¹(p_null) at L = 256, averaged over the power keys", fontsize=9); save(fig, "fig6_pairing")
# ------------------------------------------------------------------ supplements, values, the assembled report
with gzip.GzipFile(OUTDIR / "descriptive_rows_full.csv.gz", "wb", mtime=0) as fh:
    cols = list(res["descriptive_rows"][0].keys()); fh.write((",".join(cols) + "\n" + "\n".join(",".join("" if r[c] is None else str(r[c]) for c in cols) for r in res["descriptive_rows"])).encode())
with gzip.GzipFile(OUTDIR / "null_rows_full.csv.gz", "wb", mtime=0) as fh:
    cols = sorted({c for r in res["null_rows"] for c in r}); fh.write((",".join(cols) + "\n" + "\n".join(",".join("" if r.get(c) is None else str(r.get(c)).replace(",", ";") for c in cols) for r in res["null_rows"])).encode())
(OUTDIR / "tables.md").write_text("\n\n".join(f"### {k}\n\n{v}" for k, v in TABLES.items()))
# registered descriptive values for the prose
for cell in CELLS:
    d = W1_OWN[cell]; c = cell.split("_")[0]; reg(f"w1_{c}_class", d["class"]); reg(f"w1_{c}_realised_median_pp", pp(d["median"])); reg(f"w1_{c}_predicted_median_pp", pp(d["pred_median"])); reg(f"w1_{c}_ci", f"[{pp(d['lo'])}, {pp(d['hi'])}]"); reg(f"w1_{c}_tol_pp", pp(d["tol"]))
    for rule in RULES:
        d2 = W2_OWN[(cell, rule)]; reg(f"w2_{c}_{rule}_class", d2["class"]); reg(f"w2_{c}_{rule}_R", fnum(d2["R"], 3)); reg(f"w2_{c}_{rule}_ci", f"[{fnum(d2['lo'], 3)}, {fnum(d2['hi'], 3)}]")
    r = drow(cell, PRIMARY, "raw", L_PRIM, cell, "nominal", A_PRIM); reg(f"power_{c}_nominal_raw_pp", pp(r["power_mean"])); r = drow(cell, PRIMARY, "raw", L_PRIM, cell, f"conformal@{NCALS[-1]}", A_PRIM); reg(f"power_{c}_conformal_raw_pp", pp(r["power_mean"])); reg(f"cost_{c}_conformal_raw_median_pp", pp(r["cost_q50"]))
    r = drow(cell, "kgw_h1_d2.0", "raw", L_PRIM, cell, "nominal", A_PRIM); reg(f"power_{c}_nominal_raw_d2_pp", pp(r["power_mean"]))
    q = res["quality"][f"{cell}|{PRIMARY}"]; reg(f"loop_{c}_primary_pct", pp(q["loop"]["mean"], 2)); reg(f"ppl_{c}_primary", fnum(q["ppl"]["mean"], 1)); reg(f"ppl_{c}_none", fnum(res["quality"][f"{cell}|none"]["ppl"]["mean"], 1)); reg(f"ppl_{c}_human", fnum(hr[cell]["ppl"], 1))
# ---- registered values for the conductor's reading (section 8): every number it cites, from the same structures as the tables above
MTAG = {"nominal": "nominal", "multiplier20": "multiplier", "empirical": "empirical", "pooled": "pooled", f"conformal@{NCALS[-1]}": "conformal", f"tolerance@{NCALS[-1]}": "tolerance"}
w1rows = {r["cell"]: r for r in res["W1"]["rows"]}
for cell, d in W1_OWN.items():
    c = cell.split("_")[0]; blo, bhi = d["pred_median"] - d["tol"], d["pred_median"] + d["tol"]
    reg(f"w1_{c}_band", f"[{pp(blo, 2)}, {pp(bhi, 2)}]"); reg(f"w1_{c}_ci_2dp", f"[{pp(d['lo'], 2)}, {pp(d['hi'], 2)}]"); reg(f"w1_{c}_overshoot_pp", pp(max(blo - d["lo"], d["hi"] - bhi, 0.0), 2))
reg("w1_share_within_min_pct", pp(min(r["share_keys_within_tol"] for r in w1rows.values()), 0)); reg("w1_share_within_max_pct", pp(max(r["share_keys_within_tol"] for r in w1rows.values()), 0))
reg("w1_corr_min", fnum(min(r["corr_real_pred"] for r in w1rows.values()), 2)); reg("w1_corr_max", fnum(max(r["corr_real_pred"] for r in w1rows.values()), 2))
w2rows = res["W2"]["rows"]
reg("w2_R_min", fnum(min(r["R_pow"] for r in w2rows), 3)); reg("w2_R_max", fnum(max(r["R_pow"] for r in w2rows), 3)); reg("w2_n_R_below_1", sum(1 for r in w2rows if r["R_pow"] < 1))
reg("w2_n_sdb_method_below_nominal", sum(1 for r in w2rows if r["sd_between_method"] < r["sd_between_nominal"]))
r_wr = next(r for r in w2rows if r["cell"] == "wikipedia_en_256" and r["rule"] == "raw"); reg("w2_wikipedia_raw_ci_hi_excess", fnum(r_wr["ci_hi"] - 1.0, 3))
reg("w2_min_finite_resamples", min(r["finite_resamples"] for r in w2rows))
reg("w2_sdb_nominal_min_pp", pp(min(r["sd_between_nominal"] for r in w2rows))); reg("w2_sdb_nominal_max_pp", pp(max(r["sd_between_nominal"] for r in w2rows)))
reg("w2_noise_sd_min_pp", pp(min(float(np.sqrt(r["ms_resid_nominal"] / r["n"])) for r in w2rows))); reg("w2_noise_sd_max_pp", pp(max(float(np.sqrt(r["ms_resid_nominal"] / r["n"])) for r in w2rows)))
reg("w2_sd_obs_nominal_min_pp", pp(min(r["sd_observed_nominal"] for r in w2rows))); reg("w2_sd_obs_nominal_max_pp", pp(max(r["sd_observed_nominal"] for r in w2rows)))
w3r_ = res["W3"]["rows"]; inel = [r for r in w3r_ if not r["w3_eligible"]]; resolved = [r for r in w3r_ if r["w3_class"] in ("consistent", "inconsistent")]; unres = [r for r in w3r_ if r["w3_class"] == "unresolved"]
reg("w3_n_ineligible", len(inel)); reg("w3_n_ineligible_ncal5000", sum(1 for r in inel if variant_parts(r["variant"])[1] == NCALS[-1])); reg("w3_n_ineligible_h2", sum(1 for r in inel if r["h"] == 2))
reg("w3_n_ineligible_theory_share", sum(1 for r in inel if r.get("theory_share") is None or r["theory_share"] < w3["theory_share_min"])); reg("w3_n_ineligible_flag", sum(1 for r in inel if r.get("flags")))
ts_in = [r["theory_share"] for r in inel if r.get("theory_share") is not None]; reg("w3_ineligible_theory_share_min", fnum(min(ts_in), 2) if ts_in else "—"); reg("w3_ineligible_theory_share_max", fnum(max(ts_in), 2) if ts_in else "—")
rat = np.array([r["w3_ratio"] for r in resolved], dtype=np.float64); reg("w3_ratio_median_resolved", fnum(float(np.median(rat)), 3)); reg("w3_ratio_p10_resolved", fnum(float(np.quantile(rat, 0.10)), 3)); reg("w3_ratio_p90_resolved", fnum(float(np.quantile(rat, 0.90)), 3)); reg("w3_n_resolved_ratio_below_1", int((rat < 1).sum()))
reg("w3_unresolved_ratio_min", fnum(min(r["w3_ratio"] for r in unres), 3) if unres else "—"); reg("w3_unresolved_ratio_max", fnum(max(r["w3_ratio"] for r in unres), 3) if unres else "—")
reg("w3_unresolved_sources", ", ".join(sorted({CELL_LABEL[r["source"]] for r in unres})) or "none"); reg("w3_unresolved_cells", ", ".join(sorted({CELL_LABEL[r["cell"]] for r in unres})) or "none"); reg("w3_n_unresolved_h1_raw", sum(1 for r in unres if r["h"] == 1 and r["rule"] == "raw"))
H_PRIM = arm_spec(grid, PRIMARY)["h"]; V_CONF = f"conformal@{NCALS[-1]}"
for cell in CELLS:
    c = cell.split("_")[0]
    rn0 = null_file[(cell, 0, "kgw", "raw", L_PRIM, None, "nominal", A_PRIM)]; reg(f"mn_{c}_h0_raw_nominal_mean_pp", pp(rn0["level_mean"], 2)); reg(f"mn_{c}_h0_raw_nominal_sd_pp", pp(rn0["level_sd"], 2))
    rn1 = null_file[(cell, H_PRIM, "kgw", "raw", L_PRIM, None, "nominal", A_PRIM)]; reg(f"mn_{c}_h1_raw_nominal_mean_pp", pp(rn1["level_mean"], 2)); reg(f"mn_{c}_h1_raw_nominal_share_pct", pp(rn1["share_above_alpha"], 0))
    rc_ = null_file[(cell, H_PRIM, "kgw", "raw", L_PRIM, cell, V_CONF, A_PRIM)]; reg(f"mn_{c}_h1_raw_conformal_mean_pp", pp(rc_["level_mean"], 2)); reg(f"mn_{c}_h1_raw_conformal_share_pct", pp(rc_["share_above_alpha"], 0))
    reg(f"mn_{c}_h1_distinct_conformal_share_pct", pp(null_file[(cell, H_PRIM, "kgw", "distinct", L_PRIM, cell, V_CONF, A_PRIM)]["share_above_alpha"], 0))
    for v, tag in MTAG.items():
        if tag != "nominal":
            reg(f"cost_{c}_{tag}_raw_median_pp", pp(drow(cell, PRIMARY, "raw", L_PRIM, cell, v, A_PRIM)["cost_q50"]))
        if tag in ("conformal", "pooled", "multiplier"):
            reg(f"cost_{c}_{tag}_distinct_median_pp", pp(drow(cell, PRIMARY, "distinct", L_PRIM, cell, v, A_PRIM)["cost_q50"]))
    reg(f"cost_{c}_conformal_distinct_mean_pp", pp(drow(cell, PRIMARY, "distinct", L_PRIM, cell, V_CONF, A_PRIM)["cost_mean"]))
    r = drow(cell, PRIMARY, "raw", L_PRIM, cell, V_CONF, A_PRIM); reg(f"cost_{c}_conformal_raw_q5_pp", pp(r["cost_q05"])); reg(f"cost_{c}_conformal_raw_q95_pp", pp(r["cost_q95"]))
    r = drow(cell, "kgw_h2_d0.5", "raw", L_PRIM, cell, V_CONF, A_PRIM); reg(f"cost_{c}_conformal_raw_h2_median_pp", pp(r["cost_q50"]))
    for tag, v, lab, (aa, ab, ra, rb) in (("nominal", "nominal", "h2_minus_h1_raw", ("kgw_h2_d0.5", "kgw_h1_d0.5", "raw", "raw")), ("nominal", "nominal", "distinct_minus_raw", ("kgw_h1_d0.5", "kgw_h1_d0.5", "distinct", "raw")), ("conformal", V_CONF, "distinct_minus_raw", ("kgw_h1_d0.5", "kgw_h1_d0.5", "distinct", "raw"))):
        m_, lo_, hi_, kk_ = paired(cell, aa, ab, ra, rb, v); reg(f"remedy_{c}_{tag}_{lab}", f"{pp(m_)} [{pp(lo_)}, {pp(hi_)}]")
    c1, c2, gsd = MECH[(cell, PRIMARY, "raw", L_PRIM)]; reg(f"mech_{c}_corr_null_power", fnum(c1, 2)); reg(f"mech_{c}_r2", fnum(c1 ** 2, 2)); reg(f"mech_{c}_corr_null_green", fnum(c2, 2)); reg(f"mech_{c}_green_sd_pp", pp(gsd, 2))
    reg(f"mech_{c}_corr_null_power_d2", fnum(MECH[(cell, "kgw_h1_d2.0", "raw", L_PRIM)][0], 2)); reg(f"mech_{c}_corr_null_power_h2", fnum(MECH[(cell, "kgw_h2_d0.5", "raw", L_PRIM)][0], 2))
    for rule in RULES:
        tr = [(drow(cell, PRIMARY, rule, L_PRIM, src, V_CONF, A_PRIM), null_file[(cell, H_PRIM, "kgw", rule, L_PRIM, src, V_CONF, A_PRIM)]) for src in SOURCES if src != cell]
        reg(f"transfer_{c}_{rule}_power_min_pp", pp(min(r_["power_mean"] for r_, _ in tr))); reg(f"transfer_{c}_{rule}_power_max_pp", pp(max(r_["power_mean"] for r_, _ in tr)))
        if rule == "raw":
            reg(f"transfer_{c}_{rule}_share_min_pct", pp(min(n_["share_above_alpha"] for _, n_ in tr), 0)); reg(f"transfer_{c}_{rule}_share_max_pct", pp(max(n_["share_above_alpha"] for _, n_ in tr), 0))
            reg(f"transfer_{c}_{rule}_diag_share_pct", pp(null_file[(cell, H_PRIM, "kgw", rule, L_PRIM, cell, V_CONF, A_PRIM)]["share_above_alpha"], 0))
    reg(f"loop_{c}_d2_pct", pp(res["quality"][f"{cell}|kgw_h1_d2.0"]["loop"]["mean"], 2)); reg(f"loop_{c}_none_pct", pp(res["quality"][f"{cell}|none"]["loop"]["mean"], 2))
    e_ = PAIR[(cell, PRIMARY, "raw")]; reg(f"pair_{c}_primary_raw_mean_z", fnum(float(e_.mean()), 2)); reg(f"pair_{c}_primary_raw_sd_z", fnum(float(e_.std(ddof=1)), 2)); reg(f"pair_{c}_d2_raw_mean_z", fnum(float(PAIR[(cell, "kgw_h1_d2.0", "raw")].mean()), 2))
for (cell, v), d in OP.items():
    c = cell.split("_")[0]; tag = MTAG[v]
    reg(f"op_{c}_{tag}_share_above_alpha_pct", pp((d["l3"] > A_PRIM).mean(), 0))
    if tag in ("nominal", "conformal"):
        reg(f"op_{c}_{tag}_share_above_alpha_modelnull_pct", pp((d["l0"] > A_PRIM).mean(), 0)); reg(f"op_{c}_{tag}_corr", fnum(float(np.corrcoef(d["l3"], d["pi"])[0, 1]), 2) if d["l3"].std() > 0 and d["pi"].std() > 0 else "—")
    if tag == "nominal":
        reg(f"op_{c}_{tag}_stored_mean_pp", pp(d["l3"].mean(), 2))
d2rows = [r_ for r_ in (drow(cell, "kgw_h1_d2.0", rule, L_PRIM, cell, v, A_PRIM) for cell in CELLS for rule in RULES for v in VARIANTS) if r_]   # every method and N_cal at that setting
reg("power_d2_min_mean_pp", pp(min(r_["power_mean"] for r_ in d2rows))); reg("cost_d2_max_mean_pp", pp(max(r_["cost_mean"] for r_ in d2rows), 2))
r_q = max(d2rows, key=lambda r_: r_["cost_q95"]); reg("cost_d2_max_q95_pp", pp(r_q["cost_q95"])); reg("cost_d2_max_q95_setting", f"{CELL_LABEL[r_q['cell']]}, {r_q['rule']} rule, {r_q['variant']}"); reg("n_d2_rows", len(d2rows)); reg("n_d2_rows_cost_q95_pos", sum(1 for r_ in d2rows if r_["cost_q95"] > 0))
for cell in CELLS:   # F5: the shape of the h = 0 raw nominal model-null levels over the 1,000 keys (L = 256, alpha = 0.01)
    c = cell.split("_")[0]; lv0 = ARR[f"null|{cell}|h0|kgw|raw|L{L_PRIM}|fixed"][VFIX.index("nominal"), ALPHAS.index(A_PRIM)].astype(np.float64) / VALUES["N0"]; q25, q50, q75 = np.quantile(lv0, [0.25, 0.5, 0.75]); m0 = float(lv0.mean())
    reg(f"mn_{c}_h0_raw_nominal_q25_pct", pp(q25, 2)); reg(f"mn_{c}_h0_raw_nominal_q50_pct", pp(q50, 2)); reg(f"mn_{c}_h0_raw_nominal_q75_pct", pp(q75, 2)); reg(f"mn_{c}_h0_raw_nominal_n_mid", int(((lv0 > 0.05) & (lv0 < 0.95)).sum())); reg(f"mn_{c}_h0_raw_nominal_n_ge95", int((lv0 >= 0.95).sum()))
    reg(f"mn_{c}_h0_raw_nominal_var_ratio", fnum(float(lv0.var(ddof=1) / (m0 * (1 - m0))), 2))
reg("w2_min_finite_required", int(np.ceil(w2["min_finite_resample_share"] * BOOT_B))); reg("w2_min_finite_gap", int(VALUES["w2_min_finite_resamples"]) - int(np.ceil(w2["min_finite_resample_share"] * BOOT_B))); reg("n_mismatches", len(CHECKS["mismatches"]))
reg("w2_agree_disagree_clause", "none agrees and none disagrees" if res["W2"]["n_agree"] == 0 and res["W2"]["n_disagree"] == 0 else f"{res['W2']['n_agree']} agree and {res['W2']['n_disagree']} disagree")
r_ = drow("stackexchange_en_256", PRIMARY, "raw", L_PRIM, "news_en_256", V_CONF, A_PRIM); n_ = null_file[("stackexchange_en_256", H_PRIM, "kgw", "raw", L_PRIM, "news_en_256", V_CONF, A_PRIM)]
reg("transfer_stackexchange_from_news_raw_power_pp", pp(r_["power_mean"])); reg("transfer_stackexchange_from_news_raw_share_pct", pp(n_["share_above_alpha"], 0))
reg("n_tables", len(TABLES)); reg("n_figures", len(FIGS)); reg("checks_summary", "; ".join(f"{k} {v}" for k, v in CHECKS["verified"].items()))
(OUTDIR / "prose_values.json").write_text(json.dumps(VALUES, indent=1, default=str))
prose = PROSE.read_text(); tab_n = {}
def sub_table(m):
    name = m.group(1)
    if name not in TABLES:
        raise SystemExit(f"unknown table placeholder {name}")
    return TABLES[name]
def sub_fig(m):
    name = m.group(1)
    if name not in FIGS:
        raise SystemExit(f"unknown figure placeholder {name}")
    return f"![{name}]({'report/' if REAL else ''}{FIGS[name]})" if REAL else f"![{name}]({FIGS[name]})"
def sub_val(m):
    name = m.group(1)
    if name not in VALUES:
        raise SystemExit(f"unresolved placeholder [[{name}]]")
    USED.add(name); return str(VALUES[name])
text = re.sub(r"<<TABLE:([A-Za-z0-9_]+)>>", sub_table, prose); text = re.sub(r"<<FIG:([A-Za-z0-9_]+)>>", sub_fig, text); text = re.sub(r"\[\[([A-Za-z0-9_]+)\]\]", sub_val, text)
if REAL:
    text = text.replace("](report/", "](../outputs/study4_v0.1/report/")
left = re.findall(r"\[\[[^\]]+\]\]|<<[A-Z]+:[^>]+>>", text)
if left:
    raise SystemExit(f"unresolved placeholders remain: {left[:5]}")
if FIXTURE:
    text = "**FIXTURE REPORT: a synthetic inventory with every number planted; not the study (research/study4/s4_fixture.py).**\n\n" + text
REPORT.write_text(text); CHECKS["unused_registered_values"] = sorted(set(VALUES) - USED); CHECKS["tables"] = list(TABLES); CHECKS["figures"] = list(FIGS); CHECKS["mode"] = VALUES["mode_label"]
(OUTDIR / "checks.json").write_text(json.dumps(CHECKS, indent=1, default=float))
print(f"report written: {REPORT} ({len(TABLES)} tables, {len(FIGS)} figures, {len(VALUES)} values, {len(CHECKS['unused_registered_values'])} registered-but-unused) in {time.time() - T_START:.0f}s")
