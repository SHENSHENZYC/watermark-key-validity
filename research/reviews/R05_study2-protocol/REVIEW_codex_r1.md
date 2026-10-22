# R05 — Study 2 protocol — Codex round 1

Date: 2026-10-11 (America/Chicago; verification continued on 2026-10-12 UTC).

## 1. Baseline and scope

Baseline: `main` at **`54a2c65af7d9dfa45b033f99a031c87fdd62a367`**. The working tree was clean when this review began. I recommend **REVISE before the lock**: the inventory gate can silently lose a live cell or accept contradictory rejection counts, and the language-disparity calculation has two substantive errors. These are implementation defects, not evidence against the research question or evidence that production outcomes have been inspected.

I read the root `AGENTS.md`, the full review orientation and R05 prompt; Study 2's full protocol, grid and seven scoped modules, plus its fill script; the manifest, validation fixtures/timings/projection/power summaries and key-free input structure and chains; the relevant imported Study 1 implementation and protocol §§3, 6, 9; the audit's eligibility table and seal implementation; the gate's constraints 1–16; the Milestone 3 decision-log entries, current handoff and re-screen. I inspected the validation's per-cell power rows programmatically rather than reproducing the large JSON verbatim. Study 1's results and the R02 corpus verdict were not reopened.

Verification used short, read-only Python computations, metadata, token **ids**, hashes, Git history, retained synthetic validation records and small synthetic counterexamples. In-memory substitutions tested malformed records without editing their files. No raw corpus text, model weights, production-key score, study run, full validator or inputs pass was read or run. No file other than this memo was changed; nothing was committed or downloaded. The retained validation results are evidence I inspected, not a claim that I independently reran its long fixtures.

## 2. Claims against evidence and derivations

### Literature and scope

Substring checks in the existing extracted texts support the protocol's restrained positioning:

- `research/literature/txt/2609.37310.txt`, PDF p.3: “a specific deployed key can still exhibit a high false positive rate.”
- `research/literature/txt/2506.16349.txt`, PDF p.27: “if similar effects can be observed in LLM watermarking.”
- `research/literature/txt/2509.24368.txt`, PDF p.21, Table 2: across-key SDs 1.2%, 0.3%, 0.1%; sampled maxima 17.0%, 1.7%, 1.1%.
- `research/literature/txt/2308.00113.txt`, PDF p.7: “S ∼ Γ(T, 1)”, supporting the ideal exponential-score sum's Gamma law.
- `research/literature/txt/textgrain_openai_2026.txt`, PDF p.6: “A ﬁxed deployed key and ﬁnite precision arithmetic require empirical calibration checks”.

These do not establish this project's priority, and §12 correctly claims none. The protocol separates mean-score identities, a distributional approximation for levels, empirical measurement and future remedies. Its use of “deployed-style” is appropriate: splitmix64 independent colouring is a stated surrogate, not a reproduction of every published KGW implementation or a deployed service's PRF.

### Predictor and identities

For independent centered scores with variance one, the Gumbel implementation correctly uses `w_iu = n_iu/sqrt(M_i)`, `V_i = sum_u n_iu²/M_i`, and document-averaged weights `wbar`. Thus

`Var_K(zbar) = sum_u wbar_u²`,

`rho_bar = [N_eff Var_K(zbar) - mean_i V_i]/(N_eff - 1)`,

and `sigma_model² = mean_i V_i - rho_bar`. The mean offset is zero because the ideal score has mean one. These are second-moment statements; the common-factor representation is an additional assumption, as disclosed.

Given a shift `d`, write `p_i(d) = normal_sf((tau_i-d)/sigma)` and `a(d) = mean_i p_i(d)`. The implemented variance is correctly

`Var_d(a(d)) + E_d[mean_i p_i(d)(1-p_i(d))]/N_eff`.

