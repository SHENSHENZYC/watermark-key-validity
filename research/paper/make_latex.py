#!/usr/bin/env python3
"""Convert the assembled draft to LaTeX and compile it with Tectonic (Stage 9; the page count that matters).

Reads ``PAPER_DRAFT_v0.1.md`` (the assembly's output, never a section file), takes the title block from its YAML front
matter (title, author as ``Name (Affiliation; email)``, the date line, the abstract), strips the manual section and
appendix numbers (LaTeX numbers sections and appendices itself; every table and figure keeps the assembly's label
inside its caption, printed with ``labelformat=empty``, so every cross-reference in the text stays as assembled), makes
the two statements unnumbered sections, places the bibliography where the assembly placed it, points the figures at
PDF copies converted from the figure scripts' SVG files (``rsvg-convert``; the PNG is used where no SVG exists), runs
pandoc (natbib citations, longtable tables), maps the non-ASCII characters of the prose to LaTeX macros (so that
pdflatex with ``inputenc`` and Tectonic's XeTeX give the same result), sizes each table's columns from its content, sets
the widest on landscape pages and splits a table whose columns fit no page into column panels that repeat the table's
identifying columns (R13 F3, F11), writes ``latex/main.tex``, ``latex/references.bib`` (the master bibliography with the
internal ``note`` fields removed) and ``latex/figures/*.pdf``, compiles with Tectonic (BibTeX runs inside), and records
the page counts in ``latex/page_count_latex.json`` (the full PDF, the page the statements start on, the page the
references start on, the main text before the statements, the appendices' first page, the overfull lines, the
level and orientation of every column panel).

Run: .venv/bin/python research/paper/make_latex.py [--no-compile]
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent
FIGURES = PAPER / "figures"
OUT = PAPER / "latex"
FIGS = OUT / "figures"
SRC = PAPER / "PAPER_DRAFT_v0.1.md"
COMPILE = "--no-compile" not in sys.argv

PREAMBLE = r"""\documentclass[11pt,letterpaper]{article}
% pdflatex-compatible preamble; Tectonic (XeTeX) compiles the same source.
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs,longtable,array,calc}
\usepackage{float}
\usepackage{pdflscape}
\usepackage{caption}
\captionsetup{labelformat=empty,font=small,skip=4pt}
\usepackage[numbers,sort&compress]{natbib}
\usepackage{xcolor}
\usepackage[hidelinks,breaklinks]{hyperref}
\usepackage{url}
\urlstyle{same}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\setlength{\parskip}{4pt plus 1pt}
\setlength{\emergencystretch}{2em}
\setlength{\parindent}{0pt}
\setlength{\LTpre}{6pt}\setlength{\LTpost}{6pt}
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.1}
\renewcommand{\topfraction}{0.95}\renewcommand{\bottomfraction}{0.9}\renewcommand{\textfraction}{0.05}\renewcommand{\floatpagefraction}{0.75}
\makeatletter\setlength{\@fptop}{0pt}\makeatother
\makeatletter\renewcommand{\@makefntext}[1]{\noindent\makebox[1.2em][l]{\@thefnmark}#1}\makeatother
"""

# non-ASCII characters of the prose -> LaTeX (text mode; \ensuremath keeps them valid inside math too). The en and em
# dashes and the curly quotes are left to inputenc (pdflatex) or the engine (XeTeX); accented Latin letters are mapped.
CHARMAP = {
    "\u03b1": r"\ensuremath{\alpha}", "\u03b2": r"\ensuremath{\beta}", "\u03b3": r"\ensuremath{\gamma}", "\u03b4": r"\ensuremath{\delta}",
    "\u03b5": r"\ensuremath{\varepsilon}", "\u03ba": r"\ensuremath{\kappa}", "\u03bc": r"\ensuremath{\mu}", "\u03c0": r"\ensuremath{\pi}",
    "\u03c1": r"\ensuremath{\rho}", "\u03c3": r"\ensuremath{\sigma}", "\u03c4": r"\ensuremath{\tau}", "\u0394": r"\ensuremath{\Delta}", "\u2206": r"\ensuremath{\Delta}",
    "\u2264": r"\ensuremath{\leq}", "\u2265": r"\ensuremath{\geq}", "\u2192": r"\ensuremath{\rightarrow}", "\u2212": r"\ensuremath{-}",
    "\u00d7": r"\ensuremath{\times}", "\u2208": r"\ensuremath{\in}", "\u2016": r"\ensuremath{\|}", "\u2248": r"\ensuremath{\approx}",
    "\u00b1": r"\ensuremath{\pm}", "\u00b7": r"\ensuremath{\cdot}", "\u2032": r"\ensuremath{'}", "\u2026": r"\ldots{}", "\u00a7": r"\S{}",
    "\u2113": r"\ensuremath{\ell}", "\u221a": r"\ensuremath{\surd}",
    "\u00b2": r"\ensuremath{^{2}}", "\u00b9": r"\ensuremath{^{1}}", "\u207b": r"\ensuremath{^{-}}",
    "\u2080": r"\ensuremath{_{0}}", "\u2082": r"\ensuremath{_{2}}", "\u2083": r"\ensuremath{_{3}}", "\u2084": r"\ensuremath{_{4}}",
    "\u00c3": r"\ensuremath{\tilde{A}}", "\u0101": r"\ensuremath{\bar{a}}",
    "\u0107": r"\'c", "\u010d": r"\v{c}", "\u0161": r"\v{s}", "\u017e": r"\v{z}", "\u0142": r"\l{}", "\u00e7": r"\c{c}", "\u00e9": r"\'e", "\u00e1": r"\'a", "\u00fc": r'\"u', "\u00f6": r'\"o', "\u00e4": r'\"a', "\u00e8": r"\`e",
    "\u00ed": r"\'i", "\u00f3": r"\'o", "\u00fa": r"\'u", "\u00f1": r"\~n", "\u00e0": r"\`a", "\u00a0": "~",
}
LEFT_ALONE = set("\u2014\u2013\u2019\u2018\u201c\u201d")   # handled by inputenc / the engine


def prepare_markdown(md: str):
    m = re.match(r"---\n(.*?)\n---\n", md, re.S)
    yaml, body = m.group(1), md[m.end():]
    meta = {k: v for k, v in re.findall(r'^(\w[\w-]*): "(.*?)"$', yaml, re.M)}
    am = re.search(r"^abstract: \|\n((?:  .*\n?)+)", yaml, re.M)
    abstract = "\n".join(ln[2:] for ln in am.group(1).splitlines()).strip()
    out, appendix, stmts = [], False, 0
    for line in body.split("\n"):
        if line.startswith("# References"):
            out.append("\nBIBLIOGRAPHYMARKER\n"); continue
        if line.strip() == "::: {#refs}" or (line.strip() == ":::" and out and out[-1].strip() == "::: {#refs}"):
            continue
        h = re.match(r"^(#{1,3}) (.*)$", line)
        if h:
            level, text = h.groups()
            if re.match(r"^Appendix [A-Z] ", text):
                if not appendix:
                    out.append("\nAPPENDIXMARKER\n"); appendix = True
                text = re.sub(r"^Appendix [A-Z] ", "", text)
            elif re.match(r"^[A-Z]\.\d+ ", text):
                text = re.sub(r"^[A-Z]\.\d+ ", "", text)
            elif re.match(r"^\d+(\.\d+)? ", text):
                text = re.sub(r"^\d+(\.\d+)? ", "", text)
            elif text in ("AI use and independent review", "Code and data availability", "Acknowledgements"):
                text = text + " {-}"; stmts += 1
            line = f"{level} {text}"
        out.append(line)
    assert stmts == 2, f"expected the two statements as unnumbered sections, found {stmts}"
    body = "\n".join(out)
    body = re.sub(r"\]\(figures/([A-Za-z0-9_]+)\.png\)", r"](figures/\1.pdf)", body)
    body = re.sub(r"(?<![<(\[`])(https?://[^\s)>\]`]+)", r"<\1>", body)   # bare URLs -> autolinks (pandoc emits \url{})
    return meta, abstract, body


def pandoc(md_text: str) -> str:
    r = subprocess.run(["pandoc", "-f", "markdown", "-t", "latex", "--natbib", "--top-level-division=section", "--wrap=none"],
                       input=md_text, text=True, capture_output=True, check=True)
    return r.stdout


def map_chars(tex: str) -> str:
    # combining marks follow their base letter: bar, hat and tilde (Greek bases first, then any word character)
    greek = {"\u03c1": r"\rho", "\u03ba": r"\kappa", "\u03b1": r"\alpha", "\u03b4": r"\delta", "\u03c3": r"\sigma", "\u03b2": r"\beta", "\u03b3": r"\gamma", "\u03bc": r"\mu"}
    for mark, macro in (("\u0304", "bar"), ("\u0302", "hat"), ("\u0303", "tilde")):
        for g, gm in greek.items():
            tex = tex.replace(g + mark, "\\ensuremath{\\%s{%s}}" % (macro, gm))
        tex = re.sub(r"(\w)" + mark, lambda m, macro=macro: "\\ensuremath{\\%s{%s}}" % (macro, m.group(1)), tex)
    tex = re.sub(r"\u221a([A-Za-z])", r"\\ensuremath{\\sqrt{\1}}", tex)   # √T
    for ch, rep in CHARMAP.items():
        tex = tex.replace(ch, rep)
    left = sorted({c for c in tex if ord(c) > 126 and c not in LEFT_ALONE})
    if left:
        print("WARNING: unmapped non-ASCII characters left in the LaTeX:", [f"U+{ord(c):04X} {c!r}" for c in left])
    return tex


def strip_bib_notes(src: Path, dst: Path) -> int:
    s = src.read_text(encoding="utf-8")
    out, i = [], 0
    pat = re.compile(r",\s*\n\s*note\s*=\s*\{")
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:]); break
        out.append(s[i:m.start()])
        j, depth = m.end(), 1
        while depth:
            j += 1
            depth += {"{": 1, "}": -1}.get(s[j - 1], 0)
        i = j
    text = "".join(out)
    assert not re.search(r"^\s*note\s*=", text, re.M), "a note field survived"
    text = re.sub(r"(?<!\\)&", r"\\&", text)   # a bare ampersand in a field value is an alignment tab to LaTeX
    text = map_chars(text)                          # accented names (Jovanović, Souček) for the legacy T1 font
    dst.write_text(text, encoding="utf-8")
    return len(re.findall(r"^@", text, re.M))


def convert_figures() -> tuple[int, int]:
    FIGS.mkdir(parents=True, exist_ok=True)
    n_svg = n_png = 0
    for png in sorted(FIGURES.glob("*.png")):
        svg = png.with_suffix(".svg"); dst = FIGS / (png.stem + ".pdf")
        if svg.exists() and shutil.which("rsvg-convert"):
            subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(dst), str(svg)], check=True); n_svg += 1
        else:   # no vector source: the PNG is used as it is
            shutil.copy(png, FIGS / png.name); n_png += 1
    return n_svg, n_png



# --- tables -----------------------------------------------------------------------------------------------------
TEXT_WIDTH_PT = {"portrait": 469.75, "landscape": 648.0}    # Letter, 1in margins: 6.5in and 9in
LEVELS = [("footnotesize", 9.0, 3.0, "portrait"), ("scriptsize", 7.0, 2.5, "portrait"), ("scriptsize", 7.0, 2.5, "landscape")]
CHAR_EM = 0.60   # average character width in em for Latin Modern Roman with an allowance for digits, capitals and bold
PAD_PT = 4.0     # added to every column's need
PANELS: dict[str, list[str]] = {}   # table label -> the level and orientation of each of its column panels (recorded in page_count_latex.json)


def _cell_text(cell: str) -> str:
    cell = re.sub(r"\\begin\{minipage\}\[[^\]]*\]\{[^}]*\}\\raggedright", "", cell)
    cell = cell.replace("\\end{minipage}", "")
    cell = re.sub(r"\\(?:textbf|texttt|emph|textit)\{((?:[^{}]|\{[^{}]*\})*)\}", r"\1", cell)
    cell = re.sub(r"\\ensuremath\{[^{}]*(?:\{[^{}]*\})*[^{}]*\}", "x", cell)
    cell = re.sub(r"\\[A-Za-z]+\{?\}?", "", cell)
    cell = cell.replace("{[}", "[").replace("{]}", "]").replace("\\_", "_").replace("\\%", "%").replace("\\&", "&").replace("\\allowbreak{}", " ")
    return re.sub(r"\s+", " ", cell).strip()


def _caption_name(cell: str) -> str:
    """A header cell as plain caption text: pandoc's minipage wrapper (whose \\linewidth would overflow a caption line) and
    the inserted break opportunities removed, the LaTeX of the label itself kept."""
    cell = re.sub(r"\\begin\{minipage\}\[[^\]]*\]\{[^}]*\}\\raggedright", "", cell).replace("\\end{minipage}", "")
    return re.sub(r"\s+", " ", cell.replace("\\allowbreak{}", "")).strip()


def _breakable(cell: str) -> str:
    """Break opportunities inside a plain cell: after a slash, an at sign or an escaped underscore (labels such as stackexchange/en@256)."""
    if "\\includegraphics" in cell:
        return cell
    return re.sub(r"(/|@|\\_)(?=[A-Za-z0-9])", r"\1\\allowbreak{}", cell)


def _measure(cols: list[list[str]]) -> tuple[list[int], list[int]]:
    longest_piece = [1] * len(cols); longest_cell = [1] * len(cols)
    for i, col in enumerate(cols):
        for c in col:
            pieces = re.split(r"[ /\u2013\u2014-]+", c)
            longest_piece[i] = max(longest_piece[i], max((len(x) for x in pieces), default=1))
            longest_cell[i] = max(longest_cell[i], len(c))
    return longest_piece, longest_cell


def _fit(longest_piece: list[int], longest_cell: list[int], ncol: int):
    """The first level at which every column's widest unbreakable piece fits; None if none does (the table is split)."""
    cap = 60 if ncol <= 6 else 40 if ncol <= 11 else max(12, int(240 / ncol))
    for size, pt, colsep, orient in LEVELS:
        avail = TEXT_WIDTH_PT[orient] - 2 * (ncol - 1) * colsep
        need = [lp * CHAR_EM * pt + PAD_PT for lp in longest_piece]
        pref = [max(n, min(lc, cap) * CHAR_EM * pt + PAD_PT) for n, lc in zip(need, longest_cell)]
        if sum(need) <= avail:
            if sum(pref) <= avail:
                widths = pref
            else:
                slack = avail - sum(need); extra = [max(p - n, 0.0) for p, n in zip(pref, need)]; s = sum(extra) or 1.0
                widths = [n + slack * e / s for n, e in zip(need, extra)]
            return size, colsep, orient, [w / avail for w in widths]
    return None


def _emit(label: str | None, caption: str | None, part: str, spec_lines: list[str], hcells: list[str], rows: list[list[str]], fit, foot: str) -> str:
    size, colsep, orient, rel = fit
    it = iter(rel)
    spec2 = "\n".join(re.sub(r"\\real\{[0-9.]+\}", lambda _m: "\\real{%.4f}" % next(it), ln) for ln in spec_lines)
    spec2 = re.sub(r"\(\\columnwidth - \d+\\tabcolsep\)", "(\\\\columnwidth - %d\\\\tabcolsep)" % (2 * (len(rel) - 1)), spec2)
    head = "\\toprule\\noalign{}\n" + " & ".join(hcells) + " \\\\\n\\midrule\\noalign{}\n"
    cap_tex = ""
    if caption is not None:
        cap_tex = "\\caption*{\\textbf{%s%s.} %s}\\tabularnewline\n" % (label, part, caption)
    body = "\n".join(" & ".join(r) + " \\\\" for r in rows)
    open_ = ("\\begin{landscape}" if orient == "landscape" else "") + "{\\%s\\setlength{\\tabcolsep}{%gpt}" % (size, colsep)
    close = "}" + ("\\end{landscape}" if orient == "landscape" else "")
    return (open_ + "\\begin{longtable}[]{@{}\n" + spec2 + "@{}}\n" + cap_tex + head + ("\\endfirsthead\n" + head if cap_tex else "") + "\\endhead\n"
            + foot + body + "\n\\end{longtable}" + close)


def process_tables(body: str) -> str:
    """Column widths from the content (each column's longest unbreakable piece as its need, its longest cell capped as its
    preference), the font and orientation as the first level at which the needs fit; a table whose needs fit no level is
    split into column panels, each repeating the table's identifying columns, the shortest prefix of its columns whose
    values identify every row (R13 F3, F11: the first column alone did not identify the rows of any split table); the
    caption inside the first head; break opportunities inside the cell and header labels."""
    pat = re.compile(r"(?:\\textbf\{(Table [A-E]?\d+[a-d]?)\.\} (.*?)\n\n)?\\begin\{longtable\}\[\]\{@\{\}\n(.*?)@\{\}\}\n(.*?)\\end\{longtable\}", re.S)
    report = []

    def one(m: re.Match) -> str:
        label, caption, spec, inner = m.group(1), m.group(2), m.group(3), m.group(4)
        spec_lines = [ln for ln in spec.split("\n") if ln.strip()]
        ncol = sum(ln.count("\\real{") for ln in spec_lines)
        assert ncol == len(spec_lines) >= 1, (ncol, len(spec_lines))
        head, sep, rest = inner.partition("\\endhead\n")
        assert sep, "a longtable without \\endhead"
        hrow = re.sub(r"\\toprule\\noalign\{\}|\\midrule\\noalign\{\}", "", head).strip()
        assert hrow.endswith("\\\\"), hrow[-40:]
        hcells = [re.sub(r"(/|@|\\_)(?=[A-Za-z0-9])", r"\1\\allowbreak{}", c.strip()) for c in re.split(r"(?<!\\)&", hrow[:-2])]
        assert len(hcells) == ncol, (len(hcells), ncol)
        foot_lines, rows = [], []
        for ln in rest.split("\n"):
            if ln.rstrip().endswith("\\\\"):
                cells = [_breakable(c.strip()) for c in re.split(r"(?<!\\)&", ln.rstrip()[:-2])]
                assert len(cells) == ncol, (len(cells), ncol, ln[:80])
                rows.append(cells)
            elif ln.strip():
                foot_lines.append(ln)
        foot = "".join(l + "\n" for l in foot_lines)   # \bottomrule\noalign{} and \endlastfoot
        cols = [[_cell_text(hcells[i])] + [_cell_text(r[i]) for r in rows] for i in range(ncol)]
        lp, lc = _measure(cols)
        fit = _fit(lp, lc, ncol)
        if fit is not None:
            report.append((label or "?", ncol, [(fit[0], fit[2])]))
            return _emit(label, caption, "", spec_lines, hcells, rows, fit, foot)
        # split into column panels (R13 F3, F11): the identifying columns, the shortest prefix of columns whose values
        # identify every row, are repeated in every panel; each panel then holds the longest run of the remaining columns
        # that fits a page at some level, so that every value can be read against the labels that identify its row
        plain = [[_cell_text(c) for c in r] for r in rows]
        nkey = next((p for p in range(1, ncol + 1) if len({tuple(r[:p]) for r in plain}) == len(plain)), None)
        assert nkey is not None, f"{label}: no column prefix identifies every row; add a row identifier before splitting"
        key = list(range(nkey))
        names = ", ".join(_caption_name(hcells[i]) for i in key)
        ident = ("its identifying column 1 (%s)" % names) if nkey == 1 else ("its identifying columns 1--%d (%s)" % (nkey, names))
        panels, start = [], nkey
        while start < ncol:
            end = start
            while end < ncol:
                idx = key + list(range(start, end + 1))
                if _fit([lp[i] for i in idx], [lc[i] for i in idx], len(idx)) is None:
                    break
                end += 1
            if end == start:   # one column that never fits beside the identifying columns: emit it alone at the widest level
                end = start + 1
            panels.append(key + list(range(start, end))); start = end
        out, fits = [], []
        for k, idx in enumerate(panels, 1):
            fit_k = _fit([lp[i] for i in idx], [lc[i] for i in idx], len(idx)) or ("scriptsize", 2.5, "landscape", [1.0 / len(idx)] * len(idx))
            fits.append((fit_k[0], fit_k[2]))
            part = "" if k == 1 else " (part %d of %d)" % (k, len(panels))
            if k == 1:
                cap_k = (caption or "") + " This table is set in %d column panels; %s identif%s every row and %s repeated in each panel; this panel holds columns 1--%d of %d." % (
                    len(panels), ident, "ies" if nkey == 1 else "y", "is" if nkey == 1 else "are", idx[-1] + 1, ncol)
            else:
                span = ("Column %d" % (idx[-1] + 1)) if idx[nkey] == idx[-1] else ("Columns %d--%d" % (idx[nkey] + 1, idx[-1] + 1))
                cap_k = "%s of %d of the table above, with %s repeated." % (span, ncol, ident)
            assert idx[nkey:] == list(range(idx[nkey], idx[-1] + 1)), idx
            out.append(_emit(label, cap_k if label else None, part, [spec_lines[i] for i in idx], [hcells[i] for i in idx], [[r[i] for i in idx] for r in rows], fit_k, foot))
        assert sorted(set(i for idx in panels for i in idx)) == list(range(ncol)), (label, panels)   # every column in some panel
        report.append((label or "?", ncol, fits))
        PANELS[label or "?"] = [f"{s} {o}" for s, o in fits]
        return "\n\n".join(out)

    body = pat.sub(one, body)
    counts = {}
    for _, ncol, fits in report:
        for size, orient in fits:
            key = (size, orient, "panel" if len(fits) > 1 else "whole")
            counts[key] = counts.get(key, 0) + 1
    print("tables:", len(report), "|", ", ".join(f"{n} {s} {o} {w}" for (s, o, w), n in sorted(counts.items())), "| panels:", PANELS)
    return body

def main() -> int:
    OUT.mkdir(exist_ok=True)
    meta, abstract_md, body_md = prepare_markdown(SRC.read_text(encoding="utf-8"))
    abstract = map_chars(pandoc(abstract_md)).strip()
    body = map_chars(pandoc(body_md))
    body = body.replace("BIBLIOGRAPHYMARKER", "\\bibliographystyle{plainnat}\n\\bibliography{references}")
    body = body.replace("APPENDIXMARKER", "\\appendix")
    body = body.replace(r"\begin{figure}", r"\begin{figure}[htbp]")

    body = process_tables(body)
    body = re.sub(r"\\includegraphics\{", r"\\includegraphics[width=\\linewidth,keepaspectratio]{", body)   # pandoc 3.0 emits no size
    body = re.sub(r"\\includegraphics\[([^\]]*)\]", lambda m: r"\includegraphics[" + re.sub(r"height=\\textheight,?", "", m.group(1)).rstrip(",") + ("" if "keepaspectratio" in m.group(1) else ",keepaspectratio") + "]", body)
    # break opportunities inside \texttt: every four hex characters of a digest, and after / _ . -
    body = re.sub(r"\\texttt\{([0-9a-f]{8,})", lambda m: "\\texttt{" + re.sub(r"([0-9a-f]{4})(?=[0-9a-f])", r"\1\\allowbreak{}", m.group(1)), body)
    body = re.sub(r"\\texttt\{((?:[^{}]|\{[^{}]*\})*)\}", lambda m: "\\texttt{" + re.sub(r"(/|\\_|\.|-)(?!\\allowbreak)", r"\1\\allowbreak{}", m.group(1)) + "}", body)
    assert "\\begin{table}" not in body or True
    author = meta["author"]
    m = re.match(r"(.*?) \((.*?); (.*?)\)$", author)
    author_tex = (f"{m.group(1)}\\\\ {m.group(2)}\\\\ \\texttt{{{m.group(3)}}}" if m else author)
    date_tex = re.sub(r"(https?://\S+)", lambda u: "\\url{" + u.group(1).rstrip(".") + "}" + ("." if u.group(1).endswith(".") else ""), meta["date"])
    title_tex = map_chars(meta["title"])
    tex = (PREAMBLE + "\n" + f"\\title{{{title_tex}}}\n\\author{{{author_tex}}}\n\\date{{{date_tex}}}\n\n"
           + "\\begin{document}\n\\maketitle\n\n\\begin{abstract}\n" + abstract + "\n\\end{abstract}\n\n" + body + "\n\\end{document}\n")
    (OUT / "main.tex").write_text(tex, encoding="utf-8")
    n_bib = strip_bib_notes(PAPER / "references.bib", OUT / "references.bib")
    n_svg, n_png = convert_figures()
    cites = sorted(set(re.findall(r"\\cite[a-z]*(?:\[[^\]]*\])*\{([^}]*)\}", tex)))
    keys = sorted({k.strip() for c in cites for k in c.split(",")})
    bibkeys = set(re.findall(r"^@\w+\{(\w+),", (OUT / "references.bib").read_text(encoding="utf-8"), re.M))
    missing = [k for k in keys if k not in bibkeys]
    assert not missing, f"citation keys without entries: {missing}"
    for fig in re.findall(r"\\includegraphics\[[^\]]*\]\{figures/([^}]+)\}", tex):
        assert (FIGS / fig).exists(), f"figure file missing: {fig}"
    n_tab = tex.count("\\begin{longtable}"); n_fig = tex.count("\\begin{figure}")
    print(f"main.tex written: {len(tex.splitlines())} lines; {len(keys)} cited keys (all in references.bib, {n_bib} entries); "
          f"{n_svg} figures from SVG and {n_png} from PNG; {n_tab} tables ({tex.count(chr(92) + 'begin{landscape}')} on landscape pages); {n_fig} figures")
    if not COMPILE:
        return 0
    r = subprocess.run(["tectonic", "--keep-logs", "--keep-intermediates", "main.tex"], cwd=OUT, capture_output=True, text=True)
    (OUT / "tectonic.log").write_text(r.stdout + "\n" + r.stderr, encoding="utf-8")
    if r.returncode != 0:
        print("TECTONIC FAILED; last lines:\n" + "\n".join((r.stdout + r.stderr).splitlines()[-40:])); return 1
    warn = [l for l in (r.stdout + r.stderr).splitlines() if "warning" in l.lower()]
    pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", "main.pdf"], cwd=OUT, capture_output=True, text=True).stdout).group(1))
    starts: dict[str, int | None] = {"statements": None, "references": None, "appendices": None}
    for i in range(1, pages + 1):
        t = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "main.pdf", "-"], cwd=OUT, capture_output=True, text=True).stdout
        if starts["statements"] is None and re.search(r"^AI use and independent review\s*$", t, re.M): starts["statements"] = i
        if starts["references"] is None and re.search(r"^References\s*$", t, re.M): starts["references"] = i
        if starts["appendices"] is None and re.search(r"^A\s+Notation and derivations\s*$", t, re.M): starts["appendices"] = i
    assert all(starts.values()), starts
    log = (OUT / "main.log").read_text(errors="ignore") if (OUT / "main.log").exists() else ""
    counts = {"engine": "Tectonic " + subprocess.run(["tectonic", "--version"], capture_output=True, text=True).stdout.strip().split()[-1],
              "full_pdf_pages": pages, "statements_start_page": starts["statements"], "references_start_page": starts["references"],
              "appendices_start_page": starts["appendices"], "main_text_pages_before_statements": starts["statements"] - 1,
              "overfull_hbox_lines": sum(1 for l in log.splitlines() if l.startswith("Overfull \\hbox")),
              "tables": n_tab, "figures": n_fig, "cited_keys": len(keys), "bib_entries": n_bib, "column_panels": PANELS}
    (OUT / "page_count_latex.json").write_text(json.dumps(counts, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(counts), f"| {len(warn)} warning lines (tectonic.log)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
