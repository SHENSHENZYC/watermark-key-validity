"""Stage 4 freeze: download the decided null corpora (audit §3, decision D2) pinned to their Hub revisions, one file at a
time, and write a hashed manifest. Raw files go to research/corpora/data/<source>/ (git-ignored).

Each manifest entry records repo id, path, revision, retrieval UTC time, local byte size, local SHA-256 and the Hub's own
LFS SHA-256 and size (from get_paths_info) as the independent checksum; a mismatch is recorded and the file is marked
EXCLUDED, never patched. Nothing is parsed here. Terms: research/corpora/TERMS_OF_USE_CHECK.md.
Usage: .venv/bin/python tools/freeze_corpora.py            (the initial selection)
       .venv/bin/python tools/freeze_corpora.py --expand <stackexchange|gutenberg|wikipedia.<lang>>   (ONE next shard in the P8 order)
"""
import datetime, hashlib, json, pathlib, sys, time
from huggingface_hub import HfApi, hf_hub_download

DATA = pathlib.Path("research/corpora/data")
MANIFEST = pathlib.Path("outputs/corpora_manifest_v0.1.json")
PACE_S = 2.0

# (source, repo id, pinned revision prefix, files) -- the full revision SHA is taken from the census file (resolve_revisions);
# initial selection: audit §3; expansion order: audit P8
SOURCES = {
    "news": ("common-pile/news_filtered", "59aaa8f104e1", ["news-dolma-0000.json.gz", "README.md"]),
    "stackexchange": ("common-pile/stackexchange_filtered", "c0ac7373830c", ["stackexchange-dolma-0000.json.gz", "stackexchange-dolma-0022.json.gz", "README.md"]),
    "gutenberg": ("common-pile/project_gutenberg_filtered", "3cdf6879c807", ["project_gutenberg-dolma-0000.json.gz", "project_gutenberg-dolma-0003.json.gz", "project_gutenberg-dolma-0007.json.gz", "project_gutenberg-dolma-0011.json.gz", "README.md"]),
    "wikipedia": ("wikimedia/wikipedia", "b04c8d1ceb2f", ["20231101.en/train-00000-of-00041.parquet", "20231101.de/train-00000-of-00020.parquet", "20231101.ru/train-00000-of-00021.parquet",
                                                           "20231101.ar/train-00000-of-00007.parquet", "20231101.zh/train-00000-of-00006.parquet", "20231101.ja/train-00000-of-00015.parquet", "README.md"]),
}
EXPANSION = {  # P8: fixed order, nothing else
    "stackexchange": ["stackexchange-dolma-0011.json.gz", "stackexchange-dolma-0033.json.gz"],
    "gutenberg": ["project_gutenberg-dolma-0001.json.gz", "project_gutenberg-dolma-0005.json.gz"],
    "wikipedia.en": ["20231101.en/train-00001-of-00041.parquet", "20231101.en/train-00002-of-00041.parquet"],
    "wikipedia.de": ["20231101.de/train-00001-of-00020.parquet", "20231101.de/train-00002-of-00020.parquet"],
    "wikipedia.ru": ["20231101.ru/train-00001-of-00021.parquet", "20231101.ru/train-00002-of-00021.parquet"],
    "wikipedia.ar": ["20231101.ar/train-00001-of-00007.parquet", "20231101.ar/train-00002-of-00007.parquet"],
    "wikipedia.zh": ["20231101.zh/train-00001-of-00006.parquet", "20231101.zh/train-00002-of-00006.parquet"],
    "wikipedia.ja": ["20231101.ja/train-00001-of-00015.parquet", "20231101.ja/train-00002-of-00015.parquet"],
}


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p, chunk=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def resolve_revisions(api):
    """The census stored full SHAs; take them from the census file so that short prefixes above are never used."""
    census = json.loads(sorted(pathlib.Path("outputs").glob("corpora_census_*.json"))[-1].read_text())
    full = {}
    for src, (repo, rev, files) in SOURCES.items():
        sha = census["datasets"][repo]["sha"]
        assert sha.startswith(rev[:12]), (repo, sha, rev)
        full[src] = sha
    return full


def main(expand=None):
    api = HfApi()
    man = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"terms": "research/corpora/TERMS_OF_USE_CHECK.md", "audit": "research/corpora/CORPORA_AUDIT_v0.1.md", "entries": {}}
    full = resolve_revisions(api)
    jobs = []
    if not expand:
        for src, (repo, rev, files) in SOURCES.items():
            for f in files:
                jobs.append((src, repo, full[src], f))
    if expand:   # --expand <key>: one shard only, the next in the P8 order that is not yet frozen (R02 F5)
        base = expand.split(".")[0]
        repo, rev, _ = SOURCES[base]
        done = {e["path"] for e in man["entries"].values() if e.get("status") == "OK"}
        nxt = [f for f in EXPANSION[expand] if f not in done]
        if not nxt:
            print(f"P8 cap reached for {expand}: no further shard may be added", flush=True); return
        jobs = [(base, repo, full[base], nxt[0])]
        print(f"expansion step for {expand}: fetching {nxt[0]} (remaining after it: {len(nxt) - 1})", flush=True)
    for src, repo, rev, f in jobs:
        key = f"{repo}@{rev[:12]}:{f}"
        if key in man["entries"] and man["entries"][key].get("status") == "OK":
            print("skip (frozen)", key, flush=True); continue
        t0 = time.time()
        entry = {"source": src, "repo_id": repo, "revision": rev, "path": f, "retrieved_utc": now()}
        try:
            info = api.get_paths_info(repo, [f], repo_type="dataset", revision=rev)
            if not info:
                raise FileNotFoundError(f"{f} not in {repo}@{rev}")
            i = info[0]
            entry["hub_size"] = getattr(i, "size", None)
            entry["hub_lfs_sha256"] = getattr(getattr(i, "lfs", None), "sha256", None)
            local = hf_hub_download(repo, f, repo_type="dataset", revision=rev, local_dir=str(DATA / src))
            p = pathlib.Path(local)
            entry["local_path"] = str(p.relative_to(pathlib.Path.cwd())) if p.is_absolute() else str(p)
            entry["bytes"] = p.stat().st_size
            entry["sha256"] = sha256_file(p)
            ok_size = entry["hub_size"] is None or entry["hub_size"] == entry["bytes"]
            ok_sha = entry["hub_lfs_sha256"] is None or entry["hub_lfs_sha256"] == entry["sha256"]
            entry["status"] = "OK" if (ok_size and ok_sha) else "EXCLUDED: hub size or LFS sha256 mismatch"
            print(entry["status"], key, entry["bytes"], "bytes", f"{time.time()-t0:.0f}s", flush=True)
        except Exception as e:  # record the gap; never retry in a loop
            entry["status"] = f"FAILED: {type(e).__name__}: {str(e)[:200]}"
            print(entry["status"], key, flush=True)
        man["entries"][key] = entry
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=True))
        time.sleep(PACE_S)
    n_ok = sum(1 for e in man["entries"].values() if e.get("status") == "OK")
    print(f"DONE: {n_ok} OK of {len(man['entries'])} entries; manifest {MANIFEST}", flush=True)


if __name__ == "__main__":
    exp = sys.argv[sys.argv.index("--expand") + 1] if "--expand" in sys.argv else None
    main(exp)
