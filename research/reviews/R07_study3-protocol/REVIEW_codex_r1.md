# R07 — Study 3 protocol: independent review, round 1

Reviewer: Codex. Review date: 2026-10-13 local / 2026-10-14 UTC.

## 1. Baseline and scope

Baseline: **main, 0a479cf741229c262bf8aefc2d112805a1f4305d**. The worktree was clean at entry. This review concerns the draft before its lock; it does not reopen R06 or change Studies 1–2.

Read AGENTS.md and REVIEW_ORIENTATION.md in full, the R07 prompt, the entire Study 3 protocol and grid, all seven proposed pinned Study 3 modules, the calibration manifest, VALIDATION.json, and the structure and selected pairs of INPUTS.json. Also read the requested Study 2 protocol/report passages, gate items and constraints, D9–D11 and the Milestone 5 record, the re-screen and its recorded coverage, and AutoMark's local text at the requested sections. Additional source checks are identified below.

I independently reproduced the metadata-only split; checked all calibration and Study 2 cache digests; checked the imported core digests against their existing locks; scanned the production records' key ranges; recomputed the cost projection, all primary eligibility/materiality blocks, order indices and selected predictions; and ran the analyzer against the existing synthetic inventory in memory. Refusal counterexamples below use copies of JSON objects and patched reads in memory, leaving the records untouched. No real text was read, no Study 3 production key was scored, no production run or long validation was started, and nothing was downloaded. Only this memo was written.

**Recommendation: revise before locking.** The fresh-key design, threshold algorithms, covariance identity and compute feasibility are supported. Six major findings concern incomplete record gates, calibration/guarantee wording, an estimand mismatch in the exceedance comparison, and an inaccurate description of a nearest neighbour. Two minor findings concern the promised-output contract and sampling wording.

## 2. Claims against evidence

### Information timing and frozen inputs

The inspected record supports the claim that no Study 3 per-key outcome on real text exists. The Study 3 output directory has inputs, manifests, validation records/logs, token caches and synthetic validation directories, but no production cells. Searching INPUTS.json for level_counts, key_mean and sd_obs found none. Its grid, manifest, core and inputs-script digests match the current files. The git sequence records D9–D11, the code, inputs and validation before R07, including the two disclosed pre-outcome corrections.

Across all 1,248 Study 1 cell records, the recorded key start is 20,000, with K equal to 200, 500 or 2,000; across all 3,468 Study 2 records it is 22,000 with K = 1,000. Neither intersects 23,000–24,999. The existing synthetic Study 3 pilot records use evaluation keys starting at 1,000,000 and fitting keys at 1,500,000, K = 64 each. The validator's larger probes also use validation-range keys on synthetic tokens. The occurrences of 23,000 as Study 2's exclusive range endpoint and 24,000 as a character cap are not uses of Study 3 keys. This is confirmation from the inspected code, history and records, not a claim about unrecorded activity outside them.

The metadata-only plan reproduces the manifest's seeds, pool digests, evaluation/calibration id digests, scan endpoints, skipped counts and evaluation sizes. Every calibration set is disjoint from every evaluation set and all other calibration sets. The English Wikipedia skips are 578 and 952; its two evaluation sets overlap in 1,068 ids. Gutenberg has 7,122 evaluation books and 5,000 calibration books at permutation positions 7,122–12,121, including 2,878 of Study 2's former evaluation books. Those books have left Study 3's evaluation set. All inspected token-cache hashes match, and the manifest binds Study 2's manifest correctly. The imported Study 1 and Study 2 cores still match their locked hashes.

Fresh keys make the disclosed reuse sound for an evaluation conditional on these texts and this input-adaptive design. It is an independent replication over keys, not an independent corpus replication or an untouched choice of text laws. The existing disclosure says this appropriately. F8 corrects the stronger uniform-pool/fresh-text wording.

### Decisive primary-source checks

