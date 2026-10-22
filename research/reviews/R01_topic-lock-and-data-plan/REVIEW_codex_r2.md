# R01 — independent review, round 2

Date: 2026-10-09. Reviewer: Codex. Scope: revised topic lock and Stage 4 plan, before the data freeze.

## 1. Baseline and material read

Baseline: `main` at **`769332a78ca2d47e36a573c4dd1cda5b055efa42`**. The working tree was clean when this review began.

Read, in the requested order, `AGENTS.md`, the full review orientation, my round-1 memo and `RESPONSE_claude_r1.md`; then `KEYCOND_GATE_v0.2.md`, the revised brief, the revised corpus audit, the census JSON and the 2026-10-09 decision-log entries including D1–D3. The checkpoint's original `PROMPT.md` supplies historical scope; the user's round-2 prompt governs this memo. I also checked the current handoff, the unchanged corpus terms record, the relevant compute log, and the decisive pages of the three newly stored sources. Earlier quotation checks are documented in round 1; I did not repeat the entire original literature review.

**Assessment:** D1's narrower contribution remains worth pursuing. D2 resolves the C4 policy conflict. D3 fixes the central holdout principle. However, the response's statement that all blocking findings are resolved is premature: the new transfer target still jumps from mean shifts to tail guarantees without sufficient assumptions, and the selected Common Pile files do not match the proposed freeze/reconciliation procedure. Additional mathematical qualifications and deterministic holdout details are needed.

I treat D1–D3 as decisions already taken, not questions to reopen. This checkpoint need not deliver a theorem, implementation, timing study or empirical result. It must describe a mathematically coherent target and an executable data plan. New findings below start at F12; the disposition of every original finding is explicit in §6.

## 2. Claims against evidence

### 2.1 New primary-source checks and factual tracing

PDF pages below are one-based pages obtained by splitting the local text files at form feeds. Substring checks normalize whitespace and PDF ligatures; a literal ASCII search alone misses textGrain's `ﬁ` characters.

| Source and local file | Check | Assessment |
|---|---|---|
| OpenAI textGrain, `research/literature/txt/textgrain_openai_2026.txt`, PDF p.6 | Found “A fixed deployed key and finite precision arithmetic require empirical calibration checks” and “score only the first occurrence of each distinct context window”. | The new row accurately records the fixed-key caveat and the **context-only** retention rule. This is not generally the same retention rule as unique `(context, token)` tuples. |
| Delbianco, Tohmé, Acciarri, `2610.06317.txt`, PDF pp.10–11 | p.10 lists key epoch, language, domain and length among cell variables. **Proposition 2 is on p.11**, as are the frozen-calibration variability discussion and the `1/(n+1)` resolution floor. | The gate's pp.10–11 attribution is correct. The proposition averages over calibration samples under conditional exchangeability; it does not assert a deterministic guarantee for every frozen calibration set. |
| Gloaguen et al., `2602.06754.txt`, PDF p.4 | Found “correlated Bernoulli random variables” followed by the requirement of exactly `γ|Σ|` ones. | Correct antecedent for the fixed-cardinality model. It does not establish the new project's proposed corpus-to-FPR prediction. |

No new quotation failed after normalization, and none of the three added rows has a wrong cited page range. The accepted round-1 checks on Jovanović, Gloaguen's appendix, Fernandez, Three Bricks, Vovk, Kuditipudi and Li stand. In particular, Gloaguen already measures a per-key FPR on a real text distribution, so the current residual-gap item (i), which still says no retrieved work takes that object on real text laws, is false as written.

The new census correctly distinguishes partial viewer counts from published totals. The Common Pile card totals of 126,673 news documents, 30,987,814 StackExchange documents and 55,454 Gutenberg documents are supported by the primary cards inspected in this review. They are not counts of eligible, deduplicated, frozen units. The JSON independently records the file-format contradiction discussed in §3.2.

One response-table correction is necessary: the claim that the failed Qwen Instruct attempt was “not found” is wrong. `outputs/compute_check_2026-10-08/llama3b_offline.log:1–3` explicitly records the `Qwen/Qwen2.5-1.5B-Instruct` attempt and its missing-cache/connection failure. The successful base-model timing and the brief's principal table remain correct; this does not change the compute budget.

### 2.2 Exact fixed-size variance and the size of the correction

