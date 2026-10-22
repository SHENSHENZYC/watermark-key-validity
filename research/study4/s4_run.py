"""Study 4 runner (v1): the generation record. In study mode it verifies the lock (the pinned files' digests, the review's resolution, the
key record, Study 3's record digests), binds Study 3's record through s4_record, loads the pinned model (weights re-hashed against the model
manifest) and generates unit by unit, resumable: a complete unit whose provenance and digests match is reused and logged; a mismatching
unit is refused (never overwritten); a unit with an array file and no record is incomplete and is regenerated.

Units (study mode; the grid's order, cell by cell: the null units first, then every arm's keys):
  null__<cell>__c<chunk>      n_per_unit (500) unwatermarked continuations of production prompts [chunk*500, (chunk+1)*500)
  gen__<cell>__<arm>__k<key>  n_watermarked (50) continuations of production prompts [0, 50) under one evaluation key and one arm
Record per unit: <name>.npz (tokens int32 N x n_new; logp float32: the model's unshifted log-probability of each chosen token; flag uint8:
the hook's green flag (gen units); eos_mass float16: the excluded EOS's mass per step) and <name>.json (provenance, digests, timing).
The sampler's generator is seeded per unit by (int(sha256(unit name)[:8], 16), 20261016); MPS bfloat16 logits are not promised
bit-reproducible, so the committed arrays are the record and every downstream number is recomputed from them.
Validation mode (--validation): validation keys, the pilot prompts of the grid's first cell, a scratch output directory, no lock.
Usage: caffeinate -i .venv/bin/python -u research/study4/s4_run.py --grid research/study4/grid_v0.1.json [--lock outputs/study4_v0.1/PRE_RUN_LOCK.json | --validation] [--out DIR] [--limit N]
"""
import datetime, hashlib, json, pathlib, resource, subprocess, sys, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import s4_gen as G, s4_data as SD, s4_keys as K4, s4_record as RC, s4_wm as W

STUDY = "study4_v0.1"
OUT = ROOT / "outputs/study4_v0.1"
PINNED = ["research/STUDY4_PROTOCOL_v0.1.md", "research/study4/grid_v0.1.json", "outputs/study4_v0.1/VALIDATION.json", "outputs/study4_v0.1/INPUTS.json",
          "outputs/study4_v0.1/prompts_manifest.json", "outputs/study4_v0.1/model_manifest_qwen2.5-1.5b.json",
          "research/study4/s4_core.py", "research/study4/s4_run.py", "research/study4/s4_analyze.py", "research/study4/s4_validate.py", "research/study4/s4_data.py", "research/study4/s4_keys.py",
          "research/study4/s4_wm.py", "research/study4/s4_gen.py", "research/study4/s4_record.py", "research/study4/s4_inputs.py",
          "research/study3/s3_core.py", "research/study3/s3_data.py", "research/study3/s3_keys.py", "research/study3/s3_run.py", "research/study3/grid_v0.1.json", "outputs/study3_v0.1/RUN_MANIFEST.json", "outputs/study3_v0.1/PRE_RUN_LOCK.json", "outputs/study3_v0.1/tokens_manifest.json", "outputs/study3_v0.1/INPUTS.json",
          "research/study2/s2_core.py", "research/study2/s2_data.py", "research/study2/s2_keys.py", "outputs/study2_v0.1/tokens_manifest.json", "research/study1/s1_core.py", "tools/key_policy.py", "tools/corpora_access.py"]
GRID_CANON = "research/study4/grid_v0.1.json"
RESOLUTION_CANON = "research/reviews/R09_study4-protocol/RESOLUTION.md"
PROV_SKIP = ("written_utc",)


class ProvenanceError(RuntimeError):
    pass


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def utc():
    return f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}"


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30


def unit_seed(name):
    return int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)


