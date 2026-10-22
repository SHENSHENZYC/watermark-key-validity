# R01 — Independent review: topic lock and Stage 4 data plan

Reviewer: Codex. Date: 2026-10-09. Recommendation: retain the fixed-key validity question, but revise the gate and data plan before accepting this checkpoint. The phenomenon and practical decision are well supported. The proposed general dispersion law, the claimed calibration sample-size consequence, and several data-freeze assurances are not yet supported as written.

## 1. Baseline and scope

Baseline: `main`, commit **`8a71845cdfb7175a6486e47b571e624b038a955f`**, obtained with `git rev-parse HEAD`. The working tree was clean before this review.

I read the root `AGENTS.md`, the complete review orientation and R01 prompt, then the requested handoff, complete decision log, brief, topic screen, C07 gate, Arena/BT gate, own-reading notes and all reader notes present in `research/literature/notes/`, followed by the corpus terms check, draft audit and complete census JSON. I checked the decisive passages against the local full texts, using `tools/grep_pages.py` and direct substring searches on form-feed-separated PDF pages. Additional reads included `tools/census_hub.py`, the relevant compute logs, and the primary web sources identified below. I did not independently reproduce the published experiments or read every cited paper cover to cover; the distinction between a checked passage and a reported experimental result matters.

This review covers the written Stage 1–4 work. Recommendations concerning a future loader, experiment or protocol are requirements for the proposed design, not allegations of bugs in code that does not exist. Local checks were short, read-only calculations and searches. No data, models or literature files were downloaded into the repository; no model, simulation study or long job was run. Only this memo is written; nothing is committed or published.

## 2. Claims against evidence

### 2.1 Decisive quotation and page checks

**None of the requested decisive quotations failed substantively or was attributed to the wrong PDF page.** Searches used exact text fragments; whitespace was normalized when a sentence crossed lines. PDF extraction renders some mathematical symbols differently, so a whole equation is not necessarily one literal substring. The interpretations attached to several correct quotations need correction.

| Source and local full text | Checked PDF page and searchable evidence | Assessment |
|---|---|---|
| Jovanović et al., `research/literature/txt/2506.16349.txt` | p.27: `only ≈25% chance`, `stratified split`, and `An interesting question, to the best of our knowledge not explored before` occur in the cited discussion. The following paragraph explicitly raises LLM subdomains, Cyrillic tokens and excessive FPR. | Correct quotation and page. **The same page also gives the hypergeometric distribution in Eq. (9).** Thus the gate's unqualified “no theory” description is inaccurate: a finite-vocabulary special case of random-key green-mass dispersion already exists. It does not give the proposed general LLM theory. |
| Gloaguen et al., `research/literature/txt/2509.24368.txt` | p.21, Table 2: maximum FPR at nominal 1% is **17.0%, 1.7%, 1.1%**; key-to-key SD is **1.2%, 0.3%, 0.1%** for Unigram, `C = {−1}`, and `C = {−2, −1}` respectively. Figure 7 contains `the seed-to-seed variation is significant`. | All requested numbers and context settings match. The table names **100 keys and 10,000 null samples**; p.22 supplies **200-token C4 realnewslike** texts. These are reported empirical rates and percentage-point spreads, not independently reproduced population FPRs. The table does not establish that its key-average FPR equals 1%. |
| Fernandez et al., `research/literature/txt/2512.16904.txt` | p.19: `fixing a specific key s creates preferences for certain (k + 1)-grams`; the discussion gives the green-fraction shift from 0.5 to 0.505 and long-text p-value collapse. Table 6 and its caption specify 100 null texts and across-key mean-p-value spreads. | Correct. Table 6 reports SDs **0.029–0.044** for mean p-values, not FPR dispersion at a specified alpha. It measures a form of key sensitivity without separating sampling noise. It is too strong to say that dispersion “is not measured.” |
| Same Fernandez paper | p.6: `testing 50 candidate keys`, selection by the KS statistic, then `1.5M Wikipedia` documents, up to 100k tokens and average 715 tokens. p.19 specifies **100 non-watermarked texts of 800 characters** for screening. | Correct. “The authors report verification on 1.5M documents” is supported. This is not an independently established guarantee for screened keys, all text laws or all lengths. |
| Three Bricks, `research/literature/txt/2308.00113.txt` | p.3, Fig. 2: `10 master keys × 100k sequences of 256 tokens sampled from Wikipedia`. p.4: `They now match perfectly, except for h = 0 where the FPR is still slightly underestimated.` | Correct. The latter follows the rule not to rescore an already seen `(h+1)`-tuple. It is an empirical statement about the plotted experiment. The residual's explanation by across-key variability is the conductor's hypothesis, not the paper's demonstrated explanation. Raw length 256 is not the number of retained scores. |
| Vovk, `research/literature/txt/1209.2673.txt` | p.2 lists the cube's unconditional, training-, object-, label-, and combined conditional notions. | Correct. This supplies the conceptual analogy. Also relevant, but underused in the gate: pp.3–6 explicitly discuss PAC training-conditional validity, calibration sample size and classical tolerance regions; Proposition 2b supplies a binomial condition. |
| Kuditipudi et al., `research/literature/txt/2307.15593.txt` | p.6 contains `independent, identically distributed copy` and `uniformly distributed over {1/(T + 1), 2/(T + 1), . . . , 1}` for a non-atomic statistic. | Correct quotation. Explain the symmetry **conditional on the fixed text**; pairs sharing that text are not unconditionally independent merely because keys are independent. The finite Monte Carlo p-value is discrete. Its rejection probability is at most alpha, with equality only at appropriate attainable levels or with suitable extra randomization; ties require the stated qualification. |
| Li et al., `research/literature/txt/2404.01245.txt` | p.8: `we regard ζ as a random variable`. | Correct. The immediate definition concerns unbiased generation. Read together with the working pseudorandomness assumptions and detection theory, it supports averaging over auxiliary randomness. The quotation alone is not a theorem of exact finite-sample Type I error for every implemented PRF or every proposed comparator. |

