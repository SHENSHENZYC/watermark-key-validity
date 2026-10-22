"""Study 4 validator (v1; before the lock; validation keys and pilot prompts only; no evaluation key is generated with). Fixtures and
measurements, every one recorded in outputs/study4_v0.1/VALIDATION.json (pinned by the lock):
 F1 the hook-detector equality on synthetic texts at h = 0, 1, 2 (s4_wm.check_against_detector);
 F2 the record binding: the real record accepted (inventory digest, lock digest, key binding); four refusals on scratch copies;
 F3 the core's self-tests (uniform null p-values; the planted between-key SD; the pooled-law predictor against the normal; classifications);
 F4 the analyzer on the validation record: accepted and complete; then refusals on scratch copies (a missing unit, an extra file, a tampered
    array, a relabelled provenance, a token outside the vocabulary, a positive log-probability) and the contract path (a flipped hook flag is
    counted as a contract failure, not refused; the run-void share);
 F5 the lock schema: a well-formed lock on a scratch copy of the pinned files accepted; variants refused (a missing pinned file, a changed digest,
    the wrong checkpoint, a wrong key record, a wrong Study 3 inventory digest, final true, before_outcomes false, a non-ISO date, a pinned set differing);
 F6 the cost projection from the validation run's own unit wall-clock times (the runner itself at the production batch size), scaled to the
    production inventory; the analyzer's output size scaled likewise;
 F7 the pre-lock inputs: the pilot law per arm (its hook flags equal the detector; n texts), the human reference per cell;
 F8 the prompts: the production cache digests, the plan reproduced, disjointness from the Study 2/3 sets and the pilot ids; the key subset
    reproduced from its seed; the key policy's refusals;
 F9 every branch of the rule rows with planted data (W1, W2, W3), the two-way estimator under a random model with an interaction and on a
    fixed table, the zero-denominator guard, the finite-share boundary through the decision helper and through w2_row, the key-bootstrap
    interval's coverage of the prompt-conditional and of the population ratio on exact-target paired tables at the planned sizes (interval
    availability required; the reviewer's shared-additive-interaction model of R09 F22 included; the superseded crossed construction and
    two constructions with a prompt channel recorded), the pooled law at ties, the sampler against a compensated cumulative sum with two
    float32 mutants;
 F10 the budget stop's accounting on a resumed run (model-free), from this run's own cost projection.
Usage: .venv/bin/python -u research/study4/s4_validate.py --grid research/study4/grid_v0.1.json --record outputs/study4_v0.1/validation_runner_test/cells
"""
import copy, datetime, hashlib, json, pathlib, re, shutil, sys, tempfile, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study2")); sys.path.insert(0, str(ROOT / "research/study3"))
import s4_core as T4, s4_run as R, s4_record as RC, s4_analyze as A, s4_wm as W, s4_data as SD, s4_keys as K4
import s2_data as D

OUT = ROOT / "outputs/study4_v0.1"


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def utc():
    return f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}"


def expect_refusal(fn, exc_types, label, results):
    try:
        fn(); results[label] = "ACCEPTED (wrong)"; return False
    except exc_types as e:
        results[label] = f"refused: {type(e).__name__}: {str(e)[:90]}"; return True


