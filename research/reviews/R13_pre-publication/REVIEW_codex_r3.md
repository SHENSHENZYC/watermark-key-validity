# R13 — pre-publication review, round 3

Reviewer: Codex (OpenAI). Date: 2026-10-22 UTC.

## 1. Baseline and scope

The hand-over baseline is `cb826e60aa4a136d8c890de9a89cf45785fb1d06`. During the review, `git rev-parse HEAD` advanced to `84442b178167241fb2686e19fcb6c05b05dd2b74`. I checked that intervening commit: it changes only the handoff and decision log to record the round-3 hand-over and the wait for this memo. The paper, tools and reviewed evidence are unchanged. The round-2 corrections are `e8ec870`; decision S1 is `c42d3ff28974a2f90a976c9ec2f7ca736662d7c1`.

The snapshot is the sibling `watermark-key-validity` repository at `a6a14999a0ec6edc39492d959e89f76c051342d0`, a single root built from clean source commit `c42d3ff`. Both working trees were clean before this memo. I read the orientation and round-3 prompt, then the requested response, log entries, snapshot builder and package, bibliography builder and records, converter and typeset pages, discussion correction, gate, orientation corrections and dated round-1 response note in the requested order. I also inspected the later hand-over entry, statements, review-count scanner, site and relevant diffs.

Checks were read-only: source and manifest comparisons, Git history and remote-ref inspection, GitHub API reads, JSON comparisons, in-memory conversion and table comparisons, PDF text extraction and visual inspection, and short isolated failure probes. No study, model, download, clone, rebuild of an on-disk artefact, commit, push or release operation was performed. This memo is the only file I wrote.

## 2. Claims against evidence

### Disposition of F9–F13

| Item | Recheck and disposition |
|---|---|
| F9, excluded material in publication history | **Resolved for the inspected package and remote.** Every commit reachable from every local ref is the one root `a6a1499`. Its tree contains neither the claim gate's raw captures nor `bib_sources/raw_responses/`. `git ls-remote origin` returns only `HEAD` and `refs/heads/main`, both at that root. The GitHub branches endpoint returns one branch at that SHA; tags are empty. The new repository is private, with Pages off. F14 concerns the checker's failure handling, not an excluded file found in this history. |
| F10, embedded source text in bibliography records | **Resolved.** The distributed GitHub and Crossref JSON has no `patch` or `abstract` field. Comparing all 23 saved full-response/projection pairs reproduces the declared transformation: twelve GitHub patch fields removed from five records, seven Crossref abstract fields removed, and projection annotations added; other retained fields are unchanged. The notes and fetch log identify the removals. The raw responses are absent from the snapshot's entire reachable history. |
| F11, unidentified rows in second panels | **Resolved.** Each panel repeats a complete, unique identifying prefix, with names in the caption. Every original header, row and cell survives, in order; only those identifying columns are repeated. The requested rendered pages have readable labels and separated columns. Details below. |
| F12, maximum across domains | **Resolved.** The draft, §8 source, open item and PDF page 21 now specify the maximum across the five reference domains, matching `PREREGISTRATION.md` §9 at `8ebb6b4`. The measured screen remains distinct from the proposed predicted-rate audit. |
| F13, inconsistent current-state descriptions | **Substantively resolved.** The response records the actual mixed panel layouts; the orientation distinguishes reproducible TeX/bibliography content from PDF creation metadata; the gate marks the mutual-non-citation assertion as superseded and identifies the 24-key count as the measurement commit's statement. Two small residual record errors are F15. |

### Snapshot contents, history and provenance

The manifest lists 7,665 files, all of whose SHA-256 values match. There are no unexplained missing or extra package files; the manifest itself is additional to its digest list. Its 372 exclusions match the source tree, including 291 raw captures and 23 full bibliography API responses. I independently compared the retained source files against Git blobs at `c42d3ff`, applying the declared substitutions to the 23 generalised files: no unexplained mismatch. The two path-bearing exceptions, `outputs/study2_v0.1/VALIDATION.json` and `outputs/study4_v0.1/model_manifest_qwen2.5-1.5b.json`, remain byte-identical. The generated package files and 18 site files account for the other differences; every site file equals its working-copy counterpart.

The fresh remote has repository ID `1429157364`, created `2026-10-22T02:37:55Z`. The renamed, superseded repository has distinct ID `1428772573` and remains private with Pages off. The preserved bundle has 405,629,806 bytes and SHA-256 `f6e764ae03abc3cccb968452bfe65e2147e17712662e65fec536929432559a42`, matching the log; its advertised heads retain the superseded tip `9731bd1`. Thus the earlier history was preserved privately, while the inspected publication repository starts at the cleared root. This conclusion covers the reachable refs inspected, not a general claim about hosting-provider retention of inaccessible objects.

