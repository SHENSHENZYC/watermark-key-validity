# R07 — Study 3 protocol, round 3

Reviewer: Codex. Date: 2026-10-15. Scope: F9–F11 and their fixtures, as requested.

## 1. Baseline and material read

Baseline: `b7b81b8907cc575fc0373679b899d38c809ee6a2` on `main`; the working tree was clean. Comparison baseline: `c7df74e`.

I read the orientation and checkpoint prompt, then the round-2 response; the requested diffs of `s3_core.py`, `s3_analyze.py`, `s3_validate.py` and `s3_protocol_fill.py`; current and superseded INPUTS/VALIDATION; the changed protocol passages; and the decision log's round-2 entry. Checks used the saved synthetic pilot and key-free numerical inputs. I also checked the unchanged token manifest and the earlier studies' locks and pinned files.

Only this memo was written. Python bytecode writing was disabled. No full validator, input regeneration, real-text scoring, download, commit or long computation was performed. The protocol fill was checked with its write intercepted in memory; the protocol itself was not rewritten.

The material numerical defect in F9 is resolved. The requested F10 mutations now fail, and F11's main correction and generated paragraph are present. Two minor residual details, F12–F13 below, should be handled in the resolution; neither changes the saved predictions or the study's design. No blocking or major finding remains in this bounded review.

## 2. Claims against evidence

### F9: independent numerical checks

The Beta-cutoff identity is correct for the registered levels: with `m = floor(a N_E)`, `0 <= m < N_E`, and independent `W ~ Beta(m+1, N_E-m)`,

`P(Binomial(N_E, ell) > m) = P(W < ell)`.

For positive residual scales, substituting the model's `ell` gives the implemented condition

`X < sigma_E Phi^-1(1-W) - sigma_C Phi^-1(U)`.

Integrating the Gaussian X yields the two-beta expectation in `finite_share_perkey`; reversing the inequality for the fixed-threshold shift D yields the normal survival function in `finite_share_fixed`. The directions, Beta parameters and strict count cutoff agree with the target. At v = 0 the direct binomial-tail expectation avoids a discontinuous two-dimensional indicator; at rho_E = 0 the fixed-threshold level is constant. The zero-order-index case remains handled by the predictor's early return.

I independently recomputed all four entries in the prior F9 table:

| Setting, alpha = .01 | Measured-share threshold | Regenerated INPUTS | Independent reference | Absolute difference |
|---|---:|---:|---:|---:|
| h0 raw, llama news evaluation, nominal | 2alpha | .609754953 | .609754961546 | 8.55e-9 |
| Same setting | 5alpha | .437757071 | .437757085599 | 1.46e-8 |
| h0 raw, llama wikipedia/en@1024 → wikipedia/zh@256, conformal N_cal = 5,000 | 2alpha | .542666086 | .542665811379 | 2.75e-7 |
| h0 raw, llama gutenberg/en@1024 → wikipedia/ja@256, conformal N_cal = 5,000 | 2alpha | .393261411 | .393261360768 | 5.02e-8 |

For the fixed-threshold rows I integrated the original conditional binomial tail against the normal density on [-12,12], using adaptive quadrature with absolute tolerance 1e-12 and relative tolerance 1e-11. The reported integration errors were below 1e-12. For the per-key rows I separately implemented the two-beta expectation in chunks, without calling the production finite-share functions, at 3,000 and 6,000 nodes per variable. The references changed by approximately 5.53e-8 and 9.92e-9 between those resolutions. These comparisons use the rounded stored moments, which are sufficiently precise for the stated error targets.

I also recomputed the five explicitly selected convergence extremes from `fixtures.b.finite_shares`: maximum v, minimum positive v, maximum and minimum residual-variance ratio, and Gutenberg evaluation at maximum v. Each production-versus-four-fold-finer difference reproduced its saved value exactly. The largest was **6.9060142554e-5**, below the registered 1e-4 criterion.

