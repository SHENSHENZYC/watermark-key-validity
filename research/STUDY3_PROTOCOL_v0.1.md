# Study 3 — Remedies and transfer: per-key and scheme-level calibration of key-randomised detection tests on real null text — protocol v0.1

Date: 2026-10-13. **Status: LOCKED before outcomes (2026-10-15; `outputs/study3_v0.1/PRE_RUN_LOCK.json`; checkpoint R07 agreed at round 3, `research/reviews/R07_study3-protocol/RESOLUTION.md`; Yichen's "lock and run now" of 2026-10-15).** No per-key level of any Study 3 key exists on any real text. The only computations on real text for this study are key-free: the calibration sets' draw and tokenisation, and the inputs of §2 and §11.
Scripts: `research/study3/s3_core.py` (p-values, the six threshold methods, AutoMark's screen, the calibrated-threshold predictor, the set moments and cross-set shift covariances), `s3_data.py` (the evaluation and calibration sets, the calibration token cache), `s3_keys.py` (the Study 3 key ranges), `s3_inputs.py` (the key-free inputs), `s3_run.py` (the two-pass runner: lock verification, provenance, reuse refusals), `s3_analyze.py` (the inventory gate, the body contract, the rules and the descriptive rows), `s3_validate.py` (fixtures, the validation run, the cost probe, the eligibility counts), `s3_protocol_fill.py` (§11 from the validation and inputs records; not pinned).
Imported unchanged: Study 1's locked core `research/study1/s1_core.py` (the hash, contexts, tuples, retention rules, `bvn_upper`, `mixture_predictor`); Study 2's locked `research/study2/s2_core.py` (real-text chains, uniforms per key chunk, Gumbel scores, the crossed bootstrap), `s2_data.py` (the pools, the draw, the seal, tokenisation) and `s2_keys.py`; `tools/key_policy.py` and `tools/corpora_access.py` (the seal).
Grid: `research/study3/grid_v0.1.json`. Supersedes: none. Gate: `research/KEYCOND_GATE_v0.3.md`: residual-gap items (iii) and (iv), item 5 (H-transfer, which controls the difference of means only), item 7 (remedies), target T2 in its location-family form, and wording constraints 10, 13 and 14. Study 2: `research/STUDY2_REPORT_v0.1.md` §6 Q4 and §8 item 5. R06 carried-forward items: `research/reviews/R06_study2-report/RESOLUTION.md`.

**Decisions this protocol implements** (all recorded in the decision log on 2026-10-13):
- **D9 (scope).** Per-key conformal and tolerance calibration, transferred across every pair of cells within each tokenizer, with the cross-tokenizer case secondary. Compared with the nominal test and with AutoMark's 1/β multiplier and an empirical multiplier. A pre-registered transfer predictor built from the key-free covariance identity. Thresholds frozen for Study 4. No new scheme.
- **D10 (settings).** KGW γ = 0.25 (independent colouring) and Gumbel-max; the raw and distinct rules; h ∈ {0, 1, 2}; L = 256 in all ten cells; both tokenizers; α = 0.01 primary, with 0.05 and 0.001 secondary; β = δ = 0.05.
- **D11 (sizes).** K = 1,000 evaluation keys (23,000–23,999) and 1,000 fitting keys (24,000–24,999). Study 2's frozen texts serve as the evaluation sets (Gutenberg: 7,122 of them). One shared calibration set of 5,000 further texts per cell, disjoint from every Study 3 evaluation set (Gutenberg's includes 2,878 of Study 2's texts, which leave its evaluation set), with nested N_cal ∈ {500, 1,000, 2,000, 5,000}. A calibration-set bootstrap.

## 1. Question and type
**An applied evaluation of remedies for key-conditional validity on real null text, plus an out-of-sample adequacy check of a key-free predictor of what a calibrated threshold does on another text law.**

Study 2 measured how one fixed key's false-positive rate at a nominal α disperses across keys. Its §6 Q4 left the transfer hypotheses open, because a correlation of sampled levels at one threshold does not determine the error of a threshold estimated on one law and applied to another. Study 3 asks four questions:
- **Q1 (calibration within a law).** A deployer sets a per-key threshold on N_cal null texts of the law it will face. How is the realised false-positive rate distributed across keys, by N_cal, rule, width, tokenizer and family? Is that distribution the i.i.d. reference law (Beta(j, N_cal + 1 − j) for a key whose calibration texts are independent draws from its continuous score law; here a model, because the calibration set is one finite-pool sample shared by every key), and at which N_cal does per-key calibration leave a smaller dispersion than the nominal test?
- **Q2 (transfer).** The same threshold, set on law P′, is applied to law P: another English register, another language, or (secondarily) another tokenizer. How is the realised rate distributed, and does a key-free predictor built from the realised texts' exact second moments (§3) anticipate it?
- **Q3 (remedies compared on the null side).** Per method: the key-mean, the dispersion, the upper key quantiles, the share of keys above α, and AutoMark's screen. Six methods are compared:
  - the nominal test;
  - AutoMark's multiplier 1/β = 20 (its guarantee presupposes per-text p-values that are sound over the key; §3);
  - an empirical multiplier fitted on a calibration law (a plug-in analogue of AutoMark's smallest passing multiplier, not their test);
  - a key-agnostic pooled null calibration;
  - per-key conformal calibration;
  - per-key tolerance calibration.

  Each method's null-side cost is its threshold in z-units. The power side is Study 4's.
- **Q4 (the design remedy).** How the retention rule and the context width change all of the above, paired, on the same texts and keys.

What this study does not do: measure power, prove a theorem, claim a transfer guarantee (gate constraint 10), or touch any held-out text.

## 2. Information timing
**Texts.**
- **The evaluation sets** are Study 2's production samples: per cell, the first 10,000 ids of Study 2's seeded permutation (Gutenberg: the first 7,122), as frozen by Study 2's pinned token manifest. They are cut to the first 256 window tokens; for the @1024 cells that is a prefix of Study 2's window, and books start at token 1,000 as before.
- **The calibration sets** are 5,000 further ids of each cell's same permutation, scanned in permutation order and skipping any id that lies in any cell's evaluation set or in an earlier cell's calibration set (578 skipped for wikipedia/en@256 and 952 for wikipedia/en@1024; 0 elsewhere). Every prefix is therefore a uniform sample without replacement from the cell's pool *minus those exclusions*: a uniform permutation scan conditional on the remaining admissible ids. The two English Wikipedia pools are nested, so wikipedia/en@256's scan also excludes the en@1024 evaluation ids, a length-dependent exclusion relative to its full pool. Gutenberg, whose pool holds only 2,122 books Study 2 did not sample, uses positions 7,122–12,121 of its permutation: those 2,122 books and the last 2,878 of Study 2's sample, which leave Study 3's evaluation set. "Same law" and "near-identical law" below are design labels for cells and pairs, not exact distributional equalities.
- The calibration texts were drawn, loaded through the seal and tokenised exactly as Study 2's, **before the lock**. Their arrays are frozen under `outputs/study3_v0.1/tokens_manifest.json`, which records the pool, seed, scan positions, ids digests, every array's SHA-256, the seal's digests, and the digest of Study 2's manifest. The lock pins that manifest, and the runner verifies every array before use.

**Key-free inputs**, computed before the lock and disclosed (`outputs/study3_v0.1/INPUTS.json`, pinned):
- for every evaluation set and every calibration prefix, the set moments: ρ̄, σ², mean V_i, mean M, and the tuple count;
- for every calibration prefix against every evaluation set, the cross-set shift covariance ρ_CE;
- the calibrated-threshold predictor's values for every pair, method, N_cal and α.

These are the predictions the rules compare the outcomes with. The predictions are known before the lock; the outcomes (the per-key realised levels) are not.

**Keys.**
- Evaluation keys 23,000–23,999 and fitting keys 24,000–24,999 (`s3_keys.py`). Both ranges are fresh and disjoint from Study 1's 20,000–21,999, Study 2's 22,000–22,999, the reserved confirmatory range 30,000–30,999 and the validation namespace 1,000,000+.
- The fitting keys enter only the two scheme-level thresholds, and only on calibration sets. A scheme-level threshold is never judged on the keys it was fitted on.

**What was known when this design was chosen (input-adaptive; disclosed):**
- Study 2's outcomes on the same evaluation texts under keys 22,000–22,999 were known: its Table 14 dispersions motivated the grid (D10), and its correlations motivated the transfer question (D9).
- Study 3's keys are fresh, so no Study 3 outcome exists; the texts' key-free structure was known to both studies.
- Broader claims carry the R05 qualification: the design is conditional on the realised texts and chosen from disclosed statistics of them.

**No per-key level of any Study 3 key on real text is computed before the lock.** The validation (§11) uses synthetic tokens and validation keys, and reads only key-free quantities, sizes and digests of the real sets. The held-out partition is untouched (`final: false`).

## 3. Target, sign, units
**Setting.** Each comparison is indexed by:
- a calibration cell P′, with calibration set C and its first N_cal texts C_n;
- an evaluation cell P, with evaluation set E of N_E texts;
- a tokenizer, family, rule, width h (L = 256), method m and level α.

**Primary target.** For each key k, the realised level on E:

α̂_P(k; m, C_n) = N_E⁻¹ Σ_{x∈E} 1{p_k(x) < t_k^m(C_n)}

- p_k(x) is the published test's per-text p-value: for KGW, Φ̄(z) of the z-test centred at γ; for Gumbel-max, the exact Gamma(M, 1) upper tail of the score sum.
- The rejection rule is strict: p < t.
- This is the brief's α_P(k, D_cal) with the calibration set frozen and the evaluation texts fixed. The finite-evaluation-text term is part of it, as in Studies 1 and 2.

**Reported over the K keys** (every table states K, N_E and the subset it is computed on):
- the key-mean, the SD (ddof 1), the 1, 5, 50, 95 and 99% quantiles, the maximum and minimum;
- the shares of keys above α, 2α and 5α, and the number of keys at level 0;
- AutoMark's screen (Algorithm 3, lines 9–11) on the one shared evaluation set:
  - c is the smallest count that is significant at γ_s = 1% for a key at level α (Binomial(N_E, α));
  - B is the number of keys whose count is at least c;
  - b = β + (1 − β)r, with r the screen's null size.

  The keys' screens share the texts, so B is a descriptive count, not their test.

**Methods.** Each method is a threshold on p (`s3_core` docstring); rejection is strict, p < t.
- **nominal:** t = α.
- **multiplier20** (AutoMark's 1/β multiplier, Proposition 1): t = αβ = α/20. Their guarantee (soundness given a key) presupposes a detector whose per-text p-values are sound over the key (their Equation (2)). That holds exactly for the distinct-rule Gumbel test under the hash's ideal-randomness assumption; the distinct-rule KGW z-test is asymptotic (at M = 256 and p < 0.0005 its exact binomial size is 0.00081); the raw rule violates it, since a repeated tuple makes a text's p-value a function of one colouring (a 256-token repetition of one token has z = 27.7 and p = 2.4·10⁻¹⁶⁹ for a quarter of ideal keys). In this study the arm is numerical; a failure of it under the raw rule is not a failure of their proposition, and its label names the correction, not a guarantee.
- **empirical multiplier** (scheme level; a plug-in analogue of AutoMark App. C's "smallest passing multiplier"; it runs neither their Algorithm 2 nor their Algorithm 3 and inherits no test-level guarantee). On C with the fitting keys:
  - for each fitting key, t*_k is the (⌊αN_C⌋+1)-th smallest p, the largest threshold whose realised level on C is at most α;
  - t_emp = min(α, the (⌊βK_fit⌋+1)-th smallest t*_k), so that at most ⌊βK_fit⌋ fitting keys exceed α on C;
  - κ̂ = α/t_emp.
- **pooled** (scheme level; key-agnostic null calibration): t_pool is the (⌊αN_C K_fit⌋+1)-th smallest of the fitting keys' p-values on C, the largest threshold whose key-averaged realised level on C is at most α. It is not capped at α.
- **per-key conformal:**
  - t_k is the j-th smallest of key k's p-values on C_n, with j = ⌊α(N_cal+1)⌋ computed in exact rational arithmetic;
  - j = 0 never rejects;
  - under exchangeability of the calibration texts and a fresh text of the same law, the rank argument gives marginal validity only: the fresh text rejects with probability at most j/(N_cal+1), averaged over the calibration draw;
  - when a key's calibration texts are i.i.d. draws from its continuous score law, the population level given the calibration set is exactly Beta(j, N_cal+1−j) (Vovk 2012, p.2: examples "generated independently from the same probability distribution"). That is the reference law the predictor adopts as a model (§3, below); it is not implied by exchangeability alone, and sampling without replacement from a finite pool gives a discrete rank law instead.
- **per-key tolerance** (Vovk 2012, Prop. 2b):
  - the j_δ-th smallest, with j_δ = max{j ≥ 1: P(Bin(N_cal, α) ≤ j−1) ≤ δ} (a numerical binomial CDF; the conformal and floor indices are exact rational arithmetic);
  - under the same i.i.d. continuous-score condition, P(population level > α) ≤ δ over repeated calibration draws for a fixed key. That is a statement about the calibration draw per key, not a statement that at most a δ share of keys fail on the one frozen calibration set C of this study; the comparison of the measured share of keys above α with δ is a reference diagnostic (§7), not a PAC-over-keys guarantee;
  - if no such j exists, the method never rejects ("abstains": at α = 0.001 for N_cal ≤ 2,000).

  For discrete (KGW) scores both per-key methods are conservative under those conditions: a tie at the order statistic is not rejected. The calibration set is one finite-pool sample shared by every key (§2), so every statement above that assumes i.i.d. sampling is a model for this study, whose adequacy T1 measures.

**The null-side cost** of each threshold is z(t) − z_α, with z(t) = Φ̄⁻¹(t). The runner stores, per calibration unit, family, rule, method, N_cal and α, the 5, 50 and 95% quantiles and the mean of z(t) and of z(t) − z_α over the keys with a positive threshold (n_positive), and the number of abstaining keys (n_abstain; an all-abstaining method has no quantiles); for the scheme-level methods it stores t_emp, κ̂ and t_pool with their z values. The power cost is Study 4's.

**The calibrated-threshold predictor** (key-free; Study 1's common-factor model extended to a threshold set on another text set). The predictor's inputs are exact second moments. Its structure is an assumption: one Gaussian shift, one residual variance per set, Gaussian residuals, and p read as Φ̄ of the standardised statistic for both families. Study 2 measured that structure at a fixed threshold, and found a median under-prediction of about a fifth at γ = 0.25 and α = 0.01.

1. **The model.** In z-units, on a text set S, key k gives z_i = D_k^S + e_i: D_k^S is the key's mean shift on S's law, and the residuals e_i are i.i.d. N(0, σ_S²) across texts and keys.
2. **The inputs, exact identities at the realised weights:**
   - ρ̄_S is Study 1's unbiased average pairwise across-key covariance of two texts' z;
   - σ_S² = mean_i V_i − ρ̄_S, with V_i = Σ_u n_iu²/M_i;
   - ρ_CE = Σ_u w_C(u) w_E(u), the mean over cross pairs of Cov_K(z_i, z_j). Here w is the set's document-averaged z-weight n_iu/√M_i over the integer tuple ids. This is exact under independent colours or unit-variance scores (the hash is a function of the integer ids alone), and the same for both families.
3. **The threshold.** A per-key threshold with order index j sits at D_k^C + σ_C Φ⁻¹(U), where U ~ Beta(N_cal+1−j, j) is the coverage.
4. **The realised level on E's law:** ℓ = Φ̄((X + σ_C Φ⁻¹(U))/σ_E), where X = D^C − D^E ~ N(0, v) and v = ρ̄_C + ρ̄_E − 2ρ_CE. The estimate obeys an exact identity: because ρ̄ = A − σ²/n for each set, v + τ_v = ‖w_C − w_E‖² ≥ 0 with τ_v = σ_C²/N_cal + σ_E²/N_E. A negative estimate within that floor is sampling noise around a non-negative population quantity (0 on the diagonal); it is set to 0, recorded as v_raw, and not flagged. A value below −τ_v is impossible and is flagged; such a pair is ineligible for T1.
5. **The computation.**
   - Given U, the integral over X is closed: the mean is Φ̄(a/s) with s = √(σ_E² + v); the second moment is Owen's T, with correlation v/(σ_E² + v).
   - The U integral is a 20,000-node midpoint rule on the probability scale. The integrand is smooth; the rule's error against the exact Beta law is in §11.
   - The finite-evaluation-text term E[ℓ(1 − ℓ)]/N_E is added for the conditional SD.
   - The theory share is the population variance over the total.
   - Two predicted shares of keys above each level a ∈ {α, 2α, 5α}, which are different estimands: the **population share** P(ℓ > a), in closed form from the same law; and the **finite-evaluation share** P(count > ⌊aN_E⌋) = E[BinomSF(⌊aN_E⌋; N_E, ℓ)]. A measured share over N_E evaluation texts estimates the finite-evaluation one, which the comparison uses; the two differ by the binomial noise of the count (for the tolerance method at N_cal = 5,000 and α = 0.01 within a law: 0.0466 against 0.0767 at N_E = 10,000). **Computation (R07 F9).** Through the identity BinomSF(m; N_E, ℓ) = P(W < ℓ) with W ~ Beta(m+1, N_E−m), the per-key share is P(X < σ_E Φ̄⁻¹(W) − σ_C Φ⁻¹(U)) = E_{U,W}[Φ((σ_E Φ̄⁻¹(W) − σ_C Φ⁻¹(U))/√v)], a smooth integrand on the probability scales of U and W, integrated by a 1,000 × 1,000 midpoint rule; at v = 0 it is E_U[BinomSF(m; N_E, ℓ(U))] on 1,000 midpoint nodes of U. For a fixed threshold at z = t_z with D ~ N(0, ρ̄_E) the share is E_W[Φ̄((t_z − σ_E Φ̄⁻¹(W))/√ρ̄_E)] on 4,000 midpoint nodes of W (ρ̄_E = 0: the binomial tail at the constant level). A first version integrated the binomial tail over X by a fixed Gauss–Hermite rule and missed the tail's narrow transition (errors of 2–3 percentage points at h = 0 on the frozen inputs; found by the reviewer at R07 round 2 and corrected before any outcome). §11 checks the rule against the Beta-binomial law within a law, against a four-fold finer rule on settings taken from the frozen inputs (the largest and smallest positive v, the extreme residual-scale ratios, both evaluation sizes, every level, both methods, a random sample) and against Monte Carlo at three settings, with the acceptance errors of §9.
6. **Special cases.**
   - Within one law, C and E are disjoint samples, so v estimates 0; then, under the model, the level is exactly Beta(j, N_cal+1−j) when σ_C = σ_E.
   - Fixed thresholds go through `s1_core.mixture_predictor` on E. The scheme-level thresholds use their model-implied values:
     - the empirical multiplier: z_emp = σ_C z_α + √ρ̄_C z_β, capped at α;
     - pooled: z_pool = z_α √(ρ̄_C + σ_C²).

**Units and pairing.**
- Keys: K = 1,000 evaluation keys.
- Texts: N_E = 10,000 per evaluation set (Gutenberg 7,122); a calibration set of 5,000 per cell.
- The same keys and the same evaluation texts serve every method, calibration source, rule, family and width of a cell and tokenizer, so every comparison inside an evaluation cell is paired.
- The calibration prefixes are nested.

**Sign conventions.**
- "Larger dispersion" means a larger SD of α̂ across keys.
- "Calibration reduces the dispersion" means R_obs = SD(conformal)/SD(nominal) < 1.
- The predictor is adequate for a pair when the observed-to-predicted SD ratio lies in [2/3, 3/2] (Studies 1–2's band).

## 4. Data, split and holdout
**Cells.** The ten cells of Studies 2 and 3: news/en@256, wikipedia/en@256, stackexchange/en@256, wikipedia/{de, ru, ar, zh, ja}@256, wikipedia/en@1024 and gutenberg/en@1024, all in the open partition.

**Eligibility.** Each cell's own pool, as Study 2 defined it: length-eligible under both tokenizers for the cell's window. A cell's calibration texts therefore follow the cell's own law: the @1024 cells' texts are at least 1,024 tokens long (books: 2,024) although only 256 are scored.

**Sets.** The evaluation and calibration sets are as in §2, with every calibration id disjoint from every evaluation set and from every other calibration set (asserted in `s3_data.plan_sets`). The two English Wikipedia cells' evaluation sets share ids (Study 2's samples overlap; §11 gives the count); this affects comparisons between those two deployment cells, not the disjointness of calibration from evaluation.

**Tokenisation.** As Study 2's (§4 there): both pinned tokenizers, no special tokens, the capped character prefix, and the cell's window cut to the first 256 tokens.

**Holdout.** The sealed 20% is untouched: no lock of this study is final.

**Storage.** Raw text never leaves `research/corpora/data/`. The token caches are git-ignored. The committed record holds counts and statistics only.

## 5. Competitors and baselines
**Detectors.**
- The red–green z-test at γ = 0.25 under independent colouring. Here g = γ exactly, because γV is an integer at both vocabularies.
- The Gumbel-max test: the score −ln(1 − U(key, tuple)) summed over the retained positions, with the exact Gamma(M, 1) tail.
- The same uniforms serve both families, so the two families are paired through the keys.

**Grid.** The raw and distinct rules; h ∈ {0, 1, 2}; L = 256; α ∈ {0.01, 0.05, 0.001}.

**Methods** (§3): nominal, multiplier20 (1/β at β = 0.05), empirical multiplier (β = 0.05), pooled, per-key conformal and per-key tolerance (δ = 0.05), at N_cal ∈ {500, 1,000, 2,000, 5,000}.

**Calibration sources.** For each evaluation cell, every calibration cell under the same tokenizer: the diagonal plus 9 others. Secondarily, every calibration cell under the other tokenizer, for the scheme-level methods and the per-key methods at N_cal ∈ {1,000, 5,000} and α = 0.01.

**Pair classes** (grid fields):
- diagonal;
- near-identical (wikipedia/en@256 with wikipedia/en@1024);
- within-English (the five English cells);
- English–other;
- other–other (pairs of non-English Wikipedia languages);
- cross-tokenizer.

**The published record each method follows** (cited, not re-run):
- the 1/β multiplier (for a detector sound over the key: Proposition 1's prerequisite) and the screen: AutoMark (Gloaguen, Staab, Vechev 2026, Eq. 2, Eq. 3, Proposition 1, Algorithm 3, App. C; gate constraints 13–14);
- per-key empirical thresholds: Aremu et al. 2026; Genhatharan 2026 (per key and length, priced);
- class-conditional conformal calibration with the frozen-calibration variability: Delbianco, Tohmé, Acciarri 2026;
- training-conditional (tolerance) validity: Vovk 2012;
- null-corpus calibration and its portability limits: SAC-Copula, Li & He 2026; Xie, Chen, Ren, Su 2025.

## 6. Primary metric and contrast
**The primary block:**
- family KGW;
- the raw and distinct rules;
- h ∈ {1, 2};
- both tokenizers;
- every ordered pair (calibration cell, evaluation cell) within a tokenizer, the diagonal included (100 per tokenizer);
- per-key conformal calibration at N_cal ∈ {1,000, 5,000};
- α = 0.01.

That is 1,600 (pair, setting) rows. The pairs of one evaluation cell share keys and texts, and the rows are counted as paired, as in Studies 1–2.

**T1 (adequacy of the calibrated-threshold predictor; pass/fail).**
- **Statistic:** the ratio SD_obs(α̂)/SD_pred, with SD_pred the predictor's conditional SD, and its key-bootstrap 95% interval (200 resamples of the keys).
- **Classification:** consistent when the interval lies inside [2/3, 3/2], inconsistent when it is disjoint from it, unresolved otherwise.
- **Eligibility:** a predicted theory share of at least 0.75 and no flag on the prediction. The theory share separates the dispersion that the shifts and the calibration sample create from the finite-evaluation-text floor.
- **Pass:** at least 30 resolved, and at least 80% of the resolved consistent.
- **Reported:** the candidate, eligible, resolved, consistent, inconsistent and unresolved counts by N_cal, rule, h, tokenizer and pair class, never the share alone. Every inconsistent or unresolved row is listed with v, v_raw, τ_v, ρ̄_C, ρ̄_E, ρ_CE, σ_C², σ_E², j, N_E, K, the theory share, and the observed and predicted key-means (all carried in the analyzer's T1 rows).
- **The diagonal at N_cal = 5,000 is never eligible:** the Beta term's SD (about 0.14 pp) is of the order of the finite-evaluation floor (about 0.10 pp), so the theory share lies below 0.75 (0.59–0.67 by the key-free inputs). T1's pass therefore establishes nothing about adequacy on that block; it is reported descriptively against the i.i.d. reference law with the floor stated.

**T2 (does per-key calibration change the dispersion as predicted?; pass/fail).**
- **Material pairs:** over the same block, the pairs whose predicted ratio R_pred = SD_pred(conformal, C_n → E)/SD_pred(nominal on E) lies outside [2/3, 3/2]. The wide band absorbs the fixed-threshold predictor's measured bias of about a fifth (R06's carried-forward item: the baseline's bias enters the error budget).
- **Statistic:** the observed ratio R_obs = SD_obs(conformal)/SD_obs(nominal), with the same keys and the same evaluation texts, and its paired key-bootstrap 95% interval (the same resampled keys in numerator and denominator).
- **Classification:** agree when the interval excludes 1 on the predicted side, disagree when it excludes 1 on the other side, unresolved when it contains 1.
- **Pass:** at least 30 resolved, and at least 90% of the resolved agree.
- T2 is a sign rule: it asks whether the direction of calibration's effect on the dispersion is predictable from the key-free inputs. The magnitude is T1's question.

The predicted sides are pre-stated per pair in `INPUTS.json`, and their counts by class are in §11:
- "calibration helps" (R_pred < 2/3) is expected on the diagonal under the raw rule and at large N_cal;
- "calibration hurts" (R_pred > 3/2) is expected where the calibration and evaluation laws share little tuple mass, so that v ≈ ρ̄_C + ρ̄_E.

## 7. Secondary diagnostics (descriptive)
Every item below is computed by the analyzer from the stored counts (`results.json` fields named), or recorded by the runner where the counts do not determine it.

| Promised output | Estimand and denominator | Source (analyzer / runner field) |
|---|---|---|
| The remedy table: per method × pair class × family × rule × h × α — key-mean, SD, quantiles, max, measured shares above α / 2α / 5α, keys at 0, AutoMark's screen B against b·K, and the predicted mean, SD and shares above α / 2α / 5α as two estimands (population and finite-evaluation; the finite-evaluation share is the one comparable with the measured share) | Over the K = 1,000 evaluation keys, on the N_E evaluation texts of the evaluation cell | `descriptive_rows` (from the counts; the predictions from `INPUTS.json`: `pred_share_above_*_pop`, `pred_share_above_*_finite`) |
| The exceedance diagnostic for each method: the measured share of keys with realised level above α beside β (multipliers) or δ (tolerance) and beside the finite-evaluation prediction, with the screen. A reference diagnostic, not a PAC-over-keys check: the tolerance statement is over calibration draws per key (§3), the measured share carries the finite-evaluation noise, and the screen's B is a dependent count on one shared evaluation set | As above | `descriptive_rows` |
| The null-side cost: per calibration unit, family, rule, method, N_cal and α, the 5, 50, 95% quantiles and mean of z(t) and of z(t) − z_α over the keys with a positive threshold, with n_positive and n_abstain; κ̂, t_emp and t_pool with z_emp and z_pool | Over the K evaluation keys with a positive threshold (per-key methods) or the K_fit fitting keys on the N_C = 5,000 calibration texts (scheme-level methods) | `pass1[...]["summary"]` (runner pass 1: `per_key_z[...]["z"]`, `scheme`) |
| The break-even N_cal: per diagonal setting, the smallest N_cal at which R_obs < 1 with its paired interval excluding 1 | Paired over the K keys | Computed by the report builder from `descriptive_rows` and the counts; labelled descriptive |
| The calibration-set component: over B = 50 resamples of the calibration texts, the SD of the key-mean, SD, share above α and 99% key quantile of the per-key methods (α = 0.01; N_cal 1,000 and 5,000; every same-tokenizer calibration cell) | Over the K keys per resample | `cal_boot` (runner pass 2) |
| The crossed key-by-document bootstrap on the diagonal (200): the quantiles, the sampled maximum and the shares above 2α and 5α for the nominal, multiplier20, empirical and pooled methods and the per-key methods at N_cal 1,000 and 5,000 (α = 0.01) | Texts and keys resampled; the maximum is the sampled maximum's interval, never a population extreme (gate constraint 12) | `crossed` (runner pass 2) |
| The cross-tokenizer transfer (calibrate under one tokenizer's tokens, evaluate under the other's with the same key) with its prediction | Over the K keys | `descriptive_rows` with class `cross_tokenizer` |
| The Gumbel family, h = 0, α = 0.05 and 0.001, and N_cal = 500 and 2,000: the same summaries, with T1's statistic reported as a secondary block | As above | `descriptive_rows`; the builder computes the secondary T1 blocks from the counts with the analyzer's functions |
| T1 and T2 rows with every diagnostic (T1: v, v_raw, τ_v, ρ̄_C, ρ̄_E, ρ_CE, σ_C², σ_E², j, N_E, K, the theory share, the observed and predicted SDs and key-means; T2: R_pred, R_obs with its paired interval, the nominal SDs, N_E, K) | As §6 | `t1_rows`, `t2_rows` |
| REP | §9 | `rep_rows` |

The **near-identical pair** (wikipedia/en@256 with wikipedia/en@1024) is the positive control of transfer: its predicted v is small, so its transferred dispersion should be close to the diagonal's. No rule is decided on it.

## 8. Uncertainty
**Keys and texts.**
- Keys are independent draws given the texts. Every across-key statistic of the primary rules carries a key-bootstrap interval (200 resamples; paired where two methods share the keys).
- The calibration texts and the evaluation texts are fixed: the target is conditional on them.

**The two bootstraps.**
- **The calibration-set bootstrap** (B = 50 resamples of the N_cal texts with replacement, per calibration cell; thresholds recomputed; levels on E) describes how the summaries would vary over calibration sets. It is descriptive, and no rule uses it.
- **The crossed key-by-document bootstrap** on the diagonal (200) gives the deployer's intervals.

**Precision.**
- The normal-theory relative SE of an SD is 2.2% at K = 1,000.
- For nearly Bernoulli per-key levels it is larger (Study 2 §8, R05 F7), and the 95% intervals are nominal.
- At the primary α = 0.01, N_E = 10,000 contributes a finite-text SD of about √(α/N_E) = 0.1 pp per key. The predictor includes this term (§3), and it is part of the target.

**Seeds.**
- The calibration-set bootstrap: sha256 of the unit name, with 20261014.
- The crossed bootstrap: sha256 of the unit name, with 20261015.
- The analyzer's key bootstraps: sha256 of the row name, with 20261016.
- The validation: 99261013 and 99261014.
- The colouring hash is Study 1's splitmix64 with the key mixed in. A hash supplies computational, not statistical, independence. The validation checks the across-key covariance identity with validation keys (§11).

## 9. Pre-registered rules and materiality thresholds (every tolerance the code applies is stated here; R04 F1)
- **T1 (adequacy).** As in §6:
  - band [2/3, 3/2];
  - eligibility: theory share at least 0.75 and no prediction flag;
  - at least 30 resolved, and at least 80% consistent.
- **T2 (sign).** As in §6:
  - material band [2/3, 3/2] on R_pred;
  - at least 30 resolved, and at least 90% agree.
- **REP (integrity: Study 2's nominal dispersion reproduced with independent keys).**
  - **Scope:** every (tokenizer, evaluation cell except Gutenberg, h, rule) of the KGW family at α = 0.01. Gutenberg's evaluation set is a 7,122-text prefix of Study 2's.
  - **Comparison:** the nominal across-key SD with Study 3's keys against Study 2's observed SD on the same texts with Study 2's keys (Study 2's record). Its inventory digest is checked against Study 2's pinned `RUN_MANIFEST.json`.
  - **Gross failure:** |SD₃ − SD₂| > 6·√(se₃² + se₂²) + 10⁻¹². Here se₃ is Study 3's key-bootstrap SE, and se₂ is Study 2's stored key-bootstrap SE.
  - **Pass:** no gross failure. The threshold is heuristic, as in Study 2's S3; the two key samples are independent.
  - **On failure:** an implementation audit, and no outcome is reported until it is resolved in a new version.
- **Integrity checks (refusals, not rules).**
  - **The lock.** The runner verifies it against this version's canonical identity before any study unit: study `study3_v0.1`; the protocol, grid, validation, inputs and tokens-manifest paths named here; checkpoint R07; an ISO date not before 2026-10-13; 64-hex digests of exactly the pinned files, which must match; `approved_by: "Yichen"`; `before_outcomes: true`; `final: false`; and the key record equal to the grid's. The pinned files include Study 2's token manifest and run manifest. The runner also checks the tokens manifest's sizes against the grid and its binding to Study 2's manifest.
  - **Token arrays.** Every array is verified against its manifest before use.
  - **Provenance.** Every unit carries its provenance (the lock, grid, code and manifest digests, the unit's token digest, the key starts, K, K_fit, N) and its identity. An evaluation unit also carries the digests of every threshold file it used. A unit with foreign provenance, another identity or a mismatching array digest stops the run.
  - **The analyzer** requires the verified lock before reading any unit in study mode. Its inventory gate derives the provenance every unit must carry from the lock, the canonical grid, the pinned code and the manifests (never from the unit itself: the lock, grid, core, runner and manifest digests, the unit's token digest, the key starts, K, K_fit and N) and refuses:
    - an incomplete or padded inventory;
    - a unit whose provenance differs from the derived one in any field, or whose identity differs;
    - an evaluation unit whose counts file differs from its digest, whose threshold map does not cover exactly the registered sources (every calibration cell under every tokenizer of the run), whose digests differ from the pass-1 records' or between its record and its provenance copy;
    - a calibration unit whose committed thresholds file is missing or differs from its digest, or which lacks its summary or info;
    - any calibration unit that fails the **calibration contract**: N_C, K, K_fit, the α list, the N_cal list and the method lists as registered; exactly the expected threshold arrays (per-key arrays of length K for every family, rule, method, N_cal and α; one scalar per scheme-level method and α), finite in [0, 1]; the empirical multiplier's threshold at most α; every variant's thresholds non-decreasing in α (tolerance 10⁻¹⁵); the recorded order index equal to its recomputation and an abstaining method carrying an all-zero array; every registered z summary (abstaining entries included) equal, field by field, to its recomputation from the committed array; the scheme summaries equal to the arrays (within 10⁻¹²), κ̂ = α/t_emp (∞ at 0), z_emp and z_pool equal to their recomputation, and the fit detail's indices equal to ⌊αN_C⌋ and ⌊βK_fit⌋;
    - any evaluation unit that fails the **evaluation contract**: N_E equal to the registered size of its cell (and to the provenance's N); the axis metadata (the α list, the same-tokenizer and cross-tokenizer variant lists, the source list, the cross tokenizers, the fixed variants) exactly as registered; exactly the expected count arrays with the registered shapes and dtype uint16; every count in [0, N_E]; counts nested across α for every variant (every method's threshold is non-decreasing in α); the crossed block on the diagonal with every registered variant populated (finite ordered bounds in [0, 1], a finite non-negative SE, B = 200); the calibration bootstrap with B = 50 finite values in [0, 1] for every statistic, same-tokenizer source and registered (method, N_cal); the screening constants c, r and b finite and equal to their recomputation (c exactly; r and b within 10⁻¹²).
    The validation (§11) exercises each refusal on a mutated copy of the complete pilot inventory and the acceptance of the unmutated one.
- **Other constants the code applies:**
  - key bootstrap 200; crossed bootstrap 200; calibration bootstrap 50;
  - the Beta midpoint rule, 20,000 nodes;
  - the screen's γ_s = 0.01;
  - a negative estimate of v is set to 0 without a flag when it lies within its algebraic floor −τ_v (§3), and flagged as impossible below −τ_v(1 + 10⁻⁹);
  - the interval slack 10⁻¹² at the range bounds of the crossed block;
  - the key chunk 8;
  - the finite-evaluation shares: 1,000 midpoint nodes per Beta variable (U and W) for the per-key methods and 4,000 nodes in W for the fixed thresholds (§3); the population shares are closed forms; the validation's acceptance errors: 10⁻⁵ against the Beta-binomial law within a law (and 10⁻³ for the population share against the Beta law there, the 20,000-node rule's indicator error), 10⁻⁹ against the binomial law at ρ̄_E = 0, 10⁻⁴ between the production rule and a four-fold finer rule for the per-key methods on frozen-input settings and 10⁻⁵ for the fixed thresholds, and 4 Monte-Carlo SEs + 10⁻⁴ against 400,000 draws, the SE computed as √(max(p̂(1 − p̂), 10⁻¹²)/400,000);
  - the calibration contract's slacks: the empirical threshold at most α + 10⁻¹² in the summary and equal to its array within 10⁻¹²; the z summaries' floats equal to their recomputation within 10⁻¹² · max(1, |reference|) (absolute below unit magnitude, relative above it; counts and None exactly), κ̂, z_emp and z_pool within 10⁻⁹ · max(1, |reference|), and κ̂ = +∞ required, and only +∞ accepted, when t_emp = 0; the v floor's comparison carries an additional −10⁻³⁰⁰ guard (no practical effect);
  - the conformal order index and the empirical and pooled floor indices are exact rational arithmetic; the tolerance index uses the numerical binomial CDF (its maximality is checked at every registered setting in §11).
  - Every text retains at least one tuple at L = 256 under both rules (asserted); g = γ is asserted at both vocabularies.

## 10. Stop and pivot rules, and what a null result means
- **Over budget.** If the validation projects more than the 10-hour budget, the grid is reduced before the lock (never after it), in the pre-registered order of `grid_v0.1.json`:
  1. calibration bootstrap 50 → 20;
  2. crossed bootstrap 200 → 100;
  3. drop the cross-tokenizer evaluation;
  4. K_fit 1,000 → 500;
  5. drop α = 0.001.
- **REP fails.** The run's outcomes are not reported, and the implementation is audited in a new version; the failed version is kept.
- **T1 fails.** The report states the calibrated-threshold predictor's range of validity on real text (by pair class, N_cal, rule, width, tokenizer and v), and the measured realised levels stand on their own. The research question is answered by the measured distributions whichever way T1 comes out.
- **T2 fails.** Whether per-key calibration reduces or increases the dispersion is not predictable from the key-free inputs at the material band, and the per-class counts show where. That would be a result about the deployability of per-key calibration, not a failure of the study.

There is no pivot of the project on Study 3's outcome. Study 4 (the power side) takes the frozen thresholds; its design is Yichen's decision after Study 3's report.

## 11. Inputs validated before the lock (synthetic tokens and validation keys; key-free inputs on the real sets; no per-key level on real text)
<!-- S11:BEGIN (generated by research/study3/s3_protocol_fill.py; do not edit by hand) -->
*Generated from `VALIDATION.json` (run 20261015T193602Z) and `INPUTS.json` by `research/study3/s3_protocol_fill.py`; no number below is typed by hand.* The pre-lock re-screen is `research/study3/rescreen/RESCREEN_2026-10-13.md`.

**(a) The token caches.** Every calibration array matches its manifest digest, shape, dtype and id range; the evaluation and calibration plan is reproduced from the units metadata (Study 2's draws, the scan, disjointness: True); Study 2's token manifest is bound by digest (True); the seal's partition and units digests are current (True): all_ok = True. Calibration ids at permutation positions news_en_256 10,000–14,999 (0 skipped); wikipedia_en_256 10,000–15,577 (578 skipped); stackexchange_en_256 10,000–14,999 (0 skipped); wikipedia_de_256 10,000–14,999 (0 skipped); wikipedia_ru_256 10,000–14,999 (0 skipped); wikipedia_ar_256 10,000–14,999 (0 skipped); wikipedia_zh_256 10,000–14,999 (0 skipped); wikipedia_ja_256 10,000–14,999 (0 skipped); wikipedia_en_1024 10,000–15,951 (952 skipped); gutenberg_en_1024 7,122–12,121 (0 skipped). Evaluation sets: N_E = 10,000 (gutenberg 7,122); calibration sets: 5,000 per cell under both tokenizers.

**(b) Fixtures (validation randomness; synthetic scores and tokens).** The order indices: N_cal 500, α 0.01: j_conf 5, j_tol 2; N_cal 500, α 0.05: j_conf 25, j_tol 17; N_cal 500, α 0.001: j_conf 0, j_tol 0; N_cal 1,000, α 0.01: j_conf 10, j_tol 5; N_cal 1,000, α 0.05: j_conf 50, j_tol 39; N_cal 1,000, α 0.001: j_conf 1, j_tol 0; N_cal 2,000, α 0.01: j_conf 20, j_tol 13; N_cal 2,000, α 0.05: j_conf 100, j_tol 84; N_cal 2,000, α 0.001: j_conf 2, j_tol 0; N_cal 5,000, α 0.01: j_conf 50, j_tol 39; N_cal 5,000, α 0.05: j_conf 250, j_tol 225; N_cal 5,000, α 0.001: j_conf 5, j_tol 2 (the tolerance index maximal in every case: True; j = 0 means the method never rejects). On i.i.d. continuous scores (20,000 replicates): N_cal 1000, α 0.01: conformal mean 0.01 against the exact 0.00999, SD 0.003132 against 0.003142, tolerance share above α 0.028 against the exact tail 0.0287; N_cal 5000, α 0.01: conformal mean 0.009988 against the exact 0.009998, SD 0.001396 against 0.001407, tolerance share above α 0.0455 against the exact tail 0.0466; N_cal 2000, α 0.05: conformal mean 0.05001 against the exact 0.04998, SD 0.004838 against 0.00487, tolerance share above α 0.0406 against the exact tail 0.0423; N_cal 5000, α 0.001: conformal mean 0.001001 against the exact 0.0009998, SD 0.0004489 against 0.0004469, tolerance share above α 0.0396 against the exact tail 0.0404 (all within tolerance: True). On discrete (binomial, M = 250, γ = 0.25) scores the conformal level is conservative (mean 0.008221 against the continuous bound 0.00999: True). The empirical multiplier's and the pooled threshold's defining properties and maximality hold on 20 random fitting tables at every α (True); `counts_below` equals brute force with ties (True).
The calibrated-threshold predictor reproduces the exact Beta law within a law (largest relative error of the mean 4e-06, of the SD 6.9e-05: True) and 400,000-draw Monte Carlo with a cross-law shift and unequal residual variances (mean 0.01673 / 0.01674, SD 0.009393 / 0.009382, share above α 0.751 / 0.752; mean 0.01242 / 0.01242, SD 0.003899 / 0.003899, share above α 0.71 / 0.711; mean 0.05831 / 0.0583, SD 0.03791 / 0.0379, share above α 0.495 / 0.495; predicted / Monte Carlo; all within 1%: True). `cross_cov` equals the brute-force mean over cross pairs and `set_moments` equals Study 1's `population_estimates` field for field (True); with 4,000 validation keys the across-key covariance of two sets' mean z matches the identity ⟨w_C, w_E⟩ (h 0 raw: 4.4 against 4.43, z -0.26; h 0 distinct: 0.297 against 0.302, z -0.7; h 1 raw: 0.295 against 0.304, z -1.3; h 1 distinct: 0.0905 against 0.0923, z -0.85; all within 4 SE: True).
The finite-evaluation exceedance shares (§3): within a law (v = 0, equal residual scales) the predictor equals the Beta-binomial law at every level in 5 settings (largest absolute error 2e-06; acceptance 1e-05), and a fixed threshold at ρ_E = 0 equals the binomial law (error 0; acceptance 1e-09). With a positive shift variance, the production rule (Q = 1,000 midpoint nodes per Beta variable) against a four-fold finer rule on 45 settings taken from the frozen inputs (the largest and smallest positive v, 3.02 and 6.96e-09; the residual-scale ratios 0.612–1.69; both evaluation sizes; every level; both per-key methods; a seeded random sample; 46,767 candidate settings): largest absolute difference 6.9e-05 (acceptance 0.0001); the fixed thresholds' rule (Q = 4,000) against Q = 16,000 on 120 (set, α, method) cases: largest difference 4.5e-06 (acceptance 1e-05). Monte Carlo (400,000 draws of U, X and the binomial count): llama|wikipedia_en_1024->llama|wikipedia_zh_256 conformal N_cal 5000 at alpha: predicted 0.6522 against 0.653 ± 0.00075; llama|wikipedia_en_1024->llama|wikipedia_zh_256 conformal N_cal 5000 at 2alpha: predicted 0.5427 against 0.5417 ± 0.00079; llama|gutenberg_en_1024->llama|wikipedia_ja_256 conformal N_cal 5000 at alpha: predicted 0.4904 against 0.4909 ± 0.00079; llama|gutenberg_en_1024->llama|wikipedia_ja_256 conformal N_cal 5000 at 2alpha: predicted 0.3933 against 0.3929 ± 0.00077; llama|news_en_256|E nominal N_cal — at 2alpha: predicted 0.6098 against 0.6104 ± 0.00077; llama|news_en_256|E nominal N_cal — at 5alpha: predicted 0.4378 against 0.4383 ± 0.00078 (acceptance 4 SE + 1e-4); all as required: True.

**(c)–(f) Fixtures (all as required).** The key policy accepts the evaluation, fitting and validation ranges and refuses the reserved range, Study 1's and Study 2's ranges, the audit's development keys, keys below the validation namespace, and each Study 3 range under the other purpose (True); the lock schema accepts the complete canonical lock under a copied root and refuses 22 of 22 variants (among them a missing `approved_by`, `final: true`, `before_outcomes: false`, a non-ISO or early date, the wrong study, non-canonical paths, checkpoint R05, the R06 resolution, a tampered, non-hex, missing or extra digest, a missing Study 2 manifest digest, a key-record or fit-start mismatch, a wrong review digest and a non-canonical grid argument; accepted: ['complete_canonical']); a matching unit is reusable and a foreign grid, another identity, another mode or a tampered counts file are refused (True); the analyzer accepts the complete pilot inventory and 1 boundary case (a zero empirical threshold with κ̂ = +∞) and refuses 70 mutations of it (the inventory: a missing or extra unit; the provenance gate: every field of the derived provenance altered in turn, the study, the mode and the identity; the threshold map: emptied, one source missing, a foreign digest, a copy mismatch; the committed thresholds file missing or tampered; the calibration contract: a missing summary, a wrong size or α axis, a threshold above 1 or non-finite, a wrong shape, an extra key, thresholds not nested across α, an abstention violated, an empirical threshold above α; the evaluation contract: N_E wrong with the screen recomputed, the α, variant and source axes reversed or shortened, a wrong fixed-variant list, a fabricated cross-tokenizer source, an extra or missing array, a count above N_E, counts not nested, a wrong shape or dtype, a crossed block missing, unpopulated, wrong-B or with a non-finite SE, calibration-bootstrap values missing, non-finite, negative or above 1, a wrong, non-finite or missing screening constant; the calibration summaries: an emptied or removed z summary, a wrong or missing cost or count field, a wrong κ̂, z_emp or fit index, a finite κ̂ at a zero threshold) (True); the REP decision function passes exactly equal and within-noise values and flags a gross one (True).

**(g) The timed validation run.** The synthetic grid (3 Zipf cells at V = 128,256 sharing the vocabulary to different degrees, h ∈ [0, 1], K = 64 evaluation and 64 fitting validation keys, N_eval = 2,000, a 1,000-text calibration set, N_cal ∈ [100, 500, 1000]) ran in 7.5 s (12 units) and the analyzer executed in pilot mode on it with the pilot inputs (status: analyzed; T1 rows 18, eligible 8; T2 rows 18, material 18; descriptive rows 1872; the conductor read the execution status and the counts only).

**(h) The cost probe.** One production-sized pass-1 and pass-2 unit on synthetic Zipf tokens at V = 128,256 with K = 1,000 evaluation and 1,000 fitting validation keys (N_cal set 5,000, N_E 10,000, every calibration source and the cross-tokenizer counts included): h = 0: pass 1 24.7 s (|D| 81,541), pass 2 9.1 s (|D| 104,841); h = 2: pass 1 58.1 s (|D| 1,063,724), pass 2 40.9 s (|D| 2,054,763); peak resident memory of the validator 3.17 GB. **Projection (seconds = a + b·|D| per pass from the two probe points, applied to every production unit's tuple count from `INPUTS.json`; an extrapolation with margin, not a guarantee): 0.92 h** against the 10-hour budget (the reduction order of §10 applies before the lock only).

**(i) Eligibility and materiality from the key-free inputs (α = 0.01; the primary block).** Of the 1,600 primary (pair, setting) rows, 1,494 are T1-eligible (theory share ≥ 0.75, no flag) and 879 are T2-material (R_pred outside [2/3, 3/2]): predicted 'calibration helps' in 336 and 'calibration hurts' in 543. By block (rule | h | tokenizer | N_cal | pair class: T1-eligible / T2-material of the rows): h1 distinct llama N1000 diagonal: 10 / 0; h1 distinct llama N1000 english_other: 50 / 38; h1 distinct llama N1000 near_identical: 2 / 0; h1 distinct llama N1000 other_other: 20 / 19; h1 distinct llama N1000 within_english: 18 / 3; h1 distinct llama N5000 diagonal: 0 / 9; h1 distinct llama N5000 english_other: 50 / 27; h1 distinct llama N5000 near_identical: 0 / 2; h1 distinct llama N5000 other_other: 20 / 11; h1 distinct llama N5000 within_english: 18 / 0; h1 distinct qwen N1000 diagonal: 10 / 3; h1 distinct qwen N1000 english_other: 50 / 37; h1 distinct qwen N1000 near_identical: 2 / 2; h1 distinct qwen N1000 other_other: 20 / 11; h1 distinct qwen N1000 within_english: 18 / 5; h1 distinct qwen N5000 diagonal: 0 / 10; h1 distinct qwen N5000 english_other: 50 / 23; h1 distinct qwen N5000 near_identical: 0 / 2; h1 distinct qwen N5000 other_other: 20 / 7; h1 distinct qwen N5000 within_english: 18 / 0; h1 raw llama N1000 diagonal: 10 / 10; h1 raw llama N1000 english_other: 50 / 19; h1 raw llama N1000 near_identical: 2 / 2; h1 raw llama N1000 other_other: 20 / 7; h1 raw llama N1000 within_english: 18 / 14; h1 raw llama N5000 diagonal: 0 / 10; h1 raw llama N5000 english_other: 50 / 27; h1 raw llama N5000 near_identical: 0 / 2; h1 raw llama N5000 other_other: 20 / 11; h1 raw llama N5000 within_english: 18 / 14; h1 raw qwen N1000 diagonal: 10 / 10; h1 raw qwen N1000 english_other: 50 / 28; h1 raw qwen N1000 near_identical: 2 / 2; h1 raw qwen N1000 other_other: 20 / 16; h1 raw qwen N1000 within_english: 18 / 12; h1 raw qwen N5000 diagonal: 0 / 10; h1 raw qwen N5000 english_other: 50 / 32; h1 raw qwen N5000 near_identical: 0 / 2; h1 raw qwen N5000 other_other: 20 / 17; h1 raw qwen N5000 within_english: 18 / 12; h2 distinct llama N1000 diagonal: 10 / 9; h2 distinct llama N1000 english_other: 50 / 50; h2 distinct llama N1000 near_identical: 2 / 2; h2 distinct llama N1000 other_other: 20 / 20; h2 distinct llama N1000 within_english: 18 / 18; h2 distinct llama N5000 diagonal: 0 / 0; h2 distinct llama N5000 english_other: 49 / 31; h2 distinct llama N5000 near_identical: 0 / 0; h2 distinct llama N5000 other_other: 20 / 13; h2 distinct llama N5000 within_english: 15 / 9; h2 distinct qwen N1000 diagonal: 10 / 4; h2 distinct qwen N1000 english_other: 50 / 47; h2 distinct qwen N1000 near_identical: 2 / 0; h2 distinct qwen N1000 other_other: 20 / 20; h2 distinct qwen N1000 within_english: 18 / 14; h2 distinct qwen N5000 diagonal: 0 / 2; h2 distinct qwen N5000 english_other: 50 / 17; h2 distinct qwen N5000 near_identical: 0 / 1; h2 distinct qwen N5000 other_other: 20 / 7; h2 distinct qwen N5000 within_english: 17 / 6; h2 raw llama N1000 diagonal: 10 / 4; h2 raw llama N1000 english_other: 50 / 28; h2 raw llama N1000 near_identical: 2 / 1; h2 raw llama N1000 other_other: 20 / 9; h2 raw llama N1000 within_english: 18 / 10; h2 raw llama N5000 diagonal: 0 / 3; h2 raw llama N5000 english_other: 49 / 3; h2 raw llama N5000 near_identical: 0 / 0; h2 raw llama N5000 other_other: 20 / 0; h2 raw llama N5000 within_english: 15 / 2; h2 raw qwen N1000 diagonal: 10 / 4; h2 raw qwen N1000 english_other: 50 / 22; h2 raw qwen N1000 near_identical: 2 / 2; h2 raw qwen N1000 other_other: 20 / 1; h2 raw qwen N1000 within_english: 18 / 7; h2 raw qwen N5000 diagonal: 0 / 9; h2 raw qwen N5000 english_other: 50 / 21; h2 raw qwen N5000 near_identical: 0 / 2; h2 raw qwen N5000 other_other: 20 / 6; h2 raw qwen N5000 within_english: 17 / 9.
The evaluation sets' ρ̄ and σ² at L = 256 reproduce Study 2's pinned `INPUTS.json` values (KGW, γ = 0.25) in 108 comparisons with largest absolute differences 3e-14 and 3e-14. The two English Wikipedia cells' evaluation sets share 1068 ids (Study 2's samples; both calibration sets are disjoint from both).
Of the 28,800 conformal predictions (pair × N_cal × α), 687 have a negative point estimate of v (the most negative 9.1% of ρ̄_C + ρ̄_E), every one within its algebraic floor and set to 0 unflagged; 0 lie below the floor.

**Not computed before the lock:** any per-key level of a Study 3 key on real text, any study unit. The evaluation keys 23,000–23,999 and the fitting keys 24,000–24,999 appear nowhere in any output. all_ok = True.
<!-- S11:END -->

## 12. Nearest published work; what is not claimed
**Nearest published work.**
- **AutoMark** (Gloaguen, Staab, Vechev 2026, arXiv 2609.37310): soundness given a key (Eq. 3), the verification test (Algorithm 3), the multiplier 1/β (Proposition 1), and the smallest passing multiplier with its power cost (App. C). This study compares against their remedy and does not re-run their test (constraints 13–14).
- **Genhatharan 2026** (GitHub `nisaharan/when-nominal-false-positive-rates-fail`): per-key, per-length empirical calibration on 5,000 outputs, which brings held-out cells to 0.16–0.96%, priced at a few points of detection.
- **Aremu et al. 2026**: per-key thresholds "on held-out benign data".
- **Delbianco, Tohmé, Acciarri 2026**: per-cell conformal calibration, including key epoch, language, domain and length, with the frozen-calibration variability √(α(1−α)/n).
- **Vovk 2012**: training-conditional (tolerance) validity.
- **SAC-Copula** (Li & He 2026): threshold portability across corpora at nominal 1% and 5%.
- **Xie, Chen, Ren, Su 2025**: null-text conformal calibration.
- **Nemecek, Zafar, Ganguly, Singh, Chaudhary, Ayday 2026** (arXiv 2608.20047, v1 2026-08-20; found at this re-screen, missed by the earlier screens): an evaluation framework with "detection thresholds calibrated empirically per deployment context" (the abstract) over six schemes, three generators and eleven languages. Its §4.1 defines, beside the per-language threshold, a global threshold "calibrated from the pooled null" over the languages, "our headline" for cross-lingual deployment with a single detector, and its Tables 2 and 7 compare detection under that global threshold with per-language recalibration (the arXiv HTML, re-read by the conductor on 2026-10-15 after R07 round 1 corrected the re-screen's first reading; to be confirmed against the PDF at the claim gate). The study varies no key and reports no per-key level, so it does not characterise variation across keys. It is the nearest neighbour of the transfer question on the language axis: it occupies the failure of nominal thresholds across languages, per-language calibration, and the comparison of a pooled cross-language threshold with per-language thresholds; it does not run an ordered per-key transfer (a threshold set on one law applied to another, per key) or an across-key evaluation.
- **ChainMark** (Li-Chen and Kim 2026, arXiv 2607.18445): a one-corpus pooled null recalibration, and an unmeasured statement that key rotation leaves the null unchanged; a neighbour of the pooled arm and a practice statement under constraint 16.
- **Ding, Wei, Zhu, Dai 2026** (arXiv 2609.32678): rejection thresholds for e-processes from independent null samples, applied to Gumbel-max detection under the idealised null (each key would need its own reference bank, by their limitations); a key-agnostic methodological neighbour.
- The pre-lock re-screen is `research/study3/rescreen/RESCREEN_2026-10-13.md` (2026-10-13; the arXiv API, the arXiv search page, OpenAlex, GitHub and the vLLM documentation; no occupant of per-key calibration, of calibration transfer or of a comparison with the multiplier; AutoMark still v1; Genhatharan's repository unchanged since 2026-09-11; one Semantic Scholar lookup answered HTTP 429 and was recorded as a gap).

Wording constraints 1–16 of the gate apply to every sentence of the report. In addition, from this re-screen: no transfer sentence may present the failure of nominal thresholds across languages, per-language calibration, or the comparison of a pooled cross-language threshold with per-language thresholds as new (Nemecek et al. 2026); what remains is the transfer of a per-key calibration and its key-conditional realised level. And from R07: AutoMark's multiplier is their guarantee only for a detector sound over the key (Proposition 1's prerequisite); the report states that condition wherever the arm is interpreted, and never presents the empirical plug-in as their test.

**What this study adds:** per-key calibration's realised-level distribution measured within and across laws on a grid of cells, rules, widths, tokenizers and families, against a key-free predictor of the transfer from the exact cross-set covariance identity, and against AutoMark's multipliers and a pooled calibration on the same keys and texts.

**Not claimed:**
- priority on per-key calibration, on its pricing or on the multiplier (constraints 13–14), on per-language calibration, on the failure of nominal thresholds across languages or on the comparison of a pooled cross-language threshold with per-language thresholds (Nemecek et al. 2026), or on pooled null recalibration (ChainMark 2026);
- any theorem; T2 of the gate is tested in its location-family form, never proved;
- any transfer guarantee; the transferred levels are measurements with their own error (constraint 10);
- any power statement (Study 4);
- any statement about the held-out partition or a population extreme;
- that a hash is statistically independent;
- any real-world discrimination claim from a language disparity (constraint 10).

**Lock.** After R07's AGREE and Yichen's word, write `outputs/study3_v0.1/PRE_RUN_LOCK.json` with exactly this schema:

`{study: "study3_v0.1", date (ISO), approved_by: "Yichen", before_outcomes: true, final: false, grid: "research/study3/grid_v0.1.json", protocol: "research/STUDY3_PROTOCOL_v0.1.md", validation: "outputs/study3_v0.1/VALIDATION.json", inputs: "outputs/study3_v0.1/INPUTS.json", tokens_manifest: "outputs/study3_v0.1/tokens_manifest.json", hashes: {sha256 of exactly the pinned files: the protocol, the grid, VALIDATION.json, INPUTS.json, the Study 3 tokens manifest, Study 2's tokens manifest and RUN_MANIFEST.json, s3_core.py, s3_run.py, s3_analyze.py, s3_validate.py, s3_data.py, s3_keys.py, s3_inputs.py, research/study2/s2_core.py, s2_data.py, s2_keys.py, research/study1/s1_core.py, tools/key_policy.py, tools/corpora_access.py}, review: {checkpoint: "R07", resolution: "research/reviews/R07_study3-protocol/RESOLUTION.md", sha256}, keys: {eval_start: 23000, K: 1000, fit_start: 24000, K_fit: 1000}}`

The lock records that approval; the approval itself is Yichen's message. Set this file's status line to LOCKED before its digest is taken. Commit and push the lock **before** running:
1. `PYTHONHASHSEED=0 .venv/bin/python -u research/study3/s3_run.py --grid research/study3/grid_v0.1.json` (log `outputs/study3_v0.1/run.log`; the units under `outputs/study3_v0.1/cells/` are committed after the run as the record: every unit's JSON, every evaluation unit's counts file and every calibration unit's `__thresholds.npz` with the per-key and scheme-level thresholds, the input Study 4 takes; the calibration-bootstrap thresholds stay local under `thresholds_local/` with their digests in the units and the run manifest);
2. then `s3_analyze.py --grid research/study3/grid_v0.1.json --lock outputs/study3_v0.1/PRE_RUN_LOCK.json` → `outputs/study3_v0.1/results.json`.
