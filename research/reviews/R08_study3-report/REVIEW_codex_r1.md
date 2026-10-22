# R08 — Study 3 report: independent review, round 1

Date: 2026-10-15. Reviewer: Codex (OpenAI). Baseline: `main`, `4a01cc8bb4c7e76ccc1eba987ef6334b38dcef3d`; working tree clean at entry.

The locked record and the three registered verdicts reproduce. I recommend revision of the report: Table 16 mixes tokenizer directions, and several interpretation sentences overstate what the measurements establish. These are corrections to the unpinned reporting path; none calls for changing the locked protocol, thresholds, counts, predictions or analyzer.

## 1. Baseline and material examined

Read the repository instructions and review orientation; R08's prompt; the protocol's requested sections and lock/run paragraph; the report and prose template; the analyzer, report builder, relevant runner/provenance functions, fixture generator and manifest builder; the lock, results, inputs, checks, prose values, manifest and logs; the main tables and relevant full supplements; all six rendered figures; R07's resolution; the gate's wording constraints; the requested decision-log entries and handoff. Inspected unit metadata, count arrays and committed threshold arrays. Checked the complete descriptive CSV against the results by identity and selected numeric fields.

No grid, validator or report builder was run. No data, model or PDF was downloaded; no holdout access, commit or external posting occurred. The authorized analyzer rerun wrote only a scratch result outside the repository. This memo is the only repository file written.

## 2. Claims against evidence

### Lock and record

- All **20 pinned files** matched their lock digests using `shasum -a 256`. The R07 resolution matched `9c22c19c…`. For every pinned path, `git log --oneline 5e44a2e..HEAD -- <path>` was empty.
- The lock tree contains no Study 3 cell file. The record first appears in `887a2c7`, committed at **20:51:18Z**, after the run ended at **20:45:53Z**. The report commit `3cf1914` is at **21:52:36Z**. This supports the recorded chronology; Git history is not an independent witness to unrecorded activity.
- Independently enumerated the exact expected **240 filenames**, comprising 120 unit records and 120 array files. Inventory SHA-256: `c270ab818620c1f3189f83cb3095f1a7ed5b30064c9895f54e4e24b6f6c1733d`, equal to the manifest. No unit JSON contains a FIXTURE marker.
- Independently checked all 120 units' study/mode, lock/grid/core/runner/manifest digests, key starts **23,000/24,000**, **K = K_fit = 1,000**, slot identity and N. All 60 calibration token digests matched the token manifest. The locked analyzer additionally regenerated evaluation provenance and checked the complete body contracts and threshold dependencies. For example, `cal__llama__news_en_256__h1` has N = 5,000 and the registered threshold axes; `eval__qwen__gutenberg_en_1024__h2` has N_E = 7,122, the registered fixed/same/cross axes and all 20 threshold sources.
- The run log has one start, one completion, 120 unit lines and no reuse. Its endpoints are **19:47:53Z–20:45:53Z**; launch notes name `5e44a2e` and the correct lock. All unit timestamps postdate launch. `run_stdout.log` contains `DONE`; the detailed record is `run.log`. The logs and manifest support zero restarts/resumes and no recorded execution deviation. `final: false` remains set.
- Raw results: **108,011,668 bytes**, SHA-256 `42bb915363fdb373053e722bf8dc463d83e97f1bbe57cbc810af215555032e89`. Gzip: **19,534,907 bytes**, SHA-256 `c77f38a8545e5d0bd4571916f3b031a1c75ed8b59f270b804b3ce83dd338af5d`. Decompression yields the raw digest. The report's 108 MB and log's approximately 103 MiB describe the same bytes.
- Reran `verify_lock`, then the locked `s3_analyze.analyze(..., mode='study', lock_path=..., s2_cells=s2_inventory_ok())`, serializing with the analyzer's separators into a temporary directory. It finished in **52.63 s**, with the **identical raw-results digest**. The command-line `main` writes the canonical output, so I used its verified analysis function and a scratch destination. No refusal was disabled.

### Independent numerical checks

