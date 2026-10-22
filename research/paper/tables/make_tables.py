#!/usr/bin/env python3
"""The paper's six main-text tables, generated from the locked outputs and asserted against the agreed reports.

T1 the four studies, locks and verdicts; T2 the deployer's view in numbers; T3 the predictor by block; T4 the
remedies on the diagonal; T5 transfer by pair class; T6 the power cost (OUTLINE_v0.1.md §6; decision O3). Each
table is written to research/paper/tables/table<N>_<slug>.md with its caption as the first line; every value
that a section quotes is registered under the prefix 't' in paper_values.json; every value that an agreed
report also prints is checked against that report's register (checks.json; the script fails on a mismatch).

Usage:  .venv/bin/python research/paper/tables/make_tables.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import median

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paperlib as P  # noqa: E402

OUT = P.PAPER / "tables"
OUT.mkdir(exist_ok=True)


def write(name: str, caption: str, table: str) -> None:
    (OUT / f"{name}.md").write_text(f"Table — {caption}\n\n{table}", encoding="utf-8")
    print(f"wrote tables/{name}.md")


def med(xs):
    xs = [float(x) for x in xs if x is not None and np.isfinite(float(x))]
    return float(median(xs)) if xs else float("nan")


def rounds(checkpoint: str) -> int:
    folders = [p for p in (P.ROOT / "research" / "reviews").iterdir() if p.name.startswith(checkpoint + "_")]
    assert len(folders) == 1, checkpoint
    return len(list(folders[0].glob("REVIEW_*_r*.md")))


# ============================================================ T1: the four studies, locks and verdicts
r1, r2, r3, r4 = (P.results(s) for s in ("s1", "s2", "s3", "s4"))
g1, g2, g3, g4 = (P.grid(s) for s in ("s1", "s2", "s3", "s4"))
R1, R2, R3, R4 = (P.register(s) for s in ("s1", "s2", "s3", "s4"))

# Study 1
A = r1["rules"]
P.check("T1 s1 R1 consistent", A["R1"]["n_consistent"], R1["r1_consistent"]); P.check("T1 s1 R1 resolved", A["R1"]["n_resolved"], R1["r1_resolved"])
P.check("T1 s1 R1 unresolved", A["R1"]["n_unresolved"], R1["r1_unresolved"]); P.check("T1 s1 R1 eligible", A["R1"]["n_eligible"], R1["r1_eligible"])
P.check("T1 s1 R1 candidates", A["R1"]["n_candidates"], R1["r1_candidates"])
P.check("T1 s1 R2 checks", A["R2"]["n_checks"], R1["r2_checks"]); P.check("T1 s1 R2 flagged", A["R2"]["n_flagged"], R1["r2_flagged"]); P.check("T1 s1 R2 zeros", A["R2"]["n_structural_zero"], R1["r2_zeros"])
P.check("T1 s1 R3 checks", A["R3"]["n_checks"], R1["r3_checks"]); P.check("T1 s1 R3 gross", A["R3"]["n_gross"], R1["r3_gross"])
P.check("T1 s1 R3 max reduction", A["R3"]["max_reduction_V_ge_10000"], R1["red_z10000_h0_Lmax"], scale=100)
P.check("T1 s1 R4 chains", A["R4"]["n_chains"], R1["r4_chains"]); P.check("T1 s1 R4b n", A["R4b_saturation"]["n"], R1["r4b_n"]); P.check("T1 s1 R5 chains", A["R5"]["n_chains"], R1["r5_chains"])
assert A["R1"]["pass"] and A["R2"]["pass"] and A["R3"]["pass"] and A["R4"]["pass"] and A["R4b_saturation"]["reproduced"] and A["R5"]["pass"]
assert A["R3"]["reduction_below_1pct_for_V_ge_10000"] is False
s1_rules = (f"R1 adequacy of the predictor PASS ({A['R1']['n_consistent']} of {A['R1']['n_resolved']} resolved cells consistent, {A['R1']['n_unresolved']} unresolved; {A['R1']['n_eligible']} eligible of {A['R1']['n_candidates']}); "
            f"R2 the simulator's key-mean against the exact binomial PASS ({A['R2']['n_checks']} checks, {A['R2']['n_flagged']} flagged, {A['R2']['n_structural_zero']} structural zeros); "
            f"R3 the identities PASS ({A['R3']['n_checks']:,} checks, {A['R3']['n_gross']} gross failures) with the registered fixed-size statement refuted (largest reduction {100 * A['R3']['max_reduction_V_ge_10000']:.1f}% at V ≥ 10,000); "
            f"R4 H-length on ρ̄ under the raw rule PASS ({int(A['R4']['share_non_decreasing'] * A['R4']['n_chains'])} of {A['R4']['n_chains']} chains); R4b saturation reproduced ({A['R4b_saturation']['n']} cells); "
            f"R5 H-width on Ã(h) PASS ({int(A['R5']['share_non_increasing'] * A['R5']['n_chains'])} of {A['R5']['n_chains']} chains)")
# Study 2
B = r2["rules"]; c = B["S1_adequacy"]["counts"]
P.check("T1 s2 S1 consistent", c["consistent"], R2["s1_consistent"]); P.check("T1 s2 S1 resolved", c["resolved"], R2["s1_resolved"]); P.check("T1 s2 S1 inconsistent", c["inconsistent"], R2["s1_inconsistent"])
P.check("T1 s2 S1 unresolved", c["unresolved"], R2["s1_unresolved"]); P.check("T1 s2 S1 eligible", c["eligible"], R2["s1_eligible"]); P.check("T1 s2 S1 candidate", c["candidate"], R2["s1_candidate"])
P.check("T1 s2 S2 checks", B["S2_key_mean_audit"]["n_checks"], R2["s2_checks"]); P.check("T1 s2 S2 flagged", B["S2_key_mean_audit"]["n_flagged"], R2["s2_flagged"])
P.check("T1 s2 S3 checks", B["S3_identities"]["n_checks"], R2["s3_checks"]); P.check("T1 s2 S3 gross", B["S3_identities"]["n_gross"], R2["s3_gross"])
P.check("T1 s2 S4 chains", B["S4_H_length_raw"]["n_chains"], R2["s4_chains"]); P.check("T1 s2 S4 failing", len(B["S4_H_length_raw"]["failing"]), R2["s4_failing_n"])
P.check("T1 s2 S5 chains", B["S5_H_width"]["n_chains"], R2["s5_chains"]); P.check("T1 s2 S5 holding", B["S5_H_width"]["n_holding"], R2["s5_chains"])
assert B["S1_adequacy"]["pass"] and B["S2_key_mean_audit"]["pass"] and B["S3_identities"]["pass"] and not B["S4_H_length_raw"]["all_hold"] and B["S5_H_width"]["all_hold"]
s2_rules = (f"S1 adequacy on real text PASS ({c['consistent']} of {c['resolved']} resolved cells consistent, {c['inconsistent']} inconsistent, {c['unresolved']} unresolved; {c['eligible']} eligible of {c['candidate']}); "
            f"S2 the hash colouring's key-mean against the ideal colouring PASS ({B['S2_key_mean_audit']['n_checks']:,} checks, {B['S2_key_mean_audit']['n_flagged']} flagged); "
            f"S3 the identities PASS ({B['S3_identities']['n_checks']:,} checks, {B['S3_identities']['n_gross']} gross failures); "
            f"S4 H-length on the observed SD under the raw rule FAIL ({len(B['S4_H_length_raw']['failing'])} of {B['S4_H_length_raw']['n_chains']} chains fail); "
            f"S5 H-width on the observed SD at the longest length PASS ({B['S5_H_width']['n_holding']} of {B['S5_H_width']['n_chains']} chains)")
# Study 3
T1, T2, REP = r3["T1"], r3["T2"], r3["REP"]
t1_inc = sum(1 for x in r3["t1_rows"] if x.get("class_T1") == "inconsistent"); t2_mat = sum(1 for x in r3["t2_rows"] if x.get("material"))
P.check("T1 s3 T1 consistent", T1["n_consistent"], R3["t1_consistent"]); P.check("T1 s3 T1 resolved", T1["n_resolved"], R3["t1_resolved"]); P.check("T1 s3 T1 unresolved", T1["n_unresolved"], R3["t1_unresolved"])
P.check("T1 s3 T1 eligible", T1["n_eligible"], R3["t1_eligible"]); P.check("T1 s3 T1 rows", T1["n_rows"], R3["t1_candidate"]); P.check("T1 s3 T1 inconsistent", t1_inc, R3["t1_inconsistent"])
P.check("T1 s3 T2 agree", T2["n_agree"], R3["t2_agree"]); P.check("T1 s3 T2 resolved", T2["n_resolved"], R3["t2_resolved"]); P.check("T1 s3 T2 unresolved", T2["n_unresolved"], R3["t2_unresolved"]); P.check("T1 s3 T2 material", t2_mat, R3["t2_material"])
P.check("T1 s3 REP checks", REP["n_checks"], R3["rep_checks"]); P.check("T1 s3 REP gross", REP["n_gross"], R3["rep_gross"])
assert T1["pass"] and T2["pass"] and REP["pass"]
s3_rules = (f"T1 adequacy of the calibrated-threshold predictor PASS ({T1['n_consistent']:,} of {T1['n_resolved']:,} resolved rows consistent, {t1_inc} inconsistent, {T1['n_unresolved']} unresolved; {T1['n_eligible']:,} eligible of {T1['n_rows']:,}); "
            f"T2 the predicted sign of calibration's effect on the dispersion PASS ({T2['n_agree']} of {T2['n_resolved']} resolved material rows agree, {T2['n_unresolved']} unresolved; {t2_mat} material); "
            f"REP Study 2's nominal dispersion reproduced with independent keys PASS ({REP['n_checks']} checks, {REP['n_gross']} gross failures)")
# Study 4
W1, W2, W3 = r4["W1"], r4["W2"], r4["W3"]
P.check("T1 s4 W1 consistent", W1["n_consistent"], R4["w1_n_consistent"]); P.check("T1 s4 W1 inconsistent", W1["n_inconsistent"], R4["w1_n_inconsistent"]); P.check("T1 s4 W1 unresolved", W1["n_unresolved"], R4["w1_n_unresolved"])
P.check("T1 s4 W2 agree", W2["n_agree"], R4["w2_n_agree"]); P.check("T1 s4 W2 disagree", W2["n_disagree"], R4["w2_n_disagree"]); P.check("T1 s4 W2 unresolved", W2["n_unresolved"], R4["w2_n_unresolved"])
P.check("T1 s4 W3 consistent", W3["n_consistent"], R4["w3_n_consistent"]); P.check("T1 s4 W3 resolved", W3["n_resolved"], R4["w3_n_resolved"]); P.check("T1 s4 W3 unresolved", W3["n_unresolved"], R4["w3_n_unresolved"])
P.check("T1 s4 W3 eligible", W3["n_eligible"], R4["w3_n_eligible"]); P.check("T1 s4 W3 candidate", W3["n_candidate"], R4["w3_n_candidate"])
assert W1["pass"] and (not W2["pass"]) and W3["pass"]
s4_rules = (f"W1 the threshold-shift prediction of the median per-key cost PASS ({W1['n_consistent']} cells consistent, {W1['n_inconsistent']} inconsistent, {W1['n_unresolved']} unresolved of {W1['n_rows']}); "
            f"W2 the across-key dispersion of power after against before calibration FAIL ({W2['n_agree']} agree, {W2['n_disagree']} disagree, {W2['n_unresolved']} unresolved of {W2['n_rows']} rows); "
            f"W3 the key-free predictor on the model's own null law PASS ({W3['n_consistent']} of {W3['n_resolved']} resolved rows consistent, {W3['n_unresolved']} unresolved; {W3['n_eligible']} eligible of {W3['n_candidate']})")

for s, reg_key in (("s1", "run_hours"), ("s2", "run_hours"), ("s3", "run_hours"), ("s4", "run_hours")):
    P.check(f"T1 {s} run hours", P.manifest(s)["run"]["duration_hours"], P.register(s)[reg_key])
L1, L2, L3, L4 = (P.lock(s) for s in ("s1", "s2", "s3", "s4"))
vals = {}
def lockcell(s, L):
    cp = L["review"]["checkpoint"]; assert cp == P.CHECKPOINT_OF_LOCK[s]
    n = rounds(cp); h = P.manifest(s)["run"]["duration_hours"]
    vals[f"t_lock_{s}_date"], vals[f"t_lock_{s}_checkpoint"], vals[f"t_lock_{s}_rounds"], vals[f"t_run_{s}_hours"] = L["date"], cp, n, h
    return f"{L['date']}, after checkpoint {cp} ({n} rounds); run {h:.2f} h"
laws = g1["laws"]; Vs = sorted({l["V"] for l in laws if l["kind"] == "zipf" and l.get("role") == "core"})
t1_rows = [
    ["1 Theory and simulation", f"{R1['n_core_laws']} core and {R1['n_ill_laws']} illustration synthetic laws (i.i.d. Zipf over V = {Vs[0]:,}–{Vs[-1]:,}, first-order Markov chains, two control laws); K = {R1['K']} keys ({R1['K_fixed']} under the fixed-size colouring on a core subset); N = {R1['N']} texts of up to {max(g1['L']):,} tokens per law",
     f"rules raw, distinct, first; h ∈ {{0, …, 4}}; γ ∈ {{0.5, 0.25}}; α ∈ {{0.01, 0.05, 0.001}}; {int(R1['n_cells']):,} cells ({int(R1['n_live']):,} live)", lockcell("s1", L1), s1_rules],
    ["2 Measurement on real null text", f"{R2['n_corpus']} frozen corpus cells × {R2['n_tok']} tokenizers; K = {R2['K']} keys (seeds {R2['key_start']}–{R2['key_end']}); N = {R2['N']} texts per cell",
     f"KGW γ ∈ {{0.25, 0.5}} and Gumbel-max; rules raw, distinct, first; h ∈ {{0, …, 4}}; L chains 64–256 (64–1,024 for the two 1,024-token cells); α ∈ {{0.01, 0.05, 0.001}}; {int(R2['n_cells']):,} cells", lockcell("s2", L2), s2_rules],
    ["3 Remedies and transfer", f"the same 10 cells × 2 tokenizers; Study 2's evaluation texts (N_E = {R3['N_E']}, Gutenberg {R3['N_E_gutenberg']}) and {R3['N_C']} calibration texts per cell; K = {R3['K']} evaluation keys ({R3['key_eval_range']}) and {R3['K_fit']} fitting keys ({R3['key_fit_range']})",
     f"six methods (nominal, multiplier 1/β at β = {g3['beta']}, empirical multiplier, pooled, per-key conformal and tolerance at δ = {g3['delta']}) at N_cal ∈ {{500, 1,000, 2,000, 5,000}}; rules raw, distinct; h ∈ {{0, 1, 2}}; L = {g3['L']}; every ordered pair of calibration and evaluation cell within a tokenizer and across the two", lockcell("s3", L3), s3_rules],
    ["4 The power side", f"Qwen2.5-1.5B generations: {R4['n_cells']} English prompt cells; K₄ = {R4['K4']} of Study 3's keys × {R4['n_tx']} prompts × {g4['generation']['n_new']} tokens per arm; a null arm of {R4['N0']:,} unwatermarked continuations per cell scored for all {R3['K']} evaluation keys",
     f"three arms (h = 1, δ = 0.5; h = 1, δ = 2.0; h = 2, δ = 0.5); rules raw, distinct; L ∈ {{64, 128, 256}}; every committed threshold of Study 3 (six methods, ten calibration sources, N_cal, α ∈ {{0.01, 0.05, 0.001}}); {R4['n_units']} units", lockcell("s4", L4), s4_rules],
]
write("table1_studies", "The four pre-registered studies: design, grid, lock and every registered rule with its verdict and counts. A failed rule stays failed; the tolerances and the two text/code discrepancies are in Appendix B; the locks, records and review rounds in Appendix E.",
      P.md_table(["Study", "Units, keys and texts", "Grid", "Lock (date; checkpoint agreed before it; run)", "Pre-registered rules and verdicts"], t1_rows))
for k, v in vals.items():
    P.register_value(k, v)

# ============================================================ T2: the deployer's view in numbers (Study 2 Tables 16–17)
DV = r2["descriptive"]["deployer_view"]
def dv(tag, tok, fam, rule, h=1, a=0.01):
    L = P.LMAX[tag]
    xs = [x for x in DV if x["tag"] == tag and x["tokenizer"] == tok and x["family"] == fam and x["h"] == h and x["rule"] == rule and float(x["alpha"]) == a and x["L"] == L and (fam != "kgw" or float(x["gamma"]) == 0.25)]
    assert len(xs) == 1, (tag, tok, fam, rule, len(xs))
    return xs[0]
def q99ci(x):
    lo, hi = x["crossed"]["q0.99"]["ci95"]; return f"{100 * x['quantiles']['0.99']:.2f} [{100 * lo:.2f}, {100 * hi:.2f}]"
t2_rows = []
agg = {("raw", "q0.5"): [], ("raw", "q0.99"): [], ("raw", "max"): [], ("raw", "share2"): [], ("raw", "mean"): [],
       ("distinct", "q0.5"): [], ("distinct", "q0.99"): [], ("distinct", "max"): [], ("distinct", "share2"): [], ("distinct", "mean"): [],
       ("gumbel", "mean"): [], ("gumbel", "q0.99"): [], ("gumbel", "max"): []}
for tag in P.CELL_ORDER:
    for tok in ("llama", "qwen"):
        a_, b_, g_ = dv(tag, tok, "kgw", "raw"), dv(tag, tok, "kgw", "distinct"), dv(tag, tok, "gumbel", "distinct")
        for rule, x in (("raw", a_), ("distinct", b_)):
            agg[(rule, "q0.5")].append(x["quantiles"]["0.5"]); agg[(rule, "q0.99")].append(x["quantiles"]["0.99"]); agg[(rule, "max")].append(x["max_key"]); agg[(rule, "share2")].append(x["share_2alpha"]); agg[(rule, "mean")].append(x["key_mean"])
        agg[("gumbel", "mean")].append(g_["key_mean"]); agg[("gumbel", "q0.99")].append(g_["quantiles"]["0.99"]); agg[("gumbel", "max")].append(g_["max_key"])
        if tok == "llama":
            t2_rows.append([P.CELL_LABEL[tag], f"{100 * a_['key_mean']:.2f}", f"{100 * a_['quantiles']['0.5']:.2f}", q99ci(a_), f"{100 * a_['share_2alpha']:.1f}",
                            f"{100 * b_['key_mean']:.2f}", f"{100 * b_['quantiles']['0.5']:.2f}", q99ci(b_), f"{100 * b_['max_key']:.2f}", f"{100 * b_['share_2alpha']:.1f}", q99ci(g_)])
# the register's ranges are over both tokenizers (Study 2 §5): check them
def chk_range(name, vals_, reg_name, scale=100):
    lo, hi = P.num_range(R2[reg_name]); P.check(f"T2 {name} min", min(vals_) * scale, lo, tol=0.5 * 10 ** (-P.decimals(R2[reg_name].split('–')[0])) + 1e-9); P.check(f"T2 {name} max", max(vals_) * scale, hi, tol=0.5 * 10 ** (-P.decimals(R2[reg_name].split('–')[1])) + 1e-9)
chk_range("raw h1 median key", agg[("raw", "q0.5")], "dep_raw_h1_median_range"); chk_range("raw h1 99% key", agg[("raw", "q0.99")], "dep_raw_h1_q99_range")
chk_range("raw h1 worst key", agg[("raw", "max")], "dep_raw_h1_worst_range"); chk_range("raw h1 share 2α", agg[("raw", "share2")], "dep_raw_h1_share2_range")
for nm, key in (("dep_distinct_h1_median_range", "q0.5"), ("dep_distinct_h1_q99_range", "q0.99"), ("dep_distinct_h1_worst_range", "max"), ("dep_distinct_h1_share2_range", "share2"), ("dep_distinct_h1_keymean_range", "mean"), ("dep_raw_h1_keymean_range", "mean")):
    if nm in R2:
        chk_range(nm, agg[("distinct" if "distinct" in nm else "raw", key)], nm)
for nm, key in (("depg_distinct_h1_keymean_range", "mean"), ("depg_distinct_h1_q99_range", "q0.99"), ("depg_distinct_h1_worst_range", "max")):
    if nm in R2:
        chk_range(nm, agg[("gumbel", key)], nm)
write("table2_deployer", f"What one fixed key faces on real null text: per-key levels at the nominal α = 1% under the Llama-3.2 tokenizer at h = 1 and each cell's longest length (K = {R2['K']} keys on the N = {R2['N']} realised texts of each cell; Gutenberg's window starts at token 1,000). Key-mean, median and 99% key in %, the 99% key with its crossed key-by-document 95% interval; \"worst\" is the worst of the sampled keys, never a population extreme. The Qwen2.5 rows and every quantile's crossed interval are in Table D12a (Gumbel-max in Table D12b).",
      P.md_table(["Corpus cell", "KGW raw: key-mean", "median key", "99% key [crossed 95% CI]", "keys > 2α (%)", "KGW distinct: key-mean", "median key", "99% key [CI]", "worst sampled key", "keys > 2α (%)", "Gumbel-max distinct: 99% key [CI]"], t2_rows))
for rule in ("raw", "distinct"):
    for key, nm in (("q0.5", "median"), ("q0.99", "q99"), ("max", "worst"), ("share2", "share2a"), ("mean", "keymean")):
        v = agg[(rule, key)]; P.register_value(f"t2_kgw_{rule}_h1_{nm}_min", f"{100 * min(v):.1f}"); P.register_value(f"t2_kgw_{rule}_h1_{nm}_max", f"{100 * max(v):.1f}")
for key, nm in (("mean", "keymean"), ("q0.99", "q99"), ("max", "worst")):
    v = agg[("gumbel", key)]; P.register_value(f"t2_gumbel_distinct_h1_{nm}_min", f"{100 * min(v):.1f}"); P.register_value(f"t2_gumbel_distinct_h1_{nm}_max", f"{100 * max(v):.1f}")

# ============================================================ T3: the predictor by block (Studies 1–2)
def block_row(study, label, blk, reg, prefix, has_candidate=True, resolved_key="rows"):
    rows_ = blk.get("rows", [])
    if "counts" in blk:
        cnt = blk["counts"]; cand, elig, res, cons, inc, unres = cnt["candidate"], cnt["eligible"], cnt["resolved"], cnt["consistent"], cnt["inconsistent"], cnt["unresolved"]
    else:
        cand, elig, res, cons, inc, unres = blk["n_candidates"], blk["n_eligible"], blk["n_resolved"], blk["n_consistent"], blk["n_inconsistent"], blk["n_unresolved"]
    stat = [x for x in rows_ if x.get("status") in ("consistent", "inconsistent", "unresolved")]
    ratios_res = [x["ratio"] for x in stat if x["status"] in ("consistent", "inconsistent") and x.get("ratio") is not None]
    ratios_elig = [x["ratio"] for x in stat if x.get("ratio") is not None]
    m_res, m_elig = med(ratios_res), med(ratios_elig)
    # the register's medians (names differ between the studies)
    if prefix is not None:
        for nm, val in ((f"{prefix}_consistent", cons), (f"{prefix}_inconsistent", inc), (f"{prefix}_unresolved", unres), (f"{prefix}_eligible", elig)):
            if nm in reg:
                P.check(f"T3 {study} {label} {nm}", val, reg[nm])
        if f"{prefix}_resolved" in reg:
            P.check(f"T3 {study} {label} resolved", res, reg[f"{prefix}_resolved"])
        if f"{prefix}_ratio_median" in reg and np.isfinite(m_res):
            P.check(f"T3 {study} {label} median ratio", m_res, reg[f"{prefix}_ratio_median"])
        if f"{prefix}_ratio_median_eligible" in reg and np.isfinite(m_elig):
            P.check(f"T3 {study} {label} median ratio eligible", m_elig, reg[f"{prefix}_ratio_median_eligible"])
    return [study, label, f"{cand}", f"{elig}", f"{res}", f"{cons}", f"{inc}", f"{unres}", P.fnum(m_res, 3) if np.isfinite(m_res) else "—", P.fnum(m_elig, 3) if np.isfinite(m_elig) else "—"], (cons, res, m_res)

t3_rows = []
row, _ = block_row("1", "primary: γ = 0.5, raw and distinct, α = 0.01 (R1)", r1["rules"]["R1"], R1, "r1"); t3_rows.append(row)
S1_SEC = [("alpha_0.05", "α = 0.05", "sec_alpha_0.05"), ("alpha_0.001", "α = 0.001", "sec_alpha_0.001"), ("first_rule", "the first rule", "sec_first_rule"),
          ("gamma_extra", "γ = 0.25 (two laws)", "sec_gamma_extra"), ("unit_sigma_predictor", "the unit-variance predictor", "sec_unit_sigma_predictor"),
          ("illustration", "the illustration laws", "sec_illustration"), ("fixed_colouring", "the fixed-size colouring (core subset)", "sec_fixed_colouring")]
for key, label, pre in S1_SEC:
    row, _ = block_row("1", label, r1["rules"]["R1_secondary"][key], R1, pre); t3_rows.append(row)
row, _ = block_row("2", "primary: γ = 0.25, raw and distinct, h ≥ 1, α = 0.01 (S1)", r2["rules"]["S1_adequacy"], R2, "s1"); t3_rows.append(row)
S2_SEC = [("h0_kgw_indep_g0.25_raw_distinct", "h = 0", "sec_h0_kgw_indep_g0.25_raw_distinct"), ("first_rule_kgw_indep_g0.25", "the first rule", "sec_first_rule_kgw_indep_g0.25"),
          ("gamma0.5_kgw_indep_raw_distinct", "γ = 0.5", "sec_gamma0.5_kgw_indep_raw_distinct"), ("alpha0.05_primary_cells", "α = 0.05", "sec_alpha0.05_primary_cells"),
          ("alpha0.001_primary_cells", "α = 0.001", "sec_alpha0.001_primary_cells"), ("fixed_h0_kgw", "the fixed-size colouring at h = 0", "sec_fixed_h0_kgw"),
          ("gumbel_raw_distinct", "Gumbel-max, raw and distinct", "sec_gumbel_raw_distinct"), ("gumbel_first", "Gumbel-max, the first rule", "sec_gumbel_first")]
for key, label, pre in S2_SEC:
    row, _ = block_row("2", label, r2["secondary_adequacy"][key], R2, pre); t3_rows.append(row)
# the builder's unit-variance block of Study 2 (not in the locked analyser): the register only (constraint 29)
t3_rows.append(["2", "the unit-variance predictor (the report builder's block)", R2["sec_unit_candidate"], R2["sec_unit_eligible"], R2["sec_unit_resolved"], R2["sec_unit_consistent"], R2["sec_unit_inconsistent"], R2["sec_unit_unresolved"], R2["sec_unit_ratio_median"], "—"])
write("table3_predictor", "The first-order predictor by block: the registered primary rule of each study (R1, S1) and the descriptive secondary blocks, with the candidate, eligible (theory share ≥ 0.75, mean M ≥ 30), resolved, consistent, inconsistent and unresolved counts and the median observed-to-predicted SD ratio over the resolved and over the eligible cells of each block. A cell is consistent when the ratio's key-bootstrap 95% interval lies inside [2/3, 3/2]; the blocks are not independent replications (one key sample per study) and a median is a description of the block, never a correction factor. Study 2's unit-variance block is the report builder's, not the locked analyser's.",
      P.md_table(["Study", "Block", "Candidate", "Eligible", "Resolved", "Consistent", "Inconsistent", "Unresolved", "Median ratio (resolved)", "Median ratio (eligible)"], t3_rows))
P.register_value("t3_n_rows", len(t3_rows))

# ============================================================ T4: the remedies on the diagonal (Study 3 Table 8)
DR = r3["descriptive_rows"]
METHODS8 = ["nominal", "multiplier20", "empirical", "pooled", "conformal@1000", "conformal@5000", "tolerance@1000", "tolerance@5000"]
def diag_rows(rule, method, h=1, a=0.01):
    cls = "fixed" if method in ("nominal", "multiplier20") else "diagonal"
    xs = [x for x in DR if x["family"] == "kgw" and x["rule"] == rule and x["h"] == h and float(x["alpha"]) == a and x["variant"] == method and x["class"] == cls]
    assert len(xs) == 20, (rule, method, len(xs))
    return xs
PASS1 = r3["pass1"]
Z_ALPHA = 2.3263478740408408
def zcost(rule, method, h=1, a=0.01):
    """The median over the 20 calibration units of the median key's null-side cost z(t) − z_α (Study 3 Table 11)."""
    costs = []
    for name, u in PASS1.items():
        if not name.endswith(f"__h{h}"):
            continue
        s = u["summary"][f"kgw|{rule}"]
        if method == "nominal":
            costs.append(0.0)
        elif method == "multiplier20":
            from scipy.stats import norm
            costs.append(float(norm.isf(a * g3["beta"]) - norm.isf(a)))
        elif method == "empirical":
            costs.append(s["scheme"][str(a)]["z_emp"] - Z_ALPHA)
        elif method == "pooled":
            costs.append(s["scheme"][str(a)]["z_pool"] - Z_ALPHA)
        else:
            z = s["per_key_z"][f"{method}|{a}"]["z"]; costs.append(z["cost_q50"] if z.get("n_positive", 0) > 0 else float("nan"))
    assert len(costs) == 20, (rule, method, len(costs))
    return med(costs)
