#!/usr/bin/env python3
"""Build the GitHub Pages site for the paper (Stage 9; the site is the publication of record, decision P1, 2026-10-21).

Writes docs/ (git-ignored in the working repository; copied into the public snapshot by tools/make_public_snapshot.py and
served by GitHub Pages from the snapshot repository's main branch, /docs):
  index.html   the paper page: title, author, date, links (PDF, HTML version, code), the abstract (from the filled
               abstract section, citations resolved against references.bib), what the repository holds, a BibTeX block,
               the licences and the AI-use disclosure; Google Scholar's citation_* meta tags
  paper.pdf    the paper as typeset (research/paper/latex/main.pdf)
  paper.html   the HTML render (research/paper/render/paper_full.html) with its figures under figures/ and its stylesheet
  figures/     the figure PNGs of the render
  .nojekyll    so that GitHub Pages serves the files as they are
Run: .venv/bin/python tools/make_site.py [--published YYYY-MM-DD]   (without --published the page says it is a
pre-publication build; the publication build names the date and the posting tag)
"""
from __future__ import annotations

import datetime as dt
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "research" / "paper"
DOCS = ROOT / "docs"
REPO_URL = "https://github.com/SHENSHENZYC/watermark-key-validity"
SITE_URL = "https://shenshenzyc.github.io/watermark-key-validity/"
PUBLISHED = None
if "--published" in sys.argv:
    PUBLISHED = sys.argv[sys.argv.index("--published") + 1]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", PUBLISHED), PUBLISHED

asm = (PAPER / "assemble.py").read_text(encoding="utf-8")
TITLE = re.search(r'^TITLE = "(.*)"$', asm, re.M).group(1)
AUTHOR_RAW = re.search(r'^AUTHOR = "(.*?)"', asm, re.M).group(1)
m = re.match(r"(.*?) \((.*?); (.*?)\)$", AUTHOR_RAW)
AUTHOR, AFFIL, EMAIL = (m.group(1), m.group(2), m.group(3)) if m else (AUTHOR_RAW, "", "")
YEAR = "2026"
TODAY = dt.date.today().strftime("%-d %B %Y")

# --- the abstract, from the filled section, citations resolved
abs_src = PAPER / "filled" / "00_abstract.md"
assert abs_src.exists(), "run research/paper/assemble.py first (it fills the sections)"
abs_md = abs_src.read_text(encoding="utf-8").split("## Open items")[0].split("\n", 1)[1].strip()
abs_html = subprocess.run(["pandoc", "-f", "markdown", "-t", "html", "--citeproc", "--mathml", "--bibliography", str(PAPER / "references.bib"),
                           "--metadata", "suppress-bibliography=true", "--metadata", "link-citations=false"],
                          input=abs_md, text=True, capture_output=True, check=True).stdout.strip()
assert "[[" not in abs_html and "@" not in re.sub(r"<[^>]+>", "", abs_html).replace("@gmail", ""), "an unresolved placeholder or citation in the abstract"

# --- files
if DOCS.exists():
    shutil.rmtree(DOCS)
(DOCS / "figures").mkdir(parents=True)
shutil.copy(PAPER / "latex" / "main.pdf", DOCS / "paper.pdf")
shutil.copy(PAPER / "render" / "paper.css", DOCS / "paper.css")
n_fig = 0
for p in sorted((PAPER / "render" / "figures").glob("*.png")):
    shutil.copy(p, DOCS / "figures" / p.name); n_fig += 1
page = (PAPER / "render" / "paper_full.html").read_text(encoding="utf-8")
assert page.count('src="figures/') == n_fig, (page.count('src="figures/'), n_fig)
assert "file://" not in page and "/Users/" not in page, "an absolute local path survived in the HTML version"
(DOCS / "paper.html").write_text(page, encoding="utf-8")
(DOCS / ".nojekyll").write_text("", encoding="utf-8")

# --- BibTeX for the citation box
key = "zhao2026keyconditional"
bibtex = "\n".join([f"@misc{{{key},", "  author = {Zhao, Yichen},", f"  title  = {{{TITLE}}},", f"  year   = {{{YEAR}}},",
                    "  howpublished = {Preprint, self-published},", f"  url    = {{{SITE_URL}}},",
                    f"  note   = {{Code, protocols, locks, records and results: {REPO_URL}}}", "}"])

links = [("Paper (PDF)", "paper.pdf", "primary"), ("HTML version", "paper.html", ""), ("Code, protocols, records and results", REPO_URL, "")]
links_html = "\n".join(f'      <a class="btn {cls}" href="{html.escape(href)}">{html.escape(label)}</a>' for label, href, cls in links)
if PUBLISHED:
    d = dt.date.fromisoformat(PUBLISHED).strftime("%-d %B %Y")
    status_note = f'<p class="note">Published here as a preprint on {d} (UTC); the repository holds the posting commit under the tag <code>v0.1-published</code>.</p>'
    date_meta = PUBLISHED.replace("-", "/")
