# R06 — Study 2 report: independent review, round 3

Date: 2026-10-13. Reviewer: Codex. Baseline: `main`, `f0a65cbfd44c286bdcdd2bd38c1701e2edc44e7d`. Comparison baseline: round 2, `9db4bd5da6af86399ff90c6ebb70ff94c5361bdb`.

**Recommendation: AGREE for this bounded review.** F9–F11 are closed: the complete diagnostic supplement agrees with the cells, the corrected S4 counts and qualifications reproduce, and the medians now use their stated denominators. F12's specifically requested S1 substitutions and dated correction are implemented. A minor generation-discipline residual remains: three outcome-count phrases are still literal words in the template. Their current values are correct; I recommend the small cleanup specified below without another substantive review round. No blocking or major finding remains open.

## 1. Baseline and what was read

I followed the requested sequence: the conductor's round-2 response; the specified portions of the regenerated report; the new `tables_pairwise_full.md`; the builder and template changes since `9db4bd5`; and the decision log's round-2 entry. I checked these against the round-2 findings, the orientation, the locked grid and relevant analysis rules, the saved cells, `results.json`, the lock and manifest, and the generated prose values. The earlier full review of the experiment remains the baseline; this round is bounded to F9–F12.

The working tree was clean at the start. All computations were short, read-only local checks with bytecode writing disabled. I did not run the canonical report builder, the study grid, the overlap generator or a new bootstrap; download anything; or access held-out texts. This memo is the only file written.

## 2. Claims against evidence

### Complete pairwise/heterogeneity supplement

I independently reconstructed the expected filenames from the locked grid and matched them to **3,468 live cell files**. All have `N_eff = N = 10,000`, `K = 1,000`, and no FIXTURE marker. Recomputing the inventory digest gives the manifest's `f3b4a0ceb246c0154903d7b99fb55f28999fa4e50ef2aabf24b1e626d9ac6766`.

The new supplement contains exactly **10,404 unique (cell file, alpha) rows**, with no missing, duplicate or extra pair: every expected cell at each of 0.01, 0.05 and 0.001. I checked **all 21 columns of every row**, rather than only a sample. The observed SD was recomputed from the integer rejection counts; predictor ratios and the absolute subsample-SD difference were recomputed; the remaining diagnostics were traced to their saved fields. Every displayed value agrees at the report's formatting precision.

This includes both pairwise predictions, the simulated-shift prediction where available, first-subsample covariance mean/CV and correlation quantiles/maximum, replicate CV, zero-variance share, theory share, and model/observed residual variance. The caption correctly identifies which heterogeneity fields belong to the first subsample and which replicate field is shown. Fixed-colouring cells correctly show no simulated-shift value.

The previously omitted example, `wikipedia_zh_256__llama__kgw__h4__independent__g0.25__L128__raw.json`, now appears at all three alpha values. At alpha = 0.01, its pairwise SD **0.0010565124144850412** renders as **0.106 pp**, and its covariance CV **33.49143221648193** renders as **33.5**. Its replicate SD, replicate CV and other columns also match. The builder iterates over every live cell and alpha and checks row/cell coverage; my independent set comparison additionally verifies uniqueness and exact membership. The report names the supplement in its header and diagnostics paragraph. F9 is closed.

### S4: observed-SD tolerance, rho sequences and overlapping groups

I reconstructed all 100 primary raw-rule chains directly from the cells and applied the registered condition to each adjacent length:

`SD_next >= SD_current - 2 * (SE_current + SE_next)`.

The decisions match the saved analysis: **76 holding, 24 failing**. Among the independently selected holding chains, **61** have non-decreasing `rho_bar` at every step and **15** have a decrease somewhere. This is a separate descriptive count, not a replacement for the registered SD rule.

The report's counterexample reproduces: news/Qwen at h = 2 has rho **0.0384810404 → 0.0273685938 → 0.0253544128**, while its SD is **0.790696276 → 0.816172113 → 0.787029738 pp**. The latter sequence holds within tolerance. The revised Q3 no longer infers growth of shift dispersion from the holding decision.

