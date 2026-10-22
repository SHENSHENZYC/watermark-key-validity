"""Stage 4 loader, step 1: parse the frozen files, normalise licences, count tokens under both pinned tokenizers,
and compute MinHash signatures. Writes metadata only (no text) to outputs/corpora_units_v0.1/.

Rules implemented: research/corpora/CORPORA_AUDIT_v0.1.md §§3–5 (units, allow-list P1, eligibility, shingling).
Deterministic: PYTHONHASHSEED is forced to 20261009 (shingle hashes use str.hash); MinHash permutations from PCG64(20261009).
Usage: .venv/bin/python -u tools/corpora_loader.py [--limit N] [--sources news,stackexchange,gutenberg,wikipedia]
"""
import os, sys
HASHSEED = "20261009"
if os.environ.get("PYTHONHASHSEED") != HASHSEED:  # re-exec with a fixed hash seed so that shingle hashes are reproducible
    os.execve(sys.executable, [sys.executable] + sys.argv, {**os.environ, "PYTHONHASHSEED": HASHSEED, "TOKENIZERS_PARALLELISM": "true"})

import datetime, gzip, hashlib, json, pathlib, re, time, unicodedata
import numpy as np
import pyarrow as pa, pyarrow.parquet as pq
from multiprocessing import Pool

DATA = pathlib.Path("research/corpora/data")
OUT = pathlib.Path(os.environ.get("CORPORA_UNITS_DIR", "outputs/corpora_units_v0.2"))   # v0.1 (2026-10-09) is the superseded record; override for test runs only
MANIFEST = pathlib.Path("outputs/corpora_manifest_v0.1.json")
TOKENIZERS = {"llama": ("meta-llama/Llama-3.2-1B", "4e20de362430cd3b72f300e6b0f18e50e7166e08"),
              "qwen": ("Qwen/Qwen2.5-1.5B", "8faed761d45a263340a0528343f099c05c9a4323")}
TOK_CAP = {"news": 12000, "stackexchange": 12000, "wikipedia": 12000, "gutenberg": 24000}   # characters tokenised (counts censored above)
SHINGLE_CAP_WORD, SHINGLE_CAP_CHAR = 20000, 8000   # characters shingled (normalised text)
N_PERM, LSH_BANDS, LSH_ROWS = 128, 16, 8
BOOK_SKIP = 1000   # the book window starts at token 1,000 (audit §3)
NONEN_SITES = re.compile(r"^(es|ru|ja|pt)\.stackoverflow\.com$|^rus\.stackexchange\.com$")

# --- licence normalisation (audit P1, R02 F3): a CLOSED enumeration of the complete label strings observed in the frozen
# data (17 combinations over 2,617,347 units, enumerated 2026-10-09); any other string, None, or a malformed schema is OTHER
# and excluded. No pattern matching: a label that is not byte-identical to an entry here is not admitted. ---
_CC_LABELS = {
    "Creative Commons - Attribution - https://creativecommons.org/licenses/by/4.0/": "cc-by-4.0",
    "Creative Commons - Attribution Share-Alike - https://creativecommons.org/licenses/by-sa/2.5/": "cc-by-sa-2.5",
    "Creative Commons - Attribution Share-Alike - https://creativecommons.org/licenses/by-sa/3.0/": "cc-by-sa-3.0",
    "Creative Commons - Attribution Share-Alike - https://creativecommons.org/licenses/by-sa/4.0/": "cc-by-sa-4.0",
    "Public Domain": "public-domain",
}
WIKI_LABEL = "project:CC BY-SA 3.0/4.0 + GFDL (inherited)"
ALLOWED_IDENTITIES = {"cc-by-4.0", "cc-by-sa-2.5", "cc-by-sa-3.0", "cc-by-sa-4.0", "public-domain"}

def licence_identity(label):
    if isinstance(label, str) and label in _CC_LABELS:
        return _CC_LABELS[label]
    return "OTHER:" + (repr(label)[:80] if label is not None else "None")

def allowed(identity):
    return identity in ALLOWED_IDENTITIES

# --- text normalisation and shingles (audit §5.2) ---
_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)

def normalise(text):
    t = unicodedata.normalize("NFC", text).lower()
    t = _PUNCT.sub(" ", t)
    return _WS.sub(" ", t).strip()

_CJK = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uff00-\uffef]")

