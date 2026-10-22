"""Shared helpers for the paper's generated tables and figures (Stage 8; guide A4.1, A4.10).

Every table and figure script reads the locked outputs through this module, asserts its values against the
agreed reports' registers (``prose_values.json``) with ``check``, registers the values it prints for the prose
placeholders ``[[paper:name]]`` with ``register``, and writes its checks to ``research/paper/checks.json``.
The palette is the dataviz skill's validated reference palette (categorical slots 1–4 pass the adjacent-pair
gates in light mode: ``node scripts/validate_palette.js "#2a78d6,#eb6834,#1baf7a,#eda100" --mode light``, run
2026-10-19; aqua and yellow sit below 3:1 on the surface, so every figure carries a legend and direct labels).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "research" / "paper"
PAPER_VALUES = PAPER / "paper_values.json"
CHECKS_FILE = PAPER / "checks.json"

STUDY_DIR = {"s1": "outputs/study1_v0.3", "s2": "outputs/study2_v0.1", "s3": "outputs/study3_v0.1", "s4": "outputs/study4_v0.1"}
STUDY_NAME = {"s1": "study1_v0.3", "s2": "study2_v0.1", "s3": "study3_v0.1", "s4": "study4_v0.1"}
CHECKPOINT_OF_LOCK = {"s1": "R03", "s2": "R05", "s3": "R07", "s4": "R09"}
CHECKPOINT_OF_REPORT = {"s1": "R04", "s2": "R06", "s3": "R08", "s4": "R10"}

# --- the palette (dataviz reference instance, light mode) ------------------------------------------------
SLOT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]        # categorical slots 1–4, fixed order, never cycled
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"          # text tokens
GRIDLINE, AXIS = "#e1e0d9", "#c3c2b7"
SURFACE = "#ffffff"                                        # the paper's page is white
SEQ_BLUE = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
DIV_BLUE, DIV_MID, DIV_RED = "#2a78d6", "#f0efec", "#e34948"
SVG_HASHSALT = "paper_v0.1"

_cache: dict[str, object] = {}


def sha256(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_json(rel: str) -> object:
    if rel not in _cache:
        _cache[rel] = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    return _cache[rel]


def lock(s: str) -> dict:
    return _load_json(f"{STUDY_DIR[s]}/PRE_RUN_LOCK.json")


def manifest(s: str) -> dict:
    return _load_json(f"{STUDY_DIR[s]}/RUN_MANIFEST.json")


def grid(s: str) -> dict:
    return _load_json(lock(s)["grid"])


def register(s: str) -> dict:
    return _load_json(f"{STUDY_DIR[s]}/report/prose_values.json")


def results(s: str) -> dict:
    """The locked analyser's output, verified against the lock (Studies 1–2) or the run manifest's digest (3–4)."""
    key = f"results:{s}"
    if key in _cache:
        return _cache[key]
    d = ROOT / STUDY_DIR[s]
    p = d / "results.json"
    if p.exists():
        raw = p.read_bytes()
    elif (d / "results.json.gz").exists():
        raw = gzip.decompress((d / "results.json.gz").read_bytes())
    else:
        raise FileNotFoundError(f"{s}: no results file")
    digest = hashlib.sha256(raw).hexdigest()
    res = json.loads(raw)
    lock_sha = sha256(d / "PRE_RUN_LOCK.json")
    if s == "s1":
        assert res["provenance"]["lock_sha256"] == lock_sha, "study 1 results were produced under another lock"
    elif s == "s2":
        assert res["lock"]["sha256"] == lock_sha, "study 2 results were produced under another lock"
    else:
        rec = manifest(s)["analysis_output"]
        assert rec["sha256"] == digest, f"{s}: results.json differs from the digest the run manifest records"
    assert res.get("label", "STUDY") == "STUDY" and "FIXTURE" not in res, f"{s}: not a study-mode results file"
    _cache[key] = res
    return res


def cells_dir(s: str) -> Path:
    return ROOT / STUDY_DIR[s] / "cells"


# --- parsing the registers' formatted strings ------------------------------------------------------------
def num(text: str) -> float:
    """A register string ('1,000', '61.4%', '0.499', '−0.013', '14.0') as a float on its printed scale."""
    t = str(text).strip().replace(",", "").replace("−", "-").replace("%", "").replace(" pp", "").strip()
    return float(t)


def num_range(text: str) -> tuple[float, float]:
    a, b = str(text).split("–")
    return num(a), num(b)


def decimals(text: str) -> int:
    t = str(text).strip().replace("%", "")
    return len(t.split(".")[1]) if "." in t else 0


CHECKS: list[dict] = []
_FAILED: list[str] = []


def check(what: str, computed: float, expected: str | float, tol: float | None = None, scale: float = 1.0) -> None:
    """Assert that a computed value equals a register's printed value to half a unit in its last digit."""
    exp = num(expected) if isinstance(expected, str) else float(expected)
    comp = float(computed) * scale
    if tol is None:
        tol = 0.5 * 10 ** (-decimals(expected)) + 1e-9 if isinstance(expected, str) else 1e-9
    ok = abs(comp - exp) <= tol
    CHECKS.append({"what": what, "computed": comp, "expected": exp, "tol": tol, "ok": ok})
    if not ok:
        _FAILED.append(f"{what}: computed {comp!r}, register {exp!r} (tol {tol})")


