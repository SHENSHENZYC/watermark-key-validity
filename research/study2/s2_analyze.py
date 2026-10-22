"""Study 2 analysis (v1): applies the pre-registered rules S1-S5 (protocol v0.1 §9) and the descriptive blocks (§7) to the cell
JSONs. Before any experiment-level decision it requires the COMPLETE expected inventory of the grid (every expected cell present,
no unexpected file), a verified canonical lock in study mode (or validation provenance in --pilot mode), every cell's provenance
equal to the current lock, grid, code and manifest digests and the key record, every cell's slot and body equal to its expected
slot, and every alpha and required statistic field in the live cells; it raises InventoryError otherwise. No new computation on
texts or keys; reads cells only.
Usage: .venv/bin/python research/study2/s2_analyze.py --grid research/study2/grid_v0.1.json --lock outputs/study2_v0.1/PRE_RUN_LOCK.json
       [--cells outputs/study2_v0.1/cells] [--out outputs/study2_v0.1/results.json]
       --pilot [--cells <validation dir>] [--out <file outside the cells directory>]   (synthetic validation cells; no lock; output labelled PILOT)
"""
import json, pathlib, sys
import numpy as np
from scipy.stats import spearmanr, pearsonr
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / "research/study1"))
import s1_core as C
from s2_run import expected_cells, verify_lock, sha, slot_of, body_matches_slot, OUT, STUDY, GRID_CANON, TOKENS_MANIFEST, HERE as RUN_HERE, ROOT, in_deployer_subset, validate_cell_body, CellBodyError

S2_PBOUND = C.R2_PBOUND; S3_GROSS_SE = C.R3_GROSS_SE


class InventoryError(RuntimeError):
    pass


def specs_and_tokenizers(grid, pilot):
    """The corpus specs and tokenizer labels the rules iterate over: the production grid, or the synthetic validation spec in pilot mode
    (so that the pilot exercises S1, S4, S5 and the descriptive paths; R05 F1)."""
    if pilot:
        v = grid["validation"]; return [{"tag": v["tag"], "L": v["L"], "source": "synthetic", "lang": "synthetic", "L_cell": max(v["L"])}], {v["tokenizer_label"]: {"V": v["law"]["V"]}}, v["h"]
    return grid["cells"], grid["tokenizers"], grid["h"]


def load_inventory(cells_dir, grid, pilot, lock_path=None, grid_path=GRID_CANON):
    """The experiment-identity gate: study mode needs the verified canonical lock before anything is read; the inventory must be
    exactly the expected set; every cell's provenance, slot and body contract (validate_cell_body: N_eff = N, the required fields,
    K integer level counts in [0, N_eff] reconciled with the stored summaries, nested across alpha, the crossed block on deployer
    cells) must hold; raises InventoryError otherwise."""
    if not pilot:
        if lock_path is None:
            raise InventoryError("study mode requires --lock (the verified canonical lock)")
        verify_lock(lock_path, grid_path); lock_sha = sha(lock_path); mode = "study"; key_start = grid["key_seed_start"]; man_sha = sha(TOKENS_MANIFEST); man = json.loads(pathlib.Path(TOKENS_MANIFEST).read_text())
    else:
        lock_sha = None; mode = "validation"; key_start = grid["validation_key_seed_start"]; man_sha = None; man = None
    expected = expected_cells(grid, validation=pilot); exp_names = {c["file"] for c in expected}
    on_disk = {f.name for f in pathlib.Path(cells_dir).glob("*.json") if not f.name.startswith("costs__")}
    missing = sorted(exp_names - on_disk); extra = sorted(on_disk - exp_names)
    if missing or extra:
        raise InventoryError(f"inventory incomplete: {len(missing)} expected cells missing (first: {missing[:3]}); {len(extra)} unexpected files (first: {extra[:3]})")
    specs, toks, _ = specs_and_tokenizers(grid, pilot); L_of = {sp["tag"]: sp["L"] for sp in specs}
    cur = {"study": STUDY, "mode": mode, "lock_sha256": lock_sha, "grid_sha256": sha(grid_path), "core_sha256": sha(RUN_HERE / "s2_core.py"), "run_sha256": sha(RUN_HERE / "s2_run.py"),
           "s1core_sha256": sha(ROOT / "research/study1/s1_core.py"), "tokens_manifest_sha256": man_sha, "key_start": int(key_start)}
    cells = []
    for c in expected:
        try:
            d = json.loads((pathlib.Path(cells_dir) / c["file"]).read_text())
        except Exception as e:
            raise InventoryError(f"{c['file']}: unreadable ({e})")
        pv = d.get("provenance", {})
        want = dict(cur, K=c["K"], N=c["N"], tokens_sha256=("synthetic" if pilot else man["cells"][c["tag"]]["tokenizers"][c["tokenizer"]]["sha256"]))
        diff = [k for k, v in want.items() if pv.get(k) != v]
        if pv.get("slot") != slot_of(c):
            diff.append("slot")
        if diff:
            raise InventoryError(f"{c['file']}: provenance differs from the current experiment in {diff}")
        if not body_matches_slot(d, slot_of(c)):
            raise InventoryError(f"{c['file']}: body disagrees with its slot")
        try:
            validate_cell_body(d, dict(c, L_list=L_of[c["tag"]]), grid)
        except CellBodyError as e:
            raise InventoryError(f"{c['file']}: {e}")
        cells.append(dict(c, data=d))
    return cells