def cjk_share(norm):
    head = norm.replace(" ", "")[:2000]   # the first 2,000 non-space characters (audit §5.2)
    return (len(_CJK.findall(head)) / len(head)) if head else 0.0

def shingles(norm):
    """Audit §5.2 segmentation rule: character 5-grams for CJK-dominant text (>= 30% CJK characters); otherwise word
    5-grams when the normalised text has >= 5 whitespace-delimited words; otherwise character 5-grams; fewer than 5
    units of either kind gives no shingles (a singleton for near-duplicate purposes)."""
    if cjk_share(norm) >= 0.30:
        s = norm[:SHINGLE_CAP_CHAR].replace(" ", "")
        return ("char", {s[i:i + 5] for i in range(len(s) - 4)}) if len(s) >= 5 else ("none", set())
    words = norm[:SHINGLE_CAP_WORD].split(" ")
    if len(words) >= 5 and len(norm) > 0:
        return "word", {" ".join(words[i:i + 5]) for i in range(len(words) - 4)}
    s = norm[:SHINGLE_CAP_CHAR].replace(" ", "")
    if len(s) >= 5:
        return "char", {s[i:i + 5] for i in range(len(s) - 4)}
    return "none", set()

_rng = np.random.default_rng(int(HASHSEED))
PERM_A = (_rng.integers(1, 2**63, size=N_PERM, dtype=np.uint64) * np.uint64(2) + np.uint64(1))   # odd multipliers
PERM_B = _rng.integers(0, 2**63, size=N_PERM, dtype=np.uint64)
MASK64 = (1 << 64) - 1

def minhash(shingle_set):
    x = np.fromiter((hash(s) & MASK64 for s in shingle_set), dtype=np.uint64, count=len(shingle_set))
    with np.errstate(over="ignore"):
        h = (x[:, None] * PERM_A[None, :] + PERM_B[None, :]) >> np.uint64(32)
    return h.min(axis=0).astype(np.uint32)

def worker(args):
    """One record: normalise, exact hash, shingles, minhash. Returns metadata only."""
    idx, text = args
    norm = normalise(text)
    kind, sh = shingles(norm)
    sig = minhash(sh) if sh else None
    return idx, hashlib.sha256(norm.encode("utf-8")).hexdigest(), kind, len(sh), sig

# --- record iteration per source ---
def frozen_files(source):
    man = json.loads(MANIFEST.read_text())
    out = []
    for k, e in man["entries"].items():
        if e["source"] == source and e.get("status") == "OK" and not e["path"].endswith("README.md"):
            out.append((e["path"], pathlib.Path(e["local_path"])))
    return sorted(out)

def iter_dolma(path, counts, limit=None):
    """Yield (line_no, record) from a gzipped JSON-lines file; count physical lines and unparseable ones."""
    n = 0
    try:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                counts["physical_lines"] += 1
                try:
                    r = json.loads(line)
                except Exception:
                    counts["unparseable_lines"] += 1
                    continue
                if not isinstance(r, dict) or not isinstance(r.get("text"), str):
                    counts["unparseable_lines"] += 1
                    continue
                counts["parsed_records"] += 1
                yield n, r
                if limit and counts["parsed_records"] >= limit:
                    return
    except (OSError, EOFError) as e:
        counts["decompression_failure"] = f"{type(e).__name__}: {e} after line {n}"

def iter_parquet(path, counts, limit=None):
    pf = pq.ParquetFile(path)
    counts["footer_rows"] = pf.metadata.num_rows
    row = 0
    for rg in range(pf.metadata.num_row_groups):
        t = pf.read_row_group(rg, columns=["id", "url", "title", "text"]).to_pylist()
        for r in t:
            counts["physical_lines"] += 1
            if not isinstance(r.get("text"), str):
                counts["unparseable_lines"] += 1; row += 1; continue
            counts["parsed_records"] += 1
            yield row, r
            row += 1
            if limit and counts["parsed_records"] >= limit:
                return

