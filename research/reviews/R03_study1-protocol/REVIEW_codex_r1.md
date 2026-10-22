# R03 — Study 1 protocol before lock — independent review, round 1

Reviewer: Codex. Date: 2026-10-09. Recommendation: revise before locking or running Study 1. The basic simulator is largely faithful, but the proposed decisions currently mix different estimands, include an incorrect identity comparison, and rely on uncertainty rules that do not support their interpretation. The pre-lock literature screen also missed a direct treatment of validity given a key in a paper it retrieved.

## 1. Baseline and scope read

Baseline: **`d3cd087b82219e7a7779557087ac35cab19265a7`**, current `HEAD` of `main`; the working tree was clean at review start.

Read `AGENTS.md`, `research/reviews/REVIEW_ORIENTATION.md` in full and `research/reviews/R03_study1-protocol/PROMPT.md`; then, in the requested order, `research/STUDY1_PROTOCOL_v0.1.md`, gate v0.2 §Residual gap, `DESIGN_NOTES_v0.1.md`, `s1_core.py`, `s1_run.py`, `s1_analyze.py`, `s1_validate.py`, `outputs/study1_v0.1/VALIDATION.json`, `grid_v0.1.json`, the re-screen note, and the four specified decision-log entries. I also inspected the saved six query outputs, validation timing log, relevant handoff/brief passages and local literature text at the pages below.

Checks were short, in-memory Python calculations and fixtures, using `-B` to avoid bytecode writes. They covered an explicit retention oracle, packed/direct colour equality, the two cell-statistics implementations, weights, identity boundaries, a mock lock and a mock analyzer input. No study grid, validation grid, model or corpus analysis was run. No data, model or PDF was downloaded. No real-text holdout was accessed. Only this memo is written; nothing is committed.

## 2. Claims against evidence

### What checks out

- **Detector.** `s1_core.py:185–191` implements the stated strict test, with centre γ, denominator `sqrt(M γ(1−γ))`, `norm.isf(alpha)`, and no rejection when M = 0. The exact independent/distinct reference at lines 213–218 correctly uses `binom.sf(floor(threshold), M, gamma)` for positive M. Discreteness means this reference need not equal nominal α; using it in place of α is correct.
- **Retention and prefixes.** `Chain.mask` groups within each document and retains the first position of each tuple or context. A later suffix cannot change an earlier first occurrence, so slicing these masks is valid. An explicit token-sequence oracle passed all 27 combinations of three widths, three prefix lengths and three rules. The first-context rule at h = 0 retains exactly one scored token per document.
- **Queried fixed-size sets.** The construction at `s1_core.py:165–181` is distributionally correct under the stated ideal-randomness assumption: for j queried tokens, draw H hypergeometrically and choose a uniform H-subset of those j tokens. For a particular subset S of size r, its probability is `choose(V−j,m−r)/choose(V,m)`, exactly the restriction of a uniform m-subset of the vocabulary. Ranking independent continuous uniforms gives the required uniform choice. A separate six-token toy check gave exactly three greens in every fully queried class and approximately one-half marginal frequencies. This is a statement about the ideal model, not a proof of statistical independence for SplitMix64 and PCG streams.
- **Independent colours and packing.** The independent implementation is exactly `uniforms(key, tuple_id) < gamma`. At the production chunk size 48, packed and direct colours were identical for both colourings, including a partial final byte/chunk, on the tiny fixtures. The two implementations of cell statistics also agreed. The default chunk size 50 has a separate defect, noted in F10.
- **Document weights.** For positive-M documents, `w_hat = mean_i(n_iu/M_i)` and `q_hat_k = sum_u w_hat_u G_ku` are exactly the same linear quantity; the fixture verified this numerically. These are document-averaged, not pooled-position weights.
- **Fixed-size identity.** Expanding the covariance sum gives

  `Var_K(q) = g(1−g) A − g(1−g)/(V−1) (B−A) = g(1−g)(VA−B)/(V−1)`.

  With independent Bernoulli(g) colours the variance is `g(1−g)A`, and their ratio is `(V−B/A)/(V−1)`. The derivation in the gate is correct. The code's independent sampler is instead Bernoulli(γ); this distinction matters in actual grid cells (F2).

