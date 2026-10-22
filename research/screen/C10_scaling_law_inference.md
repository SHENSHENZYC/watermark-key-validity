# C10 — Statistical inference for scaling laws at toy scale (search-level screen, 2026-10-08)

## Candidate (one sentence)
Quantify how uncertain fitted scaling exponents and compute-optimal allocations are from a realistic number of runs with seed noise, and test whether standard Chinchilla-style fitting procedures recover known exponents in a controlled 1–20M-parameter testbed.

## Queries run (query, source, hits scanned)
- `abs:"scaling law" AND (abs:uncertainty OR abs:"confidence interval" OR abs:bootstrap)`, arXiv API, 25 hits (mostly physics or unrelated; 3 relevant).
- `abs:"scaling law" AND abs:"random seed"`, arXiv API, 4 hits.
- `abs:"Bayesian scaling law" OR abs:"Bayesian scaling laws"`, arXiv API, 1 hit (in-context learning; not relevant).
- `abs:"compute-optimal" AND (abs:replication OR abs:discrepancies OR abs:"estimation")`, arXiv API, 25 hits (2 relevant).
- `abs:"scaling law" AND abs:extrapolation AND (abs:error OR abs:reliability OR abs:reliable)`, arXiv API, 25 hits.
- OpenAlex (from 2023, date-sorted), four searches, 25 each: `"scaling law" uncertainty confidence interval exponent estimation` (431), `"scaling laws" seed variance small models reliability extrapolation` (214), `"Bayesian scaling laws"` (14), `"compute-optimal" scaling replication Chinchilla discrepancies` (114); noisy but surfaced 2609.35707, 2609.21638, 2608.28308, 2608.07222 and a truncated id 2609.14xxx.
- arXiv API `id_list` abstracts: 2609.35707, 2603.22339, 2605.08541, 2604.22753, 2609.21638, 2608.28308, 2608.07222, 2502.17356, 2404.10102 (600 characters each).
- WebSearch: `scaling laws uncertainty confidence intervals exponents seed variance small models 2025 arXiv`, about 20 links; WebSearch for Conformalized Scaling Laws and the Porian id (2406.19146 confirmed; CSL found only as an ICML 2026 listing).
- HF API licence fields: roneneldan/TinyStories, HuggingFaceFW/fineweb-edu, Salesforce/wikitext.

## Nearest prior work
| Work (authors, year, venue or arXiv id, source of the hit) | What it already answers | Remaining difference |
|---|---|---|
| Hoffmann et al. 2022, "Training Compute-Optimal Large Language Models" (Chinchilla), arXiv 2203.15556 (id recalled, unverified in this session) | Approaches 1–3 for compute-optimal allocation; point estimates and a parametric loss fit. | No uncertainty treatment beyond reported intervals that later work disputes. |
| Besiroglu, Erdil, Barnett, You 2024, "Chinchilla Scaling: A replication attempt", arXiv 2404.10102; arXiv API id fetch | Approach 3 confidence intervals are "implausibly narrow" (would need >600,000 experiments versus fewer than 500 run); re-derived fit consistent with Approaches 1–2. | Re-analysis of one extracted dataset; no controlled ground truth, no seed-noise model, no coverage study. |
| Porian, Wortsman, Jitsev, Schmidt, Carmon 2024, "Resolving Discrepancies in Compute-Optimal Scaling of Language Models", arXiv 2406.19146, NeurIPS 2024; WebSearch | Explains the Kaplan–Chinchilla gap via last-layer FLOPs, warmup length and scale-dependent optimiser tuning. | Not an uncertainty study. |
| Choshen, Zhang, Andreas 2024, "A Hitchhiker's Guide to Scaling Law Estimation", arXiv 2410.11840, ICML 2025; WebSearch | Practical guidance from ~1,000 public models; seed-to-seed scatter is large; prefers wider size sweeps over repeated seeds. | Observational on existing families; no known-truth testbed; no coverage check of interval procedures. |
| Czech, Xu, Elmatad, Wang et al. 2026, "Problems with Chinchilla Approach 2: Systematic Biases in IsoFLOP Parabola Fits", arXiv 2603.22339; arXiv API q10d | Parabolic IsoFLOP fits bias compute-optimal allocation even on noise-free synthetic data; quantifies cost with a 90% CI. | Bias of one approach, not seed-noise variance or interval coverage across approaches. |
| Kricheli, Reid, Sarkar, Gandikota et al. 2026, "Tokens-per-Parameter Coverage Is Critical for Robust LLM Scaling Law Extrapolation", arXiv 2605.08541; arXiv API q10a and q10d | Collinear D = kN designs make the Gauss–Newton problem ill-conditioned; 30 seed refits with percentile bands. | Design diagnosis at larger scale; not a frequentist coverage study at toy scale. |
| Sermaxhaj, Alipour, Sinani, Hog et al. 2026, "ScAn-Bench: Evaluating Scaling Analysis Methodology", arXiv 2609.35707; OpenAlex and id fetch | Surrogate benchmarks from 4,524 LLM and 8,024 VLM checkpoints to evaluate how scaling laws and prescriptions are obtained. | Surrogate of real pipelines rather than a known-truth testbed with seed replication (inference from a truncated abstract); the closest potential overlap. |
| Zhao, Qin, Alvarez-Melis, Kakade et al. 2025, "Random Scaling of Emergent Capabilities", arXiv 2502.17356; Ajroldi et al. 2026, OpenEuroLLM scaling laws, arXiv 2608.28308; Li et al. 2026, "Spend Less, Fit Better", arXiv 2604.22753; Bukkapatnam and Karuturi, "Conformalized Scaling Laws", ICML 2026 (no arXiv id found); Kirkley 2026, "Detectability limits of scaling laws", arXiv 2609.21638 | Seed bimodality drives apparent emergence; seed noise quantified at 50M (std about 2.7e-3, via WebSearch summary); active experiment selection for fitting; split-conformal intervals (OLS 95% intervals reportedly cover 61% in a Pythia-style simulation, via WebSearch); resolution limits for exponents in complex systems. | None reports coverage of standard CI procedures under a known truth at 1–20M; Kirkley's theory is for size–output scaling in cities and organisms, not loss curves (transfer would be the candidate's work). |

