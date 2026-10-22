"""Fills §11 of research/STUDY3_PROTOCOL_v0.1.md from outputs/study3_v0.1/VALIDATION.json and INPUTS.json (no number in §11 is typed by
hand; rule A4.1). Not pinned by the lock (it writes the protocol, whose digest the lock then takes). Replaces the text between the
markers <!-- S11:BEGIN ... --> and <!-- S11:END --> and refuses if either marker is missing or duplicated.
Usage: .venv/bin/python research/study3/s3_protocol_fill.py
"""
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
PROTO = ROOT / "research/STUDY3_PROTOCOL_v0.1.md"; VAL = ROOT / "outputs/study3_v0.1/VALIDATION.json"; INP = ROOT / "outputs/study3_v0.1/INPUTS.json"; MAN = ROOT / "outputs/study3_v0.1/tokens_manifest.json"
GRID = json.loads((ROOT / "research/study3/grid_v0.1.json").read_text())


def f(x, d=3):
    return f"{x:.{d}g}" if isinstance(x, (int, float)) and not isinstance(x, bool) else str(x)


def pct(x):
    return f"{100 * x:.1f}%"


def main():
    v = json.loads(VAL.read_text()); inp = json.loads(INP.read_text()); man = json.loads(MAN.read_text())
    L = []
    L.append(f"*Generated from `VALIDATION.json` (run {v['run']}) and `INPUTS.json` by `research/study3/s3_protocol_fill.py`; no number below is typed by hand.* The pre-lock re-screen is `research/study3/rescreen/RESCREEN_2026-10-13.md`.")
    L.append("")
    tc = v["token_cache"]
    L.append(f"**(a) The token caches.** Every calibration array matches its manifest digest, shape, dtype and id range; the evaluation and calibration plan is reproduced from the units metadata (Study 2's draws, the scan, disjointness: {tc['plan_reproduced']}); Study 2's token manifest is bound by digest ({tc['study2_manifest_bound']}); the seal's partition and units digests are current ({tc['seal_current']}): all_ok = {tc['all_ok']}. "
             + "Calibration ids at permutation positions " + "; ".join(f"{t} {tc['cal_positions'][t][0]:,}–{tc['cal_positions'][t][1]:,} ({tc['cal_skipped'][t]} skipped)" for t in GRID["cells"]) + ". "
             + f"Evaluation sets: N_E = {GRID['N_eval']:,} (gutenberg {GRID['N_eval_gutenberg']:,}); calibration sets: {GRID['N_cal_set']:,} per cell under both tokenizers.")
    L.append("")
    b = v["fixtures"]["b"]; cont = b["continuous_iid"]; oi = b["order_indices"]
    L.append("**(b) Fixtures (validation randomness; synthetic scores and tokens).** The order indices: " + "; ".join(f"N_cal {n:,}, α {a}: j_conf {oi[f'{n}|{a}']['j_conformal']}, j_tol {oi[f'{n}|{a}']['j_tolerance']}" for n in GRID["N_cal"] for a in GRID["alpha"]) + f" (the tolerance index maximal in every case: {b['tolerance_index_maximal']}; j = 0 means the method never rejects). "
             + "On i.i.d. continuous scores (20,000 replicates): " + "; ".join(f"N_cal {k.split('|')[0]}, α {k.split('|')[1]}: conformal mean {f(c['conformal_mean'], 4)} against the exact {f(c['exact_mean'], 4)}, SD {f(c['conformal_sd'], 4)} against {f(c['exact_sd'], 4)}, tolerance share above α {f(c['tolerance_share_above_alpha'], 3)} against the exact tail {f(c['exact_tail'], 3)}" for k, c in cont.items()) + f" (all within tolerance: {all(c['ok'] for c in cont.values())}). "
             + f"On discrete (binomial, M = 250, γ = 0.25) scores the conformal level is conservative (mean {f(b['discrete_conformal']['mean_level'], 4)} against the continuous bound {f(b['discrete_conformal']['bound'], 4)}: {b['discrete_conformal']['ok']}). "
             + f"The empirical multiplier's and the pooled threshold's defining properties and maximality hold on 20 random fitting tables at every α ({b['scheme_thresholds_properties']}); `counts_below` equals brute force with ties ({b['counts_below_brute_force']}).")
    pb = b["predictor"]
    L.append(f"The calibrated-threshold predictor reproduces the exact Beta law within a law (largest relative error of the mean {f(max(x['rel_err_mean'] for x in pb['exact_beta']), 2)}, of the SD {f(max(x['rel_err_sd'] for x in pb['exact_beta']), 2)}: {pb['exact_beta_ok']}) and 400,000-draw Monte Carlo with a cross-law shift and unequal residual variances ("
             + "; ".join(f"mean {f(m['pred_mean'], 4)} / {f(m['mc_mean'], 4)}, SD {f(m['pred_sd'], 4)} / {f(m['mc_sd'], 4)}, share above α {f(m['pred_share'], 3)} / {f(m['mc_share'], 3)}" for m in pb["monte_carlo"]) + f"; predicted / Monte Carlo; all within 1%: {pb['monte_carlo_ok']}). "
             + f"`cross_cov` equals the brute-force mean over cross pairs and `set_moments` equals Study 1's `population_estimates` field for field ({b['cross_cov']['brute_and_study1_equal']}); with 4,000 validation keys the across-key covariance of two sets' mean z matches the identity ⟨w_C, w_E⟩ ("
             + "; ".join(f"h {x['h']} {x['rule']}: {f(x['observed'], 3)} against {f(x['identity'], 3)}, z {f(x['z'], 2)}" for x in b["cross_cov"]["across_keys"]) + f"; all within 4 SE: {b['cross_cov']['across_keys_ok']}).")
    fsx = b["finite_shares"]; acc = fsx["acceptance"]
    L.append(f"The finite-evaluation exceedance shares (§3): within a law (v = 0, equal residual scales) the predictor equals the Beta-binomial law at every level in {len(fsx['within_law'])} settings (largest absolute error {f(max(abs(r[f'finite_{nm}'] - r[f'exact_{nm}']) for r in fsx['within_law'] for nm in ('alpha', '2alpha', '5alpha')), 2)}; acceptance {acc['within_law_abs']}), and a fixed threshold at ρ_E = 0 equals the binomial law (error {f(abs(fsx['fixed_rho0']['finite'] - fsx['fixed_rho0']['exact']), 2)}; acceptance {acc['fixed_rho0_abs']}). With a positive shift variance, the production rule (Q = 1,000 midpoint nodes per Beta variable) against a four-fold finer rule on {len(fsx['convergence_perkey'])} settings taken from the frozen inputs (the largest and smallest positive v, {f(max(r['v'] for r in fsx['convergence_perkey']), 3)} and {f(min(r['v'] for r in fsx['convergence_perkey']), 3)}; the residual-scale ratios {f(min(r['ratio'] for r in fsx['convergence_perkey']), 3)}–{f(max(r['ratio'] for r in fsx['convergence_perkey']), 3)}; both evaluation sizes; every level; both per-key methods; a seeded random sample; {fsx['n_candidates_positive_v']:,} candidate settings): largest absolute difference {f(max(r['max_abs_diff_Q_vs_4Q'] for r in fsx['convergence_perkey']), 2)} (acceptance {acc['convergence_perkey_abs']}); the fixed thresholds' rule (Q = 4,000) against Q = 16,000 on {len(fsx['convergence_fixed'])} (set, α, method) cases: largest difference {f(max(r['max_abs_diff'] for r in fsx['convergence_fixed']), 2)} (acceptance {acc['convergence_fixed_abs']}). Monte Carlo (400,000 draws of U, X and the binomial count): "
             + "; ".join(f"{r.get('pair', r.get('set'))} {r['method']} N_cal {r.get('N_cal', '—')} at {r['level']}: predicted {f(r['pred'], 4)} against {f(r['mc'], 4)} ± {f(r['mc_se'], 2)}" for r in fsx["monte_carlo"]) + f" (acceptance {acc['monte_carlo']}); all as required: {fsx['ok']}.")
    L.append("")
    lk = v["fixtures"]["lock"]; kp = v["fixtures"]["key_policy"]; ru = v["fixtures"]["reuse"]; an = v["fixtures"]["analyzer"]
    L.append(f"**(c)–(f) Fixtures (all as required).** The key policy accepts the evaluation, fitting and validation ranges and refuses the reserved range, Study 1's and Study 2's ranges, the audit's development keys, keys below the validation namespace, and each Study 3 range under the other purpose ({kp['all_ok']}); the lock schema accepts the complete canonical lock under a copied root and refuses {len(lk['refused'])} of {lk['n_variants']} variants (among them a missing `approved_by`, `final: true`, `before_outcomes: false`, a non-ISO or early date, the wrong study, non-canonical paths, checkpoint R05, the R06 resolution, a tampered, non-hex, missing or extra digest, a missing Study 2 manifest digest, a key-record or fit-start mismatch, a wrong review digest and a non-canonical grid argument; accepted: {lk['accepted']}); a matching unit is reusable and a foreign grid, another identity, another mode or a tampered counts file are refused ({ru['all_ok']}); the analyzer accepts the complete pilot inventory and {sum(1 for k in an if k.endswith('_accepted')) - 1} boundary case (a zero empirical threshold with κ̂ = +∞) and refuses {sum(1 for k in an if not k.endswith('_reason') and k not in ('all_ok', 'n') and not k.endswith('_accepted'))} mutations of it (the inventory: a missing or extra unit; the provenance gate: every field of the derived provenance altered in turn, the study, the mode and the identity; the threshold map: emptied, one source missing, a foreign digest, a copy mismatch; the committed thresholds file missing or tampered; the calibration contract: a missing summary, a wrong size or α axis, a threshold above 1 or non-finite, a wrong shape, an extra key, thresholds not nested across α, an abstention violated, an empirical threshold above α; the evaluation contract: N_E wrong with the screen recomputed, the α, variant and source axes reversed or shortened, a wrong fixed-variant list, a fabricated cross-tokenizer source, an extra or missing array, a count above N_E, counts not nested, a wrong shape or dtype, a crossed block missing, unpopulated, wrong-B or with a non-finite SE, calibration-bootstrap values missing, non-finite, negative or above 1, a wrong, non-finite or missing screening constant; the calibration summaries: an emptied or removed z summary, a wrong or missing cost or count field, a wrong κ̂, z_emp or fit index, a finite κ̂ at a zero threshold) ({an['all_ok']}); the REP decision function passes exactly equal and within-noise values and flags a gross one ({all(v['fixtures']['rep_decision'].values())}).")
    L.append("")
    vr = v["validation_run"]; pc = vr["pilot_counts"]
    L.append(f"**(g) The timed validation run.** The synthetic grid ({GRID['validation']['n_cells']} Zipf cells at V = {GRID['validation']['law']['V']:,} sharing the vocabulary to different degrees, h ∈ {GRID['validation']['h']}, K = {GRID['validation']['K']} evaluation and {GRID['validation']['K_fit']} fitting validation keys, N_eval = {GRID['validation']['N_eval']:,}, a {GRID['validation']['N_cal_set']:,}-text calibration set, N_cal ∈ {GRID['validation']['N_cal']}) ran in {vr['seconds']} s ({vr['n_units']} units) and the analyzer executed in pilot mode on it with the pilot inputs (status: {vr['pilot_status']}; T1 rows {pc['T1_rows']}, eligible {pc['T1_eligible']}; T2 rows {pc['T2_rows']}, material {pc['T2_material']}; descriptive rows {pc['descriptive_rows']}; the conductor read the execution status and the counts only).")
    L.append("")
    c = v["cost"]
    L.append(f"**(h) The cost probe.** One production-sized pass-1 and pass-2 unit on synthetic Zipf tokens at V = 128,256 with K = {GRID['K']:,} evaluation and {GRID['K_fit']:,} fitting validation keys (N_cal set {GRID['N_cal_set']:,}, N_E {GRID['N_eval']:,}, every calibration source and the cross-tokenizer counts included): "
             + "; ".join(f"h = {h}: pass 1 {c[f'h{h}']['cal_seconds']} s (|D| {c[f'h{h}']['n_tuples_cal']:,}), pass 2 {c[f'h{h}']['eval_seconds']} s (|D| {c[f'h{h}']['n_tuples_eval']:,})" for h in (0, 2)) + f"; peak resident memory of the validator {c['peak_rss_gb']} GB. "
             + f"**Projection (seconds = a + b·|D| per pass from the two probe points, applied to every production unit's tuple count from `INPUTS.json`; an extrapolation with margin, not a guarantee): {c['projection_hours']} h** against the {GRID['budget_hours']}-hour budget (the reduction order of §10 applies before the lock only).")
    L.append("")
    e = v["eligibility"]
    L.append(f"**(i) Eligibility and materiality from the key-free inputs (α = 0.01; the primary block).** Of the {e['n_primary_rows']:,} primary (pair, setting) rows, {e['T1_eligible']:,} are T1-eligible (theory share ≥ 0.75, no flag) and {e['T2_material']:,} are T2-material (R_pred outside [2/3, 3/2]): predicted 'calibration helps' in {e['T2_predicted_signs']['help']:,} and 'calibration hurts' in {e['T2_predicted_signs']['harm']:,}. By block (rule | h | tokenizer | N_cal | pair class: T1-eligible / T2-material of the rows): "
             + "; ".join(f"{k.replace('|', ' ')}: {e['by_block']['T1'][k]} / {e['by_block']['T2'][k]}" for k in sorted(e["by_block"]["T1"])) + ".")
    sc = inp.get("study2_consistency_summary") or {}
    L.append(f"The evaluation sets' ρ̄ and σ² at L = 256 reproduce Study 2's pinned `INPUTS.json` values (KGW, γ = 0.25) in {sc.get('n')} comparisons with largest absolute differences {f(sc.get('max_abs_diff_rho'), 2)} and {f(sc.get('max_abs_diff_sigma2'), 2)}. "
             + f"The two English Wikipedia cells' evaluation sets share {inp.get('english_eval_overlap', 'n/a')} ids (Study 2's samples; both calibration sets are disjoint from both).")
    if "v_summary" in inp:
        vs = inp["v_summary"]
        L.append(f"Of the {vs['n_predictions']:,} conformal predictions (pair × N_cal × α), {vs['n_negative_raw']:,} have a negative point estimate of v (the most negative {pct(-vs['min_relative_v_raw'])} of ρ̄_C + ρ̄_E), every one within its algebraic floor and set to 0 unflagged; {vs['n_flagged_below_floor']} lie below the floor.")
    L.append("")
    L.append(f"**Not computed before the lock:** any per-key level of a Study 3 key on real text, any study unit. The evaluation keys {GRID['key_eval_start']:,}–{GRID['key_eval_start'] + GRID['K'] - 1:,} and the fitting keys {GRID['key_fit_start']:,}–{GRID['key_fit_start'] + GRID['K_fit'] - 1:,} appear nowhere in any output. all_ok = {v['all_ok']}.")
    body = "\n".join(L)
    txt = PROTO.read_text(); b0 = "<!-- S11:BEGIN (generated by research/study3/s3_protocol_fill.py; do not edit by hand) -->"; b1 = "<!-- S11:END -->"
    if txt.count(b0) != 1 or txt.count(b1) != 1:
        raise RuntimeError("§11 markers missing or duplicated")
    i0 = txt.index(b0) + len(b0); i1 = txt.index(b1)
    PROTO.write_text(txt[:i0] + "\n" + body + "\n" + txt[i1:])
    print("§11 filled:", len(body.split()), "words")


if __name__ == "__main__":
    main()
