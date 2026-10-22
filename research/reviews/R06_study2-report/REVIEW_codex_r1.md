# R06 — Study 2 report: independent review, round 1

Date: 2026-10-13. Reviewer: Codex. Baseline: `main`, `23ed55a4a8f643ce32e924023ef412b8900db75f`.

**Recommendation: revise the report and its unpinned reporting code.** The locked record is coherent, and I reproduce the registered verdicts: S1 PASS, S2 PASS, S3 PASS, S4 FAIL, S5 PASS. I found no reason to edit the locked protocol, change these verdicts, or rerun the production grid. The outstanding issues are an actual denominator error in the post-hoc tokenizer computation, incomplete delivery of registered diagnostics, and interpretations that sometimes exceed the evidence despite their surrounding caveats. In particular, the report must not carry its present calibration-transfer conclusion into Study 3 as an established premise.

## 1. Baseline, scope, and work performed

I read the root `AGENTS.md`, the full review orientation and R06 prompt; the specified protocol sections and lock schema; the complete report and prose template; the result rules, secondary blocks and descriptive outputs; the builder, analyzer, manifest, fixture and tokenizer-overlap code; the checks, manifest, run and launch records; the relevant Milestone 4 decision-log entries and handoff; and the gate's wording constraints. I inspected the six supplements and viewed all six PNG figures. I also checked the relevant Study 1 passage and local literature passages below.

Checks were read-only, short local computations, except for writing this memo. I did not run `s2_run.py`, invoke the report builder in its canonical-writing mode, change any other file, commit, download a model/data/PDF, or access the held-out texts. Python checks used `-B`/`PYTHONDONTWRITEBYTECODE=1`. I called the locked analyzer's inventory and analysis functions in memory and compared the resulting analysis payload with the recorded one. Separate calculations from the stored counts checked the summaries, classifications, chain decisions and descriptive statistics; they did not merely read the builder's success flags.

Limits of the audit: I did not regenerate the underlying token-by-key rejection matrix or re-bootstrap it. The stored bootstrap intervals/SEs are the uncertainty record used in the rules. Rounded per-key mean scores permit a close independent reconstruction of S3's estimator, not recovery of every unrounded original value or the fixed-colouring bootstrap draws. Source inspection confirms the fixture guards; I did not create another fixture or dynamically mutation-test every refusal. Git/log evidence establishes the recorded chronology, not what a person privately inspected during the run.

## 2. Claims against evidence

### 2.1 The lock and production record

- `shasum -a 256` matched all **15 pinned files** and the R05 resolution digest. The lock SHA-256 is `434d8f3d8210d5ed30a3339d3805705e4339d081e57639c6b50ef2b8a29f9cc6`. Path-specific history shows no pinned-file change after `b0e0036`.
- The lock commit precedes launch; its UTC timestamp is 2026-10-13T02:50:08Z, consistent with the recorded local lock date of October 12. Launch was at `74a52e0`. The record commit `61fda20` at 2026-10-13T18:51:25Z follows the logged end at 18:36:36Z. No production cell is tracked before the lock. The builder's development commits occur during the run, as disclosed.
- Independently generating the expected slots gives **3,468**, exactly matching disk. All are live, with `N_eff = N = 10,000` and `K = 1,000`; there are no markers or FIXTURE-labelled production cells. The inventory digest independently reproduces as `f3b4a0ceb246c0154903d7b99fb55f28999fa4e50ef2aabf24b1e626d9ac6766`.
- The verified inventory loader accepted the complete production inventory under the current lock, including its provenance, slot and body checks. The checked records carry the expected grid, code, Study 1 core, token-manifest and token-array digests and production key start 22,000. I also rehashed all 20 token arrays and the cached tokenizer JSON files against their manifests.
- Across all **10,404 cell/alpha blocks**, direct calculations from integer level counts reproduce the means, SDs, five quantiles, extrema and exceedance shares. Across **9,180 independent-KGW/Gumbel prediction comparisons**, the stored first-order prediction, exact marginal reference, `rho_bar` and `mean_M` equal the relevant pre-lock `INPUTS.json` values. This supports the claim that the compared predictions were disclosed before the outcomes.
- The log has one start, one completion, 3,468 cell records and 100 completed chains, with no resumed/skipped chain. It records 13:45:36Z–18:36:36Z, consistent with the manifest's 4.85 hours. The 100 chain projections reproduce from `VALIDATION.json`'s coefficients and the key-free sizes in `INPUTS.json`. The peak RSS and cost records support the timing table.
- `final: false` is consistent across the relevant records and access path; I found no holdout-opening record. The restart waiver is disclosed in the decision log, manifest and report. The launch notes are the more precise account of actual machine state, including applications remaining open; the report should be understood as recording Yichen's decision, not as proof that every other process had exited.

