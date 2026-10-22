# R12 — assembled draft, round 3

Reviewer: Codex. Date: 2026-10-20 UTC.

## 1. Baseline and scope

Baseline: `main` at **`fb85388b38f023c8df0eaca0d1cb16bbe351b7fa`**. The working tree was clean at entry. This is the requested re-review of F15–F21 and the changes made in response, including regressions in those changes. It does not reopen the agreed study outcomes, protocols, claim gate, J1–J11 or O1–O11.

I read the orientation and checkpoint prompt; `RESPONSE_claude_r2.md`, including its verification table and four dated corrections; the rewritten literal scanner, every allow-list entry and the inventory; the requested six script diffs from `659fd3d`; the specified assembled-paper passages and their section sources; the bibliography, fetch log, saved validation report and relevant local covers/texts; the round-two decision-log entry and handoff status. I checked the changed claims against the relevant registers, grids, audit JSON, side computation, agreed report blocks and locked code passages. The preceding memos supply the unchanged broader audit.

All seven requested commands completed successfully, using `.venv/bin/python`:

| Command under `research/paper/` | Observed result |
| --- | --- |
| `fill_paper.py --check` | **552** placeholders in 16 files; self-test passes; 427 inventoried literals: 186 in prose, 241 in formulas; 127 grid-checked, 151 allow-listed, 149 algebraic, 0 unallowed |
| `literals.py --selftest` | Pass |
| `tables/make_tables.py` | 359 checks, 0 failed |
| `tables/make_appendix_tables.py` | 82 checks, 0 failed |
| `reviews_table.py` | 11 agreed checkpoints, R12 open; agreed totals remain 33 rounds and 171 findings; R12 has two completed rounds and 21 findings before this memo |
| `build_references.py --offline` | 50 entries; one extraction warning, two resolved differences |
| `assemble.py --render` | 3 main tables, 6 main figures, 38 appendix tables, 7 appendix figures, 50 citation keys; all assembly checks pass |

After these commands, `git status --short` was empty, `git diff --exit-code` passed, and the paper-directory status with ignored paths showed only `render/` and `filled/`. The assembled Markdown is byte-identical to `HEAD`, SHA-256 **`e85767de143d718e49aa35c05fcf97ca8bbc5e7c19a7feb93e8c31fadc13d5a6`**. The saved `filled/LITERALS.md` also byte-matches the current scanner's generated report.

I ran no study runner, analyzer, report builder or side-computation script, loaded no model or token cache, downloaded nothing and committed nothing. Short probes used in-memory strings or read existing files. The authorized render and page preview are ignored outputs. This memo is the only review-authored non-ignored repository change.

## 2. Claims against evidence

### 2.1 Disposition of F15–F21

| Prior finding | Round-three assessment |
| --- | --- |
| **F15 — literal audit** | Substantial corrections verified: the original escape sentences are caught; formula tolerances are inspected; exceptions are bound to occurrences; the previously missed own-study counts now use placeholders. The claimed exhaustive enforcement is still not established: ordinary numeric forms escape completely, and intentional exclusions are absent from the claimed three-class inventory. **Open as F22.** |
| **F16 — author order, cover log and locator** | Huang's order and TextSeal's override match the local covers. Published arXiv-backed entries now retain their cover-check status, including skips. The Unigram locator is corrected. The response's statement that Common Pile's local cover was checked contradicts that log; see F24. |
| **F17 — captions** | The corrected content of D2b, D7b and D12a matches the evidence. Figure 5 now distinguishes the cross-tokenizer table from the Qwen counterpart in the named supplement. D7b's citations render. The change to caption markup introduces a separate rendering defect affecting 15 appendix captions, including D12a; see F23. |
| **F18 — plural references** | The stale sentence now names D14, D15 and Figure 5 correctly. The added numeric plural pattern handles lists as intended. No nonexistent Table 5 remains in this passage. |
| **F19 — conditional floor and slack** | Corrected. A.2 conditions the rejection probabilities on the common shift and takes the outer expectation over it. A.5 states the implemented relative slack and absolute guard. |
| **F20 — nominal wording and abstract conditions** | Corrected. §6.1 says “near nominal,” §6.3 says “near α,” and the abstract identifies per-key conformal calibration on 5,000 same-cell human null texts. Its power sentence now carries constraint 17's requested conditions. |
| **F21 — PDF scale and boundaries** | Corrected and independently reproduced. All six variants have identical measured body-word boxes. The full PDF's statements, references and appendices begin on pages 18, 19 and 21. F23 concerns caption parsing, not a recurrence of global shrinking. |

