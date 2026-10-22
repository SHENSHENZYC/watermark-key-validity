# C08 — A calibrated hypothesis test for model lineage (search-level screen, 2026-10-08)

## Candidate (one sentence)
Test "model B was fine-tuned from base A" from weights or activations with a null distribution built from independent models and a controlled false-positive rate, across a public population of small Hugging Face fine-tunes (Llama-3.2-1B, Qwen2.5-0.5B, SmolLM2 families), and measure how power falls with fine-tuning depth, pruning, quantisation and model merging.

## Queries run (query, source, hits scanned)
- `abs:"model lineage" OR abs:"model genealogy"`, arXiv API (sorted by date), 25 hits scanned (about half off-topic: population genetics, LCA, surveys).
- `abs:fingerprint AND abs:"language model" AND (abs:"hypothesis test" OR abs:"false positive" OR abs:"statistical test")`, arXiv API, 16 hits.
- `(abs:"model provenance" OR abs:"derived model" OR abs:"derivative models") AND abs:"language model"`, arXiv API, 25 hits.
- `abs:"model merging" AND abs:fingerprint`, arXiv API, 12 hits.
- `abs:fingerprint AND abs:"fine-tuned" AND abs:"base model"`, arXiv API, 12 hits.
- arXiv API `id_list` fetch of 8 abstracts (2502.00706, 2510.19796, 2608.07786, 2601.11683, 2509.26404, 2511.06390, 2410.14273, 2509.26598), truncated at 620 characters each.
- WebSearch: `LLM "model lineage" OR "model genealogy" detection fingerprint fine-tuned base model statistical test 2025`, 3 result blocks, about 27 links scanned.
- WebSearch: REEF and PhyloLM arXiv ids (confirmed 2410.14273 and 2404.04671; both ICLR 2025 per proceedings links).
- WebFetch (via fetch tool): arxiv.org/abs/2607.10617 (modelDNA) and arxiv.org/abs/2602.00772 (Provable Model Provenance Set).
- Hugging Face Hub API: `GET /api/models?filter=base_model:<relation>:<base>&limit=1000` for 4 bases x 5 relation types; `GET /api/models/<id>` for licence and gating fields.