### Published evidence re-checked locally

Whitespace-normalized substring searches confirmed the following against the local PDF-text page segments, not just the reading notes:

- `research/literature/txt/2506.16349.txt`, PDF p.27: “is given by a hypergeometric distribution with PMF”; equation (9) and the surrounding discussion give the alive/dead-code special case and its subdomain interpretation.
- `research/literature/txt/2509.24368.txt`, PDF p.21: “the key-to-key standard deviation is on the order of 1%.” Table 2 reports SDs 1.2%, 0.3%, 0.1%, with 100 keys and 10,000 null samples in the caption. These remain evidence that per-key dispersion was already measured.
- `research/literature/txt/textgrain_openai_2026.txt`, PDF p.6: “score only the ﬁrst occurrence of each distinct context window.” The same page states no detection for no scored positions and qualifies the fixed-key guarantee. The protocol borrows that retention rule, not textGrain's full detector.

The saved validation numbers trace correctly to `VALIDATION.json`: observed/exact variance ratios 0.998145 and 0.994980, two-token fixed-size variances approximately 0 and 0.0799214, and binomial-reference discrepancies 0.915 and 0.676 of the **implemented** SE. This verifies transcription, not the validity of that SE. The new literature evidence in §5 changes the claimed completeness of the nearest-work account.

## 3. Method and statistics

The synthetic scope, strict test definition, separation of exact identities from an approximation, and exclusion of real-text conclusions are appropriate. Excluding V = 2/10/100 and the first-context h = 0 case from a primary normal-approximation check is defensible. It does not establish that all remaining cells satisfy the gate's local-shift, variance or conditional-CLT conditions.

I enumerated **grid specifications only**, without simulating cells: 1,140 output cells, at most 360 R1 candidates before eligibility, 882 R2 checks, and 258 paired-colouring comparisons for R3.

| Rule | What it currently establishes, and its limits |
|---|---|
| R1 | A point-estimate band check for the code's sampled-key predictor, not the protocol's exact predictor. No eligible cells gives fail, not an automatic pass. Negative corrected variance becomes zero and therefore fails against an eligible positive prediction. The lower eligibility cutoff does not make those point decisions sufficiently precise (F3–F4). |
| R2 | The correct binomial reference is available, but a normal 3-SE check is only a diagnostic. The reference averages over the same sampled texts, so its text variation is not independent uncertainty. Structural-zero rejection cells pass automatically and should be counted separately. Failure calls for an implementation/uncertainty audit; it does not logically prove the sampler wrong (F6). |
| R3 | The identity is testable at fixed realized weights. The implemented comparison is wrong when g differs from γ, and its SE ignores unequal K and pairing. Degenerate variances need an explicit branch. The below-1% statement is properly posed as something the exact ratio can refute; it is not a consequence of large V alone (F2, F6). |
| R4 | Tests unconditional monotonicity of the **level** SD, whereas the gate's conditional H-length concerns a z-shift while weights remain concentrated. The coded tolerance is not the uncertainty stated in §8. Flat estimates below the noise floor can pass without informative evidence (F5). |
| R5 | The population collision ordering is sound for projective raw laws. Independently generated empirical weights at different h, with different scored-position windows, are not that exact projective family. The arbitrary 0.01% tolerance for A is not a text-sampling error bound (F5). |

At N = 4,000 and level 1%, a key has about 40 rejections and a binomial SE of **0.1573 percentage points**. At level 0.1%, these become four rejections and **0.0500 percentage points**, with a 1.83% probability of zero rejections for a key whose true level is exactly 0.1%. The latter resolution is inadequate for precise per-key tail quantiles or a worst-key claim without intervals. K = 500 can describe a broad dispersion, but its adequacy depends on the size and distribution of that dispersion. The quoted 3.2% is the normal-theory relative error for an ordinary SD, not for the noise-subtracted SD or every bounded, skewed distribution of per-key levels. Detailed implications are in F3.

