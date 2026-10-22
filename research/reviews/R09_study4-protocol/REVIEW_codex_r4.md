# R09 — Study 4 protocol, independent re-review, round 4

Reviewer: Codex. Date: 2026-10-16 (UTC).

## 1. Baseline and scope

Baseline: **`b12f13b20411b11fbf2c232b510b10646b1f2e62`**, `main`; the working tree was clean at the start. This review is bounded to F18–F21 and their corrections.

Read `AGENTS.md`, the review orientation in full, and the Round 4 prompt. Then read, in the requested order, `RESPONSE_claude_r3.md`; the changes since `999292312835319ce245c6cdd541c2d39c4a36ec` in `s4_analyze.py`, `s4_core.py` and `s4_validate.py`; the protocol's D17 header and revised §§3, 6, 8–11; `VALIDATION.json`; and the decision log's round-3/D17 entries and dated corrections. Also checked the appended correction to `RESPONSE_claude_r2.md` and the unchanged runner's clock/provenance definitions.

All computations were short and model-free, with bytecode writes disabled and a 55-second alarm per Python process. I reproduced the round-3 experiment against the new row function, all seven current coverage models and the superseded crossed comparison, the bounded-effects estimator fixture, the decision boundaries, the sampler probes/mutants and the budget arithmetic. I did **not** rerun the full validator or analyzer, load a model, download anything or commit. Only this memo was written.

**Assessment:** the key bootstrap repairs the exact centering defect identified in F18, and the seven recorded coverage results reproduce. F19–F21 are substantively resolved. However, the justification that pairing removes a shared key-by-prompt interaction is false for a variance ratio. The current interval still omits material prompt-sampling uncertainty for the retained population target. A nested, fully paired model with the **same additive interaction in both tables** gives only **149/300** coverage. This is F22, the remaining major issue. F23 is a minor coverage-fixture reporting/guard issue.

## 2. Claims against evidence

### The implementation and its centering

`s4_analyze.py:161–164` draws the B × K indices once with `boot_indices`, applies each row of indices to both tables, keeps all prompt columns fixed and recomputes both components. `w2_decide` receives the resulting ratios and implements the registered finite-share and observed-denominator checks. The code, serialized `bootstrap` label and D17 description agree.

For an observed table, let \(a=(K-1)/K\). A key-only resample gives

\[
E_*[s_K^{2*}]=a s_K^2,\qquad
E_*[MS_E^*]=a MS_E,\qquad
E_*[\widehat v_K^*]=a\widehat v_K.
\]

I enumerated all 27 key resamples of the 3 × 2 binary table used in the earlier check: the raw original component is 1/6, and the exact resampling mean is 1/9, agreeing with the factor 2/3 to floating-point precision. The round-3 additive displacement is gone. A common rescaling of the two raw components would indeed cancel in their SD ratio; equivalently, dividing each bootstrap raw component by the same positive factor would not change its floored SD ratio. **This centering identity is not a coverage theorem for the ratio and does not supply the omitted prompt variation.**

The unchanged round-3 reproducer now gives **275/300** covering intervals, all 300 finite, versus 144/300 previously. The median interval endpoints are [0.2074891677, 0.6704009568]. This is a substantial improvement on that model.

### The seven exact-target models

I reproduced the current fixture's model definitions, seeds and calls through `w2_row`, without invoking the validator's main routine. Every generated table pair satisfied `Yc <= Yn`, including the model named `UNPAIRED`. The exact component targets are correct: the mean-zero prompt modulation does not change the key's prompt-averaged coefficient.

| Fixture | Finite intervals / 300 | Covering intervals | Coverage among finite intervals |
|---|---:|---:|---:|
| Ratio 0.5 | 300 | 272 | 0.9067 |
| Ratio 1 | 300 | 278 | 0.9267 |
| Ratio 2/3 | 300 | 280 | 0.9333 |
| Ratio 1.5, nominal key amplitude 0.04 | 228 | 219 | 0.9605 |
| Ratio 0.5, nominal key amplitude 0.03 | 138 | 124 | 0.8986 |
| Proportional prompt modulation of both key effects | 300 | 279 | 0.9300 |
| Different prompt modulation, labeled `UNPAIRED` | 300 | 264 | 0.8800 |

The superseded crossed construction covers **151/300 = 0.5033** on the first model's tables, matching the stored 0.503. All final figures in `VALIDATION.json` and generated §11 are consistent with these checks. I did not independently reconstruct the conductor's separate preliminary comparisons of candidate interval methods; those are reported exploratory evidence in the response, not the current fixture results.

