# R06 — Study 2 report: independent review, round 2

Date: 2026-10-13. Reviewer: Codex. Baseline: `main`, `9db4bd5da6af86399ff90c6ebb70ff94c5361bdb`. Comparison baseline: round 1, `23ed55a4a8f643ce32e924023ef412b8900db75f`.

**Recommendation: REVISE, bounded to the residuals below.** The numerical corrections and new tables largely succeed. The corrected tokenizer overlap and sampled mean-score correlations reproduce, the new table rows agree with the saved cells, and the locked experiment remains intact. Two substantive parts of the round-1 findings remain open: the all-live-cell pairwise/heterogeneity output requested in F4, and categorical S4 mechanism statements within F5's scope. Neither requires changing the protocol, the recorded analysis, or a registered verdict.

## 1. Baseline and what was read

I read the conductor's response first, including its verification table, F1–F8 dispositions and two further corrections; then the requested regenerated report sections and tables, the four specified supplements, the corrected overlap script and both overlap JSON files, the builder/template changes since `23ed55a`, and the decision log's round-1 entry. I applied the orientation's memo structure and the gate constraints. The earlier full protocol/record review remains the starting point, rather than reopening the agreed study design.

I inspected the Markdown table headers and captions and parsed all data rows in the four supplements. Independent short scripts compared those rows with the stored cells, reconstructed sample token-weight vectors and correlations, and checked history/hashes. I did not invoke the canonical-writing builder or overlap script, rerun the grid, re-bootstrap the rejection matrix, download anything, or access the held-out texts. The only file written by this review is this memo.

## 2. Claims against evidence

### 2.1 Immutable record and figures

- All **15 pinned hashes** and the R05 resolution digest still match the lock. Path-specific history shows no pinned-file change after `b0e0036`; `final` remains false.
- The requested combined `git log --oneline -- <paths>` has no later record edit than `61fda20` and no later locked-code/protocol edit than the applicable lock history. Comparing the current working files with `61fda20` also gives no difference for `cells/` (including cost records), `results.json`, `RUN_MANIFEST.json`, `run.log`, `run_stdout.log` or `launch_notes.log`.
- All six **PNG files are byte-identical** to round 1. The six SVG files are not byte-identical, but their only differences are the generation date and generated element IDs/references. Parsing the SVGs and normalising those fields yields identical documents for all six. The figures' content is unchanged.
- `tokenizer_overlap_superseded_r1.json` is byte-identical to round 1's original `tokenizer_overlap.json`. The erroneous post-hoc output has been preserved rather than overwritten without a record.

Consequently the round-1 audit of S1 PASS, S2 PASS, S3 PASS, S4 FAIL and S5 PASS remains applicable to the same experiment. This round independently rechecks the changed reporting calculations; it does not claim a new production run or bootstrap.

### 2.2 F1: corrected denominator and the new overlap identity

The semantic computation now includes every token position, with ids outside the common vocabulary range counted as nonmatches. I checked all **20 tokenizer/corpus occurrence fractions** against the cached arrays. They agree with the corrected JSON, including Qwen Russian **13.796953125%**, Arabic **11.383671875%**, and Japanese **14.0089453125%**. The same-string count is now explicitly separated from the hash-overlap estimand, and the former causal claim about only 410 ids is withdrawn.

For raw retention at fixed length, each retained occurrence has document-averaged weight `1 / (N (L-h))`. Under the ideal independent colouring law,

`Cov(qhat_L, qhat_Q) = g(1-g) sum_t w_L(t) w_Q(t)`,

while the two variances are `g(1-g) A_L` and `g(1-g) A_Q`. Thus the common factor cancels in the correlation. This is a statement about the **mean green fraction**, not an identity for the FPR correlation or a calibration-transfer guarantee.

I independently counted integer unigrams/pairs, constructed their hash tuple ids from the pinned mixing formulas, formed the weight vectors, joined them by shared hash ids, and computed the dot products. I separately correlated the stored per-key `q_hat.values`. The following eight pairs of production cells cover short/long text and high/low overlap:

| Corpus cell | h | L | Shared hash tuples | Identity-predicted correlation | Observed stored-qhat correlation |
|---|---:|---:|---:|---:|---:|
| news/en@256 | 0 | 256 | 24,192 | 0.873909017 | 0.863361851 |
| news/en@256 | 1 | 256 | 25,175 | 0.398905266 | 0.387265387 |
| wikipedia/ar@256 | 0 | 256 | 2,319 | 0.171277736 | 0.160358823 |
| wikipedia/ar@256 | 1 | 256 | 1,863 | 0.038258637 | 0.005699130 |
| wikipedia/ja@256 | 0 | 256 | 3,216 | 0.065346422 | 0.095634088 |
| wikipedia/ja@256 | 1 | 256 | 2,458 | 0.004867799 | -0.012508885 |
| gutenberg/en@1024 | 0 | 1024 | 29,481 | 0.944188995 | 0.937831137 |
| gutenberg/en@1024 | 1 | 1024 | 94,348 | 0.765644493 | 0.782981173 |

All match the new overlap output, as do both shared-weight fractions in each sampled row. Across the 16 individual weight vectors, the largest absolute difference from the stored `identity_q.A` is **5.72e-17**, and the largest relative difference is **1.64e-13**. The implementation's guard is actually `1e-9 * max(1, A)`, despite the JSON label saying “relative”; these sampled values also satisfy the stronger literal relative comparison. This label does not affect the reproduced result.

The observed correlations are finite-key estimates from rounded stored qhat values. The identity and close numerical correspondence support the revised mean-score explanation; they do not establish exact equality between the empirical and predicted correlations. The report appropriately distinguishes these quantities from the level correlations and discloses the additional computation as post-hoc.

### 2.3 New tables and the conductor's two additional corrections

The following checks succeeded against the actual Markdown, not only against `checks.json`:

- **Table 3:** six explicit S1 counts by width, and the existing six counts by tokenizer/rule. Independent width counts are `(candidate, eligible, resolved, consistent, inconsistent, unresolved)` = **(136,136,115,112,3,21)**, **(136,60,51,50,1,9)**, **(136,15,14,14,0,1)** and **(136,6,4,2,2,2)** for h = 1–4.
- **Table 4 / diagnostic supplement:** 39 primary occurrences in the body match the supplement exactly. The supplement has **548 data rows**, including all **101 unit-sigma occurrences: 83 inconsistent and 18 unresolved**. I checked eligibility, status, predictor-specific ratio/interval and all four key-count fields for every row. The unit-sigma rows use their own predictor correctly. The remaining completeness issue is different: this remains a selected-occurrence supplement, not the all-live-cell diagnostic output (F9).
- **Deployer tables:** **720 data rows in 18 tables**, covering 240 cells at three alpha values. All five quantile values and their crossed interval bounds match the stored fields at the displayed precision. Each row states `1,000 / 10,000`, and each table has the numeric K/N_eff caption. The 80 body rows in Tables 16–17 agree with the full supplement.
- **Population supplement:** all **10,404 cell/alpha rows** agree with the recorded two-way estimate, its SE, predictor variance, ratio, two-SE indicator, population/conditional SD and predictor floor. I also checked `s_K_squared - MS_E/N_eff` against the recorded signed estimate. All **48 summary rows** in Table 15b reproduce.
- **Eligible population summary:** independently selecting the **217 eligible primary cells** gives median variance ratio **1.556528955**, 10th/90th percentiles **1.193634112 / 2.205162465**, **22/217** within two bootstrap SEs, and **zero** negative estimates. The correction from 544 candidates to 217 eligible cells is implemented. It is properly called a variance ratio; the squared resolved S1 median rounds to **1.47**. The decision-log entry's “1.46” is a small transcription discrepancy; the report's value is correct.
- **Key-count supplement:** all **10,404 rows** match direct counts from the saved integer levels, including level 1. There are **2,043** cell/alpha blocks with at least one zero-level key and none with a level-1 key. At alpha = 0.01, all **272** constant-level cells have all keys at zero and are exactly KGW first-rule h = 0 cells. The conductor's second additional correction is supported.
- **Table 12 / F8:** the caption now accurately identifies the sample-variance ratio and separates S3's known-mean estimator. The maximum reduction's **42.2% vocabulary coverage** and **2,695 effective support / 2.10% of V** are correctly distinguished.

### 2.4 Disposition of round-1 findings