The unique-threshold frequencies in `mixture_general` preserve the document average, including variable retained counts. At zero shift variance it becomes a point mass and leaves the correct independent-residual floor; with both variances zero it is deterministic. At zero residual variance its **discrete-node** calculation is correct, but Gaussian quadrature does not thereby become an exact Gaussian tail calculation (F6).

I independently compared the general Gaussian form with the saved closed-form predictions at **all 6,120 independent KGW cell/alpha combinations for N = 10,000**, using only the saved moments. The largest absolute SD difference was **2.086e-13**; none exceeded 1e-9. This is stronger evidence for the actual input regime than the retained validator's one synthetic chain, and it bounds the practical consequence of F6 for those cells. The registered KGW decision still uses Study 1's closed form.

For the simulated shift, let `v_id = var_unit * sum(wbar_z²)`. The heavy-plus-Gaussian draw has variance `v_id` under its simulation law. Multiplication by `sqrt(rho_bar/v_id)` therefore gives variance `rho_bar` **in expectation over that simulation**, not exactly in the finite B-draw sample. The retained variance ratio 1.01436 is consistent with this distinction. This is a reasonable moment-matched **shape diagnostic**: it retains the realized weights' heavy-tuple shape while changing its scale to the population-shift estimate. It is not the exact law of a population shift, removes no higher-order sampling effects, retains Gaussian residuals and a common-factor structure, and is not a causal decomposition of prediction error. Any reported improvement should be larger than plausible simulation/subsample noise before being attributed to skew or discreteness. The protocol largely makes these limits clear; “simulates the shift's exact across-key law” in §1 should be read with, and preferably qualified by, §3's heavy-tuple/remainder/rescaling definition.

The Gamma threshold `(Gamma.isf(alpha, M)-M)/sqrt(M)` is the correct transformation. Under **ideal independent continuous uniforms**, distinct tuples within each fixed text yield an exact Gamma(M,1) sum, so its conditional-on-that-text key-mean rejection probability is alpha. Averaging across texts preserves alpha even if texts share tuples. Raw repetition does not have that Gamma null law. The actual 53-bit uniforms and float32 score storage are numerical surrogates, so “exactly alpha” belongs to the ideal null model, not an exact finite-precision theorem about the hash.

For the Gumbel mean-score identity, `A = sum(wbar_q²)` and the fourth cumulant is 6. Therefore `mu4 = 6 sum(wbar_q⁴) + 3 A²` and the known-mean variance estimator has SE `sqrt((6 sum(wbar_q⁴) + 2 A²)/K)`, exactly as implemented. The KGW independent formula substitutes `g(1-g)(1-6g(1-g))`. The scale-aware tolerances and structural-zero branches agree with §9, and observed constancy does not override an SE.

At h = 0, `colour_fixed` first draws the number of green covered tokens as Hypergeometric(V,m,j), then selects a uniform subset of that size using ranks. Under the ideal randomness model this is the restriction of a uniform m-subset of the full vocabulary and has the claimed finite-population covariance. The fixed-colouring bootstrap operates on the squared deviations from the known mean, which is the correct estimator to bootstrap. This exactness is within a chain: the imported routine does not construct one globally consistent full-vocabulary colouring across different covered-token dictionaries. Study 2's cross-domain/tokenizer correlations exclude fixed colouring, so that limitation does not invalidate them. At h ≥ 1, infeasibility is a practical statement about running this implementation over very many context classes, not a mathematical impossibility of sampling the model.

## 3. Method, statistics, precision and storage

### S1–S5 at their boundaries

**S1.** The code implements the band [2/3,3/2], mean M ≥ 30, theory share ≥ 0.75, no predictor flag, at least 30 resolved cells and at least 80% consistent among resolved cells. A finite interval wholly in the band is consistent, a disjoint interval inconsistent, and an overlapping/nonfinite interval unresolved. Nonpositive predicted SD is ineligible. Counts are paired-cell counts, not independent replications. I reproduced **544 candidates and 217 eligible** at N = 10,000, with no KGW input sigma flag. The primary h ≥ 1 scope is explicit and differs intentionally from Study 1.

