# R02 — Stage 4 data verdict: independent review, round 3

Date: 2026-10-09. Reviewer: Codex.

## 1. Baseline and scope

Baseline: **main, 90a907cb7176b26705565ca496a45dc36cc9bf90**. At the start, `outputs/study1_v0.1/validation_run.log` already had an unrelated working-tree modification. I did not inspect or change it. HEAD remained at this commit throughout the review.

I read AGENTS.md, the full review orientation, the checkpoint prompt, my round-2 memo and the conductor's round-2 response; CORPORA_AUDIT_v0.3.md, DATA_LAYOUT.md, the v0.3 audit JSON and partition summary, the planted-copy report and D4 additions JSON; all six requested scripts; and the decision-log entry headed “R02 round 2.” I also checked the loader's parser/acceptance inputs, the unchanged loader/freezer code relative to the preceding baseline, the v0.3 counts and digests, the final partition's metadata, the recorded 0.80 scratch-run log, and RESEARCH_HANDOFF.md. The present user request determines the round-3 filename; the older PROMPT.md is historical checkpoint context. Study 1 and its outputs are outside scope.

I ran the requested duplicate test on `outputs/corpora_units_v0.3` and the synthetic seal suite. Additional short checks covered hashes, metadata and JSON arithmetic, synthetic file acceptance/reporting, driver control flow, an actual 60-member candidate bucket, and cell-length boundaries. Temporary synthetic fixtures were removed. No check exceeded one minute; the duplicate test took approximately seven seconds. No full corpus rebuild or actual corpus audit was run. Corpus text was read only by the explicitly requested planted-copy test, whose 18 selected inputs I verified are exposed and open; no held-out text was opened. Only this memo was added. Nothing was committed or downloaded.

**Assessment:** no blocking implementation finding remains. The v3 code implements the corrected candidate/confirmation rule, the seal checks actual cell scope with bound length metadata, and the capacity counts pass. F10/F11's previously untested failure paths also passed bounded independent checks in this review. The repository still lacks the durable tests promised in the response, and some comparison/reporting statements need correction; these are non-blocking follow-ups F14–F16, not grounds to rebuild the otherwise verified map again.

## 2. Claims against evidence

### Disposition of F8–F13 and earlier residuals

| Finding | Disposition | Evidence and residual work |
|---|---|---|
| F8, prefilter and fixture mismatch, blocking | **Resolved** | `candidate_pairs` enumerates all unordered pairs within each band-key bucket into a set. The production loop calls `confirm_pair` for every distinct pair; the estimate only fills the confusion table. The fixture uses those same functions and reproduces its saved output exactly. Prefix candidate limitations and transitive-component limitations are explicit. The old two counterexamples now link as specified. |
| F9, actual cell scope and eligibility binding, major | **Resolved** | Source/language come from the verified final map; reference-tokenizer counts come from metadata verified against the units digest. The registered lock must bind that digest. Each requested ID must match a requested cell and its length requirement; books include the 1,000-token offset. The opening log includes the sorted-ID digest. All 17 supplied seal cases pass; additional boundary checks are described below. |
| F10, acceptance before counting, major | **Implementation resolved; durable tests carried forward** | `file_acceptance` runs before metadata/signature loading and clustering. The audit excludes the recorded rejected files before joining the partition or counting. Independent synthetic checks covered the requested short/malformed/decompression cases and additional rejection paths. The report labels rejected files QUARANTINED rather than the promised EXCLUDED; this is a wording mismatch, not admission of failed units. |
| F11, build control flow, major | **Implementation resolved; durable tests carried forward** | The driver stops on P1/P5/P6 failure, passes the selected directory to expansion loading, refuses an existing version before subprocesses run, and raises a failing exit on a non-PASS final audit. Independent command-capture checks exercised these paths. Both actual existing-version guards refused v0.3 without rebuilding it. |
| F12, misstated D4 basis, major | **Substantially resolved; non-blocking record corrections remain** | The exact-Jaccard ranges, deletion linkage counts and production/fixture correspondence are now correct. The old Stack Exchange-only characterisation is explicitly withdrawn, and the new JSON separates additions by source/language. The prose still confuses added multi-cluster membership with representative loss and overstates metadata-based interpretation; see F14. D4's threshold/bands are not reopened. |
| F13, pointers and overlap wording, minor | **Mostly resolved; minor residue** | DATA_LAYOUT and orientation point to v0.3; the handoff's results paragraph has the correct current counts; the categorical overlap claim is replaced. One handoff pointer and several reporting details remain stale, and the documented audit command writes to the old default output; see F15. |

