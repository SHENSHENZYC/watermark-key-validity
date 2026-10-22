# R12 — assembled draft, round 2

Reviewer: Codex. Date: 2026-10-20 UTC.

## 1. Baseline and scope

Baseline: `main` at **`659fd3da0feb82563749110d6b110dbaad512fe7`**. The working tree was clean at entry. This is the requested re-review of the response to F1–F14 and the implementation of O9–O11, not a reopening of R01–R11, the agreed study outcomes, the locked protocols, the claim gate or J1–J11.

I read the response and its verification/disposition table; the specified revised passages of the assembled draft and their section sources; the literal scanner, allow-list and regenerated inventory; the six requested script diffs from `c34fd0f`; the changed bibliography entries and their saved records, fetch log and validation report; O9–O11; the October 20 decision-log entries; the handoff status; and the orientation's paper map and R12 row. I consulted the relevant locked protocol passages and core-code definitions as evidence, the agreed report blocks and registers, the overlap and two-way side-computation outputs, and the local literature texts and PDF covers. The round-one memo supplies the unchanged broader audit.

All six requested commands completed successfully:

| Command under `research/paper/` | Result |
| --- | --- |
| `fill_paper.py --check` | 543 placeholders in 16 files; scanner reports 175 literals: 95 grid settings, 80 allow-listed, 0 unallowed |
| `tables/make_tables.py` | 359 checks, 0 failed |
| `tables/make_appendix_tables.py` | 82 checks, 0 failed |
| `reviews_table.py` | 11 agreed checkpoints and R12 open; agreed totals 33 rounds, 171 findings |
| `build_references.py --offline` | 50 entries; one extraction warning, three purportedly resolved differences; see F16 |
| `assemble.py --render` | 3 main tables, 6 main figures, 38 appendix tables, 7 appendix figures, 50 citation keys; all assembly checks pass |

After these commands, `git status --short` was empty and `git diff --exit-code` passed. The assembled Markdown is byte-identical to `HEAD`, SHA-256 **`4c7a7ce25f3a9fe7d25b6d0cd2f437275fd19be4fc7a8139bfe2b56b17ae8915`**. Passing checks do not establish the properties their implementations omit; the residual findings below include examples that pass them.

I ran no study runner, analyzer or report builder, loaded no model or token cache, downloaded nothing, and committed nothing. The authorized render and local cover/page previews are under ignored `render/`. This memo is the only review-authored repository change.

## 2. Claims against evidence

### 2.1 Disposition of the round-one findings

