# R11 claim gate — independent Codex review, round 1

Date: 2026-10-19 UTC. Reviewer: Codex. Conductor: Claude Code (recorded as Fable 5.1).

## 1. Baseline, scope and work performed

Baseline: `main`, HEAD **`161d43043faeafba9bbae54bd9d464a83cdb643f`**. The working tree was clean before the review. This review concerns the claim gate and its new side computation, not a reconsideration of R01–R10, a protocol amendment, or a change to any agreed report's numbers or verdicts.

I read root `AGENTS.md`, the full review orientation and R11 prompt; `research/CLAIM_GATE_v0.1.md`; gate v0.3's competitor table, occupied list, derivation/comparison and constraints; the three claim-gate screens and samples of their raw records; the Milestone 10 and J1 decision-log entries; all four reports' §2 and §5–§8, their cited tables/prose, and Study 4's attribution section; the R04, R06, R08 and R10 resolutions and R09's F18/F22/D18 resolution; the handoff and relevant brief; the side script, generated memo and JSON; and the local literature pages identified below. I checked the eleven manifest entries tagged `CLAIM` against the PDF bytes on disk. Their sizes and SHA-256 digests match.

I ran the expressly authorized `--stored-only` side computation with Python bytecode disabled. It completed in about 84 seconds. I preserved its pre-run side files and restored them byte-for-byte after comparing the result. Its numerical results reproduced; only generation-time metadata changed. Immediately after the run, the changed paths were its two stored-summary JSON files and generated memo. A before/after digest comparison of tracked files found no other changes. I also regenerated all seven Study 1 subset cells **in memory**, through the side module's `regen_part()`, without invoking a study-mode runner, analyzer or report builder. Every saved alpha block and every exact-reproduction flag matched the saved regeneration JSON. I did not rerun the full synthetic experiment: its saved six rows were inspected, and a separate short, count-only mathematical counterexample is reported below with a reproducer.

No model was loaded; no corpus, weights or PDF was downloaded; no lock, record, report, verdict or literature manifest was edited; no commit was made. Public metadata, repository text and documentation were read. The sole retained new file is this memo. All four locks still say `final: false`; I did not open held-out text.

**Assessment:** much of the claim list is a faithful and useful condensation. The gate cannot stand **as worded**. In particular, E1 promotes conditional uncertainty into a population reading despite R09 D18; Unigram contains a stronger, directly relevant variance antecedent than the new table credits; several rows lose conditions or registration labels; and the software screen missed a concrete two-key calibration/transfer artifact. These are repairs to the gate, not reasons to rerun the agreed studies.

## 2. Claims against evidence

### 2.1 Row-by-row audit

“Faithful” below means the numerical statements trace to the named agreed report table or interpretation section, and the proposed status is supported at that scope. It does not independently establish a model assumption or turn a descriptive summary into a guarantee. References S1–S4 here mean the four **study reports**, not similarly named decision rules.