The failure sets have sizes **18 h = 4**, **6 news**, and **2 non-news h = 1**. Their union is exactly the 24 failing chains; their 26 memberships include the same two news h = 4 chains twice. Both §5 and Q3 now state this overlap.

The maximum theory share at L = 64 or 128 over the **16 non-news failing h = 4 chains** is **0.4672125970**, consistent with the displayed 0.467. The two news chains are correctly excluded from that account:

| News h = 4 | Theory share at L = 64 | Theory share at L = 128 |
|---|---:|---:|
| Llama-3.2 | 0.7799817533 | 0.6571700546 |
| Qwen2.5 | 0.8770642959 | 0.8062009483 |

These render as 0.780/0.657 and 0.877/0.806. The revised discussion explicitly attributes the decomposition to the predictor and calls the lattice explanation plausible, rather than an identified decomposition of observed variance. S4 remains FAIL as registered. F10 is closed.

### Median denominators and paired comparisons

I independently selected the relevant blocks and recomputed eligibility and interval-based status from the cells. These match `results.json`. The resulting denominators and medians are:

| Block | Eligible n | Eligible median | Resolved n | Resolved median |
|---|---:|---:|---:|---:|
| Primary | 217 | 1.233656107 | 184 | 1.211648473 |
| Alpha = 0.05 | 315 | 1.078146540 | 315 | 1.078146540 |
| Alpha = 0.001 | 94 | 1.573997196 | 60 | 1.721958177 |
| Gamma = 0.5 | 353 | 0.983808447 | 348 | 0.983513966 |
| Gumbel raw/distinct | 335 | 1.457564091 | 195 | 1.329975723 |
| Gumbel first | 78 | 1.531626891 | 49 | 1.647002106 |

The unit-sigma block's stated resolved median is also correct: **1.318941145** over **195** resolved cells, from 213 eligible cells.

On the **same 217 eligible primary cells**, common-factor/pairwise/simulated-shift medians are **1.233656107 / 1.196828341 / 1.192436899**. On the **same 184 resolved primary cells**, they are **1.211648473 / 1.174939253 / 1.182859239**. Thus the revised comparisons 1.23/1.20/1.19 and 1.21/1.17/1.18 are accurate and no longer mix selection sets.

Section 5 identifies the Table 5 medians as resolved-subset medians and supplies eligible medians for the principal contrasts. Q2 states the corresponding denominators. Alpha = 0.05 is now described as a smaller discrepancy, rather than no discrepancy. The H-domain heading says the cross-language correlations depend on tokenizer and pair. F11 is closed.

### Generated prose and dated correction

All eight changed template lines, after substitution using `prose_values.json`, occur exactly in the rendered report. No unresolved placeholder remains. In particular, §6 Q2 and §8 item 1 now use `[[s1_inconsistent]]` and `[[s1_unresolved]]`, rendering **6** and **33**.

The squared resolved primary median is **1.4680920219299531**, rounding to **1.47**. The round-2 decision-log entry explicitly corrects the previous entry's 1.46 and preserves the earlier entry as history. The correction is accurate.

I cannot, however, confirm the broader response/log statement that no literal outcome count remains anywhere in §§5–8. The remaining worded counts are detailed under F12 below. This does not invalidate any displayed numerical result.

## 3. Method and statistics

The corrections preserve the distinction between a registered observed-SD decision and a mechanistic explanation. The 61/15 split is explicitly descriptive; it neither strengthens the tolerance criterion nor changes its failure count. Restricting the finite-text account to the supported non-news subset, with the predictor's approximation stated, resolves the substantive inference problem identified in round 2.

The medians now compare like selection sets. They remain descriptions of dependent cells sharing texts and keys, not independent replications, causal contrasts across gamma/alpha, or universal correction factors. The complete diagnostic table exposes low-theory-share and otherwise ineligible cells instead of conditioning their visibility on an adequacy failure.

