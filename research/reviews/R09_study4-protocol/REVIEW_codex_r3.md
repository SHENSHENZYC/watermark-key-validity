# R09 — Study 4 protocol, independent re-review, round 3

Reviewer: Codex. Date: 2026-10-16 (UTC).

## 1. Baseline and scope

Baseline: **`999292312835319ce245c6cdd541c2d39c4a36ec`**, `main`; the working tree was clean when reviewed. This review is bounded to F13–F17, their corrections and fixtures, and consequences of those corrections. It does not reopen the agreed Studies 1–3 or the findings resolved in earlier rounds.

Read the orientation and R09 prompt; `RESPONSE_claude_r2.md`, including its verification table and D16; the changes since the round-2 baseline `bf751c92d97a141cc7d171e834aa86e9cf455a13` in `s4_analyze.py`, `s4_run.py` and `s4_validate.py`; the protocol's header, §§3 and 6–11; `VALIDATION.json`; and the decision log's round-2/D16 entries. Followed the revised calls into `s1_core.twoway_population_variance`, `s4_core.between_key_sd_twoway`, `s4_record.CalUnit.threshold` and `s4_gen._sample_rows` to check their semantics.

Performed short, model-free computations in memory, with bytecode writes disabled and a 55-second alarm per Python process. These included reproducing the synthetic W2 fixtures, independently reconstructing a crossed interval, driving the actual finite-resample branch with controlled estimator returns, mutation checks of the sampler, recomputing the resume arithmetic, and checking the new bootstrap's centering and coverage. No full validator, inputs builder or analyzer was rerun; the recorded analyzer time is 209.5 seconds. No model was loaded, nothing was downloaded, and only this memo was written.

**Assessment:** D16 fixes the estimand mismatch and the raw point estimator is correct for that target under the stated model. Resampling both dimensions and preserving the pairing is appropriate, but the particular *uncentered percentile interval* now implemented is not adequate: its resampled variance components are centered near the observed variances rather than the corrected components. A short exact-model check gives 48% coverage for a nominal 95% ratio interval. This is the remaining major issue, F18. F14 and F16 are resolved; F15 and F17 are substantially corrected, with the minor residues below.

## 2. Claims against evidence

### D16 and the point estimator

Protocol §3, line 50, now explicitly targets “the variance across keys of the key's expected power over the cell's prompt law, keys and prompts both random,” and distinguishes this from the variance of a fixed table's key means. The header and §§6, 8 and 9 follow that choice. This addresses F13's target objection.

Write the crossed model as

\[
Y_{ki}=\mu+A_k+B_i+E_{ki},
\]

with centered key and prompt effects, independent sampling of the two factors, and the interaction plus generation noise in the orthogonal residual component. Let their variance components be \(v_K,v_P,v_e\). For the balanced table, the shared prompt main effect cancels from the sample variance of the key means, giving

\[
E[s_K^2]=v_K+v_e/n,\qquad E[MS_E]=v_e,
\qquad E[s_K^2-MS_E/n]=v_K.
\]

Study 1's function at `s1_core.py:434–442` implements exactly this ANOVA subtraction; Study 4 transposes the key-by-prompt table correctly. Thus the **raw variance estimate** is unbiased under this model. The floored variance, square root and ratio are not thereby unbiased; the protocol records the floor and raw components and should retain that distinction.

I reproduced the final F9 arithmetic at its actual settings: 400 tables, 100 keys, 50 prompts; Gaussian key SD 0.08, prompt SD **0.12**, interaction SD 0.06; probabilities clipped to [0.001, 0.999].

| Quantity | Independent result |
|---|---:|
| Mean raw two-way estimate | 0.00632972067614925 |
| Monte Carlo SE of that mean | 0.00006962672486430 |
| Mean independent-binomial proxy | 0.00604490442383014 |
| Monte Carlo SE of that mean | 0.00006960034557737 |
| Unclipped model's key component | 0.0064 |
| Unclipped proxy expectation, \(v_K-v_P/n\) | 0.006112 |
| Clipped probabilities | 2,794 / 2,000,000 |