t4_rows = []
for rule in ("raw", "distinct"):
    for m in METHODS8:
        xs = diag_rows(rule, m)
        km, sd, q99, sh, pf, ppop = (med([x["key_mean"] for x in xs]), med([x["sd"] for x in xs]), med([x["quantiles"]["0.99"] for x in xs]), med([x["share_above_alpha"] for x in xs]),
                                     med([x["pred_share_above_alpha_finite"] for x in xs]), med([x["pred_share_above_alpha_pop"] for x in xs]))
        zc = zcost(rule, m)
        pre = f"rem_h1_{rule}_{m.replace('@', '')}"
        for nm, val, sc in ((f"{pre}_keymean_median", km, 100), (f"{pre}_sd_median", sd, 100), (f"{pre}_q99_median", q99, 100), (f"{pre}_share_alpha_median", sh, 100), (f"{pre}_pred_share_finite_median", pf, 100)):
            if nm in R3:
                P.check(f"T4 {nm}", val, R3[nm], scale=sc)
        zn = f"zc_h1_{rule}_{m.replace('@', '')}_cost_q50_median"
        if zn in R3 and R3[zn] not in ("n/a", "—"):
            P.check(f"T4 {zn}", zc, R3[zn])
        t4_rows.append([rule, P.METHOD_LABEL[m], f"{100 * km:.3f}", f"{100 * sd:.3f}", f"{100 * q99:.2f}", f"{100 * sh:.1f}", f"{100 * pf:.1f}", f"{100 * ppop:.1f}", P.fnum(zc, 2)])
        for nm, val in (("keymean", km), ("sd", sd), ("q99", q99), ("share_alpha", sh), ("pred_share_finite", pf), ("pred_share_pop", ppop)):
            P.register_value(f"t4_{rule}_{m.replace('@', '')}_{nm}", f"{100 * val:.3f}" if nm in ("keymean", "sd") else (f"{100 * val:.2f}" if nm == "q99" else f"{100 * val:.1f}"))
        P.register_value(f"t4_{rule}_{m.replace('@', '')}_zcost", P.fnum(zc, 2))