def main(grid_path, record_dir):
    grid = json.loads(pathlib.Path(grid_path).read_text()); record_dir = pathlib.Path(record_dir); res = {"study": grid["study"], "written_utc": utc(), "grid_sha256": sha(grid_path), "record_dir": str(record_dir), "fixtures": {}, "all_ok": True}
    def ok(name, cond, detail=None):
        res["fixtures"][name] = {"ok": bool(cond), "detail": detail}; res["all_ok"] = res["all_ok"] and bool(cond); print(f"{'ok ' if cond else 'FAIL'} {name}: {detail if detail is not None else ''}", flush=True)
    V = grid["model"]["V"]
    # F1 hooks against the detector
    rng = np.random.default_rng(99261017); f1 = {h: W.check_against_detector(rng, h=h) for h in (0, 1, 2)}; bc = W.boundary_case()
    ok("F1_hook_equals_detector", all(v["ok"] for v in f1.values()) and bc["ok"] and bc["detector_green"] and not bc["float32_would_say"],
       {h: {k: v[k] for k in ("green_equal_on_scored", "uniforms_exactly_equal_on_scored", "batch_hash_equal", "key_switch_ok", "n_scored")} for h, v in f1.items()} | {"boundary_case_R09_F2": bc})
    # F2 the record binding
    Rrec = RC.Record(verify_files=True); det = {"inventory_sha256": Rrec.man["inventory"]["inventory_sha256"], "lock_sha256": Rrec.lock_sha, "keys": [int(Rrec.keys[0]), int(Rrec.keys[-1])]}
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="s4_validate_")); shutil.copytree(RC.CELLS_DIR, tmp / "cells"); f2 = {}
    f = tmp / "cells/cal__qwen__news_en_256__h1__thresholds.npz"; z = np.load(f); d = {k: np.array(z[k]) for k in z.files}; d["kgw|distinct|conformal@5000|0.01"][3] *= 1.0001; np.savez_compressed(f, **d)
    expect_refusal(lambda: RC.Record(cells_dir=tmp / "cells"), RC.RecordError, "tampered_threshold", f2); shutil.copy(RC.CELLS_DIR / f.name, f)
    j = tmp / "cells/cal__qwen__news_en_256__h1.json"; rec = json.loads(j.read_text()); rec["unit"]["tag"] = "wikipedia_en_256"; j.write_text(json.dumps(rec, indent=0))
    expect_refusal(lambda: RC.Record(cells_dir=tmp / "cells"), RC.RecordError, "relabelled_record", f2); shutil.copy(RC.CELLS_DIR / j.name, j)
    (tmp / "cells/eval__llama__news_en_256__h0.npz").unlink(); expect_refusal(lambda: RC.Record(cells_dir=tmp / "cells"), RC.RecordError, "missing_file", f2); shutil.copy(RC.CELLS_DIR / "eval__llama__news_en_256__h0.npz", tmp / "cells/eval__llama__news_en_256__h0.npz")
    man = json.loads(RC.MANIFEST.read_text()); man["lock"]["sha256"] = "0" * 64; mp = tmp / "manifest.json"; mp.write_text(json.dumps(man)); expect_refusal(lambda: RC.Record(manifest=mp, verify_files=False), RC.RecordError, "lock_digest_mismatch", f2)
    # the unit-field guard itself (digests consistent): a manifest whose digest entry is updated for the relabelled record
    rec = json.loads(j.read_text()); rec["unit"]["tag"] = "wikipedia_en_256"; j.write_text(json.dumps(rec, indent=0)); man = json.loads(RC.MANIFEST.read_text()); man["inventory"]["file_digests"][j.name] = sha(j)
    man["inventory"]["inventory_sha256"] = RC._inventory_digest(man["inventory"]["file_digests"]); mp2 = tmp / "manifest2.json"; mp2.write_text(json.dumps(man))
    expect_refusal(lambda: RC.Record(cells_dir=tmp / "cells", manifest=mp2, verify_files=True).cal("qwen", "news_en_256", 1), RC.RecordError, "relabelled_record_with_consistent_digests", f2); shutil.copy(RC.CELLS_DIR / j.name, j)
    ok("F2_record_binding", all(v.startswith("refused") for v in f2.values()), det | f2)
    # F3 the core's self-tests (re-run here)
    import subprocess
    r3 = subprocess.run([sys.executable, str(HERE / "s4_core.py")], capture_output=True, text=True); ok("F3_core_selftests", "ALL OK" in r3.stdout, r3.stdout.strip().splitlines()[-1][:120] if r3.stdout else r3.stderr[-300:])
    # F7 the pre-lock inputs: bound to the current prompt manifest and grid; the pilot law of every arm on every prompt cell (sorted p-values; flags equal the detector); W1's tolerance rule
    inputs = json.loads((OUT / "INPUTS.json").read_text()); inputs["_sha256"] = sha(OUT / "INPUTS.json"); pl = inputs["pilot_law"]; arms_ok = []; n_exp = pl["n_prompts"] * len(pl["keys"])
    for arm in grid["arms"]:
        a = pl["arms"][arm["name"]]
        for cell in grid["cells"]:
            c = a["by_cell"].get(cell)
            if c is None:
                arms_ok.append(False); continue
            fl = ROOT / c["file"]
            arms_ok.append(c["hook_flags_equal_detector"] and c["n_texts"] == n_exp and fl.exists() and sha(fl) == c["sha256"] and all(len(c["p_values"][k]) == n_exp for k in c["p_values"]) and all(0.0 <= min(v) and max(v) <= 1.0 for v in c["p_values"].values()))
    prov_ok = inputs["prompts_manifest_sha256"] == sha(OUT / "prompts_manifest.json") and inputs["grid_sha256"] == sha(grid_path) and inputs["pilot_manifest_sha256"] == sha(ROOT / grid["prompts"]["pilot_manifest"])
    tol_ok = all(c in inputs["W1_tolerance"] and abs(inputs["W1_tolerance"][c]["tolerance_pp"] - max(grid["W1"]["tolerance_pp"], 2 * inputs["W1_tolerance"][c]["cluster_bootstrap"]["se_pp"])) < 1e-9 for c in grid["cells"])
    ok("F7_pilot_law_inputs", all(arms_ok) and prov_ok and tol_ok and all(c in inputs["human_reference"] for c in grid["cells"]) and all(k >= K4.VALIDATION_MIN for k in pl["keys"]),
       {"provenance_bound_to_current_manifest_and_grid": prov_ok, "tolerance_rule_applied": tol_ok, "W1_tolerance_pp": {c: round(inputs["W1_tolerance"][c]["tolerance_pp"], 2) for c in grid["cells"] if c in inputs["W1_tolerance"]},
        "cluster_se_pp": {c: round(inputs["W1_tolerance"][c]["cluster_bootstrap"]["se_pp"], 2) for c in grid["cells"] if c in inputs["W1_tolerance"]},
        "arms": {a: {c: {"n": d["n_texts"], "power_nominal_0.01_raw256": d["z"]["raw@256"]["power_nominal_0.01"], "loop_share": d["loop_share"], "ppl": round(d["ppl"], 2)} for c, d in pl["arms"][a]["by_cell"].items()} for a in pl["arms"]},
        "human_ppl_admissible_law": {c: round(v["ppl"], 2) for c, v in inputs["human_reference"].items()}})
    # F8 prompts and keys
    pm = json.loads((OUT / "prompts_manifest.json").read_text()); cells = [c for c in SD.PROMPT_CELLS_ALL if D.cell_tag(c) in grid["cells"]]; plan = SD.plan_prompts(cells, grid["prompts"]["n_prod"], 96)
    pil = json.loads((ROOT / grid["prompts"]["pilot_manifest"]).read_text()); f8 = {}
    for c in cells:
        t = D.cell_tag(c); e = pm["cells"][t]["kinds"]["prod"]; p = ROOT / e["file"]
        f8[t] = {"array_digest_ok": p.exists() and sha(p) == e["sha256"], "ids_digest_ok": plan[t]["prod_ids_sha256"] == e["ids_sha256"], "pilot_ids_ok": plan[t]["pilot_ids_sha256"] == pil["cells"][t]["kinds"]["pilot"]["ids_sha256"], "n": e["n"], "positions": plan[t]["prod_positions"]}
    keys_ok = grid["keys"]["power_keys"] == K4.power_keys(grid["keys"]["subset_seed"], grid["keys"]["K4"]) and len(set(grid["keys"]["power_keys"])) == grid["keys"]["K4"]
    kp = {}
    expect_refusal(lambda: K4.check_keys([24000], "study4_power"), K4.KeyPolicyError, "fitting_key", kp); expect_refusal(lambda: K4.check_keys([30005], "study4_null"), K4.KeyPolicyError, "reserved_key", kp)
    expect_refusal(lambda: K4.check_keys(grid["keys"]["power_keys"][:-1] + [23001], "study4_power"), K4.KeyPolicyError, "wrong_subset", kp); expect_refusal(lambda: K4.check_keys([999], "validation"), K4.KeyPolicyError, "low_validation_key", kp)
    ok("F8_prompts_and_keys", all(all(v[k] for k in ("array_digest_ok", "ids_digest_ok", "pilot_ids_ok")) for v in f8.values()) and keys_ok and all(v.startswith("refused") for v in kp.values()), {"cells": f8, "keys_reproduced": keys_ok, "policy": kp})
    # F4 the analyzer on the validation record, then mutations
    t0 = time.time(); out, arrays = A.analyze(grid, record_dir, inputs, "validation", validation=True, log=lambda m: None); t_an = time.time() - t0
    n_units = len(R.expected_units(grid, True)); f4 = {"accepted": True, "units": n_units, "seconds": round(t_an, 1), "W1_rows": out["W1"]["n_rows"], "W2_rows": out["W2"]["n_rows"], "W3_candidates": out["W3"]["n_candidate"], "descriptive_rows": len(out["descriptive_rows"]), "null_rows": len(out["null_rows"]),
          "contract_failures": out["integrity"]["n_contract_failures"], "null_inputs_max_abs_diff": out["null_inputs_consistency_summary"]}
    vjson = tmp / "results_validation.json"; vjson.write_text(json.dumps(out, default=float)); f4["results_bytes"] = vjson.stat().st_size
    muts = {}
    def scratch_record():
        d = tmp / f"rec_{len(muts)}"; shutil.copytree(record_dir, d); return d
    d = scratch_record(); (d / "null__news_en_256__c0.npz").unlink(); expect_refusal(lambda: A.analyze(grid, d, inputs, "validation", validation=True, log=lambda m: None), A.InventoryError, "missing_unit", muts)
    d = scratch_record(); (d / "extra.npz").write_bytes(b"x"); expect_refusal(lambda: A.analyze(grid, d, inputs, "validation", validation=True, log=lambda m: None), A.InventoryError, "extra_file", muts)
    gen_name = next(p.stem for p in record_dir.glob("gen__*.npz"))
    d = scratch_record(); z = np.load(d / f"{gen_name}.npz"); arr = {k: np.array(z[k]) for k in z.files}; arr["tokens"][0, 5] = (arr["tokens"][0, 5] + 1) % V; np.savez_compressed(d / f"{gen_name}.npz", **arr)
    expect_refusal(lambda: A.analyze(grid, d, inputs, "validation", validation=True, log=lambda m: None), A.InventoryError, "tampered_array_digest", muts)
    d = scratch_record(); rec = json.loads((d / f"{gen_name}.json").read_text()); rec["provenance"]["arm"]["delta"] = 9.0; (d / f"{gen_name}.json").write_text(json.dumps(rec)); expect_refusal(lambda: A.analyze(grid, d, inputs, "validation", validation=True, log=lambda m: None), A.InventoryError, "relabelled_provenance", muts)
    def retag(d, name, arrays_new):
        np.savez_compressed(d / f"{name}.npz", **arrays_new); rec = json.loads((d / f"{name}.json").read_text()); rec["npz_sha256"] = sha(d / f"{name}.npz"); (d / f"{name}.json").write_text(json.dumps(rec))
    d = scratch_record(); z = np.load(d / f"{gen_name}.npz"); arr = {k: np.array(z[k]) for k in z.files}; arr["tokens"][0, 5] = V; retag(d, gen_name, arr); expect_refusal(lambda: A.analyze(grid, d, inputs, "validation", validation=True, log=lambda m: None), A.BodyError, "token_outside_vocabulary", muts)
    d = scratch_record(); z = np.load(d / f"{gen_name}.npz"); arr = {k: np.array(z[k]) for k in z.files}; arr["logp"][0, 0] = 0.5; retag(d, gen_name, arr); expect_refusal(lambda: A.analyze(grid, d, inputs, "validation", validation=True, log=lambda m: None), A.BodyError, "positive_logprob", muts)
    # the contract path: a flipped hook flag is counted, not refused
    d = scratch_record(); z = np.load(d / f"{gen_name}.npz"); arr = {k: np.array(z[k]) for k in z.files}; arr["flag"][0, 10] = 1 - arr["flag"][0, 10]; retag(d, gen_name, arr)
    out_m, arr_m = A.analyze(grid, d, inputs, "validation", validation=True, log=lambda m: None)
    arm_key = next(k for k in out_m["quality"] if gen_name.split("__")[2] in k)
    void_ok = (out_m["integrity"]["n_contract_failures"] == 1 and out_m["integrity"]["contract_failures"][0]["unit"] == gen_name and out_m["integrity"]["run_void"] is True
               and all(out_m[w]["pass"] is None and "void" in out_m[w].get("note", "") for w in ("W1", "W2", "W3")) and out_m["descriptive_rows"] == [] and out_m["null_rows"] == []
               and out_m["quality"][arm_key]["n_units_in_tables"] == out_m["quality"][arm_key]["n_units"] - 1 and not bool(arr_m[f"contract_ok|{arm_key}"].all()))
    muts["flipped_hook_flag"] = f"counted and void: {out_m['integrity']['n_contract_failures']} failure(s) of {out_m['integrity']['units']} units; rules suppressed and the unit left out of the quality table: {void_ok}"
    # the void predicate at its boundary (section 9: more than 5% of the generation units)
    bound = grid["integrity"]["max_contract_failure_share"]; pred_ok = (not (bound > bound)) and ((bound + 1e-9) > bound) and (not ((bound - 1e-9) > bound))
    muts["void_predicate_boundary"] = f"share == {bound}: not void; share > {bound}: void: {pred_ok}"
    # an analysis-only grid change is refused
    g2 = json.loads(json.dumps(grid)); g2["W1"]["tolerance_pp"] = 99.0
    expect_refusal(lambda: A.analyze(g2, record_dir, inputs, "validation", validation=True, log=lambda m: None), A.InventoryError, "analysis_only_grid_change", muts)
    # the calibration-moment allowance is enforced (an injected mismatch refused)
    saved = A.T4.cal_moment_ok; A.T4.cal_moment_ok = lambda a, b, rel=None: False
    try:
        expect_refusal(lambda: A.analyze(grid, record_dir, inputs, "validation", validation=True, log=lambda m: None), A.BodyError, "calibration_moment_mismatch", muts)
    finally:
        A.T4.cal_moment_ok = saved
    ok("F4_analyzer", f4["contract_failures"] == 0 and all(v.startswith("refused") for k, v in muts.items() if k not in ("flipped_hook_flag", "void_predicate_boundary")) and void_ok and pred_ok, f4 | {"mutations": muts})
    # F5 the lock schema on a scratch copy of the pinned files
    sroot = tmp / "root"; missing = []
    for rel in R.PINNED:
        src = ROOT / rel; dst = sroot / rel; dst.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            shutil.copy(src, dst)
        else:
            dst.write_text(f"placeholder for {rel} (not yet written at validation time)\n"); missing.append(rel)
    resd = sroot / "research/reviews/R09_study4-protocol"; resd.mkdir(parents=True); (resd / "RESOLUTION.md").write_text("placeholder resolution\n")
    def make_lock():
        return {"study": R.STUDY, "date": "2026-10-16", "approved_by": "Yichen", "before_outcomes": True, "final": False, "grid": "research/study4/grid_v0.1.json", "protocol": "research/STUDY4_PROTOCOL_v0.1.md", "validation": "outputs/study4_v0.1/VALIDATION.json",
                "inputs": "outputs/study4_v0.1/INPUTS.json", "prompts_manifest": "outputs/study4_v0.1/prompts_manifest.json", "model_manifest": "outputs/study4_v0.1/model_manifest_qwen2.5-1.5b.json",
                "hashes": {rel: sha(sroot / rel) for rel in R.PINNED}, "review": {"checkpoint": "R09", "resolution": "research/reviews/R09_study4-protocol/RESOLUTION.md", "sha256": sha(resd / "RESOLUTION.md")},
                "keys": {"K4": grid["keys"]["K4"], "subset_seed": grid["keys"]["subset_seed"], "power_keys_sha256": hashlib.sha256(json.dumps(grid["keys"]["power_keys"]).encode()).hexdigest()},
                "record": {"inventory_sha256": grid["record"]["inventory_sha256"], "lock_sha256": grid["record"]["lock_sha256"]}}
    lp = tmp / "lock.json"; lp.write_text(json.dumps(make_lock())); f5 = {}
    try:
        R.verify_lock(lp, sroot / "research/study4/grid_v0.1.json", root=sroot); f5["well_formed"] = "accepted"
    except Exception as e:
        f5["well_formed"] = f"REFUSED (wrong): {e}"
    variants = {"missing_pinned": lambda L: L["hashes"].pop("research/study4/s4_core.py"), "changed_digest": lambda L: L["hashes"].__setitem__("research/study4/s4_run.py", "0" * 64), "wrong_checkpoint": lambda L: L["review"].__setitem__("checkpoint", "R08"),
                "wrong_keys": lambda L: L["keys"].__setitem__("K4", 99), "wrong_record_digest": lambda L: L["record"].__setitem__("inventory_sha256", "1" * 64), "final_true": lambda L: L.__setitem__("final", True), "before_outcomes_false": lambda L: L.__setitem__("before_outcomes", False),
                "non_iso_date": lambda L: L.__setitem__("date", "16/10/2026"), "extra_pinned": lambda L: L["hashes"].__setitem__("research/study4/extra.py", "2" * 64), "wrong_resolution_digest": lambda L: L["review"].__setitem__("sha256", "3" * 64)}
    for name, mut in variants.items():
        L = make_lock(); mut(L); lp.write_text(json.dumps(L)); expect_refusal(lambda: R.verify_lock(lp, sroot / "research/study4/grid_v0.1.json", root=sroot), (R.ProvenanceError, RC.RecordError, K4.KeyPolicyError, FileNotFoundError), name, f5)
    L = make_lock(); lp.write_text(json.dumps(L)); shutil.copy(sroot / "research/study4/grid_v0.1.json", sroot / "alt_grid.json")
    expect_refusal(lambda: R.verify_lock(lp, sroot / "alt_grid.json", root=sroot), R.ProvenanceError, "alternate_grid_path", f5)
    L = make_lock(); (resd / "PROMPT.md").write_text("a prompt\n"); L["review"]["resolution"] = "research/reviews/R09_study4-protocol/PROMPT.md"; L["review"]["sha256"] = sha(resd / "PROMPT.md"); lp.write_text(json.dumps(L))
    expect_refusal(lambda: R.verify_lock(lp, sroot / "research/study4/grid_v0.1.json", root=sroot), R.ProvenanceError, "prompt_as_resolution", f5)
    L = make_lock(); lp.write_text(json.dumps(L)); dep = sroot / "research/study3/s3_run.py"; dep.write_text(dep.read_text() + "\n# a transitive dependency changed after the lock\n")
    expect_refusal(lambda: R.verify_lock(lp, sroot / "research/study4/grid_v0.1.json", root=sroot), R.ProvenanceError, "transitive_dependency_changed", f5); shutil.copy(ROOT / "research/study3/s3_run.py", dep)
    ok("F5_lock_schema", f5["well_formed"] == "accepted" and all(v.startswith("refused") for k, v in f5.items() if k != "well_formed"), f5 | {"placeholders_for_missing_pinned_files": missing, "n_pinned": len(R.PINNED)})
    # F6 the cost projection from the validation run's own wall-clock (the runner at the production batch size)
    log = (record_dir.parent / "run.log").read_text().splitlines(); done = [(l.split()[0], l.split("done ")[1].split(" ")[0], float(re.search(r"\((\d+\.?\d*)s", l).group(1))) for l in log if "   done " in l]
    ts = [datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ") for t, _, _ in done]; starts = [datetime.datetime.strptime(l.split()[0], "%Y-%m-%dT%H:%M:%SZ") for l in log if "start phase" in l]
    wall = {}
    prev = min(starts) if starts else ts[0]
    for (t, name, s_), tt in zip(done, ts):
        wall[name] = (tt - prev).total_seconds(); prev = tt
    per_arm = {}
    for name, w_ in wall.items():
        key = "null" if name.startswith("null__") else name.split("__")[2]; per_arm.setdefault(key, []).append(w_)
    v = grid["validation"]; na = grid["null_arm"]
    t_null_per_text = float(np.mean(per_arm["null"])) / v["null_n"]; t_gen = {a: float(np.mean(w_)) for a, w_ in per_arm.items() if a != "null"}
    n_gen_units = len(grid["cells"]) * grid["keys"]["K4"]; n_null_units = len(grid["cells"]) * (na["n_texts"] // na["n_per_unit"])
    proj_s = sum(n_gen_units * t_gen[a["name"]] * (grid["prompts"]["n_watermarked"] / v["n_prompts"]) for a in grid["arms"]) + n_null_units * na["n_per_unit"] * t_null_per_text
    results_bytes_proj = f4["results_bytes"] * len(grid["cells"])   # the descriptive and null rows aggregate over keys and scale with the prompt cells
    cost = {"validation_units": len(done), "wall_seconds_per_gen_unit_by_arm": {a: round(np.mean(w_), 1) for a, w_ in per_arm.items() if a != "null"}, "wall_seconds_per_null_text": round(t_null_per_text, 3), "generation_call_seconds_sum": round(sum(s_ for _, _, s_ in done), 1),
            "production_units": {"gen": n_gen_units * len(grid["arms"]), "null": n_null_units}, "projected_hours": round(proj_s / 3600, 2), "projected_results_json_bytes_rough": int(results_bytes_proj), "analyzer_seconds_validation": round(t_an, 1), "model_rss_gb_runner": max(float(json.loads((record_dir / f"{n}.json").read_text())["peak_rss_gb"]) for _, n, _ in done)}
    ok("F6_cost_projection", proj_s / 3600 < 2 * 12.7, cost)
    # F9 the rule rows' branches with planted data (W1 consistent / inconsistent / unresolved; W2 agree / disagree on both sides and the zero-denominator case on shared-prompt tables; W3 consistent / inconsistent / unresolved / ineligible), the pooled law at ties, the sampler
    rg = np.random.default_rng(99261019); f9 = {}; n_tx = grid["prompts"]["n_watermarked"]; w1 = grid["W1"]; w2 = grid["W2"]; w3 = grid["W3"]
    real = rg.binomial(n_tx, 0.20, size=100) / n_tx; f9["W1_consistent"] = A.w1_row("x", real, np.full(100, 0.20), real, w1, 512)["class"]
    f9["W1_inconsistent"] = A.w1_row("x", real, np.full(100, 0.45), real, w1, 512)["class"]
    wide = rg.uniform(0.0, 0.7, size=100); f9["W1_unresolved"] = A.w1_row("x", wide, np.full(100, 0.33), wide, w1, 512)["class"]
    K_, pm_ = 100, np.array([-0.15] * 25 + [0.15] * 25)                                    # a prompt main effect shared by every key (R09 F6)
    def table(sd_key, seed_):
        r_ = np.random.default_rng(seed_); km = np.clip(r_.normal(0.5, sd_key, size=K_), 0.02, 0.98); return r_.binomial(1, np.clip(km[:, None] + pm_[None, :], 0.01, 0.99)).astype(float)
    Yn = table(0.15, 11); f9["W2_raw_agree_below_1"] = A.w2_row("x", "raw", Yn, table(0.04, 12), w2)["class"]; f9["W2_raw_disagree"] = A.w2_row("x", "raw", Yn, table(0.30, 13), w2)["class"]
    f9["W2_distinct_agree_inside_band"] = A.w2_row("x", "distinct", Yn, table(0.15, 14), w2)["class"]; f9["W2_distinct_disagree"] = A.w2_row("x", "distinct", Yn, table(0.30, 15), w2)["class"]
    rz = A.w2_row("x", "raw", np.zeros((K_, 50)), table(0.04, 17), w2)                                  # an estimated denominator of exactly 0: the guard itself
    f9["W2_unresolved_zero_denominator"] = rz["class"]
    zero_guard_ok = rz["sd_between_nominal"] == 0.0 and not np.isfinite(rz["R_pow"]) and rz["finite_resamples"] == 0 and not np.isfinite(rz["ci_lo"])
    f9["W2_zero_denominator_fields"] = f"sd {rz['sd_between_nominal']}, ratio {rz['R_pow']}, finite resamples {rz['finite_resamples']}: guard reached {zero_guard_ok}"
    # the finite-resample rule at its boundary (R09 F19), through the production decision helper and through w2_row itself (a counted wrapper on the component estimator
    # zeroes the nominal table's component on the first k resamples; calls 0 and 1 are the observed tables): 179 finite of 200 -> unresolved with nan ends; 180 and 181 -> classified
    rb_base = np.full(200, 0.5); fs = {}
    for k_nan in (21, 20, 19):
        rb = rb_base.copy(); rb[:k_nan] = np.nan; lo_, hi_, cls_, nf_ = A.w2_decide(0.5, rb, w2, "below_1"); fs[f"helper_{200 - k_nan}_finite"] = (nf_, cls_, bool(np.isfinite(lo_) and np.isfinite(hi_)))
    saved_tw = A.T4.between_key_sd_twoway
    def driven(k_zero):
        calls = {"n": 0}
        def patched(Y):
            out_ = saved_tw(Y); i_ = calls["n"]; calls["n"] += 1
            if i_ >= 2 and (i_ - 2) % 2 == 0 and (i_ - 2) // 2 < k_zero:
                out_ = dict(out_, sd_between=0.0)
            return out_
        A.T4.between_key_sd_twoway = patched
        try:
            r_ = A.w2_row("x", "raw", Yn, table(0.04, 12), w2)
        finally:
            A.T4.between_key_sd_twoway = saved_tw
        return (r_["finite_resamples"], r_["class"], bool(np.isfinite(r_["ci_lo"]) and np.isfinite(r_["ci_hi"])))
    for k_zero in (21, 20, 19):
        fs[f"w2_row_{200 - k_zero}_finite"] = driven(k_zero)
    fin_ok = (fs["helper_179_finite"] == (179, "unresolved", False) and fs["helper_180_finite"] == (180, "agree", True) and fs["helper_181_finite"] == (181, "agree", True)
              and fs["w2_row_179_finite"] == (179, "unresolved", False) and fs["w2_row_180_finite"] == (180, "agree", True) and fs["w2_row_181_finite"] == (181, "agree", True))
    f9["W2_finite_share_boundary"] = f"(finite resamples, class, finite interval) {fs}; 179 of 200 unresolved and 180, 181 classified, in the helper and through w2_row: {fin_ok}"
    # the interval's calibration (R09 F18, F22, F23; D17, D18): the actual w2_row on exact-target paired tables at the planned K = 100 and n = 50, bounded effects (no clipping),
    # shared uniforms so that the method's rejection set is nested in the nominal's; 300 tables per model. Two true ratios per table: the PROMPT-CONDITIONAL ratio R(D) (the
    # floored square-rooted ratio of the two-way estimator's RAW expectations given the table's prompts, the target of protocol section 3 under D18) and the POPULATION ratio
    # (the ratio of the square roots of the population components over the prompt law: the raw components' expectation over prompt samples, not the expectation of R(D); R09
    # F24). Acceptance: in every well-separated model at least 100 finite intervals (else FAILED, never skipped) and the conditional ratio covered in
    # at least 85% of them (a gross-failure bound; the coverages recorded); the two weak-signal models (a small nominal component) record their interval availability, the
    # resolved classes and both coverages as diagnostics. Finite intervals and resolved classifications (agree/disagree against the raw side) are counted separately (F23).
    # The population-ratio coverage is recorded for every model (its under-coverage under a shared additive interaction is D18's stated limitation), as are, on two models,
    # the superseded crossed percentile construction (R09 F18) and two constructions with a prompt channel (keys resampled with a random half of the prompts; a two-way
    # jackknife sum on the log ratio), the alternatives D18 declined
    def cov_tables(rng_, aK=.08, aKc=.5, mu_c=.3, bP=.12, cI=.06, dscale=None, same_mod=True, additive=None):
        """One paired table: (Yn, Yc, the conditional ratio given this table's prompts, the population ratio). Bounded effects; nested rejection sets."""
        if additive is not None:   # the reviewer's model (R09 F22): P_n = 0.5 + l_n S + g S D, P_c = 0.3 + l_c S + g S D: the SAME additive interaction under different key main effects
            l_n, l_c, g_ = additive; s_ = rng_.choice([-1.0, 1.0], (K_, 1)); d_ = rng_.choice([-1.0, 1.0], (1, n_tx)); h_ = g_ * s_ * d_; u_ = rng_.random((K_, n_tx))
            Pn = 0.5 + l_n * s_ + h_; Pc = 0.3 + l_c * s_ + h_; db = float(d_.mean()); sd2 = float(d_.var(ddof=1))
            vn_ = (l_n + g_ * db) ** 2 - g_ ** 2 * sd2 / n_tx; vc_ = (l_c + g_ * db) ** 2 - g_ ** 2 * sd2 / n_tx; cond_ = float(np.sqrt(max(vc_, 0.0) / vn_)); pop_ = l_c / l_n
        else:
            a_ = rng_.choice([-aK, aK], (K_, 1)); b_ = rng_.choice([-bP, bP], (1, n_tx)); c_ = rng_.choice([-cI, cI], (K_, n_tx)); u_ = rng_.random((K_, n_tx))
            if dscale is None:   # exchangeable interaction: the conditional functional equals the population component for every prompt sample
                Pn = 0.5 + a_ + b_ + c_; Pc = mu_c + aKc * a_ + b_ + c_; cond_ = aKc
            else:                # the key effect scaled by the prompt, A(1 + D): the conditional functional a_K^2 ((1 + mean D)^2 - var(D)/n) moves with the prompt sample
                d_ = rng_.choice([-dscale, dscale], (1, n_tx)); d2_ = d_ if same_mod else rng_.choice([-dscale, dscale], (1, n_tx))
                Pn = 0.5 + a_ * (1 + d_) + b_ + c_; Pc = mu_c + aKc * a_ * (1 + d2_) + b_ + c_
                fn_ = (1 + float(d_.mean())) ** 2 - float(d_.var(ddof=1)) / n_tx; fc_ = (1 + float(d2_.mean())) ** 2 - float(d2_.var(ddof=1)) / n_tx; cond_ = aKc * float(np.sqrt(max(fc_, 0.0) / fn_))
            pop_ = aKc
        if Pn.min() < 0.0 or Pn.max() > 1.0 or Pc.min() < 0.0 or (Pc > Pn).any():
            raise RuntimeError("the coverage fixture produced an invalid or non-nested probability table")
        return (u_ < Pn).astype(float), (u_ < Pc).astype(float), cond_, float(pop_)
    def crossed_percentile(name_, Yn_, Yc_, B=200):
        """The superseded construction of round 2 (keys and prompts resampled, paired, uncentred percentiles), kept here only to record its coverage (R09 F18)."""
        bn_, bc_ = T4.between_key_sd_twoway(Yn_), T4.between_key_sd_twoway(Yc_); R_ = bc_["sd_between"] / bn_["sd_between"] if bn_["sd_between"] > 0 else float("nan")
        rng_ = T4.rng_for(f"W2|{name_}"); Rb_ = []
        for _ in range(B):
            ki_ = rng_.integers(0, K_, size=K_); pi_ = rng_.integers(0, n_tx, size=n_tx)
            vn_ = T4.between_key_sd_twoway(Yn_[ki_][:, pi_])["sd_between"]; vc_ = T4.between_key_sd_twoway(Yc_[ki_][:, pi_])["sd_between"]; Rb_.append(vc_ / vn_ if vn_ > 0 else np.nan)
        lo_, hi_, _, _ = A.w2_decide(R_, Rb_, w2, "below_1"); return {"R_pow": R_, "ci_lo": lo_, "ci_hi": hi_}
    def keys_half_prompts(name_, Yn_, Yc_, B=200):
        """An alternative with a prompt channel (declined at D18): keys resampled with replacement and a random half of the prompts without replacement (the delete-d jackknife at d = n/2), paired."""
        bn_, bc_ = T4.between_key_sd_twoway(Yn_), T4.between_key_sd_twoway(Yc_); R_ = bc_["sd_between"] / bn_["sd_between"] if bn_["sd_between"] > 0 else float("nan")
        rng_ = T4.rng_for(f"W2|{name_}"); Rb_ = []
        for _ in range(B):
            ki_ = rng_.integers(0, K_, size=K_); pi_ = np.sort(rng_.permutation(n_tx)[: n_tx // 2])
            vn_ = T4.between_key_sd_twoway(Yn_[ki_][:, pi_])["sd_between"]; vc_ = T4.between_key_sd_twoway(Yc_[ki_][:, pi_])["sd_between"]; Rb_.append(vc_ / vn_ if vn_ > 0 else np.nan)
        lo_, hi_, _, _ = A.w2_decide(R_, Rb_, w2, "below_1"); return {"R_pow": R_, "ci_lo": lo_, "ci_hi": hi_}
    def jackknife_sum(name_, Yn_, Yc_, B=200):
        """An alternative with a prompt channel (declined at D18): a log-normal interval with the variance of the log ratio summed over a key bootstrap (prompts fixed) and a delete-one-prompt jackknife (keys fixed); the cell-noise channel is counted twice (conservative)."""
        bn_, bc_ = T4.between_key_sd_twoway(Yn_), T4.between_key_sd_twoway(Yc_); R_ = bc_["sd_between"] / bn_["sd_between"] if bn_["sd_between"] > 0 else float("nan")
        if not np.isfinite(R_) or R_ <= 0:
            return {"R_pow": R_, "ci_lo": float("nan"), "ci_hi": float("nan")}
        rng_ = T4.rng_for(f"W2|{name_}"); idx_ = T4.boot_indices(K_, rng_, B); lr_ = []
        for ki_ in idx_:
            vn_ = T4.between_key_sd_twoway(Yn_[ki_])["sd_between"]; vc_ = T4.between_key_sd_twoway(Yc_[ki_])["sd_between"]; lr_.append(np.log(vc_ / vn_) if (vn_ > 0 and vc_ > 0) else np.nan)
        lr_ = np.array(lr_); fl_ = np.isfinite(lr_)
        if fl_.mean() < w2["min_finite_resample_share"]:
            return {"R_pow": R_, "ci_lo": float("nan"), "ci_hi": float("nan")}
        lj_ = []
        for j_ in range(n_tx):
            m_ = np.ones(n_tx, dtype=bool); m_[j_] = False; vn_ = T4.between_key_sd_twoway(Yn_[:, m_])["sd_between"]; vc_ = T4.between_key_sd_twoway(Yc_[:, m_])["sd_between"]; lj_.append(np.log(vc_ / vn_) if (vn_ > 0 and vc_ > 0) else np.nan)
        lj_ = np.array(lj_)
        if not np.isfinite(lj_).all():
            return {"R_pow": R_, "ci_lo": float("nan"), "ci_hi": float("nan")}
        se_ = float(np.sqrt(lr_[fl_].var(ddof=1) + (n_tx - 1) / n_tx * ((lj_ - lj_.mean()) ** 2).sum())); return {"R_pow": R_, "ci_lo": R_ * np.exp(-1.96 * se_), "ci_hi": R_ * np.exp(1.96 * se_)}
    cov_models = {"ratio_0.5": ({}, True), "ratio_1.0": ({"aKc": 1.0}, True), "ratio_2/3_boundary": ({"aKc": 2 / 3}, True), "ratio_1.5_weak_nominal_component": ({"aK": .04, "aKc": 1.5}, False),
                  "small_nominal_component_aK_0.03": ({"aK": .03}, False), "proportional_prompt_modulation_of_both_key_effects": ({"dscale": .5}, True), "different_prompt_modulation_of_the_two_key_effects": ({"dscale": .5, "same_mod": False}, True),
                  "shared_additive_interaction_R09_F22": ({"additive": (0.2, 0.1, 0.18)}, True), "shared_additive_interaction_g_0.09": ({"additive": (0.2, 0.1, 0.09)}, True)}
    alternatives = {"superseded_crossed_percentile_R09_F18": crossed_percentile, "keys_x_half_prompts": keys_half_prompts, "jackknife_sum_lognormal": jackknife_sum}
    cov = {}; cov_ok = True; cov_fail = []
    for name_, (kw_, well_) in cov_models.items():
        rc_ = np.random.default_rng(99261021); tabs_ = [cov_tables(rc_, **kw_) for _ in range(300)]
        rows_ = [A.w2_row(f"F9cov|{name_}|{i}", "raw", yn_, yc_, w2) for i, (yn_, yc_, _, _) in enumerate(tabs_)]
        fin_ = [(r_, t_[2], t_[3]) for r_, t_ in zip(rows_, tabs_) if np.isfinite(r_["ci_lo"])]; n_fin = len(fin_)
        cc_ = int(sum(r_["ci_lo"] <= cr_ <= r_["ci_hi"] for r_, cr_, _ in fin_)); cp_ = int(sum(r_["ci_lo"] <= pr_ <= r_["ci_hi"] for r_, _, pr_ in fin_))
        cov[name_] = {"well_separated": well_, "population_ratio": round(tabs_[0][3], 4), "conditional_ratio_range": [round(min(t_[2] for t_ in tabs_), 4), round(max(t_[2] for t_ in tabs_), 4)], "finite_intervals": n_fin,
                      "classes": {c_: int(sum(r_["class"] == c_ for r_ in rows_)) for c_ in ("agree", "disagree", "unresolved")},
                      "covered_conditional": cc_, "coverage_conditional": (round(cc_ / n_fin, 3) if n_fin else None), "covered_population": cp_, "coverage_population": (round(cp_ / n_fin, 3) if n_fin else None),
                      "median_width": (round(float(np.median([r_["ci_hi"] - r_["ci_lo"] for r_, _, _ in fin_])), 3) if n_fin else None), "median_R_pow": round(float(np.median([r_["R_pow"] for r_ in rows_ if np.isfinite(r_["R_pow"])])), 4)}
        if well_:
            okm_ = n_fin >= 100 and (cc_ / n_fin if n_fin else 0.0) >= 0.85; cov_ok = cov_ok and okm_
            if not okm_:
                cov_fail.append(name_)
        if name_ in ("ratio_0.5", "shared_additive_interaction_R09_F22"):
            alt_ = {}
            for an_, fn_ in alternatives.items():
                ra_ = [fn_(f"F9alt|{an_}|{name_}|{i}", yn_, yc_) for i, (yn_, yc_, _, _) in enumerate(tabs_)]; fa_ = [(r_, t_[2], t_[3]) for r_, t_ in zip(ra_, tabs_) if np.isfinite(r_["ci_lo"])]
                alt_[an_] = {"finite_intervals": len(fa_), "coverage_population": (round(sum(r_["ci_lo"] <= pr_ <= r_["ci_hi"] for r_, _, pr_ in fa_) / len(fa_), 3) if fa_ else None), "coverage_conditional": (round(sum(r_["ci_lo"] <= cr_ <= r_["ci_hi"] for r_, cr_, _ in fa_) / len(fa_), 3) if fa_ else None),
                             "median_width": (round(float(np.median([r_["ci_hi"] - r_["ci_lo"] for r_, _, _ in fa_])), 3) if fa_ else None)}
            cov[name_]["alternatives"] = alt_
    def cov_line(k_, v_):
        s_ = (f"{k_} ({'well-separated' if v_['well_separated'] else 'weak signal, diagnostic'}): population ratio {v_['population_ratio']}, conditional ratio {v_['conditional_ratio_range'][0]}–{v_['conditional_ratio_range'][1]}; finite intervals {v_['finite_intervals']} of 300 (classes agree {v_['classes']['agree']}, disagree {v_['classes']['disagree']}, unresolved {v_['classes']['unresolved']}); "
              f"coverage of the conditional ratio {v_['coverage_conditional']} ({v_['covered_conditional']}), of the population ratio {v_['coverage_population']} ({v_['covered_population']}); median width {v_['median_width']}")
        if "alternatives" in v_:
            s_ += "; alternatives on the same tables: " + ", ".join(f"{an_}: finite {d_['finite_intervals']}, coverage population {d_['coverage_population']}, conditional {d_['coverage_conditional']}, median width {d_['median_width']}" for an_, d_ in v_["alternatives"].items())
        return s_
    f9["W2_interval_coverage"] = "; ".join(cov_line(k_, v_) for k_, v_ in cov.items()) + f"; acceptance (at least 100 finite intervals and conditional coverage at least 0.85 in every well-separated model): {cov_ok}" + (f" (failed: {cov_fail})" if cov_fail else "")
    # the target of D16 under the two-way random model WITH a key-by-prompt interaction, with BOUNDED effects so that the planted components are exact and no probability is
    # clipped (R09 F20): keys A = +-0.08 (v_K = 0.0064), prompts B = +-0.12 (v_b = 0.0144), interaction C = +-0.06 (0.0036), P = 0.5 + A + B + C in [0.24, 0.76], Bernoulli noise.
    # Over 400 tables the two-way estimator's mean must recover v_K within 3 SE + 1e-4, and the independent-binomial proxy's mean must sit at its derived expectation
    # v_K - v_b/n (it subtracts the prompt main effects' spread as if it were noise: R09 F6, F13) and more than 2 SE from v_K
    tw = []; bp = []; rr = np.random.default_rng(99261020); v_K, v_b = 0.08 ** 2, 0.12 ** 2
    for i in range(400):
        a = rr.choice([-0.08, 0.08], size=(K_, 1)); b = rr.choice([-0.12, 0.12], size=(1, n_tx)); c = rr.choice([-0.06, 0.06], size=(K_, n_tx)); Pm = 0.5 + a + b + c
        if Pm.min() < 0.0 or Pm.max() > 1.0:
            raise RuntimeError("the bounded-effects fixture produced a probability outside [0, 1]")
        Yr = rr.binomial(1, Pm).astype(float)
        tw.append(T4.between_key_sd_twoway(Yr)["var_between_raw"]); bp.append(T4.between_key_sd(Yr.mean(axis=1), n_tx)["var_between_raw"])
    se_tw = float(np.std(tw, ddof=1) / np.sqrt(400)); se_bp = float(np.std(bp, ddof=1) / np.sqrt(400)); exp_bp = v_K - v_b / n_tx
    f9["W2_random_effects_with_interaction"] = f"planted key component {v_K:.4f} (bounded effects +-0.08 / +-0.12 / +-0.06: exact components, no clipping); two-way {np.mean(tw):.5f} (SE of the mean {se_tw:.5f}); binomial proxy {np.mean(bp):.5f} against its derived expectation v_K - v_b/n = {exp_bp:.5f} (SE {se_bp:.5f})"
    cex_ok = abs(np.mean(tw) - v_K) < 3 * se_tw + 1e-4 and abs(np.mean(bp) - exp_bp) < 3 * se_bp + 1e-4 and abs(np.mean(bp) - v_K) > 2 * se_bp
    # the fixed-table interaction case of R09 F13 (zero generation noise): the key-mean variance of that fixed table is NOT the target; the estimator's documented output
    Yf = np.zeros((K_, n_tx)); Yf[:50, :24] = 1; Yf[50:, 24:] = 1; rf = T4.between_key_sd_twoway(Yf)
    f9["W2_fixed_table_interaction_not_the_target"] = f"fixed-table key-mean variance {Yf.mean(axis=1).var(ddof=1):.6f}; two-way raw {rf['var_between_raw']:.6f}, floored SD {rf['sd_between']}; MS_E {rf['ms_resid']:.4f}"
    fixed_ok = abs(rf["var_between_raw"] - (-0.004741290455576168)) < 1e-9 and rf["sd_between"] == 0.0
    lv = rg.normal(0.010, 0.0020, size=1000).clip(0, 1)
    f9["W3_consistent"] = A.w3_fields(lv, {"sd_cond": 0.0020, "theory_share": 0.9}, [], w3, "F9|c")["w3_class"]; f9["W3_inconsistent"] = A.w3_fields(lv, {"sd_cond": 0.0020 / 3, "theory_share": 0.9}, [], w3, "F9|i")["w3_class"]
    f9["W3_unresolved"] = A.w3_fields(lv, {"sd_cond": float(lv.std(ddof=1)) / 1.5, "theory_share": 0.9}, [], w3, "F9|u")["w3_class"]   # the ratio exactly at the band's upper edge: its interval straddles it
    f9["W3_ineligible_theory_share"] = A.w3_fields(lv, {"sd_cond": 0.0020, "theory_share": 0.5}, [], w3, "F9|e")["w3_class"]
    f9["W3_ineligible_flag"] = A.w3_fields(lv, {"sd_cond": 0.0020, "theory_share": 0.9}, ["v_below_algebraic_floor"], w3, "F9|f")["w3_class"]
    # the pooled law at ties (R09 F1): the strict rule; the abstaining key; a lattice of KGW p-values
    law3 = T4.PooledLaw(np.array([0.01, 0.01, 0.001])); pw = law3.power_at(np.array([0.01, 0.001, 0.0]))
    Mlat = 255; Glat = np.arange(40, 120); plat = __import__("scipy.stats", fromlist=["norm"]).norm.sf((Glat - 0.25 * Mlat) / np.sqrt(Mlat * 0.1875)); lawl = T4.PooledLaw(plat)
    lat_ok = all(abs(lawl.power_at(np.array([t]))[0] - np.mean(plat < t)) < 1e-15 for t in plat[:: 7])
    f9["PooledLaw_ties"] = f"tied threshold {pw[0]:.4f} (1/3 expected); below every value {pw[1]}; abstention {pw[2]}; lattice strict counts equal: {lat_ok}"
    ties_ok = pw[0] == 1 / 3 and pw[1] == 0.0 and pw[2] == 0.0 and lat_ok
    # the sampler (R09 F9, F15, F19): deterministic uniforms in [0, 1) against an independently computed exact CDF (a Neumaier compensated sum), including uniforms in the region a float32 accumulation erases; zero-mass plateaus; a draw of exactly 0
    import s4_gen as G, math
    Vt = grid["model"]["V"]; pt = np.full((1, Vt), 1e-9, dtype=np.float32); pt[0, 0] = 1 - 1e-9 * (Vt - 1); pt = pt / pt.sum(axis=1, keepdims=True)
    def neumaier_cumsum(x):
        """A compensated (Neumaier) running sum: an independent, more accurate cumulative sum than np.cumsum's plain float64 accumulation."""
        out = np.empty(len(x)); s_ = 0.0; c_ = 0.0
        for i, v in enumerate(x.tolist()):
            t = s_ + v
            c_ += (s_ - t) + v if abs(s_) >= abs(v) else (v - t) + s_
            s_ = t; out[i] = s_ + c_
        return out
    exact = neumaier_cumsum(pt[0].astype(np.float64)); total = exact[-1]                                 # an exact cumulative sum, independent of the sampler's
    c32 = float(np.cumsum(pt[0])[-1])                                                                     # a float32 accumulation stops here
    probes = np.array([0.0, 0.5, c32 + 1e-7, 0.99990, 0.99999, 1 - 1e-12])                                 # the last three lie beyond the float32 terminal: erased by a float32 accumulation; every probe a valid uniform in [0, 1) (R09 F19)
    probes_in_domain = bool(((probes >= 0.0) & (probes < 1.0)).all())
    class U:
        def __init__(self, u): self.u = u
        def random(self, n): return np.full(n, self.u)
    total_sampler = float(np.cumsum(pt[0].astype(np.float64))[-1])                                       # the sampler scales its uniform by its own row total
    got = np.array([int(G._sample_rows(pt, U(u))[0]) for u in probes]); want = np.minimum(np.array([int(np.searchsorted(exact, u * total_sampler, side="right")) for u in probes]), Vt - 1)
    tail_region_ok = bool((got[2:] > 0).all())                                                            # a float32 regression would return 0 (or the clipped last index) for these
    # two float32 mutants of the sampler, recorded as evidence of the probes' power (R09 F19): (A) a float32 accumulation with the terminal-mass scaling; (B) the unscaled float32 argmax form
    c32v = np.cumsum(pt[0]); mutA = np.minimum(np.array([int(np.searchsorted(c32v, np.float32(u) * c32v[-1], side="right")) for u in probes]), Vt - 1); mutB = np.array([int((c32v > u).argmax()) for u in probes])
    mutants_caught = bool((mutA[2:5] != want[2:5]).all() and (mutB[2:5] != want[2:5]).all())
    q = np.zeros((1, 6)); q[0, 3] = 0.5; q[0, 5] = 0.5; rs = np.random.default_rng(0); plateau = np.bincount([G._sample_rows(q, rs)[0] for _ in range(2000)], minlength=6)
    samp_ok = bool(np.array_equal(got, want)) and tail_region_ok and probes_in_domain and mutants_caught and plateau[[0, 1, 2, 4]].sum() == 0 and G._sample_rows(q, U(0.0))[0] == 3
    f9["sampler"] = f"deterministic uniforms in [0, 1) ({probes_in_domain}) {got.tolist()} against the exact (Neumaier) CDF {want.tolist()} (equal: {bool(np.array_equal(got, want))}; the three tail probes beyond the float32 terminal {c32:.9f} select positive indices: {tail_region_ok}; the float32 mutants return {mutA.tolist()} and {mutB.tolist()}, caught on the three tail probes: {mutants_caught}); plateau counts {plateau.tolist()}; a zero draw lands on index 3: {int(G._sample_rows(q, U(0.0))[0])}"
    want = {"W1_consistent": "consistent", "W1_inconsistent": "inconsistent", "W1_unresolved": "unresolved", "W2_raw_agree_below_1": "agree", "W2_raw_disagree": "disagree", "W2_distinct_agree_inside_band": "agree", "W2_distinct_disagree": "disagree",
            "W2_unresolved_zero_denominator": "unresolved", "W3_consistent": "consistent", "W3_inconsistent": "inconsistent", "W3_unresolved": "unresolved", "W3_ineligible_theory_share": "ineligible", "W3_ineligible_flag": "ineligible"}
    ok("F9_rule_row_branches", all(f9[k] == v for k, v in want.items()) and cex_ok and fixed_ok and ties_ok and samp_ok and zero_guard_ok and fin_ok and cov_ok, {k: f"{f9[k]} (expected {v})" for k, v in want.items()} | {k: f9[k] for k in ("W2_random_effects_with_interaction", "W2_fixed_table_interaction_not_the_target", "W2_zero_denominator_fields", "W2_finite_share_boundary", "W2_interval_coverage", "PooledLaw_ties", "sampler")})
    # F10 the budget stop's accounting on a resumed run (model-free; R09 F17, F21): reused units earn no projected-time credit (their verification runs under the invocation's clock)
    units_all = R.expected_units(grid, False); cost_proj = cost                                             # the projection computed above in this run, never a previous file's (R09 F21)
    reused = units_all[:620]; new_units = units_all[620:630]                                               # the reviewer's example: two cells complete, then ten new null units
    ph_new = R.projected_hours(grid, cost_proj, new_units); ph_all = R.projected_hours(grid, cost_proj, reused + new_units)
    f10 = {"projected_hours_new_units_only": round(ph_new, 4), "projected_hours_if_reused_were_credited": round(ph_all, 4), "three_hours_on_the_new_units_stops": R.budget_exceeded(3.0, ph_new, grid["stop"]["max_hours_factor_over_projection"]),
           "three_hours_would_pass_if_reused_were_credited": not R.budget_exceeded(3.0, ph_all, grid["stop"]["max_hours_factor_over_projection"]), "twice_the_projection_does_not_stop": not R.budget_exceeded(2.0 * ph_new, ph_new, grid["stop"]["max_hours_factor_over_projection"]),
           "just_above_twice_stops": R.budget_exceeded(2.0 * ph_new + 1e-9, ph_new, grid["stop"]["max_hours_factor_over_projection"])}
    ok("F10_budget_stop_resume_accounting", f10["three_hours_on_the_new_units_stops"] and ph_new < 1.0 and f10["twice_the_projection_does_not_stop"] and f10["just_above_twice_stops"], f10)
    res["fixture_tolerances"] = {"F3_core": "as printed by s4_core's self-tests", "F6_projection_bound": "2 x 12.7 h", "F9_W2_random_effects": "over 400 tables of bounded effects (exact components): |two-way mean - v_K| < 3 SE + 1e-4; |proxy mean - (v_K - v_b/n)| < 3 SE + 1e-4 and the proxy more than 2 SE from v_K; the fixed-table case to 1e-9",
                                 "F9_W2_finite_share": "179 finite of 200 unresolved with nan ends; 180 and 181 classified; through w2_decide and through w2_row", "F9_W2_interval_coverage": "in every well-separated exact-target model (300 tables, K = 100, n = 50) at least 100 finite intervals, else failed, and the key-bootstrap 95% interval covers the prompt-conditional ratio in at least 85% of them (a gross-failure bound; the coverages of the conditional and of the population ratio, the classes, the widths, the weak-signal models and the alternative constructions recorded, never accepted or refused)", "F9_PooledLaw_lattice": "1e-15", "F9_sampler": "exact equality with an independent compensated (Neumaier) cumulative sum on six deterministic uniforms in [0, 1), three beyond the float32 terminal; two float32 mutants (a float32 accumulation with the terminal-mass scaling; the unscaled float32 argmax form) must differ from the exact indices on the three tail probes",
                                 "F9_W3_unresolved": "the planted ratio exactly 1.5 (the sample's own SD / 1.5)", "F7_tolerance_rule": "1e-9 on max(5 pp, 2 x SE)"}
    res["cost"] = cost; res["inputs_sha256"] = inputs["_sha256"]; res["prompts_manifest_sha256"] = sha(OUT / "prompts_manifest.json"); res["model_manifest_sha256"] = sha(OUT / grid["model"]["weights_manifest"].split("/")[-1]) if (OUT / grid["model"]["weights_manifest"].split("/")[-1]).exists() else None
    res["analysis_validation_summary"] = {"W1": {k: out["W1"][k] for k in ("n_rows", "n_consistent", "n_inconsistent", "pass")}, "W2": {k: out["W2"][k] for k in ("n_rows", "n_agree", "n_disagree", "pass")}, "W3": {k: out["W3"][k] for k in ("n_candidate", "n_eligible", "n_resolved", "n_consistent", "pass")},
                                         "note": "validation keys with the record's thresholds standing in; every code path exercised; no scientific meaning"}
    shutil.rmtree(tmp)
    (OUT / "VALIDATION.json").write_text(json.dumps(res, indent=1, default=float)); print("all_ok", res["all_ok"], "projected hours", cost["projected_hours"], flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[a.index("--grid") + 1] if "--grid" in a else "research/study4/grid_v0.1.json", a[a.index("--record") + 1] if "--record" in a else str(OUT / "validation_runner_test/cells"))
