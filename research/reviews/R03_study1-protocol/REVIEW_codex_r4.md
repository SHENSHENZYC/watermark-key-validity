# R03 — Study 1 protocol before lock — independent review, round 4

Date: 2026-10-10 UTC. Reviewer: Codex.

Recommendation: **AGREE on this bounded re-review.** The blocking round-3 numerical failure and the major two-tail error are repaired, and the moment and role/guard corrections work. Two minor implementation/reporting qualifications remain below; neither demonstrates a failure of the registered grid. This recommendation concerns F17–F20 and leaves the lock/run decision to Yichen.

## 1. Baseline and scope read

Baseline: `eaf3e92140a5f4a13026201e3d1f276e130c4023`, matching the requested `eaf3e92`. The working tree was clean at the start.

Read the orientation in full and the prompt's Round 4 section; `RESPONSE_claude_r3.md`, including the verification table and dispositions; the protocol's round-3 corrections paragraph and §§3, 8, 9 and 11; the four Python-file diffs since `3cde956`, with surrounding definitions where needed; and the relevant validation records for R3 decisions, R2 enumerations and thresholds, mixture moments, provenance and inventory guards. Also checked the changed handoff/brief passages and decision-log tail for consistency with this bounded review.

Independent checks used short `python -B` computations and in-memory mutations of reads. They included the original F17 fixture, the actual analyzer decision function, exact binomial sums, scalar threshold roots, independent numerical integration, the existing validation inventory, and the pairwise subsample-selection boundary. Completed numerical checks each took less than one second of reported tool wall time. No full validator, production simulation, download, commit or other file write was performed. Only this memo is written.

## 2. Claims against evidence

### Disposition of F17–F20

| Finding | Assessment |
|---|---|
| F17, blocking: R3 roundoff failure and overstated calibration | **Blocking defect resolved.** The actual decision now compares the absolute difference with `6*SE + tolerance`, so the old tiny-positive-SE failure cannot recur through that branch. The unsupported experiment-level tail probability has been withdrawn. The broader constant-estimator shortcut needs the minor qualification in F22. |
| F18, major: one-sided bound used for a two-sided decision | **Decision and guarantee resolved.** The implementation uses `min(1, 2*exp(-K*KL))`; both the counterexample and covered-support enumerations reproduce. One auxiliary validation field still stores the old one-sided quantity, F21. |
| F19, minor: missed narrow transition in quadrature | **Resolved at the identified boundary.** The convolution mean and bivariate-normal second moment replace quadrature. Independent integration with transition-scaled breakpoints agrees at sigma² = 1e−8 and 1e−6. |
| F20, minor: role metadata and guard fixtures | **Resolved.** Full law specifications are bound to slots; analysis uses expected roles. Role-only mutations fail both reuse and inventory checks. The marker and no-lock fixtures now reach their named guards. The grid reference and brief's constraint count are corrected. |

### R3: original failure and actual decisions

Re-ran the F17 validation fixture: `Chain(TwoToken(0.9), h=0, N=20, L_max=64, seed=3)`, raw incidence, fixed colouring at gamma=0.5, keys 1,000,000–1,001,999, and statistics RNG 9. The absolute discrepancy remains **3.0682921481339775e−17**, against tolerance **1.25078125e−10**; the estimator is marked constant, its SE is zero, and `r3_check` returns **gross=False**.

Independently called `r3_check` on the six specified decision cases. Exactly-zero SE with equal values, a tiny positive SE with a roundoff-sized difference, 5-SE deviation, 7-SE deviation, negligible structural-zero observation, and material structural-zero observation returned **[False, False, False, True, False, True]**, matching the validation record. An additional zero-SE case with a difference materially above tolerance returned **True**. The analyzer's main R3 loop calls this same function, so these fixtures test the decision it actually uses.

### R2: two tails, enumerations and thresholds