def live(c):
    """Every non-degenerate cell of this grid is live: the inventory gate requires N_eff = N (R05 F1)."""
    return (not c["degenerate"]) and c["data"].get("N_eff", 0) > 0


def levels_of(d, alpha):
    """The per-key levels from the stored integer counts of rejecting texts (exact: k / N_eff)."""
    return np.array(d["levels"][str(alpha)]["level_counts"], dtype=np.float64) / d["N_eff"]


def status_of(lv, band, min_M, min_share, mean_M):
    """R1-type status: eligible when mean M >= min_M and the predictor's theory share >= min_share; consistent / inconsistent /
    unresolved from the key-bootstrap interval of the observed-to-predicted ratio against the band."""
    pred = lv["pred_first_order"]
    if mean_M < min_M or pred["sd_cond"] <= 0 or pred["theory_share"] < min_share or pred.get("flags"):
        return "ineligible"
    lo, hi = lv["ratio_boot_ci95"]
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return "unresolved"
    if lo >= band[0] and hi <= band[1]:
        return "consistent"
    if hi < band[0] or lo > band[1]:
        return "inconsistent"
    return "unresolved"


def row_for(c, a, status):
    d = c["data"]; lv = d["levels"][str(a)]; pop = d["population"]
    return {"file": c["file"], "tag": c["tag"], "tokenizer": c["tokenizer"], "family": c["family"], "h": c["h"], "L": c["L"], "rule": c["rule"], "colouring": c["colouring"], "gamma": c["gamma"], "alpha": a, "status": status,
            "mean_M": d["mean_M"], "N_eff": d["N_eff"], "sigma_delta": pop.get("sd_zshift_pop"), "theory_share": lv["pred_first_order"]["theory_share"], "sd_obs": lv["sd_obs_conditional"], "sd_obs_ci95": lv["sd_obs_boot_ci95"],
            "sd_pred": lv["pred_first_order"]["sd_cond"], "ratio": lv["ratio_obs_over_pred"], "ratio_ci95": lv["ratio_boot_ci95"], "key_mean_level": lv["key_mean_level"], "pred_mean_level": lv["pred_first_order"]["mean_level"],
            "exact_mean_if_distinct": lv.get("exact_marginal_if_indep_distinct", lv.get("exact_marginal_if_distinct")), "sigma2_model": pop.get("sigma_model2"), "sigma2_observed": d["z_var_within_key"]["mean_over_keys"],
            "ratio_pairwise": (lv["sd_obs_conditional"] / lv["pred_pairwise_gaussian"]["sd_cond"]) if (lv.get("pred_pairwise_gaussian") and lv["pred_pairwise_gaussian"]["sd_cond"] > 0) else None,
            "pairwise_replicate_sd": lv["pred_pairwise_gaussian"].get("sd_cond_replicate") if lv.get("pred_pairwise_gaussian") else None,
            "ratio_simulated_shift": lv.get("ratio_obs_over_pred_simulated_shift"), "ratio_unit_sigma": (lv["sd_obs_conditional"] / lv["pred_unit_sigma"]["sd_cond"]) if lv["pred_unit_sigma"]["sd_cond"] > 0 else None,
            "heterogeneity": d.get("covariance_heterogeneity"), "n_keys_level_zero": int(sum(1 for k in lv["level_counts"] if k == 0)), "n_keys_level_one": int(sum(1 for k in lv["level_counts"] if k == d["N_eff"])),
            "n_distinct_levels": int(len(set(lv["level_counts"]))), "n_keys_above_5alpha": int(sum(1 for k in lv["level_counts"] if k > 5 * a * d["N_eff"]))}


