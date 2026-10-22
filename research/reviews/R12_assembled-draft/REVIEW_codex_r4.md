# R12 — assembled draft, round 4

Reviewer: Codex. Date: 2026-10-20 UTC.

## 1. Baseline and scope

Baseline: `main` at **`709109ad0c956950b29b039b9372c00c75986000`**. The working tree was clean at entry. This is the bounded re-review of **F22–F24** authorized by Yichen after round three. The preceding reviews supply the unchanged scientific and source audit; the agreed study outcomes, protocols, claim gate and wording decisions are not reopened.

I read `RESPONSE_claude_r3.md`, including the verification table, dispositions and dated corrections; the revised `literals.py`, its unchanged allow-list and generated inventory; `assemble.py`; the assembled E.2 and its section source; the orientation, including §1; the round-two response's postscript and the decision log's round-three entry; the checkpoint prompt and previous memo. I inspected the diff from the round-three baseline, checked the relevant saved cover-log entry, and examined the regenerated HTML and PDF captions. Independent string probes and inventory checks used the existing scanner without editing it.

All four requested commands completed successfully, using `.venv/bin/python`:

| Command under `research/paper/` | Observed result |
| --- | --- |
| `literals.py --selftest` | Pass: the twelve escape probes and the permitted-conventions control |
| `fill_paper.py --check` | **560** placeholders in 16 files, all resolved; 427 literals: 186 in prose, 241 in formulas; 127 grid-checked, 151 allow-listed, 149 algebraic, 0 unallowed; self-test passes |
| `reviews_table.py` | 11 agreed checkpoints and R12 open; agreed totals remain 33 rounds and 171 findings; R12 has three completed rounds and 24 findings before this memo |
| `assemble.py --render` | All checks pass; 3 main tables, 6 main figures, 38 appendix tables, 7 appendix figures, 50 citation keys; 92 full pages and 18 main-text pages |

Before adding this memo, `git status --short` was empty and `git diff --exit-code` passed. The targeted ignored-path status showed `research/paper/render/` and `research/paper/filled/`. The assembled Markdown is byte-identical to `HEAD`, SHA-256 **`b808e4c92d257291e86fd89368d19fa9c29fb1a15af1c770fb55aeade854b186`**. The saved literal inventory exactly equals the scanner's report plus the final newline written by the fill script.

The prompt and response's **552 placeholders / 1,154 excluded spans** are not the final baseline's counts. The actual **560 / 1,155** are consistently recorded in the current inventory, register, build metadata and E.2. The differences are traced below; they are supporting-record corrections, not changed study results.

## 2. Claims against evidence

### 2.1 F22: the repaired cases and the scope of the check

The four round-three escapes now produce unallowed occurrences: `seventy-five`, an unlabelled `5–95%`, `$.123$`, and `$\text{sixty}$`. The earlier eight cases also pass their regression checks. Reading the implementation confirms the relevant changes: compound cardinals in `WORDS`; the quantile-band exception requiring its labelled phrase; leading-decimal alternatives in both numeral patterns; counting-word and design-`one` scans inside formula spans.

I also called `scan_text(sentence, "00_abstract.md", load_allowlist())` on independent examples:

| Probe | Observed classification |
| --- | --- |
| `There were eighty-seven keys.` | `eighty-seven` unallowed |
| `There were ninety–nine keys.` | `ninety` and `nine` unallowed |
| `We measured .375 of the sampled keys above nominal.` | `.375` unallowed |
| `We measured $.375$ of the sampled keys above nominal.` | `.375` unallowed inside the formula |
| `We counted $\text{twenty-one}$ failures.` | `twenty-one` unallowed inside the formula |
| `We used $\text{one source}$ for calibration.` | `one source` unallowed inside the formula |
| `We measured 1–99% of the sampled keys above nominal.` | `1` and `99%` unallowed |
| `The bands cover 1–99% and 5–95% of the sampled keys; 93% failed.` | The labelled band is inventoried as an excluded convention; `93%` is unallowed |
| `A two-way table compared two datasets.` | `two-way` is an excluded identifier; the separate `two` is unallowed |

