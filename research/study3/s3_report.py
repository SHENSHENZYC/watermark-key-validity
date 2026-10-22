"""Study 3 report builder (protocol v0.1): every table, figure and number in research/STUDY3_REPORT_v0.1.md comes from the locked
outputs (outputs/study3_v0.1/cells/*, results.json, RUN_MANIFEST.json, the pre-lock INPUTS.json), never typed by hand (rule A4.1 of
the research-project-guide).

Before writing anything the builder RE-COMPUTES, with its own code (not s3_analyze's functions), from the record:
  - every descriptive row (87,840 in the production grid): the key-mean, across-key SD, quantiles, extrema, exceedance shares, keys at
    zero, distinct levels and AutoMark's screen (c, r, b, B) from the stored integer counts;
  - every pass-1 summary: the z summaries of every per-key threshold array (the quantiles and means of z(t) and of the null-side cost
    over the keys with a positive threshold; the abstention counts; the order indices from their definitions) and the scheme-level
    thresholds (t_emp, kappa, t_pool, z_emp, z_pool) from the committed thresholds files;
  - T1 (the ratio SD_obs / SD_pred with the key-bootstrap interval under the protocol's seed convention, eligibility, the class, the
    counts and the verdict), T2 (R_pred from the key-free inputs, R_obs with the paired interval, materiality, the class, the counts and
    the verdict) and REP (the nominal SD with Study 3's keys against Study 2's record, Study 2's inventory digest against its pinned
    run manifest, the gross-failure rule and the verdict);
  - in both modes: that every prediction compared with an outcome (the predicted SD, mean level, theory share, population and
    finite-evaluation shares, v, the set moments and the cross-set covariances) equals the key-free INPUTS.json disclosed before the lock
    (the fixture's results come from the locked analyzer reading the same inputs, so the check is real in both modes);
and asserts that all of these equal results.json (every mismatch is collected and reported before raising). It then computes the
builder's own descriptive blocks the protocol lists for the report (the secondary adequacy blocks with T1's statistic; the break-even
N_cal on the diagonal; the diagonal at N_cal = 5,000 against the i.i.d. reference law; the aggregations by pair class), labelled as its
own, and writes <report dir>/: tables.md, tables_*_full.md supplements, descriptive_rows_full.csv.gz, prose_values.json, checks.json and
fig1..fig6 (.png, .svg); then assembles the report from research/study3/report_prose_v0.1.md by filling <<TABLE:name>>, <<FIG:name>>
and [[name]] and refusing any unresolved placeholder (registered-but-unused names are listed).
Usage: .venv/bin/python research/study3/s3_report.py                      (study mode: verifies the lock; writes outputs/study3_v0.1/report/ and research/STUDY3_REPORT_v0.1.md)
       .venv/bin/python research/study3/s3_report.py --fixture --results <results.json of a FIXTURE inventory> --cells <fixture dir>/cells --out-dir <dir outside the repository>
       (fixture mode: every unit record and the results file must carry the FIXTURE marker; the output is labelled FIXTURE and can never be the canonical report or report directory)
Not pinned by the lock.
"""
import gzip, hashlib, json, math, pathlib, re, sys, time
from fractions import Fraction
import numpy as np
import pandas as pd
from scipy.stats import binom, norm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
from matplotlib.colors import LinearSegmentedColormap   # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study2")); sys.path.insert(0, str(ROOT / "research/study1")); sys.path.insert(0, str(ROOT / "tools"))
from s3_run import OUT, STUDY, GRID_CANON, INPUTS, S2_RUN_MANIFEST, verify_lock, expected_units, unit_name, variant_names, cross_variant_names, FAMILIES   # noqa: E402  (pinned; read only)

T_START = time.time()
ARGV = sys.argv[1:]
FIXTURE = "--fixture" in ARGV
PROSE = HERE / "report_prose_v0.1.md"
if FIXTURE:
    RES = pathlib.Path(ARGV[ARGV.index("--results") + 1]).resolve(); CELLS = pathlib.Path(ARGV[ARGV.index("--cells") + 1]).resolve(); OUTDIR = pathlib.Path(ARGV[ARGV.index("--out-dir") + 1]).resolve()
    for p in (RES, CELLS, OUTDIR):
        if ROOT.resolve() in p.parents or p == ROOT.resolve():
            raise SystemExit(f"fixture mode reads and writes outside the repository only ({p})")
    REPORT = OUTDIR / "STUDY3_REPORT_fixture.md"; MANIFEST = None
else:
    if len(ARGV) > 0:
        raise SystemExit("study mode takes no arguments (canonical paths only)")
    RES = ROOT / OUT / "results.json"; CELLS = ROOT / OUT / "cells"; OUTDIR = ROOT / OUT / "report"; REPORT = ROOT / "research" / "STUDY3_REPORT_v0.1.md"; MANIFEST = ROOT / OUT / "RUN_MANIFEST.json"
    if not MANIFEST.exists():
        raise SystemExit("study mode needs outputs/study3_v0.1/RUN_MANIFEST.json (run s3_manifest.py first)")
OUTDIR.mkdir(parents=True, exist_ok=True)
REAL = not FIXTURE
REP_SE, REP_TOL, SCREEN_GS, BOOT_B = 6.0, 1e-12, 0.01, 200
# dataviz palette (validated 2026-10-15 with scripts/validate_palette.js, light surface, all pairs, three slots): the rules raw/distinct are slots 1/2;
# the law relation of a pair uses slots 1/2/3 (same or near-identical law / within English / across languages) with the class told apart by marker;
# the tokenizers by marker and line style, the families by panel; every figure carries a legend and every value is in a table (the relief rule)
COL_RULE = {"raw": "#2a78d6", "distinct": "#eb6834"}; COL_GROUP = {"same": "#2a78d6", "english": "#eb6834", "language": "#1baf7a"}; COL_FAM = {"kgw": "#2a78d6", "gumbel": "#eb6834"}
INK, MUTED, GRIDC, SURFACE = "#0b0b0b", "#898781", "#e1e0d9", "#fcfcfb"; SEQ = ["#cde2fb", "#86b6ef", "#2a78d6", "#104281"]
MK_TOK = {"llama": "o", "qwen": "^"}; LS_TOK = {"llama": "-", "qwen": ":"}; MK_CLASS = {"diagonal": "o", "near_identical": "D", "within_english": "s", "english_other": "o", "other_other": "^"}
GROUP_OF = {"diagonal": "same", "near_identical": "same", "within_english": "english", "english_other": "language", "other_other": "language"}
DIVERGING = LinearSegmentedColormap.from_list("div", ["#e34948", "#f0efec", "#2a78d6"])
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRIDC, "grid.linewidth": 0.8, "grid.linestyle": "-", "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "lines.linewidth": 1.8, "lines.markersize": 4.5, "svg.hashsalt": "study3_v0.1"})   # a fixed salt: the SVG element ids are reproducible (R08 F9)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


# ------------------------------------------------------------------ loading
grid = json.loads((ROOT / GRID_CANON).read_text())
lock = verify_lock(ROOT / OUT / "PRE_RUN_LOCK.json", GRID_CANON, root=ROOT)
LOCK_SHA = sha(ROOT / OUT / "PRE_RUN_LOCK.json")
if RES.exists():
    RES_BYTES = RES.read_bytes()
elif REAL and (ROOT / OUT / "results.json.gz").exists():
    RES_BYTES = gzip.decompress((ROOT / OUT / "results.json.gz").read_bytes())
else:
    raise SystemExit(f"no results file at {RES}")
RES_SHA = hashlib.sha256(RES_BYTES).hexdigest(); res = json.loads(RES_BYTES); del RES_BYTES
if res.get("study") != STUDY or res.get("mode") != "study":
    raise SystemExit(f"results file is not a study-mode analysis of {STUDY}: {res.get('study')!r}, {res.get('mode')!r}")
if FIXTURE and "FIXTURE" not in res:
    raise SystemExit("fixture mode: the results file carries no FIXTURE marker")
if REAL and "FIXTURE" in res:
    raise SystemExit("study mode: the results file carries a FIXTURE marker")
manifest = json.loads(MANIFEST.read_text()) if MANIFEST else None
if REAL:
    if manifest["analysis_output"]["sha256"] != RES_SHA:
        raise SystemExit("results.json differs from the digest recorded in RUN_MANIFEST.json")
    if manifest["lock"]["sha256"] != LOCK_SHA:
        raise SystemExit("RUN_MANIFEST.json names another lock")
inputs = json.loads((ROOT / INPUTS).read_text())
if inputs["grid_sha256"] != sha(ROOT / GRID_CANON) or lock["hashes"][INPUTS] != sha(ROOT / INPUTS):
    raise SystemExit("INPUTS.json is not the pinned key-free inputs of this grid")
P = grid["primary"]; BAND = (float(P["band"][0]), float(P["band"][1])); A_PRIMARY = float(P["alpha"]); ALPHAS = list(grid["alpha"]); IA01 = ALPHAS.index(A_PRIMARY)
TOKS = list(grid["tokenizers"]); TAGS = list(grid["cells"]); HS = list(grid["h"]); RULES = list(grid["rules"]); NCALS = list(grid["N_cal"]); BETA = grid["beta"]; DELTA = grid["delta"]
VS = variant_names(NCALS); VX = cross_variant_names(grid); K = grid["K"]; K_FIT = grid["K_fit"]; N_C = grid["N_cal_set"]
SP = {"cells": TAGS, "toks": grid["tokenizers"], "h": HS, "K": K, "K_fit": K_FIT, "N_cal": NCALS, "N_cal_set": N_C, "N_eval": grid["N_eval"]}
EN = set(grid["english_cells"]); NEAR = set(grid["near_identical_pair"]); LANG = list(grid["language_cells"])
LABEL = {t: f"{t.rsplit('_', 2)[0]}/{t.rsplit('_', 2)[1]}@{t.rsplit('_', 2)[2]}" for t in TAGS}
CLASS_LABEL = {"diagonal": "diagonal", "near_identical": "near-identical", "within_english": "within English", "english_other": "English–other", "other_other": "other–other", "cross_tokenizer": "cross-tokenizer", "fixed": "fixed thresholds"}
CLASS_ORDER = ["diagonal", "near_identical", "within_english", "english_other", "other_other"]
METHOD_LABEL = {"nominal": "nominal", "multiplier20": "multiplier20 (α/20)", "empirical": "empirical multiplier", "pooled": "pooled", "conformal": "per-key conformal", "tolerance": "per-key tolerance"}
UNITS = expected_units(grid, False)
recs = {}; thr = {}; counts = {}
for u in UNITS:
    n = unit_name(u["kind"], u["tokenizer"], u["tag"], u["h"]); d = json.loads((CELLS / f"{n}.json").read_text())
    if FIXTURE and "FIXTURE" not in d:
        raise SystemExit(f"fixture mode: {n} carries no FIXTURE marker")
    if REAL and "FIXTURE" in d:
        raise SystemExit(f"study mode: {n} carries a FIXTURE marker")
    if d.get("unit") != u or (d.get("provenance") or {}).get("lock_sha256") != LOCK_SHA:
        raise SystemExit(f"{n}: the record is not this lock's or disagrees with its slot")
    recs[n] = d
    if u["kind"] == "cal":
        f = CELLS / pathlib.Path(d["thresholds_file"]).name
        if sha(f) != d["thresholds_sha256"]:
            raise SystemExit(f"{n}: the committed thresholds file differs from its recorded digest")
        z = np.load(f); thr[n] = {k: z[k] for k in z.files}
    else:
        f = CELLS / f"{n}.npz"
        if sha(f) != d["npz_sha256"]:
            raise SystemExit(f"{n}: the counts file differs from its recorded digest")
        z = np.load(f); counts[n] = {k: z[k] for k in z.files}
INV_FILES = sorted(f for f in CELLS.iterdir() if f.is_file() and f.suffix in (".json", ".npz"))
INV_SHA = hashlib.sha256("".join(f"{f.name}:{sha(f)}\n" for f in INV_FILES).encode()).hexdigest()
if REAL and INV_SHA != manifest["inventory"]["inventory_sha256"]:
    raise SystemExit("the cells directory differs from the inventory digest of RUN_MANIFEST.json")
S2_CELLS = ROOT / json.loads((ROOT / S2_RUN_MANIFEST).read_text())["inventory"]["cells_dir"]


def tok_label(t):
    return {"llama": "Llama-3.2", "qwen": "Qwen2.5"}.get(t, t)


# ------------------------------------------------------------------ formatting and the value registry
VALUES = {}; USED = set()


def reg(name, value):
    value = fnum(value) if isinstance(value, (int, np.integer)) and not isinstance(value, bool) else str(value); m = re.fullmatch(r"(.+?)–\1", value)
    if m:
        value = m.group(1)
    if name in VALUES and VALUES[name] != value:
        raise SystemExit(f"placeholder {name} registered twice with different values ({VALUES[name]!r} / {value!r})")
    VALUES[name] = value; return VALUES[name]


def fin(x):
    return x is not None and isinstance(x, (int, float, np.floating, np.integer)) and not isinstance(x, bool) and np.isfinite(x)


def fnum(x, d=None):
    """A number for prose or a table: integers with thousands separators; floats to d decimals (default: 3 significant figures)."""
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n/a" if x is None or np.isnan(x) else ("∞" if x > 0 else "−∞")
    if isinstance(x, (bool, np.bool_)):
        return "yes" if x else "no"
    if isinstance(x, (int, np.integer)):
        return f"{int(x):,}"
    x = float(x)
    if d is not None:
        s = f"{x:,.{d}f}"
    else:
        s = f"{x:.3g}" if abs(x) < 1e4 else f"{x:,.0f}"
        if "e" in s:
            s = f"{x:.2e}"
    return s.replace("-", "−")


def pp(x, d=2):
    """A level in percentage points."""
    return "n/a" if not fin(x) else fnum(100 * float(x), d)


def pct(x, d=1):
    return "n/a" if not fin(x) else f"{100 * float(x):.{d}f}%"


def ci(lo, hi, f=fnum):
    return f"[{f(lo)}, {f(hi)}]"


def rng_str(vals, f=fnum):
    vals = [v for v in vals if fin(v)]
    if not vals:
        return "n/a"
    lo, hi = min(vals), max(vals); return f(lo) if f(lo) == f(hi) else f"{f(lo)}–{f(hi)}"


def esc(x):
    return str(x).replace("|", "\\|")


def md_table(header, rows, align=None):
    rows = [[esc(c) for c in r] for r in rows]
    for r in rows:
        if len(r) != len(header):
            raise SystemExit(f"table row has {len(r)} cells, header {len(header)}: {r[:4]}")
    sep = ["---"] * len(header) if align is None else [{"l": ":---", "r": "---:", "c": ":---:"}[a] for a in align]
    return "\n".join(["| " + " | ".join(esc(h) for h in header) + " |", "| " + " | ".join(sep) + " |"] + ["| " + " | ".join(r) + " |" for r in rows])


# ------------------------------------------------------------------ the builder's own statistics (not s3_analyze's functions)
def rng_for(name, salt=20261016):
    """The protocol's seed convention (§8): sha256 of the row name with the analyzer's salt; the builder reproduces the seeded draw."""
    return np.random.default_rng([int(hashlib.sha256(name.encode()).hexdigest()[:8], 16), salt])


def boot_idx(name, salt=20261016, B=BOOT_B):
    return rng_for(name, salt).integers(0, K, size=(B, K))


def summ_own(k, N, a):
    v = np.asarray(k, dtype=np.float64) / N
    return {"key_mean": float(v.mean()), "sd": float(v.std(ddof=1)), "quantiles": {q: float(np.quantile(v, float(q))) for q in ("0.01", "0.05", "0.5", "0.95", "0.99")}, "max": float(v.max()), "min": float(v.min()),
            "share_above_alpha": float(np.mean(v > a)), "share_above_2alpha": float(np.mean(v > 2 * a)), "share_above_5alpha": float(np.mean(v > 5 * a)), "n_zero": int((v == 0).sum()), "n_distinct": int(len(np.unique(v)))}


def screen_own(k, N, a, beta, gs=SCREEN_GS):
    """AutoMark's screen on one evaluation set: c = the smallest count significant at gs for a key at level a; B = #keys with count >= c; b = beta + (1 - beta) r."""
    tail = binom.sf(np.arange(0, N + 2) - 1, N, a)          # P(Bin(N, a) >= c) for c = 0 .. N + 1
    c = int(np.flatnonzero(tail <= gs).min()); r = float(tail[c])
    return {"c": c, "r": r, "b": float(beta + (1 - beta) * r), "B": int((np.asarray(k) >= c).sum())}


def j_conf_own(N, a):
    return int(math.floor(Fraction(str(a)) * (int(N) + 1)))


def j_tol_own(N, a, d):
    cdf = binom.cdf(np.arange(0, int(N) + 1), int(N), a); ok = np.flatnonzero(cdf <= d)
    return min(int(ok.max()) + 1, int(N)) if len(ok) else 0


def zq_own(t, a):
    t = np.asarray(t, dtype=np.float64); n_abs = int((t <= 0).sum()); tp = t[t > 0]; za = float(norm.isf(a))
    out = {"n_positive": int(len(tp)), "n_abstain": n_abs, "z_alpha": za}
    if not len(tp):
        return out | {k: None for k in ("q05", "q50", "q95", "mean", "cost_q05", "cost_q50", "cost_q95", "cost_mean")}
    z = norm.isf(tp); q = {"q05": float(np.quantile(z, 0.05)), "q50": float(np.quantile(z, 0.5)), "q95": float(np.quantile(z, 0.95)), "mean": float(z.mean())}
    return out | q | {f"cost_{k}": v - za for k, v in q.items()}


def classify_band(lo, hi, band=BAND):
    if band[0] <= lo and hi <= band[1]:
        return "consistent"
    if hi < band[0] or lo > band[1]:
        return "inconsistent"
    return "unresolved"


def classify_sign(lo, hi, predicted_above_one):
    if lo > 1 or hi < 1:
        return "agree" if (lo > 1) == predicted_above_one else "disagree"
    return "unresolved"


def pair_class(tagC, tagE):
    if tagC == tagE:
        return "diagonal"
    if {tagC, tagE} == NEAR:
        return "near_identical"
    if tagC in EN and tagE in EN:
        return "within_english"
    if tagC in EN or tagE in EN:
        return "english_other"
    return "other_other"


def pred_of(h, rule, tokC, tagC, tokE, tagE, variant, a):
    """The pre-lock prediction for one row: per-key (method@N_cal) or fixed (nominal, multiplier20 on E; empirical, pooled fitted on C)."""
    blk = inputs["blocks"][f"h{h}|{rule}"]; A = str(a)
    if variant in ("nominal", "multiplier20"):
        return blk["sets"][f"{tokE}|{tagE}|E"]["pred_fixed"][A][variant]
    pk = blk["pairs"][f"{tokC}|{tagC}->{tokE}|{tagE}"]
    return pk["per_key"][variant.split("@")[1]][A][variant.split("@")[0]] if "@" in variant else pk["fixed"][A][variant]


def levels(n, fr, kind, ic=None, iv=None, ia=None, io=None):
    """Per-key levels (K,) of an evaluation unit n: kind 'fixed' (iv in 0/1 = nominal/multiplier20, ia), 'same' (ic, iv, ia) or 'cross' (io, ic, iv)."""
    N_E = recs[n]["N_E"]; arr = counts[n][f"{fr}|{kind}"]
    k = arr[iv, ia] if kind == "fixed" else (arr[ic, iv, ia] if kind == "same" else arr[io, ic, iv])
    return k.astype(np.float64) / N_E


# ------------------------------------------------------------------ the independent re-computation against results.json
MISM = []; CHK = {}
SHARE_KEYS = ("share_above_alpha_pop", "share_above_2alpha_pop", "share_above_5alpha_pop", "share_above_alpha_finite", "share_above_2alpha_finite", "share_above_5alpha_finite")


def close(a, b, tol, what):
    if a is None and b is None:
        return
    if a is None or b is None or not (abs(float(a) - float(b)) <= tol):
        MISM.append(f"{what}: own {a!r} vs results {b!r} (tol {tol})")


