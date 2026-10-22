# C13 — Statistical reliability of activation-patching importance claims (search-level screen, 2026-10-08)

## Candidate (one sentence)
Determine how many prompts and what multiple-testing control are needed for component-importance rankings (attention heads, MLPs) from activation patching to be stable and significant, and how often published-style procedures declare spurious components.

## Queries run (query, source, hits scanned)
- `abs:"activation patching" AND (abs:statistical OR abs:"hypothesis test" OR abs:significance OR abs:reliability)`, arXiv API, 25 hits.
- `abs:"circuit discovery" AND (abs:"false discovery" OR abs:"multiple testing" OR abs:stability OR abs:reliability OR abs:"statistical")`, arXiv API, 9 hits.
- `abs:"mechanistic interpretability" AND (abs:"hypothesis testing" OR abs:"multiple testing" OR abs:"false discovery" OR abs:"statistical test")`, arXiv API, 4 hits.
- `abs:"activation patching"` sorted by date, arXiv API, 40 hits scanned (applications dominate; 3 methodological).
- `abs:circuit AND abs:faithfulness AND abs:"language model"` and `abs:"attribution patching"`, arXiv API: HTTP 429 on both attempts; not recovered (covered by WebSearch below).
- OpenAlex (from 2023, date-sorted), four searches, 25 each: too noisy to use (`"activation patching" statistical significance reliability` 105; `"circuit discovery" ...` 396; `"mechanistic interpretability" "hypothesis testing" ...` 3,868; `"attribution patching" OR "activation patching" prompts variance` 121,706).
- arXiv API `id_list` abstracts: 2606.16920, 2607.08349, 2510.00845, 2602.22968, 2608.13754, 2606.06267, 2606.09899, 2511.11711, 2605.08348, 2607.19317, 2410.13032 (600 characters each).
- WebSearch: `activation patching circuit discovery statistical reliability "multiple testing" OR "false discovery" OR "hypothesis testing" prompts 2025`, 7 result blocks, about 60 links; WebSearch for the Miller and Syed ids (2407.08734, 2310.10348 confirmed).

## Nearest prior work
| Work (authors, year, venue or arXiv id, source of the hit) | What it already answers | Remaining difference |
|---|---|---|
| Shi, Beltran-Velez, Nazaret, Zheng et al. 2024, "Hypothesis Testing the Circuit Hypothesis in LLMs", arXiv 2410.13032, NeurIPS 2024; WebSearch and id fetch | Formal tests of whether a *given* circuit preserves behaviour, is localised and is minimal. | Tests a proposed circuit; does not address the discovery step's component ranking or multiple testing over hundreds of components (inference; not mentioned in the abstract). |
| Meloux, Portet, Peyrard 2025, "Mechanistic Interpretability as Statistical Estimation: A Variance Analysis", arXiv 2510.00845 (v4); arXiv API q13b | Frames circuit discovery as statistical estimation on causal mediation analysis; shows single-input CMA scores have high intrinsic variance and that circuits are unstable as a result. | Closest predecessor. Whether it gives sample-size rules, null-calibrated p-values or FDR control over components was not visible at search level. |
| Wu, Tonin, Cevher 2026, "Demystifying Variance in Circuit Discovery of LLMs", arXiv 2606.16920, ICML 2026; WebSearch and id fetch | Decomposes EAP-IG variance into resampling, rephrasing and sample-wise components; proposes CEAP with a theoretical guarantee to cut resampling variance. | Studies EAP-IG (gradient approximation), not exact activation patching; variance reduction rather than error-rate control. |
| Asiaee 2026, "Certified Interventional Fidelity: Anytime-Valid, Adaptive Evaluation of Causal Claims in Mechanistic Interpretability", arXiv 2607.08349; WebSearch and id fetch | Anytime-valid sequential inference for patching, ablation and fidelity effects that are monitored or adapted during evaluation. | Per-claim validity; handling of selection over many components is unclear from the truncated abstract. |
| Anani, Lorenz, Schiele, Fritz et al. 2026, "Certified Circuits: Stability Guarantees for Mechanistic Circuits", arXiv 2602.22968; arXiv API q13b | Provable stability guarantees for discovered circuits with respect to the concept dataset. | Certification framework, not an audit of spurious-discovery rates in common practice. |
| Mahale 2026, "Explanation Multiplicity: Circuit-Level Interpretability Evidence Does Not Survive Defensible Analytic Variation", arXiv 2608.13754; WebSearch and id fetch | Pre-registered crossed grid over seven analytic axes (ablation operator, corruption, metric, prompt variant, seed, granularity, ...); circuits are functionally unstable; one model, one task. | Analytic-choice variation, not prompt sample size or multiple testing. |
| Miller, Chughtai, Saunders 2024, "Transformer Circuit Faithfulness Metrics are not Robust", arXiv 2407.08734; Zhang and Nanda 2023, "Towards Best Practices of Activation Patching", arXiv 2309.16042; Heimersheim and Nanda 2024, "How to use and interpret activation patching", arXiv 2404.15255; Conmy et al. 2023, ACDC, arXiv 2304.14997; Syed, Rager, Conmy 2023, "Attribution Patching Outperforms Automated Circuit Discovery", arXiv 2310.10348 (BlackboxNLP 2024); WebSearch | Ablation and corruption choices change faithfulness scores and the heads selected; methodological guidance; baseline discovery algorithms. | No error-rate control or sample-size analysis. |
| Enkhbayar 2025, "Which Sparse Autoencoder Features Are Real? Model-X Knockoffs for False Discovery Rate Control", arXiv 2511.11711; "Do VLMs Share Safety Neurons Across Modalities?", arXiv 2608.30750 (Benjamini–Hochberg against a control-neuron null; via WebSearch, unverified); Li and Subramani 2026, "How Much Do Circuits Tell Us?", arXiv 2605.08348; Bayat Makou et al. 2026, "Many Circuits, One Mechanism", arXiv 2606.06267; Zhang and Wang 2026, "When Attribution Patching Lies", arXiv 2606.09899; Seth et al. 2026, CircuitKIT, arXiv 2607.19317 | FDR control already used in neighbouring interpretability problems (SAE features; neurons); consistency and specificity of circuits across 6 tasks and 5 models; "phantom specialisation"; second-order correction for attribution patching; a toolkit that flags reproducibility and statistical-power gaps (via WebSearch). | None applies multiple-testing control to head- or MLP-level activation-patching rankings in LLMs with a calibrated null, or reports a spurious-component rate against prompt count. |

