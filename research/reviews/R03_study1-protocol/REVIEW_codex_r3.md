# R03 — Study 1 protocol before lock — independent review, round 3

Date: 2026-10-10 UTC. Reviewer: Codex.

Recommendation: resolve the remaining R3 numerical failure before locking. The canonical lock repair works, the model assumptions are now explicit, and the rare-key R2 problem is substantially repaired. However, a correct two-token fixture still fails R3 solely because roundoff produces a tiny positive bootstrap SE. R2 also understates its two-sided false-audit bound. These are concrete corrections to the proposed checks, not reasons to abandon the study or revisit D5. Yichen retains the checkpoint/arbitration decision.

## 1. Baseline and scope read

Baseline: `3cde9569f1fb74c3f9734e93f792e9641518a088`, matching the requested `3cde956`. The working tree was clean before this memo.

Read the orientation in full; the R03 prompt's Round 3 section; `RESPONSE_claude_r2.md`, including its verification table, dispositions and three additional points; protocol v0.3, beginning with the round-2 changes paragraph; all four Study 1 Python files; `grid_v0.3.json`; the complete v0.3 validation record; the gate's adjacent-work rows, revised candidate/verdict and constraint 16. Also checked the handoff, decision-log tail, brief, dated corrections to the round-1 response, and corrected corpus-audit key-exposure wording.

Independent checks used `python -B`, small arrays, exact probability calculations, one-dimensional integration, and in-memory filesystem fixtures. Each command took less than a second of reported tool wall time. No validator or production grid was run; no production seeds, sealed data, model, download, commit or other file modification was used. Only this memo is written. The validation record's larger simulations are the conductor's evidence, not runs repeated by this review.

## 2. Claims against evidence

### Disposition of F11–F16

| Finding | Round-3 assessment |
|---|---|
| F11: experiment identity | The blocking canonical-path/provenance defects are resolved. Independent fixtures accept the canonical lock and matching cell, and refuse the old path/checkpoint/date, stale-digest, wrong-slot, wrong-body and missing-alpha cases. A narrower role-metadata gap remains, F20. |
| F12: unstated joint assumptions | Resolved as an adequacy-study specification. The common-factor assumptions and nonlinear covariance approximation are explicit; the ddof-1 coefficient is corrected. The secondary pairwise calculation reproduces the exactly Gaussian two-block result. Its text-subsampling uncertainty still limits attribution. |
| F13: zero variance and quadrature | The unit-variance substitution is removed and the exact zero limit works. Invalid sigma inputs are flagged, with the zero-limit fallback explicitly disclosed. A small near-zero quadrature error remains, F19. |
| F14: rare-key R2 calibration | The original zero-observation/infinite-SE failure is resolved by using a bounded-mean check. The stated per-check and experiment-level bounds omit the second tail, F18. |
| F15: R3 zeros and coverage verdict | Exact-zero colour variances now work and nominal-95% coverage is descriptive. The constant-estimator boundary is only repaired when its computed SE is literally zero; positive roundoff SEs still produce false gross failures, F17. The claimed extreme-tail calibration is also stronger than the evidence. |
| F16: wording and pilot inventory | Substantially resolved. The candidate wording is superseded, priority qualified, earlier numbers corrected, the pilot disclosed, and analysis output moved outside the inventory. The two successful pilot analysis executions are recorded. |

### Lock and inventory checks

`s1_run.py:113` now pins exactly the eight declared files, canonical paths, R03 resolution identity, ISO date, study and key record, with explicit exceptions. In a virtual copied root containing the real pinned-file bytes and a fixture resolution, the canonical lock passed. Changing the protocol to the grid, checkpoint to R02, date to junk, or validation to v0.2 was refused separately. This tests canonical identity without creating a real lock or asserting human approval.

A genuine tiny validation cell passed `load_inventory` and resume. Changing its grid digest, slot, body width or alpha set caused refusal. Reading the analyzer confirms it verifies the lock in study mode and compares deterministic per-law seeds and key records. The earlier uniformly stale complete-inventory acceptance is no longer present.

