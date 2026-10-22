# R05 — Study 2 protocol, independent review, round 2

Date: 2026-10-12. Reviewer: Codex. Checkpoint: Stage 5, before the Study 2 lock.

## 1. Baseline and scope

Reviewed `main` at **`8a7d450a6926e49a75ca2c7ab3ffc71e5f7c46f5`**, against the round-1 baseline **`54a2c65af7d9dfa45b033f99a031c87fdd62a367`**. The working tree was clean when this review began.

I read the root `AGENTS.md`, the review orientation in full, and the checkpoint prompt. Following the round-2 order, I read `RESPONSE_claude_r1.md`; the changes to `s2_core.py`, `s2_run.py`, `s2_analyze.py` and `s2_validate.py`; the regenerated validation record; the current and both superseded input records; the protocol's changed passages and regenerated §11; and the round-1 decision-log entry and handoff corrections. I also inspected the `s2_inputs.py` and `s2_protocol_fill.py` changes, the relevant unchanged helper functions and grid, the token manifest and seal metadata, and Study 1's lock and run-manifest digests.

Independent checks were short, local, and read-only: hashing, recursive JSON comparisons, small numerical integrations, the retained synthetic pilot's inventory and analysis, and synthetic/in-memory malformed-record probes. I did **not** run the validator, inputs pass, production-scale runner probe, or study runner; read raw corpus text; download anything; or alter an existing file. Timing and memory measurements below are traced to the retained validation and its implementation, not independently re-measured.

**Assessment:** the numerical predictor fix, language calculation, frozen inputs, and revised compute evidence withstand this re-check. The main remaining issue is an incomplete record contract: malformed decision fields can still turn an audit failure into a pass, and a stored deployer flag can still suppress required descriptive rows. The retained pilot itself does not contain the malformed values used to demonstrate these defects. Findings F9–F11 below continue the numbering from round 1.

## 2. Claims against evidence and derivations

### Disposition of F1–F8

| Round-1 finding | Evidence checked at this baseline | Disposition |
|---|---|---|
| F1: silent loss of live slots | `validate_cell_body` requires integer `N_eff == N`, rejects a marker/flagged body, and is called by both inventory loading and runner reuse. The study lock check now precedes inventory listing. The retained pilot loads as 66 cells, all 66 live; missing/zero `N_eff` are independently refused. Pilot analysis reaches 8 S1 candidates, 3 S4 chains and 2 S5 chains. | The live-slot defect is fixed. The related requirement to derive deployer membership from the grid is not enforced by the descriptive consumer: F10. |
| F2: unchecked rejection counts | Counts must have length K, be integers in `[0,N_eff]`, reproduce the principal summaries within `1e-9`, and nest across alpha. The recorded negative, fractional, over-range, contradictory-summary and nesting refusals have corresponding implementation branches. The original malformed-count defects are addressed. | Partly fixed: finite decision values, structural-zero consistency and interval validity remain unchecked, contrary to the round-1 recommendation. F9. |
| F3: seven pools and all-zero disparity | The language set is selected by `source == "wikipedia"` and `L_cell == 256`. All-zero, some-zero and all-positive keys are separated, with ratios only over the last group. | Fixed. Independently exercised both the helper and the full production slot selection with synthetic level vectors. |
| F4: missing crossed 1% quantile | `crossed_bootstrap` now computes `q0.01`; all 36 crossed blocks in the retained pilot contain it and the other seven promised statistics. Removing `q0.01` is refused. | The computation/storage omission is fixed. The contract still accepts empty nested values and can omit the entire deployer row through its flag: F10. |
| F5: text-bootstrap stream claim | §8 now identifies the downstream Monte Carlo draws that change. `study1_fields_identical` distinguishes the B=30 equivalence from the deterministic B=5 comparison and names the N=600, L=256 fixture accurately. | Fixed. This does not promise identical bootstrap or subsample realizations at B=5. |
| F6: Gaussian quadrature at zero residual variance | Both Gumbel prediction call sites and `s2_inputs.py` use `mixture_gaussian_closed`; KGW's per-text cross-check does too. The simulated-shift sample still uses direct averaging. | Fixed. Independent integration and boundary checks are described below. |
| F7: rare-key precision and dead-detector prose | The Bernoulli SD uncertainty, empty-tail bootstrap limitation, nominal interval qualification, eligibility interpretation and endpoint/tie/tail counts are now stated. The validator reports the exact-mean dead-detector counts. | Substantially fixed; one surviving sentence contradicts the corrected dead-detector calculation: F11. |
| F8: grid provenance and timing | The current grid hash matches `INPUTS.json`, the validation's input hash matches the current input file, the reviewed input is preserved byte-for-byte, and the log corrects the historical rates. The runner probe and its scaling are disclosed. | Fixed. Scientific input quantities are unchanged except for evaluating Gumbel predictions by the closed form; regenerated operational timings also change. |