| Row | Evidence checked and disposition |
|---|---|
| A1 | Brief's research question and gate v0.3 framing: faithful attribution, but retain “exactly, conservatively or asymptotically, by method” and **key-independent** null law when lifted into the draft. “Each method guarantees” without its assumptions is too loose. No new given-key theorem was established. |
| A2 | S1 Table 1: 1,098 R3 checks, nine structural zeros, 94.3% diagnostic coverage on 1,089; S2 Table 1: 3,468 checks, 94.8%. Algebra is correct for independent context colourings and the scored weights. “Established elementary identity” is appropriate. Attribution/residual-novelty wording is incomplete: F2. |
| A3 | S1 Tables 1 and 6/§5, S2 Table 12: the 28.305% refutation, 0.92/0.87% synthetic bounds, 0.346/2.101/0.139% real-text reductions and 7/68 count match. Coverage qualification and separation of the three collisions are good. R4b stays “reproduced,” with its tolerance discrepancy. The covered-support finite-population formula needs the Unigram antecedent: F2. |
| A4 | S1 R1/Table 1 and §5–§6; S2 Tables 1 and 5 and §5: counts, ratio ranges and block medians match. Registered pass plus measured bias, with an unisolated mechanism, is the right status. The Gumbel and other secondary weaknesses should be carried alongside this row's broad predictor language: F9. |
| A5 | S1 R4/R4b and §6 Q3; S2 Tables 1, 6–8 and §5: numerical growth factors, 40/40 descriptive checks, 24/100 failures and 76/61 counts match. The row correctly identifies **overlapping** groups and the 16 non-news h=4 chains. Its status shorthand and, more seriously, constraint 23/J3 lose those distinctions: F3. |
| A6 | S1 Table 1/§6 Q4 and S2 Tables 1/9: numerical factors, 48/48 and 40/40 counts and eligibility summaries match. R5 is a rule about between-text collision under the raw rule, whereas S5 concerns observed SD. The parenthesis incorrectly lets R5 certify an SD claim: F3. |
| A7 | S1 Table 14/§5, S2 Table 16/§5, S4 Table 14/§8: the quoted synthetic/human summaries and model-null mean, median and middle-mass counts match. “Measured,” with the untested law-versus-measurement distinction, matches the agreed reading and J1. This review does not turn the available tail summaries into a new shape test. |
| B1 | S2 Tables 16–17 and §5–§6: all stated level/quantile/share ranges and 609/1,020 count trace. Correctly sampled-key, finite-text and measured. Preserve that this is the **deployer subset**, using each cell's longest length; it is not a common-L range. |
| B2 | S2 Table 1 and §7: 3,060 audit checks, S3 integrity and audit power limits match. Appropriate established integrity claim, not evidence of exact PRF independence. S1's separate R2 audit is missing from the claimed complete inventory: F9. |
| B3 | S2 Tables 18–19/§5: correlations 0.562/0.827, 0.027/0.125, 0.176/0.460 and 0.233 match. Correctly descriptive, paired and not transfer. Shared-id explanation stays a hypothesis. |
| B4 | S2 Table 20/§5: quoted disparity shares, ratios, difference SD and Bernoulli benchmark match their rule/width blocks. Appropriate empirical, finite-text language. Keep the table's handling of zero component levels when reproducing the full disparity display. |
| B5 | S2 Table 21/§5 and overlap side output: dispersion ratios, correlation ranges and 0.3% semantic-id fraction match. Keep level correlation distinct from q-hat correlation. Post-hoc status and superseded first version are correctly retained. |
| B6 | S2 Table 12/§5: duplicates A3 faithfully, including 42.2% support coverage and 2,695 effective conditional support. Measured, not a universal vocabulary-size guarantee. |
| C1 | S3 Tables 1, 6, 8, 10/§5–§6: mean ranges, 0.44/0.33/0.17 pp, 45.6/47.0/48.1%, 4.7/7.3/7.7%, tail range and T1 counts/ratios match. The reference-law/finite-evaluation distinction is good. Its first “lattice ties” parenthesis should itself be suggestive. Several summaries require their h=1, distinct, alpha=.01, conformal/tolerance@5000 context: F5. |
| C2 | S3 Tables 8, 10, 11/§5–§7: multiplier, empirical-fit, range and flag counts match. Prerequisite and numerical-arm distinctions are correct. Retain the h=1, alpha=.01, 20-unit context and label kappa summaries as medians/ranges across units. |
| C3 | S3 Table 8/§6 Q3: 0.994% mean, 0.397 pp SD and 41.4% exceedance belong to **distinct h=1**; raw h=1 has 0.891% mean and 0.466 pp SD. The rounded numbers in the row are present, but the combined sentence needs those ownership labels: F5. |
| C4 | S3 Tables 1, 7, 9, 15 and §5 transfer paragraph: 3.5/2.7/3.0 ratios, 0.59/0.17 pp, 3.02/1.43%, 8.3/0.0%, shift correlations, T1 class medians, T2 875/875 and cross-tokenizer 1,573/1,574 trace. The 1.01–1.25% pair range is in §5. Most headline transfer numbers are **distinct h=1, alpha=.01, conformal@5000**, with SDs/quantiles/shares summarized over ordered pairs. The row and J8 omit this: F5. Partial prior transfer practice also requires attribution: F7. |
| C5 | S3 Table 12/§5–§6: break-even counts and 0.20/0.141 pp benchmarks match. Correctly a labelled builder computation with a paired interval criterion, not a registered decision. |
| C6 | S3 Table 11/§5: z shifts/quantiles, zero-order abstention regimes and six positive-order zero thresholds match. Appropriate measured status and numerical-cause restraint. |
| C7 | S3 Table 8/§6 Q4: paired numerical contrasts and 747/747 versus 724/747 match. “Makes the multiplier conservative instead of failing” conflicts with its own constraints and S3 §7, even though inherited from §6 Q4. “Unbiased” also needs measured/model qualification: F5. |
| C8 | S3 Tables 1 and 13/§5: REP 108/0, 21.6% maximum difference, 1.9% summary variability and 0.141 pp Beta term match. Correct distinction between across-key summaries and one key's calibration-draw variability. |
| D1 | S4 Tables 8/12 and §8: all method costs, quantiles, nominal powers, strength/width/rule contrasts and saturation summaries trace. Correctly measured at the stated primary setting, 100 keys and 50 shared prompts, with prior pricing attributed. “Threshold above alpha” refers to the **p-value cutoff**, not a z cutoff. |
| D2 | S4 Tables 2–3/§8: W1 counts, bands, news interval/tolerance-edge difference and per-key agreement/correlations match. Registered conditional adequacy, not proof of a common individual-key score law. |
| D3 | S4 Tables 2, 4–5/§8: six unresolved rows, all point estimates below one, intervals and noise magnitudes match. D18 target, population limitation and Yichen's design-limit decision are faithfully preserved. An interval below one is not automatically a resolution under W2's registered margin. |
| D4 | S4 Tables 2, 6–7/§8: 216/216, 221/240, five unresolved, nineteen ineligible, 0.973 and 142/216 match. Correctly conditional adequacy, one shared generated sample per cell. |
| D5 | S4 Tables 9, 13–14/§8: the 100-key operating-point shares and correlations match; the last model means are over 1,000 keys, while the cited corpus means 2.37/3.47/3.78 are over the **100 power keys**. State the latter explicitly: F5. |
| D6 | S4 Table 10/§8: correlations and R-squared values match. Correctly a mechanism hypothesis, not a causal effect or variance decomposition. |
| D7 | S4 Table 13/§8: transfer-source powers and 1,000-key null shares match. Keep the primary h=1, delta=.5, L=256, alpha=.01 setting explicit beside this row; power and null denominators differ. |
| D8 | S4 Table 14/§8: the first portion is h=0; the calibrated 0.74/0.77/0.99 and 19/18/43%, 53/48/49% portions are **h=1**. The missing transition changes the scientific comparison: F4. |
| D9 | S4 Tables 15–16/§8: loop percentages and per-prompt mean/SD effects trace. Correctly descriptive; no text was excluded and this is not a general quality evaluation. |
| E1 | Report diagnostic counts and saved side-table numbers mostly reproduce exactly. The inference that these justify a conservative crossed SE and a population reading with key-only uncertainty does not follow (F1). The regenerated text/key SE range is misstated (F6). |

F1 positioning can remain “at least third in line” as a limited historical characterization. Its **contribution sentence**, and §§3–4/7's residual/absence assertions, must be revised for F2 and F7; this is not a request to decide an exhaustive priority rank.

### 2.2 Literature quotations and occupied parts

I searched the local form-feed-separated texts for the quoted anchors and checked their surrounding pages. Whitespace/ligature normalization is distinguished from literal extraction; equations split over lines were read in context. This supports the following audit, with the qualifications in F2, F7 and F10.

