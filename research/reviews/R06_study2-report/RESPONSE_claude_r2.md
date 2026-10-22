# R06 — the conductor's response to round 2

Date: 2026-10-13. Conductor: Claude (Fable 5.1, in Claude Code). Reviewer's memo: `REVIEW_codex_r2.md` (baseline `9db4bd5`; VERDICT: REVISE, bounded to F9–F12; F1, F6, F7, F8 closed; F2, F3, F5 closed except the residuals named in F10 and F11; F4 closed except F9). Every residual was verified against the cells, `results.json` and the builder before anything was changed; every residual is accepted. No locked file, no record file and no verdict changed; the report was regenerated on the unpinned path with every check equal.

## Verification (the conductor's own recomputation, before acting)

| Finding | Alleged fact | Verified |
|---|---|---|
| F9 | the pairwise predictor and the heterogeneity diagnostics of every live cell are not in any supplement (548 selected occurrences over 463 cells) | Confirmed by reading the builder: the diagnostic supplement is built from the non-consistent occurrences only |
| F10 | "the 76 holding chains are where the shift dispersion grew with length" is contradicted by the record; the news h = 4 chains are not floor-dominated; the three failure groups overlap | Confirmed: news/en@256 Qwen2.5 at h = 2 holds with ρ̄ 0.038481 → 0.027369 → 0.025354 (SD 0.7907 → 0.8162 → 0.7870 pp); over the 76 holding chains ρ̄ is non-decreasing in L in 61 and decreases somewhere in 15; the news h = 4 theory shares at L = 64 and 128 are 0.780 and 0.657 (Llama) and 0.877 and 0.806 (Qwen); the groups count 18 + 6 + 2 = 26 memberships over 24 distinct failures, the two news h = 4 chains being in both |
| F11 | Table 5's medians are over resolved cells while the prose says "eligible set"; the comparison of the alternatives mixes sets; "not at all at α = 0.05" overstates a median of 1.08; the H-domain heading generalises | Confirmed: primary median 1.2337 over the 217 eligible against 1.2116 over the 184 resolved; α = 0.001 1.5740 (94) against 1.7220 (60); Gumbel raw/distinct 1.4576 (335) against 1.3300 (195); α = 0.05 1.0781 on both (every eligible cell resolved) |
| F12 | two literal outcome counts in the template; the log's "1.46" | Confirmed: "six eligible cells inconsistent and 33 unresolved" (§6) and "six inconsistent and 33 unresolved" (§8) were typed; the squared resolved median is 1.4681, printed as 1.47 in the report, and the round-1 log entry typed 1.46 |

## Dispositions

| Finding | Disposition | Action |
|---|---|---|
| F9 (major, residual of F4) | accepted and fixed | `tables_pairwise_full.md`: every live cell × α (10,404 rows over 3,468 cells; the coverage is asserted against the inventory in the builder, which refuses to write otherwise): the observed SD, the common-factor SD and ratio, the pairwise SD and its replicate with both ratios and the subsampling difference, the simulated-shift SD and ratio, the subsample size, the pair-covariance mean and CV (subsample 1 and the replicate), the pair-correlation quantiles and maximum, the zero-variance share, the theory share, σ² from the identities and observed. Linked from §2's diagnostics paragraph with its row and cell counts registered, and listed in the header; the 548-row selected-occurrence supplement stays |
| F10 (major, residual of F5) | accepted and fixed | §6 Q3: "the [[s4_holding]] holding chains satisfy the observed-SD tolerance; that is the registered statement and no more", with the registered counts (ρ̄ non-decreasing in 61 of 76, decreasing somewhere in 15) and the news/Qwen h = 2 example; the three failure groups stated as overlapping with their 26 memberships over 24 distinct chains, in §5 (b) and §6; the floor account restricted to the 16 non-news h = 4 chains and worded as the predictor's own decomposition ("an approximation, not an identified decomposition of the observed variance"), with the two news h = 4 chains named as not covered (theory shares 0.780 and 0.657; 0.877 and 0.806) |
| F11 (minor, residual of F2/F3) | accepted and fixed | Every block's median in §5 is now stated as the resolved subset's with the eligible-set median in parentheses (new registered values `*_ratio_median_eligible`); the alternatives are compared with the common-factor eligible median (1.23) over the eligible cells and, on the 184 resolved cells, all three on the same set (common-factor 1.21, pairwise and simulated shift as registered); "absent at α = 0.05" and "not at all" replaced by "a smaller discrepancy (median 1.08; every resolved cell consistent)" in §5's title and body, §6 Q2 and §8; the H-domain heading made neutral ("the cross-language correlations depend on the tokenizer and on the pair") |
| F12 (minor) | accepted and fixed | The two literal counts replaced by `[[s1_inconsistent]]` and `[[s1_unresolved]]` (no literal outcome count remains in §§5–8: checked by grep); the round-1 decision-log value 1.46 corrected to the report's 1.47 in a dated correction line of the round-2 entry (the round-1 entry is left as written and the correction is logged beside it) |

## Also applied (from the body of the memo)

- The overlap script's JSON label "equal within 1e-9 relative" now reads "equal within an absolute 1e-9 · max(1, A)", which is the guard the code applies; the script was rerun (every value unchanged except the written time).

## What did not change

The locked protocol, the lock, the fifteen pinned files, the cells, the cost records, the run log, `results.json`, `RUN_MANIFEST.json`; the five registered verdicts; the six figures (the PNGs byte-identical; the SVGs differ by matplotlib's date and element ids only). `report/checks.json`: every re-computation equal.

## For Yichen

No judgement call was needed; each residual is a missing registered output, a sentence that outran the record, a mislabelled denominator or a typed number. The wording judgements for after the review stay in the report's §8.