Two small numerical checks clarify interpretation. With Jovanović's stated `|V|=192`, 48 green tokens and 12 alive tokens, Eq. (9) gives

\[
\Pr(G_{\rm alive}=3)=\binom{48}{3}\binom{144}{9}/\binom{192}{12}=0.26653484.
\]

The paper's approximate 25% is a rough characterization, faithfully quoted by the gate. Under independent uniform p-values, the SD of a 100-text mean is `sqrt(1/(12×100)) = 0.02887`. That is a useful reference for Fernandez's table, but does not prove all its 0.029–0.044 variation is noise, especially with shared texts and imperfect null uniformity.

### 2.2 Dispersion derivation, line by line

Let `P` be a specified null document law independent of the random key `K`. First consider a token-weighted statistic without deduplication, with a well-defined tuple distribution `p(u)` and `E_K G_K(u)=gamma`.

**Mean.** The identity

\[
\delta_k=\sum_u p(u)(G_k(u)-\gamma)
\]

is correct for that weighting, and `E_K delta_K=0` follows from unbiased colouring. Independence between positions in a text is not required for this mean identity. However, the law of a randomly chosen scored position, a document-averaged law, and a corpus token-frequency law can differ. The gate must specify which it uses.

**Variance.** The general identity is

\[
\operatorname{Var}_K(\delta_K)
=\sum_{u,v}p(u)p(v)\operatorname{Cov}_K(G_K(u),G_K(v))
=p^\top\Sigma_Kp.
\]

The gate's `gamma(1−gamma) sum_u p(u)^2` follows if distinct tuples receive pairwise independent Bernoulli colours. This is an ideal independently coloured tuple model. It does **not** automatically describe KGW.

For a concrete KGW-style model, let `u=(c,v)`, let the vocabulary size be `V>1`, and draw a uniform green subset of exactly `m` tokens independently for each context `c`. Write `gamma=m/V`, `p_c=sum_v p_cv`, and assume different contexts have independent random subsets. Distinct tokens in the same context have covariance `−gamma(1−gamma)/(V−1)`. Therefore

\[
\boxed{\operatorname{Var}_K(\delta_K)
=\frac{\gamma(1-\gamma)}{V-1}
\left[V\sum_{c,v}p_{cv}^2-\sum_c p_c^2\right].}
\]

This is an elementary finite-population correction, not by itself a novel theorem. With `h=0` and a uniform vocabulary law, it is **zero**, whereas the gate gives `gamma(1−gamma)/V`. If a context hash merges distinct contexts, aggregate their masses into the actual seed-equivalence classes before using this model. Structured hashing or dependence between those classes can require the full covariance formula. A finite seeded PRNG/PRF is a further implementation assumption; computational pseudorandomness is not an identity of statistical independence over all inputs. If `gamma V` is not integral, account for the implementation's rounding and actual green fraction.

**Within-text dependence and the normal approximation.** For IID tuple draws under a fixed key, put `q_k=gamma+delta_k`. The conditional Bernoulli variance is `q_k(1−q_k)`, not necessarily `gamma(1−gamma)`. More generally, if a suitable conditional CLT holds with long-run variance `sigma_k^2`,

\[
\alpha_P(k)\approx\bar\Phi\!\left(
\frac{\sqrt{\gamma(1-\gamma)}z_{1-\alpha}-\sqrt n\,\delta_k}{\sigma_k}
\right).
\]

Here `sigma_k^2` includes serial covariances of the score process when that description is applicable. The gate's formula additionally assumes `sigma_k≈sqrt(gamma(1−gamma))`, adequate CLT/tail accuracy, and a specified number `n` of retained scores. Overlapping language tuples are dependent; stationarity/mixing, document heterogeneity, rare-event accuracy and key-dependent variance cannot simply be omitted. The z-score requires `0<gamma<1`; at either endpoint its denominator vanishes. Zero conditional variance, tiny `n` and extremely small alpha are further boundary cases where this approximation is inappropriate.

**The stated comparator changes the weights.** The brief explicitly uses the repeated-tuple repair. For raw document length `L`, let `U_L(X)` be the retained unique tuples and `M_L=|U_L|`. When `M_L>0`, its mean green fraction is

\[
\sum_u a_u(L)G_k(u),\qquad
a_u(L)=E_P[\mathbf1\{u\in U_L(X)\}/M_L].
\]

These weights are not generally `p_h(u)`. They depend on length and occupancy, and the random denominator and joint inclusion probabilities also affect the test's distribution. Even a variance identity for the mean is not a formula for the tail rejection probability. Define the zero-score decision and retain both raw length and scored count in the design. Tuple deduplication also does not remove all dependence caused by using the same fixed-size green list for different tokens in one context.

**Consequences and extremes.**