def adequacy_block(cells, grid, select, alpha, label):
    P = grid["primary"]; rows = []; counts = {"candidate": 0, "eligible": 0, "resolved": 0, "consistent": 0, "inconsistent": 0, "unresolved": 0}
    for c in cells:
        if not select(c) or not live(c):
            continue
        counts["candidate"] += 1; lv = c["data"]["levels"][str(alpha)]
        st = status_of(lv, P["band"], P["min_mean_M"], P["min_theory_share"], c["data"]["mean_M"])
        if st != "ineligible":
            counts["eligible"] += 1; counts[st] += 1
            if st != "unresolved":
                counts["resolved"] += 1
        rows.append(row_for(c, alpha, st))
    return {"label": label, "alpha": alpha, "counts": counts, "rows": rows}


def rule_s1(cells, grid, pilot=False):
    specs, toks, _ = specs_and_tokenizers(grid, pilot); P = grid["primary"]
    sel = lambda c: c["family"] == P["family"] and c["gamma"] == P["gamma"] and c["colouring"] == P["colouring"] and c["rule"] in P["rules"] and c["h"] in P["h"]
    blk = adequacy_block(cells, grid, sel, float(P["alpha"]), "primary: KGW independent, gamma 0.25, raw and distinct, h >= 1, alpha 0.01")
    k = blk["counts"]; share = k["consistent"] / k["resolved"] if k["resolved"] else float("nan")
    blk.update({"pass": bool(k["resolved"] >= P["min_resolved"] and share >= P["pass_share"]), "consistent_share_of_resolved": share, "min_resolved": P["min_resolved"], "pass_share": P["pass_share"], "band": P["band"],
                "by_h": {str(h): {s: sum(1 for r in blk["rows"] if r["h"] == h and r["status"] == s) for s in ("consistent", "inconsistent", "unresolved", "ineligible")} for h in P["h"]},
                "by_rule": {ru: {s: sum(1 for r in blk["rows"] if r["rule"] == ru and r["status"] == s) for s in ("consistent", "inconsistent", "unresolved", "ineligible")} for ru in P["rules"]},
                "by_tokenizer": {t: {s: sum(1 for r in blk["rows"] if r["tokenizer"] == t and r["status"] == s) for s in ("consistent", "inconsistent", "unresolved", "ineligible")} for t in toks},
                "by_cell": {sp["tag"]: {s: sum(1 for r in blk["rows"] if r["tag"] == sp["tag"] and r["status"] == s) for s in ("consistent", "inconsistent", "unresolved", "ineligible")} for sp in specs},
                "non_consistent_rows": [r for r in blk["rows"] if r["status"] in ("inconsistent", "unresolved")]})
    return blk


def secondary_blocks(cells, grid):
    P = grid["primary"]; g0 = P["gamma"]; out = {}
    out["h0_kgw_indep_g0.25_raw_distinct"] = adequacy_block(cells, grid, lambda c: c["family"] == "kgw" and c["colouring"] == "independent" and c["gamma"] == g0 and c["rule"] in ("raw", "distinct") and c["h"] == 0, 0.01, "h = 0 (the regime Study 1 left unresolved); the simulated-shift ratio is in each row")
    out["first_rule_kgw_indep_g0.25"] = adequacy_block(cells, grid, lambda c: c["family"] == "kgw" and c["colouring"] == "independent" and c["gamma"] == g0 and c["rule"] == "first", 0.01, "the first rule (textGrain)")
    out["gamma0.5_kgw_indep_raw_distinct"] = adequacy_block(cells, grid, lambda c: c["family"] == "kgw" and c["colouring"] == "independent" and c["gamma"] == 0.5 and c["rule"] in ("raw", "distinct"), 0.01, "gamma = 0.5 (Study 1's primary gamma)")
    for a in (0.05, 0.001):
        out[f"alpha{a}_primary_cells"] = adequacy_block(cells, grid, lambda c: c["family"] == "kgw" and c["colouring"] == "independent" and c["gamma"] == g0 and c["rule"] in P["rules"] and c["h"] in P["h"], a, f"the primary cells at alpha = {a}")
    out["fixed_h0_kgw"] = adequacy_block(cells, grid, lambda c: c["family"] == "kgw" and c["colouring"] == "fixed", 0.01, "the fixed-size colouring at h = 0 (exact; one global class)")
    out["gumbel_raw_distinct"] = adequacy_block(cells, grid, lambda c: c["family"] == "gumbel" and c["rule"] in ("raw", "distinct"), 0.01, "the Gumbel-max family (per-text Gamma thresholds; the common-factor predictor with a Gaussian residual is an approximation to an Exp(1) score sum)")
    out["gumbel_first"] = adequacy_block(cells, grid, lambda c: c["family"] == "gumbel" and c["rule"] == "first", 0.01, "Gumbel-max, the first rule")
    return out


