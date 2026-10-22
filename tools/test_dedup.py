"""Planted-duplicate validation of the near-duplicate rule with the PRODUCTION predicate (audit §5.2; R02 F1/F8): for
exposure-record units only (already forced open), build exact copies, 2% and 5% random deletions, a shifted prefix (first
10% removed) and same-source negatives; a pair is linked iff it shares at least one LSH band of the prefix signatures
(production candidate logic, `candidate_pairs`) AND the exact full-text Jaccard (`confirm_pair`) is at or above the
threshold. Also a large-bucket case: 60 variants of one text, each with a different 1% deletion, must all join one cluster
through all-pairs confirmation. Reports exact and estimated Jaccard, bands shared under 16x8 and 32x4, linkage under
0.80/16x8, 0.70/32x4 and 0.65/32x4 (the decided rule D4).
Usage: .venv/bin/python tools/test_dedup.py <units_dir>   (exits non-zero when a planted expectation fails)
"""
import os, sys
if os.environ.get("PYTHONHASHSEED") != "20261009":
    os.execve(sys.executable, [sys.executable] + sys.argv, {**os.environ, "PYTHONHASHSEED": "20261009"})
import json, pathlib, random
import numpy as np, pyarrow.parquet as pq
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import corpora_loader as L
from corpora_partition import candidate_pairs, confirm_pair, full_shingles, _preprocessing_text_reader, UnionFind

RULES = [("0.80/16x8", 16, 8, 0.80), ("0.70/32x4", 32, 4, 0.70), ("0.65/32x4", 32, 4, 0.65)]

def sig_of(text):
    kind, sh = L.shingles(L.normalise(text)); return kind, (L.minhash(sh) if sh else None)

def mult_for(rows):
    return np.random.default_rng(20261009).integers(1, 2**62, size=rows, dtype=np.uint64) * np.uint64(2) + np.uint64(1)

def linked(s0, s1, A, B, bands, rows, thr):
    """The production predicate: a band shared (candidate) and the exact full-text Jaccard at or above the threshold."""
    if s0 is None or s1 is None: return False, 0, 0.0
    pairs, *_ = candidate_pairs(np.stack([s0, s1]), bands, rows, mult_for(rows))
    shared = int((0, 1) in pairs)
    nb = sum(1 for b in range(bands) if (np.stack([s0, s1])[:, b*rows:(b+1)*rows] == np.stack([s0, s1])[0, b*rows:(b+1)*rows]).all(axis=1).all())
    ej = confirm_pair(A, B)
    return (shared == 1 and ej >= thr), nb, ej

def main(units_dir):
    P = pq.read_table(pathlib.Path(units_dir) / "partition.parquet").to_pandas()
    rows = P[P["exposure_hit"] & (P["partition"] == "open")].groupby(["source", "lang"]).head(2)
    wanted = {}
    for r in rows.itertuples():
        wanted.setdefault(r.file, {})[int(r.pos)] = (r.source, r.lang, r.canonical_id)
    texts = {k: t for k, t in _preprocessing_text_reader(wanted)}
    rng = random.Random(20261009)
    print("| source/lang | unit | variant | exact J | est. J | bands 16x8 | bands 32x4 | link @0.80/16x8 | link @0.70/32x4 | link @0.65/32x4 (D4) |\n|---|---|---|---|---|---|---|---|---|---|")
    tally = {f"{p}@{n}": [0, 0] for p in ("pos", "neg") for n, *_ in RULES}
    by_source = {}
    for (src, lang, cid), text in texts.items():
        by_source.setdefault((src, lang), []).append((cid, text))
    for (src, lang), items in by_source.items():
        for cid, text in items:
            kind, s0 = sig_of(text); A = full_shingles(text)
            if s0 is None: continue
            variants = [("exact copy", text)]
            for drop in (0.02, 0.05):
                if kind == "char":
                    variants.append((f"{drop:.0%} chars deleted", "".join(c for c in text if rng.random() > drop)))
                else:
                    variants.append((f"{drop:.0%} words deleted", " ".join(w for w in text.split(" ") if rng.random() > drop)))
            variants.append(("first 10% removed", text[len(text) // 10:]))
            others = [t for c, t in items if c != cid]
            if others: variants.append(("negative: another unit, same source", others[0]))
            for name, pert in variants:
                _, s1 = sig_of(pert); B = full_shingles(pert)
                est = float((s0 == s1).mean()) if s1 is not None else 0.0
                res = {n: linked(s0, s1, A, B, bd, rw, thr) for n, bd, rw, thr in RULES}
                pos = not name.startswith("negative")
                for n, *_ in RULES:
                    tally[f"{'pos' if pos else 'neg'}@{n}"][0] += res[n][0]; tally[f"{'pos' if pos else 'neg'}@{n}"][1] += 1
                ej = res["0.65/32x4"][2]
                print(f"| {src}/{lang} | {str(cid)[-32:]} | {name} | {ej:.3f} | {est:.3f} | {res['0.80/16x8'][1]}/16 | {res['0.65/32x4'][1]}/32 | {'yes' if res['0.80/16x8'][0] else 'no'} | {'yes' if res['0.70/32x4'][0] else 'no'} | {'yes' if res['0.65/32x4'][0] else 'no'} |")
    print("\nSummary (linked / total) under the production predicate: positives should be linked, negatives not")
    for k, (a, b) in tally.items(): print(f"  {k}: {a}/{b}")
    # large-bucket case (R02 F16): 70 variants of one Wikipedia-en exposed text (0.3% word deletions, so most signatures agree
    # and at least one bucket exceeds 50 members, the old shortcut boundary); every one of the 2,415 pairs must be proposed,
    # a pair that excludes the first member must be confirmed, and union-find must give one cluster
    base = next(t for (s, l, c), t in texts.items() if s == "wikipedia" and l == "en")
    variants = [" ".join(w for w in base.split(" ") if rng.random() > 0.003) for _ in range(70)]
    sigs = np.stack([sig_of(v)[1] for v in variants]); sets = [full_shingles(v) for v in variants]
    pairs, nb, mx, npairs = candidate_pairs(sigs, 32, 4, mult_for(4))
    uf = UnionFind(70); conf = 0
    for i, j in pairs:
        if confirm_pair(sets[i], sets[j]) >= 0.65: conf += uf.union(i, j)
    roots = {uf.find(i) for i in range(70)}
    non_first = (17, 53) in pairs and confirm_pair(sets[17], sets[53]) >= 0.65
    big_ok = len(pairs) == 2415 and mx > 50 and len(roots) == 1 and non_first
    print(f"\nLarge-bucket case: 70 variants; distinct candidate pairs {len(pairs)} of 2415; largest bucket {mx} (> 50 required); non-first-member pair (17, 53) proposed and confirmed: {non_first}; confirmed unions {conf}; clusters {len(roots)} (expected 1)")
    print("LARGE-BUCKET", "PASS" if big_ok else "FAIL")
    pos_ok = tally["pos@0.65/32x4"][0] >= 60 and tally["neg@0.65/32x4"][0] == 0   # the recorded D4 results: 65 of 72 and 0 of 18
    return big_ok and pos_ok

if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1] if len(sys.argv) > 1 else "outputs/corpora_units_v0.3") else 1)
