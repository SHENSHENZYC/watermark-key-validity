# R03 — Study 1 protocol before lock — independent review, round 2

Date: 2026-10-09 (America/Chicago; 2026-10-10 UTC). Reviewer: Codex.

Recommendation: revise before locking. The revision resolves several substantive round-1 errors, and the conditional-on-texts target is now coherent. The remaining blocking issue is experiment identity: the lock and analyzer still accept inputs that do not establish the promised R03-approved experiment. Additional corrections are needed to the predictor's stated assumptions, its zero-variance boundary, and the calibration and boundary handling of the simulator checks. No production result is needed to resolve these points.

## 1. Baseline and scope read

Baseline: `cb056a847d682513d06e1b558affcc4c869c3a80` on `main`. The working tree was clean before this memo.

Read the review orientation in full and the R03 prompt's Round 2 section; `RESPONSE_claude_r1.md`, including its verification table, dispositions and implementation addendum; `research/STUDY1_PROTOCOL_v0.2.md`, starting with the changes paragraph; all four Study 1 Python files; `research/study1/grid_v0.2.json`; `tools/key_policy.py`; `outputs/study1_v0.2/VALIDATION.json`; the revised competitor rows, comparison, residual gap and verdict in `research/KEYCOND_GATE_v0.3.md`; and `research/corpora/CORPORA_AUDIT_v0.3.md` §5 item 6. Also checked the round-1 review, relevant handoff and brief passages, the decision-log tail, and decisive passages in the two newly available local literature texts.

Checks were short, read-only Python computations, source inspection and in-memory fixtures. Imports used `python -B`; mock locks and mock inventories were not written to disk. I did not run the validator, the study grid, a model, or any corpus analysis. I did not download files, inspect the sealed holdout, commit, or change anything except this memo. Existing validation results are identified as the conductor's results; independently recomputed quantities are identified below.

## 2. Claims against evidence

### Round-1 disposition audit

| Finding | Round-2 assessment |
|---|---|
| F1: missed occupants | Substantially addressed. AutoMark and Genhatharan now receive the relevant claims; D5 records Yichen's decision to continue with narrower claims. A contradictory candidate paragraph remains (F16). |
| F2: different green probabilities | Resolved. Both samplers use `floor(gamma*V)/V`; the detector remains centered at gamma. Degenerate green-set sizes are marked. |
| F3: biased population correction | The point-estimator defect is resolved. `s_K² − MS_E/N` uses the two-way residual, and the population quantity is secondary. Bootstrap uncertainty is approximate, not an exact finite-sample guarantee. |
| F4: target/predictor mismatch | The original mismatch is resolved: the observed primary SD is conditional on fixed texts and uncorrected, and predictor inputs come from the identities. The replacement mixture introduces additional assumptions and a boundary implementation defect (F12–F13). |
| F5: missing diagnostics and inappropriate curves | Largely resolved. The weights account for variable M; per-key score variance, coverage, M, between-text quantities, bootstrap tolerances, burn-in and the support control are present. The mixture's extra dependence assumptions still need to be distinguished from these moment identities (F12). |
| F6: R2/R3 uncertainty and extremes | Partly resolved. The conditional SE and each colouring's own identity are now used. Calibration does not cover important declared regimes; exact-zero variance still fails numerically (F14–F15). |
| F7: lock, resume and incomplete analysis | Still open, blocking. Filename completeness and several refusal cases are fixed, but canonical lock identity, current-run provenance and per-cell semantic identity are not enforced (F11). |
| F8: retained pilot and key reuse | Addressed for prospective work. The old pilot is retained and disclosed, production uses 20,000–21,999, validation uses 1,000,000+, and the new reserved range is 30,000–30,999. This does not erase the old exposure. |
| F9: unsupported runtime projection | Addressed. There is a measured cost model, fresh timestamped validation directory, and a computed projection; see below for its limits. |
| F10: text/code and boundary inconsistencies | The K declarations, fixed-subset role, packing default, M=0 convention and traversal caveat are addressed. Remaining wording and boundary issues are specified separately below. |

### Identities, estimator and implementation checks

The exact colouring identities remain correct for arbitrary weights: independent variance is `g(1−g) Σw²`; fixed-size variance is `g(1−g)(V Σw² − Σ_c w_c²)/(V−1)`. Exhaustive enumeration of fixed green subsets with weights proportional to `(1,…,V)` gave:

| V, gamma | Enumerated fixed variance | Implemented identity |
|---|---:|---:|
| 4, 0.5 | 0.016666666666666663 | 0.016666666666666680 |
| 10, 0.25 | 0.0048484848484848485 | 0.004848484848484845 |

