# R04 — Study 1 report: independent review, round 1

Reviewer: Codex. Baseline: `main`, `58ab64e32a9171e65e81d1a963136b228e08822a` (clean working tree before this memo). Review date: 2026-10-10, America/Chicago.

**Recommendation: REVISE the report and its supporting presentation.** The saved run, inventory, locked analyzer output and principal counts reproduce. The main problems are interpretation and reporting: a mistaken collision identity, an unsupported width-based power conclusion, over-attribution of predictor errors, incomplete diagnostics, and an undisclosed difference between R4b's locked prose and its locked implementation. These findings do not justify changing the locked protocol, analyzer or outcomes, or rerunning the grid.

## 1. Baseline and scope read

Read the root `AGENTS.md`, the complete review orientation and R04 prompt; the locked protocol, particularly §§3, 6–9, 11–12 and the lock schema; the report and prose template; `results.json`, `checks.json`, `prose_values.json` and the report tables, including the full curve and fixed-subset tables; the report builder, manifest builder, locked analyzer, relevant runner/core routines and grid; the lock, manifest, entire run log and cost records; the Milestone 2 decision-log entries, handoff, relevant brief text and gate wording constraints. Inspected all five figure PNGs and rechecked the source passages below in the existing local literature text.

Performed short, read-only computations on the saved statistics. Independently reconstructed the expected inventory and checked all cell slots, bodies and provenance; recomputed rule statistics rather than accepting `checks.json`; replayed the pinned analyzer on the saved cells with the canonical lock and intercepted its sole output write in memory. Its serialized output matched the saved `results.json` byte for byte. Reassembled the report from its saved table/value registries and template in memory: byte match. No study generation, validation run, download, corpus access, commit or modification outside this memo was performed. R01–R03's agreed design is not reopened.

## 2. Claims against evidence

### Lock, run and record

`shasum -a 256` matched all eight complete digests in `PRE_RUN_LOCK.json`. Abbreviations below identify the full hashes that were compared:

| Pinned file | SHA-256 prefix | Result |
|---|---|---|
| `outputs/study1_v0.3/VALIDATION.json` | `bddc40b57a581130` | match |
| `research/STUDY1_PROTOCOL_v0.3.md` | `0df505ef7597d4c7` | match |
| `research/study1/grid_v0.3.json` | `9e3474adfe098294` | match |
| `research/study1/s1_analyze.py` | `1a2e801986b5faa9` | match |
| `research/study1/s1_core.py` | `69a18a98481122e1` | match |
| `research/study1/s1_run.py` | `f86470aa83608688` | match |
| `research/study1/s1_validate.py` | `bc1442837e411a2` | match |
| `tools/key_policy.py` | `b1fe47d7c6721b502` | match |

The R03 resolution digest also matches, in full: `c2c5dc96a54cad187762e81b76fc6891a3c42ed271b5f627695097c5e4457547`. The lock itself hashes to `ff265b500f0dbd0cc019c883b7764fab01dd3b73b5b9e3350e2dd912337dd4fd`.

Per-path `git log --oneline -- <path>` shows no pinned-file change after lock commit `b994105`. The lock was recorded at 03:15:35 UTC, before the run at 03:26:16–04:55:50 UTC on 2026-10-10. The log records launch HEAD `efa548c`; the report builder was first committed during the run as `73868aa`. The manifest was written at 04:56:18 UTC. Cells, results and manifest first enter Git in `62aa6ea`, at 04:57:34 UTC, after completion; the report baseline follows at 05:11:29 UTC. No tracked study cells exist at the lock commit or earlier history examined.

