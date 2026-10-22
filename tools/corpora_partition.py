"""Stage 4 loader, step 2 (v2, after R02 round 1): duplicate clustering across all frozen sources with EXACT confirmation,
cluster identities and representatives, exposure forcing, the holdout assignment, and finalisation (audit §5).

Candidate pairs are EVERY distinct pair of units that share at least one LSH band of their MinHash signatures (bands × rows
configurable; no estimate-based prefilter, no first-member shortcut: R02 round 2, F8); each candidate pair is then confirmed
by the exact Jaccard similarity of the 5-gram shingle sets (64-bit fingerprints) of the FULL normalised texts, re-read for
the candidate units only (a preprocessing read permitted by audit P6; no scores, no examples). Files that fail acceptance
(decompression failure, accounting identity, unparseable lines, or the external card/footer reconciliation: R02 round 2,
F10) are excluded before clustering, with the reason recorded. Union–find over exact-duplicate and confirmed
near-duplicate edges gives the clusters.

Outputs in <units_dir>: partition.parquet (provisional), partition_summary.json; with --final <ver>: partition_v<ver>.parquet,
partition_v<ver>.sha256 and units_v<ver>.sha256 (the authoritative map and the units-metadata digest the sealed accessor
binds to); an existing final version is refused BEFORE any write and there is no overwrite option.
Usage: .venv/bin/python -u tools/corpora_partition.py <units_dir> [--bands 32 --rows 4 --threshold 0.65] [--final 0.3]
"""
import os, sys
if os.environ.get("PYTHONHASHSEED") != "20261009":
    os.execve(sys.executable, [sys.executable] + sys.argv, {**os.environ, "PYTHONHASHSEED": "20261009"})
import gzip, hashlib, json, pathlib, time
import numpy as np, pyarrow as pa, pyarrow.parquet as pq
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import corpora_loader as L

EXPOSURE = pathlib.Path("outputs/exposure_records_v0.1.json")
MANIFEST = pathlib.Path("outputs/corpora_manifest_v0.1.json")
CARD = {"news-dolma-0000.json.gz": 126673}   # external counts for the complete files (audit P5)


class UnionFind:
    def __init__(self, n):
        self.p = np.arange(n, dtype=np.int64)
    def find(self, i):
        p = self.p; root = i
        while p[root] != root:
            root = p[root]
        while p[i] != root:
            p[i], i = root, p[i]
        return root
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb); return True
        return False


def band_keys(S, b, rows, mult):
    block = S[:, b * rows:(b + 1) * rows].astype(np.uint64)
    with np.errstate(over="ignore"):
        return (block * mult[None, :]).sum(axis=1)


def full_shingles(text):
    """Exact-confirmation domain: 5-gram shingles (word or character by the loader's rule) of the FULL normalised text."""
    norm = L.normalise(text)
    if L.cjk_share(norm) >= 0.30:
        s = norm.replace(" ", ""); sh = {s[i:i + 5] for i in range(len(s) - 4)} if len(s) >= 5 else set()
    else:
        words = norm.split(" ")
        if len(words) >= 5 and norm:
            sh = {" ".join(words[i:i + 5]) for i in range(len(words) - 4)}
        else:
            s = norm.replace(" ", ""); sh = {s[i:i + 5] for i in range(len(s) - 4)} if len(s) >= 5 else set()
    return np.unique(np.fromiter((hash(x) & L.MASK64 for x in sh), dtype=np.uint64, count=len(sh)))


def file_acceptance(meta):
    """Per-file acceptance before clustering (audit P5; R02 F10): a file is accepted only if it has no decompression failure,
    its accounting identity holds, it has no unparseable line, and (where an external count exists) it reconciles exactly
    to the card count or the Parquet footer. Returns {path: reason} for the rejected files."""
    rejected = {}
    for f in meta["files"]:
        c = meta["counts_per_file"][f["path"]]
        if f.get("quarantined"):
            rejected[f["path"]] = "quarantined by the loader: " + str(f["quarantined"]); continue
        if "decompression_failure" in c:
            rejected[f["path"]] = "decompression failure: " + str(c["decompression_failure"]); continue
        if c["physical_lines"] != c["parsed_records"] + c["unparseable_lines"]:
            rejected[f["path"]] = "accounting identity failed"; continue
        if c["unparseable_lines"] != 0:
            rejected[f["path"]] = f"{c['unparseable_lines']} unparseable lines"; continue
        if f["path"] in CARD and c["parsed_records"] != CARD[f["path"]]:
            rejected[f["path"]] = f"card count {CARD[f['path']]} != parsed {c['parsed_records']}"; continue
        if "footer_rows" in c and c["parsed_records"] != c["footer_rows"]:
            rejected[f["path"]] = f"footer rows {c['footer_rows']} != parsed {c['parsed_records']}"; continue
    return rejected


