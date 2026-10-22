# R11 — claim gate, Codex round 2

Date: 2026-10-19 UTC. Independent reviewer: Codex. Scope: the requested bounded re-review of round-1 findings F1–F10, the revised claim gate, and preservation of the agreed studies. The prior blocking and major findings are closed. Three minor wording/state residuals are identified below as F11–F13; none requires a changed result, protocol, computation or judgement by Yichen.

## 1. Baseline and material read

Baseline: **`cb5985797f65469dfeed913654158d328f57dd4b`**, on `main`; the working tree was clean. HEAD remained at that commit through the review. The round-1 comparison baseline is `161d43043faeafba9bbae54bd9d464a83cdb643f`.

Read the response first, then the requested claim-gate rows and sections, the regenerated side memo and script delta, the dated decision-log entries, the handoff's status/waiting-on text, and the orientation's R11 row. Rechecked the relevant original report tables and prose, R09's resolution for D17/D18, the saved side-computation JSON, all four locks and their pinned files, the specified raw request logs, the local literature pages, and the GitHub amendment at its full commit ID. The round-1 review supplies the broader unchanged-evidence review; this round does not repeat every search or every study calculation.

At this actual baseline, the gate's decisions block and the later log entries already record **all J1–J11 as decided**, including J9's earlier decision. The top-level handoff reflects that state. I treat those as Yichen's recorded decisions, not choices for this reviewer to make. The response's earlier pending list is a dated intermediate record.

Only this memo was written. No commit, data/model download, study-mode runner, analyzer, report builder, full bootstrap rerun, or new study was performed. Checks were short reads, hashes, arithmetic, a memory-only rendering of the side memo, and read-only GitHub API requests.

## 2. Claims against evidence

### Disposition of F1–F10

| Round-1 finding | Evidence checked in round 2 | Disposition |
|---|---|---|
| **F1, blocking: population inference from a key-only SE** | E1, constraint 25, J11 and 1G now distinguish the text-conditioned functional from the population key component. The crossed counts are historical descriptive diagnostics; the key-only recounts are a conditional sensitivity calculation with the held-correction approximation named. D17 and D18 are cited, and neither construction is given a validated population confidence or general conservativeness claim. This matches R09's F22/D18 resolution. | **Closed.** The remaining model-description imprecision is F12 below, not a surviving population-inference claim. |
| **F2, major: Unigram antecedents** | A2, A3, §3, §4, §7 and J10 attribute Lemma C.21, Remark E.2 and Lemma F.2 and narrow the contribution. The local PDF-text pages 31, 34 and 36 contain the stated results; the reductions to A2/A3 are correct. | **Closed.** No new generic sampling-without-replacement identity is claimed. |
| **F3, major: registered estimands and failure groups** | Study 1 Table 1 defines R4 on raw-rule rho-bar and R5 on raw-rule between-text collision. A5/A6 and constraint 23 now preserve those estimands and label the other retention rules descriptive. Study 2 §5 supports 16 non-news chains within the 18 h=4 failures, two overlapping news chains, and 26 group memberships over 24 failing chains. J3 retains the registered failure and labels the explanation plausible. | **Major issue closed.** J3 still uses the h=1 lattice example while explaining the h=4 dip; minor F11 below. |
| **F4, major: D8's width transition** | Both widths were checked against Study 4 Table 14, including the raw means and raw/distinct shares. D8 explicitly changes to h=1 and states the 1,000-key model-null denominator. | **Closed.** The new h=0 values and retained h=1 values match their rows. |
| **F5, major: remedy conditions and overstatements** | C1 states the primary setting and calls the tie account suggestive. C3 separates the raw and distinct pooled results. C4/J8 carry the distinct-rule, h=1, alpha=.01, conformal@5000 setting and ordered-pair aggregation. C7 uses a measured near-nominal mean and treats raw-rule multiplier results outside Proposition 1's prerequisite. D5 distinguishes the 100 and 1,000 keys; D7 states its settings and denominators. Checked against Study 3 Tables 8–9/§5 and Study 4 Tables 9, 13–14/§8. | **Closed.** These are conditional measurements, not guarantees or a general remedy ranking. |
| **F6, minor: SE ratio range** | Independently divided the seven saved text-only SEs by the exact key-only SEs; checked the generated line and the three-line addition to `memo()`. The complete memo renders identically in memory when its recorded timestamp is supplied. | **Closed.** The range is 6.4%–27.4%, at alpha=.01 on this subset only. |
| **F7, major: missing software prior practice** | Read the pinned amendment at full commit `b3adb0f13301506e6ee0f49be26e99f6abde5829`; verified its statements, table examples, commit date and repository metadata. The new row, §4, constraint 32 and C4/J8 distinguish this practice from the many-key dispersion/prediction study. §2 B now discloses the push-date search limit and withdraws universal absence. | **Closed.** The older public artifact is properly treated as prior work. |
| **F8, major: concurrent screens** | The raw A/B logs contain requests at the same seconds, 00:31:04Z and 00:31:16Z. §2 now says concurrent, records the uncertifiable aggregate pacing and specifies a future single queue. | **Closed as a disclosure/process correction.** This does not retrospectively certify compliance. |
| **F9, minor: incomplete inventory** | B2 now includes Study 1 R2 and its power limits. A4 includes the weak Gumbel and first-rule blocks. C1 includes the h=0 and alpha=.001 exceptions. 1G is explicitly bounded and incorporates the missing distinctions. Constraint 30 includes the 500/2,000/200 Study 1 key samples and pairing exception. | **Closed.** The additions agree with the reports and grid. |
| **F10, minor: quotes and workflow state** | The 2610.17655 input quote matches p.16 after whitespace normalization; the Guidelines phrase is present on p.26. §3 distinguishes mathematical transcription and API/extract provenance. E1 uses Monte Carlo agreement language. The handoff's leading status and waiting-on lines correctly reflect round 2 and completed wording decisions. | **Core corrections closed.** One later stale handoff bullet remains, F13 below. |