| Source | Page-confirmed evidence and reading |
|---|---|
| Jovanović et al., `2506.16349` | PDF p.27, “hypergeometric distribution,” Eq.9 and the subdomain/open-question discussion: correctly attributed finite-vocabulary case and motivating question. |
| Gloaguen et al., `2509.24368` | p.21, Table 2/Fig.7: 100 keys, 10,000 null texts and SDs 1.2%, 0.3%, 0.1%. The width measurement is prior, not new here. |
| Fernandez et al., `2512.16904`; TextSeal, `2605.12456` | Former pp.6/19, “fixing a specific key” and mean-shift/key screening; latter pp.5/21/38, “Secret keys are calibrated per method” and absence of a Bayesian FPR guarantee. Correctly distinguished from this project's dispersion prediction. |
| Three Bricks, `2308.00113`; Kirchenbauer, `2301.10226`, `2306.04634`; Cai et al., `2510.22007` | Three Bricks pp.3–4 pools ten keys and repairs repeated tuples; original KGW p.4 states a random-list idealization; reliability p.19 examines repeated-n-gram correction; Cai pp.1–3 treats collision-induced Type I inflation. The within-text mechanism is occupied. |
| Genhatharan, `genhatharan_nominal_fpr_2026` | pp.1/7–9 and Fig.10 p.11 confirm key/vocabulary dependence, many-key measurement and **per-key calibration priced in power**. The gate's §IV-H/Fig.10 attribution is substantive and necessary; use PDF pp.9/11 in the paper. |
| AutoMark, `2609.37310` | pp.4–5 (Eq.2/Eq.3 and separate null sample per key), p.29 (empirical/guaranteed multipliers and power comparison), p.42 Prop.1: prerequisite is soundness over the key. Occupied parts correctly credited except C7's shortcut. |
| Gloaguen et al., `2602.06754` | p.4, “correlated Bernoulli random variables”: correct antecedent, but less direct for A2 than Unigram's existing calculation. |
| Vovk, `1209.2673`; Bian–Barber, `2205.03647`; Liang–Barber, `2311.04295`; Ren–Barber, `2205.15461` | Vovk p.2 cube, pp.3/5–6 training-conditional/tolerance results; Bian–Barber p.2 “might result in 0% training-conditional coverage”; Liang–Barber pp.1–2 stability route; Ren–Barber p.11 “two sources of variability.” Correct transfer framing; the last distinction is directly relevant to F1. |
| Aremu et al., `2603.23171`; Xie et al., `2507.23113`; Delbianco et al., `2610.06317` | Aremu pp.4–5 calibrates once per key; Xie p.6 distribution-free conformal score calibration; Delbianco p.10 includes key epoch in cells, p.11 Prop.2 averages over calibration draws and discusses a frozen set's variability. Calibration practice and its conditioning are occupied. |
| Li et al., `2404.01245`, `2411.13868`; Huang et al., `2312.07930`; Kuditipudi et al., `2307.15593` | Respectively p.8 random key variable, p.11 perfect-pseudorandomness assumption, p.5 Type I definition, and p.6 fresh-key symmetry: the gate correctly preserves their guarantees on their own terms. |
| Fu–Russell, `2506.15975`; anytime-valid sources `2602.14286`, `2602.17608`, `2607.21958` | Fu–Russell p.6 concerns many-key multiplicity. The sequential sources' null conditions and e-process construction (pp.9, 8, and 5 respectively) do not establish the fixed-key text-law dispersion claimed here. |
| SAC-Copula, `2608.20839`; Global sketch, `2606.04486` | pp.7/23 and p.5 respectively: source-dependent threshold portability and base-model/length calibration already exist. These remain pertinent neighbors of transfer, not evidence that transfer itself is new. |
| Nemecek et al., `2608.20047` | p.4, “A per-language threshold” and “pooled null”; key mentions on pp.1–3 are background. Per-language/pooled calibration and language-dependent nominal failure are occupied; no varied-key grid is reported. |
| ChainMark, `2607.18445` | p.1 “a one-corpus recalibration”; p.16 “Rotating keys per deployment epoch”: pooled recalibration and a key-rotation statement, not measured across-key invariance. |
| Ding et al., `2609.32678` | p.29 100 reference banks with 499 null paths; pp.35–36 key reconstruction and a 4,999-path ideal-null bank; p.40 null pivot diagnostics. The gate correctly withdraws the previous claim about needing a new reference bank for other keys. No per-key calibration study is supplied by these passages. |
| LUNA, `2606.00613` | pp.7–8 two negative classes; pp.15–17 App.D, Tables 12–14. I also read the omitted appendix tables/protocol: human-negative operating points are recalibrated on that negative class; these are aggregate comparisons, not the present many-key transfer. The new two-key software source below is closer to D5/D8. |
| TI-WM, `2610.14378` | pp.1–2, “128 prompts per key” and explicit source-shift/power limitation. Three-key AUC reporting and tokenizer-free scoring, not a per-key FPR dispersion law. |
| ByteMark, `2610.14427` | pp.7–9, “same-pool empirical 1% threshold,” and tokenizer-search multiplicity. Same-pool calibration and multiple candidate tokenizers must stay distinct from a held fixed key's FPR. |
| textGrain theory, `2610.17655` | p.1 detectability with a secret key; p.16 algorithm inputs and binomial scan. The mathematics does not supply the claimed dispersion law. The quoted input phrase adds a word absent from the extraction: F10. |
| Li Ma, `2609.15657` | p.1 “This guarantee does not cover violations of the conditional null”; p.26 edits exclusions. Correctly an assumed conditional pivot null, not a demonstration that it holds for arbitrary fixed keys. |
| Unigram, `2306.17439` | pp.3/5/8 quoted scheme/Type I passages are real, **but pp.31/34/36 are decisive omitted variance antecedents**. See F2. |
| Power-Calibrated Watermarking, `2607.05694`; Input Repetition Masking, `2504.12229` | Former p.4 strength/power setting and p.38 risk paragraph; latter p.1 mimicry and input masking. Neither quoted passage establishes the project's across-key law; both are properly neighboring mechanisms. |
| Islam et al. review | The saved OpenAlex abstract supports the short phrase about false-positive control and the stated review size. It is abstract-only evidence; it cannot certify absence of a result in the inaccessible body. |
| EU Code 129555; Guidelines 131215; NIST AI 100-4; OpenAI textGrain | Code PDF p.17, NIST p.12 and textGrain p.6 quoted phrases match. The Guidelines phrase occurs at PDF pp.2/5/26; the table currently omits a page. These support motivation and stated limitations, not a compliance conclusion. |
| vLLM, Google SynthID-Text, Hugging Face | Saved extracts agree with the current public pages read independently: vLLM warns of key-dependent realized FPR; Google requires Bayesian training for each key; HF advises a private key. Dates/source identity should accompany web quotations. They do not support the screen's universal software-absence statement. |