def confirm_pair(A, B):
    """Exact Jaccard of two sorted unique uint64 shingle-fingerprint arrays (the production confirmation; the fixture calls it)."""
    if len(A) == 0 or len(B) == 0:
        return 0.0
    inter = len(np.intersect1d(A, B, assume_unique=True))
    return inter / (len(A) + len(B) - inter)


def candidate_pairs(Ssub, bands, rows, mult, log=None):
    """Every distinct pair of signature rows that shares at least one band (production candidate logic; the fixture reuses it)."""
    pairs, n_buckets, max_bucket, n_bucket_pairs = set(), 0, 0, 0
    for b in range(bands):
        keys = band_keys(Ssub, b, rows, mult)
        order = np.argsort(keys, kind="stable"); ks = keys[order]
        starts = np.flatnonzero(np.r_[True, ks[1:] != ks[:-1]]); ends = np.r_[starts[1:], len(ks)]
        for a, e in zip(starts, ends):
            g = e - a
            if g < 2:
                continue
            n_buckets += 1; max_bucket = max(max_bucket, int(g)); n_bucket_pairs += g * (g - 1) // 2
            G = np.sort(order[a:e]); ii, jj = np.triu_indices(g, 1)
            pairs.update(zip(G[ii].tolist(), G[jj].tolist()))
        if log:
            log(f"  band {b}: buckets {n_buckets}, largest {max_bucket}, distinct candidate pairs so far {len(pairs)}")
    return pairs, n_buckets, max_bucket, n_bucket_pairs


def _preprocessing_text_reader(wanted_by_file):
    """Read the texts of the given (file -> {pos: unit_index}) units from the raw files. Preprocessing only (P6): used
    here for exact duplicate confirmation before the partition is final; scientific loads go through corpora_access."""
    man = json.loads(MANIFEST.read_text())
    paths = {e["path"]: pathlib.Path(e["local_path"]) for e in man["entries"].values() if e.get("status") == "OK"}
    for file, wanted in wanted_by_file.items():
        local = paths[file]
        if local.suffix == ".parquet":
            pf = pq.ParquetFile(local); row = 0
            for rg in range(pf.metadata.num_row_groups):
                n = pf.metadata.row_group(rg).num_rows
                hit = [p for p in wanted if row <= p < row + n]
                if hit:
                    col = pf.read_row_group(rg, columns=["text"]).column("text").to_pylist()
                    for p in hit:
                        yield wanted[p], col[p - row]
                row += n
        else:
            remaining = dict(wanted)
            with gzip.open(local, "rt", encoding="utf-8") as fh:
                for n, line in enumerate(fh, 1):
                    if n in remaining:
                        yield remaining.pop(n), json.loads(line)["text"]
                        if not remaining:
                            break