The independently generated filename set equals the actual set: **1,248 cells, including 54 degenerate markers and 1,194 live cells**, plus 42 cost records. All expected slot/body/provenance checks passed, including the full law specification, lock/grid/code digests, required alpha blocks, N = 4,000 and recorded key-array lengths. The live allocation is 720 independent core cells at K = 500, 96 fixed core cells at K = 200, 162 small-vocabulary illustration cells at K = 2,000, and 216 other illustration cells at K = 500. These use the corresponding ranges starting at 20,000; the K = 2,000 range ends at 21,999, not every illustration law uses that many keys. The inventory digest reproduces as `a9fd2cf88b76d76a60fd5040ea50c9c907269f60af04ad4f5416c47c55ca5bc0`.

The full log reconciles to 1,194 unique computed live cells, six groups of nine markers, 42 chains, one start, one completion and exit 0; no skipped/resumed chain or error is recorded. Chain times sum to 5,372.7 seconds (1.492 hours), consistent with the 1.493-hour elapsed run. `final: false` is preserved.

The runner's logged command need not contain a literal `--lock`: its production path selects and verifies the canonical lock by default, and the start line names it. The analyzer's STUDY entry point requires the lock and validates the inventory, provenance, slots, bodies and marker status before decisions; pilot provenance is different. The in-memory replay with the lock reproduces the saved analysis. This supports faithful execution through the inspected entry points. Git and JSON cannot prove the historical absence of untracked cells, the actual time of a push, the human approval message, or an unrecorded historical command line. The analyzer's historical argv is not independently attested; do not turn these checks into a stronger claim that bypass was impossible under arbitrary execution.

### Numerical reproduction

All **3,582** recorded level means and sample SDs reproduce from per-key values. The known-mean estimates reconstructed from seven-decimal stored q-values differ from the full-precision saved estimates by at most `1.806e-8`, within the rounding bound obtained from `|e_k| ≤ 5e-8`; this is not a discrepancy in the analyzer. The exact identities and independent-colouring fourth-moment SEs also reproduce from the saved weight summaries.

| R1 block | Candidates | Eligible | Resolved | Consistent | Inconsistent | Unresolved |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 360 | 180 | 152 | 152 | 0 | 28 |
| alpha = 0.05 | 360 | 204 | 204 | 204 | 0 | 0 |
| alpha = 0.001 | 360 | 135 | 74 | 71 | 3 | 61 |
| First rule | 180 | 26 | 26 | 26 | 0 | 0 |
| Extra gamma | 120 | 57 | 47 | 47 | 0 | 10 |
| Unit-sigma predictor | 360 | 180 | 138 | 136 | 2 | 42 |
| Illustration | 126 | 99 | 77 | 74 | 3 | 22 |
| Fixed colouring | 190 | 147 | 109 | 106 | 3 | 38 |

These are independently reproduced counts, agreeing with the report. Primary R1 passes. Secondary blocks are correctly labelled descriptive; the first-rule block's 26 resolved cells would not meet the primary minimum of 30, and the report appropriately does not present its 100% share as a separate confirmatory PASS.

| Rule | Independent result | Assessment |
|---|---|---|
| R2 | 891 nonstructural checks; 18 structural checks separately; zero flags; minimum two-sided KL bound `0.2736128705`; union bound `0.000891` | PASS reproduces |
| R3 | 1,098 checks including 9 structural zeros; zero gross failures; diagnostic coverage `1027/1089 = 94.3067%`; 96 core fixed cells separately have zero gross failures | PASS reproduces |
| R3 reduction statement | 540 eligible core cells; maximum reduction `0.2830525760`; 45 cells at or above 1% | REFUTED reproduces |
| R4 | 40 raw-rule chains; 200 adjacent comparisons; no failure | PASS reproduces |
| R4b | Four longest-length comparisons pass `3 SE + 1e-9`; all fail literal `3 SE` | Locked implementation reproduces; prose needs disclosure (F1) |
| R5 | 48 raw-rule chains; 192 adjacent comparisons; no failure | PASS reproduces |

The largest reduction is the Zipf V = 10,000, s = 1, h = 0, L = 2,048 distinct cell. The smallest R2 bound occurs in the two-token, h = 1, independent, gamma = 0.5, L = 1,024 distinct cell at alpha = 0.05. R4's smallest signed tolerance margin is approximately `1.6383e-5`; R5's is `3.6158e-8`.

