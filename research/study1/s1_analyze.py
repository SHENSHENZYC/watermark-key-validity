"""Study 1 analysis (v5, after R03 round 4): applies the pre-registered rules R1-R5 (protocol v0.3 §9) to the cell JSONs.
Before any experiment-level decision it requires the COMPLETE expected inventory of the grid (every expected cell present, no
unexpected file), a verified canonical lock in study mode (or validation provenance in --pilot mode), every cell's provenance
equal to the current lock, grid and code digests and the deterministic seed and key record, every cell's slot and body equal
to its expected slot, markers exactly at the degenerate slots, every alpha and every required statistic field in the live
cells, and complete chains for the monotonicity rules; it raises InventoryError otherwise. No new simulation; reads cells only.
Usage: .venv/bin/python research/study1/s1_analyze.py --grid research/study1/grid_v0.3.json --lock outputs/study1_v0.3/PRE_RUN_LOCK.json
       [--cells outputs/study1_v0.3/cells] [--out outputs/study1_v0.3/results.json]
       --pilot [--cells <validation dir>] [--out <file outside the cells directory>]   (the grid's validation laws; no lock; output labelled PILOT)
"""
import json, pathlib, sys
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import s1_core as C
from s1_run import expected_cells, law_name, OUT, STUDY, GRID_CANON, verify_lock, sha, text_seed_for, body_matches_slot, slot_of

R1_BAND = (2.0 / 3.0, 1.5); R1_ALPHA = "0.01"; R1_RULES = ("raw", "distinct"); R1_MIN_M = 30; R1_MIN_THEORY_SHARE = 0.75; R1_MIN_RESOLVED = 30; R1_PASS_SHARE = 0.80
R2_PBOUND = C.R2_PBOUND; R3_GROSS_SE = C.R3_GROSS_SE; R3_REDUCTION_V = 10000; R3_REDUCTION_BOUND = 0.01
REQUIRED_CELL_FIELDS = ("N_eff", "frac_M0", "mean_M", "q_hat", "zbar", "z_var_within_key", "identity_q", "identity_z", "population", "levels", "covariance_heterogeneity")
REQUIRED_LEVEL_FIELDS = ("key_mean_level", "unconditional_rate", "se_conditional_on_texts", "r2_kl_pbound", "sd_obs_conditional", "sd_obs_boot_ci95", "pred_first_order", "pred_unit_sigma",
                         "pred_pairwise_gaussian", "ratio_obs_over_pred", "ratio_boot_ci95", "population_est", "exact_marginal_if_indep_distinct", "structural_zero", "level_values")


class InventoryError(RuntimeError):
    pass


