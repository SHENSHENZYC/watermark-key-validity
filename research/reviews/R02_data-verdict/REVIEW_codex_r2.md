# R02 — Stage 4 data verdict: independent review, round 2

Date: 2026-10-09. Reviewer: Codex.

## 1. Baseline and scope

Baseline: **main, 850d89d103b9ee474065a0de0746d31185eb56de**. The working tree was clean when this round-2 review began. On the repeated review request of 2026-10-09, HEAD and the requested tracked inputs were unchanged; this existing, untracked memo was the only working-tree difference. I revalidated the final-map digest, tokenizer asset hashes, held-out shares, P7 cells and confusion counts, reran the 14-case seal suite and reproduced the synthetic cell-scope counterexample. The findings and verdict remain unchanged.

I read AGENTS.md, REVIEW_ORIENTATION.md in full, the R02 prompt, my round-1 memo and the conductor's response; CORPORA_AUDIT_v0.2.md, DATA_LAYOUT.md, the v0.2 audit JSON, loader counts and partition summary, seal allow-list, settings comparison and planted-copy report; all nine requested scripts; and the decision-log entries headed “R02 round 1” and “Stage 4 exit, procedure v2,” including D4. I also checked RESEARCH_HANDOFF.md, the final partition's metadata and digest, and the relevant changes from the round-1 baseline. The older prompt's output filename is superseded by the user's explicit round-2 request. Study 1 design and results are outside this review.

Checks were short local computations: JSON/report arithmetic; metadata-only partition checks; hashing the final map and cached tokenizer assets; synthetic licence cases; execution of `tools/test_seal.py`; an additional synthetic seal case; and isolated checks of the partition finalisation guard and build-driver control flow. The seal suite ran with a temporary fixture directory that was removed afterward. The driver check substituted in-memory paths and subprocess results; it neither built nor downloaded anything. No corpus text, including held-out text, was opened by this review. I did not rerun the loader, full partitioner, audit or planted-copy text reader. No individual check exceeded one minute. Only this memo was added; nothing was committed or downloaded.

**Assessment:** the rebuild fixes important parts of every round-1 finding, and the recorded capacity still passes. F3 and F6 are resolved. F1, F2, F4, F5 and F7 are partially resolved. The remaining blocking issue is the production duplicate prefilter and its omission from the validation fixture (F8). The current counts are internally consistent outputs of the implemented procedure; they do not establish that every LSH bucket pair received the promised full-text confirmation.

## 2. Claims against evidence

### Disposition of F1–F7

| Round-1 finding | Disposition | Verified correction and remaining gap |
|---|---|---|
| F1, duplicate predicate, blocking | **Partially resolved** | Full-text shingle-set intersection/union now confirms retained pairs; the first-member shortcut is gone; the candidate prefix caps are explicitly disclosed. But an estimated-similarity prefilter still discards bucket pairs before confirmation, and the fixture omits that filter. See F8. |
| F2, seal, blocking | **Partially resolved** | The accessor verifies the versioned map's digest, resolves IDs and positions from it, validates the partition enum, and requires a registered final lock with matching study, manifest, partition and nonempty cells. All 14 supplied fixture cases pass. Actual requested IDs are still not checked against the cells named by the caller and lock. See F9; the original relabelling/no-lock bypass is fixed. |
| F3, licence allow-list and P1, major | **Resolved** | Five complete label strings are enumerated, with the separate Wikipedia project label; unknown/malformed labels are rejected. A thread requires a nonempty component-licence list with no fallback. P1 is computed from admitted identities and included in `core` and the verdict. Synthetic contradictory-label, wrong-host, null and malformed-component cases are rejected. |
| F4, failed-file exclusion, major | **Partially resolved** | Decompression failure and failed line-accounting identity now quarantine the whole file; partitioning and auditing skip flagged files. The news audit also requires the clean condition. External count mismatches are still discovered after admission without quarantining their files. See F10. |
| F5, expansion and finalisation, major | **Partially resolved** | The freezer selects exactly the next unfrozen P8 shard; the loader's `--only` path merges its record; a driver reclusters and recounts; ordinary final-map overwrite is refused. The driver can finalise after non-count audit failures, fails to route expansion loading to its selected version, and can overwrite current summaries before refusing an existing final version. See F11. |
| F6, capped counts and tokenizer provenance, minor | **Resolved** | The memo now identifies censored prefix counts and the two unresolved long-window books. Counts record tokenizer revisions, five asset digests in total, character caps and `add_special_tokens=False`; all five digests match the cached files. The 1,024-token book floor remains supported. |
| F7, synchronised record, minor | **Partially resolved** | The principal presentation fixes are present: current audit title, closed R01 row, P8 “not needed,” full P7 detail, exposure/CJK definitions, capped medians and seal-file state. Some current-state links and numbers remain stale, while new validation claims overstate their evidence. See F12–F13. |

