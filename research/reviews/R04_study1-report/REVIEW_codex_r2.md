# R04 — Study 1 report: independent review, round 2

Reviewer: Codex. Baseline: `main`, `712b0c3ed476cdb6c10b2093e86ee14938eda065`; working tree clean before this memo. Round-1 comparison baseline: `58ab64e32a9171e65e81d1a963136b228e08822a`.

**Recommendation: AGREE.** The round-1 major findings are substantively addressed. The locked results remain intact, the new diagnostic supplement reproduces, and the report now distinguishes the registered decisions from exploratory interpretation and unavailable uncertainty. Three minor labeling/scope corrections remain below; none changes a decision or requires another study run. This verdict concerns R04, not approval of a Study 2 design or a population-extreme claim.

## 1. Scope and checks

Read in the requested order: `RESPONSE_claude_r1.md`, the regenerated report (including the process/deviation disclosures, Tables 4, 8, 8b and 14, and §§5–8), the complete `tables_r1_diagnostics_full.md`, both builder/template diffs since `58ab64e`, Figures 2–5, and the decision log's round-1 response and dated corrections. Referred back to the orientation's memo requirements, round-1 memo, locked protocol, gate constraints 1, 3, 11–13 and 16, saved results/cells and relevant implementation. Checked the updated handoff. Figure 1's PNG is unchanged from the reviewed baseline.

Used short read-only checks, including independent extraction/calculation from saved key levels, GFM-to-HTML rendering with Pandoc in memory, and hashing/history comparisons. Did not execute the report builder, generate texts, run validation, download anything, inspect the holdout or change any file other than this memo.

## 2. Claims against evidence

### The lock and record are unchanged

Re-ran `shasum -a 256` against all eight pinned files: every complete digest matches `PRE_RUN_LOCK.json`; the R03 resolution digest also matches. A history/tree comparison from `b994105` to this baseline finds no change to the eight pinned files, the lock or its resolution memo. The lock retains `final: false`.

The requested `git log --oneline -- outputs/study1_v0.3/cells outputs/study1_v0.3/results.json research/STUDY1_PROTOCOL_v0.3.md research/study1/s1_analyze.py` has no later record change than `62aa6ea` and no later pinned-protocol change than `b994105`. An additional comparison against `62aa6ea` confirms no change to **cells and cost records, `results.json`, `RUN_MANIFEST.json`, or `run.log`**. `report/checks.json` is unchanged from round 1. Accordingly, the round-1 independent rule reproduction remains applicable; no new outcome-dependent analysis rule was introduced.

### The diagnostic supplement and added uncertainty reproduce

Read and independently checked **all 212 printed non-consistent occurrences, representing 141 distinct cells**. Reconstructed their keys and statuses from the locked block rows and underlying intervals; recomputed observed SDs and means from per-key values, both observed/pairwise-predicted ratios, and the absolute difference between the two pairwise predicted SDs. Compared all printed diagnostic fields, including predictor/identity/observed sigma², theory share, M, heterogeneity summaries and cross-block occurrence labels. **Zero field mismatches** at the report's formatting precision.

| Block | Inconsistent | Unresolved |
|---|---:|---:|
| Primary | 0 | 28 |
| Alpha = 0.05 | 0 | 0 |
| Alpha = 0.001 | 3 | 61 |
| First rule | 0 | 0 |
| Extra gamma | 0 | 10 |
| Unit-sigma predictor | 2 | 42 |
| Illustration | 3 | 22 |
| Fixed colouring | 3 | 38 |

Thus the supplement includes the previously missing **173 secondary unresolved occurrences**, as well as the 11 inconsistent and 28 primary unresolved occurrences. The zero-occurrence blocks require no data rows. Tables 4 and 8 use the same correctly sourced diagnostic fields. There is a minor standalone labeling omission, F13.

For all **24 Table 14 rows**, independently checked the printed SD and saved key-bootstrap CI, mean, sampled maximum, and shares above 2 alpha and 5 alpha against the saved key levels. They match. The added bands in Figures 2–3 use the same saved conditional SD intervals. Figure 4 now expressly identifies its bands as empirical key-distribution spread, not confidence bands.

Rechecked Table 8b's decisions directly: the literal `3 SE` test passes **0/4**; the locked implemented `3 SE + 1e-9` test passes **4/4**. Its residuals and SEs agree with round 1. This is properly disclosed as a pre-existing text/code discrepancy, not silently repaired.

Reassembled the report in memory from the current template, saved table/value registries and the five checked figure references: byte match. This establishes assembly reproducibility, separately from the numerical checks above.

### Interpretation and source attribution

