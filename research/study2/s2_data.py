"""Study 2 data layer (v1): the ten confirmatory corpus cells of the data audit v0.3 (§9), the open eligible pool of each cell
under BOTH pinned tokenizers (metadata only), the seeded production draw, text access through the seal
(tools/corpora_access.Access, open partition only, final_lock None), tokenisation with the pinned tokenizers, and a token cache
(.npy, git-ignored) with a tracked manifest (sizes, SHA-256 of each array, SHA-256 of the sorted ids, the seal's digests, the
tokenizer provenance). Nothing here touches a key. The held-out partition is never requested.
"""
import datetime, hashlib, json, os, pathlib, sys
import numpy as np, pandas as pd, pyarrow.parquet as pq
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

UNITS_DIR = ROOT / "outputs/corpora_units_v0.3"; UNITS_VERSION = "0.3"
CELLS = [("news", "en", 256), ("wikipedia", "en", 256), ("stackexchange", "en", 256), ("wikipedia", "de", 256), ("wikipedia", "ru", 256),
         ("wikipedia", "ar", 256), ("wikipedia", "zh", 256), ("wikipedia", "ja", 256), ("wikipedia", "en", 1024), ("gutenberg", "en", 1024)]
TOKENIZERS = {"llama": {"repo": "meta-llama/Llama-3.2-1B", "revision": "4e20de362430cd3b72f300e6b0f18e50e7166e08", "V": 128256, "note": "V = the model config's vocab_size (the dimension a KGW permutation acts on); len(tokenizer) = 128256"},
              "qwen": {"repo": "Qwen/Qwen2.5-1.5B", "revision": "8faed761d45a263340a0528343f099c05c9a4323", "V": 151936, "note": "V = the model config's vocab_size 151936 (the dimension a KGW permutation acts on); len(tokenizer) = 151665, so 271 ids never occur in text"}}
BOOK_SKIP = 1000          # a book's study window starts at token 1,000 (DATA_LAYOUT.md), under each tokenizer separately


def cell_tag(cell):
    s, l, L = cell; return f"{s}_{l}_{L}"


def cell_str(cell):
    s, l, L = cell; return f"{s}/{l}@{L}"


def need_tokens(cell):
    s, l, L = cell; return L + (BOOK_SKIP if s == "gutenberg" else 0)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def ids_digest(ids):
    return hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()


def load_units_meta():
    """The per-unit metadata of every file joined to the finalised partition map (metadata only; no text)."""
    meta = json.loads((UNITS_DIR / "counts.json").read_text())
    part = pq.read_table(UNITS_DIR / f"partition_v{UNITS_VERSION}.parquet", columns=["canonical_id", "partition", "is_representative", "allowed"]).to_pandas()
    frames = [pq.read_table(UNITS_DIR / f["units_file"], columns=["canonical_id", "source", "lang", "n_tok_llama", "n_tok_qwen", "tok_censored", "group"]).to_pandas() for f in meta["files"]]
    units = pd.concat(frames, ignore_index=True)
    return units.merge(part, on="canonical_id", how="inner")


def eligible_pool(df, cell):
    """Sorted canonical ids of the OPEN, allowed, representative units of the cell that are length-eligible under BOTH tokenizers
    (the Llama count defines the audit's eligibility; the Qwen count is required too so that every text is scored under both)."""
    s, l, L = cell; need = need_tokens(cell)
    d = df[(df.source == s) & (df.lang == l) & (df.partition == "open") & (df.is_representative) & (df.allowed) & (df.n_tok_llama >= need) & (df.n_tok_qwen >= need)]
    return sorted(d.canonical_id.tolist()), {"open_representatives": int(((df.source == s) & (df.lang == l) & (df.partition == "open") & df.is_representative & df.allowed).sum()),
                                             "eligible_llama": int(((df.source == s) & (df.lang == l) & (df.partition == "open") & df.is_representative & df.allowed & (df.n_tok_llama >= need)).sum()),
                                             "eligible_both": int(len(d))}


def draw(pool_ids, N, seed):
    """The seeded production draw: a PCG64 permutation of the sorted pool; the first N ids. A prefix of the draw is itself a
    uniform sample without replacement, so N can be reduced before the lock without redrawing."""
    rng = np.random.default_rng(int(seed)); perm = rng.permutation(len(pool_ids))
    if N > len(pool_ids):
        raise ValueError(f"N = {N} exceeds the pool of {len(pool_ids)}")
    return [pool_ids[i] for i in perm[:N]]


def load_texts(ids, cap=None):
    """Open-partition text through the seal (the only sanctioned path); returns {canonical_id: text}. With cap, each text is
    truncated to its first `cap` characters as it is read (the audit's capped prefix; books are long and the window lies inside it)."""
    from corpora_access import Access
    acc = Access(str(UNITS_DIR), UNITS_VERSION)
    out = {cid: (t[:cap] if cap else t) for cid, t in acc.load_texts(ids, "open")}
    missing = [i for i in ids if i not in out]
    if missing:
        raise RuntimeError(f"{len(missing)} requested ids were not returned by the seal, e.g. {missing[0]!r}")
    return out, {"partition_sha256": acc.partition_sha256, "units_sha256": acc.units_sha256, "manifest_sha256": sha_file(acc.manifest)}


def get_tokenizer(name):
    os.environ.setdefault("HF_HUB_OFFLINE", "1"); os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    from transformers import AutoTokenizer
    spec = TOKENIZERS[name]
    tok = AutoTokenizer.from_pretrained(spec["repo"], revision=spec["revision"])
    return tok