| Finding | Round-2 assessment |
|---|---|
| F1 | Closed substantively: full denominator, preserved superseded output, distinct semantic/hash estimands, and independently reproduced mean-score overlap computation. |
| F2 | Calibration-transfer overclaim closed. The corrected pair-class/tokenizer numbers are accurate, and Study 3 transfer is explicitly hypothetical. The broad “barely across languages” headline should still be narrowed; see F11. |
| F3 | Causal identification and universal correction-factor claims withdrawn. The remaining eligible-versus-resolved median labels are inaccurate; see F11. |
| F4 | Partially closed: the new quantiles, counts, population output and unit-sigma rows pass. The all-live-cell pairwise/heterogeneity output remains absent; see F9. |
| F5 | Language-reference and Arabic-only claims corrected. S4's summary still makes unsupported mechanism/generalisation statements; see F10. |
| F6 | Closed: key-averaged inflation is distinguished from individual rates, the below-nominal counts are shown, and S2/S3 are described as audits. |
| F7 | Named attribution is now present at the phenomenon/mechanism claims. No first/earliest or unoccupied-remedy claim remains. |
| F8 | Closed: estimator label and vocabulary-support description are corrected. |

## 3. Method and statistics

The new population table is descriptive and retains signed negative estimates; it does not silently turn them into positive evidence. The main population summary and S1's squared median use related but different selected sets (217 eligible versus 184 resolved); they may be compared as rough descriptions with those denominators stated, not as equal estimands or an identity between medians.

The corrected transfer discussion now makes the necessary distinction: correlation of levels at one original threshold does not specify the error of an estimated threshold transported to another law. Within-English, cross-language and cross-tokenizer calibration remain Study 3 hypotheses, with calibration-sample and target-law uncertainty still to be measured. No remedy, power result, population maximum or real-world discrimination conclusion is established by this round.

The remaining S4 problem is not its registered FAIL or its arithmetic. It is the inference from a tolerance-based decision on observed FPR dispersion to an explanation involving shift dispersion and variance components. The stored values provide direct counterexamples to that inference (F10).

## 4. Process and wording constraints

The header correctly says round 1 returned REVISE and that this build is an answer, not an approval. The new work stays on the unpinned report path, preserves the superseded overlap result and does not change the immutable record. The unit-sigma discrepancy is still disclosed as the builder's block. AI roles, Yichen's decision authority and the restart waiver remain stated.

The named attributions address the central requirements of gate constraints **1, 3, 11, 13 and 16**. The new text separates within-text repetition from fixed-key dispersion, acknowledges the prior per-key measurements and mean-shift/tokenizer mechanisms, and claims neither priority nor an unoccupied remedy. The transfer limitation now respects **constraint 10**, and the deployer captions preserve **constraint 12**'s sampled-maximum qualification and crossed intervals. Complete bibliographic links/release details should accompany these author-year references when incorporated into the paper.

I rechecked the decisive local substrings at their recorded PDF pages: Jovanović (`2506.16349.txt`, p. 27), “vocabulary may introduce a particularly biased split”; Gloaguen et al. (`2509.24368.txt`, p. 21), “over 100 different keys”; AutoMark (`2609.37310.txt`, p. 4), “soundness given a key”; Genhatharan (`genhatharan_nominal_fpr_2026.txt`, p. 1), “Per-key, per-length empirical calibration”. These support the attribution changes without a new priority search.

The remaining process-language defect is the header's literal claim that every outcome number is inserted programmatically: new prose contains hard-coded outcome counts (F12).

## 5. Independent search

I did not repeat the optional literature search in this bounded correction review. The limited round-1 search and its limitations remain the search record. No conclusion about absence of newer work or novelty is added here.

## 6. Residual findings

### F9 — Major, residual of F4: all-live-cell pairwise/heterogeneity reporting is still missing

**Evidence.** Protocol §7 requires “The pairwise Gaussian predictor and the heterogeneity on every live cell.” Round-1 F4 explicitly identified the missing all-live-cell diagnostic table. The response adds population and key-count tables, but neither includes these quantities. `s2_report.py:616–623` still limits the diagnostic output to inconsistent/unresolved adequacy occurrences. Its **548 occurrences cover only 463 distinct physical cells**, leaving **3,005 of the 3,468 live cells** without this diagnostic presentation. The JSON record contains the values, so no experiment is missing.

For example, `wikipedia_zh_256__llama__kgw__h4__independent__g0.25__L128__raw.json` contains pairwise predicted SD **0.0010565124144850412** at alpha = 0.01 and pair-covariance CV **33.49143221648193**, but those diagnostics are not exposed by the new all-cell tables.

