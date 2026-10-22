# R08 — Study 3 report: independent review, round 2

Date: 2026-10-15. Reviewer: Codex (OpenAI). Baseline: `main`, `406d7b5e5e783f2fa494a57bf5dbabadf70585ea`; working tree clean at entry. Round-1 comparison: `4a01cc8bb4c7e76ccc1eba987ef6334b38dcef3d`.

The principal numerical and interpretive corrections are implemented, including all 32 rows of Table 16. The locked record and registered verdicts are unchanged. I recommend another bounded revision: the new claim of byte-identical builds is false, and three small narrative/process residuals remain. No change to the locked protocol, analyzer, predictions, thresholds or counts is needed.

## 1. Baseline and material examined

Read the response's verification table and dispositions, the requested report sections and captions, all Table 16 rows, the builder and template changes since round 1, the dated decision-log correction, the handoff and the review orientation. Read the round-2 prompt and relevant unchanged builder functions. Compared the generated report with its template, values and tables in memory. Inspected the relevant results, pre-lock inputs, threshold arrays, supplementary tables, checks, manifest, lock and Git history.

Only short local checks were run. I did not run the builder, analyzer, grid or validator this round, download anything, access the holdout, or commit. The round-1 analyzer reproduction remains applicable because the analyzer, its inputs and the result bytes are unchanged. This memo is the only repository file written.

## 2. Claims against evidence

### Frozen record and verdicts

- Re-hashed all **20 pinned files** against the lock: no difference. For every pinned path, `git log --oneline 5e44a2e..HEAD -- <path>` is empty. The R07 resolution still matches its review digest. The lock retains `final: false`.
- The requested record paths, also including the stdout and launch logs, have **no commit after `887a2c7`**. All **240 record files** independently match the manifest's individual digests; no inventory change was found.
- Raw results remain **108,011,668 bytes**, SHA-256 `42bb915363fdb373053e722bf8dc463d83e97f1bbe57cbc810af215555032e89`. The gzip remains **19,534,907 bytes**, SHA-256 `c77f38a8545e5d0bd4571916f3b031a1c75ed8b59f270b804b3ce83dd338af5d`; decompression equals the raw bytes.
- Every table row in Tables **1–5** is identical to round 1. T1 remains PASS: 1,600 candidates, 1,494 eligible, 1,474 resolved, 1,471 consistent, 3 inconsistent, 20 unresolved. T2 remains PASS: 879 material, 875 resolved/agreed, 0 disagreed, 4 unresolved. REP remains PASS: 108 checks, 0 gross failures. The corresponding verdict objects in `checks.json` are unchanged.

### Round-1 findings

