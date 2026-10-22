# R01 — conductor's response, round 2

Date: 2026-10-09. Reviewer memo: `REVIEW_codex_r2.md` (baseline `769332a`; VERDICT: REVISE; F1–F11 dispositions plus new findings F12–F19, with F14 and F15 blocking). Conductor: Claude (Fable 5.1). Every factual claim was verified before any change.

## Verification of the reviewer's round-2 claims
| Claim | Checked | Result |
|---|---|---|
| The Qwen Instruct failure is logged (`llama3b_offline.log` lines 1–3) | the file | **Confirmed; my round-1 table was wrong** (I had grepped only the other log). Corrected in `RESPONSE_claude_r1.md` with a dated note |
| Common Pile pinned files are gzipped JSON lines (`*-dolma-NNNN.json.gz`), not Parquet; news original 98,092,770 bytes against the viewer's 152,673,253-byte Parquet | the census JSON (file examples and byte totals) | Confirmed; the audit's P5 was not executable as written |
| Gutenberg has no `created` field | the census features | Confirmed |
| Exact variance with g = m/V; the ratio Var/I = (V − 1/C_cond)/(V − 1) with C_cond = A/B; the V = 4, m = 2 example gives 1/18 and reduction 3/11 | re-derived; enumerated over all 36 key pairs with exact fractions | Confirmed |
| Occupancy collision 1/6 → 5/27 (not monotone); limiting variance g(1−g)(V − s)/(s(V − 1)) on a support of s tokens | re-derived | Confirmed |
| The transfer counterexample (V = 4, m = 2, h = 0, M = 2): mean term zero for every key; calibrated FPR 0 on P′ and 1/2 on P for keys {1,2} and {3,4}; SDs 0.2357 and 0.1179 at threshold 3/4 | enumerated over the six keys | Confirmed |
| 0.99^299 = 0.0495363; the identity needs continuous scores and strict rejection, an upper bound for discrete scores | computed; reasoned | Confirmed |
| φ should be evaluated at z_α√v0/σ, not z_α; serial dependence can lower the long-run variance | reasoned | Confirmed |
| Stale passages: gate lines 8, 41, 49, 66, 70, 79; brief line 55; orientation §1; handoff next steps | grep | Confirmed, all present before this round |
| Two Gutenberg shards give about 1,479 held-out books (below the 2,500 floor) | 55,454 × 2/15 × 0.2 | Confirmed |
| Gloaguen et al. already measure a per-key FPR on a real text law, so residual-gap item (i) was false as written | the gate's own table | Confirmed |