write("table4_remedies", f"The remedies on the null side when the calibration law is the deployment law (the diagonal): KGW, γ = 0.25, h = 1, α = 0.01; medians over the 20 (tokenizer, cell) units of K = {R3['K']} keys on the N_E = {R3['N_E']} evaluation texts (Gutenberg {R3['N_E_gutenberg']}). The share of keys above α is the finite-evaluation estimand, measured and predicted; the reference law's population share is a model quantity. The multiplier arm is read under Proposition 1's prerequisite only (the distinct rule); the empirical plug-in is not AutoMark's test; the null-side cost is the median key's threshold in z-units above z_α (the scheme-level methods' fitted threshold). The h = 2 rows are in Table D8b; every α and every unit are in the Study 3 report's supplement `tables_remedy_full.md` in the companion repository.",
      P.md_table(["Rule", "Method", "Key-mean (%)", "SD (pp)", "99% key (%)", "Keys > α, measured (%)", "predicted, finite-evaluation (%)", "predicted, population (%)", "Median key's cost (z)"], t4_rows))

# ============================================================ T5: transfer by pair class (Study 3 Tables 9 and 15)
T1R = [x for x in r3["t1_rows"] if x["rule"] == "distinct" and x["h"] == 1 and x["N_cal"] == 5000]
T2R = [x for x in r3["t2_rows"] if x["rule"] == "distinct" and x["h"] == 1 and x["N_cal"] == 5000]
t5_rows = []
for cls in ("diagonal", "near_identical", "within_english", "english_other", "other_other", "cross_tokenizer"):
    xs = [x for x in DR if x["family"] == "kgw" and x["rule"] == "distinct" and x["h"] == 1 and float(x["alpha"]) == 0.01 and x["variant"] == "conformal@5000" and x["class"] == cls]
    assert xs, cls
    km, sd, q99, sh2 = med([x["key_mean"] for x in xs]), med([x["sd"] for x in xs]), med([x["quantiles"]["0.99"] for x in xs]), med([x["share_above_2alpha"] for x in xs])
    ratio_med = med([x["sd"] / x["pred_sd"] for x in xs if x.get("pred_sd") and x["pred_sd"] > 0])   # the builder's ratio column: observed over predicted SD
    pre = f"cls_{cls}_conformal5000_h1_distinct"
    for nm, val, sc in ((f"{pre}_sd_median", sd, 100), (f"{pre}_q99_median", q99, 100), (f"{pre}_ratio_median", ratio_med, 1)):
        if nm in R3:
            P.check(f"T5 {nm}", val, R3[nm], scale=sc)
    if cls != "cross_tokenizer":
        t1c = [x for x in T1R if x["class"] == cls]; t2c = [x for x in T2R if x["class"] == cls]
        cons = sum(1 for x in t1c if x.get("class_T1") == "consistent"); resd = sum(1 for x in t1c if x.get("class_T1") in ("consistent", "inconsistent")); elig = sum(1 for x in t1c if x.get("eligible"))
        agree = sum(1 for x in t2c if x.get("class_T2") == "agree"); mat = sum(1 for x in t2c if x.get("material"))
        t1txt = f"{cons} of {resd} ({elig} eligible)" if elig else "not eligible (the Beta term is of the order of the floor)"
        t2txt = f"{agree} of {mat}" if mat else "no material row"
    else:
        t1txt = f"ratio median {P.fnum(ratio_med, 3)} (the predictor's check in Appendix D)"; t2txt = "—"
    t5_rows.append([P.CLASS_LABEL[cls], f"{len(xs)}", f"{100 * km:.2f}", f"{100 * sd:.2f}", f"{100 * q99:.2f}", f"{100 * sh2:.1f}", P.fnum(ratio_med, 3), t1txt, t2txt])
    for nm, val in (("keymean", f"{100 * km:.2f}"), ("sd", f"{100 * sd:.2f}"), ("q99", f"{100 * q99:.2f}"), ("share2a", f"{100 * sh2:.1f}"), ("ratio", P.fnum(ratio_med, 3)), ("n_pairs", len(xs))):
        P.register_value(f"t5_{cls}_{nm}", val)