| Finding | Round-2 verification and disposition |
| --- | --- |
| **F1 — Table 16** | **Resolved.** The builder selects both `tokC` and `tokE`, plus `near_identical` for transfer and `diagonal` for the comparator, and raises before `.iloc[0]` unless each selection has exactly one row (`s3_report.py:826–830`). Independently matched all 32 rendered rows against their complete identities in `results.json`, including both SDs, their ratio, T1 status, both diagonal SDs, both key-means and v: zero differences. The Qwen/distinct/h = 1/conformal@5000/en@1024→en@256 row now displays **0.169/0.176 pp**, mean **0.999%**, as intended. |
| **F2 — population versus measured shares** | **Resolved in the report.** §§5, 6 Q1 and 8 item 3 label the population quantities as the reference law's model quantities. Conformal's measured median **45.6%** is now compared with the finite prediction **47.0%**, with **48.1%** separately labelled as the population reference. Tolerance similarly separates **7.3% measured**, **7.7% finite prediction**, and **4.7% model population share**. Recomputed the unit ranges from the unchanged results; they agree. The blanket sampling-precision assertion is removed. |
| **F3 — remedy comparisons** | **Resolved in the report's numerical comparisons; handoff residual at F11 below.** Recomputed the named h = 1 summaries: pooled SD **0.396939 pp** versus nominal **0.441204 pp** under distinct, and **0.465577** versus **1.363057 pp** under raw. The empirical finite share exceeds β in **4/20 distinct** and **2/20 raw** units, with maxima **6.0%/6.1%**. Independently recovered κ̂ from the committed empirical threshold arrays: distinct **1.792712–2.777527**, median **2.293481**; raw **9.443332–246.380238**, median **25.885972**. The multiplier20 zero claim is now generated: **0/20** distinct units have any key above α. Q4 gives named contrasts and withholds a power ranking. |
| **F4 — calibration resamples and the floor** | **The Table 13 interpretation and §7 correction are resolved; a residual in §6 Q1 remains at F10 below.** The caption, supplement and interpretation distinguish stability of summaries over keys from variability of a fixed key across calibration draws. The reference Beta SDs independently reproduce as **0.140670 pp** at N_cal = 5,000 and **0.314173 pp** at 1,000. The diagonal theory-share range **0.587476–0.671505** supports §7's statement that the finite-text component is substantial but smaller. No empirical per-key variance decomposition is claimed. |
| **F5 — universal and ranked assertions** | **Resolved numerically and substantively.** Independently recovered **13/1,600** rows with R_obs > R_pred, **2 material**, and the consistent T1 rows' minimum theory share **0.753387**. The four unresolved rows' nominal ratios are **1.895226, 1.895226, 1.287127, 1.220362**; their conformal ratios **1.234877, 1.198183, 0.845156, 0.851395**. Each quotient equals R_obs/R_pred to floating-point precision. These ratios are generated into the report; the interpretation acknowledges both terms. Transfer v is described as one component of the predictor, with the residual scales, order index and finite-evaluation term also named. |
| **F6 — zero thresholds** | **Resolved.** Independently counted the committed arrays using the order-index definitions: **960,000 structural abstentions in 960 settings** at α = 0.001, plus **6 positive-index zeros** at j = 1. All six are Gumbel/raw/conformal@1000 on Gutenberg: Llama h = 0: **1**, h = 1: **1**, h = 2: **3**; Qwen h = 1: **1**. The generated count and setting list agree. The suggested numerical cause is explicitly unisolated; Study 4 is told to preserve the thresholds and abstentions. |
| **F7 — captions** | **Resolved for the requested tables and supplements.** Tables 4–16 now identify the key denominator and applicable evaluation-text denominator, aggregation and subset. Table 14 explicitly refers to the unit's N_E, supplied numerically in its row column; Table 11 appropriately uses calibration texts and positive-threshold/fitting-key denominators. The REP, break-even, calibration-bootstrap and crossed-bootstrap supplement headers supply the missing context. |
| **F8 — record and typed zero** | **The named zero and dated corrections are resolved.** Recovered **three** affected evaluation cells: Gutenberg **11**, Arabic Wikipedia **10**, Stack Exchange **2**. The dated log correction acknowledges the earlier two-cell and “halves” errors and identifies the historical commit messages. The handoff's cell count is corrected. The old “no key above α” is replaced with a generated unit count. New literal outcome counts in the replacement prose are noted at F12 below. |

The template, committed `prose_values.json` and `tables.md` reproduce every non-figure byte of the report when assembled in memory; there are no unresolved placeholders. This checks rendering consistency, not just that the response says the edits were made.

### Figures and reproducibility

Figures **1 and 3–6 PNGs are byte-identical** to `4a01cc8`. Their SVGs are not byte-identical: after removing the old creation date and canonicalizing generated element IDs/references, they are identical. Thus their geometry, labels and embedded image payloads are unchanged.

For Figure 2, the normalized SVG trees have the same 3,623 elements. Differences are confined to **320 vertical connector paths' x coordinates** and **640 marker x coordinates**; all connector endpoints retain their y coordinates, and there are no changed text nodes or other attributes. I also viewed the current PNG. This supports the claim that the plotted values and selections are unchanged and only horizontal jitter moved.

The new jitter seed is a stable SHA-256-derived integer. The CSV's gzip timestamp is zero, and its decompressed bytes are identical to round 1. SVG creation dates are removed. These corrections work, but they do **not** establish identical files across builds: randomized SVG IDs and elapsed-time fields remain (F9).

### Decisive source checks

Rechecked the unchanged source qualifications locally. AutoMark, `research/literature/txt/2609.37310.txt`, PDF p.42, Proposition 1: “Let β ∈ (0, 1] and let Pξ be a detector that satisfies Equation (2).” Vovk, `research/literature/txt/1209.2673.txt`, PDF p.2: “generated independently from the same probability distribution”. The revised report preserves the prerequisite and the model qualification; no new theorem or source-priority claim is introduced. The Nemecek attribution and its previously recorded PDF-confirmation gap are unchanged from round 1.

## 3. Method and statistics

This round changes reporting and rendering, not the registered estimand, seed convention, bands, eligibility, materiality, pairing or decision thresholds. The revised §1 correctly characterizes regenerated bootstrap intervals as an independent implementation check on the **same prescribed realization**, not independent draws or coverage validation. The report now distinguishes measured finite-E shares from model population shares and does not infer a guarantee from their comparison.

The Table 13 revision removes the incorrect inference from stable across-key summaries to stable individual keys. Its Beta comparison is explicitly under the reference law. The remaining floor overstatement is local to §6 Q1; it is not a problem in the locked predictor or eligibility calculation. Power, selection of Study 4 settings and paper wording judgments remain outside this review's decisions.

## 4. Process

