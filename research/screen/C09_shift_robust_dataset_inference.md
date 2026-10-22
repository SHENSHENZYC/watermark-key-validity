# C09 — Shift-robust dataset inference with negative controls (search-level screen, 2026-10-08)

## Candidate (one sentence)
Make dataset-membership inference for LLMs valid under distribution shift between candidate members and reference non-members by a matched negative-control design (post-cutoff texts from the same source; multi-model differencing), and measure its power.

## Queries run (query, source, hits scanned)
- `abs:"dataset inference" AND abs:"language model"`, arXiv API, 15 hits.
- `abs:"membership inference" AND abs:"distribution shift"`, arXiv API, 24 hits (second attempt; first attempt HTTP 429).
- `abs:"membership inference" AND abs:"language model" AND (abs:temporal OR abs:"non-members" OR abs:"non-member")`, arXiv API, 25 hits.
- `abs:"negative control" AND (abs:"membership inference" OR abs:"training data detection")`, arXiv API, 1 hit (off-topic: single-cell benchmarks).
- `abs:"membership inference" AND abs:"pretraining data" AND abs:"language model"`, arXiv API, 5 hits.
- OpenAlex `search="membership inference" "distribution shift" language models non-members` (from 2023, date-sorted), 25 of 306 scanned; `search="negative control" membership inference language model training data`, 25 of 282 (noise, nothing relevant); `search="dataset inference" language model`, 25 of 565 (noise). Date-sorted OpenAlex was weak for this topic.
- arXiv API `id_list` abstracts: 2610.02986, 2606.17464, 2602.02819, 2609.10830, 2608.07914, 2606.03305, 2506.15271, 2609.33909 (620 characters each).
- WebSearch: `"dataset inference" LLM membership inference "distribution shift" non-members temporal 2025`, about 27 links; WebSearch for the Das, Meeus and Zhang ids (confirmed 2406.16201, 2406.17975, 2409.19798).
- WebFetch (via fetch tool): Hugging Face dataset card iamgroot42/mimir. HF API: monology/pile-uncopyrighted, EleutherAI/pile, EleutherAI/pythia-1.4b.

## Nearest prior work
| Work (authors, year, venue or arXiv id, source of the hit) | What it already answers | Remaining difference |
|---|---|---|
| Maini, Jia, Papernot, Dziedzic 2024, "LLM Dataset Inference: Did you train on my dataset?", arXiv 2406.06443, NeurIPS 2024; arXiv API q09a and q09b | Aggregates per-sequence MIA features over a dataset and returns a p-value; requires an IID held-out "private" set from the same distribution. | Assumes a same-distribution held-out set; shift between suspect and validation sets is the acknowledged weak point, not solved. |
| Zhao, Maini, Boenisch, Dziedzic 2025, "Unlocking Post-hoc Dataset Inference with Synthetic Data", arXiv 2506.15271; arXiv API q09a | Replaces the missing in-distribution held-out set with generated synthetic data plus calibration, for the post-hoc setting. | Synthetic rather than natural post-cutoff controls; whether validity under residual shift is quantified was not visible in the truncated abstract. |
| Zarzecki, Dubinski, Cygert 2026, "The Reliability Gap in Benchmark Auditing: Distribution Shift and Scale as Failure Modes of Contamination Detection", arXiv 2606.03305; WebSearch and id fetch | Identifies distribution shift (suspect vs validation sets violating IID) and small scale as failure modes of DI-style contamination detection; reports false flags under shift (WebSearch summary). | Diagnosis of failure, not a validated design that restores validity (inference from a truncated abstract). |
| Shi, Xiang, Xu, Lau 2026, "OLMo-Detect: A Multi-Stage, Confounder-Controlled Benchmark for Membership Inference on LLMs", arXiv 2610.02986; arXiv API q09b and q09c | Benchmark on the fully open OLMo 2 pipeline with distributional alignment of members and non-members and corpus-filtered non-members, across training stages. | Benchmark-side control; does not give an auditor a procedure when alignment is impossible. OLMo 2, not Pythia/Pile. |
| Wang, Wang, Li, Neel 2026, "CheckMIABench: Firm Foundations for Membership Inference Attacks on Language Models", arXiv 2606.17464; arXiv API q09b | Clean member/non-member constructions motivated by the finding that blind methods beat published attacks under subtle shift. | Again benchmark construction, not a shift-robust inference procedure. |
| Das, Zhang, Tramer 2024, "Blind Baselines Beat Membership Inference Attacks for Foundation Models", arXiv 2406.16201; Meeus et al. 2024/2025, "SoK: Membership Inference Attacks on LLMs are Rushing Nowhere (and How to Fix It)", arXiv 2406.17975, SaTML 2025; Zhang, Das, Kamath, Tramer 2024, "Position: Membership Inference Attacks Cannot Prove that a Model Was Trained On Your Data", arXiv 2409.19798; WebSearch (SoK also in q09b) | Shift confound established; SoK proposes randomised test splits, injected canaries, randomised fine-tuning and "post-hoc controls"; position paper argues the null cannot be sampled post hoc. | "Post-hoc controls" is named as a remedy, but (at search level) not built out as a matched negative-control falsification test with reported false-positive rate and power. |
| Duan, Suri, Mireshghallah, Min et al. 2024, "Do Membership Inference Attacks Work on Large Language Models?" (MIMIR), arXiv 2402.07841, COLM 2024; arXiv API q09b | Shows temporal shift (temporal_wiki, temporal_arxiv) inflates apparent MIA success; near-chance otherwise on Pythia/Pile. | Uses post-cutoff texts to *demonstrate* the confound; the candidate would use them as *negative controls* to calibrate the realised false-positive rate (inverted role; my inference). |
| Shihab, Akter, Sharma 2026, "When Is Benchmark Contamination Detectable? Information Limits and Power-Calibrated Audits", arXiv 2608.07914; Even et al. 2026, "Causal Evaluation of Membership Inference Attacks", arXiv 2602.02819; Nik Khah 2026, "Detectable Only Where It Is Confounded", arXiv 2609.10830; Liu et al. 2026, "Near-Duplicate Families Break Exact-Record Membership Inference", arXiv 2609.33909; OpenAlex and arXiv API | Power formalisation with matched clean/seen controls (detectability governed by alpha*rho*sqrt(m)); causal framing of memorisation and validity of zero-run evaluations; exact duplication counts from open corpora (OLMo-2, Pythia); near-duplicate confound. | Not dataset inference under shift per se, but they occupy "power-calibrated audit with matched controls" and "ground-truth membership from open corpora". |

