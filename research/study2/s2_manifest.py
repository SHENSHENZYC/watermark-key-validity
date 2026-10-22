"""Study 2 run manifest: rebuilt from the run log, the cost records, the lock, the launch notes and the environment (never from memory).
Writes outputs/study2_v0.1/RUN_MANIFEST.json with: the lock (verified again; digest, date, approval, review), the git commit named in the
launch notes and the one at manifest time, the run's start and end (UTC) from the run log, the per-chain table (built size, build, key-loop
and cell-statistics seconds, cells, chain seconds, peak RSS) from the cost records with the validation's fitted projection of that chain
beside it (the cost model of VALIDATION.json applied to the sizes of INPUTS.json, exactly as the validator projected the grid), the totals
against the fitted and the probe-scaled projections, the number of "start" lines (restarts) and "skipped" chains (resumes), the inventory
(cells on disk, a digest over every cell file) and the machine state at launch (from the launch notes: HEAD, swap, the wrapper).
Usage: .venv/bin/python research/study2/s2_manifest.py [--launch-notes outputs/study2_v0.1/launch_notes.log]
       [--fixture --log <validation_run.log> --cells <validation dir> --out <file outside the canonical path>]   (no lock; labelled VALIDATION)
"""
import datetime, hashlib, json, pathlib, platform, re, subprocess, sys
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study1")); sys.path.insert(0, str(ROOT / "tools"))
from s2_run import OUT, STUDY, GRID_CANON, VALIDATION, INPUTS, verify_lock, sha, expected_cells   # noqa: E402

TS = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)")


def parse_log(path):
    lines = pathlib.Path(path).read_text().splitlines()
    starts = [l for l in lines if l.startswith("start ")]; dones = [l for l in lines if l.startswith("DONE ")]
    built = {}; scored = {}; done = {}; skipped = []; n_cell_lines = 0
    for l in lines:
        m = TS.match(l)
        if not m:
            continue
        t = m.group(1); rest = l[len(t) + 1:]
        mb = re.match(r"chain (\S+) built: \|D\|=(\d+) contexts=(\d+) \(([\d.]+)s\)", rest)
        ms = re.match(r"\s+(\S+): (\d+) keys scored for (\d+) \(rule, L\) combos in ([\d.]+)s \(nnz total (\d+)\)", rest)
        md = re.match(r"chain (\S+) done \(([\d.]+)s; peak RSS so far ([\d.]+) GB\)", rest)
        mk = re.match(r"chain (\S+): every cell present", rest)
        if mb:
            built[mb.group(1)] = {"built_utc": t, "n_tuples": int(mb.group(2)), "n_contexts": int(mb.group(3)), "build_seconds_log": float(mb.group(4))}
        elif ms:
            scored[ms.group(1)] = {"K": int(ms.group(2)), "n_combos": int(ms.group(3)), "key_loop_seconds_log": float(ms.group(4)), "nnz_total": int(ms.group(5))}
        elif md:
            done[md.group(1)] = {"done_utc": t, "chain_seconds_log": float(md.group(2)), "peak_rss_gb_log": float(md.group(3))}
        elif mk:
            skipped.append(mk.group(1))
        elif rest.startswith("  cell "):
            n_cell_lines += 1
    first_ts = next((TS.match(l).group(1) for l in lines if TS.match(l)), None)
    start_utc = re.search(r"run (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", starts[0]).group(1) if starts else first_ts
    end_utc = dones[-1].split()[1] if dones else None
    return {"n_start_lines": len(starts), "start_lines": starts, "n_done_lines": len(dones), "start_utc": start_utc, "end_utc": end_utc, "chains_built": built, "chains_scored": scored, "chains_done": done,
            "skipped_chains": skipped, "n_cell_lines": n_cell_lines, "n_lines": len(lines)}