def rule_s2(cells, grid):
    """The key-mean audit: KGW independent colouring and the Gumbel family under the DISTINCT rule, every alpha: the two-sided KL bound
    on the key-mean level's deviation from its exact value given the texts (binomial for KGW; exactly alpha for continuous Gumbel scores)."""
    checks = []; flagged = []; sz = 0
    for c in cells:
        if not live(c) or c["rule"] != "distinct" or (c["family"] == "kgw" and c["colouring"] != "independent"):
            continue
        for a in grid["alpha"]:
            lv = c["data"]["levels"][str(a)]; lev = levels_of(c["data"], a)
            ex = lv.get("exact_marginal_if_indep_distinct", lv.get("exact_marginal_if_distinct"))
            if bool(lev.max() == 0.0 and ex == 0.0):                   # the structural zero derived from the counts and the exact mean, never read from a flag (R05 F9)
                sz += 1; continue
            pb = C.kl_chernoff_pbound(float(lev.mean()), float(ex), c["K"])   # recomputed from the counts (the stored value was reconciled with it by the body contract)
            dev_se = (lv["key_mean_level"] - ex) / lv["se_conditional_on_texts"] if lv["se_conditional_on_texts"] > 0 else float("nan")
            rec = {"file": c["file"], "alpha": a, "key_mean": lv["key_mean_level"], "exact": ex, "kl_pbound": pb, "kl_pbound_stored": lv["r2_kl_pbound"], "normal_dev_se": dev_se, "K": c["K"]}
            checks.append(rec)
            if pb < S2_PBOUND:
                flagged.append(rec)
    devs = np.array([r["normal_dev_se"] for r in checks if np.isfinite(r["normal_dev_se"])])
    return {"n_checks": len(checks), "n_flagged": len(flagged), "flagged": flagged, "structural_zeros": sz, "pass": len(flagged) == 0, "pbound_threshold": S2_PBOUND,
            "union_bound_false_audit": len(checks) * S2_PBOUND, "smallest_pbound": float(min([r["kl_pbound"] for r in checks], default=float("nan"))),
            "normal_diagnostic": {"n": int(len(devs)), "sd": float(devs.std(ddof=1)) if len(devs) > 1 else None, "max_abs": float(np.abs(devs).max()) if len(devs) else None, "share_abs_gt3": float(np.mean(np.abs(devs) > 3)) if len(devs) else None},
            "by_family": {f: {"checks": sum(1 for r in checks if r["file"].split("__")[2] == f), "flagged": sum(1 for r in flagged if r["file"].split("__")[2] == f)} for f in ("kgw", "gumbel")}}


