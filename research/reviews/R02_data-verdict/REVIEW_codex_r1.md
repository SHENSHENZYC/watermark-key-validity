# R02 — Stage 4 data verdict: independent review, round 1

Date: 2026-10-09. Reviewer: Codex.

## 1. Baseline and scope

Baseline: **main, 129e367fd0d34de88974e28db8f2c881180cb4e6**. The working tree was clean when this review began.

I read AGENTS.md, the full review orientation and the R02 prompt; then the requested audit, DATA_LAYOUT.md, manifest, loader counts, partition summary, audit JSON, both exposure files, planted-duplicate report, all six named scripts, terms check and the two named decision-log entries. I also checked RESEARCH_HANDOFF.md, the relevant F20–F22 corrections in KEYCOND_GATE_v0.2.md and the prior review, the run logs, tracked-output inventory and ignore rules. Study 1 design notes, protocols and scientific results were not reviewed.

Independent checks used short, read-only computations: all 17 local file sizes and SHA-256 hashes; Wikipedia Parquet footers; the per-unit metadata and partition; signature-file headers and row indices; JSON arithmetic; and synthetic, in-memory examples for the candidate-comparison loop, licence normalisation and access function. No corpus text was displayed or scored, no held-out text was opened, and no full loader, partitioner or audit was rerun. The synthetic access check used a fabricated stream, never a corpus file. No downloads, commits or other file changes were made.

**Assessment:** the frozen bytes and reported numerical counts check out. They support the capacity part of PASS. The duplicate rule and seal do not yet support the stronger claim that the agreed Stage 4 procedure has passed. F1 and F2 are blocking; the remaining findings distinguish current observations from failure paths that were not exercised.

## 2. Claims against evidence

### Freeze, reconciliation and count flow

The manifest contains 13 data files and four README files, totalling **7,293,594,148 bytes**, all marked OK. I recomputed every local digest and size: all match the manifest, and all 13 data-file digests also match their recorded Hub LFS SHA-256. The four READMEs have no Hub LFS digest; the assertion in audit §6 that *every* file has that independent comparison is too broad.

The recorded physical-line/row and parsed-record totals are both **2,617,347**, with zero unparseable entries. Every file satisfies physical = parsed + unparseable. News reconciles to **126,673**, the card count recorded in the census and audit. The six actual Wikipedia footers independently give ar 174,172; de 142,266; en 156,289; ja 92,632; ru 92,623; zh 230,792, matching the loader and audit. Stack Exchange and Gutenberg are partial shard selections: their checks establish successful parsing, not equality to an independently published per-shard count.

The numerical flow is:

- 2,617,347 parsed units minus 230 exact-duplicate unions and 3,416 near-duplicate unions = **2,613,701 representatives**.
- Subtract 19,060 licence-excluded representatives = **2,594,641 allowed representatives**.
- These split into **2,075,866 open** and **518,775 held out**.

I checked that the licence-excluded and non-representative sets do not overlap in this execution; therefore the subtraction above is valid here. In general those two exclusion columns need an intersection or sequential definition before treating them as additive.

### Held-out shares

Recomputed from partition_summary.json, counting all representatives before the licence filter:

| Source/language | Held out / clusters | Share |
|---|---:|---:|
| News/en | 25,291 / 126,524 | 19.989% |
| Stack Exchange/en | 317,167 / 1,586,565 | 19.991% |
| Gutenberg/en | 2,963 / 15,247 | 19.433% |
| Wikipedia/ar | 34,252 / 171,470 | 19.976% |
| Wikipedia/de | 28,568 / 142,239 | 20.085% |
| Wikipedia/en | 31,221 / 156,098 | 20.001% |
| Wikipedia/ja | 18,608 / 92,617 | 20.091% |
| Wikipedia/ru | 18,528 / 92,609 | 20.007% |
| Wikipedia/zh | 46,018 / 230,331 | 19.979% |
| Gutenberg/da, outside target cells | 0 / 1 | 0% |

