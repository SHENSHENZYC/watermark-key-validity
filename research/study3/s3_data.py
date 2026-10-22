"""Study 3 data layer (v1; decision D11, 2026-10-13). Nothing here touches a key.

Per corpus cell (the ten cells of Study 2; study length L = 256 in every cell):
- the EVALUATION set is Study 2's frozen production sample (the first 10,000 ids of the cell's seeded permutation; Gutenberg: the
  first 7,122 of them), read from Study 2's token cache through its manifest (digest-verified) and cut to the first 256 window
  tokens (for the @1024 cells a prefix of Study 2's window; books from token 1,000 as in Study 2);
- the CALIBRATION set is 5,000 further ids of the SAME permutation, scanned in permutation order and skipping every id that lies in
  any cell's evaluation set or in an earlier cell's calibration set (a uniform permutation scan conditional on the remaining
  admissible ids: every prefix of length N_cal is a uniform sample without replacement from the cell's pool MINUS those exclusions;
  the two English Wikipedia pools are nested, so wikipedia/en@256 also excludes the ids of the en@1024 evaluation set, a
  length-dependent exclusion relative to its full pool); for Gutenberg it is positions 7,122-12,121 of its permutation: its 2,122
  books not sampled by Study 2 and the last 2,878 of Study 2's sample, which therefore leave Study 3's evaluation set (so the
  Gutenberg calibration set is disjoint from Study 3's evaluation sets but not from Study 2's);
- the calibration texts are loaded through the seal (open partition only) and tokenised exactly as Study 2's (s2_data.tokenise_window
  on the audit's capped prefix with the cell's own window length, then cut to 256 tokens), cached as .npy (git-ignored) under a
  tracked manifest that records the pool, seed, scan positions, the exclusion set's digest, every array's SHA-256, and the seal.
The eligibility of a cell's calibration text is the cell's own (Study 2's pool definition), so the calibration law is the cell's law.
"""
import datetime, hashlib, json, pathlib, sys
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/study2"))
import s2_data as D   # Study 2's locked data layer (pinned by Study 2's lock), unchanged

L_STUDY = 256
N_EVAL = 10000
N_EVAL_GUTENBERG = 7122
N_CAL = 5000
S2_MANIFEST = "outputs/study2_v0.1/tokens_manifest.json"
CELLS = D.CELLS


def is_books(cell):
    return cell[0] == "gutenberg"


def permutation(pool, cell, seed_base):
    """The cell's full seeded permutation of its sorted pool (Study 2's draw with N = the pool size; its first 10,000 ids are
    Study 2's sample, which the caller checks against Study 2's manifest)."""
    seed = int(seed_base) + int(hashlib.sha256(D.cell_str(cell).encode()).hexdigest()[:8], 16)
    return D.draw(pool, len(pool), seed), seed


def plan_sets(s2_manifest, df=None):
    """The evaluation and calibration ids of every cell (metadata only; no text). Returns {tag: {...}} and asserts that every
    Study 2 draw is reproduced, that the calibration sets are disjoint from every evaluation set and from each other, and that
    each calibration set has N_CAL ids from its own cell's pool."""
    df = D.load_units_meta() if df is None else df
    base = int(s2_manifest["seed_base"]); perms = {}; pools = {}
    for cell in CELLS:
        tag = D.cell_tag(cell); pool, counts = D.eligible_pool(df, cell); perm, seed = permutation(pool, cell, base)
        e = s2_manifest["cells"][tag]
        if seed != e["seed"] or D.ids_digest(pool) != e["pool_sha256"] or D.ids_digest(perm[:e["N"]]) != e["ids_sha256"]:
            raise RuntimeError(f"{tag}: the Study 2 draw is not reproduced from the metadata")
        perms[tag] = (perm, seed, counts); pools[tag] = pool
    ev = {}
    for cell in CELLS:
        tag = D.cell_tag(cell); perm = perms[tag][0]
        ev[tag] = perm[:N_EVAL_GUTENBERG] if is_books(cell) else perm[:N_EVAL]
    eval_union = set().union(*[set(v) for v in ev.values()])
    taken = set(); plan = {}
    for cell in CELLS:
        tag = D.cell_tag(cell); perm, seed, counts = perms[tag]
        if is_books(cell):
            pos = list(range(N_EVAL_GUTENBERG, N_EVAL_GUTENBERG + N_CAL)); cal = [perm[p] for p in pos]
            if len(cal) != N_CAL or any(c in taken for c in cal):
                raise RuntimeError(f"{tag}: the book calibration block is short or not disjoint")
            skipped = 0
        else:
            cal, pos, skipped = [], [], 0
            for p in range(N_EVAL, len(perm)):
                cid = perm[p]
                if cid in eval_union or cid in taken:
                    skipped += 1; continue
                cal.append(cid); pos.append(p)
                if len(cal) == N_CAL:
                    break
            if len(cal) != N_CAL:
                raise RuntimeError(f"{tag}: only {len(cal)} calibration ids available")
        taken |= set(cal)
        plan[tag] = {"cell": cell, "pool_size": len(pools[tag]), "pool_sha256": D.ids_digest(pools[tag]), "pool_counts": counts, "seed": seed,
                     "eval_ids": ev[tag], "eval_n": len(ev[tag]), "eval_ids_sha256": D.ids_digest(ev[tag]),
                     "cal_ids": cal, "cal_positions": [int(pos[0]), int(pos[-1])], "cal_skipped": int(skipped), "cal_ids_sha256": D.ids_digest(cal)}
    # disjointness, asserted (explicit exceptions, never assert)
    all_cal = [c for t in plan for c in plan[t]["cal_ids"]]
    if len(set(all_cal)) != len(all_cal):
        raise RuntimeError("calibration sets overlap")
    if set(all_cal) & eval_union:
        raise RuntimeError("a calibration id lies in an evaluation set")
    for t in plan:
        if not set(plan[t]["cal_ids"]) <= set(pools[t]):
            raise RuntimeError(f"{t}: a calibration id lies outside the cell's pool")
    return plan


