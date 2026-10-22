# Key-conditional false-positive rates of LLM watermark detectors: dispersion identities, a systematic measurement on open corpora, per-key calibration and its power cost

Public snapshot of the research repository behind the paper (Yichen Zhao, independent researcher, 2026). It holds the
four pre-registered protocols with their lock files, the validation records, run manifests and the locked analysers'
results, the per-text records of every study, every script that generated a number, table or figure in the paper, the
paper's sources, the review prompts, memos and resolutions of the thirteen independent-review checkpoints, the source and
claim gates, and the decision log that records each decision in order. It holds **no corpus text, no model weights, no
literature PDFs and none of the third-party pages, READMEs or extracted texts the literature screens captured**: the first
three were git-ignored throughout and the captures stay in the private record (the screens' memos list every query and
quotation); the bibliography's records under `research/paper/bib_sources/` are the arXiv API's metadata (CC0) and
projections of the Crossref and GitHub API responses to their provenance fields (no diff body of a cited commit, no
publisher's abstract; the full responses stay in the private record), and the hashed manifests let a rebuild be checked.

**Paper page:** https://shenshenzyc.github.io/watermark-key-validity/ (the PDF, an HTML version and this repository; served from `docs/`).

## What is where
| Path | Contents |
|---|---|
| `research/STUDY<n>_PROTOCOL_v*.md` | The four pre-registered protocols (locked by hash before any outcome; `LOCKED` in their status line) |
| `outputs/study<n>_v*/` | `PRE_RUN_LOCK.json` (the hashes of the protocol, the pinned code and the inputs, the commit, the "no outcomes" statement), `VALIDATION.json`, `INPUTS.json`, `RUN_MANIFEST.json`, `results.json` (Study 3's as `results.json.gz`), the record `cells/`, the run logs, `report/` (the generated tables, figures and checks) |
| `research/study<n>/` | The locked code (runner, analyser, validator, core; the runners refuse to start without the lock), the grid, the report builder and its prose source, the fixture generator, the pre-lock re-screen |
| `research/STUDY<n>_REPORT_v0.1.md` | The generated reports (never edited by hand) |
| `research/corpora/`, `outputs/corpora_*`, `DATA_LAYOUT.md`, `tools/` | The terms-of-use check, the data audit (v0.3 current), the freeze and build scripts, the hashed manifests (counts, digests, the holdout identifiers; no text), the sealed access layer |
| `research/paper/` | The paper: `sections/` (one file per section, every number a placeholder), `tables/` and `figures/` (one script each, reading the locked outputs and asserting against the reports), `fill_paper.py`, `literals.py`, `assemble.py`, `make_latex.py`, `latex/` (the LaTeX source and the PDF), `references.bib` with `bib_sources/`, `PAPER_DRAFT_v0.1.md` |
| `research/reviews/` | The orientation for the reviewer and, per checkpoint R01–R13, the prompt, the reviewer's memos, the conductor's responses and the resolution |
| `research/KEYCOND_GATE_v*.md`, `research/CLAIM_GATE_v0.1.md`, `research/FINAL_GATE_v0.1.md`, `research/TOPIC_SCREEN_v0.1.md`, `research/PROJECT_BRIEF.md` | The source gates, the claim gate, the final gate, the topic screen and the brief |
| `research/DECISION_LOG.md` | Every decision, result and correction, dated, in order |
| `docs/` | The paper page (built by `tools/make_site.py`: `index.html`, `paper.pdf`, `paper.html` with `figures/`) |

## Rebuilding
1. Python 3.12 (`requirements-lock.txt`) with PyTorch (MPS or CUDA) and `transformers`; the pinned model revisions are in the token and model manifests under `outputs/` (Llama 3.2 is gated on Hugging Face; accept its licence there).
2. The corpora: `tools/freeze_corpora.py` downloads the pinned Hub files named in `outputs/corpora_manifest_v0.1.json` and checks their SHA-256 against the manifest; `tools/corpora_build.py` rebuilds the units; the holdout stays sealed (`tools/corpora_access.py`; no lock in the paper is final).
3. A study: its runner under `research/study<n>/` verifies every hash in its `PRE_RUN_LOCK.json` first. Run times on one Apple M5 laptop are in the run manifests (1 to 12 hours).
4. The paper: the scripts under `research/paper/tables/` and `research/paper/figures/`, then `fill_paper.py --check`, `assemble.py --render` (pandoc and headless Chrome) and `make_latex.py` (pandoc and Tectonic).

## Licences
Code (every `.py` file and the scripts) is under the MIT licence (`LICENSE`). The text of the protocols, reports, gates, the
decision log and the paper, and the figures, are under CC BY 4.0 (`LICENSE-TEXT`). Third-party materials are not
included: the models are used under their own licences (Qwen2.5 Apache-2.0; Llama 3.2 Community Licence, tokenizer only),
the null corpora are the Common Pile v0.1 subsets (per-document licence strings recorded per unit) and the Wikimedia dumps
of 2023-11-01 (CC BY-SA 3.0 / GFDL), neither redistributed here, and the papers read are listed with their licences in
`research/FINAL_GATE_v0.1.md` (§7), whose rights table also covers the bibliography's primary records under
`research/paper/bib_sources/` (arXiv API metadata under CC0; the Crossref and GitHub API records projected to their
provenance fields, without the diff bodies of the cited commits and the publishers' abstracts).

## Use of AI tools
The prose and the code were drafted by Claude (Anthropic) in Claude Code under the author's instruction and section-level
review, and every major checkpoint was reviewed by an independent second model, Codex (OpenAI), before the project proceeded
(the memos are under `research/reviews/`); the author took every design, lock, wording and publication decision, read every
word, and takes full responsibility. No AI system is an author.

## Citing
See `CITATION.cff`. The paper is published at https://shenshenzyc.github.io/watermark-key-validity/ (a self-published preprint); cite it by that URL and this repository.

## About this snapshot
Built by `tools/make_public_snapshot.py` from the working repository at the commit named in `SNAPSHOT_MANIFEST.json`
(every file's SHA-256 is listed there). The session briefing, the model instructions and the project's Claude skills are
not included, nor are the claim gate's raw captures of third-party pages (`research/claim_gate/raw_*`) or the full API
responses behind the bibliography (`research/paper/bib_sources/raw_responses/`, of which the distributed records are
projections, each with a `_projection` note); the local paths of
the working machine were generalised to `<repository>`, `<projects>` and `<home>` in every file except the records whose
SHA-256 a lock or run manifest pins, which are byte-identical to the working repository's and so carry the working
folder's path verbatim (both lists are in `SNAPSHOT_MANIFEST.json`); nothing else was edited.