| Round-one item | Round-two assessment |
| --- | --- |
| Round 1 F1 | The substantive given-key overclaim is corrected in §8, and §3.6/§6.1 explicitly distinguish calibration-draw validity from validity for every frozen set. The reference-law qualification replaces “by construction.” Two exact-nominal phrases remain in §6; see F20. |
| Round 1 F2 | Corrected. §3.6/A.3 state projective monotonicity for `C(p_h)`, not empirical occupancy collision or observed SD. §3.3 gives `(s−1)/(V−1)`; §3.4/A.1 restore the `h = 0` common-support condition. R5/S5 remain their registered empirical hypotheses. |
| Round 1 F3 | Corrected in substance. Fraction weights `w_q`, colour coefficients `w_z`, and standardized weights `b` are distinguished, with the required conversion and covariance assumptions. The cross-set covariance and algebraic floor use `b`; Unigram's unique-token count is identified as this paper's `s`; `a` and the lower bound on `z_emp` are defined. |
| Round 1 F4 | Gumbel mean, variance, fourth cumulant, tolerance and unboundedness are supplied correctly; the quadrature counts and zero-variance branches match the protocol/code. The heterogeneous-threshold floor still needs its conditioning written explicitly, and the numerical floor comparison is not fully transcribed; see F19. |
| Round 1 F5 | Corrected. B.2 requires independent ideal-key draws conditional on the texts and allows dependence between texts/checks. It does not assert validity under arbitrary dependence between key draws. |
| Round 1 F6 | The missing evidence is now supplied or given a precise companion-file destination. All six new extracted report blocks match. D2b's values match the side computation. Some new captions/destinations are inaccurate; see F17/F18. |
| Round 1 F7 | Substantial progress: design counts and word forms are generated, and a literal inventory exists. **Not closed:** the inventory is not exhaustive, some occurrence-to-reason matches are wrong, and the paper still overstates enforcement. See F15. |
| Round 1 F8 | The SD and transfer qualifiers, model, strength, width, length, level, calibration size, keys and prompts have largely been restored. The abstract's power sentence still omits the calibration source and leaves the method implicit; see F20. The generated ranges are unchanged and correct. |
| Round 1 F9 | Every explicit `§n.m` reference has a matching current heading; the headings describe their paragraphs. The plural table-reference path escapes renumbering/validation and leaves a nonexistent Table 5; see F18. |
| Round 1 F10 | Corrected. §5.5 separately labels the `h = 1` and `h = 0` shares, all matching their registers and Table D11. |
| Round 1 F11 | Corrected. The specified threshold gives the claimed counterexample; A.8 states the checked-row domain and counts accurately. |
| Round 1 F12 | ICLR pages, TextSeal order and NIST record are corrected. The new automatic cover-order inference introduces a wrong Huang author order, and the published-entry cover log remains incomplete; see F16. |
| Round 1 F13 | The specifically requested §6.4 and Figure 6 citations are present; §5.1 carries the R4b discrepancy; the EU phrase appears once, in §2. The newly added operating-point caption needs the same local attribution/conditions; see F17. |
| Round 1 F14 | Bibliography status is settled in the section open items; availability correctly identifies Study 3's compressed analyzer output and its regeneration route. O9–O11 are recorded and applied. Residual audit descriptions and the render's scale/page attribution need correction; see F15/F21 and §4 below. |

### 2.2 Numerical and table checks

The following comparisons are independent of merely trusting the builders' success messages:

* **D7b:** all 18 rows and the complete block match Study 4's `operating_points` block, report Table 9.
* **D12a and D12b:** all 40 rows each, including the column notes, match Study 2's `deployer_kgw` and `deployer_gumbel` blocks, report Tables 16–17. The Qwen rows and quantile/worst-key crossed intervals are now present.
* **D13a, D13b and D13c:** respectively 120, 72 and 80 rows, with their notes, match Study 3's `remedy_class`, `cross_tok` and `t1_by_block` blocks, report Tables 9, 15 and 2. Each extracted table is also a verbatim substring of the agreed report.
* **D2b:** I checked all 120 numeric data fields against `outputs/study2_v0.1/report/tokenizer_overlap.json`, allowing only the table's displayed rounding. Shared-id counts, both occurrence-weight shares, predicted/observed correlations at both widths, and both semantic occurrence shares match. The source lengths are 256 for eight cells and 1,024 for the other two; the caption does not match that metadata.
* **D14 and D15:** the complete data bodies of `table2_deployer.md` and `table5_transfer.md` are unchanged from `c34fd0f`. Their move preserves the measurements; the main text retains their headline values.
* Both named companion supplements, `outputs/study3_v0.1/report/tables_remedy_full.md` and `tables_pairs_kgw_alpha0.01_full.md`, exist and are tracked. The absence of a public repository URL is the already recorded Stage 9 item, not a missing local supplement.

The revised language shares are exactly `75.1%–76.4%` / `66.5%–74.4%` at `h = 1`, and `99.8%–100.0%` / `99.7%–99.9%` at `h = 0` (raw/distinct). The Study 3 register still gives `0.98%–1.01%` for the conformal distinct-rule key-mean, `45.6%` for its measured exceedance share, and `3.5` for the English–other transfer factor. The power design remains 100 keys, 50 prompts per key and three prompt cells. A.8's counts match the two side JSON summaries: **3,180/3,582** and **9,724/10,404**.

