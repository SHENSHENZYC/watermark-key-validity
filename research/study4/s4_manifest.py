"""Study 4 run manifest (not pinned; provisional until the lock): rebuilt from the run log, the unit records, the lock, the launch notes and
the environment, never from memory. Writes outputs/study4_v0.1/RUN_MANIFEST.json with: the lock (verified again), the git commit named in
the launch notes and the one at manifest time, the run's start and end (UTC) from the log, the phases with their durations, the per-unit
table (kind, cell, arm or chunk, key, seconds and tok/s from the record and the wall-clock between consecutive done lines, the hook cache
statistics, the green share, the array digest) with the validator's projection beside each arm (VALIDATION.json `cost`), the totals against
the projection, the number of start lines (restarts) and reused units (resumes), the inventory (every committed file under cells/ with a
digest over all of them) and the machine state at launch (from the launch notes).
Usage: .venv/bin/python research/study4/s4_manifest.py [--launch-notes outputs/study4_v0.1/launch_notes.log]
       .venv/bin/python research/study4/s4_manifest.py --validation --log <dir>/run.log --cells <dir>/cells --out <file outside the canonical path>
"""
import datetime, hashlib, json, pathlib, platform, re, subprocess, sys
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from s4_run import OUT, STUDY, verify_lock, sha, expected_units, unit_name   # noqa: E402

TS = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)")
GRID = ROOT / "research/study4/grid_v0.1.json"


def ts(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)


def parse_log(path):
    lines = pathlib.Path(path).read_text().splitlines()
    starts = [l for l in lines if l.startswith("start ")]; ends = [l for l in lines if l.startswith("end ")]
    units = {}; reused = []; phases = []; prev_t = None
    for l in lines:
        m = TS.match(l)
        if not m:
            continue
        t = m.group(1); rest = l[len(t) + 1:].strip()
        md = re.match(r"done (\S+) \(([\d.]+)s, ([\d.]+) tok/s, rss ([\d.]+) GB\)$", rest)
        mr = re.match(r"reused (\S+)$", rest); mp = re.match(r"start phase (.+)$", rest)
        if md:
            units[md.group(1)] = {"done_utc": t, "seconds_log": float(md.group(2)), "tok_per_s_log": float(md.group(3)), "rss_gb_log": float(md.group(4)), "wall_seconds": (ts(t) - ts(prev_t)).total_seconds() if prev_t else None}; prev_t = t
        elif mr:
            reused.append(mr.group(1))
        elif mp:
            if phases:
                phases[-1]["end_utc"] = t
            phases.append({"phase": mp.group(1), "start_utc": t}); prev_t = t
    if phases and ends:
        phases[-1]["end_utc"] = ends[-1].split()[3]
    for p in phases:
        p["hours"] = round((ts(p["end_utc"]) - ts(p["start_utc"])).total_seconds() / 3600, 4) if p.get("end_utc") else None
    start_utc = re.search(r"run (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", starts[0]).group(1) if starts else None
    end_utc = ends[-1].split()[3] if ends else None
    end_fields = dict(re.findall(r"(\w+)=([\d.]+)", ends[-1])) if ends else {}
    return {"n_start_lines": len(starts), "start_lines": starts, "n_end_lines": len(ends), "start_utc": start_utc, "end_utc": end_utc, "end_fields": end_fields, "units": units, "reused_units": reused, "phases": phases, "n_lines": len(lines)}


