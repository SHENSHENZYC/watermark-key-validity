"""Study 3 run manifest: rebuilt from the run log, the unit records, the lock, the launch notes and the environment (never from memory).
Writes outputs/study3_v0.1/RUN_MANIFEST.json with: the lock (verified again; digest, date, approval, review), the git commit named in the
launch notes and the one at manifest time, the run's start and end (UTC) from the run log, the per-unit table (kind, tokenizer, cell, width,
seconds from the record and from the log, the tuple count, the local bootstrap file's digest for calibration units) with the validator's
per-pair projection beside each (tokenizer, cell, width) (VALIDATION.json `cost.per_unit_pair_seconds`, the cost model applied to the
key-free tuple counts of INPUTS.json, exactly as the validator projected the run), the totals against the projection, the number of
"start" lines (restarts) and "reused" units (resumes), the inventory (every committed file under cells/: the unit records, the counts
files and the thresholds files, with a digest over all of them) and the machine state at launch (from the launch notes).
Usage: .venv/bin/python research/study3/s3_manifest.py [--launch-notes outputs/study3_v0.1/launch_notes.log]
       [--fixture --log <validation_run.log> --cells <validation dir>/cells --out <file outside the canonical path>]   (no lock; labelled VALIDATION)
Not pinned by the lock.
"""
import datetime, hashlib, json, pathlib, platform, re, subprocess, sys
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study2")); sys.path.insert(0, str(ROOT / "research/study1")); sys.path.insert(0, str(ROOT / "tools"))
from s3_run import OUT, STUDY, GRID_CANON, VALIDATION, INPUTS, verify_lock, sha, expected_units, unit_name   # noqa: E402

TS = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)")


def parse_log(path):
    lines = pathlib.Path(path).read_text().splitlines()
    starts = [l for l in lines if l.startswith("start ")]; dones = [l for l in lines if l.startswith("DONE ")]
    units = {}; reused = []; h_done = {}
    for l in lines:
        m = TS.match(l)
        if not m:
            continue
        t = m.group(1); rest = l[len(t) + 1:].strip()
        mu = re.match(r"pass ([12]) (\S+) \(([\d.]+)s\)$", rest)
        mr = re.match(r"pass ([12]) (\S+): present with matching provenance; reused$", rest)
        mh = re.match(r"h = (\d+) done \(peak RSS so far ([\d.]+) GB\)", rest)
        if mu:
            units[mu.group(2)] = {"pass": int(mu.group(1)), "done_utc": t, "seconds_log": float(mu.group(3))}
        elif mr:
            reused.append(mr.group(2))
        elif mh:
            h_done[int(mh.group(1))] = {"done_utc": t, "peak_rss_gb_log": float(mh.group(2))}
    start_utc = re.search(r"run (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", starts[0]).group(1) if starts else None
    end_utc = dones[-1].split()[1] if dones else None
    return {"n_start_lines": len(starts), "start_lines": starts, "n_done_lines": len(dones), "start_utc": start_utc, "end_utc": end_utc, "units": units, "reused_units": reused, "h_done": h_done, "n_lines": len(lines)}


