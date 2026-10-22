# C11 — Generalisability theory for LLM judges (search-level screen, 2026-10-08)

Conventions. "Observed" sentences report what a search result or page said; anything obtained through the fetch tool is a paraphrase and is marked "via fetch tool". "Inference" and "Proposal" sentences are mine. Every "nothing found" statement is search-level; absence is not proof of novelty.

## Candidate (one sentence)
Decomposing LLM-judge scores into item, judge, prompt-template and decoding-seed variance components (a G-study), what reliability do common judge set-ups reach, and how many judges × templates × items are needed for a target reliability (a D-study)?

## Queries run
- arXiv API (project tool), `abs:"generalizability theory" AND (abs:"language model" OR abs:LLM OR abs:"language models")` — HTTP 429; replaced by the arXiv web search below.
- arXiv API, `abs:"variance components" AND abs:judge`, newest first, max 25 — 2 hits (2609.29709, 2605.06652).
- arXiv API, `abs:judge AND abs:"prompt template" AND (abs:variance OR abs:reliability OR abs:"variance components") AND (LLM terms)` — read timeout after a 429; not completed.
- arXiv web search (fetch tool), all fields `"generalizability theory"`, newest first, size 50 — 20 hits shown, 10 involving LLMs, AI raters or LLM judges.
- arXiv web search (fetch tool), abstract `"LLM-as-a-judge" AND (ICC OR intraclass OR "variance components" OR "variance decomposition")` — 0 results.
- WebSearch, `"generalizability theory" "LLM-as-a-judge" OR "large language model" judge variance components reliability decision study` — about 30 links; found 2608.29517, 2603.01865, 2507.19980, 2607.11981, 2606.13685, 2609.29709, 2609.27787, the AIME-Con 2026 paper by Li & Lee, and reference-list leads 2606.19544, 2602.00521, 2604.11581.
- WebSearch, `"Judging the Judges" Thakur 2024 arXiv ...` — confirmed 2406.12624 (GEM workshop 2025); also surfaced 2510.09738 ("Judge's Verdict") and 2606.00093.
- WebSearch, `"Evaluating general-purpose AI with psychometrics" Wang 2023 arXiv` — confirmed 2310.16379.
- Abstract pages fetched (fetch tool): 2609.27787, 2608.29517, 2603.01865, 2609.21277.
- Dataset cards as for C04 (MT-Bench human judgments, PandaLM, HelpSteer2, JudgeBench, RewardBench).

