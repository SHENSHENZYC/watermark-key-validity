"""Study 1 run manifest: rebuilt from the run log, the cost records, the lock and the environment (never from memory).
Writes outputs/study1_v0.3/RUN_MANIFEST.json with: the lock (verified again, digest), the git commit named in the launch log and
the one at manifest time, the run's start and end (UTC) from the run log, the per-chain table (built size, build and colouring
seconds, cells, chain seconds) from the cost records with the projection beside it (VALIDATION.json), the totals, the number of
"start" lines (restarts) and "skipped" chains (resumes), the inventory (cells on disk, markers, a digest over every cell file),
and the machine state at launch (from the launch log: swap, HEAD).
Usage: .venv/bin/python research/study1/s1_manifest.py --launch-log <stdout log of the launch>
       [--fixture --log <validation_run.log> --cells <validation dir> --out <file>]   (no lock; labelled VALIDATION)
"""
import datetime, hashlib, json, pathlib, platform, re, subprocess, sys
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "tools"))
from s1_run import OUT, STUDY, GRID_CANON, verify_lock, sha, expected_cells   # noqa: E402

TS = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)")


def parse_log(path):
    lines = pathlib.Path(path).read_text().splitlines()
    starts = [l for l in lines if l.startswith("start ")]; dones = [l for l in lines if l.startswith("DONE ")]
    chain_built = {}; chain_done = {}; skipped = []
    for l in lines:
        m = TS.match(l)
        if not m:
            continue
        t = m.group(1); rest = l[len(t) + 1:]
        mb = re.match(r"chain (\S+) built: \|D\|=(\d+) contexts=(\d+) \(([\d.]+)s\)", rest)
        md = re.match(r"chain (\S+) done \(([\d.]+)s\)", rest)
        ms = re.match(r"chain (\S+): every cell present", rest)
        if mb:
            chain_built[mb.group(1)] = {"built_utc": t, "n_tuples": int(mb.group(2)), "n_contexts": int(mb.group(3)), "build_seconds_log": float(mb.group(4))}
        elif md:
            chain_done[md.group(1)] = {"done_utc": t, "chain_seconds_log": float(md.group(2))}
        elif ms:
            skipped.append(ms.group(1))
    first_ts = next((TS.match(l).group(1) for l in lines if TS.match(l)), None)
    start_utc = re.search(r"run (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", starts[0]).group(1) if starts else first_ts
    end_utc = dones[-1].split()[1] if dones else None
    return {"n_start_lines": len(starts), "start_lines": starts, "n_done_lines": len(dones), "start_utc": start_utc, "end_utc": end_utc,
            "chains_built": chain_built, "chains_done": chain_done, "skipped_chains": skipped, "n_lines": len(lines)}


