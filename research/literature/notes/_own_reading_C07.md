# C07 — my own page-confirmed reading notes (Yichen's session, 2026-10-08)

All quotations are exact substrings of the pdftotext files in `research/literature/txt/` (page = form-feed segment index, 1-based), checked by grep in this session. "Inference" sentences are mine.

## Gloaguen, Staab, Jovanović, Vechev, "Watermarking Diffusion Language Models" (arXiv 2509.24368v3, 17 Sep 2026; "Published as a conference paper at ICLR 2026", p.1)
- p.21 (Table 2 caption): "We compare the maximum FPR@1% (measured on 10000 samples of unwatermarked data over 100 different keys ξ) and the standard deviation of the FPR@1% between Unigram and our approach. We find that the error in FPR@1% of Unigram can be 17 times higher than the expected one, and that the key-to-key standard deviation is on the order of 1%."
- p.21 (Table 2 values): "maxξ FPR@1 17.0% 1.7% 1.1% stdξ FPR@1 1.2% 0.3% 0.1%" for Unigram, Ours (C = {−1}), Ours (C = {−2, −1}).
- p.21 (Fig. 7 caption): "Each line corresponds to a different watermark key ξ. We find that with Unigram (left) the seed-to-seed variation is significant; at α = 1% it spans multiple orders of magnitude. This is not the case for our approach (middle and right), with seed-to-seed variation drastically diminishing as the context size |C| increases."
- p.21: "assumes randomness over the Red/Green list. Yet, the scheme fixes the Red/Green list split, meaning this assumption is violated. This phenomenon has been observed in Jovanović et al. (2025) (Appendix E.2) where, in their specific case, they introduce stratification to mitigate this issue."
- p.22: "hashing to seed the watermark is a good approximation of the Red/Green list randomness assumption".
- The reference "Jovanović et al. (2025)" is, by the bibliography (p.15), "Nikola Jovanović, Ismail Labiad, Tomáš Souček, Martin Vechev, and Pierre Fernandez. Watermarking autoregressive image generation. Advances in Neural Information Processing Systems, 2025." (not Ward, whose App. E.2 is about countermeasures: 2410.03537 p.21.)
- Inference: the per-key dispersion of the false-positive rate is observed and quantified (max and SD over 100 keys) for Unigram against context sizes 1 and 2 in an appendix; its mechanism is named informally ("fixes the Red/Green list split"); no theory of what controls it, no text-length dependence, no per-key remedy beyond "increase context size" (and, in the image paper, stratification).

## Jovanović, Labiad, Souček, Vechev, Fernandez, "Watermarking Autoregressive Image Generation" (arXiv 2506.16349v2, 23 Oct 2025; Meta FAIR, ETH Zurich; NeurIPS 2025 per the ICLR 2026 paper's bibliography)
- p.27: "We see (in red ) that there is in fact only ≈25% chance that the green ratio among alive tokens γ ′ is equal to γ, as the statistical test expects. To resolve this, for Taming we use a stratified split, i.e., we separately sample a red/green split on alive and dead codes, ensuring that γ ′ = γ".
- p.27: "An interesting question, to the best of our knowledge not explored before, is if similar effects can be observed in LLM watermarking. For example, a uniformly random split of a large multilingual vocabulary may introduce a particularly biased split on e.g., Cyrillic tokens, which are effectively the majority of the alive ones when the LLM is prompted to write in a language that uses the Cyrillic script. Especially for h = 0, this may point at unfairness towards certain subdomains, where for a particular subdomain the watermark is overly conservative or more importantly has a much higher FPR than stated theoretically."
- Inference: the question is named as open (October 2025) and framed by subdomain: for a fixed key the realised false-positive rate depends on the text distribution (language, domain), which is exactly the key-conditional validity question with P varying by subpopulation; the remedy they use (a stratified green/red split so that the green fraction is exact within strata) is the image-token analogue of stratifying an LLM vocabulary by token frequency, a variance-reduction idea with a direct theory. Gloaguen et al. (ICLR 2026, above) then measured the effect for Unigram and two context sizes without theory or a remedy beyond context size.