This review validates the new presentation against saved statistics; it does not re-estimate subsample predictions or bootstrap intervals from a rejection matrix. The agreed design, precision limitations and earlier verification of S1–S5 remain unchanged.

## 4. Process and wording constraints

All **15 pinned file hashes** and the R05 resolution digest match the lock. Their path-specific history has no change after `b0e0036`. The requested combined history has no record or PNG edit after **`61fda20`**. A direct working-file comparison with that commit gives no difference for the cells (including cost records), `results.json`, `RUN_MANIFEST.json`, `run.log`, `run_stdout.log`, `launch_notes.log`, the specified locked protocol/code, or the PNGs. All **six PNGs are individually byte-identical** to their `61fda20` versions. The lock's `final` flag remains false.

The revised header accurately calls this build an answer to round 2's REVISE, not an approval. The changes remain on the unpinned reporting path; no registered rule, recorded outcome or figure PNG changed. S1 PASS, S2 PASS, S3 PASS, S4 FAIL and S5 PASS therefore remain the previously verified decisions.

No new literature or priority claim is needed for F9–F12. For the orientation's quotation check, I reconfirmed the existing local substrings: Jovanović, `2506.16349.txt`, PDF p. 27, “vocabulary may introduce a particularly biased split”; Gloaguen et al., `2509.24368.txt`, p. 21, “over 100 different keys”; AutoMark, `2609.37310.txt`, p. 4, “soundness given a key”; and Genhatharan, `genhatharan_nominal_fpr_2026.txt`, p. 1, “Per-key, per-length empirical calibration”. The narrowed headings add no transfer guarantee, theorem, remedy, population extreme or priority claim. No new terms-of-use or holdout issue arose from these local checks.

## 5. Independent search

I did not repeat the optional literature search in this bounded correction review. The earlier search record and its limitations stand. No inference about absence of newer work or novelty is made here.

## 6. Findings and dispositions

### F9 — Previously major; closed

**Evidence:** exact grid coverage and all 10,404 rows independently verified, including the formerly missing cell and both pairwise subsamples. **Recommendation:** retain the supplement and its coverage check.

### F10 — Previously major; closed

**Evidence:** 76/24 decisions, the 61/15 rho split, 26 memberships over 24 failures, the 16-chain non-news subset and the news theory shares reproduce. The prose now separates the tolerance decision from the plausible mechanism. **Recommendation:** preserve the registered FAIL and the post-hoc qualification of narrower length hypotheses.

### F11 — Previously minor; closed

**Evidence:** the stated eligible/resolved medians and the alternatives' comparisons on matching sets reproduce; alpha = 0.05 and the H-domain headline are appropriately narrowed. **Recommendation:** keep these denominators explicit when moving results into the paper.

### F12 — Minor, non-blocking residual: the requested substitutions are fixed, but a few worded outcome counts remain

**Evidence:** the two locations identified in round 2 now use generated S1 values, and the dated 1.47 correction is correct. However, `research/study2/report_prose_v0.1.md:149` still contains “The two h = 4 chains that hold” and “the four failing chains”; line 179 still contains “two further h = 1 chains”. These phrases also appear in the rendered report (§5 and §8 item 2). The words **two**, **four** and **two** describe observed chain outcomes, rather than fixed design parameters. They are correct for the saved experiment, but are literal counts despite the stronger generation claim.

**Recommendation:** derive the first two counts from the corresponding holding/failing sets, or remove the redundant count words; use the existing `[[s4_fail_h1_nonnews_n]]` in §8 item 2. Do not describe the template as free of literal outcome counts until that cleanup is applied. This is a small residual of F12, not an analytical defect or a reason to rerun the experiment. No further substantive review round is needed for these substitutions.

The substantive reporting and interpretation residuals are resolved. The remaining F12 cleanup can be recorded in the checkpoint resolution while retaining the locked experiment and all registered verdicts.

VERDICT: AGREE