# the transfer factors the report quotes (English–other against the diagonal, etc.)
sd_diag = med([x["sd"] for x in DR if x["family"] == "kgw" and x["rule"] == "distinct" and x["h"] == 1 and float(x["alpha"]) == 0.01 and x["variant"] == "conformal@5000" and x["class"] == "diagonal"])
for cls, nm in (("within_english", "transfer_factor_within_english"), ("english_other", "transfer_factor_english_other"), ("other_other", "transfer_factor_other_other")):
    sd_c = med([x["sd"] for x in DR if x["family"] == "kgw" and x["rule"] == "distinct" and x["h"] == 1 and float(x["alpha"]) == 0.01 and x["variant"] == "conformal@5000" and x["class"] == cls])
    P.check(f"T5 {nm}", sd_c / sd_diag, R3[nm]); P.register_value(f"t5_factor_{cls}", f"{sd_c / sd_diag:.1f}")
write("table5_transfer", f"Transfer of a per-key conformal threshold (N_cal = 5,000) across text laws and tokenizers: KGW distinct rule, h = 1, α = 0.01; medians over the ordered (calibration cell, evaluation cell) pairs of each class, each pair over K = {R3['K']} keys on the evaluation cell's N_E texts. The ratio is the observed to the predicted across-key SD (the key-free predictor); T1 counts the pairs whose ratio interval lies inside [2/3, 3/2] among the resolved and eligible pairs of the class at this setting, T2 the material pairs whose observed sign of calibration's effect agrees with the predicted one. A measurement with its own error, not a transfer guarantee; the raw rule and h = 2 by class are in Table D13a, the cross-tokenizer rows in Table D13b, T1 by block in Table D13c, and every ordered pair in the Study 3 report's supplement `tables_pairs_kgw_alpha0.01_full.md` in the companion repository.",
      P.md_table(["Pair class", "Pairs", "Key-mean (%)", "SD (pp)", "99% key (%)", "Keys > 2α (%)", "Median SD ratio, observed / predicted", "T1 consistent of resolved", "T2 agree of material"], t5_rows))

