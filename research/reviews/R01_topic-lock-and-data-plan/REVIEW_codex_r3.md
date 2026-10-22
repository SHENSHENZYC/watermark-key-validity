# R01 — independent review, round 3

Date: 2026-10-09. Reviewer: Codex. Scope: topic lock and the Stage 4 data plan, before download or scientific use.

## 1. Baseline and material read

Baseline: `main` at **`9b403436335997405f745309c7ccfb423dda23ba`**. The working tree was clean at the start of this review.

Read `AGENTS.md`, the full review orientation, my round-2 memo and `RESPONSE_claude_r2.md`; then the changed gate, corpus audit, corpus terms check, brief's research question, orientation §1, handoff, and the decision-log entry headed “R01 round 2.” Also checked the census JSON, the dated correction in `RESPONSE_claude_r1.md`, the checkpoint's historical prompt, and relevant local source passages. The user's round-3 prompt governs the output and scope.

**Assessment: the two round-2 blockers, F14 and F15, are resolved.** The topic now has a coherent transfer target, and the selected files have an appropriate format-specific freeze plan. D1–D3 remain sound decisions. I agree to R01 at its stated planning scope. This is not a data-audit PASS or validation of a theorem, detector implementation or compute budget.

The response overstates complete closure of F13, F16 and F19. Three nonblocking follow-ups below cover a remaining retention-rule qualification, preprocessing details to settle before final partition assignment, and residual summary errors. They can be carried into the already planned Stage 4 implementation/data audit and Stage 5 protocol review; they do not require another topic/source/holdout decision or justify withholding this checkpoint's agreement.

## 2. Claims against evidence

### 2.1 Fixed-size identities and relative correction

Gate Residual gap items 1–2 now correctly define `g=m/V`, center the mean shift at `g`, and retain the deterministic `g−γ` offset for a detector centered at the requested fraction. For independent uniform size-`m` green sets over effective seed classes,

\[
E_K\delta_K(w)=0,\qquad
\operatorname{Var}_K\delta_K(w)
=\frac{g(1-g)}{V-1}(VA-B),
\]

with `A=Σw_cv²`, `B=Σw_c²`. The covariance of two distinct token indicators in one class is `−g(1−g)/(V−1)`; cross-class covariances vanish under the stated idealization. When contexts share a seed, the weights for their common token coordinates must be aggregated before forming `A` and `B`. Read the gate's “effective seed class” notation in this sense.

The definition `C_cond=A/B` is now the correct squared-class-mass average. For `0<m<V`, `I=g(1−g)A>0`, and

\[
\frac{\operatorname{Var}\delta}{I}
=\frac{V-1/C_{\rm cond}}{V-1},\qquad
\frac{I-\operatorname{Var}\delta}{I}
=\frac{1/C_{\rm cond}-1}{V-1}.
\]

The endpoints and the regime for the approximation `1/(VC_cond)` are correct. The gate appropriately excludes `V=1` and handles degenerate colour fractions separately; the ratio itself is undefined when `I=0`. Computing the correction for the actually retained weights, rather than assuming raw next-token concentration survives deduplication, closes the original issue.

I independently enumerated three small cases using exact fractions: `V=3, γ=1/2, m=1, w=(1/2,1/3,1/6)` gives zero centered mean, variance `1/54` and ratio `3/14`; uniform weights with `V=4,m=2` give variance zero; a point mass with the same split gives variance `1/4` and ratio one. All agree with the revised identities. No research simulation was run.

### 2.2 Occupancy, support and width

Item 3 correctly distinguishes retaining every distinct tuple from retaining the first token after each distinct context. With key-independent retention, the identity follows directly from linearity of expectation:

\[
a_u(L)=E\!\left[\frac{1\{u\in U_L\}}{M_L}\mid M_L>0\right],\qquad
E\!\left[\frac1{M_L}\sum_{u\in U_L}(G_k(u)-g)\mid M_L>0\right]
=\sum_u a_u(L)(G_k(u)-g).
\]

Use the explicit conditional notation above for the gate's “on `{M_L>0}`.” If zero-score documents produce no detection, their contribution to unconditional FPR is zero; the eligible-document FPR is multiplied by `P(M_L>0)`. These probability weights should not be confused with an unnormalized expectation that assigns zero on the empty case.