Nearly binary levels do not make the SD ratio undefined, nor should real-text outcomes be removed retrospectively for being inconvenient. They do invalidate a general normal-SD precision claim. For an approximately Bernoulli per-key level with success probability p, the delta-method relative SE of its SD is approximately `abs(1-2p)/(2 sqrt(K p(1-p)))`: at p = .01 and K = 1,000 this is **15.6%**, not the normal benchmark's 2.2%. A sample containing no rare keys has a degenerate nonparametric bootstrap. M and theory-share eligibility control the finite-text floor, not this rare-key problem (F7). S1 remains an empirical adequacy rule without a stated experiment-wide type-I guarantee; it is not a theorem that the eligible cells have well-calibrated 95% bootstrap coverage. Nothing here establishes that any actual real-text cell has binary outcomes before the lock.

**S2.** Independently solving `KL(a || mu) = log(2e6)/K` reproduces the validation:

| K | mu | Lower boundary | Upper boundary | Bound at a = 0 |
|---:|---:|---:|---:|---:|
| 500 | .05 | .007598784 | .110410229 | 1.455e-11 |
| 500 | .01 | none | .042150312 | .01314097 |
| 500 | .001 | none | .015835656 | 1 (clipped) |
| 1,000 | .05 | .017656771 | .091181336 | 1.058e-22 |
| 1,000 | .01 | none | .031182436 | 8.634e-5 |
| 1,000 | .001 | none | .010190481 | .73539085 |

The strict flag is outside these root boundaries, since the code uses `< 1e-6`. `expected_cells` gives 1,020 eligible-family distinct-rule slots and three alpha values, hence at most **3,060 checks and 0.00306** by the union bound. Dependence among texts or cells does not defeat this argument; independence of the ideal key draws is required. A dead detector is flaggable iff `mu > 1-(5e-7)^(1/K)`, giving .028600356 and .014403914. At the saved N = 10,000 inputs, only **20 of 680 distinct KGW cells** clear the latter threshold at alpha = .01; none of the 340 Gumbel cells does. All 680 KGW distinct cells clear it at .05 and none at .001. This resolves the confusing sentence in §9 (F7).

**S3.** The fourth-moment formulas, six-SE heuristic and zero handling are coherent. At a fixed-colouring structural zero the tolerance, not an estimated bootstrap scale, decides. A zero bootstrap SE in a constant sample does not by itself prove a population identity; the code correctly records constancy separately. The retained 20,000-key identity and 200-subsample SE checks support the formulas, without certifying six-SE tail probabilities.

**S4/S5.** The implemented tolerance is exactly `2(se + se')`; no undeclared additive scientific tolerance is present. Both are weak monotonicity rules. An identically zero sequence or a flat sequence of saturated SDs holds, even at zero SE; that demonstrates no strict growth/decay. A structural zero is distinct from an accidentally constant sample. The tolerances ignore pairing covariance and have no simultaneous guarantee, already disclosed. Their “every chain is expected to hold; report all failures and counts” framing is honest preregistration. A failure is a failure of the stated observed-level monotonicity criterion for that corpus/width, not a universal refutation of the mean-shift identity. Likewise, a flat saturated pass is weak evidence about the proposed mechanism. The retained pilot executed **zero S4/S5 chains** because its synthetic tags do not match the production spec loop; its zero failures are not tests of those paths. I separately checked the helper's zero and flat-sequence behavior.

### Compute and power

Using the stored rates and every input chain's sizes, I recomputed the projection rather than accepting its rounded total:

| N | K | Recomputed hours | Stored rounded hours |
|---:|---:|---:|---:|
| 4,000 | 500 | 2.218338 | 2.22 |
| 4,000 | 1,000 | 3.203147 | 3.20 |
| 10,000 | 500 | 3.834731 | 3.83 |
| 10,000 | 1,000 | 6.264169 | 6.26 |

