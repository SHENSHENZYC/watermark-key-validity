#!/usr/bin/env python3
"""Assemble the paper draft from the section drafts (guide Stage 8, step 5; outline §8).

Builds ``research/paper/PAPER_DRAFT_v0.1.md`` from ``sections/*.md``: fills every placeholder through
``fill_paper`` (failing on any unresolved name), strips each section's "Open items" block into
``PAPER_OPEN_ITEMS_v0.1.md``, numbers the tables and figures (the main text sequentially in order of appearance,
asserted equal to the numbers the file names and the prose carry; the appendices by their letter and index), turns
the ``Table —`` and ``Figure —`` caption lines into numbered captions, places the reference list after the two
statements and before the appendices, checks that every citation key has an entry and every entry is cited, that
every "Table N", "Figure N", "Table Dn", "Figure Dn" and "Appendix Dn" reference in the prose resolves to a float,
that every "§n.m" and "Appendix X.n" reference resolves to a heading or a labelled paragraph, that a reference to an
appendix table with sub-tables names the sub-table, that every supplement a main-text caption promises exists and carries
the promised content (R12 F6), that no numeral or counting word the literal scan's patterns recognise is typed outside a placeholder without a grid
check, an algebraic status or an allow-listed reason, with the spans set aside counted by class (``literals.py``; R12 F7, F15, F22), that no placeholder, marker, absolute path or private-folder name survives,
and that the lock digests in the lock table (Appendix E) are those of the lock files on disk; writes ``paper_build.json``
with the digests of every input and the literal inventory's counts.

``--render`` then renders the draft to HTML with pandoc (citeproc, MathML) and to PDF with headless Chrome at
Letter 11 pt single column, once in full and once for the main text alone (the abstract to the availability
statement, bibliography suppressed), and reports the page counts with ``pdfinfo`` (guide Part G, 2026-10-06).

Usage:  .venv/bin/python research/paper/assemble.py [--render] [--version v0.1]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import fill_paper  # noqa: E402
import literals  # noqa: E402

SECTIONS = HERE / "sections"
TABLES = HERE / "tables"
FIGURES = HERE / "figures"
TITLE = "Key-conditional false-positive rates of LLM watermark detectors: dispersion identities, a systematic measurement on open corpora, per-key calibration and its power cost"
AUTHOR = "Yichen Zhao (Independent Researcher; alexyczhao@gmail.com)"   # P1 (Yichen, 2026-10-21 UTC): name, affiliation and email on the title page
MAIN_FILES = ["01_introduction.md", "02_related_work.md", "03_theory.md", "04_studies.md", "05_dispersion.md", "06_remedies.md", "07_power.md", "08_discussion.md"]
STATEMENT_FILES = ["09_ai_use.md", "10_availability.md"]
APPENDIX_FILES = ["11_appendix_A.md", "12_appendix_B.md", "13_appendix_C.md", "14_appendix_D.md", "15_appendix_E.md"]
APPENDIX_TABLE_OVERRIDE = {"table3_predictor": "D1", "table2_deployer": "D14", "table5_transfer": "D15"}   # O5 moved the predictor-by-block table to Appendix D as its first item; O9 the deployer and transfer tables
# the supplements the main text and its captions promise, each with a substring its table must carry (a semantic check, R12 F6)
PROMISES = [("D12a", ["Qwen2.5", "[crossed 95% CI]", "Worst sampled key"]), ("D12b", ["Qwen2.5", "[crossed 95% CI]"]),
            ("D8b", ["| 2 |"]), ("D13a", ["| raw |", "| 2 |", "English–other"]), ("D13b", ["kgw", "Ordered pairs"]), ("D13c", ["Inconsistent", "Unresolved"]),
            ("D2b", ["predicted corr.", "observed corr."]), ("D7b", ["corr(ℓ_k, π_k)", "conformal"]), ("D6a", ["unresolved"]), ("D7", ["conformal"]),
            ("D10a", ["N_cal"]), ("D10b", ["abstain"]), ("D10d", ["abstain"]), ("D9a", ["rep-4"]), ("D11", ["max/min"])]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CSS = """
