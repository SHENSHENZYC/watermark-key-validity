# R04 — Study 1 report — resolution

Date: 2026-10-10. Checkpoint: R04 (Stage 6 exit for Study 1: the locked run, its analysis under the lock, the record and the generated report `research/STUDY1_REPORT_v0.1.md`). Conductor: Claude (Fable 5.1). Reviewer: Codex. **Verdict: AGREE at round 2.** No dispute is open; the three minor round-2 findings are applied in the resolution commit.

## Rounds
| Round | Baseline | Verdict | Findings | Outcome |
|---|---|---|---|---|
| 1 | `58ab64e` | REVISE | F1–F10 (F1–F6 major, F7–F10 minor) | The lock, the record and every rule count reproduced (the analyzer's output byte for byte); the problems were in the interpretation and the presentation. All accepted: R4b's text/code tolerance disclosed (Table 8b); the collision reading corrected (the gate's identity with C_cond = A/B of the scored weights stands; the pre-registered number is refuted as registered); the h ≥ 3 and attribution claims narrowed with both pairwise subsamples and explicit prediction/observation factors; the full diagnostic supplement (212 occurrences over 141 cells); the priority phrase removed and the record named; key-bootstrap intervals and the uncertainty gap stated; a generated process-and-disclosure paragraph; the rendering repaired. Two further corrections of the conductor's own (a wrong σ_δ boundary; a reintroduced figure-title collision) |
| 2 | `712b0c3` | **AGREE** | F11–F13 (minor) | The 212 supplement rows, Table 14, Table 8b and the assembly reproduced; the narrowed interpretation and the attribution accepted. Applied in this commit: the analytic C_0 labelled beside the realised collision and the "C_cond near C_0" reading called retrospective (F11); the longest-length and all-length counts, the two unresolved groups and the σ_δ range's population separated in §§5–6 (F12); an α column in the diagnostic tables and a link to the supplement (F13) |

Every finding was reproduced by the conductor before any change; every finding was accepted; none was disputed; no judgement call was put to Yichen in this checkpoint.

## What the agreed state is
The record of Study 1 under protocol v0.3 (`outputs/study1_v0.3/cells/`, `run.log`, `results.json`, `RUN_MANIFEST.json`; commit `62aa6ea`, unchanged since), the lock (`b994105`, unchanged), and the report generated from them by `research/study1/s1_report.py` from `research/study1/report_prose_v0.1.md`: `research/STUDY1_REPORT_v0.1.md` with `outputs/study1_v0.3/report/` (tables, the three supplements, `checks.json`, `prose_values.json`, five figures). The reviewed state is `712b0c3`; the resolution commit adds the F11–F13 corrections and this memo. The results: R1 PASS (152 of 152 resolved cells consistent; 28 unresolved, all at h = 0), R2 PASS, R3 PASS with the pre-registered "reduction below 1% for V ≥ 10,000" statement refuted (distinct rule at h ≤ 1; up to 28.3%), R4 PASS, R4b reproduced under the locked rule (with the text/code tolerance discrepancy disclosed), R5 PASS. The reviewer's AGREE is review advice on the report and its record; it is not an approval of a Study 2 design or of any population-extreme claim.

## Open items carried forward (non-blocking)
- The paper's theory section must keep three collision quantities distinct: A/B of the scored weights (the fixed-size reduction), the tuple collision C_h, and the between-text collision Ã(h); the refuted numerical statement is reported as refuted, with its retrospective explanation labelled as such (round 1 F2, round 2 F11).
- The deployer's view carries no crossed key-by-text uncertainty for the per-key quantiles or the worst sampled key; any population-extreme inference in the paper needs a separately authorised analysis or a new study (round 1 F7).
- R4b's locked analyzer applies 3·SE + 10⁻⁹ where the protocol's text says 3·SE; disclosed, not repaired; every future protocol states every tolerance its code applies (round 1 F1).
- The interpretation of the h = 0 unresolved cells (one correlated key sample; discreteness and skew of the score) is suggestive, not an attribution; Study 2's design takes it as a hypothesis (round 1 F4).
- Study 2's widths, rules and precision are Yichen's decision after its own power analysis; the report's §6 proposal is a proposal (round 1 F3).
- The full prior-work references of the agreed gate accompany the paper's text wherever the phenomenon or the mechanism is discussed (round 1 F6; gate constraints 1, 3, 11–13, 16).

## Next
Stage 5 for Study 2 (measurement on the frozen corpora), in a new milestone session on Yichen's word; the Study 2 protocol goes through checkpoint R05 before its lock.