### Decisive literature passages rechecked

These are checks against existing local `research/literature/txt/<id>.txt`, with PDF pages counted by form feeds; no new PDF was downloaded.

- **Jovanović et al., arXiv 2506.16349, PDF p.27, Eq. 9 and adjacent paragraph:** rechecked the finite-vocabulary split calculation and the question “if similar effects can be observed in LLM watermarking.” This is an antecedent, not a new question introduced by this report.
- **Gloaguen et al., arXiv 2509.24368, PDF p.21, Figure 7/Table 2:** the existing across-key measurement uses 10,000 texts and 100 keys; reported SDs are 1.2%, 0.3%, 0.1%, and sampled maxima 17.0%, 1.7%, 1.1%. These are prior measured key effects, not values inferred from this study.
- **AutoMark, arXiv 2609.37310, PDF p.3:** “a specific deployed key can still exhibit a high false positive rate.” Rechecked the PAC-over-keys formulation on p.4 as well. The phenomenon is explicitly occupied.
- **Fernandez et al., arXiv 2512.16904, PDF p.19, Appendix A.3:** “fixing a specific key s creates preferences for certain (k + 1)-grams.” The passage describes the resulting mean shift and screening 50 candidate keys on 100 texts of 800 characters each. This supports attribution of the mechanism and existing screening practice.

Genhatharan's role is stated in the agreed gate and protocol; I do not represent a fresh full-source audit of that work in this round. The verified passages above already rule out presenting the general per-key effect as new.

## 3. Method and statistics

The primary target is precisely conditional on the realised texts, and the rule computations respect that target. I checked the following derivations and boundaries:

- **R1:** selection by core role, independent colouring, gamma = 0.5, alpha = 0.01, raw/distinct, mean M ≥ 30 and theory share ≥ 0.75; interval containment in `[2/3, 3/2]`, disjointness, and overlap produce consistent, inconsistent and unresolved statuses respectively. All statuses reproduce. For five selected cells, reconstructed all 200 key-bootstrap SD replicates using the recorded values and seeded stream, accounting for the preceding 30 text-bootstrap index draws without regenerating texts. Their percentile intervals match exactly. Samples included the resolved ratio minimum, an unresolved short raw cell, a positive h = 3 cell, and the two-token fixed raw/distinct cases.
- **R2:** recomputed `min(1, 2 exp(-K KL(average || exact_mean)))`, with the continuous conventions at observed averages 0 and 1 and structural exact means handled separately. Dependence between cells does not invalidate the union bound. Its conservatism and weak power against rare rejecting keys remain material: failure to flag is not evidence of numerical equality of means (F4).
- **R3:** used `s0² = mean((q_k-g)²)`, `g = floor(gamma V)/V`, the independent variance `g(1-g)A`, the fixed variance `g(1-g)(VA-B)/(V-1)`, and independent SE squared `[kappa4 A4 + 2 variance²]/K`. Rechecked the additive `6 SE + tau` rule and the structural-zero branch. In the two-token fixed raw h = 0, L = 1,024 example, exact variance is about `1.28050e-6`, stored SE about `1.324e-21`, and tau about `1.25001e-10`; the tolerance, correctly, governs. The corresponding distinct case is structurally zero. The huge standardized deviations at negligible SE are not substantive identity failures. Coverage is a diagnostic on shared-key cells, not a calibrated experiment-level test.
- **R4/R5:** rechecked both directions and the sum-of-adjacent-SE tolerances. These are checks of the named raw-rule quantities, not simultaneous guarantees or proofs of monotonicity for all retention rules and populations. The descriptive distinct/first rho curves also pass the same length comparison on these laws. R5 on between-text collision does not itself establish a level-SD theorem.
- **R4b:** derived the support limits from `s g(1-g)/(s gamma(1-gamma))` under independence and its `(V-s)/(V-1)` fixed-size multiplier, then evaluated the four longest-length residuals (F1).