The check remains syntactic. For example, `We recorded 1e3 failures.`, `We recorded a billion failures.` and `There was one failure.` yield no occurrences. `Beta(17, 29)` is inventoried as excluded notation, and `$1$` is classified as algebraic even in the sentence `The failure fraction was $1$.` These probes show why manual reading remains necessary; passing the scanner cannot establish the meaning or provenance of every numerical assertion.

E.2 now says the scan classifies the numerals and counting words **“its patterns recognise”**, refuses an unclassified **“recognised literal”**, and states explicitly:

> “a numeral written in a form outside its patterns is not seen by it, and the drafts were read for such cases by the author at the section reviews and by the independent reviewer at the rounds of checkpoint R12.”

This is the material correction to F22. The new probes above do not contradict that qualified statement. The orientation's §1 also calls the check syntactic and limits classification to recognized patterns. It does not itself repeat the manual-reading sentence, and older exhaustive language remains in its paper map and script documentation; F26 identifies that documentation cleanup.

The current inventory reproduces as follows:

| Excluded class | Spans recorded |
| --- | ---: |
| Cross-references | 195 |
| Identifiers | 270 |
| Citation blocks | 106 |
| Labelled quantile conventions | 13 |
| Exponents or subscripts | 84 |
| Placeholders, code spans and markers | 478 |
| Notation | 9 |
| **Total recorded** | **1,155** |

The allow-list still contains **126 rules**, of which **39** have source predicates; all 39 source predicates match. Its 151 matched occurrences and the 127 grid settings and 149 algebraic constants reproduce. The allow-list has no diff from the preceding reviewed baseline. One explicit removal path—the fixed adequacy band—still bypasses the inventory; this limited residual is F25.

### 2.2 F23: every caption now renders as a caption

`table_block()` now emits a leading blank line before the fenced div (`assemble.py:99`). The render also checks the caption-container count against the table count and rejects literal fences in the HTML's text.

I independently parsed the regenerated HTML rather than relying only on that check. The full document contains **41 distinct caption divs and 41 tables**, alternating one caption and one table throughout. The caption labels exactly match the build's table map: **3 main and 38 appendix tables**. This includes every one of the 15 appendix captions that failed in round three. All 41 caption prefixes also occur in the extracted PDF text. Neither the HTML text nor the PDF text contains `:::`. The same checks pass for all six render variants, including the variants containing no tables.

I visually inspected full-PDF p. 66, the previous D12a failure location. The D12 item description and Table D12a caption are separate blocks, the caption has its smaller intended type, and the literal fences are gone. **F23 is closed.**

The full draft remains 92 pages; the main text remains 18, or 19 with the statements. The other variants remain 14 pages without figures, 15 without tables and 12 for prose alone. Independent first-page word-box measurements give **35.005746 × 11.080688 pt** for `deployer` in every variant. The full-PDF boundaries remain statements p. 18, references p. 19 and appendices p. 21. The caption repair has preserved the corrected body scale.

### 2.3 F24: the historical corrections are supported

The postscript on `RESPONSE_claude_r2.md` explicitly withdraws the Common Pile cover claim. The saved `fetch_log.json:138` says **“no local PDF text: the cover was not checked”**; the named local text remains absent. The response correctly leaves the published author order on its separately saved primary-record evidence. No new cover verification is claimed here.

The corrected round-two count of **552** is reproducible: replacing only the current E.2 source with its round-three-baseline predecessor gives 552 placeholders across the sections. The new E.2 adds **eight** placeholders—one total and seven exclusion-class counts—bringing the current total to **560**. Its added `R12` reference also contributes the extra excluded identifier: **269 → 270**, and **1,154 → 1,155** recorded spans. These differences explain the stale round-three narrative totals without any change to a result.

The **126 rules / 151 occurrences** distinction is now explicit, and the orientation's §1 gives **18 / 92** pages. F24's historical corrections are accepted. F26 covers the final-build summaries that were not updated after the last E.2 edits.

## 3. Method and statistics

No statistical design, estimand, rule, tolerance, reported outcome or power claim changes in this bounded correction. The important methodological boundary is now explicit: the literal checker validates recognized syntax and registered constants; the source review supplies the semantic check. It cannot infer that a number inside a formula is a result rather than algebra, or that a numeric string excluded as notation is scientifically appropriate.

