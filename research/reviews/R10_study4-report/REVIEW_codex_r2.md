# R10 — Study 4 report: independent review, round 2

Reviewer: Codex. Date: 2026-10-17 UTC. Conductor: Claude Code.

**Recommendation: AGREE for this bounded re-review.** The four major round-1 findings are resolved, and the locked record and registered verdicts are unchanged. Two minor reporting corrections remain below, F9–F10; neither requires a new analysis or changes a result. One corrects an overbroad description in my own round-1 memo as well as the regenerated caption.

## 1. Baseline and scope read

Baseline: `main`, **`080086a379f7b40c8a617706b718fdb97ea79f97`**. The working tree was clean at the start. The report fixes are at `354cd02`; comparison baseline is `4b10360`.

I read the conductor's response first, followed by the specified regenerated report sections, captions and Tables 3, 5, 7, 18 and 19; the diffs of `s4_report.py`, `report_prose_v0.1.md` and `s4_manifest.py`; the round-1 decision-log entry and dated corrections; the handoff and the orientation in full. I also checked the appended round-2 prompt, the relevant protocol promises, committed inputs/results/arrays, report tables/values/checks and CSV headers/counts, and the locked human-reference calculation where needed to verify the revised quality caption.

This is a review of the F1–F8 dispositions and the unchanged evidence, not a reopening of R09's design or the prior studies. I used only short read-only checks, with Python bytecode writing disabled and execution alarms. No model, builder entry point, runner or analyzer entry point was run. No download, holdout access, commit, or change to an existing file was made. Only this memo was written; computation finished before the restricted window.

## 2. Claims against evidence

### Unchanged lock, record, verdicts and figures

The requested path-specific `git log --oneline 4b10360..HEAD -- ...` produced no entries. I extended that history check to all 32 pinned paths, the lock and R09's resolution; it was also empty. The protected paths have no working-tree diff against `4b10360`. All 32 pinned files again matched their lock digests under `shasum -a 256`, and all 1,860 Study 4 record files matched the manifest's exact file set and hashes. `s4_record.Record()` also verified Study 3's committed record before returning thresholds.

| Object | Current SHA-256, unchanged from the reviewed record |
|---|---|
| `PRE_RUN_LOCK.json` | `7067b4e1457c7ed977a311409914e3034721993eae5eddc44f6934c8d1b4cdd9` |
| `results.json` | `5ee9842146d8c6171c21902ca56e0e06a7441eaa433d81844380d5b34d6cfc9e` |
| `results_arrays.npz` | `efa16831a3bd53e812fc48a7d32c97676b778c548043904f326426bd78ab8783` |
| `RUN_MANIFEST.json` | `dd647449b4f75289fe4e608332635eb9f4298c374a8c8b76fda8062bca16cbe7` |

The PNG diff against `f49f676` is empty, and direct comparison of each current PNG's bytes with its Git blob confirmed equality for all six figures. The analysis and its classifications remain **W1 PASS: 2 consistent, 0 inconsistent, 1 unresolved; W2 FAIL: 0 agree, 0 disagree, 6 unresolved; W3 PASS: 240 candidate, 221 eligible, 216 resolved and consistent, 0 inconsistent, 5 unresolved**. The round-1 independent derivations therefore still apply; I did not unnecessarily rerun those bootstraps.

### F1 — Null abstentions: resolved

I enumerated the committed same-tokenizer thresholds through `s4_record` over source, width, family, rule, method/calibration size and alpha. I independently recovered **480 structural settings and one positive-index setting**, and matched every grouped row of Table 18: 16 structural groups of 30 settings each, plus the singleton. Each structural group spans ten sources and three widths and enters 270 model-null rows.

The positive-index setting is exactly `gutenberg_en_1024`, h = 1, Gumbel/raw, conformal@1000, alpha = 0.001, j = 1, key **23626**, threshold zero. I checked the actual count arrays, not just the JSON summaries: every one of the **4,320 structural rows** is all-zero, and key 23626 has zero counts in all **nine** affected positive-index rows. The structural-row summaries also have `keys_at_zero = K = 1000`, mean zero and SD zero. This independently confirms `checks.json`'s `null_abstention_rows_all_zero: 4320` and additionally verifies the singleton's affected counts.

