# R09 — Study 4 protocol: independent review, round 1

## 1. Baseline and scope

**Baseline:** `main`, HEAD `fd37e53985407e5103f76d3b455a3a67c9e2f086` (commit dated 2026-10-16 04:09:32 UTC). Reviewed on 2026-10-16. The tracked working tree was clean at the start and remained unchanged during the checks. An untracked `research/study4/s4_manifest.py` appeared during the review; it is outside this baseline and was neither reviewed nor modified.

I read `AGENTS.md`, the complete `research/reviews/REVIEW_ORIENTATION.md`, R09's `PROMPT.md`, protocol §§1–12 and the lock paragraph, and the requested implementation files in the specified order. I read the grid, both manifests, `VALIDATION.json`, the summaries and relevant sorted pilot-law values in `INPUTS.json`, the re-screen, D12–D14 and the subsequent build/validation entries, and design notes §§4–8. Supporting checks covered the imported detector functions, Study 3's threshold/count writer and inventory formula, the calibration-input serializer, the earlier resolutions and gate constraints, the handoff/brief, the pilot records, and `s4_sizes.py`.

**Recommendation: revise before the lock.** The paired study is useful and its available generation records respect the evaluation-key embargo. However, there are reproducible correctness and binding defects, including a W1 prediction error larger than its acceptance tolerance, a hook/detector counterexample, and acceptance of an unpinned grid. The shared-prompt design also needs a defensible interpretation of its uncertainty and noise correction.

I loaded no model, downloaded no files, generated no model text, changed no previous study record, and committed nothing. Local Python ran with bytecode writing disabled; bounded probes used a 55-second limit. The supplied hook, record and core self-checks completed in approximately 0.39, 0.48 and 1.59 seconds, respectively, and reported success. The additional checks below expose cases those tests do not cover. The full validator, input generator and analyzer were not run.

## 2. Claims against evidence

### Information timing and the frozen inputs

The available record supports **no model generation under keys 23,000–23,999 before the lock**. A recursive search, including ignored JSON files, for `"key"` followed by an evaluation-key value returned no match. The design pilot names keys 1,000,311–1,000,312; the probe names 1,000,301; all six validation generation units name 1,000,501–1,000,502. I inspected the `key` arrays in all three pilot-law NPZs: each contains exactly 1,000,401–1,000,408, and each file matches its digest in `INPUTS.json`. No production cells or production lock were present in the reviewed record. `INPUTS.json` contains pilot powers for those validation keys, not evaluation-key powers or levels. This is an audit of available artifacts, not proof that an unrecorded computation never happened.

`s4_keys.power_keys()` exactly reproduces the grid's 100 sorted keys, beginning 23013, 23016 and ending 23992. The first committed key-policy/grid implementation is `0cd6c87`, dated 2026-10-16 02:50:04 UTC, after D14. **The seed predates evaluation-key generation, not all generation:** the design pilot began at 01:38:04 UTC. The narrower chronology is the relevant one and should be used when answering the timing question.

Pairing each selected key's future power with its already committed Study 3 level is sound. The selection is a reproducible uniform subset, thresholds are not fitted to the new watermarked texts, and §2 discloses the conductor's prior access to Study 3. This is a prospective power study conditional on a known null-side record, not a fresh test of Study 3. Choosing δ = 0.5 from two separate validation keys is an acceptable disclosed design choice to avoid saturation; it does not establish optimality, representativeness of those two keys, or power at a deployed strength.

The current production prompt plan independently reproduced 146,054 globally consumed IDs, the manifest's ID digests, and scan positions news 15000–20019, Wikipedia 15578–21650, Stack Exchange 15000–19999. The three current production arrays match their manifest digests. The pilot-first draw followed by the production scan excludes the relevant consumed and pilot sets. **The human-reference part of `INPUTS.json` nevertheless belongs to the superseded production manifest**, discussed in F4.

### Generation and detector equivalence

For a valid detector position, `s1_core.context_ids` starts at zero and applies, for j = 1,…,h,

`cid_j = mix64(cid_(j−1) * C1 + (x[t−j] + 1) * C2 + j)`.

`s4_wm.context_hash` and its batch version use the same predecessor order, uint64 arithmetic and recurrence. Substituting each candidate v into `mix64(cid_h * C2 + (v + 1) * C1)` gives exactly `s1_core.tuple_ids` for that candidate. The first h generated positions use prompt context, whereas the detector invalidates those positions when it receives the continuation alone. This is stated in the hook module and protocol §3 and is harmless for the defined continuation-only statistic; later scored positions have identical contexts.