# ============================================================ T6: the power cost (Study 4 Tables 8 and 12)
D4 = r4["descriptive_rows"]
CELLS4 = list(g4["cells"]); PRIM = g4["primary_arm"]; L_PRIM = g4["primary_length"]; A_PRIM = float(g4["primary_alpha"])
def drow(cell, arm, rule, variant, L=L_PRIM, a=A_PRIM):
    src = None if variant in ("nominal", "multiplier20") else cell
    xs = [x for x in D4 if x["cell"] == cell and x["arm"] == arm and x["rule"] == rule and x["L"] == L and float(x["alpha"]) == a and x["variant"] == variant and x["source"] == src]
    assert len(xs) == 1, (cell, arm, rule, variant, len(xs))
    return xs[0]
METHODS6 = ["nominal", "multiplier20", "empirical", "pooled", "conformal@5000", "tolerance@5000"]
REGM = {"multiplier20": "multiplier", "empirical": "empirical", "pooled": "pooled", "conformal@5000": "conformal", "tolerance@5000": "tolerance"}
t6_rows = []
def cellfmt(x):
    return f"{100 * x['power_mean']:.1f}", f"{100 * x['cost_q50']:.1f} [{100 * x['cost_q05']:.1f}, {100 * x['cost_q95']:.1f}]"