def rule_s3(cells, grid):
    """The identity audit: the known-mean variance estimator of the per-key mean score (q_hat for KGW; s_bar for Gumbel) against the
    exact identity at the realised document-averaged weights, gross failure beyond 6 SE + tau; structural zeros; coverage diagnostic."""
    checks = []; gross = []; cover = []; sz = 0
    for c in cells:
        if not live(c):
            continue
        d = c["data"]; blk = d["q_hat"] if c["family"] == "kgw" else d["s_bar"]
        ex = blk["exact_var_own_colouring"]; s0 = blk["var_known_mean"]; se = blk["var_known_mean_se"]; tol = blk["r3_tolerance"]
        rec = {"file": c["file"], "observed": s0, "exact": ex, "se": se, "tol": tol, "structural_zero": blk["structural_zero"], "constancy": blk["observed_sample_constancy"]}
        if blk["structural_zero"]:
            sz += 1; rec["gross"] = bool(s0 > tol)
        else:
            rec["gross"] = bool(abs(s0 - ex) > S3_GROSS_SE * se + tol); rec["dev_se"] = (s0 - ex) / se if se > 0 else None
            lo, hi = blk["var_boot_ci95"]; cover.append(lo <= ex <= hi)
        checks.append(rec)
        if rec["gross"]:
            gross.append(rec)
    return {"n_checks": len(checks), "n_gross": len(gross), "gross": gross, "structural_zeros": sz, "pass": len(gross) == 0, "coverage_nominal95": float(np.mean(cover)) if cover else None,
            "dev_se_sd": float(np.std([r["dev_se"] for r in checks if r.get("dev_se") is not None], ddof=1)) if sum(r.get("dev_se") is not None for r in checks) > 1 else None,
            "dev_se_max_abs": float(max(abs(r["dev_se"]) for r in checks if r.get("dev_se") is not None)) if any(r.get("dev_se") is not None for r in checks) else None,
            "by_colouring": {k: {"checks": sum(1 for r in checks if f"__{k}__" in r["file"]), "gross": sum(1 for r in gross if f"__{k}__" in r["file"])} for k in ("independent", "fixed", "uniform")},
            "fixed_vs_independent_h0": fixed_ratio_table(cells)}


def fixed_ratio_table(cells):
    """At h = 0: the observed fixed/independent variance ratio of q_hat against the exact (V - 1/C_cond)/(V - 1), and the realised
    reduction (1/C_cond - 1)/(V - 1) per rule (descriptive; the Study 1 refuted statement measured on real text)."""
    rows = []; by = {(c["tag"], c["tokenizer"], c["gamma"], c["L"], c["rule"], c["colouring"]): c for c in cells if c["family"] == "kgw" and c["h"] == 0 and live(c)}
    for (tag, tok, g, L, rule, col), c in by.items():
        if col != "fixed":
            continue
        ci = by.get((tag, tok, g, L, rule, "independent"))
        if ci is None:
            continue
        idq = c["data"]["identity_q"]; vf = c["data"]["q_hat"]["var_across_keys"]; vi = ci["data"]["q_hat"]["var_across_keys"]
        rows.append({"tag": tag, "tokenizer": tok, "gamma": g, "L": L, "rule": rule, "V": c["V"], "C_cond": idq["C_cond"], "one_over_C_cond": 1.0 / idq["C_cond"] if idq["C_cond"] > 0 else None, "exact_ratio": idq["exact_ratio_formula"],
                     "reduction": (1.0 / idq["C_cond"] - 1.0) / (c["V"] - 1) if idq["C_cond"] > 0 else None, "observed_ratio": vf / vi if vi > 0 else None, "coverage_share_of_V": c["data"]["coverage"].get("share_of_V_if_h0")})
    return rows


def chain_monotone(seq, se, direction):
    """direction 'nondecreasing': s_{j+1} >= s_j - 2(se_j + se_{j+1}); 'nonincreasing': s_{j+1} <= s_j + 2(se_j + se_{j+1})."""
    viol = []
    for j in range(len(seq) - 1):
        tol = 2 * (se[j] + se[j + 1])
        if direction == "nondecreasing" and seq[j + 1] < seq[j] - tol:
            viol.append(j)
        if direction == "nonincreasing" and seq[j + 1] > seq[j] + tol:
            viol.append(j)
    return viol


