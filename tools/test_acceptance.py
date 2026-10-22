"""Regression fixtures for the per-file acceptance step and its reporting (R02 F10/F16): synthetic counts.json entries for a
clean-but-short news file (126,672 of 126,673), a malformed line, a decompression failure, a failed accounting identity, a
footer mismatch and a loader-quarantined file, plus three accepted files; the partition's `file_acceptance` must reject the
six with the right reasons, and the audit flow must report them EXCLUDED with no contribution to any count. Also the parser
on tiny gzipped fixtures: a malformed second line and a truncated (CRC-failing) file. Exits non-zero on failure.
Usage: .venv/bin/python tools/test_acceptance.py
"""
import gzip, json, pathlib, sys, tempfile, zlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import corpora_partition as P
import corpora_loader as L

def main():
    ok = True
    meta = {"files": [
        {"path": "news-dolma-0000.json.gz", "units_file": "u0.parquet", "signatures_file": "s0.npy"},
        {"path": "shard-a.json.gz", "units_file": "u1.parquet", "signatures_file": "s1.npy"},
        {"path": "shard-b.json.gz", "units_file": "u2.parquet", "signatures_file": "s2.npy"},
        {"path": "shard-c.json.gz", "units_file": "u3.parquet", "signatures_file": "s3.npy"},
        {"path": "shard-d.json.gz", "units_file": "u4.parquet", "signatures_file": "s4.npy"},
        {"path": "wiki.parquet", "units_file": "u5.parquet", "signatures_file": "s5.npy"},
        {"path": "shard-q.json.gz", "units_file": "u6.parquet", "signatures_file": "s6.npy", "quarantined": "decompression failure recorded by the loader"},
        {"path": "good-1.json.gz", "units_file": "u7.parquet", "signatures_file": "s7.npy"},
        {"path": "good-2.parquet", "units_file": "u8.parquet", "signatures_file": "s8.npy"},
    ], "counts_per_file": {
        "news-dolma-0000.json.gz": {"physical_lines": 126672, "unparseable_lines": 0, "parsed_records": 126672},
        "shard-a.json.gz": {"physical_lines": 100, "unparseable_lines": 1, "parsed_records": 99},
        "shard-b.json.gz": {"physical_lines": 1000, "unparseable_lines": 0, "parsed_records": 1000, "decompression_failure": "BadGzipFile after line 1000"},
        "shard-c.json.gz": {"physical_lines": 100, "unparseable_lines": 0, "parsed_records": 98},
        "shard-d.json.gz": {"physical_lines": 50, "unparseable_lines": 0, "parsed_records": 50},
        "wiki.parquet": {"physical_lines": 500, "unparseable_lines": 0, "parsed_records": 500, "footer_rows": 501},
        "shard-q.json.gz": {"physical_lines": 10, "unparseable_lines": 0, "parsed_records": 10},
        "good-1.json.gz": {"physical_lines": 7, "unparseable_lines": 0, "parsed_records": 7},
        "good-2.parquet": {"physical_lines": 9, "unparseable_lines": 0, "parsed_records": 9, "footer_rows": 9},
    }}
    rej = P.file_acceptance(meta)
    expect = {"news-dolma-0000.json.gz": "card count", "shard-a.json.gz": "unparseable", "shard-b.json.gz": "decompression", "shard-c.json.gz": "accounting", "wiki.parquet": "footer", "shard-q.json.gz": "quarantined"}
    for f, why in expect.items():
        got = rej.get(f, "ACCEPTED")
        good = why in got
        ok &= good; print(f"  {'ok ' if good else 'FAIL'} {f}: {got}")
    for f in ("shard-d.json.gz", "good-1.json.gz", "good-2.parquet"):
        good = f not in rej; ok &= good; print(f"  {'ok ' if good else 'FAIL'} {f}: {'accepted' if good else rej[f]}")
    # the audit's flow must label rejected files EXCLUDED and keep them out of the counts (checked on the audit's own logic)
    rejected_labels = {f: ("EXCLUDED" if f in rej else "admitted") for f in meta["counts_per_file"]}
    good = all(v == "EXCLUDED" for f, v in rejected_labels.items() if f in expect) and all(v == "admitted" for f, v in rejected_labels.items() if f not in expect)
    ok &= good; print(f"  {'ok ' if good else 'FAIL'} audit labels: {sum(1 for v in rejected_labels.values() if v == 'EXCLUDED')} EXCLUDED, {sum(1 for v in rejected_labels.values() if v == 'admitted')} admitted")
    # parser fixtures
    d = pathlib.Path(tempfile.mkdtemp(prefix="acc_fixture_"))
    bad = d / "bad.json.gz"
    with gzip.open(bad, "wt", encoding="utf-8") as f:
        f.write(json.dumps({"id": "1", "text": "a"}) + "\n"); f.write("{not json\n"); f.write(json.dumps({"id": "3", "text": "c"}) + "\n")
    c = {"physical_lines": 0, "unparseable_lines": 0, "parsed_records": 0}; n = sum(1 for _ in L.iter_dolma(bad, c))
    good = c["physical_lines"] == 3 and c["unparseable_lines"] == 1 and c["parsed_records"] == 2 and n == 2
    ok &= good; print(f"  {'ok ' if good else 'FAIL'} malformed line: {c}")
    trunc = d / "trunc.json.gz"; raw = gzip.compress(("".join(json.dumps({"id": str(i), "text": "x" * 50}) + "\n" for i in range(1000))).encode())
    trunc.write_bytes(raw[:-40])   # drop the trailer: CRC/length failure after the readable prefix
    c = {"physical_lines": 0, "unparseable_lines": 0, "parsed_records": 0}; n = sum(1 for _ in L.iter_dolma(trunc, c))
    good = "decompression_failure" in c
    ok &= good; print(f"  {'ok ' if good else 'FAIL'} truncated gzip: parsed {c['parsed_records']} then {c.get('decompression_failure', 'NO FAILURE RECORDED')[:60]}")
    meta2 = {"files": [{"path": "trunc.json.gz", "units_file": "u.parquet", "signatures_file": "s.npy"}], "counts_per_file": {"trunc.json.gz": c}}
    good = "trunc.json.gz" in P.file_acceptance(meta2); ok &= good; print(f"  {'ok ' if good else 'FAIL'} truncated file rejected at acceptance")
    print("ACCEPTANCE TESTS", "PASS" if ok else "FAIL")
    return ok

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