* For the independent-colour, small-shift, approximately constant-variance model, first-order linearization yields `Var_K alpha_P(K) ≈ phi(z)^2 n C_h`. This gives a useful **local heuristic**, not a universal law for FPR dispersion.
* FPR lies in `[0,1]`. Its variance is at most `1/4`, and at most `alpha(1−alpha)` when its key mean really equals alpha; moreover `Pr_K(alpha_P(K)>t)≤alpha/t` under marginal level control. Indefinite growth with `sqrt(n C_h)` cannot be a literal conclusion.
* Length growth can fail for the repaired detector. At `h=0`, once a document contains every vocabulary token, deduplication retains exactly the vocabulary, its green fraction is gamma for every fixed-size key, and a positive-threshold green-count z-test has no across-key variation. In contrast, repeatedly counting one identical tuple can make the *marginal* raw z-test invalid as well: at large length it rejects whenever that tuple is green, with probability gamma over keys, rather than a small nominal alpha.
* For consistently nested tuple laws, `C_{h+1}≤C_h`; a steep decrease does not follow from a Zipfian unigram law. More strongly, the corrected fixed-size variance need not decrease with `h`. A stationary two-token Markov chain with marginal probabilities `(0.5,0.5)` and transition probabilities 0.9 to stay, 0.1 to switch has `C_0=0.5`, `C_1=0.41`. With one green token per context, mean-shift variance is 0 at `h=0` and 0.08 at `h=1`. Enumeration of the two and four possible colourings confirms these values. This is a counterexample to a general context-width monotonicity claim, not a prediction about natural language.
* Dependence on subdomain and language is plausible and follows through the full text law and covariance structure. Its sign, magnitude and fairness interpretation are empirical questions. Equal raw-token lengths under different tokenizers need not represent equal text content or equal numbers of scores.
* For a general keyed score `s_K(u)`, a covariance quadratic form still applies to its mean under appropriate moments. Gumbel, inverse-transform, tournament and activation statistics need their own score law, shared randomness and rejection rule. Replacing `G` by a score symbol does not prove the same `C_h` law or a CLT for all of them.

### 2.3 Remedies do not yet follow as guarantees

The condition `N≫1/C_h` can arise when comparing IID Monte Carlo uncertainty in an estimated **mean shift** with its typical across-key size. It is not a general sample-size requirement for controlling a document-level FPR. Calibration depends on the target tail probability, confidence/tolerance, number of independent documents, ties, selection and distribution matching.

For a fixed score and key, independent calibration documents and a future document give an ordinary conformal rank guarantee averaged over the calibration sample. For a deployer who also freezes that sample, use an explicitly stated tolerance/PAC guarantee. Vovk's existing pp.3–6 already give that machinery. As a simple illustration under continuous IID scores, setting the threshold to the maximum of `m` calibration scores gives

\[
\Pr_{\rm cal}\{\Pr_P(S>\max_i S_i\mid k,\mathrm{cal})>\alpha\}
=(1-\alpha)^m.
\]

Thus `m=299` suffices for a 1% tail bound with 95% calibration confidence for this conservative rule, regardless of `C_h`; its power may be poor. This is a check of the claimed necessity of `N≫1/C_h`, not a proposed final protocol. A useful contribution would quantify the power/validity trade-off and any *additional*, key-sensitive efficiency result beyond existing rank/tolerance theory.

Stratification requires a specified randomization with feasible integer quotas, frequency estimates learned on permitted data and an explicit covariance calculation. Jovanović's alive/dead split is an existing special case; “removes the between-stratum part” needs a defined decomposition. Averaging independent key-specific **mean shifts** divides their variance by the ensemble size. It does not automatically control FPR conditional on the realized ensemble, validate averaging p-values, or preserve watermark power. E-value averaging retains the relevant marginal expectation guarantee only under its assumptions. Averaging all independent colours of an arbitrary fixed text can remove the watermark signal as well as the null shift. Specify which keys participate in generation and detection, and evaluate the resulting power.

## 3. Method, precision and feasibility

### 3.1 Research question and residual contribution

The decision, information set and basic failure mechanism are clear: someone deploys one secret key and needs a reliable error statement for a stated null population. The target needs the full conditioning set. For example, distinguish

\[
\alpha_P(k)=\Pr_{X\sim P,R}\{\mathrm{reject}(X;k,R)\}
\quad\text{from}\quad
\alpha_P(k,D_{\rm cal})=\Pr_{X\sim P,R}\{\mathrm{reject}(X;k,D_{\rm cal},R)\}.
\]

`R` denotes any fresh test randomization, including resampled reference keys. State whether the desired result is for each key, most random keys with a specified failure probability, a screened-key selection procedure, or an average over calibration samples. These are different guarantees. A fixed-key deterministic detector cannot have nontrivial error control uniformly over *every* possible null text law: any rejected text can be made a point-mass null. A distribution-specific or calibrated claim is the natural scope here.

The current comparator list mixes approximate z-tests, discrete randomization tests, ideal pivotal tests and sequential tests. Replace “exact on average” as a blanket assertion with a method-specific guarantee and assumptions. Specify each detector's repeat rule and, for an e-process, the filtration and stopping rule. Measure marginal miscalibration separately from across-key dispersion; showing the former is not evidence that only the latter is present.