Other named search neighbors (including TANGO/DenMark, the embargoed keyless-audit manuscript, governance papers and inaccessible standards/publisher records) remain at the access level recorded in the screens. I did not infer their full-text contents from titles or abstracts, nor treat their absence from a retrieved result set as a negative full-text finding.

## 3. Method and statistics

### 3.1 Independent algebra check

Let the binary rejection table have N text rows and K key columns, column means a_k, sample variance s_K² and two-way residual mean square MS_E. Define C_ij as the sample covariance over the K keys between text rows i and j, using denominator K−1. Direct expansion gives

\[
\hat v=s_K^2-\frac{MS_E}{N}
 =\frac{1}{N(N-1)}\sum_{i\ne j} C_{ij},
\qquad s_K^2=\frac{1}{N^2}\sum_{i,j}C_{ij}.
\]

This identity checks the code's binary residual-sum-of-squares shortcut as well as its weighted resampling formula. Write a=(K−1)/K. Conditional on the observed table:

- **Key-only resampling, MS_E recomputed:** E_* C_ij*=a C_ij, hence E_* v*=a v-hat.
- **Text-only resampling, keys fixed:** distinct bootstrap row slots can select the same original row. The expected off-diagonal bootstrap average is N^-2 sum C_ij=s_K².
- **Crossed resampling:** E_* v*=a s_K². Thus the displacement from v-hat is exactly d=MS_E/N−s_K²/K. It need not be positive in every cell.
- **a_k-only approximation:** resampling the stored column means estimates the spread of s_K²* with MS_E/N held fixed. If that fixed correction is subtracted, its mean is a s_K²−MS_E/N, differing from the exact key-only mean a v-hat by −MS_E/(KN). A close SE match on seven tables is an empirical approximation check, not an identity for the SE on all tables.

Under independent sampled keys and iid sampled texts, the raw two-way component is unbiased for Var_K(E_X Y_XK). Conditional on the sampled texts, however, its key expectation is the corresponding **off-diagonal text-row covariance functional**. That is the distinction R09 F22 and D18 preserve. Neither the exact crossed centering identity nor a small observed text-only SE makes it disappear.

The reports use normal intervals centered at v-hat, so the crossed resample's mean displacement was not mechanically inserted into their “within 2 SE” counts. This is correctly stated in E1. Conversely, removing/recentering that displacement alone does not establish coverage. The problem remaining is the spread and its target.

### 3.2 Reproduction and limits

The stored calculation reproduced 3,582 S1 and 10,404 S2 (cell,alpha) rows. The summary subsets with positive SE and nonzero component have 3,180 and 9,724 rows. Counts reproduce as follows:

| Diagnostic | Reported crossed SE | Stored-level key-only SE | Normal-theory SE |
|---|---:|---:|---:|
| S1, 360 cells | 309 | 292 | 256 |
| S2, 217 eligible primary cells | 22 | 20 | 14 |

All seven regenerated rejection tables reproduced their stored population blocks exactly at every alpha. The regenerated side JSON's alpha dictionaries also matched the saved ones. This verifies reconstruction through the locked functions; it does not validate all population uncertainty. The seven cells are a selected S1 subset, not a representative S2 coverage study.

The full synthetic experiment's six saved rows cover two beta-key models and one logistic key-by-text model at the two study sizes. They support the **model-specific** reported ranges, with finite Monte Carlo error (300/400 replicates), not uniform conservativeness. In particular, some nominal-95% coverages are 0.93 or 0.94. The logged repetition of an initial 100-replicate large-size run after inspecting its SE discrepancy should remain disclosed as exploratory; the larger run does not convert the design into a prespecified validation.

The script reads a glob of live cell JSONs rather than independently authenticating each against Git. For this review I verified that the cell files it read were tracked and unchanged; thus they were the committed cells at this baseline. Its only write sites are the four named side JSONs and its generated memo. The in-memory regeneration imports definitions from the locked code, not the runner's study-mode main. No locked output changed.

### 3.3 A short counterexample to the population interpretation

This is a reviewer diagnostic, **not an additional study result**. Let independent keys B_k~Bernoulli(0.25), iid texts T_i~Bernoulli(0.04), and Y_ik=T_i B_k. It is a legitimate crossed binary table with key-independent text law and marginal rejection probability .01. Its population key variance is .25·.75·.04²=.0003. With q-hat the sampled text fraction,

\[
\hat v=s_B^2 c,\quad
c=\hat q^2-\frac{\hat q(1-\hat q)}{N-1},\quad
E_K(\hat v\mid T)=.25\cdot.75\,c.
\]

The exact conditional key-bootstrap SE can be computed from binomial moments; no large rejection arrays or inner bootstrap are needed. In 200,000 independent tables per size, seed 20261019, the normal intervals v-hat ±1.96 SE_key had:

| K,N | Mean key SE / unconditional sampling SD | Population-target coverage | Text-conditioned-target coverage |
|---|---:|---:|---:|
| 500,4000 | 0.3149 | 0.4596 | 0.9428 |
| 1000,10000 | 0.3479 | 0.5048 | 0.9466 |

The raw estimator's bias was negligible at this Monte Carlo precision. This example does **not** establish bad coverage on the actual watermark tables; it demonstrates why the six side models and Study 4 precedent do not establish a generally valid population reading.

Reproducer (NumPy only; no files written):

```python
import numpy as np
rng = np.random.default_rng(20261019)
p, q, R = .25, .04, 200000
for K, N in [(500, 4000), (1000, 10000)]:
    kh = rng.binomial(K, p, R) / K
    th = rng.binomial(N, q, R) / N
    c = (N * th * th - th) / (N - 1)
    v = c * K / (K - 1) * kh * (1 - kh)
    s2 = kh * (1 - kh)
    mu4 = s2 * (1 - 3 * s2)
    se = abs(c) * np.sqrt((mu4 - (K - 3)/(K - 1) * s2**2) / K)
    population = p * (1 - p) * q*q
    conditional = p * (1 - p) * c
    print(K, N, se.mean()/v.std(ddof=1),
          np.mean(abs(v-population) <= 1.96*se),
          np.mean(abs(v-conditional) <= 1.96*se))
```

**Recommendation for the paper:** retain the agreed point estimates and crossed counts as historical descriptive diagnostics. If the key-only recounts are shown, identify them as a conditional sensitivity calculation using an a_k-only SE approximation; they are not replacement validated population intervals. A population claim would need a construction retaining the text channel, for example an appropriately derived two-sample U-statistic/influence-function analysis, with coverage checked for the intended target. That is a proposal for separately authorized work, not a requirement to modify a lock or silently rerun the reports. Narrowing the gate is sufficient here.

## 4. Process, constraints, judgements and outline readiness

### 4.1 Constraints 17–33

| Constraint(s) | Assessment |
|---|---|
| 17 | Correct R10 carry-forward. Apply the same visible conditioning discipline to D7/D8 and the transfer summary; D5 must label both key sets. |
| 18–19 | Consistent with D18/R10 and prior pricing. The all-unresolved W2 finding and limits must remain prominent. |
| 20–21 | Correct, but C7 contradicts 20. Finite-evaluation exceedance, reference-law population share and tolerance over calibration draws must not be merged. |
| 22 | Correct, extending the R06 carry-forward. Preserve each eligible/resolved denominator and the secondary-family limitations. |
| 23 | Incorrect as written: registered raw-rule synthetic R4 versus descriptive other rules; finite-text account applies to 16 non-news h=4 failures, not all 18. F3. |
| 24 | Consistent with prior constraints 9–10 and the Nemecek attribution. |
| 25 | Not sufficient: two labels do not fix the target mismatch. Rewrite in light of D18 and F1. |
| 26–29 | Appropriate model/design, PRF, post-hoc and discrepancy qualifications. The first clause of C1 must obey its own suggestive-mechanism qualification. |
| 30 | Useful but compressed: S1 also has 2,000-key illustration laws and a 200-key fixed core subset; fixed-colouring pairing is within chains, not the entire grid. State these exceptions when relevant. S4 null summaries use 1,000 keys although power uses 100. |
| 31 | Appropriate disclosure obligation. This memo supplies a Codex review round; it is not independent human peer review. The paper should describe the actual drafting/review roles and rounds, with model identities from the run record rather than inferred names. |
| 32 | Appropriate existing neighbors, but add the two-key fixed-threshold transfer/negative-source artifact in F7. This is more direct prior practice than an aggregate AUC comparison alone. |
| 33 | Correct separation of source vocabulary from compliance. Add the missing Guidelines page; cite vLLM by access date/source revision consistently. Do not infer what an actual deployment does beyond the source. |

The overlap with constraints 1–16 is mostly deliberate reinforcement, not harmful redundancy. Missing from the condensed gate are an explicit preservation of **all** prior distinctions (especially sampled-text targets and the difference between mean-shift variance and FPR variance), the exceptions in constraint 30, and an explicit statement that unrun candidate remedies/extensions are not results. See F9.

### 4.2 J1–J11: recommendations remain Yichen's decisions

| Judgement | Review recommendation and trade-off |
|---|---|
| J1 | The recorded “yes” matches the 2026-10-19 decision log. Preserve the descriptive paragraph and model-null comparison, with the untested shape explanation; do not reopen the decision. The handoff's “waiting on J1” is stale. |
| J2 | Recommend the block-specific version. A shorter version is acceptable only if its adjacent table/caption retains eligibility, unresolved counts and measured bias; the footnote alternative should not imply validation of all cells or regimes. |
| J3 | Recommend the registered verdict plus the corrected overlapping groups and a labelled plausible lattice account. The current recommended sentence is factually wrong (F3); appendix placement is a presentation choice, not a way to drop the qualification. |
| J4 | The labelled overlap paragraph and hypothesis sentence are supported. Appendix-only is a fair alternative for space. Keep the superseded computation disclosed. |
| J5 | No new tie computation is necessary for the current bounded claim. Keep the explanation suggestive everywhere. Computing tie shares would measure association with ties; by itself it would not isolate the entire cause of conservative levels. The alternative currently promises too much by saying the account would then be “measured.” |
| J6 | Recommend the qualified three-sentence multiplier description. It respects Proposition 1 and distinguishes the empirical plug-in. Reporting only the distinct rule is a fair space trade-off if the omitted numerical arm is still documented. |
| J7 | Recommend both estimands, at the stated h/rule/alpha/N_cal setting. Quoting only 7.3% without explaining finite-evaluation noise is not an equally defensible scientific alternative; shortening should preserve that distinction. |
| J8 | Recommend the transfer/predictor sentence **after** adding the setting and pair-summary labels (F5) and prior practice (F7). A shorter sentence may move prediction detail to the next sentence/table; it must not become a general transfer guarantee. |
| J9 | Correctly recorded as decided: W2 is a design limit, not a reason to launch v0.2 now. |
| J10 | Keep the bounded historical phrase but revise the contribution sentence for Unigram and the software artifact. This is an attribution correction, not Yichen's discretionary acceptance of a stronger novelty claim. |
| J11 | Present corrected options: both historical/conditional-sensitivity counts with no validated population confidence, or omit the unvalidated uncertainty comparison while retaining the point diagnostic; a new population construction would be separate work. The two current options both omit D18's essential target restriction. |