Overall: **522,616 / 2,613,701 = 19.995248%**. The audit's “19.4–20.1% by source and language” describes the intended source/language cells, with the Danish singleton excluded. These counts must not be confused with eligible or licence-filtered counts; for example, allowed Stack Exchange held-out representatives number 313,326.

### P7 cells and the Gutenberg floor

Every open/held-out Llama count below agrees with bins_by_source_lang. I also independently reconstructed all four counts per cell—open Llama, open intersection, held-out Llama and held-out intersection—from the per-unit metadata joined to the partition. All agree with the JSON.

| Cell | Open, Llama eligible | Held out, Llama eligible | Held out, also Qwen eligible |
|---|---:|---:|---:|
| news/en @256 | 37,736 | 9,366 | 9,366 |
| wikipedia/en @256 | 95,108 | 23,754 | 23,753 |
| stackexchange/en @256 | 982,116 | 245,263 | 245,256 |
| wikipedia/de @256 | 100,067 | 25,259 | 25,253 |
| wikipedia/ru @256 | 62,260 | 15,505 | 15,505 |
| wikipedia/ar @256 | 85,329 | 21,475 | 21,425 |
| wikipedia/zh @256 | 121,528 | 30,316 | 29,105 |
| wikipedia/ja @256 | 68,217 | 17,166 | 17,144 |
| wikipedia/en @1024 | 36,073 | 8,946 | 8,946 |
| gutenberg/en @1024 | 12,120 | **2,917** | **2,917** |

Thus all ten current cells exceed 2,500, including the tokenizer intersection. Gutenberg has **417 units of margin**, or 16.68% above the floor. Its 2,963 held-out English representatives include 46 that fail the 2,024-token eligibility requirement. The 2,917 count is therefore the relevant number, not the unfiltered book total. Revised clustering must reproduce the capacity check; this margin is not permission to assume it will survive unchanged.

### Exposure and mechanical partition checks

The original exposure record contains 30 news entries, ten books, one thread and one Japanese Wikipedia article: 42 units. The format inspection adds 39 entries, eight already among those 42. Hence **42 + 39 − 8 = 73**. Equivalently, the consolidated file contains news 30 + books 19 + threads 6 + Wikipedia 18 = 73. All 39 inspection entries are covered.

The actual partition contains exactly those source-level exposure counts. They force 74 units open: 20 books and the other 54 units. The forced-open mask equals membership in an exposure-containing cluster, and no exposed or forced-open unit is held out.

News is matched on metadata.provenance, as required. Books are actually matched on rec_id, whereas §5.4 promises matching on metadata.url. I checked the per-unit metadata: all 19 selected book IDs have the corresponding canonical Gutenberg ebook URL. The discrepancy did not miss an exposure in this execution, but the documentation and matching method should agree.

Additional independent metadata checks found:

- No duplicate canonical IDs among the 2,617,347 units.
- Exactly 2,613,701 distinct cluster IDs and that many representative rows, with no duplicate representative cluster IDs.
- Every representative's canonical ID equals its cluster ID; no member has an ID smaller than its cluster ID.
- Every unit's stored partition agrees with the specified SHA-256/modulo-five rule plus exposure forcing.
- For all 13 files, sig_file matches the expected signature stem, the array has the recorded number of rows and 128 columns, nonnegative sig_row values enumerate those rows in order, and negative indices coincide with empty shingle sets.

This supports the corrected signature-offset mapping and the representative/assignment implementation. It does not validate the near-duplicate edge predicate itself.

## 3. Method and statistics

### Rules P1–P8