The saved `fixtures.analyzer_inventory` refusals are supported by the relevant branches, and its no-lock test now reaches `study mode requires --lock`. Its passing result should not be read as validation of malformed values it never tests; F9 and F10 identify those gaps. The pilot's eight S1 candidates are all ineligible at its N=600 setting. It exercises candidate/grouping paths, not every eligible/resolved S1 branch. This is a limit of the fixture, not a change to the production rule.

### Per-text Gaussian closed form

Write `pi_i(d) = Phi_bar((tau_i-d)/sigma)` and `m(d) = N^-1 sum_i pi_i(d)` under the stated common-factor model. For `delta ~ N(mu,var)`, let `a_i = (tau_i-mu)/sqrt(var+sigma2)` and `r = var/(var+sigma2)`. Then:

- `E m = mean_i Phi_bar(a_i)`.
- `E m^2 = mean_{i,j} P(Z_i > a_i, Z_j > a_j)` for standard bivariate normal variables with correlation r, including a pair of conditionally independent residual draws when the thresholds coincide.
- `Var_delta(m) = E m^2 - (E m)^2`.
- The additional conditional Bernoulli variance of the finite-text rejection fraction is `[E m - mean_i P(Z_i > a_i, Z_i' > a_i)]/N`.

The multiplicity weights, full threshold-pair average, diagonal term and final floor in `s2_core.py:156–185` implement these expressions. This is an exact evaluation of the **assumed Gaussian common-factor model**, not an exact Gumbel rejection-level law. The protocol preserves that distinction.

I checked varying thresholds `[1.3,1.8,2.3,2.3,2.8]`, mu=0.2, at `(var,sigma2)` equal to `(1,0)`, `(1,1e-6)`, `(1,.001)`, `(.04,.9)`, `(0,.9)` and `(0,0)`. Independent one-dimensional adaptive integration, split around the transitions, or direct interval-probability evaluation at sigma=0 agreed in the mean, population variance and floor to a largest absolute error of **`4.03e-16`**. A fully deterministic mixed-threshold case, mu=2.3 and both variances zero, gives mean 0.4 and both variance terms zero, respecting strict rejection. With var=0 and sigma positive, population dispersion vanishes and only the finite-text floor remains. At sigma=0 and var positive, the floor vanishes and the threshold-dependent indicator mean retains its across-key variation.

The retained fixture additionally reports exact agreement with Study 1's one-threshold closed form at sigma2 in `{0,1e-6,.001,.5,1}`, and a `2.80e-16` SD difference from the old quadrature at an ordinary residual variance with 799 distinct thresholds. Its 400,000-draw tiny-sigma comparison is a Monte Carlo sanity check; the direct integration above supplies a more precise independent check without rerunning that fixture.

### Language and crossed uncertainty

On synthetic count vectors attached to every expected production slot, `correlations` produces **24 language blocks, each containing exactly six languages**, and excludes `wikipedia_en_1024` from every language block. It produces 24 between-corpus matrices and 1,020 tokenizer comparisons. A four-key helper example with one all-zero key, one some-zero key, and positive max/min ratios 1 and 6 produces counts `(1,1,2)`, shares above 2 and 5 of 0.5, median ratio 3.5 and maximum 6. Pairwise difference SDs use all four keys. This matches §7's denominators and zero conventions.

