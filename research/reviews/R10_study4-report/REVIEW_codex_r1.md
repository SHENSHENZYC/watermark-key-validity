# R10 — Study 4 report: independent review, round 1

Reviewer: Codex. Date: 2026-10-17 UTC. Conductor: Claude Code. Scope: Stage 6 exit for Study 4, under the existing lock.

The record checks out, and the registered verdicts reproduce: **W1 PASS, W2 FAIL, W3 PASS**. I recommend revising the report before accepting this checkpoint. The main problems are an incomplete abstention disclosure, missing promised reporting fields, and two interpretations that overstate the observed results. None calls for changing the protocol, thresholds, committed analysis, eligibility rules, or verdicts.

## 1. Baseline and scope read

Baseline: `main`, **`4b103604314cd2ecd5a82116d205190edd7a3c6c`** (`4b10360`), with a clean working tree at the start of review.

I read the root `AGENTS.md`, `research/reviews/REVIEW_ORIENTATION.md` in full, and `research/reviews/R10_study4-report/PROMPT.md`; the requested protocol sections and final lock paragraph; the report and prose template; the relevant parts of `results.json`, its arrays, both complete CSV supplements, `checks.json`, `prose_values.json`, and all 17 tables; the complete report builder, fixture generator, and manifest builder; the locked record interface and relevant runner, analyzer, detector and prediction code; the manifest, launch notes and run logs; the two specified Milestone 9 entries and their correction; the current handoff; R09's resolution; and the gate's wording constraints. I inspected all six PNG figures and their plotting code. I re-read the pertinent passages in the two existing local literature text extractions, with PDF page numbers determined by form feeds.

Checks were read-only, short local commands and Python programs supplied on stdin with bytecode writing disabled and execution time limits. I did not invoke the runner, the analyzer's study entry point, or the report builder's entry point; load a model; regenerate an inventory; download anything; access the held-out partition; or alter any existing file. The only review output is this memo. All review computation occurred before the 18:00 UTC restriction.

## 2. Claims against evidence

### Lock, record and chronology

All **32 pinned files** matched `PRE_RUN_LOCK.json` under `shasum -a 256`. The R09 resolution matched its pinned digest, `d4065c399db7d6c80732bb2dd8a0ea934464ac2eee9a28e13f167abe2f76c74a`. Path-specific Git history showed no changes to the pinned files or that resolution after `f5dcd60`.

| Object | Independently verified result |
|---|---|
| Study 4 lock | SHA-256 `7067b4e1457c7ed977a311409914e3034721993eae5eddc44f6934c8d1b4cdd9`; written `2026-10-17T02:13:03Z`; `final: false`; before-outcomes declaration present |
| Study 3 record | All 240 files rehashed through `s4_record.Record`; inventory `c270ab818620c1f3189f83cb3095f1a7ed5b30064c9895f54e4e24b6f6c1733d`; lock `0e2889287d9d814166213e360766e93097de63401842516e3cb308056c666df6`; no cell-history change after `887a2c7` |
| Study 4 record | Exact manifest file set, 1,860 files, all digests matching; 930 records, comprising 900 generation and 30 null units; zero FIXTURE markers; `complete: true` |
| Study 4 inventory | `2c6863586e8f20aa4ec33897de48dca3df27287fff2f1e7b68cea22fe2241194` |
| `results.json` | `5ee9842146d8c6171c21902ca56e0e06a7441eaa433d81844380d5b34d6cfc9e`, matching the manifest's `analysis_output` |
| `results_arrays.npz` | `efa16831a3bd53e812fc48a7d32c97676b778c548043904f326426bd78ab8783`, matching both the analysis and manifest |

The lock's Git tree contains no Study 4 unit files. The run's first line names the locked grid, lock digest and launch HEAD. The completed record/analysis/manifest commit `d556574` follows the run, and report commit `f49f676` follows that. The two disclosed intermediate commits added 110 unit files; the final record commit added the remaining 1,750, with no modification of the earlier files. Their present hashes agree with the final manifest. There is a small description error: `6cc37b1` contains **37 generation units and 10 null units**, not 47 generation units; `f31dcad` contains eight generation units. This does not change the 55-unit total or compromise their bytes (F7).