The pinned analyzer requires and verifies the lock in study mode and applies the body contract before decisions. Its replay here succeeds with that contract active; the recorded analysis agrees with the replay. I found no bypass in the reviewed production path. This is stronger evidence than a stored `verified: true` flag, while not purporting to prove the absence of every possible execution outside the recorded path.

### 2.2 Registered decisions and secondary adequacy

I recomputed eligibility and status using the cell's prediction, mean M, flags, theory share and stored SD bootstrap interval. With a positive prediction, divide that interval by the prediction; an interval wholly inside the band is consistent, wholly below or above it is inconsistent, and an intersecting interval is unresolved. Counts below agree with the report; secondary rows are descriptive.

| Block | Candidate | Eligible | Resolved | Consistent | Inconsistent | Unresolved |
|---|---:|---:|---:|---:|---:|---:|
| S1 primary | 544 | 217 | 184 | 178 | 6 | 33 |
| h = 0 | 136 | 136 | 116 | 116 | 0 | 20 |
| First rule | 340 | 97 | 89 | 89 | 0 | 8 |
| gamma = 0.5 | 680 | 353 | 348 | 348 | 0 | 5 |
| alpha = 0.05 | 544 | 315 | 315 | 315 | 0 | 0 |
| alpha = 0.001 | 544 | 94 | 60 | 25 | 35 | 34 |
| Fixed colouring, h = 0 | 408 | 272 | 241 | 241 | 0 | 31 |
| Gumbel, raw/distinct | 680 | 335 | 195 | 115 | 80 | 140 |
| Gumbel, first | 340 | 78 | 49 | 23 | 26 | 29 |
| Unit-sigma, builder block | 544 | 213 | 195 | 112 | 83 | 18 |

Thus S1 meets both registered requirements: 184 resolved cells exceed 30, and 178/184 = 96.7% exceeds 80%. All 39 primary inconsistent/unresolved occurrences are present with the principal protocol §6 diagnostics. Table 2 supplies the six counts by corpus/rule. Width/length counts in Table 3 are recoverable from its four displayed counts, but the promised six-count presentation by width and tokenizer is not fully explicit; see F4.

**S2:** independently evaluating `min(1, 2 exp(-K KL(abar || mu)))` gives 3,060 checks, no structural-zero case and no flag; every recorded bound is capped at 1. The normal diagnostic has SD 0.9850666 and maximum absolute deviation about 3.49736. The registered verdict is PASS. It is a coarse audit, not an equivalence test proving calibration at every key or at arbitrary precision.

**S3:** I checked the identity formulas, scale-aware tolerance, structural-zero condition and decisions, and independently checked the fourth-moment SE formulas where applicable. There are 3,468 checks, no structural zeros and no gross failures under `abs(s0_squared - exact_variance) > 6 SE + tau`. The normalised deviations have SD about 0.944179 and maximum absolute value about 3.55691; bootstrap coverage is 0.948385. Reconstructing the known-mean estimator from six-decimal per-key values gives maximum relative difference about 0.000186655, consistent with the disclosed rounding limitation. The fixed/independent reduction formulas reproduce; the observed ratio's label is wrong, not S3's decision (F8).

**S4:** applying each adjacent tolerance `2(se_L + se_Lprime)` gives 76/100 holding and the same 24 failures. The 18 failing h = 4 chains all fail at the 64-to-128 step. The descriptive results also reproduce: distinct 71/100, first 67/100, gamma = 0.5 raw 91/100 and distinct 89/100; Gumbel raw 96/100, distinct 92/100 and first 90/100. The report correctly retains FAIL rather than changing eligibility after observing the failures.