def same_num(a, b, what):
    if (a is None) != (b is None) or (a is not None and not (abs(float(a) - float(b)) <= 1e-12 * max(1.0, abs(float(b))))):
        MISM.append(f"{what}: {a!r} vs {b!r}")


t0 = time.time()
# (a) the descriptive rows, in the analyzer's order; the predictions against INPUTS.json
DESC = []; res_desc = res["descriptive_rows"]; n_pred_checked = 0; max_pred_diff = 0.0
for u in UNITS:
    if u["kind"] != "eval":
        continue
    n = unit_name("eval", u["tokenizer"], u["tag"], u["h"]); rec = recs[n]; N_E = rec["N_E"]; tokE, tagE, h = u["tokenizer"], u["tag"], u["h"]
    for f in FAMILIES:
        for r in RULES:
            fr = f"{f}|{r}"
            for ia, a in enumerate(ALPHAS):
                for iv, vname in enumerate(("nominal", "multiplier20")):
                    k = counts[n][f"{fr}|fixed"][iv, ia]; s = summ_own(k, N_E, a); sc = screen_own(k, N_E, a, BETA); pred = pred_of(h, r, None, None, tokE, tagE, vname, a)
                    DESC.append({"family": f, "rule": r, "h": h, "tokE": tokE, "tagE": tagE, "tokC": None, "tagC": None, "class": "fixed", "variant": vname, "alpha": a, "N_E": N_E, **s, "screen_B": sc["B"], "screen_b": sc["b"],
                                 "pred_sd": pred["sd_cond"], "pred_mean": pred["mean_level"], **{f"pred_{k_}": pred[k_] for k_ in SHARE_KEYS}, "pred_theory_share": pred["theory_share"], "pred_flags": pred["flags"]})
            for ic, tagC in enumerate(TAGS):
                cls = pair_class(tagC, tagE)
                for ia, a in enumerate(ALPHAS):
                    for iv, vname in enumerate(VS):
                        k = counts[n][f"{fr}|same"][ic, iv, ia]; s = summ_own(k, N_E, a); sc = screen_own(k, N_E, a, BETA); pred = pred_of(h, r, tokE, tagC, tokE, tagE, vname, a)
                        DESC.append({"family": f, "rule": r, "h": h, "tokE": tokE, "tagE": tagE, "tokC": tokE, "tagC": tagC, "class": cls, "variant": vname, "alpha": a, "N_E": N_E, **s, "screen_B": sc["B"], "screen_b": sc["b"],
                                     "pred_sd": pred["sd_cond"], "pred_mean": pred["mean_level"], **{f"pred_{k_}": pred[k_] for k_ in SHARE_KEYS}, "pred_theory_share": pred["theory_share"], "pred_flags": pred["flags"], "pred_j": pred.get("j")})
            for io, ot in enumerate(rec.get("cross_tokenizers") or []):
                for ic, tagC in enumerate(TAGS):
                    for iv, vname in enumerate(VX):
                        a = grid["cal_bootstrap"]["alpha"]; k = counts[n][f"{fr}|cross"][io, ic, iv]; s = summ_own(k, N_E, a); sc = screen_own(k, N_E, a, BETA); pred = pred_of(h, r, ot, tagC, tokE, tagE, vname, a)
                        DESC.append({"family": f, "rule": r, "h": h, "tokE": tokE, "tagE": tagE, "tokC": ot, "tagC": tagC, "class": "cross_tokenizer", "variant": vname, "alpha": a, "N_E": N_E, **s, "screen_B": sc["B"], "screen_b": sc["b"],
                                     "pred_sd": pred["sd_cond"], "pred_mean": pred["mean_level"], **{f"pred_{k_}": pred[k_] for k_ in SHARE_KEYS}, "pred_theory_share": pred["theory_share"], "pred_flags": pred["flags"], "pred_j": pred.get("j")})
if len(DESC) != len(res_desc):
    MISM.append(f"descriptive rows: own {len(DESC)} vs results {len(res_desc)}")
for own, rr in zip(DESC, res_desc):
    key = tuple(own[k] for k in ("family", "rule", "h", "tokE", "tagE", "tokC", "tagC", "class", "variant", "alpha"))
    if key != tuple(rr[k] for k in ("family", "rule", "h", "tokE", "tagE", "tokC", "tagC", "class", "variant", "alpha")):
        MISM.append(f"descriptive row order differs at {key} vs {tuple(rr[k] for k in ('family', 'rule', 'h', 'tokE', 'tagE', 'tokC', 'tagC', 'class', 'variant', 'alpha'))}"); break
    w = f"desc {key}"
    for k in ("key_mean", "sd", "max", "min", "share_above_alpha", "share_above_2alpha", "share_above_5alpha", "screen_b"):
        close(own[k], rr[k], 1e-12, f"{w} {k}")
    for q in own["quantiles"]:
        close(own["quantiles"][q], rr["quantiles"][q], 1e-12, f"{w} q{q}")
    for k in ("n_zero", "n_distinct", "screen_B"):
        if own[k] != rr[k]:
            MISM.append(f"{w} {k}: own {own[k]} vs results {rr[k]}")
    for k in ("pred_sd", "pred_mean") + tuple(f"pred_{k_}" for k_ in SHARE_KEYS):
        same_num(own[k], rr.get(k), f"{w} {k} (INPUTS vs results)"); n_pred_checked += 1
        if own[k] is not None and rr.get(k) is not None:
            max_pred_diff = max(max_pred_diff, abs(float(own[k]) - float(rr[k])))
    if "pred_theory_share" in rr:
        same_num(own["pred_theory_share"], rr["pred_theory_share"], f"{w} pred_theory_share")
CHK["descriptive_rows_recomputed"] = len(DESC); CHK["predictions_checked_against_inputs"] = n_pred_checked; CHK["max_abs_diff_prediction_results_vs_inputs"] = max_pred_diff
print(f"descriptive rows recomputed: {len(DESC)} ({time.time() - t0:.0f}s)", flush=True)

# (b) the pass-1 summaries from the committed thresholds files
n_z = 0; n_scheme = 0; ORDER_IDX = {}
for u in UNITS:
    if u["kind"] != "cal":
        continue
    n = unit_name("cal", u["tokenizer"], u["tag"], u["h"]); summ = res["pass1"][n]["summary"]; arrays = thr[n]
    if res["pass1"][n]["summary"] != recs[n]["summary"] or res["pass1"][n]["info"] != recs[n]["info"]:
        MISM.append(f"{n}: results.json pass1 block differs from the record")
    for f in FAMILIES:
        for r in RULES:
            fr = f"{f}|{r}"
            for a in ALPHAS:
                for m in grid["methods_per_key"]:
                    for nc in NCALS:
                        j = j_conf_own(nc, a) if m == "conformal" else j_tol_own(nc, a, DELTA); ORDER_IDX[(m, nc, a)] = j
                        t = arrays[f"{fr}|{m}@{nc}|{a}"]; z = summ[fr]["per_key_z"][f"{m}@{nc}|{a}"]
                        if z["j"] != j:
                            MISM.append(f"{n} {fr} {m}@{nc} {a}: order index own {j} vs record {z['j']}")
                        if j == 0 and (t != 0).any():
                            MISM.append(f"{n} {fr} {m}@{nc} {a}: an abstaining method carries a positive threshold")
                        ref = zq_own(t, a); n_z += 1
                        for k_, rv in ref.items():
                            sv = z["z"].get(k_)
                            if rv is None or isinstance(rv, int):
                                if sv != rv:
                                    MISM.append(f"{n} {fr} {m}@{nc} {a}: z field {k_} own {rv!r} vs record {sv!r}")
                            else:
                                close(rv, sv, 1e-12 * max(1.0, abs(rv)), f"{n} {fr} {m}@{nc} {a} z {k_}")
                sc = summ[fr]["scheme"][str(a)]; te = float(arrays[f"{fr}|empirical|{a}"][0]); tp = float(arrays[f"{fr}|pooled|{a}"][0]); n_scheme += 1
                close(te, sc["t_emp"], 1e-12, f"{n} {fr} {a} t_emp"); close(tp, sc["t_pool"], 1e-12, f"{n} {fr} {a} t_pool")
                if te > a + 1e-12:
                    MISM.append(f"{n} {fr} {a}: the empirical threshold exceeds alpha")
                kap = a / te if te > 0 else float("inf")
                if kap == float("inf"):
                    if not (isinstance(sc["kappa_emp"], float) and sc["kappa_emp"] == float("inf")):
                        MISM.append(f"{n} {fr} {a}: kappa at a zero threshold is not +inf")
                else:
                    close(kap, sc["kappa_emp"], 1e-9 * max(1.0, kap), f"{n} {fr} {a} kappa")
                for key_, tv in (("z_emp", te), ("z_pool", tp)):
                    zr = float(norm.isf(tv)) if tv > 0 else None
                    if zr is None:
                        if sc[key_] is not None:
                            MISM.append(f"{n} {fr} {a}: {key_} should be None")
                    else:
                        close(zr, sc[key_], 1e-9 * max(1.0, abs(zr)), f"{n} {fr} {a} {key_}")
CHK["z_summaries_recomputed"] = n_z; CHK["scheme_summaries_recomputed"] = n_scheme
print(f"pass-1 summaries recomputed: {n_z} z summaries, {n_scheme} scheme summaries ({time.time() - t0:.0f}s)", flush=True)

# (c) T1 and T2 under the protocol's seed convention; REP against Study 2's record
T1_OWN = []; T2_OWN = []; REP_OWN = []
s2m = json.loads((ROOT / S2_RUN_MANIFEST).read_text()); s2files = sorted(f for f in S2_CELLS.glob("*.json") if not f.name.startswith("costs__"))
s2dig = hashlib.sha256("".join(f"{f.name}:{sha(f)}\n" for f in s2files).encode()).hexdigest()
CHK["study2_inventory_digest_equals_pinned_manifest"] = bool(s2dig == s2m["inventory"]["inventory_sha256"])
if s2dig != s2m["inventory"]["inventory_sha256"]:
    MISM.append("Study 2's cell inventory differs from its pinned run manifest")
for u in UNITS:
    if u["kind"] != "eval":
        continue
    n = unit_name("eval", u["tokenizer"], u["tag"], u["h"]); tokE, tagE, h = u["tokenizer"], u["tag"], u["h"]; N_E = recs[n]["N_E"]
    for r in RULES:
        fr = f"{P['family']}|{r}"; lvn = levels(n, fr, "fixed", iv=0, ia=IA01)
        if h in P["h"] and tokE in P["tokenizers"]:
            for ic, tagC in enumerate(TAGS):
                cls = pair_class(tagC, tagE)
                for nc in P["N_cal"]:
                    lv = levels(n, fr, "same", ic=ic, iv=VS.index(f"{P['method']}@{nc}"), ia=IA01); pred = pred_of(h, r, tokE, tagC, tokE, tagE, f"{P['method']}@{nc}", A_PRIMARY); pnom = pred_of(h, r, None, None, tokE, tagE, "nominal", A_PRIMARY)
                    name = f"{tokE}|{tagC}->{tagE}|h{h}|{r}|{nc}"; idx = boot_idx(name); sd_b = lv[idx].std(axis=1, ddof=1); sdn_b = lvn[idx].std(axis=1, ddof=1); sd = float(lv.std(ddof=1)); sdn = float(lvn.std(ddof=1))
                    blk = inputs["blocks"][f"h{h}|{r}"]; mC = blk["sets"][f"{tokE}|{tagC}|C{nc}"]; mE = blk["sets"][f"{tokE}|{tagE}|E"]
                    eligible = (pred["theory_share"] >= P["min_theory_share"]) and not pred["flags"] and pred["sd_cond"] > 0
                    row = {"pair": name, "class": cls, "tok": tokE, "tagC": tagC, "tagE": tagE, "h": h, "rule": r, "N_cal": nc, "N_E": int(N_E), "K": K, "j": pred.get("j"), "sd_obs": sd, "sd_pred": pred["sd_cond"], "theory_share": pred["theory_share"],
                           "flags": pred["flags"], "eligible": bool(eligible), "key_mean_obs": float(lv.mean()), "key_mean_pred": pred["mean_level"], "v": pred.get("v"), "v_raw": pred.get("v_raw"), "tau_v": pred.get("tau_v"),
                           "rho_C": mC["rho"], "rho_E": mE["rho"], "rho_CE": blk["pairs"][f"{tokE}|{tagC}->{tokE}|{tagE}"]["cross"][str(nc)]["rho_CE"], "sigma2_C": mC["sigma2"], "sigma2_E": mE["sigma2"], "ratio_point": sd / pred["sd_cond"] if pred["sd_cond"] > 0 else float("nan")}
                    if eligible:
                        lo, hi = float(np.quantile(sd_b, 0.025) / pred["sd_cond"]), float(np.quantile(sd_b, 0.975) / pred["sd_cond"]); row.update({"ratio": sd / pred["sd_cond"], "ratio_ci95": [lo, hi], "class_T1": classify_band(lo, hi)})
                    T1_OWN.append(row)
                    Rp = pred["sd_cond"] / pnom["sd_cond"] if pnom["sd_cond"] > 0 else float("nan"); mb = P["T2_material_band"]; material = bool(np.isfinite(Rp) and (Rp < mb[0] or Rp > mb[1]))
                    rr = sd_b / np.where(sdn_b > 0, sdn_b, np.nan); lo2, hi2 = float(np.nanquantile(rr, 0.025)), float(np.nanquantile(rr, 0.975))
                    row2 = {"pair": name, "class": cls, "tok": tokE, "tagC": tagC, "tagE": tagE, "h": h, "rule": r, "N_cal": nc, "N_E": int(N_E), "K": K, "R_pred": Rp, "R_obs": sd / sdn if sdn > 0 else float("nan"), "R_obs_ci95": [lo2, hi2], "material": material,
                            "sd_nominal_obs": sdn, "sd_nominal_pred": pnom["sd_cond"], "sd_obs": sd, "sd_pred": pred["sd_cond"], "predicted_side": ("helps" if Rp < 1 else "hurts") if np.isfinite(Rp) else "n/a"}
                    if material:
                        row2["class_T2"] = classify_sign(lo2, hi2, Rp > 1)
                    T2_OWN.append(row2)
        if tagE not in grid["rep"]["exclude"]:
            lvr = levels(n, fr, "fixed", iv=0, ia=ALPHAS.index(grid["rep"]["alpha"])); idx = boot_idx(f"rep|{tokE}|{tagE}|{h}|{r}"); se3 = float(lvr[idx].std(axis=1, ddof=1).std(ddof=1)); sd3 = float(lvr.std(ddof=1))
            l2 = json.loads((S2_CELLS / f"{tagE}__{tokE}__kgw__h{h}__independent__g0.25__L256__{r}.json").read_text())["levels"][str(grid["rep"]["alpha"])]
            d = abs(sd3 - l2["sd_obs_conditional"]); th = REP_SE * math.sqrt(se3 ** 2 + l2["sd_obs_boot_se"] ** 2) + REP_TOL
            REP_OWN.append({"tok": tokE, "tag": tagE, "h": h, "rule": r, "sd_s3": sd3, "se_s3": se3, "sd_s2": l2["sd_obs_conditional"], "se_s2": l2["sd_obs_boot_se"], "z": d / (th - REP_TOL), "gross": bool(d > th)})


def rule_summary(rows, key, ok, pass_share):
    rs = [x for x in rows if key in x]; n_ok = sum(x[key] == ok for x in rs); n_res = sum(x[key] != "unresolved" for x in rs)
    return {"n_rows": len(rows), "n_eligible": len(rs), "n_resolved": n_res, f"n_{ok}": n_ok, "n_unresolved": len(rs) - n_res, "share": (n_ok / n_res) if n_res else None, "pass": bool(n_res >= P["min_resolved"] and n_ok / max(n_res, 1) >= pass_share)}


T1S = rule_summary(T1_OWN, "class_T1", "consistent", P["T1_pass_share"]); T2S = rule_summary(T2_OWN, "class_T2", "agree", P["T2_pass_share"])
REPS = {"n_checks": len(REP_OWN), "n_gross": sum(x["gross"] for x in REP_OWN), "pass": bool(REP_OWN) and not any(x["gross"] for x in REP_OWN)}
for nm, own, ref in (("T1", T1S, res["T1"]), ("T2", T2S, res["T2"]), ("REP", REPS, res["REP"])):
    for k in own:
        if k == "share":
            close(own[k], ref.get(k), 1e-12, f"{nm} share")
        elif own[k] != ref.get(k):
            MISM.append(f"{nm} {k}: own {own[k]} vs results {ref.get(k)}")
r_t1 = {x["pair"]: x for x in res["t1_rows"]}; r_t2 = {x["pair"]: x for x in res["t2_rows"]}
if len(r_t1) != len(T1_OWN) or len(r_t2) != len(T2_OWN):
    MISM.append(f"rule rows: own T1 {len(T1_OWN)} / T2 {len(T2_OWN)} vs results {len(r_t1)} / {len(r_t2)}")
for x in T1_OWN:
    y = r_t1.get(x["pair"])
    if y is None:
        MISM.append(f"T1 row {x['pair']} absent from results"); continue
    for k in ("class", "tok", "tagC", "tagE", "h", "rule", "N_cal", "N_E", "K", "j", "eligible", "flags"):
        if x[k] != y.get(k):
            MISM.append(f"T1 {x['pair']} {k}: own {x[k]!r} vs results {y.get(k)!r}")
    for k in ("sd_obs", "key_mean_obs"):
        close(x[k], y[k], 1e-12, f"T1 {x['pair']} {k}")
    for k in ("sd_pred", "theory_share", "key_mean_pred", "v", "v_raw", "tau_v", "rho_C", "rho_E", "rho_CE", "sigma2_C", "sigma2_E"):
        same_num(x[k], y.get(k), f"T1 {x['pair']} {k} (INPUTS vs results)")
    if x["eligible"]:
        close(x["ratio"], y["ratio"], 1e-12, f"T1 {x['pair']} ratio"); close(x["ratio_ci95"][0], y["ratio_ci95"][0], 1e-12, f"T1 {x['pair']} ci lo"); close(x["ratio_ci95"][1], y["ratio_ci95"][1], 1e-12, f"T1 {x['pair']} ci hi")
        if x["class_T1"] != y.get("class_T1"):
            MISM.append(f"T1 {x['pair']} class: own {x['class_T1']} vs results {y.get('class_T1')}")
    elif "class_T1" in y:
        MISM.append(f"T1 {x['pair']}: results classify an ineligible row")
for x in T2_OWN:
    y = r_t2.get(x["pair"])
    if y is None:
        MISM.append(f"T2 row {x['pair']} absent from results"); continue
    for k in ("class", "tok", "tagC", "tagE", "h", "rule", "N_cal", "N_E", "K", "material"):
        if x[k] != y.get(k):
            MISM.append(f"T2 {x['pair']} {k}: own {x[k]!r} vs results {y.get(k)!r}")
    for k in ("R_obs", "sd_nominal_obs"):
        close(x[k], y[k], 1e-12, f"T2 {x['pair']} {k}")
    close(x["R_obs_ci95"][0], y["R_obs_ci95"][0], 1e-12, f"T2 {x['pair']} ci lo"); close(x["R_obs_ci95"][1], y["R_obs_ci95"][1], 1e-12, f"T2 {x['pair']} ci hi")
    same_num(x["R_pred"], y["R_pred"], f"T2 {x['pair']} R_pred"); same_num(x["sd_nominal_pred"], y["sd_nominal_pred"], f"T2 {x['pair']} sd_nominal_pred")
    if x.get("class_T2") != y.get("class_T2"):
        MISM.append(f"T2 {x['pair']} class: own {x.get('class_T2')} vs results {y.get('class_T2')}")
r_rep = {(x["tok"], x["tag"], x["h"], x["rule"]): x for x in res["rep_rows"]}
if len(r_rep) != len(REP_OWN):
    MISM.append(f"REP rows: own {len(REP_OWN)} vs results {len(r_rep)}")