Every retained crossed block has B=200, finite nonnegative SEs and ordered intervals in `[0,1]`. Small all-zero and all-one rejection tables give the expected degenerate intervals for the new 1% quantile as well as the maximum and exceedance shares. Adding this quantile consumes no additional random draws within the bootstrap loop.

### Literature checks

The changed implementation does not alter the prior-work positioning. I rechecked the decisive local text substrings and PDF-page boundaries:

- AutoMark, `research/literature/txt/2609.37310.txt`, PDF p.3: “a specific deployed key can still exhibit a high false positive rate.”
- Jovanović et al., `2506.16349.txt`, PDF p.27: “if similar effects can be observed in LLM watermarking.”
- Gloaguen et al., `2509.24368.txt`, PDF p.21, Table 2: sampled maxima 17.0%, 1.7%, 1.1% and across-key SDs 1.2%, 0.3%, 0.1%.
- Three Bricks, `2308.00113.txt`, PDF p.7: the exponential-score sum's Gamma law.

These support retaining the attribution and ideal-null qualifications; they do not validate the newly implemented common-factor approximation on real text.

## 3. Method, statistics, precision and rule boundaries

The scientific grid and decision thresholds did not change. I compared the rules and numerical literals in the core/analyzer with the grid and §§3, 5–9. The governing constants match:

| Item | Registered and implemented value |
|---|---|
| Production precision | N=10,000; K=1,000, including fixed h=0 |
| S1 | KGW independent, gamma=.25, raw/distinct, h=1–4, alpha=.01; mean M>=30, theory share>=.75, no model flag; interval inside `[2/3,3/2]`; >=30 resolved, >=80% consistent |
| S2 | Distinct rule, KGW independent and Gumbel; three alphas; two-sided KL bound strictly below `1e-6` |
| S3 | Exact known-mean fourth-moment SE, or fixed-colouring key bootstrap; gross deviation beyond `6 SE + tau`; scale tolerance `1e-9`; Exp(1) fourth cumulant 6 |
| S4/S5 | Adjacent observed SDs; tolerance `2(se+se')`; S4 raw length chains, S5 raw/distinct width chains at longest length |
| Resampling | Keys 200, two-way 100, texts 5 in production/30 for equivalence, crossed 200 |
| Other diagnostics | Two disjoint 300-text pairwise samples; 2,000 heavy tuples and 20,000 simulated shifts; 1%, 5%, 50%, 95%, 99% key quantiles; shares above 2alpha and 5alpha |
| Integrity | N_eff=N; reconciliation tolerance `1e-9`; nested counts; key chunk 8; registered seeds unchanged |

The inherited numerical guards and model flags remain in place. The newly listed `1e-9` reconciliation tolerance is explicit. The 200-node Gauss–Hermite constant is still listed in §9, but now belongs to the retained validation comparison rather than a production Gaussian predictor; that role should be labelled when cleaning up the text. I found no new outcome-selection threshold or undisclosed change to S1–S5.

S1 eligibility still controls the relative finite-text floor rather than rare-key precision. The revised Bernoulli approximation gives a relative SD-estimation SE of about **15.6%** at p=.01, K=1,000, versus the **2.24%** normal benchmark. The endpoint and tie summaries are useful context, not a coverage guarantee. I independently recover **153/544** eligible primary cells at N=4,000 and **217/544** at N=10,000. The latter's unchanged width counts are 136, 60, 15 and 6; rule counts 116 raw and 101 distinct; tokenizer counts 86 Llama and 131 Qwen.

S2's dead-detector threshold is `1-exp(log(1e-6/2)/1000) = 0.01440391433775623`. Recounting the frozen inputs gives 20/680 KGW distinct cells above this threshold at nominal .01, all 680 at .05, and none at .001; the corresponding Gumbel counts are 0/340, 340/340 and 0/340. The bound depends on the **exact cell mean**, not just nominal alpha. The 3,060-check union bound remains .00306, under independent draws of the ideal key law and without requiring independence between texts or cells. The residual prose error is F11.

