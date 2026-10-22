# R09 — Study 4 protocol: independent review, round 2

## 1. Baseline and scope

**Baseline:** `main`, HEAD `bf751c92d97a141cc7d171e834aa86e9cf455a13` (2026-10-16 17:09:27 UTC). Reviewed on 2026-10-16. The tracked working tree was clean at the start of this review.

**Recommendation: revise before the lock.** Most round-1 corrections are effective and independently reproducible. W1's regenerated laws and tolerances check out. The remaining substantive issue is W2: the new two-way correction does not, without an additional model, estimate the stated dispersion of rejection probabilities averaged over the fixed 50 prompts. It removes genuine key-by-prompt variation as well as generation noise. Findings F14–F17 concern narrower reporting, fixture, interpretation and resumed-budget issues.

I read the root instructions and complete review orientation, the round-2 request and checkpoint prompt, `RESPONSE_claude_r1.md`, and the requested code diffs against round 1 (`fd37e53985407e5103f76d3b455a3a67c9e2f086`) in the specified order. I then read the revised protocol sections, regenerated inputs and validation, re-screen correction and round-1/D15 log entries. Supporting reads covered the relevant complete functions, Study 1's unchanged two-way estimator, the current and archived pilot arrays, manifests, validation records and log, the earlier memo, and the handoff.

This review is bounded to the round-1 dispositions, the corrections and their consequences. I changed only this memo, committed nothing, downloaded nothing and loaded no model. Python checks disabled bytecode writes and used a 55-second alarm; none approached a minute. The complete validator, input generator and full null-block analyzer were not rerun. I exercised the analyzer's early-return void path with an in-memory injected contract failure, without changing any recorded array. Lock probes likewise used an in-memory fixture, not a production lock or resolution.

## 2. Claims against evidence

### Disposition of F1–F12

| Round-1 finding | Independent re-check | Disposition |
|---|---|---|
| F1: strict-rule pilot prediction | The archived original pilot NPZ in `pilot_law_superseded_r1/` matches its old digest. Re-scoring its tokens gives 41 distinct raw p-values. The old versus strict predicted medians reproduce as 9.765625 → 15.234375 pp, 21.484375 → 25.1953125 pp and 25.1953125 → 29.8828125 pp; the maximum per-key change is 6.25 pp. Every current per-cell pilot p-value also reproduces exactly. | **Resolved.** `PooledLaw` uses `searchsorted(..., side="left")` on p-values, correctly counting `p < t`; zero thresholds give zero power. |
| F2: hook rounding and mixed cache values | The hook self-check passes at h = 0, 1, 2, with exact uniform equality and the key switch. The boundary uniform is still 0.2499999939965537, float32 still rounds it to 0.25, and the new cache correctly returns green. Recomputed flags agree at every scored position in all nine regenerated laws. | **Resolved.** Boolean masks and float64 uniforms have separate stores; no tolerance substitutes for equality. |
| F3: grid, resolution and transitive binding | There are 32 pinned paths. With current real file digests and a virtual resolution, the schema accepts the well-formed fixture and refuses an alternate grid path, `PROMPT.md` as the resolution, and a changed `s3_run.py` digest. An analysis-only tolerance change is refused. The actual seven-unit validation inventory passes the current provenance comparison. | **Resolved for the reported defects.** The runner returns the canonical grid, and the analyzer requires equal content. |
| F4: stale human reference and normalization | All seven input provenance digests checked—grid, production and pilot manifests, model manifest, core, generator and hook—equal the current files. Production arrays pass their manifest loader. The reference function excludes inadmissible logits before normalization and selects the 192 continuation positions. Human repetition means reproduce from the current arrays. | **Binding and normalization resolved.** I traced the likelihood/PPL values to the regenerated record and code; I did not independently rescore model likelihoods. The null arm's matched-window output is still missing from `quality` (F14). |
| F5: W1 uncertainty and interpretation | All three independent 2,000-replicate crossed pilot bootstraps reproduce the saved results exactly, including `max(5 pp, 2 × SE)`. The target and small-cluster limitations are now stated, and laws are cell-specific. | **Statistical correction resolved as a conditional adequacy criterion.** One contradictory failure-reading sentence remains in §10 (F16). |
| F6: shared-prompt dispersion | Both supplied additive examples reproduce: the core example gives mean two-way variance about 0.00152; F9 gives 0.001580324 against planted 0.0016, versus binomial proxy 0.001123204. But an interaction counterexample disproves the claimed general fixed-prompt interpretation. | **Not resolved.** See F13; F14 also identifies the surviving old estimator in descriptive output. |
| F7: failure exclusion and void suppression | Injecting one contract failure into the actual six generation units produces share 1/6, `run_void=True`, all three rule passes `None`, no descriptive/null rows, and only one of the affected arm's two units in its quality table. Passing masks remain in the arrays. | **Resolved in implementation.** The early return occurs before null analysis; failed units are audit data rather than quality-table observations. |
| F8: moment allowance | The rounding example 2.0565777947567527 versus 2.05657779 is accepted; replacing the stored value by 2.0565779 is refused. The analyzer now raises `BodyError` on either failed moment comparison. The supplied validation reports that enforcement path. | **Resolved.** The explicit allowance `1e-8 × max(1, abs(reference))` is appropriate for the pinned nine-significant-digit record. |
| F9: sampler tail loss | The float64 CDF gives three tail selections among the specified seed's 20,000 uniforms. I passed the tail uniforms through the actual sampler and obtained the same indices. For masses `[0,0,0,.5,0,.5]`, uniforms `[0,.49,.5,nextafter(1,0)]` select `[3,3,5,5]`. | **Code resolved.** The validator's statistical tail guard is too permissive to detect the original tail-loss defect (F15). |
| F10: W2 derivation | §6 now gives the cells' own Study 3 dispersion figures, calls both sides heuristic, names the missing slope/threshold/covariance information and disclaims a unique explanation of disagreement. | **Substantially resolved.** §10 retains an incorrect directional interpretation for distinct-rule disagreement (F16). |
| F11: serialized outputs | The added W2 components, W3 moments/covariance/shared-tuple count and shares, abstention index/kind, passing-unit counts/masks, float64 p-values, green shares, null first-prompt p-values and axis metadata are present in the code. Builder computations are named. | **Mostly resolved.** Two remaining output-contract mismatches are F14. |
| F12: predecessor's per-key costs | Rechecked the local PDF text, PDF p.11, by substring: “Change in detection rate from calibration, by key and prefix length”. The operating-point caption is present on the same page. The re-screen and §12 now acknowledge Figure 10 and §IV-H and constrain priority claims accordingly. | **Resolved.** The limited-screen qualification is appropriate. |