Let `V ≥ 2`, `m = floor(γV)` and **`g = m/V`**. Assume uniform size-`m` green sets, independent across effective seed classes, and a key-independent probability vector `w_cv`. Write

\[
A=\sum_{c,v}w_{cv}^{2},\qquad B=\sum_c w_c^2,\qquad w_c=\sum_v w_{cv}.
\]

**Item 1:** As currently defined, `δ_K = Σw_cv(G_K(c,v)−γ)` has expectation **`g−γ`**, not zero. Center at `g`, or explicitly assume `γV` is an integer. This matters to the word “exact,” even when the rounding error is practically tiny.

**Item 2:** For distinct tokens within one context,

\[
\operatorname{Var}_K(G_{cv})=g(1-g),\qquad
\operatorname{Cov}_K(G_{cv},G_{cv'})=-\frac{g(1-g)}{V-1}.
\]

Consequently, with either centering convention,

\[
\boxed{\operatorname{Var}_K\delta_K(w)=
\frac{g(1-g)}{V-1}(VA-B).}
\]

The gate's covariance structure is correct. Its coefficient is exact only after replacing `γ` by `g` or imposing integer `γV`. This remains an ideal random-green-set calculation, not a proof that a finite seeded PRNG supplies statistically independent context lists. The hash-merging and full-covariance qualifications are appropriate.

To make the stated relative correction meaningful, define

\[
C_{\mathrm{cond}}=\frac AB
=\frac{\sum_c w_c^2\sum_v(w_{cv}/w_c)^2}{\sum_cw_c^2}.
\]

This uses **squared-context-mass weights**, not ordinary averaging over the context distribution. For the independent-colour approximation `I = g(1−g)A`, the exact ratios are

\[
\frac{\operatorname{Var}\delta}{I}
=\frac{V-1/C_{\mathrm{cond}}}{V-1},\qquad
\frac{I-\operatorname{Var}\delta}{I}
=\frac{1/C_{\mathrm{cond}}-1}{V-1}.
\]

Thus `1/(V C_cond)` is an order approximation when `V` is large **and** the subtraction of 1 in the numerator is negligible. The relative reduction is exactly zero at `C_cond=1` and exactly one at `C_cond=1/V`. The useful sufficient regime `V C_cond ≫ 1` survives, but “drop the second term” also overlooks the factor `V/(V−1)`. The relevant conditional concentration must be computed for the **actual score weights**, including occupancy weights where applicable; peaked raw next-token probabilities do not automatically establish it after deduplication.

A short exhaustive calculation over two independent `V=4,m=2` green sets, with context weight vectors `(1/2,1/6,0,0)` and `(1/12,1/12,1/12,1/12)`, gave variance `1/18` both by enumeration and by this identity. Its exact relative reduction is `3/11`. This was a finite algebra check, not a research simulation.

Boundary conditions: `m=0` or `m=V` gives zero colour variance and no nondegenerate green-score z-test; `V=1` needs separate treatment. If the published detector centers at the requested `γ` rather than `g`, preserve that deterministic offset in its level calculation.

### 2.3 Occupancy weights, length and width

**Item 3:** The occupancy identity is a useful repair. For key-independent retention and `M_L>0`,

\[
E_X\!\left[\frac{1}{M_L}\sum_{u\in U_L(X)}(G_k(u)-g)\right]
=\sum_u a_u(L)(G_k(u)-g),\quad
a_u(L)=E_X\!\left[\frac{1\{u\in U_L(X)\}}{M_L}\right].
\]

Specify how `M_L=0` is handled, and whether the target conditions on score eligibility. For context-only retention, the selected first token after each context must define `U_L`; retaining all distinct tuples is a different detector. “Raw counting” likewise needs a specified document-level or pooled-position weighting convention.

Two statements following the identity are still unjustified:

* **`C(a(L))` need not fall with length.** Consider three equally likely documents with prefixes `(a1,b1,z)`, `(a2,b2,z)`, `(a3,b3,z)`, all six private tokens distinct. At `L=2`, the six occupancy weights are `1/6`, giving collision `1/6`. At `L=3`, `a_z=1/3` and the other weights are `1/9`, giving `5/27 > 1/6`. Exact enumeration confirms this. Labeling the eventual FPR behavior a hypothesis does not repair the preceding unconditional collision claim.
* **The retained set need not tend to the entire tokenizer vocabulary.** If an ergodic document process eventually covers an active support of `s<V` tokens at `h=0`, its limiting occupancy weights are uniform on that support, and

\[
\operatorname{Var}_K\delta_K\longrightarrow
g(1-g)\frac{V-s}{s(V-1)},
\]

  which is positive for `0<s<V`. Full-vocabulary coverage and its zero limit require a stated support/coverage condition. A mixture of restricted document processes requires further care even if their aggregate support is large.

**H-width:** monotonicity of collision is valid for projectively consistent raw tuple laws, because extending a tuple refines a partition. The detector's normalized, per-document occupancy weights for different widths need not form that projective family. Distinguish these cases. Even where collision decreases, FPR dispersion does not follow solely from the mean-shift identity: the scored count, conditional variance and rejection rule also change.

T1 remains a reasonable research target if its support, retention and document-process assumptions are specified. Saturation need not mean zero, and a universal decreasing collision curve should not be its premise.

### 2.4 Level approximation, local dispersion and calibration

**Item 4:** At a fixed scored count `M`, let the published z-statistic use center `b` and denominator variance `v0=b(1−b)`. Under an appropriate fixed-key CLT, with score mean `q_k` and per-score asymptotic variance `σ_k²`,

\[
\alpha_P(k\mid M)\approx
\overline\Phi\!\left(
\frac{z_\alpha\sqrt{v_0}-\sqrt M(q_k-b)}{\sigma_k}
\right).
\]

This is the gate's improved form with its assumptions made explicit. Serial dependence can **increase or decrease** long-run variance; “larger under serial dependence” is not generally true. Retained scores need not be stationary or satisfy the assumed CLT, and the exact covariance of their sum is the more general object.

For common fixed `σ`, linearization at `q_k=b` gives

\[
\operatorname{SD}_K\alpha_P(K)
\approx
\phi\!\left(\frac{z_\alpha\sqrt{v_0}}\sigma\right)
\frac{\sqrt M}\sigma\operatorname{SD}_K(q_K-b).
\]

The gate retains `σ` in the multiplier but uses `φ(z_α)`. That substitution also requires `σ≈sqrt(v0)`; otherwise the density is evaluated at the wrong point. Insert the exact fixed-size mean variance when claiming that model. If `σ_k` varies appreciably across keys, variation in `σ_k` and its covariance with the mean shift also enter the linearization.

With random `M_L(X)`, document-level FPR is a mixture over counts. The unconditional occupancy mean and a representative or observed `M` cannot simply be inserted into the displayed formula. One route is to condition on `M`, use the corresponding mean and variance, then average; another is a justified joint approximation. These are protocol/theory choices, not requirements to run anything now.

The boundedness statements are sound with their stated premise: if `E_K α_P(K)=α`, then its variance is at most `α(1−α)` and Markov gives `P_K(α_P(K)>t)≤α/t` for `t>0`. A conservative key-marginal guarantee supports the Markov upper bound, but equality to nominal `α` must not be assumed for every published comparator.

**Item 7:** replacing `N≫1/C_h` by document-level tolerance/conformal calibration is correct. For a fixed key, independent identically distributed calibration/test scores from the same law, a continuous score distribution, and rejection **strictly above** the calibration maximum,

\[
P_{D_{\rm cal}}\{\alpha_P(k,D_{\rm cal})>\alpha\}=(1-\alpha)^N.
\]

For discrete scores with strict rejection this is generally an **upper bound**, not equality; rejecting at the maximum can invalidate it. Numerically, `0.99^299=0.0495363` is correct. State the probability over calibration sets, its failure probability and tie convention. This is a conservative maximum-threshold example, not a guarantee of useful power or an automatic guarantee for all simultaneously considered keys/cells. Those choices belong in the later protocol.

### 2.5 Mean transfer is not false-positive transfer

**H-transfer's algebra:** put `d_cv=w_P(c,v)−w_P′(c,v)` and `d_c=Σ_v d_cv`. Under independent colours, the stated mean-shift variance is correct with `g(1−g)`. Under fixed-size sets its exact signed-weight extension is

\[
\operatorname{Var}_K(\delta_K(w_P)-\delta_K(w_{P'}))
=\frac{g(1-g)}{V-1}
\left[V\sum_{c,v}d_{cv}^2-\sum_cd_c^2\right].
\]

No probability-vector assumption on `d` is needed for this covariance calculation. The centering constants cancel since `Σd=0`.

**The missing implication:** this controls a difference of means. A calibrated threshold's FPR depends on the whole document-score distribution. Equal occupancy weights, vocabulary size and scored count can coexist with very different score tails.

An exact counterexample uses `V=4,m=2,h=0,M=2`, with no repeats. Define the text distributions independently of the key:

* `P` chooses `(1,2)` or `(3,4)` with equal probability.
* `P′` chooses `(1,3)`, `(1,4)`, `(2,3)` or `(2,4)` with equal probability.

Both have `a_v=1/4`; the proposed mean-transfer term is **zero for every key**. For the legitimate key with green set `{1,2}`, the green fraction under `P′` is always `1/2`; under `P` it is 0 or 1 with equal probability. Calibration on `P′` using its maximum and strict rejection has FPR 0 there and **1/2 on `P`**, for every calibration sample size. The key `{3,4}` behaves identically, so this is not a key selected adaptively after defining the distributions.

For another view, at the common green-fraction threshold `3/4`, exhaustive enumeration over all six keys gives FPR vectors

\[
P:(1/2,0,0,0,0,1/2),\qquad
P':(0,1/4,1/4,1/4,1/4,0).
\]

Their across-key SDs are `0.235702` and `0.117851`, despite identical `w,M,V`. This is an exact boundary counterexample, not a claim that the small-`M` CLT is accurate. It identifies the missing joint document structure.

Therefore T2 cannot promise a general per-key PAC FPR-transfer statement by adding the current mean-shift term to a tolerance bound. For example, a valid formulation could use a score-tail distance

\[
\Delta_k=\sup_t\left|P(S_k(X)>t)-P'(S_k(X)>t)\right|,
\quad
\alpha_P(k,D_{\rm cal})\leq\alpha_{P'}(k,D_{\rm cal})+\Delta_k,
\]

and then bound `Δ_k` under stated assumptions. A location-family approximation with controlled variance/tails is another possible route. Neither is supplied by the collision distance alone. The choice remains the conductor's research design.

T3 is an **empirical adequacy hypothesis** in general; `C(w),M,V` do not identify FPR dispersion. A predictive approximation can be useful within a specified regime with additional covariance/shape controls. Successful numerical prediction is not itself a theorem. Revise the T1–T3 acceptance language so that T3 validation alone does not license a theorem claim.

**Item 6:** extending the mean/covariance algebra to other keyed scores is reasonable, subject to finite second moments and the stated retention and seed-dependence assumptions. It supplies neither a shared level law nor a common calibration guarantee. The revision properly says that each family needs its own derivation.

## 3. Method, precision, feasibility and rule extremes

### 3.1 Question and narrowed scope

The revised target `α_P(k,D_cal)` with fresh test randomization integrated out is substantially more precise. The method-specific comparator qualifications, primary KGW study, second Gumbel family, one main remedy plus one alternative, and one power-study model make a credible three-month project possible. They do not yet demonstrate that the full remaining null grid fits the laptop. The explicit commitment to time the actual detector before a Stage 5 lock is an appropriate resolution at this checkpoint.

The scope can support the A6 standard through substantive results on approximation adequacy, length/context effects, domain/language variation, calibration transfer and power costs. There is no reason to restore optional detector families just to fill figures or tables. No result has yet established that dispersion will be large or that a new remedy will improve on existing calibration.

### 3.2 The census and freeze plan disagree about the actual files

The selected revisions' JSON records root files such as:

| Source | Pinned revision prefix | Census root evidence |
|---|---|---|
| `common-pile/news_filtered` | `59aaa8f104e1` | `.gitattributes`, `README.md`, **`news-dolma-0000.json.gz`**; 3 files total. |
| `common-pile/stackexchange_filtered` | `c0ac7373830c` | **`stackexchange-dolma-0000.json.gz`** among 46 root files including metadata. |
| `common-pile/project_gutenberg_filtered` | `3cdf6879c807` | **`project_gutenberg-dolma-0000.json.gz`** among 17 root files including metadata. |

These are compressed JSON source shards. The audit calls them 1/44/15 **Parquet** files and P5 requires their Parquet footers. The separate viewer conversion does not make the pinned source files Parquet. For news, the JSON itself distinguishes **98,092,770 original data bytes** from **152,673,253 viewer-Parquet bytes**; the audit combines the original size with the converted format.

Specify the actual pinned source paths, source format and parser, then reconcile decompressed record counts and parse failures for JSON shards. Retain footer checks for actual Wikipedia Parquet files. If choosing viewer-converted files instead, they need their own paths/revisions/completeness checks and size budget; do not silently substitute them. A partial-shard total being smaller than the full card total is expected, not itself a reconciliation failure. Exact frozen counts remain to be measured; the current card/viewer distinctions are otherwise an improvement.

### 3.3 Proceed rules P1–P8

| Rule | Assessment at its boundaries |
|---|---|
| **P1** | D2 removes the C4/HC3 conflict, and rejecting non-allowlisted document labels is a sound plan. Record the chosen Common Pile cards and license mapping in the terms check before download; the present terms file contains none of those three sources. Missing/ambiguous labels must fail or be excluded. For Wikipedia, explicitly record inherited source licensing where row-level metadata is absent. The cards' possible misassignment caveat is appropriately retained. |
| **P2** | Open, deduplicated, eligible units and a common 256-token comparison fix the main old defects. Twenty sites with 200 units each guarantees site representation, not precise per-site 1% tail estimates: at `N=200`, nominal relative standard error is about **70%**. State whether sites are descriptive strata or final inferential cells. |
| **P3** | Five named non-English language cells, each counted after filters/split, is well posed. The reported Qwen intersection prevents assuming Llama eligibility implies Qwen eligibility. Claims at longer lengths need their own counts. |
| **P4** | Two source families are named, but Gutenberg does not prove absence of overlaps or quoted text in Wikipedia/forums. Enforce cross-source deduplication rather than asserting “no overlap.” A book window starting at token 1,000 needs at least 1,024 **retained window** tokens; a raw book length of 1,024 is insufficient. Fix indexing and the reference tokenizer/window rule before filtering. |
| **P5** | Not executable for the selected Common Pile format; correct as in §3.2. Excluded or failed files must not contribute to required counts. Card counts are whole-source comparators, not exact expected yields of a selected shard. |
| **P6** | The separation between a provenance/eligibility audit and scientific use is appropriate. Duplicate detection necessarily reads text, so name it among the allowed preprocessing operations. It should emit counts/cluster identities, not examples, detector outputs or collision estimates from sealed units. The seal test is a later implementation requirement, not missing code for this review. |
| **P7** | `N≥2,500` yields about **19.9% relative standard error** if the true FPR is 1% and documents are independent; it is not a 20% confidence-interval half-width or an error guarantee at other true rates. At smaller rates the relative error is larger and at zero it is undefined. “If not, limit the claim” gives no minimum at all: a cell with zero held-out units could pass that branch while §5 promises confirmation in every register/language. Make the mandatory cells and floor binding, or explicitly omit failed cells from confirmatory claims before lock. |
| **P8** | Predetermined additions and no rehashing are good. State the initial Wikipedia shard and a finite expansion cap/order within the known inventory. A failed complete-news count has no remaining news shard to add and must fail the audit. Every addition must be included in final cross-source clustering **before scientific use**, so later cluster merges cannot move previously used open texts into the holdout. |

There is also a concrete budget/count tension. At the card-average yield, two Gutenberg shards contain `55,454×2/15≈7,394` books. Even before exclusions, an 80/20 split has about **5,915 open and 1,479 held out**. Thus it can meet the 5,000-open P4 floor while missing the 2,500-held-out P7 floor for the long-book cell. Four shards give only about 2,958 held-out books before filters and deduplication. These are expectations, not guarantees about actual shard composition. The planned expansions may be necessary, so the initial 4.5-GB total is not the budget for a guaranteed successful audit. Do not reinterpret a failure as success by citing the open count.

The crossed key-by-document uncertainty plan fixes the original independence mistake. It still needs a later protocol definition of sampling units after deduplication, confidence levels, key count and simultaneous versus per-cell claims. These details may properly wait for Stage 5; the promised holdout floor and units cannot remain ambiguous at the freeze.

## 4. Process, holdout, provenance and consistency

### 4.1 D3 is the right principle; complete its deterministic specification

Whole duplicate clusters, a registered lock hash, manifest binding, logged openings and reserved confirmatory keys resolve the central policy objections in F6/F7. The current text, however, still hashes individual canonical document IDs while saying a whole cluster goes to one side. State the deterministic **cluster identifier** used for assignment and whether deduplication retains one representative or treats a cluster as an analysis unit. Counts of documents left inside clusters are not automatically independent deduplicated units.

Before the first scientific use, freeze normalization, shingle/token rules, the MinHash threshold/seeds and clustering/transitivity convention, representative selection, and the final cluster-to-partition map. These are preprocessing choices, not requests for outcomes or code now. Finish any count-driven shard expansion before this final assignment. If a later provenance correction links an already used open item to a held-out item, quarantine the affected cluster from confirmation rather than moving prior exposure into the sealed sample.

Force the **whole cluster** containing any inspected census row open, not merely the individual row. Record stable IDs/provenance for those rows; a site name and approximate date alone may not identify one item. The resulting held-out fraction is approximate and can be smaller because of these exclusions; count it afterward. A disjoint confirmatory seed range in a named stream is an adequate practical reservation at this stage, with the ideal independent-key law distinguished from the PRNG implementation in the protocol.

Review exposure record: web rendering of the primary cards also exposed news/Gutenberg preview snippets. Conservatively add the news-360info entries with provenance `news-dolma-0000.json.gz:1` through `:30`, and Gutenberg IDs `1,10,100,10000,10001,10002,10003,10004,10005,10006`, to the already-viewed exclusion record, propagating it to their duplicate clusters. No score, collision estimate or scientific selection was made from these previews.

### 4.2 Source choice is acceptable; provenance claims need narrower wording

The primary Common Pile cards support the proposed open-content sourcing approach and disclose possible license misassignment. The old C4 blocking finding is closed by exclusion; this review does not require a new policy exception. Add the selected sources and applicable per-document license handling to `TERMS_OF_USE_CHECK.md`, which still documents the superseded source set and contains outdated access/proposal statements. This is a missing provenance record, not evidence that Common Pile is unlicensed.

The census's Gutenberg schema is **`added,id,metadata,source,text`**; it has no `created` field. The audit's shared schema and its promise of per-document vintage strata cannot be applied uniformly. `added` dates ingestion, not authorship/publication. The card supports public-domain filtering and an old-book PG19 component; it does not establish that every selected book window is pre-LLM or “pre-LLM by a century.” Keep unknown vintage as unknown, or use documented publication metadata. Likewise, a StackExchange question creation date alone does not date every answer, comment or later edit in the assembled thread. Do not infer exact content vintages from dump dates.

### 4.3 Accepted corrections remain contradicted in active summaries

The log correctly records D1–D3 and the current handoff's opening paragraph correctly says round 2 is pending. Several active sections still contradict those decisions or the new wording constraints:

* Gate line 8 retains “uncharacterised and unremedied” and a blanket unique-ngram repair; line 49 denies prior use of the per-key real-text object; line 66 promises a “closed-form dispersion law.” These contradict constraints 8–11 and the response's claim that the phrases were withdrawn.
* Gate's data-feasibility paragraph still lists C4, WikiText and HC3, optional detector families and an unsupported CPU “minutes to hours” claim. It is inside v0.2 without a historical/superseded label.
* Brief line 55 still introduces exact key-marginal guarantees for all listed families and a human-text target, despite the qualified target in line 57. The orientation's opening retains the same old universal law and broad plan.
* “First LLM measurement” in the competitor framing and the gate's later priority language should follow the new “earliest located” rule. “Validated approximation” should mean a future acceptance criterion until validation exists. The handoff correctly says no established results yet.
* The handoff's later next-step list still asks Yichen to decide source set and holdout, although its opening and the log record those decisions. Update the live instructions; preserve dated historical entries.
* The conductor response's denial of the logged Qwen Instruct failure needs correction as described in §2.1.

The new wording constraints themselves are valuable. Apply them consistently rather than adding more general cautions. The current revision can preserve v0.1 as history while presenting one coherent active scope.

## 5. Independent search and access limits

Web access was available. In this round I repeated bounded searches for `watermark` with `key-conditional` (including an after-2026-10-08/before-2026-10-10 query), `per-key false positive`, `training-conditional validity` and `seed-to-seed`. The relevant primary result again included [Gloaguen et al.'s ICLR paper](https://openreview.net/pdf?id=3aBWTYGcaT), already covered in the gate. I found no additional verified post-2026-10-08 primary result establishing the proposed corpus-to-FPR dispersion law. That is a search outcome, not evidence of absence or priority. The three additions found in round 1 are now represented in the local record and their decisive passages were checked above.

I also inspected the primary [Common Pile news card](https://huggingface.co/datasets/common-pile/news_filtered), [StackExchange README](https://huggingface.co/datasets/common-pile/stackexchange_filtered/blob/main/README.md) and [Gutenberg README](https://huggingface.co/datasets/common-pile/project_gutenberg_filtered/blob/main/README.md). The latter two displayed the same revision prefixes as the census. Some pinned/card-blob URLs returned a tool-level “not accessible” error; accessible main-card views were read, and local pinned census evidence supplies the format finding. No bot check was bypassed, and no corpus/model/PDF file was downloaded or saved. I did not contact anyone, commit, or run a study. Local enumeration and inspection commands each completed well under one minute.

## 6. Dispositions and new findings

### 6.1 Round-1 findings F1–F11

| Original finding | Round-2 disposition | What is resolved / remains |
|---|---|---|
| **F1 — dispersion law** | **Partly resolved; still open.** | Fixed-size covariance and occupancy weighting are substantial corrections. Rounding/relative-correction definitions, occupancy claims, level linearization, and mean-to-FPR transfer still need correction: F12–F14. |
| **F2 — novelty record** | **Partly resolved.** | The new/expanded competitor rows and acknowledgment of Jovanović, Vovk and calibration antecedents resolve the main evidence omission. Active residual-gap and priority assertions still contradict that record: F19. |
| **F3 — guarantee and sample size** | **Partly resolved.** | The conditioning set and withdrawal of `N≫1/C_h` are sound. Specify calibration-set probability/ties and restrict the proposed transfer guarantee: F12, F14. |
| **F4 — C4 open-content condition** | **Resolved by D2.** | No C4 or HC3 and no exception is claimed. Document the newly chosen sources before download: F18. This does not reopen D2. |
| **F5 — census/yields** | **Original count errors corrected; new implementation mismatch open.** | Partial viewer counts and oa-stackexchange enumeration are repaired. The Common Pile source-format/Parquet confusion must be fixed: F15. |
| **F6 — cross-source leakage** | **Resolved in principle by D3; specification not complete.** | Whole-cluster assignment, dropping WikiText and the stronger seal address the original design. Finish deterministic cluster assignment, expansion ordering and inspected-cluster exclusion before scientific use: F16. |
| **F7 — key adaptation/precision** | **Mostly resolved; precision boundary remains.** | Fresh confirmatory keys, screened-key independence and crossed uncertainty are now explicit. P7's escape clause and “relative error” wording need tightening: F17. |
| **F8 — proceed boundaries** | **Partly resolved.** | Common lengths, binding site representation and open eligible counts are fixed. Held-out floors, long-book yield, window eligibility and bounded expansion need completion: F17; formats: F15. |
| **F9 — human-text interpretation** | **Resolved in the revised target.** | The key-independent null and absence of detector-certified authorship are correct. Remove residual human-only shorthand from active summaries and make vintage fields supportable: F18–F19. |
| **F10 — compute scope** | **Resolved for this checkpoint, conditional on the stated Stage 5 timing gate.** | D1 and the narrowed brief are credible planning remedies; actual null-grid feasibility is still unmeasured. No new benchmark is required in R01. Remove the contradictory old CPU timing claim: F19. |
| **F11 — consistency/provenance** | **Partly resolved.** | Downrating, access confirmation and correction log are improvements. Several active summaries and the response's compute-log statement remain inconsistent: F18–F19. |

### 6.2 New findings

#### F12 — Major: the revised “exact” and local formulas still mix incompatible conventions

**Evidence:** Gate Residual gap items 1, 2, 4 and 7 use `γ` after defining `m=floor(γV)`, leave `C_cond` unspecified, retain `φ(z_α)` with a general `σ`, call dependence variance-increasing, and state the maximum-threshold equality without continuity/tie conditions. Derivations and corrected equations are in §§2.2/2.4.

**Recommendation:** define `g`, `C_cond`, centering and scored-count conditioning; give the exact variance ratio; correct the derivative and variance language; state calibration randomness and ties. Distinguish ideal identities from PRNG implementations and empirical approximations. These are textual/algebraic repairs before relying on the revised gate.

#### F13 — Major: occupancy monotonicity and zero saturation are still asserted without valid conditions

**Evidence:** Item 3 says collision falls with length and the retained set tends to the vocabulary. The `1/6 → 5/27` prefix example refutes the first general claim; an active support `s<V` has a positive limiting across-key variance. H-width also reuses raw-law monotonicity for unspecified repaired weights.

**Recommendation:** retain the occupancy identity; make length/width behavior conditional hypotheses with explicit support, coverage and retention rules. Define empty-score handling. T1 should allow nonzero saturation and nonmonotone curves.

#### F14 — Blocking: the proposed PAC transfer guarantee is not controlled by the stated transfer term

**Evidence:** T2 combines a tolerance bound with H-transfer's mean-distance term, while item 7 says the tuple law enters through that term. The two null laws in §2.5 have zero mean-transfer discrepancy for every key but a calibrated FPR jump from 0 to 1/2 for two of six keys. The same `w,M,V` also supports different across-key FPR dispersions, defeating an unrestricted reading of T3.

**Recommendation:** before accepting the mathematical target, state sufficient distributional assumptions or change T2 to bound an appropriate score-tail discrepancy; keep the mean-shift identity as one component. Treat T3 as a regime-specific empirical predictor unless a separate theorem is proved. A finished proof is not required now, but a transfer guarantee must not be premised on information that cannot control the target.

#### F15 — Blocking for the data freeze: selected source files cannot satisfy the Parquet-based plan

**Evidence:** The pinned census shows Common Pile `*.json.gz` source shards; audit §§2–3 calls them Parquet and P5 requires footer row counts. Original and viewer-converted byte totals are mixed. See §3.2.

**Recommendation:** correct formats, explicit paths, parsers and reconciliation checks for the chosen pinned representation, and separate original, uncompressed and viewer-converted sizes. No new data download is needed to make this plan coherent. Do not begin the freeze under the current P5.

#### F16 — Major: cluster assignment and expansion are not yet deterministic enough to preserve D3

**Evidence:** Audit §5 combines hashing individual IDs with whole-cluster assignment but gives no cluster key/representative convention. P8 does not explicitly settle expansion before final cross-source assignment. Inspected-row exclusion is stated at row rather than cluster level.

**Recommendation:** specify the cluster identity, deduplicated analysis unit, deterministic preprocessing parameters and order of expansion → final clustering → partition assignment → scientific use. Force all inspected clusters open and count after exclusions; quarantine later cross-partition provenance conflicts. Implement/test this at Stage 4, without reopening the chosen holdout policy.

#### F17 — Major: P7's fallback removes its floor and the initial book budget does not support it

**Evidence:** P7 permits an unspecified claim reduction even with zero confirmatory units. Twenty sites with 200 open units do not each support precise 1% FPR inference. Two Gutenberg shards average only about 1,479 held-out books before exclusions, below 2,500, though they can pass P4. “20% relative error” omits the standard-error qualification.

**Recommendation:** name mandatory confirmatory cells and a binding floor; explicitly exclude unsupported cells from confirmation rather than silently passing them. State precision as nominal relative standard error at a specified true rate. Bound the expansion inventory/budget and apply eligibility to the selected book window. Preserve P8's FAIL outcome when mandatory counts remain unmet.

#### F18 — Minor: the new source set lacks a matching terms record and a valid common vintage schema

**Evidence:** The unchanged terms check has no Common Pile entries. Gutenberg has no `created` field in the census; ingestion dates and thread creation dates do not establish the vintage of all included content. Public-domain selection alone does not prove the century-old claim for every book.

**Recommendation:** before download, record the chosen source cards, revisions and license handling; before vintage comparisons, define source-specific fields and an unknown category. Remove categorical overlap/vintage assertions unsupported by the metadata. The source choice itself is acceptable.

#### F19 — Major: active project summaries still repeat claims the response says were withdrawn

**Evidence:** Gate lines 8, 49, 66 and its data-feasibility paragraph; brief line 55; orientation introduction; stale handoff next steps; and the incorrect response-table denial of the Qwen Instruct failure. These conflict with the new constraints and D1–D3, as detailed in §4.3.

**Recommendation:** synchronize the active question, residual-gap wording, source set, compute status and result status. Preserve dated historical material with explicit superseded labels. Correct the response's factual log statement. This is application of the already accepted revisions, not a new scope decision.

The topic remains promising under D1. Acceptance of R01 should follow correction of the incoherent transfer premise and the source-format freeze plan, with the remaining plan/specification corrections recorded; it should not require empirical outcomes or reopen the decisions already made.

VERDICT: REVISE