I independently enumerated all 930 expected slots and checked the record provenance and array digests, including the seeded power keys, null chunks, lock/grid/code references and unit identity. The core is bound transitively by the lock; it need not be a separate field in every unit's code-digest dictionary. For 24 body samples spanning all cell/arm blocks and null blocks, I checked the hook flags against the locked colouring and recomputed the stored KGW p-values at every length/rule; there were no flag mismatches and the p-values agreed exactly. This supplements, rather than replaces, the complete record hashing and inventory check.

The pinned analyzer's study path verifies the canonical grid and lock, checks the complete canonical inventory and record bodies, and writes the canonical analysis paths. The supplied outputs and history are consistent with those checks having been used; I found no evidence of a bypass. Static code and provenance are not an independent attestation of every historical process invocation, and I have not rerun the prohibited study analysis.

### Numerical reproduction

I used separate arithmetic on the arrays and committed thresholds, not the builder's or analyzer's row functions, for the following checks:

- **All 16,524 descriptive rows:** counts re-scored from the stored per-text p-values at the original thresholds; means, quantiles, costs, observed variances, two-way components, binomial proxies, and power-side abstentions checked. All counts agreed; 297,432 scalar comparisons had maximum absolute discrepancy about `1.24e-16`.
- **All 33,048 null rows:** level means, SDs, quantiles and above-alpha/zero shares independently calculated from counts. Both complete CSV supplements agree field by field with the JSON rows; neither is a selected subset.
- **All W1, W2 and W3 rows:** bootstrap index arrays regenerated with SHA-256 of the specified row name and salt `20261019`; statistics, interval ends and decisions independently reproduced. W1 and W3 interval ends were bit-identical; W2 arithmetic differed by at most about `6.7e-16`.
- **Prediction binding:** all W1 costs reproduced from the per-cell pre-lock pilot law and committed thresholds, including strict threshold comparisons. The three tolerance values agree with the pre-lock SE rule. Across all serialized calibration-prefix checks, maximum discrepancies against Study 3's pinned inputs were approximately `4.7568e-9` for rho and `4.9930e-9` for sigma-squared, within the specified allowance. For three W3 examples spanning diagonal/transfer, raw/distinct, widths and calibration sizes, I separately reconstructed incidence moments and cross-set overlap from the existing token arrays; moment/covariance differences were at most `2.22e-16`, and predictions using those independently reconstructed inputs agreed to floating-point precision. The generated evaluation moments are legitimately post-run inputs; the calibration thresholds and calibration-prefix reference moments were fixed before the lock.
- **Quality:** re-derived repetition, loop shares, perplexity, EOS mass, first-192 log-probabilities and green shares from all 930 unit arrays, then aggregated in the analyzer's stated units. All 207 summary statistics agreed to within `1.11e-16`. No quality-based exclusion occurred. For example, primary-arm loop counts were 1, 4 and 23 out of 5,000 texts per cell; the high-strength counts were 11, 16 and 78. The problem with Table 15 is its labels and denominators, not these values (F3).

W1's numbers, in percentage points, are:

| Cell | Realised median | Key-bootstrap interval | Predicted median | Pre-lock predicted-median SE | Tolerance c | Class |
|---|---:|---|---:|---:|---:|---|
| News | 14.0 | [10.0, 16.0] | 15.234375 | 2.580873 | 5.161747 | unresolved |
| Wikipedia | 20.0 | [16.0, 22.025] | 20.117188 | 3.171910 | 6.343820 | consistent |
| Stack Exchange | 26.0 | [22.0, 28.0] | 25.000000 | 2.884957 | 5.769914 | consistent |

News's lower band endpoint is `10.072628...` pp, just above the interval's 10 pp endpoint. It must remain unresolved. Two consistent and zero inconsistent cells give **PASS**.