### Map, count flow and held-out shares

The actual final map hashes to **`4e810c0269f78923d79de4b1b99838a875e6da7e94946f09dd3c83e3ac8ea9d0`**, matching its sidecar, summary and audit. Metadata checks reproduce 2,617,347 unique canonical IDs and 2,610,022 clusters/representatives; each representative has the minimum canonical ID in its cluster. Every assignment agrees with the recorded hash/modulo-five rule plus exposure forcing. All **73 exposure hits and 73 forced-open units** are open: news 30, books 19, threads 6 and Wikipedia 18.

The count flow is **2,617,347 − 230 exact unions − 7,095 near-duplicate unions = 2,610,022 clusters**. Subtracting 19,060 licence-excluded representatives gives **2,590,962 allowed representatives**, split into **2,072,902 open + 518,060 held out**. The excluded and non-representative sets do not overlap in this execution, so this subtraction is valid here. Counts report 13 input files, no quarantines and no unparseable records; physical and parsed totals both sum to 2,617,347. Round 1's raw-file hash/footer checks remain relevant to the unchanged freeze manifest; I did not repeat the entire raw-byte audit this round.

Shares recomputed from `partition_summary.json` count all clusters, before licence/length filtering:

| Source/language | Held out / clusters | Share |
|---|---:|---:|
| news/en | 25,277 / 126,430 | 19.992881% |
| stackexchange/en | 317,144 / 1,586,421 | 19.991162% |
| gutenberg/en | 2,962 / 15,250 | 19.422951% |
| wikipedia/ar | 33,850 / 169,379 | 19.984768% |
| wikipedia/de | 28,564 / 142,213 | 20.085365% |
| wikipedia/en | 31,183 / 155,908 | 20.000898% |
| wikipedia/ja | 18,583 / 92,493 | 20.091250% |
| wikipedia/ru | 18,506 / 92,539 | 19.998055% |
| wikipedia/zh | 45,832 / 229,388 | 19.980121% |
| gutenberg/da, outside target cells | 0 / 1 | 0% |

Overall: **521,901 / 2,610,022 = 19.996038%**. This denominator differs from the licence-filtered held-out total above.

### P7 cells and confusion counts

The audit's `cells`, P7 dictionary and reference-tokenizer `bins_by_source_lang` agree. Qwen columns below are the audit's reported intersections; this round did not independently retokenise documents.

| Cell | Open, Llama eligible | Held out, Llama eligible | Held out, also Qwen eligible |
|---|---:|---:|---:|
| news/en @256 | 37,696 | 9,362 | 9,362 |
| wikipedia/en @256 | 95,048 | 23,738 | 23,737 |
| stackexchange/en @256 | 982,015 | 245,245 | 245,238 |
| wikipedia/de @256 | 100,065 | 25,259 | 25,253 |
| wikipedia/ru @256 | 62,249 | 15,500 | 15,500 |
| wikipedia/ar @256 | 85,264 | 21,459 | 21,409 |
| wikipedia/zh @256 | 121,418 | 30,284 | 29,073 |
| wikipedia/ja @256 | 68,208 | 17,165 | 17,143 |
| wikipedia/en @1024 | 36,046 | 8,941 | 8,941 |
| gutenberg/en @1024 | 12,124 | **2,917** | **2,917** |

All ten exceed 2,500. Gutenberg retains **417 units of margin**. The open floors pass, and **28 of 35** eligible forum sites exceed 200 threads. Books 13286 and 61765 have capped counts 2,930 and 2,634: these establish neither full-text ineligibility for a 3,048-token requirement nor a failure of the 2,024-token requirement used by P7.

Recomputed from the comparison JSON, with columns ordered by estimated/exact threshold decisions:

| Setting | Both ≥ T | Estimate ≥ T, exact < T | Estimate < T, exact ≥ T | Both < T | Sum = retained candidate pairs | Near unions |
|---|---:|---:|---:|---:|---:|---:|
| 0.80 / 16×8 | 40,056 | 1,608 | 1,750 | 24,525 | 67,939 | 3,186 |
| 0.70 / 32×4 | 58,331 | 4,597 | 3,384 | 128,296 | 194,608 | 5,389 |
| 0.65 / 32×4 | 73,465 | 8,293 | 11,975 | 192,614 | 286,347 | 7,095 |

Each exact-Jaccard histogram also sums to its candidate count. At D4, **85,440** retained pairs satisfy the exact threshold; **7,095** of their union operations join previously separate components. Pair counts and successful unions are different quantities. The final summary matches the D4 comparison's confusion counts. Its **5,061,391** bucket-pair examinations count occurrences across bands, including repeats; they are not 5,061,391 distinct exact confirmations.

These confusion tables condition on surviving the prefilter. They cannot quantify positives discarded before confirmation. Further, the estimate uses prefix shingles and the confirmation uses full text, so their disagreement combines estimation error and a change of comparison domain.

## 3. Method and statistics

The current unit/cell definitions and deterministic assignment are precise enough to reproduce the reported capacity. P1 and tokenizer provenance now have substantive checks. P2–P4 and P7 numerically pass for this map. P5 passes on the observed files but its failure path remains incomplete; P6 passes the supplied suite but lacks actual cell-scope enforcement. P8 was not exercised because the initial pool passes. The synthetic driver checks therefore identify latent failures, not evidence that an expansion occurred in this build.

For retained candidates, `corpora_partition.py:49–60,158–167` uses full normalised text and computes intersection divided by union of unique shingle fingerprints. This is no longer a MinHash estimate used as final confirmation. Strictly, the sets contain 64-bit hashes of shingles rather than the literal strings; that qualification is separate from the demonstrated prefilter defect. The blockwise bucket loop removes the old star shortcut, but its `est >= threshold - 0.15` condition is an additional recall restriction.

The explicit prefix limitation is an improvement. However, the formula **1 − (1 − s⁴)³²**, approximately 0.998 at s = 0.65 under the ideal independent-MinHash model, concerns the similarity of the sets used for candidate generation. Full-text similarity does not lower-bound prefix similarity, and the formula does not include the estimate cutoff. It is not a 99.8% recovery guarantee for full-text pairs satisfying D4.

The planted report contains 18 originals, each with four positive variants and a same-source comparison. The 18 negative directions are only nine distinct unordered pairs, not independent evidence on 18 natural negative pairs, and not a sample of difficult template-sharing negatives. Their zero links do not establish a false-merge prevalence. Likewise, zero discovered cross-source clusters does not establish absence of cross-source overlap. Connected components enforce the chosen edge relation transitively; no claim that every pair within a component clears the threshold follows.

**D4 is already Yichen's decision.** I do not reopen the choice of 0.65 or 32×4. I flag the misstated supporting ranges, fixture linkage and characterisation of additional merges in F8/F12. Removing the unsafe prefilter while retaining D4 would correct the specified candidate-confirmation path; it would require a new versioned partition and capacity audit before scientific use. The binomial precision statements remain nominal independent-unit calculations, not evidence that deduplication alone establishes independence or inferential power for the later studies.

## 4. Process, holdout and record

The superseded v0.1 results are preserved and labelled. D4 is logged before the final v0.2 map. The reviewed changes are preprocessing, and I found no scientific outcomes in the requested materials that would make a corrective rebuild an outcome-driven protocol alteration. This is not an audit of all possible local access history.

The actual allow-list contains `locks: []`; the actual openings log is absent. The synthetic positive access test used fabricated text and its own lock/log. No actual held-out opening was needed for any check. The final-map digest verifies integrity against the sidecar, while a registered lock additionally binds the digest to the study; the unresolved problem is whether the requested units are in its declared cells.

The frozen source set and terms evidence are unchanged by this rebuild. F3's correction establishes conservative handling of the declared labels, not independent verification of every document's copyright status. No external access, posting, publication, messaging or visibility change occurred. The brief's scientific claims were not revised here. Current-state documentation still needs the corrections in F13, and the stronger duplicate/validation assertions need F8/F12 rather than a purely editorial update.

## 5. Independent search and limits

