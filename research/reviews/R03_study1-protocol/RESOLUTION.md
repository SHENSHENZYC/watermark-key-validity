# R03 — Study 1 protocol before lock — resolution

Date: 2026-10-10. Checkpoint: R03 (the Study 1 protocol, theory and simulation of the across-key dispersion of a red–green watermark test's false-positive rate; no real text). Conductor: Claude (Fable 5.1). Reviewer: Codex. **Verdict: AGREE at round 4** (bounded re-review of the round-3 corrections, by Yichen's decision under rule A7 after three rounds without AGREE). No dispute is open.

## Rounds
| Round | Baseline | Verdict | Findings | Outcome |
|---|---|---|---|---|
| 1 | `d3cd087` | REVISE | F1–F10 (F1, F2, F3, F4, F7 blocking) | Two occupants found (AutoMark; Genhatharan): gate v0.3, decision D5 (continue, re-narrowed). Protocol v0.2: both colourings at g; the conditional-on-texts target; the population estimates without the finite-text floor; lock schema; key namespaces; computed projection |
| 2 | `cb056a8` | REVISE | F11–F16 (F11 blocking) | Protocol v0.3: canonical lock identity and slot-level provenance; the predictor named a common-factor approximation with its assumptions, plus a pairwise Gaussian predictor and heterogeneity diagnostics; zero-variance limits; R2 by Hoeffding's KL bound; R3 by the known-mean estimator with structural zeros; wording and adjacent-work rows |
| 3 | `3cde956` | REVISE | F17–F20 (F17 blocking) | Corrections in place at v0.3: the tolerance-inclusive R3 rule; the two-sided KL bound; closed-form mixture moments; the full law specification bound to the slot; guard fixtures |
| 4 | `eaf3e92` | **AGREE** | F21, F22 (minor, non-blocking) | Implemented before the lock: the two-sided bound field and the quantitative dead-detector condition; no SE override by observed constancy |

Every finding was reproduced by the conductor before any change; every finding was accepted; none was disputed. Decision D5 (Yichen, 2026-10-09) and the A7 decision for a bounded round 4 (Yichen, 2026-10-10) are in `research/DECISION_LOG.md`.

## What the agreed protocol is
`research/STUDY1_PROTOCOL_v0.3.md` (DRAFT until the lock; v0.1 and v0.2 kept; the round-2 and round-3 texts are commits `3cde956` and `eaf3e92`), `research/study1/grid_v0.3.json`, the code `research/study1/s1_core.py`, `s1_run.py`, `s1_analyze.py`, `s1_validate.py`, `tools/key_policy.py`, and the validation record `outputs/study1_v0.3/VALIDATION.json` regenerated after the round-4 cleanups. The reviewer's AGREE is review advice on F17–F20 and the record; it is not an approval to lock or run, which is Yichen's.

## Open items carried forward (non-blocking)
- The common-factor predictor is an approximation whose adequacy R1 measures; the pairwise predictor and the heterogeneity diagnostics are for attribution, suggestive only (round 3, §3).
- R2's KL rule trades power for an exact bound; under-rejection at α = 0.01 is not flaggable at K = 500 (round 4, F21); R3's calibration is heuristic (round 3).
- The projection (1.7 h) is an extrapolation with margin, not a guarantee (rounds 2–4).
- The paper's priority wording: "at least third in line by the retrieved record" (round 2, F16).

## Next
Yichen's "lock and run?". On his word: `outputs/study1_v0.3/PRE_RUN_LOCK.json` with exactly the schema of the protocol's last paragraph (the eight pinned digests, this memo's digest, `approved_by: "Yichen"`, `before_outcomes: true`, `final: false`), committed and pushed before the run; the run in a fresh milestone session; then `s1_analyze.py` with the lock; then the report (checkpoint R04).