for x in REP_OWN:
    y = r_rep.get((x["tok"], x["tag"], x["h"], x["rule"]))
    if y is None:
        MISM.append(f"REP row {x['tok']} {x['tag']} {x['h']} {x['rule']} absent"); continue
    for k in ("sd_s3", "se_s3", "sd_s2", "se_s2", "z"):
        close(x[k], y[k], 1e-9 * max(1.0, abs(x[k])), f"REP {x['tok']} {x['tag']} h{x['h']} {x['rule']} {k}")
    if x["gross"] != y["gross"]:
        MISM.append(f"REP {x['tok']} {x['tag']} h{x['h']} {x['rule']} gross: own {x['gross']} vs results {y['gross']}")
CHK.update({"T1": T1S, "T2": T2S, "REP": REPS, "t1_rows": len(T1_OWN), "t2_rows": len(T2_OWN), "rep_rows": len(REP_OWN), "n_mismatches": len(MISM), "mode": "FIXTURE" if FIXTURE else "STUDY",
            "lock_sha256": LOCK_SHA, "results_sha256": RES_SHA, "inventory_sha256": INV_SHA})   # no elapsed time in the committed checks file (R08 F9); the timing is printed
(OUTDIR / "checks.json").write_text(json.dumps({"checks": CHK, "mismatches": MISM[:200]}, indent=1, default=str))
if MISM:
    print("\n".join(MISM[:40]))
    raise SystemExit(f"{len(MISM)} mismatches between the builder's re-computation and results.json (checks.json)")
print(f"independent re-computation: all equal to results.json ({time.time() - t0:.0f}s; the elapsed time is not written to checks.json): T1 {T1S} T2 {T2S} REP {REPS}", flush=True)
# ---- end of part 1 (the checks); part 2 (the builder's own blocks, the tables, the figures and the assembly) follows

# ------------------------------------------------------------------ the builder's own descriptive blocks (labelled the builder's; protocol §7)
t0 = time.time()
DF = pd.DataFrame([{k: v for k, v in d.items() if k not in ("quantiles", "pred_flags")} | {f"q{q}": d["quantiles"][q] for q in d["quantiles"]} | {"flagged": bool(d["pred_flags"])} for d in DESC])
DF["ratio"] = np.where(DF["pred_sd"] > 0, DF["sd"] / DF["pred_sd"].where(DF["pred_sd"] > 0), np.nan)
DF["method"] = DF["variant"].str.split("@").str[0]; DF["N_cal"] = DF["variant"].str.split("@").str[1].astype(float)
DF["screen_exceeds"] = DF["screen_B"] > DF["screen_b"] * K
DF["eligible"] = (DF["pred_theory_share"] >= P["min_theory_share"]) & (~DF["flagged"]) & (DF["pred_sd"] > 0)


def unit_of(row):
    return unit_name("eval", row["tokE"], row["tagE"], row["h"])


def levels_of(row):
    """The per-key levels behind one descriptive row."""
    n = unit_of(row); fr = f"{row['family']}|{row['rule']}"
    if row["class"] == "fixed":
        return levels(n, fr, "fixed", iv=("nominal", "multiplier20").index(row["variant"]), ia=ALPHAS.index(row["alpha"]))
    if row["class"] == "cross_tokenizer":
        return levels(n, fr, "cross", io=recs[n]["cross_tokenizers"].index(row["tokC"]), ic=TAGS.index(row["tagC"]), iv=VX.index(row["variant"]))
    return levels(n, fr, "same", ic=TAGS.index(row["tagC"]), iv=VS.index(row["variant"]), ia=ALPHAS.index(row["alpha"]))


def nominal_of(row):
    return levels(unit_of(row), f"{row['family']}|{row['rule']}", "fixed", iv=0, ia=ALPHAS.index(row["alpha"]))


# (1) the secondary adequacy blocks with T1's statistic (the builder's seed convention: salt 20261017; the analyzer's rows are not re-used)
pri_h = DF["h"].isin(P["h"]); pri_same = DF["class"].isin(CLASS_ORDER); a01 = DF["alpha"] == A_PRIMARY; kgw = DF["family"] == P["family"]; conf = DF["method"] == "conformal"
SEC_SEL = {"gumbel": (DF["family"] == "gumbel") & pri_same & pri_h & conf & DF["N_cal"].isin(P["N_cal"]) & a01,
           "h0": kgw & pri_same & (DF["h"] == 0) & conf & DF["N_cal"].isin(P["N_cal"]) & a01,
           "alpha0.05": kgw & pri_same & pri_h & conf & DF["N_cal"].isin(P["N_cal"]) & (DF["alpha"] == 0.05),
           "alpha0.001": kgw & pri_same & pri_h & conf & DF["N_cal"].isin(P["N_cal"]) & (DF["alpha"] == 0.001),
           "ncal500": kgw & pri_same & pri_h & conf & (DF["N_cal"] == 500) & a01,
           "ncal2000": kgw & pri_same & pri_h & conf & (DF["N_cal"] == 2000) & a01,
           "tolerance": kgw & pri_same & pri_h & (DF["method"] == "tolerance") & DF["N_cal"].isin(P["N_cal"]) & a01,
           "cross_tokenizer": kgw & (DF["class"] == "cross_tokenizer") & pri_h & conf & DF["N_cal"].isin(P["N_cal"]) & a01,
           "gumbel_tolerance": (DF["family"] == "gumbel") & pri_same & pri_h & (DF["method"] == "tolerance") & DF["N_cal"].isin(P["N_cal"]) & a01}
SEC_LABEL = {"gumbel": "Gumbel-max (conformal; raw and distinct; h ∈ {1, 2}; N_cal 1,000 and 5,000; α = 0.01)", "h0": "h = 0 (KGW; conformal; N_cal 1,000 and 5,000; α = 0.01)", "alpha0.05": "α = 0.05 (KGW; conformal; h ∈ {1, 2}; N_cal 1,000 and 5,000)",
             "alpha0.001": "α = 0.001 (KGW; conformal; h ∈ {1, 2}; N_cal 1,000 and 5,000)", "ncal500": "N_cal = 500 (KGW; conformal; h ∈ {1, 2}; α = 0.01)", "ncal2000": "N_cal = 2,000 (KGW; conformal; h ∈ {1, 2}; α = 0.01)",
             "tolerance": "per-key tolerance (KGW; h ∈ {1, 2}; N_cal 1,000 and 5,000; α = 0.01)", "cross_tokenizer": "cross-tokenizer (KGW; conformal; h ∈ {1, 2}; N_cal 1,000 and 5,000; α = 0.01)", "gumbel_tolerance": "Gumbel-max, per-key tolerance (h ∈ {1, 2}; N_cal 1,000 and 5,000; α = 0.01)"}
SEC = {}; SEC_ROWS = []
for name, sel in SEC_SEL.items():
    sub = DF[sel]; st = []
    for _, row in sub.iterrows():
        rec_ = {"block": name, **{k: row[k] for k in ("family", "rule", "h", "tokE", "tagE", "tokC", "tagC", "class", "variant", "alpha", "sd", "pred_sd", "pred_theory_share", "key_mean", "pred_mean", "N_E")}, "eligible": bool(row["eligible"]), "status": "ineligible"}
        if row["eligible"]:
            lv = levels_of(row); idx = boot_idx(f"sec|{row['family']}|{row['tokC']}|{row['tagC']}->{row['tokE']}|{row['tagE']}|h{row['h']}|{row['rule']}|{row['variant']}|{row['alpha']}", salt=20261017)
            sd_b = lv[idx].std(axis=1, ddof=1); lo, hi = float(np.quantile(sd_b, 0.025) / row["pred_sd"]), float(np.quantile(sd_b, 0.975) / row["pred_sd"])
            rec_.update({"ratio": float(row["sd"] / row["pred_sd"]), "ratio_ci95": [lo, hi], "status": classify_band(lo, hi)})
        st.append(rec_)
    SEC_ROWS += st
    el = [x for x in st if x["eligible"]]; rs = [x for x in el if x["status"] != "unresolved"]
    SEC[name] = {"candidate": len(st), "eligible": len(el), "resolved": len(rs), "consistent": sum(x["status"] == "consistent" for x in rs), "inconsistent": sum(x["status"] == "inconsistent" for x in rs), "unresolved": len(el) - len(rs),
                 "share": (sum(x["status"] == "consistent" for x in rs) / len(rs)) if rs else None, "ratio_median_resolved": float(np.median([x["ratio"] for x in rs])) if rs else None, "ratio_median_eligible": float(np.median([x["ratio"] for x in el])) if el else None,
                 "ratio_min": min((x["ratio"] for x in rs), default=None), "ratio_max": max((x["ratio"] for x in rs), default=None)}
print(f"secondary blocks: {sum(v['candidate'] for v in SEC.values())} rows ({time.time() - t0:.0f}s)", flush=True)

# (2) the break-even N_cal on the diagonal (paired key bootstrap; the builder's salt 20261018; descriptive)
BE_ROWS = []
for u in UNITS:
    if u["kind"] != "eval":
        continue
    n = unit_name("eval", u["tokenizer"], u["tag"], u["h"]); tok, tag, h = u["tokenizer"], u["tag"], u["h"]; ic = TAGS.index(tag)
    for f in FAMILIES:
        for r in RULES:
            fr = f"{f}|{r}"; lvn = levels(n, fr, "fixed", iv=0, ia=IA01); sdn = float(lvn.std(ddof=1))
            for m in grid["methods_per_key"]:
                row = {"family": f, "rule": r, "h": h, "tok": tok, "tag": tag, "method": m, "sd_nominal": sdn, "break_even": None}
                for nc in NCALS:
                    lv = levels(n, fr, "same", ic=ic, iv=VS.index(f"{m}@{nc}"), ia=IA01); idx = boot_idx(f"be|{f}|{tok}|{tag}|h{h}|{r}|{m}@{nc}", salt=20261018)
                    rr = lv[idx].std(axis=1, ddof=1) / np.where(lvn[idx].std(axis=1, ddof=1) > 0, lvn[idx].std(axis=1, ddof=1), np.nan); sd = float(lv.std(ddof=1))
                    R = sd / sdn if sdn > 0 else float("nan"); lo, hi = float(np.nanquantile(rr, 0.025)), float(np.nanquantile(rr, 0.975))
                    pr_ = pred_of(h, r, tok, tag, tok, tag, f"{m}@{nc}", A_PRIMARY); pn_ = pred_of(h, r, None, None, tok, tag, "nominal", A_PRIMARY)
                    row[f"R{nc}"] = R; row[f"R{nc}_ci"] = [lo, hi]; row[f"Rpred{nc}"] = pr_["sd_cond"] / pn_["sd_cond"] if pn_["sd_cond"] > 0 else float("nan"); row[f"abstain{nc}"] = bool(pr_.get("j", 1) == 0)
                    if row["break_even"] is None and np.isfinite(R) and R < 1 and hi < 1:
                        row["break_even"] = nc
                BE_ROWS.append(row)
BE = pd.DataFrame(BE_ROWS)
print(f"break-even rows: {len(BE)} ({time.time() - t0:.0f}s)", flush=True)

# (3) the diagonal at N_cal in {1,000, 5,000} against the i.i.d. reference law (Beta(j, N + 1 - j); the floor stated)
DIAG_ROWS = []
for _, row in DF[pri_same & (DF["class"] == "diagonal") & a01 & DF["method"].isin(grid["methods_per_key"]) & DF["N_cal"].isin(P["N_cal"])].iterrows():
    nc = int(row["N_cal"]); j = ORDER_IDX[(row["method"], nc, row["alpha"])]; N_E = row["N_E"]
    beta_mean = j / (nc + 1) if j > 0 else 0.0; beta_sd = math.sqrt(j * (nc + 1 - j) / ((nc + 1) ** 2 * (nc + 2))) if j > 0 else 0.0
    floor = math.sqrt(beta_mean * (1 - beta_mean) / N_E) if j > 0 else 0.0
    DIAG_ROWS.append({**{k: row[k] for k in ("family", "rule", "h", "tokE", "tagE", "variant", "method", "key_mean", "sd", "q0.99", "share_above_alpha", "pred_mean", "pred_sd", "pred_theory_share", "pred_share_above_alpha_finite", "ratio", "eligible", "N_E")},
                      "N_cal": nc, "j": j, "beta_mean": beta_mean, "beta_sd": beta_sd, "floor_sd": floor, "beta_plus_floor_sd": math.sqrt(beta_sd ** 2 + floor ** 2),
                      "beta_share_above_alpha": float(1 - __import__("scipy.stats", fromlist=["beta"]).beta.cdf(row["alpha"], j, nc + 1 - j)) if j > 0 else 0.0})
DIAG = pd.DataFrame(DIAG_ROWS)

# (4) the calibration-set component (the runner's cal_boot block: the SD over the B = 50 resamples) and the crossed blocks (the runner's)
CB_ROWS = []; CR_ROWS = []
for u in UNITS:
    if u["kind"] != "eval":
        continue
    n = unit_name("eval", u["tokenizer"], u["tag"], u["h"]); rec = recs[n]
    for fr, blk in rec["cal_boot"].items():
        f, r = fr.split("|")
        for tagc, d in blk.items():
            for mn, vals in d.items():
                CB_ROWS.append({"family": f, "rule": r, "h": u["h"], "tokE": u["tokenizer"], "tagE": u["tag"], "tagC": tagc, "class": pair_class(tagc, u["tag"]), "variant": mn, "B": len(vals["sd"]),
                                **{f"sd_over_cal_{k}": float(np.std(vals[k], ddof=1)) for k in ("key_mean", "sd", "share_above_alpha", "q99")}, **{f"mean_over_cal_{k}": float(np.mean(vals[k])) for k in ("key_mean", "sd", "share_above_alpha", "q99")}})
    for fr, blk in rec["crossed"].items():
        f, r = fr.split("|")
        for v, d in blk.items():
            CR_ROWS.append({"family": f, "rule": r, "h": u["h"], "tok": u["tokenizer"], "tag": u["tag"], "variant": v, "B": d["B"], **{f"{k}_lo": d[k]["ci95"][0] for k in ("q0.01", "q0.05", "q0.5", "q0.95", "q0.99", "max", "share2", "share5")},
                            **{f"{k}_hi": d[k]["ci95"][1] for k in ("q0.01", "q0.05", "q0.5", "q0.95", "q0.99", "max", "share2", "share5")}})
CB = pd.DataFrame(CB_ROWS); CR = pd.DataFrame(CR_ROWS)

# (5) the null-side cost (the runner's pass-1 summaries, recomputed above from the committed arrays)
ZC_ROWS = []
for u in UNITS:
    if u["kind"] != "cal":
        continue
    n = unit_name("cal", u["tokenizer"], u["tag"], u["h"]); summ = recs[n]["summary"]
    for fr, s in summ.items():
        f, r = fr.split("|")
        for key, z in s["per_key_z"].items():
            v, a = key.split("|"); zz = z["z"]
            ZC_ROWS.append({"family": f, "rule": r, "h": u["h"], "tok": u["tokenizer"], "tag": u["tag"], "variant": v, "method": v.split("@")[0], "N_cal": int(v.split("@")[1]), "alpha": float(a), "j": z["j"], "n_positive": zz["n_positive"], "n_abstain": zz["n_abstain"],
                            "z_alpha": zz["z_alpha"], **{k: zz[k] for k in ("q05", "q50", "q95", "mean", "cost_q05", "cost_q50", "cost_q95", "cost_mean")}})
        for a, sc in s["scheme"].items():
            za = float(norm.isf(float(a)))
            for v, tkey, zkey in (("empirical", "t_emp", "z_emp"), ("pooled", "t_pool", "z_pool")):
                ZC_ROWS.append({"family": f, "rule": r, "h": u["h"], "tok": u["tokenizer"], "tag": u["tag"], "variant": v, "method": v, "N_cal": N_C, "alpha": float(a), "j": None, "n_positive": K_FIT if sc[tkey] > 0 else 0, "n_abstain": 0 if sc[tkey] > 0 else K_FIT,
                                "z_alpha": za, "q05": None, "q50": sc[zkey], "q95": None, "mean": sc[zkey], "cost_q05": None, "cost_q50": (sc[zkey] - za) if sc[zkey] is not None else None, "cost_q95": None, "cost_mean": (sc[zkey] - za) if sc[zkey] is not None else None,
                                "kappa": sc["kappa_emp"] if v == "empirical" else None, "t": sc[tkey]})
ZC = pd.DataFrame(ZC_ROWS)
print(f"blocks built ({time.time() - t0:.0f}s)", flush=True)

# ------------------------------------------------------------------ tables
T = {}; T1D = pd.DataFrame(T1_OWN); T2D = pd.DataFrame(T2_OWN); REPD = pd.DataFrame(REP_OWN)
T1D["status"] = T1D["class_T1"].where(T1D["eligible"], "ineligible") if "class_T1" in T1D else "ineligible"
T2D["status"] = T2D["class_T2"].where(T2D["material"], "immaterial") if "class_T2" in T2D else "immaterial"


def counts_t1(sub):
    el = sub[sub["eligible"]]; rs = el[el["status"] != "unresolved"]
    return [len(sub), len(el), len(rs), int((rs["status"] == "consistent").sum()), int((rs["status"] == "inconsistent").sum()), int((el["status"] == "unresolved").sum()), fnum(float(rs["ratio"].median()), 3) if len(rs) else "n/a", fnum(float(el["ratio"].median()), 3) if len(el) else "n/a"]


def counts_t2(sub):
    mt = sub[sub["material"]]; rs = mt[mt["status"] != "unresolved"]
    return [len(sub), len(mt), int((mt["predicted_side"] == "helps").sum()), int((mt["predicted_side"] == "hurts").sum()), len(rs), int((rs["status"] == "agree").sum()), int((rs["status"] == "disagree").sum()), int((mt["status"] == "unresolved").sum())]


T1_HEAD = ["Block", "Candidate", "Eligible", "Resolved", "Consistent", "Inconsistent", "Unresolved", "Median ratio (resolved)", "Median ratio (eligible)"]
T2_HEAD = ["Block", "Rows", "Material", "Predicted helps", "Predicted hurts", "Resolved", "Agree", "Disagree", "Unresolved"]
rows = [["all"] + counts_t1(T1D)] + [[f"class {CLASS_LABEL[c]}"] + counts_t1(T1D[T1D["class"] == c]) for c in CLASS_ORDER]
rows += [[f"N_cal = {nc:,}"] + counts_t1(T1D[T1D["N_cal"] == nc]) for nc in P["N_cal"]] + [[f"rule {r}"] + counts_t1(T1D[T1D["rule"] == r]) for r in RULES]
rows += [[f"h = {h}"] + counts_t1(T1D[T1D["h"] == h]) for h in P["h"]] + [[tok_label(t)] + counts_t1(T1D[T1D["tok"] == t]) for t in TOKS]
T["t1_by_class"] = md_table(T1_HEAD, rows)
rows = [[f"{r} | h = {h} | {tok_label(t)} | N_cal = {nc:,} | {CLASS_LABEL[c]}"] + counts_t1(T1D[(T1D["rule"] == r) & (T1D["h"] == h) & (T1D["tok"] == t) & (T1D["N_cal"] == nc) & (T1D["class"] == c)])
        for r in RULES for h in P["h"] for t in TOKS for nc in P["N_cal"] for c in CLASS_ORDER]
T["t1_by_block"] = md_table(["Rule | h | tokenizer | N_cal | class"] + T1_HEAD[1:], rows)
rows = [["all"] + counts_t2(T2D)] + [[f"class {CLASS_LABEL[c]}"] + counts_t2(T2D[T2D["class"] == c]) for c in CLASS_ORDER] + [[f"N_cal = {nc:,}"] + counts_t2(T2D[T2D["N_cal"] == nc]) for nc in P["N_cal"]]
rows += [[f"rule {r}"] + counts_t2(T2D[T2D["rule"] == r]) for r in RULES] + [[f"h = {h}"] + counts_t2(T2D[T2D["h"] == h]) for h in P["h"]] + [[tok_label(t)] + counts_t2(T2D[T2D["tok"] == t]) for t in TOKS]
rows += [[f"predicted {s}"] + counts_t2(T2D[T2D["predicted_side"] == s]) for s in ("helps", "hurts")]
T["t2_by_class"] = md_table(T2_HEAD, rows)
rows = [[f"{r} | h = {h} | N_cal = {nc:,} | {CLASS_LABEL[c]}"] + counts_t2(T2D[(T2D["rule"] == r) & (T2D["h"] == h) & (T2D["N_cal"] == nc) & (T2D["class"] == c)]) for r in RULES for h in P["h"] for nc in P["N_cal"] for c in CLASS_ORDER]
T["t2_by_block"] = md_table(["Rule | h | N_cal | class"] + T2_HEAD[1:], rows)
DIAG_HEAD = ["Pair (calibration → evaluation)", "Tokenizer", "Rule", "h", "N_cal", "Class", "Status", "Ratio [95% CI]", "SD obs (pp)", "SD pred (pp)", "Key-mean obs (%)", "Key-mean pred (%)", "Theory share", "v", "v_raw", "τ_v", "ρ̄_C", "ρ̄_E", "ρ_CE", "σ_C²", "σ_E²", "j", "N_E", "K"]