| W2 cell/rule | R_pow | Nominal 95% key-bootstrap interval | Finite of 200 | Class |
|---|---:|---|---:|---|
| News/raw | 0.960703 | [0.708340, 1.271030] | 200 | unresolved |
| News/distinct | 0.870238 | [0.341542, 1.737360] | 199 | unresolved |
| Wikipedia/raw | 0.728073 | [0.518672, 1.002168] | 200 | unresolved |
| Wikipedia/distinct | 0.703217 | [0.328782, 0.944655] | 200 | unresolved |
| Stack Exchange/raw | 0.876120 | [0.333864, 1.859596] | 199 | unresolved |
| Stack Exchange/distinct | 0.675929 | [0, 1.564804] | 181 | unresolved |

These give zero agree, zero disagree, six unresolved: **FAIL**, as registered. A point estimate below one does not meet either interval rule by itself.

For W3 I recovered **240 candidate, 221 eligible, 216 resolved, 216 consistent, zero inconsistent, five unresolved and 19 ineligible**. Table 6 correctly gives the candidate/eligible/resolved/consistent/inconsistent/unresolved counts by cell, width, rule, source class and calibration size. The five unresolved rows are the listed raw-rule, h = 1, Wikipedia-source transfers. The resolved count exceeds 30 and the consistent fraction of resolved rows exceeds 80%, giving **PASS**. The 19 excluded rows fail the theory-share condition; there is no hidden exclusion of a flagged or adverse resolved row.

### Prior work and permissible claims

Local substring searches re-established the relevant priority and prerequisite statements:

- `research/literature/txt/2609.37310.txt`, PDF p. 29, Appendix C: **“any scheme that is sound over the key becomes sound given a key.”** Proposition 1 on PDF p. 42 explicitly assumes Equation (2); the proof first relates the scaled rejection event to the original event at alpha times beta, then uses its key-average bound and Markov's inequality. The prerequisite is essential. Appendix C, pp. 29–30, compares guaranteed, empirically screened and uncorrected versions, including a power cost; the study's empirical plug-in is not the paper's two-screen empirical procedure.
- `research/literature/txt/genhatharan_nominal_fpr_2026.txt`, PDF p. 9, Section IV-H, explicitly prices calibration on 50 watermarked outputs per cell. Figure 10's caption, PDF p. 11, says **“Operating point of each detector key at 512 tokens before and after per-key calibration”** and describes detection changes by key and prefix length. PDF p. 16 qualifies these as development-scale measurements.

The report names Section IV-H, Figure 10 and Appendix C, disclaims priority, conditions the multiplier reading on Proposition 1, and distinguishes its plug-in. Those parts satisfy the R09 carry-forward. Its costs, operating points and threshold-shift assessment should enter Stage 7 as measurements under the stated conditions, not new priority claims or theorem claims.

## 3. Method, statistics and figures

I did not reopen the agreed design. Under that design the rule calculations are sound, including the boundaries: W1 requires containment rather than a point estimate inside the band; raw W2 requires an interval wholly below one; distinct W2 requires containment in [2/3, 3/2]; a zero observed W2 denominator or fewer than 180 finite resamples leaves the row unresolved; W3 eligibility precedes the ratio classification and the pass denominator uses resolved rows only. The six W2 observed denominators are positive. Stack Exchange/distinct has 181 finite resamples, so it clears availability and is unresolved because its interval crosses the band, not because availability failed.

The prompt-conditioned W2 target remains the SD-scale ratio `R(D)` of the floored conditional raw components on its positive-denominator domain. It is neither the uncorrected variance of the 50-prompt key means nor a confidence statement about the population ratio over the prompt law. Section 8 mostly preserves this distinction. Its measured-validator-coverage citation is present. The protocol's well-separated-model conditional coverages range from approximately 0.907 to 0.943; the shared-additive-interaction example gives 0.943 conditional coverage but only 0.510 population coverage. I traced these to the pinned validation/protocol record; I did not repeat the coverage experiment. “Nominal 95%” is therefore the appropriate wording, and exact numerical reproduction does not improve its calibration.