The independent probes support the specified scanner repairs and the need for the new limitation statement. The seven unlisted band occurrences all denote the fixed adequacy band already checked in the earlier reviews. `allowed_values()` also asserts the corresponding pinned bands equal `[2/3, 3/2]`. Their omission from the inventory is a bookkeeping defect with no demonstrated numerical consequence in this draft.

The prior scientific audit stands. I did not rerun study computations or repeat the derivations and literature checks that this round does not change.

## 4. Process

The diff from `fb85388` is confined to paper, review, log and handoff material. No study protocol, locked study code or output, agreed report, or claim gate changed in that diff. The decision log records Yichen's authorization for this bounded fourth round. This review did not open the holdout or load a model, corpus or token cache.

The requested paper checks and render regenerated byte-identical tracked artifacts. Short probes read existing inputs or used strings in memory; the PDF page preview is under the ignored render directory. This memo is the only review-authored non-ignored repository change. Nothing was committed, downloaded, posted, uploaded or sent externally. No study-mode runner, analyzer, report builder or side-computation script was run.

## 5. Independent search

No new literature search was conducted in this bounded F22–F24 review. This is a scope choice, not an access limitation or evidence that no newer occupant exists. The earlier search record and the recorded Zenodo access gap remain for the Stage 9 gate. This memo makes no updated novelty claim.

## 6. Findings

### F25 — Minor, non-blocking: seven fixed-band occurrences are still removed without an inventory entry

**Evidence.** `literals.py:74` recognizes `[2/3, 3/2]`, and line 224 blanks it before either the formula scan or the exclusion-accounting loop. It never calls `aside()` or `add()` for that span. The probe `The interval was [2/3, 3/2].` therefore returns an empty list. There are **seven** such occurrences in the current section bodies: `06_remedies.md:27`, `07_power.md:17`, twice at `11_appendix_A.md:15`, and `12_appendix_B.md:10`, `:16` and `:18`. None has an inventory entry. Thus the response's “Every span the scan sets aside is now counted” remains too broad.

**Assessment.** All seven occurrences name the registered adequacy band, and the scanner separately asserts that band against the pinned inputs. E.2 now disclaims semantic completeness. This residual does not retain F22's former major severity or establish an incorrect study result.

**Recommendation.** Inventory each occurrence as a grid-verified band, or give the band an explicit excluded class and count it. Preserve the existing grid assertion, regenerate the inventory and registered counts, and make the description match the resulting categories. Include this case in the inventory-accounting control.

### F26 — Minor, non-blocking: supporting audit summaries lag the final build and scope statement

**Evidence.** `RESPONSE_claude_r3.md:9`, the round-four prompt and `DECISION_LOG.md:1001` retain **1,154** excluded spans and **269** identifiers; the current baseline consistently records **1,155 / 270**. The round-three log's build paragraph still says **552** placeholders, while the requested check resolves **560**. The eight new E.2 count placeholders and its added `R12` reference account exactly for these differences. The historical round-two correction to 552 is itself correct and should remain historical.

The orientation's §1 is qualified, but its §2 paper map (`REVIEW_ORIENTATION.md:55`) still says **“every numeral and counting word outside a placeholder”** belongs to the allowed classes. `literals.py:5` and `:196`, and `assemble.py:13` and `:220`, retain similar exhaustive descriptions. The manual-reading qualification appears in E.2 but is not repeated in the orientation's §1, despite the response describing both as updated in that respect.

**Recommendation.** Add a dated final-build correction giving 560 placeholders and 1,155 recorded excluded spans, including 270 identifiers; preserve the valid 552 count as the round-two state. Bring the orientation's paper map and script descriptions into line with E.2's recognized-pattern scope, and name the manual reading in the orientation. If F25 changes the inventory totals, record those subsequent totals with their own baseline rather than overwriting the historical counts.

F22's substantive coverage and manuscript-scope corrections are accepted; F23 is closed; F24's historical corrections are verified. F25–F26 are limited, non-blocking inventory and documentation cleanup suitable for the resolution record. No blocking or major finding remains open in this bounded review.

VERDICT: AGREE
