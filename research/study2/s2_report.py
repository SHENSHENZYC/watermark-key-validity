"""Study 2 report builder (protocol v0.1): every table, figure and number in research/STUDY2_REPORT_v0.1.md comes from the locked
outputs (outputs/study2_v0.1/cells/*.json, results.json, RUN_MANIFEST.json), never typed by hand (rule A4.1 of the research-project-guide).

Before writing anything the builder RE-COMPUTES, with its own code (not s2_analyze), from the per-cell files:
  - every (cell, alpha)'s key-mean level, across-key SD, quantiles, extrema and exceedance shares from the stored integer level counts;
  - S1's eligibility, status and counts (primary and every secondary block, plus the unit-sigma block the protocol lists and the locked
    analyzer does not carry, which the builder reports as its own, disclosed);
  - S2's two-sided KL bound per check and the flagged set; S3's gross-failure decision per cell, the structural zeros, the coverage
    diagnostic and the fixed/independent ratio rows; S4's and S5's chain decisions; the deployer subset (from the grid) and its rows;
    the between-cell, between-tokenizer and language-disparity statistics;
  - in study mode only (REAL): that every cell's prediction, exact key-mean reference, rho_bar and mean M equal the key-free inputs
    disclosed before the lock (outputs/study2_v0.1/INPUTS.json);
and asserts that all of these equal results.json (every mismatch is collected and reported before raising).
Writes <report dir>/: tables.md, tables_*_full.md supplements, prose_values.json, checks.json and fig1..fig6 (.png, .svg); then assembles the
report from research/study2/report_prose_v0.1.md by filling <<TABLE:name>>, <<FIG:name>> and [[name]] and refusing any unresolved
placeholder (registered-but-unused names are listed).
Usage: .venv/bin/python research/study2/s2_report.py                      (study mode: verifies the lock; writes outputs/study2_v0.1/report/ and research/STUDY2_REPORT_v0.1.md)
       .venv/bin/python research/study2/s2_report.py --fixture --results <results.json of a FIXTURE inventory> --cells <fixture dir> --out-dir <dir outside the repository> [--manifest <file>]
       (fixture mode: every cell must carry the FIXTURE marker; the output is labelled FIXTURE and can never be the canonical report or report directory)
"""
import json, math, pathlib, re, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
from matplotlib.colors import LinearSegmentedColormap   # noqa: E402
from scipy.stats import spearmanr   # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study1")); sys.path.insert(0, str(ROOT / "tools"))
from s2_run import OUT, STUDY, GRID_CANON, INPUTS, verify_lock, sha, expected_cells, QUANTILE_KEYS   # noqa: E402

ARGV = sys.argv[1:]
FIXTURE = "--fixture" in ARGV
PROSE = HERE / "report_prose_v0.1.md"
if FIXTURE:
    RES = pathlib.Path(ARGV[ARGV.index("--results") + 1]).resolve(); CELLS = pathlib.Path(ARGV[ARGV.index("--cells") + 1]).resolve(); OUTDIR = pathlib.Path(ARGV[ARGV.index("--out-dir") + 1]).resolve()
    for p in (RES, CELLS, OUTDIR):
        if ROOT.resolve() in p.parents or p == ROOT.resolve():
            raise SystemExit(f"fixture mode reads and writes outside the repository only ({p})")
    REPORT = OUTDIR / "STUDY2_REPORT_fixture.md"; MANIFEST = pathlib.Path(ARGV[ARGV.index("--manifest") + 1]) if "--manifest" in ARGV else None
else:
    if len(ARGV) > 0:
        raise SystemExit("study mode takes no arguments (canonical paths only)")
    RES = ROOT / OUT / "results.json"; CELLS = ROOT / OUT / "cells"; OUTDIR = ROOT / OUT / "report"; REPORT = ROOT / "research" / "STUDY2_REPORT_v0.1.md"; MANIFEST = ROOT / OUT / "RUN_MANIFEST.json"
    if not MANIFEST.exists():
        raise SystemExit("study mode needs outputs/study2_v0.1/RUN_MANIFEST.json (run s2_manifest.py first)")
OUTDIR.mkdir(parents=True, exist_ok=True)
REAL = not FIXTURE

S2_PBOUND = 1e-6; S3_GROSS_SE = 6.0
# dataviz palette (validated 2026-10-10 with scripts/validate_palette.js, light surface, all pairs; reused from Study 1): rules raw/distinct/first = slots 1/2/3;
# the tokenizers are told apart by marker and line style, the families by panel; every figure carries a legend and every value is in a table (the relief rule)
COL_RULE = {"raw": "#2a78d6", "distinct": "#eb6834", "first": "#1baf7a"}; COL_FAM = {"kgw": "#2a78d6", "gumbel": "#4a3aa7"}; COL_COLOURING = {"independent": "#2a78d6", "fixed": "#4a3aa7", "uniform": "#1baf7a"}
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#898781", "#e1e0d9", "#fcfcfb"; SEQ = ["#cde2fb", "#86b6ef", "#2a78d6", "#104281"]
MK_RULE = {"raw": "o", "distinct": "s", "first": "D"}; MK_TOK = {"llama": "o", "qwen": "^"}; LS_TOK = {"llama": "-", "qwen": ":"}
DIVERGING = LinearSegmentedColormap.from_list("div", ["#eb6834", SURFACE, "#2a78d6"])
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.8, "grid.linestyle": "-", "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "lines.linewidth": 1.8, "lines.markersize": 4.5})

# ------------------------------------------------------------------ loading
res = json.loads(RES.read_text()); grid = json.loads((ROOT / GRID_CANON).read_text())
if res.get("study") != STUDY or res.get("mode") != "study":
    raise SystemExit(f"results file is not a study-mode analysis of {STUDY}: {res.get('study')!r}, {res.get('mode')!r}")
lock = verify_lock(ROOT / OUT / "PRE_RUN_LOCK.json", GRID_CANON, root=ROOT)
if res["lock"]["sha256"] != sha(ROOT / OUT / "PRE_RUN_LOCK.json") or res["grid_sha256"] != sha(ROOT / GRID_CANON):
    raise SystemExit("results.json was not produced under the current lock and grid")
res_cells_dir = pathlib.Path(res["cells_dir"]); res_cells_dir = res_cells_dir if res_cells_dir.is_absolute() else (ROOT / res_cells_dir)
if res_cells_dir.resolve() != CELLS.resolve():
    raise SystemExit(f"results.json analysed {res_cells_dir}, not the cells directory given ({CELLS})")
if REAL and CELLS.resolve() != (ROOT / OUT / "cells").resolve():
    raise SystemExit("study mode reads the canonical cells directory only")
P = grid["primary"]; BAND = (float(P["band"][0]), float(P["band"][1])); A_PRIMARY = str(P["alpha"]); ALPHAS = [str(a) for a in grid["alpha"]]
EXPECTED = expected_cells(grid); L_OF = {sp["tag"]: sp["L"] for sp in grid["cells"]}; SPECS = grid["cells"]; TOKS = list(grid["tokenizers"]); HS = grid["h"]
cells = {}
for c in EXPECTED:
    d = json.loads((CELLS / c["file"]).read_text())
    if FIXTURE and "FIXTURE" not in d:
        raise SystemExit(f"fixture mode: {c['file']} carries no FIXTURE marker")
    if REAL and "FIXTURE" in d:
        raise SystemExit(f"study mode: {c['file']} carries a FIXTURE marker")
    if any(d.get(f) != c[f] for f in ("tag", "tokenizer", "family", "h", "L", "rule", "colouring", "gamma", "K", "N")):
        raise SystemExit(f"{c['file']}: body disagrees with its expected slot")
    cells[c["file"]] = dict(c, L_list=L_OF[c["tag"]], data=d)
LIVE = [c for c in cells.values() if not c["degenerate"] and c["data"].get("N_eff", 0) > 0]
if len(LIVE) != len(EXPECTED):
    raise SystemExit("every cell of this grid must be live (N_eff = N by the body contract)")
BY = {(c["tag"], c["tokenizer"], c["family"], c["h"], c["L"], c["rule"], c["colouring"], c["gamma"]): c for c in LIVE}
LABEL = {sp["tag"]: f"{sp['source']}/{sp['lang']}@{sp['L_cell']}" for sp in SPECS}; TAGS = [sp["tag"] for sp in SPECS]
WIKI256 = [sp["tag"] for sp in SPECS if sp.get("source") == "wikipedia" and sp.get("L_cell") == 256]
LMAX = {sp["tag"]: max(sp["L"]) for sp in SPECS}; ALL_L = sorted({L for sp in SPECS for L in sp["L"]})
G0 = P["gamma"]; K = grid["K"]; N = grid["N"]
manifest = json.loads(pathlib.Path(MANIFEST).read_text()) if MANIFEST and pathlib.Path(MANIFEST).exists() else None
inputs = json.loads((ROOT / INPUTS).read_text()) if REAL else None


def lev(c, a):
    return np.asarray(c["data"]["levels"][str(a)]["level_counts"], dtype=np.float64) / c["data"]["N_eff"]


def tok_label(t):
    return {"llama": "Llama-3.2", "qwen": "Qwen2.5"}.get(t, t)


# ------------------------------------------------------------------ formatting and the value registry
VALUES = {}; USED = set()


def reg(name, value):
    value = str(value); m = re.fullmatch(r"(.+?)–\1", value)
    if m:
        value = m.group(1)
    if name in VALUES and VALUES[name] != value:
        raise SystemExit(f"placeholder {name} registered twice with different values")
    VALUES[name] = value; return VALUES[name]


def fin(x):
    return x is not None and isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x)


def fnum(x, d=None):
    if not fin(x):
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
    return "—" if not fin(x) else fnum(100 * x, d)


def pct(x, d=1):
    return "—" if not fin(x) else f"{100 * x:.{d}f}%"


def ci(lo, hi, f=fnum):
    return f"[{f(lo)}, {f(hi)}]"


def rng_str(vals, f=fnum):
    vals = [v for v in vals if fin(v)]
    return f"{f(min(vals))}–{f(max(vals))}" if vals else "—"


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


def kl_bound_two_sided(abar, mu, Kk):
    return 1.0 if abar == mu else min(1.0, 2.0 * math.exp(-Kk * kl_bern(abar, mu)))


def exact_ref(lv):
    return lv.get("exact_marginal_if_indep_distinct", lv.get("exact_marginal_if_distinct"))


def s1_status_own(c, alpha, pred_key="pred_first_order"):
    d = c["data"]; lv = d["levels"][str(alpha)]; p = lv[pred_key]
    if d["mean_M"] < P["min_mean_M"] or not p["sd_cond"] > 0 or p["theory_share"] < P["min_theory_share"] or p.get("flags"):
        return "ineligible", float("nan"), (float("nan"), float("nan"))
    sd_pred = p["sd_cond"]; lo, hi = [b / sd_pred for b in lv["sd_obs_boot_ci95"]]; ratio = lv["sd_obs_conditional"] / sd_pred
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return "unresolved", ratio, (lo, hi)
    if lo >= BAND[0] and hi <= BAND[1]:
        return "consistent", ratio, (lo, hi)
    if hi < BAND[0] or lo > BAND[1]:
        return "inconsistent", ratio, (lo, hi)
    return "unresolved", ratio, (lo, hi)


def s1_block_own(cs, alpha, pred_key="pred_first_order"):
    st = {c["file"]: s1_status_own(c, alpha, pred_key)[0] for c in cs}
    k = {"candidate": len(cs), "eligible": sum(1 for s in st.values() if s != "ineligible"), "consistent": sum(1 for s in st.values() if s == "consistent"),
         "inconsistent": sum(1 for s in st.values() if s == "inconsistent"), "unresolved": sum(1 for s in st.values() if s == "unresolved")}
    k["resolved"] = k["consistent"] + k["inconsistent"]; share = k["consistent"] / k["resolved"] if k["resolved"] else float("nan")
    return {"counts": k, "status": st, "share": share, "pass": bool(k["resolved"] >= P["min_resolved"] and k["resolved"] > 0 and share >= P["pass_share"])}


def sel_primary(c):
    return c["family"] == P["family"] and c["gamma"] == P["gamma"] and c["colouring"] == P["colouring"] and c["rule"] in P["rules"] and c["h"] in P["h"]


SECONDARY_SEL = {"h0_kgw_indep_g0.25_raw_distinct": (lambda c: c["family"] == "kgw" and c["colouring"] == "independent" and c["gamma"] == G0 and c["rule"] in ("raw", "distinct") and c["h"] == 0, "0.01"),
                 "first_rule_kgw_indep_g0.25": (lambda c: c["family"] == "kgw" and c["colouring"] == "independent" and c["gamma"] == G0 and c["rule"] == "first", "0.01"),
                 "gamma0.5_kgw_indep_raw_distinct": (lambda c: c["family"] == "kgw" and c["colouring"] == "independent" and c["gamma"] == 0.5 and c["rule"] in ("raw", "distinct"), "0.01"),
                 "alpha0.05_primary_cells": (sel_primary, "0.05"), "alpha0.001_primary_cells": (sel_primary, "0.001"),
                 "fixed_h0_kgw": (lambda c: c["family"] == "kgw" and c["colouring"] == "fixed", "0.01"),
                 "gumbel_raw_distinct": (lambda c: c["family"] == "gumbel" and c["rule"] in ("raw", "distinct"), "0.01"), "gumbel_first": (lambda c: c["family"] == "gumbel" and c["rule"] == "first", "0.01")}
BLOCK_LABEL = {"h0_kgw_indep_g0.25_raw_distinct": "h = 0 (raw and distinct; γ = 0.25)", "first_rule_kgw_indep_g0.25": "the first rule (γ = 0.25, every h)", "gamma0.5_kgw_indep_raw_distinct": "γ = 0.5 (raw and distinct, every h)",
               "alpha0.05_primary_cells": "the primary cells at α = 0.05", "alpha0.001_primary_cells": "the primary cells at α = 0.001", "fixed_h0_kgw": "the fixed-size colouring at h = 0 (every rule, both γ)",
               "gumbel_raw_distinct": "Gumbel-max, raw and distinct (every h)", "gumbel_first": "Gumbel-max, the first rule", "unit_sigma_builder": "the unit-σ predictor on the primary cells (computed by the builder; §5)"}


def dep_own(c):
    d = grid["deployer_subset"]
    if c["h"] not in d["h"] or c["rule"] not in d["rules"] or c["family"] not in d["families"]:
        return False
    if d.get("longest_L_only") and c["L"] != LMAX[c["tag"]]:
        return False
    if c["family"] == "kgw" and (c["colouring"] != "independent" or c["gamma"] not in d["kgw_gamma"]):
        return False
    return True


def monotone_own(seq, se, direction):
    for j in range(len(seq) - 1):
        tol = 2 * (se[j] + se[j + 1])
        if direction == "up" and seq[j + 1] < seq[j] - tol:
            return False
        if direction == "down" and seq[j + 1] > seq[j] + tol:
            return False
    return True


def corr_own(x, y):
    if x.std() == 0 or y.std() == 0:
        return None, None
    return float(np.corrcoef(x, y)[0, 1]), float(spearmanr(x, y)[0])