| Rule | Assessment of this execution and its implementation |
|---|---|
| P1 | Observed allowed labels map to the intended identities; the 19,060 unlabelled-component threads are excluded; every admitted book is labelled Public Domain; Wikipedia's inherited licence is recorded. However, the implementation is a permissive label parser rather than the promised enumeration of exact labels, and the audit hard-codes P1 true. See F3. |
| P2–P4 | The audit correctly filters allowed representatives in the open partition, uses Llama eligibility, requires the book offset of 1,000 tokens, and reports the Qwen intersection. All numerical floors pass; 28 of 35 eligible forum sites exceed 200 threads. This conclusion is conditional on the current clusters and the documented prefix-token eligibility convention. |
| P5 | Actual frozen-byte and count reconciliations pass. The code does not fully implement the required treatment of failed files; in particular, the news branch can overlook a recorded decompression failure. See F4. |
| P6 | The reported pre-seal computations are permitted preprocessing, and the recorded three negative seal tests pass. They are insufficient to establish the promised seal. See F2. |
| P7 | The code names all ten cells, applies the 2,500 floor to the reference-tokenizer counts and lists failed/excluded cells; none currently fail. A reduced-scope PARTIAL outcome is distinguishable from full PASS. |
| P8 | The source lists and their order/caps are correct. No expansion was needed. The described one-shard-at-a-time provisional loop and final-map lifecycle are not implemented by the supplied scripts. See F5. |

### Near-duplicate validation and recommendation

The report has 18 originals from nine source/language strata, with two perturbations per original. I recounted **13/18 links at the 2% deletion setting and 0/18 at 5%**. All 18 of the 2% copies share a band; the five misses at that setting come from the estimated-similarity threshold. At 5%, only seven share a band, and none passes that threshold. The experiment tests random deletions, not general rewriting; a 5% deletion copy still retains roughly 95% of the original deletion units.

Three distinct issues must not be conflated:

1. For ideal MinHash rows, 16×8 LSH proposes a pair with true shingle Jaccard 0.8 with probability 1 − (1 − 0.8^8)^16 = **0.9470488**. This is candidate coverage, not final linkage coverage or the probability that the corpus is leakage-free.
2. The implementation additionally thresholds the same 128-row estimate. At true Jaccard 0.8, an ideal independent-row calculation gives Pr[Binomial(128, 0.8) ≥ 103] = **0.500055** before considering the candidate condition. This illustrates the loss from substituting an estimate for exact confirmation; it is not a measured error rate for this particular hash family.
3. A genuinely sub-0.8 pair may appropriately fail the agreed exact threshold. Because the validation reports no exact Jaccard values, its five 2% misses cannot be classified as estimator errors versus below-threshold pairs. Nor does the experiment estimate natural leakage prevalence.

**Recommendation to Yichen:** before scientific use, broaden the validation and adopt a looser, explicitly agreed near-copy rule if the final holdout is intended to exclude lightly edited versions of development texts. My preference is broader protection against such copies. Evaluate exact thresholds around **0.65–0.70**, with candidate settings appropriate to that range, on exposed/open or wholly synthetic fixtures before choosing the final rule. Lowering the final threshold alone is insufficient: ideal candidate coverage at J = 0.70 is only 61.3% under 16×8, versus 99.985% under 32×4; at J = 0.65 it is 40.4% versus 99.815%.

Those are candidate configurations, not a new protocol or an instruction to silently replace the agreed 0.8 rule. Include exact copies, controlled 2% and 5% changes, shifted prefixes, same-template/different-content negatives and the scripts actually present. Report exact similarity, candidate recovery and final linkage separately. Check candidate cost and component growth before a full rebuild.

The trade-off is real: lower thresholds and transitive closure can merge distinct templated articles, short stubs or threads, reducing coverage and potentially the book-cell margin. Tighter rules preserve distinct units but leave edited copies across partitions, weakening the interpretation of an untouched confirmation sample and the independent-unit precision calculation. The present small planted-copy check establishes neither a small natural leakage rate nor an excessive false-merge rate. I would not accept it as sufficient support for “overlap ... is enforced away” (audit §3). If Yichen retains a near-verbatim-only policy, record that decision and restrict the independence/overlap claims accordingly. The concrete implementation divergences in F1 still need resolution either way.

At a true rate of 1%, N = 2,500 gives binomial standard error 0.001990, or 0.199 percentage points and 19.9% relative error. The memo correctly labels this nominal and conditional on independent units. It is not a familywise guarantee across cells or keys, nor evidence that 2,500 possibly related texts yield that effective precision. Those inferential choices belong to the later protocols.