All implemented acceptance guards pass. The proxy expectation follows because its subtraction charges the variation of prompt main effects within a key as though it were independent noise. Clipping makes the quoted planted component approximate: integrating the clipped Gaussian conditional mean gives \(v_K\approx0.00638210524\), \(v_P\approx0.01436008452\), hence proxy expectation about 0.00609490355. This small difference is below the fixture's tolerance; it does not undermine the point-estimator conclusion. It should not be described as an exact unclipped planting (F20).

The fixed-table fixture also reproduces exactly. Its first 50 keys reject the first 24 prompts and its remaining 50 keys reject the other 26:

| Quantity | Independent result |
|---|---:|
| Variance of the fixed key means | 0.000404040404040405 |
| Residual mean square | 0.257266542980829 |
| Raw two-way component | −0.004741290455576168 |
| Floored between-key SD | 0 |

The changed interpretation is correct: this is a counterexample to a fixed-table target, not a failure of the population-component identity.

### F14: labels and windows

The emitted descriptive dictionary at `s4_analyze.py:255–259` now has `power_sd_observed`, `power_sd_between_twoway`, `power_var_between_raw_twoway`, `ms_resid_twoway`, `power_sd_between_binomial_proxy` and `power_var_between_raw_binomial_proxy`. The ambiguous `power_sd_between` field is gone. The two-way component uses the per-text float64 p-values and the relevant strict thresholds; the nominal, multiplier, scalar empirical/pooled and per-key threshold cases agree with `CalUnit.threshold`. W2 separately emits the observed SDs, two-way components and nested `binomial_proxy` fields.

The null quality path now appends and aggregates `mean_logp_first_192` (`s4_analyze.py:312–314`), as the watermarked path already does. On the saved 96-text validation null array I obtain −3.0261030197143555 over the first 192 tokens, versus −3.0807297229766846 over all 256; the all-token perplexity is 21.7742862701416. The windows are distinct and the current dictionary emits the requested one. This conclusion follows from the current emission code and the array computation, not a new full analyzer run. Protocol §7 matches these fields. **F14 resolved.**

### F15: rule branches and sampler

The planted raw-rule rows still classify as agree/disagree, and the distinct-rule rows as agree/disagree, under the revised crossing. The all-zero nominal table now really reaches the zero-denominator guard: nominal SD 0, nonfinite ratio and interval endpoints, zero finite resamples, class unresolved.

The stored “finite-share boundary” result is weaker than claimed: `s4_validate.py:200–201` compares constants to the configured cutoff without calling `w2_row`. I separately drove the actual production branch with a positive observed denominator and controlled 179, 180 and 181 finite ratios out of 200. It returns unresolved at 179 and a finite classified interval at 180 and 181, correctly implementing “fewer than 90%.” Thus the implementation is currently correct, but the committed fixture does not protect it (F19).

The compensated-CDF sampler check now has real power against float32 accumulation. Reproduced indices are `[0, 0, 103, 51935, 141935, 151935]`. A mutant using float32 accumulation with the current terminal-mass scaling returns `[0, 0, 0, 0, 0, 151935]`; the old unscaled float32/argmax form returns all zeros. Both fail. The valid tail probes `c32 + 1e-7`, 0.99990 and 0.99999 therefore catch the regression. The plateau test reproduces `[0, 0, 0, 1007, 0, 993]`, and a zero draw selects index 3. One remaining probe is outside the RNG's domain (F19); it does not negate the three valid probes' effectiveness.

### F16 and F17

Protocol §10 now separates unresolved and inconsistent W1 rows, avoids assigning a mechanism to failure, and explicitly recognizes that a distinct-rule interval below the band is a reduction that disagrees with “little change.” These readings agree with §6. **F16 resolved.**