In particular, **bit-for-bit interval regeneration is more than a seed check here**, because independently implemented thresholding, variance/cost calculations, resampled statistics and quantiles also reproduce the result. It is an independent implementation check of the specified algorithm on this record. It is **not** independent evidence of 95% frequentist coverage, adequacy of the bootstrap model, independence of hashes, or validity of the population extrapolation. The two implementations deliberately share the target, bootstrap design and random indices.

W1 is properly conditional on the fixed pilot law; c is a materiality allowance informed by the pilot's uncertainty, not a calibrated joint error rate. Its per-key correlation and within-c share remain descriptive. W3 is a conditional adequacy check on one generated sample per cell, shared across its many source rows; it supplies neither 240 replications nor a generated-text validity guarantee. The report says this explicitly. Shorter lengths are explicitly not calibrated operating points; the model-null and transfer blocks are presented as measurements without a transfer guarantee. I found no claim about held-out outcomes, other models/languages/attacks/samplers, hash independence, or Gumbel generation power.

All six inspected figures show the selected data without an adverse-data exclusion or an axis limit that hides points. W1's median tolerance and interval bands and W2/W3's rule bands are drawn correctly. The W3 figure includes all 240 candidates, including ineligible rows. The operating-point and length figures use six named methods at the primary settings; the fuller method/calibration-size results are retained in the CSV. Figure 6 sorts each arm/rule's prompt effects separately: the horizontal rank is not a common prompt identity across curves. Its current “sorted by effect” axis is accurate; making “sorted separately” explicit would help the paper. Table/figure denominator and window clarifications are requested in F3.

## 4. Process and consistency

The log contains one study start, zero reused units and 930 completed units. It records `02:13:52Z` to `14:05:24Z`, 11.859 hours, and no budget stop. The launch note records a clean lock-commit tree at `02:13:51Z` and exit code zero at `14:05:25Z`. The runner's peak RSS is 2.92 GB; phase-start swap is about 2.9–3.4 GB. The analysis records 798 seconds and 3.28 GB in its own RSS measure. The decision log separately reports 3.53 GB from `/usr/bin/time -l`; those are separately labelled measurements, not a numerical contradiction. The run and analysis completed well before the off-power window.

The decision log discloses the watchdog's self-matching defect and disarming before 17:45. The logs show no watchdog stop or interrupted run. They cannot independently establish the watchdog's transient process state, so that history should remain attributed to the conductor's dated account rather than called a tested enforcement mechanism. The actual completion times establish compliance for this run.

The builder verifies the lock/record binding and arrays digest and refuses a study result marked FIXTURE. Fixture mode resolves both input and output paths, refuses paths inside the repository and writes a separately named, marked report outside it. I found no `or True`, `assert True`, or bare `pass` disabling a builder check. `checks.json` reports no mismatches; my independent arithmetic supports that report. The remaining literal-outcome exception is described in F8.

For reproducibility I used **two in-memory processes with different `PYTHONHASHSEED` values**, without invoking the builder. Reassembling the template from the saved tables and registered values produced exactly the committed report; independently serializing and compressing the JSON rows produced exactly both committed gzip supplements; reproducing the W3 panel with the specified style and metadata produced exactly its saved PNG and SVG in both processes. The report SHA-256 was `dd3ad110d142082d02f9aa612944f36658976c19d9a5ae79e3c46b4d20f007ef`; the W3 PNG was `912698dafae4c5bd6b4e0941cb2f206d1bcc45acd824d27f57af46db722c79a9`. This confirms those bytes and the checked deterministic serialization/rendering paths. I did **not** independently repeat two complete 18-file builds; that broader historical claim remains the conductor's logged check.

The report discloses conductor, reviewer and Yichen's role. The fixture work was performed **during the run**, not before its start, as the report incorrectly says (F7). No fixture outcome is present in the study inventory or supplied study result. The original intermediate-commit disclosure was corrected in the dated log; the residual generation/null wording error is minor. The numerical interpretations questioned below are repeated in the decision log and need dated corrections there when the report is revised. R09's open Studies 1–2 crossed-bootstrap-SE side check remains outside this review and should stay on the paper's prerequisite list.

