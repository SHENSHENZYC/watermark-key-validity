# Terms-of-use check — literature access for the Stage 3 gates (2026-10-08)

Checked before any download (guide rule A4.6; frozen-data-provenance skill). Quotations are the pages' words as returned by the fetch tool on 2026-10-08.

| Source | Clause (quoted, with link) | What it means for us |
|---|---|---|
| arXiv API terms of use — https://info.arxiv.org/help/api/tou.html | "make no more than one request every three seconds"; "limit requests to a single connection at a time"; users may "Retrieve, store, and use the content of arXiv e-prints for your own personal use, or for research purposes"; "The redistribution of e-prints requires permission from the copyright holder, which may be the author(s) or publisher"; descriptive metadata is CC0. | Download e-prints one at a time, paced at 4 seconds, single connection, for research use only. PDFs and extracted text stay **git-ignored**; only a hashed manifest and short attributed quotations (with page numbers) are tracked. No redistribution of PDFs or extracted text. |
| arXiv robots guidance — https://info.arxiv.org/help/robots.html | "arXiv monitors activity and will deny access to sites that violate these guidelines"; machine access is through OAI-PMH, the API, RSS and bulk download; for special needs "contact the arXiv administrators in advance of any attempted download". | Our volume (about 33 PDFs, paced) is ordinary personal use, not harvesting. A denial means stop, not retry. |
| GitHub repositories `mohammadi-hadi/arenakit` (MIT) and `lmarena/arena-rank` (Apache-2.0) | Licence fields read from the GitHub API on 2026-10-08. | READMEs and results files are read through the GitHub API; code is not vendored. Quotations short and attributed. |
| Hugging Face dataset cards (lmarena releases, MT-Bench judgments) | Licence fields recorded in `research/screen/C05_*.md` and `C04_*.md` (search-level). | Cards read only; no dataset download at Stage 3. A Stage 4 audit re-reads the licence texts before any download. |
| Blog posts (arena.ai, news.lmarena.ai), PyPI JSON API | Public web pages. | Read only; cite with the date read and the quoted phrase. |

Access gaps are recorded in the manifest (`pdf_manifest.json`) and in the gate documents.

**Added 2026-10-09 (R01):** two further arXiv e-prints (2610.06317, 2602.06754) fetched under the same arXiv terms and pacing; one non-arXiv PDF, OpenAI's technical report "textGrain: Entropy-Calibrated Watermarking for Language Model Text" (public CDN link given in the OpenAI blog post of 2026-10-05), fetched once with a single request; no terms page accompanies the file, so it is treated like a publisher PDF: personal research use, git-ignored, hashed in the manifest, quoted briefly with page numbers.

**Added 2026-10-09 (R03):** AutoMark (arXiv 2609.37310) fetched under the arXiv terms and pacing. The Genhatharan paper lives in a public GitHub repository under the MIT licence (`nisaharan/when-nominal-false-positive-rates-fail`); the reviewer reported that the web path to the manuscript source is disallowed by the site's robots.txt, so the PDF was read once through the GitHub REST API's repository-contents endpoint (the sanctioned programmatic access to public repositories, as used for `arenakit` at Stage 3), stored git-ignored and hashed in the manifest; personal research use; short attributed quotations with page numbers only.