### Regenerated input consistency

For each of the nine laws I verified the NPZ digest, the exact key blocks (1,000,401–1,000,408, each with 64 prompts), all six stored p-value vectors against fresh detector scoring of the saved tokens, their sorted JSON copies, and the scored-position hook flags. This verifies all 4,608 saved pilot texts without regenerating any text.

The primary W1 results reproduce as follows; percentages and percentage points have different columns deliberately:

| Prompt cell | Pilot nominal power (%) | Predicted key-median cost (pp) | Cluster SE (pp) | Fixed tolerance (pp) |
|---|---:|---:|---:|---:|
| News | 66.9921875 | 15.2343750 | 2.580873266 | 5.161746532 |
| Wikipedia | 51.1718750 | 20.1171875 | 3.171910006 | 6.343820012 |
| Stack Exchange | 58.0078125 | 25.0000000 | 2.884956902 | 5.769913805 |

Direct Boolean counting of `pilot_p < threshold` agrees with `PooledLaw` for every selected key. The saved bootstrap dictionaries reproduce exactly with seed 927 and 2,000 draws, including their quantiles, not just the rounded SEs. The tolerance rule uses the fixed selected keys' committed thresholds; it uses no evaluation-key generation outcome.

`VALIDATION.json` points to the current `INPUTS.json` digest `39ea1272c8fa20eebdb1df2e95fb1a534afef4355a54df0b89feb553b30748f8` and current grid digest `7a1c88f125f8689a65b0224b9f51e3707814c2f8a1d021fc61279defa3887ce2`. Its recorded successes are consistent with the inspected implementations, subject to F15's distinction between returning an expected class and exercising the claimed branch. Its F7 verifies provenance and the tolerance formula; it does not itself re-score every stored p-value. The independent checks above supply that latter check for this baseline.

The human reference contains 1,000 current-manifest continuations per cell, length 192, zero reported excluded-id tokens and admissible-law PPLs 11.627549, 9.503513 and 8.931099. Its repetition means independently reproduce as 0.0234232804, 0.0295767196 and 0.0575925926. The actual likelihood values remain a traced computation, not a model-free recomputation.