No data/model/PDF download, access-control workaround, or external posting occurred. The existing `final: false` lock and code paths remain intact. This review adds no claim about held-out data and does not substitute a filesystem audit for the agreed seal.

## 5. Independent search

Web access was available. I made a narrow update search on 2026-10-17 using the queries `watermark "per-key" calibration power after:2026-10-16 before:2026-10-18`, `watermark "across-key" "power" after:2026-10-16 before:2026-10-18`, and `watermark calibrated "unwatermarked" "model-generated" after:2026-10-16 before:2026-10-18`; I also searched combinations of calibration/key, power/dispersion and false-positive/unwatermarked with arXiv/OpenReview domain restrictions. Returned results were irrelevant, secondary, or older; their crawl dates did not establish new publication dates. I found no verifiable new primary work in that interval that changes this review. This limited, noisy search is not evidence of novelty or an exhaustive literature clearance. The decisive priority check above rests on the existing local primary papers, not the search snippets.

## 6. Findings and recommendations

### F1 — Major: the abstention inventory omits the model-null block and its positive-index zero

**Evidence.** Report §1 says “2160 settings carry abstaining keys,” and Table 17 reports only structural zeros among the power rows. `s4_report.py` builds that summary from `descriptive_rows` alone. The number is correct for those rows but is incomplete for the report's full threshold inventory. `null_rows`'s `keys_at_zero` counts zero observed detections; it is not a threshold-abstention count and has no abstention-kind field.

Reading the committed Qwen thresholds through `s4_record`, I found 480 distinct structural-zero threshold settings (480,000 key-threshold pairs), applied in **4,320 model-null rows** across three cells and three lengths. There is also one **positive-index** zero: source `gutenberg_en_1024`, h = 1, Gumbel/raw, `conformal@1000`, alpha = 0.001, order index **j = 1**, key **23626**, threshold **0**. It appears in nine model-null rows. This key is outside the power subset, explaining why the power-only summary misses it. It is a committed zero, not a new result to repair. Protocol §7 expressly requires abstentions by setting, kind and order index.

**Recommendation.** Keep all locked files unchanged. Add a labelled builder-derived null-abstention supplement from the committed thresholds, with row identity, key count, structural/positive-index kind, j, and the key identity for the singleton. Separate the 2,160 power-row count from the 4,320 structural and nine positive-index null-row counts, and define “setting” so repeated applications are not mistaken for distinct thresholds. Verify the affected counts remain zero and explicitly state that these thresholds were not repaired.

### F2 — Major: complete the promised-output audit trail and the missing W1 fields

**Evidence.** Protocol §6 requires realised and predicted key-means beside every W1 row, and §7 requires the predicted-median cluster-bootstrap **SE**, interval and tolerance. Table 3 supplies the interval and tolerance but omits the SE and both key-means, even though the values exist in `INPUTS.json/W1_tolerance` and `results.json/W1.rows`. The SEs are 2.580873, 3.171910 and 2.884957 pp for news, Wikipedia and Stack Exchange respectively.

Table 7 lists all five unresolved W3 rows but does not show sigma_E-squared, sigma_C-squared, shared-tuple count, v_raw, j, or the predicted finite-evaluation/population shares. Those data **are present in the full null CSV**; I am not alleging missing underlying analysis. Tables 4–5 likewise show both raw two-way components, observed variances/SDs and proxy SDs/noise, but not the raw corrected binomial-proxy variances explicitly promised by §7. The full descriptive rows retain those values. There is no report checklist mapping every §7 item to its exact table/supplement fields; Table 17 is an integrity table. This leaves the reader to reconstruct whether the promises were met from a large raw CSV or JSON.

