# R01 topic lock and data plan — RESOLUTION

Date: 2026-10-09. Rounds: 3. Reviewer: Codex (OpenAI). Conductor: Claude (Fable 5.1, Anthropic). Final verdict: **AGREE** (`REVIEW_codex_r3.md`, baseline `9b40343`), with three non-blocking follow-ups F20–F22. Agreed state: commit `9b40343` as reviewed, plus the F20–F22 textual edits applied in the resolution commit named in the decision log.

## What changed because of the review
- **Positioning (D1, Yichen):** the contribution is an adequacy check plus a transfer plus a small method; a theorem is claimed only if the gate's T1 or T2 is proved; T3 is an empirical adequacy criterion. The "closed-form dispersion law" of v0.1 is withdrawn.
- **Gate v0.2** (v0.1 kept): the derivation rewritten as exact identities (the fixed-size split's across-key variance with g = m/V, C_cond = A/B and the exact ratio; the occupancy weights of each retention rule; the level approximation with its conditions; the signed-weight transfer variance that controls the difference of means only, with the reviewer's counterexample recorded) and hypotheses H-length, H-width, H-domain, H-transfer with stated conditions; three competitor rows added (textGrain 2026-10-05; Delbianco et al. 2610.06317; Gloaguen et al. 2602.06754) and three corrected (Jovanović's Eq. 9; Fernandez's Table 6; Vovk pp.3–6); wording constraints 8–12; "first" → "earliest located".
- **Brief:** the one-sentence question and the target with its conditioning set; comparators' guarantees by method; the narrowed Stage 5 plan; the compute note labelled as a downrating with the null side untimed.
- **Data (D2, Yichen):** the source set is the Common Pile's news, Stack Exchange threads and Project Gutenberg books (per-document CC BY, CC BY-SA, Public Domain) plus Wikipedia 20231101 in six languages; no C4 (database licence, content unresolved), no WikiText-103, no HC3; no exception to the brief's rule. Formats and pinned paths corrected (Dolma gzipped JSON lines; Parquet for Wikipedia); the census records partial viewer counts.
- **Holdout (D3, Yichen):** a sealed 20% of cluster units in every source and language after cross-source exact and near-duplicate clustering, assigned by a hash of the cluster identifier, with the exposure record's clusters forced open, reserved confirmatory keys, a lock-bound seal with logged openings, a provisional expansion loop and quarantine of later cross-partition links.
- **Proceed rule:** P1–P8 on open, deduplicated, eligible units; a normalised licence allow-list; ten target confirmatory cells with a binding floor and explicit exclusion on failure; a capped expansion order with a FAIL outcome.
- **Terms:** rows for the three Common Pile sources; the superseded sources marked.
- **Record:** six conductor errors logged as corrections (the v0.1 novelty wording; the derivation; the C4 count; the key-overfitting remark; the unlabelled compute downrating; the compute-log statement in the round-1 response).

## Disputes settled by Yichen
None: no finding was disputed in any round.

## Carried forward (not blocking)
- **F20** (applied textually in the gate; re-checked at the Study 1 protocol review): the support-size saturation formula holds for the all-distinct-token rule with a common covered support; the context-only rule's limit goes through its occupancy weights; conditioning on M_L > 0 explicit.
- **F21** (written into the audit §5; implemented and tested in the loader before any scientific use; verified at the data-audit checkpoint): the provisional clustering/count/expansion loop; shingle segmentation for scripts without whitespace; empty-shingle and identifier-tie rules; the approximate coverage of LSH stated as a limitation and validated on planted duplicates; exposure identifiers resolved on `metadata.provenance` and `metadata.url`.
- **F22** (applied): the orientation's guarantee and null-law wording; two "first" phrases; "poor power"; "only through transfer"; "frozen" for "selected"; the book-vintage shorthand.
- Standing items from the gate: the Stage 5 timing of the actual hash-and-count implementation before any lock; the paced pre-lock arXiv re-screen; the SynthID Supplement if obtainable.

## Next checkpoint
R02: the data verdict (Stage 4 exit: freeze manifest, loader with the seal, audit with the count flow and the P7 cells), merged with the Study 1 protocol review if both are ready together (Yichen decides the merge).