### Unexpected observations

The metadata supports the 19,060 Stack Exchange exclusions and the reported leading sites (askubuntu 8,017; apple 2,870; academia 2,143). The stored unlabelled component appears as OTHER:None; it is excluded. This is the conservative outcome required by the existing rule, not grounds to recover those threads by an exception.

The Danish book, ebook 29124, is an allowed open representative but lies outside gutenberg/en, so it contributes to none of the mandatory book-cell counts. That is correctly handled by the audit. Future selection code must retain the language filter; “not used” is not an accessor-level exclusion.

I reproduced the overall Llama medians: news 111 tokens, forum 470, Wikipedia 682, books 5,802. News has a median of 497 characters, and only 37,736 of 101,233 open representatives reach 256 tokens. Thus the news cell represents the length-eligible subset of these frozen outlets. It does not support a claim about typical news articles or arbitrary longer-length comparisons.

Books have **14,384/15,300 = 94.013%** censored counts. Censoring is properly flagged; 5,802 is the median prefix count, not the median whole-book length. All censored books exceed the 2,024-token requirement used by P7, so this observation does not threaten the 2,917 floor. However, two open representative books have capped Llama counts 2,930 and 2,634 despite text lengths of 585,527 and 1,472,520 characters. They fail the 3,048-token test used for the 2,048-token book window. Their true full-text eligibility was not determined. The claim that censoring simply establishes “≥ 3,048” for the books is therefore too broad; see F6.

## 4. Process and consistency

The available code and records show parsing, licence/language labelling, length tokenisation, duplicate preprocessing, exposure inspection, one open seal-test read and planted-copy validation using exposed open units. I found no corpus detector scores, empirical occupancy/collision estimates or calibration outputs among the reviewed Stage 4 artefacts. The validation is an additional reuse of already exposed text, consistent with the permitted preprocessing. The audit's open test reads the already exposed first news article.

This supports, but cannot prove exhaustively, the claim of no scientific use before the partition was fixed. Source inspection and an absent openings log cannot establish that no other process read a raw file. I did not treat the seal as operating-system access control or require such control; F2 concerns the sanctioned API's own claimed checks.

Neither corpora_seal_allowlist.json nor holdout_openings.jsonl exists on disk at this baseline. A missing allow-list is treated as an empty list, so it denies registered-lock access safely; an absent openings log is consistent with no successful sanctioned opening. DATA_LAYOUT.md nevertheless describes these as existing tracked artefacts and should distinguish an absent, deny-all default from an existing empty file.

The terms check precedes the freeze in the recorded sequence. All selected sources are covered, and the cards' licence-misassignment caveat is preserved. This review verifies application of the declared allow-list; it does not independently establish the underlying copyright status of every document. Current raw data and derived arrays are ignored. The decision log records the signature-array commit/push correction; the current tracked inventory excludes them.

F20 is applied in gate v0.2: the support-size formula is restricted to the all-distinct-token rule with a common covered support, the context-only counterexample is retained and conditioning on M_L > 0 is explicit. I found no reason in this checkpoint to reopen that mathematical correction. F21 is partly implemented: identifiers, representatives, hash assignment, exposure forcing, CJK/empty handling and signature indexing have supporting evidence; the duplicate predicate, final-map lifecycle and seal remain incomplete. F22's substantive wording corrections are largely present, but current-state summaries still need the cleanup in F7.

## 5. Independent search and limits of this review

This round checks an executed data procedure, not a new theorem, priority claim or protocol. I did not repeat R01's external literature search or fetch new papers or licence pages. Web access was not the limiting factor; keeping the review within the requested Stage 4 scope was. No absence of newer work is asserted. The pre-lock literature re-screen remains a later checkpoint obligation.

The independent evidence here is the local byte, footer, metadata, arithmetic and synthetic-code checks described above. Natural near-duplicate recall, false-merge prevalence, full-text token lengths for censored records and the complete history of unsanctioned access were not established.