for rule in ("raw", "distinct"):
    for m in METHODS6:
        row = [f"h = 1, δ = 0.5", rule, P.METHOD_LABEL[m]]
        for cell in CELLS4:
            x = drow(cell, PRIM, rule, m); pw, cost = cellfmt(x); row += [pw, cost]
            c = cell.split("_")[0]
            if m == "nominal":
                P.check(f"T6 power {c} nominal {rule}", x["power_mean"], R4[f"power_{c}_nominal_raw_pp"], scale=100) if rule == "raw" and f"power_{c}_nominal_raw_pp" in R4 else None
            else:
                nm = f"cost_{c}_{REGM[m]}_{rule}_median_pp"
                if nm in R4:
                    P.check(f"T6 {nm}", x["cost_q50"], R4[nm], scale=100)
                if m == "conformal@5000" and rule == "raw":
                    P.check(f"T6 power {c} conformal raw", x["power_mean"], R4[f"power_{c}_conformal_raw_pp"], scale=100)
                    P.check(f"T6 cost {c} conformal raw q5", x["cost_q05"], R4[f"cost_{c}_conformal_raw_q5_pp"], scale=100); P.check(f"T6 cost {c} conformal raw q95", x["cost_q95"], R4[f"cost_{c}_conformal_raw_q95_pp"], scale=100)
            P.register_value(f"t6_{c}_{rule}_{m.replace('@', '')}_power", pw); P.register_value(f"t6_{c}_{rule}_{m.replace('@', '')}_cost_median", f"{100 * x['cost_q50']:.1f}")
            P.register_value(f"t6_{c}_{rule}_{m.replace('@', '')}_cost_q05", f"{100 * x['cost_q05']:.1f}"); P.register_value(f"t6_{c}_{rule}_{m.replace('@', '')}_cost_q95", f"{100 * x['cost_q95']:.1f}")
        t6_rows.append(row)
