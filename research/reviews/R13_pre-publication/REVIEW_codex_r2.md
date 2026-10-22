# R13 — pre-publication, round 2

Independent reviewer: Codex. Reviewed 2026-10-22 UTC (2026-10-21 local).

## 1. Baseline and scope read

The requested working baseline is `5ba69a3`; the substantive corrections are in `13eeae9e42082440681a92e75e16c31346f09545` (`13eeae9`). At review, `git rev-parse HEAD` returned `43848eb9a914e40bde89e459d7423c6143470161`. Its difference from `5ba69a3` is confined to `RESEARCH_HANDOFF.md` and four added lines in `research/DECISION_LOG.md`; the paper, converters and snapshot builder are unchanged. The working tree was clean before this memo. The snapshot is `../watermark-key-validity` at `9731bd11333e4086669e28793254a1ac206f4c4d`, whose manifest names clean source commit `13eeae9e42082440681a92e75e16c31346f09545`, built at `2026-10-21T23:25:27Z`.

I read the orientation and round-two prompt, then the response to round one, the dated decision-log entry, the five corrected passages and their section open items, the specified gate sections and correction block, the Bonet bibliography entry and provenance, the LaTeX converter and repaired PDF pages, and the snapshot builder, manifest, README and site. I also inspected the agreed reports' source tables, the generated LaTeX, the compilation logs, `reviews_table.py`, the AI-use and availability statements, the site builder, the bibliography builder, and the snapshot's Git history and retained bibliography records.

The external rechecks used read-only GitHub API responses at keylottery commit `8ebb6b4f52927d0adbe9084d53ba49f3f825d6eb` and Bonet commits `e2d47aef5f18c119647c65655dae44c877813895` and `6261c02de24cdc3005bc6eafe2147b9405cb63a7`. No repository was cloned, no corpus, model or PDF was downloaded, no study was run, and no builder that writes canonical outputs was executed. Local checks were short, read-only computations; only this memo was written.

## 2. Claims against evidence

### Disposition of the round-one findings

| Round-one item | Recheck and disposition |
|---|---|
| R1/F1, same-domain standardisation | **Resolved.** The pinned `report/claims.json`, C7, gives pooled FPR/α at α = 0.01 of approximately 1.170, 1.181, 1.294, 1.156 and 1.125 across the five domains; its 95th-percentile keys remain above the ideal reference. The new §6.1 distinguishes standardising each key's score from restoring a nominal key-averaged false-positive rate. Its open item and the gate's correction block now use the correct estimand. |
| R1/F2, screening and masking | **The substantive conflation is resolved; one precision issue remains, F12.** The pinned proposal and `report/screening.json` distinguish the measured mean-score screen from the proposed predicted-rate audit. S3's clean-text comparison is ten screened against ten random keys, 400 prompts each, OPT-1.3B, δ = 1 and α = 0.0001. The recorded mean powers are 0.66275 and 0.659, giving random minus screened = −0.00375, with interval [−0.051, 0.04175]; the rounded −0.4 points and [−5.1, 4.2] are faithful. C6 separately gives the approximately 8.7-point masking loss at ε = 0.01 under those δ and α settings. The corrected sentence separates the experiments and does not rank remedies. |
| R1/F3, colliding columns | **The collisions and empty-cell corruption are resolved; the replacement presentation needs F11.** The repaired PDF pages have separated columns and the C1 total now occupies the right cells. All original values, columns and rows are preserved in the six split tables. However, a repeated first column is not a sufficient row identifier in these tables. |
| R1/F4, redistribution of third-party captures | **Not resolved for release.** All 291 named raw captures are absent from the current tree, but remain in its pushed parent commit (F9). Separately, current-tree bibliography JSON contains substantial third-party patches, contrary to its classification as metadata (F10). The latter is an additional issue found in this round, not something the first memo had established. |
| R1/F5, dating clause | **Resolved in the paper.** §1 now states the self-dating, public repository date and this project's lock chronology without asserting present mutual non-citation. That chronology supports the cautious concurrent-work description; it does not independently prove either author's knowledge. A superseded assertion survives in the gate's analysis, addressed in F13. |
| R1/F6, Bonet citation | **Resolved.** The caveat is present in the README at `e2d47ae`, dated 2026-08-31T02:48:26Z, and absent from the earlier scaffold at `6261c02`. The latter commit's message supplies the 24-key count. The bibliography now links the former README and distinguishes the measurement commit; the fetch log, gate §3 and constraint 35 agree. |
| R1/F7, supposedly pinned paths | **Resolved for the current tree.** The builder now derives its exceptions from locks/manifests. The two retained records are Study 2's `VALIDATION.json` and Study 4's `model_manifest_qwen2.5-1.5b.json`; their digests are actually pinned, and their snapshot bytes are unchanged. The other path-bearing files receive the declared substitutions. Historical copies are covered by F9's release-history check. |
| R1/F8, Russian comparison | **Resolved.** The new §5.5 describes the reported upper-key quantile comparison, approximately 2 versus 4.2 at matched effective length about 55, rather than treating that ratio as an across-key SD ratio. This matches the pinned proposal's comparison. |