I did not conduct a new external literature search or fetch papers/licence pages. This round reviews the rebuilt Stage 4 implementation and its evidence; web availability was not the limiting factor. No claim of novelty or absence of newer occupants is made, and R01's literature review is not expanded by this memo. No new scientific quotation is relied on, so there is no new PDF-page quotation check to report.

The independent evidence is local code, metadata, JSON arithmetic and bounded synthetic checks. Actual natural-pair recall, false-merge prevalence, text-level validation of the comparison's metadata sample, and full-document lengths of censored records remain unverified. Rebuilding the corpus would exceed the requested review scope and time limit.

## 6. New findings and recommendations

### F8 — BLOCKING: the production prefilter discards qualifying bucket pairs, and the fixture tests a different procedure

**Evidence.** Audit §5.2 and the decision log describe exact confirmation of every bucket pair. `corpora_partition.py:23,138–145` instead retains a pair only if its prefix-signature estimate is at least T − 0.15. `tools/test_dedup.py:60` tests shared band plus full-text exact Jaccard, omitting this condition.

The existing report supplies a direct counterexample without any new text read: Gutenberg ebook 1, “first 10% removed,” has full-text Jaccard **0.996**, estimate **0.422**, and one shared 32×4 band. The fixture reports “yes” at D4; production discards it because 0.422 < 0.50. At 0.80/16×8, Wikipedia ar:7's shifted variant similarly has exact 0.898, estimate 0.648 and four shared bands, but fails the 0.65 estimate cutoff despite the fixture's “yes.”

Applying the production predicate to the report's rows gives direct positive-pair linkage **46/72, 51/72 and 64/72**, respectively, instead of **47/72, 52/72 and 65/72**. These are arithmetic rechecks of the displayed fixture rows, whose relevant values are unambiguous at the cutoffs; they are not a new corpus run, a corpus-wide recall estimate or a prediction of indirect component membership.

**Implication.** Full-text confirmation is correctly implemented for survivors, but the promised all-bucket-pair confirmation and reported validation are not. The 0.15 margin has no demonstrated safe bound across prefix and full-text similarities. The final map may omit additional edges; this review has not measured their number.

**Recommendation.** Retain D4's threshold/bands and exact-confirm every distinct LSH bucket pair, removing the unsupported estimate cutoff; alternatively, any different candidate policy needs explicit, accurately validated treatment. Make the fixture exercise the production predicate, include the two counterexamples and a large-bucket case, and state prefix candidate omissions and the limits of the coverage formula. Rebuild/version the partition and audit before use, preserving v0.2 as the record of the present implementation.

### F9 — major: lock cell scope is still self-reported rather than checked against requested IDs

**Evidence.** `corpora_access.py:34–35` loads authoritative source/language, but `load_texts` checks only ID existence and partition. `check_seal:62–67` compares the caller's cell list with the lock's list and logs it; neither function verifies that the requested IDs belong to those cells.

I executed the supplied 14-case suite successfully. In a separate temporary variant of that same synthetic suite, I changed only the held-out fixture unit's authoritative source to `different-source`, leaving the valid lock/request at `fx/en@1`. The positive path still returned that unit and logged the claimed cell; all 14 reported cases still passed. This did not involve any real held-out ID or text.

**Recommendation.** Derive each requested unit's source/language from the bound map and verify membership in the permitted cell scope before text access. Where a cell also binds length/window eligibility, use bound eligibility provenance for that check. Log the actual scope, with requested unique IDs or a reproducible ID-set digest, and add a wrong-source/wrong-language synthetic case. Keep the existing map, digest, enum and full-lock tests, which now work.

### F10 — major: quarantine still does not cover external reconciliation mismatches before clustering/counting

**Evidence.** `corpora_loader.py:248–259` quarantines only a decompression failure or failed physical = parsed + unparseable identity. A cleanly parsed news file with 126,672 records passes that predicate, although it fails the required 126,673 reconciliation. `audit_corpora.py:24–36` admits its units and constructs representatives before lines 50–56 mark reconciliation false; the cells then count those representatives without excluding the failed file. A nonzero unparseable count with a valid accounting identity likewise makes the audit's clean condition false without triggering loader quarantine.

The CRC/readable-prefix case raised in F4 is fixed. The current files have no recorded failures, so this finding does not assert that their counts are contaminated. It identifies an incomplete implementation of §4/P5's requirement that a file with a mismatch be excluded and never help a count pass.