S3's estimator and tolerances are unchanged. S4/S5 remain weak monotonicity checks: structural-zero chains or constant saturated SD chains can satisfy them without establishing strict growth or strict decline. This is consistent with the registered per-chain counts and the absence of a simultaneous guarantee. These mathematical rules are distinct from the malformed-value behavior in F9: a NaN SE must not silently make every adjacent comparison hold.

### Compute evidence and D8

Recomputing the projection from the retained fitted rates and current chain sizes gives:

| N | K | Recomputed hours | Saved rounded hours |
|---|---:|---:|---:|
| 4,000 | 500 | 2.157894 | 2.16 |
| 4,000 | 1,000 | 3.109060 | 3.11 |
| 10,000 | 500 | 3.721955 | 3.72 |
| 10,000 | 1,000 | 6.066895 | 6.07 |

At D8's setting the components are 131.11 s build, 2,762.94 s hash, 11,121.83 s products and 7,824.95 s statistics. The new probe invokes `run_chain` itself at N=10,000, K=1,000, h=4, all five lengths and three rules, producing 45 synthetic cells across both families and both KGW gammas. Its 10,196,162 tuples and 58,919,807 total nonzeros cover the large-chain workload better than the former isolated operation timings. It uses validation keys and temporary outputs.

The saved probe time is **806.7 s**, compared with **601.6 s** and **612.4 s** for the two long Llama h=4 production chains. Applying the larger ratio to the unrounded full projection gives **8.13525 h**, leaving about **1.865 h** under the 10-hour budget. Thus the protocol's 8.1-hour budget basis is reproduced. This remains an extrapolation from one synthetic chain, explicitly described as such, rather than a measured full run.

The process peak is **4.95 GiB** (`ru_maxrss / 2**30`; the JSON field says `gb`), already reached before the probe. It is an upper bound on the probe's own peak within that process, not an additional 4.95 GiB allocation by the probe. The saved evidence supports keeping D8, with a smaller runtime margin than the original 6.26-hour estimate suggested. K=1,000 remains my recommendation for the sampled 99% quantile and primary-band resolution. No new precision choice is needed for the fixes below.

## 4. Process, frozen inputs, Study 1 and wording

**Frozen token content is unchanged.** `tokens_manifest.json` is byte-identical to the round-1 baseline, with SHA-256 `07e8a00558234fdfc64922d6d6363f1ce158aece12d17249210a725f28494e3c`. I independently rehashed all **20 arrays** and checked shape, dtype and stored id bounds; all match. Recomputing all ten pools and seeded draws from units metadata reproduces their pool, seed and sampled-id digests. The seal's partition, units and corpus-manifest digests also match. These checks read metadata and token ids only.

**The input regeneration preserves scientific quantities.** The reviewed `INPUTS_cfc9849grid_superseded.json` is byte-for-byte equal to `54a2c65:outputs/study2_v0.1/INPUTS.json`. Recursive comparisons of both superseded files with current `INPUTS.json` find no changes to chain sizes, KGW quantities/predictions or Gumbel moments. Outside `gumbel.pred`, changes are confined to the grid digest where appropriate and operational metadata: write time, elapsed/build times and peak RSS. Within Gumbel predictions, the method field is added and numerical evaluations change; across all **6,120** Gumbel cell/alpha predictions, the largest change in predicted conditional SD is **`2.09861e-11`**. Thus these realized inputs were not in the numerical regime where round 1's quadrature defect was large; the fix nevertheless makes that boundary correct.

The current grid SHA-256 is `709f6adfd9b68708fb3c47599b92837fed30eb56053ee3a8cbd25c5ed8d0558a`, matching the current inputs. The inputs' SHA-256 is `35da63acce7a914a947368414be01e75b63cbbae4150792e8b446dcf4e46b55b`, matching `VALIDATION.json.projection.inputs_sha256`. Input fields named `mean_level` and `exact_binomial_key_mean_if_distinct` remain key-free predictions; they are not observed levels or `sd_obs` records.