Two recorded negative fixtures stop earlier than their names imply: `marker_replaced_by_live_cell` fails provenance, and `study_mode_without_lock` fails inventory completeness. Their intended guards are present in the code, but those particular executions do not independently exercise them. Fixtures should alter only the condition being tested.

### Mathematics and numerical checks

The corrected within-key sample-variance identity is

`mean(V_i) − rho_bar + N/(N−1) mean[(mu_i−mu_bar)²]`.

The implemented coefficient now matches this expression. The pairwise Gaussian covariance uses the correct bilinear form, including the fixed-size context correction. Its diagonal-plus-off-diagonal indicator-variance formula is correct when evaluated on all texts. On 20 fixed coordinates in two equal, internally identical Gaussian groups, evaluating all pairs returned SD **0.07035623639735140**, versus the analytic **0.07035623639735145** at alpha=0.01. This checks the formula without requiring a sampled-key approximation.

Independent one-dimensional integration checks of `bvn_upper` agreed to about machine precision on ordinary positive/negative correlations and the ±1 limits. At exactly zero thresholds, the implementation's epsilon substitution caused an absolute error about **4.0e−13**, immaterial here. The conductor's non-Gaussian two-block pilot records common-factor and pairwise ratios **2.0765** and **1.0268**; these are consistent with the intended diagnostic, not proof of universal Gaussian adequacy.

The zero-sigma mixture now returns mean **0.01**, SD **0.099498743710662** and finite-text term **0**, as required. The ordinary-variance mixture agrees with its analytic Gaussian moments. The near-zero case is discussed in F19.

For R3 under independent colours, the known-mean estimator and fourth-moment SE are correct:

`Var(s0²) = [g(1−g)(1−6g(1−g)) Σw⁴ + 2 Var(q)²]/K`.

A fixed-size full-coverage identity is now set to zero with the stated tolerance. That is distinct from a nonzero variance whose *squared centered observation* is constant over keys; the latter exposes F17.

For R2, convexity gives `E exp(lambda X) <= 1−mu+mu exp(lambda)` for X in [0,1]. Independence across keys and Chernoff optimization then give the implemented one-sided KL bound. Shared keys across cells do not obstruct a union bound. Choosing the tail after observing the deviation does require accounting for both tails, however.

The covered-support enumeration in `VALIDATION.json` is traceable to `s1_validate.py:129`: at gamma=0.5 its probabilities are **1.12582e−7** for K=500 and **3.03532e−7** for K=2,000. The old K=500 all-zero-key event has probability 0.02125 but no longer flags R2. These particular enumerations are compatible with the proposed threshold; they do not establish the claimed universal two-sided bound.

### Record and literature verification

The current grid digest matches the validation record. Relative to v0.2, only `study` and the explanatory `validation_note` changed; the numerical design is unchanged. There are at most **909** non-degenerate independent/distinct alpha checks before structural-zero exclusions. The projected 42 chain times sum independently to **6,369.6 seconds = 1.76933 hours**; 1,194 live cells plus 54 markers give 1,248 files. The record reports 650.2 seconds for validation and 4.98 GB peak validator memory. The six-hour feasibility conclusion remains a reasonable extrapolation with margin.

Local substring checks again confirm `research/literature/txt/2609.37310.txt`, PDF p.4, “novel second requirement,” and p.42, “multiplying by 1/β”; `genhatharan_nominal_fpr_2026.txt`, PDF p.1, “from 0.27% to 48.4%,” and p.7, “88 of 128 keys (69%).” The revised allocation of formal per-key validity, remedies and prior measurement remains supported. This verifies the cited passages, not those papers' experimental reproducibility.

## 3. Method and statistics

The primary target remains coherent: across-key SD of the empirical level on fixed texts. The common-factor predictor is properly presented as an approximation to be tested. All candidate/eligible/resolved counts are now reported, so R1's resolved-subset success criterion can be interpreted. Its normal-theory SD precision benchmark is appropriately qualified.