### 2.2 Literal inventory, sources and generated counts

The allow-list contains **126 rules**, of which **39 carry a source specification**. Every context contains its literal, and every supplied source regex matches its named local file. I reviewed the occurrence-to-reason bindings in the current scan: the three weight normalisations are no longer assigned the collision-quantity reason, and the two disjoint subsamples have their own reason. `s1_core.py:348–358` supplies the latter's substantive evidence, including the construction of the second disjoint subsample where sufficient texts are available; the constant `PAIR_SUBSAMPLE = 300` supplies its size.

The protocol/code sources support the newly inventoried tolerances and coefficients, including the R4b discrepancy, the Gumbel fourth cumulant and identity tolerance, the audit probability, REP's slack, and the two constants in A.5's floor comparison. The worked-example allowances describe the examples re-derived in the earlier reviews. The currently matched reasons are appropriate; the problem in F22 is coverage, not a recurrence of the previous wrong-context matches.

The new generated phrases also check out:

* `s3:t1_fail_n_tagE` is **3**, supplying “three evaluation cells.”
* `paper:g_s2_s4_groups` is **3**, from the nonempty groups whose registered membership counts are 18 at `h = 4`, 6 news chains and 2 further `h = 1` chains. The report explicitly calls them overlapping groups, so the phrase does not imply their counts sum to the total.
* `paper:g_n_models` is **1**, with the single-model grid structure checked. Its placeholders now appear in the abstract, contribution, Figure 6 and discussion passages.
* `paper:g_n_sources` is **4**, and its check now compares the grid's count with the audit JSON's actual source count.

The counts in E.2 reproduce the implemented scan exactly. They count the occurrences the scanner recognizes; they are not evidence that it recognizes every numeric expression.

### 2.3 Tables, captions and references

I independently compared the six extracted supplementary blocks, including their notes, with their source blocks and checked that their table rows occur verbatim in the agreed reports:

| Paper table | Source | Data rows |
| --- | --- | --- |
| D7b | Study 4, `operating_points`, Table 9 | 18 |
| D12a | Study 2, `deployer_kgw`, Table 16 | 40 |
| D12b | Study 2, `deployer_gumbel`, Table 17 | 40 |
| D13a | Study 3, `remedy_class`, Table 9 | 120 |
| D13b | Study 3, `cross_tok`, Table 15 | 72 |
| D13c | Study 3, `t1_by_block`, Table 2 | 80 |

All **120 numeric data fields** of D2b match the side JSON at their displayed precision. Both width records have `L = 256` for eight cells and `L = 1024` for `wikipedia_en_1024` and `gutenberg_en_1024`. The side script's docstring and production-cell selection specify the raw rule at the longest length, with 1,000 keys; the register supplies 10,000 texts. The revised caption agrees with those facts.

D7b's conditions match the grid and registers: Qwen2.5-1.5B, `δ = 0.5`, `h = 1`, raw rule, `L = 256`, `α = 0.01`, 100 power keys, 50 generated texts per key, 5,000 model-null texts and the diagonal human-null source, with `N_cal = 5000` for the per-key methods. The three prompt cells do not include Gutenberg, so its quoted Study 3 evaluation count of 10,000 is appropriate. The rendered caption on full-PDF pages 53–54 contains the Genhatharan, AutoMark, LUNA and artefact citations as citations, not bare keys.

D12a now separates the key-mean from the columns with crossed intervals and the SD's key-bootstrap interval. Figure 5 names `tables_pairs_kgw_alpha0.01_full.md` for the Qwen counterpart and D13b for cross-tokenizer transfer. Appendix D's introduction correctly names D14 and D15. In-memory checks of the new renumbering pattern map “Tables 1 and 4” to “Tables 1 and 2” and “Tables 1, 4 and 6” to “Tables 1, 2 and 3,” using the actual source-to-main mapping.

### 2.4 Bibliography and local-source checks