The new design-register values agree with the grids: four studies, four corpus sources, six languages, two tokenizers, five Study 2 widths, three retention rules, twenty cell/tokenizer units, five English and five other-language cells, six methods, three generation arms, two strengths, two generation widths, one model, six core laws and two control laws. The log-scale band half-width is `log2(1.5)`, displayed as `0.58`; “about a fifth” is generated from the registered primary ratio `1.21`. Not every assertion advertised as an independent-record check actually is one: for example, “G sources = audit sources” compares the computed source count with the literal `4`. The value is right; the check's label is stronger than its implementation.

The review counts remain appropriately restricted to agreed R01–R11. R12 is named as open, and its findings do not enter the agreed totals. No model is listed as an author and no target venue is named.

### 2.3 Derivations and quotations

For the fixed-size reduction, setting `A = 1/s`, `B = 1` gives `(s−1)/(V−1)` directly. It reaches one only at `s = V`. The stated `h = 0` covered-support variance is then `g(1−g)(V−s)/(s(V−1))`. The earlier two-text counterexample still distinguishes empirical occupancy collision from projective raw-law collision; the revised manuscript no longer asserts the false implication.

The conversion is `w_z = b/sqrt(γ(1−γ))`. At `g = γ` with independent colours, `Cov_K(z_i,z_j) = <b_i,b_j>`. Writing `A_S = ||b_S||²` and `ρ̄_S = A_S − σ_S²/n_S` gives

`v_raw + σ_C²/N_cal + σ_E²/N_E = ||b_C − b_E||²`.

These scales now agree between §3 and A.1/A.5. The p-scale cap `t_emp ≤ α` correctly becomes `z_emp ≥ z_α`. For Exp(1) scores the mean is one, variance one and fourth cumulant six, so the weighted-mean variance is `A` and the specified Gumbel tolerance is `10⁻⁹ A`.

The A.6 enumeration over all six green sets gives `(deployment level, calibration level) = (1/2,0)` for `{1,2}` and `{3,4}`, and `(0,0)` for the other four, using `max(P′ count)+1/2`. This verifies the revised threshold construction. A.5's 20,000-node moment integral, 1,000-by-1,000 finite-share integral, 1,000-node `v = 0` branch, 4,000-node fixed-threshold integral and `ρ̄_E = 0` binomial branch match the pinned definitions. The remaining transcription points are F19.

I repeated the substring checks for the remaining decisive direct quotations:

| Quotation | Local source and PDF page |
| --- | --- |
| “might result in 0% training-conditional coverage…” | `2205.03647.txt`, p. 2 |
| “two sources of variability” | `2205.15461.txt`, p. 11 |
| “the bias belongs to the pair of key and vocabulary” | `genhatharan_nominal_fpr_2026.txt`, p. 1 |
| “by the variance formula for sampling without replacement” | `2306.17439.txt`, **p. 32**; Lemma C.21 begins on p. 31 |
| “the error rate of the detection” | `ec_code_of_practice_129555.txt`, p. 17 |

The EU quotation has exactly one occurrence in the assembled draft. §8 paraphrases it without drawing a compliance conclusion. The Unigram quotation's locator should be p. 32 or pp. 31–32, rather than p. 31 alone; the round-one memo already recorded the two-page passage.

The three saved official ICLR BibTeX files support pages **43738–43772**, **49660–49704**, and **100104–100149**. The cited arXiv versions remain unchanged. The NIST Crossref file now exists and records the DOI, corporate author, title and issue date 2024-11-20; the bibliography uses the local cover's title wording. The saved validator has zero errors and four recommended-field warnings, for the unchanged TMLR/HDSR omissions assessed in round one. These warnings are separate from the cover-order issue.

I visually inspected both local covers relevant to the ordering changes. TextSeal v2 places Rebuffi third, as now entered. Huang v1 places **Jiao fourth, Jordan fifth**, agreeing with the original arXiv order and disagreeing with the newly generated bibliography.

## 3. Method and statistics