**Recommendation.** Add the missing W1 columns directly. Add a compact W3 unresolved-row diagnostic supplement and explicit W2 proxy-component columns or a clearly keyed supplement. Include a generated §7 checklist that names every promised item, its estimand/denominator, and its exact destination, including complete length/transfer/calibration-size results that are intentionally not in the selected main tables. A supplement is sufficient; no expansion of the locked analysis or new study is required.

### F3 — Minor: captions obscure different key sets, units and scoring windows

**Evidence.** Several table captions omit K, n and/or N₀. Table 13 combines power over **100 keys and 50 texts/key** with null levels over **all 1,000 keys and 5,000 texts**, without stating that difference. Thus news's diagonal model-null above-alpha share is 23% for the power subset in Table 9 but about 19% for the full null set in Table 13; both are correct. Table 9 also omits the **10,000 corpus-text** denominator for its stored levels.

Table 15's “units” are 100 generation key-batches of 50 texts, ten null chunks of 500 texts, and 1,000 individual human continuations. Its perplexity is a mean of unit-level exponentiated mean log-probabilities, over 256 generated tokens versus 192 human tokens; only the separately reported first-192 log-probability is matched in window. Its loop-share entries are percentages, but the heading has no percent unit. Table 10 repeats the hook's full-256-token green share at each detector length/rule without stating that its window is fixed. The length and transfer summaries are assembled by the builder but their captions do not identify that provenance as clearly as the operating-point/mechanism/remedy/pairing blocks do.

**Recommendation.** Make every substantive table caption self-contained: state the relevant key set, text denominator, calibration size, window, units and builder provenance; use “not applicable” where K/n/N₀ do not apply to an administrative table. Label the mixed populations in Table 13 and the batch sizes/aggregation and percent unit in Table 15. State that Table 10's green share always uses all 256 tokens. Clarify that Figure 6 sorts each series separately. These are presentation changes; the checked numbers are correct.

### F4 — Major: small high-strength costs are reported as no visible cost

**Evidence.** Report §8, line 680, concludes “on 256-token texts at that strength no calibration cost is visible”; line 692 repeats “at δ = 2.0 no cost is visible,” and the decision log repeats it. The same paragraph reports a largest mean cost of 0.8 pp. At the stated primary alpha and diagonal sources, all 72 high-strength cell/rule/variant rows have key-mean power at least **99.18%**, but the largest mean cost is **0.76 pp**, not zero. Wikipedia/raw's empirical row has a **4 pp 95th-percentile per-key cost**. Saturation of the mean does not establish absence of a per-key cost, and the final sentence also drops alpha/source qualifications.

**Recommendation.** Say that power is near saturation and measured mean costs are small at h = 1, delta = 2.0, L = 256, alpha = 0.01 and the diagonal sources. Report the generated mean-cost range or maximum alongside a per-key upper quantile, and avoid either a zero-cost implication or an equivalence claim. Carry a dated correction into the decision log and use that bounded statement at Stage 7.

### F5 — Major: “nearly binary” does not describe the measured generated-null levels

**Evidence.** Report §8, line 688, interprets the h = 0/raw results as “the nearly binary per-key levels Studies 1 and 2 found on human text, here on generated text.” The decision log repeats that conclusion. Directly from `results_arrays.npz`, at L = 256, alpha = 0.01, nominal threshold, the 25th/50th/75th percentiles of the 1,000 per-key levels are:

| Cell | 25th | Median | 75th | Keys with level at least 95% |
|---|---:|---:|---:|---:|
| News | 0.655% | 3.10% | 12.165% | 0 |
| Wikipedia | 1.015% | 4.42% | 15.00% | 1 |
| Stack Exchange | 3.160% | 6.65% | 13.375% | 0 |

Respectively 417, 475 and 598 keys lie strictly between 5% and 95%. Their observed variance is only about 0.275, 0.259 and 0.131 times the Bernoulli variance with the same mean. The distributions are highly dispersed and skewed, but this record does not demonstrate near-binary levels. The earlier studies are outside scope; their wording cannot establish the shape of this new distribution.

