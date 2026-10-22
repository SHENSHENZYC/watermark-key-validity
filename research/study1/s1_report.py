"""Study 1 report builder (protocol v0.3): every table, figure and number in research/STUDY1_REPORT_v0.1.md comes from the locked
outputs (outputs/study1_v0.3/cells/*.json and results.json), never typed by hand (rule A4.1 of the research-project-guide).

Before writing anything the builder RE-COMPUTES, with its own code (not s1_analyze), from the per-cell files:
  - every cell's key-mean level and across-key SD from the recorded per-key levels, and R1's eligibility, status and counts;
  - R2's two-sided KL-Chernoff bound per check and the flagged set;
  - R3's known-mean estimator from the recorded per-key q values and the gross-failure decision per cell, the coverage diagnostic;
  - R4's and R5's monotonicity decisions per chain and R4b's analytic limits;
and asserts that all of these equal results.json (every mismatch is collected and reported before raising).
Writes <report dir>/: tables.md, tables_curves_full.md, prose_values.json, checks.json and fig1..fig5 (.png, .svg); then assembles the
report from research/study1/report_prose_v0.1.md by filling <<TABLE:name>>, <<FIG:name>> and [[name]] and refusing any unresolved
placeholder (registered-but-unused names are listed).
Usage: .venv/bin/python research/study1/s1_report.py                      (study mode: verifies the lock; writes outputs/study1_v0.3/report/ and research/STUDY1_REPORT_v0.1.md)
       .venv/bin/python research/study1/s1_report.py --pilot --results <pilot results.json> --cells <validation dir> --out-dir <dir outside the repository>
       (fixture mode on the disclosed pilot: label PILOT; can never write the canonical report or report directory)
"""
import json, math, pathlib, re, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
from scipy.stats import norm      # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "tools"))
from s1_run import OUT, STUDY, GRID_CANON, verify_lock, sha, expected_cells, law_name   # noqa: E402

ARGV = sys.argv[1:]
PILOT = "--pilot" in ARGV
PROSE = HERE / "report_prose_v0.1.md"
if PILOT:
    RES = pathlib.Path(ARGV[ARGV.index("--results") + 1]); CELLS = pathlib.Path(ARGV[ARGV.index("--cells") + 1]); OUTDIR = pathlib.Path(ARGV[ARGV.index("--out-dir") + 1]).resolve()
    if ROOT.resolve() in OUTDIR.parents or OUTDIR == ROOT.resolve():
        raise SystemExit("pilot mode must write outside the repository")
    REPORT = OUTDIR / "STUDY1_REPORT_fixture_PILOT.md"; MANIFEST = pathlib.Path(ARGV[ARGV.index("--manifest") + 1]) if "--manifest" in ARGV else None
else:
    if len(ARGV) > 0:
        raise SystemExit("study mode takes no arguments (canonical paths only)")
    RES = ROOT / OUT / "results.json"; CELLS = ROOT / OUT / "cells"; OUTDIR = ROOT / OUT / "report"; REPORT = ROOT / "research" / "STUDY1_REPORT_v0.1.md"; MANIFEST = ROOT / OUT / "RUN_MANIFEST.json"
OUTDIR.mkdir(parents=True, exist_ok=True)

R1_BAND = (2.0 / 3.0, 1.5); R1_ALPHA = "0.01"; R1_RULES = ("raw", "distinct"); R1_MIN_M = 30; R1_MIN_THEORY_SHARE = 0.75; R1_MIN_RESOLVED = 30; R1_PASS_SHARE = 0.80
R2_PBOUND = 1e-6; R3_GROSS_SE = 6.0; R3_REDUCTION_V = 10000; R3_REDUCTION_BOUND = 0.01
# dataviz palette (validated 2026-10-10 with scripts/validate_palette.js, light surface, all pairs): rules raw/distinct/first = slots 1/2/3;
# colourings independent/fixed = blue/violet; the aqua slot is below 3:1 contrast, so every figure carries a legend and every value is in a table (the relief rule)
COL_RULE = {"raw": "#2a78d6", "distinct": "#eb6834", "first": "#1baf7a"}; COL_COLOURING = {"independent": "#2a78d6", "fixed": "#4a3aa7"}
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#898781", "#e1e0d9", "#fcfcfb"; SEQ = ["#cde2fb", "#86b6ef", "#2a78d6", "#104281"]
MK_RULE = {"raw": "o", "distinct": "s", "first": "D"}
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.8, "grid.linestyle": "-", "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "lines.linewidth": 2.0, "lines.markersize": 5})

# ------------------------------------------------------------------ loading
res = json.loads(RES.read_text())
if PILOT:
    assert res["label"].startswith("PILOT"), "pilot mode needs the pilot analysis file"
else:
    assert res["label"] == "STUDY", f"results label {res['label']!r} is not STUDY"
    verify_lock(ROOT / OUT / "PRE_RUN_LOCK.json", GRID_CANON, root=ROOT)
grid = json.loads((ROOT / GRID_CANON).read_text())
EXPECTED = expected_cells(grid, grid["validation_laws"] if PILOT else None)
cells = {}
for e in EXPECTED:
    d = json.loads((CELLS / e["file"]).read_text()); d["_exp"] = e; d["file"] = e["file"]; cells[e["file"]] = d
assert len(cells) == res["n_cells"], (len(cells), res["n_cells"])
LIVE = [c for c in cells.values() if "levels" in c and c.get("N_eff", 0) > 0 and not c.get("degenerate")]
CORE = [c for c in LIVE if c["_exp"]["role"] == "core"]
G0 = grid["gamma"][0]; Lw = max(grid["L"])
ALPHAS = [str(a) for a in grid["alpha"]]
manifest = json.loads(MANIFEST.read_text()) if (MANIFEST and pathlib.Path(MANIFEST).exists()) else None


def key_of(c):
    return (c["_exp"]["name"], c["h"], c["colouring"], c["gamma"], c["L"], c["rule"])


BY = {key_of(c): c for c in cells.values()}
CORE_LAWS = [law_name(l) for l in grid["laws"] if l.get("role", "core") == "core"] if not PILOT else [law_name(l) for l in grid["validation_laws"] if l.get("role", "core") == "core"]
ILL_LAWS = [law_name(l) for l in (grid["validation_laws"] if PILOT else grid["laws"]) if l.get("role", "core") != "core"]
LAW_SPEC = {law_name(l): l for l in grid["laws"] + grid["validation_laws"]}


def law_label(name, short=False):
    s = LAW_SPEC[name]; k = s["kind"]
    if k == "zipf":
        return f"Zipf V={s['V']:,}, s={s['s']}" if not short else f"Zipf {s['V']:,}" + ("" if s["s"] == 1.0 else f" s{s['s']}")
    if k == "markov":
        return f"Markov V={s['V']:,} (S={s['S']}, ε={s['eps']})" if not short else f"Markov {s['V']:,}"
    if k == "twotoken":
        return f"two-token chain (p_stay={s['p_stay']})" if not short else "two-token"
    if k == "support":
        return f"support control (uniform on {s['s_support']} of {s['V']:,})" if not short else "support 50/1,000"
    return name


# ------------------------------------------------------------------ formatting and the value registry
VALUES = {}; USED = set()


def reg(name, value):
    value = str(value); m = re.fullmatch(r"(.+?)–\1", value)
    if m:
        value = m.group(1)                      # a range whose two ends print alike collapses to one value
    if name in VALUES and VALUES[name] != value:
        raise SystemExit(f"placeholder {name} registered twice with different values")
    VALUES[name] = value; return VALUES[name]


def fnum(x, d=None):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    if x < 0:
        return "−" + fnum(-x, d)
    if d is not None:
        return f"{x:,.{d}f}"
    ax = abs(x)
    if ax == 0:
        return "0"
    if ax >= 1000:
        return f"{x:,.0f}"
    if ax >= 100:
        return f"{x:.0f}"
    if ax >= 10:
        return f"{x:.1f}"
    if ax >= 1:
        return f"{x:.2f}"
    if ax >= 0.01:
        return f"{x:.3f}"
    return f"{x:.2e}"


def pp(x, d=None):
    return "—" if x is None or not np.isfinite(x) else fnum(100 * x, d)


def pct(x, d=1):
    return "—" if x is None or not np.isfinite(x) else f"{100 * x:.{d}f}%"


def ci(lo, hi, f=fnum):
    return f"[{f(lo)}, {f(hi)}]"


def esc(x):
    return str(x).replace("|", "\\|")