**Residual-gap judgment:** a systematic predictive account of across-key FPR, tested across declared lengths, context constructions and text populations, remains a plausible useful project. The existence of the effect, its mean-shift explanation, some finite-vocabulary theory, key screening, per-key empirical calibration and general calibration sample-size theory are already occupied. New sources in §5 reinforce this. The corrected covariance identity alone is standard algebra. A strong theory claim needs an additional result about the actual repaired detector, dependence, tail approximation or a practically predictive bound. An adequacy paper could still be valuable if those ambitious universal claims fail, provided its primary question and reporting are fixed before results. I would not abandon C07 for the rejected Arena question on the present evidence, but would not accept the present “closed-form dispersion law” as an established reason for PASS.

### 3.2 Precision and the proceed rule

The gate's nominal `10^4` independent texts for approximately 10% relative standard error at true FPR 1% is correct. It is not a uniform precision guarantee across keys or populations. The following calculations use IID documents and a true 1% rate; they exclude calibration and key-sampling uncertainty.

| Evaluation documents per key | Expected false positives | FPR standard error, percentage points | Relative standard error |
|---:|---:|---:|---:|
| 1,250 | 12.5 | 0.2814 | 28.1% |
| 2,500 | 25 | 0.1990 | 19.9% |
| 5,000 | 50 | 0.1407 | 14.1% |
| 10,000 | 100 | 0.0995 | 9.95% |
| 50,000 | 500 | 0.0445 | 4.45% |

At 10,000 documents, measurement noise is approximately **equal to** Gloaguen's reported 0.1-percentage-point context-two spread, not below it as audit §4 says. At true FPR 0.1%, 10,000 texts give only ten expected events and roughly 31.6% relative SE. Zero observed events do not establish zero FPR; the one-sided 95% IID binomial upper bound is about `3/N`.

The same documents under all keys form a crossed key/document design. The observed dispersion of estimated FPRs combines actual key variation and finite-document effects; repeated texts couple the errors across keys. Use an analysis that acknowledges both random sources, with suitable document clustering and uncertainty for key quantiles. Do not treat all `keys × texts` cells as independent observations, or subtract one universal binomial noise term without justifying the model. “Worst key” must mean worst among the sampled keys. At 500–1,000 keys, the most extreme key-tail estimates have few observations.

The rules need these boundaries resolved before freeze:

* **P1:** its “met on paper” status is unsupported for C4 under the brief's open-content requirement (§4 below).
* **P2–P4:** explicitly define all minima on the **open, deduplicated, eligible document/cluster counts**, as §5 intends. State that all required inequalities are conjunctive and how excluded files affect them. Counts before filters or before the holdout do not count.
* **P2:** the forum's 128-token exception is a defensible source constraint, but comparisons at 128 versus 256 tokens confound register and length. Require a common-length comparison where feasible. Twenty sites is only a nominal yield, not a binding subdomain rule; 10,000 answers could otherwise be dominated by one site. If site contrasts are essential, declare which sites/minimum counts support them, or limit that claim.
* **P3:** the five languages are named in the plan, which is good. Count them after filtering and splitting. Under Qwen tokenization, a passage meeting a Llama length threshold need not meet the corresponding Qwen threshold; define matched-document and matched-length analyses separately.
* **P4:** two named sources do not ensure independent long-document support if those sources are WikiText and Wikipedia. Record overlap and decide whether this is a two-source or a two-independent-population requirement.
* **P5:** retain raw row counts before cleaning separately from document counts after reconstruction. A metadata mismatch needs a recorded reason; excluding a failed file must not silently let a required complete split become “complete.” Unversioned viewer counts are not automatically exact counts for a pinned original snapshot.
* **P6:** distinguish the permitted metadata/length/deduplication audit from scientific use of sealed text. “Before any statistic” otherwise conflicts with the audit itself. No detector scores, empirical collision estimates for Study 1, calibration, or manual example selection should use the holdout before its authorized opening.
* **Holdout precision:** 10,000 open documents under an approximately 80:20 split implies only about 2,500 held out; 5,000 open long documents implies about 1,250. The confirmatory sample can therefore have 20–28% relative SE at 1%, even when the open-data rules pass. Specify a holdout event/precision floor aligned with its claim, or explicitly accept that limited resolution.
* **Extremes/fallback:** a hash split gives an expected fraction, not an exact quota; a small eligible stratum may have no holdout observations. Predetermine additional-shard order and failure handling, rather than rehashing until counts pass. Option 3 has only two English registers and cannot satisfy the current P2. It needs an explicit revised rule if selected. A licence caveat alone cannot make Option 2's unresolved HC3 sources meet P1.

### 3.3 Three months, measured compute, and A6

The brief's main throughput table agrees with `outputs/compute_check_2026-10-08/qwen1.5b_llama1b.log` and `llama3b_offline.log`: batch-eight generation is 267.5, 197.1 and 110.8 tokens/s for Llama 1B, Qwen 1.5B and Llama 3B; allocated memory is approximately 3.24, 3.31 and 7.24 GB. The logged Qwen **Instruct** attempt failed; the successful Qwen timing is for the **base** model. The distinction is correctly reflected in the principal table and should survive protocol selection.

Recomputed projections: 5,000 × 256 generated tokens take **1.80 hours** at 197.1 tokens/s or **3.21 hours** at 110.8 tokens/s, before study-specific overhead. Forward scoring 10,000 × 256 tokens takes approximately 26 minutes at 1,647 tokens/s or ten minutes at 4,474 tokens/s. These support a modest power check. The benchmark generated only 128 new tokens and logs an attention-mask warning for batching; longer prompts, actual masks, watermark hooks, sustained thermal performance and usable output lengths still require a short study-specific pilot. The previous project's 3.6-hour hooked timing is reported context, not independently verified here.

