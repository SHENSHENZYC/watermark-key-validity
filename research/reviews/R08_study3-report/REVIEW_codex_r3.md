# R08 — Study 3 report: independent review, round 3

Date: 2026-10-15. Reviewer: Codex (OpenAI). Baseline: `main`, `6a90e4e57024f80565ec3f89af6f943cff4ea256`; working tree clean at entry. Comparison baseline: `406d7b5e5e783f2fa494a57bf5dbabadf70585ea`.

I agree with this bounded re-review of F9–F12. The reproducibility defects identified at round 2 are corrected, the new summaries reproduce, and the handoff agrees with the report. One minor residual in the numerical-generation convention is recorded below; it does not change a number, interpretation or verdict and does not block agreement.

## 1. Baseline and material examined

Read, in the requested order, `RESPONSE_claude_r2.md`; the three revised report passages and Table 16; the builder, template and handoff diffs since `406d7b5`; the decision log's round-2 entry; and the orientation's R08 row. Checked the relevant builder definitions, pinned `INPUTS.json`, results, break-even supplement, generated values and checks, lock, manifest and Git history. The orientation's memo structure and reviewer restrictions remain applicable.

Ran only short read-only computations and in-memory rendering probes. No builder, analyzer, grid or validator was run. No download, holdout access or commit occurred. This memo is the only repository file written. F1–F8 and the protocol design were not reopened.

## 2. Claims against evidence

### F9: reproducibility

The builder now sets `svg.hashsalt` to **`study3_v0.1`** (`s3_report.py:72`), preserves `metadata={"Date": None}`, and retains the SHA-256 jitter seed and gzip `mtime=0`. Both elapsed-time assignments have been removed from `checks.json`; neither `seconds_checks` nor `seconds_total` remains in the source or the saved checks. Timing is printed instead.

Table 16 now iterates over `grid["near_identical_pair"]`, a list, rather than `NEAR`, a set (`s3_report.py:825`). The remaining `NEAR` use is a set-equality classification, not output ordering. Independently constructed the expected nested order from the grid: all **32 rendered rows** match it. Their order and contents are also unchanged from this round's comparison baseline.

I repeated the rendering counterexample as a positive probe in **two separate Python processes**, with `PYTHONHASHSEED=1` and `987654`. Using the builder's actual rcParams, its date-free save options, SHA-derived jitter and grid-list ordering, the processes produced identical SVG, PNG and gzip bytes and identical pair order/jitter values. The probe included line markers, a scatter collection, clipping and an embedded image, exercising the formerly random SVG identifiers. It wrote only to memory.

The response now explicitly reports a complete comparison of **28/28 report-directory files plus the report**, in separate processes with no exclusions, and acknowledges that the earlier claim had checked only one PNG. I confirmed the directory contains 28 files. Against `406d7b5`, only `checks.json`, `prose_values.json` and the six SVGs differ there, exactly as reported. The SVGs are identical after canonicalizing generated IDs and references; their geometry, text and image payloads are unchanged. I did not independently repeat two complete builds: the full-build measurement is the conductor's reported check, supported here by code inspection and the independent process-separated probes. The specific counterexamples from round 2 are resolved.

### F10: the finite-text share at break-even

Independently selected the seven KGW/distinct/h = 2/conformal units marked “never” in the unchanged break-even supplement and joined their identities to the pinned evaluation-set nominal predictions in `INPUTS.json`. Calculated the finite-text share as **1 − theory_share**:

| Quantity | Independent value | Rendered value |
| --- | --- | --- |
| Minimum among the seven units | 0.382408761 | 38.2% |
| Maximum among the seven units | 0.685052275 | 68.5% |
| Units with share strictly above 0.5 | 4 of 7 | “a majority in 4 of them” |
| Median over all 20 h = 2/distinct nominal units | 0.3502708475 | 35.0% |

All agree with the newly generated placeholders. The builder reads the nominal prediction for each evaluation unit; it does not substitute the calibrated diagonal's variance. §6 Q1 now says “comparable with the shift term” and specifies the predicted nominal variance and the two aggregation populations. This resolves the unsupported dominance assertion.

### F11: the handoff

The established-results paragraph now states the empirical multiplier's **measured** share is at or below β in most units, with **4/20 distinct** and **2/20 raw** exceptions at h = 1 and cell-dependent κ̂. It describes pooled calibration as targeting the key-average without per-key control and gives its absolute SD reduction under both rules. Conformal's **45.6% measured** share is compared with **47.0% finite prediction**, while **48.1% population reference** is explicitly a model quantity. The three rejected phrases are absent. These statements agree with the revised report and the values independently checked at round 2.