- **AutoMark**, local research/literature/txt/2609.37310.txt, PDF p.42, Proposition 1, requires a detector that **“satisfies Equation (2)”**. Equation (2), p.4, is pointwise soundness over the key. App. C, p.29, defines the empirical choice through **“both soundness tests (Algorithms 2 and 3)”**. Page 30 specifies fresh reference texts per key; Algorithm 3, p.36, supplies the screening tail. The multiplier's prerequisite and the difference from this study's plug-in fit matter: F4.
- **Vovk**, local research/literature/txt/1209.2673.txt, PDF p.2, states examples are **“generated independently from the same probability distribution P”**. Proposition 2b on p.6 gives the binomial-CDF training-conditional bound and its continuous-score exactness condition. Exchangeability alone is insufficient for the exact Beta/population-tolerance assertions as currently worded: F3.
- **Nemecek et al.**, the primary arXiv HTML, §4.1 and Tables 2/7, explicitly includes a global threshold calibrated on null generations pooled across languages, compared with language-specific thresholds. That contradicts the re-screen's statement about finding no pooled/shared/single thresholds. This HTML check has no PDF page claim; no PDF was downloaded. See F6 and the linked primary source there.

### Methods and predictor

All 12 registered (N_cal, alpha) pairs reproduce the stored indices. For N_cal = 500/1,000/2,000/5,000, respectively:

| alpha | Conformal j | Tolerance j |
|---|---|---|
| 0.01 | 5 / 10 / 20 / 50 | 2 / 5 / 13 / 39 |
| 0.05 | 25 / 50 / 100 / 250 | 17 / 39 / 84 / 225 |
| 0.001 | 0 / 1 / 2 / 5 | 0 / 0 / 0 / 2 |

The conformal and empirical/pooled floor indices use Fraction arithmetic. The tolerance index uses SciPy's numerical binomial CDF; it is maximal at each registered setting. Thus the blanket claim that all threshold-index arithmetic is rational should be narrowed, but there is no index error on this grid. At j = 0 the implemented threshold is zero and strict rejection never occurs. Searchsorted with side = left implements strict p < t and correctly excludes ties. The empirical fit's two order statistics and cap ensure at most floor(beta K_fit) fitting keys exceed alpha on C. The pooled order statistic gives the largest threshold meeting the pooled fitting-table constraint. Fitting keys are never evaluated on E. These are valid empirical definitions; they are not AutoMark's hypothesis tests.

For the model, let q(U) = sigma_C Phi^-1(U), U ~ Beta(N_cal + 1 - j, j), independently of X ~ N(0,v). Conditional on U,

- E_X[ell] = Phi_bar(q/s), with s² = sigma_E² + v;
- E_X[ell²] is the bivariate upper normal tail at (q/s,q/s), with correlation v/s².

Integrating gives m and m2. The population variance is m2 - m² and the finite-evaluation contribution is (m - m2)/N_E. The implementation's within-U plus between-U variance is the same identity. At v = 0 and equal residual scales, ell = 1 - U, giving the Beta reference law under the stated model. The 20,000-node midpoint rule is consistent with the saved exact-Beta and Monte Carlo fixtures; those fixtures check that model, not its truth on fixed real corpora. Recomputing three within-law, cross-language and cross-tokenizer examples from the rounded stored moments agreed with their saved mean/SD/theory-share/share predictions to maximum absolute differences of approximately 6.4e-9, 8.8e-10 and 4.5e-10.

For normalized tuple weights a_iu = n_iu/sqrt(M_i), independent unit-variance tuple scores give Cov_K(z_i,z_j) = sum_u a_iu a_ju. Averaging cross pairs yields the dot product of set-average weights. The Bernoulli normalization cancels gamma(1-gamma); standardized Exp(1) scores also have variance one. Therefore cross_cov is the same exact identity for both idealized families, including its dependence on shared integer tuple ids. Applying a Gaussian tail model to those second moments is a separate assumption, especially for Gamma-tail p-values and varying retained lengths; the draft discloses this distinction.

Writing A = ||w||², rho_bar = n/(n-1)(A - meanV/n), and sigma² = meanV - rho_bar gives A = rho_bar + sigma²/n. Hence v_raw + tau_v = ||w_C - w_E||². I checked this algebra and the stored moment relation over all 9,600 pair-prefix combinations; the largest discrepancy induced by nine-significant-digit storage was 1.46e-8. Recounting the prediction flags reproduces 28,800 conformal entries, 687 negative v_raw entries and none below the floor. The minimum relative value reproduces -0.090521069 to storage precision. This is an integrity bound, not evidence that clipping every admissible negative estimate gives an accurate transfer model. That adequacy remains an empirical question.

The model-implied empirical threshold follows from setting the upper beta fraction of Gaussian calibration shifts above the bad-key boundary; the pooled threshold follows from the marginal variance rho_C + sigma_C². They are population/model limits, omitting finite fitting-table uncertainty. That is acceptable as a declared predictor. F5 concerns the different population-versus-finite-E distinction in its reported shares.