At D8's setting the components are **132.75 s build, 2,731.17 s hash, 11,364.18 s products, 8,322.91 s statistics**. The hash rate is 1.33459e-8 seconds per tuple-key and the product rate 2.10764e-9 per nnz-key-scoring. The 10-hour budget leaves **3.736 hours**, about **60% of the projected runtime**, for extrapolation error. The four-point statistics fit has small in-sample residuals but is not a runtime guarantee: real retained-count heterogeneity, simulated-shift integration, fixed-colouring work and full runner memory are not separately profiled by all four points.

The largest actual dictionary is 9,799,419 tuples, below the timed synthetic dictionary's 10,196,162. The longest actual chain has 58,199,507 nnz across its retained rule/length matrices, versus 30,599,878 in the timing's three longest-length matrices. Production additionally holds all rule/length score arrays at K = 1,000: the two uint16 KGW arrays plus one float32 Gumbel array total about **1.2e9 bytes** over 15 combinations at N = 10,000, before other working arrays. Thus the recorded **5.05 GiB** validator peak is encouraging against 16 GB, but is not a measured peak of the complete production runner at K = 1,000. I see no demonstrated memory infeasibility; retain margin and label this evidence accurately.

Recomputed eligibility:

| Dimension | N = 4,000 | N = 10,000 |
|---|---|---|
| Total | 153/544 | 217/544 |
| h = 1, 2, 3, 4 | 122, 24, 7, 0 | 136, 60, 15, 6 |
| raw, distinct | 89, 64 | 116, 101 |
| Llama, Qwen | 59, 94 | 86, 131 |

| Corpus cell | Eligible at 4,000 | Eligible at 10,000 |
|---|---:|---:|
| news/en@256 | 25 | 40 |
| wikipedia/en@256 | 15 | 19 |
| stackexchange/en@256 | 12 | 12 |
| wikipedia/de@256 | 11 | 17 |
| wikipedia/ru@256 | 13 | 19 |
| wikipedia/ar@256 | 11 | 20 |
| wikipedia/zh@256 | 5 | 13 |
| wikipedia/ja@256 | 16 | 19 |
| wikipedia/en@1024 | 27 | 35 |
| gutenberg/en@1024 | 18 | 23 |

These agree with `VALIDATION.json.power`. The retained h = 0 and Gumbel eligibility summaries are 136 and 335/680 at N = 10,000. This is an eligibility analysis, not power under a specified model-error alternative. **K = 1,000 remains my recommendation**, consistent with D8: the .99 quantile interpolates between the tenth and eleventh worst keys rather than the fifth and sixth at K = 500. The normal benchmark ratio half-widths of 4.38% versus 6.20% are correct but distribution-specific. Neither K provides precise population-extreme inference, which is properly disclaimed.

### What the stored cells support

At N_eff ≤ 10,000, rounding a level to seven decimals and then multiplying by N_eff and rounding to an integer recovers the rejection count: the maximum first-rounding error in count units is .0005, far below .5. Exact integer counts therefore support recomputation of key means, SDs, empirical quantiles, exceedance shares, correlations, paired level differences and fresh **key-only** bootstrap summaries. Key identity/order follows the stored key start and K.

They do **not** reconstruct the rejection matrix by document. A future builder cannot recover new crossed intervals, the two-way residual component, or score-tail/calibration curves from column totals alone. Rounded six-decimal q/s-bar arrays do not reproduce the full-precision S3 estimator exactly; its saved scalar estimates/SEs are the record. Dropped per-key zbar values are not generally recoverable from q/s-bar when retained counts vary. The cached ids and pinned implementation permit a separately authorized recomputation, but that is different from deriving a result from the committed cell record. This makes the missing crossed .01 quantile worth fixing before the lock (F4).