def verify_lock(lock_path, grid_path, root=ROOT):
    """Explicit exceptions, never assert. The lock pins exactly PINNED; the review is R09 with its resolution's digest; the key record is the
    grid's; Study 3's record digests are the grid's and the actual record's."""
    root = pathlib.Path(root); lock = json.loads(pathlib.Path(lock_path).read_text())
    if pathlib.Path(grid_path).resolve() != (root / GRID_CANON).resolve():
        raise ProvenanceError(f"the grid must be the canonical locked file {GRID_CANON}; got {grid_path}")
    grid = json.loads((root / GRID_CANON).read_text())   # the grid returned to the caller is the pinned file's content
    req = {"study": STUDY, "approved_by": "Yichen", "before_outcomes": True, "final": False, "grid": "research/study4/grid_v0.1.json", "protocol": "research/STUDY4_PROTOCOL_v0.1.md",
           "validation": "outputs/study4_v0.1/VALIDATION.json", "inputs": "outputs/study4_v0.1/INPUTS.json", "prompts_manifest": "outputs/study4_v0.1/prompts_manifest.json", "model_manifest": "outputs/study4_v0.1/model_manifest_qwen2.5-1.5b.json"}
    for k, v in req.items():
        if lock.get(k) != v:
            raise ProvenanceError(f"lock field {k!r} is {lock.get(k)!r}, expected {v!r}")
    try:
        datetime.date.fromisoformat(lock.get("date", ""))
    except ValueError:
        raise ProvenanceError("lock date is not an ISO date")
    h = lock.get("hashes", {})
    if set(h) != set(PINNED):
        raise ProvenanceError(f"lock pins {sorted(set(h) ^ set(PINNED))} differently from the canonical set")
    for rel, d in h.items():
        if not isinstance(d, str) or len(d) != 64 or sha(root / rel) != d:
            raise ProvenanceError(f"pinned file {rel} differs from its locked digest")
    rv = lock.get("review", {})
    if rv.get("checkpoint") != "R09" or rv.get("resolution") != RESOLUTION_CANON or not (root / RESOLUTION_CANON).exists() or sha(root / RESOLUTION_CANON) != rv.get("sha256"):
        raise ProvenanceError("the lock's review record is not R09's resolution file at its digest")
    ks = lock.get("keys", {})
    if ks.get("K4") != grid["keys"]["K4"] or ks.get("subset_seed") != grid["keys"]["subset_seed"] or ks.get("power_keys_sha256") != hashlib.sha256(json.dumps(grid["keys"]["power_keys"]).encode()).hexdigest():
        raise ProvenanceError("the lock's key record differs from the grid's")
    if grid["keys"]["power_keys"] != K4.power_keys(grid["keys"]["subset_seed"], grid["keys"]["K4"]):
        raise ProvenanceError("the grid's power keys are not the seeded subset")
    K4.check_keys(grid["keys"]["power_keys"], "study4_power")
    rec = lock.get("record", {})
    R = RC.Record(verify_files=True)
    if rec.get("inventory_sha256") != grid["record"]["inventory_sha256"] or R.man["inventory"]["inventory_sha256"] != grid["record"]["inventory_sha256"] or rec.get("lock_sha256") != grid["record"]["lock_sha256"] or R.lock_sha != grid["record"]["lock_sha256"]:
        raise ProvenanceError("Study 3's record digests differ between the lock, the grid and the record")
    return lock, grid, R


def expected_units(grid, validation=False):
    units = []
    if validation:
        v = grid["validation"]; cell = grid["cells"][0]; keys = list(range(v["keys_start"], v["keys_start"] + v["n_keys"]))
        units.append({"kind": "null", "cell": cell, "chunk": 0, "n": v["null_n"], "prompt_range": [0, v["null_n"]]})
        for arm in grid["arms"]:
            for k in keys:
                units.append({"kind": "gen", "cell": cell, "arm": arm["name"], "key": k, "n": v["n_prompts"], "prompt_range": [0, v["n_prompts"]]})
        return units
    na = grid["null_arm"]; n_chunks = na["n_texts"] // na["n_per_unit"]
    for cell in grid["cells"]:
        for c in range(n_chunks):
            units.append({"kind": "null", "cell": cell, "chunk": c, "n": na["n_per_unit"], "prompt_range": [c * na["n_per_unit"], (c + 1) * na["n_per_unit"]]})
        for arm in grid["arms"]:
            for k in grid["keys"]["power_keys"]:
                units.append({"kind": "gen", "cell": cell, "arm": arm["name"], "key": k, "n": grid["prompts"]["n_watermarked"], "prompt_range": [0, grid["prompts"]["n_watermarked"]]})
    return units