def independent_checks():
    mism = []; chk = {}; R = res["rules"]

    def close(a, b, tol, what):
        if a is None or b is None or not (abs(a - b) <= tol):
            mism.append(f"{what}: own {a!r} vs results {b!r} (tol {tol})")
    # per (cell, alpha): the stored summaries from the integer counts; the KL bound; s0^2 from the 6-decimal mean-score values
    n_lv = 0; max_s0_rel = 0.0
    for c in LIVE:
        d = c["data"]
        for a in ALPHAS:
            lv = d["levels"][a]; v = lev(c, a); n_lv += 1
            close(float(v.mean()), lv["key_mean_level"], 1e-9, f"{c['file']} a={a} key mean"); close(float(v.std(ddof=1)), lv["sd_obs_conditional"], 1e-9, f"{c['file']} a={a} SD")
            close(float(v.max()), lv["max_key"], 1e-12, f"{c['file']} a={a} max"); close(float(v.min()), lv["min_key"], 1e-12, f"{c['file']} a={a} min")
            close(float(np.mean(v > 2 * float(a))), lv["share_keys_above_2alpha"], 1e-12, f"{c['file']} a={a} share2"); close(float(np.mean(v > 5 * float(a))), lv["share_keys_above_5alpha"], 1e-12, f"{c['file']} a={a} share5")
            for q in QUANTILE_KEYS:
                close(float(np.quantile(v, float(q))), lv["quantiles"][q], 1e-9, f"{c['file']} a={a} quantile {q}")
            ex = exact_ref(lv); b = kl_bound_two_sided(float(v.mean()), float(ex), c["K"])
            if not (abs(b - lv["r2_kl_pbound"]) <= 1e-9 * max(1.0, b)):
                mism.append(f"{c['file']} a={a} KL bound own {b} vs file {lv['r2_kl_pbound']}")
        blk = d["q_hat"] if c["family"] == "kgw" else d["s_bar"]; qv = np.asarray(blk["values"], dtype=np.float64); s0_own = float(((qv - blk["exact_mean"]) ** 2).mean())
        tol = 2e-6 * float(np.abs(qv - blk["exact_mean"]).max()) + 1e-12
        close(s0_own, blk["var_known_mean"], tol, f"{c['file']} s0^2 from the 6-decimal values")
        if blk["var_known_mean"] > 0:
            max_s0_rel = max(max_s0_rel, abs(s0_own - blk["var_known_mean"]) / blk["var_known_mean"])
    chk["n_level_blocks_recomputed"] = n_lv; chk["max_rel_diff_s0_from_rounded_values"] = max_s0_rel
    # S1 primary and the secondary blocks
    own = s1_block_own([c for c in LIVE if sel_primary(c)], A_PRIMARY); S1 = R["S1_adequacy"]
    for k in ("candidate", "eligible", "resolved", "consistent", "inconsistent", "unresolved"):
        if own["counts"][k] != S1["counts"][k]:
            mism.append(f"S1 {k}: own {own['counts'][k]} vs results {S1['counts'][k]}")
    if own["pass"] != S1["pass"]:
        mism.append(f"S1 pass: own {own['pass']} vs results {S1['pass']}")
    rows_status = {r["file"]: r["status"] for r in S1["rows"]}
    if rows_status != own["status"]:
        mism.append(f"S1 per-cell statuses differ: {sorted(set(rows_status.items()) ^ set(own['status'].items()))[:5]}")
    chk["S1"] = dict(own["counts"], pass_=own["pass"], share=own["share"])
    sec_own = {name: s1_block_own([c for c in LIVE if sel(c)], a) for name, (sel, a) in SECONDARY_SEL.items()}
    for name, blk in sec_own.items():
        rb = res["secondary_adequacy"].get(name)
        if rb is None:
            mism.append(f"secondary block {name} absent from results.json"); continue
        for k in ("candidate", "eligible", "resolved", "consistent", "inconsistent", "unresolved"):
            if blk["counts"][k] != rb["counts"][k]:
                mism.append(f"secondary {name} {k}: own {blk['counts'][k]} vs results {rb['counts'][k]}")
        if {r["file"]: r["status"] for r in rb["rows"]} != blk["status"]:
            mism.append(f"secondary {name}: per-cell statuses differ")
    if set(res["secondary_adequacy"]) != set(SECONDARY_SEL):
        mism.append(f"secondary block names differ: {sorted(set(res['secondary_adequacy']) ^ set(SECONDARY_SEL))}")
    sec_own["unit_sigma_builder"] = s1_block_own([c for c in LIVE if sel_primary(c)], A_PRIMARY, "pred_unit_sigma")   # the protocol's §6 block the analyzer lacks (builder-only; disclosed)
    chk["secondary"] = {n: dict(b["counts"], share=b["share"]) for n, b in sec_own.items()}
    # S2
    checks2 = []; flagged = []; zeros = 0
    for c in LIVE:
        if c["rule"] != "distinct" or (c["family"] == "kgw" and c["colouring"] != "independent"):
            continue
        for a in ALPHAS:
            lv = c["data"]["levels"][a]; v = lev(c, a); ex = exact_ref(lv)
            if v.max() == 0.0 and ex == 0.0:
                zeros += 1; continue
            checks2.append((c["file"], float(a)))
            if kl_bound_two_sided(float(v.mean()), float(ex), c["K"]) < S2_PBOUND:
                flagged.append((c["file"], float(a)))
    S2 = R["S2_key_mean_audit"]
    for k, v in (("n_checks", len(checks2)), ("structural_zeros", zeros), ("n_flagged", len(flagged))):
        if S2[k] != v:
            mism.append(f"S2 {k}: own {v} vs results {S2[k]}")
    if sorted((x["file"], float(x["alpha"])) for x in S2["flagged"]) != sorted(flagged):
        mism.append("S2 flagged set differs")
    if S2["pass"] != (len(flagged) == 0) or abs(S2["pbound_threshold"] - S2_PBOUND) > 0:
        mism.append("S2 pass or threshold differs")
    for fam in ("kgw", "gumbel"):
        if S2["by_family"][fam]["checks"] != sum(1 for f, _ in checks2 if f.split("__")[2] == fam) or S2["by_family"][fam]["flagged"] != sum(1 for f, _ in flagged if f.split("__")[2] == fam):
            mism.append(f"S2 by_family {fam} differs")
    chk["S2"] = {"n_checks": len(checks2), "structural_zeros": zeros, "n_flagged": len(flagged), "flagged": flagged}
    # S3
    gross = []; cov = []; n3 = 0; z3 = 0; by_col = {}
    for c in LIVE:
        blk = c["data"]["q_hat"] if c["family"] == "kgw" else c["data"]["s_bar"]; ex = blk["exact_var_own_colouring"]; s0 = blk["var_known_mean"]; se = blk["var_known_mean_se"]; tol = blk["r3_tolerance"]
        g = bool(s0 > tol) if blk["structural_zero"] else bool(abs(s0 - ex) > S3_GROSS_SE * se + tol); n3 += 1; z3 += int(blk["structural_zero"])
        by_col.setdefault(c["colouring"], [0, 0]); by_col[c["colouring"]][0] += 1; by_col[c["colouring"]][1] += int(g)
        if g:
            gross.append(c["file"])
        if not blk["structural_zero"]:
            lo, hi = blk["var_boot_ci95"]; cov.append(lo <= ex <= hi)
    S3 = R["S3_identities"]
    for k, v in (("n_checks", n3), ("structural_zeros", z3), ("n_gross", len(gross))):
        if S3[k] != v:
            mism.append(f"S3 {k}: own {v} vs results {S3[k]}")
    if sorted(x["file"] for x in S3["gross"]) != sorted(gross):
        mism.append("S3 gross set differs")
    if S3["pass"] != (len(gross) == 0):
        mism.append("S3 pass differs")
    if S3["coverage_nominal95"] is not None:
        close(float(np.mean(cov)), S3["coverage_nominal95"], 1e-12, "S3 coverage")
    for col, (nn, ng) in by_col.items():
        if S3["by_colouring"][col]["checks"] != nn or S3["by_colouring"][col]["gross"] != ng:
            mism.append(f"S3 by_colouring {col} differs")
    fx_own = {}
    for c in LIVE:
        if c["family"] == "kgw" and c["h"] == 0 and c["colouring"] == "fixed":
            ci_ = BY.get((c["tag"], c["tokenizer"], "kgw", 0, c["L"], c["rule"], "independent", c["gamma"]))
            if ci_ is None:
                continue
            idq = c["data"]["identity_q"]; vf = c["data"]["q_hat"]["var_across_keys"]; vi = ci_["data"]["q_hat"]["var_across_keys"]
            fx_own[(c["tag"], c["tokenizer"], c["gamma"], c["L"], c["rule"])] = {"exact_ratio": idq["exact_ratio_formula"], "reduction": (1.0 / idq["C_cond"] - 1.0) / (c["V"] - 1) if idq["C_cond"] > 0 else None, "observed_ratio": vf / vi if vi > 0 else None, "C_cond": idq["C_cond"]}
    fx_res = {(r["tag"], r["tokenizer"], r["gamma"], r["L"], r["rule"]): r for r in S3["fixed_vs_independent_h0"]}
    if set(fx_own) != set(fx_res):
        mism.append("S3 fixed/independent rows differ")
    for k_, v_ in fx_own.items():
        r_ = fx_res.get(k_)
        if r_:
            for f_ in ("exact_ratio", "reduction", "observed_ratio"):
                if (v_[f_] is None) != (r_[f_] is None) or (v_[f_] is not None and abs(v_[f_] - r_[f_]) > 1e-12 * max(1.0, abs(v_[f_]))):
                    mism.append(f"S3 fixed/independent {k_} {f_} differs")
    chk["S3"] = {"n_checks": n3, "structural_zeros": z3, "n_gross": len(gross), "coverage": float(np.mean(cov)) if cov else None, "n_fixed_rows": len(fx_own)}
    # S4 and S5 (own monotonicity), decided and descriptive
    own4 = {}; own4_desc = {}
    for fam, col, g in (("kgw", "independent", G0), ("gumbel", "uniform", "na"), ("kgw", "independent", 0.5)):
        for rule in grid["rules"]:
            for tag in TAGS:
                for tok in TOKS:
                    for h in HS:
                        ch = sorted([c for c in LIVE if c["tag"] == tag and c["tokenizer"] == tok and c["h"] == h and c["family"] == fam and c["colouring"] == col and c["gamma"] == g and c["rule"] == rule], key=lambda c: c["L"])
                        if len(ch) < 2:
                            continue
                        seq = [c["data"]["levels"][A_PRIMARY]["sd_obs_conditional"] for c in ch]; se = [c["data"]["levels"][A_PRIMARY]["sd_obs_boot_se"] for c in ch]; ok = monotone_own(seq, se, "up")
                        if fam == "kgw" and g == G0 and rule == "raw":
                            own4[(tag, tok, h)] = ok
                        else:
                            own4_desc.setdefault(f"{fam}_g{g}_{rule}", []).append(ok)
    S4 = R["S4_H_length_raw"]; res4 = {(r["tag"], r["tokenizer"], r["h"]): r["holds"] for r in S4["decided"]}
    if own4 != res4:
        mism.append(f"S4 chain decisions differ: {sorted(set(own4.items()) ^ set(res4.items()))[:4]}")
    if S4["n_chains"] != len(own4) or S4["n_holding"] != sum(own4.values()) or S4["all_hold"] != all(own4.values()):
        mism.append("S4 counts differ")
    for key_, oks in own4_desc.items():
        rs = S4["descriptive_summary"].get(key_)
        if rs is None or rs["n_chains"] != len(oks) or rs["n_holding"] != sum(oks):
            mism.append(f"S4 descriptive {key_} differs")
    chk["S4"] = {"n_chains": len(own4), "n_holding": sum(own4.values()), "failing": sorted(k for k, v in own4.items() if not v), "descriptive": {k: [len(v), sum(v)] for k, v in own4_desc.items()}}
    own5 = {}; own5_desc = {}
    for fam, col, g in (("kgw", "independent", G0), ("gumbel", "uniform", "na"), ("kgw", "independent", 0.5)):
        for rule in grid["rules"]:
            for tag in TAGS:
                for tok in TOKS:
                    ch = sorted([c for c in LIVE if c["tag"] == tag and c["tokenizer"] == tok and c["L"] == LMAX[tag] and c["family"] == fam and c["colouring"] == col and c["gamma"] == g and c["rule"] == rule], key=lambda c: c["h"])
                    if len(ch) < 2:
                        continue
                    seq = [c["data"]["levels"][A_PRIMARY]["sd_obs_conditional"] for c in ch]; se = [c["data"]["levels"][A_PRIMARY]["sd_obs_boot_se"] for c in ch]; ok = monotone_own(seq, se, "down")
                    if fam == "kgw" and g == G0 and rule in ("raw", "distinct"):
                        own5[(tag, tok, rule)] = ok
                    else:
                        own5_desc.setdefault(f"{fam}_g{g}_{rule}", []).append(ok)
    S5 = R["S5_H_width"]; res5 = {(r["tag"], r["tokenizer"], r["rule"]): r["holds"] for r in S5["decided"]}
    if own5 != res5:
        mism.append(f"S5 chain decisions differ: {sorted(set(own5.items()) ^ set(res5.items()))[:4]}")
    if S5["n_chains"] != len(own5) or S5["n_holding"] != sum(own5.values()) or S5["all_hold"] != all(own5.values()):
        mism.append("S5 counts differ")
    res5_desc = {}
    for r in S5["descriptive"]:
        res5_desc.setdefault(f"{r['family']}_g{r['gamma']}_{r['rule']}", []).append(r["holds"])
    for key_, oks in own5_desc.items():
        if key_ not in res5_desc or len(res5_desc[key_]) != len(oks) or sum(res5_desc[key_]) != sum(oks):
            mism.append(f"S5 descriptive {key_} differs")
    chk["S5"] = {"n_chains": len(own5), "n_holding": sum(own5.values()), "failing": sorted(k for k, v in own5.items() if not v), "descriptive": {k: [len(v), sum(v)] for k, v in own5_desc.items()}}
    # the deployer subset from the grid, and its rows
    dep_cells = [c for c in LIVE if dep_own(c)]; want = {(c["tag"], c["tokenizer"], c["family"], c["gamma"], c["h"], c["L"], c["rule"], float(a)) for c in dep_cells for a in ALPHAS}
    got = {(r["tag"], r["tokenizer"], r["family"], r["gamma"], r["h"], r["L"], r["rule"], float(r["alpha"])) for r in res["descriptive"]["deployer_view"]}
    if want != got:
        mism.append(f"deployer rows differ: own {len(want)} vs results {len(got)}")
    for r in res["descriptive"]["deployer_view"]:
        c = BY.get((r["tag"], r["tokenizer"], r["family"], r["h"], r["L"], r["rule"], "independent" if r["family"] == "kgw" else "uniform", r["gamma"]))
        if c is None:
            mism.append(f"deployer row without a cell: {r['tag']} {r['tokenizer']} {r['family']} h{r['h']} L{r['L']} {r['rule']}"); continue
        lv = c["data"]["levels"][str(r["alpha"])]
        if r["crossed"] is None or r["crossed"].get("B") != 200 or abs(r["key_mean"] - lv["key_mean_level"]) > 1e-12 or abs(r["max_key"] - lv["max_key"]) > 1e-12 or any(abs(r["quantiles"][q] - lv["quantiles"][q]) > 1e-12 for q in QUANTILE_KEYS):
            mism.append(f"deployer row values differ for {c['file']} a={r['alpha']}")
        if not c["data"].get("deployer_subset"):
            mism.append(f"deployer row on a cell whose stored flag is false: {c['file']}")
    chk["deployer"] = {"n_cells": len(dep_cells), "n_rows": len(want)}
    # correlations (between cells, between tokenizers, the language disparity)
    CR = res["descriptive"]["correlations"]; n_pairs = 0
    for e in CR["between_cells"]:
        cs = {t: BY[(t, e["tokenizer"], e["family"], e["h"], 256, e["rule"], "independent" if e["family"] == "kgw" else "uniform", e["gamma"])] for t in e["tags"]}
        for i, a_ in enumerate(e["tags"]):
            for j, b_ in enumerate(e["tags"]):
                if i >= j:
                    continue
                pr, sr = corr_own(lev(cs[a_], 0.01), lev(cs[b_], 0.01)); n_pairs += 1
                for own_v, res_v, nm in ((pr, e["pearson"][i][j], "pearson"), (sr, e["spearman"][i][j], "spearman")):
                    if (own_v is None) != (res_v is None) or (own_v is not None and abs(own_v - res_v) > 1e-9):
                        mism.append(f"between-cell {nm} differs: {e['tokenizer']} {e['family']} h{e['h']} {e['rule']} {a_}-{b_}")
    if len(CR["between_cells"]) != 2 * len(TOKS) * 3 * 2:
        mism.append(f"between-cell matrices: {len(CR['between_cells'])} (expected {2 * len(TOKS) * 3 * 2})")
    for e in CR["language_disparity"]:
        A = np.stack([lev(BY[(t, e["tokenizer"], e["family"], e["h"], 256, e["rule"], "independent" if e["family"] == "kgw" else "uniform", e["gamma"])], 0.01) for t in e["languages"]])
        mx = A.max(axis=0); mn = A.min(axis=0); pos = mn > 0; ratio = mx[pos] / mn[pos]
        if sorted(e["languages"]) != sorted(WIKI256):
            mism.append("language disparity languages differ from the six Wikipedia @256 cells")
        for own_v, res_v, nm in ((int((mx == 0).sum()), e["n_keys_all_zero"], "all_zero"), (int(((mn == 0) & (mx > 0)).sum()), e["n_keys_some_zero"], "some_zero"), (int(pos.sum()), e["n_keys_all_positive"], "all_positive")):
            if own_v != res_v:
                mism.append(f"language disparity {nm} differs ({e['tokenizer']} {e['family']} h{e['h']} {e['rule']})")
        if pos.any():
            for own_v, res_v, nm in ((float(np.mean(ratio > 2)), e["share_all_positive_keys_ratio_gt2"], "gt2"), (float(np.mean(ratio > 5)), e["share_all_positive_keys_ratio_gt5"], "gt5"), (float(np.median(ratio)), e["median_ratio_all_positive_keys"], "median"), (float(ratio.max()), e["max_ratio_all_positive_keys"], "max")):
                close(own_v, res_v, 1e-9, f"language disparity {nm} ({e['tokenizer']} {e['family']} h{e['h']} {e['rule']})")
    n_tok = 0
    for e in CR["between_tokenizers"]:
        col = "independent" if e["family"] == "kgw" else "uniform"; a_ = BY[(e["tag"], "llama", e["family"], e["h"], e["L"], e["rule"], col, e["gamma"])]; b_ = BY[(e["tag"], "qwen", e["family"], e["h"], e["L"], e["rule"], col, e["gamma"])]
        la, lb = lev(a_, 0.01), lev(b_, 0.01); pr, sr = corr_own(la, lb); n_tok += 1
        close(float(la.std(ddof=1)), e["sd_llama"], 1e-12, "tokenizer sd_llama"); close(float(lb.std(ddof=1)), e["sd_qwen"], 1e-12, "tokenizer sd_qwen")
        if (pr is None) != (e["pearson"] is None) or (pr is not None and abs(pr - e["pearson"]) > 1e-9):
            mism.append(f"tokenizer correlation differs: {e['tag']} {e['family']} h{e['h']} {e['rule']} L{e['L']}")
    chk["correlations"] = {"n_between_cell_matrices": len(CR["between_cells"]), "n_pairs_recomputed": n_pairs, "n_language_blocks": len(CR["language_disparity"]), "n_tokenizer_pairs": n_tok}
    # REAL only: the prediction compared with the outcome is the one disclosed before the lock (INPUTS.json)
    if REAL:
        mx_pred = 0.0; mx_ex = 0.0; mx_rho = 0.0; n_in = 0
        for c in LIVE:
            if c["family"] == "kgw" and c["colouring"] != "independent":
                continue
            rec = inputs["chains"][f"{c['tag']}__{c['tokenizer']}__h{c['h']}__N{c['N']}"]["cells"][f"L{c['L']}__{c['rule']}"]
            r_in = rec["kgw"][str(c["gamma"])] if c["family"] == "kgw" else rec["gumbel"]
            if r_in.get("N_eff", 0) != c["data"]["N_eff"]:
                mism.append(f"INPUTS N_eff differs for {c['file']}"); continue
            close(r_in["mean_M"], c["data"]["mean_M"], 1e-9, f"INPUTS mean M {c['file']}"); mx_rho = max(mx_rho, abs(r_in["rho_bar"] - c["data"]["population"]["rho_bar"]))
            close(r_in["rho_bar"], c["data"]["population"]["rho_bar"], 1e-7 * max(1.0, abs(r_in["rho_bar"])), f"INPUTS rho_bar {c['file']}")
            for a in ALPHAS:
                p_in = r_in["pred"][a]; p_c = c["data"]["levels"][a]["pred_first_order"]; n_in += 1
                for f_ in ("sd_cond", "mean_level", "theory_share"):
                    mx_pred = max(mx_pred, abs(p_in[f_] - p_c[f_])); close(p_in[f_], p_c[f_], 1e-7 * max(1.0, abs(p_in[f_])), f"INPUTS prediction {f_} {c['file']} a={a}")
                if c["family"] == "kgw":
                    ex_in = p_in["exact_binomial_key_mean_if_distinct"]; ex_c = c["data"]["levels"][a]["exact_marginal_if_indep_distinct"]; mx_ex = max(mx_ex, abs(ex_in - ex_c)); close(ex_in, ex_c, 1e-9, f"INPUTS exact key mean {c['file']} a={a}")
        chk["inputs_disclosed_before_lock"] = {"n_predictions_compared": n_in, "max_abs_diff_prediction": mx_pred, "max_abs_diff_exact_key_mean": mx_ex, "max_abs_diff_rho_bar": mx_rho, "inputs_sha256": sha(ROOT / INPUTS), "inputs_sha256_in_lock": lock["hashes"][INPUTS]}
    else:
        chk["inputs_disclosed_before_lock"] = "not checked in fixture mode (the fixture's predictions are planted)"
    if mism:
        (OUTDIR / "checks_FAILED.json").write_text(json.dumps({"mismatches": mism, "checks": chk}, indent=1, default=str))
        raise AssertionError(f"{len(mism)} mismatch(es) between the builder's re-computation and results.json; first: {mism[:5]}")
    (OUTDIR / "checks.json").write_text(json.dumps({"mismatches": [], "checks": chk}, indent=1, default=str))
    return chk, sec_own


CHK, SEC_OWN = independent_checks()