For R2, 882 independent exact normal checks would have about 2.38 expected 3-sigma misses; the 99% rule allows at most eight. This makes the thresholds intelligible as a heuristic, but the checks here are strongly dependent through keys, texts and prefixes, and some are discrete/rare. That calculation is not a calibration of the actual rule. For R3, K = 200 gives the stated equal-K approximation a relative SE of 14.1%, hence a 3-SE band about 42.4% wide. It cannot empirically resolve a 1% correction; computing the exact correction is a distinct and legitimate exercise.

What a theory-section reader still needs is specified in F4–F5: a consistent population or realized-text target; variance and retained-count diagnostics for the gate's approximation; a measure of local-shift size; occupancy/support coverage and the relevant limiting prediction; and uncertainty for the resulting curves. Without those, a failure identifies a simplified predictor's failure but generally cannot identify which condition failed.

## 4. Process, timing and disclosure

The draft status, R03 checkpoint, request for Yichen's subsequent lock/run decision, and `final: false` are consistent across protocol, handoff and the specified log entries. At review time there is **no `PRE_RUN_LOCK.json` and no study `cells/` directory**. This is consistent with no production run; it does not prove that no outcome quantity has been computed. In particular, **210 JSON files still exist in `outputs/study1_v0.1/validation/`**. I checked existence/counts without reading their scientific results. F8 addresses both the inaccurate discarded-output wording and key reuse. This is separate from, and does not reopen, the real-corpus holdout verdict at R02.

The recorded timing is credible as a measurement. The grid SHA in `validation_run.log` is the current grid SHA, `fe31957c17d480c9c6d163160d4265cf0aa249aef8e6c53fbe1ea3b4d39cd4ff`. The five Zipf chain durations are 5, 44, 70, 107 and 117 seconds: **343 seconds** in total. The three executed two-token chains sum to 17 seconds, and two unused h = 3/4 dictionaries are also built before the runner checks the illustration-width restriction. Total elapsed 365 seconds is consistent. The 102 Zipf cell timers sum to 250 seconds; those timers omit chain construction and colouring, so they must not be mistaken for full run cost. `VALIDATION.json` records child peak RSS 5,521.9 MB, supporting the stated 5.5 GB observation.

The approximately two-hour projection is plausible, not demonstrated. Thirty core chains at 120 seconds is one hour before the extra γ chains, fixed-colouring sorts and illustration work. The validation measured only one core family's expensive fixed sort, on 584,443 tuples at h = 1; larger dictionaries require extrapolation. The code comments promise a projection but do not actually calculate one. There is substantial apparent slack against six hours, and I found no evidence of dishonest timing. F9 asks for an auditable cost table and fresh-run validation, not a full pre-lock study run. The reduction order is explicit and correctly restricted to before lock; reductions also change precision and should trigger a recalculation of the statistical requirements.

The orientation explicitly commits to naming all AI models, including the reviewer, in the AI-use disclosure; the brief commits to Yichen reading and revising the prose. This review is an AI review by Codex, not human peer review. Preserve the review and record the actual model/version and tasks performed when compiling that disclosure. Nothing in this review authorizes a publication, push, download, or real-text analysis.

## 5. Independent search for occupants or newer work

On 2026-10-09 I searched the web for combinations of watermark with “key-conditional”, “fixed key”, “per-key”, “dispersion”, “false positive” and “training-conditional”, including arXiv-restricted queries, then opened primary sources. Exact phrase searches were sparse; a broader search was decisive. I used HTML, not downloaded PDFs. The saved q1–q6 files support entry counts **2, 0, 0, 0, 0, 11**, but contain truncated summaries, not a sufficient full-text screen.

**AutoMark, Gloaguen, Staab and Vechev, arXiv:2609.37310v1, submitted 2026-09-29, is a direct occupant of part of the stated gap.** Its §3.2 defines a bound on the probability, over keys, that a fixed text law's FPR exceeds α. §3.3 supplies a verification test; Appendix I.2 proves a p-value multiplier correction; Appendix C evaluates correction costs and fixed-key validity. Appendix D.1 specifies 1,000 keys and 20,000 fresh texts per key. The heading “Soundness given a key” is decisive. This does not by itself establish that it contains the proposed occupancy-variance identity or length predictor, but classifying it only as a future scoop signal is incorrect. [Primary HTML, §§3.2–3.3 and Appendices C, D.1, I.2](https://arxiv.org/html/2609.37310v1); [submission record](https://arxiv.org/abs/2609.37310).