The report generally separates descriptive secondary blocks, approximation from identity, and simulated laws from real text. Its observed per-key quantiles, sampled maxima and shares trace to the saved levels. The weaknesses are the claims drawn from those numbers, not an adverse recomputation of R1–R5. Study 2 needs a conditional collision definition, a regime-specific error account, explicit h = 3 exceptions, and precision statements that preserve the distinction between fixed-text key dispersion and population false-positive rates.

## 4. Process and presentation

The record supports no post-lock alteration of a pinned file and no recorded run restart, skipped chain or holdout access. The simulator's inputs and outputs are synthetic; `final: false` and the key namespace are correct. I did not inspect the sealed data. No terms-of-use workaround was needed or attempted.

The builder is outside the lock, as disclosed, and its checks are real: no `or True`, `assert True`, or bare `pass` disabling a check was found. Its resolved-path pilot guard rejects an output directory within the repository and chooses a fixture report path; study mode accepts canonical paths only. Source inspection supports that fixture mode cannot select the canonical report through its normal arguments. The saved generated artifacts are reproducible, but reproduction does not establish that each prose label or interpretation is semantically correct (F8).

The protocol discloses the pre-lock pilot. The Milestone 2 log also discloses viewing fixture figures after the lock and subsequent builder/template corrections. That disclosure is missing from the report itself, as are named AI-use and reviewer roles (F9). The report and decision log share the collision, attribution and width misinterpretations; agreement between summaries is not independent evidence. Keep the old decision-log entry as history and append a dated correction.

The figures' units, log axes and principal selections are mostly clear, and the tabulated series provide the full core curves behind the selected h = 1 illustrations. I found no evidence of outcome cropping that changes the numerical verdict. There are broken image links, invalid table delimiters, an overlapping title and an inaccurate “every live cell” caption (F10), and uncertainty is not fully presented in the deployer's view (F7).

## 5. Independent search

Web access was available. Made a limited general-web search with `watermark "per-key" "false-positive" after:2026-10-10`, `KGW "key" "calibration" after:2026-10-10`, and `watermark "across-key" dispersion after:2026-10-10`. No relevant newer study was located in the returned results; several hits concerned unrelated watermarking or other false-positive problems. This narrow, nearly same-day search is not an exhaustive arXiv/GitHub/documentation re-screen and supplies no evidence of novelty. No source was downloaded.

## 6. Findings

### F1 — Major: disclose R4b's locked code/prose discrepancy

**Evidence.** Protocol §9 and report Table 1 state “within 3 text-bootstrap SEs.” The pinned analyzer (`s1_analyze.py`, saturation calculation) and builder (`s1_report.py:315`) instead use `3*SE + 1e-9`. From the saved longest-length rows:

| Colouring | gamma | Absolute residual from limit | Text-bootstrap SE | Residual / SE |
|---|---:|---:|---:|---:|
| Fixed | 0.25 | `1.55431e-14` | `1.38299e-16` | 112.39 |
| Fixed | 0.5 | `1.28009e-13` | `2.82985e-15` | 45.27 |
| Independent | 0.25 | `1.63203e-14` | `2.43936e-16` | 66.90 |
| Independent | 0.5 | `1.34337e-13` | `3.55935e-15` | 37.74 |

**Inference.** Numerical saturation is excellent, to roughly `1e-13`, and the implementation tolerance existed before outcomes. This is not evidence of post-hoc rule manipulation. Nevertheless, the reported literal criterion is false in all four cells; “Deviations: none” without qualification conceals a locked specification/implementation inconsistency.

**Recommendation.** Preserve the locked artifacts and `reproduced` output. Add a report note/table stating the implemented criterion, the residuals, the failure of the literal prose-only comparison, and the numerical nature of the discrepancy; cross-reference it in the run/deviation summary. Any future formal criterion belongs to a new protocol. Do not silently edit the locked prose or rerun the grid.