The separate **2,160 power-table rows** with abstentions are all structural, j = 0, at alpha = 0.001. Section 1 and Tables 17–18 distinguish power rows from distinct null threshold vectors and define the latter's repeated application across cells/lengths. No zero threshold was repaired. F1 is closed.

### F2 — Added diagnostics and checklist: resolved, with a minor locator typo

I compared the displayed new fields at their stated rounding with their sources:

- All three Table 3 realised/predicted key-means and predicted-median SEs match `results.json/W1.rows` and `INPUTS.json/W1_tolerance`. The pre-lock SEs are 2.580873, 3.171910 and 2.884957 pp for news, Wikipedia and Stack Exchange respectively.
- Both added raw corrected binomial-proxy variances match `W2.rows[].binomial_proxy` in all six Table 5 rows.
- All seven added diagnostics—v_raw, sigma_E-squared, sigma_C-squared, shared-tuple count, j, and both predicted above-alpha shares—match the five relevant W3 rows in Table 7. All unresolved rows are present; there are no inconsistent rows to omit.

Table 19 covers all 13 protocol §7 items. Its entry counts agree with the actual destinations: 18 operating-point rows, 54 mechanism rows, 36 length rows with three lengths, 60 transfer rows, 72 contrast rows, 12 generated/null quality rows plus three human-reference rows, 18 pairing series, three W1 rows, six W2 rows and five unresolved W3 rows. The complete supplements retain 16,524 descriptive and 33,048 null rows; the latter comprise 32,400 calibration-source rows and 648 fixed-threshold rows, including 16,524 Gumbel rows. The checklist explicitly distinguishes selected main tables from complete supplements. Its residual-mean-square field locator is misspelled (F10); the underlying field and data are present. The major omission in F2 is closed.

### F3 — Captions and key-set labels: substantially resolved

I checked the captions of Tables 1–17, the revised column headings and Figure 6. The consequential ambiguities are corrected: Table 9 names the 100 power keys and both 10,000/5,000-text null denominators; Table 13 explicitly combines 100-key power with 1,000-key null summaries; Table 14 states N₀; the length/transfer blocks identify the builder's summaries; Table 10 labels the green share's fixed 256-token window; Table 15 identifies key-batches, null chunks, human continuations, windows and percentage units; Figure 6 says each series is sorted separately. The corresponding 100-key versus 1,000-key labels now accompany the operating-point and transfer shares in §8.

The response's claim that *every caption* states every denominator/window/provenance detail is stronger than the literal text: for example, Table 10 still relies on surrounding material for n = 50 and the stored-null N_E = 10,000, while Table 4 gives K in its rows. These do not recreate the mixed-key-set ambiguity, but a common caption cross-reference would make the remaining summaries self-contained (F10). More importantly, the newly explicit generic perplexity aggregation needs a human-reference exception (F9). The principal F3 fixes stand; these residuals are minor.

### F4–F5 — Revised numerical interpretations: resolved

I selected all **72** high-strength rows from the unchanged `results.json` at h = 1, delta = 2.0, L = 256, alpha = 0.01 and diagonal sources/fixed thresholds, including every calibration size. The minimum mean power is **99.18%**, maximum mean cost **0.76 pp**, maximum 95th-percentile per-key cost **4.0 pp**, and **28** rows have positive 95th-percentile cost. These match the registered values and revised prose. The full sentence names its scope, calls power near saturation, and explicitly rejects absence of per-key cost. F4 is closed; retain those setting qualifiers when excerpting the conclusion for the paper.

For F5 I recomputed directly from the h = 0/raw/nominal/L = 256/alpha = 0.01 arrays:

| Cell | Quartiles of per-key levels (%) | Keys strictly between 5% and 95% | Keys at least 95% | Variance / Bernoulli variance at the same mean |
|---|---|---:|---:|---:|
| News | 0.66 / 3.10 / 12.17 | 417 | 0 | 0.28 |
| Wikipedia | 1.02 / 4.42 / 15.00 | 475 | 1 | 0.26 |
| Stack Exchange | 3.16 / 6.65 / 13.38 | 598 | 0 | 0.13 |

Every formatted value matches `prose_values.json` and §8. The broad/right-skewed description is supported; the report no longer asserts near-binary generated-null levels or identifies the cause of the difference from earlier studies. F5 is closed.

### F6–F8 — Wording, chronology and generation: resolved in substance

The W2 interval is now expressly for **R(D), the SD-scale ratio**, on its positive-denominator domain. The generated availability threshold is **180** and the observed minimum finite count remains 181. Future prompt samples or prompt-channel constructions are possibilities needing their own evaluation, with the wider population-target alternatives distinguished. The mechanism sentence now says “consistent with the hypothesis” and explains why the green-share association does not identify a key-specific watermark effect. These changes close F6 without altering the design.

The fixture sentence says “during the run” and points to the recorded chronology; the orientation and dated log correctly identify 37 generation units and ten null chunks in `6cc37b1`, plus eight generation units in `f31dcad`. “Before any real outcome was read” remains the conductor's recorded process statement, not something commit timestamps alone can prove.

I evaluated only the modified manifest metadata expression in memory. Against the actual launch lines it recovers `used = 1739.31M` from the embedded swap text, keeps the absent command as `None`, and supplies the explanatory note. An explicit `vm.swapusage` line takes precedence, and an explicit command suppresses the missing-command note. I did not invoke the manifest writer. The committed manifest remains unchanged with its original null structured fields and complete launch line. F7 is closed.

The original hard-coded “0 mismatches” and “none agrees and none disagrees” are absent from the template and now supplied by registered values. Their values match the checks and W2 counts. In-memory substitution of all saved tables, figures and **331 registered values** reproduces the report exactly, with no unresolved placeholders; SHA-256 is `0a04f09699d0aee3eecba75eec8333f83ac8d0fb0b100ad13fb85586d33a90aa`. This checks assembly, not a fresh complete builder execution. F8's two identified exceptions are fixed; one newly introduced literal availability-count word is noted in F10.

### Literature and wording constraints

The relevant attribution and limitations remain unchanged. I again located AutoMark's **“any scheme that is sound over the key becomes sound given a key”** in `research/literature/txt/2609.37310.txt`, PDF p. 29, and Genhatharan's **“Operating point of each detector key at 512 tokens before and after per-key calibration”** in `research/literature/txt/genhatharan_nominal_fpr_2026.txt`, PDF p. 11. The report still names Genhatharan §IV-H/Figure 10 and AutoMark Appendix C, retains Proposition 1's prerequisite, distinguishes the empirical plug-in, and makes no new priority claim. The revisions do not add a theorem, transfer guarantee, population confidence claim, or claim about other models, attacks, languages or Gumbel generation power.

## 3. Method and statistics

No statistic, bootstrap, threshold, tolerance, eligible set, rule boundary or pass condition changed. The corrections are derived reporting and interpretation changes. W1 remains conditional on the pre-lock pilot law; W2 remains a nominal key-bootstrap interval for the prompt-conditioned ratio, with its validator-coverage caveat; W3 remains a conditional adequacy check on shared generated samples, not independent source-row replications or nominal validity on generated text. Zero thresholds remain zero, including the positive-index singleton.

The existing six figures are unchanged, so their round-1 visual review still applies. Their new caption clarifications do not alter the plotted data. Exact interval/byte reproduction remains an implementation check rather than evidence of coverage. No additional simulation or model run is warranted to resolve the two minor issues below.

## 4. Process and consistency