def main(units_dir, bands, rows, threshold, final=None):
    t0 = time.time()
    units_dir = pathlib.Path(units_dir)
    assert bands * rows <= L.N_PERM, "bands × rows must not exceed the signature length"
    if final and (units_dir / f"partition_v{final}.parquet").exists():
        raise SystemExit(f"REFUSED: partition_v{final}.parquet exists; a finalised map is never overwritten (use a new version number)")
    meta = json.loads((units_dir / "counts.json").read_text())
    rejected = file_acceptance(meta)
    files = [f for f in meta["files"] if f["path"] not in rejected]
    tables, sigs, offsets = [], [], {}
    for f in files:
        tables.append(pq.read_table(units_dir / f["units_file"], columns=["source", "lang", "file", "pos", "rec_id", "canonical_id", "text_sha256", "sig_file", "sig_row", "allowed", "provenance", "group"]))
        S = np.load(units_dir / f["signatures_file"])
        stem = f["signatures_file"][len("signatures__"):-len(".npy")]
        offsets[stem] = sum(s.shape[0] for s in sigs); sigs.append(S)
    U = pa.concat_tables(tables).to_pandas()
    S = np.concatenate(sigs) if sigs else np.zeros((0, L.N_PERM), np.uint32)
    N = len(U)
    off = U["sig_file"].map(offsets)
    assert not off.isna().any(), "signature offsets missing for " + str(sorted(set(U["sig_file"][off.isna()])))
    sig_global = np.where(U["sig_row"].values >= 0, U["sig_row"].values + off.astype(np.int64).values, -1)
    print(f"loaded {N} units from {len(files)} files ({len(meta['files']) - len(files)} quarantined), {S.shape[0]} signatures ({time.time()-t0:.0f}s)", flush=True)
    uf = UnionFind(N)
    # 1. exact duplicates by the full normalised-text hash
    n_exact = 0
    sha = U["text_sha256"].values; order = np.argsort(sha, kind="stable"); ss = sha[order]
    starts = np.flatnonzero(np.r_[True, ss[1:] != ss[:-1]]); ends = np.r_[starts[1:], len(ss)]
    for a, b in zip(starts, ends):
        if b - a > 1:
            m = order[a:b]
            for x in m[1:]:
                n_exact += uf.union(int(m[0]), int(x))
    print(f"exact-duplicate unions: {n_exact} ({time.time()-t0:.0f}s)", flush=True)
    # 2. LSH candidate pairs: every distinct pair sharing a band (no prefilter)
    has = sig_global >= 0; idx_units = np.flatnonzero(has); Ssub = S[sig_global[idx_units]]
    rng = np.random.default_rng(20261009)
    mult = (rng.integers(1, 2**62, size=rows, dtype=np.uint64) * np.uint64(2) + np.uint64(1))
    pairs_local, n_buckets, max_bucket, n_bucket_pairs = candidate_pairs(Ssub, bands, rows, mult, log=lambda m: print(m + f" ({time.time()-t0:.0f}s)", flush=True))
    pairs = {(int(idx_units[i]), int(idx_units[j])) for i, j in pairs_local}
    # 3. exact confirmation on the full normalised texts of the candidate units
    cand_units = sorted({i for p in pairs for i in p})
    wanted_by_file = {}
    for i in cand_units:
        wanted_by_file.setdefault(U["file"].values[i], {})[int(U["pos"].values[i])] = i
    shingle_sets = {}
    for i, text in _preprocessing_text_reader(wanted_by_file):
        shingle_sets[i] = full_shingles(text)
    print(f"exact confirmation: {len(pairs)} candidate pairs over {len(cand_units)} units; shingle sets built ({time.time()-t0:.0f}s)", flush=True)
    n_conf, n_above, confusion = 0, 0, {"est>=T&exact>=T": 0, "est>=T&exact<T": 0, "est<T&exact>=T": 0, "est<T&exact<T": 0}
    exact_hist = np.zeros(20, dtype=np.int64)
    for (i, j) in pairs:
        exact = confirm_pair(shingle_sets[i], shingle_sets[j])
        est = float((S[sig_global[i]] == S[sig_global[j]]).mean())   # recorded for the confusion table only
        exact_hist[min(19, int(exact * 20))] += 1
        confusion[("est>=T" if est >= threshold else "est<T") + "&" + ("exact>=T" if exact >= threshold else "exact<T")] += 1
        if exact >= threshold:
            n_above += 1; n_conf += uf.union(i, j)
    print(f"pairs at or above the exact threshold {threshold}: {n_above}; union operations that joined components: {n_conf}; confusion {confusion} ({time.time()-t0:.0f}s)", flush=True)
    # 4. clusters, identities, representatives
    roots = np.array([uf.find(i) for i in range(N)], dtype=np.int64)
    cid = U["canonical_id"].values.astype(str)
    tie = np.array([f"{s}|{r}|{h}" for s, r, h in zip(U["source"].values, U["rec_id"].values, U["text_sha256"].values)])
    order = np.lexsort((tie, cid, roots))
    cluster_id = np.empty(N, dtype=object); is_rep = np.zeros(N, dtype=bool); size = np.zeros(N, dtype=np.int64)
    rs = roots[order]; starts = np.flatnonzero(np.r_[True, rs[1:] != rs[:-1]]); ends = np.r_[starts[1:], N]
    cross = 0
    for a, e in zip(starts, ends):
        m = order[a:e]; cluster_id[m] = cid[m[0]]; is_rep[m[0]] = True; size[m] = e - a
        if e - a > 1 and len(set(U["source"].values[m])) > 1:
            cross += 1
    # 5. exposure forcing and assignment
    exp = json.loads(EXPOSURE.read_text()); hit = np.zeros(N, dtype=bool)
    for rule in exp["rules"]:
        m = U["source"].values == rule["source"]
        vals = {rule["values_prefix"] + str(l) for l in rule["lines"]} if "values_prefix" in rule else set(rule["values"])
        hit |= m & np.isin(U[rule["field"]].values.astype(str), list(vals))
    forced = np.isin(roots, np.unique(roots[hit]))
    h = np.array([int(hashlib.sha256(c.encode("utf-8")).hexdigest()[:16], 16) % 5 == 0 for c in cluster_id], dtype=bool)
    partition = np.where(h & ~forced, "holdout", "open")
    out = pa.Table.from_pydict({"source": U["source"].values, "lang": U["lang"].values, "file": U["file"].values, "pos": U["pos"].values, "rec_id": U["rec_id"].values,
                                "canonical_id": cid, "cluster_id": cluster_id.astype(str), "cluster_size": size, "is_representative": is_rep,
                                "exposure_hit": hit, "forced_open": forced, "partition": partition, "allowed": U["allowed"].values})
    pq.write_table(out, units_dir / "partition.parquet")
    import pandas as pd
    df = pd.DataFrame({"source": U["source"].values, "lang": U["lang"].values, "rep": is_rep, "part": partition})
    summary = {"n_units": N, "n_files": len(files), "n_quarantined_files": len(meta["files"]) - len(files), "n_with_signature": int(has.sum()), "exact_duplicate_unions": n_exact,
               "rejected_files": rejected, "lsh": {"bands": bands, "rows": rows, "buckets_with_2plus": n_buckets, "largest_bucket": max_bucket, "bucket_pair_occurrences_across_bands": n_bucket_pairs, "prefilter": "none: every distinct band-sharing pair is exactly confirmed"},
               "candidate_pairs_distinct": len(pairs), "candidate_units": len(cand_units), "pairs_at_or_above_threshold": n_above, "near_duplicate_unions": n_conf, "confusion_est_vs_exact_record_only": confusion,
               "exact_jaccard_histogram_20bins": exact_hist.tolist(), "threshold_exact_jaccard": threshold, "n_clusters": int(is_rep.sum()), "cross_source_clusters": cross,
               "exposure_hits": int(hit.sum()), "forced_open_units": int(forced.sum()), "holdout_share_of_clusters": float(np.mean(partition[is_rep] == "holdout")),
               "by_source_lang": {f"{s}/{l}": {"clusters": int(len(g)), "holdout": int((g.part == "holdout").sum()), "holdout_share": float((g.part == "holdout").mean())} for (s, l), g in df[df.rep].groupby(["source", "lang"])},
               "assignment": "holdout iff int(sha256(cluster_id)[:16],16) % 5 == 0 and the cluster holds no exposure record", "seconds": round(time.time() - t0), "final_version": None}
    if final:
        fp = units_dir / f"partition_v{final}.parquet"
        if fp.exists():
            raise SystemExit(f"REFUSED: {fp} exists; a finalised map is never overwritten")
        pq.write_table(out, fp)
        digest = hashlib.sha256(fp.read_bytes()).hexdigest()
        (units_dir / f"partition_v{final}.sha256").write_text(digest + "\n")
        uh = hashlib.sha256()
        for f in meta["files"]:   # the units-metadata digest the lock also binds (R02 F9): every units file plus counts.json
            uh.update((units_dir / f["units_file"]).read_bytes())
        uh.update((units_dir / "counts.json").read_bytes())
        (units_dir / f"units_v{final}.sha256").write_text(uh.hexdigest() + "\n")
        summary["final_version"] = final; summary["partition_sha256"] = digest; summary["units_sha256"] = uh.hexdigest()
        print(f"FINALISED partition_v{final}.parquet sha256 {digest}; units digest {uh.hexdigest()}", flush=True)
    (units_dir / "partition_summary.json").write_text(json.dumps(summary, indent=1, default=int))
    print(json.dumps({k: v for k, v in summary.items() if k not in ("by_source_lang", "exact_jaccard_histogram_20bins")}, indent=1, default=int), flush=True)
    print("DONE partition", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    g = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
    main(a[0] if a and not a[0].startswith("--") else "outputs/corpora_units_v0.2", g("--bands", 32), g("--rows", 4), g("--threshold", 0.65), a[a.index("--final") + 1] if "--final" in a else None)