J1 and J9 are the only decisions recorded as already taken; I found no evidence that J2–J8/J10–J11 had been approved. Their recommendations should not be written as decisions.

### 4.3 Process and completeness

The numerical source discipline is largely good: the reports and generated side JSON provide traceable sources. It does not prevent a number from acquiring the wrong condition in a new sentence (D8), an incorrect ratio summary (E1), or a stronger registration label (J3). Those require gate-level correction. The handoff and log repeat E1's reading and therefore require a dated reconciliation when it changes; the historical entries should not be silently rewritten. The brief remains a topic/study-plan record, not evidence that every originally proposed remedy was run.

The PDFs/extracted texts remain ignored, and the eleven CLAIM fetch times are spaced at least four seconds. The fetcher uses a single sequential request stream. The **screens**, however, were not run one after another: the raw logs show overlapping A/B arXiv activity, including records in the same second. Consequently the aggregate-pacing assertion cannot be certified from each subagent's local sleep. F8 identifies the evidence without claiming more request-timing precision than the logs provide. Access gaps (403/challenges/429/inaccessible manuscripts) remain gaps; no bypass was necessary in this review. The source-specific raw C records are sometimes extracted summaries, not complete raw pages, so their quotation status should be described accurately.

Section 1G is a useful summary but is **not literally the union** it calls itself. It omits, among other things: the difference between key-independent null provenance and human authorship; random/screened/ensemble keys; score-shift versus FPR dispersion; calibrated sample targets and finite-evaluation noise; absence of an identified causal skew/tie/variance decomposition; and unrun stratified-split/ensemble/activation/fingerprint extensions. S1's R2 integrity pass and important descriptive weak regimes are also missing from the positive/negative inventory. F9 recommends a compact source/status crosswalk rather than an enormous main-text disclaimer.

After these corrections, there is enough **existing agreed evidence** to plan Stage 8; no new outcome is needed merely to make an outline. The proposed figure families have agreed sources: S1 identity/length/dispersion figures; S2 adequacy, deployer and cross-cell figures; S3 calibration-size, transfer and break-even figures; S4 threshold-cost, operating-point and paired-remedy figures. The outline still needs a row mapping each chosen table/figure to its report, generated source, estimand, conditions and limitations. The new SE material is post-hoc and not yet a validated population uncertainty result. I recommend keeping that qualification in an appendix or methods note, not elevating the recount to a new headline.

## 5. Independent search and screening audit

Web access was available. On 2026-10-19 UTC I independently reran **three verbatim arXiv API queries**, sequentially, with four-second sleeps after completion and no PDFs fetched:

| Screen query | Returned now | Comparison with saved screen |
|---|---|---|
| A q08: `abs:watermark AND abs:"per-key"` | 1: 2610.14378v1, updated 2026-10-09 | Same count and paper. Three-key AUC neighbor, not an FPR grid. |
| A q27: `abs:watermark AND abs:"fixed key" AND abs:"false positive"` | 1: 2610.14378v1 | Same count and paper. |
| B 01: `abs:watermark AND abs:calibration AND abs:key AND abs:threshold` | 3: 2610.04151v1, 2609.35881v2, 2607.18445v1 | Same count. Soft-binding benchmark, genome watermark, and ChainMark respectively; only the last is directly relevant to the present calibration discussion. |

The saved A q08/q27 and B01 raw files reproduce their stated entry counts. A's directory has 143 files, B's 120, C's 16. Sampled OpenAlex raw records distinguish total matches from retrieved results: A search 01 has `meta.count=151` but 50 records; B search 01 has 129 but 50. Thus the caps/access limits matter. The known-id update check is a bounded check of that list, not a statement that no relevant work anywhere changed after October 13.

I additionally searched the web for `watermark` with `per-key`, `fixed key`, or `key-dependent` and `false positive`, including date-restricted searches after **2026-10-16**, GitHub-domain searches, and deployed-documentation searches. I read primary GitHub/public-documentation results rather than adopting snippets. Current vLLM, Google and HF documentation confirmed the phrases described above. The current Genhatharan repository still has latest commit `41cffb3bcd7f647b744670bd1c8afa84c9f2dc9a` (2026-09-11); AutoMark's release repository reports `349abd3badfe72e4b2e3e735768b187a5b332d01` (2026-10-01). The search did not establish a new post-October-16 occupant; this is a limited negative search result, not proof of novelty. The substantive omissions found are **older**.