### F2 — Major: correct the conditional collision and the explanation of the reduction result

**Evidence.** Report §5, line 348, says the gate's order `1/(V C_cond)` was reasoned for raw tuple laws “where C_cond is the tuple collision C_h”; §8 and decision log line 242 carry that interpretation forward. Gate residual-gap item 2 explicitly defines `C_cond=A/B` for the weights actually scored. Its exact reduction is `(1/C_cond-1)/(V-1)` for any such weights, with the stated asymptotic conditions; it is not restricted to raw counting.

For an i.i.d. population raw tuple law, `A=C0^(h+1)` and `B=C0^h`, so **`C_cond=C0`, not `C_h` when h > 0**. The saved Zipf V = 10,000, s = 1, h = 1, L = 2,048 raw cell illustrates this: `A=0.000295581558`, `B=0.017212350140`, `A/B=0.017172643792`, versus analytic `C_h=0.000294807323`.

**Inference.** The universal “below 1%” statement is refuted exactly as registered. The conditional-collision identity and its order expression are not refuted. Deduplication changes the scored weights, which the gate already accommodates.

**Recommendation.** Correct the report's derivation and append a dated decision-log correction. Retain the reduction verdict; state its observed size through `A/B`, distinguish this from tuple collision and between-text collision, and remove the proposed raw-only repair of a valid formula. The paper's theory section needs these three quantities kept distinct.

### F3 — Major: retain the visible h = 3 exceptions and withdraw the width-based power conclusion

**Evidence.** Report §6, lines 362–364, calls dispersion at h ≥ 3 “invisible against 4,000 texts,” says the finite-text term is most of the observed SD, and proposes expecting far more texts to see it at all. The decision log similarly says it sits at the floor. Yet four primary-eligible h = 3 cells have theory shares above 0.75:

| Law/rule, gamma = 0.5 | L | Theory share | Observed SD, percentage points |
|---|---:|---:|---:|
| Zipf V = 10,000, s = 1.2, raw | 1,024 | 0.7970 | 0.3567 |
| Same, raw | 2,048 | 0.8930 | 0.4894 |
| Same, distinct | 2,048 | 0.7704 | 0.3449 |
| Markov V = 1,000, raw | 2,048 | 0.7609 | 0.3245 |

All are resolved and consistent. The second cell's ratio is `0.97841`, CI `[0.89056, 1.06421]`; its two-way population variance estimate is `2.1340e-5` with SE `2.1356e-6`. The nominal `sqrt(0.01*0.99/4000)=0.1573` pp is a Bernoulli benchmark, not a universal lower bound on across-key SD. The theory share is a variance fraction, not an SD fraction. The report's assertion about more slowly decaying real-text collisions is not established by this synthetic run.

**Recommendation.** State that most h ≥ 3 candidates do not meet the theory-share eligibility threshold, with these explicit exceptions. Describe h = 4 separately. Withdraw the blanket invisibility and sample-size claims, and label real-text collision behaviour as a question. Recommend that Study 2 choose widths and precision using cell-specific collision/variance evidence and its own power work, leaving the choice to Yichen.

### F4 — Major: narrow R1/R2 conclusions and make attribution suggestive

**Evidence.** Report lines 349 and 360 say heterogeneity “is not the cause,” the pairwise predictor “never improves,” and residual normality is the binding approximation. Protocol §3 explicitly permits only suggestive attribution and requires agreement between the two subsamples where attribution matters. Equal counts inside a broad band do not compare prediction errors: on **73 of 180** primary eligible cells the pairwise point ratio is closer to one. In the fixed Zipf V = 10, h = 2, gamma = 0.25, L = 64 raw illustration cell, the common-factor ratio is `3.00382`; the two pairwise ratios are `1.33232` and `1.46459`, with pair-covariance CV `0.81435`. That is substantial improvement on one of the simulated laws.

