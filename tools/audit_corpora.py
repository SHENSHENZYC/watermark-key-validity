"""Stage 4 audit: the count flow, the proceed rule P1–P8, the confirmatory cells and the seal test (audit §§4–6).
Reads <units_dir> (loader outputs and partition.parquet) and the manifest; writes outputs/corpora_audit_v0.1.json and
prints Markdown tables for the memo. Metadata only: no text is read except in the seal test, which reads one open unit.
Usage: .venv/bin/python -u tools/audit_corpora.py [units_dir] [--out outputs/corpora_audit_v0.1.json]
"""
import datetime, json, pathlib, sys, tempfile
import numpy as np, pandas as pd, pyarrow.parquet as pq
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import corpora_access as access
ALLOWED_IDENTITIES = {"cc-by-4.0", "cc-by-sa-2.5", "cc-by-sa-3.0", "cc-by-sa-4.0", "public-domain"}

BINS = [128, 256, 512, 1024, 2048]
BOOK_SKIP = 1000
CARD = {"news-dolma-0000.json.gz": 126673}   # the one complete source (audit P5)
CELLS_256 = [("news", "en"), ("wikipedia", "en"), ("stackexchange", "en"), ("wikipedia", "de"), ("wikipedia", "ru"), ("wikipedia", "ar"), ("wikipedia", "zh"), ("wikipedia", "ja")]
CELLS_1024 = [("wikipedia", "en"), ("gutenberg", "en")]
FLOOR_HOLDOUT, FLOOR_P2, FLOOR_P3, FLOOR_P4, SITE_MIN, N_SITES = 2500, 10000, 10000, 5000, 200, 20