For i.i.d. bounded per-key levels with mean mu, the upper and lower KL rejection regions each have probability at most half the chosen tolerance. Their union therefore has probability at most **1e−6** under the new rule. Dependence between different cells does not invalidate the subsequent union bound. Recounting the grid gives at most **909** non-degenerate independent/distinct alpha checks, hence **0.000909**, conservatively rounded to 9.1e−4 in the protocol. This derivation is under the stated ideal independent-key model.

Exact enumeration independently reproduces:

| Regime | K | False-audit probability under corrected rule |
|---|---:|---:|
| Round-3 counterexample, mu = 0.027254722688931254 | 500 | 2.4585336520525188e−8 |
| Covered support, gamma=0.5 | 500 | 2.1818316682616443e−8 |
| Covered support, gamma=0.5 | 2,000 | 2.402092597389055e−7 |
| Covered support, gamma=0.25 | 500 | 1.777835410455832e−8 |
| Covered support, gamma=0.25 | 2,000 | 4.9307608479619404e−8 |

The counterexample's lower tail is no longer flagged; its remaining probability is entirely upper-tail. Scalar roots of `KL(a||mu) = log(2e6)/K` agree with the validator's threshold grid to its 1e−5 resolution. For example, at mu=0.01 and K=500 the continuous upper boundary is **0.042150311958990556**, versus the first flagged grid point **0.04216**. There is no flagged lower tail. At mu=0.05 and K=500 the boundaries are **0.007598783553235263** and **0.11041022913716207**. These are rejection boundaries, not power probabilities.

### Moments and metadata

Under the stated common-factor Gaussian model, with total variance `rho + sigma²`, the convolution gives the first moment and two residual draws sharing the factor give the second moment with correlation `rho/(rho + sigma²)`. The implemented formulas follow that derivation. Independent integration of the squared conditional level, split around the narrow transition, gives population-variance discrepancies at most **3.1e−15** for sigma² in {0, 1e−8, 1e−6, 1e−3}. At sigma²=1e−6 the mean is **0.010000031001095885** and the finite-text term **3.759222162771133e−9**; at 1e−8 the latter remains positive, **3.759215313967057e−10**. The exact zero limit and deterministic zero-total-variance cases work. The validation's zero-rho case has a residual population SD about 6.4e−9 from floating-point cancellation, immaterial to its conditional SD; closed form does not mean exact floating-point arithmetic.

The saved validation grid digest matches the current grid. Its **210-cell** inventory passes `load_inventory`, and a matching cell passes reuse. With only `law.role` changed in memory, reuse fails at the body/slot check and inventory loading fails at the body/grid check. With only a marker's `levels` key added, loading reaches and fails the marker-status guard. A complete inventory using the validation laws in study mode without a lock reaches and fails **“study mode requires --lock”**. These independently confirm the reported fixtures without altering files.

For the new pairwise replication, an instrumented call confirms one 300-text subsample at N_eff=599 and two disjoint 300-text subsamples at N_eff=600, with the reported difference computed from the two results. The validation reports SDs **0.0066781693** and **0.0066527787** for its light-overlap example. The two-block example correctly reports no replicate because it has only 400 texts.

## 3. Method and statistics

The primary target, predictor assumptions and grid are not reopened in this bounded round. The moment correction changes numerical evaluation of the stated model; it does not turn the common-factor approximation into a consequence of covariance identities alone.

The corrected R2 decision has the stated finite-sample bound under its assumptions. Its conservative power tradeoff remains. A dead detector is detectable when `2*(1-mu)^K < 1e−6`, not merely because mu is positive: the thresholds are approximately mu>0.02860036 at K=500 and mu>0.00722808 at K=2,000. Protocol §9's “every cell whose exact null rejection probability is positive” should be read with this necessary quantitative condition, or supported specifically for the registered cells. This is a qualification of the power wording, not a failure of the corrected validity bound.

The revised R3 calibration is explicitly heuristic and no longer asserts an experiment-level false-audit probability. The 400-replicate evidence establishes central behavior in the stated setting; it cannot guarantee that every future 6-SE crossing is an implementation fault. Such a crossing remains an audit trigger. The tolerance-inclusive decision resolves the demonstrated floating-point failure independently of any tail approximation.