def unit_name(u):
    return f"null__{u['cell']}__c{u['chunk']}" if u["kind"] == "null" else f"gen__{u['cell']}__{u['arm']}__k{u['key']}"


def arm_spec(grid, name):
    return next(a for a in grid["arms"] if a["name"] == name)


def provenance(mode, lock_sha, grid, grid_sha, pm_sha, prompt_sha, model_man, code, u, prompts_kind):
    arm = arm_spec(grid, u["arm"]) if u["kind"] == "gen" else {"name": "none", "family": None, "h": None, "delta": None}
    return {"study": STUDY, "mode": mode, "lock_sha256": lock_sha, "grid_sha256": grid_sha, "code_sha256": code, "prompts_manifest_sha256": pm_sha, "prompts_kind": prompts_kind, "prompt_array_sha256": prompt_sha,
            "model": {"repo": model_man["repo"], "revision": model_man["revision"], "weights_sha256": model_man["files"]["model.safetensors"]["sha256"]},
            "unit": {k: v for k, v in u.items()}, "arm": arm, "gamma": grid["gamma"], "n_new": grid["generation"]["n_new"], "P": grid["prompts"]["P"], "temperature": grid["generation"]["temperature"],
            "seed": unit_seed(unit_name(u)), "sampler": grid["generation"]["sampler"]}


def prov_equal(a, b):
    return {k: v for k, v in a.items() if k not in PROV_SKIP} == {k: v for k, v in b.items() if k not in PROV_SKIP}


def unit_status(out_dir, name, prov):
    jp, npz = out_dir / f"{name}.json", out_dir / f"{name}.npz"
    if jp.exists():
        rec = json.loads(jp.read_text())
        if "FIXTURE" in rec or not prov_equal(rec.get("provenance", {}), prov) or not npz.exists() or sha(npz) != rec.get("npz_sha256"):
            raise ProvenanceError(f"{name}: an existing record does not match this run's provenance or its array digest; refusing to overwrite")
        return "reuse"
    return "incomplete" if npz.exists() else "new"


def unit_projection(grid, proj, u):
    """The validator's projected wall seconds for one unit (VALIDATION.json cost: per generation unit by arm at the validation size, scaled to the unit's size; per null text)."""
    if u["kind"] == "null":
        return proj["wall_seconds_per_null_text"] * u["n"]
    return proj["wall_seconds_per_gen_unit_by_arm"][u["arm"]] * u["n"] / grid["validation"]["n_prompts"]


def projected_hours(grid, proj, units_generated):
    """The validator's projection summed over the units this invocation generated (reused units are not credited: R09 F17)."""
    return sum(unit_projection(grid, proj, x) for x in units_generated) / 3600


def budget_exceeded(elapsed_h, projected_h, factor):
    return elapsed_h > factor * projected_h


def memory_line():
    """MPS allocated and driver memory and the machine's swap at this moment (the process RSS alone misses Metal memory: R09)."""
    try:
        import torch, subprocess
        sw = subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True).stdout.strip()
        return f"mps_alloc_gb={torch.mps.current_allocated_memory() / 1e9:.2f} mps_driver_gb={torch.mps.driver_allocated_memory() / 1e9:.2f} rss_gb={rss_gb():.2f} swap={sw}"
    except Exception as e:
        return f"memory unavailable ({type(e).__name__})"


