#!/usr/bin/env python3
"""The appendix tables (B, C, D, E), generated, never typed (guide A4.1).

Three kinds of table:
  * **extracted**: a named block of an agreed report's generated ``tables.md`` (``outputs/<study>/report/tables.md``,
    written by that study's report builder from the locked record and reviewed at its checkpoint), copied verbatim
    with a paper caption; every table line is asserted to be a substring of the committed report
    (``research/STUDY<n>_REPORT_v0.1.md``), so the appendix carries exactly the agreed table;
  * **computed**: the data tables C1 (the count flow per frozen file) and C2 (the ten cells) from the Stage 4 audit
    JSON with their totals asserted, the lock table E2 from the four ``PRE_RUN_LOCK.json`` and ``RUN_MANIFEST.json``
    files with the run hours asserted against the registers, and D5 (the secondary diagnostic's two SE counts) from
    the labelled side computation's JSON (R09 F18);
  * the values the appendix prose quotes are registered under the prefixes ``c`` (data), ``e`` (locks) and ``d``
    (the side computation) in ``paper_values.json``.

Usage:  .venv/bin/python research/paper/tables/make_appendix_tables.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paperlib as P  # noqa: E402

OUT = P.PAPER / "tables"
REPORT_MD = {"s1": "research/STUDY1_REPORT_v0.1.md", "s2": "research/STUDY2_REPORT_v0.1.md",
             "s3": "research/STUDY3_REPORT_v0.1.md", "s4": "research/STUDY4_REPORT_v0.1.md"}
REPORT_TABLE = {("s1", "rules"): 1, ("s2", "rules"): 1, ("s3", "rules"): 1, ("s4", "rules"): 2,
                ("s2", "deployer_kgw"): 16, ("s2", "deployer_gumbel"): 17, ("s4", "operating_points"): 9,
                ("s3", "remedy_class"): 9, ("s3", "cross_tok"): 15, ("s3", "t1_by_block"): 2,
                ("s2", "tokenizer_axis"): 21, ("s1", "reduction"): 6, ("s2", "reduction"): 12,
                ("s1", "r1_failures"): 4, ("s2", "s1_failures"): 4, ("s3", "t1_failures"): 3, ("s4", "w3_failures"): 7,
                ("s4", "w2_rows"): 4, ("s4", "w2_components"): 5, ("s4", "model_null"): 14, ("s4", "transfer"): 13,
                ("s3", "remedy_diag"): 8, ("s4", "quality"): 15, ("s4", "pairing"): 16, ("s3", "breakeven"): 12,
                ("s3", "zcost"): 11, ("s3", "calboot"): 13, ("s4", "null_abstentions"): 18, ("s2", "language"): 20}
STUDY_N = {"s1": 1, "s2": 2, "s3": 3, "s4": 4}


def blocks(s: str) -> dict[str, str]:
    text = (P.ROOT / P.STUDY_DIR[s] / "report" / "tables.md").read_text(encoding="utf-8")
    out, name, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^### (\S+)\s*$", line)
        if m:
            if name:
                out[name] = "\n".join(buf).strip("\n")
            name, buf = m.group(1), []
        elif name:
            buf.append(line)
    if name:
        out[name] = "\n".join(buf).strip("\n")
    return out


_report_cache: dict[str, str] = {}


def report_text(s: str) -> str:
    if s not in _report_cache:
        _report_cache[s] = (P.ROOT / REPORT_MD[s]).read_text(encoding="utf-8")
    return _report_cache[s]


def write(name: str, caption: str, body: str) -> None:
    (OUT / f"{name}.md").write_text(f"Table — {caption}\n\n{body.rstrip()}\n", encoding="utf-8")
    print(f"wrote tables/{name}.md")


def extract(tid: str, s: str, block: str, caption: str) -> None:
    b = blocks(s)[block]
    table_lines = [ln for ln in b.splitlines() if ln.startswith("|")]
    assert len(table_lines) >= 3, (s, block)
    joined = "\n".join(table_lines)
    assert joined in report_text(s), f"{s}:{block}: the table text is not in the agreed report"
    ncol = table_lines[0].count("|") - 1
    for ln in table_lines[2:]:
        assert ln.count("|") - 1 == ncol or ln.replace("\\|", "").count("|") - 1 == ncol, (s, block, ln[:60])
    P.check(f"appendix {tid} ({s} {block}) rows", len(table_lines) - 2, len(table_lines) - 2)
    n = REPORT_TABLE[(s, block)]
    src = (f"Extracted verbatim from the Study {STUDY_N[s]} report's generated Table {n} (block `{block}` of "
           f"`{P.STUDY_DIR[s]}/report/tables.md`, written by the report builder from the locked record and agreed at "
           f"checkpoint {P.CHECKPOINT_OF_REPORT[s]}); the report's own column note follows the table.")
    write(f"table{tid}_{block}", f"{caption} {src}", b)


def main() -> int:
    # --- B: the pre-registered rules against the observed results, one table per study ------------------------
    extract("B1", "s1", "rules", "Study 1 (synthetic laws): every pre-registered rule with its criterion, the observed counts and its verdict (R1–R5, R4b and the refuted fixed-size statement). A failed rule stays failed.")
    extract("B2", "s2", "rules", "Study 2 (real null text): the pre-registered rules S1–S5 with their criteria, observed counts and verdicts; S4's failing chains are listed in full (the three overlapping groups of §5 are counted from them).")
    extract("B3", "s3", "rules", "Study 3 (remedies and transfer): the pre-registered rules T1, T2 and REP with their statements, observed counts and verdicts.")
    extract("B4", "s4", "rules", "Study 4 (the power side): the pre-registered rules W1, W2 and W3 with their pass conditions, observed counts and verdicts; W2's failure is every row unresolved (Tables D6a and D6b).")
    # --- D: the supplementary tables (D1 is tables/table3_predictor.md, generated by make_tables.py) -----------
    extract("D2a", "s2", "tokenizer_axis", "The tokenizer axis: for the same texts, the across-key SD under Qwen2.5 tokens against the Llama-3.2 value and the across-tokenizer correlation of the per-key levels, by family, width and rule; the labelled post-hoc overlap account that explains the co-movement is Table D2b.")
    extract("D3a", "s1", "reduction", "The fixed-size reduction (1/C_cond − 1)/(V − 1) on the synthetic laws by rule and width: the registered statement 'below 1% for V ≥ 10,000' is refuted under the distinct rule at h ≤ 1.")
    extract("D3b", "s2", "reduction", "The fixed-size reduction on real text at V ≥ 128k by rule.")
    extract("D4a", "s1", "r1_failures", "Study 1, R1: the inconsistent and unresolved cells with the protocol's diagnostics (every one at h = 0).")
    extract("D4b", "s2", "s1_failures", "Study 2, S1: the inconsistent and unresolved cells with the protocol's diagnostics.")
    extract("D4c", "s3", "t1_failures", "Study 3, T1: the inconsistent and unresolved rows with the protocol's diagnostics (every one under the raw rule).")
    extract("D4d", "s4", "w3_failures", "Study 4, W3: the unresolved rows with every diagnostic the protocol names (every one a Wikipedia-source transfer row at h = 1 under the raw rule).")
    extract("D6a", "s4", "w2_rows", "W2 by prompt cell and rule (a stated design limit): the two-way between-key components of power before and after per-key calibration, the observed SDs, the binomial proxy, the ratio R_pow with its paired key-bootstrap interval for the prompt-conditioned target, the predicted side and the class (every row unresolved).")
    extract("D6b", "s4", "w2_components", "W2's components per row: the raw two-way values before the floor, the residual mean square and the prompt component (the between-key component of power is of the order of its noise correction at 100 keys × 50 prompts).")
    extract("D7", "s4", "model_null", "The model's own null law: the nominal and the diagonal conformal@5000 levels of the 1,000 evaluation keys on the 5,000 unwatermarked generations per cell, with the predictor's values; the aggregate comparison of the two negative classes is LUNA's and the two-key practice the artefact's (§7.4).")
    extract("D8a", "s4", "transfer", "The transfer sources on the power side: the conformal@5000 power over the 100 power keys and the model-null level over the 1,000 evaluation keys under every calibration source beside the diagonal; no transfer guarantee.")
    extract("D8b", "s3", "remedy_diag", "The remedy table on the diagonal at h = 1 and h = 2 (the remedy table of §6 condenses the h = 1 rows): per method and rule, the key-mean level, the across-key SD, the key quantiles and the shares above α, 2α and 5α, medians over the 20 (tokenizer, cell) units.")
    extract("D9a", "s4", "quality", "Quality diagnostics per cell and arm with the human reference: the model's perplexity of its own tokens, rep-4, the loop share (rep-4 above 0.5); no text excluded.")
    extract("D9b", "s4", "pairing", "The per-prompt pairing: the watermark's effect per prompt averaged over the 100 power keys, by arm and rule.")
    extract("D10a", "s3", "breakeven", "The break-even calibration size on the diagonal: the smallest N_cal at which per-key conformal calibration's across-key dispersion falls below the nominal test's (paired key bootstrap).")
    extract("D10b", "s3", "zcost", "The null-side cost z(t) − z_α of each method: the key quantiles of the threshold in z-units, the abstaining keys counted.")
    extract("D10c", "s3", "calboot", "The calibration-set component: the variation of the across-key summaries over resamples of the calibration texts, beside the Beta term of one fixed key's threshold.")
    extract("D10d", "s4", "null_abstentions", "The null-block threshold settings with abstaining keys: the committed thresholds at or below zero never reject and are never repaired.")
    # the supplements the main text and its captions promise (R12 F6): the deployer's view in full, the operating points, the transfer blocks
    R4 = P.register("s4"); g4 = P.grid("s4"); arm = next(a for a in g4["arms"] if a["name"] == g4["primary_arm"])
    extract("D7b", "s4", "operating_points", f"The per-key operating points before and after calibration: Study 3's stored corpus null level (over its N_E = {P.register('s3')['N_E']} texts) and the model-null level (over N₀ = {R4['N0']} unwatermarked generations) of each of the {R4['K4']} power keys against its realised power over {R4['n_tx']} generated texts, per method and prompt cell, on Qwen2.5-1.5B at the primary arm (δ = {arm['delta']}, h = {arm['h']}), the raw rule, L = {g4['primary_length']}, α = {g4['primary_alpha']}, the per-key and scheme-level thresholds set on the same-cell human null texts (the diagonal source; N_cal = {g4['primary_method']['N_cal']:,} for the per-key methods), with the correlation of a key's null level and its power under each method. The per-key operating point before and after calibration is the view Genhatharan 2026 and AutoMark report before this study [@genhatharan2026nominal; @gloaguen2026automark]; the aggregate comparison of the two negative classes is LUNA's [@park2026luna] and the two-key practice the artefact's [@xlr8harder2026synthid]; one model and three English prompt cells, no transfer claim.")
    extract("D12a", "s2", "deployer_kgw", "The deployer's view in full (KGW, γ = 0.25, h = 1, α = 1%, the longest length of each cell) under both tokenizers and both rules: the key-mean; the key quantiles, the sampled worst key and the shares above 2α and 5α, each of these with its crossed key-by-document 95% interval; and the across-key SD with its key-bootstrap interval; the Llama-3.2 rows at h = 1 condense to Table D14.")
    extract("D12b", "s2", "deployer_gumbel", "The same for Gumbel-max under both rules.")
    extract("D13a", "s3", "remedy_class", "The remedy table by pair class under both rules and both widths: per class, rule, width and method, the key-mean, the across-key SD, the 99% key, the sampled worst key, the shares above α, 2α and 5α, the predicted mean, SD and shares and the median observed-to-predicted SD ratio, medians over the ordered pairs of the class; Table D15 condenses the distinct-rule h = 1 rows.")
    extract("D13b", "s3", "cross_tok", "The cross-tokenizer transfer: a threshold calibrated under one tokenizer's tokens and evaluated under the other's with the same key, per family, rule, width and method, with the key-free predictor's SD and share beside the observed ones.")
    extract("D13c", "s3", "t1_by_block", "T1 by block (rule, width, tokenizer, N_cal and pair class): the candidate, eligible, resolved, consistent, inconsistent and unresolved counts with the median ratios; every ordered pair's own row is in the Study 3 report's supplement `tables_pairs_kgw_alpha0.01_full.md` in the companion repository.")
    extract("D11", "s2", "language", "The H-language disparity: the per-key ratio of the largest to the smallest of a key's six Wikipedia-language levels at L = 256, by tokenizer, family, width and rule; empirical ratios over the sampled keys and realised texts, never a discrimination claim.")

    # --- C: the data (computed from the Stage 4 audit JSON and the freeze manifest) ---------------------------
    audit = json.loads((P.ROOT / "outputs" / "corpora_audit_v0.3.json").read_text())
    manifest = json.loads((P.ROOT / "outputs" / "corpora_manifest_v0.1.json").read_text())
    flow = audit["flow"]; ps = audit["partition_summary"]
    rows, tot = [], {"physical_lines": 0, "parsed_records": 0, "licence_excluded": 0, "non_representative_duplicates": 0, "representatives_allowed": 0, "open_representatives": 0, "holdout_representatives": 0, "unparseable_lines": 0}
    SRC = {"news": "Common Pile v0.1 news", "stackexchange": "Common Pile v0.1 Stack Exchange", "project_gutenberg": "Common Pile v0.1 Project Gutenberg", "2023": "Wikimedia Wikipedia 2023-11-01"}
    for f, d in flow.items():
        src = next(v for k, v in SRC.items() if f.startswith(k))
        lang = re.search(r"20231101\.(\w\w)/", f).group(1) if f.startswith("2023") else "en"
        rows.append([f"`{f}`", src, lang, f"{d['physical_lines']:,}", f"{d['unparseable_lines']:,}", f"{d['licence_excluded']:,}", f"{d['non_representative_duplicates']:,}", f"{d['representatives_allowed']:,}", f"{d['open_representatives']:,}", f"{d['holdout_representatives']:,}"])
        for k in tot:
            tot[k] += d[k]
    P.check("C1 total representatives = n_allowed_representatives", tot["representatives_allowed"], float(audit["n_allowed_representatives"]))
    P.check("C1 open + holdout = allowed", tot["open_representatives"] + tot["holdout_representatives"], float(audit["n_allowed_representatives"]))
    P.check("C1 parsed = n_units", tot["parsed_records"], float(audit["n_units"]))
    P.check("C1 unparseable = 0", tot["unparseable_lines"], 0.0)
    P.check("C1 licence excluded = P1", tot["licence_excluded"], float(audit["rules"]["P1"]["licence_excluded_units"]))
    rows.append(["**total**", "", "", f"{tot['physical_lines']:,}", f"{tot['unparseable_lines']:,}", f"{tot['licence_excluded']:,}", f"{tot['non_representative_duplicates']:,}", f"{tot['representatives_allowed']:,}", f"{tot['open_representatives']:,}", f"{tot['holdout_representatives']:,}"])
    write("tableC1_corpora_flow", f"The frozen null corpora (Stage 4, procedure v3; `outputs/corpora_audit_v0.3.json`): per frozen file, the physical lines, the unparseable lines, the units excluded by the licence allow-list, the non-representative duplicates (never scored), the allowed cluster representatives and their open and held-out partitions. Every file reconciled exactly to its card count or footer; the held-out share of clusters is {100 * ps['holdout_share_of_clusters']:.2f}%.",
          P.md_table(["File", "Source", "Lang.", "Lines", "Unparseable", "Licence-excluded", "Duplicates (non-rep.)", "Representatives", "Open", "Held out"], rows))
    cells = audit["cells"]; crow = []
    for c in P.CELL_ORDER:
        lab = P.CELL_LABEL[c]; d = cells[lab]
        crow.append([lab, f"{d['open']:,}", f"{d['open_qwen']:,}", f"{d['holdout']:,}", f"{d['holdout_qwen']:,}"])
    write("tableC2_cells", "The ten confirmatory cells (source/language@L): the open units eligible at the cell's length under the Llama-3.2 tokenizer, the subset also eligible under Qwen2.5, and the held-out counts (never opened; `final: false` in every lock). The proceed rule's floor was 2,500 eligible units per cell in each partition.",
          P.md_table(["Cell", "Open eligible", "Open, Qwen-eligible too", "Held out eligible", "Held out, Qwen-eligible too"], crow))
    entries = manifest["entries"]
    P.register_value("c_n_files", len(entries)); P.register_value("c_n_data_files", sum(1 for e in entries.values() if e["hub_lfs_sha256"]))
    P.register_value("c_total_bytes", sum(e["bytes"] for e in entries.values())); P.register_value("c_total_gib", f"{sum(e['bytes'] for e in entries.values()) / 2**30:.2f}")
    P.register_value("c_n_units", audit["n_units"]); P.register_value("c_n_clusters", audit["n_clusters"]); P.register_value("c_n_representatives", audit["n_allowed_representatives"])
    P.register_value("c_n_open", tot["open_representatives"]); P.register_value("c_n_holdout", tot["holdout_representatives"])
    P.register_value("c_holdout_share_pct", f"{100 * ps['holdout_share_of_clusters']:.2f}")
    P.register_value("c_licence_excluded", tot["licence_excluded"]); P.register_value("c_duplicates", tot["non_representative_duplicates"])
    P.register_value("c_exact_unions", ps["exact_duplicate_unions"]); P.register_value("c_near_unions", ps["near_duplicate_unions"])
    P.register_value("c_pairs_confirmed", ps["pairs_at_or_above_threshold"]); P.register_value("c_candidate_pairs", ps["candidate_pairs_distinct"]); P.register_value("c_candidate_units", ps["candidate_units"])
    P.register_value("c_lsh_bands", ps["lsh"]["bands"]); P.register_value("c_lsh_rows", ps["lsh"]["rows"]); P.register_value("c_threshold", ps["threshold_exact_jaccard"])
    P.register_value("c_exposure_hits", ps["exposure_hits"]); P.register_value("c_forced_open", ps["forced_open_units"]); P.register_value("c_cross_source_clusters", ps["cross_source_clusters"])
    P.register_value("c_n_cells", len(cells)); P.register_value("c_cell_floor", 2500)
    P.register_value("c_licences", ", ".join(audit["rules"]["P1"]["admitted_identities"]))
    P.register_value("c_minhash_perm", audit["loader_meta"]["minhash"]["n_perm"])
    P.register_value("c_cap_chars", audit["loader_meta"]["tok_cap_chars"]["news"]); P.register_value("c_cap_chars_books", audit["loader_meta"]["tok_cap_chars"]["gutenberg"]); P.register_value("c_book_skip", audit["loader_meta"]["book_skip_tokens"])
    P.register_value("c_n_sources", 4); P.register_value("c_n_languages", len({re.search(r'20231101\.(\w\w)/', f).group(1) for f in flow if f.startswith('2023')}))
    P.register_value("c_stackexchange_sites", audit["rules"]["P2"]["n_sites"]); P.register_value("c_news_outlets", len(audit["news_outlets"]))

    # --- E2: the locks and records ------------------------------------------------------------------------------
    erows = []; n_pinned_total = 0
    for s in ("s1", "s2", "s3", "s4"):
        L = P.lock(s); M = P.manifest(s); R = P.register(s)
        n_pinned = len(L["hashes"]); n_pinned_total += n_pinned
        hours = M["run"]["duration_hours"]
        P.check(f"E2 run hours {s}", hours, R["run_hours"])
        launch = M["git"].get("launch", {}); head = launch.get("head_at_launch") or re.search(r"HEAD=([0-9a-f]{7,40})", launch.get("launch_line", "")).group(1)
        inv = M["inventory"]; n_files = inv.get("n_cell_files", inv.get("n_files"))
        ao = M.get("analysis_output") or {}
        res_sha = ao.get("sha256") or ""
        if not res_sha:  # Studies 1–2: the results file's digest from the file itself
            res_sha = P.sha256(P.ROOT / P.STUDY_DIR[s] / "results.json")
        erows.append([f"{STUDY_N[s]}", f"`{Path(L['protocol']).name}`", L["date"], L["review"]["checkpoint"], f"{n_pinned}", f"`{P.sha256(P.ROOT / P.STUDY_DIR[s] / 'PRE_RUN_LOCK.json')[:12]}`", f"`{head[:7]}`", M["run"]["start_utc"][:16].replace("T", " "), f"{hours:.2f}", f"{n_files:,}", f"`{inv['inventory_sha256'][:12]}`", f"`{res_sha[:12]}`", "no" if not L["final"] else "yes"])
        P.register_value(f"e_s{STUDY_N[s]}_n_pinned", n_pinned); P.register_value(f"e_s{STUDY_N[s]}_lock_date", L["date"]); P.register_value(f"e_s{STUDY_N[s]}_checkpoint", L["review"]["checkpoint"])
        P.register_value(f"e_s{STUDY_N[s]}_head_at_launch", head[:7]); P.register_value(f"e_s{STUDY_N[s]}_n_record_files", n_files)
    P.register_value("e_n_pinned_total", n_pinned_total)
    P.register_value("e_n_locks", 4)
    write("tableE2_locks", "The four pre-run locks and their records: the protocol, the lock date, the checkpoint whose agreement preceded it, the number of pinned files (the protocol, grid, code, validation record, manifests and, from Study 2 on, the earlier studies' pinned files), the lock's digest, the commit at launch, the run's start and duration, the record's file count and inventory digest, the locked analyser's results digest, and whether the lock opened the holdout (`final`). Every lock carries `before_outcomes: true` and `approved_by: Yichen`; the runners refuse to start without the verified lock and the analysers recompute under it.",
          P.md_table(["Study", "Protocol", "Locked", "After", "Pinned files", "Lock digest", "Launch commit", "Run start (UTC)", "Hours", "Record files", "Inventory digest", "Results digest", "Holdout opened"], erows))

    # --- D5: the secondary population diagnostic with both SE counts (the side computation; R09 F18, D18) ------
    side1 = json.loads((P.ROOT / "outputs/study1_v0.3/report/twoway_se_check.json").read_text()); side2 = json.loads((P.ROOT / "outputs/study2_v0.1/report/twoway_se_check.json").read_text())
    r1 = side1["recount_population_diagnostic"]; r2 = side2["recount_table15b"]
    P.check("D5 S1 stored crossed count = recomputed", r1["within2_crossed_stored_in_results"], float(r1["within2_crossed_recomputed"]))
    P.check("D5 S1 mismatch_se = 0", r1["mismatch_se"], 0.0)
    drows = [["1 (synthetic laws; the R1 cells)", f"{r1['n']}", f"{r1['within2_crossed_stored_in_results']}", f"{r1['within2_key_only']}", f"{r1['within2_normal']}", f"{side1['summary']['n_with_positive_se_and_nonzero_v']:,} of {side1['summary']['n_rows']:,}"],
             ["2 (real text; the eligible primary cells)", f"{r2['n_eligible']}", f"{r2['within2_crossed']}", f"{r2['within2_key_only']}", f"{r2['within2_normal']}", f"{side2['summary']['n_with_positive_se_and_nonzero_v']:,} of {side2['summary']['n_rows']:,}"]]
    for k, v in (("d_s1_n", r1["n"]), ("d_s1_within2_crossed", r1["within2_crossed_stored_in_results"]), ("d_s1_within2_key_only", r1["within2_key_only"]), ("d_s1_within2_normal", r1["within2_normal"]),
                 ("d_s2_n", r2["n_eligible"]), ("d_s2_within2_crossed", r2["within2_crossed"]), ("d_s2_within2_key_only", r2["within2_key_only"]), ("d_s2_within2_normal", r2["within2_normal"]),
                 ("d_B_crossed", side1["B_crossed_stored"]), ("d_B_key_only", side1["B_key_only"]), ("d_s1_rows_checked", side1["summary"]["n_with_positive_se_and_nonzero_v"]), ("d_s2_rows_checked", side2["summary"]["n_with_positive_se_and_nonzero_v"]),
                 ("d_s1_rows_total", side1["summary"]["n_rows"]), ("d_s2_rows_total", side2["summary"]["n_rows"])):
        P.register_value(k, v)
    write("tableD5_secondary_diagnostic", "The secondary population diagnostic of Studies 1 and 2: the two-way estimate s_K² − MS_E/N of the across-key variance of the level against the predictor's population variance, counted as 'within 2 SEs' under three SE constructions: the reports' crossed key-by-text bootstrap (its resamples centre at (K − 1)/K · s_K², the R09 F18 identity, so these counts are historical descriptive diagnostics), a key-only bootstrap from the stored per-key levels (the uncertainty of the text-conditioned functional, R09 F22 and D18, with the a_k-only approximation; a conditional sensitivity calculation), and normal theory. Neither construction carries a validated population confidence statement; the labelled side computation `research/study1/TWOWAY_SE_CHECK_2026-10-18.md` is the source and the agreed reports are unchanged.",
          P.md_table(["Study (cells)", "Cells", "Within 2 crossed SEs (reported)", "Within 2 key-only SEs (recount)", "Within 2 normal-theory SEs", "Stored rows whose crossed mean was checked against the identity"], drows))

    # --- D2b: the tokenizer-overlap account (the labelled post-hoc side computation of Study 2; corrected at R06) ----
    ov = json.loads((P.ROOT / "outputs/study2_v0.1/report/tokenizer_overlap.json").read_text()); R2 = P.register("s2")
    cells_ov = ov["cells"]; orows = []
    reg_pairs = {h: {m[0]: (m[1], m[2]) for m in re.findall(r"([\w/@]+) ([\d.e−-]+) / ([\d.e−-]+)", R2[f"ov_{h}_by_cell"])} for h in ("h0", "h1")}
    for c in P.CELL_ORDER:
        lab = P.CELL_LABEL[c]; d = cells_ov[c]
        row = [lab]
        for h in ("h0", "h1"):
            x = d[h]; pred, obs = x["rho_pred_qhat"], x["rho_obs_qhat_stored_values"]
            rp, ro = reg_pairs[h][lab]
            tol = lambda s: (0.005 * abs(P.num(s)) + 1e-12) if "e" in s else None   # the register prints small values in scientific notation to three significant digits
            P.check(f"D2b {lab} {h} predicted", pred, rp, tol=tol(rp)); P.check(f"D2b {lab} {h} observed", obs, ro, tol=tol(ro))
            row += [f"{x['n_tuples_shared']:,}", f"{100 * x['weight_share_on_shared_tuples_llama']:.1f}% / {100 * x['weight_share_on_shared_tuples_qwen']:.1f}%", P.fnum(pred, 3), P.fnum(obs, 3)]
        row.append(f"{100 * d['semantic_share_llama']['share_occurrences_on_same_string_ids']:.1f}% / {100 * d['semantic_share_qwen']['share_occurrences_on_same_string_ids']:.1f}%")
        orows.append(row)
    P.check("D2b ids with the same string", ov["semantic"]["ids_same_string"], R2["ov_ids_same"]); P.check("D2b ids compared", ov["semantic"]["ids_compared"], R2["ov_ids_compared"])
    P.register_value("d_ov_written", ov["written_utc"][:10])
    Ls = sorted({d[h]["L"] for d in cells_ov.values() for h in ("h0", "h1")}); assert Ls == [256, 1024], Ls
    assert re.search(r"under the raw\s+rule at the cell's longest length", (P.ROOT / "research/study2/tokenizer_overlap.py").read_text(encoding="utf-8")), "the side script's rule and length"
    write("tableD2b_tokenizer_overlap", f"The labelled post-hoc overlap account of the across-tokenizer co-movement (the side computation `research/study2/tokenizer_overlap.py` of {ov['written_utc'][:10]}, not pre-registered; its first version compared string-identical ids and was corrected at checkpoint R06, the superseded output kept beside it): per corpus cell at its longest length (L = {Ls[0]}, or {Ls[1]:,} for the two {Ls[1]:,}-token cells), at h = 0 and h = 1 under the raw rule, over the N = {R2['N']} realised texts and the stored q̂ values of the K = {R2['K']} production keys: the number of integer tuple ids shared by the two tokenizers' document-averaged weight vectors, the share of each tokenizer's occurrence weight that sits on the shared tuples (Llama-3.2 / Qwen2.5), the identity-predicted correlation of the per-key mean green fraction q̂ from the shared hash inputs, and the observed correlation of the stored q̂ values of the two production cells; the last column is the semantic diagnostic (the share of each tokenizer's token occurrences on the {ov['semantic']['ids_same_string']} ids of {ov['semantic']['ids_compared']:,} whose token string is the same in both vocabularies), not the hash-overlap estimand. The colouring hash is a function of the integer ids alone, so the identity, not shared strings, accounts for the co-movement; the shared-id account of the cross-language correlations under Qwen2.5 remains a hypothesis.",
          P.md_table(["Cell", "h = 0: shared ids", "weight on shared (L / Q)", "predicted corr.", "observed corr.", "h = 1: shared pairs", "weight on shared (L / Q)", "predicted corr.", "observed corr.", "same-string occurrence share (L / Q)"], orows))

    P.flush_values(("c", "e", "d"))
    P.finish_checks("appendix_tables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