The 0.85 acceptance threshold is transparently described as a gross-failure bound. Passing it is not validation of 95% coverage. Also, the table's denominators are **finite intervals**, not resolved W2 classifications; the current record uses the latter word for the former (F23).

### F19: decision branches and sampler

The boundary now genuinely goes through production. I reproduced both paths:

| Finite ratios out of 200 | `w2_decide` | Counted-wrapper call through `w2_row` |
|---|---|---|
| 179 | unresolved, nonfinite endpoints | unresolved, nonfinite endpoints |
| 180 | agree, finite endpoints | agree, finite endpoints |
| 181 | agree, finite endpoints | agree, finite endpoints |

The wrapper made the expected 402 estimator calls per row (two observed and two per resample), zeroed only the designated nominal bootstrap components, and restored the estimator afterward. A nonfinite observed ratio also remains unresolved when all 200 resamples are finite. The zero-denominator fixture retains its explicit field checks.

All six sampler uniforms now lie in [0, 1); the sixth is 0.999999999999. The sampler and independent Neumaier reference both return `[0, 0, 103, 51935, 141935, 151935]`. The recorded float32 mutants reproduce `[0, 0, 0, 0, 0, 151935]` and `[0, 0, 0, 0, 0, 0]`; each differs from the reference on all three designated tail probes. The acceptance expression checks the valid domain, reference equality, mutant detection and plateau/zero-draw conditions. **F19 resolved.**

### F20: exact bounded planting and corrected descriptions

The current random-effects fixture uses equiprobable bounded effects ±0.08, ±0.12 and ±0.06. Its probabilities lie in [0.24, 0.76], so no clipping approximation remains. Independent recomputation over the specified 400 tables gives:

| Quantity | Recomputed value |
|---|---:|
| Mean raw two-way component | 0.00640146423417852 |
| Monte Carlo SE | 0.00005991906501341 |
| Mean independent-binomial proxy | 0.00611202403628118 |
| Monte Carlo SE | 0.00005997396400499 |
| Exact population key component | 0.0064 |
| Exact proxy expectation | 0.006112 |

The recorded tolerance matches the implemented `3 * SE + 1e-4` checks and the proxy-separation guard. The fixed-table caveat is retained, and the Study 4 wrapper's docstring now correctly states the population target and raw-estimator unbiasedness under the two-way model. The dated log/response corrections preserve the historical entries while specifying the actual prior settings and their clipping. The serialized sampler tolerance now names Neumaier accumulation. **F20 substantively resolved.** Two non-executable comments in `s4_validate.py` still say `math.fsum` and “neither credited nor timed”; these can be synchronized with the corrected executable code and protocol during cleanup.

### F21: resume clock and fresh projection

The revised §§9–10 describe the runner literally: elapsed time begins after model loading, includes prompt loading and reuse verification, and prior units receive no projected-time credit. The runner is unchanged. F10 now assigns `cost_proj = cost` unconditionally and no longer reads a previous `VALIDATION.json` or skips itself when that file is absent.

The current cost gives 0.7375 h for the ten new null units and 8.5458333333 h if 620 reused units were incorrectly credited. Three hours stops the former; equality at twice the projection does not stop, and adding 10⁻⁹ h does. These reproduce the fixture and its new boundary fields. **F21 resolved.**

## 3. Method and statistics

The cancellation of an **additive prompt main effect** is correct: adding the same column effect to every key changes neither the sample variance across key means nor the doubly centered residuals. The population component remains \(\operatorname{Var}_K E_{P,G}[Y\mid K]\), as D16 requires. Neither fact makes a key-only bootstrap generally adequate for that component's population ratio.

Protocol §8, line 121, goes further: “the prompt sample's contribution to the ratio's uncertainty enters only through a key-by-prompt interaction whose prompt-dependence differs between the two tables (the pairing on the same texts removes a shared one).” That assertion is not correct. A common *multiplicative modulation of both complete key effects* can cancel in a ratio. A common *additive interaction* generally does not, because its contribution is relative to different main-effect magnitudes.

The successful prompt-dependent fixture is of the special proportional form: nominal key effect \(A_k(1+D_i)\), method key effect \(0.5A_k(1+D_i)\). The model labeled `UNPAIRED` changes the modulation, but it still uses the same keys, prompts and uniforms and has nested rejections. Different dependence on a shared prompt is compatible with the actual experiment's paired design; pairing does not rule it out.