def build_cal_cache(out_dir, tokenizers=("llama", "qwen"), log=print):
    """Load and tokenise every cell's calibration set under both tokenizers; write <out_dir>/tokens/<tag>__<tok>__cal.npy (git-ignored,
    N_CAL x 256 int32) and <out_dir>/tokens_manifest.json (tracked)."""
    out_dir = pathlib.Path(out_dir).resolve(); tdir = out_dir / "tokens"; tdir.mkdir(parents=True, exist_ok=True)
    s2m = json.loads((ROOT / S2_MANIFEST).read_text()); plan = plan_sets(s2m)
    toks = {t: D.get_tokenizer(t) for t in tokenizers}
    man = {"study": "study3_v0.1", "written_utc": f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}", "L": L_STUDY, "N_cal": N_CAL, "N_eval": N_EVAL, "N_eval_gutenberg": N_EVAL_GUTENBERG,
           "seed_base": int(s2m["seed_base"]), "study2_manifest": S2_MANIFEST, "study2_manifest_sha256": D.sha_file(ROOT / S2_MANIFEST),
           "units_dir": str(D.UNITS_DIR.relative_to(ROOT)), "units_version": D.UNITS_VERSION, "tokenizers": s2m["tokenizers"], "book_skip_tokens": D.BOOK_SKIP,
           "text_cap_chars": D.TOK_CAP_CHARS, "add_special_tokens": False, "cells": {}}
    seal = None
    for cell in CELLS:
        tag = D.cell_tag(cell); p = plan[tag]
        log(f"{D.cell_str(cell)}: calibration ids at permutation positions {p['cal_positions']} ({p['cal_skipped']} skipped); loading texts")
        texts, seal = D.load_texts(p["cal_ids"], cap=D.TOK_CAP_CHARS[cell[0]])
        entry = {k: v for k, v in p.items() if k not in ("cell", "eval_ids", "cal_ids")} | {"cell": D.cell_str(cell), "tag": tag, "L_window_tokenised": cell[2], "first_cal_ids": p["cal_ids"][:3], "tokenizers": {}}
        for t, tok in toks.items():
            X, n_full = D.tokenise_window([texts[i] for i in p["cal_ids"]], tok, cell, cell[2])
            X = np.ascontiguousarray(X[:, :L_STUDY])
            f = tdir / f"{tag}__{t}__cal.npy"; np.save(f, X)
            entry["tokenizers"][t] = {"file": str(f.relative_to(ROOT)), "shape": list(X.shape), "dtype": str(X.dtype), "sha256": D.sha_file(f), "max_id": int(X.max()), "min_id": int(X.min()),
                                      "capped_prefix_tokens_median": int(np.median(n_full)), "capped_prefix_tokens_min": int(n_full.min()), "distinct_ids_in_window": int(len(np.unique(X)))}
            log(f"  {t}: {X.shape} sha {entry['tokenizers'][t]['sha256'][:12]}")
        man["cells"][tag] = entry
    man["seal"] = seal
    (out_dir / "tokens_manifest.json").write_text(json.dumps(man, indent=1))
    return man


def load_eval(tag, tok, s3_manifest, root=ROOT):
    """The evaluation tokens of a cell: Study 2's cached array (digest-verified by s2_data.load_tokens), the first eval_n rows and the
    first 256 window tokens; the ids digest of those rows is checked against this study's manifest."""
    s2m = json.loads((pathlib.Path(root) / S2_MANIFEST).read_text())
    if D.sha_file(pathlib.Path(root) / S2_MANIFEST) != s3_manifest["study2_manifest_sha256"]:
        raise RuntimeError("Study 2's token manifest differs from the digest recorded in Study 3's manifest")
    e = s3_manifest["cells"][tag]
    X = D.load_tokens(s2m, tag, tok, root=root)
    return np.ascontiguousarray(X[:e["eval_n"], :L_STUDY])


def load_cal(tag, tok, s3_manifest, root=ROOT):
    """The calibration tokens of a cell (N_CAL x 256), verified against this study's manifest (digest, shape, dtype)."""
    e = s3_manifest["cells"][tag]["tokenizers"][tok]; p = pathlib.Path(root) / e["file"]
    if not p.exists():
        raise RuntimeError(f"calibration token cache missing: {p}")
    if D.sha_file(p) != e["sha256"]:
        raise RuntimeError(f"CALIBRATION TOKEN CACHE MISMATCH: {p}")
    X = np.load(p)
    if list(X.shape) != e["shape"] or str(X.dtype) != e["dtype"]:
        raise RuntimeError(f"calibration token cache {p}: shape/dtype differ from the manifest")
    return X


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--build" in a:
        build_cal_cache(ROOT / "outputs/study3_v0.1")
    elif "--plan" in a:
        s2m = json.loads((ROOT / S2_MANIFEST).read_text()); pl = plan_sets(s2m)
        for t, p in pl.items():
            print(f"{t:22s} pool {p['pool_size']:7d} eval {p['eval_n']:6d} cal positions {p['cal_positions']} skipped {p['cal_skipped']}")