The **tuple IDs are exact**, but the complete green-flag equivalence is false because the hook cache rounds uniforms before thresholding (F2). The random F1 fixture cannot certify all candidates. Its field `uniforms_equal_on_scored` also means `allclose(..., atol=2e-7)`, not exact equality of uniforms.

At the current settings, the loop uses temperature 1 and no explicit top-k/top-p filter. It computes EOS mass from the unshifted full softmax before zeroing the special/padding IDs, then renormalizes over admissible IDs. KGW adds δ to green admissible logits and samples the shifted softmax. All continuations have 256 generated tokens. This is a **forced-length, restricted-token generation law**; suppressing EOS at every step is not the unrestricted model law or, in general, the unrestricted law conditioned on surviving all 256 steps. W3's null is precisely this implemented unwatermarked law.

The seeding is as stated in protocol §8: PCG64 receives `[unit_seed + batch_offset, 20261016]`; the pilot law additionally uses the specified name hash xor salt as its first seed component. The grid's sampler string omits the offset, although the protocol and code include it. The intended inverse-CDF algorithm is reasonable, but float32 accumulation can erase tail mass (F9).

`logp` records the chosen token's **unshifted admissible-law** log probability, subject to a `1e-45` floor. Calling its exponential average “perplexity under the unshifted admissible model on generated tokens” is accurate. It is not a direct quality measure or the watermarked sampler's likelihood. Human-reference scoring currently uses the full vocabulary rather than the admissible law, and uses 192 tokens versus the generations' 256; those differences matter to comparisons (F4). The Gumbel branch implements the argmax of log(U)/p on positive-probability candidates, with finite-precision/clipping qualifications; there is no production Gumbel generation arm to validate here.

Batch 50 and MPS bfloat16 are compatible with treating the saved arrays as the authoritative realization. That convention does not excuse a mismatched hook or an inaccurately described sampling law. Cache eviction itself only changes recomputation and timing; the float32 representation, not FIFO eviction, causes F2.

### Study 3 binding and stored null levels

I independently re-hashed all 240 files. The inventory is

`c270ab818620c1f3189f83cb3095f1a7ed5b30064c9895f54e4e24b6f6c1733d`,

and the lock is

`0e2889287d9d814166213e360766e93097de63401842516e3cb308056c666df6`.

`s4_record._inventory_digest` uses exactly `s3_manifest.py:57`'s SHA-256 of the sorted `filename:digest\n` concatenation. The lock/grid/`s3_keys` key range agrees, and index i maps to 23000+i. The record and NPZ digest checks, study/mode/lock checks, unit-field check and top-level FIXTURE guard are appropriate. The additional consistent-digest relabel fixture at `s4_validate.py:60–63` actually calls `.cal(...)` after rebuilding the manifest and therefore does exercise the unit-field guard. The earlier relabel fixture alone exercises only the byte-digest check.

Calibration arrays are checked for expected shape, finiteness and nonnegativity; the loader does **not** impose the same shape/finiteness contract on evaluation arrays. I independently checked all 480 fixed/same evaluation arrays for shape, finite nonnegative counts and counts ≤ N_E; they passed. The existing immutable, previously validated record is usable, but a statement that this loader itself checks every array would be inaccurate.

The stored-null axes agree with `s3_run.run_eval_unit`: fixed `(variant, alpha, key)` and same `(source, variant, alpha, key)`. `EvalUnit.null_count` indexes them correctly. Zero thresholds are returned unchanged; strict rejection gives zero power and `abstaining` marks them. No repair is introduced. The four original refusal fixtures plus the fifth semantic fixture provide useful binding coverage, not comprehensive coverage of Study 4's lock (F3).

### Literature checked against the primary record

I rechecked substrings in the local PDF text, counting pages at form feeds:

- AutoMark, `research/literature/txt/2609.37310.txt`, PDF p.42: “a detector that is sound over the key”; p.30: “correcting with 1/β is overly conservative in many cases, costing significant power.” These support the prerequisite and power-cost attribution. App. C's empirical procedure is described on p.29. The protocol appropriately retains the prerequisite and treats the raw-rule multiplier as a numerical arm.
- Genhatharan, `research/literature/txt/genhatharan_nominal_fpr_2026.txt`, PDF p.2: “a median two points of detection at 512 tokens”; p.11, Figure 10(b): “Change in detection rate from calibration, by key and prefix length.” This supports the pricing attribution but also shows that the predecessor contains a per-key cost display, not merely one summary line (F12).

