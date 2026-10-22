"""Seal tests on a synthetic fixture (never the real holdout): relabelled rows, stale ids, unknown partition, missing or
unregistered lock, wrong partition or units digest, incomplete lock, units outside the requested cells by source or by
length (R02 F9), and the positive path with its opening log.
Usage: .venv/bin/python tools/test_seal.py
"""
import gzip, hashlib, json, pathlib, sys, tempfile
import pyarrow as pa, pyarrow.parquet as pq
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from corpora_access import Access, SealError

def main():
    d = pathlib.Path(tempfile.mkdtemp(prefix="seal_fixture_"))
    raw = d / "fx.json.gz"
    with gzip.open(raw, "wt", encoding="utf-8") as f:
        for i in range(1, 4):
            f.write(json.dumps({"id": str(i), "text": f"fixture text {i}"}) + "\n")
    man = d / "manifest.json"; man.write_text(json.dumps({"entries": {"fx": {"path": "fx.json.gz", "local_path": str(raw), "status": "OK"}}}))
    t = pa.Table.from_pydict({"canonical_id": ["u1", "u2", "u3"], "file": ["fx.json.gz"] * 3, "pos": [1, 2, 3], "partition": ["open", "open", "holdout"], "source": ["fx"] * 3, "lang": ["en"] * 3})
    fp = d / "partition_v9.9.parquet"; pq.write_table(t, fp); (d / "partition_v9.9.sha256").write_text(hashlib.sha256(fp.read_bytes()).hexdigest() + "\n")
    # bound units metadata: u3 has 300 tokens (eligible for L=256, not 512); u1 has 10 tokens
    um = pa.Table.from_pydict({"canonical_id": ["u1", "u2", "u3"], "n_tok_llama": [10, 10, 300]}); uf = d / "units__fx.parquet"; pq.write_table(um, uf)
    (d / "counts.json").write_text(json.dumps({"files": [{"units_file": "units__fx.parquet"}]}))
    uh = hashlib.sha256(); uh.update(uf.read_bytes()); uh.update((d / "counts.json").read_bytes()); (d / "units_v9.9.sha256").write_text(uh.hexdigest() + "\n")
    allow = d / "allow.json"; allow.write_text(json.dumps({"locks": []})); openings = d / "openings.jsonl"
    A = Access(d, "9.9", manifest=man, allowlist=allow, openings=openings)
    results = {}
    def expect_refusal(name, fn):
        try:
            list(fn()); results[name] = "FAILED: not refused"
        except SealError as e:
            results[name] = f"refused ({e})"
    results["open_load"] = "OK " + str(list(A.load_texts(["u1"], "open")))
    expect_refusal("holdout_no_lock", lambda: A.load_texts(["u3"], "holdout"))
    expect_refusal("relabelled_holdout_as_open", lambda: A.load_texts(["u3"], "open"))
    expect_refusal("stale_id", lambda: A.load_texts(["u9"], "open"))
    expect_refusal("unknown_partition", lambda: A.load_texts(["u1"], "dev"))
    def lock(**kw):
        p = d / f"lock_{len(list(d.glob('lock_*')))}.json"; p.write_text(json.dumps(kw)); return p
    good = {"final": True, "study": "fixture", "manifest_sha256": hashlib.sha256(man.read_bytes()).hexdigest(), "partition_sha256": A.partition_sha256, "units_sha256": A.units_sha256, "cells": ["fx/en@256", "other/en@256", "fx/en@512"]}
    unreg = lock(**good); expect_refusal("unregistered_lock", lambda: A.load_texts(["u3"], "holdout", final_lock=unreg, study="fixture", cells=["fx/en@256"]))
    def register(p):
        j = json.loads(allow.read_text()); j["locks"].append(hashlib.sha256(p.read_bytes()).hexdigest()); allow.write_text(json.dumps(j))
    wrongdig = lock(**{**good, "partition_sha256": "0" * 64}); register(wrongdig); expect_refusal("wrong_partition_digest", lambda: A.load_texts(["u3"], "holdout", final_lock=wrongdig, study="fixture", cells=["fx/en@256"]))
    wrongu = lock(**{**good, "units_sha256": "0" * 64}); register(wrongu); expect_refusal("wrong_units_digest", lambda: A.load_texts(["u3"], "holdout", final_lock=wrongu, study="fixture", cells=["fx/en@256"]))
    nostudy = lock(**{k: v for k, v in good.items() if k != "study"}); register(nostudy); expect_refusal("lock_without_study", lambda: A.load_texts(["u3"], "holdout", final_lock=nostudy, study="fixture", cells=["fx/en@256"]))
    nocells = lock(**{**good, "cells": []}); register(nocells); expect_refusal("lock_without_cells", lambda: A.load_texts(["u3"], "holdout", final_lock=nocells, study="fixture", cells=["fx/en@256"]))
    notfinal = lock(**{**good, "final": False}); register(notfinal); expect_refusal("lock_not_final", lambda: A.load_texts(["u3"], "holdout", final_lock=notfinal, study="fixture", cells=["fx/en@256"]))
    reg = lock(**good); register(reg)
    expect_refusal("cells_outside_lock", lambda: A.load_texts(["u3"], "holdout", final_lock=reg, study="fixture", cells=["fx/en@128"]))
    expect_refusal("study_mismatch", lambda: A.load_texts(["u3"], "holdout", final_lock=reg, study="other", cells=["fx/en@256"]))
    expect_refusal("unit_outside_requested_cell_source", lambda: A.load_texts(["u3"], "holdout", final_lock=reg, study="fixture", cells=["other/en@256"]))
    expect_refusal("unit_fails_cell_length", lambda: A.load_texts(["u3"], "holdout", final_lock=reg, study="fixture", cells=["fx/en@512"]))
    got = list(A.load_texts(["u3"], "holdout", final_lock=reg, study="fixture", cells=["fx/en@256"]))
    logged = [json.loads(l) for l in openings.read_text().splitlines()]
    results["registered_lock_positive_path"] = f"OK {got}; openings logged: {len(logged)} (study={logged[-1]['study']}, cells={logged[-1]['cells']}, n_units={logged[-1]['n_units']}, ids_sha256={logged[-1]['ids_sha256'][:12]})"
    # tamper with the map after finalisation: the accessor must refuse to bind
    fp.write_bytes(fp.read_bytes() + b"\n")
    try:
        Access(d, "9.9", manifest=man, allowlist=allow, openings=openings); results["tampered_map"] = "FAILED: bound"
    except SealError as e:
        results["tampered_map"] = f"refused ({e})"
    ok = results["open_load"].startswith("OK") and results["registered_lock_positive_path"].startswith("OK") and all(v.startswith("refused") for k, v in results.items() if k not in ("open_load", "registered_lock_positive_path"))
    print(json.dumps(results, indent=1)); print("SEAL TESTS", "PASS" if ok else "FAIL")
    return ok

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