### Decisive numerical checks

**D8, Study 4 Table 14.** All entries below concern L=256, alpha=.01, diagonal conformal@5000, and 1,000 evaluation keys on 5,000 model-null texts per cell. Cell order is news / Wikipedia / Stack Exchange.

| Width | Raw key-mean level (pp) | Raw share above alpha (%) | Distinct share above alpha (%) |
|---|---|---|---|
| h=0 | 0.939 / 0.885 / 1.101 | 33.7 / 25.8 / 56.8 | 59.4 / 45.6 / 60.9 |
| h=1 | 0.741 / 0.767 / 0.988 | 19.0 / 18.0 / 43.3 | 53.1 / 48.0 / 49.3 |

The gate's rounded means are faithful. D5 now labels the model-null nominal means 2.20 / 3.29 / 3.75 pp as a 1,000-key summary and the corpus means 2.37 / 3.47 / 3.78 pp as a 100-power-key summary. D7 preserves Table 13's 100-key × 50-text power denominator and 1,000-key × 5,000-text null denominator.

**C3/C7, Study 3 Table 8.** At h=1, alpha=.01, medians over 20 units, pooled distinct gives key-mean 0.994%, SD 0.397 pp, share above alpha 41.4%; pooled raw gives 0.891%, 0.466 pp, 28.4%. The nominal SDs are 0.441 and 1.363 pp, respectively. The distinct multiplier mean is 0.072%; the raw multiplier's median share above alpha is 10.1%. The gate now keeps both the rule labels and the prerequisite distinction.

**C4/J8, Study 3 Table 9.** At distinct h=1, conformal@5000, the diagonal SD is 0.172 pp; within-English, English–other and other–other class medians are 0.467, 0.595 and 0.524 pp. The English–other 99% key is 3.02% against the diagonal's 1.43%; the corresponding shares above 2 alpha are 8.3% and 0.0%. The setting and aggregation added to the gate are essential and supported.

**Inventory additions.** Study 1 Table 1 gives R2's 891 checks, zero flags and 18 separately counted structural zeros. Study 2 Table 5 gives 115/195=59.0% consistent for Gumbel raw/distinct, resolved median 1.33, and 23/49=46.9% for its first-rule block, median 1.65. Study 3 §5 gives 612/630 consistent at h=0, with 18 inconsistent, and 1,117/1,149 at alpha=.001, with 32 inconsistent. These weaker blocks are correctly labelled descriptive rather than promoted into additional registered passes.

**F6.** In saved subset order, the text-only/exact-key-only SE percentages are 9.2181, 17.2193, 22.5428, 6.4361, 8.3233, 14.0833 and 27.4456. The extrema format to **6.4%–27.4%**. The a_k-only/exact-key-only ratios range from 0.957596 to 0.999664; the fresh crossed/exact-key-only ratios from 0.968572 to 1.050575. All 21 saved (cell, alpha) blocks have the exact-reproduction flag. These flags were also independently reproduced in round 1; no new regeneration was needed for a memo-only code change.

### Page and source checks