## 3. Method, rules, precision and record

### Primary rules

I recomputed every eligibility/materiality block from INPUTS.json. All blocks equal VALIDATION.json: **1,600 candidates; 1,494 T1-eligible; 879 T2-material; 336 predicted helpful and 543 harmful**. The existing synthetic analyzer also completes in memory with 18 T1 rows, 18 T2 rows and 1,872 descriptive rows.

T1's interval classification is correct at its boundaries: an interval equal to the band is consistent; one touching a boundary from outside is unresolved. The rule needs 30 resolved rows and 80% consistency among resolved rows. The N_cal = 5,000 diagonal theory shares range from 0.5875 to 0.6715, all below 0.75; at 1,000 they range from 0.8658 to 0.9109. The Beta SD of about 0.14 pp and evaluation floor of about 0.10 pp explain the former exclusion. **Keep these rows descriptive; do not weaken eligibility merely to include them.** The report must make clear that T1's pass cannot establish adequacy for that excluded diagonal block. Q1 still has its measured distributions and descriptive model comparisons.

T2 correctly uses identical bootstrap key indices in numerator and denominator and treats intervals touching 1 as unresolved. A pre-stated sign rule is honest: it assesses direction, with magnitude assessed separately. The 2/3–3/2 material band is a reasonable heuristic margin against the observed baseline bias; a median bias of about a fifth is not a bound that this band is guaranteed to absorb for every cell. Counts by direction and class are essential because the pairs are strongly dependent. Neither the 80% nor 90% aggregate criterion is a formal multiplicity-adjusted confidence statement.

REP's 6 sqrt(se3² + se2²) + 1e-12 threshold uses independent key samples on the same fixed texts; excluding Gutenberg is correct. The Study 2 inventory digest verifies successfully. A failure can indicate an implementation/provenance problem or an inadequately estimated rare-key SE; the prescribed audit is appropriate, and a failed run must remain visible rather than being silently replaced. No need to alter this rule before the lock.

### Compute and precision

From the two cost probes, the independently reconstructed seconds models are:

- calibration: 22.01920009 + 3.532946508e-5 |D|;
- evaluation: 7.436450073 + 1.682118567e-5 |D|.

Summing both over all 60 (tokenizer, cell, width) pairs, including the specified lower bounds, gives **0.9390598333 hours**; every rounded per-pair cost equals the saved record. The budget is about 10.65 times that projection. The saved peak RSS is 2.92 GB. I did not rerun the cost probe. Two synthetic tuple-count points cannot guarantee runtime or peak memory on all real chains, and the production threshold cache holds multiple source cells simultaneously, but the margin is ample for this pre-lock decision. The reduction order is explicit and appropriately restricted to before the lock.

At K = 1,000, the Gaussian SD relative SE benchmark is 1/sqrt(2·999) = 2.237%. It supports resolving large T2 effects, with the stated caveat for skewed or near-Bernoulli levels. The 99th percentile has only about ten keys beyond it; the central 95% binomial rank range is roughly 983–996. It is a coarse sampled tail, not a precisely established population extreme. B = 200 gives only about five bootstrap draws per 2.5% tail; B = 50 makes the calibration-component SD itself noisy. These limitations are acceptable for descriptive outputs if carried into the report, without an implicit claim of uniform precision over all pairs.

The screening arithmetic is correct. At alpha = 0.01, N_E = 10,000 gives c = 125, r = 0.00847918105 and b = 0.0580552220; Gutenberg gives c = 92, r = 0.00984935391 and b = 0.0593568862. The shared-E count B is correctly described as descriptive. It is not AutoMark's independent-reference-text test, and the binomial screening benchmark itself is an idealization of this frozen finite-corpus design.

### Record sufficiency

The proposed committed uint16 count arrays suffice to recompute per-key summaries, T1/T2, paired key bootstraps, and descriptive break-even comparisons. Stored crossed-bootstrap intervals and calibration-bootstrap summary vectors suffice to reproduce the promised tables and the SD across the saved calibration resamples. The committed per-key and scheme threshold arrays, together with key ordering, tokenizer/version, rule, width, length and the strict p-value rule, are sufficient detector inputs for Study 4. Native Gamma thresholds on generated texts can be obtained through the same p-value evaluator at the generated text's retained length.