More directly, consider independent equiprobable signs \(S_k,D_i\in\{-1,+1\}\) and independent uniforms \(U_{ki}\), shared between the two thresholds. Define

\[
P^n_{ki}=0.5+0.2S_k+0.18S_kD_i,\qquad
P^c_{ki}=0.3+0.1S_k+0.18S_kD_i,
\]

and \(Y^n_{ki}=1\{U_{ki}<P^n_{ki}\}\), \(Y^c_{ki}=1\{U_{ki}<P^c_{ki}\}\).

Here:

- The additive interaction **\(0.18S_kD_i\) is identical in both tables**.
- Nominal probabilities lie in [0.12, 0.88], and method probabilities in [0.02, 0.58]; no clipping or invalid probabilities occur.
- \(P^n-P^c=0.2+0.1S_k\) is positive for every key and prompt, so the method's rejection set is always a subset of the nominal set.
- The prompt-averaged key powers are \(0.5+0.2S_k\) and \(0.3+0.1S_k\). Thus the population components are exactly 0.04 and 0.01, and their SD ratio is exactly **0.5**.

This is an admissible paired rejection model at two ordered thresholds: for any key/prompt, a score distribution can assign probabilities \(P^c\), \(P^n-P^c\) and \(1-P^n\) below the lower threshold, between thresholds and above the upper threshold. Its validity does not rely on treating the thresholds themselves as prompt-dependent.

The omitted uncertainty is visible algebraically. Given the sampled prompt signs, with mean \(\bar D\) and sample variance \(s_D^2\), the expected raw component for key coefficient \(\lambda\), averaging over keys and generation, is

\[
E[\widehat v_\lambda\mid D]
=(\lambda+0.18\bar D)^2-\frac{0.18^2s_D^2}{n}.
\]

Generation noise cancels in this expectation. Averaging over prompts recovers \(\lambda^2\), so the point estimator is still correct for the population target. But the conditional expression changes with \(\bar D\), and the changes at \(\lambda=0.2\) and \(\lambda=0.1\) do not cancel in their ratio. Holding the prompts fixed leaves that uncertainty unrepresented.

At K = 100, n = 50, using the actual revised `w2_row` on 300 tables:

| Quantity | Independent result |
|---|---:|
| Finite reported intervals | 300 / 300 |
| Intervals covering the true ratio 0.5 | **149 / 300 = 49.7%** |
| Intervals entirely below / above 0.5 | 91 / 60 |
| Mean raw nominal component | 0.04002201058201058 |
| Mean raw method component | 0.01007645571359857 |
| Median point ratio | 0.4829898933014587 |
| Median interval endpoints | [0.4233386117, 0.5344159087] |

The coverage Monte Carlo SE is about 2.9 percentage points. This failure is not a small-denominator selection effect: every row has a finite interval. The component means agree with their exact population targets. The problem is the omitted prompt variation, not the earlier centering defect or a non-nested pair of tables.

Reproducer from the repository root with `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python` (a few seconds):

```python
import signal
signal.alarm(55)
import sys, json, numpy as np
from pathlib import Path
sys.path.insert(0, 'research/study4')
import s4_analyze as A
w = json.loads(Path('research/study4/grid_v0.1.json').read_text())['W2']
rng = np.random.default_rng(2026101604)
rows = []
for rep in range(300):
    s = rng.choice([-1., 1.], (100, 1))
    d = rng.choice([-1., 1.], (1, 50))
    h = .18*s*d
    pn = .5 + .2*s + h
    pc = .3 + .1*s + h
    assert (pc >= 0).all() and (pn <= 1).all() and (pc <= pn).all()
    u = rng.random((100, 50))
    yn, yc = (u < pn).astype(float), (u < pc).astype(float)
    assert (yc <= yn).all()
    rows.append(A.w2_row(f'R4shared{rep}', 'raw', yn, yc, w))
finite = [r for r in rows if np.isfinite(r['ci_lo'])]
print(len(finite), sum(r['ci_lo'] <= .5 <= r['ci_hi'] for r in finite))
# 300 149
```

This is a check of the claimed uncertainty construction, not a prediction that the unobserved production data will follow this model. It directly contradicts the stated reason for excluding prompt uncertainty under a shared interaction. Recording one milder nonproportional model at 88% coverage does not bound this limitation.

## 4. Process

