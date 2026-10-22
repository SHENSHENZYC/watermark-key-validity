# R07 — Study 3 protocol, round 2

Reviewer: Codex. Date: 2026-10-15. Scope: the round-1 revisions, their regenerated records, and the independent checks requested for round 2. This review does not authorize the lock or a study run.

## 1. Baseline and material read

Baseline: `c7df74e6e7ac4ef52a683485318ebd0c59078471` on `main`; the working tree was clean at the start of this review. The comparison baseline is `0a479cf`, the round-1 review baseline.

I read the orientation and checkpoint prompt; `RESPONSE_claude_r1.md`; the requested diffs of `s3_analyze.py`, `s3_core.py`, `s3_run.py`, `s3_inputs.py`, `s3_data.py`, `s3_validate.py` and the grid; the current and superseded INPUTS and VALIDATION records; the changed protocol passages including regenerated §11 and the lock paragraph; the dated re-screen correction; and the round-1 entries in the decision log. I checked the affected current functions, the §11 fill script, the synthetic pilot record, the token manifest, and the earlier studies' locks and pinned files. I rechecked the decisive Vovk and AutoMark passages in the local text, and Nemecek et al. §4.1 in the primary arXiv HTML.

All executable checks were short, read-only or in memory, with Python bytecode writing disabled. I did not run the validator, regenerate inputs, run study keys, load raw text, download a file, or commit. The only file written is this memo. Two preliminary probe-harness attempts stopped on my own assumptions about a result key and a stored file path; the corrected harness completed. An optional SciPy Jacobi-quadrature cross-check overflowed its weight normalization and was discarded; no finding relies on that calculation.

The main result is that the requested provenance and evaluation-body repairs work, and the frozen inputs are intact. The new finite-evaluation share has the right estimand but a material integration error on actual frozen-input settings. That remaining defect prevents agreement before lock.

## 2. Claims against evidence

### Disposition of the round-1 findings

| Round-1 finding | Round-2 assessment |
|---|---|
| F1: provenance and threshold inventory | The provenance derivation, complete source maps, digest checks and threshold-array contract are verified. A smaller remaining calibration-summary hole is F10 below. |
| F2: denominators, axes and nonfinite values | Addressed in the requested scope. Independent mutations are refused and the complete pilot remains accepted. |
| F3: i.i.d. versus exchangeability, and frozen C | Addressed. The protocol separates marginal rank validity, the i.i.d. Beta/tolerance reference law, and a share of keys on one frozen calibration set. |
| F4: multiplier prerequisite | Addressed. `multiplier20`, the pointwise-over-key prerequisite, the raw-rule limitation and the empirical plug-in qualification agree across the affected executable paths and main protocol text. |
| F5: population versus finite-evaluation shares | The estimands and output fields are now correctly separated. Numerical accuracy with nonzero shift variance remains open: F9. |
| F6: Nemecek et al. | The dated correction, protocol treatment and decision-log correction agree with the primary source. |
| F7: promised diagnostics, cost and storage | The runner supplies the added cost/count fields and the analyzer supplies the T1 diagnostics; the committed/local threshold distinction and arithmetic qualification are corrected. F10 concerns accepting damaged summaries, not missing fields in the unmodified pilot. |
| F8: calibration sampling wording | The main protocol now states the conditional admissible-pool scan, the nested-pool exclusion and Gutenberg's reuse of 2,878 Study 2 texts. The design-label qualification is explicit. |

### Primary-source checks