The main corrections are supported: `C_cond=A/B` is the scored-weight conditional collision; for the i.i.d. population raw tuple law, `A=C0^(h+1)` and `B=C0^h`, so their ratio is `C0`. The universal below-1% statement stays refuted. Four h = 3 cells remain explicitly identified as eligible and consistent, with h = 4 reported separately. The ratio comparison is no longer a ±20% real-text guarantee or a unique diagnosis of residual non-normality. R2 is described as no triggered audit, with its power limits.

The new source-attribution paragraph distinguishes within-text repetition from key dependence and names the prior record, including AutoMark and Genhatharan. The renewed priority phrase is removed; no replacement “first,” “earliest,” theorem, remedy or measured real-text-rate claim appears. Rechecked these local source substrings again, using form-feed PDF page numbering:

- `research/literature/txt/2506.16349.txt`, PDF p.27: “if similar effects can be observed in LLM watermarking.”
- `research/literature/txt/2609.37310.txt`, PDF p.3: “a specific deployed key can still exhibit a high false positive rate.”
- `research/literature/txt/2512.16904.txt`, PDF p.19: the passage beginning “fixing a specific” and explaining the key's preferences and consequent mean shift.

These remain evidence for attributing the phenomenon and mechanism, not for novelty. The full prior-work references in the agreed gate should accompany the eventual paper text. Minor scope slips within the otherwise narrowed interpretation are identified in F11–F12.

## 3. Method and statistics

No design reopening is needed. The primary result remains the registered factor-1.5 interval criterion, with 152 consistent of 152 resolved, 180 eligible and 28 unresolved; secondary blocks remain descriptive. The two pairwise replicas are now visible where causal interpretation is discussed, and the report acknowledges that the study does not isolate Gaussian-model error from sampling variation. The improved small-vocabulary pairwise example is retained rather than erased by the primary pass rate.

The width conclusion now preserves the four exceptions and calls the 0.157 pp quantity a Bernoulli benchmark rather than a universal SD floor. The new Study 2 paragraph leaves widths and sample size to its own power analysis and Yichen. Its use of the measured error range as a prior expectation is a proposal to check, not evidence of a real-text bound.

The deployer's view remains conditional on K = 500 sampled keys and N = 4,000 realised texts per law. The report explicitly says that crossed key-by-text uncertainty for quantiles and the worst key is unavailable. This is an acceptable resolution of round-1 F7 for a descriptive report: **gate constraint 12's crossed-uncertainty component is disclosed as unfulfilled, not claimed to have been supplied**. It remains a limitation to address before any population-extreme inference in the paper. The added SD intervals do not purport to be confidence intervals for a key quantile or maximum.

The conductor's additional short-cell correction is substantially right: there are 32 consistent h = 0 primary raw cells, including eight at M ≤ 128; the four unresolved raw cells have M = 64, 64, 64, 128. Across all 32 consistent cells, shift SD spans `0.995464`–`11.089279`. This does not support the withdrawn “below about 0.8” boundary. The other additional correction—the Figure 5 title collision—is visibly repaired.

## 4. Process, rendered Markdown and figures

The report now names Claude as conductor and Codex as reviewer, states Yichen's responsibility, separates pilot and production namespaces, discloses post-lock fixture viewing, and correctly describes R04 as open at the time of that build. The historical claim of who viewed a fixture is a process record, not independently observable execution telemetry; it is no longer omitted. The unpinned builder/template edits do not affect the locked analyzer.

The decision log preserves the earlier entry and appends dated corrections to the collision explanation, h ≥ 3 statement, attribution, R4b criterion and priority wording. The response and handoff consistently identify round 2 as pending. No unresolved dispute or concealed change to the run record was found.

Rendered the report and all four `tables*.md` files as GFM HTML in memory and checked the resulting table structures. The report has **17 rectangular tables**; all row/header column counts agree, including the 19-column Table 4, 20-column Table 8, 10-column Table 8b and 12-column Table 14. R2 and R3's Table 1 verdicts now remain in their proper final cells. All **five image targets and four Markdown link targets** in the report resolve from the report's directory. Supplement references are still code text rather than hyperlinks (F13).

Viewed Figures 2–5. Confidence bands, spread-band labels, units and selections agree with the code and tables. Figure 5's titles no longer collide; its caption identifies **1,185 plotted live cells, nine excluded structural zeros, and 96 included core fixed cells outside the R3 decision**. No new cropped-data or selection issue was found. The source diff adds formatting, diagnostics and disclosures; the numerical decision checks and pilot output guard remain intact.

## 5. Independent search

No new web search in this bounded correction review. Round 1's limited search and its explicit non-novelty caveat stand. No literature or other material was downloaded.

## 6. Findings and dispositions

### Round-1 findings