Earlier residuals **F1/F2/F4/F5** are resolved by the substantive F8–F11 corrections. **F3 and F6 remain resolved**: the loader/freezer did not change, the closed licence mapping and P1 verdict check remain, and capped-prefix eligibility/tokenizer provenance is retained. The v0.3 counts file is byte-identical to v0.2's. **F7** has only the non-blocking record residue noted above.

### Final map, digests and count flow

I independently recomputed both digests, using the recorded file order for the concatenated units files followed by `counts.json`:

- Partition: **`8b9cf24aa9cece47acbc9c8c61f6b9fc0199c06e5f451f8fe9a0b1c28f61feae`**.
- Units metadata: **`911d2a24487b347f0b72fc62ecc3edd0326d546d00f984cf1d0f6f902574cdd9`**.

They match the sidecars and summary; the partition hash also matches the audit. The provisional map used by the duplicate fixture is currently byte-identical to the final map.

Metadata checks reproduce **2,617,347 unique canonical IDs**, **2,610,020 clusters** and exactly one representative per cluster, with the minimum canonical ID as representative and cluster identity. Every partition assignment agrees with the recorded hash/modulo-five rule plus exposure forcing. All **73 exposure hits and 73 forced-open units** are open.

The count flow is **2,617,347 − 230 exact unions − 7,097 near unions = 2,610,020 clusters**. There are **19,060 licence exclusions**, with no overlap between the excluded and non-representative sets in this execution. Thus **2,590,960 allowed representatives = 2,072,900 open + 518,060 held out**. No file was rejected in this actual build; all 13 files reconcile according to their applicable external-count or parse-complete rule.

Comparing the actual v0.2 and v0.3 maps, **two Gutenberg rows change cluster ID and representative status; zero rows change partition**. The additional unions remove two open book representatives. All held-out cell counts remain unchanged; open `gutenberg/en@1024` changes from 12,124 to **12,122**.

### Held-out shares and P7

Recomputed from the summary, before licence/length filtering:

| Source/language | Held out / clusters | Share |
|---|---:|---:|
| news/en | 25,277 / 126,430 | 19.992881% |
| stackexchange/en | 317,144 / 1,586,421 | 19.991162% |
| gutenberg/en | 2,962 / 15,248 | 19.425498% |
| wikipedia/ar | 33,850 / 169,379 | 19.984768% |
| wikipedia/de | 28,564 / 142,213 | 20.085365% |
| wikipedia/en | 31,183 / 155,908 | 20.000898% |
| wikipedia/ja | 18,583 / 92,493 | 20.091250% |
| wikipedia/ru | 18,506 / 92,539 | 19.998055% |
| wikipedia/zh | 45,832 / 229,388 | 19.980121% |
| gutenberg/da, outside target cells | 0 / 1 | 0% |

Overall: **521,901 / 2,610,020 = 19.996054%**. This includes licence-excluded representatives and therefore differs from the allowed held-out total.

The audit's cells, P7 dictionary and reference-tokenizer bins agree:

| Cell | Open eligible | Held out eligible | Held out, also Qwen eligible |
|---|---:|---:|---:|
| news/en @256 | 37,696 | 9,362 | 9,362 |
| wikipedia/en @256 | 95,048 | 23,738 | 23,737 |
| stackexchange/en @256 | 982,015 | 245,245 | 245,238 |
| wikipedia/de @256 | 100,065 | 25,259 | 25,253 |
| wikipedia/ru @256 | 62,249 | 15,500 | 15,500 |
| wikipedia/ar @256 | 85,264 | 21,459 | 21,409 |
| wikipedia/zh @256 | 121,418 | 30,284 | 29,073 |
| wikipedia/ja @256 | 68,208 | 17,165 | 17,143 |
| wikipedia/en @1024 | 36,046 | 8,941 | 8,941 |
| gutenberg/en @1024 | 12,122 | **2,917** | **2,917** |

All ten exceed 2,500, with **417 units of book-cell margin**. P2–P4 also pass, including 28 forum sites with at least 200 eligible open threads. These are checks of the frozen metadata and reported counts, not fresh tokenisation.

### Candidate counts and executed validation

The four confusion entries sum to **73,465 + 8,293 + 11,977 + 3,001,281 = 3,095,016 distinct candidate pairs**. The 20-bin exact-Jaccard histogram has the same sum. The exact-positive entries sum to **85,442**, of which **7,097** union operations join previously separate components. The **5,061,391** bucket-pair occurrences include repeats across bands; they are not distinct pairs. All these quantities agree between the final summary and audit.

Compared with v0.2, the exact-positive count and successful-union count each rise by two. This supports the recorded statement that the removed prefilter had discarded two qualifying candidate edges in this execution. I checked the enumeration/confirmation code and aggregates; I did not rerun full-corpus exact confirmation, whose recorded runtime exceeds the review limit.