| Rule | Independently recovered counts | Verdict |
| --- | --- | --- |
| T1 | 1,600 candidates; 1,494 eligible; 1,474 resolved; 1,471 consistent; 3 inconsistent; 20 unresolved | PASS: 99.7965% consistent among resolved, above 80%; at least 30 resolved |
| T2 | 1,600 candidates; 879 material; 875 resolved; 875 agree; 0 disagree; 4 unresolved | PASS: 100% agree among resolved, above 90%; at least 30 resolved |
| REP | 108 checks; 0 gross failures | PASS |

I independently classified every primary row from its interval and the registered bands, and checked every primary prediction, moment, covariance, eligibility and materiality field against `INPUTS.json`. I recomputed the observed SDs/means and both bootstrap intervals from counts for **69 primary rows**, including every non-consistent T1 row and every unresolved T2 row. Differences were zero. All **108 REP** SDs, bootstrap SEs, stored Study 2 references and decisions were independently reproduced. Study 2's 3,468-file inventory digest is `f3b4a0ceb246c0154903d7b99fb55f28999fa4e50ef2aabf24b1e626d9ac6766`, equal to its pinned manifest.

All **702,720 descriptive prediction fields** independently matched the pre-lock inputs exactly, including all six population/finite exceedance shares. Independently recomputed **300 descriptive rows** spanning the inventory, including quantiles, extrema, zero/distinct counts, exceedance shares and screen statistics: zero differences. Recomputed **288 threshold z summaries** from three calibration units, including positive-threshold and abstention counts. All **87,840 CSV rows** matched results by identity and five observed/predicted statistics.

The primary tables provide the requested marginal breakdowns and full row diagnostics. The 106 ineligible rows are precisely the pre-lock input-based exclusions, all at N_cal = 5,000: 80 diagonal, 16 near-identical, 8 within-English and 2 English–other. Their exclusion is not an outcome-dependent selection. The secondary, break-even and diagonal-reference blocks are labelled as the builder's. The promised output families are available across the supplements and CSV, although the captions and Table 16 need correction below.

### Decisive source checks