The pairwise predictor is secondary and need not be promoted to another pass/fail rule. Its 300-text calculation estimates the full fixed-text average of nonlinear pairwise tail covariances. It therefore adds subsampling error, and clipping a negative estimated variance to zero does not remove that uncertainty. A pairwise/common-factor comparison can suggest heterogeneity; a single subsample cannot uniquely attribute every disagreement to heterogeneity versus nonnormality. Report it as a diagnostic, and assess subsample stability where an attribution is important.

R2 trades substantial power for a finite-sample bound. That tradeoff is now disclosed. A threshold-crossing table is not a full power curve under every alternative. In particular, “a dead detector … caught … in every cell” needs the qualification that the exact null rejection probability is sufficiently positive; structural-zero cells cannot detect that fault. The factor-of-two correction can preserve the current rejection region if its larger bound is reported honestly, or preserve the intended bound by halving the per-tail threshold.

R3's change from nominal interval coverage to gross deviations is sensible, but neither a CLT at K≥200 nor adding two orders of magnitude to a normal tail proves the stated experiment-level probability. Four hundred replicates of one setting establish central calibration there; zero exceedances cannot certify probabilities around 1e−7. The numeric defect in F17 must be repaired independently of that interpretive limitation.

R4/R5 remain descriptive checks with explicitly non-simultaneous tolerances. The support-limit tolerance and distinct handling of degenerate colours, no-retained-text cells and structural-zero rejections are retained. No new grid or experiment is needed for the concrete corrections below.

## 4. Process and disclosure

The protocol, handoff and log consistently keep v0.3 in DRAFT pending review and Yichen's lock/run instruction. Neither its production lock nor production `cells/` directory exists at review time. The validator explicitly discloses that it examines synthetic outcome statistics on validation laws/seeds/keys. Earlier pilots remain records; production and confirmatory namespaces remain separated. No real-corpus holdout issue was reopened.

The gate's candidate summary, adjacent-work rows and constraint 16 now support attribution to the existing record. The conductor labels the arXiv 2607.13003 row as based on its abstract and on the reviewer's earlier section-level inspection, rather than claiming a new full-paper read. The earlier validation corrections are dated. Minor stale references remain: protocol §8 still points to `grid_v0.2.json`, and the brief still says fifteen wording constraints after constraint 16 was added.

This review supplies evidence for Yichen's checkpoint decision. It does not lock a protocol, authorize a production run, or change a rule after outcomes.

## 5. Independent search for occupants or newer work