# ------------------------------------------------------------------ registered values and tables
T = {}; R = res["rules"]; S1, S2, S3, S4, S5 = R["S1_adequacy"], R["S2_key_mean_audit"], R["S3_identities"], R["S4_H_length_raw"], R["S5_H_width"]; SEC = res["secondary_adequacy"]; DV = res["descriptive"]
reg("n_cells", res["n_cells"]); reg("n_live", res["n_live"]); reg("K", f"{K:,}"); reg("N", f"{N:,}"); reg("n_corpus", len(TAGS)); reg("n_tok", len(TOKS)); reg("key_start", f"{grid['key_seed_start']:,}"); reg("key_end", f"{grid['key_seed_start'] + K - 1:,}")
reg("label", "FIXTURE (synthetic inventory; not the study)" if FIXTURE else "STUDY"); reg("lock_sha", sha(ROOT / OUT / "PRE_RUN_LOCK.json")[:16] + "…"); reg("results_sha", sha(RES)[:16] + "…")
reg("n_level_blocks_recomputed", CHK["n_level_blocks_recomputed"]); reg("s0_max_rel_diff", f"{CHK['max_rel_diff_s0_from_rounded_values']:.1e}")
reg("conductor", "Claude (Fable 5.1, in Claude Code)"); reg("reviewer", "Codex")
rv_dir = ROOT / "research" / "reviews" / "R06_study2-report"; revs = sorted(rv_dir.glob("REVIEW_*_r*.md")) if rv_dir.exists() else []
if (rv_dir / "RESOLUTION.md").exists():
    reg("r06_status", "agreed (RESOLUTION.md present)")
elif revs:
    vline = next((l.strip() for l in reversed(revs[-1].read_text().splitlines()) if l.strip().startswith("VERDICT:")), "no verdict line"); reg("r06_status", f"open; the latest review on file is {revs[-1].name} ({vline}); this build answers it and is not an approval")
else:
    reg("r06_status", "open; no review on file yet")
if REAL:
    ic = CHK["inputs_disclosed_before_lock"]; reg("inputs_n_pred", f"{ic['n_predictions_compared']:,}"); reg("inputs_max_diff_pred", f"{ic['max_abs_diff_prediction']:.1e}"); reg("inputs_max_diff_exact", f"{ic['max_abs_diff_exact_key_mean']:.1e}"); reg("inputs_max_diff_rho", f"{ic['max_abs_diff_rho_bar']:.1e}")
else:
    for k_ in ("inputs_n_pred", "inputs_max_diff_pred", "inputs_max_diff_exact", "inputs_max_diff_rho"):
        reg(k_, "n/a (fixture)")
# S1
k1 = S1["counts"]
for k_ in k1:
    reg(f"s1_{k_}", k1[k_])
reg("s1_share", pct(S1["consistent_share_of_resolved"])); reg("s1_verdict", "PASS" if S1["pass"] else "FAIL"); reg("s1_min_resolved", P["min_resolved"]); reg("s1_pass_share", pct(P["pass_share"], 0)); reg("s1_min_M", P["min_mean_M"]); reg("s1_min_share", P["min_theory_share"])
rows_el = [r for r in S1["rows"] if r["status"] != "ineligible"]; rat_res = [r["ratio"] for r in rows_el if r["status"] in ("consistent", "inconsistent")]; rat_all = [r["ratio"] for r in rows_el if fin(r["ratio"])]
reg("s1_ratio_min", fnum(min(rat_res)) if rat_res else "—"); reg("s1_ratio_max", fnum(max(rat_res)) if rat_res else "—"); reg("s1_ratio_median", fnum(float(np.median(rat_res))) if rat_res else "—")
reg("s1_ratio_q10", fnum(float(np.quantile(rat_all, 0.1))) if rat_all else "—"); reg("s1_ratio_q90", fnum(float(np.quantile(rat_all, 0.9))) if rat_all else "—"); reg("s1_ratio_median_eligible", fnum(float(np.median(rat_all))) if rat_all else "—")
for h in P["h"]:
    b = S1["by_h"][str(h)]; reg(f"s1_h{h}_eligible", b["consistent"] + b["inconsistent"] + b["unresolved"]); reg(f"s1_h{h}_consistent", b["consistent"]); reg(f"s1_h{h}_candidates", sum(1 for r in S1["rows"] if r["h"] == h))
for ru in P["rules"]:
    b = S1["by_rule"][ru]; reg(f"s1_{ru}_eligible", b["consistent"] + b["inconsistent"] + b["unresolved"]); reg(f"s1_{ru}_consistent", b["consistent"]); reg(f"s1_{ru}_inconsistent", b["inconsistent"]); reg(f"s1_{ru}_unresolved", b["unresolved"])
for t in TOKS:
    b = S1["by_tokenizer"][t]; reg(f"s1_{t}_eligible", b["consistent"] + b["inconsistent"] + b["unresolved"]); reg(f"s1_{t}_consistent", b["consistent"])
# S2
reg("s2_checks", f"{S2['n_checks']:,}"); reg("s2_zeros", S2["structural_zeros"]); reg("s2_flagged", S2["n_flagged"]); reg("s2_verdict", "PASS" if S2["pass"] else "AUDIT FLAG"); reg("s2_min_pbound", fnum(S2["smallest_pbound"]) if fin(S2["smallest_pbound"]) else "—")
reg("s2_union", fnum(S2["union_bound_false_audit"])); nd = S2["normal_diagnostic"]; reg("s2_dev_sd", fnum(nd.get("sd"))); reg("s2_dev_max", fnum(nd.get("max_abs"))); reg("s2_dev_share3", pct(nd.get("share_abs_gt3"), 2)); reg("s2_dev_n", nd.get("n"))
for fam in ("kgw", "gumbel"):
    reg(f"s2_{fam}_checks", f"{S2['by_family'][fam]['checks']:,}"); reg(f"s2_{fam}_flagged", S2["by_family"][fam]["flagged"])
# S3
reg("s3_checks", f"{S3['n_checks']:,}"); reg("s3_zeros", S3["structural_zeros"]); reg("s3_gross", S3["n_gross"]); reg("s3_verdict", "PASS" if S3["pass"] else "FAIL"); reg("s3_coverage", pct(S3["coverage_nominal95"]) if S3["coverage_nominal95"] is not None else "—")
reg("s3_dev_sd", fnum(S3["dev_se_sd"])); reg("s3_dev_max", fnum(S3["dev_se_max_abs"])); reg("s3_n_coverage", S3["n_checks"] - S3["structural_zeros"])
for col in ("independent", "fixed", "uniform"):
    reg(f"s3_{col}_checks", f"{S3['by_colouring'][col]['checks']:,}"); reg(f"s3_{col}_gross", S3["by_colouring"][col]["gross"])
reg("s3_constancy", sum(1 for c in LIVE if (c["data"]["q_hat"] if c["family"] == "kgw" else c["data"]["s_bar"])["observed_sample_constancy"]))
# S4, S5
reg("s4_chains", S4["n_chains"]); reg("s4_holding", S4["n_holding"]); reg("s4_verdict", "PASS" if S4["all_hold"] else "FAIL"); reg("s4_failing_n", len(S4["failing"]))
reg("s4_failing", "; ".join(f"{LABEL[r['tag']]} {tok_label(r['tokenizer'])} h = {r['h']}" for r in S4["failing"]) or "none")
for key_, v in S4["descriptive_summary"].items():
    reg(f"s4_desc_{key_}", f"{v['n_holding']} of {v['n_chains']}")
reg("s5_chains", S5["n_chains"]); reg("s5_holding", S5["n_holding"]); reg("s5_verdict", "PASS" if S5["all_hold"] else "FAIL"); reg("s5_failing_n", len(S5["failing"]))
reg("s5_failing", "; ".join(f"{LABEL[r['tag']]} {tok_label(r['tokenizer'])} {r['rule']}" for r in S5["failing"]) or "none")
for key_, v in CHK["S5"]["descriptive"].items():
    reg(f"s5_desc_{key_}", f"{v[1]} of {v[0]}")

T["rules"] = md_table(["Rule (protocol §9)", "Pre-registered criterion", "Observed", "Verdict"], [
    [f"S1 adequacy of the common-factor predictor on real text (primary; KGW, independent colouring, γ = {G0}, raw and distinct rules, h ∈ {{{', '.join(str(h) for h in P['h'])}}}, every corpus cell, both tokenizers, every length, α = {A_PRIMARY})",
     f"≥ {P['min_resolved']} resolved cells and ≥ {pct(P['pass_share'], 0)} of the resolved cells consistent (key-bootstrap ratio interval inside [{fnum(BAND[0])}, {fnum(BAND[1])}]); eligible when mean M ≥ {P['min_mean_M']}, theory share ≥ {P['min_theory_share']}, no σ² flag",
     f"candidates {k1['candidate']}; eligible {k1['eligible']}; resolved {k1['resolved']}; consistent {k1['consistent']}; inconsistent {k1['inconsistent']}; unresolved {k1['unresolved']}; share consistent {VALUES['s1_share']}", f"**{VALUES['s1_verdict']}**"],
    ["S2 the key-mean audit (distinct rule; KGW independent both γ and Gumbel; every α)", f"no check with a two-sided Hoeffding–KL bound below {S2_PBOUND:g} (per-check false audit ≤ {S2_PBOUND:g}; union bound over the checks)",
     f"{VALUES['s2_checks']} checks ({VALUES['s2_zeros']} structural zeros counted separately; KGW {VALUES['s2_kgw_checks']}, Gumbel {VALUES['s2_gumbel_checks']}); flagged {VALUES['s2_flagged']} (KGW {VALUES['s2_kgw_flagged']}, Gumbel {VALUES['s2_gumbel_flagged']}); smallest bound {VALUES['s2_min_pbound']}; union bound {VALUES['s2_union']}; normal (ā − μ)/SE: SD {VALUES['s2_dev_sd']}, max |·| {VALUES['s2_dev_max']}, share above 3 {VALUES['s2_dev_share3']} (diagnostic)", f"**{VALUES['s2_verdict']}**"],
    ["S3 the exact identities (every live cell; the known-mean variance estimator of q̂ or s̄ against the identity at the realised weights)", f"no gross failure: |s₀² − σ²_exact| ≤ {S3_GROSS_SE:g}·SE + τ; structural zeros ≤ τ",
     f"{VALUES['s3_checks']} checks ({VALUES['s3_zeros']} structural zeros; independent {VALUES['s3_independent_checks']}, fixed {VALUES['s3_fixed_checks']}, Gumbel {VALUES['s3_uniform_checks']}); gross failures {VALUES['s3_gross']}; (s₀² − σ²)/SE: SD {VALUES['s3_dev_sd']}, max |·| {VALUES['s3_dev_max']}; nominal-95% coverage {VALUES['s3_coverage']} of {VALUES['s3_n_coverage']} (diagnostic)", f"**{VALUES['s3_verdict']}**"],
    [f"S4 H-length on the observed dispersion (per chain: corpus cell × tokenizer × h; KGW independent γ = {G0}, raw rule, α = {A_PRIMARY})", "SD_K(α̂) non-decreasing in L within 2(se_L + se_L′) in every chain (the counts are the result)",
     f"{VALUES['s4_chains']} chains; holding {VALUES['s4_holding']}; failing: {VALUES['s4_failing']}", f"**{VALUES['s4_verdict']}**"],
    [f"S5 H-width on the observed dispersion (per chain: corpus cell × tokenizer × rule ∈ {{raw, distinct}} at the longest length; KGW independent γ = {G0}, α = {A_PRIMARY})", "SD_K(α̂) non-increasing in h within 2(se_h + se_h+1) in every chain (the counts are the result)",
     f"{VALUES['s5_chains']} chains; holding {VALUES['s5_holding']}; failing: {VALUES['s5_failing']}", f"**{VALUES['s5_verdict']}**"]])

# S1 by corpus cell and rule; by tokenizer; by h and L
rows = []
for tag in TAGS:
    for ru in P["rules"]:
        rs = [r for r in S1["rows"] if r["tag"] == tag and r["rule"] == ru]; el = [r for r in rs if r["status"] != "ineligible"]; rsv = [r for r in el if r["status"] in ("consistent", "inconsistent")]; rr = [r["ratio"] for r in rsv]
        rows.append([LABEL[tag], ru, len(rs), len(el), len(rsv), sum(1 for r in rsv if r["status"] == "consistent"), sum(1 for r in rsv if r["status"] == "inconsistent"), sum(1 for r in el if r["status"] == "unresolved"),
                     rng_str(rr), fnum(float(np.median(rr))) if rr else "—", ", ".join(str(h) for h in sorted({r["h"] for r in el})) or "—"])
T["s1_by_cell"] = md_table(["Corpus cell", "Rule", "Candidates", "Eligible", "Resolved", "Consistent", "Inconsistent", "Unresolved", "Ratio range (resolved)", "Median ratio", "Widths with eligible cells"], rows) + "\n\nBoth tokenizers pooled; candidates = every length of the cell's chain × h ∈ {1, 2, 3, 4}."
rows = []
for t in TOKS:
    for ru in P["rules"]:
        rs = [r for r in S1["rows"] if r["tokenizer"] == t and r["rule"] == ru]; el = [r for r in rs if r["status"] != "ineligible"]; rsv = [r for r in el if r["status"] in ("consistent", "inconsistent")]; rr = [r["ratio"] for r in rsv]
        rows.append([tok_label(t), ru, len(rs), len(el), len(rsv), sum(1 for r in rsv if r["status"] == "consistent"), sum(1 for r in rsv if r["status"] == "inconsistent"), sum(1 for r in el if r["status"] == "unresolved"), rng_str(rr), fnum(float(np.median(rr))) if rr else "—"])
T["s1_by_tok"] = md_table(["Tokenizer", "Rule", "Candidates", "Eligible", "Resolved", "Consistent", "Inconsistent", "Unresolved", "Ratio range (resolved)", "Median ratio"], rows)
rows = []
for h in P["h"]:
    rs = [r for r in S1["rows"] if r["h"] == h]; el = [r for r in rs if r["status"] != "ineligible"]; rsv = [r for r in el if r["status"] in ("consistent", "inconsistent")]; rr = [r["ratio"] for r in rsv]
    rows.append([f"h = {h}", len(rs), len(el), len(rsv), sum(1 for r in rsv if r["status"] == "consistent"), sum(1 for r in rsv if r["status"] == "inconsistent"), sum(1 for r in el if r["status"] == "unresolved"), rng_str(rr), fnum(float(np.median(rr))) if rr else "—"])
T["s1_by_h"] = md_table(["Width", "Candidates", "Eligible", "Resolved", "Consistent", "Inconsistent", "Unresolved", "Ratio range (resolved)", "Median ratio"], rows) + "\n\nBoth rules, both tokenizers, every corpus cell and length pooled."
hl = {}
for r in S1["rows"]:
    hl.setdefault((r["h"], r["L"]), []).append(r["status"])
rows = []
for h in P["h"]:
    rows.append([f"h = {h}"] + [(f"{sum(1 for s in hl.get((h, L), []) if s == 'consistent')} / {sum(1 for s in hl.get((h, L), []) if s in ('consistent', 'inconsistent'))} / {sum(1 for s in hl.get((h, L), []) if s != 'ineligible')} of {len(hl.get((h, L), []))}" if (h, L) in hl else "—") for L in ALL_L])
T["s1_by_hL"] = md_table(["Width", *[f"L = {L:,}" for L in ALL_L]], rows) + f"\n\nEach entry: consistent / resolved / eligible of the candidate cells (both rules, both tokenizers, every corpus cell whose chain has that length; the @256 cells stop at L = 256). An eligible cell needs mean M ≥ {P['min_mean_M']} and a theory share ≥ {P['min_theory_share']}."


def diag_row(r, block, pred_key="pred_first_order"):
    """One diagnostic row for a non-consistent occurrence, built from the cell file (the block's alpha and predictor)."""
    c = cells[r["file"]]; d = c["data"]; a = str(r["alpha"]); lv = d["levels"][a]; p = lv[pred_key]; sd = lv["sd_obs_conditional"]; sp = p["sd_cond"]
    ratio = sd / sp if sp > 0 else float("nan"); lo, hi = [(b / sp if sp > 0 else float("nan")) for b in lv["sd_obs_boot_ci95"]]
    pw = lv.get("pred_pairwise_gaussian") or {}; het = d.get("covariance_heterogeneity") or {}; q = het.get("pair_corr_quantiles") or {}
    r1 = sd / pw["sd_cond"] if pw.get("sd_cond", 0) > 0 else float("nan"); r2 = sd / pw["sd_cond_replicate"] if pw.get("sd_cond_replicate") else float("nan")
    return [BLOCK_LABEL.get(block, "primary"), LABEL[c["tag"]], tok_label(c["tokenizer"]), c["family"], c["rule"], c["h"], c["L"], c["colouring"], c["gamma"], a, r["status"], f"{fnum(ratio)} {ci(lo, hi)}", fnum(100 * sd), fnum(100 * sp),
            fnum(d["population"]["sd_zshift_pop"]), fnum(d["mean_M"], 0), fnum(p["theory_share"]), f"{fnum(p['sigma2'])} / {fnum(d['population']['sigma_model2'])} / {fnum(d['z_var_within_key']['mean_over_keys'])}",
            f"{pp(lv['key_mean_level'])} / {pp(p['mean_level'])} / {pp(exact_ref(lv))}", f"{fnum(r1)} / {fnum(r2)}", fnum(100 * pw["subsample_sd_difference"]) if pw.get("subsample_sd_difference") is not None else "—", fnum(het.get("pair_cov_cv")),
            f"{fnum(q.get('0.5'))} / {fnum(q.get('0.9'))} / {fnum(q.get('0.99'))} / {fnum(het.get('pair_corr_max'))}", fnum(lv.get("ratio_obs_over_pred_simulated_shift")), fnum(sd / lv["pred_unit_sigma"]["sd_cond"]) if lv["pred_unit_sigma"]["sd_cond"] > 0 else "—",
            f"{sum(1 for k_ in lv['level_counts'] if k_ == 0)} / {sum(1 for k_ in lv['level_counts'] if k_ == d['N_eff'])} / {len(set(lv['level_counts']))} / {sum(1 for k_ in lv['level_counts'] if k_ > 5 * float(a) * d['N_eff'])}"]


DIAG_HEAD = ["Block", "Corpus cell", "Tokenizer", "Family", "Rule", "h", "L", "Colouring", "γ", "α", "Status", "Ratio [95% CI]", "SD obs (pp)", "SD pred (pp)", "σ_δ = √ρ̄", "Mean M", "Theory share", "σ² predictor / identities / observed",
             "Key-mean level obs / pred / exact-binomial (%)", "Pairwise ratio, subsample 1 / 2", "Pairwise subsampling difference (pp)", "Pair-cov CV", "Pair-corr q50 / q90 / q99 / max", "Simulated-shift ratio", "Unit-σ ratio", "Keys at 0 / at 1 / distinct levels / keys > 5α"]