def rule_s4(cells, grid, alpha=0.01, pilot=False):
    """H-length on the OBSERVED across-key SD of the level under the raw rule (KGW independent, gamma 0.25, every cell, tokenizer and h):
    non-decreasing in L within the key-bootstrap tolerance; the count of chains holding is the result; descriptive for the other rules
    and for Gumbel."""
    specs, toks, hs = specs_and_tokenizers(grid, pilot); P = grid["primary"]; out = {"decided": [], "descriptive": []}
    for fam, col, g in (("kgw", "independent", P["gamma"]), ("gumbel", "uniform", "na"), ("kgw", "independent", 0.5)):
        for rule in grid["rules"]:
            for sp in specs:
                for tok in toks:
                    for h in hs:
                        ch = [c for c in cells if c["tag"] == sp["tag"] and c["tokenizer"] == tok and c["h"] == h and c["family"] == fam and c["colouring"] == col and c["gamma"] == g and c["rule"] == rule and live(c)]
                        ch.sort(key=lambda c: c["L"])
                        if len(ch) < 2:
                            continue
                        seq = [c["data"]["levels"][str(alpha)]["sd_obs_conditional"] for c in ch]; se = [c["data"]["levels"][str(alpha)]["sd_obs_boot_se"] for c in ch]
                        viol = chain_monotone(seq, se, "nondecreasing")
                        rec = {"tag": sp["tag"], "tokenizer": tok, "family": fam, "gamma": g, "rule": rule, "h": h, "L": [c["L"] for c in ch], "sd_obs": seq, "se": se, "holds": not viol, "violations_at": viol,
                               "rho_bar": [c["data"]["population"]["rho_bar"] for c in ch], "mean_M": [c["data"]["mean_M"] for c in ch]}
                        (out["decided"] if (fam == "kgw" and g == P["gamma"] and rule == "raw") else out["descriptive"]).append(rec)
    dec = out["decided"]; out["n_chains"] = len(dec); out["n_holding"] = sum(r["holds"] for r in dec); out["all_hold"] = all(r["holds"] for r in dec) if dec else None
    out["failing"] = [r for r in dec if not r["holds"]]
    out["descriptive_summary"] = {f"{r['family']}_g{r['gamma']}_{r['rule']}": None for r in out["descriptive"]}
    for key in list(out["descriptive_summary"]):
        rs = [r for r in out["descriptive"] if f"{r['family']}_g{r['gamma']}_{r['rule']}" == key]; out["descriptive_summary"][key] = {"n_chains": len(rs), "n_holding": sum(r["holds"] for r in rs)}
    return out


def rule_s5(cells, grid, alpha=0.01, pilot=False):
    """H-width on the OBSERVED across-key SD of the level at each cell's longest length (KGW independent, gamma 0.25, raw and distinct):
    non-increasing in h within the key-bootstrap tolerance; the count of chains holding is the result; descriptive otherwise."""
    specs, toks, _ = specs_and_tokenizers(grid, pilot); P = grid["primary"]; out = {"decided": [], "descriptive": []}
    for fam, col, g in (("kgw", "independent", P["gamma"]), ("gumbel", "uniform", "na"), ("kgw", "independent", 0.5)):
        for rule in grid["rules"]:
            for sp in specs:
                Lmax = max(sp["L"])
                for tok in toks:
                    ch = [c for c in cells if c["tag"] == sp["tag"] and c["tokenizer"] == tok and c["L"] == Lmax and c["family"] == fam and c["colouring"] == col and c["gamma"] == g and c["rule"] == rule and live(c)]
                    ch.sort(key=lambda c: c["h"])
                    if len(ch) < 2:
                        continue
                    seq = [c["data"]["levels"][str(alpha)]["sd_obs_conditional"] for c in ch]; se = [c["data"]["levels"][str(alpha)]["sd_obs_boot_se"] for c in ch]
                    viol = chain_monotone(seq, se, "nonincreasing")
                    rec = {"tag": sp["tag"], "tokenizer": tok, "family": fam, "gamma": g, "rule": rule, "L": Lmax, "h": [c["h"] for c in ch], "sd_obs": seq, "se": se, "holds": not viol, "violations_at": viol,
                           "A_between": [c["data"]["population"]["A_q_between"] for c in ch], "rho_bar": [c["data"]["population"]["rho_bar"] for c in ch], "mean_M": [c["data"]["mean_M"] for c in ch]}
                    (out["decided"] if (fam == "kgw" and g == P["gamma"] and rule in ("raw", "distinct")) else out["descriptive"]).append(rec)
    dec = out["decided"]; out["n_chains"] = len(dec); out["n_holding"] = sum(r["holds"] for r in dec); out["all_hold"] = all(r["holds"] for r in dec) if dec else None
    out["failing"] = [r for r in dec if not r["holds"]]
    return out