These are independent checks, not study cells. Direct and packed colourings also agreed for both models on a tiny V=10 chain with 60 validation keys and chunk size 48. The corrected two-way estimator returned exactly zero on a rejection table varying across texts but constant across keys, as it should. Its decomposition and the weighted binary-table bootstrap arithmetic check out algebraically.

For fixed eligible texts, write `V_i = Var_K(z_i)`, `C_ij = Cov_K(z_i,z_j)`, and `Vbar = Var_K(N⁻¹Σz_i)`. Then

`rho_bar = N/(N−1) [Vbar − mean(V_i)/N] = Σ_{i≠j} C_ij/[N(N−1)]`.

That equality is exact. Its expectation over i.i.d. text samples is the population across-key mean-shift variance. The corresponding calculation for `A_between` is also sound. Thus the finite-text contribution to the realized mean-score identity is removed as intended. This verifies a second-moment statement; it does not establish the joint score model needed to predict threshold indicators (F12).

The conditional primary target and its key bootstrap now refer to the same source of randomness. Under the explicitly assumed common-factor Gaussian model, the mixture formula plus `E[a(1−a)]/N` is also correct. The reason to replace the linearization is credible: a nonlinear tail probability need not retain its local derivative approximation at large shifts. The implementation and the conditions for using that model nevertheless need F12–F13.

### Published evidence re-checked

Substring searches in the local form-feed-separated texts confirm:

- `research/literature/txt/2609.37310.txt`, PDF p.4: “soundness given a key” is introduced as a “novel second requirement.” The surrounding passage and Eq. 3 support the PAC-over-keys characterization. PDF p.42 explicitly proves the `1/beta` multiplier construction; p.29 reports failures of the uncorrected soundness-given-a-key test. This supports the revised gate's allocation of those contributions to AutoMark.
- `research/literature/txt/genhatharan_nominal_fpr_2026.txt`, PDF p.1: “from 0.27% to 48.4% [47.4, 49.3] at 512 tokens.” The adjacent discussion attributes the shift to each key's null green rate. PDF p.7 contains “88 of 128 keys (69%)”; p.8 acknowledges prior per-key empirical thresholds. These support treating measurement, the mean-shift mechanism and calibration as occupied, with their stated scope.

I verified these passages, not the independent reproducibility of either paper's experiments. D5 is recorded at `research/DECISION_LOG.md:214`; the review does not reopen Yichen's positioning decision.

### Validation and projection

The validation record's grid digest matches the current grid. It records 549.8 seconds for the validation run, 210 cells, 54 degenerate markers, and 5.67 GB peak resident memory for the validator process. Its timing and statistics are retained pilot evidence, not production outcomes.

I independently summed the 42 projected chain times: **5,461.3 seconds = 1.51703 hours**, agreeing with the reported 1.52 hours. Their 1,194 live cells plus 54 markers give the expected 1,248 files. The model uses measured colouring rates and a fitted cell-cost model, with chain sizes built on validation seeds and both gamma multiplicities included. This is an auditable extrapolation with substantial margin against six hours. It is not a six-hour guarantee: the largest fixed sorts and other law families are extrapolated from the validation family. A full pre-lock run is unnecessary to resolve F9.

## 3. Method and statistics

The question is now precise enough for an adequacy study: dispersion across keys of the empirical rejection fraction on specified, fixed synthetic texts. It must remain distinct from the population dispersion over newly sampled texts. The separate two-way diagnostic preserves that distinction.

R1 now has explicit consistent/inconsistent/unresolved states, a minimum resolved count and a theory-share condition. The latter meaningfully prevents the finite-text term alone from satisfying the adequacy band. Passing applies to the resolved eligible subset; a paper must also show all eligible and unresolved counts. The one validation cell with a ratio near one does not establish general model correctness, and is not “exact up to normality” merely because colouring is independent and tuples are deduplicated.

The stated 3.2% relative SD error at K=500 is a normal-distribution benchmark. It is not a general precision calculation for bounded, highly skewed per-key levels. For example, the fully covered support-control regime in F14 has Bernoulli per-key levels with p≈0.00767, for which the asymptotic relative SD error is about 25% at K=500. The empirical bootstrap appropriately reflects some such uncertainty, but a zero-event sample cannot recover unseen rare keys by resampling itself.