The proposed lattice account has genuine numerical support. Direct binomial-tail calculations at gamma = 0.25, nominal alpha = 0.01 give sizes **1.47022%, 0.96347%, 1.27558%** at M = 63, 127, 255. At M = 60, 124, 252, 508, 1020 they give **1.54163%, 1.02197%, 1.34992%, 1.15445%, 1.00450%**, with independent-Bernoulli SD benchmarks **0.12320, 0.10057, 0.11540, 0.10682, 0.09972 pp** for N = 10,000. These confirm the reported arithmetic, not a complete decomposition of the observed variance or identification of each failure's cause (F5).

**S5:** 40/40 registered chains hold under the adjacent-width tolerance. The first-rule descriptive result, 0/20, has the stated h = 0 structural-zero explanation at the primary level. It should not be read as evidence of a general adverse width effect.

### 2.3 Descriptive calculations and presentation

I independently reproduced both correlation matrices for all 24 between-cell settings (2,400 matrix entries per correlation type), the 1,020 across-tokenizer pairs, and all 24 six-language blocks from stored level counts. That includes the three mutually exclusive language cases, their denominators, the all-positive ratio summaries and all pairwise-difference SDs. The language table correctly separates undefined some-zero ratios from all-zero keys.

The grid selects the expected 240 deployer cells; the stored crossed blocks contain the required five quantiles, maxima and exceedance-share intervals. Their presence in cells is not the same as their presence in the report: the lower two quantiles and some other promised outputs are omitted (F4).

The figures are readable and disclose their plotted subsets. I found no cropped extrema or misleading hidden log scale. Figure 4 labels its 1/N plotting floor and distinguishes the sampled maximum; this floor is a display convention, not an imputed positive rate. Figure 5's panels identify the Llama settings and the full supplement is available. Its restricted selection becomes misleading only when the prose generalises its appearance to both tokenizers and all language pairs (F2).

The cited Study 1 range is traceable: `STUDY1_REPORT_v0.1.md` §2 gives 0.792–1.20, which rounds to the quoted 0.79–1.20. That comparison changes both the text laws and the primary gamma (Study 1: 0.5; Study 2: 0.25); it cannot by itself isolate a real-text effect.

### 2.4 Prior-work quotations rechecked locally

I confirmed these exact substrings in the form-feed-separated local text, with PDF page numbers:

| Source | Verified quotation | Bearing on this report |
|---|---|---|
| `research/literature/txt/2506.16349.txt`, p. 27 | “vocabulary may introduce a particularly biased split” | Jovanović et al. explicitly raise multilingual subdomain bias; this is an antecedent, not this study's newly discovered question. |
| `research/literature/txt/2509.24368.txt`, p. 21 | “over 100 different keys” | Gloaguen et al.'s table measures maximum FPR and across-key SD on 10,000 unwatermarked samples. |
| `research/literature/txt/2609.37310.txt`, p. 4 | “soundness given a key” | AutoMark states the per-key validity distinction formally. |
| `research/literature/txt/genhatharan_nominal_fpr_2026.txt`, p. 1 | “Per-key, per-length empirical calibration” | Genhatharan's abstract discusses mean shifts, tokenizer dependence and measured calibration; these subjects already have named occupants. |

These are checks of the local cited versions, not new downloads or claims of exhaustive priority. F7 concerns attribution in this report, not a reopening of the agreed literature gate.

## 3. Method and statistical assessment

The realised-text target, paired key sample, finite-text component, production namespace and registered decision rules are sufficiently precise to audit. I do not reopen R05's design. The gross identity check, conditional key bootstrap, descriptive two-way estimator and crossed deployer intervals answer different questions and must stay separate in the prose.

S1's aggregate pass is not a uniform factor-1.5 approximation guarantee: six eligible cells are inconsistent and 33 unresolved. Different alpha/gamma blocks have different eligible/resolved sets; their medians describe those sets, not a controlled intervention isolating gamma or tail depth. Shared keys and text prefixes also mean that counts of cells and near-normal histograms are not independent replication counts. The report generally acknowledges this dependence, but some conclusions then outrun it.

The protocol already states the important extremes: degenerate rare-key bootstraps, structural zeros, S2's weak under-rejection sensitivity, S3's heuristic six-SE threshold and the lack of a simultaneous guarantee for S4/S5. The observed production record does not activate a new boundary defect. In particular, all live cells have positive effective N; zero predictions and constant vectors receive the intended special handling. The first-rule h = 0 degeneracy is disclosed rather than silently excluded from the descriptive width result.