Repeated bounded searches for `site:arxiv.org watermark "key-conditional" "false positive"`, `site:github.com watermark "per-key" "false-positive"`, and the official vLLM v0.31.0 watermarking page with “key-dependent.” The search returned the already identified Genhatharan repository and [official vLLM documentation](https://docs.vllm.ai/en/v0.31.0/features/watermarking/), whose Detection section again supports the fixed-key limitation despite within-document deduplication. No additional direct dispersion study was verified. This is a limited search result, not a novelty or priority proof.

The adjacent [arXiv 2607.13003v1](https://arxiv.org/html/2607.13003v1) classification remains based on the previous round's inspection of Definition 3.5, Theorem 3.6 and Appendix C.6: enrolled-key attribution with a source-aware decoder, rather than the present KGW dispersion account. No blocked endpoint was retried or bypassed, and no literature file was downloaded.

## 6. Findings and recommendations

### F17 — **blocking** — R3 still declares a correct constant-estimator case a gross failure

**Evidence.** `s1_analyze.py:172` divides by every positive SE; the scale-aware equality tolerance is used only when the SE is exactly zero. Floating-point bootstrap arithmetic can give a positive SE for a mathematically constant squared deviation.

A short reproducible fixture uses `Chain(TwoToken(0.9), h=0, N=20, L_max=64, seed=3)`, raw incidence at L=64, fixed colouring at gamma=0.5 with validation keys `range(1000000,1002000)`, and `cell_statistics(..., alphas=[0.01], rng=np.random.default_rng(9))`. It gives:

| Quantity | Value |
|---|---:|
| Known-mean variance estimate | 0.0001562499999999996 |
| Exact identity as computed | 0.00015624999999996891 |
| Absolute difference | 3.0682921481339775e−17 |
| Bootstrap SE | 3.6456501852366906e−20 |
| Existing numerical tolerance | 1.25078125e−10 |
| Implemented standardized deviation | 841.6309827419087 |

The analyzer's rule therefore fails this correct simulator. At h=0 with V=2 and one fixed green token, q takes two complementary values, so `(q−0.5)²` is constant for every key: its true estimation SE is zero. This boundary belongs to the declared two-token illustrations, which enter R3's overall decision. A separate five-text L=64 construction with mean token weights (0.55,0.45) also falsely fails at K=200, 500 and 2,000. No production outcome was used.

**Recommendation.** Apply the scale-aware difference tolerance before dividing, or compare against a threshold that includes both numerical tolerance and `6*SE`. Recognize the constant squared-estimator case analytically where available. Exercise the analyzer's actual decision on both exactly-zero and tiny-positive computed SEs; the current `equal_within_tolerance` validation field alone does not test its branch. Also replace the unsupported “at most about 2e−4” R3 false-audit statement with an explicitly heuristic calibration statement or a justified bound. The latter does not require a large new validation run merely to remove an unproved claim.

### F18 — major — R2's one-sided bound is reported as a two-sided test guarantee

**Evidence.** `kl_chernoff_pbound` correctly documents a bound “on the observed side,” but the analyzer flags either side at 1e−6 and reports `n_checks * 1e−6` (`s1_analyze.py:156`). Protocol §9 makes the same per-check claim. The guaranteed bound from these two Chernoff inequalities is **2e−6 per check**, hence at most **0.001818** over the maximum 909 checks, not 0.000909.

This is not just a missing proof. For K=500 and Bernoulli per-key levels with `mu = 1 − (0.999e−6)^(1/500) = 0.027254722688931254`, exact binomial enumeration of the implemented rule gives lower-tail rejection probability **9.99e−7**, upper-tail probability **7.300283930097026e−8** (37 or more successes), and total **1.0720028393009513e−6**. This contradicts the claimed universal 1e−6 bound. It is a bounded-mean counterexample, not a claimed grid outcome.

**Recommendation.** Either retain the rejection region and report the two-tail bound everywhere, or use 5e−7 per tail / `min(1, 2*exp(−K*KL))` to retain the stated per-check tolerance. Recompute the small enumeration and threshold tables if the region changes. The revised method still resolves the old 2.1% false-audit problem.

### F19 — minor — Adaptive quadrature still misses part of a narrow transition

**Evidence.** At `(mu, rho, alpha, N, sigma²)=(0,1,0.01,4000,1e−6)`, `mixture_predictor` returns mean **0.00998938281852298**. The exact Gaussian convolution gives **0.010000031001095885**. The implemented finite-text term is **1.87644e−9**, versus **3.75922e−9** from the bivariate-normal moment identity; total SD differs by only **0.0147%**. At sigma²=1e−8 the unflagged integral drops the finite-text term to zero. Thus the numerical fix is much better, but a breakpoint only at the transition center can miss its narrow shoulders. Monte Carlo noise in the validation masks this error.

**Recommendation.** Use the analytic convolution mean and bivariate-normal second moment already available, or split integration at several sigma-scaled distances around the transition and verify convergence. Add analytic comparisons for near-zero variance. This residual error is small relative to R1's adequacy band and is not the reason for the blocking verdict.

### F20 — minor — Bind the role used for rule selection to the expected grid slot

**Evidence.** `body_matches_slot` compares the law through `law_name`, which omits `role`. Changing only a valid tiny cell's `law.role` from core to illustration was accepted by both resume and inventory loading. The analyzer then uses that body role to select R1/R4/R5 and the core-fixed exclusion in R3. The canonical provenance fixes otherwise work.

**Recommendation.** Validate the full relevant law specification, or take role and other design classifications directly from `_exp`. Add a role-only mutation fixture. Make the marker/no-lock refusal fixtures reach their named guards, and correct the stale grid/constraint-count references noted above. These are bounded follow-ups to the now-resolved canonical lock defect.

VERDICT: REVISE
