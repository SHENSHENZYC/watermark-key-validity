"""Study 4 analyzer (v1). Study mode (--lock): the lock re-verified; the inventory gate (every expected unit present with the expected
provenance and its array digest, no extra file, no FIXTURE marker); the body contracts (array shapes, dtypes, ranges; for every generation
unit the hook-flag contract: the LOCKED detector's green indicator at every scored position of the committed tokens equals the stored
flag); the scoring of every text with the locked detector code at both rules and every length; the power at every committed threshold of
the text's key (every method, N_cal, alpha and same-tokenizer calibration source); the model-null block for all 1,000 evaluation keys;
the pre-registered rules W1-W3; the descriptive blocks. Writes results.json (aggregates and rows) and results_arrays.npz (per-key counts).
Validation mode (--validation DIR): the same on a validation record (validation keys and pilot prompts) with the record's thresholds of
evaluation key (23,000 + i) standing in for validation key (keys_start + i): every code path exercised, no scientific meaning, labelled.
Usage: .venv/bin/python -u research/study4/s4_analyze.py --grid research/study4/grid_v0.1.json --lock outputs/study4_v0.1/PRE_RUN_LOCK.json
       .venv/bin/python -u research/study4/s4_analyze.py --grid ... --validation outputs/study4_v0.1/validation_<utc>/cells [--out FILE]
"""
import datetime, hashlib, json, pathlib, resource, sys, time
import numpy as np
from scipy.stats import norm
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study3")); sys.path.insert(0, str(ROOT / "research/study2"))
import s4_core as T4, s4_run as R, s4_record as RC, s4_gen as G
import s3_data as SD3, s3_run as R3, s2_core as S

OUT = ROOT / "outputs/study4_v0.1"
VARIANTS_FIXED = ["nominal", "multiplier20"]


class InventoryError(RuntimeError):
    pass


class BodyError(RuntimeError):
    pass


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def utc():
    return f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}"


def variants_all(grid):
    return VARIANTS_FIXED + R3.variant_names(grid["N_cal"])


def variant_parts(v):
    if "@" in v:
        m, n = v.split("@"); return m, int(n)
    return v, None


# ---------------- inventory ----------------
def load_inventory(cells_dir, grid, mode, lock_path=None, validation=False):
    cells_dir = pathlib.Path(cells_dir); grid_path = ROOT / "research/study4/grid_v0.1.json"; grid_sha = sha(grid_path)
    if mode == "study":
        lock, grid_v, Rrec = R.verify_lock(lock_path, grid_path); lock_sha = sha(lock_path); pm_path = ROOT / grid["prompts"]["manifest"]; prompts_kind = "prod"
    else:
        lock_sha = None; Rrec = RC.Record(verify_files=True); grid_v = json.loads(grid_path.read_text()); pm_path = ROOT / grid["prompts"]["pilot_manifest"]; prompts_kind = "pilot"
    if json.dumps(grid, sort_keys=True) != json.dumps(grid_v, sort_keys=True):
        raise InventoryError("the analysis grid differs from the canonical grid file (an analysis-only change is refused)")
    pm = json.loads(pm_path.read_text()); pm_sha = sha(pm_path); model_man = json.loads((ROOT / grid["model"]["weights_manifest"]).read_text())
    code = {f: sha(HERE / f) for f in ("s4_gen.py", "s4_wm.py", "s4_run.py", "s4_data.py", "s4_keys.py", "s4_record.py")}
    units = R.expected_units(grid, validation); expected = set(); recs = {}
    for u in units:
        name = R.unit_name(u); expected |= {f"{name}.json", f"{name}.npz"}
        jp, npz = cells_dir / f"{name}.json", cells_dir / f"{name}.npz"
        if not jp.exists() or not npz.exists():
            raise InventoryError(f"{name}: record or array missing")
        rec = json.loads(jp.read_text())
        if mode == "study" and "FIXTURE" in rec:
            raise InventoryError(f"{name}: a FIXTURE record in study mode")
        prov = R.provenance(mode, lock_sha, grid, grid_sha, pm_sha, pm["cells"][u["cell"]]["kinds"][prompts_kind]["sha256"], model_man, code, u, prompts_kind)
        if not R.prov_equal(rec.get("provenance", {}), prov):
            raise InventoryError(f"{name}: provenance differs from the expected")
        if sha(npz) != rec.get("npz_sha256"):
            raise InventoryError(f"{name}: array digest differs from the record")
        recs[name] = rec
    present = {p.name for p in cells_dir.iterdir() if p.is_file()}
    if present - expected:
        raise InventoryError(f"extra files in the record: {sorted(present - expected)[:5]}")
    inv_digest = hashlib.sha256("".join(f"{n}:{sha(cells_dir / n)}\n" for n in sorted(expected)).encode()).hexdigest()
    return units, recs, Rrec, pm, {"n_files": len(expected), "inventory_sha256": inv_digest, "lock_sha256": lock_sha, "grid_sha256": grid_sha, "prompts_manifest_sha256": pm_sha, "mode": mode}