def run_unit(model, info, grid, u, prompts_X, prov, out_dir, cache, log):
    name = unit_name(u); P = grid["prompts"]["P"]; n_new = grid["generation"]["n_new"]; t0 = time.time()
    lo, hi = u["prompt_range"]
    if hi > prompts_X.shape[0] or hi - lo != u["n"]:
        raise ProvenanceError(f"{name}: prompt range {lo}-{hi} exceeds the prompt cache ({prompts_X.shape[0]} rows) or differs from the unit's size {u['n']}")
    pr = prompts_X[lo:hi, :P]
    if u["kind"] == "gen":
        arm = arm_spec(grid, u["arm"]); B = grid["generation"]["batch_watermarked"]
        parts = [G.generate_batch(model, info, pr[i:i + B], n_new, "kgw", key=u["key"], h=arm["h"], delta=arm["delta"], gamma=grid["gamma"], seed=prov["seed"] + i, cache=cache) for i in range(0, len(pr), B)]
    else:
        B = grid["generation"]["batch_null"]
        parts = [G.generate_batch(model, info, pr[i:i + B], n_new, "none", seed=prov["seed"] + i) for i in range(0, len(pr), B)]
    tokens = np.concatenate([p["tokens"] for p in parts]).astype(np.int32); logp = np.concatenate([p["logp"] for p in parts]).astype(np.float32)
    eos = np.concatenate([p["eos_mass"] for p in parts]).astype(np.float16)
    arrays = {"tokens": tokens, "logp": logp, "eos_mass": eos}
    if u["kind"] == "gen":
        arrays["flag"] = np.concatenate([p["flag"] for p in parts]).astype(np.uint8)
    npz = out_dir / f"{name}.npz"; np.savez_compressed(npz, **arrays)
    secs = sum(p["seconds"] for p in parts); rec = {"unit": u, "name": name, "n": int(tokens.shape[0]), "n_new": int(tokens.shape[1]), "npz_sha256": sha(npz),
           "seconds": round(secs, 1), "tok_per_s": round(tokens.size / secs, 1), "seconds_model": round(sum(p["seconds_model"] for p in parts), 1), "seconds_hook": round(sum(p["seconds_hook"] for p in parts), 1),
           "cache_hits": int(sum(p["cache_hits"] for p in parts)), "cache_misses": int(sum(p["cache_misses"] for p in parts)), "green_share_hook": float(arrays["flag"].mean()) if "flag" in arrays else None,
           "mean_logp": float(logp.mean()), "eos_mass_mean": float(eos.astype(np.float32).mean()), "peak_rss_gb": round(rss_gb(), 2), "provenance": dict(prov, written_utc=utc())}
    (out_dir / f"{name}.json").write_text(json.dumps(rec, indent=0))
    log(f"{utc()}   done {name} ({rec['seconds']}s, {rec['tok_per_s']} tok/s, rss {rec['peak_rss_gb']} GB)")
    return rec