prim_rows = [diag_row(r, "primary") for r in sorted(S1["non_consistent_rows"], key=lambda r: (r["status"], r["tag"], r["tokenizer"], r["rule"], r["h"], r["L"]))]
T["s1_failures"] = md_table(DIAG_HEAD, prim_rows) if prim_rows else "_No inconsistent or unresolved eligible cell in the primary block._"
reg("s1_n_failure_rows", len(prim_rows))
sup = list(prim_rows); occ = {}
for name, blk in SEC.items():
    for r in blk["rows"]:
        if r["status"] in ("inconsistent", "unresolved"):
            sup.append(diag_row(r, name)); occ.setdefault(r["file"], []).append(name)
n_unit_rows = 0
for f_, st_ in sorted(SEC_OWN["unit_sigma_builder"]["status"].items()):
    if st_ in ("inconsistent", "unresolved"):
        sup.append(diag_row({"file": f_, "alpha": A_PRIMARY, "status": st_}, "unit_sigma_builder", "pred_unit_sigma")); occ.setdefault(f_, []).append("unit_sigma_builder"); n_unit_rows += 1
(OUTDIR / "tables_s1_diagnostics_full.md").write_text("# Study 2 — every inconsistent or unresolved occurrence of the primary block, the analyzer's eight secondary blocks and the builder's unit-σ block, with the protocol's diagnostics\n\nGenerated by `research/study2/s2_report.py` from the cell files (the block's α and predictor, so the ratio and interval columns of the unit-σ rows are the unit-σ predictor's; both pairwise subsamples; the simulated-shift and unit-σ ratios; the key-count resolution).\n\n" + (md_table(DIAG_HEAD, sup) if sup else "_None._") + "\n")
reg("n_diag_rows", len(sup)); reg("n_diag_rows_unit", n_unit_rows); reg("n_sec_unresolved_total", sum(b["counts"]["unresolved"] for b in SEC.values())); reg("n_sec_inconsistent_total", sum(b["counts"]["inconsistent"] for b in SEC.values()))
# secondary blocks (the analyzer's eight, then the builder's unit-sigma block)
rows = [["**primary: KGW independent, γ = 0.25, raw and distinct, h ≥ 1, α = 0.01**", k1["candidate"], k1["eligible"], k1["resolved"], k1["consistent"], k1["inconsistent"], k1["unresolved"], VALUES["s1_share"], VALUES["s1_ratio_median"], f"{VALUES['s1_ratio_min']}–{VALUES['s1_ratio_max']}"]]
for name, blk in SEC.items():
    kk = blk["counts"]; rr = [r["ratio"] for r in blk["rows"] if r["status"] in ("consistent", "inconsistent")]
    rows.append([BLOCK_LABEL[name], kk["candidate"], kk["eligible"], kk["resolved"], kk["consistent"], kk["inconsistent"], kk["unresolved"], pct(kk["consistent"] / kk["resolved"]) if kk["resolved"] else "—", fnum(float(np.median(rr))) if rr else "—", rng_str(rr)])
    for k_ in ("candidate", "eligible", "resolved", "consistent", "inconsistent", "unresolved"):
        reg(f"sec_{name}_{k_}", kk[k_])
    reg(f"sec_{name}_share", pct(kk["consistent"] / kk["resolved"]) if kk["resolved"] else "—"); reg(f"sec_{name}_ratio_median", fnum(float(np.median(rr))) if rr else "—"); reg(f"sec_{name}_ratio_range", rng_str(rr))
    re_ = [r["ratio"] for r in blk["rows"] if r["status"] != "ineligible" and fin(r["ratio"])]; reg(f"sec_{name}_ratio_median_eligible", fnum(float(np.median(re_))) if re_ else "—")
us = SEC_OWN["unit_sigma_builder"]; ku = us["counts"]; rr = [s1_status_own(cells[f], A_PRIMARY, "pred_unit_sigma")[1] for f, s in us["status"].items() if s in ("consistent", "inconsistent")]
rows.append([BLOCK_LABEL["unit_sigma_builder"], ku["candidate"], ku["eligible"], ku["resolved"], ku["consistent"], ku["inconsistent"], ku["unresolved"], pct(us["share"]) if ku["resolved"] else "—", fnum(float(np.median(rr))) if rr else "—", rng_str(rr)])
for k_ in ("candidate", "eligible", "resolved", "consistent", "inconsistent", "unresolved"):
    reg(f"sec_unit_{k_}", ku[k_])
reg("sec_unit_share", pct(us["share"]) if ku["resolved"] else "—"); reg("sec_unit_ratio_median", fnum(float(np.median(rr))) if rr else "—")
T["secondary"] = md_table(["Block (descriptive; the same statistic)", "Candidates", "Eligible", "Resolved", "Consistent", "Inconsistent", "Unresolved", "Share consistent", "Median ratio", "Ratio range (resolved)"], rows)
# the pairwise and simulated-shift predictors beside the common-factor one, on the eligible primary cells
pr_ = [r for r in rows_el if r["ratio_pairwise"] is not None and fin(r["ratio_pairwise"])]; ss_ = [r for r in rows_el if fin(r["ratio_simulated_shift"])]
rows_rs = [r for r in rows_el if r["status"] in ("consistent", "inconsistent")]
reg("pair_ratio_median_resolved", fnum(float(np.median([r["ratio_pairwise"] for r in rows_rs if r["ratio_pairwise"] is not None and fin(r["ratio_pairwise"])])))); reg("ss_ratio_median_resolved", fnum(float(np.median([r["ratio_simulated_shift"] for r in rows_rs if fin(r["ratio_simulated_shift"])])))); reg("n_resolved_primary", len(rows_rs))
reg("pair_n", len(pr_)); reg("pair_ratio_median", fnum(float(np.median([r["ratio_pairwise"] for r in pr_]))) if pr_ else "—"); reg("pair_ratio_q10", fnum(float(np.quantile([r["ratio_pairwise"] for r in pr_], 0.1))) if pr_ else "—"); reg("pair_ratio_q90", fnum(float(np.quantile([r["ratio_pairwise"] for r in pr_], 0.9))) if pr_ else "—")
reg("pair_in_band", sum(1 for r in pr_ if BAND[0] <= r["ratio_pairwise"] <= BAND[1])); reg("cf_in_band_point", sum(1 for r in rows_el if fin(r["ratio"]) and BAND[0] <= r["ratio"] <= BAND[1])); reg("pair_closer_n", sum(1 for r in pr_ if abs(r["ratio_pairwise"] - 1) < abs(r["ratio"] - 1)))
reg("ss_n", len(ss_)); reg("ss_ratio_median", fnum(float(np.median([r["ratio_simulated_shift"] for r in ss_]))) if ss_ else "—"); reg("ss_closer_n", sum(1 for r in ss_ if abs(r["ratio_simulated_shift"] - 1) < abs(r["ratio"] - 1)))
het_cv = [r["heterogeneity"]["pair_cov_cv"] for r in rows_el if r.get("heterogeneity") and fin(r["heterogeneity"].get("pair_cov_cv"))]; reg("het_cv_median", fnum(float(np.median(het_cv))) if het_cv else "—"); reg("het_cv_max", fnum(max(het_cv)) if het_cv else "—")
h0b = SEC["h0_kgw_indep_g0.25_raw_distinct"]; h0rows = [r for r in h0b["rows"] if r["status"] != "ineligible"]
for ru in ("raw", "distinct"):
    rs = [r for r in h0rows if r["rule"] == ru]; reg(f"h0_{ru}_n_eligible", len(rs)); reg(f"h0_{ru}_ratio_range", rng_str([r["ratio"] for r in rs])); reg(f"h0_{ru}_ratio_median", fnum(float(np.median([r["ratio"] for r in rs]))) if rs else "—")
    reg(f"h0_{ru}_ss_ratio_range", rng_str([r["ratio_simulated_shift"] for r in rs])); reg(f"h0_{ru}_ss_closer_n", sum(1 for r in rs if fin(r["ratio_simulated_shift"]) and abs(r["ratio_simulated_shift"] - 1) < abs(r["ratio"] - 1)))
    reg(f"h0_{ru}_n_consistent", sum(1 for r in rs if r["status"] == "consistent")); reg(f"h0_{ru}_n_inconsistent", sum(1 for r in rs if r["status"] == "inconsistent")); reg(f"h0_{ru}_n_unresolved", sum(1 for r in rs if r["status"] == "unresolved"))
# S2 and S3 detail
flag_rows = [[x["file"], x["alpha"], x["K"], pp(x["key_mean"], 3), pp(x["exact"], 3), fnum(x["kl_pbound"]), fnum(x["normal_dev_se"])] for x in S2["flagged"]]
T["s2_flagged"] = md_table(["Cell", "α", "K", "Key-mean level (%)", "Exact given the texts (%)", "Two-sided KL bound", "(ā − μ)/SE"], flag_rows) if flag_rows else "_No flagged check._"
gross_rows = [[x["file"], fnum(x["observed"]), fnum(x["exact"]), fnum(x["se"]), fnum(x["tol"]), fnum(x.get("dev_se")), "yes" if x["structural_zero"] else "no"] for x in S3["gross"]]
T["s3_gross"] = md_table(["Cell", "s₀² observed", "σ²_exact", "SE", "τ", "(s₀² − σ²)/SE", "Structural zero"], gross_rows) if gross_rows else "_No gross failure._"
s2x = sorted([x for x in S2.get("flagged", [])], key=lambda x: x["kl_pbound"])
# the largest S2 deviations and the dead-detector regime, from the cells
r2x = []
for c in LIVE:
    if c["rule"] != "distinct" or (c["family"] == "kgw" and c["colouring"] != "independent"):
        continue
    for a in ALPHAS:
        lv = c["data"]["levels"][a]; ex = exact_ref(lv)
        if lv["max_key"] == 0.0 and ex == 0.0:
            continue
        se = lv["se_conditional_on_texts"]; r2x.append(((lv["key_mean_level"] - ex) / se if se > 0 else float("inf"), c, a, lv))
fin2 = [x for x in r2x if np.isfinite(x[0])]; mx2 = max(fin2, key=lambda t: abs(t[0])) if fin2 else None
if mx2:
    reg("s2_maxdev_cell", f"{LABEL[mx2[1]['tag']]}, {tok_label(mx2[1]['tokenizer'])}, {mx2[1]['family']}{'' if mx2[1]['family'] == 'gumbel' else f' γ = {mx2[1]['gamma']}'}, h = {mx2[1]['h']}, L = {mx2[1]['L']}, α = {mx2[2]}"); reg("s2_maxdev_value", fnum(mx2[0]))
    reg("s2_maxdev_mean", pct(mx2[3]["key_mean_level"], 3)); reg("s2_maxdev_exact", pct(exact_ref(mx2[3]), 3)); reg("s2_maxdev_bound", fnum(mx2[3]["r2_kl_pbound"]))
dead = [x for x in r2x if not np.isfinite(x[0])]; reg("s2_dead_n", len(dead)); reg("s2_dead_cells", "; ".join(f"{LABEL[x[1]['tag']]} {tok_label(x[1]['tokenizer'])} {x[1]['family']} h = {x[1]['h']} L = {x[1]['L']} α = {x[2]} (exact mean {pct(exact_ref(x[3]), 3)})" for x in dead[:12]) + (" …" if len(dead) > 12 else "") or "none")
# S4 and S5 grids and the failing chains
dec4 = {(r["tag"], r["tokenizer"], r["h"]): r for r in S4["decided"]}
rows = [[LABEL[tag], tok_label(tok)] + [("holds" if dec4[(tag, tok, h)]["holds"] else f"FAILS at L = {', '.join(str(dec4[(tag, tok, h)]['L'][j + 1]) for j in dec4[(tag, tok, h)]['violations_at'])}") if (tag, tok, h) in dec4 else "—" for h in HS] for tag in TAGS for tok in TOKS]
T["s4_grid"] = md_table(["Corpus cell", "Tokenizer", *[f"h = {h}" for h in HS]], rows) + f"\n\nS4 per chain (KGW independent γ = {G0}, raw rule, α = {A_PRIMARY}): the observed across-key SD of the level non-decreasing along the cell's length chain within 2(se_L + se_L′)."
rows = []
for r in S4["failing"]:
    rows.append([LABEL[r["tag"]], tok_label(r["tokenizer"]), r["h"], ", ".join(str(L) for L in r["L"]), " → ".join(f"{pp(s)} ± {pp(e)}" for s, e in zip(r["sd_obs"], r["se"])), " → ".join(fnum(x) for x in r["rho_bar"]), " → ".join(fnum(x, 0) for x in r["mean_M"])])
T["s4_failing"] = md_table(["Corpus cell", "Tokenizer", "h", "L chain", "SD of the level (pp) ± key-bootstrap SE, along L", "ρ̄ along L", "Mean M along L"], rows) if rows else "_No failing S4 chain._"
rows = [[f"{k_.split('_g')[0]}", k_.split('_g')[1].rsplit('_', 1)[0], k_.rsplit('_', 1)[1], v["n_chains"], v["n_holding"]] for k_, v in S4["descriptive_summary"].items()]
T["s4_descriptive"] = md_table(["Family", "γ", "Rule", "Chains", "Non-decreasing within the tolerance"], rows) + "\n\nThe same monotonicity statement under the other rules, γ = 0.5 and the Gumbel family (descriptive; saturation and non-monotonicity are allowed there; protocol §9)."
dec5 = {(r["tag"], r["tokenizer"], r["rule"]): r for r in S5["decided"]}
rows = [[LABEL[tag], tok_label(tok)] + [("holds" if dec5[(tag, tok, ru)]["holds"] else f"FAILS at h = {', '.join(str(dec5[(tag, tok, ru)]['h'][j + 1]) for j in dec5[(tag, tok, ru)]['violations_at'])}") if (tag, tok, ru) in dec5 else "—" for ru in ("raw", "distinct")] for tag in TAGS for tok in TOKS]
T["s5_grid"] = md_table(["Corpus cell", "Tokenizer", "raw rule", "distinct rule"], rows) + f"\n\nS5 per chain (KGW independent γ = {G0}, the cell's longest length, α = {A_PRIMARY}): the observed across-key SD of the level non-increasing in h within 2(se_h + se_h+1)."
rows = []
for r in S5["failing"]:
    rows.append([LABEL[r["tag"]], tok_label(r["tokenizer"]), r["rule"], r["L"], " → ".join(f"{pp(s)} ± {pp(e)}" for s, e in zip(r["sd_obs"], r["se"])), " → ".join(fnum(x) for x in r["A_between"]), " → ".join(fnum(x) for x in r["rho_bar"]), " → ".join(fnum(x, 0) for x in r["mean_M"])])
T["s5_failing"] = md_table(["Corpus cell", "Tokenizer", "Rule", "L", "SD of the level (pp) ± SE, h = 0 → 4", "Ã(h)", "ρ̄(h)", "Mean M(h)"], rows) if rows else "_No failing S5 chain._"
rows = [[k_.split('_g')[0], k_.split('_g')[1].rsplit('_', 1)[0], k_.rsplit('_', 1)[1], v[0], v[1]] for k_, v in CHK["S5"]["descriptive"].items()]
T["s5_descriptive"] = md_table(["Family", "γ", "Rule", "Chains", "Non-increasing within the tolerance"], rows) + "\n\nThe same statement under the first rule, γ = 0.5 and the Gumbel family (descriptive)."
# curves against L at h = 1 (KGW gamma 0.25, alpha 0.01), observed / predicted; the full file carries every h, both families and gamma 0.5


def curve_rows(h, fam, g, col, rules, what):
    rows = []
    for tag in TAGS:
        for tok in TOKS:
            for ru in rules:
                vals = []
                for L in ALL_L:
                    c = BY.get((tag, tok, fam, h, L, ru, col, g))
                    if c is None:
                        vals.append("—"); continue
                    lv = c["data"]["levels"][A_PRIMARY]
                    vals.append(f"{pp(lv['sd_obs_conditional'])} / {pp(lv['pred_first_order']['sd_cond'])}" if what == "sd" else f"{fnum(c['data']['population']['rho_bar'])} ({fnum(c['data']['mean_M'], 0)})")
                rows.append([LABEL[tag], tok_label(tok), ru] + vals)
    return rows


T["curves_h1"] = md_table(["Corpus cell", "Tokenizer", "Rule", *[f"L = {L:,}" for L in ALL_L]], curve_rows(1, "kgw", G0, "independent", grid["rules"], "sd")) + f"\n\nEach entry: observed / predicted across-key SD of the per-key level at α = {A_PRIMARY} (percentage points), KGW γ = {G0}, independent colouring, h = 1; the @256 cells stop at L = 256."
full = [f"# Study 2 — the complete dispersion curves (every corpus cell, tokenizer, width and rule; α = {A_PRIMARY})", "", "Generated by `research/study2/s2_report.py` from the cell files. Each entry: observed / predicted across-key SD of the per-key level (pp); then ρ̄ (mean M)."]
for fam, g, col, name in (("kgw", G0, "independent", f"KGW γ = {G0}"), ("kgw", 0.5, "independent", "KGW γ = 0.5"), ("gumbel", "na", "uniform", "Gumbel-max")):
    for h in HS:
        full += ["", f"## {name}, h = {h}", "", md_table(["Corpus cell", "Tokenizer", "Rule", *[f"L = {L:,}" for L in ALL_L]], curve_rows(h, fam, g, col, grid["rules"], "sd")), "", md_table(["Corpus cell", "Tokenizer", "Rule", *[f"ρ̄ (M) at L = {L:,}" for L in ALL_L]], curve_rows(h, fam, g, col, grid["rules"], "rho"))]
(OUTDIR / "tables_curves_full.md").write_text("\n".join(full) + "\n")
# width at the longest length
rows = []
for tag in TAGS:
    for tok in TOKS:
        vals = []
        for h in HS:
            cr = BY.get((tag, tok, "kgw", h, LMAX[tag], "raw", "independent", G0)); cd = BY.get((tag, tok, "kgw", h, LMAX[tag], "distinct", "independent", G0))
            vals.append(f"{pp(cr['data']['levels'][A_PRIMARY]['sd_obs_conditional']) if cr else '—'} / {pp(cd['data']['levels'][A_PRIMARY]['sd_obs_conditional']) if cd else '—'}")
        rows.append([LABEL[tag], tok_label(tok), f"{LMAX[tag]:,}"] + vals)
T["width_sd"] = md_table(["Corpus cell", "Tokenizer", "L", *[f"h = {h}" for h in HS]], rows) + f"\n\nObserved across-key SD of the per-key level at α = {A_PRIMARY} (pp), raw / distinct rule, KGW γ = {G0}, independent colouring, at the cell's longest length."
rows = []
for tag in TAGS:
    for tok in TOKS:
        vals = []
        for h in HS:
            c = BY.get((tag, tok, "kgw", h, LMAX[tag], "raw", "independent", G0)); vals.append(f"{fnum(c['data']['population']['A_q_between'])} ({fnum(c['data']['population']['rho_bar'])})" if c else "—")
        rows.append([LABEL[tag], tok_label(tok), f"{LMAX[tag]:,}"] + vals)
T["width_A"] = md_table(["Corpus cell", "Tokenizer", "L", *[f"h = {h}" for h in HS]], rows) + f"\n\nÃ(h), the between-text collision of the retained-tuple weights under the raw rule (ρ̄ in parentheses), KGW γ = {G0}, at the cell's longest length."
# the deployer's view (alpha 0.01, h = 1, longest L) for KGW and Gumbel; the full file carries every deployer cell and alpha
dep_rows = DV["deployer_view"]