- **AutoMark**, local `research/literature/txt/2609.37310.txt`, PDF p.42, Proposition 1: “Let β ∈ (0, 1] and let Pξ be a detector that satisfies Equation (2).” Its prerequisite is substantive. The report correctly distinguishes the raw numerical arm from a refutation of that proposition and distinguishes the empirical plug-in from their test. Appendix C, p.29, uses the smallest multiplier passing both of their tests; this study does not reproduce that procedure.
- **Vovk 2012**, local `research/literature/txt/1209.2673.txt`, PDF p.2: “generated independently from the same probability distribution”. Proposition 2b on PDF p.6 gives the binomial condition and its continuous-score qualification. These support the reference model and repeated-calibration interpretation, not a measured population share over keys on one frozen C.
- **Nemecek et al.**, [primary HTML §4.1](https://arxiv.org/html/2608.20047v1#S4.SS1): the global threshold is “calibrated from the pooled null” and “is our headline”. The report's attribution of the pooled-versus-per-language comparison is appropriate. No local PDF text exists for this paper; PDF confirmation remains the explicitly carried-forward claim-gate task.
- The disclosed Study 2 figure is correct: its resolved S1 median is **1.21**, reasonably described as about 1.2. No literature claim checked here establishes priority for this study.

## 3. Method and statistics

The registered question and conditional estimand remain precise. The count-based SD uses ddof 1; T1 compares with the conditional prediction; T2 resamples numerator and denominator using the same indices; REP combines independent-key SEs with the registered factor 6 and additive tolerance. Boundary conventions are correct: a T1 interval wholly inside the closed band is consistent, a disjoint interval inconsistent, and overlap unresolved; a T2 interval touching 1 is unresolved. Ineligible/immaterial rows do not enter their respective pass denominators. Abstentions remain in the descriptive record.

The seed regeneration is an independent implementation check of indexing, arithmetic, pairing, quantiles and classification for the **same prescribed bootstrap realization**. It is more than a seed check, but is **not** an independent set of bootstrap draws, a stability analysis across seeds, or a validation of interval coverage. The report should preserve that distinction. Rows share keys/texts and are not independent replications; the pass fractions are the registered descriptive decision criteria, not confidence levels for universal adequacy.

The raw KGW lattice explanation is plausible and appropriately introduced as an account not isolated by this study. The distinct and raw contrast, the synthetic discrete-score fixture and constant raw M support offering it as a hypothesis. They do not identify the mechanism behind every transfer exception. The primary non-consistent rows affect **three**, not two, evaluation cells: Gutenberg 11, Arabic Wikipedia 10, Stack Exchange 2.

Viewed all six figures and checked their selection code. No plotted outcome is cropped by the limits identified here. Log axes and the log₂ heatmap are labelled; the observed/predicted heatmaps share a color range; Figure 3 explicitly selects Llama/distinct/h = 1, with other settings in the record. Fixed-threshold points in Figure 2 are once per evaluation unit, not replicated across calibration sources. The other plotted subsets are disclosed. The numerical substitution in Table 16 is a table-selection error, not a figure-selection error.

## 4. Process and carried-forward items

The builder's mismatch checks are active; no `or True`, `assert True`, or bare `pass` was found in it. It rejects FIXTURE markers in study mode. Fixture mode resolves its paths, refuses repository paths and writes a separate fixture report outside the repository. The generator marks synthetic units and its analysis output; the canonical inventory has no markers and independently reproduces. I did not rerun the approximately six-minute fixture workflow. The historical claim that its render preceded reading descriptive outcomes is disclosed in the log; I cannot independently establish the conductor's reading chronology.

There is no evidence of protocol drift or missing committed thresholds. The AI/reviewer disclosure is present. R07's estimator labels, multiplier prerequisite, dependent-screen caution and descriptive diagonal treatment are present in tables/limitations, but several interpretation sentences undo those qualifications (F2–F5). “Same law”/“near-identical” should also be explicitly retained as design labels in the report, with the protocol's finite-pool/exclusion qualification. No new uniform quadrature-error guarantee is claimed. Caption completeness, the typed zero and stale decision-log statements are addressed below.

For Study 4, the report already carries the essential requirement to preserve the exact threshold-to-key mapping and disclose abstentions/null-law mismatch. Retain that: bind tokenizer, family, rule, width, calibration cell, N_cal, α and evaluation-key index to the committed array digest. F6 adds a small but real abstention detail. Selection of settings and power evaluation remains Yichen's later decision; this review authorizes neither a new run nor a change to frozen thresholds.

## 5. Independent search

Performed bounded web searches for `watermark "per-key" calibration after:2026-10-13`, `"watermark" "calibration transfer" after:2026-10-13`, and `"AutoMark" "multiplier" after:2026-10-13`, followed by arXiv-targeted searches for per-key/per-deployment calibration and AutoMark. Date-filter results were noisy and included older or irrelevant work. No newly dated, relevant occupant was verified. The primary results included the already-known [AutoMark](https://arxiv.org/abs/2609.37310) and [Nemecek et al.](https://arxiv.org/abs/2608.20047); I rechecked the latter's HTML as above. This bounded absence is not evidence of novelty. No access barrier was circumvented.

## 6. Findings

### F1 — major: Table 16 substitutes cross-tokenizer outcomes for all Qwen rows

**Evidence.** `s3_report.py:825–827` selects `tokC == tok` but never `tokE == tok`, then takes `.iloc[0]`, for both the transferred and diagonal rows. Because the Llama evaluation units occur first, all **16 Qwen rows out of 32** select Qwen→Llama outcomes. Their status and v are subsequently obtained from the within-Qwen T1 row. Thus one displayed row combines different comparisons.

For Qwen, distinct, h = 1, conformal@5000, en@1024→en@256, Table 16 shows observed/predicted SD **0.583/0.605 pp** and key-mean **1.147%**. Those are cross-tokenizer values. The intended within-Qwen values are **0.169365/0.176391 pp**, key-mean **0.998760%**. The displayed diagonal is contaminated similarly. The correct registered T1 rows and the independently generated near-pair prose are unaffected.

**Recommendation.** Require both tokenizer identities and the intended pair class, assert exactly one match, and join diagnostics by that complete identity. Regenerate all 32 rows and verify both outcomes and diagonal comparators against their full identities. Leave the locked record unchanged.

### F2 — major: interpretation turns model population shares into empirical validity

**Evidence.** §5 says tolerance “keeps the population share above α” at 4.7%; §6 Q1 says it “holds” that share “in population terms”; §8 repeats the unqualified population figure. The 4.7% is **Beta.sf(0.01, 39, 4962) = 0.0465657**, a reference-model quantity, not an observed population-over-keys measurement. Observed frozen-C levels use finite E. Their median 7.3% and finite prediction about 7.7% do not establish a population guarantee over keys. The limitations correctly say this, but do not repair the affirmative interpretation.

The same paragraph compares conformal's measured **45.6%** with **48.1%**, the population Beta reference, despite R07 requiring the finite-evaluation comparison. Table 8's finite prediction is approximately **47.0%**. Nor does Table 6 alone establish the blanket §6 assertion “match … within the sampling precision”: for example Qwen Chinese distinct h = 1 conformal@5000 has measured share **41.4%**, finite prediction **46.9168%**; no corresponding uncertainty assessment is supplied for that claim.

**Recommendation.** Label every population number as the i.i.d./working-model reference, including §§5, 6 and 8. Compare observed shares to finite predictions, with population references separately labelled. Say the aggregate summaries are close where supported; remove blanket precision/validity assertions unless a clearly labelled descriptive uncertainty comparison supports them. Do not convert this into a new registered test.

### F3 — major: remedy rankings contradict the reported measurements

**Evidence.** §6 Q3 says “The per-key methods are the only ones that reduce the dispersion” and pooled calibration fixes “the mean and not the dispersion.” Table 8, distinct h = 1, reports SDs **0.441 pp nominal, 0.048 multiplier20, 0.240 empirical, 0.397 pooled, 0.172 conformal@5000**. Under raw h = 1, pooled reduces **1.363 to 0.466 pp**. Reducing the mean can reduce absolute SD; that is still a reduction in the registered dispersion metric.

The same paragraph's unqualified empirical multiplier “meets β on its own law” drops §5's median-unit qualification. Among diagonal h = 1 units, the measured finite share exceeds 5% in **2/20 raw** and **4/20 distinct** units (maxima 6.1% and 6.0%). This is not proof of population failure either; the measured share must simply be described correctly. Calling the fitted multiplier a “rule-specific constant” also hides its substantial cell dependence: the reported raw range is **9.44–246.38**.

§6 Q4 ranks the distinct rule as the “larger lever” than calibration without specifying an estimand. For absolute SD, raw nominal→distinct nominal is **1.363→0.441 pp**, whereas raw nominal→raw conformal@5000 is **1.363→0.167 pp**. The blanket ranking does not follow.

**Recommendation.** Compare mean and absolute dispersion together, at explicitly named settings. Describe pooled calibration as targeting the average without enforcing per-key control, not as leaving SD unchanged. State empirical evaluation ranges and fitted multiplier variation. Keep null-side comparisons separate from the still-unmeasured power trade-off; replace the overall lever ranking with specific paired contrasts.

### F4 — major: stability of across-key summaries is confused with fixed-key calibration variability

**Evidence.** §5 concludes from Table 13 that “the dispersion a deployer faces is across keys, not across calibration draws”. Table 13 bootstraps **summaries over 1,000 keys**: a stable key-mean or stable across-key SD does not imply a stable level for any one fixed key. Averaging can stabilize a summary while individual thresholds/levels move substantially. The retained `cal_boot` summaries do not give a per-key variance decomposition.

The report also says the finite-evaluation term “dominates” on the N_cal = 5,000 diagonal (§7). The pre-lock theory-share range there is **0.587476–0.671505**: under the model, the non-floor component is larger. At j = 50 and N_E = 10,000 the Beta SD is **0.140670 pp**, finite-floor SD **0.099479 pp**, and theory share **0.666622**. Failure of the 0.75 eligibility criterion does not mean the floor is a majority of variance.

**Recommendation.** Conclude only that the reported across-key summaries vary little over these bootstrap resamples. Explicitly distinguish this from fixed-key calibration-draw variability. Describe the finite-text term as non-negligible/comparable and responsible for ineligibility, not dominant; retain the Beta contribution and conditional estimand. No new computation is necessary to make the current claim accurate.

### F5 — minor: remove universal and ranked claims unsupported by the row diagnostics

**Evidence.** §5 calls T2's sign predictable “everywhere it was tested” although four material rows are unresolved, and says R_obs lies below R_pred “throughout”; it is above in **13/1,600 rows**, including **2 material rows**. The four unresolved rows' nominal observed/predicted ratios are **1.895, 1.895, 1.287, 1.220**; their conformal ratios are **1.235, 1.198, 0.845, 0.851**. Both numerator and denominator discrepancies contribute, via R_obs/R_pred = conformal-ratio/nominal-ratio; aggregate medians alone do not isolate the cause.

The non-consistent T1 theory shares **0.834–0.988** are not “the lowest of the eligible rows”: consistent rows reach **0.753**. The transfer statement that v “sets the transfer error” also needs the working model's residual scales, order statistic and finite-E terms; the exact covariance identity alone does not determine transferred level error.

**Recommendation.** Say all **resolved material** signs agree and that R_obs is generally lower, report the local ratios if explaining the four exceptions, and drop the unsupported ranking of theory shares. Bound the adequacy language to the eligible blocks actually evaluated. Present v as a component of the assumed predictor; keep the lattice explanation suggestive and same/near-identical-law labels approximate.

### F6 — minor: the abstention total includes six positive-index zero thresholds

**Evidence.** §5 attributes **960,006** abstaining entries at α = 0.001 to the j = 0 settings. Those settings account for exactly **960,000**. Six more stored zero thresholds have **j = 1**, all Gumbel/raw/conformal@1000 on Gutenberg: Llama h = 0 (1), Llama h = 1 (1), Qwen h = 1 (1), Llama h = 2 (3). `s3_report.py:1013` sums all per-key zero thresholds rather than only j = 0 cases. Their numerical cause was not isolated in this review.

**Recommendation.** Generate separate counts for structural j = 0 abstentions and stored zero thresholds at positive j, and identify the latter settings for Study 4. Preserve the committed thresholds and strict rejection rule; do not silently reinterpret or repair them.

### F7 — minor: the promised standalone denominator captions are incomplete

**Evidence.** The decision log asserts K and N_E appear in every caption, but Tables **9, 13 and 16**, for example, state neither; Table 15 omits N_E. Some row tables carry N_E/K columns, while aggregate tables require the reader to recover them elsewhere. Similar omissions occur in supplement captions. Table 17 documents output availability but does not make these tables independently interpretable.

**Recommendation.** Add generated K, applicable N_E values, aggregation denominator and subset to each relevant table caption. For threshold-cost tables use N_C/K_fit or positive-threshold counts as appropriate. This is a presentation correction, not a missing-data or missing-analysis finding.

### F8 — minor: reconcile the narrative record and generate the residual zero claim

**Evidence.** The Milestone 6 decision-log entry and R08 prompt say the T1 exceptions occupy two evaluation cells; the results and report correctly list **three**, including two Stack Exchange rows. The log also says conformal@1000 “halves” the distinct h = 1 nominal SD, but **0.332/0.441 ≈ 0.75**, not one half. In the prose template §6 Q3, “no key above α” is a typed outcome count in words. It happens to be true for the referenced multiplier block, but is not generated as the report's process claim requires.

**Recommendation.** Record dated corrections to the factual summary, reconcile current review/orientation context where needed, and replace the literal zero assertion with a generated count and explicit subset. The settings/design constants typed in prose are not outcome counts; the disclosed Study 2 approximation is verified and can remain.

VERDICT: REVISE
