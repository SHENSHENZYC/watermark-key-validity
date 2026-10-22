# R06 — the Study 2 report: resolution

Checkpoint: R06, the Study 2 report (Stage 6 exit for Study 2: the locked run on the frozen null corpora, its analysis under the lock, the record, the generated report v0.1, the builder, fixture, manifest and overlap scripts). Conductor: Claude (Fable 5.1, in Claude Code). Reviewer: Codex. Rule A7 of the research-project-guide.

## Rounds

| Round | Baseline | Verdict | Findings | Outcome |
|---|---|---|---|---|
| 1 | `23ed55a` (2026-10-13) | REVISE | F1–F7 major, F8 minor: the post-hoc tokenizer computation's denominator and estimand; "transfers" and two false correlation comparisons; the categorical attribution of the predictor's bias; registered outputs missing from the report (the 1% and 5% deployer quantiles, the population diagnostic, the key-count resolution, the unit-σ occurrences, the six S1 counts by width); the finite-text benchmarks stated as variance attributions; "inflated for every key"; missing named attribution; Table 12's caption and the "most of the vocabulary" sentence | every finding verified by the conductor's own recomputation and accepted; applied on the unpinned report path (`RESPONSE_claude_r1.md`, commit `9db4bd5`) |
| 2 | `9db4bd5` | REVISE, bounded to F9–F12 | the all-live-cell pairwise and heterogeneity supplement still missing; S4's summary still inferring a mechanism from the tolerance decision and misdescribing the news h = 4 chains and the overlapping groups; the Table 5 medians' denominators and the "absent" wording; two typed outcome counts and a typed 1.46 in the log | every residual verified and accepted; applied (`RESPONSE_claude_r2.md`, commit `f0a65cb`) |
| 3 | `f0a65cb` | **AGREE** (bounded) | F9–F11 closed; F12 closed except three worded chain counts in the template, a minor non-blocking residual | the residual applied in this resolution commit (the three counts now generated: `s4_hold_h4_n`, `s4_fail_h1_n`, `s4_fail_h1_nonnews_n`; a scan of §§5–8 for number words beside outcome nouns finds only design counts left: one fixed key, the ten corpus cells, the five non-English cells, the two production cells of a tokenizer pair) |

## What changed across the rounds, and what did not

Changed (all on the unpinned report path; the report regenerated after every change with the builder's independent re-computation equal to `results.json`): `research/study2/s2_report.py`, `research/study2/report_prose_v0.1.md`, `research/study2/tokenizer_overlap.py` and its outputs (`report/tokenizer_overlap.json`; the first, erroneous output kept as `report/tokenizer_overlap_superseded_r1.json`), the report `research/STUDY2_REPORT_v0.1.md` and the report directory (new supplements `tables_population_full.md`, `tables_key_counts_full.md`, `tables_pairwise_full.md`; the deployer tables with the 1% and 5% quantiles and K / N_eff; the diagnostic supplement with the unit-σ block; the six S1 counts by width; the corrected captions, headings and interpretation).

Unchanged, confirmed by the reviewer at every round: the locked protocol and the fifteen pinned files (every hash equal to the lock; no change after the lock commit `b0e0036`), the record (`outputs/study2_v0.1/cells/`, `run.log`, `run_stdout.log`, `launch_notes.log`, `results.json`, `RUN_MANIFEST.json`; no change after `61fda20`), the five registered verdicts (S1 PASS, S2 PASS, S3 PASS, S4 FAIL, S5 PASS; the reviewer reproduced them independently at round 1), the six figures (the PNGs byte-identical to `61fda20`; the SVGs differ by matplotlib's date and element ids only), `final: false`.

## The agreed state

The report v0.1 as regenerated in this resolution commit, with its §5 observations labelled as the conductor's reading, its §6 interpretation labelled as inference for the claim gate, its §7 limitations, and its §8 open items (the wording of the predictor's validity on real text; H-length's scope as registered with its three overlapping failure groups and any narrower hypothesis post-hoc; the unit-σ text/code discrepancy as a standing rule for the next protocol; the overlap computation's place; Study 3's design inputs and transfer hypotheses; the figures for the paper). The agreed commit is the one carrying this memo (named in the decision log).

## Carried forward

- For the paper: keep the medians' denominators explicit (resolved against eligible sets); keep the attribution of the phenomenon, the mean-shift mechanism and the per-key measurement to the published record with full bibliographic details; state H-length with every observed exception visible; treat the population diagnostic and the finite-text benchmarks as descriptive references.
- For Study 3: the transfer hypotheses of §6 Q4 (within-English, cross-language, cross-tokenizer calibration transfer) are to be tested with the calibration-sample error and the evaluation on the target law measured; the predictor's bias at γ = 0.25 belongs in the baseline's error budget; the within-tokenizer cross-language tuple overlap can be computed key-free as the across-tokenizer overlap was.
- For the next protocol: list the protocol's promised report blocks beside the analyzer's functions before the lock (the unit-σ lesson); state every reported output's estimand and denominator in the report builder's contract.