TOK_CAP_CHARS = {"news": 12000, "stackexchange": 12000, "wikipedia": 12000, "gutenberg": 24000}   # the audit's capped-prefix convention (counts.json tok_cap_chars)


def tokenise_window(texts, tok, cell, L_max, batch=256):
    """Token ids of each text WITHOUT special tokens, tokenised on the audit's capped character prefix (12,000 characters; 24,000 for
    books), the same prefix on which eligibility was counted, so the window [skip, skip + L_max) (skip = 1,000 for books, 0 otherwise)
    lies inside it by construction; every text must have at least skip + L_max tokens (asserted). Byte-pair tokenisation is local to
    pre-tokens, so the window's ids equal those of the full text's tokenisation."""
    skip = BOOK_SKIP if cell[0] == "gutenberg" else 0; cap = TOK_CAP_CHARS[cell[0]]
    X = np.empty((len(texts), L_max), dtype=np.int32); n_full = np.empty(len(texts), dtype=np.int64)
    for i0 in range(0, len(texts), batch):
        enc = tok([t[:cap] for t in texts[i0:i0 + batch]], add_special_tokens=False)["input_ids"]
        for j, ids in enumerate(enc):
            if len(ids) < skip + L_max:
                raise RuntimeError(f"text {i0 + j} has {len(ids)} tokens < {skip + L_max} (eligibility violated)")
            X[i0 + j] = ids[skip:skip + L_max]; n_full[i0 + j] = len(ids)
    return X, n_full


def build_token_cache(cells, N, seed_base, out_dir, tokenizers=("llama", "qwen"), log=print):
    """Draw, load and tokenise the production sample of every cell under every tokenizer; write <out_dir>/tokens/<tag>__<tok>.npy
    (git-ignored) and <out_dir>/tokens_manifest.json (tracked). Returns the manifest."""
    out_dir = pathlib.Path(out_dir).resolve(); tdir = out_dir / "tokens"; tdir.mkdir(parents=True, exist_ok=True)
    df = load_units_meta(); toks = {t: get_tokenizer(t) for t in tokenizers}
    man = {"study": "study2_v0.1", "written_utc": f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}", "N": int(N), "seed_base": int(seed_base), "units_dir": str(UNITS_DIR.relative_to(ROOT)), "units_version": UNITS_VERSION,
           "tokenizers": {t: dict(TOKENIZERS[t], files_sha256=json.loads((UNITS_DIR / "counts.json").read_text())["tokenizer_provenance"][t]["files_sha256"]) for t in tokenizers},
           "book_skip_tokens": BOOK_SKIP, "text_cap_chars": TOK_CAP_CHARS, "add_special_tokens": False, "cells": {}}
    seal = None
    for cell in cells:
        tag = cell_tag(cell); L_max = cell[2]
        pool, counts = eligible_pool(df, cell)
        seed = int(seed_base) + int(hashlib.sha256(cell_str(cell).encode()).hexdigest()[:8], 16)
        ids = draw(pool, N, seed)
        log(f"{cell_str(cell)}: pool {len(pool)} (open reps {counts['open_representatives']}, llama-eligible {counts['eligible_llama']}); drew {N} with seed {seed}; loading texts")
        texts, seal = load_texts(ids, cap=TOK_CAP_CHARS[cell[0]])
        entry = {"cell": cell_str(cell), "tag": tag, "L_max": L_max, "need_tokens": need_tokens(cell), "pool": counts, "pool_size": len(pool), "pool_sha256": ids_digest(pool), "seed": seed, "N": N, "ids_sha256": ids_digest(ids), "first_ids": ids[:3], "tokenizers": {}}
        for t, tok in toks.items():
            X, n_full = tokenise_window([texts[i] for i in ids], tok, cell, L_max)
            p = tdir / f"{tag}__{t}.npy"; np.save(p, X)
            entry["tokenizers"][t] = {"file": str(p.relative_to(ROOT)), "shape": list(X.shape), "dtype": str(X.dtype), "sha256": sha_file(p), "max_id": int(X.max()), "min_id": int(X.min()),
                                      "capped_prefix_tokens_median": int(np.median(n_full)), "capped_prefix_tokens_min": int(n_full.min()), "distinct_ids_in_window": int(len(np.unique(X)))}
            log(f"  {t}: {X.shape} sha {entry['tokenizers'][t]['sha256'][:12]} distinct ids {entry['tokenizers'][t]['distinct_ids_in_window']}")
        man["cells"][tag] = entry
    man["seal"] = seal
    (out_dir / "tokens_manifest.json").write_text(json.dumps(man, indent=1))
    return man


def load_tokens(manifest, tag, tok, N=None, root=ROOT):
    """Load a cached token array and verify its digest against the manifest (refuse on mismatch); optionally the first N rows."""
    e = manifest["cells"][tag]["tokenizers"][tok]; p = pathlib.Path(root) / e["file"]
    if not p.exists():
        raise RuntimeError(f"token cache missing: {p}")
    if sha_file(p) != e["sha256"]:
        raise RuntimeError(f"TOKEN CACHE MISMATCH: {p} differs from the manifest digest")
    X = np.load(p)
    if list(X.shape) != e["shape"] or str(X.dtype) != e["dtype"]:
        raise RuntimeError(f"token cache {p}: shape/dtype differ from the manifest")
    return X if N is None else X[:N]