def diag_row(x):
    return [f"{LABEL[x['tagC']]} → {LABEL[x['tagE']]}", tok_label(x["tok"]), x["rule"], x["h"], f"{x['N_cal']:,}", CLASS_LABEL[x["class"]], (x.get("class_T1") if x["eligible"] else "ineligible"), f"{fnum(x['ratio'], 3)} {ci(*x['ratio_ci95'], lambda v: fnum(v, 3))}" if x["eligible"] else fnum(x["ratio_point"], 3),
            pp(x["sd_obs"], 3), pp(x["sd_pred"], 3), pct(x["key_mean_obs"], 3), pct(x["key_mean_pred"], 3), fnum(x["theory_share"], 3), fnum(x["v"], 4), fnum(x["v_raw"], 4), fnum(x["tau_v"], 5), fnum(x["rho_C"], 4), fnum(x["rho_E"], 4), fnum(x["rho_CE"], 4), fnum(x["sigma2_C"], 3), fnum(x["sigma2_E"], 3), x["j"], f"{x['N_E']:,}", f"{x['K']:,}"]


fail = [x for x in T1_OWN if x.get("class_T1") in ("inconsistent", "unresolved")]
T["t1_failures"] = md_table(DIAG_HEAD, [diag_row(x) for x in sorted(fail, key=lambda x: (x["class_T1"], x["h"], x["rule"], x["tok"], x["N_cal"], x["tagE"], x["tagC"]))]) if fail else "_No inconsistent or unresolved row._"
T2_ROW_HEAD = ["Pair (calibration → evaluation)", "Tokenizer", "Rule", "h", "N_cal", "Class", "Predicted side", "R_pred", "R_obs [paired 95% CI]", "Status", "SD conformal obs (pp)", "SD nominal obs (pp)", "SD conformal pred (pp)", "SD nominal pred (pp)", "N_E", "K"]


def t2_row(x):
    return [f"{LABEL[x['tagC']]} → {LABEL[x['tagE']]}", tok_label(x["tok"]), x["rule"], x["h"], f"{x['N_cal']:,}", CLASS_LABEL[x["class"]], x["predicted_side"], fnum(x["R_pred"], 3), f"{fnum(x['R_obs'], 3)} {ci(*x['R_obs_ci95'], lambda v: fnum(v, 3))}",
            x.get("class_T2", "immaterial"), pp(x["sd_obs"], 3), pp(x["sd_nominal_obs"], 3), pp(x["sd_pred"], 3), pp(x["sd_nominal_pred"], 3), f"{x['N_E']:,}", f"{x['K']:,}"]


fail2 = [x for x in T2_OWN if x.get("class_T2") in ("disagree", "unresolved")]
T["t2_failures"] = md_table(T2_ROW_HEAD, [t2_row(x) for x in sorted(fail2, key=lambda x: (x["class_T2"], x["h"], x["rule"], x["tok"], x["N_cal"], x["tagE"], x["tagC"]))]) if fail2 else "_No disagreeing or unresolved material row._"
REP_HEAD = ["Tokenizer", "Evaluation cell", "h", "Rule", "SD Study 3 keys (pp)", "SE (pp)", "SD Study 2 keys (pp)", "SE (pp)", "|difference| / threshold", "Gross"]
rows = [[f"{tok_label(t)} | h = {h} | {r}", len(s), int(s["gross"].sum()), fnum(float(s["z"].max()), 3), pp(float(s["sd_s3"].median()), 3), pp(float(s["sd_s2"].median()), 3)] for t in TOKS for h in HS for r in RULES for s in [REPD[(REPD["tok"] == t) & (REPD["h"] == h) & (REPD["rule"] == r)]]]
T["rep"] = md_table(["Tokenizer | h | rule", "Checks", "Gross failures", "Largest |difference| / threshold", "Median SD, Study 3 keys (pp)", "Median SD, Study 2 keys (pp)"], rows)
T["rep_gross"] = md_table(REP_HEAD, [[tok_label(x["tok"]), LABEL[x["tag"]], x["h"], x["rule"], pp(x["sd_s3"], 3), pp(x["se_s3"], 3), pp(x["sd_s2"], 3), pp(x["se_s2"], 3), fnum(x["z"], 3), fnum(x["gross"])] for x in REP_OWN if x["gross"]]) if any(x["gross"] for x in REP_OWN) else "_No gross failure._"
# secondary blocks
rows = [[SEC_LABEL[k], v["candidate"], v["eligible"], v["resolved"], v["consistent"], v["inconsistent"], v["unresolved"], pct(v["share"]) if v["share"] is not None else "n/a", fnum(v["ratio_median_resolved"], 3) if v["ratio_median_resolved"] is not None else "n/a",
         fnum(v["ratio_median_eligible"], 3) if v["ratio_median_eligible"] is not None else "n/a", f"{fnum(v['ratio_min'], 3)}–{fnum(v['ratio_max'], 3)}" if v["ratio_min"] is not None else "n/a"] for k, v in SEC.items()]
T["secondary"] = md_table(["Block (the builder's; T1's statistic and bands; descriptive)", "Candidate", "Eligible", "Resolved", "Consistent", "Inconsistent", "Unresolved", "Share consistent", "Median ratio (resolved)", "Median ratio (eligible)", "Ratio range (resolved)"], rows)
# the diagonal against the i.i.d. reference law
rows = []
for f in FAMILIES:
    for r in RULES:
        for h in P["h"]:
            for m in grid["methods_per_key"]:
                for nc in P["N_cal"]:
                    s = DIAG[(DIAG["family"] == f) & (DIAG["rule"] == r) & (DIAG["h"] == h) & (DIAG["method"] == m) & (DIAG["N_cal"] == nc)]
                    if not len(s):
                        continue
                    rows.append([f, r, h, METHOD_LABEL[m], f"{nc:,}", int(s["j"].iloc[0]), len(s), int(s["eligible"].sum()), pct(float(s["beta_mean"].iloc[0]), 3), rng_str(s["key_mean"], lambda v: pct(v, 3)), pp(float(s["beta_sd"].iloc[0]), 3), rng_str(s["floor_sd"], lambda v: pp(v, 3)),
                                 rng_str(s["pred_sd"], lambda v: pp(v, 3)), rng_str(s["sd"], lambda v: pp(v, 3)), fnum(float(s["ratio"].median()), 3), rng_str(s["ratio"], lambda v: fnum(v, 2)), pct(float(s["beta_share_above_alpha"].iloc[0]), 1), rng_str(s["pred_share_above_alpha_finite"], pct), rng_str(s["share_above_alpha"], pct)])
T["diag_reference"] = md_table(["Family", "Rule", "h", "Method", "N_cal", "j", "Units", "T1-eligible", "Beta mean (%)", "Key-mean obs (%), range", "Beta SD (pp)", "Floor √(ℓ(1−ℓ)/N_E) (pp)", "SD pred (pp), range", "SD obs (pp), range", "Median SD obs / pred", "Range", "Beta share > α", "Predicted finite share > α, range", "Share > α obs, range"], rows)
# the remedy table on the diagonal and by class (KGW, alpha = 0.01, h in {1, 2}; medians over the pairs of the class)
REM_VARIANTS = ["nominal", "multiplier20", "empirical", "pooled", "conformal@1000", "conformal@5000", "tolerance@1000", "tolerance@5000"]
REM_HEAD = ["Rule", "h", "Method", "Pairs", "Key-mean (%)", "SD (pp)", "99% key (%)", "Worst sampled key (%)", "Share > α", "Share > 2α", "Share > 5α", "Keys at 0", "Screen B > b·K (pairs)", "Pred mean (%)", "Pred SD (pp)", "Median SD obs / pred", "Pred share > α (finite)", "Pred share > α (population)"]


def rem_rows(sel_class, fam=P["family"], a=A_PRIMARY, hs=P["h"], variants=REM_VARIANTS, by_class=False):
    out = []
    for r in RULES:
        for h in hs:
            for v in variants:
                base = (DF["family"] == fam) & (DF["alpha"] == a) & (DF["rule"] == r) & (DF["h"] == h) & (DF["variant"] == v)
                s = DF[base & (DF["class"].isin(["fixed"]) if v in ("nominal", "multiplier20") else base & sel_class)]
                if not len(s):
                    continue
                out.append([r, h, v, len(s), pct(float(s["key_mean"].median()), 3), pp(float(s["sd"].median()), 3), pct(float(s["q0.99"].median()), 2), pct(float(s["max"].median()), 2), pct(float(s["share_above_alpha"].median())), pct(float(s["share_above_2alpha"].median())), pct(float(s["share_above_5alpha"].median())),
                            fnum(int(s["n_zero"].median())), int(s["screen_exceeds"].sum()), pct(float(s["pred_mean"].median()), 3), pp(float(s["pred_sd"].median()), 3), fnum(float(s["ratio"].median()), 3), pct(float(s["pred_share_above_alpha_finite"].median())), pct(float(s["pred_share_above_alpha_pop"].median()))])
    return out


T["remedy_diag"] = md_table(REM_HEAD, rem_rows(DF["class"] == "diagonal"))
rows = []
for c in CLASS_ORDER:
    for row in rem_rows(DF["class"] == c, variants=["empirical", "pooled", "conformal@1000", "conformal@5000", "tolerance@1000", "tolerance@5000"]):
        rows.append([CLASS_LABEL[c]] + row)
T["remedy_class"] = md_table(["Class"] + REM_HEAD, rows)
# the exceedance diagnostic (the measured share above alpha beside beta / delta and the finite prediction; the screen)
rows = []
for c in ["diagonal", "near_identical", "within_english", "english_other", "other_other"]:
    for r in RULES:
        for h in P["h"]:
            for v in REM_VARIANTS:
                base = (DF["family"] == P["family"]) & (DF["alpha"] == A_PRIMARY) & (DF["rule"] == r) & (DF["h"] == h) & (DF["variant"] == v)
                s = DF[base & (DF["class"] == "fixed")] if v in ("nominal", "multiplier20") else DF[base & (DF["class"] == c)]
                if not len(s) or (v in ("nominal", "multiplier20") and c != "diagonal"):
                    continue
                ref = {"multiplier20": f"β = {BETA}", "empirical": f"β = {BETA} (fitted on C)", "tolerance@1000": f"δ = {DELTA}", "tolerance@5000": f"δ = {DELTA}"}.get(v, "—")
                rows.append([CLASS_LABEL[c] if v not in ("nominal", "multiplier20") else "(evaluation cell)", r, h, v, len(s), rng_str(s["share_above_alpha"], pct), pct(float(s["share_above_alpha"].median())), ref, pct(float(s["pred_share_above_alpha_finite"].median())), rng_str(s["pred_share_above_alpha_finite"], pct),
                             int(s["screen_exceeds"].sum()), fnum(int(s["screen_B"].median())), fnum(float((s["screen_b"] * K).median()), 1)])
T["exceedance"] = md_table(["Class", "Rule", "h", "Method", "Pairs", "Share > α obs, range", "Median", "Reference", "Pred finite share > α, median", "Range", "Screen B > b·K (pairs)", "Median B", "Median b·K"], rows)
# the null-side cost (medians over the 20 calibration units per setting; KGW alpha = 0.01, h in {1, 2} in the main table)
rows = []
for f in [P["family"]]:
    for r in RULES:
        for h in P["h"]:
            for v in ["empirical", "pooled"] + [f"{m}@{n}" for m in grid["methods_per_key"] for n in NCALS]:
                s = ZC[(ZC["family"] == f) & (ZC["rule"] == r) & (ZC["h"] == h) & (ZC["variant"] == v) & (ZC["alpha"] == A_PRIMARY)]
                if not len(s):
                    continue
                kap = s["kappa"].dropna() if "kappa" in s else pd.Series([], dtype=float)
                rows.append([f, r, h, v, len(s), int(s["n_abstain"].sum()), fnum(float(s["cost_q05"].median()), 3) if s["cost_q05"].notna().any() else "—", fnum(float(s["cost_q50"].median()), 3) if s["cost_q50"].notna().any() else "all abstain", fnum(float(s["cost_q95"].median()), 3) if s["cost_q95"].notna().any() else "—",
                             rng_str(s["cost_q50"], lambda x: fnum(x, 2)) if s["cost_q50"].notna().any() else "—", (f"{fnum(float(kap.median()), 2)} ({rng_str(kap, lambda x: fnum(x, 2))})" if len(kap) else "—")])
T["zcost"] = md_table(["Family", "Rule", "h", "Method", "Units", "Abstaining keys (sum)", "Cost q05, median over units", "Cost q50, median", "Cost q95, median", "Cost q50, range over units", "κ̂ median (range)"], rows)
# the break-even N_cal on the diagonal (counts of units by the smallest N_cal that breaks even)
rows = []
for f in FAMILIES:
    for r in RULES:
        for h in HS:
            for m in grid["methods_per_key"]:
                s = BE[(BE["family"] == f) & (BE["rule"] == r) & (BE["h"] == h) & (BE["method"] == m)]
                be = s["break_even"]; rows.append([f, r, h, METHOD_LABEL[m], len(s)] + [int((be == nc).sum()) for nc in NCALS] + [int(be.isna().sum()), fnum(float(s["R5000"].median()), 3), rng_str(s["R5000"], lambda x: fnum(x, 2)), fnum(float(s["Rpred5000"].median()), 3)])
T["breakeven"] = md_table(["Family", "Rule", "h", "Method", "Units"] + [f"break-even at N_cal = {nc:,}" for nc in NCALS] + ["never (within the grid)", "Median R_obs at N_cal = 5,000", "Range", "Median R_pred at 5,000"], rows)
# the calibration-set component (diagonal; medians over the 20 units)
rows = []
for f in FAMILIES:
    for r in RULES:
        for h in HS:
            for v in [f"{m}@{n}" for m in grid["methods_per_key"] for n in grid["cal_bootstrap"]["N_cal"]]:
                s = CB[(CB["family"] == f) & (CB["rule"] == r) & (CB["h"] == h) & (CB["variant"] == v) & (CB["class"] == "diagonal")]
                rows.append([f, r, h, v, len(s), int(s["B"].iloc[0]), pp(float(s["mean_over_cal_sd"].median()), 3), pp(float(s["sd_over_cal_sd"].median()), 3), rng_str(s["sd_over_cal_sd"], lambda x: pp(x, 3)), pp(float(s["sd_over_cal_key_mean"].median()), 4), pct(float(s["sd_over_cal_share_above_alpha"].median()), 2), pp(float(s["sd_over_cal_q99"].median()), 3)])
T["calboot"] = md_table(["Family", "Rule", "h", "Method", "Units", "B", "Across-key SD, mean over resamples (pp)", "SD of the across-key SD over resamples (pp), median", "Range", "SD of the key-mean (pp)", "SD of the share > α", "SD of the 99% key (pp)"], rows)
# the crossed bootstrap on the diagonal (KGW h = 1, both rules): the 99% key and the share above 2 alpha with crossed intervals, by method
rows = []
for r in RULES:
    for tok in TOKS:
        for tag in TAGS:
            s = CR[(CR["family"] == P["family"]) & (CR["rule"] == r) & (CR["h"] == 1) & (CR["tok"] == tok) & (CR["tag"] == tag)]
            row = [r, tok_label(tok), LABEL[tag], f"{recs[unit_name('eval', tok, tag, 1)]['N_E']:,}"]
            for v in REM_VARIANTS:
                x = s[s["variant"] == v]
                row.append(f"{pct(float(x['q0.99_lo'].iloc[0]), 2)}–{pct(float(x['q0.99_hi'].iloc[0]), 2)}" if len(x) else "n/a")
            rows.append(row)
T["crossed"] = md_table(["Rule", "Tokenizer", "Evaluation cell", "N_E"] + [f"99% key: {v}" for v in REM_VARIANTS], rows)
# the cross-tokenizer transfer (KGW alpha = 0.01, every h; medians over the 200 ordered pairs per setting)
rows = []
for f in FAMILIES:
    for r in RULES:
        for h in HS:
            for v in VX:
                s = DF[(DF["family"] == f) & (DF["rule"] == r) & (DF["h"] == h) & (DF["variant"] == v) & (DF["class"] == "cross_tokenizer")]
                if not len(s):
                    continue
                el = s[s["eligible"]]
                rows.append([f, r, h, v, len(s), int(s["eligible"].sum()), pct(float(s["key_mean"].median()), 3), pp(float(s["sd"].median()), 3), pp(float(s["pred_sd"].median()), 3), fnum(float(el["ratio"].median()), 3) if len(el) else "n/a", rng_str(el["ratio"], lambda x: fnum(x, 2)) if len(el) else "n/a",
                             pct(float(s["share_above_alpha"].median())), pct(float(s["pred_share_above_alpha_finite"].median())), pct(float(s["q0.99"].median()), 2)])
T["cross_tok"] = md_table(["Family", "Rule", "h", "Method", "Ordered pairs", "T1-eligible", "Key-mean (%)", "SD obs (pp)", "SD pred (pp)", "Median SD obs / pred (eligible)", "Range", "Share > α obs", "Pred finite share > α", "99% key (%)"], rows)
# the near-identical pair (the positive control of transfer) beside the two diagonals
rows = []
for tok in TOKS:
    for r in RULES:
        for h in P["h"]:
            for nc in P["N_cal"]:
                for tagC, tagE in [(a_, b_) for a_ in grid["near_identical_pair"] for b_ in grid["near_identical_pair"] if a_ != b_]:   # the grid's list order, never a set's (process-dependent; R08 F9)
                    base = (DF["family"] == P["family"]) & (DF["alpha"] == A_PRIMARY) & (DF["rule"] == r) & (DF["h"] == h) & (DF["variant"] == f"conformal@{nc}") & (DF["tokC"] == tok) & (DF["tokE"] == tok)
                    s_ = DF[base & (DF["class"] == "near_identical") & (DF["tagC"] == tagC) & (DF["tagE"] == tagE)]; dg_ = DF[base & (DF["class"] == "diagonal") & (DF["tagC"] == tagE) & (DF["tagE"] == tagE)]
                    if len(s_) != 1 or len(dg_) != 1:
                        raise SystemExit(f"near-identical table: {len(s_)} transferred and {len(dg_)} diagonal rows for {tok} {tagC}->{tagE} h{h} {r} N_cal {nc} (exactly one expected)")   # R08 F1
                    s = s_.iloc[0]; dg = dg_.iloc[0]
                    t1r = r_t1.get(f"{tok}|{tagC}->{tagE}|h{h}|{r}|{nc}", {})
                    rows.append([tok_label(tok), r, h, f"{nc:,}", f"{LABEL[tagC]} → {LABEL[tagE]}", pp(s["sd"], 3), pp(s["pred_sd"], 3), fnum(s["ratio"], 3), t1r.get("class_T1", "ineligible"), pp(dg["sd"], 3), pp(dg["pred_sd"], 3), pct(s["key_mean"], 3), pct(dg["key_mean"], 3), fnum(t1r.get("v"), 4)])
T["near_identical"] = md_table(["Tokenizer", "Rule", "h", "N_cal", "Pair", "SD obs (pp)", "SD pred (pp)", "Ratio", "T1 status", "Diagonal SD obs (pp)", "Diagonal SD pred (pp)", "Key-mean (%)", "Diagonal key-mean (%)", "v"], rows)
print(f"main tables built ({time.time() - t0:.0f}s)", flush=True)