For Study 3, the report provides useful candidate settings, not demonstrated remedies: distinct-rule h = 1 and h = 2, paired within-English and between-language/tokenizer comparisons, and the measured bias of each baseline. A new design would need to measure transfer after estimating a threshold, including calibration-sample error and evaluation on the target law. A correlation between FPRs at one original threshold does not determine those quantities. Yichen should choose that design after the revised account is reviewable.

## 4. Process assessment

The generated report is reconstructible exactly from its template, tables, figure references and 592 registered prose values. I found no `or True`, `assert True`, or disabled check disguised as a bare `pass` in the builder. Study mode rejects FIXTURE-marked cells; fixture output paths are resolved and prevented from writing the canonical repository outputs. Production values reproduce from production cells, which gives direct support for the absence of fixture contamination. It does not independently establish the historical claim that no real number was viewed before fixture development.

The missing locked-analyzer unit-sigma block is clearly disclosed in §5 and Table 11 and computed as the builder's block; leaving the pinned analyzer untouched is appropriate. The remaining omission is its absence from the supposedly exhaustive diagnostic supplement (F4).

The decision log, handoff, orientation and report agree on the run, restart waiver, open R06 checkpoint and division of responsibilities. AI use names conductor Claude and reviewer Codex and leaves decisions with Yichen. No terms-of-use, access or holdout violation surfaced in this review; the earlier corpus/terms audits remain outside this checkpoint's scope. The substantive wording issues below should be corrected in the template and regenerated, with corresponding log/handoff statements updated if they repeat the same claims; that is a recommendation to the conductor, not an edit made in this review.

## 5. Independent search

Web access was available. I made three limited searches with `after:2026-10-10 before:2026-10-14`: (i) watermark/watermarking with per-key/key-conditional; (ii) watermark detector/detection with language/register/multilingual disparities; (iii) KGW/Gumbel with false positive/calibration and key. Searches were restricted to arXiv, OpenReview and, for (i)/(iii), GitHub. I did not establish a new directly relevant occupant dated within that interval from the returned material. Date-filtered search can omit recent or poorly indexed work; this is not a novelty certificate or an update replacing the standing pre-lock re-screen. No source was downloaded and no access barrier was bypassed.

## 6. Findings and recommendations

### F1 — Major: Qwen occurrence fractions use the wrong denominator, and semantic overlap is not the hash-overlap estimand

**Evidence.** `research/study2/tokenizer_overlap.py:35` removes Qwen ids at or above `n_common` before taking `onsame.mean()`, but records `n_positions = X.size` and describes the result as a share of all production occurrences. The 410 matching strings/ids, 0–409, are verified. The denominator is not. For Russian Qwen tokens the numerator is 353,202, the full denominator 2,560,000, and the denominator used is 2,158,915: the correct share is **13.79695%**, versus **16.36016%** reported. Arabic is **11.38367%**, versus **14.18768%**; Japanese is **14.00895%**, versus **15.11313%**. Over all Qwen cells the corrected range is **11.38367%–40.59953%**, not 11.8%–40.6%. The error propagates into §§5–6 and `prose_values.json`.

The hash receives integer tuples, not token strings. An identical integer id is coloured identically even when its token string differs between tokenizers. Thus 410 counts *same-string/same-id* matches; it does not enumerate all shared hash inputs or establish what fraction of the observed FPR correlation those 410 explain. Nor does this computation measure whether longer integer tuples “rarely coincide.”

**Recommendation.** Correct the unpinned script to retain the full occurrence denominator and treat out-of-range ids as nonmatches; add a check that its denominator equals `n_positions`, then regenerate the overlap output and report. Preserve the original erroneous post-hoc value in the correction record. Label this as a semantic-alignment diagnostic. Remove the asserted attribution of correlation specifically to the 410 ids, or support it with a separately labelled, key-free weighted integer-tuple overlap calculation. No change to the locked experiment is needed.

### F2 — Major: correlation is converted into a calibration-transfer conclusion, with contradictory numerical scope

**Evidence.** Report §5, line 649, says a key's level “transfers across English registers and not across languages.” Section 6, line 661, then says per-key calibration transfers to another English register and that “its transfer error can be designed from these correlations.” Study 2 performs no such calibration or threshold-transfer experiment. Gate constraint 10 and protocol §12 expressly prohibit implying that guarantee.