For Unigram, `research/literature/txt/2306.17439.txt`, p.31's Lemma C.21 proof gives the exact finite-population variance before bounding it. Its phrase **“variance formula for sampling without replacement”** is present on that page across a line break; a line-only search also finds the repeated calculation on p.32. With one context, B=1 and A=||p_t||², the exact result reduces to gamma(1−gamma)(V A−1)/(V−1), as A2 says. On p.34, Remark E.2 gives the deduplicated count variance; dividing by m² yields gamma(1−gamma)(V−m)/(m(V−1)), A3 with s=m. P.36's Lemma F.2 supplies the general variance formula. The revised attribution is substantive, not merely an additional citation.

For `2610.17655.txt`, p.16, **“Text, tokenizer, secret key, shared partition and column configuration, context rule”** is the corrected input substring. For `ec_article50_guidelines_131215.txt`, p.26, **“marking and detection must be effective, interoperable, robust and reliable”** is present. Mathematical normalization is now disclosed in §3 rather than certified as literal PDF text.

The [pinned SynthID amendment](https://github.com/xlr8harder/synthid/blob/b3adb0f13301506e6ee0f49be26e99f6abde5829/docs/DETECTOR_SCORE_FAMILY_AMENDMENT.md) explicitly says **“Each key is calibrated separately”**. The same contract freezes each threshold for the matching-key positive tests and six negative corpora. It uses two keys and three calibration sources. Its weighted-mean table gives Human ELI5/Key A 74.8% TPR and 1.82% maximum FPR; unwatermarked Qwen/Key B 69.8% and 1.03%. The later Bayesian example reports 2.78% FPR on unmatched unwatermarked Qwen. These are the gate's examples, with the score families correctly distinguished by their context. The commit is dated 2026-08-19T06:39:39Z; the repository was created 2026-08-18 and reports MIT licensing. The API-returned Markdown blob is `c1a173072de4b25b659f02b7d628970fbb4e7de1`, SHA-256 `1f25395bc1f8f386f9d8af26b25837ce4912f849848a566f13950d7d185c51a2`. No code or score arrays were fetched or executed.

## 3. Method and statistics

The F1 correction now preserves the relevant distinction. For a fixed text sample, let C_ij be the sample covariance across keys between rejection rows i and j. The two-way estimate can be written

\[
\widehat v=\frac{1}{N(N-1)}\sum_{i\ne j}C_{ij}.
\]

Its expectation over the key sample, conditional on the texts, is the corresponding off-diagonal average of population key covariances for those texts. That is the text-conditioned functional. It is not a confidence target averaged over new text samples. R09 D18 makes the same distinction for the prompt-conditioned component.

The resampling identities remain unchanged: with a=(K−1)/K, the exact key-only resample has mean a·v-hat; the text-only resample has mean s_K²; the crossed resample has mean a·s_K². The a_k-only version instead holds MS_E/N fixed. Agreement of this approximation with exact key-only SEs on seven cells does not establish negligible population text uncertainty.

E1/constraint 25/J11 now implement this limitation. The historical crossed counts remain 309/360 and 22/217; the conditional key-only sensitivity counts remain 292/360 and 20/217; normal-theory counts remain 256/360 and 14/217. They are neither a replacement registered verdict nor a validated population coverage statement. The finite simulations' observed coverages can be reported as model-specific diagnostics. I did not rerun the conductor's new 300-table experiment; closure of F1 rests on the corrected target and the already verified counterexample, not acceptance of that extra coverage estimate as a general result.

No power, eligibility, boundary, holdout or primary decision rule changed. R4/R5 retain their registered estimands; S4 remains FAIL; W2 remains unresolved on the narrowed prompt-conditioned target. No new population interval construction is needed to close this wording review. The logit-additive model should, however, be described accurately as noted in F12.

## 4. Process and immutability

Independently recomputed every digest in all four `PRE_RUN_LOCK.json` files: **8 + 15 + 20 + 32 = 75 pin entries, covering 52 unique files; zero mismatches**. Each lock's separately recorded review-resolution digest also matches. All four locks retain `final: false`.

Both path-scoped `git log --oneline 161d430..cb59857 -- ...` and `git diff --name-only 161d430 cb59857 -- ...` are empty for the four reports, all lock-pinned paths and protocols, the locks and run manifests/logs, all four cell directories, and the analysis results. The check includes Study 3's actual tracked `results.json.gz` as well as its `results.json` path, and Study 4's `results_arrays.npz`. The tracked cell-directory inventories contain 1,290 / 3,568 / 240 / 1,860 files respectively, including cost records and companion arrays where applicable. No locked record or agreed result changed.

The side script's only delta is the three-line addition that computes and prints the ratio range and exact-block count in `memo()`. The two updated stored-summary JSON files differ only in `written_utc` and `script_sha256`; their numerical contents are unchanged. The regeneration and synthetic JSON files are unchanged. Calling only `memo()` on the saved parts, with the recorded timestamp, reproduced the entire current Markdown byte for byte in memory. There was no reason to rerun the longer stored bootstrap.

The decision log preserves the earlier Milestone 10 statements and appends dated corrections; its five correction groups cover the uncertainty reading, ratio range, concurrent screens, missed antecedents/software, and width/registered-rule wording. The later decision entries and gate decisions block agree. The orientation correctly leaves R11 OPEN with round 2 pending. The handoff's top status and waiting-on text agree, but its separate pending subsection has the stale bullet in F13.

For F8, `raw_A/arxiv_api_rerun_log.tsv` records q17 at 00:31:04Z and q22 at 00:31:16Z, while `raw_B/abs_pages_index.txt` records arXiv abstract requests at those same times. The revised gate accurately acknowledges what the logs can and cannot certify. No new compliant run could replace that historical record. This review made no arXiv requests, encountered no block, and worked around none.

The constraint set now carries the substantive round-1 corrections into the drafting requirements. AI roles remain disclosed. No material left the repository for posting, publication or communication, and this review does not authorize Stage 8 or alter any of Yichen's decisions.

## 5. Independent search and its limits

Round 1 already contained the independent searches and the Unigram/software findings. This bounded round did **not** repeat a broad search or advance its freshness cutoff. It independently reopened the newly attributed public artifact at its pinned commit, rather than treating the conductor's description as evidence, and reread the decisive local literature pages.

The two-key artifact establishes prior practice of per-key calibration and evaluating frozen thresholds across negative corpora. Its Markdown does not establish this project's many-key dispersion/prediction contribution. Conversely, that difference is not an exhaustive novelty proof. The revised §2 B correctly limits the old absence statement to the repositories searched under its date window; the gate's remaining absence claims must continue to be read with the declared search and access limits.

## 6. Findings remaining after the re-review

Round-1 F1–F10 are disposed of in §2. The following are **minor and non-blocking**, suitable for correction in the resolution without another study or a new decision from Yichen.

### F11 — minor — J3's h=4 explanation still carries the h=1 lattice example

**Evidence.** `research/CLAIM_GATE_v0.1.md:129` now says the lattice is a plausible account of the **h=4 dip**, then gives 1.47%, 0.96%, 1.28% at M=63,127,255. Those are the h=1 raw-rule counts at L=64,128,256. Study 2 §5 distinguishes them from the h=4 example, where M=L−4=60,124,252 and the exact sizes are 1.54%, 1.02%, 1.35%. A short independent binomial-tail calculation gives 1.541633%, 1.021967%, 1.349924%; the corresponding N=10,000 SD benchmarks are 0.123202, 0.100574, 0.115399 pp. The registered estimands and 16-chain restriction are now correct; the surviving problem is the illustrative width label.

**Recommendation.** Use the report's h=4 sizes/counts in that h=4 sentence, or explicitly identify the current triplet as a separate h=1 example of the lattice. Keep the account plausible and restricted to the supported chains. A5's general lattice-property example need not be changed if its h=1 scope is made clear where used. Preserve the agreed report and verdict.

### F12 — minor — Logit additivity does not mean absence of key-by-text interaction on the probability scale

**Evidence.** `RESPONSE_claude_r1.md:9` says the six side models are additive or i.i.d.-given-key and “have no such interaction”; E1 later calls them “the six additive models.” The actual code at `research/study1/twoway_se_check.py:261` uses p_ik=expit(theta_k+tau_i) for one of the three model families at each size. This is additive in the logit, not in the rejection probability: its mixed derivative is p(1−p)(1−2p), generally nonzero. Shared text effects can therefore change conditional key variance in this family too. The revised inference is appropriately model-specific, so this imprecise explanatory label does not reopen F1.

**Recommendation.** Say “the six model/size combinations tested” or name the two Beta-Bernoulli and one logit-additive family at the two sizes. Remove the claim that they have no such interaction; the supported observation is that the tested parameters did not expose the counterexample's large coverage deficit. Leave the numerical results and narrowed uncertainty target unchanged.

### F13 — minor — A later handoff bullet contradicts its corrected leading status

**Evidence.** `RESEARCH_HANDOFF.md:52`, under “Provisional or pending,” still says round 1 is pending and J1–J11 are pending. At the reviewed baseline, the top status/waiting-on lines, the next-steps entry, the gate's decisions block and the later decision-log entries all say round 1 was answered, round 2 is pending, and the wording decisions are complete. This is a leftover status duplicate, not evidence that Yichen's decisions were missing.

**Recommendation.** Synchronize that bullet with the leading status and, on resolution, the actual R11 outcome. Do not rewrite the response's historically pending list or the earlier log entries. Stage 8 still requires Yichen's word.

VERDICT: AGREE