def main(argv):
    fixture = "--fixture" in argv
    launch = argv[argv.index("--launch-log") + 1] if "--launch-log" in argv else None
    log = argv[argv.index("--log") + 1] if "--log" in argv else str(OUT / "run.log")
    cells = pathlib.Path(argv[argv.index("--cells") + 1] if "--cells" in argv else OUT / "cells")
    out = pathlib.Path(argv[argv.index("--out") + 1] if "--out" in argv else OUT / "RUN_MANIFEST.json")
    if not fixture and (str(cells) != str(OUT / "cells") or str(out) != str(OUT / "RUN_MANIFEST.json")):
        raise SystemExit("study mode writes only the canonical manifest from the canonical cells; use --fixture for anything else")
    if fixture and (str(out) == str(OUT / "RUN_MANIFEST.json")):
        raise SystemExit("fixture mode must not write the canonical manifest")
    grid = json.loads((ROOT / GRID_CANON).read_text())
    lock = None
    if not fixture:
        lock = verify_lock(ROOT / OUT / "PRE_RUN_LOCK.json", GRID_CANON, root=ROOT)
    plog = parse_log(log)
    # cost records (one per chain) and the inventory
    costs = {}
    for f in sorted(cells.glob("costs__*.json")):
        c = json.loads(f.read_text()); costs[c["tag"]] = c
    cell_files = sorted(f for f in cells.glob("*.json") if not f.name.startswith("costs__"))
    digests = {f.name: sha(f) for f in cell_files}
    inventory_digest = hashlib.sha256("".join(f"{k}:{v}\n" for k, v in sorted(digests.items())).encode()).hexdigest()
    n_marker = 0; n_live = 0; n_nodet = 0
    for f in cell_files:
        d = json.loads(f.read_text())
        if "levels" not in d:
            n_marker += 1
        elif d.get("N_eff", 1) == 0:
            n_nodet += 1
        else:
            n_live += 1
    expected = expected_cells(grid, grid["validation_laws"] if fixture else None)
    # projection beside the measurement
    proj = {}
    try:
        v = json.loads((ROOT / OUT / "VALIDATION.json").read_text()); proj = {c["chain"]: c for c in v["projection"]["chains"]}; proj_total_h = v["projection"]["total_projected_hours"]
    except Exception:
        proj_total_h = None
    chains = []
    for tag in sorted(set(costs) | set(plog["chains_built"])):
        c = costs.get(tag, {}); b = plog["chains_built"].get(tag, {}); d = plog["chains_done"].get(tag, {}); p = proj.get(tag, {})
        chains.append({"chain": tag, "n_tuples": c.get("n_tuples", b.get("n_tuples")), "n_contexts": c.get("n_contexts", b.get("n_contexts")),
                       "build_seconds": c.get("build_seconds"), "colouring_seconds": round(sum(x["seconds"] for x in c.get("colourings", [])), 1) if c else None,
                       "n_cells_computed": len(c.get("cells", [])) if c else None, "cells_seconds": round(sum(x["seconds"] for x in c.get("cells", [])), 1) if c else None,
                       "chain_seconds": c.get("chain_seconds", d.get("chain_seconds_log")), "built_utc": b.get("built_utc"), "done_utc": d.get("done_utc"),
                       "projected_chain_seconds": p.get("chain_seconds_projected"), "projected_cells": p.get("cells")})
    total_chain_s = sum(x["chain_seconds"] or 0 for x in chains)
    dur_h = None
    if plog["start_utc"] and plog["end_utc"]:
        t0 = datetime.datetime.strptime(plog["start_utc"], "%Y-%m-%dT%H:%M:%SZ"); t1 = datetime.datetime.strptime(plog["end_utc"], "%Y-%m-%dT%H:%M:%SZ")
        dur_h = round((t1 - t0).total_seconds() / 3600, 3)
    launch_info = {}
    if launch:
        lt = pathlib.Path(launch).read_text().splitlines()
        launch_info = {"launch_line": next((l for l in lt if l.startswith("launch ")), None), "swap_at_launch": next((l for l in lt if l.startswith("vm.swapusage")), None),
                       "exit_line": next((l for l in lt if l.startswith("exit ")), None), "stdout_lines": [l for l in lt if not l.startswith(("launch ", "vm.swapusage", "exit "))][:50]}
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    except Exception:
        head, dirty = None, None
    import numpy, scipy
    try:
        cpu = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip()
        mem = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip()
    except Exception:
        cpu, mem = None, None
    man = {"label": "VALIDATION (fixture; not the study)" if fixture else "STUDY", "study": STUDY, "written_utc": f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}",
           "lock": None if fixture else {"path": str(OUT / "PRE_RUN_LOCK.json"), "sha256": sha(ROOT / OUT / "PRE_RUN_LOCK.json"), "verified_at_manifest": True, "date": lock["date"], "approved_by": lock["approved_by"],
                                         "before_outcomes": lock["before_outcomes"], "final": lock["final"], "review": lock["review"]},
           "git": {"head_at_manifest": head, "tracked_changes_at_manifest": dirty, "launch": launch_info},
           "run": {"log": log, "start_utc": plog["start_utc"], "end_utc": plog["end_utc"], "duration_hours": dur_h, "n_start_lines": plog["n_start_lines"], "start_lines": plog["start_lines"],
                   "n_done_lines": plog["n_done_lines"], "skipped_chains_on_resume": plog["skipped_chains"], "sum_chain_seconds": round(total_chain_s, 1), "sum_chain_hours": round(total_chain_s / 3600, 3),
                   "projected_hours_validation": proj_total_h},
           "inventory": {"cells_dir": str(cells), "n_cell_files": len(cell_files), "n_expected": len(expected), "complete": len(cell_files) == len(expected) and {c["file"] for c in expected} == set(digests),
                         "n_live": n_live, "n_markers": n_marker, "n_no_detection": n_nodet, "n_cost_records": len(costs), "inventory_sha256": inventory_digest},
           "chains": chains,
           "environment": {"python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__, "platform": platform.platform(), "machine": platform.machine(), "cpu": cpu,
                           "memory_bytes": int(mem) if mem and mem.isdigit() else mem, "PYTHONHASHSEED": "0 (set at launch)"},
           "deviations": []}
    out.write_text(json.dumps(man, indent=1))
    print(json.dumps({k: man[k] for k in ("label", "written_utc")} | {"run": {k: man["run"][k] for k in ("start_utc", "end_utc", "duration_hours", "n_start_lines", "sum_chain_hours", "projected_hours_validation")}, "inventory": man["inventory"]}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