def dep_table(fam, h, a):
    rows = []
    for tag in TAGS:
        for tok in TOKS:
            for ru in ("raw", "distinct"):
                r = next((x for x in dep_rows if x["tag"] == tag and x["tokenizer"] == tok and x["family"] == fam and x["h"] == h and x["rule"] == ru and float(x["alpha"]) == a), None)
                if r is None:
                    continue
                c = BY[(tag, tok, fam, h, r["L"], ru, "independent" if fam == "kgw" else "uniform", r["gamma"])]; lv = c["data"]["levels"][str(a)]; cr = r["crossed"]
                def cc(k_):
                    return ci(100 * cr[k_]["ci95"][0], 100 * cr[k_]["ci95"][1]) if cr and k_ in cr else "—"
                rows.append([LABEL[tag], tok_label(tok), ru, f"{r['L']:,}", fnum(c["data"]["mean_M"], 0), f"{K:,} / {c['data']['N_eff']:,}", pp(r["key_mean"], 2), f"{pp(r['quantiles']['0.01'], 2)} {cc('q0.01')}", f"{pp(r['quantiles']['0.05'], 2)} {cc('q0.05')}", f"{pp(r['quantiles']['0.5'], 2)} {cc('q0.5')}", f"{pp(r['quantiles']['0.95'])} {cc('q0.95')}", f"{pp(r['quantiles']['0.99'])} {cc('q0.99')}",
                             f"{pp(r['max_key'])} {cc('max')}", f"{pct(r['share_2alpha'])} {cc('share2')}", f"{pct(r['share_5alpha'])} {cc('share5')}", f"{pp(lv['sd_obs_conditional'])} {ci(100 * lv['sd_obs_boot_ci95'][0], 100 * lv['sd_obs_boot_ci95'][1])}"])
    return rows


DEP_HEAD = ["Corpus cell", "Tokenizer", "Rule", "L", "Mean M", "K / N_eff", "Key-mean (%)", "1% key (%) [crossed 95% CI]", "5% key (%) [CI]", "Median key (%) [CI]", "95% key (%) [CI]", "99% key (%) [CI]", "Worst sampled key (%) [CI]", "Keys > 2α [CI, in %]", "Keys > 5α [CI, in %]", "SD of the level (pp) [key-bootstrap 95% CI]"]


def dep_note(a, h):
    return f"\n\nPer-key false-positive levels at α = {a} over the K = {K:,} production keys on the N_eff = N = {N:,} realised texts of each corpus cell (the nominal level is {100 * float(a):g}%); h = {h}, the cell's longest length. The 1%, 5%, 50%, 95% and 99% key quantiles, the worst sampled key and the shares carry their crossed key-by-document bootstrap intervals (200 resamples of texts and keys; the worst key's interval is the sampled maximum's under resampling, never a population extreme; gate constraint 12); the SD carries its key-bootstrap interval conditional on the texts."


T["deployer_kgw"] = md_table(DEP_HEAD, dep_table("kgw", 1, 0.01)) + dep_note("0.01", 1) + f" KGW, γ = {G0}, independent colouring."
T["deployer_gumbel"] = md_table(DEP_HEAD, dep_table("gumbel", 1, 0.01)) + dep_note("0.01", 1) + " Gumbel-max (the per-text Gamma threshold)."
full = ["# Study 2 — the deployer's view in full (every deployer-subset cell, every α)", "", f"Generated by `research/study2/s2_report.py`. K = {K:,} keys and N_eff = N = {N:,} texts in every row (also stated per row); the crossed key-by-document intervals in brackets."]
for fam in ("kgw", "gumbel"):
    for h in grid["deployer_subset"]["h"]:
        for a in grid["alpha"]:
            full += ["", f"## {fam}, h = {h}, α = {a}", "", md_table(DEP_HEAD, dep_table(fam, h, float(a))) + dep_note(str(a), h)]
(OUTDIR / "tables_deployer_full.md").write_text("\n".join(full) + "\n")
dk = [x for x in dep_rows if x["family"] == "kgw" and float(x["alpha"]) == 0.01]
for ru in ("raw", "distinct"):
    for h in grid["deployer_subset"]["h"]:
        rs = [x for x in dk if x["rule"] == ru and x["h"] == h]
        reg(f"dep_{ru}_h{h}_median_range", rng_str([x["quantiles"]["0.5"] for x in rs], lambda v: pct(v, 2))); reg(f"dep_{ru}_h{h}_q99_range", rng_str([x["quantiles"]["0.99"] for x in rs], pct)); reg(f"dep_{ru}_h{h}_worst_range", rng_str([x["max_key"] for x in rs], pct))
        reg(f"dep_{ru}_h{h}_share2_range", rng_str([x["share_2alpha"] for x in rs], pct)); reg(f"dep_{ru}_h{h}_share5_range", rng_str([x["share_5alpha"] for x in rs], pct)); reg(f"dep_{ru}_h{h}_keymean_range", rng_str([x["key_mean"] for x in rs], lambda v: pct(v, 2)))
for ru in ("raw", "distinct"):
    bel = []; mn = []
    for x in dk:
        if x["rule"] == ru and x["h"] == 1:
            c = BY[(x["tag"], x["tokenizer"], "kgw", 1, x["L"], ru, "independent", G0)]; v = lev(c, 0.01); bel.append(int((v < 0.01).sum())); mn.append(float(v.min()))
    reg(f"dep_{ru}_h1_keys_below_nominal_range", rng_str(bel, lambda v: fnum(v, 0))); reg(f"dep_{ru}_h1_min_key_range", rng_str(mn, lambda v: pct(v, 2)))
dg = [x for x in dep_rows if x["family"] == "gumbel" and float(x["alpha"]) == 0.01]
for ru in ("raw", "distinct"):
    rs = [x for x in dg if x["rule"] == ru and x["h"] == 1]
    reg(f"depg_{ru}_h1_q99_range", rng_str([x["quantiles"]["0.99"] for x in rs], pct)); reg(f"depg_{ru}_h1_worst_range", rng_str([x["max_key"] for x in rs], pct)); reg(f"depg_{ru}_h1_share2_range", rng_str([x["share_2alpha"] for x in rs], pct)); reg(f"depg_{ru}_h1_keymean_range", rng_str([x["key_mean"] for x in rs], lambda v: pct(v, 2)))
wk = [(c["data"]["levels"][A_PRIMARY]["max_key"], c) for c in LIVE if c["family"] == "kgw" and c["colouring"] == "independent" and c["gamma"] == G0]
m_ = max(wk, key=lambda t: t[0]); reg("worst_key_level", pct(m_[0])); reg("worst_key_cell", f"{LABEL[m_[1]['tag']]}, {tok_label(m_[1]['tokenizer'])}, {m_[1]['rule']} rule, h = {m_[1]['h']}, L = {m_[1]['L']}")
reg("n_kgw_g025_cells", len(wk)); reg("n_cells_any_key_above_2alpha", sum(1 for _, c in wk if c["data"]["levels"][A_PRIMARY]["share_keys_above_2alpha"] > 0))
# the population diagnostic (protocol §3, §7): the two-way estimate s_K^2 - MS_E/N_eff against the predictor's population variance, every live cell and alpha
def pop_rows(sel, a):
    out = []
    for c in LIVE:
        if not sel(c):
            continue
        lv = c["data"]["levels"][a]; pe = lv["population_est"]; vm = lv["pred_first_order"]["var_pop"]
        out.append({"c": c, "a": a, "twoway": pe["var_pop_signed"], "se": pe["var_pop_boot_se"], "mixture": vm, "ratio": (pe["var_pop_signed"] / vm) if vm > 0 else None, "within2": (abs(pe["var_pop_signed"] - vm) <= 2 * pe["var_pop_boot_se"]) if vm > 0 else None,
                    "sd_pop_obs": pe["sd_pop"], "sd_cond_obs": lv["sd_obs_conditional"], "floor_part": lv["pred_first_order"]["floor"]})
    return out


rows = []
for fam, col, g, name in (("kgw", "independent", G0, "KGW γ = 0.25"), ("kgw", "independent", 0.5, "KGW γ = 0.5"), ("kgw", "fixed", None, "KGW fixed (h = 0)"), ("gumbel", "uniform", "na", "Gumbel-max")):
    for ru in grid["rules"]:
        for h in HS:
            pr = pop_rows(lambda c: c["family"] == fam and c["colouring"] == col and (g is None or c["gamma"] == g) and c["rule"] == ru and c["h"] == h, A_PRIMARY)
            ok = [r for r in pr if r["ratio"] is not None]
            if not pr:
                continue
            rows.append([name, ru, h, len(pr), len(ok), fnum(float(np.median([r["ratio"] for r in ok]))) if ok else "—", rng_str([r["ratio"] for r in ok]), sum(1 for r in ok if r["within2"]), sum(1 for r in pr if r["twoway"] < 0)])
T["population"] = md_table(["Family", "Rule", "h", "Cells", "With a positive mixture variance", "Ratio two-way / mixture, median", "Range", "Within 2 bootstrap SEs", "Negative two-way estimates"], rows) + \
    f"\n\nThe secondary population target (protocol §3): the two-way decomposition s_K² − MS_E/N_eff of the per-key levels (texts random; a two-way bootstrap SE, 100 resamples) against the predictor's population variance Var(α_k) (the mixture without the finite-text floor), at α = {A_PRIMARY}, every live cell of the setting. Descriptive; noisy where the across-key variance is small (Study 1 §5)."
full = [f"# Study 2 — the population diagnostic in full (every live cell, every α)", "", "Generated by `research/study2/s2_report.py` from the cell files: the two-way estimate s_K² − MS_E/N_eff with its two-way bootstrap SE, the predictor's population variance, their ratio, and the conditional SD beside the population SD."]
for a in ALPHAS:
    pr = pop_rows(lambda c: True, a)
    full += ["", f"## α = {a}", "", md_table(["Cell file", "Two-way estimate", "Bootstrap SE", "Predictor Var(α_k)", "Ratio", "Within 2 SE", "SD_pop observed (pp)", "SD_cond observed (pp)", "Floor (predictor)"],
                                           [[r["c"]["file"], f"{r['twoway']:.3e}", f"{r['se']:.3e}", f"{r['mixture']:.3e}", fnum(r["ratio"]), ("yes" if r["within2"] else ("no" if r["within2"] is not None else "—")), pp(r["sd_pop_obs"]), pp(r["sd_cond_obs"]), f"{r['floor_part']:.2e}"] for r in pr])]
(OUTDIR / "tables_population_full.md").write_text("\n".join(full) + "\n")
elig_files = {r["file"] for r in S1["rows"] if r["status"] != "ineligible"}
pp_all = pop_rows(lambda c: c["file"] in elig_files, A_PRIMARY); pp_ = [r for r in pp_all if r["ratio"] is not None]
reg("pop_n", len(pp_)); reg("pop_n_eligible", len(pp_all)); reg("pop_ratio_median", fnum(float(np.median([r["ratio"] for r in pp_]))) if pp_ else "—"); reg("pop_ratio_q10", fnum(float(np.quantile([r["ratio"] for r in pp_], 0.1))) if pp_ else "—"); reg("pop_ratio_q90", fnum(float(np.quantile([r["ratio"] for r in pp_], 0.9))) if pp_ else "—")
reg("pop_within_2se", f"{sum(1 for r in pp_ if r['within2'])} of {len(pp_)}"); reg("pop_negative", sum(1 for r in pp_all if r["twoway"] < 0)); reg("s1_ratio_median_sq", fnum(float(np.median(rat_res)) ** 2) if rat_res else "—")
# the key-count resolution of every live cell (protocol §8): keys at level 0, at level 1, distinct levels, keys above 5 alpha
full = ["# Study 2 — the key-count resolution of every live cell (protocol §8)", "", "Generated by `research/study2/s2_report.py` from the stored integer level counts: the number of keys at level 0 and at level 1 (every text rejected), the number of distinct levels and the number of keys above 5α, with the key-mean and the across-key SD."]
kc = {a: [] for a in ALPHAS}
for a in ALPHAS:
    rows = []
    for c in LIVE:
        k_ = c["data"]["levels"][a]["level_counts"]; n0 = sum(1 for x in k_ if x == 0); n1 = sum(1 for x in k_ if x == c["data"]["N_eff"]); nd = len(set(k_)); n5 = sum(1 for x in k_ if x > 5 * float(a) * c["data"]["N_eff"])
        kc[a].append((c, n0, n1, nd, n5)); rows.append([c["file"], n0, n1, nd, n5, pp(c["data"]["levels"][a]["key_mean_level"], 3), pp(c["data"]["levels"][a]["sd_obs_conditional"])])
    full += ["", f"## α = {a}", "", md_table(["Cell file", "Keys at level 0", "Keys at level 1", "Distinct levels", "Keys > 5α", "Key-mean (%)", "SD (pp)"], rows)]
(OUTDIR / "tables_key_counts_full.md").write_text("\n".join(full) + "\n")
reg("kc_cells_any_key_at_one", sum(1 for c, n0, n1, nd, n5 in kc[A_PRIMARY] if n1 > 0)); reg("kc_cells_any_key_at_zero", sum(1 for c, n0, n1, nd, n5 in kc[A_PRIMARY] if n0 > 0)); reg("kc_max_keys_at_zero", max(n0 for c, n0, n1, nd, n5 in kc[A_PRIMARY]))
reg("kc_min_distinct_levels", min(nd for c, n0, n1, nd, n5 in kc[A_PRIMARY])); reg("kc_n_levels_total", len(kc[A_PRIMARY]) * len(ALPHAS))
reg("kc_cells_any_key_at_zero_all_alpha", sum(1 for a in ALPHAS for c, n0, n1, nd, n5 in kc[a] if n0 > 0)); reg("kc_cells_any_key_at_one_all_alpha", sum(1 for a in ALPHAS for c, n0, n1, nd, n5 in kc[a] if n1 > 0))
# the pairwise Gaussian predictor and the heterogeneity diagnostics on EVERY live cell and alpha (protocol §7; R06 F9), with a coverage assertion
rows_pw = []; n_pw_cells = set()
for a in ALPHAS:
    for c in LIVE:
        d = c["data"]; lv = d["levels"][a]; pw = lv.get("pred_pairwise_gaussian") or {}; het = d.get("covariance_heterogeneity") or {}; q = het.get("pair_corr_quantiles") or {}; rep = het.get("replicate") or {}; sd = lv["sd_obs_conditional"]; cf = lv["pred_first_order"]["sd_cond"]
        ss = lv.get("pred_simulated_shift", {}).get("sd_cond") if lv.get("pred_simulated_shift") else None
        rows_pw.append([c["file"], a, pp(sd), pp(cf), fnum(sd / cf) if cf > 0 else "—", pp(pw.get("sd_cond")), pp(pw.get("sd_cond_replicate")), fnum(sd / pw["sd_cond"]) if pw.get("sd_cond", 0) > 0 else "—", fnum(sd / pw["sd_cond_replicate"]) if pw.get("sd_cond_replicate") else "—",
                        fnum(100 * pw["subsample_sd_difference"]) if pw.get("subsample_sd_difference") is not None else "—", pp(ss) if ss is not None else "—", fnum(lv.get("ratio_obs_over_pred_simulated_shift")), het.get("n_subsample", "—"), fnum(het.get("pair_cov_mean")), fnum(het.get("pair_cov_cv")), fnum(rep.get("pair_cov_cv")),
                        f"{fnum(q.get('0.5'))} / {fnum(q.get('0.9'))} / {fnum(q.get('0.99'))} / {fnum(het.get('pair_corr_max'))}", pct(het.get("share_zero_variance_texts")), fnum(lv["pred_first_order"]["theory_share"]), fnum(d["population"]["sigma_model2"]), fnum(d["z_var_within_key"]["mean_over_keys"])]); n_pw_cells.add(c["file"])
if len(rows_pw) != len(LIVE) * len(ALPHAS) or len(n_pw_cells) != len(LIVE) or len(LIVE) != len(EXPECTED):
    raise SystemExit(f"pairwise supplement coverage: {len(rows_pw)} rows over {len(n_pw_cells)} cells against {len(LIVE)} live × {len(ALPHAS)} α")
(OUTDIR / "tables_pairwise_full.md").write_text(f"# Study 2 — the pairwise Gaussian predictor and the covariance-heterogeneity diagnostics on every live cell and every α (protocol §7)\n\nGenerated by `research/study2/s2_report.py` from the cell files: {len(rows_pw):,} rows = {len(LIVE):,} live cells × {len(ALPHAS)} α (coverage asserted against the inventory). SDs in percentage points; the ratios are observed over predicted; the pairwise predictor is evaluated on two disjoint 300-text subsamples (subsample 1 and its replicate); the heterogeneity diagnostics are of subsample 1 (the replicate's CV beside it); the simulated-shift columns exist for the independent KGW colouring and the Gumbel family.\n\n" +
    md_table(["Cell file", "α", "SD obs", "SD common-factor", "Ratio CF", "SD pairwise", "SD pairwise replicate", "Ratio pairwise", "Ratio pairwise replicate", "Subsampling difference (pp)", "SD simulated-shift", "Ratio simulated-shift", "Subsample size", "Pair-cov mean", "Pair-cov CV", "Pair-cov CV (replicate)", "Pair-corr q50 / q90 / q99 / max", "Zero-variance texts", "Theory share", "σ² (identities)", "σ² observed"], rows_pw) + "\n")
reg("pw_rows", f"{len(rows_pw):,}"); reg("pw_cells", f"{len(n_pw_cells):,}")
# correlations: the summary over the 45 pairs per setting, one example matrix, and the full file
CR = DV["correlations"]; rows = []; full = ["# Study 2 — the between-cell correlation matrices of the per-key levels (α = 0.01, L = 256; the same keys in every cell)", "", "Generated by `research/study2/s2_report.py`. Pearson above the diagonal, Spearman below."]


def matrix_md(e):
    tags = e["tags"]; rows = []
    for i, a_ in enumerate(tags):
        rows.append([LABEL[a_]] + [("1" if i == j else (fnum(e["pearson"][i][j]) if j > i else fnum(e["spearman"][i][j]))) for j in range(len(tags))])
    return md_table(["", *[LABEL[t] for t in tags]], rows)


for e in CR["between_cells"]:
    n_ = len(e["tags"]); pe = [e["pearson"][i][j] for i in range(n_) for j in range(i + 1, n_)]; sp = [e["spearman"][i][j] for i in range(n_) for j in range(i + 1, n_)]
    pe_f = [x for x in pe if x is not None]; sp_f = [x for x in sp if x is not None]
    rows.append([tok_label(e["tokenizer"]), e["family"], e["h"], e["rule"], len(pe), len(pe) - len(pe_f), rng_str(pe_f), fnum(float(np.median(pe_f))) if pe_f else "—", rng_str(sp_f), fnum(float(np.median(sp_f))) if sp_f else "—"])
    full += ["", f"## {tok_label(e['tokenizer'])}, {e['family']}, h = {e['h']}, {e['rule']} rule", "", matrix_md(e)]