## Nearest prior work
| Work (authors, year, venue or arXiv id, source of the hit) | What it already answers | Remaining difference |
|---|---|---|
| Cronbach, Gleser, Nanda, Rajaratnam 1972; Brennan, "Generalizability Theory" (Springer, year from memory, unverified); Shavelson & Webb 1991 primer (from memory) | The G-study/D-study framework, crossed and nested facet designs, generalisability and dependability coefficients. Observed: Brennan's book appears in the reference list of 2609.27787 (WebSearch snippet). | Not about LLM judges. |
| Wang et al. 2023, "Evaluating General-Purpose AI with Psychometrics", 2310.16379 (WebSearch) | A vision paper arguing for measuring latent abilities with psychometric tools. | No variance-component study. |
| Thakur et al. 2024, GEM workshop 2025, "Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges", 2406.12624 (WebSearch); "Judge's Verdict" 2510.09738 (title only); "Agreement Measurement for Rubric-based LLM Judges" 2606.00093 (title only) | Inter-rater agreement (Cohen's κ, later Scott's π) of 13 judges against humans on TriviaQA; agreement-statistic practice. | Agreement, not variance decomposition; no D-study. |
| Song, Lee, Jiao 2025, "Exploring LLM Autoscoring Reliability in Large-Scale Writing Assessments Using Generalizability Theory", 2507.19980 (WebSearch; arXiv web search) | G-theory applied to 2 human and 7 AI raters on AP Chinese writing; humans more dependable; blending human and AI scores raises reliability. | Essay scoring with API raters; facets are raters and tasks, not prompt template or seed (abstract-level). |
| Zhu, Tieleman, Bukhtiyarov, Chen 2026, "CyclicJudge", 2603.01865 (WebSearch; abstract via fetch tool) | Variance decomposition of benchmark scores into scenario, generation, judge and residual on MT-Bench and MindEval; round-robin judge-to-scenario assignment argued optimal for a fixed panel and budget. | G-theory is not named; no prompt-template facet; no D-study table (abstract-level). |
| Sunkavalli 2026, "LLM Judges as Raters: A Pre-Registered Audit of Severity, Halo, Reliability, and Version Instability in LLM Essay Scoring", 2608.29517 (WebSearch; abstract via fetch tool) | Pre-registered rater-effects battery including G- and D-studies for 12 LLM judges from 4 providers on 2,377 ENEM/Essay-BR and ASAP essays; a WebSearch snippet reports φ ≥ .80 at k ≤ 2 and that sampling temperature accounts for 38–100% of replication variance. | Essay scoring with API judges; facets are judges, versions and replications; prompt template not named (abstract-level). |
| Anand 2026, "Ask Which, Not How Good: Sizing Benchmarks Scored by an LLM", 2609.27787 (WebSearch; abstract via fetch tool) | G-theory decomposition of 373,019 judgments into system, item, judge and interactions; single-judge reliability has a ceiling set by system-by-judge variance that more items cannot lift; pairwise judging in both orders raises the ceiling to 0.986; first-position bias 8.6 pp; audit of 628 arXiv papers; MT-Bench data. | Prompt template and seed are not facets; judges not named in the abstract; the D-study is partial ("item cost of a target") rather than a judges × templates × items table. |
| Zhu 2026, "Three Ways Classical Test Theory Can Mislead About LLM Judges", 2609.29709 (arXiv API) | Argues single-judge, single-prompt statistics cannot isolate the judge; calls for gold labels or a varied scorer facet. | A critique and prescription, not a G-study. |
| Gui 2026, conditional G-theory for automated essay scoring, 2607.11981; Ning, Li, Kong 2026, "Agentic RAG Evaluation: Budget Allocation Across Questions, Trajectories, and Reads", 2610.05034; Srinivasan 2026, "Deployment Decision Reliability: A G-Theory Framework for Sizing Long-Horizon Agent Evaluations", 2608.11323; Żatuchin 2026, variance-components decomposition of LLM brand answers with a D-study, 2607.13304; Camuffo, Gambardella, Kazemi 2026, "Variance-Aware LLM Annotation", 2601.02370 (arXiv web search) | G-theory and variance-component sizing applied to adjacent LLM evaluation settings (agents, RAG, annotation, repeated queries); 2607.13304 includes repeats and paraphrases as facets. | Not LLM-as-a-judge scoring of model outputs with judge × template × seed facets. |
| Li & Lee 2026, AIME-Con 2026, G-theory for fine-tuned LLM item generation (ACL Anthology, via WebSearch) | A crossed G-theory design with seeds and prompt templates as facets — for generated test items, not judges. | The facet logic transfers; the object of measurement differs. |
| "The Coin Flip Judge?" 2606.13685 (authors unverified); Li, Yu, Li 2026, "How Many Humans Are 32 LLM Judges Worth?", 2609.21277 (WebSearch; abstract via fetch tool) | ICC(2,1) for two API judges over 50 repeated trials, about 45% of pointwise variance from run-to-run noise; human-equivalent panel size via distributional and spectral matching on ChaosNLI. | Neither names G-theory or prompt-template facets. |