`generated_units` starts empty per invocation, grows only after a completed `run_unit`, and is not extended by the reuse branch. `projected_hours` sums only that list; `budget_exceeded` implements a strict greater-than comparison. With the current recorded costs, ten new null units after 620 reused units project to **0.7375 h**, versus **8.5458333333 h** if reused units were credited. Three elapsed hours correctly stop only the former; equality at twice the projection does not stop, and a value just above it does. These reproduce F10 and §11. The erroneous credit identified by F17 is removed. The claim that reused units are also “not timed,” and F10's use of a previous validation file, need minor correction (F21).

## 3. Method and statistics

The revised question is precise: for each method, estimate \(\operatorname{Var}_K E_{P,G}[Y\mid K]\), with the threshold record held fixed and prompt and generation variation averaged out. Keeping the observed dispersion over the realized 50 prompts descriptive is the correct distinction. It does not require new generation replicates merely to define this population target.

The implementation resamples a key index vector and a prompt index vector independently, applies the **same two vectors to both indicator tables**, and recomputes the components each time. An independent implementation of the ANOVA arithmetic and the specified RNG sequence reproduces a representative ratio interval to 5.6 × 10⁻¹⁷. Thus there is no pairing or indexing bug. The problem is what distribution those resamples estimate and the use of their direct percentiles.

For a fixed observed table, let \(a=(K-1)/K\), \(b=(n-1)/n\), and let \(E_*\) denote expectation over the implemented crossed resampling. Directly averaging the sample means and centered residual sums gives

\[
E_*[s_K^{2*}]=a\left(s_K^2+\frac{b\,MS_E}{n}\right),
\qquad E_*[MS_E^*]=ab\,MS_E.
\]

Consequently,

\[
\boxed{E_*[\widehat v_K^*]=a\,s_K^2},
\qquad \widehat v_K=s_K^2-MS_E/n.
\]

This conditional bootstrap center is displaced from the estimate by
\(MS_E/n-s_K^2/K\). The extra prompt resampling introduces variation from the empirical interaction/noise; applying the usual ANOVA correction to that resample does not center it back on the original corrected component. Pairing preserves covariance between methods but does not remove these marginal displacements. When the corrected components are small relative to \(MS_E/n\), their ratio can be materially shifted.

I checked this identity by enumerating all 108 crossed resamples of a 3 × 2 binary table and by 20,000 resamples of a 100 × 50 table. In the latter check, the original raw component was 0.00723133375 and the observed variance 0.01183430303; the formula predicts bootstrap mean 0.01171596000, and the measured mean was 0.01172116840 (Monte Carlo SE 0.00001848944). The discrepancy from the original component is systematic.

For a direct check at the registered sizes, I used an exactly bounded paired model, without clipping. Draw independent equiprobable effects \(A_k=\pm0.08\), \(B_i=\pm0.12\), \(C_{ki}=\pm0.06\) and shared independent uniforms \(U_{ki}\). Set

\[
Y^n_{ki}=1\{U_{ki}<0.5+A_k+B_i+C_{ki}\},\quad
Y^c_{ki}=1\{U_{ki}<0.3+0.5A_k+B_i+C_{ki}\}.
\]

All probabilities are valid; the method's rejection set is always a subset of the nominal set, so the tables have the monotone pairing required of a lower threshold. The population key variances are exactly 0.0064 and 0.0016, giving a true SD ratio of **0.5**. Across 300 tables:

| Quantity | Result |
|---|---:|
| Mean raw nominal component | 0.006311343915343916 |
| Mean raw method component | 0.0015717059025630454 |
| Median point ratio | 0.4954014968535324 |
| Rows with finite reported intervals | 300 / 300 |
| Nominal 95% intervals covering 0.5 | **144 / 300 (48%; Monte Carlo SE about 2.9 pp)** |
| Median interval endpoints | [0.5033727405371242, 0.9218699351806172] |

The point estimation behaves as intended; the percentile interval does not. The zero-denominator/finite-share guard does not explain this result because all 300 intervals are finite. The exact centering identity also shows why increasing the bootstrap replicate count alone cannot repair it. The current “nominal” qualification appropriately disclaims an exact guarantee, but does not make this degree of undercoverage adequate for a primary classification rule.