The difference between two pairwise subsamples is a useful stability diagnostic, not a calibrated standard error or an attribution proof. The revised text's requirement for agreement and its qualification that attribution is suggestive are appropriate. No additional large simulation is necessary to establish the concrete repairs reviewed here.

## 4. Process and disclosure

The protocol remains DRAFT. Neither `outputs/study1_v0.3/PRE_RUN_LOCK.json` nor the production `cells/` directory exists. The changed log and handoff record Yichen's bounded round-4 decision, consistent with the direct user request. Corrections in place are dated, with the prior text recoverable at `3cde956`; there is no locked-production protocol being silently changed after production outcomes.

The updated §11 identifies the regenerated validation run and its use of synthetic outcome statistics as a disclosed pilot. The response discloses the intermediate placeholder-fill failure. At this baseline the reviewed sections and record contain the results. The two pilot analyzer executions and their counts are recorded. The 42 projected chain times sum to **6,270.6 seconds = 1.74183 hours**, consistent with the revised 1.74-hour projection; this remains an extrapolation, not a runtime guarantee.

No real-corpus data or holdout was accessed. No new literature claim or quotation is needed to establish F17–F20, so the prior literature verification is not presented as a fresh check in this memo. An AGREE is review advice; it is not Yichen's approval to lock or run.

## 5. Independent search for occupants or newer work

No new external search was performed in this round, in keeping with the explicit restriction to the round-3 corrections. The preceding round's search and verified attribution record are unchanged. This memo makes no new novelty, priority or search-absence claim and does not reopen the topic gate.

## 6. Findings and recommendations

### F21 — minor — Finish the two-sided correction in the auxiliary bound field

**Evidence.** `s1_validate.py:159` still assigns `bound_at_zero = (1-mu)**K`, and its nearby comment and protocol §11 retain that one-sided expression. For mu=0.01 and K=500, the saved field is **0.006570483042414603**, whereas the implemented two-sided bound is **0.013140966084828837**, as correctly stated in §9. The threshold scan itself calls the corrected function, so the listed rejection thresholds and actual R2 decision are correct.

**Recommendation.** Obtain this field from `kl_chernoff_pbound(0, mu, K)` and synchronize its explanation; also use the quantitative dead-detector condition stated in §3 above. This is a reporting correction and does not reopen F18's repaired decision or require repeating the full validation.

### F22 — minor — Sample constancy is not analytic proof of zero sampling error

**Evidence.** `s1_core.py:479` tests the range of the **observed** squared deviations and, when it is below tolerance, overrides either colouring's SE with zero before the exact independent-colour fourth-moment calculation. This is stronger than warranted by the sample. The phrase **“recognised analytically”** in the protocol and response is therefore inaccurate for this general branch, even though the original two-token/fixed case truly is constant under the key law.

A deliberately small validation illustration makes the distinction concrete: `Chain(ZipfIID(4,0), h=0, N=4, L_max=4, seed=5)`, raw incidence, gamma=0.25, and four all-red independent-colour realizations. This all-red count table is a possible sample under the specified colouring. The code reports zero SE and gross=True, while the exact fourth-moment SE is **0.03503396702080488** and would not flag the discrepancy between observed variance **0.0625** and exact variance **0.052734375**. **K=4 is outside the registered grid**; this illustrates the logical scope of the shortcut, not a demonstrated registered-grid failure. It does not undo the successful tolerance repair of F17.

**Recommendation.** Retain the exact fourth-moment SE for independent colours, and reserve a claim of zero sampling error for a distributional identity such as the fixed two-token case. Otherwise label the condition as observed sample constancy and any bootstrap SE as empirical. The new `6*SE + tolerance` rule already handles the original roundoff problem without this general override. This bounded cleanup is non-blocking for the reviewed grid; no material registered-grid failure from it has been established here.

No blocking finding remains open in the requested F17–F20 re-review.

VERDICT: AGREE