- Vovk, `research/literature/txt/1209.2673.txt`, PDF p.2: **“generated independently from the same probability distribution P”**. The following text distinguishes exchangeability as weaker. The revised i.i.d. qualification is appropriate.
- AutoMark, `research/literature/txt/2609.37310.txt`, PDF p.42, Proposition 1: a detector **“that satisfies Equation (2)”**. This supports the condition now attached to the multiplier. The revision does not claim that the empirical plug-in implements their test.
- Nemecek et al. §4.1 explicitly describes a global threshold **“calibrated from the pooled null”** and says it **“models cross-lingual deployment with a single detector”**. The corrected neighbour description is supported. The experimental axes in §3 and the key occurrences in the HTML do not supply an across-key evaluation; the narrower wording about not characterising variation across keys is preferable to the withdrawn assertion about marginalisation. [Primary HTML, §§3–4.1](https://arxiv.org/html/2608.20047v1#S4.SS1).

### Frozen-record comparison

Both `INPUTS_superseded_r1.json` and `VALIDATION_superseded_r1.json` are byte-for-byte identical to their canonical versions at `0a479cf`.

Across current and superseded INPUTS, all **600 set-moment records** and **9,600 cross-moment records** are exactly equal after JSON parsing. Recursive comparison, accounting for `guaranteed` → `multiplier20`, the population-share renaming, added share fields and paired NaNs, found no other scientific-content change. The remaining differences are the expected timestamp, code/grid digests and runtime/resource fields. Mean, variance, SD, finite-text floor, theory share, order index, flags and covariance diagnostics are preserved. The `continuous_iid` fixture is exactly the former `continuous_exchangeable` fixture under its corrected name.

The Study 3 token manifest is unchanged from the round-1 baseline and hashes to `3385c73775d9d772f8a3b2a5b4d7256f8cbeb87836cb246fa9320fbfdef7d778`. All **20 calibration token files** match their recorded digests. Its binding to Study 2's token manifest matches, as do INPUTS' bindings to that Study 3 manifest and to Study 2's INPUTS.

There is no diff from `0a479cf` in the Study 1/2 code and output directories or their active protocols. Rehashing the **8 Study 1** and **15 Study 2** pinned files found no mismatch; both review-resolution digests also match. The lock digests are:

- Study 1: `ff265b500f0dbd0cc019c883b7764fab01dd3b73b5b9e3350e2dd912337dd4fd`.
- Study 2: `434d8f3d8210d5ed30a3339d3805705e4339d081e57639c6b50ef2b8a29f9cc6`.

### Independent inventory and body probes

On the saved synthetic pilot `validation_20261015T162040Z`, the actual unmodified inventory accepts **12 units** and complete analysis returns **18 T1 rows, 18 T2 rows and 1,872 descriptive rows**.

I independently ran **59 rejection probes**, all refused by the intended inventory/body checks. These covered every `PROVENANCE_FIELDS` member in both an evaluation and a calibration record; a wrong unit identity; empty and partial maps with both copies changed together; foreign digests and copy disagreement; a missing or changed committed threshold file; doubled N_E with screening constants correctly recomputed for that doubled N_E; the alpha, variant, source, fixed-method and cross-tokenizer metadata; NaN, infinite, negative and above-one bootstrap values; all three screening constants; a nonfinite crossed SE; threshold range, finiteness, alpha nesting and abstention; calibration sizes/axes; an empirical cap violation isolated from nesting and summary mismatch; and disagreement between scheme thresholds and their arrays.

These probes mutated in-memory record/array copies or mocked the file read/existence/digest result. The saved inventory was not rewritten. The calibration-summary boundary probes, discussed in F10, were additional to those 59 successful refusals.

All **432 actual per-key z summaries** in the pilot equal recomputation by `zq` from the committed threshold arrays, including positive/abstaining counts and the cost fields. The pilot's T1 rows contain the newly promised v, v_raw, tau_v, covariance, residual-variance, j, N_E and K fields.

## 3. Method and statistics

The finite-evaluation target is now correctly written as

`E[BinomialSF(m; N_E, ell)]`, with `m = floor(a N_E)`.

When v = 0 and the residual scales agree, `ell ~ Beta(j, N_cal+1-j)`, giving the Beta-binomial survival probability. Independent recomputation reproduces the key examples:

| N_cal | j | N_E | a | New predictor | Beta-binomial reference |
|---:|---:|---:|---:|---:|---:|
| 5,000 | 50 | 10,000 | .01 | .469094995268 | .469094995281 |
| 5,000 | 39 | 10,000 | .01 | .076729381117 | .076730244096 |
| 5,000 | 50 | 7,122 | .01 | .471855408216 | .471855410683 |
| 1,000 | 10 | 10,000 | .01 | .451328013901 | .451328013895 |

The fixed-threshold rho_E = 0 check also reproduces the binomial result `.473437465942`. These checks validate the intended estimand and the zero-shift case. They do **not** exercise either new positive-variance Hermite integration branch. The existing cross-law Monte Carlo fixture still compares the population share; it does not validate the new finite share.

With positive shift variance, the binomial tail can transition over a narrow part of the Gaussian integration domain. A fixed 64- or 200-node Hermite rule can then miss that transition. This is visible on the actual frozen inputs, not merely an artificial extreme: F9 gives examples and independent checks.

The unchanged T1/T2 mean/SD predictions, eligibility and materiality are not invalidated by this share-integration defect: those calculations use the preserved moment computation. The diagonal-at-5,000 exclusion is now stated with its practical implication: a T1 pass does not establish adequacy there. Retaining descriptive diagonal results remains acceptable. No rule change is needed to cure F9; the descriptive prediction must be computed accurately before it is frozen.

I checked the new numerical constants and contract descriptions against the executable branches. The registered node counts, bootstrap sizes, seeds, T1/T2 bands and counts, REP threshold, nesting slack, scheme-summary agreement tolerance, screening tolerances and crossed-interval slack agree. The exhaustive wording is not completely true: the empirical-cap slack and finite-share fixture tolerances are not fully stated, and §11 omits the new finite-share fixture despite referring readers there. F11 records these bounded corrections.

## 4. Process

The revision history preserves the round-1 record and makes the changes on the draft Study 3 path. No Study 3 lock or production cells are present, and current INPUTS has no `level_counts`, `key_mean` or `sd_obs` fields. The diff and local record support the stated pre-outcome status; they are not evidence about computations outside this repository.

The main response, corrected re-screen, protocol and decision-log dispositions are consistent, except for the numerical-accuracy claim in F11. The earlier studies and the token manifest remain intact. I did not access the sealed holdout or raw corpus text. No publication, contact, visibility change or external submission occurred. The primary HTML read encountered no access block. The substantive guarantee, transfer and novelty qualifications requested at round 1 are now present.

## 5. Independent search

This round made a bounded primary-source verification of the corrected Nemecek claim, rather than repeating the broad occupant search already documented in round 1. Web access was available. I make no new claim that no newer occupant exists, and do not treat the previous Semantic Scholar access gap or any search absence as proof of novelty.

## 6. Findings

### F9 — Major: the new finite-evaluation shares are materially inaccurate with nonzero shift variance

**Evidence.** `s3_core.py:235–244` integrates the per-key finite share over 1,000 U midpoints and 64 Hermite X nodes; `:262–269` uses 200 Hermite nodes for fixed thresholds. The new validation cases at `s3_validate.py:122–134` all have v = 0 or rho_E = 0, so none checks these branches. The following values are already in the regenerated INPUTS:

| Frozen-input setting, alpha = .01 | Share threshold | Stored finite share | Independent reference |
|---|---:|---:|---:|
| h0 raw, llama news evaluation, nominal | 2alpha | .591405965 | .609754962 |
| Same fixed-threshold setting | 5alpha | .413938617 | .437757086 |
| h0 raw, llama wikipedia/en@1024 → wikipedia/zh@256, conformal N_cal = 5,000 | 2alpha | .508312593 | about .5426659 |
| h0 raw, llama gutenberg/en@1024 → wikipedia/ja@256, conformal N_cal = 5,000 | 2alpha | .359772686 | about .3932614 |

The fixed-threshold setting has rho_E = 1.48247692, sigma_E² = 1.68678714 and N_E = 10,000. I integrated the conditional binomial survival probability against the standard-normal density using adaptive quadrature on [-12,12]; its reported absolute errors were below 1e-11. An independent beta-cutoff calculation agreed to about 3e-8 on those two rows.

For the first per-key example, v = 2.42816238, sigma_C² = 1.86841847, sigma_E² = 2.66634918, j = 50 and N_E = 10,000. Re-running the current predictor from the rounded stored moments gives `.508312594400`, confirming the saved number. A useful independent identity is

`BinomialSF(m; N, ell) = P(W < ell)`, where `W ~ Beta(m+1, N-m)`.

For positive v, integrate the Gaussian shift analytically to obtain the finite share as

`E_(U,W)[Phi((sigma_E Phi^-1(1-W) - sigma_C Phi^-1(U))/sqrt(v))]`.

Using this smooth two-beta expectation gives `.542666086805` at 1,000 midpoint nodes per beta variable and `.542665866666` at 3,000. An independent 400,000-draw simulation of U, X and the evaluation binomial count gives `.5416475` (Monte Carlo SE `.00078782`; seed 99261071), consistent with that reference and far from the saved value. The second per-key row gives `.393261410864` and `.393261370687` at the same two resolutions. These checks took seconds and generated no real-text outcome.

**Implication.** Errors of roughly 1.8–3.4 percentage points in a predicted key share are large enough to change the descriptive interpretation. They would be mistaken for model inadequacy or a calibration effect. Fixing the population/finite estimand label alone has not completed F5. The h0 block is a registered descriptive block even though it is not the primary T1/T2 block.

**Recommendation.** Replace or adapt the numerical integration and demonstrate convergence over the frozen-input range, including substantial nonzero shift variance, unequal residual scales, both evaluation sizes and all three exceedance thresholds. The beta-cutoff identity above is one possible route; an adaptive integral with a defensible error target is another. Retain the zero-shift fixtures, but add positive-variance fixtures that would fail on these examples, and state the acceptance error. Regenerate the affected predictions and validation before lock, preserving the superseded record and confirming again that moments and the other predictions have not changed. Increasing a fixed node count without a convergence check is not sufficient evidence of repair.

### F10 — Minor: calibration summary fields can still be absent or false in an accepted result

**Evidence.** `s3_analyze.py:172–186` checks j, requires only a dictionary for a positive-j z summary, and checks only t_emp/t_pool within the scheme summary. It does not require the z summary at j = 0 or validate its promised fields. Independent mutations replacing a positive-j `z` by `{}`, removing an abstaining entry's `z`, setting a positive-j `cost_mean` to 12345, and setting `kappa_emp` to -4 all pass `validate_cal_body`. Combining them in the in-memory inventory also passes complete analysis; `results.pass1` carries those values unchanged through `s3_analyze.py:386`.

**Implication.** The actual pilot summaries are correct, as the 432 recomputations above show, and the validated thresholds still supply Study 4. This is a remaining output-contract hole: an accepted result can omit the promised abstention/cost table or carry an impossible multiplier. It is narrower than the repaired provenance and threshold-array failures.

**Recommendation.** Require the promised summary structure for every registered entry, including full abstention. Recompute the z summaries and derived scheme fields from the committed thresholds, or validate them against those recomputations with a stated tolerance and the appropriate zero-threshold conventions. Add mutations for missing cost/count fields and wrong derived values. No new data or long run is needed to test the gate.

### F11 — Minor: align the numerical claims and exhaustive-contract wording with the actual checks

**Evidence.** The response's F5 row and the 2026-10-15 decision-log entry say the Beta-binomial fixture agrees to 1e-6 at five settings. The implemented acceptance test is **absolute error < 1e-4** for each finite share, **< 1e-3** for the checked population share, and **< 1e-9** for the fixed rho_E = 0 check. One saved finite-share error exceeds 1e-6: at N_cal = 5,000, j = 50, N_E = 7,122 and a = 2alpha, the predictor is `1.3144310474174656e-6` against `3.270923124798486e-6`, an absolute difference of approximately `1.95649e-6`. The fixture correctly passes its actual 1e-4 threshold; the prose overstates it.

Protocol §3 says §11 checks the finite share against the Beta-binomial law, but regenerated §11 has no finite-share fixture paragraph, and `s3_protocol_fill.py` does not read `fixtures.b.finite_shares`. Section 9 names the node counts but omits the new fixture error thresholds. Its calibration contract says the empirical threshold is at most alpha, while `s3_analyze.py:183` allows the summary up to alpha + 1e-12, followed by a separate array/summary tolerance of 1e-12. The tiny `-1e-300` guard on the v-floor comparison also remains absent from the claimed exhaustive list; it has no practical effect here.

**Recommendation.** Correct the response/log accuracy claim, generate the finite-share validation results and actual tolerances into §11, and state the empirical-cap tolerance explicitly. Either list the harmless numerical guard or narrow the claim of exhaustiveness to material tolerances. Carry whatever validated integration/error rule replaces the current one in F9 into the same descriptions. These are documentation corrections, not reasons to alter T1/T2/REP.

VERDICT: REVISE
