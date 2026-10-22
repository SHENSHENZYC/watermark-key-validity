# R05 — Study 2 protocol, independent review, round 3

Date: 2026-10-12. Reviewer: Codex. Scope: F9–F11 and their fixtures, as requested.

## 1. Baseline and material read

Reviewed `main` at **`afd2323e2a710454e0ba5180b6430f529e7d5961`**, comparing the implementation with the round-2 baseline **`8a7d450a6926e49a75ca2c7ab3ffc71e5f7c46f5`**. The working tree was clean at the start.

I read `RESPONSE_claude_r2.md`, the specified runner/analyzer/validator diff, the regenerated `VALIDATION.json` inventory and pilot-path fixtures, and protocol §§9 and 11 in the requested order. I also checked the review instructions and prompt, the relevant consumer functions, and the corresponding log/handoff changes. This is a bounded re-review; it does not reopen the predictor, language analysis, design or literature assessment accepted in round 2.

Checks were short and local: in-memory mutations of retained synthetic pilot records, analyzer and reuse calls, a small bound calculation, byte comparisons and hashing. No validator, inputs pass, runner probe or production run was executed. No raw text was read, no download was made, and no existing file was changed.

**Assessment: F9, F10 and F11 are resolved.** The requested malformed records are refused, the two legitimate exceptions remain accepted, and the consumers no longer depend on the formerly trusted flags/bounds. One non-blocking wording correction to the new contract description is recorded as F12 below.

## 2. Claims against evidence

### F9: decision values and structural zeros

`_finite` excludes booleans and non-finite numeric values. `_interval` checks the two-element shape, finite endpoints, ordering and bounds. The completed contract validates the exact reference mean and KL bound before reconciliation, derives structural-zero status from the reference mean and counts, requires a finite nonnegative SD bootstrap SE, and checks SD/ratio intervals and their algebraic consistency with a positive predicted SD. The registered undefined-ratio case at zero prediction remains available.

`rule_s2` now recomputes the bound from the rejection counts and exact reference mean, and derives the structural zero itself. As an additional consumer check, I passed an in-memory all-rejecting Gumbel distinct-rule record directly to S2 with deliberately corrupted stored NaN bounds and true structural-zero flags. Despite bypassing the gate, S2 returned **3 checks, 3 flags, pass=false**. Those same malformed fields are rejected by the gate in ordinary use.

### F10: deployer selection and complete records

The contract requires the stored deployer flag to equal the membership derived from the grid. `deployer_block` independently selects from that grid membership, with the pilot specification passed through correctly. Exactly the five registered point-quantile keys are required. Each promised crossed statistic must contain a finite ordered interval and a finite nonnegative SE, with B=200.

The genuine pilot loads as **66 cells, all 66 live**, with **54 S2 checks and 36 deployer rows**, matching both the grid-derived count and `fixtures.pilot_rule_paths_exercised`. To distinguish consumer selection from gate validation, I also cleared every stored deployer flag *after* loading; direct `deployer_block(..., pilot=True)` still produced **36 rows**.

### Independently rerun refusal probes

Each mutation below was intercepted in memory at the read of one retained Gumbel distinct-rule deployer cell. Both full pilot inventory loading and runner reuse were tested against the same altered body and otherwise unchanged provenance.

| Mutation | Analyzer inventory | Runner reuse |
|---|---|---|
| NaN KL bound | Refused | Refused |
| False structural-zero flag | Refused | Refused |
| Reversed ratio interval `[1.4,0.8]` | Refused | Refused |
| Reversed SD interval | Refused | Refused |
| NaN SD bootstrap SE | Refused | Refused |
| False deployer flag | Refused | Refused |
| Missing deployer flag | Refused | Refused |
| Empty quantile dictionary | Refused | Refused |
| NaN point quantile | Refused | Refused |
| Null crossed-statistic values, **preserving B=200** | Refused at the populated-statistic check | Refused |
| Crossed B=100 | Refused | Refused |
| Exact reference mean 1.5 | Refused | Refused |

Preserving B=200 in the null-value probe matters: the saved validator mutation nulls B too, so its recorded refusal reaches the B check first. My independent probe reaches the nested-value check and confirms that branch as well. This is a verification distinction, not an unresolved implementation defect.

### Independently checked acceptance cases

The retained pilot contains **20 genuine KGW structural-zero alpha rows** and its complete inventory is accepted. For example, `syn_zipf_V128256_s1.0__synthetic__kgw__h0__independent__g0.25__L64__first.json` at alpha=.01 has exact reference mean 0, all rejection counts 0 and KL bound 1; its body passes the contract unchanged. This supplements the validator's constructed structural-zero fixture with a record produced by the detector itself.

For the flagged zero-prediction exception, I set each alpha's predicted SD to zero with `flags=["sigma2_nonfinite"]`, ratio NaN and ratio interval `[NaN,NaN]`, retaining the finite observation summaries. Inventory loading, runner reuse and pilot analysis all accepted this registered exception; all 66 cells and all 36 deployer rows remained present. The saved `valid_structural_zero_accepted` and `flagged_zero_prediction_accepted` results therefore have independent supporting checks.