# the smallest and largest of the three cells' conformal@5000 cost medians at the primary setting (the abstract's range; each input asserted against the Study 4 register)
for rule in ("raw", "distinct"):
    meds = []
    for cell in CELLS4:
        c = cell.split("_")[0]; v = drow(cell, PRIM, rule, "conformal@5000")["cost_q50"]
        P.check(f"T6 range input {c} conformal {rule}", v, R4[f"cost_{c}_conformal_{rule}_median_pp"], scale=100); meds.append(100 * v)
    lo, hi = f"{min(meds):.1f}", f"{max(meds):.1f}"
    P.register_value(f"t6_cost_conformal5000_{rule}_median_range", lo if lo == hi else f"{lo}–{hi}")
# the strength and design contrasts: conformal@5000 at δ = 2.0 and at h = 2 (raw rule)
for arm, lab in (("kgw_h1_d2.0", "h = 1, δ = 2.0"), ("kgw_h2_d0.5", "h = 2, δ = 0.5")):
    for m in ("nominal", "conformal@5000"):
        row = [lab, "raw", P.METHOD_LABEL[m]]
        for cell in CELLS4:
            x = drow(cell, arm, "raw", m); pw, cost = cellfmt(x); row += [pw, cost]; c = cell.split("_")[0]
            if arm == "kgw_h1_d2.0" and m == "nominal":
                P.check(f"T6 power {c} nominal raw d2", x["power_mean"], R4[f"power_{c}_nominal_raw_d2_pp"], scale=100)
            if arm == "kgw_h2_d0.5" and m == "conformal@5000":
                P.check(f"T6 cost {c} conformal raw h2", x["cost_q50"], R4[f"cost_{c}_conformal_raw_h2_median_pp"], scale=100)
            P.register_value(f"t6_{c}_{arm}_{m.replace('@', '')}_power", pw); P.register_value(f"t6_{c}_{arm}_{m.replace('@', '')}_cost_median", f"{100 * x['cost_q50']:.1f}")
        t6_rows.append(row)