To check that the nearly-zero-v case was not merely agreement between two inaccurate grids, I used another integration order: integrate U through its Beta CDF, then integrate the small Gaussian shift and the probability scale of W. Across both non-abstaining methods and the three alpha settings at that minimum-v pair, the largest discrepancy from the saved prediction was **8.28118e-5**, for the conformal share above 2alpha at alpha = .01. It remains below 1e-4. This is an absolute-error check; it does not establish small relative error for rare tails.

The five within-law fixtures, independently recomputed at all three exceedance levels, have maximum absolute Beta-binomial error **1.9564920774e-6**, below the tightened 1e-5 criterion. The fixed rho_E = 0 alpha-level result is `.47343746594184455`, equal to the binomial reference. The saved 45 per-key and 120 fixed convergence cases all meet their respective criteria; I reran the five per-key extremes, rather than the whole validator. The six stored Monte Carlo comparisons have discrepancies of **0.51–1.19 SE**, all satisfying `4 SE + 1e-4`; their construction in the validator draws U, X/D and the binomial count independently of the quadrature.

### F10: summary validation

The new `validate_cal_body` requires the exact z-summary field set and compares every field with `R.zq` computed from the committed threshold array, including abstaining entries. Integer counts exclude booleans; missing fields, NaNs and inappropriate infinities are rejected. It also checks the scheme's derived z values, multiplier and fitting indices, and requires finite fitting-summary values.

On `validation_20261015T191823Z`, the complete inventory and full pilot analysis still accept **12 units**, returning **18 T1 rows, 18 T2 rows and 1,872 descriptive rows**. Independently repeating the eight requested mutations refused all eight: empty z summary, missing abstaining summary, false cost, false abstention count, missing cost field, false multiplier, false z_emp and false fitting index. Seven additional probes were also refused: false z_pool, false second fitting index, NaN fitting median/unclipped value, boolean count, NaN cost and infinite cost.

A separate zero-threshold boundary probe exposes the minor infinity-comparison issue in F12. The unmodified pilot remains valid; this is an acceptance gap for a mutated summary, not an error in its saved thresholds.

### F11: generated text and correction

The decision log now explicitly corrects the previous 1e-6 accuracy claim, distinguishes the old acceptance threshold from the observed error, and states the tightened 1e-5 within-law criterion. Section 11 now reports the finite-share fixtures, convergence results and Monte Carlo comparisons directly from VALIDATION. Running the fill logic with `Path.write_text` intercepted produced text **identical to the current protocol**.

Section 9 states the new node counts and principal acceptance errors, the empirical-cap and array-agreement slacks, the summary-comparison coefficients, and the additional -1e-300 v-floor guard. It is still not literally exhaustive or fully precise about the remaining small details listed in F13.

## 3. Method and statistics

The new integration removes the material discrepancy found at round 2 while retaining the same finite-evaluation estimand. Its convergence and Monte Carlo evidence now exercise positive variance, unequal residual scales, both evaluation sizes, both per-key methods and all three exceedance levels. A finite sample of convergence settings is evidence of accuracy on those settings, not a uniform mathematical error bound over every possible input. The protocol describes that finite validation scope adequately.

No change to T1, T2, REP, eligibility or precision assumptions is needed for these repairs. The numerical share is descriptive; the primary mean/variance/SD computations are preserved. Relative accuracy of very rare tails is not claimed by the absolute-error criteria. The proof-of-model versus adequacy-on-real-text distinction from prior rounds remains in force and was not reopened.

## 4. Process and frozen inputs

Both superseded round-2 JSON files are byte-for-byte identical to their canonical versions at `c7df74e`. Recursive comparison of current and superseded INPUTS found no changed scientific leaf outside `share_above_alpha_finite`, `share_above_2alpha_finite` and `share_above_5alpha_finite`. All dictionary keys and list structures are preserved; 9,600 paired NaNs are unchanged. The other differences are the core digest, timestamp and execution-time/resource metadata. In particular, every set moment, covariance, population share, mean, SD, theory share and order index is unchanged.