R2's fixed-text reference and conditional SE are conceptually correct; the problem is the normal decision calibration, particularly its zero-SE behavior. R3's per-colouring variance comparison is also the right object, but a nominal 95% interval does not justify requiring at least 95% empirical coverage as a low-false-alarm experiment-level rule. R4 and R5 now concern the intended between-text quantities rather than observed rejection SD, and their shared texts and conservative sum-of-SE tolerances are reasonable descriptive hypothesis checks. These tolerances do not furnish a simultaneous confidence guarantee. R4b has the required support-specific analytic limit. Structural-zero rejections, zero colour variance, and zero within-key score variance are three different boundaries; the code must not conflate them.

For the noninteger-gamma illustrations with varying M, one small algebraic qualification also remains. If `mu_i = E_K z_i`, the exact key-averaged sample variance across the fixed texts, using the code's `ddof=1`, is

`mean(V_i) − rho_bar + N/(N−1) mean[(mu_i−mu_bar)²]`.

The implemented `sigma_model2` uses coefficient 1 on the last term. This distinction disappears in primary R1 cells because g=gamma, and is O(1/N) elsewhere. It should be corrected or explicitly given a different estimand when §3 calls it exact.

## 4. Process, timing and disclosure

The handoff, protocol and log consistently keep Study 1 in DRAFT pending R03 and Yichen's subsequent lock/run instruction. At review time neither `outputs/study1_v0.2/PRE_RUN_LOCK.json` nor the production `cells/` directory exists. No production outcome was generated by this review.

The key-range correction is explicit and the runner calls the namespace guard. Keeping the old synthetic pilot and retiring its exposed keys is the right prospective correction. The audit phrase “no outcome” should mean no confirmatory or real-corpus outcome; the toy check did produce synthetic statistics. The substantive holdout finding from R02 is unchanged.

The new validation explicitly uses outcome statistics to assess an approximation and calibrate audit rules. It is a disclosed pilot. Headings saying “no outcomes” should not obscure that fact; the relevant protection is separation from production keys/text seeds and a frozen final protocol. The review found no evidence of a production run disguised as validation.

The lock defects below are integrity checks for accidental stale inputs, copied cells and wrong checkpoint references. They are not a demand for cryptographic proof that a string saying “Yichen” represents human approval. Human approval remains a separate process requirement.

Only public searches and ordinary browser reads were used. No blocked GitHub endpoint was retried or bypassed; the Genhatharan paper was already present locally. No raw data, weights or literature files were added.

## 5. Independent search for occupants or newer work

Repeated bounded web searches for `watermark "key-conditional" "false positive"`, `watermark "per-key" "dispersion"`, and `watermark "fixed key" "false positive" October 2026`; then arXiv- and GitHub-restricted variants and a targeted official vLLM documentation query. Results were noisy and cannot establish absence or priority. No additional direct across-key dispersion study was verified in this search.

Two adjacent results deserve a bounded note:

- Official [vLLM v0.31.0 watermarking documentation](https://docs.vllm.ai/en/v0.31.0/features/watermarking/) explicitly says the realized false-positive rate can be “key-dependent even when contexts are deduplicated within each document” and recommends measurement with the deployed key. This further occupies the practical statement of the limitation; it is not a dispersion theory or a new measurement study.
- [Watermark Forensics for Generative Models, arXiv 2607.13003v1](https://arxiv.org/html/2607.13003v1), Definition 3.5, Theorem 3.6 and Appendix C.6, studies attribution among enrolled keys. Its witness decoder knows the source law and realized key set and uses a surprisal threshold for a pointwise per-innocent bound. Inference from those inspected sections: it is relevant adjacent fixed-key guarantee work, but does not establish the KGW collision/retention/width dispersion account proposed here. I did not audit the whole paper or infer that it was published after the previous screen from its search crawl date.

The two direct occupants found in round 1 remain the decisive positioning evidence. The revised claim-by-claim comparison is useful; the old candidate wording is not (F16).

## 6. Findings and recommendations

### F11 — **blocking** — The lock and inventory still do not establish the approved experiment (F7 remains open)

**Evidence.** `s1_run.py:95` takes the required protocol and validation paths from the lock itself, rather than requiring the declared canonical paths. It checks presence, but not the value, of `review.checkpoint`. A short in-memory fixture was accepted with both `protocol` and `validation` set to the grid JSON, hashes only for the grid and required code, and `review` pointing to the existing **R02** resolution with its correct digest. The real R03 protocol and validation were absent from its hash set. The same fixture accepted `date: "not-an-ISO-date"`.

`s1_analyze.py:21` requires filename completeness and uniform provenance, but does not validate that provenance against a current, verified lock, grid or code. A complete in-memory 1,248-file inventory was accepted by `load_inventory` with `study: "wrong-study"`, `lock_sha256: "not-a-digest"`, stale code/grid strings, validation-range `key_start: 1000000`, and wrong law/h/L/gamma/rule metadata; only K and N were matched. I tested this loader, not a completed scientific analysis of those mock cells. The downstream chain checks do not authenticate the lock or code either. `cell_reusable` similarly accepted a cell with wrong h/L/rule whenever its generic provenance matched. Cells in the same law with equal K share that generic provenance, so copying within a run is a realistic unguarded case.

The validator's “complete consistent” fixture itself substitutes temporary protocol, validation and resolution files (`s1_validate.py:142` onward). It proves the current permissive schema is internally consistent, not that the canonical experiment is locked.

**Recommendation.** Require the canonical study/protocol/validation/checkpoint/resolution identities declared by this version; validate the date and digest types. Before analysis, verify the supplied lock and match each cell to that lock, the grid, code and deterministic seed/key record. Compare cell metadata and marker status to its expected slot, and require the expected alpha/statistic fields. Apply the same slot check to resume. Add refusals for the concrete accepted fixtures above, including a complete uniformly stale inventory and a same-provenance wrong-cell copy. Retain the successful missing/extra-file and changed-hash checks.

### F12 — major — The replacement predictor needs its additional joint-model assumptions stated (F4–F5)

**Evidence.** Protocol §3 calls the predictor “from the identities alone,” and §11 calls the selected validation setting “exact up to normality.” The identities determine means and covariances; they do not imply common conditional means, a common residual variance, or conditional independence of the fixed texts' scores. A text sample being i.i.d. before conditioning does not make the score coordinates exchangeable over keys after those texts are fixed. With variable M and overlap, individual means, variances and pairwise covariances can differ.

An exactly Gaussian counterexample separates this issue from nonnormal tails. Take 4,000 fixed score coordinates in two equal groups: every coordinate in group 1 is the same standard normal A, every coordinate in group 2 is an independent standard normal B. The diagonal variance is 1 and average off-diagonal covariance is `1999/3999`. At alpha=0.01 the exact SD of the empirical rejection fraction is `sqrt(0.01*0.99/2) = 0.07035624`. Using those exact moments, the implemented homogeneous mixture predicts **0.03457569**, a ratio of **2.03485**, despite exact Gaussianity and theory share **0.99818**. This is an analytic model counterexample, not a claimed outcome for the grid's laws.

**Recommendation.** Retain the mixture if desired, but name it as a moment-matched common-factor approximation and state the additional homogeneity/dependence assumptions. Explain that the threshold-indicator covariance depends nonlinearly on each pair's covariance; averaging score covariances first is another approximation. Remove “exact up to normality.” Add a small heterogeneous-overlap validation case or a diagnostic that makes this failure mode interpretable. Correct the small finite-N sigma identity qualification in §3 above. This does not require the predictor to succeed everywhere or a theorem before the adequacy study.

### F13 — major — Zero within-key variance is silently replaced by unit variance; quadrature misses the sharp limit

**Evidence.** At `s1_core.py:370`, every nonpositive or nonfinite `sigma_model2` becomes **1.0**. Zero is legitimate when each text retains the same support under the distinct rule. Four identical retained sets with 4, 10 or 50 tuples gave `sigma_model2 = 0.0` and `pred_first_order.sigma2 = 1.0`; a 100-tuple case gave roundoff `−4.44e−16` and the same replacement. This changes the registered identity-based predictor into the separately labeled unit-sigma diagnostic, without flagging that change.

The 200-node quadrature also needs a boundary branch. Directly calling `mixture_predictor(0, 1, 0.01, 4000, 0)` gives mean **0.01302273** and SD **0.11337167**. The Gaussian model's exact sigma=0 limit is a Bernoulli indicator with mean **0.01**, SD **0.09949874**, and zero finite-text term. The SD discrepancy is **13.94%**, entirely numerical. The same discrepancy occurs with sigma²=1e−12, so merely replacing zero by an epsilon does not solve it. The three recorded quadrature validations all use substantially positive residual variance.

**Recommendation.** Implement the actual zero-variance limit and a scale-aware treatment of roundoff. Flag materially negative/nonfinite inputs rather than substitute another model. Use an accurate bivariate-normal moment calculation or adaptive integration/convergence check near the sharp limit. Validate zero, near-zero and ordinary residual variances. These controls are already part of the declared illustrations, even though they are excluded from primary R1.

### F14 — major — The R2 calibration misses a declared rare-key regime (F6 remains open)

**Evidence.** The recorded calibration is one Zipf validation setting, with subsamples of 500 keys. It does not cover the support control after coverage. For h=0, distinct scoring, support size 50 and gamma=0.5, every fully covered text has exactly the same rejection indicator for a given key. At alpha=0.01,

`p = P[Binomial(50, 0.5) >= 34] = 0.007673338916315053`.

With the registered K=500, the probability of observing no rejecting key is `(1−p)^500 = 0.02124857961`. On that event the implemented SE is zero, the exact reference is positive, and `s1_analyze.py:124` assigns infinite deviation: a “gross” failure forcing an audit. This is **2.125% under a correct simulator**, not a remote five-normal-SE event. The support-control setting is relevant at L=1024: a union bound over 4,000 texts and 50 tokens bounds the probability that any text lacks any support token by only **0.00020727**. The exact binomial calculation uses no production key or text seed.

For the same covered support at gamma=0.25, exact enumeration of the Binomial(K,p) sampling distribution gives a **0.7291%** chance of exceeding five estimated SEs. These checks also share keys with other cells, so their experiment-level failure probability cannot be obtained by treating cells as independent. Calling failure an audit flag is correct, but it does not calibrate the stop rule or specify how sampling noise is resolved without changing a locked rule after outcomes.

**Recommendation.** Before lock, specify the intended false-audit tolerance and calibrate the complete decision, including rare-key/saturated regimes and shared-key dependence. Exact binomial checks are available for the fully covered controls; conservative bounded-mean checks or an explicitly predeclared inconclusive/escalation procedure are alternatives elsewhere. Preserve genuine implementation failures and retain the failed run record. Do not interpret a nonparametric bootstrap of all-zero levels as resolving this issue, and do not wait for production results to choose the repair.

### F15 — major — R3 needs exact-zero handling and an experiment-level coverage calibration (F6)

**Evidence.** For a fixed-size colouring and a fully covered V-token vocabulary, q is exactly g for every key. This has zero variance even when `0 < m < V`, so the green-set degeneracy filter does not handle it. A four-text, full-coverage V=10 fixture at gamma=0.5 produced observed variance and bootstrap interval **0, [0,0]**, but `identity_for_weights` returned **1.85037e−17**; the literal containment check at `s1_analyze.py:138` failed. At V=50 and 100, cancellation produced small negative identities and the same false failure. V=10 full coverage is a declared illustration boundary.

Separately, §9 requires nominal 95% bootstrap intervals to cover the exact value in at least 95% of checks. Even if each interval had exactly 95% coverage and the checks were independent, this threshold lies near the mean coverage count and has an order-one probability of failing for many checks. Dependence and only 200 bootstrap resamples change that distribution; they do not supply a calibration. The current validation exercises execution/counts, not that experiment-level error rate.

**Recommendation.** Recognize structural zero variance analytically or use a documented scale-aware numerical tolerance, with a separate check that observed variation is also negligible. Then calibrate the overall R3 acceptance rule with the intended false-audit rate and dependence, or present coverage as a diagnostic rather than a simulator-validity verdict. Add the full-coverage fixed-colouring fixture. Do not conflate the mathematical exactness of the identity with the finite-sample coverage of its estimated variance interval.

### F16 — minor — Synchronize the remaining claims and validation record

**Evidence.** The gate's Candidate paragraph still says the rate “has been measured once in an appendix” and there is “no remedy with a stated per-key guarantee and a measured cost.” Both conflict with its new AutoMark/Genhatharan rows and verdict. The response addendum's R2 chance-failure rates differ from the final JSON, and its closing claim that every 20,000-key comparison lies within 0.3 SE is false for that record: the largest absolute deviation is **1.16283 SE**. Protocol §11's blanket “four decimals” agreement is also too strong: one mixture population SD is 0.03938639 versus Monte Carlo 0.03912583. These are modest numerical differences, not evidence against the simulator.

The validation analyzer writes `results_pilot.json` inside the same directory whose JSON inventory must contain only cells/cost records (`s1_validate.py:201`); a second identical analysis therefore sees its own prior result as an unexpected file.

**Recommendation.** Update the candidate summary and reference the final validation values rather than older calibration runs. Describe the quoted SD precision as a normal-theory benchmark and the validation as a retained pilot. Put analysis results outside the cell inventory, or use an explicit validated cell manifest. Qualify “third in line” as a limited historical characterization rather than an exhaustive priority count. These are cleanup items, not another request to revisit D5.

VERDICT: REVISE