def unit_from(source, lang, path, pos, r):
    md = r.get("metadata") or {}
    if source == "wikipedia":
        label, ids = WIKI_LABEL, ["cc-by-sa-3.0"]
        return {"source": source, "lang": lang, "file": path, "pos": pos, "rec_id": str(r.get("id")), "canonical_id": f"wiki:{lang}:{r.get('id')}",
                "url": r.get("url"), "group": lang, "licence_label": label, "licence_identity": ids[0], "allowed": True, "created": "2023-11-01 (dump)",
                "provenance": f"{path}:{pos}", "title": r.get("title")}
    label = md.get("license")
    ids = [licence_identity(label)]
    if source == "stackexchange":
        al = md.get("all_licenses")
        if not isinstance(al, list) or len(al) == 0:   # the component list must exist and be non-empty: no fallback to `license`
            ids = ["SCHEMA:all_licenses missing or empty"]
        else:
            ids = [licence_identity(x) for x in al]
    ok = len(ids) > 0 and all(allowed(i) for i in ids)
    if source == "gutenberg":
        ok = ok and ids == ["public-domain"]
    url = md.get("url"); cid = url if url else f"{source}:{r.get('id')}"
    group = md.get("site") if source == "stackexchange" else (r.get("source") if source == "news" else "books")
    lang2 = lang
    if source == "stackexchange" and group and NONEN_SITES.match(group):
        lang2 = "non-en"
    if source == "gutenberg" and md.get("language") not in (None, "en"):
        lang2 = str(md.get("language"))
    return {"source": source, "lang": lang2, "file": path, "pos": pos, "rec_id": str(r.get("id")), "canonical_id": cid, "url": url, "group": group,
            "licence_label": label if source != "stackexchange" else "|".join(str(x) for x in (md.get("all_licenses") if isinstance(md.get("all_licenses"), list) else [])),
            "licence_identity": "|".join(str(i) for i in ids), "allowed": bool(ok), "created": None if r.get("created") is None else str(r.get("created"))[:40],
            "provenance": md.get("provenance") or f"{path}:{pos}", "title": md.get("title")}