def main(argv):
    validation = "--validation" in argv
    launch = argv[argv.index("--launch-notes") + 1] if "--launch-notes" in argv else str(OUT / "launch_notes.log")
    log = argv[argv.index("--log") + 1] if "--log" in argv else str(OUT / "run.log")
    cells = pathlib.Path(argv[argv.index("--cells") + 1] if "--cells" in argv else OUT / "cells")
    out = pathlib.Path(argv[argv.index("--out") + 1] if "--out" in argv else OUT / "RUN_MANIFEST.json")
    if not validation and (str(cells) != str(OUT / "cells") or str(out) != str(OUT / "RUN_MANIFEST.json") or log != str(OUT / "run.log")):
        raise SystemExit("study mode writes only the canonical manifest from the canonical log and cells; use --validation for anything else")
    if validation and str(out) == str(OUT / "RUN_MANIFEST.json"):
        raise SystemExit("validation mode must not write the canonical manifest")
    grid = json.loads(GRID.read_text())
    lock = None
    if not validation:
        lock, _, _ = verify_lock(OUT / "PRE_RUN_LOCK.json", GRID, root=ROOT)
    plog = parse_log(log)
    files = sorted(f for f in cells.iterdir() if f.is_file() and f.suffix in (".json", ".npz"))
    digests = {f.name: sha(f) for f in files}; inventory_digest = hashlib.sha256("".join(f"{k}:{v}\n" for k, v in sorted(digests.items())).encode()).hexdigest()
    expected = expected_units(grid, validation); exp_names = {unit_name(u) for u in expected}; exp_files = {f"{n}{ext}" for n in exp_names for ext in (".json", ".npz")}
    recs = {}; n_fixture = 0
    for n in sorted(exp_names):
        jp = cells / f"{n}.json"
        if jp.exists():
            r = json.loads(jp.read_text()); recs[n] = r; n_fixture += int("FIXTURE" in r)
    units = []
    for u in expected:
        n = unit_name(u); r = recs.get(n); lg = plog["units"].get(n, {})
        units.append({"unit": n, "kind": u["kind"], "cell": u["cell"], "arm": u.get("arm", "none"), "key": u.get("key"), "chunk": u.get("chunk"), "n": u["n"], "present": r is not None, "reused": n in plog["reused_units"],
                      "seconds": r.get("seconds") if r else None, "tok_per_s": r.get("tok_per_s") if r else None, "seconds_model": r.get("seconds_model") if r else None, "seconds_hook": r.get("seconds_hook") if r else None,
                      "cache_hits": r.get("cache_hits") if r else None, "cache_misses": r.get("cache_misses") if r else None, "green_share_hook": r.get("green_share_hook") if r else None, "peak_rss_gb": r.get("peak_rss_gb") if r else None,
                      "npz_sha256": r.get("npz_sha256") if r else None, "written_utc": (r.get("provenance") or {}).get("written_utc") if r else None, **{k: lg.get(k) for k in ("done_utc", "seconds_log", "wall_seconds")}})
    # the projection beside the measurement
    val = json.loads((OUT / "VALIDATION.json").read_text()) if (OUT / "VALIDATION.json").exists() else None
    proj = val["cost"] if val else None
    by_arm = {}
    for u in units:
        if u["present"] and u["wall_seconds"] is not None:
            by_arm.setdefault(u["arm"], []).append(u["wall_seconds"])
    arm_summary = {a: {"n_units": len(v), "mean_wall_seconds": round(sum(v) / len(v), 2), "projected_wall_seconds_per_unit": (proj["wall_seconds_per_gen_unit_by_arm"].get(a) if proj and a != "none" else (proj["wall_seconds_per_null_text"] * grid["null_arm"]["n_per_unit"] if proj else None))} for a, v in by_arm.items()}
    total_wall = sum(sum(v) for v in by_arm.values()); dur_h = (ts(plog["end_utc"]) - ts(plog["start_utc"])).total_seconds() / 3600 if plog["start_utc"] and plog["end_utc"] else None
    launch_info = None
    if pathlib.Path(launch).exists():
        lt = pathlib.Path(launch).read_text().splitlines(); first = next((l for l in lt if l.startswith("launch ")), "")
        mh = re.search(r"HEAD=([0-9a-f]{40})", first); ml = re.search(r"lock_sha256=([0-9a-f]{64})", first)
        launch_info = {"launch_line": first, "head_at_launch": mh.group(1) if mh else None, "lock_sha256_at_launch": ml.group(1) if ml else None, "swap_at_launch": next((l.split(": ", 1)[1] for l in lt if l.startswith("vm.swapusage")), None) or (re.search(r"swap='([^']*)'", first).group(1) if re.search(r"swap='([^']*)'", first) else None), "command": next((l.split(": ", 1)[1] for l in lt if l.startswith("command")), None), "command_note": "the launch notes carry no command line; the command is in the decision log and the protocol" if not any(l.startswith("command") for l in lt) else None, "lines": lt}
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip(); dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    except Exception:
        head, dirty = None, None
    import numpy, scipy, torch, transformers
    try:
        cpu = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip(); mem = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip()
    except Exception:
        cpu, mem = None, None
    man = {"label": "VALIDATION (validation keys and pilot prompts; not the study)" if validation else "STUDY", "study": STUDY, "written_utc": f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}",
           "lock": None if validation else {"path": str(OUT / "PRE_RUN_LOCK.json"), "sha256": sha(OUT / "PRE_RUN_LOCK.json"), "verified_at_manifest": True, "date": lock["date"], "approved_by": lock["approved_by"], "before_outcomes": lock["before_outcomes"], "final": lock["final"], "review": lock["review"], "keys": lock["keys"], "record": lock["record"]},
           "git": {"head_at_manifest": head, "tracked_changes_at_manifest": dirty, "launch": launch_info},
           "run": {"log": log, "start_utc": plog["start_utc"], "end_utc": plog["end_utc"], "duration_hours": round(dur_h, 3) if dur_h is not None else None, "n_start_lines": plog["n_start_lines"], "start_lines": plog["start_lines"], "n_end_lines": plog["n_end_lines"], "end_fields": plog["end_fields"],
                   "reused_units_on_resume": plog["reused_units"], "n_units_in_log": len(plog["units"]), "sum_wall_seconds": round(total_wall, 1), "sum_wall_hours": round(total_wall / 3600, 3), "projected_hours": proj["projected_hours"] if proj else None,
                   "projection_source": {"validation_sha256": sha(OUT / "VALIDATION.json"), "model": "the validation run's own wall-clock per unit at the production batch size, scaled to the inventory (VALIDATION.json cost)"} if val else None,
                   "phases": plog["phases"], "by_arm": arm_summary, "peak_rss_gb_max": max((u["peak_rss_gb"] for u in units if u["peak_rss_gb"] is not None), default=None)},
           "inventory": {"cells_dir": str(cells), "n_files": len(files), "n_expected_files": len(exp_files), "complete": set(digests) == exp_files, "missing": sorted(exp_files - set(digests))[:10], "extra": sorted(set(digests) - exp_files)[:10],
                         "n_unit_records": len(recs), "n_expected_units": len(exp_names), "n_fixture_marked": n_fixture, "inventory_sha256": inventory_digest, "file_digests": digests},
           "units": units,
           "environment": {"python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__, "torch": torch.__version__, "transformers": transformers.__version__, "platform": platform.platform(), "machine": platform.machine(), "cpu": cpu, "memory_bytes": int(mem) if mem else None, "PYTHONHASHSEED": "0 (set at launch)" if launch_info and launch_info.get("command") and "PYTHONHASHSEED=0" in launch_info["command"] else None},
           "deviations": []}
    rj = OUT / "results.json"; ra = OUT / "results_arrays.npz"   # the analysis output, when it exists (the record is committed with its manifest after the analysis under the lock)
    if not validation and rj.exists():
        man["analysis_output"] = {"results_json": str(rj), "sha256": sha(rj), "bytes": rj.stat().st_size, "results_arrays_npz": str(ra) if ra.exists() else None, "arrays_sha256": sha(ra) if ra.exists() else None}
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(man, indent=1, default=float))
    print(json.dumps({k: man[k] for k in ("label", "written_utc")} | {"run": {k: man["run"][k] for k in ("start_utc", "end_utc", "duration_hours", "n_start_lines", "sum_wall_hours", "projected_hours", "peak_rss_gb_max")}, "by_arm": man["run"]["by_arm"], "inventory": {k: man["inventory"][k] for k in ("n_files", "n_expected_files", "complete", "n_fixture_marked", "inventory_sha256")}}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