**Study 1 is untouched.** There is no diff from `54a2c65` in the Study 1 code, production record, protocol/report or `tools/key_policy.py`. All eight hashes in Study 1's pre-run lock still match, and the lock's own hash matches its run manifest. Independently hashing the 1,248 production cell files reproduces the run-manifest aggregate `a9fd2cf88b76d76a60fd5040ea50c9c907269f60af04ad4f5416c47c55ca5bc0`.

**Pre-registration remains intact on the inspected record.** No Study 2 production lock or cells directory exists, and `outputs/holdout_openings.jsonl` remains absent. The 1,524 retained provenance-bearing cell JSON files inspected under the Study 1 v0.3 and Study 2 output directories comprise 1,248 starting at key 20,000 and 276 starting at 1,000,000; none starts in the Study 2 production range. The new probe's source uses validation mode and a validation-range offset. These are checks of the available record, not a claim to observe unrecorded past executions. There is no evidence here of per-key production-text outcomes before the lock or of an outcome-driven design change.

The input-adaptive doctrine, D7/D8, pre-lock reduction order and unchanged scientific grid remain as reviewed in round 1. The log and handoff now use the revised projection and explain the superseded timing/provenance claims. The revised predictor and uncertainty prose better separates exact identities, model approximations, nominal intervals and the finite sampled maximum. Gate constraints 1–16 and §12's disclaimers remain in force; no remedy, transfer guarantee, new theorem, priority claim or population extreme is introduced by this revision. F11 is the remaining substantive wording inconsistency I found. The header's old §11 fill date and the unqualified quadrature entry in §9 are minor editorial carryovers, not additional scientific findings.

## 5. Independent search

Web access is available, but I did **not** renew the optional occupant search in this bounded round-2 implementation review. I reread the unchanged 2026-10-10 re-screen and rechecked the local literature passages above. The round-1 search assessment is not upgraded to a claim of absence through 2026-10-12. The recorded arXiv API 429 and the unexamined Elsevier/Springer full texts remain access limits; no blocked endpoint was revisited or bypassed.

## 6. Findings and recommendations

### F9 — Major: malformed decision values and false structural-zero flags still bypass the body contract

**Evidence.** `s2_run.py:237–247` explicitly checks finiteness for the main count summaries, but its KL reconciliation is only `abs(stored - recomputed) > 1e-9`. With a stored NaN, that comparison is false and the record is accepted. The contract also accepts a false `structural_zero` value and does not validate the order of `ratio_boot_ci95` or the finiteness/nonnegativity of `sd_obs_boot_se`. Consumers then use those stored values directly: `s2_analyze.py:165–172` skips structural zeros and compares the stored KL bound; `status_of` at lines 91–97 tests interval endpoints without verifying their order; `chain_monotone` at lines 225–229 compares against the stored SE-derived tolerance.

I reproduced the following entirely in memory, without modifying any retained file:

| Synthetic probe | Contract/consumer result |
|---|---|
| A Gumbel distinct-rule cell with all N texts rejecting under every alpha, nested counts and correctly recomputed count summaries/KL bounds | Accepted; S2 has 3 checks and 3 flags; pass=false |
| The same cell, replacing only its three KL bounds with NaN | Accepted; S2 has 3 checks and 0 flags; **pass=true** |
| The finite-bound all-rejecting cell, setting its three `structural_zero` flags true | Accepted; S2 has **0 checks**, 0 flags; **pass=true** |
| A synthetic eligible KGW record with ratio interval `[1.4,0.8]` | Accepted; `status_of` calls the reversed interval **consistent** |
| A retained pilot body with its SD bootstrap SE replaced by NaN | Accepted; a synthetic decreasing SD sequence `[.1,.01]` with SEs `[NaN,0]` produces no S4 violation |

End-to-end in-memory interception of one ordinary pilot file also confirms that `load_inventory` accepts a NaN KL bound, and a false structural-zero flag reduces the complete pilot's S2 checks from 54 to 53 while leaving all 66 cells live. These defects are not evidence that the retained pilot statistics are wrong; they show that the claimed gate still permits silent audit suppression.

**Inference.** F2's requested validation of finite rule-driving values remains incomplete. Header provenance and valid counts do not prevent the analyzer from accepting a contradictory decision record. A fail-open numerical comparison is particularly consequential for S2, whose failure is supposed to halt reporting.