## Occupied (what the candidate can no longer claim)
- "Circuit discovery is statistical estimation and patching scores are high-variance random variables" (2510.00845); the three-way variance decomposition (2606.16920).
- Formal hypothesis tests for circuits (2410.13032); anytime-valid tests for patching effects (2607.08349); certified stability (2602.22968).
- Instability under analytic choices, ablation and corruption (2608.13754, 2407.08734, 2309.16042).
- FDR control in interpretability generally (2511.11711, 2608.30750).

## Residual gap (type: new method (modest) + adequacy check)
- Observed: no abstract read applies multiple-testing control (FWER, FDR or knockoffs) with an explicit null (clean-to-clean patching, permuted prompt labels) to head/MLP-level activation-patching rankings, nor reports how often the common procedure (top-k by mean logit difference over 20–100 prompts) selects components that vanish under replication, as a function of prompt count.
- Inference: a null-calibrated audit on GPT-2 small and Qwen2.5-0.5B with IOI-type tasks — per-component p-values from a clean-to-clean null, BH/Holm/knockoff selection, rank-stability curves against N prompts, and false-positive counts of common practice — fills that gap, provided it is positioned against 2510.00845 and 2607.08349 after reading them in full.
- Proposal: "How many prompts does a head need? Error-controlled activation patching."
- Search-level; absence is not proof of novelty: q13a–q13d (q13c in particular) and the WebSearch returned no such paper; two arXiv queries (circuit faithfulness; attribution patching) were not recovered after HTTP 429.

## Data and licence notes (search-level)
- openai-community/gpt2: licence MIT (HF API). Qwen/Qwen2.5-0.5B: apache-2.0, not gated. EleutherAI Pythia family: apache-2.0 (pythia-1.4b checked; smaller sizes not individually checked).
- Prompts: IOI and greater-than templates are generated procedurally (no data licence); TransformerLens and nnsight are MIT (recalled, unverified).
- Compute: GPT-2 small has 144 heads; full head-by-position patching over N = 500 prompts is roughly 144 x N forward passes of a 124M model — minutes to tens of minutes on MPS. Qwen2.5-0.5B (24 layers x 14 heads) is the same order. Permutation nulls multiply this by the number of permutations but remain within laptop budget (inference).

## Novelty score (1–5): 3
Justification: the variance and instability of circuit discovery is now well documented (2510.00845, 2606.16920, 2608.13754) and formal or sequential tests exist (2410.13032, 2607.08349), so "patching is noisy" is occupied; explicit multiple-testing control over components with a calibrated null and a spurious-discovery audit against prompt count was not found at search level.

## Access gaps and not done
- Two arXiv API queries (circuit faithfulness; attribution patching) failed with HTTP 429 on both passes; substituted by WebSearch.
- OpenAlex results were too noisy to use.
- Abstracts truncated at 600 characters; the full methods of 2510.00845 and 2607.08349 (the two closest) were not read — overlap could be larger than scored.
- 2608.30750 (BH-FDR on safety neurons) and CircuitKIT's power remarks are known only through WebSearch summaries (unverified).