## Occupied (what the candidate can no longer claim)
- Member/non-member distribution shift as the central confound of LLM MIA and DI (2406.16201, 2406.17975, 2402.07841, 2606.03305).
- Remedies via post-hoc controls, randomised splits or synthetic held-out data (2406.17975, 2506.15271).
- Confounder-controlled benchmarks with aligned non-members (2610.02986, 2606.17464).
- Power-calibrated audits with matched clean and seen controls, for benchmark contamination (2608.07914).
- Causal and one-run validity framing of membership evaluation (2602.02819).

## Residual gap (type: adequacy check + applied evaluation)
- Observed: the SoK lists post-hoc controls as a fix and the Reliability Gap paper shows DI failing under shift; no abstract read describes a falsification design in which known non-member, same-source, post-cutoff texts are passed through the full DI pipeline to estimate the realised false-positive rate, combined with differencing across models with different corpora and cutoffs (Pythia/Pile vs OLMo-2 vs SmolLM2) to separate memorisation from source-style effects.
- Inference: the residual contribution is an adequacy check — how often DI and Min-K%/ReCaLL-style scores declare membership on controls that cannot be members, as a function of shift magnitude — plus the power that remains once a negative-control gate is imposed.
- Proposal: "Negative-control calibration of LLM dataset inference under temporal shift", using MIMIR temporal_wiki/temporal_arxiv plus freshly collected 2025–2026 same-source text as controls, Pythia-1.4b (already cached) as the audited model and OLMo-2 / SmolLM2 as differencing models.
- Search-level; absence is not proof of novelty: `abs:"negative control" AND (abs:"membership inference" OR abs:"training data detection")` returned one irrelevant hit and the OpenAlex negative-control query returned noise; "post-hoc controls" in 2406.17975 may already contain this design in its body text, which was not read.

## Data and licence notes (search-level)
- iamgroot42/mimir (Hugging Face): licence MIT; gated (automatic approval after agreeing to share contact details); configs `arxiv`, `dm_mathematics`, `github`, `hackernews`, `pile_cc`, `pubmed_central`, `wikipedia_(en)`, `full_pile`, `c4`, `temporal_arxiv`, `temporal_wiki`; splits `ngram_7_0.2`, `ngram_13_0.2`, `ngram_13_0.8`; features member, nonmember, member_neighbors, nonmember_neighbors; size category 1K<n<10K, 2.57 GB total; intended for Pile-trained models (GPTNeo, Pythia, OPT) (all via fetch tool). The card does not state which Pile splits define members and non-members.
- monology/pile-uncopyrighted: licence "other", not gated, 100M<n<1B rows. EleutherAI/pile: licence "other", not gated. The original Pile contains copyrighted components (known issue; inference), so the uncopyrighted variant is the safer source for any redistribution. EleutherAI/pythia-1.4b: apache-2.0, not gated; already cached locally per the candidate note.
- Fresh post-cutoff controls would come from Wikipedia (CC BY-SA 4.0) and arXiv abstracts (arXiv API terms); neither licence was re-read in this session.
- Compute: scoring ~10k sequences on a 1.4B model at ~1,600 tokens/s forward is minutes to a few hours; multi-model differencing with OLMo-2-1B and SmolLM2-1.7B is feasible on MPS.

## Novelty score (1–5): 2
Justification: the confound is thoroughly documented (2406.16201, 2406.17975, 2402.07841, 2606.03305), remedies are being proposed (synthetic held-out sets 2506.15271; confounder-controlled benchmarks 2610.02986 and 2606.17464), and power-calibrated audits with matched controls exist for contamination (2608.07914). The specific negative-control falsification design with multi-model differencing was not found, but it is a modest design increment on well-occupied ground.

## Access gaps and not done
- First arXiv API pass hit HTTP 429 for four of five queries; the retry about six minutes later succeeded.
- No PDF read; the Reliability Gap and OLMo-Detect abstracts were truncated at 620 characters, so their exact remedies are not characterised.
- Did not read the Pile-uncopyrighted licence text, Wikipedia dump terms or Dolma/OLMo-2 data licences.
- OpenAlex date-sorted results were too noisy to be informative for this candidate.
