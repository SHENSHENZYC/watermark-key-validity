"""Run the provisional partition at candidate near-duplicate settings and summarise, metadata only, what each setting
merges (R02 F1, decision D4). Writes outputs/dedup_settings_comparison_<date>.json and prints a table.
Usage: .venv/bin/python -u tools/compare_dedup_settings.py <units_dir>
"""
import json, pathlib, subprocess, sys, datetime, collections
import numpy as np, pyarrow.parquet as pq, pandas as pd

SETTINGS = [("0.80/16x8", 16, 8, 0.80), ("0.70/32x4", 32, 4, 0.70), ("0.65/32x4", 32, 4, 0.65)]

def main(units_dir):
    units_dir = pathlib.Path(units_dir); out = {}
    meta = json.loads((units_dir / "counts.json").read_text())
    U = pd.concat([pq.read_table(units_dir / f["units_file"], columns=["canonical_id", "source", "lang", "group", "title", "n_tok_llama"]).to_pandas() for f in meta["files"] if not f.get("quarantined")], ignore_index=True).set_index("canonical_id")
    for name, bands, rows, thr in SETTINGS:
        r = subprocess.run([sys.executable, "-u", "tools/corpora_partition.py", str(units_dir), "--bands", str(bands), "--rows", str(rows), "--threshold", str(thr)], capture_output=True, text=True)
        if r.returncode != 0:
            print(name, "FAILED", r.stderr[-800:]); continue
        s = json.loads((units_dir / "partition_summary.json").read_text())
        P = pq.read_table(units_dir / "partition.parquet", columns=["canonical_id", "cluster_id", "cluster_size", "is_representative", "source", "lang", "partition", "allowed"]).to_pandas()
        multi = P[P["cluster_size"] > 1]
        sizes = collections.Counter(multi.groupby("cluster_id").size().tolist())
        # what gets merged: per source, the share of units in multi-member clusters; a metadata-only sample of merged pairs
        by_src = multi.groupby("source").size().to_dict()
        sample = []
        for cid, g in list(multi.groupby("cluster_id"))[:400]:
            if len(g) == 2:
                a, b = g["canonical_id"].tolist()
                ua, ub = U.loc[a], U.loc[b]
                sample.append({"source": ua["source"], "a": {"id": a[-60:], "group": ua["group"], "title": (ua["title"] or "")[:50], "tok": int(ua["n_tok_llama"])}, "b": {"id": b[-60:], "group": ub["group"], "title": (ub["title"] or "")[:50], "tok": int(ub["n_tok_llama"])}})
        rep = P[P["is_representative"] & P["allowed"]]
        out[name] = {"settings": {"bands": bands, "rows": rows, "threshold": thr}, "candidate_pairs": s["candidate_pairs"], "candidate_units": s["candidate_units"], "exact_dup_unions": s["exact_duplicate_unions"],
                     "near_dup_unions": s["near_duplicate_unions"], "confusion": s["confusion_est_vs_exact"], "n_clusters": s["n_clusters"], "cross_source_clusters": s["cross_source_clusters"],
                     "holdout_share": s["holdout_share_of_clusters"], "units_in_multi_clusters_by_source": by_src, "cluster_size_histogram": dict(sorted(sizes.items())[:12]),
                     "largest_cluster": max(sizes) if sizes else 1, "allowed_representatives": int(len(rep)), "exact_jaccard_hist": s["exact_jaccard_histogram_20bins"], "seconds": s["seconds"], "merged_pair_sample": sample[:40]}
        print(f"{name}: candidates {s['candidate_pairs']:,} | near-dup unions {s['near_duplicate_unions']:,} | clusters {s['n_clusters']:,} | cross-source {s['cross_source_clusters']} | largest cluster {max(sizes) if sizes else 1} | multi-cluster units by source {by_src} | {s['seconds']}s", flush=True)
    pathlib.Path(f"outputs/dedup_settings_comparison_{datetime.date.today().isoformat()}.json").write_text(json.dumps(out, indent=1, default=int))
    print("DONE compare", flush=True)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "outputs/corpora_units_v0.2")