else:
    status_note = '<p class="note">A pre-publication build of the paper page (not yet published; the publication date is set at the public release).</p>'
    date_meta = YEAR

index = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITLE)}</title>
<meta name="description" content="Paper page: {html.escape(TITLE)} ({html.escape(AUTHOR)}, {YEAR}).">
<meta name="citation_title" content="{html.escape(TITLE)}">
<meta name="citation_author" content="Zhao, Yichen">
<meta name="citation_publication_date" content="{date_meta}">
<meta name="citation_pdf_url" content="{SITE_URL}paper.pdf">
<style>
  :root {{ --bg: #ffffff; --fg: #1a1a1a; --muted: #5a5a5a; --line: #e3e3e3; --accent: #1f4e8c; --accent-fg: #ffffff; --box: #f6f7f9; }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #121417; --fg: #e8e8e8; --muted: #a8a8a8; --line: #2d3138; --accent: #7aa7e0; --accent-fg: #0f1a2b; --box: #1b1f25; }} }}
  :root[data-theme="dark"] {{ --bg: #121417; --fg: #e8e8e8; --muted: #a8a8a8; --line: #2d3138; --accent: #7aa7e0; --accent-fg: #0f1a2b; --box: #1b1f25; }}
  html {{ background: var(--bg); }}
  body {{ margin: 0; padding: 0 16px; background: var(--bg); color: var(--fg); font: 17px/1.55 Georgia, "Times New Roman", serif; }}
  main {{ max-width: 760px; margin: 0 auto; padding: 48px 0 64px; }}
  h1 {{ font-size: 1.7rem; line-height: 1.25; margin: 0 0 12px; font-weight: 600; }}
  .byline {{ color: var(--muted); margin: 0 0 24px; font-size: 1rem; }}
  .links {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 28px; }}
  .btn {{ display: inline-block; padding: 8px 14px; border: 1px solid var(--accent); border-radius: 6px; color: var(--accent); text-decoration: none; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 0.95rem; }}
  .btn.primary {{ background: var(--accent); color: var(--accent-fg); }}
  h2 {{ font-size: 1.15rem; margin: 32px 0 8px; font-weight: 600; letter-spacing: 0.01em; }}
  .abstract p {{ margin: 0 0 12px; text-align: left; }}
  pre {{ background: var(--box); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px; overflow-x: auto; font-size: 0.85rem; line-height: 1.45; }}
  .note, footer {{ color: var(--muted); font-size: 0.9rem; }}
  footer {{ border-top: 1px solid var(--line); margin-top: 40px; padding-top: 16px; }}
  a {{ color: var(--accent); }}
</style>
</head>
<body>
<main>
  <h1>{html.escape(TITLE)}</h1>
  <p class="byline">{html.escape(AUTHOR)}, {html.escape(AFFIL)} &middot; <a href="mailto:{html.escape(EMAIL)}">{html.escape(EMAIL)}</a> &middot; {YEAR}</p>
  <div class="links">
{links_html}
  </div>
  {status_note}
  <h2>Abstract</h2>
  <div class="abstract">
{abs_html}
  </div>
  <h2>What is in the repository</h2>
  <p>The four pre-registered protocols with their lock files (the hashes of the protocol, the pinned code and the inputs, written before any outcome existed), the validation records, run manifests and the locked analysers' results, the per-text records of every study, every script that generated a number, table or figure in the paper, the paper's sources with the placeholder registers and the literal scan, the review prompts, memos and resolutions of the thirteen independent-review checkpoints, the source, claim and final gates, and the decision log. No corpus text, model weights or literature PDFs are included; the hashed manifests let a rebuild be checked. <a href="{REPO_URL}">{REPO_URL}</a></p>
  <h2>Citation</h2>
  <pre>{html.escape(bibtex)}</pre>
  <footer>
    <p>Text and figures under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>; code under the MIT licence. The prose and the code were drafted with Claude (Anthropic) under the author's direction, and every major checkpoint was reviewed by an independent second model, Codex (OpenAI); the author designed the studies, took every decision, read every word and takes full responsibility. Page built {TODAY}.</p>
  </footer>
</main>
</body>
</html>
"""
(DOCS / "index.html").write_text(index, encoding="utf-8")
size = sum(p.stat().st_size for p in DOCS.rglob("*") if p.is_file()) / 1e6
print(f"site written to docs/: index.html ({'published ' + PUBLISHED if PUBLISHED else 'pre-publication build'}), paper.pdf, paper.html, {n_fig} figures, paper.css, .nojekyll; {size:.1f} MB")