def finish_checks(prefix: str) -> None:
    """Write this script's checks under its prefix and raise if any failed (a wrong number never ships)."""
    allc = json.loads(CHECKS_FILE.read_text()) if CHECKS_FILE.exists() else {}
    allc[prefix] = {"n": len(CHECKS), "n_failed": len(_FAILED), "checks": CHECKS}
    CHECKS_FILE.write_text(json.dumps(allc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if _FAILED:
        raise SystemExit(f"{prefix}: {len(_FAILED)} check(s) FAILED:\n  " + "\n  ".join(_FAILED))
    print(f"{prefix}: {len(CHECKS)} checks against the registers, 0 failed")


_REG: dict[str, object] = {}


def register_value(name: str, value: object) -> None:
    _REG[name] = value


def flush_values(prefix) -> None:
    """Merge this script's values into paper_values.json, replacing every earlier name under its prefix(es).

    ``prefix`` is one prefix ('t': 't1_…', 't2_…'; 'f': 'f3_…') or a sequence of prefixes for a script that registers
    under several ('c', 'e', 'd' for the appendix tables); every registered name must carry one of them."""
    prefixes = [prefix] if isinstance(prefix, str) else list(prefix)
    allv = json.loads(PAPER_VALUES.read_text()) if PAPER_VALUES.exists() else {}
    pats = [re.compile(rf"^{re.escape(p)}\d*_") for p in prefixes]
    allv = {k: v for k, v in allv.items() if not any(p.match(k) for p in pats)}
    for k, v in _REG.items():
        assert any(p.match(k) for p in pats), (k, prefixes)
        allv[k] = v
    PAPER_VALUES.write_text(json.dumps(allv, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{'/'.join(prefixes)}: {len(_REG)} values registered in paper_values.json")


# --- formatting --------------------------------------------------------------------------------------------
def fnum(x: float, d: int = 2) -> str:
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return f"{x:,.{d}f}"


def pct(x: float, d: int = 1) -> str:
    """A share in [0, 1] as a percentage string."""
    return f"{100 * x:.{d}f}%"


def pp(x: float, d: int = 2) -> str:
    """A probability in [0, 1] in percentage points."""
    return f"{100 * x:.{d}f}"


def md_table(header: list[str], rows: list[list], align: list[str] | None = None) -> str:
    align = align or ["---"] * len(header)
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join(align) + " |"]
    for r in rows:
        assert len(r) == len(header), (len(r), len(header), r)
        out.append("| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |")
    return "\n".join(out) + "\n"


CELL_LABEL = {"news_en_256": "news/en@256", "wikipedia_en_256": "wikipedia/en@256", "stackexchange_en_256": "stackexchange/en@256",
              "wikipedia_de_256": "wikipedia/de@256", "wikipedia_ru_256": "wikipedia/ru@256", "wikipedia_ar_256": "wikipedia/ar@256",
              "wikipedia_zh_256": "wikipedia/zh@256", "wikipedia_ja_256": "wikipedia/ja@256", "wikipedia_en_1024": "wikipedia/en@1024",
              "gutenberg_en_1024": "gutenberg/en@1024"}
CELL_SHORT = {"news_en_256": "news", "wikipedia_en_256": "wiki en", "stackexchange_en_256": "stack ex.", "wikipedia_de_256": "wiki de",
              "wikipedia_ru_256": "wiki ru", "wikipedia_ar_256": "wiki ar", "wikipedia_zh_256": "wiki zh", "wikipedia_ja_256": "wiki ja",
              "wikipedia_en_1024": "wiki en@1024", "gutenberg_en_1024": "gutenberg"}
CELL_ORDER = ["news_en_256", "wikipedia_en_256", "stackexchange_en_256", "wikipedia_en_1024", "gutenberg_en_1024",
              "wikipedia_de_256", "wikipedia_ru_256", "wikipedia_ar_256", "wikipedia_zh_256", "wikipedia_ja_256"]
TOK_LABEL = {"llama": "Llama-3.2", "qwen": "Qwen2.5"}
LMAX = {c: (1024 if c.endswith("1024") else 256) for c in CELL_ORDER}
METHOD_LABEL = {"nominal": "nominal", "multiplier20": "multiplier 1/β", "empirical": "empirical multiplier", "pooled": "pooled",
                "conformal@1000": "conformal, N_cal 1,000", "conformal@5000": "conformal, N_cal 5,000",
                "tolerance@1000": "tolerance, N_cal 1,000", "tolerance@5000": "tolerance, N_cal 5,000"}
CLASS_LABEL = {"diagonal": "diagonal (own law)", "near_identical": "near-identical pair", "within_english": "within English",
               "english_other": "English–other", "other_other": "other–other", "cross_tokenizer": "cross-tokenizer"}


# --- matplotlib style -----------------------------------------------------------------------------------------
def style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "sans-serif", "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "legend.fontsize": 7.5,
        "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "axes.labelcolor": INK2,
        "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRIDLINE, "grid.linewidth": 0.6, "axes.axisbelow": True,
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "lines.linewidth": 1.6, "lines.markersize": 4.5, "legend.frameon": False, "svg.hashsalt": SVG_HASHSALT,
        "figure.dpi": 100,
    })
    return plt


def save(fig, name: str, outdir: Path | None = None) -> None:
    """PNG (200 dpi) and SVG without a creation date: byte-reproducible builds (guide Part G, 2026-10-15)."""
    outdir = outdir or (PAPER / "figures")
    outdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(outdir / f"{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(outdir / f"{name}.svg", bbox_inches="tight", metadata={"Date": None})
    import matplotlib.pyplot as plt
    plt.close(fig)
    print(f"wrote {outdir.relative_to(ROOT)}/{name}.png and .svg")


def logfmt(ax, axis: str = "y", subs=(1.0, 2.0, 5.0)):
    import matplotlib.ticker as mt
    a = ax.yaxis if axis == "y" else ax.xaxis
    a.set_major_locator(mt.LogLocator(base=10, subs=subs))
    a.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:g}"))
    a.set_minor_formatter(mt.NullFormatter())