For Study 3, preserve the token manifest, deterministic ordered draws, tokenizer revisions, key namespace/order and detector definitions. The two English pools overlap in **1,068 sampled ids**, independently recomputed from metadata; cross-pool transfer claims must account for this, as well as differing length eligibility. The present three threshold levels and correlations cannot identify a score-tail discrepancy or validate transfer of a calibrated threshold. Study 3 needs its own calibration/evaluation split and tail/score records under its own protocol; this review does not require expanding Study 2 into that study. A measurement report should show endpoint/tie counts and the effective number of upper-tail keys, all derivable from the saved counts, alongside SDs and quantiles.

## 4. Process, data, lock and wording

**Pre-outcome discipline.** The inspected record supports the no-production-outcome claim. Git's Study 2 sequence is `cfc9849` (design/code and synthetic validation), `156a237` (manifest and key-free inputs), `54a2c65` (retained validation, D8 and completed draft). There is no production `cells/`, production `results.json` or `PRE_RUN_LOCK.json`. Across 2,019 experiment JSON files inspected for key-start provenance, retained Study 1 production records start at 20,000, retained later validation records at 1,000,000, and the 66 retained Study 2 pilot cells at 1,000,000. I found no scoring record starting in 22,000–22,999. The code's key-policy fixture mentions/checks that range without scoring it. This is an audit of retained records and code, not proof about deleted or unrecorded executions; the deleted synthetic shakeouts are expressly disclosed.

`INPUTS.json` contains predicted `mean_level` and `exact_binomial_key_mean_if_distinct`, so a broad grep for “level” does return matches. There are no observed `key_mean_level`, `level_values`, `level_counts` or `sd_obs` fields. `s2_inputs` calls moments/predictors with zero text-bootstrap resamples and never calls a colouring/scoring routine. The cache builder similarly has no key path. The validation scorer uses synthetic tokens and checked validation keys. Study 1's core and `tools/key_policy.py` still match their Study 1 lock digests.

**Judgment:** conditioning design and precision choices on disclosed key-free production-text statistics is acceptable for this explicitly conditional-on-realized-texts experiment. It is input-adaptive design, not untouched-corpus validation, and D7/§2 disclose it. It can select text regimes with favorable predicted detectability, so broader claims must retain that qualification. The grid's scientific cells, N/K, thresholds and reduction order already appear in `cfc9849`; the later semantic grid changes are only `text_bootstrap_B` and its note. I found no undisclosed outcome-driven grid selection. Every reduction in §10 is stated in the grid and precedes any lock. N = 6,000 would need its own pre-lock recomputation if invoked; it is not a performed reduction. A family-specific first-rule removal would also need matching runner/grid support. D8 currently invokes neither contingency.

**Data and seal.** I independently reproduced all ten eligible pools, seeds, pool digests, draw-id digests and first-three-id records from metadata. Their both-tokenizer pool counts agree with the audit's §9 table. All 20 arrays independently match digest, shape and dtype and have ids within V. The manifest/inputs/validation digest links match, except the historical grid hash described in F8. The cached book prefixes contain at least **2,029 Llama tokens and 2,030 Qwen tokens**, exceeding 1,000 + 1,024; the other windows also satisfy the capped-prefix count requirement. The prefix draw is a uniform permutation prefix without replacement; lengths are prefixes of the same cached window, not new samples. Tokenization is guaranteed for this defined capped-prefix target. The docstring's stronger universal equality to full-text tokenization does not follow merely from locality if a cap cuts a pre-token; no full-text equivalence assumption is needed for this study.

V = model-config vocabulary size consistently gives m = 32,064/64,128 and 37,984/75,968, hence g = gamma and zero centering offset. Qwen's 271 additional vocabulary dimensions have zero text weight but still belong to the fixed-size population; the finite-population correction correctly uses the declared V. No model was loaded to reverify the config independently. The manifest provenance and validation check are the inspected evidence for those revisions. `outputs/holdout_openings.jsonl` is absent; Study 2 calls the seal only for `open`, and its lock requires `final: false`.