A compact reproducer, run from the repository root with `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python`, is:

```python
import signal
signal.alarm(55)
import sys, json, numpy as np
from pathlib import Path
sys.path.insert(0, 'research/study4')
import s4_analyze as A
w = json.loads(Path('research/study4/grid_v0.1.json').read_text())['W2']
rng = np.random.default_rng(2026101603)
rows = []
for rep in range(300):
    a = rng.choice([-.08, .08], (100, 1))
    b = rng.choice([-.12, .12], (1, 50))
    c = rng.choice([-.06, .06], (100, 50))
    u = rng.random((100, 50))
    yn = (u < .5 + a + b + c).astype(float)
    yc = (u < .3 + .5*a + b + c).astype(float)
    assert (yc <= yn).all()
    rows.append(A.w2_row(f'R3paired{rep}', 'raw', yn, yc, w))
finite = [r for r in rows if np.isfinite(r['ci_lo'])]
print(len(finite), sum(r['ci_lo'] <= .5 <= r['ci_hi'] for r in finite))
# 300 144; approximately three seconds in this review environment.
```

This is a synthetic method check, not an inference about the unobserved Study 4 outcomes. It supports F18 without changing D16's population target or any locked earlier study.

## 4. Process and wording

D16 is recorded as Yichen's choice; the header now assigns the pilot-law/tolerance decision to D15 and the population W2 target to D16. The changes remain pre-lock: `PRE_RUN_LOCK.json` is absent. The changed-file list since round 2 contains no Study 1–3 locked code or committed Study 3 record file, and `INPUTS.json` is unchanged. The seven current validation records contain six generation units on keys 1,000,501–1,000,502 and one unwatermarked unit. I found no contrary evidence of new evaluation-key generation in this bounded check; I did not repeat the entire round-1 timing audit.

The new issue concerns inference on synthetic tables and can be corrected before any production outcomes exist. No access to the holdout, external transfer of repository contents, new citation claim or terms-of-use question was needed. The interpretation corrections in §10 are appropriately limited. Some fixture descriptions still refer to intermediate implementations, as detailed in F20; the final JSON and generated §11, rather than those older narrative clauses, establish what actually ran.

## 5. Independent search

No new external literature search was performed for this bounded re-review. No new novelty claim or literature quotation is accepted or rejected here. The central finding follows from the local implementation, an explicit conditional-expectation calculation and reproducible synthetic data, not search absence.

## 6. Findings and recommendations

### F18 — Major: the crossed percentile ratio interval is centered on the wrong component distribution

**Evidence.** `s4_analyze.py:145–153` directly takes percentiles of ratios of the floored raw components from ordinary crossed resamples. Protocol §6, line 86, calls this a paired 95% crossed interval and uses it for W2 classification. The exact conditional expectation and bounded paired experiment in §3 above show that the resampled raw components center at \((K-1)s_K^2/K\), not at \(s_K^2-MS_E/n\); nominal 95% coverage was 144/300 at K = 100, n = 50. The new random-effects fixture tests point-estimator averages and branch labels, not this interval's calibration.

**Inference.** The D16 estimand and raw estimator are sound, and the indices are correctly crossed and paired. Nevertheless, the present percentile construction can misrepresent uncertainty for the noise-corrected ratio at the registered sizes. This prevents agreement before the lock.

**Recommendation.** Retain the population target and develop uncertainty for the *corrected components*, preserving both factors and their between-method dependence. A component-centered bootstrap construction or an explicitly justified random-effects resampling method is a candidate to validate, not a correction to assume valid merely from its name. Do not just increase B or widen an arbitrary tolerance. Add a short exact-target paired fixture checking interval coverage/behavior at the planned K and n, including a substantial residual component, an SD ratio away from one, a ratio near the classification boundaries and a small denominator. State the chosen construction and its limitations in §§6, 8 and 9, then regenerate the validation. This recommendation does not require changing Study 1's locked implementation or obtaining production outcomes.