Study 3's inventory remains `c270ab818620c1f3189f83cb3095f1a7ed5b30064c9895f54e4e24b6f6c1733d`, and its lock remains `0e2889287d9d814166213e360766e93097de63401842516e3cb308056c666df6`. All 240 files verify; all 60 evaluation units pass the newly added uint16/shape/count-bound checks. Nothing in Studies 1–3's reviewed code or Study 3's record changed in the round-2 diff.

## 3. Method and statistics

**W1 is now an honest, limited conditional prediction check.** The strict-share identity is algebra under a shared score law; the prospective question is whether a separately generated validation-key/pilot-prompt law predicts the new keys' realized median cost on the production prompts. Separate per-cell laws remove the previous cross-cell extrapolation. Passing a median band still does not establish a homogeneous score law for individual keys, and the revised §6 says so.

D15 supplies a defensible pre-outcome operational tolerance. Twice the estimated crossed-bootstrap SE, with a 5 pp minimum, is more informative than pretending 512 texts are independent. With only eight pilot key clusters it remains a sensitivity-based allowance, not a coverage guarantee, and the realized-cost key interval conditional on the fixed prediction is not a confidence interval for a jointly estimated population prediction error. Those limits are now sufficiently explicit. Equality and abstention endpoints of the strict-share calculation are correct; band overlap remains unresolved.

**W2's target and estimator still differ.** For fixed prompts, a paired key bootstrap does not inherently need a prompt dimension. But the proposed two-way correction subtracts the fixed probability table's interaction residual as well as the generation variance. A key-only bootstrap cannot repair this point-estimand mismatch. If the intended target instead averages over newly sampled prompts, that is a different target and requires accounting for prompt sampling, ordinarily through a crossed analysis. Merely adding a prompt bootstrap to the present fixed-prompt claim is not a solution. The derivation and finite counterexample are in F13.

The observed-zero denominator guard itself works: with an all-zero nominal indicator table, `w2_row` returns zero nominal SD, zero finite resamples, undefined ratio/interval and `unresolved`. The supplied purported zero-denominator fixture does not reach that guard (F15). An intermediate mean power or exclusion of the saturated arm does not establish that a between-key variance is safely separated from zero. Floors and the 90% finite-resample requirement should remain visible limitations of any retained variance-component proxy.

**W3's corrected qualification and moment guard are sound.** It remains a conditional adequacy check on each realized generated-null set, reused across calibration sources, rather than 240 independent replications. The calibration moments remain at L = 256, the E moments use the scored L, and the finite-text term uses the generated null count. The declared serialization allowance is enforced before accepting the relevant rows. This round found no new W3 defect requiring a change to its rule.

## 4. Process

There is still no production lock and no recorded generation under an evaluation key. The recursive JSON search for a `key` field in 23,000–23,999 returned no match; the nine pilot key arrays and actual validation provenance use validation keys. The archived round-1 arrays survive separately and their digests verify. D15 is recorded as Yichen's choice before evaluation-key outcomes, with its alternatives and the conditional use of already known Study 3 thresholds disclosed. The correction to the stale human reference is substantive and is now recorded as such.

The final generated §11 agrees with the current inputs/validation on the quantities checked. From the runner log, the seven wall-time increments are 50 seconds for 96 null texts and 37, 38, 38, 38, 41, 41 seconds for the six 50-text generation units. Thus

`[300 × (37.5 + 38 + 41) + 15,000 × (50/96)] / 3,600 = 11.8784722 hours`,

which rounds to 11.88 hours. The validation output-size projection is `3 × 10,487,891 = 31,463,673` bytes, about 31 MB. The memory lines now record MPS allocation, driver memory, RSS and swap at launch/phase boundaries. They are useful measurements, not a full-run peak guarantee. The new budget check has a resume-accounting weakness (F17).

Some narrative copies still carry superseded operational numbers: the handoff says 28 pinned files, 11.5 h and about 22 MB; the regeneration log paragraph also says about 22 MB. The canonical values are now 32, 11.88 h and 31,463,673 bytes. These copies should be synchronized when resolving this round; they do not invalidate the canonical input files. The log's dated correction of the typed pilot powers is consistent with the actual values above.

No terms-of-use boundary was encountered in this round; no network retrieval or model/data download was performed. The holdout, locked prior studies, abstentions and restricted-law qualifications remain intact. The priority wording is corrected. §10's remaining scientific overinterpretations are F16.

## 5. Independent search