# ------------------------------------------------------------------ supplements
SUPP = {}
SUPP["tables_t1_full.md"] = ["# Study 3 — every T1 row of the primary block (1,600 (pair, setting) rows; KGW; raw and distinct; h ∈ {1, 2}; both tokenizers; per-key conformal; N_cal 1,000 and 5,000; α = 0.01; K = 1,000 keys; N_E as stated)", "",
                             "Generated by `research/study3/s3_report.py` from the record (the builder's own re-computation, equal to `results.json`). Ineligible rows show the point ratio without an interval.", "", md_table(DIAG_HEAD, [diag_row(x) for x in T1_OWN])]
SUPP["tables_t2_full.md"] = ["# Study 3 — every T2 row of the primary block (1,600 rows; the material rows carry a class)", "", "Generated by `research/study3/s3_report.py`. R_obs = SD(conformal)/SD(nominal) on the same keys and texts; the interval is the paired key bootstrap (200 resamples).", "", md_table(T2_ROW_HEAD, [t2_row(x) for x in T2_OWN])]
SUPP["tables_rep_full.md"] = ["# Study 3 — REP: every check (KGW, α = 0.01; the nominal across-key SD with Study 3's K = 1,000 keys against Study 2's record with its K = 1,000 keys on the same N_E = 10,000 texts; Gutenberg excluded)", "", "Generated by `research/study3/s3_report.py`. Gross failure iff |SD₃ − SD₂| > 6·√(se₃² + se₂²) + 10⁻¹².", "",
                              md_table(REP_HEAD, [[tok_label(x["tok"]), LABEL[x["tag"]], x["h"], x["rule"], pp(x["sd_s3"], 3), pp(x["se_s3"], 3), pp(x["sd_s2"], 3), pp(x["se_s2"], 3), fnum(x["z"], 3), fnum(x["gross"])] for x in REP_OWN])]
SEC_HEAD = ["Block", "Family", "Rule", "h", "Calibration (tokenizer | cell)", "Evaluation (tokenizer | cell)", "Class", "Method", "α", "Status", "Ratio [95% CI]", "SD obs (pp)", "SD pred (pp)", "Theory share", "Key-mean obs (%)", "Key-mean pred (%)", "N_E"]
SUPP["tables_secondary_full.md"] = [f"# Study 3 — the secondary adequacy blocks, every row ({len(SEC_ROWS)} rows; T1's statistic with the builder's seed convention; descriptive)", "", "Generated by `research/study3/s3_report.py`. K = 1,000 keys in every row.", "",
                                    md_table(SEC_HEAD, [[x["block"], x["family"], x["rule"], x["h"], f"{tok_label(x['tokC'])} | {LABEL[x['tagC']]}", f"{tok_label(x['tokE'])} | {LABEL[x['tagE']]}", CLASS_LABEL[x["class"]], x["variant"], x["alpha"], x["status"],
                                                         (f"{fnum(x['ratio'], 3)} {ci(*x['ratio_ci95'], lambda v: fnum(v, 3))}" if x["eligible"] else fnum(x["sd"] / x["pred_sd"] if x["pred_sd"] > 0 else float("nan"), 3)), pp(x["sd"], 3), pp(x["pred_sd"], 3), fnum(x["pred_theory_share"], 3), pct(x["key_mean"], 3), pct(x["pred_mean"], 3), f"{x['N_E']:,}"] for x in SEC_ROWS])]
AGG_HEAD = ["Family", "Rule", "h", "α", "Class", "Method", "Rows", "Key-mean (%), median", "SD (pp), median", "SD range", "99% key (%), median", "Worst key (%), median", "Share > α, median", "Share > 2α", "Share > 5α", "Keys at 0, median", "Screen B > b·K (rows)", "Pred mean (%)", "Pred SD (pp)", "Median SD obs / pred", "Ratio range", "Pred share > α (finite)", "Pred share > α (pop.)", "T1-eligible"]
rows = []
for (f, r, h, a, c, v), s in DF.groupby(["family", "rule", "h", "alpha", "class", "variant"], sort=True):
    rows.append([f, r, h, a, CLASS_LABEL[c], v, len(s), pct(float(s["key_mean"].median()), 3), pp(float(s["sd"].median()), 3), rng_str(s["sd"], lambda x: pp(x, 3)), pct(float(s["q0.99"].median()), 2), pct(float(s["max"].median()), 2), pct(float(s["share_above_alpha"].median())), pct(float(s["share_above_2alpha"].median())), pct(float(s["share_above_5alpha"].median())),
                 fnum(int(s["n_zero"].median())), int(s["screen_exceeds"].sum()), pct(float(s["pred_mean"].median()), 3), pp(float(s["pred_sd"].median()), 3), fnum(float(s["ratio"].median()), 3) if s["ratio"].notna().any() else "n/a", rng_str(s["ratio"], lambda x: fnum(x, 2)), pct(float(s["pred_share_above_alpha_finite"].median())), pct(float(s["pred_share_above_alpha_pop"].median())), int(s["eligible"].sum())])
SUPP["tables_remedy_full.md"] = [f"# Study 3 — the remedy table, every (family, rule, h, α, class, method) block ({len(rows)} blocks; medians over the rows of the block; K = 1,000 keys per row; N_E = 10,000, Gutenberg 7,122)", "", "Generated by `research/study3/s3_report.py` from the builder's re-computation of every descriptive row. The predicted shares are two estimands (population and finite-evaluation; the finite one is comparable with the measured share).", "", md_table(AGG_HEAD, rows)]
PAIR_HEAD = ["Family", "Rule", "h", "Calibration cell", "Evaluation (tokenizer | cell)", "Class", "Method", "Key-mean (%)", "SD (pp)", "1% key", "5% key", "Median key", "95% key", "99% key", "Worst key", "Share > α", "Share > 2α", "Share > 5α", "Keys at 0", "Distinct levels", "Screen B", "b·K", "Pred mean (%)", "Pred SD (pp)", "SD obs / pred", "Theory share", "Pred share > α (finite)", "Pred share > 2α (finite)", "Pred share > 5α (finite)", "N_E"]
sub = DF[(DF["family"] == P["family"]) & (DF["alpha"] == A_PRIMARY) & (DF["class"] != "cross_tokenizer")]
SUPP["tables_pairs_kgw_alpha0.01_full.md"] = [f"# Study 3 — every (pair, method) row of the KGW family at α = 0.01 within a tokenizer, plus the fixed thresholds ({len(sub)} rows; K = 1,000 keys; levels in %)", "", "Generated by `research/study3/s3_report.py`. The complete 87,840-row table (both families, every α, the cross-tokenizer rows) is `descriptive_rows_full.csv.gz`.", "",
                                             md_table(PAIR_HEAD, [[x["family"], x["rule"], x["h"], LABEL[x["tagC"]] if isinstance(x["tagC"], str) else "—", f"{tok_label(x['tokE'])} | {LABEL[x['tagE']]}", CLASS_LABEL[x["class"]], x["variant"], pct(x["key_mean"], 3), pp(x["sd"], 3), pct(x["q0.01"], 2), pct(x["q0.05"], 2), pct(x["q0.5"], 2), pct(x["q0.95"], 2), pct(x["q0.99"], 2), pct(x["max"], 2),
                                                                   pct(x["share_above_alpha"]), pct(x["share_above_2alpha"]), pct(x["share_above_5alpha"]), x["n_zero"], x["n_distinct"], x["screen_B"], fnum(x["screen_b"] * K, 1), pct(x["pred_mean"], 3), pp(x["pred_sd"], 3), fnum(x["ratio"], 3), fnum(x["pred_theory_share"], 3), pct(x["pred_share_above_alpha_finite"]), pct(x["pred_share_above_2alpha_finite"]), pct(x["pred_share_above_5alpha_finite"]), f"{x['N_E']:,}"] for _, x in sub.iterrows()])]
with gzip.GzipFile(OUTDIR / "descriptive_rows_full.csv.gz", "wb", mtime=0) as fh:          # no timestamp: the build is byte-reproducible
    fh.write(DF.drop(columns=["flagged"]).to_csv(index=False).encode())
SUPP["tables_zcost_full.md"] = [f"# Study 3 — the null-side cost z(t) − z_α, every calibration unit, family, rule, method, N_cal and α ({len(ZC)} rows; the per-key methods over the K = 1,000 evaluation keys with a positive threshold, the scheme-level methods over the K_fit = 1,000 fitting keys on N_C = 5,000 calibration texts)", "",
                                "Generated by `research/study3/s3_report.py` from the committed thresholds files (the runner's summaries recomputed). An abstaining method (j = 0) has no quantiles.", "",
                                md_table(["Family", "Rule", "h", "Tokenizer", "Calibration cell", "Method", "α", "j", "Keys with a positive threshold", "Abstaining keys", "z_α", "z(t) q05", "q50", "q95", "mean", "Cost q05", "Cost q50", "Cost q95", "Cost mean", "κ̂", "t"],
                                         [[x["family"], x["rule"], x["h"], tok_label(x["tok"]), LABEL[x["tag"]], x["variant"], x["alpha"], x["j"] if x["j"] is not None else "—", x["n_positive"], x["n_abstain"], fnum(x["z_alpha"], 3)] + [fnum(x[k], 3) if x[k] is not None and not (isinstance(x[k], float) and np.isnan(x[k])) else "—" for k in ("q05", "q50", "q95", "mean", "cost_q05", "cost_q50", "cost_q95", "cost_mean")] +
                                          [fnum(x["kappa"], 3) if fin(x.get("kappa")) else "—", f"{x['t']:.3e}" if fin(x.get("t")) else "—"] for x in ZC_ROWS])]
SUPP["tables_breakeven_full.md"] = [f"# Study 3 — the break-even N_cal on the diagonal, every unit ({len(BE)} rows; paired key bootstrap over the K = 1,000 keys; N_E = 10,000, Gutenberg 7,122; α = 0.01; descriptive)", "", "Generated by `research/study3/s3_report.py`. R = SD(method@N_cal)/SD(nominal) on the same keys and texts; the break-even is the smallest N_cal with R < 1 and the paired interval's upper bound below 1.", "",
                                    md_table(["Family", "Rule", "h", "Tokenizer", "Cell", "Method", "SD nominal (pp)"] + [f"R at N_cal = {nc:,} [95% CI] (pred)" for nc in NCALS] + ["Break-even N_cal"],
                                             [[x["family"], x["rule"], x["h"], tok_label(x["tok"]), LABEL[x["tag"]], METHOD_LABEL[x["method"]], pp(x["sd_nominal"], 3)] + [(f"{fnum(x[f'R{nc}'], 3)} {ci(*x[f'R{nc}_ci'], lambda v: fnum(v, 3))} ({fnum(x[f'Rpred{nc}'], 3)})" + (" abstains" if x[f"abstain{nc}"] else "")) for nc in NCALS] + [f"{int(x['break_even']):,}" if x["break_even"] else "never"] for x in BE_ROWS])]
SUPP["tables_calboot_full.md"] = [f"# Study 3 — the calibration-set component, every evaluation unit, family, rule, same-tokenizer calibration source and per-key method ({len(CB)} rows; B = 50 resamples of the N_cal calibration texts; α = 0.01; each across-key summary over the K = 1,000 keys on the N_E evaluation texts, 10,000 or 7,122 for Gutenberg; the SD over resamples of that summary, not the variability of any one key's level)", "", "Generated by `research/study3/s3_report.py` from the runner's `cal_boot` blocks. Descriptive; no rule uses it.", "",
                                  md_table(["Family", "Rule", "h", "Evaluation (tokenizer | cell)", "Calibration cell", "Class", "Method", "B", "Key-mean: mean over resamples (%)", "SD over resamples (pp)", "Across-key SD: mean (pp)", "SD over resamples (pp)", "Share > α: mean", "SD over resamples", "99% key: mean (%)", "SD over resamples (pp)"],
                                           [[x["family"], x["rule"], x["h"], f"{tok_label(x['tokE'])} | {LABEL[x['tagE']]}", LABEL[x["tagC"]], CLASS_LABEL[x["class"]], x["variant"], x["B"], pct(x["mean_over_cal_key_mean"], 3), pp(x["sd_over_cal_key_mean"], 4), pp(x["mean_over_cal_sd"], 3), pp(x["sd_over_cal_sd"], 4), pct(x["mean_over_cal_share_above_alpha"]), pct(x["sd_over_cal_share_above_alpha"], 2), pct(x["mean_over_cal_q99"], 2), pp(x["sd_over_cal_q99"], 3)] for x in CB_ROWS])]
CRK = ("q0.01", "q0.05", "q0.5", "q0.95", "q0.99", "max", "share2", "share5")
SUPP["tables_crossed_full.md"] = [f"# Study 3 — the crossed key-by-document bootstrap on the diagonal, every unit, family, rule and registered method ({len(CR)} rows; B = 200; α = 0.01; K = 1,000 keys and the N_E evaluation texts of the unit, 10,000 or 7,122 for Gutenberg, both resampled; the maximum is the sampled maximum's interval, never a population extreme)", "", "Generated by `research/study3/s3_report.py` from the runner's `crossed` blocks.", "",
                                  md_table(["Family", "Rule", "h", "Tokenizer", "Cell", "Method", "B"] + [f"{k} 95% CI" for k in CRK], [[x["family"], x["rule"], x["h"], tok_label(x["tok"]), LABEL[x["tag"]], x["variant"], x["B"]] + [f"{pct(x[f'{k}_lo'], 2)}–{pct(x[f'{k}_hi'], 2)}" for k in CRK] for x in CR_ROWS])]
SUPP["tables_diag_reference_full.md"] = [f"# Study 3 — the diagonal against the i.i.d. reference law, every unit ({len(DIAG)} rows; α = 0.01; conformal and tolerance at N_cal 1,000 and 5,000; K = 1,000 keys)", "", "Generated by `research/study3/s3_report.py`. Beta(j, N_cal + 1 − j) is the model's reference law for a key whose calibration texts are i.i.d. draws from its continuous score law; the floor is √(ℓ(1 − ℓ)/N_E) at the Beta mean.", "",
                                         md_table(["Family", "Rule", "h", "Tokenizer", "Cell", "Method", "N_cal", "j", "T1-eligible", "Beta mean (%)", "Key-mean obs (%)", "Beta SD (pp)", "Floor (pp)", "√(Beta² + floor²) (pp)", "SD pred (pp)", "SD obs (pp)", "SD obs / pred", "Theory share", "Beta share > α", "Pred finite share > α", "Share > α obs", "99% key (%)", "N_E"],
                                                  [[x["family"], x["rule"], x["h"], tok_label(x["tokE"]), LABEL[x["tagE"]], METHOD_LABEL[x["method"]], f"{x['N_cal']:,}", x["j"], fnum(x["eligible"]), pct(x["beta_mean"], 3), pct(x["key_mean"], 3), pp(x["beta_sd"], 3), pp(x["floor_sd"], 3), pp(x["beta_plus_floor_sd"], 3), pp(x["pred_sd"], 3), pp(x["sd"], 3), fnum(x["ratio"], 3), fnum(x["pred_theory_share"], 3), pct(x["beta_share_above_alpha"]), pct(x["pred_share_above_alpha_finite"]), pct(x["share_above_alpha"]), pct(x["q0.99"], 2), f"{x['N_E']:,}"] for x in DIAG_ROWS])]
for name_, lines_ in SUPP.items():
    (OUTDIR / name_).write_text("\n".join(lines_) + "\n")

# ------------------------------------------------------------------ the run (manifest), the integrity table and the promised-output checklist
reg("label", "FIXTURE RENDER (synthetic inventory; not an outcome)" if FIXTURE else "STUDY"); reg("lock_sha", LOCK_SHA); reg("results_sha", RES_SHA); reg("inventory_digest", INV_SHA[:12] + "…"); reg("n_files", len(INV_FILES)); reg("n_units", len(UNITS))
reg("K", K); reg("K_fit", K_FIT); reg("key_eval_range", f"{grid['key_eval_start']:,}–{grid['key_eval_start'] + K - 1:,}"); reg("key_fit_range", f"{grid['key_fit_start']:,}–{grid['key_fit_start'] + K_FIT - 1:,}"); reg("N_C", N_C); reg("N_E", grid["N_eval"]); reg("N_E_gutenberg", grid["N_eval_gutenberg"])
reg("n_cells", len(TAGS)); reg("n_tok", len(TOKS)); reg("n_h", len(HS)); reg("n_desc_rows", len(DESC)); reg("n_z_summaries", n_z); reg("n_scheme_summaries", n_scheme); reg("n_pred_checked", n_pred_checked); reg("max_pred_diff", fnum(max_pred_diff)); reg("n_t1_rows", len(T1_OWN)); reg("n_t2_rows", len(T2_OWN)); reg("n_rep_rows", len(REP_OWN))
reg("conductor", "Claude (Fable 5.1, in Claude Code)"); reg("reviewer", "Codex (OpenAI)"); reg("r08_status", "open (round 1 requested with this report)" if REAL else "n/a (fixture)")
if manifest:
    run = manifest["run"]; reg("run_start", run["start_utc"]); reg("run_end", run["end_utc"]); reg("run_hours", fnum(run["duration_hours"], 3)); reg("run_projected_hours", fnum(run["projected_hours"], 3)); reg("run_sum_unit_hours", fnum(run["sum_unit_hours"], 3))
    reg("run_restarts", run["n_start_lines"] - 1); reg("run_reused", len(run["reused_units_on_resume"])); reg("run_peak_rss", fnum(run["peak_rss_gb_max"], 2)); reg("run_head", (manifest["git"]["launch"].get("head_at_launch") or "n/a")[:7]); reg("run_swap", manifest["git"]["launch"].get("swap_at_launch") or "n/a")
    reg("manifest_written", manifest["written_utc"]); reg("run_command", manifest["git"]["launch"].get("command") or "n/a"); reg("results_bytes", f"{manifest['analysis_output']['bytes'] / 1e6:.0f} MB")
    rows = []
    for h in HS:
        pr_ = [p for p in manifest["pairs"] if p["pair"].endswith(f"|h{h}")]; s_ = sum(p["seconds"] for p in pr_); pj = sum(p["projected_seconds"] or 0 for p in pr_)
        rows.append([f"h = {h}", len(pr_), fnum(s_ / 60, 1), fnum(pj / 60, 1), fnum(s_ / pj, 2) if pj else "n/a", run["h_done"].get(str(h), {}).get("done_utc", "n/a"), fnum(run["h_done"].get(str(h), {}).get("peak_rss_gb_log"), 2)])
    rows.append(["all", len(manifest["pairs"]), fnum(run["sum_unit_seconds"] / 60, 1), fnum(run["projected_hours"] * 60, 1), fnum(run["sum_unit_hours"] / run["projected_hours"], 2), run["end_utc"], fnum(run["peak_rss_gb_max"], 2)])
    T["timing"] = md_table(["Width", "(tokenizer, cell) pairs", "Measured minutes (sum of the unit times)", "Projected minutes (the validator's model)", "Measured / projected", "Done (UTC)", "Peak RSS so far (GB)"], rows)
    SUPP["tables_timing_full.md"] = ["# Study 3 — the measured against the projected time of every (tokenizer, cell, width) pair", "", "Generated by `research/study3/s3_report.py` from `RUN_MANIFEST.json`.", "", md_table(["Pair", "Pass 1 (s)", "Pass 2 (s)", "Sum (s)", "Projected (s)", "Measured / projected"], [[p["pair"], fnum(p["cal_seconds"], 1), fnum(p["eval_seconds"], 1), fnum(p["seconds"], 1), fnum(p["projected_seconds"], 1), fnum(p["seconds"] / p["projected_seconds"], 2) if p["projected_seconds"] else "n/a"] for p in manifest["pairs"]])]
    (OUTDIR / "tables_timing_full.md").write_text("\n".join(SUPP["tables_timing_full.md"]) + "\n")
else:
    for k_ in ("run_start", "run_end", "run_hours", "run_projected_hours", "run_sum_unit_hours", "run_restarts", "run_reused", "run_peak_rss", "run_head", "run_swap", "manifest_written", "run_command", "results_bytes"):
        reg(k_, "n/a (fixture; no manifest)")
    T["timing"] = "_No run manifest (fixture)._"