def projection_per_chain(grid):
    """The validator's cost model (VALIDATION.json rates) applied to the key-free sizes (INPUTS.json), chain by chain, at the grid's N and K."""
    try:
        v = json.loads((ROOT / VALIDATION).read_text()); inp = json.loads((ROOT / INPUTS).read_text())
    except Exception:
        return {}, None, None, None
    rt = v["timing"]["real_sized_synthetic_chain"]; r_hash = rt["hash_seconds_per_tuple_key"]; r_prod = rt["product_seconds_per_nnz_key_scoring"]; cf = rt["cell_statistics_fit"]; N = grid["N"]; K = grid["K"]

    def stat_seconds(fam, nnz):
        return max(cf[fam]["a_per_nnz"] * nnz + cf[fam]["b_per_NK"] * N * K + cf[fam]["c"], 0.5)
    per = {}
    for name, chn in inp["chains"].items():
        if not name.endswith(f"__N{N}"):
            continue
        nnz = sum(c["nnz"] for c in chn["cells"].values()); hash_t = r_hash * chn["n_tuples"] * K; prod_t = r_prod * nnz * K * 3
        stat_t = sum(2 * stat_seconds("kgw", c["nnz"]) + stat_seconds("gumbel", c["nnz"]) + (2 * stat_seconds("kgw", c["nnz"]) if chn["h"] == 0 else 0.0) for c in chn["cells"].values())
        per[name[: -len(f"__N{N}")]] = round(chn["build_seconds"] + hash_t + prod_t + stat_t, 1)
    key = f"N{N}_K{K}"; fitted_h = v["projection"].get(key, {}).get("hours"); ratio = v["projection"].get("runner_probe_vs_projection", {}).get("ratio_probe_over_projection")
    ratio_max = max(ratio) if ratio else None; probe_h = round(fitted_h * ratio_max, 2) if (fitted_h is not None and ratio_max) else None
    return per, fitted_h, probe_h, {"ratio_probe_over_projection": ratio, "ratio_used": ratio_max, "projection_key": key, "validation_sha256": sha(ROOT / VALIDATION), "inputs_sha256": sha(ROOT / INPUTS)}


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
    costs = {}
    for f in sorted(cells.glob("costs__*.json")):
        c = json.loads(f.read_text()); costs[c["tag"]] = c
    cell_files = sorted(f for f in cells.glob("*.json") if not f.name.startswith("costs__"))
    digests = {f.name: sha(f) for f in cell_files}; inventory_digest = hashlib.sha256("".join(f"{k}:{v}\n" for k, v in sorted(digests.items())).encode()).hexdigest()
    n_live = 0; n_marker = 0; n_fixture = 0
    for f in cell_files:
        d = json.loads(f.read_text()); n_fixture += int("FIXTURE" in d)
        if "levels" not in d:
            n_marker += 1
        else:
            n_live += 1
    expected = expected_cells(grid, validation=fixture)
    per_proj, fitted_h, probe_h, proj_meta = ({}, None, None, None) if fixture else projection_per_chain(grid)
    chains = []
    for tag in sorted(set(costs) | set(plog["chains_built"])):
        c = costs.get(tag, {}); b = plog["chains_built"].get(tag, {}); s_ = plog["chains_scored"].get(tag, {}); d = plog["chains_done"].get(tag, {})
        chains.append({"chain": tag, "n_tuples": c.get("n_tuples", b.get("n_tuples")), "n_contexts": c.get("n_contexts", b.get("n_contexts")), "build_seconds": c.get("build_seconds", b.get("build_seconds_log")),
                       "key_loop_seconds": (c.get("key_loop") or {}).get("seconds", s_.get("key_loop_seconds_log")), "nnz_total": (c.get("key_loop") or {}).get("nnz_total", s_.get("nnz_total")),
                       "n_cells_computed": len(c.get("cells", [])) if c else None, "cells_seconds": round(sum(x["seconds"] for x in c.get("cells", [])), 1) if c else None,
                       "chain_seconds": c.get("chain_seconds", d.get("chain_seconds_log")), "peak_rss_gb": c.get("peak_rss_gb", d.get("peak_rss_gb_log")), "built_utc": b.get("built_utc"), "done_utc": d.get("done_utc"),
                       "projected_chain_seconds": per_proj.get(tag)})
    total_chain_s = sum(x["chain_seconds"] or 0 for x in chains); dur_h = None
    if plog["start_utc"] and plog["end_utc"]:
        t0 = datetime.datetime.strptime(plog["start_utc"], "%Y-%m-%dT%H:%M:%SZ"); t1 = datetime.datetime.strptime(plog["end_utc"], "%Y-%m-%dT%H:%M:%SZ"); dur_h = round((t1 - t0).total_seconds() / 3600, 3)
    launch_info = {}
    if launch and pathlib.Path(launch).exists():
        lt = pathlib.Path(launch).read_text().splitlines()
        head_line = next((l for l in lt if l.startswith("HEAD at launch")), None)
        launch_info = {"launch_line": next((l for l in lt if l.startswith("launch ")), None), "head_at_launch": head_line.split()[3] if head_line else None, "head_line": head_line,
                       "swap_at_launch": next((l.split(": ", 1)[1] for l in lt if l.startswith("vm.swapusage")), None), "machine_state": next((l for l in lt if l.startswith("machine state")), None), "wrapper": next((l for l in lt if l.startswith("wrapper")), None), "lines": lt}
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
    man = {"label": "VALIDATION (fixture; not the study)" if fixture else "STUDY", "study": STUDY, "written_utc": f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}",
           "lock": None if fixture else {"path": str(OUT / "PRE_RUN_LOCK.json"), "sha256": sha(ROOT / OUT / "PRE_RUN_LOCK.json"), "verified_at_manifest": True, "date": lock["date"], "approved_by": lock["approved_by"], "before_outcomes": lock["before_outcomes"], "final": lock["final"], "review": lock["review"]},
           "git": {"head_at_manifest": head, "tracked_changes_at_manifest": dirty, "launch": launch_info},
           "run": {"log": log, "start_utc": plog["start_utc"], "end_utc": plog["end_utc"], "duration_hours": dur_h, "n_start_lines": plog["n_start_lines"], "start_lines": plog["start_lines"], "n_done_lines": plog["n_done_lines"],
                   "skipped_chains_on_resume": plog["skipped_chains"], "n_cell_lines_in_log": plog["n_cell_lines"], "sum_chain_seconds": round(total_chain_s, 1), "sum_chain_hours": round(total_chain_s / 3600, 3),
                   "projected_hours_fitted": fitted_h, "projected_hours_probe_scaled": probe_h, "projection": proj_meta, "peak_rss_gb_max": max((x["peak_rss_gb"] for x in chains if x["peak_rss_gb"] is not None), default=None),
                   "sum_projected_chain_seconds": round(sum(v for v in per_proj.values()), 1) if per_proj else None},
           "inventory": {"cells_dir": str(cells), "n_cell_files": len(cell_files), "n_expected": len(expected), "complete": len(cell_files) == len(expected) and {c["file"] for c in expected} == set(digests), "n_live": n_live, "n_markers": n_marker,
                         "n_fixture_marked": n_fixture, "n_cost_records": len(costs), "inventory_sha256": inventory_digest},
           "chains": chains,
           "environment": {"python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__, "platform": platform.platform(), "machine": platform.machine(), "cpu": cpu, "memory_bytes": int(mem) if mem and mem.isdigit() else mem, "PYTHONHASHSEED": "0 (set at launch)"},
           "deviations": [] if fixture else ["pre-run checklist item 1 (a freshly restarted machine) not met: Yichen chose to quit the other applications and start (decision log 2026-10-13); outputs are deterministic, only timing depends on the machine state"]}
    if not fixture and n_fixture:
        raise SystemExit(f"{n_fixture} cell files carry a FIXTURE marker in the canonical cells directory")
    out.write_text(json.dumps(man, indent=1))
    print(json.dumps({k: man[k] for k in ("label", "written_utc")} | {"run": {k: man["run"][k] for k in ("start_utc", "end_utc", "duration_hours", "n_start_lines", "sum_chain_hours", "projected_hours_fitted", "projected_hours_probe_scaled", "peak_rss_gb_max")}, "inventory": man["inventory"]}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