The new §3.3 closing clause correctly keeps the mean-score identity shared with the concurrent work while naming this project's ratio, occupancy weights, cross-set term and validation. I found no new claim of exclusive priority in the five corrected passages. The remaining screening ambiguity is narrower than the original F2 error.

### Conversion and table preservation

I independently matched the six original Markdown tables against both their agreed reports and `outputs/study*/report/tables.md`, and then compared their column projections with the generated LaTeX panels. Whitespace and inserted line-break opportunities were normalised; empty cells were retained. No header or cell mismatch was found. The complete conversion comparison covered the 41 original tables and 47 resulting longtables.

| Table | Original data rows × columns | Panels, including repeated first column | Distinct first-column labels |
|---|---:|---:|---:|
| D4a | 28 × 20 | 18 + 3 columns | 6 |
| D4b | 39 × 26 | 18 + 9 columns | 1 |
| D4c | 23 × 24 | 17 + 8 columns | 15 |
| D4d | 5 × 24 | 17 + 8 columns | 2 |
| D6a | 6 × 16 | 14 + 3 columns | 3 |
| D13a | 120 × 19 | 18 + 2 columns | 5 |

These are 221 original rows and 4,622 original data cells, all preserved; only the intended first-column repetition is added. This verifies data preservation, not adequate identification of the second-panel rows.

I viewed C1 on PDF page 38 and the first and second panels beginning on pages 46/49 (D4a), 50/53 (D4b), 57/60 (D4c), 61/62 (D4d), 63/64 (D6a) and 92/97 (D13a). The previous collisions are gone. The first panels remain small landscape tables; F13 corrects the response's inaccurate claim that both panels use portrait footnotesize.

An in-memory conversion of the assembled draft reproduces the committed LaTeX abstract and body exactly. The PDF has 115 pages, with §8 ending and the unnumbered AI-use statement beginning on page 21. There are 13 figures and 53 bibliography entries. The final-pass `main.log` contains 16 overfull warnings, maximum 0.19473 pt, and no undefined-citation or missing-character warning; `tectonic.log` repeats those warnings across two TeX passes. Those sub-point overruns do not reproduce the old collision problem. I did not recompile or claim a new byte-reproducibility test of the PDF.

## 3. Method and statistics

This round changes attribution, presentation and publication packaging, not a locked design or statistical result. I found no reason to reopen the four agreed reports or their protocols. The failed and unresolved findings remain visible, including W2's unresolved rows; no outcome has been repaired by changing its rule.

The corrected standardisation statement has the proper target. Screening's wide key-level interval supports the stated inability to resolve its power cost; the masking comparison is a separate experiment, and the paper now says so. The source's S7 still supports selection of conservative keys rather than removal of dispersion. F12 asks that the actual across-domain maximum defining the measured screen be explicit. No new experiment or recomputation of a locked result is needed for that correction.

The panel problem is likewise presentational: data remain in the same ordinal order, but a reader cannot identify many second-panel values by a meaningful row key. Numeric preservation alone does not make those diagnostic tables usable.

## 4. Process, records, snapshot and site

Before creating this memo, the read-only `reviews_table.scan()` returned R13 with one round, eight findings, verdict REVISE, `agreed: false`, and `open: true`. The agreed totals are 12 checkpoints, 37 rounds and 197 findings. These agree with the AI-use statement, Appendix E.3 and E1. The open-checkpoint sentence appears in the PDF and HTML; it does not falsely count R13 as agreed. The eventual resolution must regenerate those records in the normal way. Nothing here requires changing a historical review memo.

`fill_paper.py --check` passed: 563 resolved placeholders, 455 recognised literals, zero unallowed literals and the self-test passing. The current decision-log entry and handoff correctly describe the round-one corrections, 115-page build, rebuilt snapshot and pending round-two review. Some other current-state documentation still contradicts those corrections (F13). The preserved original wording decisions should remain historical records, with explicit correction links where needed.