The broader no-theorem/no-power-guarantee/no-priority restrictions and the shorter-length qualification are present. I did not newly verify every peripheral citation or the Nemecek PDF; the earlier resolution already carries that PDF check forward to the claim gate.

## 3. Method and statistics

### W1

For strict `p < t`, power is `P(Z > z(t))`. With the ordinary CDF `F(x)=P(Z≤x)`, the cost has the proposed positive direction `F(z(t_k))−F(z_alpha)`. A lower p threshold usually produces a higher z threshold and a positive cost. An abstaining key has predicted cost equal to nominal power. The code instead uses the strict-left empirical CDF, producing the wrong endpoint for discrete scores (F1).

W1 is a genuine prospective prediction in the limited sense that a separately generated validation-key pilot law is applied to new evaluation-key texts and prompts. Under the assumed common score law, the formula follows immediately from thresholding; the nontrivial question is whether that law transfers. A successful median comparison does not establish key-homogeneity or accuracy for individual keys. A failure can reflect prompt-law transfer from news to Wikipedia/Stack Exchange, pilot sampling error, discrete endpoints, or key-dependent generation; it cannot identify the latter cause alone.

The three classifications and the “at least two consistent, none inconsistent” aggregation match the grid. Boundary overlap is unresolved. The displayed tolerance is a materiality choice, not a calibrated error rate. Its precision justification needs correction for the eight-key, 64-shared-prompt pilot and the target of the bootstrap (F5).

### W2

The implemented floor, paired index resampling, and zero-denominator handling match the stated rule. A zero observed denominator is unresolved. Fewer than 180 finite ratios among 200 resamples is unresolved; at exactly 180, the percentile interval is computed from the finite ratios only. Raw-rule agreement requires an upper endpoint strictly below 1; disagreement a lower endpoint strictly above 1. Distinct-rule agreement requires containment in [2/3,3/2], disagreement disjointness. The overall threshold is five of six agreeing with none disagreeing. These are descriptive adequacy rules, not a jointly calibrated hypothesis test.

The binomial subtraction is justified for independently sampled binomial proportions. It is not automatically the appropriate correction for 50 fixed shared prompts (F6). The denominator can be close to zero at intermediate *mean* power, so exclusion of the saturated arm does not solve the issue. In the eight-key pilot law, applying the current correction to nominal power at 256 tokens gives raw SD 0.10699 and distinct SD 0.05084; for distinct, observed variance is 0.006348 and the subtracted term is 0.003763. This is evidence of a substantially noisier dispersion estimate under distinct, not a precise estimate of its population SD.

The 1.36 pp raw-null figure is the Study 3 report's median across 20 units (both tokenizers), not each of the three proposed Qwen cells. The record gives the following h=1 nominal figures at alpha=0.01:

| Qwen cell | Raw SD (pp) | Distinct SD (pp) | Distinct binomial SD benchmark (pp) |
|---|---:|---:|---:|
| news/en@256 | 1.9351 | 0.6143 | 0.1052 |
| wikipedia/en@256 | 2.9194 | 0.6162 | 0.1056 |
| stackexchange/en@256 | 1.2809 | 0.4427 | 0.1057 |

Thus the distinct nominal dispersion is not near the finite-text floor in these cells. Smaller/null median threshold shifts can motivate an exploratory “little change” hypothesis, but do not derive a ratio-of-power-SDs band or a unique explanation of disagreement (F10).

### W3

The block is correctly 3×2×2×10×2 = 240 candidates. `w3_fields` checks theory share ≥0.75, no prediction flag and positive predicted SD; the interval and band classification match the protocol. The aggregation correctly requires at least 30 resolved and at least 80% of those consistent, with overall candidate/eligible/resolved counts. Rows provide the axes needed for the builder's stratified counts.

`null_counts` implements strict sorted-column counts with the same axes and thresholds as Study 3. The predictor uses E moments from the generated null tokens at the selected h/rule/L, C moments from each calibration prefix at L_C=256, and their cross-covariance. N_E is the concatenated null count, hence 5,000 in production, not 10,000 or 50. C moments are indeed recomputed; the claimed comparison tolerance fails on the already available validation data (F8).

