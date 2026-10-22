# Citation keys used in the section drafts (provisional inventory for step 4, `references.bib`)

Every key below is resolved at step 4 from a primary source (the arXiv API by id, the proceedings page, the publisher page, the PDF cover for author order, the repository at its commit for software, the page's own date for documentation) and validated with the citation-management skill at 0 errors; a key marked *to settle* has no primary source fixed yet. Keys follow `<firstauthor><year><word>`. The local full texts are under `research/literature/txt/` (git-ignored), tagged in `research/literature/pdf_manifest.json`.

| Key | Work | Primary identifier | Status |
|---|---|---|---|
| `kirchenbauer2023watermark` | Kirchenbauer, Geiping, Wen, Katz, Miers, Goldstein, "A watermark for large language models", ICML 2023 | arXiv 2301.10226; PMLR v202 | held |
| `kirchenbauer2024reliability` | Kirchenbauer et al., "On the reliability of watermarks for large language models", ICLR 2024 | arXiv 2306.04634 | held |
| `fernandez2023bricks` | Fernandez, Chaffin, Tit, Chappelier, Furon, "Three bricks to consolidate watermarks for large language models", WIFS 2023 | arXiv 2308.00113 | held |
| `zhao2024unigram` | Zhao, Ananth, Li, Wang, "Provable robust watermarking for AI-generated text" (Unigram), ICLR 2024 | arXiv 2306.17439 (Lemma C.21 p. 31; Remark E.2 p. 34; Lemma F.2 p. 36) | held (CLAIM tag) |
| `kuditipudi2024distortion` | Kuditipudi, Thickstun, Hashimoto, Liang, "Robust distortion-free watermarks for language models", TMLR 2024 | arXiv 2307.15593 | held |
| `aaronson2022lecture` | the Gumbel-max (exponential minimum sampling) watermark | Aaronson's talk / OpenAI; or cite through Kuditipudi et al. and Fernandez et al. | **to settle** |
| `li2025framework` | Li, Ruan, Wang, Long, Su, "A statistical framework of watermarks for large language models: pivot, detection efficiency and optimal rules", Annals of Statistics | arXiv 2404.01245 | held |
| `li2025robust` | Li, Ruan, Wang, Long, Su, "Robust detection of watermarks for large language models under human edits", JRSS-B | arXiv 2411.13868 | held |
| `cai2025collision` | Cai, Li, Long, Su, Wen, "Optimal detection of LLM watermarks with pseudorandom collision" | arXiv 2510.22007 | held |
| `huang2023optimal` | Huang et al., "Towards optimal statistical watermarking" | arXiv 2312.07930 | held |
| `jovanovic2025image` | Jovanović, Labiad, Souček, Vechev, Fernandez, "Watermarking autoregressive image generation", NeurIPS 2025 | arXiv 2506.16349 (p. 27, Eq. 9) | held |
| `gloaguen2026diffusion` | Gloaguen, Staab, Jovanović, Vechev, "Watermarking diffusion language models", ICLR 2026 | arXiv 2509.24368 (App., p. 21, Table 2) | held |
| `gloaguen2026unified` | Gloaguen, Staab, Jovanović, Vechev, "A unified framework for LLM watermarks" | arXiv 2602.06754 (p. 4) | held |
| `gloaguen2026automark` | Gloaguen, Staab, Vechev, "AutoMark: enabling autoresearch to discover better LLM watermarks" | arXiv 2609.37310 (Eq. 2–3 p. 4; Alg. 3 p. 5; Prop. 1 p. 42; App. C) | held |
| `genhatharan2026nominal` | Genhatharan, "When nominal false-positive rates fail: key- and length-dependent null behavior of canonical LLM text watermarks" | GitHub `nisaharan/when-nominal-false-positive-rates-fail`, release v1, 2026-09-11 (a repository release; constraint 15) | held |
| `fernandez2026posthoc` | Fernandez et al., "How good is post-hoc watermarking with language model rephrasing?" | arXiv 2512.16904 (p. 19) | held |
| `sander2026textseal` | Sander et al., "TextSeal" | arXiv 2605.12456 (p. 38) | held |
| `fu2025multiuse` | Fu, Russell, "Multi-use LLM watermarking and the false detection problem" | arXiv 2506.15975 | held |
| `vovk2012conditional` | Vovk, "Conditional validity of inductive conformal predictors", ACML 2012 / PMLR v25 | arXiv 1209.2673 (Prop. 2a–2b pp. 3–6) | held |
| `bian2023training` | Bian, Barber, "Training-conditional coverage for distribution-free predictive inference", EJS 2023 | arXiv 2205.03647 | held |
| `liang2025algorithmic` | Liang, Barber, "Algorithmic stability implies training-conditional coverage for distribution-free prediction methods" | arXiv 2311.04295 | held |
| `ren2022derandomized` | Ren, Barber, "Derandomised knockoffs: leveraging e-values for false discovery rate control" | arXiv 2205.15461 (p. 11) | held |
| `bashari2023derandomized` | Bashari, Epstein, Romano, Sesia, "Derandomized novelty detection with FDR control via conformal e-values", NeurIPS 2023 | arXiv 2302.07294 | held |
| `xie2025classroom` | Xie, Chen, Ren, Su, "Watermark in the classroom" | arXiv 2507.23113 | held |
| `aremu2026activation` | Aremu, Ognev, Poppi, Lukas, "Adaptively robust LLM monitoring via activation watermarking" | arXiv 2603.23171 | held |
| `delbianco2026compliance` | Delbianco, Tohmé, Acciarri, "Watermarking: from impossibility to auditable compliance" | arXiv 2610.06317 | held |
| `openai2026textgrain` | OpenAI, "textGrain: entropy-calibrated watermarking for language model text", technical report, 2026-10-05 | the report (§3.2, p. 6); cite with the date read | held |
| `nemecek2026crosslingual` | Nemecek, Zafar, Ganguly, Singh, Chaudhary, Ayday, "Auditing cross-lingual fairness in language model watermarking" | arXiv 2608.20047 | held (CLAIM) |
| `lichen2026chainmark` | Li-Chen, Kim, "ChainMark: model-free LLM watermarking with closed-form calibration" | arXiv 2607.18445 | held (CLAIM) |
| `ding2026reference` | Ding, Wei, Zhu, Dai, "Reference-null calibrated thresholds for e-processes…" | arXiv 2609.32678 | held (CLAIM) |
| `park2026luna` | Park, Park, An et al., "Linguistics-aware non-distortionary LLM watermarking (LUNA)", EMNLP 2026 | arXiv 2606.00613 | held (CLAIM) |
| `li2026tiwm` | Tung-Ling Li, "Tokenization-invariant watermarking: a byte-local method for LLM text" | arXiv 2610.14378 | held (CLAIM) |
| `wang2026bytemark` | Wang, Li, "ByteMark: a unified byte-level watermark for detection across language models" | arXiv 2610.14427 | held (CLAIM) |
| `bhattacharyya2026textgrain` | Bhattacharyya, Bonnerjee, "textGrain watermarking is harder to detect…" | arXiv 2610.17655 | held (CLAIM) |
| `ma2026predictive` | Li Ma, "Predictive likelihood ratios for language model watermark detection" | arXiv 2609.15657 | held (CLAIM) |
| `wang2026powercalibrated` | Wang, He, Liu, Li, "Beyond heuristic tuning: power-calibrated LLM watermarking", ICML 2026 | arXiv 2607.05694 | held (CLAIM) |
| `khachaturov2025repetition` | Khachaturov, Mullins, Shumailov, Dathathri, "Watermarking needs input repetition masking" | arXiv 2504.12229 | held (CLAIM) |
| `islam2026reliable` | Islam, Uddin, Xiang, "Are LLM watermarks reliable in practice? A systematic review", Computer Science Review 2026 | doi 10.1016/j.cosrev.2026.101074 (record only) | abstract-level |
| `xlr8harder2026synthid` | `xlr8harder/synthid`, "Reproducible SynthID-Text implementation for vLLM…" | GitHub, commit `b3adb0f`, 2026-08-19 (MIT) | held (API read) |
| `dathathri2024synthid` | Dathathri et al., "Scalable watermarking for identifying large language model outputs" (SynthID-Text), Nature 634, 2024 | doi 10.1038/s41586-024-08025-4 | held (main text) |
| `vllm2026watermarking` | vLLM documentation, "Text watermarking" | docs.vllm.ai, read 2026-10-15 (constraint 33: by date read) | held |
| `google2024synthidtext` | Google `synthid-text` README | GitHub, date read | held |
| `ec2026code` | EU Code of Practice on Transparency of AI-Generated Content, final 10 June 2026 (document 129555), Measure 3.2 p. 17 | Commission newsroom document id | held (CLAIM) |
| `ec2026guidelines` | Article 50 Guidelines, C(2026) 5054 final (document 131215), p. 26 | Commission newsroom document id | held (CLAIM) |
| `nist2024ai1004` | NIST AI 100-4, "Reducing risks posed by synthetic content", November 2024, p. 12 | NIST | held |
| `su2026anytime`, `huang2026anytime`, `luo2026anytime` | anytime-valid watermark detection (Su, Wang, Zhao; Huang, Xu, Ramchandran, Jiao, Jordan; Luo et al.) | arXiv 2602.14286; 2602.17608; 2607.21958 | held |
| `li2026forensics` | Li, Gao, Feng, Jiang, Sui, Hu, "Watermark forensics for generative models" | arXiv 2607.13003 | abstract + reviewer's read |
| `lihe2026saccopula`, `globalsketch2026` | SAC-Copula (Li & He); Global sketch | arXiv 2608.20839; 2606.04486 | grep-level |
| `owen1956tables` | Owen, "Tables for computing bivariate normal probabilities", Annals of Mathematical Statistics 27 (1956) | doi 10.1214/aoms/1177728074 | **to settle** (not in the local texts) |
| `hoeffding1963` | Hoeffding, "Probability inequalities for sums of bounded random variables", JASA 58 (1963) | doi 10.1080/01621459.1963.10500830 | **to settle** |
| `kandpal2025commonpile` | Kandpal et al., "The Common Pile v0.1: an 8TB dataset of public domain and openly licensed text", 2025 | arXiv id to confirm (2506.05209?) | **to settle** |
| `wikimedia2023dump` | Wikimedia Foundation, Wikipedia dumps of 2023-11-01 (Hugging Face `wikimedia/wikipedia`, config `20231101.<lang>`) | dataset card, date read | **to settle** |
| `qwen2025technical`, `meta2024llama3` | Qwen2.5 technical report; the Llama 3 herd of models | arXiv 2412.15115; 2407.21783 | **to settle** (only if the models are cited beyond the pinned revisions) |

Added at Milestone 12 (§1–§2 drafts, 2026-10-19):

| Key | Work | Primary identifier | Status |
|---|---|---|---|
| `wu2024collision` | Wu, Chen, Hu et al., "Distortion-free watermarks are not truly distortion-free under watermark key collisions" | arXiv 2406.02603 (abstract read at the claim gate, screen A; "collision" there means key reuse across generations) | abstract-level; cited to keep "collision" distinct |
| `yukhimchuk2026keylottery` | Yukhimchuk, "Key lottery: per-key false positives of LLM text watermarks" (GitHub repository with the proposal "Audit the Deployed Key, Not the Scheme"; an MBZUAI ML8502 course project) | GitHub `katcinskiy/keylottery`, commit `8ebb6b4`, 2026-10-20 (independent concurrent work; the final gate of 2026-10-21; constraints 15, 34, 36) | held |
| `bonet2026llmwatermark` | HugoAlbertBonet, "llmwatermark" (a KGW-style watermarking library whose README measures a per-key offset) | GitHub `HugoAlbertBonet/llmwatermark`, commit `6261c02`, 2026-08-31 (a practice record; constraints 15, 35) | held |
| `zhou2026blade` | Zhou, Zhao, Shen, Pu, "Token-level attribution of multi-mode LLM watermarks: optimal rule and belief weighting" (BLADE) | arXiv 2610.23601 (abstract read at the final gate; the many-key multiplicity effect and its power price) | abstract-level; cited under constraint 3 |

**Settled (Milestone 12, 2026-10-19):** `research/paper/references.bib` is built by `build_references.py` from the primary records saved under `bib_sources/` (the arXiv API by id for 38 e-prints with the version read; Crossref for 14 DOIs; the PMLR pages for ICML 2023 and ACML 2012; TMLR's bib record; the ICLR 2024 paper list and the PDF covers for the ICLR and NeurIPS venues; the GitHub API for the two repository artefacts; the lecture page; the document identifiers and dates read for the regulator and vendor sources; the freeze manifest for the Wikimedia dataset). 50 entries, one per key cited in the sections; the citation-management validator reports 0 errors (7 recommended-field warnings for venues without pages, volumes or DOIs). `aaronson2023gumbel` was renamed `aaronson2022lecture` (the lecture of 2022-11-29); `hoeffding1963`, `meta2024llama3`, `qwen2025technical`, `wang2026powercalibrated`, `bashari2023derandomized` and `google2024synthidtext` are not cited and have no entry.