D17 is recorded as Yichen's choice before the lock. The reviewed changes do not alter the generation arms, grid, sample sizes, Study 3 thresholds, `INPUTS.json`, or locked Study 1–3 code and records. The changes to the Study 4 core are a docstring correction; the runner's six generation-provenance modules are unchanged, consistent with retaining the validation generation record. The full validation's timestamp and new outputs are carried into generated §11.

The bounded checks accessed no holdout data, external service or new literature. No production outcome was used in constructing the counterexample. This review does not repeat the complete earlier generation-timing audit or reopen the earlier agreed findings. The remaining issue can be addressed before the lock, with the implications of a narrower W2 claim or wider uncertainty put to Yichen rather than silently changing the estimand.

## 5. Independent search

No new external search was performed for this bounded round. No new literature quotation or novelty claim is at issue. The statistical finding follows from the local code, explicit conditional expectations and exact-target synthetic tables; no claim is inferred from search absence.

## 6. Findings and recommendations

### F22 — Major: pairing does not remove a shared interaction's contribution to the population variance-ratio uncertainty

**Evidence.** `s4_analyze.py:161–164` fixes the prompt sample in all bootstrap draws. Protocol §8, line 121, says pairing removes a shared key-by-prompt interaction; §6 uses the resulting nominal 95% interval to classify a prediction about the population component ratio. The current prompt-dependent success fixture at `s4_validate.py:240–241` uses proportional modulation of the two key effects. The exact-target example in §3 above instead uses the **same additive interaction** in both nested tables and yields 149/300 coverage, with all 300 intervals finite. The conditional component formula identifies the missing prompt variation explicitly.

**Inference.** F18's particular centering defect is repaired, but its broader requirement—adequate uncertainty for the retained population target—is not yet met. The common `(K - 1)/K` bootstrap centering factor and cancellation of prompt main effects do not establish cancellation of interaction uncertainty. The limitation is acknowledged in part, but its stated restriction to differing/unpaired interactions understates the failure and is mathematically false as written. The fixture named `UNPAIRED` is also still paired in the experimental sense.

**Recommendation.** For the D16 population target, use and validate an uncertainty construction that includes the prompt-dependent interaction contribution while preserving the dependence between thresholds. Add the shared-additive-interaction example to the exact-target coverage checks and remove the assertion that pairing alone cancels it. A construction returning wider intervals or more unresolved rows may honestly reflect the precision of 50 prompts; width alone is not evidence against its validity. I do not certify the conductor's previously tested centered alternative simply from its reported conservative coverage: any selected method needs its own stated assumptions and validation. If Yichen instead prefers retaining the current key-only intervals, make W2 explicitly a conditional/descriptive analysis of a precisely defined prompt-conditioned functional and withdraw the population-confidence interpretation; merely adding another caveat while leaving that interpretation intact is insufficient. Either route requires an explicit protocol correction before the lock, without altering any locked earlier study.

### F23 — Minor: the coverage fixture confuses finite intervals with resolved decisions and can skip its coverage requirement

**Evidence.** `s4_validate.py:257–265` sets `res_` by finiteness of `ci_lo` and labels its length `resolved`. For the ratio-1 model the record says 300 resolved, but the actual W2 raw-side classifications are only **22 resolved** and 278 unresolved; all 300 have finite intervals. At the small denominator, 138 intervals are finite but only 62 rows have a resolved class. Moreover, the coverage requirement is evaluated only when `len(res_) >= 100`; a model falling below that count leaves `cov_ok` unchanged rather than declaring its interval behavior unvalidated.

**Inference.** The numerical coverage fractions reproduce, and finite-interval coverage is a useful diagnostic. The label overstates decision resolution, while the conditional acceptance guard can conceal loss of interval availability in a future regression. The current seven models do exceed 100 finite intervals, so this is not the cause of F22.

**Recommendation.** Report separate counts for finite intervals, unresolved rows due to denominator/finite-share guards, and resolved/unresolved side classifications. State that the coverage fraction is conditional on an interval being available. Require adequate interval availability for the well-separated validation models, and make insufficient samples a failed or explicitly unvalidated coverage check rather than an unchanged success flag; retain the small-denominator unresolved-rate diagnostic separately. Update §11 and the response/log terminology from these typed counts.

F19–F21 do not need another substantive redesign. F22 is the required methodological correction before agreement; F23 is a bounded fixture/reporting repair.

VERDICT: REVISE