# ---------------- body contracts ----------------
def validate_body(u, rec, arr, grid, V):
    name = R.unit_name(u); n_new = grid["generation"]["n_new"]; n = u["n"]
    need = {"tokens": (np.int32, (n, n_new)), "logp": (np.float32, (n, n_new)), "eos_mass": (np.float16, (n, n_new))}
    if u["kind"] == "gen":
        need["flag"] = (np.uint8, (n, n_new))
    if set(arr) != set(need):
        raise BodyError(f"{name}: arrays {sorted(arr)} differ from the contract {sorted(need)}")
    for k, (dt, shape) in need.items():
        if arr[k].dtype != dt or arr[k].shape != shape:
            raise BodyError(f"{name}: array {k} has dtype {arr[k].dtype} and shape {arr[k].shape}")
    t = arr["tokens"]
    if t.min() < 0 or t.max() >= V:
        raise BodyError(f"{name}: token ids outside [0, V)")
    if not np.isfinite(arr["logp"]).all() or (arr["logp"] > 1e-6).any():
        raise BodyError(f"{name}: log-probabilities not finite or positive")
    e = arr["eos_mass"].astype(np.float32)
    if not np.isfinite(e).all() or e.min() < 0 or e.max() > 1:
        raise BodyError(f"{name}: EOS mass outside [0, 1]")
    if u["kind"] == "gen" and not np.isin(arr["flag"], (0, 1)).all():
        raise BodyError(f"{name}: flags outside {{0, 1}}")
    if rec.get("n") != n or rec.get("n_new") != n_new:
        raise BodyError(f"{name}: the record's sizes differ from the unit's")


def hook_flag_contract(chain, key, flag, gamma, V):
    """The locked detector's green indicator equals the stored hook flag at every scored position (t >= h)."""
    det, valid = T4.detector_green_flags(chain, key, gamma, V)
    eq = det[valid] == flag[valid].astype(bool)
    return bool(eq.all()), int((~eq).sum()), int(valid.sum())


# ---------------- the analysis ----------------
def key_index(key, grid, validation):
    """The record's array index of a key: evaluation key 23,000 + i -> i; in validation mode the stand-in index (key - keys_start) mod 1,000."""
    if validation:
        return (int(key) - grid["validation"]["keys_start"]) % 1000
    return int(key) - 23000


# ---------------- the rule rows (one function each, so that the validator can drive every branch with planted data) ----------------
def w1_row(cell, real, pred, nominal_power, w, law_n):
    """W1 for one cell: the key-median of the realised costs with its key-bootstrap interval against the predicted key-median +- tolerance."""
    real = np.asarray(real, dtype=np.float64); pred = np.asarray(pred, dtype=np.float64); tol = w["tolerance_pp"] / 100
    rng = T4.rng_for(f"W1|{cell}"); idx = T4.boot_indices(len(real), rng); med_b = np.median(real[idx], axis=1); lo, hi = T4.quantiles(med_b)
    pm_ = float(np.median(pred)); cls = T4.w1_classify(lo, hi, pm_, tol)
    return {"cell": cell, "K": int(len(real)), "realised_median": float(np.median(real)), "realised_mean": float(real.mean()), "ci_lo": lo, "ci_hi": hi, "predicted_median": pm_, "predicted_mean": float(pred.mean()),
            "tolerance": tol, "class": cls, "share_keys_within_tol": float(np.mean(np.abs(real - pred) <= tol)), "corr_real_pred": float(np.corrcoef(real, pred)[0, 1]) if real.std() > 0 and pred.std() > 0 else None,
            "nominal_power_median": float(np.median(nominal_power)), "pilot_law_n": int(law_n)}


def w2_decide(R_obs, Rb, w2, side):
    """The W2 decision of one row from the observed ratio and the B resampled ratios (section 9 rule 4): unresolved when the observed
    denominator is 0 (R_obs not finite) or fewer than min_finite_resample_share of the resamples are finite; otherwise the 2.5% and
    97.5% quantiles of the finite resamples and the side classification. Returns (lo, hi, class, the number of finite resamples). One
    function, so that the validator drives the boundary (179, 180, 181 finite of 200) through the production decision (R09 F19)."""
    Rb = np.asarray(Rb, dtype=np.float64); fin = np.isfinite(Rb)
    if fin.mean() < w2["min_finite_resample_share"] or not np.isfinite(R_obs):
        return float("nan"), float("nan"), "unresolved", int(fin.sum())
    lo, hi = T4.quantiles(Rb[fin])
    return lo, hi, T4.classify_side(lo, hi, side, tuple(w2["band"])), int(fin.sum())