The local Huang v1 cover places **Huang, Xu, Ramchandran and Jiao on the first author line, with Jordan below**. The rebuilt bibliography now has Jiao fourth and Jordan fifth, and removes the erroneous difference note. TextSeal v2 places **Rebuffi third**, followed by Souček, Tran, Lacatusu, Mourachko, Parimi, Ropers, Moritz, Stark, Elsahar and Fernandez; its verified override matches.

All **38 arXiv-backed entries** now have a persisted cover status. Those statuses distinguish successful text checks, partial checks, missing local texts and the visually confirmed exceptions. They do not establish that every cover was fully checked. The Khachaturov extraction warning remains explicit; Common Pile and Wu are recorded as having no local PDF text. The other 12 entries use non-arXiv source records. The saved bibliography validator remains at 50 valid entries, zero errors and four recommended-field warnings for the unchanged TMLR/HDSR omissions.

I re-found the Unigram passage in `research/literature/txt/2306.17439.txt`: the phrase “By the variance formula for sampling without replacement” occurs across a line break on PDF p. 31 and again on p. 32. The new **pp. 31–32** locator and bibliography note are supported.

## 3. Method and statistics

The mathematical corrections resolve F19. For per-text thresholds, conditional independence given the common shift gives the floor

`E_D[mean_i pi_i(D)(1 − pi_i(D))] / N_eff`,

with `pi_i(D) = P(Z_i > tau_i | D)`. At zero residual variance these conditional probabilities are indicators, so the floor vanishes even when the thresholds differ. Repeating the two-text check with a standard-normal shift and thresholds 0 and 1 gives a marginal-probability pseudo-floor of **0.09587094108285049**, while the corrected conditional floor is **0**. A.2 now makes precisely this distinction.

A.5's comparison is `v_raw < −tau_v(1 + 10^−9) − 10^−300`, matching `s3_core.py:240` and `V_NEG_TOL = 1e-9`. The comparison is strict: with `tau_v = 0.001`, neither `−tau_v` nor the boundary `−0.001000000001` is flagged; the next representable value below the boundary is. This is a transcription check, not a rerun of Study 3.

The abstract retains the model, strength, width, length, rule, level, calibration source and size, power-key count and prompt count required by constraint 17. Its method is now explicit. The measured `0.98%–1.01%` key-mean range supports “near nominal,” not exact equality. §8 retains the qualification that validity for the given key is averaged over its calibration draw. No new guarantee, remedy ranking or resolved power-dispersion claim is introduced.

For presentation, I independently measured the first-page word “deployer” with `pdftotext -bbox` in every variant. All six have width **35.005746 pt** and height **11.080688 pt**, a full/main ratio of exactly one at that extraction precision. Page counts reproduce as 92 full, 18 main, 19 with statements, 14 without figures, 15 without tables and 12 prose-only. I located the headings inside the full PDF itself: AI use on p. 18, references on p. 19, Appendix A on p. 21. These sections share boundary pages, so page-count subtraction would still not be the right attribution method. O9's main-text length decision remains unchanged.

## 4. Process

All **75 pinned-file hash comparisons** match. Every lock still has `before_outcomes: true` and `final: false`. The diff from `659fd3d` changes paper, review and navigation material, with no change to a study protocol, study code, locked output, agreed report or claim gate. Nothing in this review opened the holdout.

The response and decision log explicitly withdraw the earlier Huang-order inference, identify the earlier scanner's limitations, replace the shrunk full-PDF count, and correct the Unigram locator. The handoff and R12 row correctly say round three is pending and R12 remains open. The remaining discrepancies in the verification record are F24; they do not change a study result.

No publication, upload, contact, visibility change or external download was performed. The scope and terms restrictions were respected.

## 5. Independent search

No new literature search was conducted in this bounded correction round. This is a scope statement, not a lack of web access or an assertion that no newer occupant exists. The earlier search record and the recorded Zenodo access gap remain for the Stage 9 gate. This memo makes no updated novelty claim.

## 6. Findings

### F22 — Major: the literal scanner still misses ordinary numeric expressions, while E.2 claims exhaustive enforcement

**Evidence.** The old regression cases now work, but the following independent calls to `scan_text(sentence, "00_abstract.md", load_allowlist())` each return an **empty list**, not an unallowed occurrence:

| Probe sentence | Escape |
| --- | --- |
| `There were seventy-five keys.` | `WORDS` excludes words adjacent to a hyphen, so both parts of a compound cardinal disappear (`literals.py:70`). |
| `We measured 5–95% of the keys above nominal.` | The `5–95%` branch is stripped without requiring a quantile-band label (`literals.py:65`). This contradicts the stated “only in their labelled form” restriction. |
| `The estimate was $.123$.` | The math numeral pattern requires an initial digit and prohibits matching after a decimal point (`literals.py:78`). |
| `We measured $\text{sixty}$ failures.` | Formula processing scans numerals, then blanks the entire math span before the counting-word scan (`literals.py:241–264`). |

Consequently the assembly would not reject these inserted statements, and its registered inventory counts would not even change. E.2 (`PAPER_DRAFT_v0.1.md:1577`) nevertheless says the scan lists “every numeral and counting word” in prose and formulas and refuses any literal outside the three classes. The orientation repeats that claim. Even intentional exclusions such as quantile labels and numeric exponents are removed rather than accounted for in those three classes.

**Inference.** This leaves F15's enforcement claim open. I have not found a wrong measured result through these probes; the major issue is the assertion that the automated check establishes a completeness property it does not enforce.

**Recommendation.** Cover compound counting words and leading-decimal forms, inspect text within formulas, and bind quantile-band exceptions to their actual labelled phrases. Add these independent probes to the self-test. Then make the manuscript describe the check's exact scope: either inventory the intentional exclusions as such, or explicitly identify the scan as a syntactic check with documented exclusions and manual source review. Do not use “every” and “refuses any” to imply semantic completeness merely because the current examples pass. Regenerate the inventory and its registered counts after the correction; no study result needs changing.

### F23 — Minor: the new fenced caption blocks render as literal markup for 15 appendix tables

**Evidence.** `assemble.py:99` returns a fenced div without a leading blank line, and `process()` appends it immediately after the preceding line. In Appendix D, the item description often directly precedes the table marker. Pandoc therefore parses the fence and caption as part of that paragraph.

The regenerated HTML contains **26 proper caption divs for 41 tables**. The other **15 captions** print the opening and closing fences as text: **D1, D2a, D3a, D4a, D5, D6a, D7, D8a, D9a, D10a, D11, D12a, D13a, D14 and D15**. I confirmed the defect visually on full-PDF p. 66: the D12 introduction runs into `::: {.table-caption} Table D12a.`, and the preceding D11 caption's closing `:::` is visible near the top. These captions also miss the div's intended 9 pt formatting.

An in-memory Pandoc check using the actual D12 excerpt produces literal fences and no caption div. Adding a blank line before the opening fence produces the intended div and no literal fence.

**Recommendation.** Ensure block separation when inserting caption divs, then assert that every assembled table has a parsed caption container and that no raw caption fence appears in the rendered output. Re-render and update the resulting page count. The corrected caption content and citations should be retained; the global scale fix itself is sound.

### F24 — Minor: a few round-two verification statements do not match the rebuilt artifacts

**Evidence.**

* `RESPONSE_claude_r2.md:10` says Common Pile's local cover text was checked and has the arXiv order. The regenerated `fetch_log.json:138` instead says **“no local PDF text: the cover was not checked”**, and the corresponding local PDF/text is absent. The published-order correction is supported by its saved record, but that does not constitute a local-cover check.
* The round-two build paragraph at `DECISION_LOG.md:989` reports **543 placeholders**; the current section files, register and rerun give **552**.
* The same round's correction paragraph calls the allow-list **151 entries**. There are **126 rules covering 151 matched occurrences**; those quantities should be distinguished.
* The orientation's §1 still describes the current render as **17 main pages, 49 overall**, despite the round-two correction and current **18/92** build.

**Recommendation.** Correct the response's Common Pile statement to the recorded skip, and add the factual count corrections to the decision record. Update the current orientation summary. Preserve genuinely historical build entries as historical, and leave the cover gap explicit; no download is necessary to correct the record.

There is no blocking finding about the scientific results or locked record. F22 remains a major open issue in the manuscript's reproducibility claim, with F23 and F24 as minor corrections.

VERDICT: REVISE