The brief's “24-hour run budget” of 15–20 million scored / 1–2 million generated tokens is substantially more conservative than multiplying its measured 3B rates by 24 hours (about 142 million / 9.57 million). That is acceptable as an operational allowance, but label the downrating rather than presenting it as the direct throughput projection. The gate's one-to-three-hour wording also slightly understates the largest unhooked 3B setting.

The null-side “minutes to hours” claim is **not measured by these model benchmarks**. Even one 256-token cell entails 0.64–12.8 billion token-key evaluations across the proposed 500–1,000 keys and 5,000–50,000 texts; at 1,024 tokens the upper end is 51.2 billion. Methods, widths, corpora, languages and tokenizers multiply this. KGW implementations that construct vocabulary permutations and key-resampling tests can cost much more than a constant-time hash per token. An efficient surrogate must be labelled rather than silently replacing the named comparator. Memory also requires blocking or sufficient-statistic accumulation, not materializing every token/key result.

**Feasibility judgment:** approximately three months is credible for a narrowed four-study sequence: a corrected primary KGW theory/simulation study; a bounded null-data grid with a second score family; one principled calibration remedy plus a limited alternative; and a paired power check on one small model. The full cross-product plus SynthID, activation transfer, ensembles, edits, multiple models and every proposed tokenizer is not yet budgeted. Fingerprints/copyright traps should remain motivation unless a separate setting is actually evaluated. This is a scope recommendation for Yichen, not a decision to remove a study.

A6 can be met with substance without adding families merely to create panels. Five plausible generated figures cover theoretical approximation/counterexamples, key-FPR distributions over length/width, predicted-versus-observed dispersion, calibration-size/transfer curves, and validity–power/edit trade-offs. Five distinct generated tables can report corpus eligibility/overlap, marginal and key-tail error summaries, approximation diagnostics, calibration reliability across deployment cells, and power/quality/runtime costs. These are proposed outputs, not promised findings. The operative standard in the brief/handoff is **4–6 figures and 4–6 tables**, stronger than the orientation's compressed “figures and tables” wording. Drafting, a reviewer cycle and the once-opened confirmation need time within the three months.

## 4. Process, terms and holdout

### 4.1 Licences and provenance

Dropping HC3 as the default is well justified by the recorded conditional licence, unknown medicine/finance rights and the distinction between a Reddit-derived content licence and an ELI5 code licence. An openly licensed Stack Exchange source is a reasonable replacement for the forum *role*, not a like-for-like replacement for HC3's populations. Its accepted-answer selection and under-1,000-character cap change the estimand and length coverage. The [Stack Overflow licensing page](https://stackoverflow.com/help/licensing) independently confirms the date-dependent CC BY-SA 2.5/3.0/4.0 regime. The revision-pinned `oa-stackexchange` card was inaccessible through this review's web tool; the selection details are traced to the local terms record and census, not represented as a newly verified raw-data audit. Retain the source licence/provenance chain and available attribution information at freeze. A site name alone is not an article/answer lineage identifier. The H4 fallback needs its own terms check if selected.

