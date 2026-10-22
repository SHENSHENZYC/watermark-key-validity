"""Stage 4 driver (R02 F5): the provisional clustering/count/expansion loop and the single finalisation of the partition.

Loop: partition (provisional) -> audit -> an integrity failure (P1, P5, P6) stops the build; if a P2–P4/P7 count fails, fetch
ONE next shard for the failing cell's source in the audit's P8 order, load it into the selected units directory, and
repeat (at most --max-steps steps); when every rule passes, finalise the partition once (partition_v<ver>.parquet, its digest
and the units digest) and run the audit against the finalised map; a non-PASS final audit is a failed build (non-zero exit).
An existing final version is refused before any write.
Usage: .venv/bin/python -u tools/corpora_build.py --version 0.2 [--bands 16 --rows 8 --threshold 0.80] [--max-steps 4] [--dry]
"""
import json, os, pathlib, subprocess, sys

PY = sys.executable
P8_SOURCE_KEY = {"stackexchange": "stackexchange", "gutenberg": "gutenberg", "wikipedia": "wikipedia.{lang}", "news": None}


def run(cmd, log, env=None):
    print("$", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    pathlib.Path(log).write_text(r.stdout + r.stderr)
    if r.returncode != 0:
        raise SystemExit(f"step failed ({cmd[1]}); see {log}\n{r.stdout[-2000:]}{r.stderr[-2000:]}")
    return r.stdout


def failing_cells(audit):
    rules = audit["rules"]; cells = []
    for k, v in rules["P2"]["open_eligible_256"].items():
        if v < 10000: cells.append(k)
    if rules["P2"]["sites_with_>=200"] < 20: cells.append("stackexchange/en@256")
    for k, v in rules["P3"]["open_eligible_256"].items():
        if v < 10000: cells.append(k)
    for k, v in rules["P4"]["open_eligible_1024"].items():
        if v < 5000: cells.append(k)
    cells += rules["P7"]["failed_excluded_cells"]
    return sorted(set(cells))


def integrity_failures(audit):
    r = audit["rules"]; return [k for k in ("P1", "P5", "P6") if not r[k]["pass"]]


def main(version, bands, rows, threshold, max_steps, dry):
    ud = "outputs/corpora_units_v" + version; out = f"outputs/corpora_audit_v{version}.json"
    pathlib.Path("outputs").mkdir(exist_ok=True)
    if pathlib.Path(ud, f"partition_v{version}.parquet").exists():
        raise SystemExit(f"REFUSED before any write: {ud}/partition_v{version}.parquet exists; a finalised version is never rebuilt (use a new version)")
    env = {**os.environ, "CORPORA_UNITS_DIR": ud}
    steps = 0
    while True:
        run([PY, "-u", "tools/corpora_partition.py", ud, "--bands", str(bands), "--rows", str(rows), "--threshold", str(threshold)], f"outputs/build_partition_step{steps}.log")
        run([PY, "-u", "tools/audit_corpora.py", ud, "--out", out], f"outputs/build_audit_step{steps}.log")
        audit = json.loads(pathlib.Path(out).read_text())
        integ = integrity_failures(audit)
        if integ:
            raise SystemExit(f"FAIL: integrity rules failed {integ} (rejected files: {audit.get('partition_summary', {}).get('rejected_files')}); no expansion or finalisation; Yichen decides")
        fails = failing_cells(audit)
        print(f"step {steps}: verdict {audit['verdict']}; failing cells: {fails}", flush=True)
        if not fails:
            break
        if steps >= max_steps:
            raise SystemExit(f"FAIL: counts still failing after {steps} expansion steps: {fails} (audit P8); Yichen decides")
        src, rest = fails[0].split("/", 1); lang = rest.split("@")[0]
        key = P8_SOURCE_KEY[src]
        if key is None:
            raise SystemExit(f"FAIL: {fails[0]} cannot be expanded (news has no further shard; audit P8)")
        key = key.format(lang=lang)
        if dry:
            print(f"DRY: would fetch the next P8 shard for {key} and reload it, then repeat", flush=True); return
        before = json.loads(pathlib.Path("outputs/corpora_manifest_v0.1.json").read_text())["entries"].keys()
        run([PY, "-u", "tools/freeze_corpora.py", "--expand", key], f"outputs/build_freeze_step{steps}.log")
        after = json.loads(pathlib.Path("outputs/corpora_manifest_v0.1.json").read_text())["entries"]
        new = [e["path"] for k, e in after.items() if k not in before and e.get("status") == "OK"]
        if not new:
            raise SystemExit(f"FAIL: no shard could be added for {key} (cap reached or fetch failed); audit P8; Yichen decides")
        run([PY, "-u", "tools/corpora_loader.py", "--only", new[0]], f"outputs/build_loader_step{steps}.log", env=env)
        steps += 1
    if dry:
        print("DRY: all counts pass; would finalise", flush=True); return
    run([PY, "-u", "tools/corpora_partition.py", ud, "--bands", str(bands), "--rows", str(rows), "--threshold", str(threshold), "--final", version], f"outputs/build_partition_final.log")
    run([PY, "-u", "tools/audit_corpora.py", ud, "--out", out, "--version", version], f"outputs/build_audit_final.log")
    audit = json.loads(pathlib.Path(out).read_text())
    print(f"FINAL: verdict {audit['verdict']}; partition {audit['partition']}", flush=True)
    if audit["verdict"] != "PASS":
        raise SystemExit(f"FAIL: the final audit did not pass ({audit['verdict']})")
    print("DONE build", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    g = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
    main(a[a.index("--version") + 1], g("--bands", 16), g("--rows", 8), g("--threshold", 0.80), g("--max-steps", 4), "--dry" in a)