@page { size: Letter; margin: 1in; }
html { font-size: 11pt; }
body { font-family: "Times New Roman", "Liberation Serif", serif; line-height: 1.3; width: 6.5in; margin: 0 auto; color: #000; }
h1 { font-size: 15pt; margin: 1.1em 0 0.4em; } h2 { font-size: 12pt; margin: 0.9em 0 0.3em; } h3 { font-size: 11pt; }
header h1.title { font-size: 17pt; text-align: center; margin-top: 0; } p.author, p.date { text-align: center; margin: 0.2em 0; }
div.abstract { margin: 1em 2em; font-size: 10pt; } div.abstract-title { font-weight: bold; text-align: center; }
p { margin: 0 0 0.55em; text-align: justify; }
table { table-layout: fixed; width: 100%; border-collapse: collapse; font-size: 7.5pt; margin: 0.6em 0 1em; }
th, td { border-top: 1px solid #999; border-bottom: 1px solid #999; padding: 1.5pt 2.5pt; vertical-align: top; overflow-wrap: anywhere; word-break: break-word; }
thead th { border-bottom: 1.5px solid #000; }
img { max-width: 100%; height: auto; display: block; margin: 0.4em auto; }
figure { margin: 0.6em 0 1em; } figcaption { font-size: 9pt; text-align: justify; margin-top: 0.3em; }
p.table-caption { font-size: 9pt; text-align: justify; margin-bottom: 0.2em; }
div#refs p, div.csl-entry { font-size: 9.5pt; text-align: left; overflow-wrap: anywhere; word-break: break-word; }
a { overflow-wrap: anywhere; word-break: break-word; }
div.table-caption p { font-size: 9pt; text-align: justify; margin-bottom: 0.2em; }
code { font-family: "Courier New", monospace; font-size: 0.85em; overflow-wrap: anywhere; }
.math { font-size: 0.95em; }
"""


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def split_open_items(text: str) -> tuple[str, str]:
    m = re.search(r"^##+\s*Open items\s*$", text, re.M)
    if not m:
        return text.rstrip() + "\n", ""
    return text[: m.start()].rstrip() + "\n", text[m.end():].strip()


RENUM = None   # set in main(): the prose's main-text table numbers -> the sequential numbers


def table_block(name: str, number: str, is_main: bool) -> str:
    raw = (TABLES / f"{name}.md").read_text(encoding="utf-8").strip()
    first, _, rest = raw.partition("\n")
    m = re.match(r"^(?:Table — |\*\*Table [A-Z]?\d*\.\*\* )(.*)$", first)
    assert m, (name, first[:60])
    caption = RENUM(m.group(1).strip()) if (RENUM and is_main) else m.group(1).strip()   # the extracted appendix tables quote the reports' own table numbers
    return f"\n::: {{.table-caption}}\n**Table {number}.** {caption}\n:::\n\n{rest.strip()}\n"   # the blank line keeps the fence out of the preceding paragraph (R12 F23)


def figure_block(name: str, number: str, caption: str) -> str:
    assert (FIGURES / f"{name}.png").exists(), name
    return f"![**Figure {number}.** {caption}](figures/{name}.png)\n"


def process(text: str, is_main: bool, counters: dict, floats: dict) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        m = re.match(r"^<<TABLE:([A-Za-z0-9_]+)>>$", s)
        f = re.match(r"^<<FIG:([A-Za-z0-9_]+)>>$", s)
        if m:
            name = m.group(1)
            if is_main:
                counters["table"] += 1; number = str(counters["table"])
                file_no = re.match(r"table(\d+)_", name).group(1)
                assert counters["table_map"][file_no] == number, (name, number)
            else:
                number = APPENDIX_TABLE_OVERRIDE.get(name) or re.match(r"table([A-E]\d*[a-d]?)_", name).group(1)
                number = number if re.search(r"\d", number) else number + "1"   # tableE_reviews -> E1
            floats["tables"][number] = name
            out.append(table_block(name, number, is_main)); i += 1; continue
        if f:
            name = f.group(1)
            caption = ""
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("Figure — "):
                caption = lines[i + 1].strip()[len("Figure — "):]; i += 1
            assert caption, f"figure {name} has no caption line"
            if is_main:
                counters["figure"] += 1; number = str(counters["figure"])
                assert name.startswith(f"fig{number}_"), f"main figure {name} would be numbered {number}"
            else:
                number = re.match(r"fig([A-E]\d+)_", name).group(1)
            floats["figures"][number] = name
            out.append(figure_block(name, number, caption)); i += 1; continue
        out.append(lines[i]); i += 1
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--version", default="v0.1")
    ap.add_argument("--date-line", default=None, help="the title block's date line (default: 'Draft <version>, <build date>'; the publication build names the site)")
    args = ap.parse_args()
    used: dict[str, set[str]] = {}; errors: list[str] = []
    filled: dict[str, str] = {}; open_items: dict[str, str] = {}
    for f in sorted(SECTIONS.glob("*.md")):
        text = fill_paper.fill_text(f.read_text(encoding="utf-8"), used, errors, f.name)
        body, items = split_open_items(text)
        filled[f.name] = body; open_items[f.name] = items
    if errors:
        print("UNRESOLVED:", *errors, sep="\n  "); return 1
    # the main-text tables are numbered sequentially in order of appearance; the prose references them by the file numbers
    # (O5 moved Table 3 to Appendix D), so the file-number -> sequential map is built from the markers and applied first
    global RENUM
    tmap: dict[str, str] = {}
    for f in MAIN_FILES:
        for m in re.finditer(r"^<<TABLE:table(\d+)_", filled[f], re.M):
            tmap[m.group(1)] = str(len(tmap) + 1)
    TABLE_REF = re.compile(r"\bTables?((?:\s*(?:,|and|–|-)?\s*\d+\b)+)")   # 'Table 4', 'Tables 2 and 5', 'Tables 1–3'
    def renum(text: str) -> str:
        def sub(m: re.Match) -> str:
            def one(n: re.Match) -> str:
                assert n.group(0) in tmap, f"'Table {n.group(0)}' referenced but no main-text table file is numbered {n.group(0)}"
                return tmap[n.group(0)]
            return m.group(0)[: m.start(1) - m.start(0)] + re.sub(r"\d+", one, m.group(1))
        return TABLE_REF.sub(sub, text)
    RENUM = renum
    filled = {k: renum(v) for k, v in filled.items()}
    counters = {"table": 0, "figure": 0, "table_map": tmap}; floats = {"tables": {}, "figures": {}}
    abstract = filled["00_abstract.md"].split("\n", 1)[1].strip()
    parts = [process(filled[f], True, counters, floats) for f in MAIN_FILES]
    stmts = [process(filled[f], False, counters, floats) for f in STATEMENT_FILES]
    apps = [process(filled[f], False, counters, floats) for f in APPENDIX_FILES]
    main_md = "\n\n".join(parts); stmt_md = "\n\n".join(stmts); app_md = "\n\n".join(apps)
    refs_md = "# References\n\n::: {#refs}\n:::\n"
    build_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    date_line = args.date_line or f"Draft {args.version}, {build_date}"
    yaml = (f"---\ntitle: \"{TITLE}\"\nauthor: \"{AUTHOR}\"\ndate: \"{date_line}\"\nbibliography: references.bib\n"
            f"link-citations: true\nabstract: |\n" + "".join("  " + ln + "\n" for ln in abstract.splitlines()) + "---\n\n")
    full = yaml + main_md + "\n\n" + stmt_md + "\n\n" + refs_md + "\n" + app_md + "\n"
    # --- checks --------------------------------------------------------------------------------------------------
    bib = (HERE / "references.bib").read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"^@\w+\{([^,]+),", bib, re.M))
    body_text = main_md + stmt_md + app_md
    cited = set(re.findall(r"(?<![\w/@.])@([A-Za-z][A-Za-z0-9]*)", body_text))   # not the '@' of a cell label such as news/en@256 or source/language@L
    problems = []
    if cited - bib_keys: problems.append(f"cited without an entry: {sorted(cited - bib_keys)}")
    if bib_keys - cited: problems.append(f"entries never cited: {sorted(bib_keys - cited)}")
    for pat, what in ((r"\[\[[a-z0-9_]+:", "placeholder"), (r"<<(?:TABLE|FIG):", "marker"), (r"/Users/", "absolute path"), (r"watermark-key-validity-lab", "the private folder's name")):
        if re.search(pat, full): problems.append(f"a {what} survives in the draft")
    # the float references are checked in the sections' own prose and captions (the extracted appendix tables quote the reports' table numbers)
    prose = "\n".join(filled[f] for f in MAIN_FILES + STATEMENT_FILES + APPENDIX_FILES)
    main_tables = {int(k) for k in floats["tables"] if k.isdigit()}; main_figs = {int(k) for k in floats["figures"] if k.isdigit()}
    for n in {int(x) for m in TABLE_REF.finditer(prose) for x in re.findall(r"\d+", m.group(1))}:
        if n not in main_tables: problems.append(f"'Table {n}' referenced but there is no main-text table {n}")
    for n in set(map(int, re.findall(r"\bFigure (\d+)\b", prose))):
        if n not in main_figs: problems.append(f"'Figure {n}' referenced but there is no main-text figure {n}")
    for ref in set(re.findall(r"\b(?:Table|Appendix) ([B-E]\d+[a-d]?)\b", prose)):
        if ref not in floats["tables"] and not any(t.startswith(ref) for t in floats["tables"]): problems.append(f"'Table/Appendix {ref}' referenced but no appendix table {ref}")
    for ref in set(re.findall(r"\bFigure (D\d+)\b", prose)):
        if ref not in floats["figures"]: problems.append(f"'Figure {ref}' referenced but no appendix figure {ref}")
    # section and appendix references resolve to a heading or a labelled paragraph; sub-table references name the sub-table
    headings = set(re.findall(r"^#\s+(\d+)\s", prose, re.M)) | set(re.findall(r"^##\s+(\d+\.\d+)\s", prose, re.M))
    for ref in set(re.findall(r"§\s*(\d+(?:\.\d+)?)", prose)):
        if ref not in headings: problems.append(f"'§{ref}' referenced but no heading is numbered {ref}")
    labels = set(re.findall(r"^\*\*([A-E]\.\d+)\s", prose, re.M))
    for ref in set(re.findall(r"\bAppendix ([A-E]\.\d+)\b", prose)):
        if ref not in labels: problems.append(f"'Appendix {ref}' referenced but no paragraph is labelled {ref}")
    for ref in set(re.findall(r"\bTable (D\d+)\b(?![a-d])", prose)):
        subs = [k for k in floats["tables"] if re.fullmatch(ref + r"[a-d]", k)]
        if subs and ref not in floats["tables"]: problems.append(f"'Table {ref}' is ambiguous: the item has the sub-tables {subs}")
    for tid, needs in PROMISES:
        if tid not in floats["tables"]: problems.append(f"the promised supplement Table {tid} does not exist"); continue
        body = (TABLES / f"{floats['tables'][tid]}.md").read_text(encoding="utf-8")
        for s in needs:
            if s not in body: problems.append(f"Table {tid} does not carry the promised content {s!r}")
    # the literal scan: no recognised numeral or counting word outside a placeholder without a grid check, an algebraic status or an allow-listed reason (R12 F7, F15, F22; a syntactic check)
    lit = literals.scan_files(sorted(SECTIONS.glob("*.md")))
    lit_summary = literals.summary(lit)
    pv = json.loads((HERE / "paper_values.json").read_text(encoding="utf-8"))
    for k, v in (("r_n_literals", lit_summary["n_literals"]), ("r_n_literals_grid", lit_summary["n_settings_checked_against_grids"]), ("r_n_literals_allowlisted", lit_summary["n_allowlisted"]), ("r_n_literals_algebraic", lit_summary["n_algebraic"]), ("r_n_literals_math", lit_summary["n_math"]), ("r_n_literals_set_aside", lit_summary["n_set_aside"]), ("r_n_placeholders", sum(len(fill_paper.PLACEHOLDER.findall(f.read_text(encoding="utf-8"))) for f in sorted(SECTIONS.glob("*.md"))))):
        if pv.get(k) != v: problems.append(f"the register's {k} = {pv.get(k)!r} is stale (the scan gives {v}); re-run reviews_table.py")
    for x in lit:
        if x["status"] == "UNALLOWED": problems.append(f"typed literal {x['text']!r} in {x['file']}:{x['line']} ({x.get('reason') or x['context'][:80]})")
    locks = {s: sha(ROOT / d / "PRE_RUN_LOCK.json")[:12] for s, d in fill_paper.STUDY_DIRS.items()}
    e2 = (TABLES / "tableE2_locks.md").read_text(encoding="utf-8")
    for s, dg in locks.items():
        if f"`{dg}`" not in e2: problems.append(f"Table E2 does not carry the current lock digest of {s} ({dg})")
    if problems:
        print("ASSEMBLY CHECKS FAILED:", *problems, sep="\n  "); return 1
    # --- write ----------------------------------------------------------------------------------------------------
    draft = HERE / f"PAPER_DRAFT_{args.version}.md"; draft.write_text(full, encoding="utf-8")
    items_md = [f"# Open items collected at assembly ({args.version}, {build_date})\n", "Every section's \"Open items\" block, verbatim, in section order; the assembled draft carries none of them.\n"]
    for f, items in open_items.items():
        if items: items_md.append(f"## {f}\n\n{items}\n")
    (HERE / f"PAPER_OPEN_ITEMS_{args.version}.md").write_text("\n".join(items_md), encoding="utf-8")
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in sorted(list(SECTIONS.glob("*.md")) + list(TABLES.glob("*.md")) + [HERE / "references.bib"] + sorted(FIGURES.glob("*.png")))}
    build = {"version": args.version, "built_utc": build_date, "title": TITLE, "sections": [f for f in filled], "main_tables": {k: v for k, v in floats["tables"].items() if k.isdigit()},
             "main_figures": {k: v for k, v in floats["figures"].items() if k.isdigit()}, "appendix_tables": {k: v for k, v in floats["tables"].items() if not k.isdigit()},
             "appendix_figures": {k: v for k, v in floats["figures"].items() if not k.isdigit()}, "placeholders_used": {k: len(v) for k, v in used.items()},
             "citations": len(cited), "literals": lit_summary, "headings": sorted(headings), "inputs_sha256": inputs, "draft_sha256": sha(draft)}
    print(f"wrote {draft.name}: {len(main_tables)} main tables, {len(main_figs)} main figures, {len(floats['tables']) - len(main_tables)} appendix tables, {len(floats['figures']) - len(main_figs)} appendix figures, {len(cited)} citation keys; open items from {sum(1 for v in open_items.values() if v)} sections")
    if not args.render:
        (HERE / "paper_build.json").write_text(json.dumps(build, indent=1, sort_keys=True) + "\n", encoding="utf-8"); return 0
    # --- render -----------------------------------------------------------------------------------------------------
    out = HERE / "render"; out.mkdir(exist_ok=True)
    (out / "paper.css").write_text(CSS, encoding="utf-8")
    if (out / "figures").exists(): shutil.rmtree(out / "figures")
    shutil.copytree(FIGURES, out / "figures", ignore=shutil.ignore_patterns("*.py", "*.svg", "*.json"))
    yaml_nobib = yaml.replace("bibliography: references.bib\n", "bibliography: references.bib\nsuppress-bibliography: true\n")
    strip_figs = lambda md: re.sub(r"^!\[.*?\]\(figures/[^)]+\)\s*$", "", md, flags=re.M)
    strip_tabs = lambda md: re.sub(r"^(?:::: \{\.table-caption\}|\*\*Table [A-E]?\d+[a-d]?\.\*\*.*|:::|\|.*)\s*$", "", md, flags=re.M)
    variants = (("full", full),
                ("main", yaml_nobib + main_md + "\n"),                                   # the abstract and sections 1-8: the budget's count
                ("main_with_statements", yaml_nobib + main_md + "\n\n" + stmt_md + "\n"),
                ("main_no_figures", yaml_nobib + strip_figs(main_md) + "\n"),
                ("main_no_tables", yaml_nobib + strip_tabs(main_md) + "\n"),
                ("main_prose_only", yaml_nobib + strip_tabs(strip_figs(main_md)) + "\n"))
    # the absolute scale: a one-paragraph page in the same stylesheet gives the unshrunk word height. A wide element that every
    # variant shares (the one-line variance display of §3.3 did, until the LaTeX conversion of 2026-10-21) shrinks every variant
    # alike, which the across-variant check cannot see; every variant must also match this reference.
    ref_html = out / "paper_scale_reference.html"; ref_pdf = out / "paper_scale_reference.pdf"
    ref_html.write_text('<!DOCTYPE html><html><head><meta charset="utf-8"><link rel="stylesheet" href="paper.css"></head><body><p>The deployer holds one key.</p></body></html>', encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={ref_pdf}", f"file://{ref_html}"], check=True, capture_output=True, cwd=out)
    bbox = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-bbox", str(ref_pdf), "-"], capture_output=True, text=True).stdout
    word = re.search(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">deployer</word>', bbox)
    nominal = round(float(word.group(4)) - float(word.group(2)), 2)
    pages = {}
    for label, md in variants:
        src = out / f"paper_{label}.md"; src.write_text(md, encoding="utf-8")
        html = out / f"paper_{label}.html"; pdf = out / f"paper_{label}.pdf"
        subprocess.run(["pandoc", str(src), "-f", "markdown", "-t", "html5", "--standalone", "--citeproc", "--mathml", "--css", "paper.css",
                        "--bibliography", str(HERE / "references.bib"), "--resource-path", str(out), "-o", str(html)], check=True, cwd=out)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", f"file://{html}"], check=True, capture_output=True, cwd=out)
        html_text = html.read_text(encoding="utf-8")
        n_divs = html_text.count('<div class="table-caption">'); n_tables = html_text.count("<table>") + html_text.count("<table ")
        if n_divs != n_tables or ":::" in re.sub(r"<[^>]+>", "", html_text):
            print(f"RENDER CAPTION CHECK FAILED ({label}): {n_divs} caption divs for {n_tables} tables, or a literal fence in the text"); return 1
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
        pages[label] = int(re.search(r"Pages:\s+(\d+)", info).group(1))
        layout = subprocess.run(["pdftotext", "-layout", "-l", "3", str(pdf), "-"], capture_output=True, text=True).stdout.splitlines()
        widths = [len(ln) for ln in layout if len(ln) > 40]
        pages[label + "_median_line_chars"] = sorted(widths)[len(widths) // 2] if widths else None
        # the physical scale: Chrome shrinks the whole document to fit its widest element (a long URL did, R12 F21); a word's box height
        bbox = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-bbox", str(pdf), "-"], capture_output=True, text=True).stdout
        word = re.search(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">deployer</word>', bbox)
        pages[label + "_word_height_pt"] = round(float(word.group(4)) - float(word.group(2)), 2) if word else None
    heights = {k: v for k, v in pages.items() if k.endswith("_word_height_pt")}
    ref = heights["main_word_height_pt"]
    if any(v is None or abs(v - ref) > 0.02 * ref for v in heights.values()):
        print("RENDER SCALE CHECK FAILED: the variants' body scales differ (a page-widening element shrinks a document):", heights); return 1
    if any(abs(v - nominal) > 0.02 * nominal for v in heights.values()):
        print(f"RENDER SCALE CHECK FAILED: a variant is shrunk against the unshrunk reference of {nominal} pt (a page-widening element shared by every variant):", heights); return 1
    # where the full PDF's parts begin (read on the page, never subtracted across differently scaled renders)
    full_pdf = out / "paper_full.pdf"; n_full = pages["full"]; starts = {}
    for i in range(1, n_full + 1):
        txt = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), str(full_pdf), "-"], capture_output=True, text=True).stdout
        for key, pat in (("statements", r"^AI use and independent review$"), ("references", r"^References$"), ("appendices", r"^Appendix A ")):
            if key not in starts and re.search(pat, txt, re.M): starts[key] = i
    assert set(starts) == {"statements", "references", "appendices"}, starts
    build["render"] = {"pages_full": pages["full"], "pages_main_text_abstract_to_section_8": pages["main"], "pages_main_with_statements": pages["main_with_statements"],
                       "pages_main_no_figures": pages["main_no_figures"], "pages_main_no_tables": pages["main_no_tables"], "pages_main_prose_only": pages["main_prose_only"],
                       "full_pdf_first_page_of": starts, "pages_full_references_and_appendices": n_full - starts["references"] + 1, "pages_full_appendices": n_full - starts["appendices"] + 1,
                       "median_line_chars_full": pages["full_median_line_chars"], "median_line_chars_main": pages["main_median_line_chars"],
                       "body_word_height_pt": heights, "body_word_height_nominal_pt": nominal, "page": "Letter, 1 in margins, 11 pt, single column; Chrome headless print; the body scale asserted equal across the variants and equal to a one-paragraph reference page's, by a word's bounding box"}
    (HERE / "paper_build.json").write_text(json.dumps(build, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"rendered: full {pages['full']} pages (the statements from page {starts['statements']}, the references from {starts['references']}, the appendices from {starts['appendices']}; body scale {ref} pt on every variant, the unshrunk reference {nominal} pt); main text (the abstract and sections 1-8, no bibliography) {pages['main']} pages "
          f"(with the two statements {pages['main_with_statements']}; without figures {pages['main_no_figures']}; without tables {pages['main_no_tables']}; prose only {pages['main_prose_only']}); "
          f"median line width {pages['main_median_line_chars']} characters (about 90–120 expected at 11 pt)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