The requested `tools/test_dedup.py outputs/corpora_units_v0.3` exited successfully and its complete stdout matched the saved report. The recomputed groups are:

| Variant | Exact-Jaccard range | Links at 0.80/16×8 | Links at 0.70/32×4 | Links at D4 |
|---|---:|---:|---:|---:|
| Exact copy | 1.000 | 18/18 | 18/18 | 18/18 |
| 2% deletion | 0.716–0.917 | 16/18 | 18/18 | 18/18 |
| 5% deletion | 0.585–0.699 | 0/18 | 0/18 | 13/18 |
| First 10% removed | 0.885–0.996 | 13/18 | 16/18 | 16/18 |
| Same-source negative | 0.000–0.008 | 0/18 | 0/18 | 0/18 |

Positive totals are **47/72, 52/72 and 65/72**. Ebook 1's shifted copy, exact 0.996 with estimate 0.422, now links under D4; ar:7's shifted copy also links under the appropriate rules. The 60-variant fixture reports **1,770 candidates, 59 successful unions and one cluster**, hence PASS. Its largest individual bucket is **50**, a test-coverage qualification discussed in F16.

### Seal and failure-path checks

All **17** supplied seal cases pass, including a wrong units digest, wrong requested source and insufficient length. A separate boundary check rejects a 1,255-token book for `gutenberg/en@256`, accepts it at 1,256, and rejects a Danish book for the English cell. The actual allow-list is empty and the actual openings log is absent; successful synthetic openings used separate temporary fixtures.

I checked the two carried-forward areas without changing their implementation:

- **F10:** tiny gzipped fixtures through the actual parser produce rejection for a clean one-record news file, a malformed second line, and a CRC failure after 1,000 valid records. A separate metadata fixture exercises the exact 126,672-versus-126,673 case, malformed input, decompression failure, bad accounting, footer mismatch and a loader-quarantined file. Running the actual partition and audit on three accepted synthetic units plus these six rejected entries succeeds without reading any rejected units/signature file. All six reasons appear in the flow; no rejected unit enters counts; P5 fails as required.
- **F11:** isolated execution of the actual driver's control flow with substituted path reads and command capture stops after the provisional steps on P5 failure; issues zero subprocess commands for an existing final version; raises on a non-PASS final audit; and, for a book count failure followed by passing counts, invokes one freezer step and one loader step with `CORPORA_UNITS_DIR=outputs/corpora_units_v9.9` before finalisation. No subprocess, download or corpus run was performed in this fixture. Separate calls to the real partitioner and driver guards refuse the existing v0.3 map immediately.

These are independent verification results, not a claim that the conductor's promised test files have been added. They remain absent from the repository and should be retained as regressions before scientific use, as already stated in the response.

## 3. Method and statistics

The operative duplicate rule now agrees with the recorded decision: prefix signatures propose candidates, every distinct candidate is confirmed using full normalised-text shingle fingerprints, and qualifying edges form connected components. `candidate_pairs` has no threshold argument or estimate filter; `corpora_partition.py:193–199` uses the estimate only for reporting. A separate synthetic 60-member shared-band bucket returns all **1,770** unordered pairs, including a non-first-member pair with signature agreement below the old cutoff. Direct confirmation checks give Jaccard 2/3 for overlapping test sets and zero for empty sets.

The record correctly distinguishes full-text similarity from the prefix-set similarity entering the ideal LSH coverage formula. It also states that not every pair within a connected component clears the threshold. The use of 64-bit shingle fingerprints is now explicit. None of these checks establishes absence of natural residual duplicates or independence of analysis units.

The 18 negative directions remain nine distinct unordered pairs, not a representative sample of difficult negatives. Planted-copy recovery measures the tested perturbations, not population recall or false-merge prevalence. The P7 precision calculation remains a nominal independent-unit calculation; the later protocols must address the crossed key/document design and multiplicity. This review does not change those scientific choices.

D4's 0.65 threshold and 32×4 bands stand. The new additions JSON sums correctly to **4,899 units**, of which **4,475 are Wikipedia**, with 1,461 involved clusters and no dropped multi-cluster members reported. The scratch-run log records 109,819 candidates, 41,809 exact-positive pairs, 3,189 near unions and 2,613,928 clusters at 0.80/16×8. Those numbers imply **3,908 fewer total representatives** under D4. They do not establish a loss of 4,475 Wikipedia representatives. I did not regenerate the scratch map or independently reconstruct the entire additions set; the JSON's arithmetic and examples were inspected, and its unsupported interpretations are qualified in F14.

## 4. Process and consistency

The v0.1/v0.2 maps and outputs are preserved as superseded records. The v3 final map and units digest identify the reviewed state; no actual partition labels changed relative to v0.2. The requested text-based fixture is restricted to already exposed open units. The synthetic tests require no real held-out access. Nothing in this review authorises a held-out opening, a new scientific analysis, or a change to a locked protocol.