T["corr_summary"] = md_table(["Tokenizer", "Family", "h", "Rule", "Pairs", "Undefined (a constant cell)", "Pearson range", "Pearson median", "Spearman range", "Spearman median"], rows) + "\n\nThe across-key correlation of the per-key levels between corpus cells at L = 256 (45 pairs of the 10 cells per setting); a correlation is undefined when a cell's levels are constant over the keys."
(OUTDIR / "tables_correlations_full.md").write_text("\n".join(full) + "\n")
ex_e = next((e for e in CR["between_cells"] if e["tokenizer"] == "llama" and e["family"] == "kgw" and e["h"] == 1 and e["rule"] == "distinct"), CR["between_cells"][0] if CR["between_cells"] else None)
T["corr_matrix"] = (matrix_md(ex_e) + f"\n\n{tok_label(ex_e['tokenizer'])}, {ex_e['family']}, h = {ex_e['h']}, {ex_e['rule']} rule, L = 256, α = {A_PRIMARY}: Pearson above the diagonal, Spearman below. Every setting is in `tables_correlations_full.md`.") if ex_e else "_No matrix._"
reg("corr_example", f"{tok_label(ex_e['tokenizer'])}, {ex_e['family']}, h = {ex_e['h']}, {ex_e['rule']} rule" if ex_e else "—")
for fam in ("kgw", "gumbel"):
    for h in (0, 1, 2):
        for ru in ("raw", "distinct"):
            es = [e for e in CR["between_cells"] if e["family"] == fam and e["h"] == h and e["rule"] == ru]; pe = [e["pearson"][i][j] for e in es for i in range(len(e["tags"])) for j in range(i + 1, len(e["tags"])) if e["pearson"][i][j] is not None]
            reg(f"corr_{fam}_h{h}_{ru}_range", rng_str(pe)); reg(f"corr_{fam}_h{h}_{ru}_median", fnum(float(np.median(pe))) if pe else "—")
# the language disparity
rows = []
for e in CR["language_disparity"]:
    rows.append([tok_label(e["tokenizer"]), e["family"], e["h"], e["rule"], e["K"], e["n_keys_all_zero"], e["n_keys_some_zero"], e["n_keys_all_positive"], pct(e["share_all_positive_keys_ratio_gt2"]) if e["share_all_positive_keys_ratio_gt2"] is not None else "—",
                 pct(e["share_all_positive_keys_ratio_gt5"]) if e["share_all_positive_keys_ratio_gt5"] is not None else "—", fnum(e["median_ratio_all_positive_keys"]), fnum(e["max_ratio_all_positive_keys"]), rng_str(list(e["sd_of_pairwise_difference_pp"].values()))])
T["language"] = md_table(["Tokenizer", "Family", "h", "Rule", "K", "Keys with all six levels 0", "Keys with a 0 and a positive level", "Keys with all six positive", "Share with max/min > 2", "Share with max/min > 5", "Median max/min", "Largest max/min", "SD of the pairwise difference (pp), range over the 15 pairs"], rows) + \
    f"\n\nThe per-key disparity across the six Wikipedia language cells at L = 256 (en, de, ru, ar, zh, ja), α = {A_PRIMARY}: the ratio of the largest to the smallest of a key's six levels is defined only for the keys with all six positive, and the shares, median and maximum are over those keys (their number is the denominator); empirical finite-text ratios over the sampled keys, not calibrated population language effects (protocol §7)."
ld = {(e["tokenizer"], e["family"], e["h"], e["rule"]): e for e in CR["language_disparity"]}
for fam in ("kgw", "gumbel"):
    for ru in ("raw", "distinct"):
        es = [ld[(t, fam, h, ru)] for t in TOKS for h in (0, 1, 2) if (t, fam, h, ru) in ld]
        reg(f"lang_{fam}_{ru}_allzero_range", rng_str([e["n_keys_all_zero"] for e in es], lambda v: fnum(v, 0))); reg(f"lang_{fam}_{ru}_somezero_range", rng_str([e["n_keys_some_zero"] for e in es], lambda v: fnum(v, 0)))
        reg(f"lang_{fam}_{ru}_allpos_range", rng_str([e["n_keys_all_positive"] for e in es], lambda v: fnum(v, 0))); reg(f"lang_{fam}_{ru}_gt2_range", rng_str([e["share_all_positive_keys_ratio_gt2"] for e in es], pct)); reg(f"lang_{fam}_{ru}_gt5_range", rng_str([e["share_all_positive_keys_ratio_gt5"] for e in es], pct))
        reg(f"lang_{fam}_{ru}_median_range", rng_str([e["median_ratio_all_positive_keys"] for e in es])); reg(f"lang_{fam}_{ru}_max_range", rng_str([e["max_ratio_all_positive_keys"] for e in es]))
        for h in (0, 1, 2):
            eh = [ld[(t, fam, h, ru)] for t in TOKS if (t, fam, h, ru) in ld]
            reg(f"lang_{fam}_{ru}_h{h}_gt2_range", rng_str([e["share_all_positive_keys_ratio_gt2"] for e in eh], pct)); reg(f"lang_{fam}_{ru}_h{h}_gt5_range", rng_str([e["share_all_positive_keys_ratio_gt5"] for e in eh], pct)); reg(f"lang_{fam}_{ru}_h{h}_median_range", rng_str([e["median_ratio_all_positive_keys"] for e in eh]))
            reg(f"lang_{fam}_{ru}_h{h}_sddiff_range", rng_str([v for e in eh for v in e["sd_of_pairwise_difference_pp"].values()])); reg(f"lang_{fam}_{ru}_h{h}_max_range", rng_str([e["max_ratio_all_positive_keys"] for e in eh], lambda v: fnum(v, 0) if v >= 100 else fnum(v)))
            fl = math.sqrt(2 * 0.01 * 0.99 / N) * 100; reg(f"lang_{fam}_{ru}_h{h}_sddiff_over_floor_range", rng_str([v / fl for e in eh for v in e["sd_of_pairwise_difference_pp"].values()], lambda v: fnum(v, 1)))
reg("lang_floor_diff_pp", fnum(math.sqrt(2 * 0.01 * 0.99 / N) * 100, 3))
# the tokenizer axis: per (family, h, rule) at L = 256 over the ten cells; the full file carries every (cell, L)
bt = CR["between_tokenizers"]; rows = []
for fam in ("kgw", "gumbel"):
    for h in HS:
        for ru in grid["rules"]:
            es = [e for e in bt if e["family"] == fam and e["h"] == h and e["rule"] == ru and e["L"] == 256]
            if not es:
                continue
            rr = [e["sd_ratio_qwen_over_llama"] for e in es if e["sd_ratio_qwen_over_llama"] is not None]; pe = [e["pearson"] for e in es if e["pearson"] is not None]
            rows.append([fam, h, ru, len(es), rng_str(rr), fnum(float(np.median(rr))) if rr else "—", rng_str(pe), fnum(float(np.median(pe))) if pe else "—", rng_str([e["key_mean_llama"] for e in es], lambda v: pct(v, 2)), rng_str([e["key_mean_qwen"] for e in es], lambda v: pct(v, 2))])
T["tokenizer_axis"] = md_table(["Family", "h", "Rule", "Cells", "SD ratio Qwen / Llama, range", "Median", "Across-tokenizer Pearson, range", "Median", "Key-mean level, Llama (%)", "Key-mean level, Qwen (%)"], rows) + \
    f"\n\nThe same texts under both tokenizers at L = 256, α = {A_PRIMARY}: the ratio of the across-key SDs of the level and the across-key correlation of the per-key levels (the identity predicts a non-zero correlation only through coinciding integer ids; protocol §7). Every (cell, L) is in `tables_tokenizer_full.md`."
full = ["# Study 2 — the tokenizer axis in full (every corpus cell, family, width, rule and length; α = 0.01)", "", "Generated by `research/study2/s2_report.py`.", "",
        md_table(["Corpus cell", "Family", "h", "Rule", "L", "SD Llama (pp)", "SD Qwen (pp)", "Ratio Qwen / Llama", "Key-mean Llama (%)", "Key-mean Qwen (%)", "Pearson", "Spearman"],
                 [[LABEL[e["tag"]], e["family"], e["h"], e["rule"], e["L"], pp(e["sd_llama"]), pp(e["sd_qwen"]), fnum(e["sd_ratio_qwen_over_llama"]), pct(e["key_mean_llama"], 2), pct(e["key_mean_qwen"], 2), fnum(e["pearson"]), fnum(e["spearman"])] for e in bt])]
(OUTDIR / "tables_tokenizer_full.md").write_text("\n".join(full) + "\n")
for fam in ("kgw", "gumbel"):
    for ru in ("raw", "distinct"):
        es = [e for e in bt if e["family"] == fam and e["rule"] == ru and e["L"] == 256 and e["h"] == 1]
        reg(f"tok_{fam}_{ru}_h1_ratio_range", rng_str([e["sd_ratio_qwen_over_llama"] for e in es])); reg(f"tok_{fam}_{ru}_h1_corr_range", rng_str([e["pearson"] for e in es]))
    es = [e for e in bt if e["family"] == fam and e["L"] == 256]; pe = [e["pearson"] for e in es if e["pearson"] is not None]
    reg(f"tok_{fam}_corr_abs_max", fnum(max(abs(x) for x in pe)) if pe else "—"); reg(f"tok_{fam}_n_pairs_L256", len(es))
# the fixed-size reduction at h = 0 (the Study 1 statement on real text at V >= 128k), by rule; the full rows in a supplement
fx = S3["fixed_vs_independent_h0"]; rows = []
for ru in grid["rules"]:
    rs = [r for r in fx if r["rule"] == ru and r["gamma"] == G0]
    if not rs:
        continue
    mx_ = max(rs, key=lambda r: r["reduction"] if r["reduction"] is not None else -1)
    rows.append([ru, len(rs), rng_str([r["reduction"] for r in rs], lambda v: pct(v, 3)), f"{LABEL[mx_['tag']]} {tok_label(mx_['tokenizer'])} L = {mx_['L']:,}", sum(1 for r in rs if r["reduction"] is not None and r["reduction"] >= 0.01), rng_str([r["one_over_C_cond"] for r in rs], lambda v: fnum(v, 0)),
                 rng_str([r["coverage_share_of_V"] for r in rs], pct), rng_str([r["observed_ratio"] for r in rs], lambda v: fnum(v, 4)), rng_str([r["exact_ratio"] for r in rs], lambda v: fnum(v, 4))])
T["reduction"] = md_table(["Rule", "Cells (both tokenizers, every L)", "Reduction (1/C_cond − 1)/(V − 1), range", "Largest, where", "Cells at or above 1%", "1/C_cond, range", "Covered share of V, range", "Observed Var_fixed/Var_indep, range", "Exact (V − 1/C_cond)/(V − 1), range"], rows) + \
    f"\n\nAt h = 0, γ = {G0}, at the realised q-weights of the production texts (a key-free quantity, in INPUTS.json before the lock; the observed ratio is the across-key sample variance of q̂ under the fixed colouring over that under the independent colouring, `q_hat.var_across_keys`, K = {K:,} each; S3's known-mean estimator is a separate check). V = 128,256 (Llama) and 151,936 (Qwen)."
(OUTDIR / "tables_fixed_h0_full.md").write_text("# Study 2 — the fixed-size colouring at h = 0 in full (every cell, tokenizer, length, rule and γ)\n\nGenerated by `research/study2/s2_report.py`.\n\n" +
    md_table(["Corpus cell", "Tokenizer", "γ", "L", "Rule", "V", "C_cond", "1/C_cond", "Covered share of V", "Reduction (1/C_cond − 1)/(V − 1)", "Exact ratio fixed/indep", "Observed ratio fixed/indep"],
             [[LABEL[r["tag"]], tok_label(r["tokenizer"]), r["gamma"], r["L"], r["rule"], f"{r['V']:,}", fnum(r["C_cond"]), fnum(r["one_over_C_cond"], 0), pct(r["coverage_share_of_V"]), pct(r["reduction"], 3), fnum(r["exact_ratio"], 5), fnum(r["observed_ratio"], 4)] for r in fx]) + "\n")
for ru in grid["rules"]:
    rs = [r for r in fx if r["rule"] == ru and r["gamma"] == G0]; reg(f"red_{ru}_max", pct(max(r["reduction"] for r in rs), 3) if rs else "—"); reg(f"red_{ru}_n_above", sum(1 for r in rs if r["reduction"] >= 0.01)); reg(f"red_{ru}_n", len(rs))
reg("red_n_total", len(fx)); reg("red_max_all", pct(max(r["reduction"] for r in fx), 3) if fx else "—")
mxr = max((r for r in fx if r["rule"] == "distinct" and r["gamma"] == G0), key=lambda r: r["reduction"]); reg("red_max_cell", f"{LABEL[mxr['tag']]}, {tok_label(mxr['tokenizer'])}, L = {mxr['L']:,}"); reg("red_max_coverage", pct(mxr["coverage_share_of_V"])); reg("red_max_inv_ccond", fnum(mxr["one_over_C_cond"], 0)); reg("red_max_inv_ccond_share", pct(mxr["one_over_C_cond"] / mxr["V"], 2)); reg("red_max_V", f"{mxr['V']:,}")
# integrity
flags = [(c["file"], a, c["data"]["levels"][a]["pred_first_order"]["flags"]) for c in LIVE for a in ALPHAS if c["data"]["levels"][a]["pred_first_order"].get("flags")]
m0 = [c for c in LIVE if c["data"]["frac_M0"] > 0]; first_h0 = [c for c in LIVE if c["rule"] == "first" and c["h"] == 0 and c["family"] == "kgw"]
sz_first = sum(1 for c in first_h0 for a in ALPHAS if c["data"]["levels"][a]["structural_zero"]); pcf = max((c["data"]["levels"][a].get("pred_per_text_vs_closed_form_abs_diff_sd", 0.0) for c in LIVE for a in ALPHAS if c["family"] == "kgw"), default=0.0)
zero_pred = sum(1 for c in LIVE for a in ALPHAS if not c["data"]["levels"][a]["pred_first_order"]["sd_cond"] > 0)
reg("n_predictor_flags", len(flags)); reg("n_M0_cells", len(m0)); reg("n_first_h0_cells", len(first_h0)); reg("n_first_h0_structural_zero_levels", sz_first); reg("n_first_h0_levels_total", 3 * len(first_h0)); reg("pcf_max", f"{pcf:.1e}"); reg("n_zero_pred_levels", zero_pred)
reg("n_dep_cells", CHK["deployer"]["n_cells"]); reg("n_dep_rows", CHK["deployer"]["n_rows"])
T["integrity"] = md_table(["Check", "Observed"], [
    ["Inventory", f"{res['n_cells']} cells exactly as the grid expects, {res['n_live']} live, {res['n_markers']} markers; N_eff = N = {N:,} in every cell (the body contract)"],
    ["Predictor flags (σ² negative or non-finite)", f"{len(flags)}" + ("" if not flags else ": " + "; ".join(f"{f} α={a} {fl}" for f, a, fl in flags[:8]))],
    ["(cell, α) levels with a zero prediction (the registered non-finite ratio)", zero_pred],
    ["Live cells with texts at M = 0", f"{len(m0)}" + ("" if not m0 else ": " + ", ".join(f"{c['file']} ({pct(c['data']['frac_M0'], 2)})" for c in m0[:6]))],
    ["The first rule at h = 0 (one token per text): structural zeros", f"{sz_first} of {3 * len(first_h0)} (cell, α) levels in {len(first_h0)} KGW cells"],
    ["KGW: |per-text closed form − Study 1's single-threshold closed form| for the predicted SD, largest", f"{pcf:.1e}"],
    ["S3 cells whose squared estimator was constant over the keys (recorded, never used)", VALUES["s3_constancy"]],
    ["Deployer subset selected from the grid", f"{CHK['deployer']['n_cells']} cells × {len(ALPHAS)} α = {CHK['deployer']['n_rows']} rows, every one with a populated crossed block (B = 200)"],
    ["The secondary unit-σ block (protocol §6)", "listed by the protocol, not computed by the locked analyzer; computed by the builder from the stored unit-σ predictor and reported in Table 5 as the builder's (a text/code discrepancy of the locked protocol, disclosed in §5)"],
    ["Re-computation of s₀² from the 6-decimal mean-score values", f"largest relative difference from the stored estimator {VALUES['s0_max_rel_diff']} (the stored estimates and SEs are the record; protocol §3)"],
    ["The predictions compared with the outcomes are the ones disclosed before the lock (INPUTS.json, pinned)", f"{VALUES['inputs_n_pred']} (cell, α) predictions compared; largest |difference| {VALUES['inputs_max_diff_pred']} (predicted SD, mean level, theory share), {VALUES['inputs_max_diff_exact']} (exact key-mean), {VALUES['inputs_max_diff_rho']} (ρ̄)"]])
# the non-consistent primary cells (section 5): where they lie and which way their ratios point
nc = S1["non_consistent_rows"]; reg("nc_n", len(nc)); reg("nc_n_ratio_gt1", sum(1 for r in nc if r["ratio"] > 1)); reg("nc_ratio_min", fnum(min(r["ratio"] for r in nc)) if nc else "—"); reg("nc_ratio_max", fnum(max(r["ratio"] for r in nc)) if nc else "—")
reg("nc_n_L64", sum(1 for r in nc if r["L"] == 64)); reg("nc_n_h1", sum(1 for r in nc if r["h"] == 1)); reg("nc_n_h2", sum(1 for r in nc if r["h"] == 2)); reg("nc_n_h3", sum(1 for r in nc if r["h"] == 3)); reg("nc_n_h4", sum(1 for r in nc if r["h"] == 4))
reg("nc_n_raw", sum(1 for r in nc if r["rule"] == "raw")); reg("nc_n_distinct", sum(1 for r in nc if r["rule"] == "distinct")); reg("nc_n_qwen", sum(1 for r in nc if r["tokenizer"] == "qwen")); reg("nc_n_llama", sum(1 for r in nc if r["tokenizer"] == "llama"))
nc64r = [r for r in nc if r["L"] == 64 and r["rule"] == "raw" and r["h"] == 1]; reg("nc_L64raw_n", len(nc64r)); reg("nc_L64raw_level_obs_range", rng_str([r["key_mean_level"] for r in nc64r], lambda v: pct(v, 2))); reg("nc_L64raw_level_pred_range", rng_str([r["pred_mean_level"] for r in nc64r], lambda v: pct(v, 2)))
reg("nc_pw_closer_n", sum(1 for r in nc if r["ratio_pairwise"] is not None and abs(r["ratio_pairwise"] - 1) < abs(r["ratio"] - 1))); reg("nc_ss_closer_n", sum(1 for r in nc if fin(r["ratio_simulated_shift"]) and abs(r["ratio_simulated_shift"] - 1) < abs(r["ratio"] - 1)))
reg("nc_pw_ratio_range", rng_str([r["ratio_pairwise"] for r in nc])); reg("nc_ss_ratio_range", rng_str([r["ratio_simulated_shift"] for r in nc]))
# the exact size of the discrete z-test at gamma 0.25 by the number of scored positions (the raw rule scores M = L - h exactly; the same in every cell)
for h in (1, 4):
    for L in ALL_L:
        cs = [c for c in LIVE if c["family"] == "kgw" and c["colouring"] == "independent" and c["gamma"] == G0 and c["rule"] == "raw" and c["h"] == h and c["L"] == L]
        if cs:
            ex = [c["data"]["levels"][A_PRIMARY]["exact_marginal_if_indep_distinct"] for c in cs]
            if max(ex) - min(ex) > 1e-9:
                raise SystemExit(f"the exact size at h = {h}, L = {L} differs across cells ({min(ex)}–{max(ex)})")
            reg(f"exact_size_h{h}_L{L}", pct(ex[0], 2)); reg(f"floor_h{h}_L{L}", fnum(100 * math.sqrt(ex[0] * (1 - ex[0]) / N), 3)); reg(f"M_h{h}_L{L}", L - h)