**Recommendation.** Establish per-file acceptance, including applicable card/footer reconciliation, before clustering and admitted-unit counts. Record failure reasons and exclude failed files consistently. Make the loader and audit agree on the treatment of parse errors. Add tiny clean-but-short news and malformed-input fixtures alongside the decompression-failure case; check that failed-file units cannot influence either clusters or floors.

### F11 — major: the new build driver can finalise failed audits and mishandles versioned state

**Evidence.** Three paths remain incomplete in `tools/corpora_build.py`:

1. `failing_cells` checks P2–P4/P7 only. Lines 46–47 break when those counts pass, and line 67 finalises without checking P1/P5/P6. With a synthetic audit having P5 false and all count floors passing, isolated execution of the actual driver control flow reached `--final`. A subsequent FAIL is printed rather than converted to a failing build exit status.
2. The expansion loader command at line 63 passes `--only` but no selected output directory. The loader's `OUT` defaults to `outputs/corpora_units_v0.2`, independently of the driver's `--version`. With a different version and no manually supplied environment override, new units go to v0.2 while clustering/auditing target the other directory. This matters for the versioned rebuild F8 requires.
3. An ordinary rerun starts by writing a provisional partition/summary and audit for the selected directory. The existing-final-map guard is reached only later. Thus the map itself is protected, but the summary and audit describing it can already have been overwritten with provisional state.

I separately called the actual partitioner's guard against the existing v0.2 final map: it immediately returned **REFUSED**, before any rebuild or write. That part of F5 is resolved. The explicit `--allow-overwrite` escape hatch exists, so claims that a version is “never overwritten” should be qualified or the guard strengthened; this is distinct from ordinary overwrite refusal.

**Recommendation.** Reject non-count integrity/quality failures before expansion or finalisation; propagate a failed final audit as a failed build. Pass the selected units directory explicitly to the loader. Check the final version's existence before any writes, or isolate provisional state so existing final reports cannot be replaced. Exercise these paths with synthetic audits and command capture; no downloads or full runs are needed to test the control flow.

### F12 — major: the record overstates the evidence presented for D4

**Evidence.** Audit §6 and the D4 log describe 2% edits at exact Jaccard 0.83–0.87, 5% edits at 0.63–0.70 and shifted prefixes at 0.89–0.91. The recorded 18-row groups actually range over **0.716–0.917**, **0.585–0.699** and **0.885–0.996**, respectively. The audit says the 0.70 rule links one of 18 five-percent edits; the report contains **zero of 18**. F8 separately corrects the production/fixture linkage discrepancy.

The audit, response and log also identify the extra merges as genuine network-wide Stack Exchange meta posts and near-identical threads. `compare_dedup_settings.py:25–34` instead takes up to 40 two-member clusters from the first 400 lexicographically grouped clusters of each complete result; it does not select newly added merges or a representative sample. All 40 D4 samples are Stack Exchange, and all 80 title fields are empty. Their groups/IDs/token lengths do not establish the claimed textual characterisation. Compared with 0.80, membership in multi-unit clusters rises by **4,475 Wikipedia units**, **226 Stack Exchange**, **163 news** and **37 books**. These are membership-count differences, not union counts, but they show why the sampled source cannot support a general account of the additions.

**Recommendation.** Correct the numerical basis and distinguish observed metadata from textual interpretation. Retain D4 as the recorded decision while presenting the corrected evidence to Yichen. Withdraw or substantiate the claim about all additional merges through an appropriately authorised preprocessing validation of the actual differences; do not infer it from this sample. This review does not request a new threshold decision.

### F13 — minor: current-state pointers and one overlap claim remain stale

**Evidence.** DATA_LAYOUT.md's audit-memo and audit-results rows still point to v0.1. REVIEW_ORIENTATION.md §2 still describes the v0.1 audit/PASS as the data entry. RESEARCH_HANDOFF.md's “Established results” paragraph still reports **2,594,641** allowed representatives and cites v0.1, despite its current v0.2 status. Audit §3 still says source overlap is “enforced away,” stronger than its own later prefix-candidate limitation permits.

**Recommendation.** Point current-state entries to v0.2 (and subsequently to the corrected version), label historical counts explicitly, and replace the categorical overlap claim with the implemented clustering guarantee and residual candidate limitation. Carry this round's unresolved findings in the handoff until review agreement. Keep the superseded files intact.

VERDICT: REVISE
