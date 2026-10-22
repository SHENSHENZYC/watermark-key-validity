#!/usr/bin/env python3
"""Word and page budget for the paper (Stage 8 of the research-project-guide; A6 standard).

Counts the prose words of every section draft in research/paper/sections/*.md and compares them
with the budget fixed in OUTLINE_v0.1.md, then estimates the main-text page count from one named
words-per-page constant and the planned (or placed) floats. The rendered PDF at assembly is the
only real page count; this script exists so that every review and log entry quotes the same
convention (guide Part G, 2026-10-05: fix the constant in a committed script before the first
section is counted).

Counting rules (prose words only):
  * a file's "## Open items" block (from that header to the end of the file) is excluded;
  * table lines (starting with '|'), figure markers ('<<FIG:...>>', '![...'), table markers
    ('<<TABLE:...>>'), HTML comments and blank lines are excluded;
  * a placeholder '[[name]]' counts as one word (it becomes one number), a citation '[@key]' as one;
  * an inline math span '$...$' counts as one word; a display equation '$$...$$' is not counted as prose
    but as one equation-equivalent of EQUATION_WORDS words of page space (reported apart);
  * headings count (they take space).

Usage:  .venv/bin/python research/paper/wordcount.py [--json] [--sections DIR]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECTIONS_DIR = HERE / "sections"

# --- the convention (one place; quoted in every review and log entry) -------------------------
WORDS_PER_PAGE = 650          # single-column 11 pt, Letter; the stricter convention of 2026-10-05
FIGURE_PAGES = 0.45           # fallback estimate for a figure not yet rendered (with its caption)
TABLE_PAGES = 0.40            # fallback estimate for a table not yet generated (with its caption)
TEXT_WIDTH_IN, TEXT_HEIGHT_IN = 6.5, 9.0   # the single-column text block the figures are scaled to
CAPTION_PAGES = 0.08          # one caption
TABLE_ROW_PAGES = 0.022       # one table row at 11 pt (a 10-column table takes 1.2 x; the header and caption 0.12)
EQUATION_WORDS = 25           # page space of one display equation, in words (about two text lines)
PAGE_TARGET = 13.0            # the outline's target after O4 (2026-10-19): the A6 ceiling, with named cuts if the render exceeds it
PAGE_MAX = 13.0               # the A6 ceiling (10-13 main pages, references and appendix excluded)
PAGE_MIN = 10.0

# --- the budget (OUTLINE_v0.1.md, section 7, re-budgeted by O4, O5, O6 and O7 on 2026-10-19); file stem -> (title, target words)
BUDGET: dict[str, tuple[str, int]] = {
    "00_abstract":      ("Abstract", 300),
    "01_introduction":  ("1 Introduction", 720),
    "02_related_work":  ("2 Related work", 620),
    "03_theory":        ("3 Setting, identities and the first-order predictor", 1350),
    "04_studies":       ("4 The four pre-registered studies: design, data and locks", 700),
    "05_dispersion":    ("5 Results I: the dispersion on synthetic laws and real text", 1050),
    "06_remedies":      ("6 Results II: remedies and transfer on the null side", 850),
    "07_power":         ("7 Results III: the power side", 800),
    "08_discussion":    ("8 Discussion, limitations and reproducibility", 500),
}
MAIN_FIGURES_PLANNED = 6
MAIN_TABLES_PLANNED = 3          # Table 3 (the predictor by block) went to Appendix D at O5 (2026-10-19); Tables 2 and 4 at O9 (2026-10-20)

PLACEHOLDER = re.compile(r"\[\[[^\]]+\]\]")
DISPLAY_MATH = re.compile(r"\$\$.*?\$\$", re.S)
INLINE_MATH = re.compile(r"\$[^$\n]+?\$")
CITATION = re.compile(r"\[@[^\]]+\]|@[A-Za-z][\w:.-]*")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
WORD = re.compile(r"[A-Za-z0-9À-ɏͰ-Ͽ][\w'’\-À-ɏͰ-Ͽ%]*")


def prose_words(text: str) -> tuple[int, int, int, int]:
    """Return (words, figure markers, table markers, display equations) of the prose part of a draft."""
    text = HTML_COMMENT.sub(" ", text)
    n_eq = len(DISPLAY_MATH.findall(text))
    text = DISPLAY_MATH.sub(" ", text)
    text = INLINE_MATH.sub(" MATH ", text)
    lines = text.splitlines()
    kept: list[str] = []
    n_fig = n_tab = 0
    in_open_items = False
    for line in lines:
        s = line.strip()
        if re.match(r"^##+\s*Open items", s, re.I):
            in_open_items = True
        if in_open_items:
            continue
        if not s:
            continue
        if s.startswith("|"):
            continue
        if s.startswith("<<FIG:") or s.startswith("!["):
            n_fig += 1
            continue
        if s.startswith("<<TABLE:"):
            n_tab += 1
            continue
        if s.startswith("Figure — ") or s.startswith("Table — "):
            continue                      # a caption line belongs to its float's page space, not to the prose
        kept.append(s)
    body = "\n".join(kept)
    body = PLACEHOLDER.sub(" NUM ", body)
    body = CITATION.sub(" CIT ", body)
    return len(WORD.findall(body)), n_fig, n_tab, n_eq


def float_estimate(sections_dir: Path) -> tuple[float, list[tuple[str, float]]]:
    """Pages of the placed floats: a rendered figure scaled to the text width (its PNG at 200 dpi) plus a caption;
    a generated table by its row and column counts. Returns (pages, [(name, pages), ...])."""
    import struct
    detail: list[tuple[str, float]] = []
    for stem in BUDGET:                                   # the main text's floats only (the appendices are outside the count)
        f = sections_dir / f"{stem}.md"
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("<<FIG:"):
                name = s[6:].rstrip(">").strip(); png = HERE / "figures" / f"{name}.png"
                if png.exists():
                    with png.open("rb") as fh:
                        head = fh.read(24)
                    w, h = struct.unpack(">II", head[16:24])
                    width_in, height_in = w / 200.0, h / 200.0
                    scale = min(1.0, TEXT_WIDTH_IN / width_in)
                    detail.append((f"fig {name}", min(1.0, height_in * scale / TEXT_HEIGHT_IN + CAPTION_PAGES)))
                else:
                    detail.append((f"fig {name} (not rendered)", FIGURE_PAGES))
            elif s.startswith("<<TABLE:"):
                name = s[8:].rstrip(">").strip(); md = HERE / "tables" / f"{name}.md"
                if md.exists():
                    rows = [ln for ln in md.read_text(encoding="utf-8").splitlines() if ln.startswith("|")]
                    ncol = rows[0].count("|") - 1 if rows else 0; nrow = max(0, len(rows) - 2)
                    wide = 1.2 if ncol >= 10 else 1.0
                    detail.append((f"table {name}", min(1.5, 0.12 + TABLE_ROW_PAGES * nrow * wide)))
                else:
                    detail.append((f"table {name} (not generated)", TABLE_PAGES))
    return sum(p for _, p in detail), detail


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sections", type=Path, default=SECTIONS_DIR)
    ap.add_argument("--json", action="store_true", help="print a JSON record instead of the table")
    args = ap.parse_args(argv)

    rows = []
    total_words = total_target = total_eq = 0
    placed_fig = placed_tab = missing = 0
    for stem, (title, target) in BUDGET.items():
        path = args.sections / f"{stem}.md"
        if path.exists():
            words, nf, nt, ne = prose_words(path.read_text(encoding="utf-8"))
            status = "ok" if words <= target else "OVER"
        else:
            words, nf, nt, ne, status = 0, 0, 0, 0, "missing"
            missing += 1
        placed_fig += nf
        placed_tab += nt
        total_eq += ne
        total_words += words
        total_target += target
        rows.append({"section": title, "file": path.name, "target": target, "words": words,
                     "equations": ne, "pages": round((words + ne * EQUATION_WORDS) / WORDS_PER_PAGE, 2),
                     "status": status, "figures_placed": nf, "tables_placed": nt})

    # the planned floats until every section exists, the placed ones afterwards
    n_fig = MAIN_FIGURES_PLANNED if missing else placed_fig
    n_tab = MAIN_TABLES_PLANNED if missing else placed_tab
    prose_pages = (total_words + total_eq * EQUATION_WORDS) / WORDS_PER_PAGE
    target_pages = total_target / WORDS_PER_PAGE
    float_pages, float_detail = float_estimate(args.sections)
    if not float_detail:
        float_pages = n_fig * FIGURE_PAGES + n_tab * TABLE_PAGES
    record = {
        "convention": {"words_per_page": WORDS_PER_PAGE, "figure_pages": FIGURE_PAGES,
                       "table_pages": TABLE_PAGES, "page_target": PAGE_TARGET, "page_max": PAGE_MAX},
        "sections": rows,
        "floats": [{"name": n, "pages": round(p, 2)} for n, p in float_detail],
        "totals": {"words": total_words, "target_words": total_target, "equations": total_eq,
                   "prose_pages": round(prose_pages, 2), "target_prose_pages": round(target_pages, 2),
                   "figures": n_fig, "tables": n_tab, "placed_figures": placed_fig, "placed_tables": placed_tab,
                   "float_pages": round(float_pages, 2),
                   "estimated_main_pages": round(prose_pages + float_pages, 2),
                   "estimated_main_pages_at_budget": round(target_pages + float_pages, 2),
                   "floats_source": "planned" if missing else "placed"},
    }
    if args.json:
        print(json.dumps(record, indent=2))
        return 0

    print(f"Word budget (words per page = {WORDS_PER_PAGE}; a figure {FIGURE_PAGES} p, a table {TABLE_PAGES} p; "
          f"target {PAGE_TARGET} p, ceiling {PAGE_MAX} p)")
    print(f"{'section':<62}{'target':>8}{'words':>8}{'eqs':>5}{'pages':>7}  status")
    for r in rows:
        print(f"{r['section']:<62}{r['target']:>8}{r['words']:>8}{r['equations']:>5}{r['pages']:>7.2f}  {r['status']}")
    t = record["totals"]
    print(f"{'TOTAL prose (pages include ' + str(EQUATION_WORDS) + ' words per equation)':<62}{t['target_words']:>8}{t['words']:>8}{t['equations']:>5}{t['prose_pages']:>7.2f}")
    print(f"floats ({t['floats_source']}): {t['figures']} figures + {t['tables']} tables = {t['float_pages']} pages "
          f"(placed so far: {t['placed_figures']} figures, {t['placed_tables']} tables)")
    for name, pg in float_detail:
        print(f"    {name:<40}{pg:6.2f} p")
    print(f"estimated main text: {t['estimated_main_pages']} pages now; {t['estimated_main_pages_at_budget']} pages at the full budget "
          f"(ceiling {PAGE_MAX}; the rendered PDF at assembly is the real count)")
    over = [r["section"] for r in rows if r["status"] == "OVER"]
    if over:
        print("OVER budget: " + "; ".join(over))
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