T["integrity"] = md_table(["Check", "Result"], [["The lock verified by the builder (schema, canonical identity, the digests of the twenty pinned files, the resolution memo)", f"yes (SHA-256 {LOCK_SHA[:12]}…)"], ["The record's inventory digest against `RUN_MANIFEST.json`", "equal" if REAL else "n/a (fixture)"], ["`results.json` against the digest in `RUN_MANIFEST.json`", "equal" if REAL else "n/a (fixture)"],
                                                 ["Every unit record carries this lock's digest and its slot; every counts and thresholds file at its recorded digest", "yes"], ["Descriptive rows re-computed from the counts and equal to `results.json`", f"{len(DESC):,}"], ["Pass-1 z summaries and scheme summaries re-computed from the committed thresholds files and equal", f"{n_z:,} and {n_scheme:,}"],
                                                 ["T1, T2 and REP rows re-derived under the protocol's seed convention and equal (every field, interval and class)", f"{len(T1_OWN):,}, {len(T2_OWN):,} and {len(REP_OWN):,}"], ["Predictions compared with outcomes equal the pre-lock `INPUTS.json` (largest difference)", f"{n_pred_checked:,} fields; {fnum(max_pred_diff)}"],
                                                 ["Study 2's cell inventory against its pinned run manifest (REP's reference)", "equal" if CHK["study2_inventory_digest_equals_pinned_manifest"] else "DIFFERS"], ["FIXTURE markers", "none in the record (study mode refuses them)" if REAL else "every unit and the results file (fixture mode requires them)"],
                                                 ["Mismatches between the builder's re-computation and `results.json`", str(len(MISM))]])
T["promised"] = md_table(["Protocol §7 promised output", "Estimand and denominator", "Where (this report)", "Done"], [
    ["The remedy table per method × pair class × family × rule × h × α (key-mean, SD, quantiles, max, shares above α/2α/5α, keys at 0, the screen, the predicted mean, SD and shares as two estimands)", "Over the K = 1,000 evaluation keys on the N_E evaluation texts of the evaluation cell (N_E = 10,000; Gutenberg 7,122); medians over the pairs of a block", "Tables 8–9 (KGW, α = 0.01, h ∈ {1, 2}); every block in `tables_remedy_full.md`; every pair in `tables_pairs_kgw_alpha0.01_full.md` and `descriptive_rows_full.csv.gz`", "✓"],
    ["The exceedance diagnostic per method: the measured share above α beside β / δ and the finite-evaluation prediction, with the screen", "The share over the K keys of realised levels above α on the N_E texts; B over the K keys against b·K", "Table 10; Figure 6; every block in `tables_remedy_full.md`", "✓"],
    ["The null-side cost per calibration unit, family, rule, method, N_cal and α (z(t) and z(t) − z_α quantiles and mean over the keys with a positive threshold; n_positive, n_abstain; κ̂, t_emp, t_pool, z_emp, z_pool)", "Over the K evaluation keys with a positive threshold (per-key methods) or the K_fit = 1,000 fitting keys on the N_C = 5,000 calibration texts (scheme-level)", "Table 11 (medians over the 20 units); Figure 5; every unit in `tables_zcost_full.md`", "✓"],
    ["The break-even N_cal per diagonal setting", "Paired over the K keys (the same resampled keys in numerator and denominator); the builder's computation, descriptive", "Table 12; Figure 4; every unit in `tables_breakeven_full.md`", "✓"],
    ["The calibration-set component (B = 50): the SD over calibration resamples of the key-mean, SD, share above α and 99% key of the per-key methods (α = 0.01; N_cal 1,000 and 5,000; every same-tokenizer calibration cell)", "Over the K keys per resample; the SD over the B resamples", "Table 13 (diagonal; medians over the 20 units); every unit and source in `tables_calboot_full.md`", "✓"],
    ["The crossed key-by-document bootstrap on the diagonal (B = 200): the quantiles, the sampled maximum and the shares above 2α and 5α for every registered method", "Texts and keys resampled; the maximum is the sampled maximum's interval, never a population extreme", "Table 14 (KGW h = 1, the 99% key by method); every unit, family, rule and method in `tables_crossed_full.md`", "✓"],
    ["The cross-tokenizer transfer with its prediction", "Over the K keys (the same key under the other tokenizer's tokens); α = 0.01", "Table 15; the secondary block in Table 7; every row in `descriptive_rows_full.csv.gz`", "✓"],
    ["The Gumbel family, h = 0, α = 0.05 and 0.001, N_cal = 500 and 2,000: the same summaries with T1's statistic as a secondary block", "As the remedy table; T1's statistic with the builder's seed convention", "Table 7 (the builder's blocks, with the tolerance and cross-tokenizer blocks added); every row in `tables_secondary_full.md`; the summaries in `tables_remedy_full.md`", "✓"],
    ["T1 and T2 rows with every diagnostic", "As §6 (K = 1,000; N_E stated per row)", "Tables 3–4 (the non-consistent and the non-agreeing rows); every row in `tables_t1_full.md` and `tables_t2_full.md`", "✓"],
    ["REP", "§9: the nominal across-key SD at α = 0.01 with Study 3's keys against Study 2's record with its keys, on the same texts", "Table 5; every check in `tables_rep_full.md`", "✓"],
    ["The near-identical pair as the positive control of transfer (no rule)", "Over the K keys; against the two cells' own diagonals", "Table 16", "✓"],
    ["The diagonal at N_cal = 5,000 reported descriptively against the i.i.d. reference law with the floor stated (never T1-eligible)", "Over the K keys; Beta(j, N_cal + 1 − j) and √(ℓ(1 − ℓ)/N_E)", "Table 6; every unit in `tables_diag_reference_full.md`", "✓"]])

# ------------------------------------------------------------------ prose values
def reg_counts(prefix, sub):
    c = counts_t1(sub); reg(f"{prefix}_candidate", c[0]); reg(f"{prefix}_eligible", c[1]); reg(f"{prefix}_resolved", c[2]); reg(f"{prefix}_consistent", c[3]); reg(f"{prefix}_inconsistent", c[4]); reg(f"{prefix}_unresolved", c[5]); reg(f"{prefix}_ratio_median", c[6]); reg(f"{prefix}_ratio_median_eligible", c[7])


reg_counts("t1", T1D)
for c in CLASS_ORDER:
    reg_counts(f"t1_{c}", T1D[T1D["class"] == c]); reg(f"t1_inel_{c}", int((~T1D[T1D["class"] == c]["eligible"]).sum()))
for nc in P["N_cal"]:
    reg_counts(f"t1_n{nc}", T1D[T1D["N_cal"] == nc])
for r in RULES:
    reg_counts(f"t1_{r}", T1D[T1D["rule"] == r])
for h in P["h"]:
    reg_counts(f"t1_h{h}", T1D[T1D["h"] == h])
for t in TOKS:
    reg_counts(f"t1_{t}", T1D[T1D["tok"] == t])
reg("t1_ineligible", int((~T1D["eligible"]).sum())); reg("t1_share", pct(T1S["share"]) if T1S["share"] is not None else "n/a"); reg("t1_pass_share", pct(P["T1_pass_share"], 0)); reg("t1_min_resolved", P["min_resolved"]); reg("t1_verdict", "PASS" if T1S["pass"] else "FAIL")
el = T1D[T1D["eligible"]]; rs = el[el["status"] != "unresolved"]
reg("t1_ratio_min", fnum(float(rs["ratio"].min()), 3)); reg("t1_ratio_max", fnum(float(rs["ratio"].max()), 3)); reg("t1_ratio_q10", fnum(float(el["ratio"].quantile(0.1)), 3)); reg("t1_ratio_q90", fnum(float(el["ratio"].quantile(0.9)), 3)); reg("t1_ratio_q25", fnum(float(el["ratio"].quantile(0.25)), 3)); reg("t1_ratio_q75", fnum(float(el["ratio"].quantile(0.75)), 3))
reg("t1_eligible_below1", int((el["ratio"] < 1).sum())); reg("t1_eligible_above1", int((el["ratio"] > 1).sum()))
fl = T1D[T1D["status"].isin(["inconsistent", "unresolved"])]
reg("t1_fail_n", len(fl)); reg("t1_fail_above1_n", int((fl["ratio"] > 1).sum())); reg("t1_fail_below1_n", int((fl["ratio"] < 1).sum())); reg("t1_fail_ratio_range", rng_str(fl["ratio"], lambda x: fnum(x, 2)) if len(fl) else "n/a")
for r in RULES:
    reg(f"t1_fail_{r}_n", int((fl["rule"] == r).sum()))
for h in P["h"]:
    reg(f"t1_fail_h{h}_n", int((fl["h"] == h).sum()))
for nc in P["N_cal"]:
    reg(f"t1_fail_n{nc}_n", int((fl["N_cal"] == nc).sum()))
for t in TOKS:
    reg(f"t1_fail_{t}_n", int((fl["tok"] == t).sum()))
reg("t1_fail_by_tagE", "; ".join(f"{LABEL[t]}: {n_}" for t, n_ in fl["tagE"].value_counts().items()) if len(fl) else "none"); reg("t1_fail_by_tagC", "; ".join(f"{LABEL[t]}: {n_}" for t, n_ in fl["tagC"].value_counts().items()) if len(fl) else "none")
reg("t1_fail_by_class", "; ".join(f"{CLASS_LABEL[c]}: {n_}" for c, n_ in fl["class"].value_counts().items()) if len(fl) else "none")
inc = T1D[T1D["status"] == "inconsistent"]; reg("t1_inconsistent_pairs", "; ".join(f"{LABEL[x['tagC']]} → {LABEL[x['tagE']]} ({tok_label(x['tok'])}, {x['rule']}, h = {x['h']}, N_cal = {x['N_cal']:,}; ratio {fnum(x['ratio'], 2)} {ci(*x['ratio_ci95'], lambda v: fnum(v, 2))})" for _, x in inc.iterrows()) if len(inc) else "none")
reg("t1_fail_theory_share_range", rng_str(fl["theory_share"], lambda x: fnum(x, 2)) if len(fl) else "n/a"); reg("t1_fail_v_range", rng_str(fl["v"], lambda x: fnum(x, 3)) if len(fl) else "n/a")
# T2
c2 = counts_t2(T2D); reg("t2_rows", c2[0]); reg("t2_material", c2[1]); reg("t2_helps", c2[2]); reg("t2_hurts", c2[3]); reg("t2_resolved", c2[4]); reg("t2_agree", c2[5]); reg("t2_disagree", c2[6]); reg("t2_unresolved", c2[7])
reg("t2_share", pct(T2S["share"]) if T2S["share"] is not None else "n/a"); reg("t2_pass_share", pct(P["T2_pass_share"], 0)); reg("t2_verdict", "PASS" if T2S["pass"] else "FAIL"); reg("t2_immaterial", int((~T2D["material"]).sum()))
for c in CLASS_ORDER:
    cc = counts_t2(T2D[T2D["class"] == c]); reg(f"t2_{c}_material", cc[1]); reg(f"t2_{c}_helps", cc[2]); reg(f"t2_{c}_hurts", cc[3]); reg(f"t2_{c}_agree", cc[5]); reg(f"t2_{c}_disagree", cc[6]); reg(f"t2_{c}_unresolved", cc[7])
for r in RULES:
    cc = counts_t2(T2D[T2D["rule"] == r]); reg(f"t2_{r}_material", cc[1]); reg(f"t2_{r}_helps", cc[2]); reg(f"t2_{r}_hurts", cc[3]); reg(f"t2_{r}_agree", cc[5]); reg(f"t2_{r}_disagree", cc[6]); reg(f"t2_{r}_unresolved", cc[7])
for nc in P["N_cal"]:
    cc = counts_t2(T2D[T2D["N_cal"] == nc]); reg(f"t2_n{nc}_material", cc[1]); reg(f"t2_n{nc}_helps", cc[2]); reg(f"t2_n{nc}_hurts", cc[3]); reg(f"t2_n{nc}_agree", cc[5])
for h in P["h"]:
    cc = counts_t2(T2D[T2D["h"] == h]); reg(f"t2_h{h}_material", cc[1]); reg(f"t2_h{h}_agree", cc[5]); reg(f"t2_h{h}_disagree", cc[6]); reg(f"t2_h{h}_unresolved", cc[7])
mt = T2D[T2D["material"]]
for s_ in ("helps", "hurts"):
    ss = mt[mt["predicted_side"] == s_]; reg(f"t2_{s_}_Rpred_median", fnum(float(ss["R_pred"].median()), 2) if len(ss) else "n/a"); reg(f"t2_{s_}_Rpred_range", rng_str(ss["R_pred"], lambda x: fnum(x, 2)) if len(ss) else "n/a"); reg(f"t2_{s_}_Robs_median", fnum(float(ss["R_obs"].median()), 2) if len(ss) else "n/a"); reg(f"t2_{s_}_Robs_range", rng_str(ss["R_obs"], lambda x: fnum(x, 2)) if len(ss) else "n/a")
    reg(f"t2_{s_}_Robs_below1_n", int((ss["R_obs"] < 1).sum())); reg(f"t2_{s_}_Robs_above1_n", int((ss["R_obs"] > 1).sum()))
nr = mt[mt["status"].isin(["disagree", "unresolved"])]
reg("t2_fail_pairs", "; ".join(f"{LABEL[x['tagC']]} → {LABEL[x['tagE']]} ({tok_label(x['tok'])}, {x['rule']}, h = {x['h']}, N_cal = {x['N_cal']:,}; predicted {x['predicted_side']}, R_pred {fnum(x['R_pred'], 2)}, R_obs {fnum(x['R_obs'], 2)} {ci(*x['R_obs_ci95'], lambda v: fnum(v, 2))}; nominal SD obs/pred {fnum(x['sd_nominal_obs'] / x['sd_nominal_pred'], 2)}, conformal SD obs/pred {fnum(x['sd_obs'] / x['sd_pred'], 2)}; {x['status']})" for _, x in nr.iterrows()) if len(nr) else "none")
un_ = T2D[T2D["status"] == "unresolved"]; cr_ = (un_["sd_obs"] / un_["sd_pred"]) if len(un_) else pd.Series([], dtype=float); nr_ = (un_["sd_nominal_obs"] / un_["sd_nominal_pred"]) if len(un_) else pd.Series([], dtype=float)
reg("t2_unresolved_conformal_above_n", int((cr_ > 1).sum())); reg("t2_unresolved_conformal_below_n", int((cr_ < 1).sum())); reg("t2_unresolved_nominal_above_n", int((nr_ > 1).sum()))
reg("diag_n5000_floor_share_range", rng_str((1 - T1D[(T1D["class"] == "diagonal") & (T1D["N_cal"] == 5000)]["theory_share"]), pct))
reg("t2_Robs_above_Rpred_n", int((T2D["R_obs"] > T2D["R_pred"]).sum())); reg("t2_Robs_above_Rpred_material_n", int(((T2D["R_obs"] > T2D["R_pred"]) & T2D["material"]).sum())); reg("t1_consistent_theory_share_min", fnum(float(T1D[T1D["status"] == "consistent"]["theory_share"].min()), 3))
im = T2D[~T2D["material"]]; reg("t2_immaterial_Robs_range", rng_str(im["R_obs"], lambda x: fnum(x, 2)) if len(im) else "n/a"); reg("t2_immaterial_Robs_median", fnum(float(im["R_obs"].median()), 2) if len(im) else "n/a")
reg("t2_immaterial_excl1_n", int(((im["R_obs_ci95"].str[1] < 1) | (im["R_obs_ci95"].str[0] > 1)).sum())); reg("t2_immaterial_below1_n", int((im["R_obs_ci95"].str[1] < 1).sum())); reg("t2_immaterial_above1_n", int((im["R_obs_ci95"].str[0] > 1).sum()))
# REP
reg("rep_checks", REPS["n_checks"]); reg("rep_gross", REPS["n_gross"]); reg("rep_verdict", "PASS" if REPS["pass"] else "FAIL"); reg("rep_max_z", fnum(float(REPD["z"].max()), 2)); reg("rep_median_z", fnum(float(REPD["z"].median()), 2)); reg("rep_sd3_range", rng_str(REPD["sd_s3"], lambda x: pp(x, 2))); reg("rep_sd2_range", rng_str(REPD["sd_s2"], lambda x: pp(x, 2)))
reg("rep_abs_diff_max", pp(float((REPD["sd_s3"] - REPD["sd_s2"]).abs().max()), 3)); reg("rep_rel_diff_max", pct(float(((REPD["sd_s3"] - REPD["sd_s2"]).abs() / REPD["sd_s2"]).max()), 1)); reg("rep_gross_rows", "; ".join(f"{tok_label(x['tok'])} {LABEL[x['tag']]} h = {x['h']} {x['rule']} ({fnum(x['z'], 2)})" for x in REP_OWN if x["gross"]) or "none")
# the secondary blocks
for k_, v in SEC.items():
    for f_ in ("candidate", "eligible", "resolved", "consistent", "inconsistent", "unresolved"):
        reg(f"sec_{k_}_{f_}", v[f_])
    reg(f"sec_{k_}_share", pct(v["share"]) if v["share"] is not None else "n/a"); reg(f"sec_{k_}_ratio_median", fnum(v["ratio_median_resolved"], 3) if v["ratio_median_resolved"] is not None else "n/a"); reg(f"sec_{k_}_ratio_median_eligible", fnum(v["ratio_median_eligible"], 3) if v["ratio_median_eligible"] is not None else "n/a")
    reg(f"sec_{k_}_ratio_range", f"{fnum(v['ratio_min'], 2)}–{fnum(v['ratio_max'], 2)}" if v["ratio_min"] is not None else "n/a")
# the diagonal against the reference law
for m in grid["methods_per_key"]:
    for nc in P["N_cal"]:
        for h in P["h"]:
            for r in RULES:
                s = DIAG[(DIAG["family"] == P["family"]) & (DIAG["method"] == m) & (DIAG["N_cal"] == nc) & (DIAG["h"] == h) & (DIAG["rule"] == r)]; pre = f"diag_{m}{nc}_h{h}_{r}"
                reg(f"{pre}_ratio_median", fnum(float(s["ratio"].median()), 2)); reg(f"{pre}_ratio_range", rng_str(s["ratio"], lambda x: fnum(x, 2))); reg(f"{pre}_sd_obs_range", rng_str(s["sd"], lambda x: pp(x, 2))); reg(f"{pre}_sd_pred_range", rng_str(s["pred_sd"], lambda x: pp(x, 2)))
                reg(f"{pre}_beta_sd", pp(float(s["beta_sd"].iloc[0]), 3)); reg(f"{pre}_floor_range", rng_str(s["floor_sd"], lambda x: pp(x, 3))); reg(f"{pre}_keymean_range", rng_str(s["key_mean"], lambda x: pct(x, 2))); reg(f"{pre}_beta_mean", pct(float(s["beta_mean"].iloc[0]), 2))
                reg(f"{pre}_share_obs_range", rng_str(s["share_above_alpha"], pct)); reg(f"{pre}_share_pred_range", rng_str(s["pred_share_above_alpha_finite"], pct)); reg(f"{pre}_beta_share", pct(float(s["beta_share_above_alpha"].iloc[0]))); reg(f"{pre}_theory_share_range", rng_str(s["pred_theory_share"], lambda x: fnum(x, 2))); reg(f"{pre}_q99_range", rng_str(s["q0.99"], lambda x: pct(x, 2)))