# S4: the failing chains by width and corpus; the two regimes (the finite-text floor at h = 4; the news chains at h = 1-3)
f4 = S4["failing"]; reg("s4_fail_h4", sum(1 for r in f4 if r["h"] == 4)); reg("s4_fail_h1", sum(1 for r in f4 if r["h"] == 1)); reg("s4_fail_h2", sum(1 for r in f4 if r["h"] == 2)); reg("s4_fail_h3", sum(1 for r in f4 if r["h"] == 3))
reg("s4_fail_news", sum(1 for r in f4 if r["tag"] == "news_en_256")); reg("s4_hold_h4", ", ".join(f"{LABEL[r['tag']]} {tok_label(r['tokenizer'])}" for r in S4["decided"] if r["h"] == 4 and r["holds"]) or "none"); reg("s4_n_h4_chains", sum(1 for r in S4["decided"] if r["h"] == 4))


def th_of(r, L):
    return BY[(r["tag"], r["tokenizer"], "kgw", r["h"], L, "raw", "independent", G0)]["data"]["levels"][A_PRIMARY]["pred_first_order"]["theory_share"]


h4nn = [r for r in f4 if r["h"] == 4 and r["tag"] != "news_en_256"]; reg("s4_fail_h4_nonnews_n", len(h4nn)); reg("s4_fail_h4_nonnews_theory_max", fnum(max(th_of(r, L) for r in h4nn for L in r["L"][:2])) if h4nn else "—")
hold4 = [r for r in S4["decided"] if r["holds"]]; nd4 = [all(r["rho_bar"][i + 1] >= r["rho_bar"][i] for i in range(len(r["rho_bar"]) - 1)) for r in hold4]
reg("s4_hold_rho_nondecreasing_n", sum(nd4)); reg("s4_hold_rho_decreasing_n", len(hold4) - sum(nd4)); reg("s4_fail_news_h4_n", sum(1 for r in f4 if r["tag"] == "news_en_256" and r["h"] == 4)); reg("s4_fail_news_non_h4_n", sum(1 for r in f4 if r["tag"] == "news_en_256" and r["h"] != 4))
reg("s4_fail_memberships", sum(1 for r in f4 if r["h"] == 4) + sum(1 for r in f4 if r["tag"] == "news_en_256") + sum(1 for r in f4 if r["h"] == 1 and r["tag"] != "news_en_256"))
reg("th_news_h4_L64_128", "; ".join(f"{tok_label(r['tokenizer'])} {fnum(th_of(r, 64))} and {fnum(th_of(r, 128))}" for r in f4 if r["tag"] == "news_en_256" and r["h"] == 4))
nq2 = next((r for r in hold4 if r["tag"] == "news_en_256" and r["tokenizer"] == "qwen" and r["h"] == 2), None)
reg("s4_news_qwen_h2_rho_seq", " → ".join(fnum(x) for x in nq2["rho_bar"]) if nq2 else "—"); reg("s4_news_qwen_h2_sd_seq", " → ".join(pp(x) for x in nq2["sd_obs"]) if nq2 else "—")
h1nn = [r for r in f4 if r["h"] == 1 and r["tag"] != "news_en_256"]; reg("s4_fail_h1_nonnews_n", len(h1nn)); reg("s4_fail_h1_nonnews_cells", "; ".join(f"{LABEL[r['tag']]} {tok_label(r['tokenizer'])}" for r in h1nn) or "none")
reg("s4_fail_news_llama_h", ", ".join(str(r["h"]) for r in sorted(f4, key=lambda r: r["h"]) if r["tag"] == "news_en_256" and r["tokenizer"] == "llama")); reg("s4_fail_news_qwen_h", ", ".join(str(r["h"]) for r in sorted(f4, key=lambda r: r["h"]) if r["tag"] == "news_en_256" and r["tokenizer"] == "qwen"))
reg("s4_fail_h4_nonnews_sd64_range", rng_str([r["sd_obs"][0] for r in h4nn], pp)); reg("s4_fail_h4_nonnews_sd128_range", rng_str([r["sd_obs"][1] for r in h4nn], pp)); reg("s4_fail_h4_nonnews_sd256_range", rng_str([r["sd_obs"][2] for r in h4nn], pp))
th4 = sorted(((th_of(r, r["L"][-1]), r) for r in S4["decided"] if r["h"] == 4), key=lambda t: -t[0])
reg("th_h4_Lmax_range", rng_str([t for t, _ in th4])); reg("th_h4_Lmax_top", "; ".join(f"{LABEL[r['tag']]} {tok_label(r['tokenizer'])} {fnum(t)}" for t, r in th4[:4])); reg("th_h4_Lmax_n_above_half", sum(1 for t, _ in th4 if t >= 0.5))
reg("th_h4_Lmax_ar", "; ".join(f"{tok_label(r['tokenizer'])} {fnum(t)}" for t, r in th4 if r["tag"] == "wikipedia_ar_256"))
h4ar = [r for r in S4["decided"] if r["h"] == 4 and r["holds"]]; reg("s4_hold_h4_n", len(h4ar)); reg("s4_fail_h1_n", sum(1 for r in f4 if r["h"] == 1)); reg("s4_hold_h4_sd_seq", "; ".join(f"{tok_label(r['tokenizer'])} {' → '.join(pp(x) for x in r['sd_obs'])} pp" for r in h4ar) or "—")
news = {(r["tokenizer"], r["h"]): r for r in f4 if r["tag"] == "news_en_256"}
reg("s4_news_llama_h1_sd_seq", " → ".join(pp(x) for x in news[("llama", 1)]["sd_obs"]) if ("llama", 1) in news else "—"); reg("s4_news_llama_h1_rho_seq", " → ".join(fnum(x) for x in news[("llama", 1)]["rho_bar"]) if ("llama", 1) in news else "—")
reg("s4_news_llama_h2_sd_seq", " → ".join(pp(x) for x in news[("llama", 2)]["sd_obs"]) if ("llama", 2) in news else "—"); reg("s4_news_llama_h2_rho_seq", " → ".join(fnum(x) for x in news[("llama", 2)]["rho_bar"]) if ("llama", 2) in news else "—")
reg("s4_news_llama_h3_rho_seq", " → ".join(fnum(x) for x in news[("llama", 3)]["rho_bar"]) if ("llama", 3) in news else "—"); reg("s4_news_llama_h4_rho_seq", " → ".join(fnum(x) for x in news[("llama", 4)]["rho_bar"]) if ("llama", 4) in news else "—")
h1f = [r for r in f4 if r["h"] == 1]; reg("s4_fail_h1_cells", "; ".join(f"{LABEL[r['tag']]} {tok_label(r['tokenizer'])}" for r in h1f) or "none"); reg("s4_fail_h1_drop_range", rng_str([1 - r["sd_obs"][1] / r["sd_obs"][0] for r in h1f], pct)); reg("s4_fail_h1_rho_ratio_range", rng_str([r["rho_bar"][1] / r["rho_bar"][0] for r in h1f], lambda v: fnum(v, 2)))
# H-domain: the five English cells against the rest (section 5)
EN = [t for t in TAGS if t.endswith("_en_256") or t.endswith("_en_1024")]
for tok in TOKS:
    for fam, h, ru in (("kgw", 0, "raw"), ("kgw", 1, "distinct"), ("kgw", 2, "distinct"), ("gumbel", 1, "distinct")):
        e = next((e for e in CR["between_cells"] if e["tokenizer"] == tok and e["family"] == fam and e["h"] == h and e["rule"] == ru), None)
        if e is None:
            continue
        idx = {t: i for i, t in enumerate(e["tags"])}; ee = [e["pearson"][idx[a]][idx[b]] for i, a in enumerate(EN) for b in EN[i + 1:]]; eo = [e["pearson"][idx[a]][idx[b]] for a in EN for b in e["tags"] if b not in EN]
        oo = [e["pearson"][idx[a]][idx[b]] for i, a in enumerate([t for t in e["tags"] if t not in EN]) for b in [t for t in e["tags"] if t not in EN][i + 1:]]
        for nm, vals in (("en_en", ee), ("en_other", eo), ("other_other", oo)):
            vals = [v for v in vals if v is not None]; reg(f"corr_{tok}_{fam}_h{h}_{ru}_{nm}_median", fnum(float(np.median(vals))) if vals else "—"); reg(f"corr_{tok}_{fam}_h{h}_{ru}_{nm}_range", rng_str(vals))
e = next((e for e in CR["between_cells"] if e["tokenizer"] == "llama" and e["family"] == "kgw" and e["h"] == 0 and e["rule"] == "raw"), None)
if e:
    idx = {t: i for i, t in enumerate(e["tags"])}; reg("corr_llama_h0raw_en256_en1024", fnum(e["pearson"][idx["wikipedia_en_256"]][idx["wikipedia_en_1024"]])); reg("corr_llama_h0raw_ja_zh", fnum(e["pearson"][idx["wikipedia_ja_256"]][idx["wikipedia_zh_256"]]))
for tok in TOKS:
    for fam, h, ru in (("kgw", 0, "raw"), ("kgw", 1, "distinct")):
        e = next((e for e in CR["between_cells"] if e["tokenizer"] == tok and e["family"] == fam and e["h"] == h and e["rule"] == ru), None)
        if e:
            idx = {t: i for i, t in enumerate(e["tags"])}; reg(f"corr_{tok}_{fam}_h{h}_{ru}_ja_zh", fnum(e["pearson"][idx["wikipedia_ja_256"]][idx["wikipedia_zh_256"]]))
reg("n_en_cells", len(EN))
# the tokenizer overlap (a post-hoc side computation by research/study2/tokenizer_overlap.py; study mode only; R06 F1: the full-denominator semantic shares and the key-free hash-overlap quantities)
ov_path = ROOT / OUT / "report" / "tokenizer_overlap.json"
OV_KEYS = ("ov_ids_compared", "ov_ids_same", "ov_share_same", "ov_last_same", "ov_occ_llama_range", "ov_occ_qwen_range", "ov_written", "ov_occ_by_cell", "ov_h0_rho_pred_range", "ov_h0_rho_obs_q_range", "ov_h1_rho_pred_range", "ov_h1_rho_obs_q_range",
           "ov_h0_wshare_llama_range", "ov_h0_wshare_qwen_range", "ov_h1_wshare_llama_range", "ov_h1_wshare_qwen_range", "ov_h0_by_cell", "ov_h1_by_cell", "ov_h0_rho_level_range", "ov_h1_rho_level_range", "ov_h0_shared_tuples_range", "ov_h1_shared_tuples_range")
if REAL and ov_path.exists() and "semantic" in json.loads(ov_path.read_text()):
    ov = json.loads(ov_path.read_text()); sm = ov["semantic"]; reg("ov_ids_compared", f"{sm['ids_compared']:,}"); reg("ov_ids_same", f"{sm['ids_same_string']:,}"); reg("ov_share_same", pct(sm["share_same_of_compared"])); reg("ov_last_same", f"{sm['first_differing_id'] - 1:,}" if sm["first_differing_id"] is not None else "—"); reg("ov_written", ov["written_utc"])
    sl = [r["semantic_share_llama"]["share_occurrences_on_same_string_ids"] for r in ov["cells"].values()]; sq = [r["semantic_share_qwen"]["share_occurrences_on_same_string_ids"] for r in ov["cells"].values()]
    reg("ov_occ_llama_range", rng_str(sl, pct)); reg("ov_occ_qwen_range", rng_str(sq, pct)); reg("ov_occ_by_cell", "; ".join(f"{LABEL[t]} {pct(r['semantic_share_llama']['share_occurrences_on_same_string_ids'])} / {pct(r['semantic_share_qwen']['share_occurrences_on_same_string_ids'])}" for t, r in ov["cells"].items()))
    for h in (0, 1):
        rp = [r[f"h{h}"]["rho_pred_qhat"] for r in ov["cells"].values()]; ro = [r[f"h{h}"]["rho_obs_qhat_stored_values"] for r in ov["cells"].values()]
        reg(f"ov_h{h}_rho_pred_range", rng_str(rp)); reg(f"ov_h{h}_rho_obs_q_range", rng_str(ro)); reg(f"ov_h{h}_wshare_llama_range", rng_str([r[f"h{h}"]["weight_share_on_shared_tuples_llama"] for r in ov["cells"].values()], pct)); reg(f"ov_h{h}_wshare_qwen_range", rng_str([r[f"h{h}"]["weight_share_on_shared_tuples_qwen"] for r in ov["cells"].values()], pct))
        reg(f"ov_h{h}_shared_tuples_range", rng_str([r[f"h{h}"]["n_tuples_shared"] for r in ov["cells"].values()], lambda v: f"{v:,.0f}"))
        rl = [e["pearson"] for e in bt if e["family"] == "kgw" and e["h"] == h and e["rule"] == "raw" and e["L"] == LMAX[e["tag"]] and e["pearson"] is not None]; reg(f"ov_h{h}_rho_level_range", rng_str(rl))
        reg(f"ov_h{h}_by_cell", "; ".join(f"{LABEL[t]} {fnum(r[f'h{h}']['rho_pred_qhat'])} / {fnum(r[f'h{h}']['rho_obs_qhat_stored_values'])}" for t, r in ov["cells"].items()))
else:
    for k_ in OV_KEYS:
        reg(k_, "n/a (no overlap file)")
# the first rule at h = 0 under S5 (descriptive): the structural zero at h = 0 makes every "non-increasing" chain fail
reg("s5_first_n_chains", CHK["S5"]["descriptive"].get("kgw_g0.25_first", [0, 0])[0]); reg("s5_first_n_holding", CHK["S5"]["descriptive"].get("kgw_g0.25_first", [0, 0])[1])
# timing from the manifest
if manifest:
    r_ = manifest["run"]; reg("run_start", r_["start_utc"]); reg("run_end", r_["end_utc"] or "—"); reg("run_hours", fnum(r_["duration_hours"], 2) if r_["duration_hours"] is not None else "—")
    reg("run_projected_hours_fit", fnum(r_["projected_hours_fitted"], 2) if r_.get("projected_hours_fitted") is not None else "—"); reg("run_projected_hours_probe", fnum(r_["projected_hours_probe_scaled"], 2) if r_.get("projected_hours_probe_scaled") is not None else "—")
    reg("run_restarts", r_["n_start_lines"] - 1); reg("run_skipped", len(r_["skipped_chains_on_resume"])); reg("run_sum_chain_hours", fnum(r_["sum_chain_hours"], 2)); reg("inventory_digest", manifest["inventory"]["inventory_sha256"][:16] + "…")
    reg("run_head", manifest["git"]["launch"].get("head_at_launch") or "—"); reg("run_swap", manifest["git"]["launch"].get("swap_at_launch") or "—"); reg("manifest_written", manifest["written_utc"]); reg("run_peak_rss", fnum(manifest["run"].get("peak_rss_gb_max"), 2))
    chs = sorted(manifest["chains"], key=lambda x: -(x["chain_seconds"] or 0))[:5]
    T["timing"] = md_table(["Chain (the five longest)", "|D| tuples", "Contexts", "Build (s)", "Key loop (s)", "Cells", "Cell statistics (s)", "Chain (s) measured", "Chain (s) projected (fitted model)", "Peak RSS so far (GB)"],
                           [[x["chain"], f"{x['n_tuples']:,}" if x["n_tuples"] else "—", f"{x['n_contexts']:,}" if x["n_contexts"] else "—", x["build_seconds"], x["key_loop_seconds"], x["n_cells_computed"], x["cells_seconds"], x["chain_seconds"], x["projected_chain_seconds"], x["peak_rss_gb"]] for x in chs]) + \
        f"\n\nMeasured {VALUES['run_hours']} h in all (chain times sum to {VALUES['run_sum_chain_hours']} h) against the validation's fitted projection of {VALUES['run_projected_hours_fit']} h and the probe-scaled {VALUES['run_projected_hours_probe']} h (protocol §11); every chain's measured and projected time is in `RUN_MANIFEST.json`."
else:
    for k_ in ("run_start", "run_end", "run_hours", "run_projected_hours_fit", "run_projected_hours_probe", "run_restarts", "run_skipped", "run_sum_chain_hours", "inventory_digest", "run_head", "run_swap", "manifest_written", "run_peak_rss"):
        reg(k_, "n/a (no manifest)")
    T["timing"] = "_No run manifest (fixture)._"

# ------------------------------------------------------------------ figures
def save(fig, name):
    for ext in ("png", "svg"):
        fig.savefig(OUTDIR / f"{name}.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)


def logfmt(ax, axis="y", subs=(1.0, 2.0, 5.0)):
    """Plain decimal labels on a log axis (1, 2, 5 per decade by default), no minor labels."""
    from matplotlib.ticker import FuncFormatter, NullFormatter, LogLocator
    for a in ((ax.xaxis, ax.yaxis) if axis == "both" else ((ax.yaxis,) if axis == "y" else (ax.xaxis,))):
        a.set_major_locator(LogLocator(base=10, subs=subs, numticks=15)); a.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        a.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10), numticks=15)); a.set_minor_formatter(NullFormatter())


rows_s1 = [r for r in S1["rows"] if r["status"] != "ineligible"]
# Fig 1: adequacy on real text
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3))
ax = axes[0]
for ru in P["rules"]:
    for tok in TOKS:
        for status, filled in (("consistent", True), ("inconsistent", False), ("unresolved", False)):
            rs = [r for r in rows_s1 if r["rule"] == ru and r["tokenizer"] == tok and r["status"] == status]
            if not rs:
                continue
            ax.scatter([100 * r["sd_pred"] for r in rs], [100 * r["sd_obs"] for r in rs], s=26, marker=MK_TOK[tok], facecolors=COL_RULE[ru] if filled else SURFACE, edgecolors=COL_RULE[ru], linewidths=1.1, label=f"{ru}, {tok_label(tok)}, {status} ({len(rs)})", zorder=3)