## Occupied (what the candidate can no longer claim)
- Critique of Chinchilla intervals (2404.10102); bias of Approach 2 (2603.22339); ill-conditioning of collinear designs (2605.08541).
- Seed variance as a first-order nuisance in scaling fits (2410.11840, 2502.17356, 2608.28308).
- Methodology benchmarks for scaling analysis (2609.35707) and experimental design for fitting (2604.22753).
- Distribution-free prediction intervals for extrapolation (Conformalized Scaling Laws, ICML 2026).

## Residual gap (type: adequacy check / simulation study)
- Observed: none of the abstracts read reports the *coverage* of confidence intervals for exponents and allocations from Approaches 1–3 under a known ground truth with seed replication at realistic run counts (10–50 runs).
- Inference: the gap is a frequentist adequacy check — simulation from a generative model of loss curves with seed noise, plus a real 1–20M testbed with 3–5 seeds per configuration — asking whether Huber-loss BFGS, bootstrap or profile intervals attain nominal coverage and how many runs give plus or minus 10% exponent precision; and whether the 1–20M regime even follows the parametric form (one 2026 preprint, "Scaling Laws in the Tiny Regime", arXiv 2603.07365, reports erratic slopes below ~5M parameters, via WebSearch, unverified).
- Proposal: "Do scaling-law confidence intervals cover? A seed-replicated tiny-model testbed", with pre-registered fitting procedures and reported coverage, bias and run-count requirements.
- Search-level; absence is not proof of novelty: queries q10a–q10e and the WebSearch returned no coverage study; ScAn-Bench's methods were not read beyond 600 characters and may overlap.

## Data and licence notes (search-level)
- roneneldan/TinyStories: licence cdla-sharing-1.0, not gated, 1M<n<10M rows (HF API). HuggingFaceFW/fineweb-edu: odc-by, not gated, 1B<n<10B rows (sample subsets exist; not checked). Salesforce/wikitext: cc-by-sa-3.0 and gfdl, not gated, 1M<n<10M rows.
- Recipes: nanoGPT (MIT; recalled, unverified); the TinyStories paper's small GPT configurations.
- Compute: 50–100 models at 1–20M parameters. Training throughput on the M5 was not measured in this session; from 1,600 tokens/s forward on a 3B model, order 10^5 tokens/s for a 10M model is a rough extrapolation (inference). At 20M tokens per run, 100 runs is about 2B tokens: hours to a few days on MPS. Feasible, and the dominant cost.

## Novelty score (1–5): 3
Justification: uncertainty and robustness of scaling-law estimation is an active 2024–2026 topic with a methodology benchmark (2609.35707), bias and conditioning analyses (2603.22339, 2605.08541) and conformal intervals (ICML 2026), but a known-truth, seed-replicated coverage study of the standard confidence-interval procedures at toy scale was not found at search level.

## Access gaps and not done
- First arXiv API pass hit HTTP 429 for all five queries; the retry succeeded. OpenAlex truncated one relevant id ("When does a scaling result justify a different allocation?", arXiv 2609.14xxx).
- Conformalized Scaling Laws: no arXiv id located; details from a WebSearch summary of the ICML 2026 page only.
- Hoffmann et al. id recalled, not verified; "Scaling Laws in the Tiny Regime" (2603.07365) abstract not read.
- ScAn-Bench method not read beyond the abstract — the closest potential overlap and the first thing to read at the gate stage.
