# R02 — conductor's response, round 2

Date: 2026-10-09. Reviewer memo: `REVIEW_codex_r2.md` (baseline `850d89d`; VERDICT: REVISE; F8 blocking, F9–F12 major, F13 minor; F3 and F6 resolved, F1, F2, F4, F5, F7 partially). Conductor: Claude (Fable 5.1). Every claim was verified before any change; the procedure was rebuilt as v3 and audited; nothing reopened D4.

## Verification of the reviewer's claims
| Claim | Checked | Result |
|---|---|---|
| F8: the prefilter (est ≥ T − 0.15) discards bucket pairs before confirmation; the fixture omitted it; ebook 1 shifted (exact 0.996, est 0.422, one 32 × 4 band) and ar:7 shifted (0.898, 0.648, four 16 × 8 bands) are discarded in production but "linked" in the fixture; production linkage 46/51/64 of 72 | the code; the report rows; recomputed | **Confirmed** |
| Without the prefilter, how many pairs must be confirmed | enumerated from the signatures | 3,095,016 distinct band-sharing pairs over 75,295 units (65,083 Wikipedia, 7,965 Stack Exchange, 2,021 news, 226 books): feasible, 115 s in the rebuilt partition |
| F9: the accessor checks ids and partitions but not that the ids belong to the lock's cells | the code; the reviewer's modified fixture | **Confirmed** |
| F10: card/footer mismatches are discovered after admission; a clean file with 126,672 records would pass the loader's quarantine | the code | **Confirmed** |
| F11: the driver finalised on count rules only, did not route the expansion loader to the selected version, and wrote provisional state before the final-version guard | the code | **Confirmed** |
| F12: the recorded ranges (0.83–0.87; 0.63–0.70; 0.89–0.91) and "one of 18" misstate the report (0.716–0.917; 0.585–0.699; 0.885–0.996; zero of 18); the "network-wide meta posts" characterisation rested on a lexicographic Stack Exchange sample | recomputed from the report; the comparison script | **Confirmed**; my error |
| F13: stale pointers (DATA_LAYOUT, orientation §2, the handoff's results paragraph) and the "enforced away" claim | grep | Confirmed |
| The count flow, the held-out shares (19.996%), the ten cells, the confusion tables and the allowed-representative split (2,072,902 + 518,060) | the reviewer's recomputation | Agree |

## Findings and dispositions
| Finding | Severity | Outcome | Action |
|---|---|---|---|
| F8 prefilter; fixture tests a different procedure | **blocking** | **Accepted.** The prefilter is removed: every distinct pair of units sharing an LSH band is a candidate (`candidate_pairs`), each confirmed by the exact full-text Jaccard (`confirm_pair`); the estimate is recorded for the confusion table only and filters nothing. The fixture now calls the production `candidate_pairs` and `confirm_pair` (so its predicate is the production predicate), includes the two counterexamples by construction (they are among the exposed units) and a 60-variant large-bucket case (1,770 of 1,770 pairs proposed and confirmed, one cluster). The coverage formula is restated as a statement about prefix-signature similarity, not a recovery guarantee for full-text pairs. Rebuilt and finalised as v0.3 (D4 retained): 3,095,016 candidates, 85,442 at or above the threshold, 7,097 unions (the prefilter had discarded two qualifying edges), 2,610,020 clusters, audit PASS on the finalised map; v0.2 kept as the record | `tools/corpora_partition.py`, `tools/test_dedup.py`, `outputs/corpora_units_v0.3/`, `outputs/corpora_audit_v0.3.json`, `CORPORA_AUDIT_v0.3.md` |
| F9 cell scope self-reported | major | **Accepted.** The accessor binds the units-metadata digest (`units_v0.3.sha256`, written at finalisation; the lock must carry it) and derives each requested unit's source, language and token count from the bound metadata; a unit outside the requested cells by source or language, or failing the cell's length (books 1,000 + L), is refused; the log records the SHA-256 of the sorted requested ids. Seventeen fixture cases pass, including a wrong units digest, a unit outside the cell by source, and a unit failing the length | `tools/corpora_access.py`, `tools/test_seal.py` |
| F10 reconciliation mismatches not quarantined before counting | major | **Accepted.** A per-file acceptance step in the partition (decompression, accounting identity, zero unparseable lines, card or footer reconciliation) excludes a failed file before clustering with its reason recorded; the audit reports excluded files and treats them as outside every count; the loader's own quarantine stays. (The clean-but-short and malformed-input fixtures are an open item: see "carried forward".) | `tools/corpora_partition.py` (`file_acceptance`), `tools/audit_corpora.py` |
| F11 driver control flow | major | **Accepted.** The driver refuses an existing final version before any write; stops on a P1, P5 or P6 failure before expansion or finalisation; passes the selected units directory to the loader through the environment; exits non-zero when the final audit is not PASS; the `--allow-overwrite` option is removed from the partitioner | `tools/corpora_build.py`, `tools/corpora_partition.py` |
| F12 the record overstates the D4 evidence | major | **Accepted.** Ranges and counts restated from the report in the memo §6 and the response; the characterisation withdrawn and replaced by a measured, metadata-only comparison of the finalised D4 map with a scratch run of the same v3 procedure at the pre-set rule (`outputs/dedup_d4_additions_2026-10-09.json`): 4,899 units newly in multi-member clusters, 4,475 of them Wikipedia (Arabic 2,675; Chinese 1,299), predominantly templated short articles; the rest republished news, network-wide Stack Exchange posts and book editions. The corrected evidence is put to Yichen in the reply; D4 stands as recorded unless he revisits it | memo v0.3 §6; log |
| F13 stale pointers; "enforced away" | minor | **Accepted.** `DATA_LAYOUT.md`, the orientation §2 and the handoff's results paragraph point to v0.3 with the v0.1/v0.2 counts labelled superseded; the overlap sentence replaced by the implemented guarantee and the residual limitation | those files |

## Carried forward (not blocking, to be done before the data are used scientifically)
- Tiny fixtures for F10's failure paths (a clean-but-short news file; a malformed line; a decompression failure) exercising the partition's acceptance and the audit's EXCLUDED reporting.
- A synthetic control-flow test of the driver (an audit with P5 false; a count failure selecting the next P8 shard; a non-PASS final audit) with command capture.

## Disputed findings
None.

## Decisions for Yichen
None required: D4 stands as recorded (the reviewer did not reopen it); the corrected evidence is reported so that he may revisit it if he wishes.

## Next
Round 3 prompt for Codex: "re-review R02 round 3: read `research/reviews/R02_data-verdict/RESPONSE_claude_r2.md`, then `research/corpora/CORPORA_AUDIT_v0.3.md`, `DATA_LAYOUT.md`, `outputs/corpora_audit_v0.3.json`, `outputs/corpora_units_v0.3/partition_summary.json`, `outputs/dedup_validation_2026-10-09.md`, `outputs/dedup_d4_additions_2026-10-09.json`, the code (`tools/corpora_partition.py`, `tools/corpora_access.py`, `tools/test_seal.py`, `tools/test_dedup.py`, `tools/audit_corpora.py`, `tools/corpora_build.py`) and the decision-log entry of 2026-10-09 headed 'R02 round 2'; re-check F8–F13 and any residual of F1–F7; write `REVIEW_codex_r3.md` ending in `VERDICT: AGREE` or `VERDICT: REVISE`."