Pre-registration and the frozen record are intact. The AI/reviewer disclosure and holdout qualification remain. The finite-pool/exclusion sentence now explicitly treats “same law” and “near-identical law” as design labels. No access-policy issue arose; this round used local evidence only.

The dated correction is preferable to rewriting historical commits. However, the current handoff still repeats two claims rejected at round 1, and the new reproducibility assertion is stronger than the implementation supports. Those current summaries should be corrected before they guide the next stage. No full two-build experiment was performed by this reviewer; the in-memory SVG counterexample and elapsed-time assignments suffice to disprove the asserted all-file byte reproducibility.

## 5. Independent search

No new occupant search in this bounded re-review. Web access was not needed for the reporting changes. Round 1's bounded search and its absence-of-evidence qualification stand; this round makes no additional novelty claim.

## 6. Remaining findings

### F9 — major: the new all-file byte-reproducibility claim is still false

**Evidence.** `RESPONSE_claude_r1.md:19` says “two consecutive builds now give byte-identical files”; the new decision-log entry repeats it (`DECISION_LOG.md:502`). The builder removes SVG dates but never sets `svg.hashsalt`. In the installed Matplotlib **3.11.2**, its value is **None**, and `RendererSVG._make_id` uses a fresh `uuid.uuid4()` in that case. A short in-memory probe using the builder's rcParams and `metadata={"Date": None}` saved the same figure twice and produced different SVG bytes and IDs. Fixing the salt in that probe made the two outputs identical. The committed SVG differences likewise include randomized path/clip/image IDs, not just the removed date.

Independently, `s3_report.py:512` and `:1224` put measured `seconds_checks` and `seconds_total` into committed `checks.json`. These remain variable even after fixing SVG IDs. The current values are **48.0/67.9 seconds**. Removing the SVG date, fixing marker jitter and zeroing the gzip timestamp cannot make elapsed time deterministic.

**Recommendation.** Set a stable SVG hash salt in the builder. Keep elapsed times in runtime logging outside the deterministic artifact set, or explicitly define and document their exclusion from a narrower comparison. Then compare two complete builds in separate processes, listing the exact files and any exclusions, and correct the response/log's premature all-file claim. This finding concerns reporting reproducibility, not scientific output drift: the results, thresholds, plotted outcomes and verdicts are unchanged.

### F10 — minor: §6 Q1 retains the floor claim corrected in §7

**Evidence.** `report_prose_v0.1.md:128`, rendered in §6 Q1, still says the seven h = 2 units beyond the break-even grid are “where the finite-text term dominates”. From the pinned `INPUTS.json`, the nominal h = 2/distinct floor contributes **38.24%–68.51%** of predicted variance in those seven units; it is a majority in **4/7**, not all seven. For example, Llama/German Wikipedia is **38.24%** and Llama/English Wikipedia@1024 **39.58%**. Across all 20 h = 2/distinct nominal units its median share is **35.03%**. If the sentence instead refers to the calibrated diagonal at N_cal = 5,000, §7 correctly establishes that the floor is the smaller component there too.

**Recommendation.** Replace this remaining “dominates” with §7's qualified statement that the finite-text component is substantial/comparable, alongside the calibration order-statistic contribution. If a majority claim is useful, generate and state its subset explicitly. Leave the pre-registered calculation unchanged.

### F11 — minor: the current handoff still carries the rejected remedy claims

**Evidence.** The Study 3 “Established results” paragraph at `RESEARCH_HANDOFF.md:40` still says “the empirical multiplier meets β” and “the pooled calibration fixes the mean only”. These are the unqualified claims corrected in the report under F3. The same paragraph describes half the keys above α “by construction”; targeting the mean alone does not force half the keys above it, and the report now gives the measured and finite-reference shares.

**Recommendation.** Align the active handoff with the revised report: empirical shares are at or below β in most units, with the stated exceptions; pooled calibration targets the mean without enforcing per-key control and can reduce absolute SD; the approximately half-above-α behavior is a measured/reference-law summary at named settings. The dated historical correction can remain as history.

### F12 — minor: the replacement prose introduces new typed outcome counts

**Evidence.** The old zero is generated, but the new T2 paragraph at `report_prose_v0.1.md:118` literally says the conformal ratios are “above in two, below in two”. Those two outcome counts are not placeholders, contrary to the report's generation claim and F8's stated lesson. They happen to be correct. The new §7 phrase “a third to two fifths” (`:136`) is also a hand-written numerical summary of the variance shares; the generated theory-share range immediately beside it already supplies the evidence.

**Recommendation.** Generate these numerical summaries, or omit the literal summaries and rely on the generated local ratios and theory-share range. This is a process correction, not an arithmetic error. Settings and design constants need not be treated as outcome counts.

VERDICT: REVISE