The withdrawal of general monotonicity is correct, as is the recorded `1/6 → 5/27` counterexample. H-width now correctly limits partition-refinement monotonicity to projectively consistent raw laws and expressly excepts arbitrary occupancy weights. T1 properly allows nonmonotone curves and nonzero limits.

One support qualification remains. The limiting formula

\[
g(1-g)\frac{V-s}{s(V-1)}
\]

holds at `h=0` **for the all-distinct-token rule**, when each document path eventually covers the same fixed support of `s` tokens. It does not follow from support size for the context-only rule mentioned in the same paragraph. At `h=0` there is one empty context; first-occurrence retention keeps just the first token, however long the document becomes. For an i.i.d. two-token process with probabilities `(0.9,0.1)`, full vocabulary coverage occurs almost surely, but its context-only occupancy weights remain `(0.9,0.1)`. With `V=2,m=1`, the across-key mean-shift variance is `4/25`, not zero. Different per-document supports in a mixture also require averaging their actual occupancy weights rather than substituting the size of their union. F20 records this remaining qualification; it does not invalidate the corrected occupancy identity or the primary tuple-deduplicated KGW study.

### 2.3 Level approximation and calibration

Item 4's fixed-count approximation is now correct under its conditional CLT assumptions:

\[
\alpha_P(k\mid M)\approx
\overline\Phi\left(\frac{z_\alpha\sqrt{v_0}-\sqrt M(q_k-b)}{\sigma_k}\right),
\qquad v_0=b(1-b).
\]

For common positive `σ`, differentiating at `q_k=b` gives exactly the revised multiplier

\[
\phi\left(z_\alpha\sqrt{v_0}/\sigma\right)\sqrt M/\sigma.
\]

The explicit treatment of key-varying variance, dependence that can raise or lower variance, and random-count mixtures resolves F12's main level concerns. In implementation, `q_k`, `σ_k` and the mean weights in this formula must all refer to the same conditioning on `M`. A zero conditional variance is a degenerate case requiring exact handling, not division by zero. These are ordinary qualifications for the later approximation check, not another universal law being claimed.

The boundedness and Markov statements are correct with their stated premises and `t>0`. Equality of the key-marginal mean to nominal `α` is no longer assumed for every comparator.

Item 7's maximum-threshold result is correct for a fixed key, i.i.d. calibration and fresh test scores from the same law, continuous scores, and strict rejection above the maximum:

\[
P_{D_{\rm cal}}\{\alpha_P(k,D_{\rm cal})>\alpha\}=(1-\alpha)^N.
\]

The discrete-score upper-bound qualification is correct. Recomputed `0.99^299=0.0495362566`. This is a probability over calibration sets for the fixed key, not a guarantee for every realized set or all cells simultaneously. The later protocol must specify any simultaneous statement and avoid reusing calibration data to choose among rules without accounting for that choice.

Two phrases should be narrower: a maximum threshold **can** cost substantial power; poor power is not inevitable. Also, it is the distribution-free sample-size bound that does not need a tuple-collision statistic. The actual threshold, its power, and discreteness/conservatism can depend on the null text law even without transfer. Replace “the tuple law enters calibration only through transfer” with that more precise statement. These wording corrections are included in F22.

### 2.4 Transfer and targets

Item 5's signed-weight variance is correct:

\[
\operatorname{Var}_K(\delta_K(w_P)-\delta_K(w_{P'}))
=\frac{g(1-g)}{V-1}
\left(V\sum_{c,v}d_{cv}^2-\sum_cd_c^2\right),
\quad d=w_P-w_{P'}.
\]

The gate now explicitly limits it to a difference of means and records the counterexample showing why that does not control FPR transfer. For the same fixed score function and rejection direction, the revised discrepancy

\[
\Delta_k=\sup_t|P(S_k>t)-P'(S_k>t)|
\]

does imply, for every realized calibration threshold,

\[
\alpha_P(k,D_{\rm cal})\leq\alpha_{P'}(k,D_{\rm cal})+\Delta_k.
\]

Conditioning on the calibration set makes the threshold fixed, so this step requires no unsupported mean-to-tail inference. For example, a same-law calibration guarantee with failure probability `β` yields a deployment bound `α+Δ_k` with at least the same calibration-set confidence. Fresh score randomization must be included in both score laws if used. Any useful further bound on `Δ_k`, or a location-family approximation replacing it, still needs its stated assumptions and validation.

**F14 is closed.** T2 is now a coherent proof target. The displayed discrepancy inequality is elementary; merely restating its definition is not a new theorem contribution. The later target should identify what estimable or structural bound is actually delivered. T3 is correctly an empirical adequacy criterion and cannot alone license a theorem. Item 6 appropriately declines a common guarantee across different score families.

### 2.5 Literature checks

The decisive quotations were checked in rounds 1–2 and are unchanged. I repeated normalized substring checks in the local texts for the retention rule now central to item 3: textGrain, PDF p.6, “score only the first occurrence of each distinct context window”; Delbianco et al., PDF p.11, the opening of Proposition 2; and Gloaguen et al.'s unified framework, PDF p.4, the correlated-Bernoulli passage. All were found on the stated pages. No new quotation/page failure was found. This is not a repeat of the entire original literature review.

## 3. Method, statistics and the data-plan extremes

### 3.1 Files and reconciliation

The selected representations now agree with the local census:

| Source | Census evidence | Revised plan |
|---|---|---|
| News, revision `59aaa8f104e1…` | `news-dolma-0000.json.gz`; 98,092,770 original data bytes; 126,673 complete viewer rows | Gzip/JSON-lines parsing and exact whole-source record reconciliation. The separate 152,673,253-byte viewer conversion is explicitly unused. |
| StackExchange, `c0ac7373830c…` | 46 root files including metadata; JSON-gzip example; 34.93 GB root total; partial viewer count | Source JSON-gzip shards, decompressed record/parse accounting; full card count only a comparator for selected shards. |
| Gutenberg, `3cdf6879c807…` | 17 root files including metadata; JSON-gzip example; 7.63 GB root total; partial viewer count | Same format-specific treatment; four initial and two possible expansion shards. |
| Wikipedia, `b04c8d1ceb2f…` | Actual `20231101.<lang>/train-00000…00002-of-<count>.parquet` paths for the selected languages | Parquet footer reconciliation; initial index 0 and capped additions 1–2 are valid inventory positions. |

The compressed Common Pile totals include small repository metadata files; this does not materially change the rounded budget. The census stores only a few filename examples for those sources, not a complete per-shard path/size manifest. The freeze should resolve the abbreviated ranges into full paths and full census SHAs; its planned manifest is the authoritative record. No physical file count or parsing outcome is yet verified, appropriately for a pre-download plan.

**F15 is closed.** P5 no longer demands a Parquet footer from JSON. During implementation, distinguish decompression failures, physical lines, successfully parsed records and semantic exclusions; record or reject malformed input explicitly rather than silently counting it as an admitted record. The complete-news target and refusal to count excluded files provide a meaningful failure condition.

### 3.2 Proceed rules and budget

P1 now rejects missing/ambiguous/non-allowlisted labels, and records inherited Wikipedia licensing. Apply the additional source-specific requirements in the terms table: all StackExchange `all_licenses` entries must pass, and Gutenberg is restricted to the public-domain label. Match normalized license identities, not a permissive substring such as `CC BY` that would also match a restricted variant.

P2–P4 now count open, eligible cluster representatives; compare registers at a common length; identify site counts as representation rather than precision; and define the book window as `[1000,1000+L)`. At `L=1024`, the source book must have at least 2,024 relevant tokens. Eligibility under Llama and the Qwen intersection are distinct, as required. Final counts must use whichever representative survives deduplication, not any longer member in its cluster.

P7 names **ten** target cells: eight at 256 tokens and two at 1,024 tokens. For an included confirmatory cell the 2,500 floor is now binding. If a capped expansion still fails, the cell is explicitly failed/excluded and cannot support a confirmatory claim. This is the explicit omission route recommended in round 2; I do not reopen it by now demanding success in every target cell. The audit should report “failed/excluded cell” separately from a full ten-cell success, rather than letting the word “mandatory” obscure the reduced final scope. P2–P4 failures remain overall failures under P8.

The precision arithmetic is correct: at true rate 1%, nominal per-key standard errors are 0.0995, 0.1990 and 0.7036 percentage points for 10,000, 2,500 and 200 independent units. Corresponding relative standard errors are 9.95%, 19.90% and 70.36%. These are neither confidence-interval widths nor guarantees at lower rates. Crossed key-by-unit inference remains a later protocol obligation.

Four Gutenberg shards average `55,454×4/15≈14,788` books, with approximately **2,958 held out before exclusions**. Six shards average about **4,436 held out**. Meeting 2,500 in expectation requires retaining about 84.5% of the four-shard average yield, or 56.4% of the six-shard yield. Actual shards, hash fractions, length eligibility and clustering can differ. The audit no longer treats these averages as guaranteed yields, and its capped failure/exclusion path handles that uncertainty.

The initial approximately 5.5-GB figure is consistent with the rounded source totals. Taking every listed expansion would roughly double it to about 11 GB of compressed/source files using whole-source average shard sizes; decompressed data and processing indexes are additional. This is a planning estimate, not a timed memory/disk audit. The next data audit must measure actual resource use and yields. No new benchmark is required during this review.

P6 correctly permits provenance, eligibility and duplicate preprocessing while forbidding scientific scores, collision estimates, calibration and example selection on the held-out data. P8 now has finite inventory limits and explicitly fails news when its complete file cannot supply a required count. The remaining operational ordering clarification is in §4.1/F21.

### 3.3 Research scope and feasibility

The corrected question and narrowed four-study plan remain credible within the stated three-month/laptop constraint, conditional on the scheduled Stage 5 timing gate. The gate's current feasibility paragraph now says CPU cost is untimed, and the old broad grid is visibly historical. The project can support substantive A6 figures/tables through approximation adequacy, variation across settings, calibration transfer and paired power costs. This is a feasibility judgment, not evidence that any proposed effect or improvement will appear.

## 4. Process, holdout and provenance

### 4.1 Holdout design

The major D3 choices are now deterministic: lexicographically smallest canonical cluster ID, one representative, a fixed SHA-256 assignment, whole-cluster exposure forcing, specified PCG64 development/confirmatory seed ranges, a manifest-bound registered lock, logged openings and quarantine of later cross-partition links. These resolve the original document-ID leakage design. There is no need to revisit the chosen 20% policy.

The implementation specification still needs three bounded clarifications before the partition map is finalized:

1. **Provisional counts before expansion.** P2–P7 depend on post-clustering, post-assignment counts, while §5.5 places the expansion decision before clustering and assignment. Make the intended iteration explicit: perform provisional clustering/assignment/counts on the current candidate pool; add the next allowed shard if a count fails; repeat within the fixed cap; then freeze the final map and run the seal test before scientific use. A provisional cluster's ID may change when members are added; this is harmless before exposure and is not permission to try new hash seeds until counts pass.
2. **Multilingual and short-text shingling.** “Word 5-gram” does not specify segmentation for Chinese/Japanese. State the segmentation rule and what happens when fewer than five units remain after normalization. Whitespace-only splitting can produce no shingles even for long CJK text. Do not treat unrelated empty-shingle sets as near duplicates or create an all-pairs bucket. Also supply deterministic tie-breaking if canonical IDs coincide. These are implementation edge rules, not a request for new scientific data analysis.
3. **Approximate matching and exposure identifiers.** LSH only proposes candidate pairs; confirming their Jaccard scores does not recover missed pairs. Under the ideal independent-MinHash calculation, 16 bands of 8 rows propose a pair of similarity 0.8 with probability `1−(1−0.8^8)^16≈0.947`, not one. State that residual near-duplicate leakage is possible, and validate the chosen preprocessing on known duplicate examples across the selected scripts. The exposure record's news `:1…:30` values came from **`metadata.provenance`** in round 2; do not assume they are physical line offsets in a subsequently filtered shard without checking. Resolve them and the book IDs to stable records, and propagate exclusions to whole clusters as already specified.

These refinements can be settled in the loader/preprocessing work already planned before scientific use and tested at the data-audit checkpoint. They do not invalidate the source-format correction or require outcomes from an unbuilt implementation now. F21 keeps them visible rather than declaring the deterministic specification completely finished.

### 4.2 Terms and vintage

The three added terms rows address F18's missing source record. The StackExchange and Gutenberg card passages agree with the primary README views inspected again in this round, showing the census revision prefixes `c0ac737` and `3cdf687`. News's sourcing/per-document-label and misassignment statements agree with the primary card inspected in round 2 on the same date; a fresh pinned-README request in this round returned a tool-level access error. I did not retrieve new corpus rows to recheck the first-row label examples; those remain census observations rather than new verification in this round.

The cards establish the collectors' stated selection and license metadata, not independent proof of every document's provenance. The audit keeps that limitation, applies exclusions, and requires no C4/HC3 exception. The strengthened all-licenses rule for assembled threads is appropriate. Sources not selected are now marked as such.

The revised vintage schema is supportable: news publication string; StackExchange question creation time with later thread content explicitly undated by it; Wikipedia dump date; Gutenberg unknown per document. The `created`-field error is removed. The book rationale still says its vintage is different from every other source despite admitting unknown individual dates; use “different source/register with unknown per-document vintage” until metadata supports a temporal comparison. This is a wording residual, not a rejection of the selected book corpus.

### 4.3 Remaining synchronization errors

The current brief's one-sentence question is corrected; the gate's “uncharacterised and unremedied” assertion and its active closed-form-law promise are removed; the broad old data paragraph is labelled superseded. The handoff no longer asks for D2/D3 again. The Qwen Instruct correction is actually present in the round-1 response. These are substantial resolutions of F19.

However, the orientation's opening still says all listed guarantees are **exact** on average and still introduces a “given human-text distribution,” then shifts to the new key-independent target. It links the question to v0.1 without clearly directing readers to the revised active statement. The gate's Gloaguen row still says “cite this as the first observation,” and its verdict retains “made the first measurement,” contrary to constraint 11. The handoff's first numbered next step still says round 2. Terms rows call selected Common Pile sources “frozen” although the status is pre-download. These should be small direct edits, not another rewrite of the historical log. F22 also covers the unsupported power/“only through transfer” wording in §2.3.

## 5. Independent search and access limits

Web access was available. I ran a bounded update search on arXiv/OpenReview for watermark plus “fixed key”/“false positive” and “key-conditional,” restricted after 2026-10-08 and before 2026-10-10. Both queries returned no results. This adds no new competitor and is not proof of novelty; the broader searches and occupants are recorded in rounds 1–2. The planned paced pre-lock literature check remains appropriate.

Primary metadata/card checks used the [StackExchange README](https://huggingface.co/datasets/common-pile/stackexchange_filtered/blob/main/README.md) and [Gutenberg README](https://huggingface.co/datasets/common-pile/project_gutenberg_filtered/blob/main/README.md), with the previously read [news card](https://huggingface.co/datasets/common-pile/news_filtered) as noted above. The pinned news raw-README request was not accessible through the web tool; no access control was bypassed. No additional corpus preview was intentionally opened in this round. No dataset, model or literature file was downloaded/saved, no study was run, and all local checks completed well under one minute.

## 6. Finding dispositions and follow-ups

### 6.1 F12–F19

| Finding | Disposition | Remaining work, if any |
|---|---|---|
| **F12 — exact/local conventions** | **Resolved.** | `g`, squared-mass `C_cond`, ratios, density argument, dependence, random-count mixture and calibration conditions are corrected. Apply the same conditioning consistently in the later implementation. |
| **F13 — occupancy limits** | **Mostly resolved; narrow residual F20.** | General monotonicity is withdrawn and support-dependent saturation allowed. Tie the explicit `s`-support formula to the all-distinct-token retention rule and common support. |
| **F14 — transfer premise, blocking** | **Resolved.** | Mean transfer is explicitly insufficient; T2 now uses a valid score-tail discrepancy target; T3 cannot establish a theorem. Actual useful bounds/proofs remain future work. |
| **F15 — file format, blocking** | **Resolved.** | The original JSON-gzip representation, paths/size distinction, parsers and P5 agree with the census. Actual file/parse checks occur at the freeze. |
| **F16 — holdout determinism** | **Core design resolved; implementation refinements F21 remain.** | Cluster IDs, representatives, exposure forcing, key reservation and quarantine are specified. Clarify provisional expansion counts and multilingual/empty-shingle behavior before final assignment. |
| **F17 — floor/budget** | **Resolved at planning scope.** | Named cells, binding floor for included cells, explicit exclusion on failure, four initial books shards and finite expansions address the finding. No guarantee is made that empirical counts will pass. |
| **F18 — terms/vintage** | **Resolved in substance.** | The terms entries and source-specific vintage schema now exist. Carry source-specific license conditions into the loader; remove the remaining book-vintage shorthand under F22. |
| **F19 — synchronization** | **Partly resolved; F22 remains.** | Major gate/brief/data changes and the compute-log correction are present. Orientation and a few other live phrases still contradict the corrected record. |

### 6.2 Residuals of F1–F11

| Original finding | Disposition in round 3 |
|---|---|
| **F1** | The original blocking universal-dispersion premise is closed by the corrected hierarchy and restricted targets. The nonblocking retention qualification is F20. |
| **F2** | Competitor evidence and the substantive residual gap are acceptable. Remaining absolute priority wording is F22. |
| **F3** | Conditioning, method-specific guarantees and the calibration sample-size basis are resolved; future protocol quantifiers remain ordinary design work. |
| **F4** | Closed by D2; no C4/HC3 exception is in force. |
| **F5** | Closed: partial counts are labelled and the format/reconciliation error is corrected. Actual yields remain unmeasured. |
| **F6** | The original cross-source split defect is closed in the adopted whole-cluster design. F21 specifies the remaining preprocessing edge rules. |
| **F7** | Closed at this checkpoint: reserved keys, independent evaluation of screened keys, crossed uncertainty and explicit confirmatory cell floors are present. |
| **F8** | Closed at planning scope: common lengths, counts after exclusion/deduplication, finite expansion and explicit failure/exclusion outcomes are now stated. Implement the provisional-count loop under F21. |
| **F9** | The target/provenance interpretation is resolved in the brief and audit; inconsistent orientation/book shorthand remains F22. |
| **F10** | Closed for R01, with the already recorded actual-implementation timing prerequisite for Stage 5. No unmeasured CPU speed claim remains active in the data-feasibility section. |
| **F11** | Substantially resolved; the remaining synchronization work is F22. |

### 6.3 New findings, none blocking R01

#### F20 — Major: the support-size saturation formula still needs its retention-rule condition

**Evidence:** Gate item 3 discusses both retention rules before giving a limit based only on `s`. First-context retention at `h=0` keeps one token; the full-support `(0.9,0.1)` example in §2.2 gives variance `4/25`, whereas the stated full-vocabulary limit would be zero.

**Recommendation:** before the Study 1 protocol, attach the formula to all-distinct-token retention with a common fixed support eventually covered on every document path. For context-only retention or heterogeneous supports, state the limit through the actual limiting occupancy weights. Keep explicit conditioning on nonempty score sets. This is a qualification of one asymptotic example, not a failure of the revised core identity or transfer target.

#### F21 — Major: complete the preprocessing edge rules before final partition assignment

**Evidence:** Audit §5 orders expansion before the clustering/assignment needed to evaluate its count triggers. Word-5-gram segmentation and empty-shingle cases are unspecified for the six-language corpus. LSH at the named settings is approximate, and the exposure record abbreviates provenance identifiers as file lines.

**Recommendation:** record the provisional clustering/count/expansion loop; pin multilingual segmentation, empty-set and ID-tie behavior; describe approximate duplicate coverage honestly; resolve exposure identifiers before forcing clusters open. Verify these in the planned loader/seal and data-audit work before scientific use. The chosen clustering/holdout policy is sound; missing implementation outcomes are not demanded at R01.

#### F22 — Minor: several active sentences still overstate the corrected record

**Evidence:** Orientation §1 retains universal exactness and human-text wording; the gate retains two “first” phrases, “poor power” as categorical wording and “only through transfer”; the handoff's next-step list is one round behind; terms say “frozen” pre-download; the book rationale asserts a vintage difference while dates are unknown.

**Recommendation:** synchronize those exact phrases with the revised brief and the verified statements above. Distinguish selected from frozen, sample-size validity from threshold/power behavior, and historical first observations from earliest located evidence. No decision, new experiment or additional source is needed for these edits.

No blocking finding remains for accepting the topic and the Stage 4 plan. Carry F20–F22 into the next implementation/protocol checkpoints at the timings specified above; retain the planned data-audit and protocol gates before scientific use.

VERDICT: AGREE