# the remedies on the diagonal and by class (KGW, alpha = 0.01)
for h in HS:
    for r in RULES:
        for v in REM_VARIANTS:
            base = (DF["family"] == P["family"]) & (DF["alpha"] == A_PRIMARY) & (DF["rule"] == r) & (DF["h"] == h) & (DF["variant"] == v)
            s = DF[base & (DF["class"] == ("fixed" if v in ("nominal", "multiplier20") else "diagonal"))]; pre = f"rem_h{h}_{r}_{v.replace('@', '')}"
            reg(f"{pre}_keymean_range", rng_str(s["key_mean"], lambda x: pct(x, 2))); reg(f"{pre}_sd_range", rng_str(s["sd"], lambda x: pp(x, 2))); reg(f"{pre}_q99_range", rng_str(s["q0.99"], lambda x: pct(x, 2))); reg(f"{pre}_median_range", rng_str(s["q0.5"], lambda x: pct(x, 2))); reg(f"{pre}_worst_range", rng_str(s["max"], lambda x: pct(x, 2)))
            reg(f"{pre}_share_alpha_range", rng_str(s["share_above_alpha"], pct)); reg(f"{pre}_share2_range", rng_str(s["share_above_2alpha"], pct)); reg(f"{pre}_share5_range", rng_str(s["share_above_5alpha"], pct)); reg(f"{pre}_nzero_range", rng_str(s["n_zero"], fnum)); reg(f"{pre}_screen_n", int(s["screen_exceeds"].sum())); reg(f"{pre}_n", len(s))
            reg(f"{pre}_ratio_median", fnum(float(s["ratio"].median()), 2) if s["ratio"].notna().any() else "n/a"); reg(f"{pre}_ratio_range", rng_str(s["ratio"], lambda x: fnum(x, 2))); reg(f"{pre}_pred_share_finite_median", pct(float(s["pred_share_above_alpha_finite"].median()))); reg(f"{pre}_share_alpha_median", pct(float(s["share_above_alpha"].median()))); reg(f"{pre}_pred_sd_range", rng_str(s["pred_sd"], lambda x: pp(x, 2)))
            reg(f"{pre}_keymean_median", pct(float(s["key_mean"].median()), 2)); reg(f"{pre}_q99_median", pct(float(s["q0.99"].median()), 2)); reg(f"{pre}_sd_median", pp(float(s["sd"].median()), 2))
            reg(f"{pre}_units_share_above_beta", int((s["share_above_alpha"] > BETA).sum())); reg(f"{pre}_units_any_above_alpha", int((s["share_above_alpha"] > 0).sum())); reg(f"{pre}_share_alpha_max", pct(float(s["share_above_alpha"].max())))
        for c in CLASS_ORDER[1:]:
            for v in ("conformal@1000", "conformal@5000", "tolerance@5000", "empirical", "pooled"):
                s = DF[(DF["family"] == P["family"]) & (DF["alpha"] == A_PRIMARY) & (DF["rule"] == r) & (DF["h"] == h) & (DF["variant"] == v) & (DF["class"] == c)]; pre = f"cls_{c}_{v.replace('@', '')}_h{h}_{r}"
                reg(f"{pre}_n", len(s)); reg(f"{pre}_sd_range", rng_str(s["sd"], lambda x: pp(x, 2))); reg(f"{pre}_sd_median", pp(float(s["sd"].median()), 2)); reg(f"{pre}_ratio_median", fnum(float(s["ratio"].median()), 2) if s["ratio"].notna().any() else "n/a"); reg(f"{pre}_ratio_range", rng_str(s["ratio"], lambda x: fnum(x, 2)))
                reg(f"{pre}_share_alpha_range", rng_str(s["share_above_alpha"], pct)); reg(f"{pre}_share_alpha_median", pct(float(s["share_above_alpha"].median()))); reg(f"{pre}_pred_share_median", pct(float(s["pred_share_above_alpha_finite"].median()))); reg(f"{pre}_keymean_range", rng_str(s["key_mean"], lambda x: pct(x, 2))); reg(f"{pre}_q99_range", rng_str(s["q0.99"], lambda x: pct(x, 2)))
                reg(f"{pre}_q99_median", pct(float(s["q0.99"].median()), 2)); reg(f"{pre}_screen_n", int(s["screen_exceeds"].sum())); reg(f"{pre}_share2_median", pct(float(s["share_above_2alpha"].median())))
# the null-side cost (KGW, alpha = 0.01)
for h in HS:
    for r in RULES:
        for v in ["empirical", "pooled"] + [f"{m}@{n}" for m in grid["methods_per_key"] for n in NCALS]:
            s = ZC[(ZC["family"] == P["family"]) & (ZC["rule"] == r) & (ZC["h"] == h) & (ZC["variant"] == v) & (ZC["alpha"] == A_PRIMARY)]; pre = f"zc_h{h}_{r}_{v.replace('@', '')}"
            reg(f"{pre}_cost_q50_median", fnum(float(s["cost_q50"].median()), 2) if s["cost_q50"].notna().any() else "all abstain"); reg(f"{pre}_cost_q50_range", rng_str(s["cost_q50"], lambda x: fnum(x, 2)) if s["cost_q50"].notna().any() else "n/a")
            reg(f"{pre}_cost_q05_median", fnum(float(s["cost_q05"].median()), 2) if s["cost_q05"].notna().any() else "n/a"); reg(f"{pre}_cost_q95_median", fnum(float(s["cost_q95"].median()), 2) if s["cost_q95"].notna().any() else "n/a"); reg(f"{pre}_abstain", int(s["n_abstain"].sum()))
            if v == "empirical":
                reg(f"{pre}_kappa_median", fnum(float(s["kappa"].median()), 2)); reg(f"{pre}_kappa_range", rng_str(s["kappa"], lambda x: fnum(x, 2)))
reg("zc_abstain_alpha0.001", int(ZC[(ZC["alpha"] == 0.001) & (ZC["method"].isin(grid["methods_per_key"]))]["n_abstain"].sum()))
zpk = ZC[ZC["method"].isin(grid["methods_per_key"])]; reg("zc_abstain_alpha0.001_structural", int(zpk[(zpk["alpha"] == 0.001) & (zpk["j"] == 0)]["n_abstain"].sum())); reg("zc_structural_settings_n", int(((zpk["alpha"] == 0.001) & (zpk["j"] == 0)).sum()))
zpos = zpk[(zpk["j"] > 0) & (zpk["n_abstain"] > 0)]; reg("zc_zero_positive_j_n", int(zpos["n_abstain"].sum())); reg("zc_zero_positive_j_rows", len(zpos))
reg("zc_zero_positive_j_settings", "; ".join(f"{tok_label(x['tok'])} {LABEL[x['tag']]} h = {x['h']} {x['family']} {x['rule']} {x['variant']} α = {x['alpha']} (j = {int(x['j'])}): {int(x['n_abstain'])}" for _, x in zpos.iterrows()) if len(zpos) else "none")
reg("zc_zero_positive_j_alphas", ", ".join(str(a_) for a_ in sorted(zpos["alpha"].unique())) if len(zpos) else "none"); reg("zc_abstain_alpha0.01", int(ZC[(ZC["alpha"] == 0.01) & (ZC["method"].isin(grid["methods_per_key"]))]["n_abstain"].sum())); reg("zc_abstain_alpha0.05", int(ZC[(ZC["alpha"] == 0.05) & (ZC["method"].isin(grid["methods_per_key"]))]["n_abstain"].sum()))
# the break-even (KGW), the calibration-set component, the crossed block, the cross-tokenizer transfer and the near-identical pair
for h in HS:
    for r in RULES:
        for m in grid["methods_per_key"]:
            s = BE[(BE["family"] == P["family"]) & (BE["rule"] == r) & (BE["h"] == h) & (BE["method"] == m)]; pre = f"be_h{h}_{r}_{m}"
            for nc in NCALS:
                reg(f"{pre}_n{nc}", int((s["break_even"] == nc).sum()))
            reg(f"{pre}_never", int(s["break_even"].isna().sum())); reg(f"{pre}_R5000_median", fnum(float(s["R5000"].median()), 2))
            fl_ = [1 - pred_of(h, r, None, None, x["tok"], x["tag"], "nominal", A_PRIMARY)["theory_share"] for _, x in s.iterrows()]; nv_ = [1 - pred_of(h, r, None, None, x["tok"], x["tag"], "nominal", A_PRIMARY)["theory_share"] for _, x in s[s["break_even"].isna()].iterrows()]
            reg(f"{pre}_floor_share_median_all", pct(float(np.median(fl_)))); reg(f"{pre}_never_floor_share_range", rng_str(nv_, pct) if nv_ else "n/a"); reg(f"{pre}_never_floor_majority_n", int(sum(v_ > 0.5 for v_ in nv_)))
            be_ = s["break_even"].dropna().astype(int); reg(f"{pre}_breakeven_range", (f"{int(be_.min()):,}" if be_.min() == be_.max() else f"{int(be_.min()):,}–{int(be_.max()):,}") if len(be_) else "never within the grid")
            reg(f"{pre}_R5000_median_dup", fnum(float(s["R5000"].median()), 2)); reg(f"{pre}_R5000_range", rng_str(s["R5000"], lambda x: fnum(x, 2))); reg(f"{pre}_R1000_median", fnum(float(s["R1000"].median()), 2)); reg(f"{pre}_R500_median", fnum(float(s["R500"].median()), 2)); reg(f"{pre}_Rpred5000_median", fnum(float(s["Rpred5000"].median()), 2))
        for v in [f"{m}@{n}" for m in grid["methods_per_key"] for n in grid["cal_bootstrap"]["N_cal"]]:
            s = CB[(CB["family"] == P["family"]) & (CB["rule"] == r) & (CB["h"] == h) & (CB["variant"] == v) & (CB["class"] == "diagonal")]; pre = f"cb_h{h}_{r}_{v.replace('@', '')}"
            reg(f"{pre}_sd_of_sd_median", pp(float(s["sd_over_cal_sd"].median()), 3)); reg(f"{pre}_rel_median", pct(float((s["sd_over_cal_sd"] / s["mean_over_cal_sd"]).median()))); reg(f"{pre}_sd_of_keymean_median", pp(float(s["sd_over_cal_key_mean"].median()), 3)); reg(f"{pre}_sd_of_share_median", pct(float(s["sd_over_cal_share_above_alpha"].median()), 2)); reg(f"{pre}_sd_of_q99_median", pp(float(s["sd_over_cal_q99"].median()), 3))
        for v in REM_VARIANTS:
            s = CR[(CR["family"] == P["family"]) & (CR["rule"] == r) & (CR["h"] == h) & (CR["variant"] == v)]; pre = f"cr_h{h}_{r}_{v.replace('@', '')}"
            reg(f"{pre}_q99_lo_range", rng_str(s["q0.99_lo"], lambda x: pct(x, 2))); reg(f"{pre}_q99_hi_range", rng_str(s["q0.99_hi"], lambda x: pct(x, 2))); reg(f"{pre}_max_hi_range", rng_str(s["max_hi"], lambda x: pct(x, 2))); reg(f"{pre}_share2_hi_range", rng_str(s["share2_hi"], pct)); reg(f"{pre}_q50_lo_range", rng_str(s["q0.5_lo"], lambda x: pct(x, 2))); reg(f"{pre}_q50_hi_range", rng_str(s["q0.5_hi"], lambda x: pct(x, 2)))
        for v in VX:
            s = DF[(DF["family"] == P["family"]) & (DF["rule"] == r) & (DF["h"] == h) & (DF["variant"] == v) & (DF["class"] == "cross_tokenizer")]; el_ = s[s["eligible"]]; pre = f"ct_h{h}_{r}_{v.replace('@', '')}"
            reg(f"{pre}_n", len(s)); reg(f"{pre}_eligible", len(el_)); reg(f"{pre}_ratio_median", fnum(float(el_["ratio"].median()), 2) if len(el_) else "n/a"); reg(f"{pre}_ratio_range", rng_str(el_["ratio"], lambda x: fnum(x, 2)) if len(el_) else "n/a"); reg(f"{pre}_sd_median", pp(float(s["sd"].median()), 2)); reg(f"{pre}_pred_sd_median", pp(float(s["pred_sd"].median()), 2))
            reg(f"{pre}_keymean_median", pct(float(s["key_mean"].median()), 2)); reg(f"{pre}_share_obs_median", pct(float(s["share_above_alpha"].median()))); reg(f"{pre}_share_pred_median", pct(float(s["pred_share_above_alpha_finite"].median()))); reg(f"{pre}_q99_median", pct(float(s["q0.99"].median()), 2))
ni = T1D[T1D["class"] == "near_identical"]; reg("ni_n", len(ni)); reg("ni_eligible", int(ni["eligible"].sum())); reg("ni_consistent", int((ni["status"] == "consistent").sum())); reg("ni_ratio_range", rng_str(ni["ratio_point"], lambda x: fnum(x, 2))); reg("ni_ratio_median", fnum(float(ni["ratio_point"].median()), 2)); reg("ni_v_range", rng_str(ni["v"], lambda x: fnum(x, 3)))
dg = T1D[T1D["class"] == "diagonal"]; reg("diag_n1000_ratio_range", rng_str(dg[dg["N_cal"] == 1000]["ratio_point"], lambda x: fnum(x, 2))); reg("diag_n5000_ratio_range", rng_str(dg[dg["N_cal"] == 5000]["ratio_point"], lambda x: fnum(x, 2))); reg("diag_n5000_ratio_median", fnum(float(dg[dg["N_cal"] == 5000]["ratio_point"].median()), 2)); reg("diag_n5000_theory_share_range", rng_str(dg[dg["N_cal"] == 5000]["theory_share"], lambda x: fnum(x, 2)))
reg("v_negative_n", int((T1D["v_raw"] < 0).sum())); reg("v_flagged_n", int(T1D["flags"].apply(len).gt(0).sum())); reg("rho_corr_range", rng_str(T1D["rho_CE"] / np.sqrt(T1D["rho_C"] * T1D["rho_E"]), lambda x: fnum(x, 2)))
for c in CLASS_ORDER:
    s = T1D[T1D["class"] == c]; reg(f"corr_{c}_range", rng_str(s["rho_CE"] / np.sqrt(s["rho_C"] * s["rho_E"]), lambda x: fnum(x, 2))); reg(f"corr_{c}_median", fnum(float((s["rho_CE"] / np.sqrt(s["rho_C"] * s["rho_E"])).median()), 2)); reg(f"v_{c}_range", rng_str(s["v"], lambda x: fnum(x, 3))); reg(f"v_{c}_median", fnum(float(s["v"].median()), 3))
VAL = json.loads((ROOT / OUT / "VALIDATION.json").read_text())
reg("val_peak_rss", fnum(VAL["cost"]["peak_rss_gb"], 2)); reg("val_discrete_conformal_mean", fnum(VAL["fixtures"]["b"]["discrete_conformal"]["mean_level"], 4)); reg("val_discrete_conformal_bound", fnum(VAL["fixtures"]["b"]["discrete_conformal"]["bound"], 4))
reg("t1_fail_n_tagE", int(fl["tagE"].nunique()) if len(fl) else 0); reg("t1_fail_tagE_ranges", "; ".join(f"{LABEL[t]}: {rng_str(fl[fl['tagE'] == t]['ratio'], lambda x: fnum(x, 2))}" for t in fl["tagE"].value_counts().index) if len(fl) else "none")
reg("n_unit_fr_blocks", sum(1 for u in UNITS if u["kind"] == "eval") * len(FAMILIES) * len(RULES))
for c in ("within_english", "english_other", "other_other"):
    sc_ = DF[(DF["family"] == P["family"]) & (DF["alpha"] == A_PRIMARY) & (DF["rule"] == "distinct") & (DF["h"] == 1) & (DF["variant"] == "conformal@5000")]
    reg(f"transfer_factor_{c}", fnum(float(sc_[sc_["class"] == c]["sd"].median() / sc_[sc_["class"] == "diagonal"]["sd"].median()), 1))
print(f"values registered: {len(VALUES)} ({time.time() - t0:.0f}s)", flush=True)

# ------------------------------------------------------------------ the rules table
T["rules"] = md_table(["Rule", "Pre-registered statement (protocol §9)", "Observed", "Verdict"], [
    ["T1 (adequacy of the calibrated-threshold predictor)", f"Over the eligible primary rows (KGW; raw and distinct; h ∈ {{1, 2}}; both tokenizers; every ordered pair within a tokenizer; per-key conformal; N_cal 1,000 and 5,000; α = 0.01; eligible when the theory share ≥ {P['min_theory_share']} and no flag), the ratio SD_obs/SD_pred with its key-bootstrap 95% interval: consistent inside [2/3, 3/2]; pass iff ≥ {P['min_resolved']} resolved and ≥ {pct(P['T1_pass_share'], 0)} of the resolved consistent",
     f"{T1S['n_eligible']:,} eligible of {T1S['n_rows']:,}; {T1S['n_resolved']:,} resolved; {T1S['n_consistent']:,} consistent ({pct(T1S['share'])}); {T1S['n_resolved'] - T1S['n_consistent']:,} inconsistent; {T1S['n_unresolved']:,} unresolved", "PASS" if T1S["pass"] else "FAIL"],
    ["T2 (the sign of calibration's effect on the dispersion)", f"Over the same block, the material pairs (R_pred outside [2/3, 3/2]): R_obs = SD(conformal)/SD(nominal) with its paired key-bootstrap 95% interval: agree when the interval excludes 1 on the predicted side; pass iff ≥ {P['min_resolved']} resolved and ≥ {pct(P['T2_pass_share'], 0)} agree",
     f"{T2S['n_eligible']:,} material of {T2S['n_rows']:,} (predicted helps {VALUES['t2_helps']}, hurts {VALUES['t2_hurts']}); {T2S['n_resolved']:,} resolved; {T2S['n_agree']:,} agree ({pct(T2S['share'])}); {T2S['n_resolved'] - T2S['n_agree']:,} disagree; {T2S['n_unresolved']:,} unresolved", "PASS" if T2S["pass"] else "FAIL"],
    ["REP (integrity: Study 2's nominal dispersion reproduced with independent keys)", "For every (tokenizer, evaluation cell except Gutenberg, h, rule) of the KGW family at α = 0.01, |SD₃ − SD₂| ≤ 6·√(se₃² + se₂²) + 10⁻¹²; pass iff no gross failure",
     f"{REPS['n_checks']} checks; {REPS['n_gross']} gross failure{'s' if REPS['n_gross'] != 1 else ''}; the largest |difference|/threshold {VALUES['rep_max_z']}", "PASS" if REPS["pass"] else "FAIL"]])

# ------------------------------------------------------------------ figures
FIG_REL = "" if FIXTURE else "../outputs/study3_v0.1/report/"


def save(fig, name):
    for ext in ("png", "svg"):
        fig.savefig(OUTDIR / f"{name}.{ext}", dpi=200 if ext == "png" else None, bbox_inches="tight", metadata={"Date": None} if ext == "svg" else None)   # no creation date: byte-reproducible
    plt.close(fig)


def logfmt(ax, axis="y", subs=(1.0, 2.0, 5.0)):
    from matplotlib.ticker import FuncFormatter, NullFormatter, LogLocator
    for a_ in ((ax.xaxis, ax.yaxis) if axis == "both" else ((ax.yaxis,) if axis == "y" else (ax.xaxis,))):
        a_.set_major_locator(LogLocator(base=10, subs=subs, numticks=15)); a_.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        a_.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10), numticks=15)); a_.set_minor_formatter(NullFormatter())