### F12: generated counts and floor range

Independently counted the four unresolved T2 rows: the nominal SD exceeds its prediction in **4/4**; the conformal SD exceeds its prediction in **2** and is below it in **2**. The three count placeholders and their rendered text agree. The comparison operators are strict, as the wording states.

For the primary diagonal at N_cal = 5,000, the complement of the unchanged theory shares ranges from **0.328494923** to **0.412523732**, rendered **32.8%–41.3%**. The new placeholder agrees; the literal “a third to two fifths” is gone.

Filled the three revised template lines from the committed values in memory: they reproduce the rendered lines exactly. The report differs from `406d7b5` on only these three lines, **948, 958 and 966**. The requested replacements are generated. A scan of the remaining literal numerals identifies the small break-even-value residual in F13 below; grid sizes, thresholds, settings and table references are not counted as empirical outcomes merely because they contain numbers.

### Frozen files, verdicts and figures

- All **20 pinned files** still match their lock hashes, with no per-path commit after `5e44a2e`. All **240 record files** match the manifest's individual digests. The record paths, including the run, stdout and launch logs, have no commit after `887a2c7`. `final: false` remains set.
- Raw results retain SHA-256 `42bb915363fdb373053e722bf8dc463d83e97f1bbe57cbc810af215555032e89`; the gzip retains `c77f38a8545e5d0bd4571916f3b031a1c75ed8b59f270b804b3ce83dd338af5d` and decompresses to the identical raw bytes.
- T1, T2 and REP verdict/count objects in the current checks, round-2 checks and locked results are equal. All three remain PASS; no table row or verdict changed in this round.
- The requested PNG diff is empty. Independently compared all **six PNGs** with the Git baseline: each is byte-identical.

No literature claim changed in these residuals. The source checks and qualifications recorded in earlier R08 memos remain applicable; this round needed no new quotation or derivation from a paper.

## 3. Method and statistics

The new computations summarize existing predictions and classifications. They introduce no selection rule, tolerance, eligibility change, inferential test or new uncertainty claim. The seven-unit floor range and the all-unit median have explicit, different denominators; the former no longer implies that every affected unit has a majority finite-text contribution. The diagonal floor range remains a model decomposition rather than an observed variance decomposition.

The rendering checks concern reproducibility in the existing environment. They neither replace the earlier numerical audit nor claim an independent bootstrap realization. The registered science and Study 4's frozen thresholds are unchanged.

## 4. Process

The revisions stay on the unpinned reporting path. The dated log now acknowledges the earlier overstatement of the two-build comparison, records the set-order discovery and states the scope of the subsequent complete comparison. The response, active handoff and orientation agree about the current round and bounded scope. No pre-registration, access-policy, holdout or disclosure issue was introduced.

The full two-build comparison was not repeated by this reviewer; that distinction is explicit above. No remaining nondeterminism was found in the specific paths reviewed under F9. The single minor generation residual below can be handled on the unpinned path in the resolution, without another scientific computation.

## 5. Independent search

No new literature search was performed: this round is expressly bounded to reporting residuals F9–F12. No new novelty claim is made.

## 6. Findings and disposition

- **F9 — major, resolved:** fixed SVG salt, elapsed times removed from the saved checks, deterministic Table 16 ordering; independent in-memory probes agree across separate processes.
- **F10 — minor, resolved:** the generated nominal floor-share range, majority count and median reproduce from the pinned inputs, with accurate wording.
- **F11 — minor, resolved:** the active handoff now carries the qualified remedy statements.
- **F12 — minor, the requested replacements resolved:** the T2 counts and diagonal floor range are generated and correct. The sentence scan leaves the non-blocking residual below.

### F13 — minor, non-blocking: the break-even sentence retains literal outcome values

**Evidence.** `report_prose_v0.1.md:128` still says the break-even size “is 500 under the raw rule, 500–2,000 under the distinct rule at h = 1”. Here those numbers describe observed break-even results, not merely the grid's permitted settings. They are literal text rather than placeholders. They are correct: the unchanged supplement gives **20/20 raw units at 500**, and distinct gives **6 at 500, 13 at 1,000 and 1 at 2,000**. The new floor summaries in the same sentence are generated correctly.

**Recommendation.** In the unpinned resolution edit, generate these break-even endpoints from the existing break-even block, or replace that clause with a reference to Table 12 while retaining the generated seven-unit statement. This closes the sentence's remaining exception to the report's numerical-generation convention. It is not an error in the results and does not block this bounded agreement.

VERDICT: AGREE