**C4 is the unresolved exception.** [ODC-BY §2.4](https://opendatacommons.org/licenses/by/1-0/) explicitly separates database rights from rights in individual contents. [Common Crawl's terms](https://commoncrawl.org/terms-of-use) reserve third-party content rights and recognize separate content terms. The research purpose and a promise not to redistribute do not establish that every underlying news page is openly licensed. This does not establish that local statistical research is unlawful; it establishes that the documented reasoning does not meet the brief's stronger “openly licensed corpora only” commitment. Keep P1 unresolved for C4 until Yichen selects a clearly licensed replacement or expressly revises the constraint with an adequate use basis. Do not silently treat a policy exception as already granted.

The CC BY-SA interpretation is substantially sound for the stated local analysis and publication of aggregate numerical results. [The 4.0 legal code](https://creativecommons.org/licenses/by-sa/4.0/legalcode.en) distinguishes reproduction from sharing and attaches the relevant sharing conditions to the latter. Keep that conclusion limited to the actual outputs; it is not a blanket statement about possible future text examples or redistributed tokenized content. The WikiText card-version discrepancy is properly disclosed. [Wikimedia's dump guidance](https://dumps.wikimedia.org/legal.html) identifies the general CC/GFDL regime but also exceptions and controlling source notices. Preserve the notices applicable to the frozen material rather than declaring every fragment identically dual-licensed. These qualifications do not make Wikipedia analogous to C4's wholly unresolved content licensing.

The tokenizer choices are already present and pinned; they are not a missing decision. Remaining details include actual tokenizer-file checksums, normalization, special tokens, BOS/EOS treatment, chat templates, truncation/window selection and whether added/special tokens enter the colourable vocabulary. Cached files establish availability, not by themselves the history of licence acceptance. Record the claimed existing Llama entitlement and applicable use-policy check; do not equate the cache with proof of an account's acceptance. Qwen's Apache licence is the simpler documented option if access provenance is uncertain.

### 4.2 Census and document construction

The stored census has `datasets["allenai/c4"]["size_partial"] = true`. It reports 1,809,584 train rows in the viewer response, while the original revision's tree lists 513 compressed JSON files totaling 15,435,025,687 bytes; the viewer's converted parquet total is 3,179,185,383 bytes. `tools/census_hub.py` records the global partial flag but does not preserve per-config/per-split partial status or demonstrate that the unversioned viewer counts match the pinned original tree. Consequently the audit cannot safely describe 1,809,584 as the full 512-shard train count or divide it by 512 to obtain approximately 3,500 documents per shard. The resulting approximately 42,000-document yield is unsupported.

As an independent warning, the [TensorFlow Datasets C4 catalogue](https://github.com/tensorflow/datasets/blob/master/docs/catalog/c4.md) lists 13,804,817 realnewslike training examples in its version. That is **not** a replacement count for the pinned Hugging Face snapshot—its validation count also differs. Reconcile version-specific counts at freeze and identify which published counts are complete. The 13,863 validation count need not be wrong just because the dataset-level response is partial.

For `oa-stackexchange`, the stored tree census lists nine root files and one directory, not the fourteen data parquet files themselves. The total row/byte figures are recorded elsewhere in the metadata, but the stated two-shard selection still needs exact paths and file sizes. Similarly, “first shard” does not guarantee a random sample of the source: article order, IDs or topical sorting can affect representativeness. A hash split within selected shards does not repair source-selection bias. Describe the target as the selected snapshot/shards unless the sampling design supports broader inference.

The proposed document units are mostly appropriate. Specify WikiText's single-equals article-boundary grammar, distinguish section headings, preserve article continuity across file boundaries where applicable, and reconcile lines before reconstructing articles. Freeze the detokenizer and all normalizations. For forum data, group answers by their parent question/thread and preserve available site/lineage metadata; answer text and question text should not be silently concatenated. For all sources, keep a count flow from raw rows to parsed documents, duplicate clusters, language/length eligibility and final partitions.

### 4.3 Holdout

A deterministic document-level hash split is a good starting point; keeping all windows of an article together is essential. The current proposal has three substantive gaps:

1. **Cross-source leakage.** Audit §8 acknowledges Wikipedia/WikiText overlap, while §6 only removes exact duplicates *within* a source. The same article can hash differently by Wikipedia ID and WikiText title, entering the holdout in one source and development in the other. “Never pooled” does not stop tuning leakage. Establish cross-source exact/near-duplicate and article-lineage groups before partition assignment, including old/new versions and any news/forum copies where detectable. Assign the whole group to one side, or explicitly exclude overlap from confirmation. Use a declared namespace for genuinely different IDs and a common canonical identity for linked content; specify text normalization and handle missing/colliding identifiers.
2. **Key adaptation.** “What can be over-fitted is the text, not the key” is false. Statistic choices, hash constructions, screening criteria and hyperparameters can adapt to a finite set of benchmark seeds. Fresh keys being cheap is the reason to reserve/generate independent confirmatory keys after design freeze. Separately, evaluate a screened deployed key on independent text without selecting it using final results. Neither form of key separation replaces document separation.
3. **Opening authority and scope.** Passing any object with `final: true` is only an interface guard, not evidence of the authorized final lock. Bind access to the specific approved protocol/version, data/split manifest and allowed analyses; record the opening. Preserve a distinction between a metadata-only eligibility audit and scientific use. Manual inspection must use open documents. Record any first-row examples already viewed during the access census. Treat later hypothesis changes after opening as exploratory and needing new confirmation, not as another opening of the same untouched holdout.

No cryptographic protection against the repository owner is necessary. The purpose is to prevent accidental or unrecorded use and make the single confirmatory opening auditable. No loader was implemented or tested in this review.

### 4.4 Null provenance and consistency

Audit §1 is right that suitably key-independent unwatermarked LLM text can be a null for watermark detection. But it then says contamination “only shifts the text law slightly,” without evidence, and describes pre-2022 sources as supporting a “human-only” reading. The research target is explicitly sensitive to the text law. Synthetic, templated or mixed text could materially change concentration and key FPR. A vintage before widespread ChatGPT use is useful provenance, not proof of exclusively human authorship. State a key-independent null-text target separately from any human-authorship target; retain vintage/source strata and a provenance sensitivity analysis. Do not use another AI detector to certify the null population. Text selected with knowledge of the tested key is a different setting.

The handoff and decision log consistently identify C07 as locked, C05 as failed and Stage 4 as pending before a data freeze. I found no evidence in the reviewed record that an outcome-driven protocol change has occurred. The Arena gate gives a concrete occupancy reason for its rejection rather than merely a preference for C07. It does not need reopening to resolve the present findings.

Several claims need synchronization without rewriting decision history: Stage 2's “no retrieved work takes the per-key FPR as its object” was superseded by the Stage 3 appendix findings; the gate introduction's “uncharacterised and unremedied” contradicts its own table; “no theory” for Jovanović overlooks Eq. (9); and “one key in experiments” should be limited to verified cases, not inferred from an unstated key count. The theory proposal is labelled as an inference in §Residual gap, but “with a closed-form dispersion law” later reads as a delivered result. Record these as corrections, leaving the historical sequence visible.

The seven wording constraints are a good foundation. Add: method-specific exact/conservative/asymptotic/PRF assumptions; every source of randomness being conditioned on; explicit distinction between mean-score and FPR dispersion; random versus screened/ensemble keys; limits of calibration under domain shift; human versus key-independent null provenance; finite-population antecedents; and “earliest located” rather than an absolute first-measurement priority claim. A calibration guarantee is not a guarantee for every future corpus. A statistical language disparity is not by itself a demonstrated real-world discrimination claim. The early-preprint mitigation should remain a proposal consistent with the recorded publication process, not permission to publish early. The absent SynthID supplement and postponed paced re-screen remain disclosed access/completeness gaps, not evidence that those sources lack a result.

## 5. Independent search

Web access was available. On 2026-10-09 I searched combinations of `key-conditional`, `fixed key`, `per-key false positive`, `seed-to-seed`, `training-conditional validity watermark`, `conditional validity randomized test`, and text-watermark calibration. I also used an explicit `after:2026-10-08 before:2026-10-10` date window, followed primary arXiv/OpenReview/publisher and official technical links, and checked the licensing sources above. Search indexes are incomplete; these are bounded search findings, not proof of absence. I did not locate a verified new post-October-8 paper that resolves the full dispersion problem. I did locate relevant **missed** work already available on October 5:

* **Li et al., textGrain: Entropy-Calibrated Watermarking for Language Model Text**, technical report dated **October 5, 2026**, [official report, §3.2, PDF p.6](https://cdn.openai.com/pdf/e9508624-d767-41b6-a26d-e34ca798ada6/textgrain-entropy-calibrated-watermarking-for-language-model-text.pdf). It derives the ideal text-conditional Gamma null using independent context randomness and only first occurrences of contexts, then states: “A fixed deployed key and finite precision arithmetic require empirical calibration checks”. The next clause explicitly denies a per-key/application guarantee from that ideal calculation alone. This strengthens the practical motivation and occupies an additional explicit statement of the limitation; the checked section does not give an across-key FPR dispersion law. Add it to the competitor/wording record. Context-only deduplication here also illustrates why one universal tuple-repair description is inadequate. This is an inspected report passage, not a reproduction or evaluation of the production system.
* **Delbianco, Tohmé and Acciarri, Watermarking: from Impossibility to Auditable Compliance**, [arXiv:2610.06317v1, submitted October 5](https://arxiv.org/abs/2610.06317). [§4 and Proposition 2](https://arxiv.org/html/2610.06317v1#S4) calibrate within cells including key epoch, language/domain and length; explicitly distinguish averaging over calibration draws from the realized error of one frozen calibration object; and discuss finite calibration resolution. Section 5 varies calibration draws in a synthetic example. This is close prior work for the remedy/calibration-variability narrative, not evidence of a measured distribution of real-corpus FPR over random watermark keys. Its next-token collision quantity concerns watermark signal/robustness and must not be equated with the gate's corpus tuple-collision quantity. Incorporate it and narrow any blanket “no application” or entirely new calibration-frame claim; I have not reproduced or endorsed its simulation or regulatory conclusions.

Other checked leads were adjacent rather than full occupants. [Gloaguen et al., A Unified Framework for LLM Watermarks, arXiv:2602.06754v1](https://arxiv.org/html/2602.06754v1) explicitly models KGW's scores as correlated Bernoulli variables with a fixed number of ones (§4.1); its main optimization concerns watermark sampling and quality/diversity/power, not the requested FPR dispersion object. [The official September 24 vLLM watermarking post](https://github.com/vllm-project/vllm-project.github.io/blob/main/_posts/2026-09-24-watermarking-in-vllm.md) discusses keyed Gumbel sampling and repeated-context safeguards, primarily a generation/dependence issue. [MUSE, arXiv:2505.24267v1](https://arxiv.org/html/2505.24267v1), found through a secondary lead, concerns tabular watermarking; targeted searches in the primary HTML did not substantiate the lead's purported fixed-key calibration claim. I do not count that secondary characterization as evidence. Xie et al.'s classroom conformal work was already in the gate and remains a direct calibration antecedent.

Access limitations: an attempted MUSE v2 HTML URL and the pinned forum card were inaccessible through the web tool; no claim relies on those unavailable versions. No bot check or denied page was circumvented. No new local literature file or manifest entry was created. The conductor should record the two October 5 sources and compare the precise residual claim before the next lock.

## 6. Findings and recommended disposition

Severity here refers to accepting **this checkpoint as drafted**. Blocking findings prevent acceptance of the current mathematical/data-plan assurances; they do not imply that C07 is an unworkable topic. Major findings must be resolved in the revised design or expressly bounded before their associated claims are locked.

### F1 — Blocking: the proposed dispersion law does not describe the stated comparator in general

**Evidence:** gate §Residual gap identifies independently coloured tuple variance with KGW, drops the conditional score variance, applies token-law weights to a deduplicated comparator and asserts broad length/context consequences. The covariance calculation and explicit counterexamples in §2.2 show the differences.

**Recommendation:** replace the universal claim with a hierarchy: independent-colour baseline, fixed-size context-block correction, then the actual document/deduplication statistic with explicit assumptions and approximation limits. Treat monotonic trends as hypotheses. Name a nontrivial residual theorem or adequacy target beyond the elementary variance identity before affirming the theory-led PASS.

### F2 — Major: the occupancy/novelty record overstates the residual gap

**Evidence:** Jovanović p.27 has a hypergeometric special-case theory; Fernandez Table 6 does measure key sensitivity; Vovk pp.3–6 already provide conditional calibration/tolerance sample-size theory. The October 5 sources in §5 are missing from the gate.

**Recommendation:** incorporate those antecedents and distinguish across-key FPR theory from known mean-shift mechanisms and calibration theory. Replace absolute first/no-theory/no-application claims with precisely scoped, search-qualified statements. Retain the question if the narrowed contribution remains worthwhile; search absence alone is not a novelty proof.

### F3 — Major: the target guarantee and calibration sample-size claim are underspecified

**Evidence:** brief §Research question and gate §§Decision/Residual gap mix exact, approximate, discrete and sequential tests; `N≫1/C_h` concerns a different estimation task. Calibration and key screening introduce further frozen randomness. Finite ensembles do not automatically give conditional validity.

**Recommendation:** write the conditioning set and quantifiers for each remedy, identify independent calibration documents and deployment-law assumptions, and compare with existing conformal/tolerance guarantees. Report validity and power together, including screening/selection costs and fresh reference-key randomness where present.

### F4 — Blocking: C4 has not passed the declared open-content condition

**Evidence:** brief §Constraints requires openly licensed corpora; audit §3 calls all four recommended sources openly licensed and P1 is “met on paper.” The terms check's C4 inference does not bridge the database/content-rights distinction (§4.1).

**Recommendation:** leave C4/P1 unresolved. Recommend an explicitly licensed news source, or obtain Yichen's explicit policy revision supported by an adequate use basis before a C4 freeze. Do not treat research purpose, a dataset tag or nonredistribution alone as the missing content licence. Keep the HC3 rejection; a caveat is not a cure for its unresolved provenance.

### F5 — Major: census completeness and shard yields are overstated

**Evidence:** census `allenai/c4.size_partial=true`; audit §§2–3 converts the partial viewer count into a full-train/per-shard yield. Forum data files were not actually enumerated by the stored root tree record. Viewer counts are not revision-linked to original files.

**Recommendation:** label incomplete counts, retain split/config completeness evidence and exact source-file paths, reconcile pinned original counts, and withdraw unsupported yield estimates. Freeze-count discrepancies should fail visibly with a reason rather than be hidden by exclusions.

### F6 — Blocking: the proposed holdout permits known cross-source leakage

**Evidence:** audit §§5–6 hash source-specific document identifiers and remove only within-source exact duplicates, while §8 acknowledges Wikipedia/WikiText overlap. Development through one version can expose content held out in another.

**Recommendation:** group linked articles/near duplicates across sources before partition assignment, or remove overlap from confirmation. Bind the seal to the particular approved lock and manifest, and define permitted eligibility auditing. Approve the split design before raw-text scientific use; this review does not approve or open any holdout.

### F7 — Major: key adaptation and confirmatory precision are not covered by the proceed rule

**Evidence:** audit §5 denies key overfitting; P2–P4 apply to the open partition, leaving a much smaller final test. At 10,000 documents, FPR measurement noise is not below the smallest cited key spread. Shared texts couple key estimates.

**Recommendation:** use independent confirmatory keys where evaluating a random-key population, independent text for screened deployed keys, and a crossed key/document uncertainty analysis. Bind confirmatory precision or explicitly limit its claims; report sampled-key tails with uncertainty rather than a population worst case.

### F8 — Major: proceed-rule boundaries and fallbacks do not preserve all promised comparisons

**Evidence:** forum length differs; site diversity is nominal; two long-text sources may overlap; Llama eligibility does not ensure Qwen eligibility; a 20% hash split gives no exact minimum; Option 3 cannot meet three-register P2.

**Recommendation:** put all counts on defined post-cleaning open units, specify common-length comparisons and essential subdomain minima, clarify P4 independence, and predeclare shard expansion/failure handling. Any selected alternative must have an explicitly approved matching rule before data outcomes drive relaxation.

### F9 — Major: the human-text interpretation is stronger than the provenance supports

**Evidence:** audit §§1/8 calls post-2022 contamination only a slight shift and pre-2022 sources human-only, while the scientific mechanism depends precisely on text-law concentration.

**Recommendation:** distinguish human-authorship from key-independent-null targets, remove the unsupported magnitude claim, preserve vintage/source information and evaluate sensitivity within the bounded study. Report cleaning, reconstruction and lineage limitations alongside final population claims.

### F10 — Major: the complete study grid lacks a compute budget

**Evidence:** the model logs substantiate a small generation study, not billions of hash/permutation/resampling evaluations multiplied across the proposed null grid. The claimed CPU runtime has no matching measurement in the reviewed record.

**Recommendation:** retain the four-study narrative but nominate a primary family/grid, one main remedy and one model, with optional extensions clearly separated. Before the relevant protocol lock, time a representative short scoring/generation workload with the actual algorithm and bound runtime/storage for the full selected grid. Reserve writing and review time; do not run that workload as part of this review.

### F11 — Minor: synchronize qualifications and provenance records

**Evidence:** the historical Stage 2 claim, gate introduction, competitor table and “closed-form law” wording do not consistently reflect the later evidence. The 24-hour compute projection is an unexplained downrating. Tokenizer acceptance is inferred from cache presence; some licence versions and fallback details remain unresolved.

**Recommendation:** append corrections in the decision log and update current summaries without rewriting historical outcomes. Add the wording qualifications in §4.4, distinguish measurements from projections and reported prior-project facts, and retain exact notices/tokenizer settings at freeze. Keep all publication and scope decisions with Yichen.

VERDICT: REVISE