### Bibliography and rights descriptions

The removed fields contain the reported 57,306 characters of patches and 9,233 characters of Crossref abstracts. The snapshot's projections equal the working projections. The retained arXiv XML contains metadata for 39 e-prints, including their abstracts; arXiv's [API terms](https://info.arxiv.org/help/api/tou.html) and [metadata licence](https://info.arxiv.org/help/license/index.html#metadata-license) explicitly distinguish CC0 metadata from the separately licensed e-prints. The README, `LICENSE-TEXT` and gate §7 now describe the distributed records as metadata/projections and exclude the captured pages, full responses, patches and publisher abstracts. I found no remaining instance of the F10 mismatch between those descriptions and the distributed bytes.

Against the round-2 reviewed bibliography, the only changes to `references.bib` are its build-date header and the lecture entry's read date, from 2026-10-21 to 2026-10-19. The latter agrees with the saved extraction/fetch record and page capture date. It changes an access date, not the source's publication date. The 53 entries otherwise remain unchanged.

### Tables and typesetting

I compared all 41 original tables against their 47 emitted longtables at header and cell level, independently of the converter's coverage assertions. For the six split tables, I also checked the Markdown tables against the agreed reports and reconstructed the original columns from the panels. There were no mismatches across their 221 rows and 4,622 original data cells.

| Table | Original rows × columns | Repeated identifying columns | Columns in panels 1 / 2 | Pages viewed |
|---|---:|---|---:|---|
| D4a | 28 × 20 | Law, Rule, h, L | 18 / 6 | 46, 49 |
| D4b | 39 × 26 | Block, Corpus cell, Tokenizer, Family, Rule, h, L | 18 / 15 | 50, 53 |
| D4c | 23 × 24 | Pair, Tokenizer, Rule, h, N_cal | 17 / 12 | 57, 60 |
| D4d | 5 × 24 | prompt cell, h, rule, source, N_cal | 17 / 12 | 61, 62 |
| D6a | 6 × 16 | prompt cell, rule | 14 / 4 | 63, 64 |
| D13a | 120 × 19 | Class, Rule, h, Method | 18 / 5 | 92, 97 |

Every identifying tuple is unique within its table. Each original non-identifying column appears exactly once, and the identifying columns appear once in each panel. The captions describe those columns correctly. I visually inspected all twelve listed panel-opening pages and C1 on page 38; the prior collision, empty-cell alignment and row-identification problems are repaired. D4b and D13a still require reading across distant panels, but their repeated labels now make that reading unambiguous.

The full TeX document generated in memory equals committed `main.tex` byte for byte, and its per-panel layout record equals `page_count_latex.json`. The PDF has 115 pages, with the main text ending and statements beginning on page 21, references starting on page 22 and appendices on page 27. The stored log has 16 overfull horizontal boxes, maximum 0.19473 pt, no overfull vertical box and no missing-character diagnostic. The tiny remaining widths do not reproduce the earlier table collisions. This is not a claim of PDF byte-reproducibility across builds.

### Statements and site

Before this memo, the review scanner independently returns 12 agreed checkpoints, 37 rounds and 197 findings, with R13 open after two REVISE rounds and thirteen findings. That agrees with the paper's disclosure and open-checkpoint sentence. R13's eventual agreement and resolution must be incorporated through the existing review-count/assembly process before the publication package is finalised; their absence from this pre-verdict snapshot is expected.

The site PDF equals the reviewed LaTeX PDF, SHA-256 `5a50ab9b86ab42a90456b571a929254afb696787e074841e9a50977455d7b16e`. The site's abstract equals the independently rendered filled abstract; its HTML paper equals the current full HTML render; local file and fragment links resolve. The landing page labels itself a pre-publication build. I found no unresolved placeholder or exposed absolute machine path there. Live public-site behaviour was not tested because Pages remains off.

## 3. Method and statistics

These corrections do not change an estimand, data value, locked rule or inferential result. The table comparison preserves the agreed results, including their failures and unresolved cases. No new study calculation is needed to fix a presentation or publication-history defect.

For F12, I re-read the pinned [pre-registration §9](https://github.com/katcinskiy/keylottery/blob/8ebb6b4f52927d0adbe9084d53ba49f3f825d6eb/PREREGISTRATION.md). Its score is `s(k) = max_d zbar_ref(k,d) / sd_k(zbar_ref(.,d))` across five domains, using the distinct rule, with the lowest-scoring fraction retained. The corrected sentence conveys that rule. It leaves the rounded −0.4-point screening cost and [−5.1, 4.2] interval attached to the measured ten-versus-ten-key experiment, with its stated model, prompts, strength and threshold. The 8.7-point masking loss remains a separate experiment. The uncertainty remains too large to resolve the screening cost, and neither comparison ranks this project's remedies. No new overstatement follows from the correction.

The fill/literal check passes with 563 placeholders, none unresolved, and 455 recognised literals, none unallowed; its self-test passes. That check remains syntactic, as disclosed. I did not rerun the locked studies, reopen the earlier derivation reviews or infer a population guarantee from the presentation checks.

## 4. Process and release discipline

The diff contains no change to the four locked protocols, pinned study files, raw study records or agreed reports. The holdout was not accessed. The source commit in the snapshot manifest predates the push/handoff log updates, which is consistent with the clean-source build sequence rather than evidence of an unrecorded paper change.

S1's recorded rename-and-recreate procedure matches the two distinct private repositories and preserved bundle. The former mutual-non-citation statement is visibly superseded, and the response's dated correction preserves the historical record. The remaining discrepancies are limited to F15. The public release, Pages switch, posting date and final read remain Yichen's decisions; agreement at this checkpoint does not perform or authorise those outward actions.

The new response/this memo/resolution and regenerated review counts will require the normal final snapshot update. Check the resulting history and actual remote refs again before release, with F14's error handling corrected or an explicit successful independent remote check recorded. This is package finalisation, not a request to rerun the studies.

## 5. Independent search for occupants or newer work

Web access was available. On 2026-10-22 UTC I ran the bounded queries `"key-conditional" watermark after:2026-10-20`, `"watermark" "per-key calibration" after:2026-10-20`, and `"keylottery" watermark after:2026-10-20`. The returned material supplied no relevant new primary-source lead; much was unrelated, so this is weak search coverage, not evidence of novelty. I separately rechecked the named concurrent project's pinned pre-registration and the official arXiv metadata terms.

This round does not replace the final gate's broader screen or expand its priority claim. The concurrent work remains attributed, and the narrower contribution language accepted in the earlier rounds remains appropriate. I did not bypass an access restriction, download literature or contact an author.

## 6. Findings

### F14 — Minor, non-blocking for the inspected snapshot: remote-read failures do not fail the history check

**Evidence.** In `tools/make_public_snapshot.py:195–204`, a failed or timed-out `git ls-remote origin` is caught and recorded as `remote_refs: {"(not read)": ...}` without adding a problem. The subsequent assertion therefore succeeds when the local tree is clean. In two isolated, read-only probes, I replaced only that subprocess call with respectively `CalledProcessError(128, ...)` and `TimeoutExpired(...)`; both calls returned normally with one local commit and `problems: []`. The `--check-only` caller then has a success path despite having verified no remote ref.

**Inference.** A future release check can appear successful during an authentication or network failure. This is not evidence that the current remote is unsafe: its refs were successfully read and independently checked in this review. That direct evidence is why this finding does not reopen F9 or block agreement on the inspected package.

**Recommendation.** Distinguish an intentional local-only check before a remote is configured from verification of a configured publication remote. For the latter, propagate a read failure or return a failing/incomplete result; do not treat it as a passed release check. Cover both a command error and timeout with small failure probes, and retain the successful remote-ref check before release. No history rewrite is needed for this correction.

### F15 — Minor, non-blocking: two residual record details remain inaccurate

**Evidence.** The R13 scope row in `research/reviews/REVIEW_ORIENTATION.md:96` still identifies snapshot commit `698575e`, although the status paragraph, Stage 9 description, log and actual snapshot now use the fresh-root record. The round-2 corrections paragraph in `research/FINAL_GATE_v0.1.md:147` says the shortest identifying prefixes have “four to seven columns”; D6a uses two (`prompt cell`, `rule`), as the response, converter and captions correctly show.

**Inference.** These are stale summary details, not a remaining table ambiguity or an unknown publication history. The primary evidence and substantive corrections are consistent.

**Recommendation.** Make the orientation's scope row reference the current snapshot/manifest or explicitly label `698575e` as the superseded round-1 snapshot. Change the gate's range to “two to seven columns”, or list the six verified counts. Apply these bounded record corrections with the resolution, preserving dated historical descriptions.

## 7. Decision

F9–F12 are resolved, and F13's substantive corrections are verified. No blocking or major finding remains in the inspected paper and package. F14 and F15 are minor corrections suitable for the resolution and final package update. The full author read and explicit release decision remain outstanding as planned.

VERDICT: AGREE