I also found **Nisaharan Genhatharan's public artifact, _When nominal false-positive rates fail_**. Its README expressly studies KGW key-dependent FPR, a mean-shift explanation with length dependence, tokenizer sensitivity and per-key/per-length calibration with a power comparison. These are the author's claims; I did not reproduce its numbers. It warrants comparison in the nearest-work account. The linked manuscript-source path was denied by robots.txt, so I stopped there; no workaround was attempted. Publication date, full methods and priority relative to this project remain unverified. [Author's repository and README](https://github.com/nisaharan/when-nominal-false-positive-rates-fail).

Search absence is not novelty evidence. These findings do not reopen the closed data checkpoint or decide a project pivot; they do require an accurate account of what Study 1 adds before its lock.

## 6. Findings and recommendations

### F1 — **blocking** — The re-screen misclassifies a directly relevant formal treatment

**Evidence.** `RESCREEN_2026-10-09.md` calls AutoMark “not as an occupant (title and abstract level; not read in full)”; protocol §12 repeats the limited scoop-signal characterization. The primary sections identified in §5 establish direct overlap. The other artifact in §5 is also absent from the local nearest-work account.

**Inference.** The search was run, but relevance was assessed too shallowly. An earlier submission date does not make a newly located treatment irrelevant. A claim that nothing appeared after October 8 cannot substitute for assessing a retrieved September paper.

**Recommendation.** Correct the screen and nearest-work account before lock. Compare the proposed contribution claim by claim with the identified definitions, tests, correction and experiments, then state the remaining Study 1 contribution narrowly. Assess the second artifact within permitted access and record any continuing access gap. Yichen decides whether the revised positioning warrants further scope changes; this memo does not decide that for him.

### F2 — **blocking** — R3 uses the wrong independent variance when γV is not an integer

**Evidence.** `colour_independent` thresholds at γ (`s1_core.py:138–143`), whereas `exact_identities` returns `g(1−g)A` for its independent variance (lines 204–210). The grid includes γ = 0.25 at V = 10 and V = 2. The analyzer then compares the observed fixed/independent ratio with `(V−1/C_cond)/(V−1)`.

For V = 10, γ = 0.25, A = 0.2, B = 1, the implementation reports independent variance 0.032 and ratio 0.555556; the actual Bernoulli(0.25) comparison has variance 0.0375 and ratio **0.474074**. For a separate four-tuple toy with V = 2, γ = 0.25 and weights `(0.45,0.05,0.45,0.05)` in two classes, the fixed sampler necessarily has zero variance, while the stated ratio is **0.780488**. The code's 3-SE allowance is 0.104713 at K = 2,000, so a correct sampler necessarily fails this check. No study cell was used for these examples.

**Recommendation.** Choose and document whether the comparison matches green probabilities or matches nominal γ. For the latter, use independent variance `γ(1−γ)A` and multiply the nondegenerate ratio by `g(1−g)/(γ(1−γ))`. For the former, change the independent sampler/reference consistently. Treat m = 0/V and zero comparison variance explicitly; do not apply a relative ratio-SE rule there. Add tiny noninteger-γV and degenerate fixtures before lock.

### F3 — **blocking** — The crossed variance correction is not unbiased, and R1's precision claim fails near eligibility

**Evidence.** Both cell-statistics functions subtract `mean(a_k(1−a_k))/N_eff` from the across-key sample variance. Protocol §8 says this removes the text variance “in expectation”. Let binary rejection `Y(X,K)` have orthogonal components with variances `v_K = Var_K E_X Y`, `v_X = Var_X E_K Y`, and interaction variance `v_E`. For N shared independent texts,

`E[s_K²(a_hat)] = v_K + v_E/N`,

but the expected subtraction is `(1−1/N)(v_X+v_E)/N`. Thus the expected signed correction is

`v_K − v_X/N + (v_X+v_E)/N²`,

not `v_K`. A simple key-independent rejection matrix, with the same 10 successes among 100 texts for every key, has true across-key variance zero and produces a signed correction of −0.0009. That is removal of a shared row effect that never contributed to across-key variation.

Even with a known noise variance and normally distributed key estimates, at the eligibility boundary `SD = 0.0005`, N = 4,000, K = 500 and mean level 0.01, the delta-method relative SE of the corrected SD is about **34.5%**, not 3.2%. In that deliberately optimistic benchmark, a chi-square calculation gives only **74.9%** probability of landing in R1's [2/3, 3/2] band when the predictor is exactly right; approximately 7.0% of variance estimates are negative. These are analytic sensitivity calculations, not simulated study outcomes.

**Recommendation.** Use a justified crossed-design variance-component estimator, for example an appropriate interaction correction from the balanced two-factor decomposition, with uncertainty for the signed variance and its SD transformation. Pre-specify how unresolved/below-floor cells enter the primary decision. Revisit the eligibility threshold, N/K or band decision using that uncertainty. State the normal/kurtosis assumption behind SD Monte Carlo errors. A noisy point estimate falling outside the band must not alone be called failure of the theory.

### F4 — **blocking** — R1 implements a different predictor and compares realized-text prediction with population dispersion

**Evidence.** Protocol §5 specifies `SD_K(q_hat)` from “the exact identity at w_hat under the cell's colouring.” The analyzer uses `sd_pred_first_order`, which both statistic functions compute from the **sampled-key** variance of q_hat (`s1_core.py:236`, `s1_run.py:98`, `s1_analyze.py:33–37`). The separate exact field is unused by R1 and always uses the independent identity, even in fixed-colouring cells. An in-memory analyzer fixture passed with sampled-key prediction 0.01 and observed SD 0.01 although its exact prediction 0.02 would fail the band.

There is a second estimand mismatch even after choosing the correct field: the identity at realized weights includes finite-text variation of those weights, whereas the corrected level variance targets a population text law. If `W_i(u)=n_iu/M_i`, then

`E[A_hat] = ||E W||² + (E||W||² − ||E W||²)/N`.

For constant M and effectively non-overlapping scored tuples, the raw realized-weight predictor has a finite-text floor `φ(z_α)/sqrt(N)`. At α = 0.01, N = 4,000 this is **0.04214 pp**, close to the **0.05 pp** eligibility threshold. In the corresponding additive-noise approximation, a 0.05 pp prediction can represent only 0.02691 pp of population signal, a ratio 0.538 before any approximation failure.

**Recommendation.** Define the primary target consistently before lock. Retain the realized-weight identity as a simulator check, but either estimate the population collision/dispersion with its finite-text correction, or formulate a genuinely conditional-on-text adequacy target and uncertainty. Use the pre-specified exact or sampled-key predictor consistently, record both distinctly, and make the exact fixed-cell prediction use the fixed identity. Do not silently choose the more favorable target after seeing outcomes.

### F5 — major — R4/R5 do not test the gate under its stated conditions; T1/T3 need additional measurements

**Evidence.** Gate item 4 retains the score-sum variance σ_k, conditions on random M, and describes a local approximation. Study 1 substitutes `σ = sqrt(γ(1−γ))` and factors `E[sqrt(M)]` out of a mean shift without testing either step. Generally, the linearized mixed shift involves `E[n_u/sqrt(M)]`, not `E[sqrt(M)] E[n_u/M]`. No per-key score-sum variance, M-stratified diagnostic, or measure of linearization size is saved.

Gate H-length is conditional on concentrated occupancy and concerns z-shift dispersion. Protocol R4 instead requires level-SD monotonicity at every length in every core chain and says any failure refutes that hypothesis. Its code tolerance is `sqrt(2/K) SD_obs + 0.5 sqrt(noise_var)`, then twice the sum for adjacent cells. This is not the 3.2% SD error in §8. At a 1% mean level and the planned N/K, a decline from 0.3 pp corrected SD to zero is allowed by a tolerance of about **0.3774 pp**.

R5 tests independently sampled weights across h (`s1_run.py:45`) and different windows t ≥ h. Its A tolerance is the unexplained factor 1.0001. Sampling noise can break empirical ordering, and when almost every tuple is unique `A_hat ≈ 1/[N(L−h)]` actually increases with h. The Markov sampler starts from its global Zipf proposal; that proposal is not generally a stationary distribution of its random support transition matrix, despite the core docstring's marginal description. Stationary/projective reasoning therefore needs explicit qualification.

T1's curves alone do not establish saturation. All current laws have full eventual support; no restricted-support case tests the gate's nonzero fixed-size distinct-token limit. The first-context limit is a different object. The design notes promised comparison with a limiting occupancy prediction; the protocol/code do not define that comparison.

**Recommendation.** Keep the present simplified formula as a clearly named baseline, but measure the gate's missing variance, M and local-shift conditions or narrow the stated theory being tested. Save sufficient per-key moments and paired quantities to diagnose failures and uncertainty. Define a z-shift diagnostic alongside level dispersion. For width, use genuinely comparable positions/laws and a justified uncertainty treatment for estimated collisions. Replace arbitrary monotonicity tolerances with calibrated paired comparisons or descriptive curves; a failure outside the gate's conditions is not a refutation of its conditional claim. For saturation, pre-specify support/coverage diagnostics and analytic limiting references, optionally adding a tiny restricted-support control. State exactly which narrower T1/T3 claims remain in Study 1.

### F6 — major — R2/R3 error bars and failure meanings need calibration and explicit boundary handling

**Evidence.** R2 compares the sample overall rejection to a binomial reference averaged over the **same texts**, but uses an SE intended for an overall mean around a population expectation. Conditional on those texts the reference is fixed; across repetitions its text component co-varies with the observed mean. The variance of their difference is not the unadjusted overall-mean variance. The crossed correction in F3 also enters that SE. At zero observed rejections the estimated SE can vanish even when the exact reference is positive; rare-key regimes do not have reliable normal 3-SE coverage.

R3 uses K from the fixed cell, although core pairs have K_fixed = 200 and K_independent = 500. Both colourings use common key-derived uniforms. Under even a normal unpaired approximation the relative ratio SE would involve `sqrt(2/(K_f−1)+2/(K_i−1))`; with pairing it also needs the covariance. General weighted/degenerate laws need fourth-moment or resampling treatment rather than automatic normal variance assumptions. At an exact zero ratio the coded allowance is zero, so floating-point deviations can fail a mathematically degenerate identity.

**Recommendation.** Specify whether R2 conditions on realized texts, and use uncertainty for its actual difference. Separate structural-zero controls from informative checks and validate the decision rule in small known cases. Calibrate R3 to the actual paired/unequal samples, or compare each variance to its own exact value with appropriate uncertainty. Pre-specify degenerate and numerical-tolerance cases. Treat a failed diagnostic first as a flag for audit, preserving the run; do not assert that a fixed percentage of heuristic misses alone establishes an invalid simulator. Likewise, a large-V reduction above 1% refutes that numerical conjecture, not the exact identity.

### F7 — **blocking** — The lock and analysis do not enforce the promised experiment identity/completeness

**Evidence.** `verify_lock` checks whatever entries appear in `lock['hashes']`, the grid entry, and two flags (`s1_run.py:30–36`). It does not require protocol/core/runner/analyzer/validation hashes, an approval field, or the other promised lock metadata. A mock lock containing **only the grid hash**, `before_outcomes: true` and `final: false` was accepted by the unmodified function. The advertised `protocol_sha256` is not separately checked. These checks also use Python `assert`, which is disabled under `python -O`.

Resume skips a cell solely because its filename exists (line 61); cell JSON has no lock digest or text/key provenance to check on reuse. The analyzer glob-loads whatever JSON files are present, with no lock or expected-grid inventory. An in-memory single-cell fixture produced **R4 pass and both R5 passes**, because a one-point chain satisfies every adjacency test vacuously. A partial run can therefore yield apparent rule successes.

**Recommendation.** Validate a required lock schema and every promised digest using explicit exceptions before production work. Bind each cell to the lock/grid, seed configuration and cell specification; verify that binding on resume. Require the complete expected cell/alpha inventory, uniqueness and minimum chain lengths before issuing experiment-level decisions. Keep any deliberate partial analysis explicitly partial. Add refusal fixtures for omitted hashes, changed code, wrong flags, incompatible cached cells and incomplete analysis. The commit/push-before-run procedure remains a human/process step unless separately enforced; do not imply the current function verifies it.

### F8 — major — Validation is a retained pilot with reused keys, not an outcome-free discarded run

**Evidence.** `s1_validate.py:38–40` computes rejection outcomes on a validation law; lines 43–48 invoke the production statistics runner over the validation families. The runner computes all level/predictor metrics for those cells. At review, **210 validation JSONs remain**, although the protocol, grid and log call them discarded. The validator contains no deletion step. Different `validation_seed_base` values change texts, but `run_chain` uses the same `key_seed_start` for validation and production; the planned key colours overlap. For h = 0 with a fully queried vocabulary, even the fixed-colouring realization is exactly shared. Moreover, `s1_validate.py:31` uses `range(20000)`, which includes reserved keys **10,000–10,999**, contrary to protocol §4's unqualified statement that they are not used.

**Inference.** No production-seed run is visible, and these computations can legitimately be implementation/pilot validation. Nevertheless, they are outcome quantities from the same laws and many of the same keys; “before any outcome” and “discarded” overstate separation. This finding does **not** claim exposure of real held-out texts, or prove that the conductor inspected the retained cell outcomes beyond the disclosed checks.

**Recommendation.** Record the pilot's exact scope and which results were inspected. Correct the retention and seed statements, and establish a separate validation key namespace/range with explicit guards for reserved keys. If prospective independence is intended, choose and record an unexposed production key sample before lock and explain that choice in the log. Resolve the pilot status transparently; deleting files now would not undo exposure. Keep the useful implementation checks, but do not present them as an outcome-free confirmation experiment.

### F9 — minor — The runtime estimate needs a reproducible projection and a fresh-run timing guard

**Evidence.** The measured 343/365-second timings are supported (§4), but the grid says 339 seconds. `s1_validate.py:54–57` comments on projection and then merely saves a log tail; no full-grid cost calculation is written. Rerunning it reuses existing validation cell files, because the runner skips filenames, so a second wall-time measurement could misleadingly time mostly skipped work while retaining old per-cell timers. Width restrictions are checked only after building unused illustration chains.

**Recommendation.** Synchronize 339/343, report chain construction, independent colouring, fixed sorting, matrix/statistics costs and γ multiplicities separately, and distinguish an estimate from an upper bound. Use an isolated fresh validation output location or an explicit cache-status refusal for timing. A small representative sort benchmark is sufficient if more evidence is needed; do not run the study grid before lock. Recompute precision if any budget reduction is selected.

### F10 — minor — Resolve remaining text/code and boundary inconsistencies

**Evidence and recommendations.**

- Protocol §§3–4 say all illustration laws use 2,000 keys; the grid and §11 give V = 100 only 500. §§3/7 and the log call the core fixed subset a reported comparison only, but R3 includes it in its pass fraction. State the actual K and decision role consistently.
- `PackedColours` defaults to `chunk=50` but asserts byte alignment at the second chunk (`s1_core.py:149,157`); a 60-key toy fails with that default. The production grid's 48 works. Use a valid default or support unaligned chunks.
- The rejection function handles M = 0 correctly, but cell summaries average over positive-M texts, and the function named `overall_rejection` is therefore conditional. If zero-M rows occur, multiply by their eligible share for an unconditional rate; all-zero-M input currently produces undefined statistics/errors. Current grid lengths exceed h, so this does not affect those planned cells, but the advertised convention should be implemented and tested.
- The ideal sampler is exact for a queried dictionary, but fixed-colouring hypergeometric draws are indexed by dictionary traversal, not independently seeded by the literal context identity. It is paired across lengths/rules within one chain as promised; do not claim a globally identical deployed fixed key across separately built dictionaries/laws without an extension-consistent sampler. Also state that finite PRNG/hash behavior approximates ideal independent draws, and clarify that the enumerated seed range is a Monte Carlo sample from that model rather than a fully enumerated key population with sampling error.
- The gate still says Study 1 tests frozen-corpus empirical weights; the design notes retain optional corpus inputs and earlier law/σ proposals. The current protocol excludes real text. Mark the deferred pieces explicitly so the narrower protocol is the operative claim. No theorem, other score-family result or remedy should be attributed to Study 1 on this design.

VERDICT: REVISE