def load_tokenizers():
    from transformers import AutoTokenizer
    toks, prov = {}, {}
    for k, (repo, rev) in TOKENIZERS.items():
        try:
            toks[k] = AutoTokenizer.from_pretrained(repo, revision=rev, local_files_only=True)
        except Exception:
            toks[k] = AutoTokenizer.from_pretrained(repo, revision=rev)
        toks[k + "_backend"] = toks[k].backend_tokenizer
        snap = pathlib.Path(os.path.expanduser("~/.cache/huggingface/hub")) / f"models--{repo.replace('/', '--')}" / "snapshots" / rev
        prov[k] = {"repo": repo, "revision": rev, "files_sha256": {f: hashlib.sha256((snap / f).read_bytes()).hexdigest() for f in ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json") if (snap / f).exists()},
                   "vocab_size": len(toks[k]), "add_special_tokens": False, "note": "counts are of the capped character prefix (TOK_CAP) without special tokens; tok_censored marks truncation"}
    toks["_provenance"] = prov
    return toks

def count_tokens(backend, texts):
    encs = backend.encode_batch(texts, add_special_tokens=False)
    return [len(e.ids) for e in encs]

def main(limit=None, sources=("news", "stackexchange", "gutenberg", "wikipedia"), only=None):
    OUT.mkdir(parents=True, exist_ok=True)
    toks = load_tokenizers()
    counts_all, n_units_total, n_sigs_total, files_out = {}, 0, 0, []
    prev = json.loads((OUT / "counts.json").read_text()) if only and (OUT / "counts.json").exists() else None
    if prev:   # --only: keep every earlier file's record and add the one new file (R02 F5)
        counts_all, files_out = dict(prev["counts_per_file"]), list(prev["files"])
        n_units_total, n_sigs_total = prev["n_units"], prev["n_signatures"]
        assert only not in counts_all, f"{only} is already loaded"
    t_start = time.time()
    with Pool(6) as pool:
        for source in sources:
            for fi, (path, local) in enumerate(frozen_files(source)):
                if only and path != only:
                    continue
                lang = path.split("/")[0].split(".")[1] if source == "wikipedia" else "en"
                counts = {"physical_lines": 0, "unparseable_lines": 0, "parsed_records": 0}
                counts_all[path] = counts
                it = iter_parquet(local, counts, limit) if local.suffix == ".parquet" else iter_dolma(local, counts, limit)
                cap = TOK_CAP[source]
                stem = f"{source}__{path.replace('/', '__')}"
                writer, sigs, n_rows = None, [], 0
                batch = []
                print(f"start {path} ({datetime.datetime.now(datetime.timezone.utc):%H:%M:%S}Z)", flush=True)
                def flush(batch, writer, sigs, n_rows):
                    units = [unit_from(source, lang, path, pos, r) for pos, r in batch]
                    texts = [r["text"] for _, r in batch]
                    capped = [t[:cap] for t in texts]
                    nl = count_tokens(toks["llama_backend"], capped); nq = count_tokens(toks["qwen_backend"], capped)
                    for u, t, c, a, b in zip(units, texts, capped, nl, nq):
                        u["n_chars"] = len(t); u["tok_censored"] = len(t) > len(c); u["n_tok_llama"] = a; u["n_tok_qwen"] = b
                    for idx, sha, kind, nsh, sig in pool.imap(worker, list(enumerate(texts)), chunksize=64):
                        u = units[idx]; u["text_sha256"] = sha; u["shingle_kind"] = kind; u["n_shingles"] = nsh; u["sig_file"] = stem
                        if sig is None:
                            u["sig_row"] = -1
                        else:
                            u["sig_row"] = len(sigs); sigs.append(sig)
                    table = pa.Table.from_pylist(units)
                    if writer is None:
                        writer = pq.ParquetWriter(OUT / f"units__{stem}.parquet", table.schema)
                    writer.write_table(table)
                    return writer, n_rows + len(units)
                for pos, r in it:
                    batch.append((pos, r))
                    if len(batch) >= 2000:
                        writer, n_rows = flush(batch, writer, sigs, n_rows); batch = []
                        if counts["parsed_records"] % 50000 == 0:
                            print(f"  {path}: {counts['parsed_records']} records, {time.time()-t_start:.0f}s", flush=True)
                if batch:
                    writer, n_rows = flush(batch, writer, sigs, n_rows)
                if writer is not None:
                    writer.close()
                np.save(OUT / f"signatures__{stem}.npy", np.stack(sigs) if sigs else np.zeros((0, N_PERM), dtype=np.uint32))
                entry = {"path": path, "units_file": f"units__{stem}.parquet", "signatures_file": f"signatures__{stem}.npy", "n_units": n_rows, "n_signatures": len(sigs),
                         "accounting_identity": counts["physical_lines"] == counts["parsed_records"] + counts["unparseable_lines"]}
                if "decompression_failure" in counts or not entry["accounting_identity"]:   # F4: quarantine the whole file; nothing from it enters the partition or the counts
                    for kind in ("units", "signatures"):
                        src = OUT / (f"{kind}__{stem}.parquet" if kind == "units" else f"{kind}__{stem}.npy")
                        if src.exists():
                            src.rename(OUT / ("quarantine__" + src.name))
                    entry["quarantined"] = counts.get("decompression_failure", "accounting identity failed")
                    print(f"QUARANTINED {path}: {entry['quarantined']}", flush=True)
                else:
                    n_units_total += n_rows; n_sigs_total += len(sigs)
                files_out.append(entry)
                print(f"done {path}: {counts} units={n_rows} ({time.time()-t_start:.0f}s)", flush=True)
    meta = {"written_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "limit": limit, "n_units": n_units_total, "n_signatures": n_sigs_total, "files": files_out,
            "counts_per_file": counts_all, "tokenizers": TOKENIZERS, "tok_cap_chars": TOK_CAP, "shingle_caps": {"word": SHINGLE_CAP_WORD, "char": SHINGLE_CAP_CHAR},
            "tokenizer_provenance": toks["_provenance"], "licence_allowlist": {"labels": _CC_LABELS, "wikipedia_label": WIKI_LABEL, "allowed_identities": sorted(ALLOWED_IDENTITIES)},
            "minhash": {"n_perm": N_PERM, "seed": int(HASHSEED), "hash": "CPython str.hash with PYTHONHASHSEED=20261009; h_i(x) = ((a_i x + b_i) mod 2^64) >> 32", "domain": "candidate generation only: shingles of the normalised-text prefix (SHINGLE_CAP); confirmation uses exact Jaccard on the full normalised text (corpora_partition.py)"},
            "lsh": {"bands": LSH_BANDS, "rows": LSH_ROWS}, "book_skip_tokens": BOOK_SKIP, "seconds": round(time.time() - t_start)}
    (OUT / "counts.json").write_text(json.dumps(meta, indent=1))
    print("WROTE", OUT, meta["n_units"], "units", meta["seconds"], "s", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    srcs = tuple(sys.argv[sys.argv.index("--sources") + 1].split(",")) if "--sources" in sys.argv else ("news", "stackexchange", "gutenberg", "wikipedia")
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    main(lim, srcs, only)