from matplotlib.lines import Line2D   # noqa: E402
CLASS_HANDLES = [Line2D([], [], marker=MK_CLASS[c], color=COL_GROUP[GROUP_OF[c]], linestyle="", markersize=5, label=CLASS_LABEL[c]) for c in CLASS_ORDER]
fx = "FIXTURE RENDER — planted numbers; not an outcome. " if FIXTURE else ""
# Fig 1: adequacy of the calibrated-threshold predictor (T1), the ratio against the shift correlation, and REP
el1 = T1D[T1D["eligible"]].copy(); el1["r"] = el1["rho_CE"] / np.sqrt(el1["rho_C"] * el1["rho_E"])
fig, axes = plt.subplots(2, 2, figsize=(10.5, 8.2))
for ax, r in zip(axes[0], RULES):
    s = el1[el1["rule"] == r]
    for c in CLASS_ORDER:
        sc_ = s[s["class"] == c]
        ax.scatter(100 * sc_["sd_pred"], 100 * sc_["sd_obs"], s=14, marker=MK_CLASS[c], c=COL_GROUP[GROUP_OF[c]], alpha=0.75, linewidths=0.4, edgecolors=SURFACE, label=CLASS_LABEL[c])
    lo, hi = 100 * min(s["sd_pred"].min(), s["sd_obs"].min()) * 0.8, 100 * max(s["sd_pred"].max(), s["sd_obs"].max()) * 1.25; xx = np.array([lo, hi])
    ax.plot(xx, xx, color=INK, lw=0.9); ax.plot(xx, BAND[0] * xx, color=MUTED, lw=0.8); ax.plot(xx, BAND[1] * xx, color=MUTED, lw=0.8)
    ax.set_xscale("log"); ax.set_yscale("log"); logfmt(ax, "both"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_xlabel("predicted across-key SD of the level (pp)"); ax.set_ylabel("observed across-key SD (pp)")
    ax.set_title(f"({'ab'[RULES.index(r)]}) T1 rows, {r} rule: {len(s):,} eligible pairs; lines y = x, 2x/3, 3x/2", loc="left", fontsize=9)
axes[0][0].legend(handles=CLASS_HANDLES, fontsize=7.5, loc="upper left", title="pair class", title_fontsize=7.5)
ax = axes[1][0]
for c in CLASS_ORDER:
    for r, filled in zip(RULES, (True, False)):
        sc_ = el1[(el1["class"] == c) & (el1["rule"] == r)]
        ax.scatter(sc_["r"], sc_["ratio_point"], s=14, marker=MK_CLASS[c], c=COL_GROUP[GROUP_OF[c]] if filled else "none", edgecolors=COL_GROUP[GROUP_OF[c]], linewidths=0.7, alpha=0.8)
ax.axhline(1.0, color=INK, lw=0.9); ax.axhline(BAND[0], color=MUTED, lw=0.8); ax.axhline(BAND[1], color=MUTED, lw=0.8); ax.set_xlabel("shift correlation of the pair, ρ_CE / √(ρ̄_C ρ̄_E) (key-free)"); ax.set_ylabel("observed / predicted SD")
ax.set_title("(c) the ratio against the pair's shift correlation (filled: raw; hollow: distinct)", loc="left", fontsize=9)
ax = axes[1][1]
for r in RULES:
    for t in TOKS:
        s = REPD[(REPD["rule"] == r) & (REPD["tok"] == t)]; ax.scatter(100 * s["sd_s2"], 100 * s["sd_s3"], s=18, marker=MK_TOK[t], c=COL_RULE[r], alpha=0.8, linewidths=0.4, edgecolors=SURFACE, label=f"{r}, {tok_label(t)}")
xx = np.array([100 * REPD[["sd_s2", "sd_s3"]].min().min() * 0.8, 100 * REPD[["sd_s2", "sd_s3"]].max().max() * 1.25]); ax.plot(xx, xx, color=INK, lw=0.9); ax.set_xscale("log"); ax.set_yscale("log"); logfmt(ax, "both")
ax.set_xlabel("Study 2's across-key SD of the nominal level, its keys (pp)"); ax.set_ylabel("Study 3's keys (pp)"); ax.set_title(f"(d) REP: {len(REPD)} checks, {int(REPD['gross'].sum())} gross failure{'s' if int(REPD['gross'].sum()) != 1 else ''}", loc="left", fontsize=9); ax.legend(fontsize=7.5, loc="upper left")
fig.suptitle(f"{fx}Study 3, T1 and REP (KGW, α = 0.01; K = {K:,} keys; N_E = {grid['N_eval']:,}, Gutenberg {grid['N_eval_gutenberg']:,})", fontsize=10, x=0.01, ha="left"); fig.tight_layout(); save(fig, "fig1_adequacy")
T["FIG_fig1_adequacy"] = f"![T1 adequacy, the ratio against the shift correlation, and REP]({FIG_REL}fig1_adequacy.png)\n\n**Figure 1.** T1 and REP. (a, b) The observed against the predicted across-key SD of the realised level for the {len(el1):,} eligible primary rows (per-key conformal; N_cal 1,000 and 5,000; α = 0.01), by pair class; (c) the point ratio against the pair's key-free shift correlation; (d) REP's {len(REPD)} nominal-rule checks against Study 2's record. Every value is in Tables 1–5 and the supplements."
# Fig 2: the deployer's view by method on the diagonal (KGW h = 1, alpha = 0.01): the median key and the 99% key per unit
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), sharey=True)
for ax, r in zip(axes, RULES):
    for i, v in enumerate(REM_VARIANTS):
        base = (DF["family"] == P["family"]) & (DF["alpha"] == A_PRIMARY) & (DF["rule"] == r) & (DF["h"] == 1) & (DF["variant"] == v); s = DF[base & (DF["class"] == ("fixed" if v in ("nominal", "multiplier20") else "diagonal"))]
        for _, x in s.iterrows():
            jit = i + (0.18 if x["tokE"] == "qwen" else -0.18) + 0.03 * np.random.default_rng(int(hashlib.sha256(x["tagE"].encode()).hexdigest()[:8], 16)).uniform(-1, 1)   # a stable seed: the build is byte-reproducible
            ax.plot([jit, jit], [100 * max(x["q0.5"], 1e-4), 100 * max(x["q0.99"], 1e-4)], color=GRIDC, lw=0.9, zorder=1)
            ax.scatter([jit], [100 * max(x["q0.5"], 1e-4)], s=12, marker=MK_TOK[x["tokE"]], c=COL_GROUP["same"], zorder=3, linewidths=0.3, edgecolors=SURFACE)
            ax.scatter([jit], [100 * max(x["q0.99"], 1e-4)], s=12, marker=MK_TOK[x["tokE"]], c=COL_GROUP["english"], zorder=3, linewidths=0.3, edgecolors=SURFACE)
        ax.plot([i - 0.32, i + 0.32], [100 * max(float(s["q0.99"].median()), 1e-4)] * 2, color=INK, lw=1.4, zorder=4)
    ax.axhline(100 * A_PRIMARY, color=MUTED, lw=0.8); ax.text(-0.45, 100 * A_PRIMARY, "α = 1%", color=MUTED, fontsize=7, va="bottom", ha="left")
    ax.set_yscale("log"); logfmt(ax); ax.set_xticks(range(len(REM_VARIANTS))); ax.set_xticklabels([{"multiplier20": "multi-\nplier20"}.get(v, v.replace("@", "\n@")) for v in REM_VARIANTS], fontsize=7.5); ax.set_xlim(-0.6, len(REM_VARIANTS) - 0.4); ax.set_title(f"({'ab'[RULES.index(r)]}) {r} rule, h = 1", loc="left", fontsize=9)
    ax.set_ylabel("per-key false-positive level (%)" if r == RULES[0] else "")
axes[0].legend(handles=[Line2D([], [], marker="o", color=COL_GROUP["same"], linestyle="", markersize=5, label="median key"), Line2D([], [], marker="o", color=COL_GROUP["english"], linestyle="", markersize=5, label="99% key"), Line2D([], [], color=INK, lw=1.4, label="median of the 99% key over the 20 units"),
                        Line2D([], [], marker="o", color=MUTED, linestyle="", markersize=5, label="Llama-3.2"), Line2D([], [], marker="^", color=MUTED, linestyle="", markersize=5, label="Qwen2.5")], fontsize=7.5, loc="lower left")
fig.suptitle(f"{fx}Study 3, the deployer's view by method on the diagonal (KGW, α = 0.01, h = 1; 20 (tokenizer, cell) units; K = {K:,} keys per unit)", fontsize=10, x=0.01, ha="left"); fig.tight_layout(); save(fig, "fig2_remedies")
T["FIG_fig2_remedies"] = f"![the deployer's view by method on the diagonal]({FIG_REL}fig2_remedies.png)\n\n**Figure 2.** The deployer's view by method when the calibration law is the deployment law (the diagonal): per unit, the median key and the 99% key of the realised level at α = 0.01, h = 1, under the raw (a) and distinct (b) rules; the per-key methods at N_cal 1,000 and 5,000. Every value is in Table 8 and `tables_pairs_kgw_alpha0.01_full.md`."
# Fig 3: transfer heat maps (Llama-3.2, KGW distinct h = 1, conformal@5000, alpha = 0.01)
HM_TOK, HM_RULE, HM_H, HM_V = "llama", "distinct", 1, "conformal@5000"
sub = DF[(DF["family"] == P["family"]) & (DF["alpha"] == A_PRIMARY) & (DF["rule"] == HM_RULE) & (DF["h"] == HM_H) & (DF["variant"] == HM_V) & (DF["tokC"] == HM_TOK) & (DF["tokE"] == HM_TOK)]
M_obs = np.full((len(TAGS), len(TAGS)), np.nan); M_pred = M_obs.copy(); M_share = M_obs.copy()
for _, x in sub.iterrows():
    i, j = TAGS.index(x["tagC"]), TAGS.index(x["tagE"]); M_obs[i, j] = 100 * x["sd"]; M_pred[i, j] = 100 * x["pred_sd"]; M_share[i, j] = x["share_above_alpha"]
SEQMAP = LinearSegmentedColormap.from_list("seq", SEQ)
fig, axes = plt.subplots(2, 2, figsize=(10.5, 9.4)); short = [LABEL[t].replace("wikipedia", "wiki").replace("stackexchange", "stackex").replace("gutenberg", "books") for t in TAGS]
for ax, (M, title, cmap, vmin, vmax) in zip(axes.ravel(), [(M_obs, "(a) observed across-key SD of the level (pp)", SEQMAP, 0, np.nanmax([M_obs, M_pred])), (M_pred, "(b) predicted SD (pp; the key-free predictor)", SEQMAP, 0, np.nanmax([M_obs, M_pred])),
                                                              (np.log2(M_obs / M_pred), "(c) log₂(observed / predicted); the band [2/3, 3/2] is ±0.58", DIVERGING, -1.0, 1.0), (M_share, "(d) observed share of keys with a level above α", SEQMAP, 0, 1)]):
    im = ax.imshow(M, cmap=cmap, vmin=vmin, vmax=vmax, aspect="equal"); ax.set_xticks(range(len(TAGS))); ax.set_xticklabels(short, rotation=60, ha="right", fontsize=7.5); ax.set_yticks(range(len(TAGS))); ax.set_yticklabels(short, fontsize=7.5); ax.grid(False)
    ax.set_xlabel("evaluation cell (the deployment law)"); ax.set_ylabel("calibration cell (the thresholds' law)"); ax.set_title(title, loc="left", fontsize=9); fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
fig.suptitle(f"{fx}Study 3, transfer of a per-key conformal threshold (N_cal = 5,000) across the ten cells: {tok_label(HM_TOK)}, KGW {HM_RULE} rule, h = {HM_H}, α = 0.01 (K = {K:,} keys)", fontsize=10, x=0.01, ha="left"); fig.tight_layout(); save(fig, "fig3_transfer")
T["FIG_fig3_transfer"] = f"![transfer heat maps]({FIG_REL}fig3_transfer.png)\n\n**Figure 3.** Transfer of a per-key conformal threshold set on one cell's 5,000 calibration texts and applied to every cell's evaluation texts ({tok_label(HM_TOK)}, KGW {HM_RULE} rule, h = {HM_H}, α = 0.01): (a) the observed across-key SD, (b) the predicted SD, (c) their ratio on a log₂ scale, (d) the observed share of keys above α. Rows are the calibration cell, columns the evaluation cell; every value is in `tables_pairs_kgw_alpha0.01_full.md` and the other tokenizer, rule and width in the supplements."
# Fig 4: the break-even N_cal on the diagonal (KGW h = 1, conformal)
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), sharey=True)
for ax, r in zip(axes, RULES):
    s = BE[(BE["family"] == P["family"]) & (BE["rule"] == r) & (BE["h"] == 1) & (BE["method"] == "conformal")]
    for _, x in s.iterrows():
        ax.plot(NCALS, [x[f"R{nc}"] for nc in NCALS], color=COL_GROUP["same"], alpha=0.55, lw=1.3, ls=LS_TOK[x["tok"]], marker=MK_TOK[x["tok"]], markersize=3.5)
    from matplotlib.ticker import NullFormatter, NullLocator, FixedLocator, FixedFormatter
    ax.axhline(1.0, color=INK, lw=0.9); ax.set_xscale("log"); ax.xaxis.set_major_locator(FixedLocator(NCALS)); ax.xaxis.set_major_formatter(FixedFormatter([f"{nc:,}" for nc in NCALS])); ax.xaxis.set_minor_locator(NullLocator()); ax.xaxis.set_minor_formatter(NullFormatter()); ax.set_xlabel("N_cal (calibration texts)"); ax.set_title(f"({'ab'[RULES.index(r)]}) {r} rule, h = 1: 20 units", loc="left", fontsize=9)
    ax.set_ylabel("SD(conformal) / SD(nominal), the same keys and texts" if r == RULES[0] else "")
axes[0].legend(handles=[Line2D([], [], color=COL_GROUP["same"], ls=LS_TOK[t], marker=MK_TOK[t], markersize=4, label=tok_label(t)) for t in TOKS], fontsize=7.5, loc="upper right")
fig.suptitle(f"{fx}Study 3, the break-even calibration size on the diagonal (KGW, per-key conformal, α = 0.01, h = 1; K = {K:,} keys; the intervals are in Table 12 and its supplement)", fontsize=10, x=0.01, ha="left"); fig.tight_layout(); save(fig, "fig4_breakeven")
T["FIG_fig4_breakeven"] = f"![break-even]({FIG_REL}fig4_breakeven.png)\n\n**Figure 4.** The observed ratio of the across-key SD under per-key conformal calibration to the nominal test's, against the calibration size, on the diagonal (KGW, α = 0.01, h = 1), one line per (tokenizer, cell) unit; the paired intervals and the break-even N_cal of every unit are in Table 12 and `tables_breakeven_full.md`."
# Fig 5: the null-side cost in z-units (KGW h = 1, alpha = 0.01)
ZV = [f"conformal@{n}" for n in NCALS] + [f"tolerance@{n}" for n in NCALS] + ["empirical", "pooled"]
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True)
for ax, r in zip(axes, RULES):
    for i, v in enumerate(ZV):
        s = ZC[(ZC["family"] == P["family"]) & (ZC["rule"] == r) & (ZC["h"] == 1) & (ZC["variant"] == v) & (ZC["alpha"] == A_PRIMARY)]
        if s["cost_q50"].notna().any():
            if s["cost_q05"].notna().any():
                ax.plot([i, i], [float(s["cost_q05"].median()), float(s["cost_q95"].median())], color=COL_RULE[r], lw=2.2, alpha=0.45, solid_capstyle="round")
            ax.scatter([i], [float(s["cost_q50"].median())], s=26, marker="o" if "@" in v else "s", c=COL_RULE[r], zorder=3, linewidths=0.4, edgecolors=SURFACE)
        else:
            ax.text(i, 0, "abstains", rotation=90, fontsize=7, color=MUTED, ha="center", va="bottom")
    ax.axhline(0.0, color=INK, lw=0.9); ax.set_xticks(range(len(ZV))); ax.set_xticklabels([v.replace("conformal@", "conf.\n@").replace("tolerance@", "tol.\n@") for v in ZV], fontsize=7.5); ax.set_xlim(-0.6, len(ZV) - 0.4); ax.set_title(f"({'ab'[RULES.index(r)]}) {r} rule, h = 1: medians over the 20 calibration units", loc="left", fontsize=9)
    ax.set_ylabel("null-side cost z(t) − z_α (z-units)" if r == RULES[0] else "")
axes[0].legend(handles=[Line2D([], [], marker="o", color=MUTED, linestyle="", markersize=5, label="median key (q50)"), Line2D([], [], color=MUTED, lw=2.2, alpha=0.5, label="5%–95% keys (medians over units)"), Line2D([], [], marker="s", color=MUTED, linestyle="", markersize=5, label="scheme-level threshold")], fontsize=7.5, loc="upper left")
fig.suptitle(f"{fx}Study 3, the null-side cost of each method in z-units (KGW, α = 0.01, h = 1; per-key methods over the keys with a positive threshold; scheme-level over the fitting keys)", fontsize=10, x=0.01, ha="left"); fig.tight_layout(); save(fig, "fig5_zcost")
T["FIG_fig5_zcost"] = f"![null-side cost]({FIG_REL}fig5_zcost.png)\n\n**Figure 5.** The null-side cost z(t) − z_α of each method (KGW, α = 0.01, h = 1): for the per-key methods the across-unit median of the 5, 50 and 95% key quantiles of the cost over the keys with a positive threshold; for the scheme-level methods the fitted threshold's cost. Every value is in Table 11 and `tables_zcost_full.md`."
# Fig 6: the exceedance diagnostic (KGW, alpha = 0.01, h in {1, 2}, same-tokenizer pairs)
EX_V = [("conformal@5000", None), ("tolerance@5000", DELTA), ("empirical", BETA), ("pooled", None)]
fig, axes = plt.subplots(1, 4, figsize=(12.5, 3.6), sharey=True)
for ax, (v, ref) in zip(axes, EX_V):
    s = DF[(DF["family"] == P["family"]) & (DF["alpha"] == A_PRIMARY) & (DF["h"].isin(P["h"])) & (DF["variant"] == v) & (DF["class"].isin(CLASS_ORDER))]
    for c in CLASS_ORDER:
        sc_ = s[s["class"] == c]; ax.scatter(sc_["pred_share_above_alpha_finite"], sc_["share_above_alpha"], s=12, marker=MK_CLASS[c], c=COL_GROUP[GROUP_OF[c]], alpha=0.7, linewidths=0.3, edgecolors=SURFACE)
    ax.plot([0, 1], [0, 1], color=INK, lw=0.9)
    if ref is not None:
        ax.axhline(ref, color=MUTED, lw=0.8); ax.text(0.98, ref + 0.015, f"{'δ' if 'tolerance' in v else 'β'} = {ref}", color=MUTED, fontsize=7, va="bottom", ha="right")
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02); ax.set_title(f"({'abcd'[EX_V.index((v, ref))]}) {v}: {len(s):,} pairs", loc="left", fontsize=9)
axes[0].set_ylabel("measured share of keys above α"); axes[0].legend(handles=CLASS_HANDLES, fontsize=7, loc="lower right"); fig.supxlabel("predicted finite-evaluation share of keys above α (the key-free predictor)", fontsize=9)
fig.suptitle(f"{fx}Study 3, the exceedance diagnostic (KGW, α = 0.01, h ∈ {{1, 2}}, both rules and tokenizers; K = {K:,} keys per pair; a reference, not a PAC-over-keys check)", fontsize=10, x=0.01, ha="left"); fig.tight_layout(); save(fig, "fig6_exceedance")
T["FIG_fig6_exceedance"] = f"![exceedance]({FIG_REL}fig6_exceedance.png)\n\n**Figure 6.** The measured share of keys whose realised level exceeds α against the finite-evaluation prediction, by pair class, for four methods (KGW, α = 0.01, h ∈ {{1, 2}}); the lines mark β (the multipliers) and δ (the tolerance method), references for the diagnostic of protocol §7. Every value is in Table 10 and `tables_remedy_full.md`."
print(f"figures written ({time.time() - t0:.0f}s)", flush=True)

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


text = re.sub(r"<<TABLE:([A-Za-z0-9_.]+)>>", sub_table, prose); text = re.sub(r"<<FIG:([A-Za-z0-9_]+)>>", sub_fig, text); text = re.sub(r"\[\[([A-Za-z0-9_.@]+)\]\]", sub_val, text)
left = re.findall(r"\[\[[^\]]+\]\]|<<[A-Z]+:[^>]+>>", text)
if left:
    raise SystemExit(f"unresolved placeholders remain: {left[:10]}")
if FIXTURE:
    text = "**FIXTURE RENDER ON A SYNTHETIC INVENTORY (planted numbers; not study outcomes; never the report)**\n\n" + text
REPORT.write_text(text)
unused = sorted(set(VALUES) - USED)
CHK["placeholders_registered"] = len(VALUES); CHK["placeholders_used"] = len(USED)
(OUTDIR / "checks.json").write_text(json.dumps({"checks": CHK, "mismatches": MISM[:200], "unused_placeholders": unused}, indent=1, default=str))
print(f"{VALUES['label']}: wrote {REPORT} ({len(text.split())} words), {len(T)} tables/figures, {len(VALUES)} values ({len(unused)} registered but unused); {time.time() - T_START:.0f}s")