vals = [100 * r["sd_pred"] for r in rows_s1] + [100 * r["sd_obs"] for r in rows_s1]; vals = [v for v in vals if v > 0]
lo = min(vals + [0.05]); hi = max(vals + [0.1]); xx = np.array([lo * 0.8, hi * 1.25]); ax.plot(xx, xx, color=MUTED, lw=1, zorder=2); ax.plot(xx, xx * BAND[1], color=MUTED, lw=0.8, ls="--", zorder=2); ax.plot(xx, xx * BAND[0], color=MUTED, lw=0.8, ls="--", zorder=2)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("predicted across-key SD of the per-key level (pp), common-factor predictor"); ax.set_ylabel(f"observed across-key SD (pp), α = {A_PRIMARY}")
ax.set_title(f"(a) the {len(rows_s1)} S1-eligible cells; dashed: the band [{fnum(BAND[0])}, {fnum(BAND[1])}]; filled = consistent", loc="left", fontsize=8.5); ax.legend(fontsize=6.5, loc="upper left", ncol=2); logfmt(ax, "both", subs=(1.0,))
ax = axes[1]
for ru in P["rules"]:
    for tok in TOKS:
        rs = [r for r in rows_s1 if r["rule"] == ru and r["tokenizer"] == tok and fin(r["ratio"])]
        if rs:
            x = np.array([r["sigma_delta"] for r in rs]); y = np.array([r["ratio"] for r in rs]); lo_ = np.array([r["ratio_ci95"][0] for r in rs]); hi_ = np.array([r["ratio_ci95"][1] for r in rs])
            ax.errorbar(x, y, yerr=[np.clip(y - lo_, 0, None), np.clip(hi_ - y, 0, None)], fmt=MK_TOK[tok], color=COL_RULE[ru], ms=3.8, lw=0.7, capsize=0, label=f"{ru} rule, {tok_label(tok)}", zorder=3, alpha=0.9)
ax.axhspan(BAND[0], BAND[1], color=GRID, alpha=0.6, zorder=1); ax.axhline(1.0, color=MUTED, lw=1, zorder=2)
ax.set_xscale("log"); logfmt(ax, "x"); ax.set_xlabel("σ_δ = √ρ̄  (across-key SD of the mean z-shift)"); ax.set_ylabel("observed / predicted SD, with key-bootstrap 95% CI"); ax.set_title("(b) the ratio against the shift dispersion; shaded: the band", loc="left", fontsize=8.5); ax.legend(fontsize=7, ncol=2)
fig.tight_layout(); save(fig, "fig1_adequacy")

# Fig 2: the SD against L at h = 1 per corpus cell (observed; three rules; both tokenizers)
ncol = 5; nrow = int(math.ceil(len(TAGS) / ncol)); fig, axes = plt.subplots(nrow, ncol, figsize=(3.1 * ncol, 2.9 * nrow), squeeze=False)
for i, tag in enumerate(TAGS):
    ax = axes[i // ncol][i % ncol]
    for ru in grid["rules"]:
        for tok in TOKS:
            Ls = L_OF[tag]; ys = []; lo_ = []; hi_ = []
            for L in Ls:
                c = BY.get((tag, tok, "kgw", 1, L, ru, "independent", G0)); lv = c["data"]["levels"][A_PRIMARY] if c else None
                ys.append(100 * lv["sd_obs_conditional"] if lv else np.nan); lo_.append(100 * lv["sd_obs_boot_ci95"][0] if lv else np.nan); hi_.append(100 * lv["sd_obs_boot_ci95"][1] if lv else np.nan)
            ax.fill_between(Ls, lo_, hi_, color=COL_RULE[ru], alpha=0.12, lw=0)
            ax.plot(Ls, ys, color=COL_RULE[ru], ls=LS_TOK[tok], marker=MK_TOK[tok], ms=3.8, label=f"{ru}, {tok_label(tok)}" if i == 0 else None)
    ax.set_xscale("log", base=2); ax.set_yscale("log"); logfmt(ax, "y"); ax.set_title(LABEL[tag], fontsize=9, loc="left"); ax.set_xticks(L_OF[tag]); ax.set_xticklabels([str(L) for L in L_OF[tag]], fontsize=7); ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    if i % ncol == 0:
        ax.set_ylabel("across-key SD of the level (pp)")
    if i // ncol == nrow - 1:
        ax.set_xlabel("text length L (tokens)")
for j in range(len(TAGS), nrow * ncol):
    axes[j // ncol][j % ncol].axis("off")
h_, l_ = axes[0][0].get_legend_handles_labels(); fig.legend(h_, l_, loc="lower center", ncol=6, fontsize=8, bbox_to_anchor=(0.5, -0.03))
fig.suptitle(f"Observed across-key SD of the per-key false-positive level at α = {A_PRIMARY} against length (h = 1, KGW γ = {G0}, independent colouring; K = {K:,} keys, N = {N:,} texts per cell; solid = Llama-3.2, dotted = Qwen2.5; shaded = key-bootstrap 95% CI)", fontsize=9, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.05, 1, 0.96)); save(fig, "fig2_length")

# Fig 3: width at the longest length per corpus cell (raw and distinct; both tokenizers)
fig, axes = plt.subplots(nrow, ncol, figsize=(3.1 * ncol, 2.9 * nrow), squeeze=False)
for i, tag in enumerate(TAGS):
    ax = axes[i // ncol][i % ncol]
    for ru in ("raw", "distinct"):
        for tok in TOKS:
            ys = []; es = []
            for h in HS:
                c = BY.get((tag, tok, "kgw", h, LMAX[tag], ru, "independent", G0)); lv = c["data"]["levels"][A_PRIMARY] if c else None
                ys.append(100 * lv["sd_obs_conditional"] if lv else np.nan); es.append(100 * lv["sd_obs_boot_se"] if lv else np.nan)
            ax.errorbar(HS, ys, yerr=es, color=COL_RULE[ru], ls=LS_TOK[tok], marker=MK_TOK[tok], ms=3.8, lw=1.5, capsize=0, label=f"{ru}, {tok_label(tok)}" if i == 0 else None)
    ax.set_yscale("log"); logfmt(ax, "y"); ax.set_xticks(HS); ax.set_title(f"{LABEL[tag]}, L = {LMAX[tag]:,}", fontsize=9, loc="left")
    if i % ncol == 0:
        ax.set_ylabel("across-key SD of the level (pp)")
    if i // ncol == nrow - 1:
        ax.set_xlabel("context width h")
for j in range(len(TAGS), nrow * ncol):
    axes[j // ncol][j % ncol].axis("off")
h_, l_ = axes[0][0].get_legend_handles_labels(); fig.legend(h_, l_, loc="lower center", ncol=4, fontsize=8, bbox_to_anchor=(0.5, -0.03))
fig.suptitle(f"Context width: the observed across-key SD of the level at α = {A_PRIMARY} at each cell's longest length (KGW γ = {G0}, independent colouring; raw and distinct rules; solid = Llama-3.2, dotted = Qwen2.5; bars = key-bootstrap SE)", fontsize=9, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.05, 1, 0.96)); save(fig, "fig3_width")

# Fig 4: the deployer's view at alpha 0.01, h = 1, the longest length: the spread of the sampled keys per corpus cell, both tokenizers
FLOOR = 100.0 / N
fig, axes = plt.subplots(2, 2, figsize=(11, 7.2), sharey=True)
for ax, (fam, ru) in zip(axes.flat, (("kgw", "raw"), ("kgw", "distinct"), ("gumbel", "raw"), ("gumbel", "distinct"))):
    for i, tag in enumerate(TAGS):
        for k_, tok in enumerate(TOKS):
            r = next((x for x in dep_rows if x["tag"] == tag and x["tokenizer"] == tok and x["family"] == fam and x["h"] == 1 and x["rule"] == ru and float(x["alpha"]) == 0.01), None)
            if r is None:
                continue
            x = i + (-0.18 if tok == "llama" else 0.18); q = {k: max(100 * r["quantiles"][k], FLOOR) for k in QUANTILE_KEYS}; mx_ = max(100 * r["max_key"], FLOOR); cr = r["crossed"]
            ax.plot([x, x], [q["0.01"], q["0.99"]], color=SEQ[1], lw=2.2, solid_capstyle="butt", zorder=2, label="1%–99% of the sampled keys" if (i == 0 and k_ == 0) else None)
            ax.plot([x, x], [q["0.05"], q["0.95"]], color=SEQ[2], lw=5, solid_capstyle="butt", zorder=3, label="5%–95% of the sampled keys" if (i == 0 and k_ == 0) else None)
            ax.scatter([x], [q["0.5"]], color=SURFACE, edgecolors=INK, s=22, zorder=5, marker=MK_TOK[tok], label=f"median key ({tok_label(tok)})" if i == 0 else None)
            ax.scatter([x], [mx_], color=INK, s=14, zorder=5, marker=MK_TOK[tok], label=f"worst sampled key ({tok_label(tok)})" if i == 0 else None)
            if cr:
                lo_, hi_ = [max(100 * v, FLOOR) for v in cr["max"]["ci95"]]; ax.plot([x, x], [lo_, hi_], color=INK, lw=0.8, zorder=4, label="crossed 95% CI of the worst key" if (i == 0 and k_ == 0) else None)
    ax.axhline(1.0, color=MUTED, lw=1, ls="--", zorder=1, label="nominal 1%" if (fam, ru) == ("kgw", "raw") else None); ax.set_yscale("log"); ax.set_xticks(range(len(TAGS))); ax.set_xticklabels([LABEL[t] for t in TAGS], rotation=35, ha="right", fontsize=7.5)
    ax.set_title(f"{'KGW, γ = ' + str(G0) if fam == 'kgw' else 'Gumbel-max'}, {ru} rule", loc="left", fontsize=9); ax.set_ylim(FLOOR * 0.8, 120)
axes[0][0].set_ylabel("per-key false-positive level at α = 1% (%)"); axes[1][0].set_ylabel("per-key false-positive level at α = 1% (%)")
for ax in axes.flat:
    logfmt(ax, "y", subs=(1.0,))
h_, l_ = axes[0][0].get_legend_handles_labels(); fig.legend(h_, l_, loc="lower center", ncol=4, fontsize=7.5, bbox_to_anchor=(0.5, -0.02))
fig.suptitle(f"What one fixed key faces: the per-key levels over the K = {K:,} sampled keys on the N = {N:,} realised texts of each corpus cell at h = 1 and the cell's longest length (levels at 0 drawn at the floor 1/N; bands = empirical spread of the sampled keys, not confidence bands)", fontsize=9, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.05, 1, 0.96)); save(fig, "fig4_keys")

# Fig 5: between-cell correlation matrices (Pearson) for three settings, Llama
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6))
picks = [("llama", "kgw", 0, "raw"), ("llama", "kgw", 1, "distinct"), ("llama", "gumbel", 1, "distinct")]; drawn = []
for ax, (tok, fam, h, ru) in zip(axes, picks):
    e = next((e for e in CR["between_cells"] if e["tokenizer"] == tok and e["family"] == fam and e["h"] == h and e["rule"] == ru), None)
    if e is None:
        ax.axis("off"); continue
    M = np.array([[np.nan if v is None else v for v in row] for row in e["pearson"]], dtype=float); im = ax.imshow(M, cmap=DIVERGING, vmin=-1, vmax=1); drawn.append(im)
    for i in range(len(e["tags"])):
        for j in range(len(e["tags"])):
            if i != j and np.isfinite(M[i, j]):
                ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=6.3, color=INK if abs(M[i, j]) < 0.6 else SURFACE)
    ax.set_xticks(range(len(e["tags"]))); ax.set_xticklabels([LABEL[t] for t in e["tags"]], rotation=45, ha="right", fontsize=7); ax.set_yticks(range(len(e["tags"]))); ax.set_yticklabels([LABEL[t] for t in e["tags"]], fontsize=7); ax.grid(False); ax.tick_params(axis="y", length=0, labelleft=(ax is axes[0]))
    ax.set_title(f"{tok_label(tok)}, {'KGW γ = ' + str(G0) if fam == 'kgw' else 'Gumbel-max'}, h = {h}, {ru} rule", loc="left", fontsize=8.5)
fig.subplots_adjust(wspace=0.08)
if drawn:
    cb = fig.colorbar(drawn[-1], ax=axes, fraction=0.025, pad=0.02); cb.set_label("Pearson correlation of the per-key levels")
fig.suptitle(f"H-domain: the across-key correlation of the per-key levels between corpus cells (the same {K:,} keys in every cell; L = 256, α = {A_PRIMARY}; every setting in tables_correlations_full.md)", fontsize=9, x=0.01, ha="left")
save(fig, "fig5_correlation")

# Fig 6: (a) S3 observed against exact variance; (b) S2 key-mean against the exact value (distinct rule); (c) the tokenizer axis at h = 1
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2))
ax = axes[0]
for col in ("independent", "fixed", "uniform"):
    cs = [c for c in LIVE if c["colouring"] == col and not (c["data"]["q_hat"] if c["family"] == "kgw" else c["data"]["s_bar"])["structural_zero"]]
    if cs:
        ax.scatter([(c["data"]["q_hat"] if c["family"] == "kgw" else c["data"]["s_bar"])["exact_var_own_colouring"] for c in cs], [(c["data"]["q_hat"] if c["family"] == "kgw" else c["data"]["s_bar"])["var_known_mean"] for c in cs], s=9, color=COL_COLOURING[col], alpha=0.6, label=f"{'Gumbel (uniform scores)' if col == 'uniform' else col + ' colouring'} ({len(cs)} cells)", zorder=3)
vals = [(c["data"]["q_hat"] if c["family"] == "kgw" else c["data"]["s_bar"])["exact_var_own_colouring"] for c in LIVE if (c["data"]["q_hat"] if c["family"] == "kgw" else c["data"]["s_bar"])["exact_var_own_colouring"] > 0]
xx = np.array([min(vals) * 0.7, max(vals) * 1.4]); ax.plot(xx, xx, color=MUTED, lw=1, zorder=2); ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("exact across-key variance of q̂ or s̄ (identity at the realised weights)"); ax.set_ylabel("observed known-mean variance s₀²"); ax.legend(fontsize=7, loc="upper left")
ax.set_title(f"(a) S3: {S3['n_checks']:,} live cells, {S3['n_gross']} gross failures", loc="left", fontsize=8.5)
ax = axes[1]
for fam in ("kgw", "gumbel"):
    xs = []; ys = []
    for c in LIVE:
        if c["rule"] != "distinct" or c["family"] != fam or (fam == "kgw" and c["colouring"] != "independent"):
            continue
        for a in ALPHAS:
            lv = c["data"]["levels"][a]; ex = exact_ref(lv)
            if ex > 0 and lv["key_mean_level"] > 0:
                xs.append(ex); ys.append(lv["key_mean_level"])
    ax.scatter(xs, ys, s=9, color=COL_FAM[fam], alpha=0.6, label=f"{'KGW independent, both γ' if fam == 'kgw' else 'Gumbel-max'} ({len(xs)} checks)", zorder=3)
xx = np.array([1e-4, 1.0]); ax.plot(xx, xx, color=MUTED, lw=1, zorder=2); ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("exact key-mean level given the texts (binomial; Gumbel: α)"); ax.set_ylabel("observed key-mean level"); ax.legend(fontsize=7, loc="upper left")
ax.set_title(f"(b) S2 (distinct rule, every α): {S2['n_checks']:,} checks, {S2['n_flagged']} flagged", loc="left", fontsize=8.5)
ax = axes[2]
for ru in grid["rules"]:
    es = [e for e in bt if e["family"] == "kgw" and e["h"] == 1 and e["rule"] == ru]
    if es:
        ax.scatter([100 * e["sd_llama"] for e in es], [100 * e["sd_qwen"] for e in es], s=18, marker=MK_RULE[ru], color=COL_RULE[ru], label=f"{ru} rule ({len(es)} cell × length pairs)", zorder=3)
vals = [100 * e["sd_llama"] for e in bt if e["family"] == "kgw" and e["h"] == 1] + [100 * e["sd_qwen"] for e in bt if e["family"] == "kgw" and e["h"] == 1]; vals = [v for v in vals if v > 0]
if vals:
    xx = np.array([min(vals) * 0.7, max(vals) * 1.4]); ax.plot(xx, xx, color=MUTED, lw=1, zorder=2)
ax.set_xscale("log"); ax.set_yscale("log"); logfmt(ax, "both"); ax.set_xlabel("across-key SD of the level (pp), Llama-3.2 tokens"); ax.set_ylabel("across-key SD of the level (pp), Qwen2.5 tokens"); ax.legend(fontsize=7, loc="upper left")
ax.set_title(f"(c) the same texts under both tokenizers (KGW γ = {G0}, h = 1, α = {A_PRIMARY})", loc="left", fontsize=8.5)
fig.tight_layout(); save(fig, "fig6_identities")
for k_, cap in (("fig1_adequacy", "Figure 1 — S1 adequacy on real text: observed against predicted across-key SD of the per-key level, and the ratio against the shift dispersion"),
                ("fig2_length", "Figure 2 — the across-key SD of the level against text length under the three retention rules (h = 1), per corpus cell and tokenizer"),
                ("fig3_width", "Figure 3 — context width: the level's across-key SD at each cell's longest length (raw and distinct rules)"),
                ("fig4_keys", "Figure 4 — the deployer's view: the distribution of per-key levels over the sampled keys by corpus cell (h = 1, the longest length; KGW and Gumbel; raw and distinct)"),
                ("fig5_correlation", "Figure 5 — H-domain: the between-cell correlation of the per-key levels (three settings; the same keys in every cell)"),
                ("fig6_identities", "Figure 6 — the exact-identity check S3, the key-mean audit S2 and the tokenizer axis")):
    T[f"FIG_{k_}"] = f"![{cap}]({('../' + str((OUTDIR / (k_ + '.png')).relative_to(ROOT))) if REAL else (k_ + '.png')})"

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


text = re.sub(r"<<TABLE:([A-Za-z0-9_.]+)>>", sub_table, prose); text = re.sub(r"<<FIG:([A-Za-z0-9_]+)>>", sub_fig, text); text = re.sub(r"\[\[([A-Za-z0-9_.]+)\]\]", sub_val, text)
left = re.findall(r"\[\[[^\]]+\]\]|<<[A-Z]+:[^>]+>>", text)
if left:
    raise SystemExit(f"unresolved placeholders remain: {left[:10]}")
if FIXTURE:
    text = "**FIXTURE RENDER ON A SYNTHETIC INVENTORY (planted numbers; not study outcomes; never the report)**\n\n" + text
REPORT.write_text(text)
unused = sorted(set(VALUES) - USED)
print(f"{VALUES['label']}: wrote {REPORT} ({len(text.split())} words), {len(T)} tables/figures, {len(VALUES)} values ({len(unused)} registered but unused: {unused[:60]}{'…' if len(unused) > 60 else ''})")
print("independent re-computation: all equal to results.json;", json.dumps({k: v for k, v in CHK.items() if k in ("S1", "S2", "S3", "S4", "S5", "deployer", "correlations", "inputs_disclosed_before_lock")}, default=str)[:1800])