The corrections preserve the agreed design and the distinctions that matter: conditional realized-text targets versus population extrapolations; finite-evaluation versus reference-population exceedance shares; independent keys versus shared texts; registered empirical width/length rules versus algebraic statements; and a measured transfer result versus a guarantee. W2 remains FAIL with all six rows unresolved. The added tables do not change a verdict or create another analysis.

F1–F5's principal conceptual errors are substantially repaired. The remaining statistical edits concern precision of the manuscript, not a reason to rerun a study: define the conditional probability in the heterogeneous-threshold floor, transcribe the floor-comparison slack or cite its exact implementation, retain “approximately/near” for measured key-means, and identify the calibration source in the abstract's power cost.

The finite-sample limits remain visible. Shared keys do not turn cell counts into independent replications; sampled maxima are not population extremes; the crossed quantile intervals now have a real destination; the synthetic figure acknowledges its report's absence of crossed intervals; and no additional prompts, calibration draws or power result have been invented.

## 4. Process, decisions and presentation

The diff from `c34fd0f` contains no change under `outputs/`, the study protocol/report paths, study implementation directories, or the fixed claim gates. Thus the revisions examined here preserve the locked scientific record. No holdout opening was needed for this review. I found no new download, terms-of-use or publication action to assess.

O9 is applied: the two selected tables are D14/D15; their headline numbers remain in the main text; the reserve prose cuts are present. O10's comparator/predictor cuts and O11's single EU quotation are applied. I treat those choices as Yichen's decisions. I do not substitute a deeper cut or reopen the target-length decision.

The requested render reproduces **18 main-only pages**, **19 with statements**, **14 without figures**, **15 without tables**, **12 prose-only**, and **65 full-draft pages**. The final main-only page has 14 nonblank extracted text lines, consistent with the reported short final page. The ceiling of about 13 is not met and the response says so. However, the full PDF and main-only PDF use different physical text scales; consequently the build's “47 pages of statements/references/appendices” subtraction is not valid. See F21. This is a render fact, not a new length preference.

The live paper map/R12 row reflect round two, but some surrounding navigation text is stale: orientation §1 still asserts “no typed number” and the old 17/49-page state; the handoff's long status paragraph appends an old “Then: §8 … appendices … bibliography … assembly … R12” queue after its updated round-two state; its “Waiting on Yichen” line still describes the handover now made. These should be reconciled when the conductor records this round, while leaving dated historical entries intact. The section open items have mostly become change histories, which is harmless if clearly labelled; their claim that the math tolerances are individually allow-listed and regex-verified is not accurate (F15).

The new promise list is a useful guard for known table content, but a substring checklist is not a semantic proof of every caption. The specific remaining failures are F17/F18. The bibliography's new order checker likewise needs visual adjudication of extraction-order disagreements, rather than automatic rewriting.

## 5. Independent search

This round is the requested bounded correction audit. I did **not** repeat the arXiv/OpenAlex/Semantic Scholar/GitHub discovery searches or download new material. Web access was not the limitation; I relied on the round-one search record and the saved primary records for these revisions. Therefore this memo makes no new absence-of-occupant claim for October 20. The embargoed Avcıbaş “Key-free auditing” record remains an unassessed access gap, already recorded for the Stage 9 gate. Neither its title nor the earlier negative search establishes novelty.

## 6. Findings and recommendations

### F15 — Major: the literal audit still does not enforce the property asserted in the paper

**Evidence.** `literals.py:37–38` removes every math span before checking settings or literals. Consequently actual typed settings and tolerances in §3/A/B never reach either the grid check or the allow-list. The open items of A/B explicitly say the tolerances are allow-listed with source passages verified by the scan, but the JSON has no such entries for the displayed `10⁻⁶`, `10⁻⁹`, `10⁻¹²` formulas. `WORDS` also omits “zero,” “one” and the tens sixty–ninety. The abstract still types “On one model's…” outside a placeholder.

In-memory checks, without editing a source file, returned **no findings** for `There were zero failures.`, `There were sixty keys.`, `The estimate was $0.123$.`, and `We used $N_{\mathrm{cal}} = 5{,}001$ null texts.` The quantile-stripping pattern also removes `95% keys` in `We measured 95% keys above nominal.`