This is an honest **conditional out-of-sample adequacy check on a new text law**, using a frozen predictor with key-free moments from the realized E set. It is not 240 independent replications, a predictor made without seeing the new texts, or an unconditional guarantee over new prompt samples. All source rows within a cell reuse the same E set and the same keys, with nested calibration prefixes. The 80% pass fraction should remain a registered descriptive criterion with its counts, not an effective sample size or a binomial significance statement. Passing W3 says nothing about ineligible rows, and does not guarantee nominal validity on generated null text.

### Compute, precision and report feasibility

The validation log's unit-boundary wall times reproduce the projection:

`[300×(37 + 36 + 39.5) + 15,000×(49/96)] / 3600 = 11.501736 hours`.

There are 900 watermarked units and 30 null units. Null timing is extrapolated from a 96-text validation unit using batches 50+46, rather than a complete production 500-text unit, so 11.5 h is a reasonable planning estimate, not a measured full-run duration. `s4_sizes.py` reproduces 12.7 h using the earlier batch-32 pilot rates. The JSON projection is `7,324,108×3 = 21,972,324` bytes; rows scale with cells rather than K. Arrays are stored separately, so this projection is not total record storage or production analyzer time.

The per-key binomial SE bound is 0.07071; at power 0.7 it is 0.06481. The planning mean SEs at K=100,n=50 are 0.0082 and 0.0136 for assumed between-key SDs 0.05 and 0.12; the corresponding normal-approximation relative SD SEs are 0.190 and 0.092. Those calculations reproduce, but depend on the noise and independence model. They do not validate 95% coverage for a floored variance ratio, or precision across new prompts. Two hundred bootstrap replicates give only about five replicates in each nominal 2.5% tail. “Twice as precisely” for doubling n in the planning option name should mean halving the binomial variance, not halving its SE.

Reference scoring in batches of four and explicit MPS cache release are sensible memory reductions. `lg.float()` still creates a temporary full-vocabulary float32 tensor for that smaller batch; it does not eliminate such a tensor altogether. The runner's 3.02 GB RSS is a CPU-process measurement, not total unified/Metal memory. The earlier probe records driver usage separately, and the log itself documents RSS missing a swap problem. Record MPS allocated/driver memory and swap at the actual launch and phase boundaries if the report will make a memory-feasibility claim. The budget stop is currently a procedural requirement: the runner logs phase boundaries but does not implement the 2× projection stop.

The underlying token, flag, logp and EOS arrays are largely sufficient for the paper and a second scoring implementation. Sampler uniforms are unnecessary for the specified statistics; saving them would not make MPS generation reproducible. Keep the grid/axis maps and failed-unit mask with the results. Exact scores should be recomputed from tokens when strict threshold decisions matter: the convenience `pvalues|…` arrays are float32. Several promised aggregate diagnostics still need explicit serialization or a pre-specified builder computation (F11).

## 4. Process and consistency

D12–D14, the current grid and the protocol agree on the model, arms, sizes, prompt lengths, generation lengths and excluded Gumbel generation arm. The holdout remains sealed and `final:false`; the current prompt plan goes through the open-partition data layer. I made no external change or data/model acquisition. The source screen reports its queries and gaps, including partial OpenAlex inspection and abstract-only readings. Its absolute “No occupant” wording should be understood as “none found in this limited screen.”

The principal carried-forward requirements are present: exact threshold-to-key binding, abstentions retained without repair, generated-null transfer measured explicitly, the multiplier's prerequisite and distinct/raw qualification, no claim of calibrated short-length operating points, and bounded settings for power statements. The inference and predecessor issues below still require narrower wording.

I enumerated numeric literals in `s4_core.py`, `s4_run.py`, `s4_analyze.py` and `s4_gen.py` and traced the operational settings and rule constants to the protocol/grid. The pass counts, bands, finite-bootstrap fraction, seed salt, lengths and principal sizes agree. The claim that §9 states **every** tolerance is too broad: the body accepts logp up to `1e-6`, generation floors probabilities at `1e-45`, the predictor clips thresholds at `1e-300`, and the hook fixture uses `2e-7`. Implementation/numerical tolerances should be distinguished from scientific materiality thresholds. Fixture-only constants need not be presented as study settings. The nine-significant-digit serialization tolerance issue is substantive (F8).

`INPUTS.json`'s manifest and grid provenance is stale relative to the final inputs. F7 verifies pilot-array digests and summary lengths but does not enforce that provenance. Consequently, `all_ok:true` is not evidence that every frozen-input relationship is consistent. The log's statement that the prompt-cache correction touched no scientific input also needs qualification: the human reference is a promised study input.

## 5. Independent search