def main(grid_path, lock_path=None, validation=False, out_dir=None, limit=None):
    grid = json.loads(pathlib.Path(grid_path).read_text()); grid_sha = sha(grid_path); mode = "validation" if validation else "study"
    if validation:
        lock_sha = None; R = RC.Record(verify_files=False); out_dir = pathlib.Path(out_dir) if out_dir else OUT / f"validation_{utc().replace(':', '').replace('-', '')}" / "cells"
        pm_path = ROOT / grid["prompts"]["pilot_manifest"]; prompts_kind = "pilot"
        K4.check_keys(list(range(grid["validation"]["keys_start"], grid["validation"]["keys_start"] + grid["validation"]["n_keys"])), "validation")
    else:
        if lock_path is None:
            raise ProvenanceError("study mode needs --lock")
        lock, grid2, R = verify_lock(lock_path, grid_path); lock_sha = sha(lock_path); out_dir = pathlib.Path(out_dir) if out_dir else OUT / "cells"
        pm_path = ROOT / grid["prompts"]["manifest"]; prompts_kind = "prod"
    out_dir.mkdir(parents=True, exist_ok=True)
    pm = json.loads(pm_path.read_text()); pm_sha = sha(pm_path)
    model_man = json.loads((ROOT / grid["model"]["weights_manifest"]).read_text())
    code = {f: sha(HERE / f) for f in ("s4_gen.py", "s4_wm.py", "s4_run.py", "s4_data.py", "s4_keys.py", "s4_record.py")}
    log_path = out_dir.parent / "run.log"; lf = open(log_path, "a")
    def log(m):
        lf.write(m + "\n"); lf.flush(); print(m, flush=True)
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    except Exception:
        head = None
    log(f"start {mode} run {utc()} grid={grid_path} sha={grid_sha} out={out_dir} lock={lock_sha} HEAD={head} limit={limit}")
    # the weights re-hashed against the manifest before loading
    snap = pathlib.Path(model_man["snapshot_dir"]) / "model.safetensors"
    if sha(snap) != model_man["files"]["model.safetensors"]["sha256"] or model_man["revision"] != grid["model"]["revision"]:
        raise ProvenanceError("the model weights differ from the model manifest, or the revision differs from the grid's")
    model, tok, info = G.load_model(grid["model"]["name"], device=grid["model"]["device"], dtype=grid["model"]["dtype"]); info = G.prepare_info(model, tok, info)
    if info["V"] != grid["model"]["V"]:
        raise ProvenanceError(f"model vocabulary {info['V']} differs from the grid's {grid['model']['V']}")
    units = expected_units(grid, validation); prompts = {}; n_done = 0; n_reused = 0; current_phase = None; t_run = time.time(); generated_units = []
    vpath = OUT / "VALIDATION.json"; proj = (json.loads(vpath.read_text()).get("cost") if (vpath.exists() and not validation) else None)
    log(f"{utc()} launch memory | {memory_line()}")
    for u in units:
        if limit is not None and n_done >= limit:
            break
        name = unit_name(u); tag = u["cell"]
        if tag not in prompts:
            prompts[tag] = SD.load_prompts(pm, tag, prompts_kind)
        prompt_sha = pm["cells"][tag]["kinds"][prompts_kind]["sha256"]
        prov = provenance(mode, lock_sha, grid, grid_sha, pm_sha, prompt_sha, model_man, code, u, prompts_kind)
        phase = f"{tag} {'null' if u['kind'] == 'null' else u['arm']}"
        if phase != current_phase:
            # the budget stop (protocol section 10), per invocation: this invocation's elapsed hours against twice the projection for the units it generated
            if proj is not None and n_done > 0:
                proj_done = projected_hours(grid, proj, generated_units); el_h = (time.time() - t_run) / 3600
                if budget_exceeded(el_h, proj_done, grid["stop"]["max_hours_factor_over_projection"]):
                    log(f"{utc()} BUDGET STOP: this invocation's elapsed {el_h:.3f} h exceeds {grid['stop']['max_hours_factor_over_projection']} x the projection {proj_done:.3f} h for the {n_done} units it generated (reused units excluded); the completed units are kept"); lf.close()
                    raise SystemExit(3)
            log(f"{utc()} start phase {phase} | {memory_line()}"); current_phase = phase
        st = unit_status(out_dir, name, prov)
        if st == "reuse":
            n_reused += 1; log(f"{utc()}   reused {name}"); continue
        if st == "incomplete":
            log(f"{utc()}   incomplete {name}: array without record; regenerating")
        cache = W.HookCache(info["V"], max_entries=512, g=W.C.green_fraction(grid["gamma"], info["V"])) if u["kind"] == "gen" else None
        run_unit(model, info, grid, u, prompts[tag], prov, out_dir, cache, log); n_done += 1; generated_units.append(u)
    log(f"end {mode} run {utc()} units_generated={n_done} units_reused={n_reused} hours={(time.time() - t_run) / 3600:.3f} peak_rss_gb={rss_gb():.2f} | {memory_line()}")
    lf.close()
    return out_dir


if __name__ == "__main__":
    a = sys.argv[1:]
    def opt(k, default=None):
        return a[a.index(k) + 1] if k in a else default
    main(opt("--grid", "research/study4/grid_v0.1.json"), lock_path=opt("--lock"), validation="--validation" in a, out_dir=opt("--out"), limit=int(opt("--limit")) if opt("--limit") else None)