For the snapshot's **current tree**, all 7,663 manifest-listed digests match; there are no missing listed files or unexplained extra files beyond the manifest itself. The 349 declared exclusions are absent. The source files match the stated source commit after the declared substitutions and additions; the 23 generalised files and two verbatim pinned records match the builder's rules. The scan found no secret-like strings or excluded corpus text, model weights, token caches, literature PDFs/text dumps, `render/` or `filled/` directories in that tree. These checks do not clear Git history or embedded third-party text: F9 and F10 are counterexamples to the release package's broader assurances.

The snapshot's `docs/` matches the working site's files. Its abstract exactly matches a fresh in-memory Pandoc rendering of the filled abstract. The PDF and HTML links resolve locally; the title, author, citation metadata, citation block and licence/AI-use footer are consistent with the paper and P1. The site identifies itself as a pre-publication build. `docs/paper.pdf` equals `research/paper/latex/main.pdf`, SHA-256 `d1f6a7b552272e4c6bb291b92dc47e9fde463c340a7b45dcde07fcee65854ad7`.

A read-only GitHub API check confirmed `private: true`, `visibility: private`, `has_pages: false`, and remote `main` at `9731bd1`, with parent `698575e3efc4d111931f31d695d68e5ba201fcf8`. Thus the problematic ancestor is already part of the private remote that is proposed for publication. The public flip, Pages activation, publication tag and any author contact remain pending on Yichen's word. No outward change was made during this review.

## 5. Independent search and limits

I re-read the named concurrent-work and Bonet sources at their pinned commits through the GitHub API. A bounded web search on 2026-10-22 UTC used `"key-conditional" watermark after:2026-10-20` restricted to arXiv, `"per-key" "watermark" after:2026-10-20` restricted to arXiv/GitHub, and `"keylottery" watermark` restricted to GitHub. It supplied no relevant new research result; its returned hits were unrelated software uses of the search terms. This is weak retrieval coverage, not evidence of absence or an exhaustive repeat of the source gate. I found no additional occupant in this bounded round and make no new priority claim. The gate's recorded access gaps remain gaps; no challenge page was bypassed.

## 6. Findings

### F9 — Major: excluded captures remain in the pushed publication history

**Evidence.** The snapshot has two commits, `9731bd1` and its parent `698575e`. The latter still contains all 291 files under `research/claim_gate/raw_A/`, `raw_B/` and `raw_C/`. For example, `git -C ../watermark-key-validity show 698575e:research/claim_gate/raw_B/github_readmes/eth-sri_automark.md` retrieves 7,287 bytes. GitHub confirms the same parent on the pushed remote. `tools/make_public_snapshot.py:12–13` explicitly preserves history during updates. The README and gate §7 nevertheless describe these captures as staying private or not distributed.

**Inference.** Removing files in the latest commit does not remove them from the repository that will become public. The proposed visibility change would expose the reachable ancestor, so the central release issue in R1/F4 remains open. The current manifest cannot establish a property of all public Git history.

**Recommendation.** Prepare a publication history containing only approved content, for example a fresh publication repository/root built from the cleared tree, while retaining the original working and review history privately. Yichen should choose the repository/history procedure; this memo authorises no rewrite or deletion. Before release, check every publicly reachable branch and tag and their ancestors for the excluded material, and ensure the chosen remote no longer exposes the superseded publication snapshots. A further ordinary deletion commit is insufficient.

### F10 — Major: retained GitHub API records contain substantial source text, not just metadata

**Evidence.** At snapshot HEAD, five files under `research/paper/bib_sources/github/` contain twelve `files[].patch` fields. In `keylottery_commit.json`, the patch for `proposal/proposal.tex` has 26,629 characters, including long paragraph contexts and old/new manuscript text. In `llmwatermark_readme_commit.json`, the README patch has 9,950 characters; six added Python files are also present as full addition patches, including `examples/animate_detection.py` and `tests/test_readme.py`. Other retained patches occur in `genhatharan_v1_commit.json`, `llmwatermark_commit.json` and `xlr8harder_synthid_commit.json`.

The gate's §7 bibliography row classifies these records as API metadata; its keylottery row limits reuse to a short phrase and says no code or number set is reused. The README's licence section and `LICENSE-TEXT` say third-party materials are not included. Those descriptions do not match the bytes being distributed. The source record also reports no keylottery reuse licence. `build_references.py` uses factual fields such as commit SHA, date, author and repository metadata to build these entries; it does not need the patches for that task.