For the three alpha = 0.001 inconsistent cells, both pairwise replicas remain poor (approximately `0.497/0.464`, `0.468/0.457`, `0.470/0.467`). This supports a remaining Gaussian-tail/discreteness problem, but does not isolate residual normality from a non-Gaussian shared shift, subsampling error or key Monte Carlo variation. The primary unresolved cells are unresolved, not registered failures at alpha = 0.01.

The “within ±20% in every resolved cell” claim is also false before rounding: resolved point ratios include `0.791798`, `1.202289` and `1.204698`. R1 certifies the registered factor-1.5 interval criterion on the tested cells, not a ±20% accuracy guarantee for real text. For a ratio of observed/predicted equal to 0.70, “20–30% over-prediction” is denominator-ambiguous: the prediction is about 43% above the observation. Finally, report line 359 says the key-mean “matches the exact binomial everywhere”; R2 supplies no flag, not that assertion, as the report's own 11.2-normal-SE example and rare-key power limits demonstrate.

**Recommendation.** Separate the registered pass, descriptive point-error range and exploratory causal account. Report both pairwise replicas, describe the h = 0 pattern as consistent with failures of the Gaussian score model/discreteness, and retain sampling uncertainty as an alternative. Remove the ±20% expected real-text accuracy and universal “never improves” claims. Replace R2's equality language with “no check triggered the registered audit,” alongside its power limitation. Use explicit ratios or a stated denominator for percentage errors.

### F5 — Major: complete the failure diagnostics, including secondary unresolved cells

**Evidence.** Table 4 lists the 28 primary unresolved cells, but shows only one pairwise ratio, covariance CV and q99. The two-subsample difference promised in protocol §3 is never surfaced. Builder lines 600–605 iterate only over secondary `inconsistent_cells`: Table 8 has 11 block-cell occurrences, while **173 secondary unresolved occurrences** are omitted (61 + 10 + 42 + 22 + 38). It also omits gamma/colouring identifiers and heterogeneity columns. The fixed-colouring block mixes gamma values, so its printed cell identifiers are incomplete. These omissions matter directly to F4; having the fields buried in cell JSON is not the promised report.

**Recommendation.** Generate a full diagnostic supplement keyed by block, alpha, law, rule, h, L, colouring and gamma, including every eligible inconsistent or unresolved occurrence. Include both pairwise predictions/ratios, their reported subsampling difference, covariance CV and correlation quantiles/max, alongside the existing sigma, M, theory share and mean-level diagnostics. Link it from the body and identify duplicated cells across descriptive blocks. Keep all secondary blocks descriptive and all locked classifications unchanged.

### F6 — Major: remove the renewed priority claim

**Evidence.** Report line 363 says “what is new here is its per-key face.” Gate constraints 13 and 16 explicitly attribute the per-key mechanism/phenomenon to the existing record. Protocol §12 disclaims priority. General references to numbered gate constraints do not supply the named attribution required where the phenomenon is discussed. The rechecked source passages in §2 establish that this is already a published object of study.

**Recommendation.** Say “measured here on these synthetic laws” and identify the contribution as the locked adequacy/retention/width comparison. Name and cite the relevant earlier work, including the gate's AutoMark and Genhatharan references, at the phenomenon/mechanism discussion. Keep the distinction between within-text miscalibration and across-key variation; neither should be presented as newly discovered here.

### F7 — Minor: show or explicitly delimit uncertainty in the deployer's view

**Evidence.** Table 14 and Figure 4 reproduce empirical key quantiles, maxima and shares. The limitations correctly state fixed realised texts and the sampled-key qualification. But the report does not give intervals for those summaries, and Figure 4's key quantile bands are distributional spread, not confidence bands. Gate constraint 12 asks for crossed key-by-document uncertainty with worst-key reporting. The saved conditional SD intervals do not meet that different request. Figures 2–3 also plot observed SD point curves without displaying their available key-bootstrap intervals.