def load_inventory(cells_dir, grid, pilot, lock_path=None, grid_path=GRID_CANON):
    """The experiment-identity gate (R03 round 2, F11); see the module docstring for the seven requirements."""
    laws = grid["validation_laws"] if pilot else None
    expected = expected_cells(grid, laws); exp_names = {c["file"] for c in expected}
    on_disk = {f.name for f in pathlib.Path(cells_dir).glob("*.json") if not f.name.startswith("costs__")}
    missing = sorted(exp_names - on_disk); extra = sorted(on_disk - exp_names)
    if missing or extra:
        raise InventoryError(f"inventory incomplete: {len(missing)} expected cells missing (first: {missing[:3]}); {len(extra)} unexpected files (first: {extra[:3]})")
    if pilot:
        lock_sha = None; mode = "validation"; seed_base = grid["validation_seed_base"]; key_start = grid["validation_key_seed_start"]
    else:
        if lock_path is None:
            raise InventoryError("study mode requires --lock (the verified canonical lock)")
        verify_lock(lock_path, grid_path); lock_sha = sha(lock_path); mode = "study"; seed_base = grid["text_seed_base"]; key_start = grid["key_seed_start"]
    cur = {"study": STUDY, "mode": mode, "lock_sha256": lock_sha, "grid_sha256": sha(grid_path), "core_sha256": sha(HERE / "s1_core.py"), "run_sha256": sha(HERE / "s1_run.py"), "text_seed_base": int(seed_base), "key_start": int(key_start)}
    cells = []
    for c in expected:
        try:
            d = json.loads((pathlib.Path(cells_dir) / c["file"]).read_text())
        except Exception as e:
            raise InventoryError(f"{c['file']}: unreadable ({e})")
        pv = d.get("provenance", {})
        want = dict(cur, text_seed=text_seed_for(c["name"], seed_base), K=c["K"])
        diff = [k for k, v in want.items() if pv.get(k) != v]
        if pv.get("slot") != slot_of(c):
            diff.append("slot")
        if diff:
            raise InventoryError(f"{c['file']}: provenance differs from the current experiment in {diff}")
        if not body_matches_slot(d, slot_of(c)) or d.get("N") != grid["N"]:
            raise InventoryError(f"{c['file']}: body disagrees with its slot or the grid's N")
        is_marker = "levels" not in d
        if bool(c["degenerate"]) != is_marker:
            raise InventoryError(f"{c['file']}: marker status {is_marker} differs from the expected degeneracy {c['degenerate']}")
        if not is_marker:
            if d.get("N_eff", 0) > 0:
                mf = [f for f in REQUIRED_CELL_FIELDS if f not in d]
                if mf:
                    raise InventoryError(f"{c['file']}: lacks the fields {mf}")
                if set(d["levels"]) != {str(a) for a in grid["alpha"]}:
                    raise InventoryError(f"{c['file']}: levels for {sorted(d['levels'])} instead of {sorted(str(a) for a in grid['alpha'])}")
                for a, lv in d["levels"].items():
                    ml = [f for f in REQUIRED_LEVEL_FIELDS if f not in lv]
                    if ml:
                        raise InventoryError(f"{c['file']} alpha {a}: lacks the fields {ml}")
            elif "flag" not in d:
                raise InventoryError(f"{c['file']}: N_eff = 0 without the no-detection flag")
        d["file"] = c["file"]; d["_exp"] = c; cells.append(d)
    return cells, cur


def r3_check(c):
    """R3's per-cell decision (R03 rounds 3 and 4, F17 and F22): a gross failure iff |s0^2 - exact| > R3_GROSS_SE x SE + tol, with tol the cell's
    scale-aware tolerance (10^-9 x g(1-g) A), so that a roundoff-sized difference never fails whatever the computed SE (where the squared deviations
    are constant over the keys by a distributional identity, as in the two-token chain at h = 0 under the fixed colouring, the bootstrap SE is zero or
    roundoff-sized and the tolerance decides); structural zeros (exact 0) require s0^2 <= tol. The SE is never overridden by observed constancy."""
    q = c["q_hat"]; exact = q["exact_var_own_colouring"]; tol = q.get("r3_tolerance", C.ZERO_REL * max(c["g"] * (1 - c["g"]) * c["identity_q"]["A"], 1e-300))
    se = q["var_known_mean_se"]; diff = abs(q["var_known_mean"] - exact); lo, hi = q["var_boot_ci95"]
    if q["structural_zero"]:
        gross = bool(q["var_known_mean"] > tol); dev = float("nan")
    else:
        gross = bool(diff > R3_GROSS_SE * se + tol); dev = (diff / se) if se > 0 else (0.0 if diff <= tol else float("inf"))
    return {"observed_var_known_mean": q["var_known_mean"], "se": se, "se_method": q["se_method"], "exact": exact, "tolerance": tol, "abs_diff": diff, "structural_zero": q["structural_zero"],
            "observed_sample_constancy": q.get("observed_sample_constancy", False), "dev_over_se": dev, "gross": gross, "ci95_covers": bool(lo <= exact <= hi) if not q["structural_zero"] else None, "rel_dev": (q["var_known_mean"] / exact - 1) if exact > 0 else float("nan")}


def ckey(c, *fields):
    return (law_name(c["law"]),) + tuple(c[f] for f in fields)