Web access is available, but I did not repeat the optional occupant search in this bounded re-review of same-day corrections. The independent search reported in round 1 is not extended by this memo. I rechecked the decisive local primary-source caption for F12; the revised re-screen appropriately describes its search as limited and does not treat absence as proof of novelty. The claim-stage search remains necessary at its scheduled checkpoint.

## 6. Findings

### F13 — major: the two-way correction does not estimate the claimed fixed-prompt power variance in the presence of interaction

**Evidence.** Protocol §3, line 48, defines the target as the across-key SD of each key's mean rejection probability over the fixed 50 prompts. `s4_core.py:115–124` and `s4_analyze.py:134–156` instead use `s_K² − MS_E/n`, claiming generation noise and key-by-prompt interaction are removed. That interaction is not generally generation noise for this target.

Let `p_ki` be the fixed key-by-prompt rejection probability, `theta_k = mean_i(p_ki)`, and `r_ki = p_ki − theta_k − mean_k(p_ki) + grand_mean(p)`. Assuming independent generation draws conditional on this fixed probability table, direct expectation of the two quadratic forms gives

```text
E[s_K² − MS_E/n | p]
  = sample_var_k(theta_k)
    − sum_ki(r_ki²) / [n (K−1) (n−1)].
```

The generation-variance terms cancel exactly, even with heterogeneous Bernoulli variances. The remaining negative term vanishes under an additive probability model, but not in general. The response's additive shared-prompt example therefore validates a special case, not the stated general conditional estimand. Study 1's unchanged population estimator is not at fault; its interpretation does not transfer automatically to this fixed-prompt target.

A deterministic, model-free counterexample uses K = 100, n = 50: the first 50 keys reject exactly the first 24 prompts; the other 50 reject exactly the last 26. The key means are 0.48 and 0.52. There is **zero generation noise**. The stated target's finite-key sample variance is 0.000404040404 and SD is 0.0201007563. The actual function returns `MS_E = 0.257266543`, raw variance **−0.004741290456** and floored SD **0**. The corresponding equally weighted two-type population variance is 0.0004, also positive.

This is not restricted to probabilities 0/1. Replacing that deterministic table Y by probabilities `p = 0.1 + 0.8Y` gives a true finite-key variance of **0.000258585859**, while the exact expected raw estimate is **−0.003034425892**. A short independent 1,000-table Bernoulli check averaged −0.003012907029, consistent with the derivation. These are mathematical fixtures, not evaluation-key outcomes.

**Inference.** W2 can erase genuine fixed-prompt dispersion in either arm and distort its ratio. Flooring, paired resampling and a finite-resample cutoff do not fix that bias. No prompt resampling is needed merely because prompts are shared if the target really conditions on them; the missing ingredient is an identifiable correction for conditional generation noise, or a narrower target/model.

**Recommendation.** Resolve the estimand before the lock. To preserve the current compute design, I recommend explicitly treating this as a two-way variance-component proxy with a limited heuristic W2 interpretation, recording both the raw component and observed key-mean dispersion, and withdrawing the general claim that it estimates fixed-prompt latent power variance. If that latent variance is essential, justify a model that identifies it or obtain generation replication within key/prompt pairs; an additive-probability assumption must be explicit and tested for sensitivity. If a random-prompt population target is chosen, derive that target and include prompt uncertainty. This is Yichen's pre-outcome design decision. Add a nonadditive fixture like the one above. Leave Study 1's locked code unchanged.

### F14 — minor: the reporting contract still mixes the old dispersion estimator and incomplete likelihood windows

**Evidence.** At `s4_analyze.py:245–253`, descriptive rows still call the independent-binomial `between_key_sd(pi, n_tx)` and put its SD in the unqualified field `power_sd_between`. Only the raw-variance field is explicitly labeled `binomial_proxy`. Protocol §3 now defines between-key SD by the two-way estimator and calls the binomial quantity secondary only; §7's power-table row still promises an unqualified noise-corrected between-key SD. §8, line 117, likewise still says the between-key SD removes the mean binomial variance.

Separately, the newly added `mean_logp_first_192` is populated for watermarked arms, but `s4_analyze.py:306–308` emits only full-length PPL for the unwatermarked arm. Protocol §4 promises comparison of the generations' first-192 and all-256 log-probabilities with the human reference; §7 includes the unwatermarked arm in these diagnostics. The raw null `logp` arrays contain the necessary values, but the promised matched-window null summary is not in `quality` and is not assigned to a builder computation.