Allow-list matching uses an entire line/paragraph (`literals.py:178`), not the literal's occurrence. The actual inventory consequently labels A.1's “three normalisations” as the collision-quantity definition, and A.2's “two disjoint seeded subsamples” as covariance algebra, bypassing its intended sourced rule. A test sentence containing “two datasets” and later “between two texts” allows both occurrences as covariance algebra. The own-study result “three evaluation cells” is also permitted as a sourced literal rather than generated, despite the unqualified “every result and count” claim.

**Inference.** The reported 175/95/80 counts faithfully summarize this scanner's output, not every remaining numeral/counting word or every verified constant. The improved pipeline still cannot support §1, §8 and E.2's universal enforcement statements.

**Recommendation.** Inventory numeric constants inside math and classify them explicitly, distinguishing algebraic constants from design settings, tolerances and results; complete the counting-word coverage; match an exception to the particular span/phrase; and distinguish quantile labels from measured key shares. Generate remaining own-study counts or state their reviewed exceptions accurately. Correct the open-item and manuscript descriptions to the property actually checked. Add focused refusal checks for these demonstrated escapes. No empirical number or locked file needs to change.

### F16 — Minor: the cover-order correction introduces an incorrect Huang author order

**Evidence.** The visual cover of `research/literature/pdfs/2602.17608.pdf`, p. 1, reads Huang, Xu, Ramchandran, **Jiao** across the first author line, then **Jordan** below. The new bibliography instead puts Jordan fourth. `build_references.py:219–225` sorts authors by first occurrence in extracted text; the extraction happens to emit Jordan before Jiao. The response, fetch log and October 20 correction entry then describe this extraction artifact as a real source disagreement.

The published-paper branch also discards `cover_log` when writing its entry log (`build_references.py:300`), so the missing Common Pile local-cover check is still absent from the saved cover audit. Other entries explicitly fall back to the first two authors when a surname repeats; these are partial checks, not full-order confirmations.

**Recommendation.** Restore Jiao fourth/Jordan fifth and remove that entry's false disagreement note. Treat extracted-order differences as candidates for visual checking, with explicit verified overrides such as TextSeal's, rather than automatically reordering. Persist checked/skipped/partial cover status for published entries too. Append the correction to the response/log. Also correct §3.3's Unigram proof-quotation locator to p. 32 or pp. 31–32.

### F17 — Minor: the restored supplements have correct values but several inaccurate captions or destinations

**Evidence.** D2b says “per corpus cell at L = 256,” but the side JSON's `h0.L` and `h1.L` are 1,024 for `wikipedia_en_1024` and `gutenberg_en_1024`. The side computation is specifically **raw rule, each cell's longest length**, on the stored production key sample; the caption omits the rule and key count.

Figure 5 says “the other tokenizer Table D13b,” whereas D13b aggregates **cross-tokenizer** calibration/evaluation pairs. It is not the same-tokenizer Qwen counterpart to the Llama heatmap; those per-pair rows are in the named companion supplement. D12a's “each with its crossed … interval” grammatically includes the key-mean, but its key-mean column has no interval. D7b's new operating-point caption names only “the primary arm” and names Genhatharan/AutoMark without citation keys; it compares both null laws without the LUNA/two-key attribution supplied in §7.4/Figure 6.

**Recommendation.** Correct D2b to the raw rule at each cell's longest length and state its key/text sample. Point Figure 5's Qwen counterpart to the correct companion rows and label D13b explicitly as cross-tokenizer transfer. Limit D12a's interval claim to columns that contain intervals. Make D7b's model/arm/prompt/calibration conditions and required local citations explicit. Generate caption metadata from the same source records where practical. Keep every table value unchanged.

### F18 — Minor: a plural reference bypasses renumbering and points to a nonexistent Table 5