**Recommendation.** Generate a comprehensive diagnostic supplement keyed by cell and alpha, including the pairwise prediction and replicate plus the stored heterogeneity diagnostics. It may be separate from the useful 548-row selected-occurrence table. Verify coverage against the inventory and link it from the report. This is the outstanding portion of the already accepted F4, not a new measurement request.

### F10 — Major, residual of F5: S4's summary still turns a tolerance decision into a mechanism result

**Evidence.** Report §6 Q3 (`STUDY2_REPORT_v0.1.md:727`) says “The 76 holding chains are where the shift dispersion grew with length.” But **news/Qwen, h = 2** holds S4 while its `rho_bar` decreases **0.0384810 → 0.0273686 → 0.0253544**. Its observed level SD is **0.790696 → 0.816172 → 0.787030 pp**: it holds the registered tolerance, not strict monotonicity, and the recorded shift variance falls.

The same paragraph describes all **18 failing h = 4 chains** as a regime “where the finite-text term dominates.” Two are news chains. At L = 64 and 128, news/Llama's predicted theory shares are **0.779982 and 0.657170**, and news/Qwen's are **0.877064 and 0.806201**. Even the predictor's decomposition does not call the finite-text term dominant in those cases. Section 5's qualified discussion of the 16 non-news failing chains cannot support the broader §6 sentence. Its “so there the across-key SD is dominated” wording should also identify a statement about the approximation, not an identified decomposition of observed variance.

Finally, the listed categories overlap: **18 h = 4 + 6 news + 2 other h = 1** count 26 memberships but 24 distinct failures because two news chains are also h = 4. The registered count is correct; the explanatory grouping needs to say that explicitly.

**Recommendation.** State that 76 chains satisfy the observed-SD tolerance, without concluding that their shift dispersion grew. Restrict the low-theory-share/floor account to its supported non-news subset and label it as an approximation-based, plausible account. Name the overlap between the failure categories. Preserve the registered verdict and the post-hoc status of any narrower length hypothesis.

### F11 — Minor, residual labels within F2/F3: identify the actual median denominators and narrow the headlines

**Evidence.** Section 5 says “Each block's median describes that block's eligible set,” and §6 Q2 repeats the eligible-set interpretation. The builder computes Table 5's medians on **resolved** cells. The distinction is numerically material:

| Block | Median over eligible cells | Median over resolved cells, used in Table 5 |
|---|---:|---:|
| Primary | 1.233656107 (217) | 1.211648473 (184) |
| alpha = 0.001 | 1.573997196 (94) | 1.721958177 (60) |
| Gumbel raw/distinct | 1.457564091 (335) | 1.329975723 (195) |

The comparison “over all eligible primary cells” also places the alternatives' eligible-set medians beside the common-factor **resolved** median 1.21. Additionally, “absent”/“not at all” at alpha = 0.05 is stronger than its median ratio **1.08**; satisfying the adequacy band is not zero discrepancy. The H-domain headline “barely across languages” still generalises across Qwen's English–other median **0.233** and ja–zh correlation **0.460**, although the body now reports them correctly.

**Recommendation.** Say “resolved subset of each eligible block” for the displayed medians. Use the common-factor eligible median **1.23** when comparing the alternatives over all eligible primary cells, or compare all three on the same resolved subset. Describe alpha = 0.05 as a smaller discrepancy/all resolved cells consistent, and make the H-domain heading neutral about pair class/tokenizer. No stored value or rule needs changing.

### F12 — Minor: newly hard-coded outcome counts contradict the generation claim

**Evidence.** The new template text in §6 Q2 contains “six eligible cells inconsistent and 33 unresolved”; §8 item 1 repeats “six inconsistent and 33 unresolved.” Those are literal outcome counts in `report_prose_v0.1.md`, while the header says every number in §§5–8 is filled from a placeholder. Their values are currently correct, but the claimed generation discipline is not.

**Recommendation.** Replace the literal counts with the existing generated S1 values (`s1_inconsistent` and `s1_unresolved`) in both locations. Also align the round-1 decision-log summary's squared-median value with the report's **1.47**. These are small reporting corrections, not changes to the record of the run.

The successful recomputations stand. I recommend one bounded correction pass for F9–F12, retaining the locked files, record and S1–S5 decisions unchanged.

VERDICT: REVISE