def main(grid_path, cells_dir, out, pilot, lock_path=None):
    grid = json.loads(pathlib.Path(grid_path).read_text())
    cells, prov = load_inventory(cells_dir, grid, pilot, lock_path, grid_path)
    live = [c for c in cells if "levels" in c and c.get("N_eff", 0) > 0 and not c.get("degenerate")]
    core = [c for c in live if c["_exp"]["role"] == "core"]          # design classifications come from the expected slot, never from the cell body (F20)
    g0 = grid["gamma"][0]
    res = {"label": "PILOT (validation laws, validation seeds and keys; not study outcomes)" if pilot else "STUDY", "provenance": prov, "n_cells": len(cells),
           "n_live": len(live), "n_degenerate_markers": sum(1 for c in cells if c.get("degenerate") and "levels" not in c), "n_no_detection": sum(1 for c in cells if c.get("N_eff", 1) == 0), "rules": {}}
    chainsL = {}
    for c in core:
        if c["colouring"] == "independent":
            chainsL.setdefault(ckey(c, "h", "gamma", "rule"), set()).add(c["L"])
    bad = [k for k, Ls in chainsL.items() if Ls != set(grid["L"])]
    if bad:
        raise InventoryError(f"{len(bad)} core chains lack lengths (first: {bad[:2]})")
    chainsH = {}
    for c in core:
        if c["colouring"] == "independent":
            chainsH.setdefault(ckey(c, "L", "gamma", "rule"), set()).add(c["h"])
    bad = [k for k, hs in chainsH.items() if hs != set(grid["h"])]
    if bad:
        raise InventoryError(f"{len(bad)} core (law, L) chains lack widths (first: {bad[:2]})")

    # ---- R1 adequacy of the common-factor predictor, conditional on the realised texts (primary at alpha = 0.01) ----
    def r1_entry(c, alpha, pred_key):
        lv = c["levels"][alpha]; p = lv[pred_key]; sd_pred = p["sd_cond"]; sd_obs = lv["sd_obs_conditional"]
        ratio = sd_obs / sd_pred if sd_pred > 0 else float("nan")
        lo, hi = [b / sd_pred if sd_pred > 0 else float("nan") for b in lv["sd_obs_boot_ci95"]]
        if not np.isfinite(ratio):
            status = "unresolved"
        elif R1_BAND[0] <= lo and hi <= R1_BAND[1]:
            status = "consistent"
        elif hi < R1_BAND[0] or lo > R1_BAND[1]:
            status = "inconsistent"
        else:
            status = "unresolved"
        pw = lv.get("pred_pairwise_gaussian") or {}; het = c.get("covariance_heterogeneity") or {}
        return {"cell": c["file"], "law": law_name(c["law"]), "h": c["h"], "L": c["L"], "rule": c["rule"], "ratio": ratio, "ratio_ci95": [lo, hi], "status": status,
                "sd_obs_pp": sd_obs * 100, "sd_pred_pp": sd_pred * 100, "theory_share": p["theory_share"], "sd_zshift_pop": c["population"]["sd_zshift_pop"], "mean_M": c["mean_M"],
                "sigma2_model": p["sigma2"], "sigma2_observed": c["z_var_within_key"]["mean_over_keys"], "pred_flags": p.get("flags", []), "sd_linear_pop_pp": (p["sd_linear_pop"] * 100) if p["sd_linear_pop"] == p["sd_linear_pop"] else None,
                "sd_pred_unit_sigma_pp": lv["pred_unit_sigma"]["sd_cond"] * 100, "key_mean_level": lv["key_mean_level"], "pred_mean_level": p["mean_level"],
                "sd_pred_pairwise_pp": (pw.get("sd_cond", float("nan")) * 100), "ratio_pairwise": (sd_obs / pw["sd_cond"]) if pw.get("sd_cond", 0) > 0 else float("nan"),
                "pair_cov_cv": het.get("pair_cov_cv"), "pair_corr_q99": (het.get("pair_corr_quantiles") or {}).get("0.99")}
    def r1_block(cs, alpha, pred_key="pred_first_order"):
        rows = [r1_entry(c, alpha, pred_key) for c in cs if c["mean_M"] >= R1_MIN_M and c["levels"][alpha][pred_key]["theory_share"] >= R1_MIN_THEORY_SHARE]
        resolved = [r for r in rows if r["status"] != "unresolved"]; cons = [r for r in resolved if r["status"] == "consistent"]
        share = len(cons) / len(resolved) if resolved else float("nan")
        return {"n_candidates": len(cs), "n_eligible": len(rows), "n_resolved": len(resolved), "n_consistent": len(cons), "n_inconsistent": len(resolved) - len(cons), "n_unresolved": len(rows) - len(resolved),
                "share_consistent": share, "pass": bool(resolved) and len(resolved) >= R1_MIN_RESOLVED and share >= R1_PASS_SHARE, "min_resolved_required": R1_MIN_RESOLVED,
                "band": R1_BAND, "inconsistent_cells": [r for r in resolved if r["status"] != "consistent"], "unresolved_cells": [r for r in rows if r["status"] == "unresolved"], "rows": rows}
    r1_set = [c for c in core if c["colouring"] == "independent" and c["rule"] in R1_RULES and c["gamma"] == g0]
    res["rules"]["R1"] = r1_block(r1_set, R1_ALPHA)
    res["rules"]["R1_secondary"] = {"alpha_0.05": r1_block(r1_set, "0.05"), "alpha_0.001": r1_block(r1_set, "0.001"),
                                    "first_rule": r1_block([c for c in core if c["colouring"] == "independent" and c["rule"] == "first" and c["gamma"] == g0], R1_ALPHA),
                                    "gamma_extra": r1_block([c for c in core if c["colouring"] == "independent" and c["rule"] in R1_RULES and c["gamma"] != g0], R1_ALPHA),
                                    "unit_sigma_predictor": r1_block(r1_set, R1_ALPHA, "pred_unit_sigma"),
                                    "illustration": r1_block([c for c in live if c["_exp"]["role"] == "illustration" and c["colouring"] == "independent" and c["rule"] in R1_RULES], R1_ALPHA),
                                    "fixed_colouring": r1_block([c for c in live if c["colouring"] == "fixed" and c["rule"] in R1_RULES], R1_ALPHA)}
    res["rules"]["population_diagnostic"] = [{"cell": c["file"], "var_pop_twoway": c["levels"][R1_ALPHA]["population_est"]["var_pop_signed"], "se": c["levels"][R1_ALPHA]["population_est"]["var_pop_boot_se"],
                                              "var_pop_mixture": c["levels"][R1_ALPHA]["pred_first_order"]["var_pop"]} for c in r1_set]
    # ---- R2 simulator validity (independent + distinct), conditional on the texts: Hoeffding's KL bound on the key-mean's deviation ----
    # decided at every alpha and every K: audit flag iff any check's TWO-SIDED bound falls below R2_PBOUND (per-check false audit <= R2_PBOUND; union bound over the checks whatever their dependence);
    # the normal 3-SE comparison is reported as a diagnostic (dev/SE quantiles); structural zeros counted separately
    r2, zeros = [], 0
    for c in live:
        if c["colouring"] != "independent" or c["rule"] != "distinct":
            continue
        for a, lv in c["levels"].items():
            if lv["structural_zero"]:
                zeros += 1; continue
            dev = abs(lv["key_mean_level"] - lv["exact_marginal_if_indep_distinct"]); se = lv["se_conditional_on_texts"]
            r2.append({"cell": c["file"], "alpha": a, "K": c["K"], "N_eff": c["N_eff"], "key_mean": lv["key_mean_level"], "exact": lv["exact_marginal_if_indep_distinct"], "kl_pbound": lv["r2_kl_pbound"],
                       "flag": bool(lv["r2_kl_pbound"] < R2_PBOUND), "dev_over_se_normal": (dev / se) if se > 0 else (float("inf") if dev > 0 else 0.0)})
    flagged = [x for x in r2 if x["flag"]]
    res["rules"]["R2"] = {"n_checks": len(r2), "n_structural_zero": zeros, "n_flagged": len(flagged), "pbound_threshold": R2_PBOUND, "false_audit_union_bound": len(r2) * R2_PBOUND,
                          "pass": bool(r2) and not flagged, "audit_flag": bool(flagged), "flagged": flagged[:100], "min_pbound": min((x["kl_pbound"] for x in r2), default=None),
                          "dev_over_se_normal_quantiles": {q: float(np.quantile([x["dev_over_se_normal"] for x in r2 if np.isfinite(x["dev_over_se_normal"])], float(q))) for q in ("0.5", "0.9", "0.99", "1.0")} if r2 else None,
                          "n_zero_se_normal": sum(1 for x in r2 if not np.isfinite(x["dev_over_se_normal"]))}
    # ---- R3 the exact identities per colouring: the known-mean variance estimator against its own exact value ----
    # gross failure iff |s0^2 - exact| > R3_GROSS_SE x SE (exact fourth-moment SE for the independent colouring; key bootstrap for the fixed colouring);
    # structural zeros: the exact value is 0 and the observed variation must be negligible; the coverage of the nominal 95% key-bootstrap intervals is a diagnostic
    r3, rep = [], []
    for c in live:
        e = r3_check(c); e.update({"cell": c["file"], "colouring": c["colouring"], "V": c["_exp"]["V"], "K": c["K"]})
        (rep if (c["_exp"]["role"] == "core" and c["colouring"] == "fixed") else r3).append(e)
    gross3 = [x for x in r3 if x["gross"]]; cov = [x["ci95_covers"] for x in r3 if x["ci95_covers"] is not None]
    big = [{"cell": c["file"], "V": c["_exp"]["V"], "reduction": 1 - c["identity_q"]["exact_ratio_formula"], "C_cond": c["identity_q"]["C_cond"]} for c in core if c["colouring"] == "independent" and c["_exp"]["V"] >= R3_REDUCTION_V]
    res["rules"]["R3"] = {"n_checks": len(r3), "n_structural_zero": sum(1 for x in r3 if x["structural_zero"]), "n_gross": len(gross3), "gross_threshold_se": R3_GROSS_SE, "pass": bool(r3) and not gross3,
                          "coverage_95_diagnostic": float(np.mean(cov)) if cov else None, "n_coverage_checks": len(cov),
                          "n_observed_sample_constancy": sum(1 for x in r3 if x["observed_sample_constancy"]),
                          "dev_over_se_quantiles": {q: float(np.quantile([x["dev_over_se"] for x in r3 if np.isfinite(x["dev_over_se"])], float(q))) for q in ("0.5", "0.9", "0.99", "1.0")} if r3 else None,
                          "gross_failures": gross3[:100], "core_fixed_subset_reported": rep, "reduction_below_1pct_for_V_ge_10000": all(x["reduction"] < R3_REDUCTION_BOUND for x in big) if big else None,
                          "max_reduction_V_ge_10000": max((x["reduction"] for x in big), default=None), "n_cells_V_ge_10000": len(big)}
    # ---- R4 H-length under the raw rule: rho_bar(L) non-decreasing within the text-bootstrap tolerance (core, independent) ----
    chains = {}
    for c in core:
        if c["colouring"] == "independent":
            chains.setdefault(ckey(c, "h", "gamma", "rule"), []).append(c)
    r4, curves = [], {}
    for k, cs in chains.items():
        cs = sorted(cs, key=lambda c: c["L"]); rule = k[-1]
        rho = [c["population"]["rho_bar"] for c in cs]; se = [c["population"]["rho_bar_boot_se"] for c in cs]
        mono = all(rho[i + 1] >= rho[i] - 2 * (se[i] + se[i + 1]) for i in range(len(rho) - 1))
        entry = {"chain": [str(x) for x in k], "L": [c["L"] for c in cs], "rho_bar": rho, "rho_bar_se": se, "mean_M": [c["mean_M"] for c in cs],
                 "level_sd_obs_pp": [c["levels"][R1_ALPHA]["sd_obs_conditional"] * 100 for c in cs], "level_sd_pred_pp": [c["levels"][R1_ALPHA]["pred_first_order"]["sd_cond"] * 100 for c in cs],
                 "non_decreasing_within_tolerance": bool(mono)}
        if rule == "raw":
            r4.append(entry)
        curves.setdefault(rule, []).append(entry)
    res["rules"]["R4"] = {"n_chains": len(r4), "share_non_decreasing": float(np.mean([x["non_decreasing_within_tolerance"] for x in r4])) if r4 else float("nan"),
                          "pass": bool(r4) and all(x["non_decreasing_within_tolerance"] for x in r4), "chains": r4}
    sat = []
    for c in live:
        if c["law"]["kind"] != "support" or c["rule"] != "distinct" or c["h"] != 0:
            continue
        s = c["law"]["s_support"]; V = c["law"]["V"]; g = c["g"]; gam = c["gamma"]
        vq = g * (1 - g) * (V - s) / (s * (V - 1)) if c["colouring"] == "fixed" else g * (1 - g) / s
        lim = s * vq / (gam * (1 - gam))
        sat.append({"cell": c["file"], "L": c["L"], "colouring": c["colouring"], "gamma": gam, "mean_M": c["mean_M"], "rho_bar": c["population"]["rho_bar"], "se": c["population"]["rho_bar_boot_se"], "limit_rho": lim,
                    "q_identity_at_realised_weights": c["identity_q"]["var_fixed" if c["colouring"] == "fixed" else "var_indep"], "limit_q": vq})
    longest = max((x["L"] for x in sat), default=None)
    at_long = [x for x in sat if x["L"] == longest]
    res["rules"]["R4b_saturation"] = {"n": len(at_long), "reproduced": (all(abs(x["rho_bar"] - x["limit_rho"]) <= 3 * x["se"] + 1e-9 for x in at_long) if at_long else None), "rows": sorted(sat, key=lambda x: (x["colouring"], x["gamma"], x["L"]))}
    # ---- R5 H-width under the raw rule: the between-text collision A_between(h) non-increasing within tolerance (core, independent) ----
    byh = {}
    for c in core:
        if c["colouring"] == "independent" and c["rule"] == "raw":
            byh.setdefault(ckey(c, "L", "gamma"), []).append(c)
    r5 = []
    for k, cs in byh.items():
        cs = sorted(cs, key=lambda c: c["h"])
        A = [c["population"]["A_q_between"] for c in cs]; se = [c["population"]["A_q_between_boot_se"] for c in cs]
        mono = all(A[i + 1] <= A[i] + 2 * (se[i] + se[i + 1]) for i in range(len(A) - 1))
        r5.append({"chain": [str(x) for x in k], "h": [c["h"] for c in cs], "A_between": A, "A_between_se": se, "A_realised": [c["identity_q"]["A"] for c in cs],
                   "C_h_analytic": [c["population"]["collision_h_analytic"] for c in cs], "rho_bar": [c["population"]["rho_bar"] for c in cs],
                   "level_sd_obs_pp": [c["levels"][R1_ALPHA]["sd_obs_conditional"] * 100 for c in cs], "non_increasing_within_tolerance": bool(mono)})
    res["rules"]["R5"] = {"n_chains": len(r5), "share_non_increasing": float(np.mean([x["non_increasing_within_tolerance"] for x in r5])) if r5 else float("nan"),
                          "pass": bool(r5) and all(x["non_increasing_within_tolerance"] for x in r5), "chains": r5}
    res["descriptive"] = {"level_sd_curves_by_rule": curves,
                          "integrity": {"degenerate_markers": [c["file"] for c in cells if c.get("degenerate") and "levels" not in c], "no_detection_cells": [c["file"] for c in cells if c.get("N_eff", 1) == 0],
                                        "cells_with_M0_texts": [{"cell": c["file"], "frac_M0": c["frac_M0"]} for c in live if c["frac_M0"] > 0],
                                        "predictor_flags": [{"cell": c["file"], "alpha": a, "flags": lv["pred_first_order"]["flags"]} for c in live for a, lv in c["levels"].items() if lv["pred_first_order"].get("flags")],
                                        "two_token_fixed_variances": {c["file"]: c["identity_q"]["var_fixed"] for c in live if c["law"]["kind"] == "twotoken" and c["rule"] == "raw" and c["colouring"] == "fixed" and c["gamma"] == 0.5 and c["L"] == max(grid["L_illustration"])}}}
    pathlib.Path(out).write_text(json.dumps(res, indent=1, default=float))
    summary = {k: {kk: vv for kk, vv in v.items() if kk in ("n_candidates", "n_eligible", "n_resolved", "n_consistent", "n_inconsistent", "n_unresolved", "share_consistent", "n_checks", "n_structural_zero", "n_flagged", "n_gross", "n_chains", "coverage_95_diagnostic", "share_non_decreasing", "share_non_increasing", "pass", "audit_flag", "reproduced", "reduction_below_1pct_for_V_ge_10000", "max_reduction_V_ge_10000")}
               for k, v in res["rules"].items() if isinstance(v, dict) and k not in ("R1_secondary",)}
    print(res["label"]); print(json.dumps(summary, indent=1, default=float))
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[a.index("--grid") + 1], a[a.index("--cells") + 1] if "--cells" in a else str(OUT / "cells"), a[a.index("--out") + 1] if "--out" in a else str(OUT / "results.json"), "--pilot" in a,
         a[a.index("--lock") + 1] if "--lock" in a else None)