def deployer_block(cells, grid, pilot=False):
    """The deployer's view over the cells the GRID places in the deployer subset (the stored flag was verified equal to this by the body
    contract; the selection never reads the flag; R05 F10)."""
    specs, _, _ = specs_and_tokenizers(grid, pilot); L_of = {sp["tag"]: sp["L"] for sp in specs}
    rows = []
    for c in cells:
        if not live(c) or not in_deployer_subset(c, grid, L_of[c["tag"]]):
            continue
        for a in grid["alpha"]:
            lv = c["data"]["levels"][str(a)]
            rows.append({"tag": c["tag"], "tokenizer": c["tokenizer"], "family": c["family"], "gamma": c["gamma"], "h": c["h"], "L": c["L"], "rule": c["rule"], "alpha": a, "K": c["K"], "N_eff": c["data"]["N_eff"],
                         "key_mean": lv["key_mean_level"], "quantiles": lv["quantiles"], "max_key": lv["max_key"], "share_2alpha": lv["share_keys_above_2alpha"], "share_5alpha": lv["share_keys_above_5alpha"], "crossed": lv.get("deployer_crossed")})
    return rows


def language_disparity(A, langs, meta):
    """Per-key disparity across the language cells (rows of A: languages; columns: keys; levels k/N_eff). Three pre-stated cases per key
    (R05 F3): ALL-ZERO (every language's level is 0: no disparity is observed; counted, never called disparate); SOME-ZERO (a zero level in
    at least one language and a positive one in another: the ratio is undefined; counted separately); ALL-POSITIVE (the largest-to-
    smallest ratio is defined; the shares above 2 and 5 and the median are over these keys only, with that denominator stated).
    Empirical finite-text ratios over the sampled keys; not calibrated population language effects."""
    mx = A.max(axis=0); mn = A.min(axis=0); K = A.shape[1]
    all_zero = mx == 0; some_zero = (mn == 0) & (mx > 0); pos = mn > 0; ratio = mx[pos] / mn[pos]
    return dict(meta, languages=list(langs), K=int(K), n_keys_all_zero=int(all_zero.sum()), n_keys_some_zero=int(some_zero.sum()), n_keys_all_positive=int(pos.sum()),
                share_all_positive_keys_ratio_gt2=float(np.mean(ratio > 2)) if pos.any() else None, share_all_positive_keys_ratio_gt5=float(np.mean(ratio > 5)) if pos.any() else None,
                median_ratio_all_positive_keys=float(np.median(ratio)) if pos.any() else None, max_ratio_all_positive_keys=float(ratio.max()) if pos.any() else None,
                sd_of_pairwise_difference_pp={f"{langs[i]}-{langs[j]}": float(100 * (A[i] - A[j]).std(ddof=1)) for i in range(len(langs)) for j in range(i + 1, len(langs))})


def correlations(cells, grid, alpha=0.01, pilot=False):
    """Across-key correlations of the per-key levels (the same keys in every cell): (a) between corpus cells at L = 256 per (tokenizer,
    family, h, rule); (b) between the two tokenizers for the same texts; (c) the per-key language disparity across the six Wikipedia
    languages at L = 256. Descriptive (H-domain, H-language, the tokenizer axis)."""
    specs, toks, hs = specs_and_tokenizers(grid, pilot); P = grid["primary"]; out = {"between_cells": [], "between_tokenizers": [], "language_disparity": []}
    language_tags = [sp["tag"] for sp in specs if sp.get("source") == "wikipedia" and sp.get("L_cell") == 256]   # the six @256 Wikipedia language cells, explicitly (R05 F3); never wikipedia_en_1024
    def lev(c):
        return levels_of(c["data"], alpha)
    def corr(x, y):
        if x.std() == 0 or y.std() == 0:
            return {"pearson": None, "spearman": None}
        return {"pearson": float(pearsonr(x, y)[0]), "spearman": float(spearmanr(x, y)[0])}
    for fam, col, g in (("kgw", "independent", P["gamma"]), ("gumbel", "uniform", "na")):
        for tok in toks:
            for h in (0, 1, 2):
                for rule in ("raw", "distinct"):
                    cs = {c["tag"]: c for c in cells if c["tokenizer"] == tok and c["family"] == fam and c["colouring"] == col and c["gamma"] == g and c["h"] == h and c["rule"] == rule and c["L"] == 256 and live(c)}
                    tags = sorted(cs)
                    if len(tags) < 2:
                        continue
                    M = {"pearson": [[None] * len(tags) for _ in tags], "spearman": [[None] * len(tags) for _ in tags]}
                    for i, a in enumerate(tags):
                        for j, b in enumerate(tags):
                            r = corr(lev(cs[a]), lev(cs[b])) if i != j else {"pearson": 1.0, "spearman": 1.0}
                            M["pearson"][i][j] = r["pearson"]; M["spearman"][i][j] = r["spearman"]
                    out["between_cells"].append({"tokenizer": tok, "family": fam, "gamma": g, "h": h, "rule": rule, "L": 256, "tags": tags, "pearson": M["pearson"], "spearman": M["spearman"]})
                    wiki = [t for t in tags if t in language_tags]
                    if len(wiki) >= 2:
                        out["language_disparity"].append(language_disparity(np.stack([lev(cs[t]) for t in wiki]), wiki, {"tokenizer": tok, "family": fam, "gamma": g, "h": h, "rule": rule}))
    for sp in specs:
        for fam, col, g in (("kgw", "independent", P["gamma"]), ("gumbel", "uniform", "na")):
            for h in hs:
                for rule in grid["rules"]:
                    for L in sp["L"]:
                        pair = {c["tokenizer"]: c for c in cells if c["tag"] == sp["tag"] and c["family"] == fam and c["colouring"] == col and c["gamma"] == g and c["h"] == h and c["rule"] == rule and c["L"] == L and live(c)}
                        if len(pair) == 2:
                            a, b = pair["llama"], pair["qwen"]; la, lb = lev(a), lev(b)
                            out["between_tokenizers"].append({"tag": sp["tag"], "family": fam, "gamma": g, "h": h, "rule": rule, "L": L, "sd_llama": float(la.std(ddof=1)), "sd_qwen": float(lb.std(ddof=1)),
                                                              "sd_ratio_qwen_over_llama": float(lb.std(ddof=1) / la.std(ddof=1)) if la.std() > 0 else None, "key_mean_llama": float(la.mean()), "key_mean_qwen": float(lb.mean()), **corr(la, lb)})
    return out