| Finding | Round-2 disposition | Evidence |
|---|---|---|
| F1 major — R4b discrepancy | Closed | §1 deviation note, §2 bullet, Table 8b and §5 distinguish literal and implemented tests; lock preserved. Table 1 should travel with that qualification if reused alone. |
| F2 major — conditional collision | Substantively closed | General `A/B` identity and i.i.d. population derivation restored; raw-only repair withdrawn. Minor numeric label remains in F11. |
| F3 major — h ≥ 3 invisibility | Closed | Four h = 3 exceptions listed; blanket invisibility and sample-size claims withdrawn. Minor denominator wording remains in F12. |
| F4 major — over-attribution and accuracy | Substantively closed | Both replicas visible; improvement example and 73/180 comparison stated; no unique causal claim or ±20% guarantee; R2 power caveat restored. Minor summary scope remains in F12. |
| F5 major — omitted diagnostics | Closed | Every non-consistent occurrence included; all 212 rows independently match. Standalone usability issue in F13. |
| F6 major — priority | Closed | Renewed priority phrase removed; named prior record and distinct known mechanisms stated. |
| F7 minor — uncertainty | Closed by explicit limitation plus available intervals | K/N and conditioning stated; SD intervals added; distributional bands distinguished; missing crossed uncertainty acknowledged. |
| F8 minor — semantic sourcing | Substantively closed | Identity sigma² now 0.742/0.715; flags correctly enter R3; growth restricted to h = 1; fixed-colouring pairing caveat restored. |
| F9 minor — process disclosure | Closed | Named roles, pilot/fixture account and non-approval status appear in §1. |
| F10 minor — rendering | Closed | GFM columns and targets pass; Figure 5 titles and inclusion/exclusion caption repaired. |

### F11 — Minor: distinguish empirical and population C0 in the new example

**Evidence.** Report §5's reduction paragraph and the dated log correction call `0.01721` the raw law's `C0`. Builder variable `z10000_h0_raw_C0` actually reads the h = 0 cell's realised `identity_q.C_cond`: `0.017212584491`. The law's saved analytic `population.collision_h_analytic` is `0.017169954068`; its square is the cited analytic `C1=0.000294807323`. Thus the numerical example mixes an empirical C0 estimate with an analytic C1 without labeling the distinction. The restored population algebra is correct and the approximate 0.58% conclusion is unaffected.

**Recommendation.** Use the analytic C0, or label `0.01721` as the realised h = 0 collision estimate. State explicitly that `A/B=C0` is a population i.i.d. identity. Unless a pre-run derivation documents the assumed premise, describe “C_cond stays near C0” as a retrospective explanation of the numerical expectation rather than a newly documented pre-registration assumption. This is a labeling correction, not a change to the locked reduction result.

### F12 — Minor: preserve the scopes of the corrected numbers in the condensed interpretation

**Evidence.** In §6 Q4, “at L = 2,048, where only 4 of the 144 candidate cells…” attaches the all-length count to the longest length. There are **four of 144 across all lengths**, but **three of 24 at L = 2,048**; the fourth is the Zipf s = 1.2 raw cell at L = 1,024. §5 already gives the correct individual lengths.

In §6 Q2, describing the h = 0 unresolved cells collectively as short cells with factors `1.25–1.43` compresses away the **24 distinct-rule unresolved cells**, including long cells; that factor range belongs to the **four raw-rule unresolved cells**. For example, Zipf V = 1,000 distinct at L = 2,048 is unresolved with ratio about 0.873. The correctly detailed §5 and Table 4 prevent ambiguity in the underlying evidence, but the summary should preserve their distinction. Likewise, `0.995–11.1` is the shift-SD range over all 32 consistent h = 0 raw cells, not only those longer than 128; the latter minimum is about 1.670.

**Recommendation.** Separate the longest-length range from the all-length eligibility sentence. Qualify the over-prediction factors as applying to the four primary raw cases and the three alpha = 0.001 inconsistent cases; mention the distinct-rule unresolved group separately. Label the shift-SD range's actual population of cells. These wording corrections leave all registered counts and the narrowed scientific conclusion unchanged.

### F13 — Minor: make the diagnostic supplement self-contained and clickable

**Evidence.** `diag_row` computes and stores `alpha`, but `DIAG_HEAD`/`diag_cells` omit it. In the rendered supplement, primary and alpha-specific labels identify alpha, while extra-gamma, unit-sigma, illustration and fixed-colouring labels do not explicitly say they use alpha = 0.01. The values are correct; I verified their block-to-alpha mapping in code. Report references to the supplement are backticked filenames, despite the response describing it as linked from the body.

**Recommendation.** Add an alpha column or a concise default-alpha legend, and turn the report's supplement reference into a relative Markdown link. This affects standalone readability and navigation, not completeness or correctness of the 212 rows.

No blocking or major finding remains open. F11–F13 are non-blocking corrections to carry into the next generated report and paper draft; they do not require a new protocol, new outcomes or another full R04 audit.

VERDICT: AGREE