The accompanying empirical generalisations also fail: at h = 1 distinct, the English median is **0.54436 for Qwen versus 0.56168 for Llama**, contrary to “every correlation is higher.” The quoted Llama cross-language range -0.028–0.082 is the **English-versus-non-English** subset, not every cross-language pair: ja–zh is **0.17632** for Llama and **0.45974** for Qwen. Qwen's English-versus-non-English median is **0.23341**. These are incompatible with “near zero at every width” across the stated scope.

**Inference.** Correlation at a single threshold describes co-movement of sampled levels. Even perfect correlation would not imply equal FPRs or validity after transporting an estimated threshold.

**Recommendation.** Replace “transfers” with the measured correlation statement, identify each pair class and tokenizer, and correct the quoted comparisons. Present within-English transfer as a hypothesis for Study 3 alongside cross-language and cross-tokenizer transfer, with error to be measured. Figure 5 may remain a labelled Llama illustration; its prose must cover the other settings accurately.

### F3 — Major: the approximation diagnostics do not identify the failed structural assumption

**Evidence.** Report §5, line 645, rules out covariance structure and shift discreteness; §6, line 659, concludes that “the structural assumption that fails is in the per-text score model.” The adjacent “suggestive account, not an attribution” label contradicts these categorical sentences. Both alternatives improve the aggregate fit somewhat; neither separately identifies or removes all interactions with the remaining Gaussian assumptions and estimation error. Symmetry at gamma = 0.5 removes binomial skew, not discreteness. The improvement at h = 0 similarly supports a possibility, not the causal conclusion that shift discreteness “does matter.”

**Recommendation.** Retain the measured ratios and say that the tested alternatives do not fully remove the discrepancy, while residual skew/discreteness is a plausible explanation requiring isolation. Keep comparisons conditioned on their eligible/resolved sets. Do not promote the median 1.72 to a universal correction factor, or the proposed §8 “adequate within a factor 1.5” wording to a pointwise guarantee: the observed primary range reaches 1.78 and the registered pass expressly allows exceptions. The Study 1 comparison should state the different primary gamma.

### F4 — Major: several registered report outputs exist in cells but are omitted from the generated report

**Evidence.** Protocol §§6–9 require more than the current report delivers:

1. `s2_report.py:728–753` formats only the 50%, 95% and 99% deployer quantiles. The registered **1% and 5% quantiles and their crossed intervals** are absent even from `tables_deployer_full.md`. That supplement says K and N_eff are “as in the body”; it does not state their numeric values at each table as promised. Here N_eff is 10,000 for every row, so a per-table caption suffices.
2. The **population diagnostic** required by §7 is stored as `levels[alpha].population_est` but never emitted by the builder. There is also no all-live-cell diagnostic table carrying the promised pairwise/heterogeneity information; the current diagnostic table selects non-consistent occurrences.
3. The §8 per-cell **keys at level 0, keys at level 1, number of distinct levels, keys above 5 alpha** are not reported comprehensively. Current diagnostic rows show only three of those four fields and only for selected occurrences; the level-1 count is missing.
4. Table 4 and the diagnostic supplement claim every non-consistent occurrence of every block, but their 447 rows omit the builder's unit-sigma block: **83 inconsistent + 18 unresolved = 101 additional occurrences**. A unit-sigma ratio column on other blocks' rows does not supply these selected occurrences or their unit-sigma eligibility/status.
5. Display the promised six S1 counts explicitly by width and tokenizer, alongside the existing corpus/rule table. Table 3 permits subtraction to recover two counts, but is not the stated six-count table.

**Recommendation.** Generate the missing outputs from the existing record, with clear estimands, uncertainty labels and per-table K/N_eff. Include the unit-sigma occurrences using that predictor's eligibility and intervals, or narrow any “every block” claim while still meeting the protocol's reporting requirement. This is reporting work; none of it requires reopening the locked grid or choosing a new outcome criterion.

### F5 — Major: finite-text benchmarks are treated as a demonstrated variance attribution