def w2_row(cell, rule, Yn, Yc, w2):
    """W2 for one (cell, rule): Yn, Yc are K x n binary rejection tables (keys x the shared prompts) at the nominal and the method's
    thresholds. The target (D16, D18) is the PROMPT-CONDITIONED functional: the expectation, over the keys and the generations, of Study 1's
    two-way estimator given the realised prompts (the across-key variance of the key's mean rejection probability over these prompts less
    1/n of their key-by-prompt interaction variance); its expectation over prompt samples is the population key component of the crossed
    decomposition (D16), for which the point estimate is unbiased (s4_core.between_key_sd_twoway: s_K^2 - MS_E/n). The ratio's interval
    (D17; R09 F18) is a KEY bootstrap: the keys resampled with replacement (the B x K index array drawn once, s4_core.boot_indices), the
    same resampled keys for both tables (paired), the prompts fixed, the component re-estimated on every resample: the sampling the
    conditional target calls for; the key resample's mean of the raw component is exactly (K-1)/K times the estimate, a factor that cancels
    in the ratio. It does NOT cover the population ratio when a key-by-prompt interaction is modulated by the prompt sample (R09 F22; D18:
    the population reading is an extrapolation, reported without a confidence statement). A crossed key-and-prompt resample is not used:
    its resamples centre at (K-1)/K s_K^2 rather than at the corrected component (R09 F18; the validator's coverage fixture records both
    constructions and the alternatives with a prompt channel). The observed dispersion of the per-key powers over the n prompts and the
    independent-binomial proxy are recorded beside it."""
    Yn = np.asarray(Yn, dtype=np.float64); Yc = np.asarray(Yc, dtype=np.float64); K, n_tx = Yn.shape
    bn, bc = T4.between_key_sd_twoway(Yn), T4.between_key_sd_twoway(Yc); pn, pc = Yn.mean(axis=1), Yc.mean(axis=1)
    bn_bin, bc_bin = T4.between_key_sd(pn, n_tx), T4.between_key_sd(pc, n_tx)
    R_obs = bc["sd_between"] / bn["sd_between"] if bn["sd_between"] > 0 else float("nan")
    rng = T4.rng_for(f"W2|{cell}|{rule}"); idx = T4.boot_indices(K, rng); Rb = []
    for ki in idx:                                                                                     # the key resample, shared by both tables (paired); the prompts fixed (section 8)
        vn = T4.between_key_sd_twoway(Yn[ki])["sd_between"]; vc = T4.between_key_sd_twoway(Yc[ki])["sd_between"]; Rb.append(vc / vn if vn > 0 else np.nan)
    side = w2["predicted_side"][rule]; lo, hi, cls, n_fin = w2_decide(R_obs, Rb, w2, side)
    return {"cell": cell, "rule": rule, "K": int(K), "n": int(n_tx), "sd_between_nominal": bn["sd_between"], "sd_between_method": bc["sd_between"], "var_between_raw_nominal": bn["var_between_raw"], "var_between_raw_method": bc["var_between_raw"],
            "var_obs_nominal": bn["var_obs"], "var_obs_method": bc["var_obs"], "sd_observed_nominal": float(np.sqrt(bn["var_obs"])), "sd_observed_method": float(np.sqrt(bc["var_obs"])), "ms_resid_nominal": bn["ms_resid"], "ms_resid_method": bc["ms_resid"], "var_prompt_raw_nominal": bn["var_prompt_raw"], "var_prompt_raw_method": bc["var_prompt_raw"],
            "binomial_proxy": {"sd_between_nominal": bn_bin["sd_between"], "sd_between_method": bc_bin["sd_between"], "var_between_raw_nominal": bn_bin["var_between_raw"], "var_between_raw_method": bc_bin["var_between_raw"], "mean_binomial_var_nominal": bn_bin["mean_binomial_var"], "mean_binomial_var_method": bc_bin["mean_binomial_var"]},
            "R_pow": R_obs, "ci_lo": lo, "ci_hi": hi, "finite_resamples": n_fin, "bootstrap": "keys resampled with replacement (the B x K indices drawn once), the same keys for both tables (paired), the prompts fixed; the two-way component re-estimated per resample (D17)", "target": "prompt-conditioned (D18): the two-way estimator's expectation given the realised prompts; the population component is its expectation over prompt samples (an extrapolation, no confidence statement)", "predicted_side": side, "class": cls, "power_mean_nominal": float(pn.mean()), "power_mean_method": float(pc.mean())}


def w3_fields(lv, pr, flags, w3, row_name):
    """W3 for one row: the observed SD of the levels against the predictor's conditional SD, the key-bootstrap interval of the ratio, eligibility and class."""
    lv = np.asarray(lv, dtype=np.float64)
    eligible = (pr.get("theory_share") is not None and pr["theory_share"] >= w3["theory_share_min"] and not flags and pr["sd_cond"] > 0)
    rng = T4.rng_for(row_name); idx = T4.boot_indices(len(lv), rng); sd_b = lv[idx].std(axis=1, ddof=1)
    ratio = float(lv.std(ddof=1) / pr["sd_cond"]) if pr["sd_cond"] > 0 else float("nan")
    lo, hi = (float(np.quantile(sd_b, 0.025) / pr["sd_cond"]), float(np.quantile(sd_b, 0.975) / pr["sd_cond"])) if pr["sd_cond"] > 0 else (float("nan"),) * 2
    cls = T4.classify_band(lo, hi, tuple(w3["band"])) if eligible else "ineligible"
    return {"w3_ratio": ratio, "w3_ci_lo": lo, "w3_ci_hi": hi, "w3_class": cls, "w3_eligible": bool(eligible)}