Web access was available. I issued three general searches with `after:2026-10-13` for (i) watermark/per-key/power/calibration, (ii) watermark/human/generated/null/calibration/threshold, and (iii) watermark/dispersion/power/keys; then three arXiv-restricted searches bounded by `after:2026-10-13 before:2026-10-17` for calibration/power, across keys, and human/null/threshold. The arXiv-restricted searches returned no results. The general results included older or tangential material, not a verified new occupant in that interval. Search indexing and date filters are incomplete; this is not evidence of novelty.

I also read the public [Genhatharan repository README](https://github.com/nisaharan/when-nominal-false-positive-rates-fail), which confirms the calibration-pricing account and its development-screen qualification. The decisive additional comparison came from the already local PDF, especially §IV-H and Figure 10 (F12). I did not repeat OpenAlex/Semantic Scholar citation enumeration, retrieve new PDFs, or circumvent an access restriction. The broader search also surfaced the already known [Xie et al. conformal framework](https://hdsr.mitpress.mit.edu/pub/ifxlo12v/release/2), published in February 2026; it is not new work since the cutoff.

## 6. Findings

### F1 — major: W1 includes tied scores that the measured power excludes

**Evidence.** `s4_core.py:104–113` uses `searchsorted(..., side="left")` and returns `1−cdf(z(t))`, i.e. P(Z≥z(t)). `power_count` and the entire Study 3 threshold contract use strict p<t, hence P(Z>z(t)). The comment “continuous scores: ties immaterial” is false for the KGW count statistic and particularly the raw L=256 lattice. A minimal exact-roundtrip fixture, `PooledLaw(norm.isf([.01,.01,.001])).power_at([.01])`, returns 1 instead of 1/3.

Using the actual frozen primary pilot's raw flags to reconstruct its 512 p-values and the 100 selected keys' committed diagonal conformal@5000 thresholds, I obtain:

| Cell | Current predicted median cost | Strict-p empirical prediction | Difference |
|---|---:|---:|---:|
| news/en@256 | 9.765625 pp | 15.234375 pp | 5.468750 pp |
| wikipedia/en@256 | 21.484375 pp | 25.1953125 pp | 3.7109375 pp |
| stackexchange/en@256 | 25.1953125 pp | 29.8828125 pp | 4.687500 pp |

All 100 predictions change in each cell; the largest individual change is 6.25 pp. These are pre-lock pilot-law predictions, not new evaluation-key outcomes.

**Inference.** This can change W1's verdict at the registered 5 pp tolerance. The Gaussian self-test misses the discrete endpoint defect.

**Recommendation.** Use the strict empirical p-tail directly, or the right-inclusive z CDF with a verified roundtrip convention; update the formula's CDF definition and add lattice/tied-threshold, nominal-equality and abstention fixtures. Recompute the pilot-law prediction checks before locking.

### F2 — major: the float32 hook cache violates the exact detector contract

**Evidence.** `s4_wm.py:69` casts hash uniforms to float32 before `kgw_green`; the locked detector compares float64 uniforms. At V=151936, validation key 1000123, h=1, previous token 70 and candidate token 104474, the locked uniform is **0.2499999939965537**. The cache rounds it to **0.25**. The detector marks the candidate green and the generation hook marks it nongreen. Both token IDs are within the vocabulary. This was found by a sub-second model-free calculation.

**Inference.** The context/tuple derivation is correct, but the claimed equality for every candidate and scored position is false. A selected boundary candidate can create a contract failure; unselected misclassified candidates also change the sampling distribution without being detected by the saved chosen-token flags. The 5% exclusion allowance is not a repair for a known systematic implementation mismatch.

**Recommendation.** For KGW, cache the exact boolean comparison computed from the float64 hash uniforms, or retain float64 uniforms. Add this boundary case and a cache-eviction/key-switch equivalence fixture. Describe the existing uniform comparison as approximate unless exact equality is actually used. Revalidate affected inputs without changing Studies 1–3.

### F3 — major: lock verification does not bind the configuration actually used, or all live dependencies

**Evidence.** `s4_run.verify_lock` hashes the canonical files, but separately reads its caller's `grid_path` and never requires that path/content to equal the locked grid. On a disposable scratch copy with a synthetically well-formed lock, I passed an alternate grid changing the first arm's δ to 9 and W1 tolerance to 99 pp; verification accepted and returned those values. In the analyzer, `load_inventory` verifies a canonical grid but continues using the caller-supplied dictionary. An analysis-only W1/W2/W3 change need not alter generation provenance, so it can pass that gate while changing a reported rule.

The review check accepts any path beginning `research/reviews/R09_`. A scratch lock naming R09's **PROMPT.md**, with its correct digest, was accepted as the resolution. Finally, the analyzer imports `s3_run.variant_names` and reads Study 3's grid and `INPUTS.json`, none of which is in the 28-file set. Although the Study 3 lock is pinned, `Record` verifies its digest, not the current hashes of these dependencies. Their current bytes do match the Study 3 lock; the defect is failure to enforce that relation later.

**Inference.** A valid lock does not yet uniquely determine the run/analysis performed. Hashing a lock document is not recursive verification of the files it lists.

**Recommendation.** Require the actual supplied grid to be the canonical locked file, pass the verified grid forward, and reject differing analysis dictionaries. Require the exact R09 resolution path. Pin the remaining executed/read dependencies or verify them through the existing Study 3 lock without changing that lock. Add alternate-grid, analysis-only-grid-change, wrong-review-file and transitive-dependency mutation fixtures.

### F4 — major: the human reference is bound to the superseded prompt cache

**Evidence.** `INPUTS.json.prompts_manifest_sha256` is `46f3c50a…`, exactly the digest of `prompts_manifest_superseded_pilot_overlap.json`; the current manifest is `fe26dedd…`. `s4_inputs.py:72–76` scores the first 1,000 rows of the then-current production cache. Comparing the preserved arrays, the first-1,000 news set loses three texts and gains three; Wikipedia loses one and gains one. Their row order also changes from the first removed pilot-overlap onward. Stack Exchange is unchanged. The first 50 rows happen to be unchanged in all three cells, which protects the watermarked-prompt selection but does not repair the declared 1,000-text reference. F7 never checks this manifest relationship.

The reference also uses full-softmax log probabilities (`s4_gen.py:125–129`), while generated logp uses the admissible-law normalization (`:79–98`). The protocol presents the human reference beside those generated perplexities without clearly separating the normalizations.

**Inference.** The frozen reference is not the reference the protocol names, and its provenance cannot currently be independently reproduced from the current input manifest. The normalization difference further limits an apparent quality comparison.

**Recommendation.** Regenerate the reference for the current prompt manifest, or explicitly bind and describe the preserved superseded reference as a different fixed reference; do not just rewrite its digest. Enforce input provenance in validation, with a documented migration for historical grid-only changes. Use matching likelihood normalization/window conventions for direct quality comparisons, or clearly label the two quantities and their limitations. No evaluation-key generation is required to fix this.

### F5 — major: W1's pilot-precision claim and failure interpretation exceed the design

**Evidence.** Protocol §8 treats the pilot mass error as a binomial share over 512 texts, and §7 promises an ordinary text bootstrap. The 512 observations are actually eight keys crossed with the same 64 prompts; `INPUTS.json` shows substantial per-key mean differences. An independent diagnostic using the corrected strict-tail prediction, 2,000 resamples and seed 927 gives ordinary flattened-text SEs of approximately **1.60, 1.94, 2.03 pp**, versus **3.13, 3.36, 3.53 pp** when resampling the eight key clusters and 64 prompt columns independently (news, Wikipedia and Stack Exchange thresholds, respectively). This small-cluster bootstrap is a sensitivity diagnostic, not a coverage guarantee.

The actual W1 key bootstrap resamples realized costs but holds the selected keys' predicted median fixed (`s4_analyze.py:125–126`). The protocol does not distinguish inference conditional on that fixed prediction from inference for a population prediction error. Moreover, only news prompts supply the pilot law, whereas two primary rows test different prompt cells. Protocol §6 says a failure means “the key's own watermark strength” sets the cost; §10 repeats that causal reading.

**Inference.** The 5 pp tolerance is not justified as a calibrated allowance for the relevant pilot uncertainty. Failure is not diagnostic of key heterogeneity alone, and passing one median is not evidence that individual keys share a score law.

**Recommendation.** State the conditional/population target explicitly. For population prediction error, use an appropriate paired key statistic and account for pilot key/prompt clustering; for a fixed-pilot adequacy criterion, label it as such and report the omitted uncertainty. Keep or revise c as Yichen's pre-outcome materiality choice, with the actual sensitivity evidence. Replace the unique failure explanation with the competing explanations, including cross-cell law transfer. Do not infer homogeneity from a median pass.

### F6 — major: W2's binomial correction is not a known-noise correction for fixed shared prompts

**Evidence.** `between_key_sd` subtracts `mean(pi_hat*(1−pi_hat)/(n−1))`. For fixed prompts, let a key's prompt-specific rejection probabilities be p_i, their mean p, and generation variance `V_gen = sum p_i(1−p_i)/n²`. Then

`E[pi_hat(1−pi_hat)/(n−1)] = V_gen + s_prompt²(p_i)/n`,

where `s_prompt²` is the sample variance of the prompt-specific probabilities. Thus the code subtracts prompt heterogeneity in addition to the generation noise. For example, with n=50, key means 0.5±0.04 and 25 prompt offsets each of −0.3 and +0.3, the true between-key variance of the fixed-prompt mean is 0.0016. The expected observed variance is 0.004768, but the expected subtracted term is 0.005004735: the expected raw correction is negative despite positive true between-key dispersion. This is a mathematical counterexample, not a model outcome.

If instead the target averages over a fresh random prompt sample, sharing the same prompts across keys creates cross-key dependence that the current independent-binomial correction and keys-only bootstrap do not address. F3's planted test uses independent binomial counts, so it does not validate the actual sampling design.

**Inference.** The numerator and denominator can be biased downward by different amounts. Flooring and the 90% finite-resample rule prevent some numerical claims but do not correct this estimand mismatch.

**Recommendation.** Define whether the target conditions on the 50 prompts. Derive and validate a correction/uncertainty procedure for that design, or explicitly downgrade the current quantity to a binomial-reference proxy and limit W2's interpretation accordingly. A crossed key/prompt analysis is relevant for a random-prompt target; replicates or a clearly justified model are needed to separate conditional generation noise from fixed-prompt heterogeneity. Add shared-prompt/heterogeneous-prompt fixtures, including a positive true SD near the correction floor. Any size or design change is Yichen's decision before outcomes.

### F7 — major: contract failures are not excluded from every table, and a void run still receives rule verdicts

**Evidence.** `s4_analyze.py:188–206` records a failed hook contract but still accumulates that unit in `quality` and serializes its counts/p-values. Later masks exclude failures from power descriptive rows, W1 and W2, but not the quality table. At `:208–210` the code only sets `run_void`; it proceeds to calculate all three rule results and `main` prints their pass values. The existing flipped-flag fixture records `run_void=True` for one failure among six units yet accepts completion of the entire analysis. It does not assert suppression of rule reading or quality exclusion.

**Inference.** This contradicts §9's “excluded from every rule and table” and the instruction that no rule is read on a void run. A run with concentrated failures can also leave empty valid-key blocks and fail in quantiles before producing a useful integrity report.

**Recommendation.** Make the gate operational: return an integrity-only result or explicitly suppress all scientific verdicts when the failure share is greater than 5%; filter every promised scientific/quality summary consistently for nonvoid runs. Retain failed raw arrays only as clearly marked audit evidence. Add fixtures below, exactly at and above the 5% boundary, including an empty valid-key block and assertions on serialized results, not just the boolean flag.

### F8 — major: the required calibration-input tolerance already fails, but validation calls it successful

**Evidence.** Protocol §§6 and 9 require absolute differences ≤1e-9. The generated §11 and `VALIDATION.json` report maxima 4.756752769e-9 for rho and 4.993008007e-9 for sigma². I reproduced both by recomputing calibration moments alone:

- Qwen Gutenberg@1024, h=0, raw, C2000: rho 2.0565777947567527 versus stored 2.05657779.
- Qwen Wikipedia/en@1024, h=2, raw, C2000: sigma² 1.177161825006992 versus stored 1.17716183.

Study 3's `s3_inputs.clean` serializes floats with **nine significant digits** (`s3_inputs.py:36–49`). The analyzer records differences but does not enforce a threshold, and F4 does not include those differences in its success condition. The single news/distinct self-test happens to pass a tighter tolerance.

**Inference.** This is consistent with serialization rounding, not evidence of a changed calibration law. Nevertheless, a literal report implementing the registered tolerance cannot pass on the reviewed inputs.

**Recommendation.** Compare at the pinned record's declared precision, or pre-register a justified scale-aware rounding allowance and enforce it on all prefixes. Include a genuinely altered-moment refusal fixture. Update the prose, validation and generated §11 consistently; leave the locked Study 3 record untouched.

### F9 — minor: float32 CDF accumulation silently removes admissible tail probability

**Evidence.** `_sample_rows` uses `np.cumsum(p, axis=1)` without a higher-precision accumulation dtype. For a float32 row with one leading mass approximately 0.999848065 and 151,935 remaining masses of 1e-9, the float64 sum is approximately 1.000000003, but the float32 CDF remains at 0.999848068 after the first token. Multiplying the uniform by this terminal CDF does not restore the erased tail: the function always selects the first token, discarding total tail mass approximately 0.000151935. With leading zero-probability IDs, an exactly zero RNG draw also selects a zero-mass entry under the current boundary convention.

**Inference.** The implementation has no explicit truncation, but its numerical sampler is not an accurate inverse CDF of the supplied law in this legal case. I did not measure this error on model logits, which are not retained, so I do not claim a production effect size.

**Recommendation.** Accumulate the CDF in float64, use a boundary convention that skips zero-mass plateaus, and add deterministic tail/zero-mass fixtures. State the logp/probability floors and the small positive-logp tolerance in the numerical contract, or remove them where unnecessary.

### F10 — minor: W2's stated derivation and mechanistic reading need narrowing

**Evidence.** Protocol §6 says distinct nominal null dispersion is near the finite-text floor, contradicted by the three cell-specific comparisons in §3 of this memo (roughly 4.2–5.8 times their binomial SD benchmarks). The raw 1.36 pp number is a broader median. Neither a null-SD comparison nor a small median threshold shift determines the ratio of two power SDs. Power-curve slopes, threshold noise and covariance with watermark strength also matter. The protocol's raw-rule disagreement reading assigns dominance to watermark-strength heterogeneity without identifying those alternatives.

**Recommendation.** Give the relevant cells' evidence and label both sides as pre-stated heuristic predictions under explicit assumptions. A disagreement rejects that predictive account; it does not identify a unique cause. Retain the mechanism diagnostic as descriptive association, not an identified variance decomposition or causal explanation. Do not turn near-zero denominators or unresolved rows into evidence of equalized power.

### F11 — minor: complete the promised-output contract before freezing the analyzer

**Evidence.** The raw corrected variance is computed but dropped from both `w2_row` and `descriptive_rows`, despite §3/§9 saying it is recorded. W2 saves only nominal `mean_binomial_var`, although §6 promises both noise terms. Fixed null rows omit `theory_share`; Gumbel rows have no predictor (which needs an explicit N/A label). Successful hook-contract counts are not serialized, only failures. The W3 moment/covariance and full predictor diagnostics are computed and discarded, leaving mean/SD/theory share and absolute consistency differences. The mechanism's per-key green shares and the first-50 null per-prompt scores are not in `results_arrays.npz`; they remain recoverable from the committed raw arrays.

**Inference.** The raw record largely supports the promised report, but the table's blanket analyzer/array-source description is incomplete. The builder must not improvise estimands after outcomes, particularly “share of between-key variance explained,” nor mistake floored zero for an observed zero variance.

**Recommendation.** Serialize both raw variance/noise components, successful contract counts and sufficient W3 diagnostics; supply explicit null predictor N/A labels and abstention counts, including positive-index zeros. Specify the builder's access to raw token/flag arrays, axis metadata, failure masks and exact mechanism/pairing formulas now. State which diagnostics are derived by the builder and test a synthetic inventory against the complete §7 checklist. Record actual runtime/library and MPS-memory metadata if those enter reproducibility or resource claims.

### F12 — minor: the nearest predecessor already reports per-key costs and operating points

**Evidence.** The re-screen calls Genhatharan's pricing a “one-line” or median comparison and describes adding the per-key distribution. The already local paper, §IV-H on PDF p.9 and Figure 10 on p.11, applies previously frozen thresholds to stored own-key watermarked scores, shows each key's before/after operating point, and plots detection-rate changes by key and prefix length. The screen read the README, not that section.

**Inference.** The stronger contribution here is the expanded paired study and prospective predictive checks, not the existence of per-key calibration-cost or operating-point measurements. The conjunctive W1–W3 question may remain unoccupied in the located record, but the component-level comparison currently understates the nearest work.

**Recommendation.** Cite §IV-H/Figure 10 explicitly and update the comparator table and contribution wording to distinguish the 100-key committed-record study, methods/settings, prediction tests and generated-null transfer. Preserve the no-priority-on-pricing restriction and describe search absence only within the recorded coverage.

The next review should verify the corrected draft and refreshed validation at a named commit before the lock. These recommendations do not authorize any change to Studies 1–3, any evaluation-key generation, or the lock itself.

VERDICT: REVISE