def md_table(header, rows, align=None):
    out = ["| " + " | ".join(esc(h) for h in header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        if len(r) != len(header):
            raise SystemExit(f"table row has {len(r)} cells for {len(header)} columns: {r[:3]}")
        out.append("| " + " | ".join(esc(x) for x in r) + " |")
    return "\n".join(out)


# ------------------------------------------------------------------ independent re-computation (own code; compared with results.json)
def kl_bern(a, m):
    if m <= 0:
        return 0.0 if a <= 0 else math.inf
    if m >= 1:
        return 0.0 if a >= 1 else math.inf
    t1 = a * math.log(a / m) if a > 0 else 0.0; t2 = (1 - a) * math.log((1 - a) / (1 - m)) if a < 1 else 0.0
    return t1 + t2


def kl_bound_two_sided(abar, mu, K):
    return 1.0 if abar == mu else min(1.0, 2.0 * math.exp(-K * kl_bern(abar, mu)))


def r1_status_own(c, alpha=R1_ALPHA, pred="pred_first_order"):
    lv = c["levels"][alpha]; sd_pred = lv[pred]["sd_cond"]; lo_sd, hi_sd = lv["sd_obs_boot_ci95"]
    if not sd_pred > 0:
        return "unresolved", float("nan"), (float("nan"), float("nan"))
    lo, hi = lo_sd / sd_pred, hi_sd / sd_pred; ratio = lv["sd_obs_conditional"] / sd_pred
    if R1_BAND[0] <= lo and hi <= R1_BAND[1]:
        return "consistent", ratio, (lo, hi)
    if hi < R1_BAND[0] or lo > R1_BAND[1]:
        return "inconsistent", ratio, (lo, hi)
    return "unresolved", ratio, (lo, hi)


def r1_block_own(cs, alpha=R1_ALPHA, pred="pred_first_order"):
    elig = [c for c in cs if c["mean_M"] >= R1_MIN_M and c["levels"][alpha][pred]["theory_share"] >= R1_MIN_THEORY_SHARE]
    st = {c["file"]: r1_status_own(c, alpha, pred)[0] for c in elig}
    n_res = sum(1 for s in st.values() if s != "unresolved"); n_con = sum(1 for s in st.values() if s == "consistent")
    share = n_con / n_res if n_res else float("nan")
    return {"n_candidates": len(cs), "n_eligible": len(elig), "n_resolved": n_res, "n_consistent": n_con, "n_inconsistent": n_res - n_con, "n_unresolved": len(elig) - n_res,
            "share_consistent": share, "pass": bool(n_res) and n_res >= R1_MIN_RESOLVED and share >= R1_PASS_SHARE, "status": st}


def independent_checks():
    mism = []; chk = {}

    def close(a, b, tol, what):
        if not (abs(a - b) <= tol):
            mism.append(f"{what}: own {a!r} vs results {b!r} (tol {tol})")
    # per-cell recomputations from the recorded per-key values (rounded to 7 decimals in the files)
    n_lv = 0
    for c in LIVE:
        for a in ALPHAS:
            lv = c["levels"][a]; vals = np.array(lv["level_values"], dtype=np.float64)
            close(float(vals.mean()), lv["key_mean_level"], 1e-6, f"{c['file']} a={a} key-mean from level_values")
            close(float(vals.std(ddof=1)), lv["sd_obs_conditional"], 3e-6, f"{c['file']} a={a} SD from level_values")
            if c["colouring"] == "independent" and c["rule"] == "distinct" and not lv["structural_zero"]:
                b = kl_bound_two_sided(lv["key_mean_level"], lv["exact_marginal_if_indep_distinct"], c["K"])
                if not (abs(b - lv["r2_kl_pbound"]) <= 1e-9 * max(1.0, b)):
                    mism.append(f"{c['file']} a={a} KL bound own {b} vs file {lv['r2_kl_pbound']}")
            n_lv += 1
        q = c["q_hat"]; qv = np.array(q["values"], dtype=np.float64); s0_own = float(((qv - q["exact_mean"]) ** 2).mean())
        close(s0_own, q["var_known_mean"], 4e-7 * float(np.abs(qv - q["exact_mean"]).max()) + 1e-13, f"{c['file']} s0^2 from q values")
    chk["n_level_blocks_recomputed"] = n_lv
    # R1 primary and secondary
    r1_set = [c for c in CORE if c["colouring"] == "independent" and c["rule"] in R1_RULES and c["gamma"] == G0]
    own = r1_block_own(r1_set); R1 = res["rules"]["R1"]
    for k in ("n_candidates", "n_eligible", "n_resolved", "n_consistent", "n_inconsistent", "n_unresolved", "pass"):
        if own[k] != R1[k]:
            mism.append(f"R1 {k}: own {own[k]} vs results {R1[k]}")
    rows_status = {r["cell"]: r["status"] for r in R1["rows"]}
    if rows_status != own["status"]:
        mism.append(f"R1 per-cell statuses differ: {sorted(set(rows_status.items()) ^ set(own['status'].items()))[:5]}")
    chk["R1"] = {k: own[k] for k in own if k != "status"}
    sec_own = {"alpha_0.05": r1_block_own(r1_set, "0.05"), "alpha_0.001": r1_block_own(r1_set, "0.001"),
               "first_rule": r1_block_own([c for c in CORE if c["colouring"] == "independent" and c["rule"] == "first" and c["gamma"] == G0]),
               "gamma_extra": r1_block_own([c for c in CORE if c["colouring"] == "independent" and c["rule"] in R1_RULES and c["gamma"] != G0]),
               "unit_sigma_predictor": r1_block_own(r1_set, R1_ALPHA, "pred_unit_sigma"),
               "illustration": r1_block_own([c for c in LIVE if c["_exp"]["role"] == "illustration" and c["colouring"] == "independent" and c["rule"] in R1_RULES]),
               "fixed_colouring": r1_block_own([c for c in LIVE if c["colouring"] == "fixed" and c["rule"] in R1_RULES])}
    for name, blk in sec_own.items():
        for k in ("n_candidates", "n_eligible", "n_resolved", "n_consistent", "n_inconsistent", "n_unresolved"):
            if blk[k] != res["rules"]["R1_secondary"][name][k]:
                mism.append(f"R1_secondary {name} {k}: own {blk[k]} vs results {res['rules']['R1_secondary'][name][k]}")
    chk["R1_secondary"] = {n: {k: b[k] for k in b if k != "status"} for n, b in sec_own.items()}
    # R2
    flagged = []; zeros = 0; n2 = 0
    for c in LIVE:
        if c["colouring"] != "independent" or c["rule"] != "distinct":
            continue
        for a in ALPHAS:
            lv = c["levels"][a]
            if lv["structural_zero"]:
                zeros += 1; continue
            n2 += 1
            if kl_bound_two_sided(lv["key_mean_level"], lv["exact_marginal_if_indep_distinct"], c["K"]) < R2_PBOUND:
                flagged.append((c["file"], a))
    R2 = res["rules"]["R2"]
    for k, v in (("n_checks", n2), ("n_structural_zero", zeros), ("n_flagged", len(flagged))):
        if R2[k] != v:
            mism.append(f"R2 {k}: own {v} vs results {R2[k]}")
    if sorted((x["cell"], x["alpha"]) for x in R2["flagged"]) != sorted(flagged):
        mism.append("R2 flagged set differs")
    chk["R2"] = {"n_checks": n2, "n_structural_zero": zeros, "n_flagged": len(flagged), "flagged": flagged}
    # R3
    gross = []; cov = []; n3 = 0; z3 = 0; reported = []
    for c in LIVE:
        q = c["q_hat"]; exact = q["exact_var_own_colouring"]; tol = q["r3_tolerance"]; se = q["var_known_mean_se"]; diff = abs(q["var_known_mean"] - exact)
        g = bool(q["var_known_mean"] > tol) if q["structural_zero"] else bool(diff > R3_GROSS_SE * se + tol)
        if c["_exp"]["role"] == "core" and c["colouring"] == "fixed":
            reported.append((c["file"], g)); continue
        n3 += 1; z3 += int(q["structural_zero"])
        if g:
            gross.append(c["file"])
        if not q["structural_zero"]:
            lo, hi = q["var_boot_ci95"]; cov.append(lo <= exact <= hi)
    R3 = res["rules"]["R3"]
    for k, v in (("n_checks", n3), ("n_structural_zero", z3), ("n_gross", len(gross))):
        if R3[k] != v:
            mism.append(f"R3 {k}: own {v} vs results {R3[k]}")
    if sorted(x["cell"] for x in R3["gross_failures"]) != sorted(gross):
        mism.append("R3 gross set differs")
    if R3["coverage_95_diagnostic"] is not None:
        close(float(np.mean(cov)), R3["coverage_95_diagnostic"], 1e-12, "R3 coverage")
    if {x["cell"]: x["gross"] for x in R3["core_fixed_subset_reported"]} != dict(reported):
        mism.append("R3 core fixed subset differs")
    big = [c for c in CORE if c["colouring"] == "independent" and c["_exp"]["V"] >= R3_REDUCTION_V]
    red = [1 - c["identity_q"]["exact_ratio_formula"] for c in big]
    if big:
        if R3["reduction_below_1pct_for_V_ge_10000"] != all(r < R3_REDUCTION_BOUND for r in red):
            mism.append("R3 reduction statement differs")
        close(max(red), R3["max_reduction_V_ge_10000"], 1e-15, "R3 max reduction")
    chk["R3"] = {"n_checks": n3, "n_structural_zero": z3, "n_gross": len(gross), "coverage": float(np.mean(cov)) if cov else None, "n_core_fixed_reported": len(reported), "n_cells_V_ge_10000": len(big), "max_reduction": max(red) if red else None}
    # R4, R5 (own monotonicity), R4b
    ch4 = {}
    for c in CORE:
        if c["colouring"] == "independent":
            ch4.setdefault((c["_exp"]["name"], c["h"], c["gamma"], c["rule"]), []).append(c)
    own4 = {}
    for k, cs in ch4.items():
        cs = sorted(cs, key=lambda c: c["L"]); r = [c["population"]["rho_bar"] for c in cs]; s = [c["population"]["rho_bar_boot_se"] for c in cs]
        own4[k] = all(r[i + 1] >= r[i] - 2 * (s[i] + s[i + 1]) for i in range(len(r) - 1))
    res4 = {(x["chain"][0], int(x["chain"][1]), float(x["chain"][2]), x["chain"][3]): x["non_decreasing_within_tolerance"] for x in res["rules"]["R4"]["chains"]}
    own4raw = {k: v for k, v in own4.items() if k[3] == "raw"}
    if own4raw != res4:
        mism.append(f"R4 chain decisions differ: {sorted(set(own4raw.items()) ^ set(res4.items()))[:4]}")
    chk["R4"] = {"n_chains": len(own4raw), "n_non_decreasing": sum(own4raw.values()), "pass": bool(own4raw) and all(own4raw.values()), "by_rule": {r: {"n": sum(1 for k in own4 if k[3] == r), "n_non_decreasing": sum(v for k, v in own4.items() if k[3] == r)} for r in grid["rules"]}}
    if chk["R4"]["pass"] != res["rules"]["R4"]["pass"]:
        mism.append("R4 pass differs")
    ch5 = {}
    for c in CORE:
        if c["colouring"] == "independent" and c["rule"] == "raw":
            ch5.setdefault((c["_exp"]["name"], c["L"], c["gamma"]), []).append(c)
    own5 = {}
    for k, cs in ch5.items():
        cs = sorted(cs, key=lambda c: c["h"]); A = [c["population"]["A_q_between"] for c in cs]; s = [c["population"]["A_q_between_boot_se"] for c in cs]
        own5[k] = all(A[i + 1] <= A[i] + 2 * (s[i] + s[i + 1]) for i in range(len(A) - 1))
    res5 = {(x["chain"][0], int(x["chain"][1]), float(x["chain"][2])): x["non_increasing_within_tolerance"] for x in res["rules"]["R5"]["chains"]}
    if own5 != res5:
        mism.append(f"R5 chain decisions differ: {sorted(set(own5.items()) ^ set(res5.items()))[:4]}")
    chk["R5"] = {"n_chains": len(own5), "n_non_increasing": sum(own5.values()), "pass": bool(own5) and all(own5.values())}
    if chk["R5"]["pass"] != res["rules"]["R5"]["pass"]:
        mism.append("R5 pass differs")
    sat = [c for c in LIVE if c["law"]["kind"] == "support" and c["rule"] == "distinct" and c["h"] == 0]
    rep = None
    if sat:
        Lmax = max(c["L"] for c in sat); oks = []
        for c in sat:
            if c["L"] != Lmax:
                continue
            s = c["law"]["s_support"]; Vv = c["law"]["V"]; g = math.floor(c["gamma"] * Vv) / Vv; gam = c["gamma"]
            vq = g * (1 - g) * (Vv - s) / (s * (Vv - 1)) if c["colouring"] == "fixed" else g * (1 - g) / s
            lim = s * vq / (gam * (1 - gam)); oks.append(abs(c["population"]["rho_bar"] - lim) <= 3 * c["population"]["rho_bar_boot_se"] + 1e-9)
        rep = all(oks)
        if rep != res["rules"]["R4b_saturation"]["reproduced"]:
            mism.append("R4b differs")
    chk["R4b"] = {"reproduced": rep, "n_cells": len(sat)}
    if mism:
        (OUTDIR / "checks_FAILED.json").write_text(json.dumps({"mismatches": mism, "checks": chk}, indent=1, default=str))
        raise AssertionError(f"{len(mism)} mismatch(es) between the builder's re-computation and results.json; first: {mism[:5]}")
    (OUTDIR / "checks.json").write_text(json.dumps({"mismatches": [], "checks": chk}, indent=1, default=str))
    return chk


CHK = independent_checks()

# ------------------------------------------------------------------ tables
T = {}; R = res["rules"]
R1, R2, R3, R4, R4b, R5 = R["R1"], R["R2"], R["R3"], R["R4"], R["R4b_saturation"], R["R5"]
reg("n_cells", res["n_cells"]); reg("n_live", res["n_live"]); reg("n_markers", res["n_degenerate_markers"]); reg("n_no_detection", res["n_no_detection"])
reg("n_core_laws", len(CORE_LAWS)); reg("n_ill_laws", len(ILL_LAWS)); reg("K", grid["K"]); reg("K_fixed", grid["K_fixed_core"]); reg("N", f"{grid['N']:,}")
for k in ("n_candidates", "n_eligible", "n_resolved", "n_consistent", "n_inconsistent", "n_unresolved"):
    reg(f"r1_{k[2:]}", R1[k])
reg("r1_share", pct(R1["share_consistent"])); reg("r1_verdict", "PASS" if R1["pass"] else "FAIL"); reg("r1_min_resolved", R1_MIN_RESOLVED)
rat = [r["ratio"] for r in R1["rows"] if r["status"] != "unresolved"]
reg("r1_ratio_min", fnum(min(rat)) if rat else "—"); reg("r1_ratio_max", fnum(max(rat)) if rat else "—"); reg("r1_ratio_median", fnum(float(np.median(rat))) if rat else "—")
rat_all = [r["ratio"] for r in R1["rows"]]
reg("r1_ratio_q10", fnum(float(np.quantile(rat_all, 0.1))) if rat_all else "—"); reg("r1_ratio_q90", fnum(float(np.quantile(rat_all, 0.9))) if rat_all else "—")
reg("r2_checks", R2["n_checks"]); reg("r2_zeros", R2["n_structural_zero"]); reg("r2_flagged", R2["n_flagged"]); reg("r2_min_pbound", fnum(R2["min_pbound"]) if R2["min_pbound"] is not None else "—")
reg("r2_union", fnum(R2["false_audit_union_bound"])); reg("r2_verdict", "PASS" if R2["pass"] else "AUDIT FLAG"); q2 = R2["dev_over_se_normal_quantiles"] or {}
reg("r2_dev_median", fnum(q2.get("0.5"))); reg("r2_dev_q90", fnum(q2.get("0.9"))); reg("r2_dev_q99", fnum(q2.get("0.99"))); reg("r2_dev_max", fnum(q2.get("1.0"))); reg("r2_zero_se", R2["n_zero_se_normal"])
reg("r3_checks", R3["n_checks"]); reg("r3_zeros", R3["n_structural_zero"]); reg("r3_gross", R3["n_gross"]); reg("r3_verdict", "PASS" if R3["pass"] else "FAIL")
reg("r3_coverage", pct(R3["coverage_95_diagnostic"]) if R3["coverage_95_diagnostic"] is not None else "—"); reg("r3_n_coverage", R3["n_coverage_checks"]); q3 = R3["dev_over_se_quantiles"] or {}
reg("r3_dev_median", fnum(q3.get("0.5"))); reg("r3_dev_q90", fnum(q3.get("0.9"))); reg("r3_dev_q99", fnum(q3.get("0.99"))); reg("r3_dev_max", fnum(q3.get("1.0"))); reg("r3_constancy", R3["n_observed_sample_constancy"])
mat = [abs(c["q_hat"]["var_known_mean"] - c["q_hat"]["exact_var_own_colouring"]) / c["q_hat"]["var_known_mean_se"] for c in LIVE
       if not (c["_exp"]["role"] == "core" and c["colouring"] == "fixed") and not c["q_hat"]["structural_zero"] and c["q_hat"]["var_known_mean_se"] > c["q_hat"]["r3_tolerance"]]
reg("r3_n_material", len(mat)); reg("r3_dev_median_material", fnum(float(np.median(mat))) if mat else "—"); reg("r3_dev_q99_material", fnum(float(np.quantile(mat, 0.99))) if mat else "—"); reg("r3_dev_max_material", fnum(max(mat)) if mat else "—")
reg("r3_n_roundoff_se", sum(1 for c in LIVE if not (c["_exp"]["role"] == "core" and c["colouring"] == "fixed") and not c["q_hat"]["structural_zero"] and c["q_hat"]["var_known_mean_se"] <= c["q_hat"]["r3_tolerance"]))
reg("r3_n_big", R3["n_cells_V_ge_10000"]); reg("r3_max_reduction", pct(R3["max_reduction_V_ge_10000"], 3) if R3["max_reduction_V_ge_10000"] is not None else "—")
reg("r3_reduction_verdict", {True: "confirmed", False: "refuted", None: "—"}[R3["reduction_below_1pct_for_V_ge_10000"]])
reg("r4_chains", R4["n_chains"]); reg("r4_share", pct(R4["share_non_decreasing"]) if R4["n_chains"] else "—"); reg("r4_verdict", "PASS" if R4["pass"] else "FAIL")
reg("r4_failing", ", ".join(f"{law_label(x['chain'][0], True)} h={x['chain'][1]} γ={x['chain'][2]}" for x in R4["chains"] if not x["non_decreasing_within_tolerance"]) or "none")
reg("r4b_n", R4b["n"]); reg("r4b_verdict", {True: "reproduced", False: "not reproduced", None: "—"}[R4b["reproduced"]])
reg("r5_chains", R5["n_chains"]); reg("r5_share", pct(R5["share_non_increasing"]) if R5["n_chains"] else "—"); reg("r5_verdict", "PASS" if R5["pass"] else "FAIL")
reg("r5_failing", ", ".join(f"{law_label(x['chain'][0], True)} L={x['chain'][1]} γ={x['chain'][2]}" for x in R5["chains"] if not x["non_increasing_within_tolerance"]) or "none")
reg("r4_distinct_non_decreasing", f"{CHK['R4']['by_rule']['distinct']['n_non_decreasing']} of {CHK['R4']['by_rule']['distinct']['n']}")
reg("r4_first_non_decreasing", f"{CHK['R4']['by_rule']['first']['n_non_decreasing']} of {CHK['R4']['by_rule']['first']['n']}")

T["rules"] = md_table(["Rule (protocol §9)", "Pre-registered criterion", "Observed", "Verdict"], [
    ["R1 adequacy of the common-factor predictor (primary; α = 0.01, γ = 0.5, raw and distinct rules, independent colouring, core laws)", f"≥ {R1_MIN_RESOLVED} resolved cells and ≥ {pct(R1_PASS_SHARE, 0)} of the resolved cells consistent (ratio interval inside [2/3, 3/2])",
     f"candidates {R1['n_candidates']}; eligible {R1['n_eligible']} (mean M ≥ {R1_MIN_M}, theory share ≥ {R1_MIN_THEORY_SHARE}); resolved {R1['n_resolved']}; consistent {R1['n_consistent']}; inconsistent {R1['n_inconsistent']}; unresolved {R1['n_unresolved']}; share consistent {pct(R1['share_consistent'])}", f"**{VALUES['r1_verdict']}**"],
    ["R2 simulator validity (independent colouring, distinct rule; every α, every K)", f"no check with a two-sided KL-Chernoff bound below {R2_PBOUND:g} (per-check false audit ≤ {R2_PBOUND:g}; union bound over the checks)",
     f"{R2['n_checks']} checks ({R2['n_structural_zero']} structural zeros counted separately); flagged {R2['n_flagged']}; smallest bound {VALUES['r2_min_pbound']}; union bound {VALUES['r2_union']}; normal |dev|/SE median {VALUES['r2_dev_median']}, 99% {VALUES['r2_dev_q99']}, max {VALUES['r2_dev_max']} (diagnostic)", f"**{VALUES['r2_verdict']}**"],
    ["R3 exact identities (every live cell, both colourings; the core fixed subset reported, not decided on)", f"no gross failure: |s₀² − σ²_exact| ≤ {R3_GROSS_SE:g}·SE + τ; structural zeros ≤ τ",
     f"{R3['n_checks']} checks ({R3['n_structural_zero']} structural zeros); gross failures {R3['n_gross']}; |dev|/SE median {VALUES['r3_dev_median']}, 99% {VALUES['r3_dev_q99']}, max {VALUES['r3_dev_max']}; nominal-95% coverage {VALUES['r3_coverage']} of {R3['n_coverage_checks']} (diagnostic)", f"**{VALUES['r3_verdict']}**"],
    ["R3 statement: fixed-size reduction below 1% for V ≥ 10,000 (core cells, exact ratio at the realised weights)", "every core cell with V ≥ 10,000 has (I − Var)/I < 1%", f"{R3['n_cells_V_ge_10000']} cells; largest reduction {VALUES['r3_max_reduction']}", f"**{VALUES['r3_reduction_verdict']}**"],
    ["R4 H-length under the raw rule (core chains, independent colouring)", "ρ̄ non-decreasing in L within 2(se_L + se_L′) in every (law, h, γ) chain", f"{R4['n_chains']} chains; non-decreasing {VALUES['r4_share']}; failing: {VALUES['r4_failing']}", f"**{VALUES['r4_verdict']}**"],
    ["R4b saturation (support control, distinct rule, h = 0, longest L)", "ρ̄ within 3 text-bootstrap SEs of the analytic limit, both colourings and both γ", f"{R4b['n']} cells at the longest L", f"**{VALUES['r4b_verdict']}**"],
    ["R5 H-width under the raw rule (core chains, independent colouring)", "Ã non-increasing in h within 2(se_h + se_h+1) in every (law, L, γ) chain", f"{R5['n_chains']} chains; non-increasing {VALUES['r5_share']}; failing: {VALUES['r5_failing']}", f"**{VALUES['r5_verdict']}**"]])

# R1 by law and rule
rows = []
for law in CORE_LAWS:
    for rule in R1_RULES:
        rs = [r for r in R1["rows"] if r["law"] == law and r["rule"] == rule]
        if not rs:
            continue
        resolved = [r for r in rs if r["status"] != "unresolved"]; rr = [r["ratio"] for r in resolved]
        rows.append([law_label(law), rule, len(rs), len(resolved), sum(1 for r in resolved if r["status"] == "consistent"), sum(1 for r in resolved if r["status"] == "inconsistent"), len(rs) - len(resolved),
                     f"{fnum(min(rr))}–{fnum(max(rr))}" if rr else "—", fnum(float(np.median(rr))) if rr else "—",
                     f"h = {min(r['h'] for r in rs)}–{max(r['h'] for r in rs)}"])
T["r1_by_law"] = md_table(["Law", "Rule", "Eligible", "Resolved", "Consistent", "Inconsistent", "Unresolved", "Ratio range (resolved)", "Median ratio", "Widths present"], rows)
# the eligible set by h and L (which cells the rule could judge)
elig_hl = {}
for r in R1["rows"]:
    elig_hl.setdefault((r["h"], r["L"]), []).append(r["status"])
rows = []
for h in grid["h"]:
    rows.append([f"h = {h}"] + [(f"{sum(1 for s in elig_hl.get((h, L), []) if s == 'consistent')}/{sum(1 for s in elig_hl.get((h, L), []) if s != 'unresolved')}/{len(elig_hl.get((h, L), []))}" if (h, L) in elig_hl else "—") for L in grid["L"]])
T["r1_by_hL"] = md_table(["Width", *[f"L = {L}" for L in grid["L"]]], rows) + "\n\nEach cell: consistent / resolved / eligible over the laws and the two rules (an eligible cell needs mean M ≥ 30 and a theory share ≥ 0.75; cells absent from the eligible set are mostly short, wide-context cells where the finite-text term dominates)."
# inconsistent and unresolved cells with the diagnostics the protocol asks for (R04 round 1, F5: both pairwise subsamples, colouring and gamma)
BLOCK_ALPHA = {"primary": (R1_ALPHA, "pred_first_order"), "alpha_0.05": ("0.05", "pred_first_order"), "alpha_0.001": ("0.001", "pred_first_order"), "first_rule": (R1_ALPHA, "pred_first_order"),
               "gamma_extra": (R1_ALPHA, "pred_first_order"), "unit_sigma_predictor": (R1_ALPHA, "pred_unit_sigma"), "illustration": (R1_ALPHA, "pred_first_order"), "fixed_colouring": (R1_ALPHA, "pred_first_order")}
BLOCKS = {"primary": R1, **R["R1_secondary"]}
BLOCK_LABEL = {"primary": "primary (α = 0.01, γ = 0.5, raw and distinct)", "alpha_0.05": "α = 0.05 (same cells)", "alpha_0.001": "α = 0.001 (same cells)", "first_rule": "the first rule (α = 0.01)", "gamma_extra": "γ = 0.25 cells (raw and distinct)", "unit_sigma_predictor": "the unit-σ predictor (σ = 1)",
               "illustration": "illustration laws (independent colouring)", "fixed_colouring": "the fixed colouring (core subset and illustration laws)"}


def diag_row(block, r):
    """One diagnostic row for a non-consistent occurrence (block, cell) built from the cell file: the block's alpha and predictor, both pairwise subsamples."""
    alpha, pk = BLOCK_ALPHA[block]; c = cells[r["cell"]]; lv = c["levels"][alpha]; p = lv[pk]; sd = lv["sd_obs_conditional"]; sp = p["sd_cond"]
    ratio = sd / sp if sp > 0 else float("nan"); lo, hi = [(b / sp if sp > 0 else float("nan")) for b in lv["sd_obs_boot_ci95"]]
    pw = lv.get("pred_pairwise_gaussian") or {}; het = c.get("covariance_heterogeneity") or {}; q = het.get("pair_corr_quantiles") or {}
    r1 = sd / pw["sd_cond"] if pw.get("sd_cond", 0) > 0 else float("nan"); r2 = sd / pw["sd_cond_replicate"] if pw.get("sd_cond_replicate") else float("nan")
    diff = (100 * pw["subsample_sd_difference"]) if pw.get("subsample_sd_difference") is not None else float("nan")
    return {"block": block, "status": r["status"], "alpha": alpha, "law": law_label(c["_exp"]["name"], True), "rule": c["rule"], "h": c["h"], "L": c["L"], "colouring": c["colouring"], "gamma": c["gamma"],
            "ratio": f"{fnum(ratio)} {ci(lo, hi)}", "sd_obs": fnum(100 * sd), "sd_pred": fnum(100 * sp), "sigd": fnum(c["population"]["sd_zshift_pop"]), "M": fnum(c["mean_M"], 0), "theory": fnum(p["theory_share"]),
            "sigma2": f"{fnum(p['sigma2'])} / {fnum(c['population']['sigma_model2'])} / {fnum(c['z_var_within_key']['mean_over_keys'])}", "level": f"{pp(lv['key_mean_level'])} / {pp(p['mean_level'])}",
            "pair": f"{fnum(r1)} / {fnum(r2)}", "pair_diff": fnum(diff), "cv": fnum(het.get("pair_cov_cv")), "corr": f"{fnum(q.get('0.5'))} / {fnum(q.get('0.9'))} / {fnum(q.get('0.99'))} / {fnum(het.get('pair_corr_max'))}", "cell": r["cell"]}


DIAG_HEAD = ["Law", "Rule", "h", "L", "Colouring", "γ", "α", "Status", "Ratio [95% CI]", "SD obs (pp)", "SD pred (pp)", "σ_δ = √ρ̄", "Mean M", "Theory share", "σ² predictor / identities / observed", "Key-mean level obs / pred (%)",
             "Pairwise ratio, subsample 1 / 2", "Pairwise subsampling difference (pp)", "Pair-cov CV", "Pair-corr q50 / q90 / q99 / max"]


def diag_cells(d):
    return [d["law"], d["rule"], d["h"], d["L"], d["colouring"], d["gamma"], d["alpha"], d["status"], d["ratio"], d["sd_obs"], d["sd_pred"], d["sigd"], d["M"], d["theory"], d["sigma2"], d["level"], d["pair"], d["pair_diff"], d["cv"], d["corr"]]


prim = sorted([diag_row("primary", r) for r in R1["inconsistent_cells"] + R1["unresolved_cells"]], key=lambda d: (d["status"], d["law"], d["rule"], d["h"], d["L"]))
rows = [diag_cells(d) for d in prim]
T["r1_failures"] = md_table(DIAG_HEAD, rows) if rows else "_No inconsistent or unresolved eligible cell._"
# the complete supplement: every non-consistent occurrence of every block, with the other blocks in which the same cell is non-consistent
occ = {}
for block, blk in BLOCKS.items():
    for r in blk["inconsistent_cells"] + blk["unresolved_cells"]:
        occ.setdefault(r["cell"], []).append(block)
sup = []
for block, blk in BLOCKS.items():
    for r in sorted(blk["inconsistent_cells"] + blk["unresolved_cells"], key=lambda r: (r["status"], r["cell"])):
        d = diag_row(block, r); sup.append([BLOCK_LABEL.get(block, "primary (α = 0.01, γ = 0.5, raw and distinct)")] + diag_cells(d) + [", ".join(b for b in occ[r["cell"]] if b != block) or "—"])
(OUTDIR / "tables_r1_diagnostics_full.md").write_text("# Study 1 — every inconsistent or unresolved occurrence of every R1 block, with the protocol's diagnostics\n\nGenerated by `research/study1/s1_report.py` from the cell files (the block's α and predictor; both pairwise subsamples; the same cell may appear under several blocks, listed in the last column).\n\n" +
                                                      md_table(["Block"] + DIAG_HEAD + ["Also non-consistent in"], sup) + "\n")
reg("n_diag_rows", len(sup)); reg("n_diag_cells", len(occ)); reg("n_sec_unresolved_total", sum(b["n_unresolved"] for b in R["R1_secondary"].values())); reg("n_sec_inconsistent_total", sum(b["n_inconsistent"] for b in R["R1_secondary"].values()))
reg("r1_n_failure_rows", len(rows))
# secondary blocks
rows = [["**primary: α = 0.01, γ = 0.5, raw and distinct**", R1["n_candidates"], R1["n_eligible"], R1["n_resolved"], R1["n_consistent"], R1["n_inconsistent"], R1["n_unresolved"], pct(R1["share_consistent"])]]
for name, blk in R["R1_secondary"].items():
    rows.append([BLOCK_LABEL[name], blk["n_candidates"], blk["n_eligible"], blk["n_resolved"], blk["n_consistent"], blk["n_inconsistent"], blk["n_unresolved"], pct(blk["share_consistent"])])
    for k in ("eligible", "resolved", "consistent", "inconsistent", "unresolved"):
        reg(f"sec_{name}_{k}", blk[f"n_{k}"])
    reg(f"sec_{name}_share", pct(blk["share_consistent"]))
    rr = [r["ratio"] for r in blk["rows"] if r["status"] != "unresolved"]
    reg(f"sec_{name}_ratio_median", fnum(float(np.median(rr))) if rr else "—"); reg(f"sec_{name}_ratio_min", fnum(min(rr)) if rr else "—"); reg(f"sec_{name}_ratio_max", fnum(max(rr)) if rr else "—")
T["r1_secondary"] = md_table(["Block (descriptive; the same statistic)", "Candidates", "Eligible", "Resolved", "Consistent", "Inconsistent", "Unresolved", "Share consistent"], rows)
# the pairwise predictor beside the common-factor one, on the eligible primary cells
pr = [r for r in R1["rows"] if np.isfinite(r["ratio_pairwise"])]
reg("pair_n", len(pr)); reg("pair_ratio_median", fnum(float(np.median([r["ratio_pairwise"] for r in pr]))) if pr else "—")
reg("pair_ratio_q10", fnum(float(np.quantile([r["ratio_pairwise"] for r in pr], 0.1))) if pr else "—"); reg("pair_ratio_q90", fnum(float(np.quantile([r["ratio_pairwise"] for r in pr], 0.9))) if pr else "—")
reg("pair_in_band", sum(1 for r in pr if R1_BAND[0] <= r["ratio_pairwise"] <= R1_BAND[1])); reg("cf_in_band_point", sum(1 for r in R1["rows"] if R1_BAND[0] <= r["ratio"] <= R1_BAND[1]))
het_cv = [r["pair_cov_cv"] for r in R1["rows"] if r["pair_cov_cv"] is not None and np.isfinite(r["pair_cov_cv"])]
reg("het_cv_median", fnum(float(np.median(het_cv))) if het_cv else "—"); reg("het_cv_max", fnum(max(het_cv)) if het_cv else "—")
# the population diagnostic
pdg = R["population_diagnostic"]; ok = [x for x in pdg if x["var_pop_mixture"] > 0]
pr_ratio = [x["var_pop_twoway"] / x["var_pop_mixture"] for x in ok]; within = [abs(x["var_pop_twoway"] - x["var_pop_mixture"]) <= 2 * x["se"] for x in ok]
reg("pop_n", len(ok)); reg("pop_ratio_median", fnum(float(np.median(pr_ratio))) if pr_ratio else "—"); reg("pop_ratio_q10", fnum(float(np.quantile(pr_ratio, 0.1))) if pr_ratio else "—"); reg("pop_ratio_q90", fnum(float(np.quantile(pr_ratio, 0.9))) if pr_ratio else "—")
reg("pop_within_2se", f"{sum(within)} of {len(within)}" if within else "—"); reg("pop_negative", sum(1 for x in pdg if x["var_pop_twoway"] < 0))
# R2 / R3 detail and the core fixed subset
fx_rows = []; fx_detail = {}
for x in sorted(R3["core_fixed_subset_reported"], key=lambda x: x["cell"]):
    c = cells[x["cell"]]; ind = BY.get((c["_exp"]["name"], c["h"], "independent", c["gamma"], c["L"], c["rule"]))
    obs_ratio = se_ratio = float("nan")
    if ind is not None and ind["q_hat"]["var_known_mean"] > 0 and x["observed_var_known_mean"] > 0:
        obs_ratio = x["observed_var_known_mean"] / ind["q_hat"]["var_known_mean"]
        se_ratio = obs_ratio * math.sqrt((x["se"] / x["observed_var_known_mean"]) ** 2 + (ind["q_hat"]["var_known_mean_se"] / ind["q_hat"]["var_known_mean"]) ** 2)
    fx_detail[(c["_exp"]["name"], c["h"], c["L"], c["rule"], c["gamma"])] = (c["identity_q"]["exact_ratio_formula"], obs_ratio, se_ratio, x)
    fx_rows.append([law_label(c["_exp"]["name"], True), c["h"], c["L"], c["rule"], c["gamma"], fnum(x["observed_var_known_mean"]), fnum(x["exact"]), fnum(x["dev_over_se"]), "yes" if x["ci95_covers"] else ("—" if x["ci95_covers"] is None else "no"),
                    fnum(c["identity_q"]["exact_ratio_formula"]), fnum(c["identity_q"]["C_cond"]), f"{fnum(obs_ratio)} ± {fnum(se_ratio)}"])
(OUTDIR / "tables_fixed_subset_full.md").write_text("# Study 1 — the core fixed subset in full (K = 200; reported, not decided on)\n\nGenerated by `research/study1/s1_report.py`.\n\n" +
    md_table(["Law", "h", "L", "Rule", "γ", "Fixed: s₀² observed", "Fixed: σ²_exact", "|dev|/SE (bootstrap)", "95% CI covers", "Exact ratio fixed/indep (V − 1/C_cond)/(V − 1)", "C_cond", "Observed ratio fixed/indep ± SE"], fx_rows) + "\n")
rows = []
for law in CORE_LAWS:
    for h in sorted({k[1] for k in fx_detail}):
        for L in sorted({k[2] for k in fx_detail}):
            vals = []
            for rule in grid["rules"]:
                d = fx_detail.get((law, h, L, rule, G0)); vals.append(f"{fnum(d[0])} → {fnum(d[1])} ± {fnum(d[2])}" if d else "—")
            if any(v != "—" for v in vals):
                rows.append([law_label(law, True), h, L] + vals)
T["fixed_subset"] = md_table(["Law", "h", "L", *[f"{r} rule: exact → observed ± SE" for r in grid["rules"]]], rows) + "\n\nThe exact ratio Var_fixed/Var_indep = (V − 1/C_cond)/(V − 1) at the realised q-weights (the same for both γ), then the observed ratio of the two known-mean variance estimates (fixed, K = 200, over independent, K = 500) with its propagated SE, at γ = 0.5. Every cell, both γ and the R3 checks of the fixed cells are in `outputs/study1_v0.3/report/tables_fixed_subset_full.md`."
reg("fixed_subset_n", len(fx_rows)); fr = [c["identity_q"]["exact_ratio_formula"] for c in CORE if c["colouring"] == "fixed"]
reg("fixed_subset_ratio_min", fnum(min(fr)) if fr else "—"); reg("fixed_subset_ratio_max", fnum(max(fr)) if fr else "—")
reg("fixed_subset_n_cover", sum(1 for x in R3["core_fixed_subset_reported"] if x["ci95_covers"])); reg("fixed_subset_n_cover_checks", sum(1 for x in R3["core_fixed_subset_reported"] if x["ci95_covers"] is not None))
reg("fixed_subset_max_dev", fnum(max(x["dev_over_se"] for x in R3["core_fixed_subset_reported"] if np.isfinite(x["dev_over_se"])))); reg("fixed_subset_n_gross", sum(1 for x in R3["core_fixed_subset_reported"] if x["gross"]))
def fx_example(law, h, L, rule):
    d = fx_detail.get((law, h, L, rule, G0)); return (fnum(d[0]), fnum(d[1]), fnum(d[2])) if d else ("—", "—", "—")
e = fx_example("zipf_V1000_s1.0", 0, Lw, "distinct"); reg("fx_z1000_exact", e[0]); reg("fx_z1000_obs", e[1]); reg("fx_z1000_se", e[2])
e = fx_example("zipf_V10000_s1.0", 0, Lw, "distinct"); reg("fx_z10000_exact", e[0]); reg("fx_z10000_obs", e[1]); reg("fx_z10000_se", e[2])
gross_rows = [[x["cell"], x["colouring"], fnum(x["observed_var_known_mean"]), fnum(x["exact"]), fnum(x["se"]), fnum(x["dev_over_se"])] for x in R3["gross_failures"]]
T["r3_gross"] = md_table(["Cell", "Colouring", "s₀² observed", "σ²_exact", "SE", "|dev|/SE"], gross_rows) if gross_rows else "_No gross failure._"
flag_rows = [[x["cell"], x["alpha"], x["K"], pp(x["key_mean"]), pp(x["exact"]), fnum(x["kl_pbound"])] for x in R2["flagged"]]
T["r2_flagged"] = md_table(["Cell", "α", "K", "Key-mean level (%)", "Exact (%)", "Two-sided KL bound"], flag_rows) if flag_rows else "_No flagged check._"
# curves against L (the h = 1 slice in the body; every width in the full file)
curves = res["descriptive"]["level_sd_curves_by_rule"]


def curve_rows(h_sel, rules):
    rows = []
    for law in CORE_LAWS:
        for rule in rules:
            for e in curves.get(rule, []):
                if e["chain"][0] == law and int(e["chain"][1]) == h_sel and float(e["chain"][2]) == G0:
                    rows.append([law_label(law, True), rule] + [f"{fnum(o)} / {fnum(p)}" for o, p in zip(e["level_sd_obs_pp"], e["level_sd_pred_pp"])])
    return rows


T["curves_h1"] = md_table(["Law", "Rule", *[f"L = {L}" for L in grid["L"]]], curve_rows(1, grid["rules"])) + "\n\nEach cell: observed / predicted across-key SD of the per-key level at α = 1% (percentage points), γ = 0.5, independent colouring, h = 1."
rows = []
for law in CORE_LAWS:
    for rule in grid["rules"]:
        for e in curves.get(rule, []):
            if e["chain"][0] == law and int(e["chain"][1]) == 1 and float(e["chain"][2]) == G0:
                rows.append([law_label(law, True), rule] + [f"{fnum(r)} ({fnum(m)})" for r, m in zip(e["rho_bar"], e["mean_M"])])
T["rho_h1"] = md_table(["Law", "Rule", *[f"L = {L}" for L in grid["L"]]], rows) + "\n\nEach cell: ρ̄ (the population across-key variance of the mean z-shift, without the finite-text floor) with the mean number M of scored positions in parentheses; h = 1, γ = 0.5."
full = ["# Study 1 — the complete dispersion curves (every core law, width, rule; γ = 0.5, independent colouring; α = 0.01)", "", "Generated by `research/study1/s1_report.py` from `results.json`. Each cell: observed / predicted across-key SD of the per-key level (pp); then ρ̄ (mean M)."]
for h in grid["h"]:
    full += ["", f"## h = {h}", "", md_table(["Law", "Rule", *[f"L = {L}" for L in grid["L"]]], curve_rows(h, grid["rules"]))]
    rows = []
    for law in CORE_LAWS:
        for rule in grid["rules"]:
            for e in curves.get(rule, []):
                if e["chain"][0] == law and int(e["chain"][1]) == h and float(e["chain"][2]) == G0:
                    rows.append([law_label(law, True), rule] + [f"{fnum(r)} ({fnum(m)})" for r, m in zip(e["rho_bar"], e["mean_M"])])
    full += ["", md_table(["Law", "Rule", *[f"ρ̄ (M) at L = {L}" for L in grid["L"]]], rows)]
(OUTDIR / "tables_curves_full.md").write_text("\n".join(full) + "\n")
# width curves at the longest core length
rows = []
for law in CORE_LAWS:
    for x in R5["chains"]:
        if x["chain"][0] == law and int(x["chain"][1]) == Lw and float(x["chain"][2]) == G0:
            rows.append([law_label(law, True)] + [f"{fnum(a)}" + (f" ({fnum(c)})" if c is not None else "") for a, c in zip(x["A_between"], x["C_h_analytic"])])
T["width_A"] = md_table(["Law", *[f"h = {h}" for h in grid["h"]]], rows) + f"\n\nÃ(h): the between-text collision of the retained-tuple weights under the raw rule at L = {Lw:,}, γ = 0.5 (the i.i.d. laws' analytic C_h = C_0^(h+1) in parentheses)."
rows = []
for law in CORE_LAWS:
    for rule in ("raw", "distinct"):
        for e in curves.get(rule, []):
            if e["chain"][0] == law and float(e["chain"][2]) == G0 and Lw in e["L"]:
                pass
        vals = []
        for h in grid["h"]:
            c = BY.get((law, h, "independent", G0, Lw, rule)); vals.append(f"{pp(c['levels'][R1_ALPHA]['sd_obs_conditional'])} (ρ̄ {fnum(c['population']['rho_bar'])})" if c and "levels" in c else "—")
        rows.append([law_label(law, True), rule] + vals)
T["width_sd"] = md_table(["Law", "Rule", *[f"h = {h}" for h in grid["h"]]], rows) + f"\n\nObserved across-key SD of the per-key level at α = 1% (pp) with ρ̄ in parentheses, L = {Lw:,}, γ = 0.5, independent colouring."
# R4b support control
rows = [[r["colouring"], r["gamma"], r["L"], fnum(r["mean_M"]), f"{fnum(r['rho_bar'])} ± {fnum(r['se'])}", fnum(r["limit_rho"]), fnum(r["q_identity_at_realised_weights"]), fnum(r["limit_q"])] for r in R4b["rows"]]
T["support"] = md_table(["Colouring", "γ", "L", "Mean M", "ρ̄ ± text-bootstrap SE", "Analytic limit ρ", "q-identity at the realised weights", "Analytic limit q"], rows) if rows else "_No support-control cell in this inventory._"
# F1 (R04 round 1): R4b's locked analyzer applies 3 SE + 1e-9 where the protocol's text says 3 SE; the literal comparison is reported beside it
rows = []; lit_pass = 0
for x in sorted(R4b["rows"], key=lambda x: (x["colouring"], x["gamma"])):
    if x["L"] != max(r["L"] for r in R4b["rows"]):
        continue
    resid = abs(x["rho_bar"] - x["limit_rho"]); lit = resid <= 3 * x["se"]; imp = resid <= 3 * x["se"] + 1e-9; lit_pass += int(lit)
    rows.append([x["colouring"], x["gamma"], x["L"], fnum(x["rho_bar"], 6), fnum(x["limit_rho"], 6), f"{resid:.2e}", f"{x['se']:.2e}", f"{3 * x['se']:.2e}", "yes" if lit else "no", "yes" if imp else "no"])
T["r4b_tolerance"] = md_table(["Colouring", "γ", "L", "ρ̄", "Analytic limit", "|residual|", "Text-bootstrap SE", "3·SE", "Within 3·SE (the protocol's text)", "Within 3·SE + 10⁻⁹ (the locked analyzer)"], rows)
reg("r4b_literal_pass_n", lit_pass); reg("r4b_tol_rows", len(rows))
reg("r4b_max_residual", f"{max(abs(x['rho_bar'] - x['limit_rho']) for x in R4b['rows'] if x['L'] == max(r['L'] for r in R4b['rows'])):.1e}" if R4b["rows"] else "—")
reg("r4b_max_3se", f"{max(3 * x['se'] for x in R4b['rows'] if x['L'] == max(r['L'] for r in R4b['rows'])):.1e}" if R4b["rows"] else "—")
# the deployer's view: per-key quantiles
rows = []
for law in CORE_LAWS:
    for rule in ("raw", "distinct"):
        for L in (256, Lw):
            c = BY.get((law, 1, "independent", G0, L, rule))
            if c and "levels" in c:
                lv = c["levels"][R1_ALPHA]
                rows.append([law_label(law, True), rule, L, fnum(c["mean_M"]), pp(lv["key_mean_level"]), pp(lv["quantiles"]["0.5"]), pp(lv["quantiles"]["0.95"]), pp(lv["quantiles"]["0.99"]), pp(lv["max_key"]), pct(lv["share_keys_above_2alpha"]), pct(lv["share_keys_above_5alpha"]), f"{pp(lv['sd_obs_conditional'])} {ci(*[100 * b for b in lv['sd_obs_boot_ci95']])}"])
T["deployer"] = md_table(["Law", "Rule", "L", "Mean M", "Key-mean (%)", "Median key (%)", "95% key (%)", "99% key (%)", "Worst sampled key (%)", "Keys > 2α", "Keys > 5α", "SD of the level (pp) [key-bootstrap 95% CI]"], rows) + f"\n\nPer-key false-positive levels at α = 1% over the K = {grid['K']} sampled production keys on the N = {grid['N']:,} realised texts of each law, h = 1, γ = 0.5, independent colouring (the nominal level is 1.00%). The quantiles, the worst sampled key and the shares are empirical summaries of the {grid['K']} sampled keys on these fixed texts; the only uncertainty computed for them is the key-bootstrap interval of the SD (last column), conditional on the texts. No crossed key-by-text uncertainty for the quantiles or for the worst key is available from the saved statistics (gate constraint 12), so the worst sampled key is reported as a sample extreme and not as a population extreme."
# worst-case summaries across all core cells at alpha = 0.01
wk = [(c["levels"][R1_ALPHA]["max_key"], c["levels"][R1_ALPHA]["share_keys_above_2alpha"], c) for c in CORE if c["colouring"] == "independent" and c["gamma"] == G0]
if wk:
    m = max(wk, key=lambda t: t[0]); reg("worst_key_level", pct(m[0])); reg("worst_key_cell", f"{law_label(m[2]['_exp']['name'], True)}, {m[2]['rule']} rule, h = {m[2]['h']}, L = {m[2]['L']}")
    reg("max_share_2alpha", pct(max(t[1] for t in wk))); reg("n_core_cells_any_key_above_2alpha", sum(1 for t in wk if t[1] > 0)); reg("n_core_indep_g05", len(wk))
    md = [c["levels"][R1_ALPHA]["share_keys_above_2alpha"] for _, _, c in wk if c["rule"] == "distinct" and c["L"] == Lw]; rw = [c["levels"][R1_ALPHA]["share_keys_above_2alpha"] for _, _, c in wk if c["rule"] == "raw" and c["L"] == Lw]
    reg("share_2alpha_distinct_Lmax_range", f"{pct(min(md))}–{pct(max(md))}" if md else "—"); reg("share_2alpha_raw_Lmax_range", f"{pct(min(rw))}–{pct(max(rw))}" if rw else "—")
# integrity
integ = res["descriptive"]["integrity"]
reg("n_M0_cells", len(integ["cells_with_M0_texts"])); reg("n_predictor_flags", len(integ["predictor_flags"]))
tt = integ["two_token_fixed_variances"]
reg("twotoken_fixed_h0", fnum(next((v for k, v in tt.items() if "__h0__" in k), float("nan")))); reg("twotoken_fixed_h1", fnum(next((v for k, v in tt.items() if "__h1__" in k), float("nan"))))
first_h0 = [c for c in LIVE if c["rule"] == "first" and c["h"] == 0]
reg("n_first_h0_cells", len(first_h0)); reg("n_first_h0_structural_zero_levels", sum(1 for c in first_h0 for a in ALPHAS if c["levels"][a]["structural_zero"]))
marker_laws = sorted({(cells[f]["_exp"]["name"], cells[f]["gamma"]) for f in integ["degenerate_markers"]})
reg("marker_slots", "; ".join(f"{law_label(n, True)} at γ = {g}" for n, g in marker_laws) or "none")
T["integrity"] = md_table(["Check", "Observed"], [
    ["Degenerate marker cells (m = ⌊γV⌋ ∈ {0, V}; enter no rule)", f"{res['n_degenerate_markers']} ({VALUES['marker_slots']})"],
    ["Cells with N_eff = 0 (no detection possible)", res["n_no_detection"]],
    ["Live cells with texts at M = 0", f"{len(integ['cells_with_M0_texts'])}" + ("" if not integ["cells_with_M0_texts"] else ": " + ", ".join(f"{x['cell']} ({pct(x['frac_M0'], 2)})" for x in integ["cells_with_M0_texts"][:6]))],
    ["Predictor flags (σ² negative or non-finite)", f"{len(integ['predictor_flags'])} (cell, α) levels in {len({x['cell'] for x in integ['predictor_flags']})} cells: " + "; ".join(sorted({x['cell'] for x in integ['predictor_flags']})) + ("; flags " + ", ".join(sorted({f for x in integ['predictor_flags'] for f in x['flags']})) if integ["predictor_flags"] else "")],
    ["Two-token chain: realised-weight fixed-size variance at h = 0 and h = 1 (reviewer's population values 0 and 0.08)", f"{VALUES['twotoken_fixed_h0']} and {VALUES['twotoken_fixed_h1']}"],
    ["The first rule at h = 0 (one token per text): structural zeros", f"{VALUES['n_first_h0_structural_zero_levels']} of {3 * len(first_h0)} (cell, α) levels"],
    ["R3 cells whose squared estimator was constant over the keys (recorded, never used)", R3["n_observed_sample_constancy"]]])
# timing from the manifest
if manifest:
    r = manifest["run"]; reg("run_start", r["start_utc"]); reg("run_end", r["end_utc"] or "—"); reg("run_hours", fnum(r["duration_hours"], 2) if r["duration_hours"] is not None else "—")
    reg("run_projected_hours", fnum(r["projected_hours_validation"], 2) if r["projected_hours_validation"] is not None else "—"); reg("run_restarts", r["n_start_lines"] - 1); reg("run_skipped", len(r["skipped_chains_on_resume"]))
    reg("run_sum_chain_hours", fnum(r["sum_chain_hours"], 2)); reg("inventory_digest", manifest["inventory"]["inventory_sha256"][:16] + "…"); reg("run_head", (manifest["git"]["launch"].get("launch_line") or "").split("HEAD=")[-1] or "—")
    reg("run_swap", (manifest["git"]["launch"].get("swap_at_launch") or "—").replace("vm.swapusage: ", "")); reg("manifest_written", manifest["written_utc"])
    chs = sorted(manifest["chains"], key=lambda x: -(x["chain_seconds"] or 0))[:5]
    T["timing"] = md_table(["Chain (the five longest)", "|D| tuples", "Build (s)", "Colouring (s)", "Cells", "Chain (s) measured", "Chain (s) projected"], [[x["chain"], f"{x['n_tuples']:,}" if x["n_tuples"] else "—", x["build_seconds"], x["colouring_seconds"], x["n_cells_computed"], x["chain_seconds"], x["projected_chain_seconds"]] for x in chs])
else:
    for k in ("run_start", "run_end", "run_hours", "run_projected_hours", "run_restarts", "run_skipped", "run_sum_chain_hours", "inventory_digest", "run_head", "run_swap", "manifest_written"):
        reg(k, "n/a (no manifest)")
    T["timing"] = "_No run manifest (fixture)._"
reg("label", res["label"]); reg("lock_sha", sha(ROOT / OUT / "PRE_RUN_LOCK.json")[:16] + "…"); reg("results_sha", sha(RES)[:16] + "…")
reg("n_level_blocks_recomputed", CHK["n_level_blocks_recomputed"])

# the refuted reduction statement, by rule and width (core, independent, V >= 10,000)
agg = {}
for c in CORE:
    if c["colouring"] == "independent" and c["_exp"]["V"] >= R3_REDUCTION_V:
        agg.setdefault((c["rule"], c["h"]), []).append((1 - c["identity_q"]["exact_ratio_formula"], c))
rows = []
for rule in grid["rules"]:
    for h in grid["h"]:
        v = agg.get((rule, h), [])
        if v:
            mx = max(v, key=lambda t: t[0]); rows.append([rule, h, len(v), pct(mx[0], 2), f"{law_label(mx[1]['_exp']['name'], True)}, L = {mx[1]['L']}", sum(1 for t in v if t[0] >= R3_REDUCTION_BOUND)])
T["reduction"] = md_table(["Rule", "h", "Cells (V ≥ 10,000)", "Largest reduction (I − Var)/I", "Where", "Cells at or above 1%"], rows) + "\n\nThe relative reduction of the fixed-size across-key variance against the independent-colour value, (1/C_cond − 1)/(V − 1), at the realised q-weights of every core cell with V ≥ 10,000 (both γ)."
for rule in grid["rules"]:
    v = [t for h in grid["h"] for t in agg.get((rule, h), [])]
    reg(f"red_{rule}_max", pct(max(t[0] for t in v), 2) if v else "—"); reg(f"red_{rule}_n_above", sum(1 for t in v if t[0] >= R3_REDUCTION_BOUND)); reg(f"red_{rule}_n", len(v))
for h in (0, 1):
    v = agg.get(("distinct", h), []); reg(f"red_distinct_h{h}_max", pct(max(t[0] for t in v), 2) if v else "—"); reg(f"red_distinct_h{h}_n_above", sum(1 for t in v if t[0] >= R3_REDUCTION_BOUND)); reg(f"red_distinct_h{h}_n", len(v))
cz = BY.get(("zipf_V10000_s1.0", 0, "independent", G0, Lw, "distinct"))
reg("inv_ccond_z10000", fnum(1 / cz["identity_q"]["C_cond"], 0) if cz else "—"); reg("coverage_z10000_distinct_Lmax", f"{cz['coverage']['distinct_retained_tuples']:,}" if cz else "—")
reg("red_z10000_h0_Lmax", pct(1 - cz["identity_q"]["exact_ratio_formula"], 1) if cz else "—")
# the h = 0 regimes of R1
def r1_rows(pred):
    return [r for r in R1["rows"] if pred(r)]
h0d = r1_rows(lambda r: r["rule"] == "distinct" and r["h"] == 0); h0r = r1_rows(lambda r: r["rule"] == "raw" and r["h"] == 0); h1p = r1_rows(lambda r: r["h"] >= 1)
def summ(prefix, rs):
    rr = [r["ratio"] for r in rs]; reg(f"{prefix}_n", len(rs)); reg(f"{prefix}_ratio_median", fnum(float(np.median(rr))) if rr else "—"); reg(f"{prefix}_ratio_min", fnum(min(rr)) if rr else "—"); reg(f"{prefix}_ratio_max", fnum(max(rr)) if rr else "—")
    reg(f"{prefix}_n_unresolved", sum(1 for r in rs if r["status"] == "unresolved")); reg(f"{prefix}_n_consistent", sum(1 for r in rs if r["status"] == "consistent"))
summ("h0d", h0d); summ("h0r", h0r); summ("h1p", h1p)
reg("h0d_pair_median", fnum(float(np.median([r["ratio_pairwise"] for r in h0d]))) if h0d else "—")
reg("h0d_level_obs_range", f"{pp(min(r['key_mean_level'] for r in h0d))}–{pp(max(r['key_mean_level'] for r in h0d))}" if h0d else "—"); reg("h0d_level_pred", f"{pp(min(r['pred_mean_level'] for r in h0d))}–{pp(max(r['pred_mean_level'] for r in h0d))}" if h0d else "—")
ex = [cells[r["cell"]]["levels"][R1_ALPHA]["exact_marginal_if_indep_distinct"] for r in h0d]; reg("h0d_exact_binomial_range", f"{pp(min(ex))}–{pp(max(ex))}" if ex else "—")
devs = [(r["key_mean_level"] - cells[r["cell"]]["levels"][R1_ALPHA]["exact_marginal_if_indep_distinct"]) / cells[r["cell"]]["levels"][R1_ALPHA]["se_conditional_on_texts"] for r in h0d]
reg("h0d_dev_se_median", fnum(float(np.median(devs))) if devs else "—"); reg("h0d_dev_se_min", fnum(min(devs)) if devs else "—"); reg("h0d_dev_se_max", fnum(max(devs)) if devs else "—")
reg("h0d_sigma2_range", f"{fnum(min(r['sigma2_model'] for r in h0d))}–{fnum(max(r['sigma2_model'] for r in h0d))}" if h0d else "—"); reg("h0d_sigd_range", f"{fnum(min(r['sd_zshift_pop'] for r in h0d))}–{fnum(max(r['sd_zshift_pop'] for r in h0d))}" if h0d else "—")
h0x = [r for r in h0r if r["status"] == "unresolved"]; reg("h0r_unres_n", len(h0x)); reg("h0r_unres_ratio_range", f"{fnum(min(r['ratio'] for r in h0x))}–{fnum(max(r['ratio'] for r in h0x))}" if h0x else "—")
reg("h0r_unres_sigd_range", f"{fnum(min(r['sd_zshift_pop'] for r in h0x))}–{fnum(max(r['sd_zshift_pop'] for r in h0x))}" if h0x else "—"); reg("h0r_unres_M_range", f"{fnum(min(r['mean_M'] for r in h0x), 0)}–{fnum(max(r['mean_M'] for r in h0x), 0)}" if h0x else "—")
reg("h0r_unres_cells", "; ".join(f"{law_label(r['law'], True)} L = {r['L']}" for r in h0x) or "none"); reg("h0r_unres_level_obs_pred", "; ".join(f"{pp(r['key_mean_level'])} against {pp(r['pred_mean_level'])}" for r in h0x) or "—")
reg("h0r_unres_pair_range", f"{fnum(min(r['ratio_pairwise'] for r in h0x))}–{fnum(max(r['ratio_pairwise'] for r in h0x))}" if h0x else "—")
# every inconsistent cell of every secondary block (the unresolved ones are in the supplement)
rows = []
for name, blk in R["R1_secondary"].items():
    for r in blk["inconsistent_cells"]:
        d = diag_row(name, r); rows.append([BLOCK_LABEL[name]] + diag_cells(d))
T["sec_inconsistent"] = md_table(["Block"] + DIAG_HEAD, rows) if rows else "_No inconsistent cell in any secondary block._"
reg("sec_incons_total", len(rows)); a001 = R["R1_secondary"]["alpha_0.001"]["inconsistent_cells"]
reg("a001_incons_n", len(a001)); reg("a001_incons_ratio_range", f"{fnum(min(r['ratio'] for r in a001))}–{fnum(max(r['ratio'] for r in a001))}" if a001 else "—"); reg("a001_incons_cells", "; ".join(f"{law_label(r['law'], True)} {r['rule']} h = {r['h']} L = {r['L']}" for r in a001) or "none")
us = R["R1_secondary"]["unit_sigma_predictor"]["inconsistent_cells"]; reg("unit_incons_n", len(us)); reg("unit_incons_cells", "; ".join(f"{law_label(r['law'], True)} {r['rule']} h = {r['h']} L = {r['L']} (ratio {fnum(r['ratio'])}; σ² from the identities {fnum(cells[r['cell']]['population']['sigma_model2'])})" for r in us) or "none")
fl = sorted({x["cell"] for x in res["descriptive"]["integrity"]["predictor_flags"]}); fst = []
for f in fl:
    c = cells[f]; st = next((r["status"] for r in R["R1_secondary"]["fixed_colouring"]["rows"] if r["cell"] == f), "not eligible")
    fst.append(f"{law_label(c['_exp']['name'], True)} h = {c['h']} L = {c['L']} {c['rule']} γ = {c['gamma']}: R3 {'structural zero' if c['q_hat']['structural_zero'] else 'checked'}; fixed-colouring block {st}")
reg("flag_cells_status", "; ".join(fst) or "none")
il = R["R1_secondary"]["illustration"]["inconsistent_cells"] + R["R1_secondary"]["fixed_colouring"]["inconsistent_cells"]; reg("ill_fixed_incons_n", len(il)); reg("ill_fixed_incons_laws", ", ".join(sorted({law_label(r["law"], True) for r in il})) or "none")
reg("ill_fixed_incons_ratio_range", f"{fnum(min(r['ratio'] for r in il))}–{fnum(max(r['ratio'] for r in il))}" if il else "—")
# R2's extremes: the largest normal deviation and the dead-detector checks
r2x = []
for c in LIVE:
    if c["colouring"] != "independent" or c["rule"] != "distinct":
        continue
    for a in ALPHAS:
        lv = c["levels"][a]
        if lv["structural_zero"]:
            continue
        dev = abs(lv["key_mean_level"] - lv["exact_marginal_if_indep_distinct"]); se = lv["se_conditional_on_texts"]
        r2x.append(((dev / se) if se > 0 else float("inf"), c, a, lv))
fin = [x for x in r2x if np.isfinite(x[0])]; mx = max(fin, key=lambda t: t[0]) if fin else None
if mx:
    reg("r2_maxdev_cell", f"{law_label(mx[1]['_exp']['name'], True)}, {mx[1]['rule']} rule, h = {mx[1]['h']}, L = {mx[1]['L']}, α = {mx[2]}"); reg("r2_maxdev_value", fnum(mx[0])); reg("r2_maxdev_keys_rejecting", sum(1 for v in mx[3]["level_values"] if v > 0))
    reg("r2_maxdev_mean", pct(mx[3]["key_mean_level"], 3)); reg("r2_maxdev_exact", pct(mx[3]["exact_marginal_if_indep_distinct"], 3)); reg("r2_maxdev_bound", fnum(mx[3]["r2_kl_pbound"])); reg("r2_maxdev_K", mx[1]["K"])
dead = [x for x in r2x if not np.isfinite(x[0])]; reg("r2_dead_n", len(dead))
reg("r2_dead_cells", "; ".join(f"{law_label(x[1]['_exp']['name'], True)} h = {x[1]['h']} L = {x[1]['L']} α = {x[2]} (exact mean {pct(x[3]['exact_marginal_if_indep_distinct'], 3)}, K = {x[1]['K']})" for x in dead) or "none")
reg("r2_dead_max_exact", pct(max((x[3]["exact_marginal_if_indep_distinct"] for x in dead), default=float("nan")), 3))
# the h = 0 raw-rule regime (nearly binary per-key levels), the floor, length and width factors
h0raw = [c for c in CORE if c["colouring"] == "independent" and c["gamma"] == G0 and c["rule"] == "raw" and c["h"] == 0]
for L in (256, Lw):
    cs = [c for c in h0raw if c["L"] == L]
    reg(f"h0raw_sd_range_L{L}", f"{pp(min(c['levels'][R1_ALPHA]['sd_obs_conditional'] for c in cs))}–{pp(max(c['levels'][R1_ALPHA]['sd_obs_conditional'] for c in cs))}" if cs else "—")
    reg(f"h0raw_worst_range_L{L}", f"{pct(min(c['levels'][R1_ALPHA]['max_key'] for c in cs))}–{pct(max(c['levels'][R1_ALPHA]['max_key'] for c in cs))}" if cs else "—")
    reg(f"h0raw_share5a_range_L{L}", f"{pct(min(c['levels'][R1_ALPHA]['share_keys_above_5alpha'] for c in cs))}–{pct(max(c['levels'][R1_ALPHA]['share_keys_above_5alpha'] for c in cs))}" if cs else "—")
    reg(f"h0raw_median_key_range_L{L}", f"{pct(min(c['levels'][R1_ALPHA]['quantiles']['0.5'] for c in cs), 2)}–{pct(max(c['levels'][R1_ALPHA]['quantiles']['0.5'] for c in cs), 2)}" if cs else "—")
reg("floor_pp", fnum(100 * math.sqrt(0.01 * 0.99 / grid["N"]), 3))
h3 = [c for c in CORE if c["colouring"] == "independent" and c["gamma"] == G0 and c["h"] >= 3 and c["L"] == Lw and c["rule"] in ("raw", "distinct")]
reg("h3plus_sd_range_Lmax", f"{pp(min(c['levels'][R1_ALPHA]['sd_obs_conditional'] for c in h3))}–{pp(max(c['levels'][R1_ALPHA]['sd_obs_conditional'] for c in h3))}" if h3 else "—")
h3t = [c["levels"][R1_ALPHA]["pred_first_order"]["theory_share"] for c in h3]; reg("h3plus_theory_share_max", fnum(max(h3t)) if h3t else "—")
def growth(law, rule, h=1):
    a = BY.get((law, h, "independent", G0, grid["L"][0], rule)); b = BY.get((law, h, "independent", G0, Lw, rule))
    return (b["population"]["rho_bar"] / a["population"]["rho_bar"], b["mean_M"] / a["mean_M"]) if a and b and a["population"]["rho_bar"] > 0 else (float("nan"), float("nan"))
for rule in grid["rules"]:
    gs = [growth(law, rule) for law in CORE_LAWS]; reg(f"rho_growth_{rule}_range", f"{fnum(min(g[0] for g in gs), 1)}–{fnum(max(g[0] for g in gs), 1)}"); reg(f"M_growth_{rule}_range", f"{fnum(min(g[1] for g in gs), 1)}–{fnum(max(g[1] for g in gs), 1)}")
fac = {"zipf": [], "markov": []}
for x in R5["chains"]:
    if int(x["chain"][1]) == Lw and float(x["chain"][2]) == G0:
        A = x["A_between"]; kind = "markov" if x["chain"][0].startswith("markov") else "zipf"
        fac[kind] += [A[i] / A[i + 1] for i in range(len(A) - 1) if A[i + 1] > 0]
reg("A_drop_zipf_range", f"{fnum(min(fac['zipf']), 0)}–{fnum(max(fac['zipf']), 0)}" if fac["zipf"] else "—"); reg("A_drop_markov_range", f"{fnum(min(fac['markov']), 0)}–{fnum(max(fac['markov']), 0)}" if fac["markov"] else "—")
for h in (1, 2):
    for rule in ("raw", "distinct"):
        cs = [BY.get((law, h, "independent", G0, Lw, rule)) for law in CORE_LAWS]; cs = [c for c in cs if c]
        reg(f"sd_h{h}_{rule}_Lmax_range", f"{pp(min(c['levels'][R1_ALPHA]['sd_obs_conditional'] for c in cs))}–{pp(max(c['levels'][R1_ALPHA]['sd_obs_conditional'] for c in cs))}" if cs else "—")
# the deployer's view at h = 1, L_max
for rule in ("raw", "distinct", "first"):
    cs = [BY.get((law, 1, "independent", G0, Lw, rule)) for law in CORE_LAWS]; cs = [c for c in cs if c]
    for q, nm in (("0.5", "median"), ("0.95", "q95"), ("0.99", "q99")):
        reg(f"dep_{rule}_{nm}_range", f"{pct(min(c['levels'][R1_ALPHA]['quantiles'][q] for c in cs), 2)}–{pct(max(c['levels'][R1_ALPHA]['quantiles'][q] for c in cs), 2)}" if cs else "—")
    reg(f"dep_{rule}_worst_range", f"{pct(min(c['levels'][R1_ALPHA]['max_key'] for c in cs))}–{pct(max(c['levels'][R1_ALPHA]['max_key'] for c in cs))}" if cs else "—")
    reg(f"dep_{rule}_share2a_range", f"{pct(min(c['levels'][R1_ALPHA]['share_keys_above_2alpha'] for c in cs))}–{pct(max(c['levels'][R1_ALPHA]['share_keys_above_2alpha'] for c in cs))}" if cs else "—")
    reg(f"dep_{rule}_share5a_range", f"{pct(min(c['levels'][R1_ALPHA]['share_keys_above_5alpha'] for c in cs))}–{pct(max(c['levels'][R1_ALPHA]['share_keys_above_5alpha'] for c in cs))}" if cs else "—")
    reg(f"dep_{rule}_keymean_range", f"{pct(min(c['levels'][R1_ALPHA]['key_mean_level'] for c in cs), 2)}–{pct(max(c['levels'][R1_ALPHA]['key_mean_level'] for c in cs), 2)}" if cs else "—")
reg("r4b_rho_indep_Lmax", fnum(next((x["rho_bar"] for x in R4b["rows"] if x["colouring"] == "independent" and x["gamma"] == G0 and x["L"] == max(r["L"] for r in R4b["rows"])), float("nan")), 4))
reg("r4b_rho_fixed_Lmax", fnum(next((x["rho_bar"] for x in R4b["rows"] if x["colouring"] == "fixed" and x["gamma"] == G0 and x["L"] == max(r["L"] for r in R4b["rows"])), float("nan")), 4))
reg("r4b_lim_indep", fnum(next((x["limit_rho"] for x in R4b["rows"] if x["colouring"] == "independent"), float("nan")), 4)); reg("r4b_lim_fixed", fnum(next((x["limit_rho"] for x in R4b["rows"] if x["colouring"] == "fixed"), float("nan")), 4))
reg("r4b_M_L64", fnum(next((x["mean_M"] for x in R4b["rows"] if x["L"] == min(r["L"] for r in R4b["rows"])), float("nan")), 1)); reg("r4b_rho_indep_L64", fnum(next((x["rho_bar"] for x in R4b["rows"] if x["colouring"] == "independent" and x["gamma"] == G0 and x["L"] == min(r["L"] for r in R4b["rows"])), float("nan")), 3))
reg("r2_n_checks_K2000", sum(1 for x in r2x if x[1]["K"] == 2000)); reg("n_first_h0_live", len(first_h0)); reg("n_first_h0_levels_total", 3 * len(first_h0))
# F4: the pairwise predictor against the common-factor one, both subsamples
reg("pair_closer_n", sum(1 for r in R1["rows"] if np.isfinite(r["ratio_pairwise"]) and abs(r["ratio_pairwise"] - 1) < abs(r["ratio"] - 1)))
def pair_two(cell, alpha):
    lv = cells[cell]["levels"][alpha]; pw = lv.get("pred_pairwise_gaussian") or {}; sd = lv["sd_obs_conditional"]
    return (sd / pw["sd_cond"] if pw.get("sd_cond", 0) > 0 else float("nan"), sd / pw["sd_cond_replicate"] if pw.get("sd_cond_replicate") else float("nan"), (100 * pw["subsample_sd_difference"]) if pw.get("subsample_sd_difference") is not None else float("nan"))
h0d_two = [pair_two(r["cell"], R1_ALPHA) for r in h0d]
reg("h0d_pair_rep_median", fnum(float(np.nanmedian([t[1] for t in h0d_two]))) if h0d_two else "—"); reg("h0d_pair_diff_max_pp", fnum(float(np.nanmax([t[2] for t in h0d_two]))) if h0d_two else "—")
reg("h0r_unres_overpred_range", f"{fnum(1 / max(r['ratio'] for r in h0x))}–{fnum(1 / min(r['ratio'] for r in h0x))}" if h0x else "—")
reg("a001_overpred_range", f"{fnum(1 / max(r['ratio'] for r in a001))}–{fnum(1 / min(r['ratio'] for r in a001))}" if a001 else "—")
reg("a001_pair_replicates", "; ".join(f"{fnum(t[0])} / {fnum(t[1])}" for t in (pair_two(r["cell"], "0.001") for r in a001)) or "—")
reg("h0r_unres_M_values", ", ".join(fnum(r["mean_M"], 0) for r in sorted(h0x, key=lambda r: r["mean_M"])) or "—")
h0c = [r for r in h0r if r["status"] == "consistent"]; reg("h0r_short_n_consistent", sum(1 for r in h0c if r["mean_M"] <= 128)); reg("h0r_cons_sigd_max", fnum(max(r["sd_zshift_pop"] for r in h0c)) if h0c else "—"); reg("h0r_cons_sigd_min", fnum(min(r["sd_zshift_pop"] for r in h0c)) if h0c else "—")
# F3: the h >= 3 exceptions
h3c = [c for c in CORE if c["colouring"] == "independent" and c["gamma"] == G0 and c["rule"] in R1_RULES and c["h"] >= 3]
h3e = sorted([r for r in R1["rows"] if r["h"] >= 3], key=lambda r: (r["law"], r["rule"], r["L"]))
reg("h3_exceptions", "; ".join(f"{law_label(r['law'], True)} {r['rule']} L = {r['L']} (theory share {fnum(r['theory_share'])}, SD {fnum(r['sd_obs_pp'])} pp, ratio {fnum(r['ratio'])}, {r['status']})" for r in h3e) or "none")
reg("h3_n_eligible_Lmax", sum(1 for r in h3e if r["L"] == Lw)); reg("h3_n_candidates_Lmax", sum(1 for c in h3c if c["L"] == Lw))
longc = [r for r in h0c if r["mean_M"] > 128]; reg("h0r_cons_long_n", len(longc)); reg("h0r_cons_long_sigd_min", fnum(min(r["sd_zshift_pop"] for r in longc)) if longc else "—")
h0du = [r for r in h0d if r["status"] == "unresolved"]; reg("h0d_unres_ratio_range", f"{fnum(min(r['ratio'] for r in h0du))}–{fnum(max(r['ratio'] for r in h0du))}" if h0du else "—"); reg("h0d_unres_L_span", f"{min(r['L'] for r in h0du)}–{max(r['L'] for r in h0du):,}" if h0du else "—")
reg("h3plus_n_ineligible", len(h3c) - len(h3e)); reg("h4_n_eligible", sum(1 for r in h3e if r["h"] == 4)); reg("h3_sd_range", f"{fnum(min(r['sd_obs_pp'] for r in h3e))}–{fnum(max(r['sd_obs_pp'] for r in h3e))}" if h3e else "—")
# F2: the conditional collision A/B of an i.i.d. raw law equals C_0 at every width, not C_h
c1 = BY.get(("zipf_V10000_s1.0", 1, "independent", G0, Lw, "raw")); c0 = BY.get(("zipf_V10000_s1.0", 0, "independent", G0, Lw, "raw"))
reg("z10000_h1_raw_AB", fnum(c1["identity_q"]["C_cond"], 5) if c1 else "—"); reg("z10000_h1_raw_Ch", f"{c1['population']['collision_h_analytic']:.3e}" if c1 else "—"); reg("z10000_h0_raw_C0", fnum(c0["identity_q"]["C_cond"], 5) if c0 else "—")
reg("z10000_C0_analytic", fnum(c0["population"]["collision_h_analytic"], 5) if c0 else "—"); reg("red_order_z10000_raw", pct(1 / (10000 * c0["population"]["collision_h_analytic"]), 2) if c0 else "—")
# F9: the process paragraph from the record
reg("conductor", "Claude (Fable 5.1, in Claude Code)"); reg("reviewer", "Codex")
rv_dir = ROOT / "research" / "reviews" / "R04_study1-report"; revs = sorted(rv_dir.glob("REVIEW_*_r*.md")); resol = (rv_dir / "RESOLUTION.md").exists()
if resol:
    reg("r04_status", "agreed (RESOLUTION.md present)")
elif revs:
    last = revs[-1]; vline = next((l.strip() for l in reversed(last.read_text().splitlines()) if l.strip().startswith("VERDICT:")), "no verdict line")
    reg("r04_status", f"open; the latest review on file is {last.name} ({vline}); this build answers it and is not an approval")
else:
    reg("r04_status", "open; no review on file yet")
h3c = [c for c in CORE if c["colouring"] == "independent" and c["gamma"] == G0 and c["rule"] in R1_RULES and c["h"] >= 3]
reg("h3plus_n_candidates", len(h3c)); reg("h3plus_n_eligible", sum(1 for r in R1["rows"] if r["h"] >= 3))

# ------------------------------------------------------------------ figures
def save(fig, name):
    for ext in ("png", "svg"):
        fig.savefig(OUTDIR / f"{name}.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)


# Fig 1: adequacy
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
ax = axes[0]
for rule in R1_RULES:
    for status, filled in (("consistent", True), ("inconsistent", False), ("unresolved", False)):
        rs = [r for r in R1["rows"] if r["rule"] == rule and r["status"] == status]
        if not rs:
            continue
        ax.scatter([r["sd_pred_pp"] for r in rs], [r["sd_obs_pp"] for r in rs], s=28, marker=MK_RULE[rule], facecolors=COL_RULE[rule] if filled else SURFACE, edgecolors=COL_RULE[rule], linewidths=1.2,
                   label=f"{rule} rule, {status} ({len(rs)})", zorder=3)
lo = min([r["sd_pred_pp"] for r in R1["rows"]] + [r["sd_obs_pp"] for r in R1["rows"]] + [0.05]); hi = max([r["sd_pred_pp"] for r in R1["rows"]] + [r["sd_obs_pp"] for r in R1["rows"]] + [0.1])
xx = np.array([lo * 0.8, hi * 1.25]); ax.plot(xx, xx, color=MUTED, lw=1, zorder=2); ax.plot(xx, xx * 1.5, color=MUTED, lw=0.8, ls="--", zorder=2); ax.plot(xx, xx * 2 / 3, color=MUTED, lw=0.8, ls="--", zorder=2)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("predicted across-key SD of the per-key level (pp), common-factor predictor"); ax.set_ylabel("observed across-key SD (pp), α = 1%")
ax.set_title("(a) R1-eligible cells; dashed lines: the band [2/3, 3/2]", loc="left", fontsize=9); ax.legend(fontsize=7.5, loc="upper left")
ax = axes[1]
for rule in R1_RULES:
    rs = [r for r in R1["rows"] if r["rule"] == rule]
    if rs:
        x = np.array([r["sd_zshift_pop"] for r in rs]); y = np.array([r["ratio"] for r in rs]); lo_ = np.array([r["ratio_ci95"][0] for r in rs]); hi_ = np.array([r["ratio_ci95"][1] for r in rs])
        ax.errorbar(x, y, yerr=[np.clip(y - lo_, 0, None), np.clip(hi_ - y, 0, None)], fmt=MK_RULE[rule], color=COL_RULE[rule], ms=4, lw=0.8, capsize=0, label=f"{rule} rule", zorder=3)
ax.axhspan(R1_BAND[0], R1_BAND[1], color=GRID, alpha=0.6, zorder=1); ax.axhline(1.0, color=MUTED, lw=1, zorder=2)
ax.set_xscale("log"); ax.set_xlabel("σ_δ = √ρ̄  (across-key SD of the mean z-shift)"); ax.set_ylabel("observed / predicted SD, with key-bootstrap 95% CI"); ax.set_title("(b) the ratio against the shift dispersion; shaded: the band", loc="left", fontsize=9); ax.legend(fontsize=7.5)
save(fig, "fig1_adequacy")

# Fig 2: dispersion against L, h = 1, per core law (small multiples), observed solid, predicted dashed
n = len(CORE_LAWS); ncol = min(3, n); nrow = int(math.ceil(n / ncol)); fig, axes = plt.subplots(nrow, ncol, figsize=(3.6 * ncol, 3.1 * nrow), squeeze=False)
for i, law in enumerate(CORE_LAWS):
    ax = axes[i // ncol][i % ncol]
    for rule in grid["rules"]:
        Ls = grid["L"]; obs = []; pred = []; lo_ = []; hi_ = []
        for L in Ls:
            c = BY.get((law, 1, "independent", G0, L, rule)); lv = c["levels"][R1_ALPHA] if c and "levels" in c else None
            obs.append(100 * lv["sd_obs_conditional"] if lv else np.nan); pred.append(100 * lv["pred_first_order"]["sd_cond"] if lv else np.nan)
            lo_.append(100 * lv["sd_obs_boot_ci95"][0] if lv else np.nan); hi_.append(100 * lv["sd_obs_boot_ci95"][1] if lv else np.nan)
        ax.fill_between(Ls, lo_, hi_, color=COL_RULE[rule], alpha=0.15, lw=0, label=f"{rule}, observed: key-bootstrap 95% CI" if i == 0 else None)
        ax.plot(Ls, obs, color=COL_RULE[rule], marker=MK_RULE[rule], ms=4.5, label=f"{rule}, observed"); ax.plot(Ls, pred, color=COL_RULE[rule], ls="--", lw=1.3, label=f"{rule}, predicted")
    ax.set_xscale("log", base=2); ax.set_yscale("log"); ax.set_title(law_label(law), fontsize=9, loc="left"); ax.set_xticks(grid["L"]); ax.set_xticklabels([str(L) for L in grid["L"]], fontsize=7)
    if i % ncol == 0:
        ax.set_ylabel("across-key SD of the level (pp)")
    if i // ncol == nrow - 1:
        ax.set_xlabel("text length L (tokens)")
for j in range(n, nrow * ncol):
    axes[j // ncol][j % ncol].axis("off")
h_, l_ = axes[0][0].get_legend_handles_labels(); fig.legend(h_, l_, loc="lower center", ncol=3, fontsize=8, bbox_to_anchor=(0.5, -0.04)); fig.suptitle(f"Across-key SD of the per-key false-positive level at α = 1% against length (h = 1, γ = 0.5, independent colouring; K = {grid['K']} keys, N = {grid['N']:,} texts; shaded = key-bootstrap 95% CI of the observed SD)", fontsize=9, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.05, 1, 0.97)); save(fig, "fig2_length")

# Fig 3: width, two rows of small multiples (Ã(h) with C_h; the level SD at L_max under raw and distinct)
fig, axes = plt.subplots(2, max(n, 1), figsize=(2.7 * max(n, 1) + 1, 6.0), squeeze=False)
for i, law in enumerate(CORE_LAWS):
    ax = axes[0][i]; x5 = next((x for x in R5["chains"] if x["chain"][0] == law and int(x["chain"][1]) == Lw and float(x["chain"][2]) == G0), None)
    if x5:
        ax.errorbar(x5["h"], x5["A_between"], yerr=np.array(x5["A_between_se"]), color=COL_RULE["raw"], marker="o", ms=4.5, lw=1.5, label="Ã(h) observed (raw rule)")
        if any(c is not None for c in x5["C_h_analytic"]):
            ax.scatter(x5["h"], [c if c is not None else np.nan for c in x5["C_h_analytic"]], facecolors=SURFACE, edgecolors=INK, s=40, zorder=4, label="analytic C_h (i.i.d. laws)")
    ax.set_yscale("log"); ax.set_title(law_label(law, True), fontsize=9, loc="left"); ax.set_xticks(grid["h"])
    if i == 0:
        ax.set_ylabel("Ã(h), raw rule")
    ax = axes[1][i]
    for rule in ("raw", "distinct"):
        ys = []; lo_ = []; hi_ = []
        for h in grid["h"]:
            c = BY.get((law, h, "independent", G0, Lw, rule)); lv = c["levels"][R1_ALPHA] if c and "levels" in c else None
            ys.append(100 * lv["sd_obs_conditional"] if lv else np.nan); lo_.append(100 * lv["sd_obs_boot_ci95"][0] if lv else np.nan); hi_.append(100 * lv["sd_obs_boot_ci95"][1] if lv else np.nan)
        ax.fill_between(grid["h"], lo_, hi_, color=COL_RULE[rule], alpha=0.15, lw=0)
        ax.plot(grid["h"], ys, color=COL_RULE[rule], marker=MK_RULE[rule], ms=4.5, label=f"level SD, {rule} rule (shaded: key-bootstrap 95% CI)")
    ax.set_yscale("log"); ax.set_xticks(grid["h"]); ax.set_xlabel("context width h")
    if i == 0:
        ax.set_ylabel("level SD (pp), α = 1%")
h0, l0 = axes[0][0].get_legend_handles_labels(); h1, l1 = axes[1][0].get_legend_handles_labels(); fig.legend(h0 + h1, l0 + l1, loc="lower center", ncol=4, fontsize=8, bbox_to_anchor=(0.5, -0.01))
fig.suptitle(f"Context width at L = {Lw:,}, γ = 0.5: the between-text collision Ã(h) under the raw rule (top; hollow = the i.i.d. laws' analytic C_h) and the across-key SD of the level at α = 1% (bottom)", fontsize=9.5, x=0.01, ha="left"); fig.tight_layout(rect=(0, 0.06, 1, 0.95), h_pad=2.0); save(fig, "fig3_width")

# Fig 4: the deployer's view, per-key level quantiles against L for one law, three rules
FAN_LAW = "zipf_V10000_s1.0" if "zipf_V10000_s1.0" in CORE_LAWS else CORE_LAWS[0]; reg("fan_law", law_label(FAN_LAW))
fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.6), sharey=True)
for ax, rule in zip(axes, grid["rules"]):
    Ls = grid["L"]; Q = {q: [] for q in ("0.01", "0.05", "0.5", "0.95", "0.99")}; mx = []; km = []
    for L in Ls:
        c = BY.get((FAN_LAW, 1, "independent", G0, L, rule)); lv = c["levels"][R1_ALPHA] if c and "levels" in c else None
        for q in Q:
            Q[q].append(100 * lv["quantiles"][q] if lv else np.nan)
        mx.append(100 * lv["max_key"] if lv else np.nan); km.append(100 * lv["key_mean_level"] if lv else np.nan)
    ax.fill_between(Ls, Q["0.01"], Q["0.99"], color=SEQ[0], label="1%–99% of the sampled keys"); ax.fill_between(Ls, Q["0.05"], Q["0.95"], color=SEQ[1], label="5%–95% of the sampled keys")
    ax.plot(Ls, Q["0.5"], color=SEQ[3], lw=2, label="median key"); ax.scatter(Ls, mx, color=INK, s=14, zorder=4, label="worst of the sampled keys"); ax.axhline(1.0, color=MUTED, lw=1, ls="--", label="nominal 1%")
    ax.set_xscale("log", base=2); ax.set_xticks(Ls); ax.set_xticklabels([str(L) for L in Ls], fontsize=7); ax.set_title(f"{rule} rule", fontsize=9, loc="left"); ax.set_xlabel("text length L (tokens)")
axes[0].set_ylabel("per-key false-positive level at α = 1% (%)"); axes[0].legend(fontsize=7.5, loc="upper left")
fig.suptitle(f"What one fixed key faces: per-key levels over the K = {grid['K']} sampled keys on the N = {grid['N']:,} realised texts, {law_label(FAN_LAW)}, h = 1, γ = 0.5 (bands = empirical spread of the sampled keys, not confidence bands)", fontsize=9, x=0.01, ha="left"); fig.tight_layout(); save(fig, "fig4_keys")

# Fig 5: (a) the support control's saturation; (b) R3: observed against exact variance, both colourings
fig, axes = plt.subplots(1, 2, figsize=(10, 4.0))
ax = axes[0]; rows5 = R4b["rows"]
if rows5:
    for colouring in ("independent", "fixed"):
        for gam, ls in ((0.5, "-"), (0.25, ":")):
            rs = sorted([r for r in rows5 if r["colouring"] == colouring and r["gamma"] == gam], key=lambda r: r["L"])
            if rs:
                ax.errorbar([r["L"] for r in rs], [r["rho_bar"] for r in rs], yerr=[r["se"] for r in rs], color=COL_COLOURING[colouring], ls=ls, marker="o", ms=4, label=f"{colouring}, γ = {gam}")
                ax.axhline(rs[0]["limit_rho"], color=COL_COLOURING[colouring], lw=0.9, ls=ls, alpha=0.6)
    ax.set_xscale("log", base=2); ax.set_xlabel("text length L (tokens)"); ax.set_ylabel("ρ̄ (across-key variance of the mean z-shift)"); ax.legend(fontsize=7.5)
ax.set_title("(a) support control, distinct rule, h = 0: ρ̄(L); thin lines = limits; γ curves coincide", loc="left", fontsize=8)
ax = axes[1]
n_plot = sum(1 for c in LIVE if not c["q_hat"]["structural_zero"]); reg("fig5b_n_plotted", n_plot); reg("fig5b_n_excluded", len(LIVE) - n_plot)
reg("fig5b_n_core_fixed", sum(1 for c in LIVE if not c["q_hat"]["structural_zero"] and c["colouring"] == "fixed" and c["_exp"]["role"] == "core"))
for colouring in ("independent", "fixed"):
    cs = [c for c in LIVE if c["colouring"] == colouring and not c["q_hat"]["structural_zero"]]
    ax.scatter([c["q_hat"]["exact_var_own_colouring"] for c in cs], [c["q_hat"]["var_known_mean"] for c in cs], s=12, color=COL_COLOURING[colouring], alpha=0.7, label=f"{colouring} colouring ({len(cs)} cells)", zorder=3)
vals = [c["q_hat"]["exact_var_own_colouring"] for c in LIVE if not c["q_hat"]["structural_zero"] and c["q_hat"]["exact_var_own_colouring"] > 0]
if vals:
    xx = np.array([min(vals) * 0.7, max(vals) * 1.4]); ax.plot(xx, xx, color=MUTED, lw=1, zorder=2)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("exact across-key variance of q̂ (identity at the realised weights)"); ax.set_ylabel("observed known-mean variance s₀²"); ax.legend(fontsize=7.5, loc="upper left")
ax.set_title(f"(b) R3: observed s₀² against the exact identity ({n_plot} live cells; {len(LIVE) - n_plot} structural zeros not plotted)", loc="left", fontsize=8); fig.tight_layout(); save(fig, "fig5_identities")
for k, cap in (("fig1_adequacy", "Figure 1 — R1 adequacy: observed against predicted across-key SD of the per-key level, and the ratio against the shift dispersion"), ("fig2_length", "Figure 2 — the across-key SD of the level against text length under the three retention rules (h = 1)"),
               ("fig3_width", "Figure 3 — context width: the between-text collision and the level's across-key SD"), ("fig4_keys", "Figure 4 — the distribution of per-key levels over the keys against length (one law, three rules)"),
               ("fig5_identities", f"Figure 5 — the support control's saturation and the exact-identity check R3 ({VALUES['fig5b_n_plotted']} live cells plotted, the {VALUES['fig5b_n_excluded']} structural zeros excluded; the {VALUES['fig5b_n_core_fixed']} core fixed cells, reported outside the R3 decision, are included)")):
    T[f"FIG_{k}"] = f"![{cap}]({('../' + str((OUTDIR / (k + '.png')).relative_to(ROOT))) if not PILOT else (k + '.png')})"

# ------------------------------------------------------------------ write tables, values, and assemble the report
(OUTDIR / "tables.md").write_text("\n\n".join(f"### {k}\n\n{v}" for k, v in T.items() if not k.startswith("FIG_")) + "\n")
(OUTDIR / "prose_values.json").write_text(json.dumps(VALUES, indent=1, ensure_ascii=False))
prose = PROSE.read_text()


def sub_table(m):
    name = m.group(1)
    if name not in T:
        raise SystemExit(f"unknown table {name}")
    USED.add("<<" + name + ">>"); return T[name]


def sub_fig(m):
    name = "FIG_" + m.group(1)
    if name not in T:
        raise SystemExit(f"unknown figure {m.group(1)}")
    USED.add(name); return T[name]


def sub_val(m):
    name = m.group(1)
    if name not in VALUES:
        raise SystemExit(f"unresolved placeholder [[{name}]]")
    USED.add(name); return VALUES[name]


text = re.sub(r"<<TABLE:([A-Za-z0-9_]+)>>", sub_table, prose); text = re.sub(r"<<FIG:([A-Za-z0-9_]+)>>", sub_fig, text); text = re.sub(r"\[\[([A-Za-z0-9_.]+)\]\]", sub_val, text)
left = re.findall(r"\[\[[^\]]+\]\]|<<[A-Z]+:[^>]+>>", text)
if left:
    raise SystemExit(f"unresolved placeholders remain: {left[:10]}")
if PILOT:
    text = "**FIXTURE RENDER ON THE DISCLOSED PILOT (validation laws, seeds and keys; not study outcomes; never the report)**\n\n" + text
REPORT.write_text(text)
unused = sorted(set(VALUES) - USED)
print(f"{res['label']}: wrote {REPORT} ({len(text.split())} words), {len(T)} tables/figures, {len(VALUES)} values ({len(unused)} registered but unused: {unused[:40]}{'…' if len(unused) > 40 else ''})")
print("independent re-computation: all equal to results.json;", json.dumps({k: v for k, v in CHK.items() if k in ("R1", "R2", "R3", "R4", "R5", "R4b")}, default=str)[:1500])