**Lock/inventory.** The fifteen-file pinned set, canonical paths, R05 resolution digest, key record, date, approval field and `before_outcomes/final` checks are implemented. Manifest N is deliberately **at least** grid N, not equal, allowing a reduced prefix; the protocol's “equal” shorthand should not imply otherwise. Cell existence and tokenizer V are checked. The resolution digest and approval field bind a record, not independent proof of human approval, correctly reserved for Yichen's message. The retained acceptance/22-refusal results are consistent with the implementation. Reuse rejects foreign provenance, wrong slots and bodies that disagree with their slots. These sound checks coexist with the missing content checks in F1/F2; a valid filename/provenance header is not a valid statistical body.

**Constants and wording.** I enumerated numeric literals in `s2_core`/`s2_analyze` and checked their imported constants. Decision thresholds and resampling sizes match §§6, 8, 9: 200 key bootstraps, 100 two-way, 5 text, 200 crossed; two 300-text pairwise subsets; T = 2,000, B = 20,000; 200 quadrature nodes; KL 1e-6, six SEs, relative zero tolerance 1e-9 and monotonicity multiplier 2. Percentile endpoints .025/.975, normal interval multiplier 1.96, score cumulants, numeric denominator safeguards, rounding and seed bounds are computational conventions rather than additional scientific acceptance bands. The discrepancies below concern missing promised summaries and overstated validation/precision prose, not an undisclosed R4b-style additive tolerance. Constraints 1–16 are incorporated without claiming a theorem, remedy, priority, human authorship proof, transfer guarantee or population maximum.

## 5. Independent search

Web access was available. I made a bounded search with `after:2026-10-10` for watermark “per-key” false positives, “key-conditional”, and Gumbel/fixed-key/null calibration, including arXiv- and GitHub-restricted variants. I found **no newly verified primary work** changing the named record. Search results are not comprehensive publication surveillance and date filters are imperfect. A secondary index surfaced the already-known textGrain report with a recent indexing/submission label; that alone does not establish a new version or result.