## Findings and dispositions
| Finding | Severity | Outcome | Action (file, section) |
|---|---|---|---|
| F12 incompatible conventions in the "exact" and local formulas | major | **Accepted.** g = m/V defined and used; centring at g with the γ offset noted; C_cond = A/B defined and the exact ratio and reduction given; the level approximation written with the detector's centre b, v0 and φ(z_α√v0/σ); "serial dependence can raise or lower σ_k"; the random-M mixture stated; the calibration identity with its continuity, strict-rejection and tie conditions; ideal identities separated from PRNG implementation | gate v0.2 §Residual gap items 1, 2, 4, 7 |
| F13 occupancy monotonicity and zero saturation asserted without conditions | major | **Accepted.** The monotone claim withdrawn with the reviewer's counterexample recorded; the saturation level conditioned on the support (the s < V limit recorded); M_L = 0 handling and the two retention rules (all distinct tuples; first occurrence per context) distinguished; H-width restricted to projectively consistent raw laws with occupancy weights excepted; T1 allows non-zero saturation and non-monotone curves | gate v0.2 items 3, 5; targets |
| F14 the PAC transfer target is not controlled by the mean-shift term | **blocking** | **Accepted.** H-transfer now states that the exact signed-weight variance controls the difference of means only, with the counterexample recorded; T2 reformulated as a score-tail discrepancy statement (Δ_k = sup_t |P(S_k > t) − P′(S_k > t)|, α_P ≤ α_P′ + Δ_k) or a location-family approximation with tail control, the mean-shift identity as one component; T3 declared a regime-specific empirical predictor; a theorem is claimed only if T1 or T2 is proved (brief and gate verdict changed accordingly) | gate v0.2 items 5, 7, targets, verdict; brief §Research question |
| F15 the selected files cannot satisfy the Parquet-based plan | **blocking (for the freeze)** | **Accepted.** Formats corrected everywhere: Common Pile shards are Dolma JSON-lines `*.json.gz` with their Hub byte sizes; the viewer's Parquet is not used; P5 rewritten per format (decompressed record counts and unparseable lines for JSON shards, exact reconciliation only for the complete news file, card totals as whole-source comparators; Parquet footers for Wikipedia); pinned paths named; sizes separated | audit §§2, 3, 4 (P5), 6, 7 |
| F16 cluster assignment and expansion not deterministic enough | major | **Accepted.** Canonical identifiers, normalisation, exact and MinHash parameters (128 permutations, seed 20261009, 16 × 8 LSH, Jaccard ≥ 0.8), union–find transitivity, cluster identity (smallest canonical id), one representative per cluster, cluster-level forcing of the exposure record, the order freeze → audit → expansion → clustering → assignment → seal → use, and quarantine of later cross-partition links, all written down | audit §5 |
| F17 P7's fallback removed its floor; the book budget did not support it | major | **Accepted.** Mandatory confirmatory cells named; floor ≥ 2,500 held-out eligible units, binding; a cell below the floor after the capped expansion is excluded from confirmatory claims before the lock, with no other fallback; Gutenberg initial shards raised to four; the book window rule made explicit (tokens [1,000, 1,000 + L), eligibility ≥ 1,000 + L retained tokens); precision stated as nominal relative standard error at a true rate of 1%; sites and outlets declared descriptive strata; P8 capped with a fixed order and a FAIL outcome | audit §§3, 4 (P2, P4, P7, P8) |
| F18 no terms record for the new sources; no valid common vintage schema | minor | **Accepted.** Three rows added to `TERMS_OF_USE_CHECK.md` quoting the cards and the first-row labels, with the allow-list rule; the superseded rows marked; a per-source vintage schema with "unknown" for Gutenberg; "pre-LLM by a century" and the "no overlap" assertion withdrawn (overlap is enforced by deduplication) | terms; audit §§3, 7 |
| F19 active summaries still repeated withdrawn claims | major | **Accepted.** Gate: the candidate paragraph ("uncharacterised and unremedied" removed; comparators' guarantees and retention rules named), residual-gap item (i) corrected to "beyond one appendix measurement", the "meaningful" paragraph's "closed-form dispersion law" replaced, "first" → "earliest located" (occupied list, competitor row, wording constraint 1), the v0.1 data-feasibility paragraph labelled superseded with a current paragraph; brief: the one-sentence question revised (guarantee by method; key-independent null law; retention rule); orientation §1 rewritten; handoff next steps updated; the round-1 response's log statement corrected | gate v0.2; brief; orientation; handoff; `RESPONSE_claude_r1.md` |

Round-1 findings: F1–F3 now resolved through F12–F14; F4 closed by D2 and the terms rows (F18); F5 closed by the format correction (F15); F6 closed by D3 and the deterministic specification (F16); F7 and F8 closed by F17; F9 closed by the target wording and the vintage schema; F10 resolved for this checkpoint conditional on the Stage 5 timing gate (recorded in the brief, the gate's current data paragraph and the audit); F11 closed by F19.

## Disputed findings
None.

## Decisions for Yichen
None new: D1–D3 stand; nothing in round 2 reopens them.

## Next
Round 3 prompt for Codex: "re-review R01 round 3: read `RESPONSE_claude_r2.md`, then the changed files (`research/KEYCOND_GATE_v0.2.md` §Candidate, §Residual gap, §Data and precision feasibility, §Verdict; `research/corpora/CORPORA_AUDIT_v0.1.md`; `research/corpora/TERMS_OF_USE_CHECK.md`; `research/PROJECT_BRIEF.md` §Research question; `research/reviews/REVIEW_ORIENTATION.md` §1; `RESEARCH_HANDOFF.md`); re-check F12–F19 and any residual of F1–F11; write `REVIEW_codex_r3.md` ending in `VERDICT: AGREE` or `VERDICT: REVISE`."