**New primary software evidence:** [xlr8harder/synthid](https://github.com/xlr8harder/synthid), latest commit `b3adb0f13301506e6ee0f49be26e99f6abde5829` dated 2026-08-19. Its pinned [score-family amendment](https://github.com/xlr8harder/synthid/blob/b3adb0f13301506e6ee0f49be26e99f6abde5829/docs/DETECTOR_SCORE_FAMILY_AMENDMENT.md) supplies the evidence discussed in F7. I read Markdown through the GitHub API; no models, datasets or score arrays were downloaded.

A further arXiv query, `abs:watermark AND abs:"language model"`, sorted by `lastUpdatedDate` descending with `max_results=50`, returned one entry updated since October 16: **Deng, Seif and Xie, [Watermarkability](https://arxiv.org/abs/2610.22810), 2610.22810v1, 2026-10-16 01:40:39 UTC**. I read the primary abstract and the HTML theory/experiment/discussion sections. Its object is the KL cost of assigning mass to a requested token set; it evaluates an adapter/controller through token adherence and perplexity. It is a new neighbor for the strength/quality discussion, not an occupant of the per-key FPR variance, calibration-transfer or calibrated-power-cost claims. The HTML has no matches for “false-positive,” “false positive,” or “variance”; that lexical check supplements, rather than replaces, the section reading. No PDF was fetched. The current vLLM watermarking-file history ends on October 15, consistent with the screen's bounded documentation check.

Other search results included a fixed-key SynthID calibration warning in [PaulBellette/qwen_paul_resampler](https://github.com/PaulBellette/qwen_paul_resampler), the existing [vLLM RFC](https://github.com/vllm-project/vllm/issues/53916), and algorithmic documentation distinguishing key-averaged generation from fixed-key behavior. These are useful practice leads, not new proofs of the project's four target contributions. The primary arXiv abstract for [2610.08668](https://arxiv.org/abs/2610.08668) is dated October 6; a third-party request for per-key FPR bootstraps is not a paper result and was not counted as one.

For the four occupant questions: (a) **partial theory occupant found**, Unigram's green-mass variance and deduplicated finite-population correction; not an established general FPR dispersion/predictor law; (b) no retrieved complete counterpart to the project grid; (c) prior two-key calibration transfer is now located, but no retrieved counterpart to the many-key dispersion plus key-free prediction; (d) Genhatharan/AutoMark already occupy pricing in kind, as the gate correctly recognizes; no retrieved replacement for the project's specified paired study and threshold-shift check. The residual should be claimed at this granularity.

## 6. Findings and required revisions

### F1 — blocking — E1/J11 do not justify population uncertainty with a key-only SE

**Evidence.** E1, constraint 25 and the Milestone 10 reading recommend reading the population diagnostic with key-only recounts, call the crossed construction conservative and cite Study 4's D17 choice. R09 F22/D18 subsequently restricted that choice to a prompt-conditioned target after population coverage failed (149/300 versus conditional 282/300). The exact algebra in §3 and the short binary counterexample show the same missing text channel. Six particular synthetic models/sizes and seven S1 cells do not establish its negligibility for S1/S2 population targets.

**Recommendation.** Keep both counts only as explicitly historical and conditional-sensitivity diagnostics; remove general coverage/conservativeness language. State the target and a_k-only approximation. Cite D18 as well as D17. If actual population confidence is wanted, propose and validate a construction with both sampling channels separately; do not relabel or regenerate a locked result. Correct the gate and append the corresponding dated log/handoff explanation. This finding concerns the interpretation, not whether the recounts were computed correctly.

### F2 — major — Unigram already contains two decisive variance antecedents of A2/A3

**Evidence.** `2306.17439.txt`, PDF p.31, Lemma C.21 proof invokes a “variance calculation for sampling without replacement” and writes the variance of p_t(G). Simplifying its equality gives

\[
\operatorname{Var}_G[p_t(G)]
=\frac{\gamma(1-\gamma)}{V-1}
 (V\|p_t\|_2^2-1),
\]

exactly A2's single-context, normalized-weight case (take B=1 and A=||p_t||²; realized fraction g replaces gamma when needed). PDF p.36, Lemma F.2 supplies the general finite-population formula. PDF p.34, Remark E.2 gives the deduplicated count variance m gamma(1−gamma)(1−(m−1)/(V−1)). Dividing by m² gives A3's covered-support formula with m=s. The present table credits only Unigram's marginal Type I theorem, and the screen/gate conclude that no retrieved work gives per-key green-mass dispersion.

**Recommendation.** Add these exact page/lemma antecedents to the competitor/occupied discussion and A2/A3. Narrow the contribution to the application to context-indexed text-law/retention weights, the associated collision/transfer formulation and empirical validation/FPR approximation as supported. Do not claim a new generic sampling-without-replacement identity or new covered-support correction. Revise F1/J10 and the “no occupant” verdict sentence accordingly. The new evidence does not erase the grid, the FPR prediction or the measured transfer/power work.

### F3 — major — H-length/width wording changes what the registered rules tested

**Evidence.** S1 Table 1 defines R4 on **raw-rule rho-bar**, R5 on **raw-rule between-text collision**. Distinct/first 40/40 length results are descriptive. Constraint 23 says registered PASS under every rule; J3 repeats it. A6 places R5's 48/48 beside the observed level-SD claim. J3 also says the finite-text term dominates in all 18 h=4 failures; S2 §5 explicitly restricts that explanation to **16 non-news chains**, with the two news chains having theory shares 0.780/0.657 and 0.877/0.806 at the failing step. Its 18+6+2 group totals overlap in two chains.

**Recommendation.** Preserve the exact registered estimand/rule for each PASS; label the other observations descriptive. Use A5's more careful 16-chain/overlap wording in constraint 23 and J3. Keep the predictor-based finite-text/lattice account a plausible explanation, not an identified variance decomposition. No registered verdict changes.

### F4 — major — D8 silently changes from h=0 to h=1

**Evidence.** S4 Table 14's raw h=0 conformal@5000 means are 0.939/0.885/1.101 pp and shares 33.7/25.8/56.8%; distinct h=0 shares are 59.4/45.6/60.9%. D8 instead quotes h=1's means 0.741/0.767/0.988 and shares 19.0/18.0/43.3%, plus distinct 53.1/48.0/49.3%, after an h=0 opening without changing the width label.

**Recommendation.** Insert an explicit new sentence/transition “At h=1 …” before the calibrated values, with L=256, alpha=.01, diagonal N_cal=5000 and the 1,000-key model-null denominator. Alternatively quote the actual h=0 calibrated rows if that is the intended contrast. Preserve the report exactly.

### F5 — major — Condensed remedy/transfer sentences lose conditions or contradict their constraints

**Evidence.** C4/J8's 3.5-fold transfer and 0.59 versus 0.17 pp are distinct h=1, alpha=.01, conformal@5000 pair-class summaries, not a generic law of per-key thresholds. C3's 0.99% mean/41.4% share are distinct-rule values; raw has a different mean/share. D5's final sentence compares a 1,000-key model mean to a 100-key corpus mean without naming the latter. C7's “multiplier … failing” conflicts with constraints 13/20 and S3 §7. C1 first asserts lattice ties before later calling them suggestive; C7's unqualified “unbiased” overstates a measured near-nominal mean.

**Recommendation.** Add a compact setting/aggregation clause to C1–C4/J7–J8 and D7; label both key sets in D5. Rewrite C7 as measured conservativeness under the distinct rule and a raw-rule numerical comparison outside Proposition 1's prerequisite. Use “measured near-nominal key-mean” and “suggestive lattice-tie account.” These edits retain the agreed numbers while preventing an invalid broader sentence in the draft.

### F6 — minor — The regenerated text-only SE range is 6.4–27.4%, not 5–15%

**Evidence.** Dividing the exact text-only SE by the exact key-only SE in the seven alpha=.01 regeneration rows gives, in table order, 9.22%, 17.22%, 22.54%, 6.44%, 8.32%, 14.08%, 27.45%. The saved JSON and independent regeneration agree. E1 and the Milestone 10 paragraph say 5–15%. The a_k-only/exact key-SE agreement within 6% is supported at alpha=.01; it should have that qualification.

**Recommendation.** Replace the range from the generated JSON, specify that it is an **SE ratio**, and keep it limited to the seven selected cells and alpha. Do not use it to infer that population text uncertainty is negligible everywhere.

### F7 — major — The software/transfer absence statement misses an existing two-key artifact

**Evidence.** The pinned `xlr8harder/synthid` amendment cited in §5 says, in its Evaluation contract, “Each key is calibrated separately against unwatermarked Qwen, human ELI5,” continuing with a third source. The surrounding contract freezes each threshold across six negative corpora; the Results table labels keys A/B and calibration source and reports both TPR and maximum FPR. It includes a human-calibrated Key-A result on unwatermarked Qwen. This predates the project (August 2026). The screen's GitHub `pushed:>=2026-09-15` restriction would exclude this unchanged repository. The broad §2 assertion that no software implements per-key calibration or reports per-key FPR is therefore false.

**Recommendation.** Add this dated public source as prior practice in C1/C4/D5/D8, constraint 32 and the occupied table; narrow the residual to the many-key systematic comparison and prediction. Remove the universal software-absence statement. Search windows for **new** work should not exclude older unrecognized occupants from the all-time priority check. No need to run or download its artifacts.

### F8 — major — The asserted serial/paced screening process is not supported by the raw logs

**Evidence.** Gate §2 says the screens ran one after another. A records 00:25–00:43 UTC; B records 00:26–00:36. A's `arxiv_api_rerun_log.tsv` and B's `abs_pages_index.txt` both record requests at **00:31:04Z** and **00:31:16Z**. The repository's terms record requires at most one request per three seconds and one connection at a time. Independent per-agent sleeps do not enforce an aggregate limit. The later eleven PDF fetches are separately paced and hash-verified; they are not the problem identified here.

**Recommendation.** Correct the retrospective claim to acknowledge overlapping screen streams; state that aggregate pacing/single-connection compliance cannot be certified from these logs (do not fabricate missing start/finish times). If fuller timing evidence exists, audit it explicitly. Use a single shared arXiv queue for future parallel literature work. Record this as a process correction; do not rerun the searches merely to make a new compliant log stand in for the old one.

### F9 — minor — The claimed complete inventory/union drops established integrity and weak regimes

**Evidence.** S1 R2 PASS (891 checks, zero flags, stated power limits) is not in the list; A4 omits S2's materially weaker descriptive Gumbel predictor (59.0% of 195 resolved consistent, median ratio 1.33; first-rule 46.9%, median 1.65); S3's h=0/far-tail secondary exceptions are absent from its broad adequacy summary. Section 1G does not include all distinctions in gate constraints 8–10 or the studies' conditional-target limitations. Constraint 30 compresses away S1 key-count/pairing exceptions. These omissions matter to a supposedly exhaustive source for the outline, even if they need not all appear in the main text.

**Recommendation.** Add a compact “secondary/integrity/limitations” crosswalk or make the completeness claim explicitly bounded. Carry the weak blocks into A4/C1's evidence notes, preserve the full constraint union by reference, and mark unrun remedies/extensions as unclaimed. Outline figure/table rows should retain their estimand and sample denominators. This needs no new scientific computation.

### F10 — minor — Quote-certification and workflow-state wording needs a small correction

**Evidence.** The §3 assertion that every quotation is an exact local substring is too strong: mathematical transcriptions normalize notation/line layout and Unigram uses ellipses; `2610.17655` p.16 has “secret key, shared partition and column configuration, context rule,” without the added initial “the.” The Guidelines phrase lacks a page despite occurring at pp.2/5/26. Some raw C records explicitly describe fetch-tool extracts rather than raw page text. The handoff still says J1 is waiting, although the log and gate record Yichen's yes. Generic “on every cell obeys” describes Monte Carlo checks, not exact equality of every stored bootstrap mean.

**Recommendation.** Distinguish literal quotes, normalized mathematical transcription and paraphrase; fix the small quotation and add the page. Describe source access accurately and the bootstrap check as agreement within Monte Carlo fluctuation. Update the current handoff state and append dated corrections for changed claim interpretations. Preserve J1/J9 as decisions and the other judgements as pending. These edits should not touch locked reports or historical outcomes.

VERDICT: REVISE