def analyze(cells, grid, pilot):
    res = {"study": STUDY, "mode": "PILOT (synthetic validation cells; not study outcomes)" if pilot else "study", "n_cells": len(cells), "n_live": sum(live(c) for c in cells), "n_markers": sum(1 for c in cells if c["degenerate"])}
    res["rules"] = {"S1_adequacy": rule_s1(cells, grid, pilot), "S2_key_mean_audit": rule_s2(cells, grid), "S3_identities": rule_s3(cells, grid), "S4_H_length_raw": rule_s4(cells, grid, pilot=pilot), "S5_H_width": rule_s5(cells, grid, pilot=pilot)}
    res["secondary_adequacy"] = secondary_blocks(cells, grid)
    res["descriptive"] = {"deployer_view": deployer_block(cells, grid, pilot), "correlations": correlations(cells, grid, pilot=pilot), "cell_summaries": [row_for(c, 0.01, "-") for c in cells if live(c)]}
    return res


def main(a):
    grid_path = a[a.index("--grid") + 1]; grid = json.loads(pathlib.Path(grid_path).read_text()); pilot = "--pilot" in a
    cells_dir = a[a.index("--cells") + 1] if "--cells" in a else str(OUT / "cells"); lock = a[a.index("--lock") + 1] if "--lock" in a else None
    out = pathlib.Path(a[a.index("--out") + 1] if "--out" in a else (OUT / "results.json"))
    if pilot and out.resolve().is_relative_to(pathlib.Path(cells_dir).resolve()):
        raise InventoryError("the pilot analysis file must be written outside the cells directory")
    cells = load_inventory(cells_dir, grid, pilot, lock, grid_path)
    res = analyze(cells, grid, pilot); res["lock"] = {"path": lock, "sha256": sha(lock) if lock else None}; res["grid_sha256"] = sha(grid_path); res["cells_dir"] = str(cells_dir)
    out.write_text(json.dumps(res, indent=1, default=float))
    r = res["rules"]; print(f"{res['mode']}: {res['n_cells']} cells ({res['n_live']} live). S1 {r['S1_adequacy']['counts']} pass={r['S1_adequacy']['pass']}; S2 flagged {r['S2_key_mean_audit']['n_flagged']}/{r['S2_key_mean_audit']['n_checks']}; "
          f"S3 gross {r['S3_identities']['n_gross']}/{r['S3_identities']['n_checks']}; S4 {r['S4_H_length_raw']['n_holding']}/{r['S4_H_length_raw']['n_chains']} chains hold; S5 {r['S5_H_width']['n_holding']}/{r['S5_H_width']['n_chains']}. -> {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
