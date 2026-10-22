# R09 — independent review, round 5

Reviewer: Codex. Date: 2026-10-17 UTC. Scope: F22, F23, their corrections, and any new blocking issue.

## 1. Baseline and material read

Baseline: `main`, **`d5cf2ddfb23ce1da80446cba71008e5255a0efcb`** (`d5cf2dd`), initially clean. Compared the corrections with round 4's baseline, `b12f13b20411b11fbf2c232b510b10646b1f2e62`.

Read `AGENTS.md` and `research/reviews/REVIEW_ORIENTATION.md` in full; the Round 5 prompt; `RESPONSE_claude_r4.md`; the protocol's revised decisions, §§3, 6, 8, 10, 12 and generated §11; the diffs and relevant function bodies in `s4_validate.py`, `s4_analyze.py`, and `s4_core.py`; Study 1's unchanged `twoway_population_variance`; the grid's W2 settings; `VALIDATION.json`, especially F9 and its tolerances; the decision log's round-4/D18 entries; the handoff's corresponding status. Also checked the section-fill code and the preceding review's reproducer.

**Assessment:** F22 is resolved by D18's explicit narrowing of the target, rather than by repairing population-ratio coverage. F23 is resolved. The conditional target and key resampling now match, and the recorded coverage results reproduce. No blocking methodological issue remains within this bounded review. F24–F25 below are minor wording/evidence corrections suitable for the resolution before the lock; they do not require changing the estimator, bootstrap, design or D18.

## 2. Claims against evidence

### The conditional functional is identifiable and the formula checks

Protocol §3 defines the target as “the expectation over the keys and the generations of Study 1's two-way estimator given the realised 50 prompts”. Read **estimator** here as the **raw variance component**, before flooring or taking a square root. This defines a precise functional; the following equivalent formula makes its normalization and interpretation explicit.

For fixed prompts D = (d₁, …, dₙ), let pᵢ(k) be the rejection probability over generation randomness at prompt dᵢ, including the method's key-bound threshold. Let Σᴰᵢⱼ = Covₖ(pᵢ(K), pⱼ(K)). Under independent generation draws across prompts conditional on a key,

\[
v_K(D)=E[\widehat v_{\rm raw}\mid D]
=\frac{\sum_{i\ne j}\Sigma^D_{ij}}{n(n-1)}.
\]

Indeed, for the covariance Σ of a full rejection row, E[s_K²] = 1ᵀΣ1/n² and E[MS_E] = (tr Σ − 1ᵀΣ1/n)/(n−1). Subtracting E[MS_E]/n leaves the displayed off-diagonal average. Generation noise contributes only to the diagonal and cancels. Equivalently, this is Varₖ(n⁻¹Σᵢpᵢ(K)) minus the sample-normalized within-prompt interaction term divided by n, as the protocol says. For iid prompts independent of keys, averaging this expression over D gives Varₖ(E_D p(K,D)), the population key component.

I independently checked the identity by exhaustive enumeration of 64 binary K = 2, n = 3 tables. The key distribution put probabilities (0.2, 0.3, 0.5) on rejection-probability vectors (0.1, 0.8, 0.3), (0.9, 0.2, 0.7), (0.2, 0.4, 0.9). The covariance formula gives −0.027333333333333338; the actual estimator's exact expectation gives −0.02733333333333332. This also demonstrates why the functional is signed and is not generally a variance of fixed-prompt key means.

The code and coverage fixture use the corresponding SD-scale target

\[
R(D)=\sqrt{[v_{K,c}(D)]_+/v_{K,n}(D)}
\quad\text{when }v_{K,n}(D)>0,
\]

with an undefined denominator otherwise. The estimator uses the same positive-part convention and its existing unresolved guard. Stating this formula directly would remove the remaining ambiguity in “ratio of the … functionals” (F24).

For the shared-additive model, the functional reduces to

\[
v_{K,\lambda}(D)=(\lambda+g\bar D)^2-g^2s_D^2/n,
\]

where s_D² uses n−1. For the A(1+D) models it is a_K²[(1+mean D)²−s_D²/n]. These are exactly the formulas now used at `s4_validate.py:243–255`. Independent cell interactions in the additive fixture have zero cross-prompt covariance; their cancellation is consistent with its constant conditional target. The fixture checks valid probabilities and nested rejection sets. Renaming the former `UNPAIRED` model correctly acknowledges that its two rejection tables remain paired.

### Population-confidence interpretation has been withdrawn

The audited sections consistently limit the interval:

- §3 names the prompt-conditioned functional and says the interval is “not for the population ratio”.
- §6 makes the population reading “an extrapolation” and requires it to be reported “never as a confidence statement”.
- §8 explicitly identifies the population ratio as what the interval does not cover, and distinguishes proportional modulation from the shared additive interaction.
- §10 forbids extending the interval to the cell's prompt law.
- §12 adds the corresponding explicit non-claim.