**Inference.** A JSON API wrapper does not turn embedded manuscript or source-code text into bibliographic facts. The current rights inventory therefore does not cover the actual package. This finding does not assert that every included patch has identical licensing restrictions; the immediate error is treating all of them as metadata and asserting their absence.

**Recommendation.** Preserve full responses privately and publish a documented projection containing the needed provenance fields without patch/diff bodies. Alternatively, inventory any deliberately retained third-party material and provide its applicable permissions, licences and notices, with accurate package descriptions. The projection is the simpler option for these citation records. Update the builder, manifest and rights description together, and apply the correction to the publication history covered by F9 as well as HEAD.

### F11 — Major: split panels lose usable row identification

**Evidence.** `make_latex.py:276–295` repeats column 1, regardless of whether it identifies a row. D4b's second panel begins on PDF page 53 with the label `primary` on every one of 39 rows; the corpus, tokenizer, rule, width and length are in the earlier panel. D13a's second panel begins on page 97 with only class and the last predicted-share column; each class occurs 24 times, with the rule, width and method in the first panel. D6a's second panel on page 64 omits the rule, while each prompt-cell label occurs twice. The first-column labels are non-unique in all six split tables, as the table above shows. Their panels have different wrapping and page breaks.

**Inference.** Values are intact and can be joined by counting ordinal rows across pages, but a reader cannot reliably identify a second-panel value from its displayed labels. This is especially consequential for the 120-row D13a comparison and the 39-row diagnostics in D4b. It is a new limitation of the F3 repair, not evidence that the agreed tables were numerically changed.

**Recommendation.** Repeat a complete identifying column set in each panel, or add a stable, unique row identifier to every panel and explain it in the captions. Refit the panels with that identifier included; if necessary, split row groups so the corresponding pieces are close together. Recheck one-to-one joins and the rendered pages while retaining every existing cell and its order. The original collisions need not be reintroduced to solve this.

### F12 — Minor: §8 omits the maximum across domains in the measured screening rule

**Evidence.** The corrected sentence in `PAPER_DRAFT_v0.1.md:243` says the screen retains the 20% with the smallest standardised mean score over five reference domains. The pinned [PREREGISTRATION.md §9](https://github.com/katcinskiy/keylottery/blob/8ebb6b4f52927d0adbe9084d53ba49f3f825d6eb/PREREGISTRATION.md), lines 68–70, defines a key's score as the **maximum** across the five domain-specific reference means, each divided by that domain's across-key SD. The proposal says the same. The response's verification already recognises this maximum, but the paper and its open item do not state it.

**Inference.** The published wording could be read as a mean pooled across domains, which would be a different key-selection rule. This does not invalidate the reported cost, but leaves the repaired method description ambiguous.

**Recommendation.** Say that it keeps the 20% of keys with the smallest **maximum, across the five reference domains, of the standardised reference-mean score**. Carry that precision into the section open item. The cost, conditions and distinction from the proposed predicted-rate audit can remain as corrected.

### F13 — Minor: current-state documentation still contradicts the corrected build and evidence

**Evidence.** Three discrepancies remain:

- The response's F3 row says the six two-panel tables are footnotesize on portrait pages. In `main.tex`, each first panel is `scriptsize` in landscape and each second panel is `footnotesize` in portrait. The converter's report at lines 296–304 retains only the last panel's `fit_k`, which explains the misleading summary.
- The orientation's R13 environment paragraph still calls the committed LaTeX outputs byte-reproducible except `tectonic.log`, whereas the new decision-log correction explicitly records PDF conversion metadata that prevents that blanket claim. Its introductory current-build description also retains the older 105-page/`698575e` snapshot state.
- Gate §2.5 still asserts that neither work cites or could have read the other, and §9 still says the Bonet key count is unknown. The round-one correction and the gate's own §3 supersede these statements. Original J13/J14 decision quotations are historical records and need not be erased, but these unqualified analysis/status sentences should not read as current findings.

**Recommendation.** Report font/orientation per panel, or explicitly describe the mixed layout, and correct the response with a dated note. Bring the orientation's current-build and reproducibility statements into agreement with the measured record. Mark the gate's superseded analysis statements as corrected and distinguish the known 24-key commit-message count from benchmark files that were not read. Preserve the original decisions and dated history. These are record corrections, not requests for additional study runs.

The release remains unready because of F9–F11. F12–F13 are bounded wording and record corrections. The successful numeric, source and digest checks above should be retained when those changes are made.

VERDICT: REVISE