## Nearest prior work
| Work (authors, year, venue or arXiv id, source of the hit) | What it already answers | Remaining difference |
|---|---|---|
| Nikolic, Baluta, Saxena 2025, "Model Provenance Testing for Large Language Models", arXiv 2502.00706, NeurIPS 2025 (venue per papers.neurips.cc link in WebSearch); hit from arXiv API q08c and WebSearch | Frames "is B derived from A" as statistical testing; black-box output similarity scored against a reference distribution from unrelated models; evaluated on 600+ models of 30M–4B parameters with roughly 90–95% precision and 80–90% recall (figures from WebSearch summary, unverified against the PDF). | Uses outputs, not weights or activations. Reports precision/recall on a population; no power curves against fine-tuning depth, pruning, quantisation or merging seen in the abstract (inference from a truncated abstract). |
| Adil and Aamir 2026, "modelDNA: Calibrated Lineage Verification and Merge Decomposition from Sampled Weight Fingerprints", arXiv 2607.10617; hit from arXiv API q08b, abstract via fetch tool | Weight-only fingerprints from 100–300 MB ranged reads; calibrated probability over eight verdict classes with abstention; AUROC 1.0 and zero false positives at its reporting threshold on 15 Hub models (13 positives, 107 hard negatives); merge decomposition by constrained least squares; lineage graph of 55 models released. | Benchmark is tiny (15 positives). Pruning and quantisation not mentioned in the abstract. A "calibrated probability" is not a frequentist false-positive guarantee under a stated null (my inference). |
| Qiu, Zeng, Hou, Wei 2026, "Provable Model Provenance Set for Large Language Models", arXiv 2602.00772; hit from WebSearch, abstract via fetch tool | Formalises provenance with a coverage guarantee at a user-specified confidence level; sequential test-and-exclusion builds a small set of candidate parents; reportedly benchmarked on 455 Hugging Face LLMs (WebSearch summary, unverified). | Guarantee is coverage of true parents (set-valued), not the false-positive rate of a single pairwise test; signal type (weights or outputs) and robustness to pruning/quantisation not stated on the abstract page. |
| Kuditipudi, Huang, Zhu, Yang et al. 2025, "Blackbox Model Provenance via Palimpsestic Membership Inference", arXiv 2510.19796; hit from arXiv API q08c | Independence-testing formulation with an explicit null (suspect model independent of the owner's randomised training run); p-values from correlation with training-data order. | Requires the owner's training-data order (Pythia-style open runs); black-box; not applicable to arbitrary hub fine-tunes whose base's data order is unknown. |
| Zhang, Liu, Qian, Zhang et al. 2024, "REEF: Representation Encoding Fingerprints", arXiv 2410.14273, ICLR 2025; and Zeng et al. 2023, "HuRef", arXiv 2312.04828; hits from arXiv API id fetch and q08e | Training-free CKA similarity between suspect and victim representations; claims robustness to pruning, fine-tuning, merging, permutation. HuRef: weight-based invariant fingerprint. | Similarity scores with heuristic thresholds and no null distribution or error rate. This is exactly the failure mechanism the candidate names. |
| Chen, Shang, Liu 2026, "Who Built This Model? Tracing LLM Lineage via Spectral Fingerprints in Weight Space", arXiv 2608.07786; hit from arXiv API q08a and q08c | Weight-only lineage discrimination formulation ("LLM biometrics"). | Abstract read only to 620 characters; no mention of calibrated error rates or power curves seen. |
| Tong, Wang, Li, Kawaguchi et al. 2025, "SeedPrints", arXiv 2509.26404; hit from WebSearch and id fetch | Statistical detector based on initialisation biases that persist through training; targets the pretraining regime where post-hoc fingerprints fail. | Different regime (pretraining lineage); error control not visible at search level. |
| Cong et al. 2024, "Have You Merged My Model?", arXiv 2404.05188; Yamabe et al. 2024, "MergePrint", arXiv 2410.08604; Nasery et al. 2025, "Are Robust LLM Fingerprints Adversarially Robust?", arXiv 2509.26598; hits from arXiv API q08d | Merging and adversarial hosts as standard robustness axes for fingerprints. | These evaluate embedded or behavioural fingerprints, not intrinsic lineage tests with calibrated error rates. |

Also seen (not tabulated): Yax, Oudeyer, Palminteri 2024, PhyloLM, arXiv 2404.04671 (ICLR 2025; output-distance phylogeny); Yoon et al. 2025, Intrinsic Fingerprint, arXiv 2507.03014; Wang et al. 2025, GhostSpec, arXiv 2511.06390 (SVD-based spectral fingerprints); Shang et al. 2026, Attesting Model Lineage via fine-tuning trajectory, arXiv 2601.11683; Wu, Zhao, Wang 2025, gradient-based fingerprinting, arXiv 2506.01631; Hu et al. 2025, Fingerprinting LLMs via Prompt Injection, arXiv 2509.25448 (ACL 2026 per WebSearch, "statistical guarantees" claimed). Instructional fingerprinting (Xu et al. 2024) did not surface in these queries; its id is unverified.

## Occupied (what the candidate can no longer claim)
- Casting lineage or provenance detection as a hypothesis test with a null built from unrelated models: Nikolic et al. (2502.00706); as an independence test with p-values: Kuditipudi et al. (2510.19796).
- "Calibrated" lineage verification from weights, with abstention and merge decomposition: modelDNA (2607.10617).
- Formal error guarantees (coverage) for provenance over hundreds of Hub models: Qiu et al. (2602.00772).
- Robustness to fine-tuning, pruning, merging and permutation as evaluation axes: REEF, HuRef, GhostSpec, merging-robustness papers.
- Population-scale evaluation on real Hub models (600+; 455): Nikolic et al.; Qiu et al.

## Residual gap (type: adequacy check / applied evaluation)
- Observed: none of the abstracts read reports the realised false-positive rate at nominal alpha *as a function of transformation depth* (LoRA rank, full fine-tuning steps, 4-bit quantisation, magnitude pruning, slerp/ties merges) for weight- or activation-based tests on a real population of sub-1B fine-tunes.
- Inference: the open question is less "a new test" than "do the dominant similarity-score fingerprints (REEF CKA, HuRef, spectral) have usable null distributions, and at what transformation depth does power collapse?" — a calibration-and-power audit.
- Proposal: recast C08 as "Do published lineage fingerprints control their false-positive rate? A null-calibrated audit on ~200 real Hugging Face fine-tunes of Qwen2.5-0.5B, SmolLM2-135M and Llama-3.2-1B, with power curves under controlled transformations", explicitly positioned against 2502.00706 and 2607.10617.
- Search-level; absence is not proof of novelty: queries q08a–q08e and the two WebSearches returned no paper whose abstract reports power-versus-depth curves with a controlled false-positive rate for weight or activation tests on sub-1B models.

## Data and licence notes (search-level)
- Hub population (Hub API, 2026-10-08; `limit=1000`, so "1000" is a cap, counts below 1000 are exact at query time; metadata is self-reported `base_model` tags): meta-llama/Llama-3.2-1B — all relations >=1000; finetune 941; adapter 755; quantized 263; merge 26. Qwen/Qwen2.5-0.5B — >=1000; finetune 742; adapter 468; quantized 116; merge 19. HuggingFaceTB/SmolLM2-135M — >=1000; finetune 945; adapter 25; quantized 74; merge 2. HuggingFaceTB/SmolLM2-360M — 185; finetune 122; adapter 19; quantized 43; merge 1. The modelDNA abstract states that over 60% of Hub models document no parentage (via fetch tool), so the labelled population is a biased sample.
- Licences (HF API `cardData.license`): Llama-3.2-1B `llama3.2` (Llama 3.2 Community License; gated: manual approval); Qwen2.5-0.5B `apache-2.0` (not gated); SmolLM2-135M and -360M `apache-2.0` (not gated); EleutherAI/pythia-1.4b `apache-2.0`; openai-community/gpt2 `mit`. The Llama licence text was not read in this session; derivative-naming and redistribution terms are unverified here.
- Access and storage: ~200 fine-tunes at 0.5–1B in bf16 is roughly 1–2.5 GB each, 200–500 GB total — the binding constraint on a 16 GB laptop. Ranged partial reads of safetensors (100–300 MB per model, as modelDNA does — via fetch tool) are a known workaround. Gated Llama repos require account acceptance; not done.
- Compute: CKA on a few hundred prompts and weight statistics are forward-only or weight-only; feasible on MPS for sub-1B models. Independent "null" models must be genuinely independent pretrains of similar size (different families), which caps the null sample size (inference).

## Novelty score (1–5): 2
Justification: at least four 2025–2026 papers (2502.00706, 2607.10617, 2602.00772, 2510.19796) already cast lineage or provenance as a statistical test with a null, a calibrated output, or a coverage guarantee, and two of them evaluate on hundreds of Hub models. What remains is an independent calibration-and-power audit of the dominant similarity-score fingerprints under controlled transformations at small scale: an adequacy check, not a new method.

## Access gaps and not done
- The arXiv API returned HTTP 429 during the first batch (shared with sibling screens); all five C08 queries succeeded, but id_list abstracts were truncated at 620 characters and no PDF was opened.
- Nikolic et al. precision/recall figures and the "455 models" figure for Qiu et al. come from WebSearch summaries (unverified).
- Did not read the Llama 3.2 Community License text or the Hub gating form; did not verify the instructional-fingerprinting (Xu et al. 2024) id; did not query the Hub for SmolLM2-1.7B or Llama-3.2-3B.
- Hub `limit` capped at 1000, so exact totals for the aggregate `base_model:` tag were not obtained.