## Occupied (what the candidate can no longer claim)
- "Apply generalisability theory to LLM judges" (2507.19980, 2609.27787, 2608.29517; CyclicJudge's decomposition is the same idea unnamed).
- "Judges, not items, are the reliability bottleneck; single-judge scores have a reliability ceiling" (2609.27787).
- "D-study for LLM essay judges" and "temperature/replication variance matters" (2608.29517).
- "Optimal allocation of a fixed judge panel across items" (2603.01865).
- "Classical reliability statistics mislead for a single judge with one prompt" (2609.29709).
- "Seeds and prompt templates as G-theory facets" exists for LLM item generation (Li & Lee 2026) and paraphrase facets for LLM answers (2607.13304).

## Residual gap
Type: adequacy check / applied evaluation. Observed: none of the LLM-judge G-theory papers I saw names the judge's prompt template as a facet (Anand: system × item × judge; CyclicJudge: scenario × generation × judge; Sunkavalli: judges × versions × replications; Song et al.: raters × tasks), and none uses small open-weight judges. Search-level; absence is not proof of novelty; the abstract-field query `"LLM-as-a-judge" AND (ICC OR intraclass OR "variance components" OR "variance decomposition")` returned zero results, and the arXiv API query on `judge AND "prompt template" AND variance` did not complete, so the template-facet gap rests on abstracts of the papers found by other routes. Inference: the field is moving fast (at least five G-theory-for-LLM-evaluation preprints in 2026), so the residual is a fully crossed judge × template × seed × item G-study with a D-study table, restricted to open-weight 1.5–3B judges, plus a check of whether Anand's single-judge ceiling and Sunkavalli's temperature finding reproduce for small open judges. Proposal: three open-weight judges × four templates × three seeds on about 300 MT-Bench or PandaLM pairs (about 10,000 judge calls, prefill-dominated and feasible on the laptop), with human labels used to separate "reliable" from "valid" as 2609.29709 recommends.

## Data and licence notes (search-level, from dataset pages via fetch tool)
| Dataset | Host | Licence as stated | Fields relevant to facets | Size |
|---|---|---|---|---|
| lmsys/mt_bench_human_judgments | Hugging Face | cc-by-4.0 | judge ids (author_x, expert_x) allow a human-rater facet; GPT-4 pair judgments; 6 models | 3,355 human + 2,400 GPT-4 rows |
| PandaLM test set | GitHub WeOpenML/PandaLM | code Apache-2.0; test-set licence not stated | label_0, label_1, label_2 — three human annotators per item (per-annotator labels released); five 7B-class models | about 1k |
| nvidia/HelpSteer2 ("disagreements" subset) | Hugging Face | cc-by-4.0 | individual annotator labels on five attributes (0–4); 3–5 annotators per response | 21,362 total |
| ScalerLab/JudgeBench | Hugging Face | mit | objective correctness labels; useful for a validity check against reliability | 620 |
| allenai/reward-bench | Hugging Face | ODC-BY with subset licences | chosen/rejected with chosen_model, rejected_model, subset | 2,985 filtered |

Blocker check: none for licences. Observed: no public dataset found releases LLM-judge scores crossed over several prompt templates and seeds; those must be generated locally. Inference: that is a compute question, not a licence one; a 3B judge at about 1,600 tokens/s prefill handles roughly 10^4 pairwise judgments in a few hours.

## Novelty score
2 / 5. Justification: the core idea (G-theory for LLM judges, D-studies, judges as the bottleneck) is occupied by at least four 2025–2026 preprints, one of them with 373k judgments and a literature audit. The residual — template and seed facets, small open-weight judges, a full D-study table — is incremental and weakly established because one targeted query did not complete.

## Access gaps and not done
- arXiv API returned HTTP 429 for the "generalizability theory" query and timed out on the prompt-template query; the arXiv web search substituted (20 hits shown for an all-fields query, newest first — older G-theory-for-AI-scoring work before 2025 was not swept).
- Full texts not read; the facet lists above come from abstracts and snippets, so a template facet hidden in a methods section would be missed.
- Reference-list leads 2606.19544 ("Reliability without validity"), 2602.00521 (IRT route to judge reliability) and 2604.11581 were seen by title only.
- OpenAlex, OpenReview and the measurement journals (Applied Psychological Measurement, Journal of Educational Measurement) were not queried; G-theory work on automated essay scoring there predates arXiv coverage.