The principal current-state pointers and counts have been updated, and the earlier overstated overlap guarantee is removed. F14/F15 identify remaining documentation corrections. The unrelated Study 1 working-tree change was present before this review and was left alone; I make no claim about scientific use in work outside the inspected Stage 4 materials.

The source set, freeze manifest, licence policy and tokenizer convention are unchanged. Prior raw-byte and terms checks are not repeated here. The licence allow-list verifies declared labels rather than establishing the copyright status of every text. No external access, publication, posting, messaging or visibility change occurred.

## 5. Independent search and limits

I did not repeat the external literature search or fetch new papers/licence pages. This checkpoint concerns implementation and local validation; web availability was not a limitation. No novelty, priority or absence-of-newer-work claim is made. There is no new scientific quotation requiring a PDF-page check.

The evidence here is code inspection, executed exposed/synthetic fixtures, hashes, metadata and arithmetic. It does not measure natural duplicate recall, false-merge prevalence, full-document lengths beyond the token caps or detector-specific tuple similarity. The metadata examples support hypotheses about the additions, not the population-level textual characterisation currently asserted in the memo.

## 6. New findings and recommendations

### F14 — minor: the revised D4 narrative still conflates membership with representative loss and overstates metadata evidence

**Evidence.** Audit §6's comparison paragraph correctly introduces 4,475 Wikipedia units newly belonging to multi-member clusters, then calls this “4,475 fewer Wikipedia representatives.” These are different counts. The recorded strict-rule and D4 cluster totals differ by **3,908 across all sources**; the additions JSON does not supply the per-source representative differences needed for the Wikipedia claim. Its 4,475 is about 0.5035% of the 888,774 Wikipedia input units, not a measured percentage loss of representatives.

Titles, groups and lengths suggest common templates or related works in the displayed examples. They do not establish that additions are predominantly templates, that news pairs are republications, or that their detector-relevant tuple content is nearly identical. In particular, the comparison contains selected examples rather than a documented representative content audit; transitive cluster membership also does not certify every member pair's similarity. The new §6 parenthetical about shifted prefix agreement, “0.14–0.85,” is inaccurate: the report's range is **0.000–0.938**.

**Recommendation.** Preserve the measured additions table, call the textual characterisations metadata-based hypotheses/examples, and avoid detector-level equivalence claims. Report representative loss from counts of representatives under both maps with the denominator specified; until then, omit the unsupported Wikipedia loss. Correct the prefix-agreement range. This does not require changing D4 or rebuilding v0.3, and does not alter the verified cell capacity.

### F15 — minor: the documented re-verification command targets the superseded audit output, with small stale-record residue

**Evidence.** DATA_LAYOUT.md:24 recommends `tools/audit_corpora.py outputs/corpora_units_v0.3 --version 0.3` but omits `--out`. The script's default at `tools/audit_corpora.py:153` is still `outputs/corpora_audit_v0.2.json`; following the instruction would overwrite the superseded audit instead of producing the v0.3 file the text says to compare. I did not execute that command.

RESEARCH_HANDOFF.md's “Where things live” data bullet still calls v0.2 current. The v0.3 audit JSON's P6 fixture-suite note still says 14 cases while the current suite has 17. Audit P5 promises EXCLUDED reporting, but the code and my synthetic run report QUARANTINED, with the correct exclusion reason and zero admitted contribution.

**Recommendation.** Give an explicit, appropriate `--out` in the re-verification command (prefer a separate comparison file when preserving the saved audit), correct the remaining current-version pointer and case-count note, and make the documented rejection label match the implementation. These are record/reproduction fixes; the reviewed v0.3 map and audit counts are not invalidated.

### F16 — minor: preserve the successful failure checks as regressions and exercise the actual large-bucket boundary

**Evidence.** The response accurately says durable F10/F11 fixtures are not yet done. Independent checks in this review passed those paths, but no test file was added under the memo-only constraint. The duplicate fixture's 60 variants produce a largest bucket of **50**, so that fixture does not cross the old `>50` shortcut boundary. Its terminal PASS/FAIL is printed rather than enforced by a failing exit status. The independent 60-member synthetic bucket used here does cross that boundary and passes the production function.

**Recommendation.** Before scientific use, retain the acceptance/reporting and driver command-capture fixtures described in §2. Add a deterministic bucket with more than 50 members and an important non-first-member pair; assert pair coverage and exact-confirmation behavior. Make failed fixture expectations produce a nonzero exit. This is regression protection for corrections already verified here, not an open defect in the current candidate loop or a reason to repeat the full corpus rebuild.

VERDICT: AGREE