def analyze(grid, cells_dir, inputs, mode, lock_path=None, validation=False, log=print):
    t_all = time.time(); units, recs, Rrec, pm, inv = load_inventory(cells_dir, grid, mode, lock_path, validation); cells_dir = pathlib.Path(cells_dir)
    V = grid["model"]["V"]; gamma = grid["gamma"]; rules = grid["rules"]; lengths = grid["lengths"]; alphas = [float(a) for a in grid["alpha"]]; N_cals = grid["N_cal"]
    vs = variants_all(grid); nv = len(vs); tok = grid["model"]["tokenizer"]; sources = list(Rrec.grid["cells"]); cells = sorted({u["cell"] for u in units})
    out = {"study": grid["study"], "mode": mode, "written_utc": utc(), "inventory": inv, "record": {"inventory_sha256": Rrec.man["inventory"]["inventory_sha256"], "lock_sha256": Rrec.lock_sha},
           "inputs_sha256": inputs.get("_sha256"), "integrity": {"units": len(units), "contract_failures": [], "n_contract_failures": 0}, "quality": {}, "W1": {}, "W2": {}, "W3": {}, "descriptive_rows": [], "null_rows": [], "null_inputs_consistency": []}
    arrays = {}
    # ---- the generation units: scores and powers ----
    cal = {}   # (source, h) -> CalUnit
    def cal_unit(src, h):
        if (src, h) not in cal:
            cal[(src, h)] = Rrec.cal(tok, src, h)
        return cal[(src, h)]
    power_counts = {}   # (cell, arm) -> uint8 array [key, rule, L, source, variant, alpha]
    pvals = {}          # (cell, arm) -> float32 [key, text, rule, L]
    key_lists = {}
    for cell in cells:
        for arm in grid["arms"]:
            gens = [u for u in units if u["kind"] == "gen" and u["cell"] == cell and u["arm"] == arm["name"]]
            if not gens:
                continue
            keys = [u["key"] for u in gens]; key_lists[(cell, arm["name"])] = keys; n = gens[0]["n"]
            cnt = np.zeros((len(keys), len(rules), len(lengths), len(sources), nv, len(alphas)), dtype=np.uint8); pv = np.zeros((len(keys), n, len(rules), len(lengths)), dtype=np.float64)
            qual = {"ppl": [], "rep4": [], "loop": [], "green": [], "eos": [], "mean_logp_first_192": []}; green_keys = np.zeros(len(keys)); contract_ok_units = 0; failed_here = []
            for ik, u in enumerate(gens):
                name = R.unit_name(u); rec = recs[name]; z = np.load(cells_dir / f"{name}.npz"); arr = {k: z[k] for k in z.files}; validate_body(u, rec, arr, grid, V)
                X = arr["tokens"]; P, M, info, chain = T4.score_set(X, V, arm["h"], [u["key"]], gamma, rules, lengths, families=("kgw",))
                ok, n_bad, n_scored = hook_flag_contract(chain, u["key"], arr["flag"], gamma, V)
                if not ok:
                    out["integrity"]["contract_failures"].append({"unit": name, "mismatched_positions": n_bad, "scored_positions": n_scored}); failed_here.append(ik)
                else:
                    contract_ok_units += 1
                ki = key_index(u["key"], grid, validation)
                for ir, r in enumerate(rules):
                    for il, L in enumerate(lengths):
                        p = P[("kgw", r, L)][:, 0]; pv[ik, :, ir, il] = p
                        for isrc, src in enumerate(sources):
                            cu = cal_unit(src, arm["h"])
                            for iv, v in enumerate(vs):
                                m, nc = variant_parts(v)
                                for ia, a in enumerate(alphas):
                                    t = cu.threshold("kgw", r, m, a, nc)[ki]
                                    cnt[ik, ir, il, isrc, iv, ia] = T4.power_count(p, t)
                green_keys[ik] = float(arr["flag"].mean())
                if ok:   # a unit that failed the hook-flag contract enters no table (section 9); its arrays stay in the record as audit evidence
                    rep = G.rep_n(X); qual["ppl"].append(float(np.exp(-arr["logp"].mean()))); qual["rep4"].append(float(rep.mean())); qual["loop"].append(float((rep > grid["integrity"]["loop_bar_rep4"]).mean()))
                    qual["green"].append(float(arr["flag"].mean())); qual["eos"].append(float(arr["eos_mass"].astype(np.float32).mean())); qual["mean_logp_first_192"].append(float(arr["logp"][:, :192].mean()))
            power_counts[(cell, arm["name"])] = cnt; pvals[(cell, arm["name"])] = pv
            arrays[f"counts|{cell}|{arm['name']}"] = cnt; arrays[f"pvalues|{cell}|{arm['name']}"] = pv; arrays[f"keys|{cell}|{arm['name']}"] = np.array(keys, dtype=np.int64)
            arrays[f"green_share|{cell}|{arm['name']}"] = green_keys; arrays[f"contract_ok|{cell}|{arm['name']}"] = np.array([ik not in failed_here for ik in range(len(keys))])
            out["quality"][f"{cell}|{arm['name']}"] = ({k: {"mean": float(np.mean(v)), "min": float(np.min(v)), "max": float(np.max(v))} for k, v in qual.items()} if qual["ppl"] else {"note": "no unit passed the contract"}) | {"n_units": len(gens), "n_units_in_tables": contract_ok_units, "n_texts_per_unit": n}
            out["integrity"].setdefault("contract_ok_units", {})[f"{cell}|{arm['name']}"] = contract_ok_units
            log(f"{utc()} scored {cell} {arm['name']}: {len(gens)} units; mean green share {np.mean(qual['green']):.3f}; mean ppl {np.mean(qual['ppl']):.1f}; loop share {np.mean(qual['loop']):.3f}")
    out["integrity"]["n_contract_failures"] = len(out["integrity"]["contract_failures"]); n_gen = sum(1 for u in units if u["kind"] == "gen")
    out["integrity"]["contract_failure_share"] = out["integrity"]["n_contract_failures"] / max(1, n_gen); out["integrity"]["run_void"] = bool(out["integrity"]["contract_failure_share"] > grid["integrity"]["max_contract_failure_share"])
    failed_units = {f["unit"] for f in out["integrity"]["contract_failures"]}
    out["axes"] = {"counts": ["key", "rule", "L", "source", "variant", "alpha"], "pvalues": ["key", "text", "rule", "L"], "rules": rules, "lengths": lengths, "sources": sources, "variants": vs, "alphas": alphas, "null_variants": R3.variant_names(N_cals), "null_fixed_variants": VARIANTS_FIXED}
    if out["integrity"]["run_void"]:
        # section 9 rule 1: no rule is read on a void run; the integrity record, the quality of the units that passed and the arrays stay
        out["W1"] = out["W2"] = out["W3"] = {"pass": None, "note": "run void: the contract failure share exceeds the registered bound; no rule read"}
        out["seconds"] = round(time.time() - t_all, 1); out["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30, 2)
        log(f"{utc()} RUN VOID: {out['integrity']['n_contract_failures']} of {n_gen} generation units failed the hook-flag contract"); return out, arrays
    # ---- descriptive rows for the generation units ----
    n_tx = grid["validation"]["n_prompts"] if validation else grid["prompts"]["n_watermarked"]
    for (cell, armname), cnt in power_counts.items():
        keys = key_lists[(cell, armname)]; arm = R.arm_spec(grid, armname); ok_mask = np.array([R.unit_name({"kind": "gen", "cell": cell, "arm": armname, "key": k}) not in failed_units for k in keys])
        ia_nom = vs.index("nominal")
        if ok_mask.sum() < 2:
            out.setdefault("empty_blocks", []).append({"cell": cell, "arm": armname, "units_in_tables": int(ok_mask.sum())}); continue
        for ir, r in enumerate(rules):
            for il, L in enumerate(lengths):
                for isrc, src in enumerate(sources):
                    for iv, v in enumerate(vs):
                        for ia, a in enumerate(alphas):
                            if v in VARIANTS_FIXED and isrc > 0:
                                continue   # a fixed threshold does not depend on the source; stored under the first source only
                            pi = cnt[ok_mask, ir, il, isrc, iv, ia] / n_tx; pnom = cnt[ok_mask, ir, il, isrc, ia_nom, ia] / n_tx; cost = pnom - pi
                            m, nc = variant_parts(v); bsd = T4.between_key_sd(pi, n_tx)
                            thr_v = cal_unit(src, arm["h"]).threshold("kgw", r, m, a, nc)[[key_index(k, grid, validation) for k in np.array(keys)[ok_mask]]] if m in ("conformal", "tolerance") else np.full(int(ok_mask.sum()), (a if m == "nominal" else a * grid["beta"]) if m in VARIANTS_FIXED else float(cal_unit(src, arm["h"]).threshold("kgw", r, m, a)[0]))
                            Yv = (pvals[(cell, armname)][ok_mask, :, ir, il] < thr_v[:, None]).astype(np.float64); tw = T4.between_key_sd_twoway(Yv)
                            thr_k = np.array([cal_unit(src, arm["h"]).threshold("kgw", r, m, a, nc)[key_index(k, grid, validation)] for k in np.array(keys)[ok_mask]]) if m in ("conformal", "tolerance") else None
                            abst = int((thr_k <= 0).sum()) if thr_k is not None else 0
                            j_idx = cal_unit(src, arm["h"]).order_index("kgw", r, m, a, nc) if m in ("conformal", "tolerance") else None
                            abst_kind = ("structural" if (j_idx == 0) else "positive_index") if abst else None
                            out["descriptive_rows"].append({"cell": cell, "arm": armname, "h": arm["h"], "delta": arm["delta"], "rule": r, "L": L, "source": src if v not in VARIANTS_FIXED else None, "class": ("fixed" if v in VARIANTS_FIXED else ("diagonal" if src == cell else "transfer")),
                                                            "variant": v, "alpha": a, "K": int(ok_mask.sum()), "n": n_tx, "power_mean": float(pi.mean()), "power_sd_observed": float(pi.std(ddof=1)), "power_sd_between_twoway": tw["sd_between"], "power_var_between_raw_twoway": tw["var_between_raw"], "ms_resid_twoway": tw["ms_resid"],
                                                            "power_sd_between_binomial_proxy": bsd["sd_between"], "power_q05": float(np.quantile(pi, 0.05)), "power_q50": float(np.quantile(pi, 0.5)), "power_q95": float(np.quantile(pi, 0.95)),
                                                            "cost_mean": float(cost.mean()), "cost_q50": float(np.quantile(cost, 0.5)), "cost_q05": float(np.quantile(cost, 0.05)), "cost_q95": float(np.quantile(cost, 0.95)),
                                                            "power_var_between_raw_binomial_proxy": bsd["var_between_raw"], "mean_binomial_var": bsd["mean_binomial_var"], "keys_abstaining": abst, "abstention_kind": abst_kind, "order_index": j_idx})
    # ---- W1 ----
    w = grid["W1"]; rows = []
    def pilot_law_for(cell):
        arm_rec = inputs["pilot_law"]["arms"][w["arm"]]; cells_rec = arm_rec.get("by_cell")
        rec = cells_rec[cell] if (cells_rec and cell in cells_rec) else arm_rec
        return T4.PooledLaw(np.array(rec["p_values"][f"{w['rule']}@{w['length']}"])), rec
    ir, il, ia, iv_c, iv_n = rules.index(w["rule"]), lengths.index(w["length"]), alphas.index(float(w["alpha"])), vs.index(f"{w['method']}@{w['N_cal']}"), vs.index("nominal")
    for cell in cells:
        if (cell, w["arm"]) not in power_counts:
            continue
        cnt = power_counts[(cell, w["arm"])]; keys = key_lists[(cell, w["arm"])]; isrc = sources.index(cell); h = R.arm_spec(grid, w["arm"])["h"]
        ok_mask = np.array([R.unit_name({"kind": "gen", "cell": cell, "arm": w["arm"], "key": k}) not in failed_units for k in keys])
        if ok_mask.sum() < 2:
            continue
        law, law_rec = pilot_law_for(cell); tol_cell = (inputs.get("W1_tolerance", {}) or {}).get(cell)
        wc = dict(w, tolerance_pp=float(tol_cell["tolerance_pp"]) if tol_cell else w["tolerance_pp"])
        real = (cnt[ok_mask, ir, il, isrc, iv_n, ia].astype(np.float64) - cnt[ok_mask, ir, il, isrc, iv_c, ia]) / n_tx
        t_keys = np.array([cal_unit(cell, h).threshold("kgw", w["rule"], w["method"], float(w["alpha"]), w["N_cal"])[key_index(k, grid, validation)] for k in np.array(keys)[ok_mask]])
        pred = law.predicted_cost(t_keys, float(w["alpha"]))
        rows.append(w1_row(cell, real, pred, cnt[ok_mask, ir, il, isrc, iv_n, ia] / n_tx, wc, law.n) | {"pilot_law_cell": law_rec.get("cell", cell), "tolerance_source": ("INPUTS.json W1_tolerance" if tol_cell else "grid")})
    n_cons = sum(1 for r_ in rows if r_["class"] == "consistent"); n_inc = sum(1 for r_ in rows if r_["class"] == "inconsistent")
    out["W1"] = {"setting": w, "rows": rows, "n_consistent": n_cons, "n_inconsistent": n_inc, "n_unresolved": len(rows) - n_cons - n_inc, "n_rows": len(rows),
                 "pass": bool(n_cons >= w["min_consistent_cells"] and n_inc <= w["max_inconsistent_cells"]) if rows else None}
    # ---- W2 ----
    w2 = grid["W2"]; rows = []; il, ia, iv_c, iv_n = lengths.index(w2["length"]), alphas.index(float(w2["alpha"])), vs.index(f"{w2['method']}@{w2['N_cal']}"), vs.index("nominal")
    for cell in cells:
        if (cell, w2["arm"]) not in power_counts:
            continue
        cnt = power_counts[(cell, w2["arm"])]; keys = key_lists[(cell, w2["arm"])]; isrc = sources.index(cell); pv = pvals[(cell, w2["arm"])]; h2 = R.arm_spec(grid, w2["arm"])["h"]
        ok_mask = np.array([R.unit_name({"kind": "gen", "cell": cell, "arm": w2["arm"], "key": k}) not in failed_units for k in keys])
        if ok_mask.sum() < 2:
            continue
        for ir, r in enumerate(rules):
            P_kt = pv[ok_mask, :, ir, il]                                                                   # K x n p-values at (rule, L)
            t_c = np.array([cal_unit(cell, h2).threshold("kgw", r, w2["method"], float(w2["alpha"]), w2["N_cal"])[key_index(k, grid, validation)] for k in np.array(keys)[ok_mask]])
            Yn = (P_kt < float(w2["alpha"])).astype(np.float64); Yc = (P_kt < t_c[:, None]).astype(np.float64)
            if int(Yn.sum(axis=1).astype(np.int64).tolist() != cnt[ok_mask, ir, il, isrc, iv_n, ia].astype(np.int64).tolist()):
                raise BodyError(f"{cell} {r}: the indicator table's nominal counts differ from the stored counts")
            rows.append(w2_row(cell, r, Yn, Yc, w2))
    n_agree = sum(1 for r_ in rows if r_["class"] == "agree"); n_dis = sum(1 for r_ in rows if r_["class"] == "disagree")
    out["W2"] = {"setting": w2, "rows": rows, "n_agree": n_agree, "n_disagree": n_dis, "n_unresolved": len(rows) - n_agree - n_dis, "n_rows": len(rows),
                 "pass": bool(n_agree >= w2["min_agree_rows"] and n_dis <= w2["max_disagree_rows"]) if rows else None}
    # ---- the model-null block ----
    man3 = json.loads((ROOT / "outputs/study3_v0.1/tokens_manifest.json").read_text()); s3in = json.loads((ROOT / "outputs/study3_v0.1/INPUTS.json").read_text())
    null_keys = list(Rrec.keys); vs3 = R3.variant_names(N_cals); w3 = grid["W3"]; w3_rows = []; cal_chains = {}   # (source, h) -> the calibration chain, built once
    for cell in cells:
        nulls = sorted([u for u in units if u["kind"] == "null" and u["cell"] == cell], key=lambda u: u["chunk"])
        if not nulls:
            continue
        X0 = []
        for u in nulls:
            name = R.unit_name(u); rec = recs[name]; z = np.load(cells_dir / f"{name}.npz"); arr = {k: z[k] for k in z.files}; validate_body(u, rec, arr, grid, V); X0.append(arr["tokens"])
            rep = G.rep_n(arr["tokens"]); out["quality"].setdefault(f"{cell}|none", {"ppl": [], "rep4": [], "loop": [], "eos": [], "mean_logp_first_192": []})
            q = out["quality"][f"{cell}|none"]; q["ppl"].append(float(np.exp(-arr["logp"].mean()))); q["rep4"].append(float(rep.mean())); q["loop"].append(float((rep > grid["integrity"]["loop_bar_rep4"]).mean())); q["eos"].append(float(arr["eos_mass"].astype(np.float32).mean())); q["mean_logp_first_192"].append(float(arr["logp"][:, :192].mean()))
        X0 = np.concatenate(X0); N_E = X0.shape[0]; out["quality"][f"{cell}|none"] = {k: {"mean": float(np.mean(v)), "min": float(np.min(v)), "max": float(np.max(v))} for k, v in out["quality"][f"{cell}|none"].items()} | {"n_units": len(nulls), "N": int(N_E)}
        for h in grid["null_arm"]["widths"]:
            P0, M0, info0, chE = T4.score_set(X0, V, h, null_keys, gamma, rules, lengths, families=tuple(grid["null_arm"]["families"]), chunk=Rrec.grid["key_chunk"])
            srcs = [cal_unit(s, h) for s in sources]
            for fam in grid["null_arm"]["families"]:
                for ir, r in enumerate(rules):
                    for il, L in enumerate(lengths):
                        fixed, same = T4.null_counts(P0[(fam, r, L)], None, fam, r, alphas, vs3, srcs, grid["beta"])
                        arrays[f"null|{cell}|h{h}|{fam}|{r}|L{L}|fixed"] = fixed; arrays[f"null|{cell}|h{h}|{fam}|{r}|L{L}|same"] = same
                        # the predictor inputs (key-free, from the generated null set) against every calibration prefix; the cal moments checked against Study 3's pinned inputs
                        preds = {}
                        if fam == "kgw":
                            for isrc, src in enumerate(sources):
                                if (src, h) not in cal_chains:
                                    cal_chains[(src, h)] = S.build_chain(SD3.load_cal(src, tok, man3), V, "cal", h)
                                chC = cal_chains[(src, h)]; inp = T4.null_predictor_inputs(chE, L, r, chC, N_cals)
                                for nc in N_cals:
                                    ref = s3in["blocks"][f"h{h}|{r}"]["sets"][f"{tok}|{src}|C{nc}"]
                                    okm = T4.cal_moment_ok(inp["C"][nc]["rho"], ref["rho"]) and T4.cal_moment_ok(inp["C"][nc]["sigma2"], ref["sigma2"])
                                    out["null_inputs_consistency"].append({"cell": cell, "h": h, "rule": r, "source": src, "N_cal": nc, "abs_diff_rho": abs(inp["C"][nc]["rho"] - ref["rho"]), "abs_diff_sigma2": abs(inp["C"][nc]["sigma2"] - ref["sigma2"]), "within_allowance": bool(okm)})
                                    if not okm:
                                        raise BodyError(f"calibration prefix {src} C{nc} at h = {h}, {r}: the recomputed moments differ from Study 3's pinned inputs beyond the allowance {T4.CAL_MOMENT_REL} x max(1, |ref|)")
                                preds[src] = (inp, T4.null_predictions(inp, N_E, alphas, N_cals, grid["delta_tol"], grid["beta"]))
                        for ia, a in enumerate(alphas):
                            for iv, v in enumerate(VARIANTS_FIXED):
                                lv = fixed[iv, ia] / N_E; pr = preds[sources[0]][1]["fixed"][str(a)][v] if preds else None
                                w3_rows.append({"cell": cell, "h": h, "family": fam, "rule": r, "L": L, "source": None, "class": "fixed", "variant": v, "alpha": a, "K": len(null_keys), "N_E": int(N_E), "level_mean": float(lv.mean()), "level_sd": float(lv.std(ddof=1)),
                                                "share_above_alpha": float((lv > a).mean()), "q99": float(np.quantile(lv, 0.99)), "pred_sd": pr["sd_cond"] if pr else None, "pred_mean": pr["mean_level"] if pr else None, "theory_share": (pr.get("theory_share") if pr else None),
                                                "predictor": ("fixed-threshold predictor on the generated set's moments" if pr else "not applicable: the predictor is KGW-only"), "block": "null"})
                            for isrc, src in enumerate(sources):
                                for iv, v in enumerate(vs3):
                                    lv = same[isrc, iv, ia] / N_E; m, nc = variant_parts(v); pr = None; flags = []
                                    if preds:
                                        inp, pd = preds[src]
                                        if m in ("conformal", "tolerance"):
                                            pr = pd["per_key"][str(nc)][str(a)][m]
                                        else:
                                            pr = pd["fixed"][str(a)][m]
                                        flags = pr.get("flags", [])
                                    diag = {}
                                    if preds and m in ("conformal", "tolerance"):
                                        inp_s = preds[src][0]; diag = {"rho_E": inp_s["E"]["rho"], "sigma2_E": inp_s["E"]["sigma2"], "rho_C": inp_s["C"][nc]["rho"], "sigma2_C": inp_s["C"][nc]["sigma2"], "rho_CE": inp_s["rho_CE"][nc]["rho_CE"], "n_shared_tuples": inp_s["rho_CE"][nc]["n_shared_tuples"],
                                                         "v": pr.get("v"), "v_raw": pr.get("v_raw"), "j": pr.get("j"), "pred_share_above_alpha_finite": pr.get("share_above_alpha_finite"), "pred_share_above_alpha_pop": pr.get("share_above_alpha_pop")}
                                    row = {"cell": cell, "h": h, "family": fam, "rule": r, "L": L, "source": src, "class": "diagonal_prompt" if src == cell else "transfer", "variant": v, "alpha": a, "K": len(null_keys), "N_E": int(N_E), "level_mean": float(lv.mean()), "level_sd": float(lv.std(ddof=1)),
                                           "share_above_alpha": float((lv > a).mean()), "q99": float(np.quantile(lv, 0.99)), "keys_at_zero": int((lv == 0).sum()), "pred_sd": pr["sd_cond"] if pr else None, "pred_mean": pr["mean_level"] if pr else None, "theory_share": pr.get("theory_share") if pr else None, "flags": flags,
                                           "predictor": ("calibrated-threshold predictor" if (pr and m in ("conformal", "tolerance")) else ("fixed-threshold predictor at the model-implied scheme threshold" if pr else "not applicable: the predictor is KGW-only")), "block": "null", **diag}
                                    # W3 rows: KGW, the widths, rules, conformal at the N_cal list, alpha, L of the grid's W3
                                    if fam == w3["family"] and h in w3["widths"] and r in w3["rules"] and m == w3["method"] and nc in w3["N_cal"] and a == float(w3["alpha"]) and L == w3["length"] and pr is not None:
                                        row |= w3_fields(lv, pr, flags, w3, f"W3|{cell}|h{h}|{r}|{src}|{v}")
                                    w3_rows.append(row)
            if h in {a["h"] for a in grid["arms"]}:
                n_w = grid["prompts"]["n_watermarked"]; sel = [null_keys.index(k) for k in grid["keys"]["power_keys"]] if not validation else list(range(min(len(null_keys), 2)))
                for r in rules:
                    arrays[f"null_pvalues_first_prompts|{cell}|h{h}|kgw|{r}|L{grid['primary_length']}"] = P0[("kgw", r, grid["primary_length"])][:n_w][:, sel].astype(np.float64)   # n_w prompts x the power keys: the per-prompt pairing with the watermarked arms
            del P0
            log(f"{utc()} null block {cell} h={h}: {N_E} texts x {len(null_keys)} keys scored")
        cal_chains.clear()
    w3r = [r_ for r_ in w3_rows if "w3_class" in r_]; n_el = sum(1 for r_ in w3r if r_["w3_eligible"]); n_res = sum(1 for r_ in w3r if r_["w3_class"] in ("consistent", "inconsistent")); n_con = sum(1 for r_ in w3r if r_["w3_class"] == "consistent")
    out["W3"] = {"setting": w3, "n_candidate": len(w3r), "n_eligible": n_el, "n_resolved": n_res, "n_consistent": n_con, "n_inconsistent": n_res - n_con, "n_unresolved": n_el - n_res,
                 "pass": bool(n_res >= w3["min_resolved"] and n_con >= w3["min_consistent_share"] * n_res) if w3r else None, "rows": [{k: v for k, v in r_.items()} for r_ in w3r]}
    out["null_rows"] = w3_rows
    out["null_inputs_consistency_summary"] = {"n": len(out["null_inputs_consistency"]), "max_abs_diff_rho": max((x["abs_diff_rho"] for x in out["null_inputs_consistency"]), default=None), "max_abs_diff_sigma2": max((x["abs_diff_sigma2"] for x in out["null_inputs_consistency"]), default=None)}
    out["seconds"] = round(time.time() - t_all, 1); out["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30, 2)
    return out, arrays


def main(a):
    def opt(k, default=None):
        return a[a.index(k) + 1] if k in a else default
    grid_path = opt("--grid", "research/study4/grid_v0.1.json"); grid = json.loads(pathlib.Path(grid_path).read_text())
    inputs = json.loads((OUT / "INPUTS.json").read_text()); inputs["_sha256"] = sha(OUT / "INPUTS.json")
    if "--validation" in a:
        cells_dir = pathlib.Path(opt("--validation")); out, arrays = analyze(grid, cells_dir, inputs, "validation", validation=True); out["label"] = "VALIDATION (validation keys and pilot prompts; the record's thresholds stand in; not the study)"
        out_path = pathlib.Path(opt("--out", cells_dir.parent / "results_validation.json"))
    else:
        out, arrays = analyze(grid, OUT / "cells", inputs, "study", lock_path=opt("--lock")); out["label"] = "STUDY"; out_path = OUT / "results.json"
    np.savez_compressed(out_path.with_name(out_path.stem + "_arrays.npz"), **arrays); out["arrays_sha256"] = sha(out_path.with_name(out_path.stem + "_arrays.npz"))
    out_path.write_text(json.dumps(out, indent=0, default=float)); print("wrote", out_path, "W1", out["W1"].get("pass"), "W2", out["W2"].get("pass"), "W3", out["W3"].get("pass"), "integrity failures", out["integrity"]["n_contract_failures"], out["seconds"], "s")


if __name__ == "__main__":
    main(sys.argv[1:])