The dated decision-log corrections withdraw the no-cost and near-binary descriptions and correct the fixture timing and early-commit composition. The handoff's current results paragraph reflects the corrected interpretation. The watchdog near-miss remains attributed to the conductor's historical account. The current lock still has `final: false`; the review made no claim about, and did not access, the held-out partition.

The substantive changes remain on the unpinned report path; the manifest script's parser fix has not rewritten the historical manifest. I verified current report assembly and unchanged PNG bytes, but did not independently repeat the conductor's two complete 18-file builds in this round. That broader check remains the conductor's logged measurement. There was no network/download activity or outward action in this re-review.

## 5. Independent search

No fresh web search was performed in this bounded, same-day re-review. Web access was available; this is not an access-gap claim. The round-1 limited update search and its explicit non-novelty limitation stand. The local primary-source passages above were rechecked because the attribution constraints remain relevant.

## 6. Remaining findings — both minor and non-blocking

### F9 — Minor: distinguish pooled human-reference perplexity from the mean over generated units

**Evidence.** Table 15's revised caption and heading (`research/STUDY4_REPORT_v0.1.md:605–607`, generated from the template and builder) apply “the mean over units of exp(−mean log-probability)” to both generated and human rows, while defining human units as single continuations. The locked human-reference code instead computes `ppl = exp(-lp[fin].mean())` across the pooled human-token array (`research/study4/s4_inputs.py:109–112`). Generated/null rows average the exponentiated means of their respective key-batches/chunks. These aggregations are different.

For example, the news human reference has `mean_logp = -2.4533772468566895` and stored `ppl = 11.627549171447754`, agreeing with the pooled exponential up to float32 rounding. Its per-text mean-log-probability quantiles differ, so a mean of per-text exponentials cannot be equated to that pooled exponential. Wikipedia and Stack Exchange use the same pooled calculation. No displayed value is wrong, and no quality exclusion or inferential claim follows from this table.

**Reviewer correction.** My round-1 F3 description was itself overbroad about the human aggregation. The correction applies to that description too; the generic mean-over-units wording should not have been extended to the human reference.

**Recommendation.** Qualify the caption/header: generated/null perplexity is the mean of unit-level perplexities (key-batches/chunks); human-reference perplexity is the exponential of the pooled mean log-probability over the 1,000 × 192-token continuations. Keep all locked values unchanged and retain the matched first-192 log-probability comparison. This is non-blocking because it is a descriptive label correction with no change to the record, verdicts or quality conclusions.

### F10 — Minor: finish the exact field locators and small generated-metadata details

**Evidence.** Table 19 names `ms_resid` as a column of `descriptive_rows_full.csv.gz` (`research/STUDY4_REPORT_v0.1.md:696`; source `research/study4/s4_report.py:537`). The actual column is **`ms_resid_twoway`**; `ms_resid` is absent. The data exist and were checked. Its quality destination would also be more exact as `results.json/quality`, `INPUTS.json/human_reference`, and values derived from the unit NPZ bodies, rather than implying every summary is stored as a scalar in the unit JSON. Table 10 still relies on surrounding text for n = 50 and stored-null N_E = 10,000. The orientation's Study 4 description still says 17 tables, although this report/checklist contains 19. Finally, the template's availability sentence hard-codes **“one above”** while its operands 181 and 180 are generated; the statement is true but that outcome-derived gap is not generated.

**Recommendation.** Correct the residual-field name and quality destinations, add the short Table 10 denominator cross-reference, update the current orientation's table count, and generate the availability gap or simply say “above the availability threshold.” These are mechanical documentation fixes for the next report/resolution update, not reasons for another study run or another substantive review round. Do not rewrite the locked record or historical manifest.

There is no remaining blocking or major finding in this re-review. F1, F2, F4 and F5 are closed; the original F6–F8 fixes are verified; the consequential F3 ambiguities are corrected with the minor human-reference exception above. The report is suitable for Stage 6 exit with F9–F10 recorded for the ordinary reporting cleanup and with the existing inferential limits retained.

VERDICT: AGREE