**Recommendation.** Finish the shared contract for the fields actually driving S1–S5: require finite/range-valid exact means and KL bounds; validate finite, ordered intervals and finite nonnegative decision SEs, with explicit exceptions only for registered ineligible/flagged cases; reconcile finite ratios and ratio intervals with their stored SD counterparts where algebraically available. Derive or verify structural-zero status from the exact reference mean and counts rather than trusting the flag (it is always false for this Gumbel level record at positive alpha). Consider using the recomputed KL bound in S2 after validation. Add the demonstrated NaN, reversed-interval, false-structural-zero and NaN-SE refusals, plus valid structural-zero/flagged-model acceptance cases, to both inventory and reuse tests. No scientific threshold needs to change.

### F10 — Major: the deployer subset can still disappear, and required uncertainty records can be empty

**Evidence.** `validate_cell_body` derives deployer membership from the grid when checking for a crossed block (`s2_run.py:220,248–251`), but does not require or reconcile the stored `deployer_subset` flag. `deployer_block` instead selects cells using `c["data"].get("deployer_subset")` (`s2_analyze.py:285–286`). Setting that flag false or deleting it in one retained deployer cell is accepted by **both** `load_inventory` and `cell_reusable`; complete pilot analysis still reports 66 live cells but emits **33 rather than 36 deployer rows**. Its three alpha rows are silently lost despite the expected grid membership and existing crossed blocks.

The nested-record checks are also incomplete. The quantile check merely iterates over keys present at `s2_run.py:240–242`, so `quantiles={}` passes vacuously and a NaN quantile also passes. A crossed dictionary containing all eight required names with every value set to `None` is accepted and forwarded into the deployer output; no `ci95`, `boot_se` or B=200 record is required. I reproduced acceptance through inventory loading, analysis and runner reuse for the null crossed values. The current pilot's genuine records contain all these values correctly, so this is a gap in enforcement rather than a remaining omission in `crossed_bootstrap` itself.

**Inference.** The Q1 record can be incomplete without a failed integrity check. This is the same class of silent subset loss that F1 sought to prevent, now confined to the deployer view. The crossed intervals cannot be reconstructed from the committed key counts, making their successful validation before accepting/reusing a cell material.

**Recommendation.** Derive deployer selection from the expected grid in the consumer, or require the stored flag to equal that selection before any consumer uses it. Require the five registered point-quantile keys with finite reconciled values. For every required crossed statistic, require a populated object with two finite ordered bounds in `[0,1]` and a finite nonnegative SE, and verify the registered resample count. Add missing/false deployer-flag, empty/missing quantile and empty/null crossed-value fixtures; assert the expected deployer-row count in the synthetic analysis. Keep the newly added 1% statistic and current language conventions unchanged.

### F11 — Minor: S2's corrected exact-mean calculation is followed by a contradictory nominal-alpha claim

**Evidence.** Protocol §9, line 40, correctly states that 20 KGW distinct cells at nominal alpha=.01 have exact mean above the dead-detector threshold, but then says: **“no under-rejection is flaggable at nominal 0.01 or 0.001.”** This is false for those 20 cells. For example, the current inputs for `gutenberg_en_1024__llama__h4__N10000`, `L64__distinct`, gamma=.25 give exact mean **0.015256744922904153**. At an observed mean of zero, the two-sided bound is **`4.207700508856269e-7`**, below `1e-6`: under-rejection is flagged at nominal .01. This follows from the existing code and frozen inputs, not a study outcome.

**Inference.** The implementation and new power table are correct, but the surviving sentence defeats the intended F7 qualification and could misstate the audit's power in the later report.

**Recommendation.** Delete that sentence or restrict it to cells whose exact mean is at or below `0.01440391433775623` at K=1,000. State explicitly that nominal .01 has the 20 KGW exceptions already counted, while Gumbel at .01 and all the registered distinct cells at .001 cannot flag under-rejection. Keep the distinction between nominal alpha and exact cell mean throughout the generated report.

VERDICT: REVISE