### F11: exact-mean versus nominal-alpha power

The contradictory blanket sentence is gone. Section 9 now identifies the 20 KGW exceptions at nominal .01, excludes Gumbel at .01, and states the absence of under-rejection flags at .001 for the registered cells. From the unchanged inputs, the cited Gutenberg/Llama/h=4/L=64/distinct/gamma=.25 example has exact mean **0.015256744922904153**. Direct evaluation of `2*(1-mu)^1000` gives **`4.2077005088567284e-7`**, matching the corrected prose and falling below `1e-6`.

## 3. Method, statistics and constants

No scientific constant changed. The grid and `s2_core.py` are byte-identical to `8a7d450`; the diff changes validation and consumption of recorded quantities, not N/K, alpha, gamma, widths, retention rules, predictors, resampling counts or S1–S5 decision thresholds. `QUANTILE_KEYS` repeats the existing five quantiles and `CROSSED_B=200` repeats `s2_core.BOOT_CROSSED`.

The new integrity helpers introduce two numerical details worth stating explicitly alongside the contract: `_interval` allows `1e-12` slack at range boundaries, and ratio/ratio-interval reconciliation uses `1e-9 * max(1,1/sd_pred)`, corresponding to scaling the SD reconciliation allowance. These are numerical integrity allowances, not changed scientific decision constants.

The regenerated §11 traces to validation run `20261013T020201Z`. Its pilot counts match my direct analysis. The saved runner probe is now 817.1 seconds and 4.2 GiB; the saved fitted projection is 6.08 hours and the stated probe-scaled projection remains 8.1 hours. These are new timing observations, not changed design constants. I read the records rather than rerunning the long measurements. The previous round's statistical qualifications and recommendation to retain D8 remain unchanged.

## 4. Process and unchanged records

Independent byte comparisons with `8a7d450` confirm that all four input records are unchanged: `INPUTS.json`, `tokens_manifest.json` and both superseded input files. Their current principal hashes remain:

- Inputs: `35da63acce7a914a947368414be01e75b63cbbae4150792e8b446dcf4e46b55b`.
- Token manifest: `07e8a00558234fdfc64922d6d6363f1ce158aece12d17249210a725f28494e3c`.
- Grid: `709f6adfd9b68708fb3c47599b92837fed30eb56053ee3a8cbd25c5ed8d0558a`.

All **20 token-array digests**, shapes and dtypes match that unchanged manifest. There is no Study 1 file change in the Git diff. All **eight Study 1 lock hashes** match, the lock's hash matches its run manifest, and independently hashing all **1,248 production cells** reproduces the run-manifest inventory digest. The Study 2 production lock, production cells directory and holdout-opening log remain absent.

The log and response accurately describe the three scoped corrections. The protocol remains a draft pending the review resolution and Yichen's separate decision. No scientific rule was changed after outcomes. This bounded review required no new terms-of-use assessment, external access or literature quotation; the prior review's attribution and wording constraints remain applicable.

## 5. Independent search

No new occupant search was performed: the user bounded this round to F9–F11 and their fixtures. Web access is available, but no novelty or current search-absence claim is made here.

## 6. Findings and recommendations

**F9 — formerly major: closed.** All requested decision-value refusals pass independently, S2 derives its bound and structural-zero status, and the registered zero cases remain accepted. No further change to the scientific rule is recommended.

**F10 — formerly major: closed.** The grid controls deployer membership at both validation and consumption; malformed flags and incomplete quantile/crossed records are refused by inventory and reuse. The pilot emits the expected 36 rows. No further change to the subset or uncertainty calculation is recommended.

**F11 — formerly minor: closed.** The corrected exact-mean qualification and numerical example agree with the frozen inputs and the bound.

### F12 — Minor, non-blocking: restrict the new recomputation claim to S2

**Evidence.** The revised §9 integrity paragraph says: “S2 and S3 decide on quantities recomputed from the counts and the exact means after this validation, never on a stored flag or bound alone.” Only S2 received that change. The unchanged `s2_analyze.py:188–195` still reads S3's `var_known_mean`, exact variance, SE, tolerance and structural-zero flag from the stored `q_hat`/`s_bar` block. Rejection counts do not determine those score-moment statistics; protocol §3 already explains that the stored S3 estimates and SEs are the record.

**Inference.** This is an overstatement in the description of the F9 fix, not a newly identified fault in S3 or a reason to reopen that previously reviewed estimator.

**Recommendation.** Remove “and S3” from the new recomputation sentence, retaining the existing S3 record description. Also state the two numerical integrity allowances identified in §3 of this memo if §9 is to enumerate every tolerance literally. These are documentation corrections suitable for the resolution before locking; they do not require a new scientific protocol, a new long validation run, or another review round on the evidence examined here.

VERDICT: AGREE