The current [vLLM documentation](https://docs.vllm.ai/en/latest/features/watermarking/#detection) still states the fixed-key calibration limitation and recommends representative unwatermarked traffic with the deployed key. The [official OpenAI provenance page](https://openai.com/index/eu-text-provenance/) links the known textGrain technical report and notes that it may be updated; I do not infer new per-key results from the page. No new full-text download was made.

For the local re-screen I verified the retained HTTP 429 traceback and inspected the search-page/OpenAlex records. The two adjacent titles and their dates/DOIs are recorded there; their full Elsevier/Springer texts were not independently read in this review. Their classification as adjacent is appropriately limited to the reported metadata/abstract reading. No bot check was circumvented. Absence from these searches does not support a priority claim.

## 6. Findings and recommendations

### F1 — Major: a missing or false N_eff silently removes a live slot from every rule

**Evidence.** `s2_analyze.py:59–76` computes `is_marker` but never uses it, then gates all required-field validation on `d.get("N_eff", 0) > 0`. `live` uses the same default at line 81. In-memory deletion of `N_eff` from one retained live pilot cell was accepted by `load_inventory`: 66 filenames still passed inventory, but only **65 cells were live**. Setting it to zero had the same effect. Every production window has L > h and every retention rule retains at least one tuple, so zero N_eff is not a legitimate marker in this registered grid.

**Inference.** The advertised complete-inventory guard can drop a damaged or incomplete cell from S1's denominators, S2/S3 audits, chains and descriptive results without refusal. Header provenance does not prevent this body defect.

**Recommendation.** Validate N_eff and the live/marker schema before branching; require N_eff = N for this grid, or validate any future legitimate zero marker against a precomputed expected input. Require the fields needed by the expected cell and derive deployer membership from the grid. Add missing-N_eff, zero-N_eff, marker-at-live-slot and missing-deployer-block refusals. Keep these checks in both reuse/content validation and the analyzer so an incomplete matching file is not silently reused. Exercise S1, S4 and S5 with synthetic fixtures that actually enter their production-style grouping paths.

### F2 — Major: rejection counts are length-checked but not validated or reconciled with the decision statistics

**Evidence.** `s2_analyze.py:74–75` checks only that the list has K entries. In-memory substitutions of **-1**, **0.5**, **N_eff + 1**, and an all-zero vector contradicting the stored nonzero summary were all accepted. S1/S2 read the stored summaries, while correlations reconstruct levels from the counts.

**Inference.** One accepted record can yield two contradictory accounts of its levels, and impossible probabilities can enter the correlation/disparity analysis. This contradicts the intended “exact k/N_eff” record contract.

**Recommendation.** Require K integer counts in [0,N_eff], consistent denominators, and finite rule-driving values subject to explicitly allowed model flags. Recompute and reconcile the key mean, sample SD, quantiles, extrema, exceedance shares and KL bound from those counts at a stated numerical tolerance. Validate the alpha nesting available from the counts. Add malformed-value and contradictory-summary fixtures; retain a distinct test that reaches the study-without-lock branch (the current fixture is rejected earlier for the wrong inventory).

### F3 — Major: the registered six-language disparity is computed over seven pools, and all-zero keys are called infinitely disparate

**Evidence.** `s2_analyze.py:323` selects every `wikipedia_` tag, including both `wikipedia_en_256` and `wikipedia_en_1024` at scoring L = 256. That is seven pools, not §7's six languages. The English samples have different eligibility and draws. Line 326 assigns infinity whenever the minimum is zero, including **maximum = minimum = 0**. A synthetic all-zero count vector in every Wikipedia cell returned shares above 2 and 5 of **1.0**, although every pairwise difference SD was zero. The reported median also silently excludes all infinite ratios.

**Inference.** The maximum/minimum statistic mixes a length-selected within-English contrast with language disparities and classifies no observed differences as the largest possible difference. These affect a central descriptive measurement, not just labels.

**Recommendation.** Select the six @256 Wikipedia language pools explicitly for the language block, while keeping both English pools in the separately labelled 10×10 corpus matrix. Pre-state separate zero cases: all-zero, positive-over-zero and positive denominator; do not count all-zero keys as >2 or >5 disparities. State denominators and whether a median is conditional on positive denominators. Add identical-positive, all-zero, one-positive/one-zero and duplicate-English fixtures. Keep these as empirical finite-text ratios, not calibrated population language effects.

### F4 — Minor: the promised crossed interval for the 1% key quantile is never saved

**Evidence.** Protocol §§3 and 7 promise crossed intervals for the listed quantiles. `s2_core.py:227–230` bootstraps .05, .5, .95 and .99, but omits .01. Retained deployer pilot cells contain the .01 point estimate and no `q0.01` crossed entry. The analyzer accepts missing crossed blocks entirely.

**Recommendation.** Add .01 to the existing crossed summaries and assert the promised summary keys on every expected deployer cell/alpha. This is cheap while the rejection table is present; a report builder cannot reconstruct its document component from level counts after the run. Continue to describe the maximum's output as resampling uncertainty for a sampled maximum, not a population-extreme confidence guarantee. The median-only 40-replicate check does not establish nominal coverage for every quantile or maximum.

### F5 — Minor: reducing the text-bootstrap count changes downstream Monte Carlo draws, not only text-bootstrap SEs

**Evidence.** Protocol §8 says that with five resamples “only the text-bootstrap SEs change”; `VALIDATION.json` reports `production_B_changes_only_text_boot_SEs: true`. But `s2_core.py:262` consumes the shared RNG before the key bootstrap at line 274, the pairwise subsample, two-way bootstrap and later diagnostic seeds. `s2_validate.py:93` tests only rho_bar, the point SD and the deterministic predictor. A small synthetic validation-key example changed the SD interval from **[.008300435, .011172376]** at B = 30 to **[.008352906, .011281052]** at B = 5, and changed the two-way SE as well.

**Recommendation.** Narrow the claim and fixture name to unchanged deterministic quantities/formulas and acknowledge changed Monte Carlo realizations, or introduce independent streams and verify the stronger assertion. No Study 1 locked code change is needed. Also call the equivalence fixture what it is: N = 600, L = 256 at real vocabulary size, not §11(b)'s “real-sized chain”.

### F6 — Minor: the fixed Gaussian quadrature does not implement the claimed Gaussian sigma = 0 limit accurately

**Evidence.** With mu = 0, shift variance = 1, sigma² = 0, alpha = .01 and N = 10,000, the 200-node general calculation gives mean **.013022727** and SD **.113371671**, versus the closed form's **.01** and **.099498744**. At sigma² = 1e-6 the discrepancy persists. Zero shift variance works correctly. The current saved independent KGW inputs all passed the much tighter cross-check above, so this is a boundary defect rather than evidence of a present S1 input failure.

**Recommendation.** Add analytic zero-residual Gaussian integration or an accuracy-controlled Gaussian path, and fixtures approaching zero residual variance as well as zero shift variance. Do not equate correct indicator evaluation at quadrature nodes with exact integration of a discontinuous Gaussian tail. Keep the discrete empirical-shift path separate, where direct averaging of the indicator is the intended operation. If left as a bounded numerical approximation, state and check the admissible accuracy regime before interpreting diagnostic failures.

### F7 — Minor: qualify the rare-key precision and dead-detector claims

**Evidence.** §8 says the rare-key regime is handled by S2 and S1 eligibility; neither assures S1 bootstrap coverage or tail resolution. The Bernoulli calculation above shows why the normal-SD benchmark can be optimistic. §9's “at alpha = 0.01 only when K = 1,000 (barely…)” can read as a general dead-detector sensitivity claim, although at nominal mean .01 no under-rejection is flaggable. The actual saved inputs give only 20/680 KGW exceptions and no Gumbel exception. “Any dependence” also needs the between-texts/cells qualification, not arbitrary dependence between keys.

**Recommendation.** State these limitations directly, use the exact-mu condition rather than the ambiguous alpha sentence, and report endpoint/tie and tail-key counts for near-binary cases. Keep the pre-stated S1 rule; do not invent an outcome-dependent exclusion. Describe 95% bootstrap intervals as nominal and the power table as eligibility plus a normal benchmark, not a guarantee that all eligible cells resolve.

### F8 — Minor: reconcile the retained-run provenance and timing prose

**Evidence.** `INPUTS.json.grid_sha256` is `85d7e963…`, which I matched to the initial `cfc9849` grid, while the current grid and validation use `709f6adf…`. The only semantic additions are the text-bootstrap count/note, irrelevant to this B = 0 input computation, so this is an explainable provenance transition, not evidence of stale scientific inputs. The Milestone 3 “Done” paragraph lists hash rate 1.30e-8, product rate 2.07e-9 and peak 6.95 GB, while the retained validation gives 1.33459e-8, 2.10764e-9 and 5.05 GiB; its fitted coefficients also differ. The handoff repeats about 7 GB. The final projection itself reproduces correctly.

**Recommendation.** Record the input-producing commit/hash and why the grid transition preserves its quantities; do not silently rewrite historical provenance. Append a dated correction linking the decision-log timing numbers to the retained run and distinguish its measured peak from a production memory allowance. Keep the 6.26-hour projection labelled an extrapolation. After the pre-lock code repairs, regenerate the appropriate validation/protocol fields and verify their hashes against the candidate being reviewed.

The design, D7/D8 scope, input timing doctrine and core identities can stand. Resolve F1–F3 and reconcile the smaller discrepancies before computing the lock; Yichen's lock/run decision remains separate from this review.

VERDICT: REVISE