**Evidence.** Appendix D's introduction, assembled draft line 381, says: “Items D12 and D13 carry the supplements that **Tables 2 and 5** promise.” There are now only three main tables. These are the former deployer/transfer promises, whose tables are now D14/D15. Both `renum` and the main-table reference check in `assemble.py` match singular `Table (\d+)`; neither sees this plural construction. The assembly passes.

**Recommendation.** Rewrite the sentence with D14/D15, and support plural lists/ranges in renumbering and validation, preferably using explicit logical float identifiers instead of bare pre-assembly numbers. Keep report-internal table references separately scoped. The numbered section-reference corrections themselves are sound.

### F19 — Minor: the varying-threshold floor needs conditional probabilities, and the flag threshold omits its numerical slack

**Evidence.** A.2 writes the floor as `E[mean_i π_i(1−π_i)]/N_eff` but defines `π_i = P(Z_i > τ_i)` without conditioning on the common shift. These marginal probabilities are constants and do not give the stated expression or its zero-residual limit. For example, with `σ = 0`, standard-normal shift, thresholds 0 and 1, and two texts, that literal reading gives approximately **0.09587094**, whereas the correct conditional floor is zero, as the next clause says.

A.5 says an estimate below `−τ_v` is flagged. The locked Study 3 protocol §9 and `s3_core.py:240` use `v_raw < −τ_v(1+10⁻⁹) − 10⁻³⁰⁰`. The mathematical floor and its numerical comparison are distinct.

**Recommendation.** Define `π_i(D) = P(Z_i > τ_i | D)` and write the outer expectation over `D`; retain the existing paired-copy expression for its evaluation. State the numerical slack or give the exact protocol/code locator beside the flag rule. These are transcription corrections, not changes to the predictor or agreed outcomes.

### F20 — Minor: finish the local calibration qualifications in §6 and the abstract

**Evidence.** §6.1 still says calibration “brings the key-mean level **to nominal**” immediately before `0.98%–1.01%`; §6.3 says “with the key-mean **at α**.” §8 now correctly says “approximately.” The abstract's power sentence says only “per-key calibration on 5,000 calibration texts”; it does not identify the **diagonal human-null calibration source**, and does not explicitly distinguish conformal from tolerance calibration there. Constraint 17 requires that source; the generated cost range is the conformal@5000 diagonal result.

**Recommendation.** Use “near nominal/near α” consistently in those measured statements. Name “per-key conformal calibration on 5,000 same-cell human-null texts” in the abstract's power sentence. This preserves O10's chosen comparator cuts and the numbers while carrying the remaining condition; it is not a new abstract-content decision. The given-key versus calibration-draw distinction is otherwise repaired.

### F21 — Minor: the full render shrinks the document, making its scale description and page subtraction misleading

**Evidence.** Visual inspection and Poppler's PDF text coordinates show substantially different physical scales in `render/paper_main.pdf` and `paper_full.pdf`. At `pdftohtml -xml -zoom 1`, the body font is reported at rounded size **10** in the main-only PDF and **7** in the full PDF. For the identical first-page text “), and the deployer who must state a”, its width is **148.443122 pt** in the main-only PDF and **109.384386 pt** in the full PDF, about 73.7% as large; its height changes proportionately. This is actual scaling, not different line wrapping.

In the full PDF, §8 is on page 12 and the AI-use/availability statements start on page 13, whereas the main-only PDF has 18 pages. Nevertheless `assemble.py` records `pages_statements_references_appendices = 65 − 18 = 47` and describes both renders as 11 pt. The identical median character count per line cannot detect uniform shrinking.

**Recommendation.** Diagnose and contain the full-document overflow/print scaling, keeping the body at the intended physical size and handling wide tables locally; check rendered font/geometry, not just characters per line. Count section boundaries within the same PDF or omit the subtraction. Until corrected, label these as differently scaled diagnostic renders. O9's table/prose choices remain Yichen's; the reproduced 18-page main-only count is not evidence of a 13-page result, and Stage 9 still needs its own typeset count.

VERDICT: REVISE