def main(units_dir, out, version=None):
    units_dir = pathlib.Path(units_dir)
    meta = json.loads((units_dir / "counts.json").read_text())
    summary_prev = json.loads((units_dir / "partition_summary.json").read_text()) if (units_dir / "partition_summary.json").exists() else {}
    quarantined = {f["path"]: f["quarantined"] for f in meta["files"] if f.get("quarantined")}
    quarantined.update(summary_prev.get("rejected_files", {}))   # files the partition's acceptance step excluded before clustering (R02 F10)
    files = [f for f in meta["files"] if f["path"] not in quarantined]
    U = pd.concat([pq.read_table(units_dir / f["units_file"]).to_pandas() for f in files], ignore_index=True)
    pfile = units_dir / (f"partition_v{version}.parquet" if version else "partition.parquet")
    P = pq.read_table(pfile).to_pandas()
    partition_state = {"file": pfile.name, "finalised": bool(version), "sha256": (units_dir / f"partition_v{version}.sha256").read_text().strip() if version and (units_dir / f"partition_v{version}.sha256").exists() else None}
    assert len(U) == len(P) and (U["canonical_id"].values == P["canonical_id"].values).all()
    U = pd.concat([U, P[["cluster_id", "cluster_size", "is_representative", "exposure_hit", "forced_open", "partition"]]], axis=1)
    # eligibility per bin (Llama reference; Qwen intersection), books need BOOK_SKIP + L
    need = np.where(U["source"].values == "gutenberg", BOOK_SKIP, 0)
    for L in BINS:
        U[f"el_{L}"] = U["n_tok_llama"].values >= need + L
        U[f"elq_{L}"] = U[f"el_{L}"] & (U["n_tok_qwen"].values >= need + L)
    rep = U[U["is_representative"] & U["allowed"]]
    # --- count flow per file ---
    flow = {}
    for f, c in meta["counts_per_file"].items():
        if f in quarantined:
            flow[f] = {**c, "EXCLUDED": quarantined[f], "note": "no unit from this file enters any count"}; continue
        sub = U[U["file"] == f]
        flow[f] = {**c, "licence_excluded": int((~sub["allowed"]).sum()), "non_representative_duplicates": int((~sub["is_representative"]).sum()),
                   "representatives_allowed": int((sub["is_representative"] & sub["allowed"]).sum()),
                   "open_representatives": int((sub["is_representative"] & sub["allowed"] & (sub["partition"] == "open")).sum()),
                   "holdout_representatives": int((sub["is_representative"] & sub["allowed"] & (sub["partition"] == "holdout")).sum())}
    # --- P5 reconciliation ---
    recon = {}
    for f, c in meta["counts_per_file"].items():
        clean = c["unparseable_lines"] == 0 and "decompression_failure" not in c and c["physical_lines"] == c["parsed_records"] + c["unparseable_lines"] and f not in quarantined
        if f in CARD:
            recon[f] = {"kind": "external (card)", "card_count": CARD[f], "parsed": c["parsed_records"], "exact": clean and c["parsed_records"] == CARD[f]}
        elif "footer_rows" in c:
            recon[f] = {"kind": "external (parquet footer)", "footer_rows": c["footer_rows"], "parsed": c["parsed_records"], "exact": clean and c["parsed_records"] == c["footer_rows"]}
        else:
            recon[f] = {"kind": "parse-complete only (partial shard; the card total is a whole-source comparator)", "parsed": c["parsed_records"], "unparseable": c["unparseable_lines"], "exact": clean}
    # --- cells ---
    def cell(src, lang, L, part, qwen=False):
        m = (rep["source"] == src) & (rep["lang"] == lang) & (rep["partition"] == part) & rep[("elq_" if qwen else "el_") + str(L)]
        return int(m.sum())
    cells = {}
    for (src, lang) in CELLS_256:
        cells[f"{src}/{lang}@256"] = {"open": cell(src, lang, 256, "open"), "open_qwen": cell(src, lang, 256, "open", True), "holdout": cell(src, lang, 256, "holdout"), "holdout_qwen": cell(src, lang, 256, "holdout", True)}
    for (src, lang) in CELLS_1024:
        cells[f"{src}/{lang}@1024"] = {"open": cell(src, lang, 1024, "open"), "open_qwen": cell(src, lang, 1024, "open", True), "holdout": cell(src, lang, 1024, "holdout"), "holdout_qwen": cell(src, lang, 1024, "holdout", True)}
    bins = {}
    for (src, lang), g in rep.groupby(["source", "lang"]):
        bins[f"{src}/{lang}"] = {str(L): {"open": int((g[f"el_{L}"] & (g["partition"] == "open")).sum()), "holdout": int((g[f"el_{L}"] & (g["partition"] == "holdout")).sum())} for L in BINS}
    forum = rep[(rep["source"] == "stackexchange") & (rep["lang"] == "en") & (rep["partition"] == "open") & rep["el_256"]]
    sites = forum.groupby("group").size().sort_values(ascending=False)
    outlets = rep[(rep["source"] == "news") & (rep["partition"] == "open") & rep["el_256"]].groupby("group").size().sort_values(ascending=False)
    # --- rules ---
    rules = {}
    adm = U[U["allowed"]]
    adm_ids = set(i for ident in adm["licence_identity"].unique() for i in str(ident).split("|"))
    se_adm = adm[adm["source"] == "stackexchange"]
    p1_ok = adm_ids <= ALLOWED_IDENTITIES and not se_adm["licence_identity"].str.contains("SCHEMA|OTHER").any() and (adm[adm["source"] == "gutenberg"]["licence_identity"] == "public-domain").all() and len(quarantined) == 0
    rules["P1"] = {"pass": bool(p1_ok), "admitted_identities": sorted(adm_ids), "licence_excluded_units": int((~U["allowed"]).sum()), "identities": U["licence_identity"].value_counts().head(14).to_dict(), "quarantined_files": quarantined}
    p2 = {k: cells[k]["open"] for k in ["news/en@256", "wikipedia/en@256", "stackexchange/en@256"]}
    rules["P2"] = {"pass": all(v >= FLOOR_P2 for v in p2.values()) and int((sites >= SITE_MIN).sum()) >= N_SITES, "open_eligible_256": p2, "sites_with_>=200": int((sites >= SITE_MIN).sum()), "n_sites": int(len(sites))}
    p3 = {f"wikipedia/{l}@256": cells[f"wikipedia/{l}@256"]["open"] for l in ["de", "ru", "ar", "zh", "ja"]}
    rules["P3"] = {"pass": all(v >= FLOOR_P3 for v in p3.values()), "open_eligible_256": p3}
    p4 = {k: cells[k]["open"] for k in ["gutenberg/en@1024", "wikipedia/en@1024"]}
    rules["P4"] = {"pass": all(v >= FLOOR_P4 for v in p4.values()), "open_eligible_1024": p4}
    rules["P5"] = {"pass": all(r["exact"] for r in recon.values()), "reconciliation": recon}
    # P6: seal test through the sealed accessor on the finalised map when there is one; on a provisional map the test is
    # deferred (the accessor refuses to bind an unfinalised partition, which is itself the required behaviour)
    seal = {}
    if partition_state["finalised"]:
        try:
            A = access.Access(units_dir, version)
            first_open = P[P["partition"] == "open"]["canonical_id"].head(1).tolist(); first_hold = P[P["partition"] == "holdout"]["canonical_id"].head(1).tolist()
            cid, text = next(A.load_texts(first_open, "open")); seal["open_load"] = f"OK ({cid}, {len(text)} chars)"
            for name, kw in [("holdout_no_lock", {}), ("holdout_rows_as_open", None)]:
                try:
                    next(A.load_texts(first_hold, "open") if kw is None else A.load_texts(first_hold, "holdout", **kw)); seal[name] = "FAILED: returned"
                except access.SealError as e:
                    seal[name] = f"refused as required ({e})"
            tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); json.dump({"final": True, "study": "bogus", "manifest_sha256": "0", "partition_sha256": "0", "cells": ["x"]}, tmp); tmp.close()
            try:
                next(A.load_texts(first_hold, "holdout", final_lock=tmp.name, study="bogus", cells=["x"])); seal["holdout_unregistered_lock"] = "FAILED: returned"
            except access.SealError as e:
                seal["holdout_unregistered_lock"] = f"refused as required ({e})"
        except Exception as e:
            seal["open_load"] = f"FAILED: {type(e).__name__}: {e}"
        seal["fixture_suite"] = "tools/test_seal.py (17 cases) must also pass; run separately"
    else:
        try:
            access.Access(units_dir, "0.0"); seal["bind_provisional"] = "FAILED: bound to a non-finalised map"
        except access.SealError as e:
            seal["bind_provisional"] = f"refused as required ({e})"
        seal["open_load"] = "deferred until finalisation"
    rules["P6"] = {"pass": (seal.get("open_load", "").startswith("OK") and all(v.startswith("refused") for k, v in seal.items() if k not in ("open_load", "fixture_suite"))) if partition_state["finalised"] else bool(seal.get("bind_provisional", "").startswith("refused")), "seal_test": seal}
    p7 = {k: v["holdout"] for k, v in cells.items()}
    rules["P7"] = {"pass_all_ten": all(v >= FLOOR_HOLDOUT for v in p7.values()), "holdout_eligible": p7, "failed_excluded_cells": [k for k, v in p7.items() if v < FLOOR_HOLDOUT]}
    rules["P8"] = {"expansion_needed": not (rules["P2"]["pass"] and rules["P3"]["pass"] and rules["P4"]["pass"] and rules["P7"]["pass_all_ten"]),
                   "order": {"wikipedia.<lang>": ["train-00001", "train-00002"], "stackexchange": ["-0011", "-0033"], "gutenberg": ["-0001", "-0005"], "news": "no further shard: a failed news count is a FAIL"}}
    summary = json.loads((units_dir / "partition_summary.json").read_text())
    core = rules["P1"]["pass"] and rules["P2"]["pass"] and rules["P3"]["pass"] and rules["P4"]["pass"] and rules["P5"]["pass"] and rules["P6"]["pass"]
    verdict = "PASS" if (core and rules["P7"]["pass_all_ten"] and partition_state["finalised"]) else ("PARTIAL" if core else "FAIL")
    if core and rules["P7"]["pass_all_ten"] and not partition_state["finalised"]:
        verdict = "PROVISIONAL (all rules pass; the partition is not finalised)"
    report = {"date_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "units_dir": str(units_dir), "partition": partition_state, "verdict": verdict, "n_units": int(len(U)), "n_clusters": int(U["is_representative"].sum()),
              "n_allowed_representatives": int(len(rep)), "flow": flow, "rules": rules, "cells": cells, "bins_by_source_lang": bins,
              "forum_sites_top": sites.head(30).to_dict(), "news_outlets": outlets.to_dict(), "partition_summary": summary, "loader_meta": {k: v for k, v in meta.items() if k not in ("files", "counts_per_file")}}
    pathlib.Path(out).write_text(json.dumps(report, indent=1, default=int))
    # Markdown
    print(f"\n**Verdict: {verdict}** (partition {partition_state['file']}; units {len(U):,}; clusters {int(U['is_representative'].sum()):,}; allowed representatives {len(rep):,})\n")
    print("| File | Lines | Unparseable | Parsed | Licence-excluded | Duplicates (non-rep.) | Representatives | Open | Held out | Reconciliation |\n|---|---|---|---|---|---|---|---|---|---|")
    for f, c in flow.items():
        if "EXCLUDED" in c:
            print(f"| {f} | {c['physical_lines']:,} | {c['unparseable_lines']} | {c['parsed_records']:,} | — | — | — | — | — | **EXCLUDED**: {c['EXCLUDED']} |"); continue
        r = recon[f]; rc = ("exact" if r["exact"] else "MISMATCH") + (f" to card {r['card_count']:,}" if "card_count" in r else (f" to footer {r['footer_rows']:,}" if "footer_rows" in r else "; parse-complete (partial shard, no external count)"))
        print(f"| {f} | {c['physical_lines']:,} | {c['unparseable_lines']} | {c['parsed_records']:,} | {c['licence_excluded']} | {c['non_representative_duplicates']:,} | {c['representatives_allowed']:,} | {c['open_representatives']:,} | {c['holdout_representatives']:,} | {rc} |")
    print("\n| Cell | Open eligible | Open, Qwen-eligible too | Held out eligible | Floor 2,500 |\n|---|---|---|---|---|")
    for k, v in cells.items():
        print(f"| {k} | {v['open']:,} | {v['open_qwen']:,} | {v['holdout']:,} | {'ok' if v['holdout'] >= FLOOR_HOLDOUT else 'FAILED/excluded'} |")
    print("\n| Rule | Pass | Detail |\n|---|---|---|")
    for k, v in rules.items():
        status = v.get("pass", v.get("pass_all_ten")) if k != "P8" else ("not needed" if not v["expansion_needed"] else "EXPANSION NEEDED")
        detail = {kk: vv for kk, vv in v.items() if kk not in ("pass", "pass_all_ten", "identities", "reconciliation", "seal_test", "order", "expansion_needed")}
        print(f"| {k} | {status} | {json.dumps(detail, default=int)} |")
    print("\nseal test:", json.dumps(seal, indent=1))
    print("\nforum sites with >= 200 open eligible threads:", int((sites >= SITE_MIN).sum()), "of", len(sites), "| top:", sites.head(8).to_dict())
    print("news outlets (open eligible@256):", outlets.to_dict())
    print("DONE audit", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    ud = args[0] if args and not args[0].startswith("--") else "outputs/corpora_units_v0.3"
    ver = args[args.index("--version") + 1] if "--version" in args else None
    out = args[args.index("--out") + 1] if "--out" in args else (f"outputs/corpora_audit_v{ver}.json" if ver else "outputs/corpora_audit_provisional.json")
    main(ud, out, ver)