Counts alone cannot reconstruct text-by-key rejection matrices, repeat or extend the crossed bootstrap, recompute threshold fitting from calibration p-values, generate new calibration resamples, or independently verify the fitting-table maximality of the empirical/pooled thresholds. Local bootstrap thresholds also do not supply the missing evaluation p-values. These are limits of recomputation, not missing promised results. A clean committed checkout should still be able to analyze the saved record without those local bootstrap files. The current analyzer is designed to allow that, but its acceptance checks need F1–F2, and the contradictory storage wording needs F7.

Study 4 should pre-specify how it selects keys/settings from this record, retain the exact threshold-to-key mapping, and report abstentions and any null-law mismatch. This is a carry-forward recommendation, not an instruction to design or run Study 4 now.

## 4. Process and wording

D9–D11 are implemented in scope and sizes. The two recorded corrections occurred before Study 3 outcomes: replacing the ad hoc negative-v rule with its algebraic bound and fixing the validator's NumPy-bool comparison do not violate a locked protocol. The holdout remains sealed, final is false, and the inspected real-text access path uses the open-partition seal. No terms restriction was bypassed in this review.

The draft generally preserves gate constraints 10, 13 and 14: transfer is measured rather than guaranteed, AutoMark receives the multiplier/test attribution, and per-key calibration and its cost are acknowledged prior work. There is no power conclusion or population-maximum claim. The exceptions requiring correction are the unqualified calibration/multiplier guarantees and the nearest-neighbour characterization below. The screen, bootstrap sizes, seeds, material bands, interval slack, v-floor tolerance and REP threshold agree with the registered code. The extra 1e-300 numerical guard has no material effect here. The numerical-CDF versus rational-floor wording is noted in F7.

The re-screen records substantial coverage: 17 arXiv API queries, 12 search-page queries, OpenAlex queries, GitHub repository checks and deployed-system documentation. It records the Semantic Scholar HTTP 429 as an access gap. GitHub repository search is not an exhaustive code search; capped search-result pages and keyword counts are not evidence of absence. The incorrect section-level characterization in F6 shows why a retrieved neighbour must be checked directly.

## 5. Independent search