**Recommendation.** Replace this with a measured description of broad/skewed across-key variation, supported by generated quantiles or an empirical CDF/histogram. If a comparison with earlier near-binary behaviour is wanted, define and evaluate a common descriptive criterion rather than carrying over the label. Correct the repeated interpretation in the decision log; leave the locked null rows and W3 verdict unchanged.

### F6 — Minor: tighten the conditional-target and mechanism interpretations

**Evidence.** Report §2, line 46, defines the W2 target as a variance functional and then calls the interval an interval “for that target”; the interval is for the **SD ratio R(D)**, as correctly distinguished in protocol §3/R09 F24. Section 8 calls 181 finite resamples “at the availability bound,” but the bound is 180. It also says a design resolving W2 “would need more prompts per key or an interval construction with a prompt channel.” That necessity/sufficiency claim is not established: the evaluated prompt-channel alternatives address population uncertainty and were wider, not demonstrated cures for resolution of this conditional ratio.

The mechanism paragraph, line 684, correctly labels the correlations descriptive, but then asserts that colouring likely tokens yields a larger green share “so the null shift and the watermark strength co-vary.” A full-text green-share/null-level correlation does not separately identify a key-specific watermark effect relative to its unwatermarked baseline. The conclusion appropriately calls this a hypothesis; the local explanatory sentence should do so too.

**Recommendation.** Name R(D) explicitly where the interval is introduced, say 181 is one above the availability threshold, and describe prospective larger designs/alternative targets as possibilities requiring their own evaluation. Make the mechanism sentence “consistent with the hypothesis that …” and preserve the distinction between green-share association and an identified strength covariance. No redesign of the current locked study is requested.

### F7 — Minor: correct the fixture chronology and residual provenance descriptions

**Evidence.** Report §1, line 9, says the builder “was tested before the run.” The run began at `02:13:52Z`; the fixture's first commit is `fc57ffb` at `02:26:13Z`, the builder commit is `3c812cd` at `02:56:56Z`, and the fixture-check commit is `6cc37b1` at `03:22:52Z`. The prompt and decision log correctly describe work during the run and before real outcomes were read. The earlier-file disclosure's 47 “generation units” also includes ten null chunks, as described above.

There is a smaller manifest parsing gap: `s4_manifest.py:96` expects a separate `vm.swapusage` line, but the actual launch note embeds `swap='...'` in the launch line, so its structured `swap_at_launch` is empty despite a recorded launch value of 1,739.31 MB. The command is not in the launch notes, so an absent structured command must not be presented as verified from that source.

**Recommendation.** Change the report's fixture claim to the accurate during-run chronology, attributing “before real outcomes were read” to the recorded process. Correct the generation/null composition in current orientation/handoff descriptions without rewriting history. If the manifest is refreshed, parse the actual launch swap format and preserve explicit unknowns for unavailable command metadata. Keep the watchdog near-miss attributed to the dated log. These corrections do not alter the lock or record integrity.

### F8 — Minor: the “every outcome generated” statement has literal exceptions

**Evidence.** `report_prose_v0.1.md` hard-codes **“0 mismatches”** in the opening paragraph and **“none agrees and none disagrees”** in the W2 reading, although nearby counts use registered placeholders. Both are true at this baseline. The builder's mismatch refusal protects the first in successful builds, but neither is literally a generated count as the report and process claim. Fixed design constants, section numbers and rule thresholds are not the problem.

**Recommendation.** Register the mismatch count and express the W2 agree/disagree counts through generated values or a generated clause. Keep judgement prose separately authored, and check the template for outcome counts in both digits and words. This is a process correction, not evidence that any present numerical result was fabricated.

The paper and claim gate can use the reproduced measured costs, their per-key spread, both null-law operating points, W2's unresolved conditional result, and W3's conditional adequacy result after these reporting corrections. The supported interpretation is narrower than absence of high-strength cost, near-binary generated-null levels, or an identified null-shift/strength covariance. I recommend closing F1, F2, F4 and F5 before Stage 6 exit, with the minor corrections above in the same report revision. The existing lock and analysis should remain untouched.

VERDICT: REVISE