**Evidence.** At h = 2, §5 line 650 calls language disparity “close to the finite-text noise” and concludes that a large part is the finite-text term because the difference SD is 1.6–2.8 times an independent-Bernoulli benchmark. Even if that benchmark were an exact additive component, its variance fraction would be only **1/1.6² to 1/2.8² = 39% to 13%**. In this experiment it is a reference at nominal 1%, not an estimated decomposition respecting each marginal level, text law and shared-key covariance.

The h = 4 arithmetic is useful, but the statement that Arabic cells are “the only cells where the shift term is visible” is contradicted by the stored predictions: at L = 256 news has theory shares **0.5471 (Llama)** and **0.7470 (Qwen)**; Qwen Wikipedia English at L = 1024 has **0.6964**, versus Arabic at L = 256 **0.4627** and **0.5750**. Holding/failing an entire chain cannot identify which components are visible at every length. The categorical “holding elsewhere” length interpretation also needs to retain the two non-news h = 1 failures in German and Russian.

**Recommendation.** Describe the lattice and floor as supported benchmarks and a plausible account of the short-length h = 4 pattern. Describe h = 2 language-difference SDs as 1.6–2.8 times the reference, without claiming the reference explains most or a known share of disparity. Use the already recorded population diagnostics, clearly qualified, if a decomposition discussion is needed. Keep all observed S4 exceptions visible and any narrower length hypothesis explicitly post-hoc and untested.

### F6 — Major: elevated key-mean FPR is incorrectly asserted for every individual key

**Evidence.** Report §6, line 658, says under the raw rule “the rate is inflated for every key by within-text repetition,” citing the **key-mean** range. Stored h = 1, longest-length counts directly contradict the universal statement: in news/Qwen, **97/1,000 keys have a level below 1%**, with minimum **0.36%**; news/Llama has **30/1,000** below 1%, minimum **0.52%**. Within-text repetition and between-key dispersion are distinct mechanisms; an elevated marginal mean does not impose a lower bound on every key's rate.

**Recommendation.** Say that within-text repetition elevates the key-averaged null level in these raw-rule settings, while individual sampled keys lie on both sides of the nominal level. Attribute the known within-text mechanism and preserve the distinction from fixed-key dispersion. Likewise, describe S2/S3 as finding no audit failure, rather than literal equality or proof of ideal hash behaviour.

### F7 — Major: promised attribution is absent from the report itself

**Evidence.** Section 7 says the phenomenon and per-key measurement “are attributed to the published record,” but the report does not name Jovanović, Gloaguen, Genhatharan or AutoMark where it states the phenomenon, mean-shift mechanism, tokenizer dependence or calibration proposal. A parenthetical gate-constraint number is not that attribution. The page-confirmed antecedents in §2.4 are directly relevant, and gate constraints 1, 13 and 16 explicitly require them. There is no explicit “first” claim; the problem is missing positive attribution, not invented priority language.

**Recommendation.** Add concise named citations at the relevant claims, with a short comparison distinguishing this study's grid and conditioned target from prior measurements. For Genhatharan, preserve the recorded public-repository/release citation rather than treating absence from arXiv as absence of publication. This can be brief and need not turn the report into a literature review.

### F8 — Minor: correct the fixed-size estimator label and vocabulary-support description

**Evidence.** Table 12's caption calls the observed fixed/independent ratio a **known-mean variance** ratio. The locked analyzer's `fixed_ratio_table` (`s2_analyze.py:206–219`) actually uses `q_hat.var_across_keys`, the sample variance. The builder reproduces that value and then supplies the wrong caption (`s2_report.py:845`). This does not invalidate S3, which uses the known-mean estimator separately.

Section 5 line 652 says the largest 2.101% reduction occurs on long texts whose deduplicated support covers “most of the vocabulary.” In the maximum row (Gutenberg/Llama, L = 1024, distinct), covered support is **42.1587% of V**, and effective support `1/C_cond` is **2,695.245** out of 128,256 (about 2.10%). Neither means most of the vocabulary. The exact reduction formula and its reported magnitude are correct.

**Recommendation.** Relabel the recorded observed ratio as the sample-variance ratio, without changing the locked analyzer. Describe the maximum using its weighted effective support and actual coverage, keeping these two different quantities separate.

The findings concern a correctable report around a credible locked record. They do not authorise new outcomes, protocol edits or a Study 3 launch. I recommend resolving F1–F8 through the unpinned report path and a documented correction, then returning the revised account for review.

VERDICT: REVISE