write("table6_power", f"The per-key power cost of each remedy on Qwen2.5-1.5B's KGW generations (γ = 0.25, L = 256, α = 0.01, the diagonal calibration source): the key-mean power (pp) and the median per-key cost against the nominal threshold with its 5th–95th percentiles across keys [pp], over K₄ = {R4['K4']} keys with n = {R4['n_tx']} texts each. Every cost carries its conditions and none ranks the remedies; the multiplier arm is read under Proposition 1's prerequisite only; the per-key shares above α on both null laws are in Figure 6 and Table D7b; priority on pricing per-key calibration and on per-key operating points is Genhatharan 2026's and AutoMark's [@genhatharan2026nominal; @gloaguen2026automark].",
      P.md_table(["Arm", "Rule", "Method", "news: power", "cost, median [5%, 95%]", "Wikipedia: power", "cost, median [5%, 95%]", "Stack Exchange: power", "cost, median [5%, 95%]"], t6_rows))

# ============================================================ G: the design counts the prose quotes in words (R12 F7)
# Every inventory count a section states ("four sources", "five widths", "twenty units") is registered here from the grids and
# locks, never typed; the fill script spells it out with the ``#w`` format. Each is asserted against an independent record.
import math
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fill_paper import words as fill_words  # noqa: E402
locks = {s: P.lock(s) for s in ("s1", "s2", "s3", "s4")}
P.register_value("g_n_studies", len(locks))
P.check("G studies = locks with before_outcomes", sum(1 for L in locks.values() if L["before_outcomes"] and not L["final"]), len(locks))
P.register_value("g_n_widths", len(g2["h"])); P.check("G widths s1 = s2", len(g1["h"]), len(g2["h"]))
P.register_value("g_n_rules", len(g2["rules"])); P.check("G rules s1 = s2", len(g1["rules"]), len(g2["rules"]))
P.register_value("g_n_tokenizers", len(g2["tokenizers"])); P.check("G tokenizers = s2 n_tok", len(g2["tokenizers"]), R2["n_tok"])
n_units = len(g3["cells"]) * len(g3["tokenizers"]); P.register_value("g_n_units", n_units)
assert f"{n_units} (tokenizer, cell) units" in (P.ROOT / "research/STUDY3_REPORT_v0.1.md").read_text(encoding="utf-8"), "the Study 3 report counts its units differently"
P.check("G cells s3 = s2 n_corpus", len(g3["cells"]), R2["n_corpus"])
P.register_value("g_n_english_cells", len(g3["english_cells"])); P.check("G English cells = s2 n_en_cells", len(g3["english_cells"]), R2["n_en_cells"])
P.register_value("g_n_language_cells", len(g3["language_cells"])); P.register_value("g_n_languages", len({c["lang"] for c in g2["cells"]})); P.check("G languages = language cells", len({c["lang"] for c in g2["cells"]}), len(g3["language_cells"]))
P.register_value("g_n_other_language_cells", sum(1 for c in g2["cells"] if c["lang"] != "en")); P.check("G other-language cells = language cells − 1", sum(1 for c in g2["cells"] if c["lang"] != "en"), len(g3["language_cells"]) - 1)
audit_sources = {lab.split("/")[0] for lab in json.loads((P.ROOT / "outputs" / "corpora_audit_v0.3.json").read_text())["cells"]}
P.register_value("g_n_sources", len({c["source"] for c in g2["cells"]})); P.check("G sources = the audit's cell sources", len({c["source"] for c in g2["cells"]}), len(audit_sources))
P.register_value("g_n_methods", len(g3["methods_fixed"]) + len(g3["methods_scheme"]) + len(g3["methods_per_key"]))
P.register_value("g_n_arms", len(g4["arms"])); P.check("G arms = s4 n_arms", len(g4["arms"]), R4["n_arms"])
P.register_value("g_n_s4_strengths", len({a["delta"] for a in g4["arms"]})); P.register_value("g_n_s4_widths", len({a["h"] for a in g4["arms"]}))
P.register_value("g_n_models", 1); assert isinstance(g4["model"], dict) and "repo" in g4["model"]
P.register_value("g_n_control_laws", sum(1 for l in g1["laws"] if l["kind"] in ("twotoken", "support")))
P.check("G core + illustration laws = n_laws", sum(1 for l in g1["laws"] if l["role"] == "core") + sum(1 for l in g1["laws"] if l["role"] == "illustration"), len(g1["laws"]))
P.register_value("g_n_core_laws", sum(1 for l in g1["laws"] if l["role"] == "core")); P.check("G core laws = s1", sum(1 for l in g1["laws"] if l["role"] == "core"), R1["n_core_laws"])
P.register_value("g_n_s3_widths", len(g3["h"]))
# the overlapping S4 groups of Study 2 §5: a group per non-empty registered membership count (h = 4; news; further h = 1)
groups = [k for k in ("s4_fail_h4", "s4_fail_news", "s4_fail_h1_nonnews_n") if P.num(R2[k]) > 0]
P.register_value("g_s2_s4_groups", len(groups))
assert f"{fill_words(len(groups))} overlapping groups" in (P.ROOT / "research/STUDY2_REPORT_v0.1.md").read_text(encoding="utf-8"), "the Study 2 report names the S4 groups differently"
# the band's half-width on the log2 scale that Figure 5 draws
for band in (g2["primary"]["band"], g4["W2"]["band"], g4["W3"]["band"]):
    assert abs(band[0] - 2 / 3) < 1e-12 and band[1] == 1.5, band
P.register_value("g_log2_band_halfwidth", f"{math.log2(1.5):.2f}")
# the predictor's under-prediction in words: the resolved median ratio of the primary block as the nearest named fraction
ratio = P.num(R2["s1_ratio_median"]); excess = ratio - 1.0
fractions = [(1 / 10, "a tenth"), (1 / 6, "a sixth"), (1 / 5, "a fifth"), (1 / 4, "a quarter"), (1 / 3, "a third"), (1 / 2, "a half")]
P.register_value("g_s1_underprediction_words", "about " + min(fractions, key=lambda f: abs(f[0] - excess))[1])
P.register_value("g_s1_underprediction_pct", f"{100 * excess:.0f}")

P.flush_values(("t", "g"))
P.finish_checks("tables")