**Inference.** A report consuming the advertised fields can label a binomial proxy as the newly defined primary dispersion and compare unmatched likelihood windows for the null arm. These are output-contract issues, not missing raw evidence.

**Recommendation.** After F13's target decision, give every dispersion field and table an explicit estimator label; either compute the selected primary quantity throughout or name the binomial SD as a secondary proxy throughout. Correct §8. Emit the null first-192 mean log-probability, or explicitly register it as a builder computation from the saved null arrays. Check the §7 table against the final serialized schema before locking.

### F15 — minor: two new F9 fixtures do not detect the defects their names claim to test

**Evidence.** Re-running `s4_validate.py:197–198`'s inputs through `w2_row` gives nominal SD **0.0339181840**, observed ratio **1.099970027**, **191/200** finite resamples and interval **[0, 3.892204916]**. Its `unresolved` result comes from overlap with 1. Neither the observed-zero guard nor the fewer-than-90%-finite guard fires. A zero true key component in a simulation is not a zero estimated denominator.

At `s4_validate.py:223`, the tail fixture accepts `abs(tail − expected) < 4 SE + 1e-6`. Here the expected tail is **0.000151932240** and the allowance is **0.000349607695**. Consequently, **zero tail selections also pass**. A sampler regression that keeps the corrected zero/plateau boundary but restores float32 accumulation would pass the tail-loss part. The current sampler itself passed my deterministic tail probes.

The new counterexample tolerance `0.0006` and sampler guard `4 SE + 1e-6` are visible in the pinned code, but not recorded in `VALIDATION.json` as §9's “fixtures use their stated tolerances (`VALIDATION.json`)” wording suggests.

**Inference.** `all_ok=True` does not demonstrate all claimed extreme branches or protection against the original tail-loss defect. This is a validation gap; the inspected zero-denominator guard and sampler are currently correct.

**Recommendation.** Use an actually zero estimated denominator and assert that value, undefined ratio and zero/insufficient finite resamples, not just the class string. Add explicit tests of the 90% finite-resample boundary. For the sampler, assert deterministic tail quantiles or exact seeded outcomes against a separately computed float64 CDF, including a case that fails if accumulation returns to float32. Record fixture acceptance tolerances or point the protocol precisely to their code definitions. Regenerate the validation summary afterward.

### F16 — minor: §10 still overinterprets W1 failure and can reverse the meaning of W2 disagreement

**Evidence.** Protocol §6 now gives the appropriately limited readings, but §10, line 136, still says: “If W1 fails: the cost is not the threshold shift alone” and “If W2 disagrees: per-key calibration does not reduce (or increases) the dispersion of power”. W1 can fail its pass rule because rows are unresolved, and an inconsistent row still does not identify the cause. For W2's distinct rule, an interval **[0.4, 0.6]** is classified `disagree` because it is below the registered band, while it supports a substantial reduction in the measured dispersion quantity. I checked that classification directly.

**Inference.** The proposed future report wording contradicts the corrected readings and, in the distinct example, the sign of the result. Thus the interpretation portions of round-1 F5/F10 are not completely resolved.

**Recommendation.** Align §10 with §6: distinguish unresolved/inadequately resolved outcomes from resolved disagreement; say W1 did not meet the registered conditional prediction criterion; say W2 rejected the rule-specific heuristic and report the observed direction. Do not infer heterogeneity or absence of a reduction from the aggregate pass flag.

### F17 — minor: the new budget stop gives resumed runs credit for work whose elapsed time is omitted

**Evidence.** `s4_run.py:216` resets `t_run` on each invocation. At lines 230–231, `proj_done` sums every preceding expected unit, including reused units, whereas `el_h` contains only this invocation's elapsed time. After resuming with the first two cells' **620 units** complete, the boundary following the third cell's ten new null units uses a projected prefix of **8.643055556 h**, although the newly generated work's projection is only **0.723611111 h**. Three hours spent on those new null units would pass the implemented comparison against 17.286111112 h, despite exceeding twice their projected runtime. Prior wall time is not added for a cumulative-run interpretation either.

**Inference.** The normal uninterrupted-run projection is correct, but the resumed check does not compare time and projected work on the same basis. Repeated restarts can weaken the stated budget protection substantially.

**Recommendation.** Specify whether the stop is per invocation or cumulative. For the former, accumulate projected time only for units generated during that invocation and handle reuse/verification overhead explicitly. For the latter, carry forward measured prior elapsed time as well as completed work. Add a model-free resume-accounting fixture. This does not require generating evaluation-key text.

VERDICT: REVISE