## 6. Findings and recommendations

### F1 — BLOCKING: the implemented duplicate predicate differs materially from the agreed rule

**Evidence.** Audit §5.2 says candidate pairs are “confirmed at Jaccard ≥ 0.8.” In corpora_partition.py:72–100 they are confirmed by equality of MinHash rows, with no exact shingle-set comparison. corpora_loader.py:24,66–79 shingles only the first 20,000 normalised characters for words or 8,000 for character shingles; these prefix limits are absent from the agreed §5 definition. The full-text exact hash does not repair approximate false merges or missed near-copy edges caused by that change of comparison domain.

For buckets above 50, the partitioner compares every member only with the first member. That is a star, not a computation of all qualifying candidate edges. In an in-memory fixture run through the actual loop, a 52-member bucket contained two signatures with **111/128 = 0.8671875** equality and one shared band, but they were not joined because neither matched the first member. The run reports 52 large-bucket occurrences where this shortcut was used; I did not infer how many actual edges it missed.

**Implication.** The published cluster counts describe a different procedure. The 0.947 candidate-coverage formula does not cover estimator thresholding, prefix truncation or this bucket shortcut. Zero discovered cross-source clusters does not prove absence of cross-source overlap.

**Recommendation.** Implement exact confirmation on the agreed shingle domain, or explicitly submit a revised domain/predicate for Yichen's decision before use. Process qualifying candidate pairs/components without the first-member shortcut discarding valid edges. Validate the corrected procedure with exact-similarity and large-bucket fixtures, make the near-copy policy decision described in §3, then rebuild/version the partition and audit before scientific use. Preserve the current outputs as the superseded implementation record; do not relabel them as results of the corrected rule.

### F2 — BLOCKING: the seal trusts caller labels and does not bind the frozen partition

**Evidence.** corpora_access.py:25–27 returns immediately for every partition name other than “holdout”. Lines 56–60 compare the caller's rows.partition only with the caller's partition argument. The accessor never resolves file/position/canonical ID against the saved partition map. A stale or relabelled row supplied as “open” passes those checks and is read without a lock or opening log; an unrecognised partition name can pass too. The in-memory fixture confirmed the latter acceptance without touching any real text.

The registered lock checks bind only the raw-file manifest, while corpora_partition.py:135 can overwrite partition.parquet without changing that manifest. The same lock can therefore outlive a different assignment. check_seal also does not require a study name or cells: it logs j.get("study") and caller-supplied cells, possibly null. The audit's three negative tests use intact labels and miss these cases.

**Recommendation.** Make the accessor resolve requested stable row keys against an authoritative, versioned partition; validate the partition enum and row identity before any text access. Bind the final lock to the partition digest and the relevant frozen preprocessing/eligibility provenance as well as the raw manifest. Require the promised study identity and record the actual requested unit/cell scope. Add synthetic tests for relabelled and stale rows, changed positions/IDs, unknown partitions, a different partition digest and incomplete registered locks. Positive-path logging can also be tested entirely with fixtures. No held-out opening is needed to repair or verify this.

### F3 — major: P1 succeeds on the observed labels but is not implemented as a closed allow-list

**Evidence.** corpora_loader.py:33–49 uses a suffix regex plus startswith("Creative Commons - Attribution"), rather than the exact-label enumeration promised by P1. Short synthetic checks show that a contradictory “Attribution NoDerivatives” label ending in the ordinary BY URL is admitted, as is a label whose hostname is notcreativecommons.org. Standard by-nc URLs are correctly rejected; the problem is ambiguity and insufficient URL/label validation, not an assertion that all restricted labels pass.

Lines 156–157 substitute metadata.license when all_licenses is missing or empty, losing the guarantee that every thread component was labelled. Actual null list entries would also need safe handling by the later string join. audit_corpora.py:66 assigns P1 true unconditionally, and the final verdict expression does not include P1. None of these counterexamples was observed among the current 17 stored label combinations; their current dispositions were checked and are consistent with the intended rule.