The header's D16 qualification and D18, the analyzer's docstring and serialized `target`, and the core's docstring agree with that restriction. I found no surviving sentence in those sections assigning W2's interval coverage over the prompt law. There are still overbroad statements about unbiasedness and the limits of alternative methods (F24–F25), but they do not restore the withdrawn population-confidence interpretation.

## 3. Method, statistics and independent checks

### Matching resampling and reproduced coverage

Given D, a key's two complete rejection rows form one joint observation; resampling these observations together preserves the threshold pairing and samples the key-and-generation variation relevant to the conditional functional. The estimator is a function of the row covariance matrix. Thus the key bootstrap is the appropriate resampling dimension for D18, with the usual finite-sample and boundary limitations of a percentile interval. The common (K−1)/K component-centering factor alone is not a coverage proof.

I reran the model-free functions extracted unchanged from source, including the production `w2_row`, `w2_decide`, two-way estimator and bootstrap helpers. All nine models used the validator's seed 99261021, row names, K = 100, n = 50, 300 tables and 200 resamples. Every count below matches `VALIDATION.json` and generated §11. Coverage denominators are **finite intervals**, while the three class counts use all 300 tables.

| Model | Finite intervals | Conditional target covered | Population target covered | Classes agree / disagree / unresolved |
|---|---:|---:|---:|---:|
| ratio 0.5 | 300 | 272 (90.7%) | 272 | 297 / 0 / 3 |
| ratio 1.0 | 300 | 278 (92.7%) | 278 | 10 / 12 / 278 |
| ratio 2/3 | 300 | 280 (93.3%) | 280 | 283 / 0 / 17 |
| ratio 1.5, weak nominal component | 225 | 217 (96.4%) | 217 | 0 / 109 / 191 |
| small nominal component, a_K = 0.03 | 139 | 125 (89.9%) | 125 | 54 / 0 / 246 |
| proportional prompt modulation | 300 | 277 (92.3%) | 277 | 295 / 0 / 5 |
| different prompt modulation | 300 | 279 (93.0%) | 270 | 297 / 0 / 3 |
| shared additive interaction, g = 0.18 | 300 | 283 (94.3%) | 153 | 300 / 0 / 0 |
| shared additive interaction, g = 0.09 | 300 | 277 (92.3%) | 231 | 300 / 0 / 0 |

The two weak-component rows are explicitly diagnostics, not acceptance models. All seven acceptance models have all 300 intervals available and exceed the declared 85% gross-failure bound. This establishes that the earlier catastrophic mismatch has been addressed for the narrowed target in these models. It does **not** establish exact 95% coverage, uniform coverage at every fixed D, or calibration outside the tested models. The simulations redraw D and assess coverage of the corresponding conditional target; their coverage is averaged over those prompt draws, conditional on interval availability.

I also reran the original round-4 reproducer unchanged in its RNG sequence and row names (`2026101604`, `R4shared{rep}`, raw rule). It again gives 300 finite intervals, **149/300 covering the population ratio 0.5**, but **282/300 covering R(D)**. The median point ratio remains 0.4829898933014587. Its conditional target ranges from **0.1935949883 to 0.6569841307**. The response's range 0.120–0.648 belongs to the regenerated F9 tables, not this original reproducer; the coverage counts themselves are correct.

### F23's availability gate is now effective

At `s4_validate.py:301–310`, `finite_intervals` and `classes` are separate, coverage divides by `n_fin`, and every `well_` model executes `n_fin >= 100 and coverage >= 0.85`. Insufficient availability appends a failure and propagates into F9's acceptance. I executed that actual acceptance block on boundary inputs:

| Well-separated model input | Result |
|---|---|
| 0 finite intervals | Fail, model named in failures |
| 99 finite, all covering | Fail |
| 100 finite, 84 covering | Fail |
| 100 finite, 85 covering | Pass |
| Weak diagnostic with 0 finite | Does not affect acceptance |

The weak-model coverage and availability remain visible. The former vacuous pass for an acceptance model is fixed. The unchanged per-row denominator/90%-finite guard and class helper were already verified in round 4; this correction does not alter them. The two stale sampler/clock comments now accurately describe the existing computation.

### Alternatives and generated evidence

I reproduced all six alternative-construction summaries on the two recorded sets of tables:

| Model | Construction | Finite | Population covered | Conditional covered | Median width |
|---|---|---:|---:|---:|---:|
| ratio 0.5 | Superseded crossed percentile | 300 | 160 | 160 | 0.415225 |
| ratio 0.5 | Keys × half prompts | 300 | 300 | 300 | 0.892697 |
| ratio 0.5 | Jackknife sum, lognormal | 252 | 249 | 249 | 0.767743 |
| Shared additive g = 0.18 | Superseded crossed percentile | 300 | 276 | 289 | 0.240274 |
| Shared additive g = 0.18 | Keys × half prompts | 300 | 289 | 300 | 0.499979 |
| Shared additive g = 0.18 | Jackknife sum, lognormal | 300 | 289 | 300 | 0.343425 |