The token manifest is byte-identical to the baseline, with SHA-256 `3385c73775d9d772f8a3b2a5b4d7256f8cbeb87836cb246fa9320fbfdef7d778`. All 20 calibration token arrays match it, and its binding to Study 2's manifest matches.

The diff contains no Study 1 or Study 2 code/record/lock changes. All **8 Study 1** and **15 Study 2** pinned files still match their locks, as do the review-resolution digests. The lock hashes remain:

- Study 1: `ff265b500f0dbd0cc019c883b7764fab01dd3b73b5b9e3350e2dd912337dd4fd`.
- Study 2: `434d8f3d8210d5ed30a3339d3805705e4339d081e57639c6b50ef2b8a29f9cc6`.

No Study 3 lock or production cells are present. The checked changes remain on the pre-outcome draft path. I accessed neither raw text nor the sealed holdout. There was no external submission or change of visibility. Agreement on this bounded review does not itself supply Yichen's authorization to lock or run.

## 5. Independent search

No new literature search or source quotation was needed for this review of F9–F11. I did not reopen the occupant/novelty assessment or the source conclusions accepted in earlier rounds. No search-absence claim is made.

## 6. Findings and disposition

**F9 is resolved.** The prior four material failures are corrected and independently reproduced well within the registered numerical tolerances. **F10's requested fixtures pass**, with the residual zero-threshold edge below. **F11's substantive correction and generated paragraph are verified**, with minor precision omissions below. These two follow-ups can be handled in the checkpoint resolution without redesigning the study or recomputing its finite-share predictions.

### F12 — Minor: the multiplier comparison accepts finite values when its reference is infinite

**Evidence.** In `s3_analyze.py:200–202`, when `t_emp = 0`, the reference `kap` is positive infinity. The explicit infinity branch is correct, but the alternative finite-number branch also accepts any finite `sk`, because both `abs(sk - kap)` and `1e-9 * max(1, kap)` become infinity, and `inf <= inf` is true.

In an in-memory calibration record, I set the empirical threshold at alpha = .001 to zero in both the summary and array, set z_emp to None and the unclipped fitting value to zero, and preserved the other contract fields. The legitimate `kappa_emp = inf` passes. Replacing only that multiplier by **-4, 0 or 1** also passes. This is a remaining F10 boundary case; it does not affect the validated threshold or the unmodified pilot's results.

**Recommendation.** Make the infinite-reference and finite-reference branches mutually exclusive: if the reference is infinite require positive infinity; otherwise perform the finite comparison. Add a zero-threshold fixture accepting infinity and refusing finite multipliers. No scientific rule or prediction needs changing.

### F13 — Minor: finish the bounded tolerance transcription in §9

**Evidence.** The finite-share fixture still checks the population share at **absolute error < 1e-3** (`s3_validate.py:136`), but that criterion is missing from both its `acceptance` dictionary and §9's list. The new Monte Carlo SE computation uses the guard `max(p_hat * (1-p_hat), 1e-12)` before dividing by 400,000 (`:177`, `:193`); that small guard is also unstated. Neither affects the reported non-extreme Monte Carlo cases.

Also, §9 calls the z-summary and scheme tolerances “relative,” while the implementation uses `abs(saved-reference) <= coefficient * max(1, abs(reference))` (`s3_analyze.py:191`, `:201`, `:205`). Thus the tolerance is absolute below unit magnitude and relative above it. Counts and None values are checked exactly.

**Recommendation.** Add the population-share criterion to the fixture metadata and §9, state the Monte Carlo variance guard, and give the actual `max(1, abs(reference))` comparison formula with its two coefficients. This completes the F11 transcription within the requested scope; it requires no change to numerical outcomes.

VERDICT: AGREE