**Recommendation.** Freeze an explicit mapping for the observed complete labels, reject unknown/contradictory forms, and validate the component-list schema conservatively. Compute P1 from assertions over admitted units and include it in the verdict. Keep the observed 19,060 exclusions.

### F4 — major: P5 failure handling does not exclude failed files before the count rules

**Evidence.** iter_dolma records a decompression_failure after yielding a readable prefix, and the loader still writes those units. audit_corpora.py:43–48 checks that flag only for partial JSON shards. A news gzip that yields 126,673 valid records and then reports a trailer/CRC failure would satisfy the news “exact” expression despite the recorded failure. More generally, failed-file records enter representatives and cell counts before reconciliation; a partial-shard failure makes P5 false but does not remove those records from P2–P4/P7 counts as the written rule requires.

**Recommendation.** Require successful decompression, the line/parse accounting identity and the applicable external reconciliation for every file. Quarantine failed files before clustering/counting admitted units, with the reason recorded, and recompute affected counts. A synthetic failing iterator or tiny fixture is sufficient for the failure-path check. The current files passed independent byte/footers checks and have no recorded failures; this finding does not dispute their present counts.

### F5 — major: the stated provisional expansion/finalisation loop is not executable as specified

**Evidence.** freeze_corpora.py:71–75 queues both expansion shards for a requested source in one invocation. audit_corpora.py:101–102 only reports whether expansion is needed and lists the order. No supplied driver adds just the next shard, reclusters/recounts, then stops if the floor is met. The partitioner writes directly over the same final filename on every run, with no provisional/final distinction or refusal after use.

**Recommendation.** Supply a documented, enforceable one-step expansion procedure or driver: take the next permitted shard only, check again, respect the source cap/news failure, and publish the final map once under a version/digest. Refuse ordinary overwrites of a finalised map. This was not exercised because the initial pool passes, so it is not a separate numerical blocker for the current initial selection; it matters before any rebuild or expansion prompted by F1.

### F6 — minor: qualify censored eligibility and complete tokenizer provenance

**Evidence.** Token counts come from capped character prefixes, not complete documents (corpora_loader.py:200–211); two censored open books fail the largest book-window threshold, as quantified above. counts.json records repository revisions and character caps, but not the tokenizer-file digests promised in audit §6a. Special-token handling is visible in code—add_special_tokens=False—rather than recorded alongside the output.

**Recommendation.** State that the reported long-length counts use the capped-prefix convention, and that censored counts below a threshold do not establish full-text ineligibility. If full-document eligibility is desired, extend only the unresolved cases under a documented preprocessing revision before use. Record tokenizer asset hashes, special-token/BOS/EOS conventions and relevant runtime/code provenance with the frozen metadata. Keep the present 1,024-token book-floor conclusion; it is supported.

### F7 — minor: synchronise the current-state record with the implementation

**Evidence.** The audit title still says “DRAFT: the plan before any download”, §8 says “Nothing downloaded”, and the orientation's R01 row still says r3 pending/open. The audit claims LFS comparison for all 17 files, labels parsing-only partial-shard checks “exact”, displays P8 as False in a Pass column even though no expansion is needed, and truncates the P7 detail. The seal files are absent rather than existing empty tracked files. Book exposure matching uses rec_id rather than the promised URL field. The CJK implementation samples the first 2,000 normalised characters and then removes spaces, whereas §5 says the first 2,000 non-space characters. The lower-level counts and code reveal these differences; the summaries should not require that reconstruction.

**Recommendation.** Separate historical planning text from current limitations; close the R01 table entry; distinguish data-file LFS verification from README hashing and parse-integrity checks from external reconciliation; print P8 as “not needed”; report the actual seal-file state; and align the exposure/CJK definitions with their implemented or corrected forms. Label token medians as capped where applicable and qualify the held-out-share range to exclude the Danish non-target singleton. The handoff should carry the R02 blockers while the data PASS remains under review.

VERDICT: REVISE