### F19 — Minor: the finite-share fixture bypasses the branch, and one sampler probe is not a uniform draw

**Evidence.** `s4_validate.py:200–201` evaluates `0.9 < cutoff` and `(0.9 - 1e-9) < cutoff`; it would still pass if the actual analyzer comparison changed from `<` to `<=`, or the branch were removed. The actual branch passed my separate 179/180/181-resample check. At lines 239–246, `total * (1 - 1e-12)` equals **1.0000000027551703** for the stored fixture row, outside [0, 1); `_sample_rows` scales that value by its terminal mass again. The valid three tail probes do reject both float32 mutants.

**Inference.** The zero-denominator and float32-regression defects of F15 are fixed, but the boundary coverage claim is overstated and the last probe tests out-of-domain clipping rather than a valid RNG tail draw.

**Recommendation.** Exercise `w2_row` itself at 179 and 180 finite ratios (181 is also useful), with a positive observed denominator, by a controlled in-memory estimator/RNG fixture or a factored decision helper shared with production. Assert interval fields and class. Replace the last sampler probe by a valid near-one uniform such as `1 - 1e-12`, retain the independent compensated reference, and assert every supplied probe is in [0, 1). Keep the successful float32 mutation evidence.

### F20 — Minor: align the recorded fixture definitions and target descriptions with the final computation

**Evidence.** The response table's F13 disposition and `DECISION_LOG.md:619` say prompt SD 0.06, 200 tables and recovery within 3 SE; the code uses prompt SD 0.12, 400 tables and `3 * SE + 1e-4` (`s4_validate.py:203–212`). The later regeneration paragraph has the final results but does not explicitly correct those definitions. `fixture_tolerances.F9_sampler`, repeated in §11, says “fsum CDF”; the implemented reference is Neumaier accumulation. The Gaussian fixture's 2,794 clipped probabilities make 0.0064 and 0.006112 approximate rather than exact targets, as quantified in §2. Finally, the unchanged first sentence of `s4_core.between_key_sd_twoway` still describes the mean probability “over these prompts,” whereas the revised analyzer and protocol correctly specify a population target.

**Inference.** These are documentation/fixture-precision residues, not evidence that the raw two-way algebra is wrong. The recorded final means reproduce and meet the actual guards.

**Recommendation.** Add a dated correction to the log, synchronize the response and fixture labels with the final settings and tolerance, name the compensated reference accurately, and update the Study 4 wrapper's target docstring. Either label the clipping approximation with its size or use bounded effects with an exact planted component. Do not silently rewrite the historical decision or alter the locked Study 1 code.

### F21 — Minor: clarify the resume clock and make F10 independent of a previous validation file

**Evidence.** The production projection correctly excludes reused units. However, `t_run` starts before iteration (`s4_run.py:225`), and prompt loading, provenance work and `unit_status`/reuse checks run under that clock; `continue` does not subtract their time. Thus the protocol's §9 claim “reused units ... are neither credited nor timed” is not literal. Separately, `s4_validate.py:255–261` computes F10 from the previous on-disk `VALIDATION.json`, although the current `cost` was already computed at lines 170–184. Without a previous file, F10 is skipped; with changed timings it can report old costs. At this baseline the current costs reproduce the saved F10 exactly.

**Inference.** The original budget-credit loophole is closed. The remaining timing discrepancy is conservative verification overhead, and the fixture dependency is a reproducibility problem, not a current numerical failure.

**Recommendation.** Either state explicitly that verification overhead counts in elapsed time while prior generation is not credited, or measure only newly performed work if that is the intended rule. Have F10 use the freshly computed `cost` unconditionally, so the resume fixture is always present and tests the projection being written. Preserve the current strict budget boundary and the generated-only projection.

F18 is the required methodological correction before the lock. The remaining findings are bounded fixture and wording repairs; they do not call for changing the generation arms, sample sizes, threshold record or D16's target.

VERDICT: REVISE