def main(argv):
    fixture = "--fixture" in argv
    launch = argv[argv.index("--launch-notes") + 1] if "--launch-notes" in argv else str(OUT / "launch_notes.log")
    log = argv[argv.index("--log") + 1] if "--log" in argv else str(OUT / "run.log")
    cells = pathlib.Path(argv[argv.index("--cells") + 1] if "--cells" in argv else OUT / "cells")
    out = pathlib.Path(argv[argv.index("--out") + 1] if "--out" in argv else OUT / "RUN_MANIFEST.json")
    if not fixture and (str(cells) != str(OUT / "cells") or str(out) != str(OUT / "RUN_MANIFEST.json") or log != str(OUT / "run.log")):
        raise SystemExit("study mode writes only the canonical manifest from the canonical log and cells; use --fixture for anything else")
    if fixture and str(out) == str(OUT / "RUN_MANIFEST.json"):
        raise SystemExit("fixture mode must not write the canonical manifest")
    grid = json.loads((ROOT / GRID_CANON).read_text()); lock = None if fixture else verify_lock(ROOT / OUT / "PRE_RUN_LOCK.json", GRID_CANON, root=ROOT)
    plog = parse_log(log)
    files = sorted(f for f in cells.iterdir() if f.is_file() and f.suffix in (".json", ".npz"))
    digests = {f.name: sha(f) for f in files}; inventory_digest = hashlib.sha256("".join(f"{k}:{v}\n" for k, v in sorted(digests.items())).encode()).hexdigest()
    expected = expected_units(grid, validation=fixture); exp_names = {unit_name(u["kind"], u["tokenizer"], u["tag"], u["h"]) for u in expected}
    exp_files = set()
    for u in expected:
        n = unit_name(u["kind"], u["tokenizer"], u["tag"], u["h"]); exp_files.add(f"{n}.json"); exp_files.add(f"{n}__thresholds.npz" if u["kind"] == "cal" else f"{n}.npz")
    proj = {}
    if not fixture:
        try:
            proj = json.loads((ROOT / VALIDATION).read_text())["cost"]["per_unit_pair_seconds"]
        except Exception:
            proj = {}
    rows = []; n_fixture = 0
    for u in expected:
        n = unit_name(u["kind"], u["tokenizer"], u["tag"], u["h"]); p = cells / f"{n}.json"
        if not p.exists():
            rows.append({"unit": n, "missing": True}); continue
        d = json.loads(p.read_text()); n_fixture += int("FIXTURE" in d); lg = plog["units"].get(n, {})
        row = {"unit": n, "kind": u["kind"], "tokenizer": u["tokenizer"], "cell": u["tag"], "h": u["h"], "seconds": d.get("seconds"), "seconds_log": lg.get("seconds_log"), "done_utc": lg.get("done_utc"),
               "n_tuples": (d.get("info") or {}).get("n_tuples"), "N": (d.get("provenance") or {}).get("N"), "written_utc": (d.get("provenance") or {}).get("written_utc")}
        if u["kind"] == "cal":
            row.update({"thresholds_file": pathlib.Path(d.get("thresholds_file", "")).name, "thresholds_sha256": d.get("thresholds_sha256"), "boot_file_local": d.get("boot_file"), "boot_sha256": d.get("boot_sha256")})
        else:
            row.update({"counts_sha256": d.get("npz_sha256"), "N_E": d.get("N_E")})
        rows.append(row)
    pairs = []
    for u in expected:
        if u["kind"] != "cal":
            continue
        key = f"{u['tokenizer']}|{u['tag']}|h{u['h']}"; c = next((r for r in rows if r.get("unit") == unit_name("cal", u["tokenizer"], u["tag"], u["h"])), {}); e = next((r for r in rows if r.get("unit") == unit_name("eval", u["tokenizer"], u["tag"], u["h"])), {})
        s_ = (c.get("seconds") or 0) + (e.get("seconds") or 0)
        pairs.append({"pair": key, "cal_seconds": c.get("seconds"), "eval_seconds": e.get("seconds"), "seconds": round(s_, 1), "projected_seconds": proj.get(key)})
    total_s = sum(p["seconds"] for p in pairs); proj_s = sum(p["projected_seconds"] or 0 for p in pairs) if proj else None
    dur_h = None
    if plog["start_utc"] and plog["end_utc"]:
        t0 = datetime.datetime.strptime(plog["start_utc"], "%Y-%m-%dT%H:%M:%SZ"); t1 = datetime.datetime.strptime(plog["end_utc"], "%Y-%m-%dT%H:%M:%SZ"); dur_h = round((t1 - t0).total_seconds() / 3600, 3)
    launch_info = {}
    if launch and pathlib.Path(launch).exists():
        lt = pathlib.Path(launch).read_text().splitlines(); first = lt[0] if lt else ""
        mh = re.search(r"HEAD=([0-9a-f]{40})", first); ml = re.search(r"lock_sha256=([0-9a-f]{64})", first)
        launch_info = {"launch_line": first, "head_at_launch": mh.group(1) if mh else None, "lock_sha256_at_launch": ml.group(1) if ml else None,
                       "swap_at_launch": next((l.split(": ", 1)[1] for l in lt if l.startswith("vm.swapusage")), None), "command": next((l.split(": ", 1)[1] for l in lt if l.startswith("command")), None), "lines": lt}
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    except Exception:
        head, dirty = None, None
    import numpy, scipy
    try:
        cpu = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip(); mem = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip()
    except Exception:
        cpu, mem = None, None
    peak = max((v["peak_rss_gb_log"] for v in plog["h_done"].values()), default=None)
    man = {"label": "VALIDATION (fixture; not the study)" if fixture else "STUDY", "study": STUDY, "written_utc": f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}",
           "lock": None if fixture else {"path": str(OUT / "PRE_RUN_LOCK.json"), "sha256": sha(ROOT / OUT / "PRE_RUN_LOCK.json"), "verified_at_manifest": True, "date": lock["date"], "approved_by": lock["approved_by"], "before_outcomes": lock["before_outcomes"], "final": lock["final"], "review": lock["review"]},
           "git": {"head_at_manifest": head, "tracked_changes_at_manifest": dirty, "launch": launch_info},
           "run": {"log": log, "start_utc": plog["start_utc"], "end_utc": plog["end_utc"], "duration_hours": dur_h, "n_start_lines": plog["n_start_lines"], "start_lines": plog["start_lines"], "n_done_lines": plog["n_done_lines"],
                   "reused_units_on_resume": plog["reused_units"], "n_unit_lines_in_log": len(plog["units"]), "sum_unit_seconds": round(total_s, 1), "sum_unit_hours": round(total_s / 3600, 3),
                   "projected_hours": round(proj_s / 3600, 3) if proj_s else None, "projection_source": {"validation_sha256": sha(ROOT / VALIDATION), "inputs_sha256": sha(ROOT / INPUTS), "model": "seconds = a + b|D| per pass from two probe points (VALIDATION.json cost.model)"} if not fixture else None,
                   "peak_rss_gb_max": peak, "h_done": plog["h_done"]},
           "inventory": {"cells_dir": str(cells), "n_files": len(files), "n_expected_files": len(exp_files), "complete": set(digests) == exp_files, "missing": sorted(exp_files - set(digests))[:10], "extra": sorted(set(digests) - exp_files)[:10],
                         "n_unit_records": sum(1 for f in files if f.suffix == ".json"), "n_expected_units": len(exp_names), "n_fixture_marked": n_fixture, "inventory_sha256": inventory_digest, "file_digests": digests},
           "analysis_output": None if fixture else {"path": str(OUT / "results.json"), "exists": (ROOT / OUT / "results.json").exists(), "sha256": sha(ROOT / OUT / "results.json") if (ROOT / OUT / "results.json").exists() else None,
                                                   "bytes": (ROOT / OUT / "results.json").stat().st_size if (ROOT / OUT / "results.json").exists() else None,
                                                   "gzip_path": str(OUT / "results.json.gz"), "gzip_sha256": sha(ROOT / OUT / "results.json.gz") if (ROOT / OUT / "results.json.gz").exists() else None,
                                                   "note": "the locked analyzer's output; the raw file is git-ignored (103 MB exceeds GitHub's file limit) and committed gzipped with the same bytes; regenerable from the committed record and the lock by s3_analyze.py in under a minute (seeded bootstraps)"},
           "units": rows, "pairs": pairs,
           "environment": {"python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__, "platform": platform.platform(), "machine": platform.machine(), "cpu": cpu, "memory_bytes": int(mem) if mem and mem.isdigit() else mem, "PYTHONHASHSEED": "0 (set at launch)"},
           "deviations": []}
    if not fixture and n_fixture:
        raise SystemExit(f"{n_fixture} unit records carry a FIXTURE marker in the canonical cells directory")
    out.write_text(json.dumps(man, indent=1))
    print(json.dumps({k: man[k] for k in ("label", "written_utc")} | {"run": {k: man["run"][k] for k in ("start_utc", "end_utc", "duration_hours", "n_start_lines", "sum_unit_hours", "projected_hours", "peak_rss_gb_max")}, "inventory": {k: man["inventory"][k] for k in ("n_files", "n_expected_files", "complete", "n_fixture_marked", "inventory_sha256")}}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