## Fernandez et al., "How good is post-hoc watermarking with language model rephrasing?" (arXiv 2512.16904)
- p.6: the key "that minimizes the deviation from U(0, 1), as measured by the Kolmogorov–Smirnov statistic. Next, we verify that the theoretical FPRs for these keys match the empirical FPRs on 1.5M Wikipedia documents"; "This ensures that the subsequent results under H1 reflect the intrinsic performance of each scheme rather than artifacts of a particular key choice. Further details are provided in Table 6."
- p.19 (Table 6 caption): "Key sensitivity analysis across models and watermarking schemes. We evaluate multiple random keys per configuration on 100 non-watermarked texts." with columns "Aggregated Statistics (All Keys) … Avg. p-val σkeys" and a "Selected “Best” Key".
- Inference: key screening by KS uniformity on null texts is used as experimental hygiene; the across-key spread is tabulated on 100 texts per key; the phenomenon is not the paper's object.

## Fernandez, Chaffin, Tit, Chappelier, Furon, "Three bricks to consolidate watermarks for LLMs" (arXiv 2308.00113)
- p.3 (Fig. 2 caption): "Results are computed over 10 master keys × 100k sequences of 256 tokens sampled from Wikipedia."; p.3: "repeat this with 10 different master keys, which makes 1M".
- Inference: the empirical false-positive check pools ten keys (marginal over keys); per-key variation is not broken out at grep level (full read by a delegated agent pending).

## Aremu, Ognev, Poppi, Lukas, "Adaptively robust LLM monitoring via activation watermarking" (arXiv 2603.23171)
- p.4: "We calibrate τk once per key on held-out benign data, before any attack evaluation, and keep it fixed across all attacks (Section 5.7)."; p.6: "with the threshold calibrated per key on a held-out benign set."
- Inference: per-key null-data calibration is practised in an activation-level scheme, without a stated theory or sample-size rule.

## Li & He, "SAC-Copula" (arXiv 2608.20839v2, 10 Sep 2026)
- p.7: "Threshold portability is nevertheless source-sensitive: Wikipedia-H0 thresholds yield realized FPRs of 6.5% and 21.0% on ELI5 Native at nominal 1% and 5%, respectively, despite strong score discrimination."
- Inference: null-text calibration transfers poorly across corpora; any per-key calibration remedy must state its null-corpus assumption.

## "Global sketch-based watermarking for diffusion language models" (arXiv 2606.04486)
- p.5: "The threshold τN is calibrated under the base model, conditional on the output length, to control the false positive rate."
- Inference: conditioning on length is practised; conditioning on the key is not mentioned at grep level.

## Statistics predecessors on conditional validity
- Vovk 2012, "Conditional validity of inductive conformal predictors" (arXiv 1209.2673), p.2: "Eight notions of conditional validity … U (unconditional), T (training conditional), O (object conditional), L (label conditional)…".
- Bian & Barber 2023, "Training-conditional coverage for distribution-free predictive inference" (arXiv 2205.03647), p.1: "training-conditional coverage is achieved by some methods but is impossible to guarantee without further assumptions for others."; p.2: "might result in 0% training-conditional coverage even though the average coverage is"; p.2: "The variability of training-conditional miscoverage level αP (Dn ) will in general depend on the distribution P , the regression algorithm A".
- Liang & Barber 2025, "Algorithmic stability implies training-conditional coverage for distribution-free prediction methods" (arXiv 2311.04295v3), p.1: "training-conditional coverage is a stronger notion of validity that ensures predictive coverage of the test point for most draws of the training data".
- Inference: the per-key false-positive rate is the exact analogue of training-conditional miscoverage (key ↔ training draw); the stability route (Liang & Barber) is a candidate theoretical tool for per-key concentration; no watermark paper found uses this framing (web search 2026-10-08: no hit for "key-conditional" or "training-conditional" with watermark).

## Delegated-read confirmation (agent notes in this folder)
- 2510.22007, 2404.01245, 2411.13868, 2312.07930: Type I guarantees stated under idealised pseudorandomness, i.e. marginal over the key; one key in experiments; no per-key dispersion or calibration (see each `<id>.md`).