Web access was available. I made a bounded arXiv-domain search for per-key watermark calibration, language/threshold transfer and AutoMark's multiplier, including after:2026-10-10 and explicit October 11–12 queries. These searches returned no additional relevant post-October-10 item; several results were irrelevant, so this is a weak negative search, not a novelty claim. AutoMark's [current abstract/version page](https://arxiv.org/abs/2609.37310) still lists only v1 of September 29. Direct inspection of the already-listed Nemecek paper found F6. I did not repeat every OpenAlex, GitHub or deployed-documentation query, and did not bypass or retry the logged Semantic Scholar restriction.

## 6. Findings

### F1 — Major: the analyzer does not enforce its promised provenance and threshold inventory

**Evidence.** In s3_analyze.py:57–87, load_inventory checks study, mode, unit and (in study mode) lock_sha256, but not the expected grid/code/manifest/token digests, key ranges, K/K_fit or N. Every one of those provenance fields can be changed while the existing synthetic inventory is accepted. More seriously, both threshold-verification loops iterate over the record's own threshold_digests dictionary. Removing one source or replacing the dictionary with an empty one is accepted. With empty maps, even the study-mode threshold-file check is skipped; I exercised that branch in memory with nonexistent threshold-file paths. Removing a calibration record's summary/info is also accepted by the inventory gate, although analysis later fails when it needs those fields.

**Implication.** A matching lock label and self-consistent count digest are insufficient to establish that the units belong to the registered execution or that the complete frozen threshold record exists. This contradicts §9 and is particularly consequential for Study 4.

**Recommendation.** Derive expected provenance and the exact source set from the verified lock/grid/manifests and unit slot; reject missing, extra or foreign fields that identify the execution. Require every registered threshold reference, agreement between its top-level and provenance copies, and every committed calibration threshold file independently of those references. Validate calibration threshold keys, shapes, finite [0,1] values, alpha nesting and abstention conventions, plus the calibration summary's required structure. Add refusal fixtures for absent/partial maps, missing committed thresholds and each foreign provenance dimension. Do not require the local bootstrap arrays merely to analyze the committed record.

### F2 — Major: the body contract accepts wrong denominators, axis identities and nonfinite bootstrap values

**Evidence.** s3_analyze.py:98–147 accepts any positive integer N_E; after changing a pilot's N_E from 2,000 to 4,000 and recomputing its screen constants, the unchanged counts pass. Reversing its alphas, variants_same and cal_sources metadata also passes. A fabricated cross-tokenizer source with a correspondingly shaped count array passes. Calibration-bootstrap vectors are checked only for length: replacing an SD with NaN or -1 passes. A NaN screen r passes because its comparison with the tolerance evaluates false; a wrong screen b is ignored. The current 15 refusal mutations do not cover these cases.

**Implication.** The analyzer can halve every level through a wrong denominator, misidentify source/variant axes, or accept unusable uncertainty results, despite the stated complete body contract. Hashing an array does not establish these meanings.

**Recommendation.** Bind N_E to the expected unit/manifest, including Gutenberg and validation exceptions. Require exact axis labels and ordering, exact other-tokenizer identities, and the expected array-key set. Check every calibration-bootstrap element for numeric type, finiteness and its admissible range; validate all screening constants with an explicit finite check. Extend the mutation suite while retaining a successful complete-record case. This is separate from F1's provenance gate.

### F3 — Major: distinguish the i.i.d. calibration law from exchangeability and the frozen-across-key target

**Evidence.** Protocol §3, line 91, and s3_core.py:17 assert an exact Beta law for exchangeable continuous scores; lines 94 and 117 then use the tolerance/within-law conclusions without the needed sampling qualification. For a fixed key with i.i.d. continuous calibration scores, F_k(p_(j)) is Beta(j,n+1-j). General exchangeability does not imply this distribution. Sampling without replacement from a fixed finite score population instead gives a discrete order-rank law. Moreover, a probability over repeated calibration draws for each fixed key is not a guarantee that at most delta of the keys fail for this one shared, frozen C.

**Implication.** The current wording promotes a model/reference law into a guarantee for a different random experiment. The calibrated predictor can remain a useful, explicitly assumed model; this finding does not invalidate its derivation or the fresh-key measurement design.

**Recommendation.** State separately: rank-based marginal conformal validity under the relevant exchangeability condition; exact Beta and binomial tolerance statements under i.i.d. calibration sampling from the same fixed-key law; and the assumed across-key residual model used for the frozen-text prediction. State strict-tie conservatism under those conditions. Label the tolerance-versus-delta comparison a reference diagnostic, not a PAC-over-keys guarantee conditional on the realized C. Explain the finite-pool sampling and shared-C qualifications in Q1, §3, §7 and the core/validation descriptions. No new independent calibration corpus is required to fix this claim.

### F4 — Major: qualify where AutoMark's “guaranteed” multiplier is actually guaranteed

**Evidence.** Protocol §§1, 3 and 5 name t = alpha beta as guaranteed without stating Proposition 1's soundness-over-the-key prerequisite. Raw repeated-tuple scores violate it: for h = 0 and a 256-token repetition of one token, KGW's green case has z = 27.7128 and p approximately 2.45e-169. At alpha = 0.01 and beta = 0.05, a point-mass null on that text has per-key level 1 for 25% of ideal independent-colour keys after the multiplier, exceeding beta. Gumbel's raw sum likewise repeats the same exponential score rather than summing independent exponentials. Even the distinct KGW z-test is an approximation: at M = 256 its exact binomial rejection probability at p < 0.0005 is 0.0008123563, not at most 0.0005.

**Implication.** Failure of this arm in such settings cannot be presented as failure of AutoMark's proposition. Calling the raw Gamma tail exact also needs the distinct-score condition. The empirical arm does not test either of AutoMark's two soundness hypotheses; its calibration fraction constraint is a different, reasonable comparator.

**Recommendation.** Keep the numerical arm but label it AutoMark's 20-fold multiplier, with its guarantee conditional on valid marginal p-values. State the applicable idealized guarantee for distinct Gumbel scores, the asymptotic status of the KGW z-test, the raw-rule limitation, and the hash assumption. Explicitly state that the empirical plug-in uses neither Algorithm 2 nor Algorithm 3 and has no inherited test-level guarantee. Carry these distinctions into every remedy/PAC interpretation, as gate constraint 8 requires.

### F5 — Major: predicted exceedance shares and measured exceedance shares have different estimands

**Evidence.** s3_core.py:164–217 computes P(ell > alpha) for the latent population level, while level_summary and the analyzer compute P(count/N_E > alpha). The SD prediction includes finite-E noise; the share prediction does not. Protocol §7 places these shares in the same comparison and calls the tolerance share against delta a PAC check. In the model's own exact within-law tolerance example, N_cal = 5,000, alpha = 0.01 and j = 39 give P(ell > alpha) = **0.0465657388**, while an independent evaluation set of 10,000 gives P(count > 100) = **0.0767302441** under the Beta-binomial law. Thus an observed share above 5% can occur even when this population tolerance benchmark is satisfied.

**Implication.** The proposed descriptive comparison can falsely look like a prediction or tolerance failure. This is additional to F3's change in the source of randomness. It does not mean that AutoMark's pointwise-valid fixed-threshold bound cannot be applied to an empirical text law; that requires the separate prerequisite in F4.

**Recommendation.** Store and label population and finite-evaluation exceedance shares separately. For the latter use E[BinomialSF(floor(alpha N_E); N_E, ell)] under the same working model, with the analogous 2alpha/5alpha quantities if compared; validate the v = 0 equal-scale case against Beta-binomial arithmetic. Alternatively, explicitly stop treating the latent share as the prediction of the measured share. Keep the screen descriptive and state which benchmark it addresses. Fix the frozen predictor/output contract before outcomes exist.

### F6 — Major: correct the nearest-neighbour read and avoid inferring key marginalization from silence

**Evidence.** RESCREEN_2026-10-13.md §1 says searches for pooled/shared/single thresholds in Nemecek et al. found nothing; the protocol and decision log characterize it as per-language calibration marginal over keys. Yet §4.1 explicitly defines a global threshold from null samples pooled across languages, and Tables 2/7 compare it with language-specific thresholds. [Primary arXiv HTML, §4.1 and Tables 2/7](https://arxiv.org/html/2608.20047v1).

**Inference.** This is a closer pooled-to-language calibration comparison than recorded. It still does not establish the proposed ordered per-key transfer experiment or an across-key evaluation. Absence of a key sweep does not establish marginalization over keys.

**Recommendation.** Correct the re-screen, protocol and log with the pooled-global comparison; replace the unsupported marginal-over-key label with the limited statement that the inspected evaluation does not characterize variation across keys. Reassess the comparison on that basis. This correction does not, by itself, require abandoning Study 3.

### F7 — Minor: make the promised-output and storage descriptions match the actual record

**Evidence.** Section 6 promises v, rho_C, rho_E, rho_CE and both residual variances on inconsistent/unresolved T1 rows, while §7 attributes every diagnostic to t1_rows/t2_rows. Those fields are absent from those rows; they are recoverable only by joining INPUTS.json. Per-row N_E/K also need joining. The pass-1 summary stores absolute z(t), not the stated cost z(t)-z_alpha; zq excludes zero thresholds and returns None for full abstention. The final lock/run paragraph says threshold files stay local, contrary to the implemented committed __thresholds.npz record and the decision log. Finally, only the floor indices use exact rational arithmetic; j_tolerance uses a numerical CDF.

**Recommendation.** Either emit the promised diagnostics and cost fields, or name the report-builder joins/transformations explicitly in the contract. State the positive-threshold denominator and the abstention count for z summaries. Correct the storage paragraph to distinguish committed detector thresholds from local bootstrap thresholds and narrow the arithmetic wording. The underlying saved counts, inputs and threshold arrays contain the required information; this is a contract/documentation repair.

### F8 — Minor: qualify “fresh” and “uniform from the cell's pool”

**Evidence.** Protocol §§2/4 and s3_data.py say each calibration prefix is uniform from the cell's pool and follows the cell's own law. The sampler excludes all evaluation ids and previously taken calibration ids. In particular, wikipedia/en@256 excludes evaluation ids from the nested en@1024 pool, giving length-dependent exclusion relative to its original full pool. Gutenberg's 5,000 texts include 2,878 used by Study 2, despite the repeated blanket description as fresh.

**Recommendation.** Describe a uniform permutation scan conditional on the remaining admissible ids, document the nested-pool exclusion, and say disjoint from Study 3's evaluation sets, with Gutenberg's Study 2 reuse explicit. Treat same-law and near-identical-law labels as corpus/design approximations rather than exact distributional equalities. The verified disjointness and fresh-key design remain sound.

VERDICT: REVISE
