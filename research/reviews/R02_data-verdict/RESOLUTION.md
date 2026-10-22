# R02 data verdict — RESOLUTION

Date: 2026-10-09. Rounds: 3. Reviewer: Codex (OpenAI). Conductor: Claude (Fable 5.1, Anthropic). Final verdict: **AGREE** (`REVIEW_codex_r3.md`, baseline `90a907c`), with three minor follow-ups F14–F16, applied in the resolution commit. Agreed state: procedure v3, the finalised map `outputs/corpora_units_v0.3/partition_v0.3.parquet` (SHA-256 `8b9cf24aa9cece47acbc9c8c61f6b9fc0199c06e5f451f8fe9a0b1c28f61feae`; units digest `911d2a24487b347f0b72fc62ecc3edd0326d546d00f984cf1d0f6f902574cdd9`), audit v0.3 **PASS** (`research/corpora/CORPORA_AUDIT_v0.3.md`; the reviewer independently reproduced both digests, the count flow, the held-out shares, the ten cells and the candidate and union counts).

## What changed because of the review
- **Round 1 (F1–F7):** exact full-text Jaccard confirmation instead of the MinHash estimate; a sealed accessor bound to a finalised, digest-checked map; a closed licence allow-list with P1 in the verdict; quarantine on decompression and accounting failures; a one-shard expansion driver; capped-prefix counts with tokenizer digests; the record synchronised. Decision **D4** (Yichen): exact Jaccard ≥ 0.65 with 32 × 4 candidate bands.
- **Round 2 (F8–F13):** the candidate prefilter removed so that every band-sharing pair is exactly confirmed (3,095,016 pairs; the prefilter had hidden two qualifying edges); the fixture made to call the production functions; the accessor binds the units-metadata digest and checks every requested unit against the lock's cells by bound source, language and length; per-file acceptance before clustering; driver control-flow fixes and no overwrite option; the D4 evidence corrected (ranges and counts restated from the report; the characterisation of the looser rule's additions withdrawn and replaced by a measured, metadata-only comparison); pointers moved to v0.3.
- **Round 3 (F14–F16, minor):** the comparison paragraph now separates multi-cluster membership (4,899 units, 4,475 of them Wikipedia) from representative loss (3,908 across all sources, from the cluster counts) and calls the textual characterisations hypotheses from metadata; the shifted-prefix agreement range corrected to 0.000–0.938; the re-verification command given an explicit output; the audit's default output versioned; the rejection label EXCLUDED in the audit as in the memo; the 17-case note regenerated into the v0.3 audit; regression fixtures added for the acceptance failure paths (`tools/test_acceptance.py`, 13 checks) and the driver's control flow (`tools/test_build_driver.py`, 4 cases); the planted-copy fixture crosses the 50-member bucket boundary with a non-first-member pair and exits non-zero on failure.

## Disputes settled by Yichen
None: no finding was disputed in any round.

## Carried forward
- The planted-copy evidence measures the tested perturbations, not natural near-duplicate recall or false-merge prevalence; the same-source negatives are nine unordered pairs. Stated in the memo; no further action at Stage 4.
- The nominal independent-unit precision of the confirmatory cells is a planning number; each protocol specifies the crossed key-by-document analysis and multiplicity.
- D4 stands as recorded; the corrected evidence is reported to Yichen, who may revisit it.

## Next checkpoint
R03: the Study 1 protocol (theory and simulation; no real text), before its lock.