**Recommendation.** Label key quantile bands explicitly as empirical distributional spread, state K and N at the deployer table/figure, and distinguish uncertainty conditional on these texts from uncertainty for population levels. Surface available key-bootstrap SD intervals in a supplement or plot. State the missing crossed uncertainty explicitly; if it cannot be recovered from saved sufficient statistics, defer population/extreme inference to a separately authorised analysis. Do not use an ordinary bootstrap of the sampled maximum to imply a population maximum, or treat a 100% observed level as known population certainty.

### F8 — Minor: fix generated labels and outcome numbers that escape semantic checks

**Evidence.** Report line 352 assigns “sigma² from the identities 1.00” to both unit-sigma failures. Builder line 608 reads `sigma2_model` from the unit-sigma variant, which is one by construction. The actual identity-based variances are **0.742268** and **0.715239**; the later 0.334–0.861 range is over all h = 0 distinct primary cells, not the two failures. The same paragraph says the two flagged V = 10 fixed-colouring cells “enter no rule,” although they enter R3 as structural-zero checks. They are not degenerate markers.

The length growth factors in line 361 come from `growth(..., h=1)` (builder lines 641–645), but the paragraph omits that width restriction. Line 368 claims shared-key pairing across every cell, whereas protocol §4 limits fixed-colouring pairing to lengths/rules within a chain because of traversal order. Finally, despite the blanket “every number ... filled placeholder” claim, the prose template contains literal outcome-sized assertions such as “20–30%,” “±20%” and “about 0.8.” In-memory report reconstruction proves generation, not correct sourcing of those assertions.

**Recommendation.** Fetch the identity-based variance from the underlying cell; distinguish predictor exclusions, structural zeros and markers; label the growth range h = 1; restore the fixed-colouring pairing caveat. Compute observational numeric summaries in the value registry, or mark a heuristic as such and avoid claiming universal numeric sourcing. Design constants and equation coefficients can remain literal; the issue is outcome claims and field meanings.

### F9 — Minor: put pilot and AI/reviewer disclosures in the report

**Evidence.** Protocol §11 and decision log line 238 disclose the pilot and post-lock figure-fixture viewing. The report has no corresponding pilot/fixture account and does not name Claude, Codex or the AI-use responsibilities. The orientation calls for named model disclosure including the reviewer. Calling sections “the conductor's reading” does not tell a reader who performed the work or whether R04 has agreed.

**Recommendation.** Add a generated process paragraph naming the conductor and reviewer from the actual record, Yichen's responsibility, the separated pilot namespaces, the post-lock fixture use for layout, and the current R04 status. Distinguish authoring the unpinned builder during the run from changing the locked analysis. Do not describe this round as approval until its findings are resolved.

### F10 — Minor: repair the rendered report and figure selection labels

**Evidence.** All five image links at report lines 337–345 begin `outputs/...`; from `research/STUDY1_REPORT_v0.1.md` they resolve into nonexistent `research/outputs/...`. Builder line 787 constructs the path relative to the repository rather than the report. Unescaped `|D|` and `|dev|` in Markdown table cells introduce extra GFM columns; Table 1's R2/R3 verdict cells can consequently fall beyond the declared columns. Figure 5's panel titles still overlap in the saved PNG despite the log's layout-fix claim. Its caption says “every live cell,” but builder lines 776–783 exclude nine structural zeros: 1,185 plotted cells, including the 96 core fixed cells reported outside the R3 decision.

**Recommendation.** Generate links relative to the report directory (`../outputs/...`), escape literal table pipes, wrap/shorten Figure 5's titles, and state the plotted inclusion/exclusion counts. Check the rendered Markdown as well as the PNGs after rebuilding from the corrected builder/template. These are presentation fixes; they should not touch the lock or analysis record.

VERDICT: REVISE