The wider alternatives do reduce raw-side classification resolution on the ratio-0.5 tables: 220 and 101 resolved, versus the selected construction's 297. That trade-off is real; it does not imply that the population target is impossible to analyze. D18's narrower scientific scope is Yichen's recorded choice.

Finally, I rendered `s4_protocol_fill.main` entirely in memory with the protocol's write method replaced by an in-memory capture. Its resulting text equals the current protocol exactly. No file was regenerated.

## 4. Process

D18 is logged as a pre-lock decision by Yichen. The round-4-to-current diff leaves Studies 1–3's locked files and records, the Study 4 grid, `INPUTS.json`, generation modules, runner and production prompt manifest unchanged. No Study 4 lock exists. The response, log and handoff consistently record the scope reduction and the open review. I did not access production outcomes or the holdout, and did not reopen the separately logged Study 1/2 secondary-SE issue.

The full validator, analyzer and input generator were **not** run. Completed numerical checks were separate model-free computations, each under 25 seconds, with a 55-second alarm and bytecode writes disabled. No model was loaded, no download or external communication occurred, and nothing was committed. The only file written for this review is this memo.

## 5. Independent search

No new external or literature search was undertaken for this bounded correction review. No external quotation or novelty claim is needed for the algebra and reproducibility checks above. This is not a fresh occupant screen. In particular, I do not treat the response/log's assertion that no established crossed-component scheme exists as a verified literature conclusion (F25).

## 6. Findings and recommendations

### F24 — Minor, non-blocking: distinguish the raw component's expectation from the SD-ratio target

**Evidence.** The new comment at `s4_validate.py:233–235` describes the population ratio as “the expectation of the former” conditional ratio. Protocol §6's W2 reading says “the point estimate is unbiased for it over prompt samples” in a paragraph discussing dispersion and the population ratio. Neither assertion holds for the nonlinear SD ratio. Unbiasedness and the iterated-expectation identity hold for each **raw variance component**. Flooring, square roots and division do not preserve them.

For an exact check in the existing F22 model, sum over the 51 possible counts J of positive prompts, weighted by Binomial(50, 1/2), using D̄ = 2J/50−1 and s_D²/50 = (1−D̄²)/49. This gives E_D[v_n(D)] = **0.04**, E_D[v_c(D)] = **0.01**, but E_D[R(D)] = **0.4762616443**, not the population SD ratio **0.5**. The exhaustive fixed-D check in §2 likewise separates the signed functional from its floored SD.

**Inference.** The implementation and the fixture's two true ratios are correct; this is a newly introduced explanation error, not a numerical defect or a reason to reverse D18.

**Recommendation.** Define v_K(D) explicitly as the expectation of the **raw** component, state the positive-part square-root ratio and its positive-denominator domain, and restrict the unbiasedness/expectation claims to raw components. Describe the population ratio as the ratio of the square roots of the population components, not as the mean conditional ratio. Apply this clarification to the §6 sentence and validator comment before the lock.

### F25 — Minor, non-blocking: keep validation conclusions within their measured scope and identify the correct sample

**Evidence.** Protocol §3 calls the interval “calibrated”; §§6 and 8 say the design “cannot bound” the population uncertainty or “cannot separate the prompt channel from the generation noise”. The response's verification table and decision log at line 649 add “no established scheme exists for variance components in crossed designs”. The supplied evidence consists of selected constructions on selected synthetic models, with conservative population intervals among the alternatives; it is neither an impossibility argument nor an exhaustive methods review. For the selected interval, the measured conditional-target coverage includes 90.7%, despite the nominal 95% label. Also, the response's F22 verification row attaches the regenerated F9 range 0.120–0.648 to the original reproducer's 282/300 result; its actual range is 0.1936–0.6570 (§3 above).

**Inference.** D18 is supportable as a deliberate scope/precision choice without these broader claims. The matched conditional resampling and transparent gross-failure check do not require asserting exact 95% calibration, impossibility of other inference, or absence of established methods.

**Recommendation.** Say that this is a **nominal 95% key-bootstrap interval for the conditional target, with the measured model-specific coverage reported**, and that the tested prompt-channel alternatives were declined for their observed width/availability trade-offs. Limit the identification statement to the inseparability of cell interaction and generation noise from one observation per key–prompt cell; do not infer that all population uncertainty bounds are unavailable. Replace the blanket literature claim with a statement about the constructions actually evaluated. Correct or relabel the response's copied range. These are prose/provenance corrections; no production computation or change to the selected method is needed.

F22 and F23 are closed under D18's stated scope. No further methodological redesign is requested by this review; the minor clarifications above can be recorded in the resolution before Yichen's separate lock decision.

VERDICT: AGREE
