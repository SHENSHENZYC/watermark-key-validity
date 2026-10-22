#!/usr/bin/env python3
"""F6 — the per-key operating points on both null laws (Study 4 Figure 4 re-rendered): each power key's stored corpus
null level (Study 3's evaluation unit, N_E = 10,000 texts; top row) and its model-null level (N₀ = 5,000 unwatermarked
generations; bottom row) against its realised power over n = 50 texts, per method, at the primary setting
(Qwen2.5-1.5B, KGW γ = 0.25, h = 1, δ = 0.5, L = 256, α = 0.01, raw rule, the diagonal calibration source). The two
headline methods are coloured (nominal; per-key conformal at N_cal = 5,000); the four other methods share the muted
ink with distinct markers (the series cap of the dataviz method for all-pairs scatter). Sources: the locked Study 4
analysis arrays (results_arrays.npz, verified by digest) and Study 3's verified record through s4_record; the shares
and correlations are checked against the agreed report's register.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paperlib as P  # noqa: E402

sys.path.insert(0, str(P.ROOT / "research" / "study4"))
import s4_record  # noqa: E402  (the pinned record binding of Study 4; read-only use)

plt = P.style()
res = P.results("s4"); R4 = P.register("s4"); g4 = P.grid("s4")
arr_path = P.ROOT / P.STUDY_DIR["s4"] / "results_arrays.npz"
assert P.sha256(arr_path) == res["arrays_sha256"], "results_arrays.npz differs from the digest recorded in results.json"
Z = np.load(arr_path)
AX = res["axes"]; RULES, LENGTHS, SOURCES, VARIANTS = AX["rules"], AX["lengths"], AX["sources"], AX["variants"]; ALPHAS = [float(a) for a in AX["alphas"]]; VS3, VFIX = AX["null_variants"], AX["null_fixed_variants"]
CELLS = list(g4["cells"]); PRIM = g4["primary_arm"]; L_PRIM = g4["primary_length"]; A_PRIM = float(g4["primary_alpha"]); N_TX = g4["prompts"]["n_watermarked"]; N0 = g4["null_arm"]["n_texts"]
H = next(a["h"] for a in g4["arms"] if a["name"] == PRIM); TOK = g4["model"]["tokenizer"]
METHODS = ["nominal", "multiplier20", "empirical", "pooled", "conformal@5000", "tolerance@5000"]
STYLE = {"nominal": (P.SLOT[0], "o", "nominal"), "conformal@5000": (P.SLOT[1], "s", "per-key conformal, N_cal 5,000"), "multiplier20": (P.MUTED, "^", "multiplier 1/β"),
         "empirical": (P.MUTED, "v", "empirical multiplier"), "pooled": (P.MUTED, "D", "pooled"), "tolerance@5000": (P.MUTED, "P", "per-key tolerance, N_cal 5,000")}
REGM = {"nominal": "nominal", "multiplier20": "multiplier", "empirical": "empirical", "pooled": "pooled", "conformal@5000": "conformal", "tolerance@5000": "tolerance"}
Rrec = s4_record.Record()   # verifies Study 3's 240 record files by digest

OP = {}
for cell in CELLS:
    k = f"{cell}|{PRIM}"; keys = [int(x) for x in Z[f"keys|{k}"]]; ok = Z[f"contract_ok|{k}"].astype(bool); counts = Z[f"counts|{k}"].astype(np.int64)
    assert keys == list(g4["keys"]["power_keys"]) and ok.all(), cell
    ev = Rrec.eval(TOK, cell, H); isrc = SOURCES.index(cell); ir = RULES.index("raw"); il = LENGTHS.index(L_PRIM); ia = ALPHAS.index(A_PRIM); idx = [kk - Rrec.key_eval_start for kk in keys]
    for v in METHODS:
        m, _, nc = v.partition("@"); iv = VARIANTS.index(v)
        pi = counts[:, ir, il, isrc, iv, ia] / N_TX
        l3 = ev.null_level("kgw", "raw", m, A_PRIM, int(nc) if nc else None, cal_source=cell)[idx]
        if v in VFIX:
            l0 = Z[f"null|{cell}|h{H}|kgw|raw|L{L_PRIM}|fixed"][VFIX.index(v), ia].astype(np.float64)[idx] / N0
        else:
            l0 = Z[f"null|{cell}|h{H}|kgw|raw|L{L_PRIM}|same"][isrc, VS3.index(v), ia].astype(np.float64)[idx] / N0
        OP[(cell, v)] = (pi, l3, l0)
        c = cell.split("_")[0]; tag = REGM[v]
        P.check(f"F6 {c} {v} share above α (corpus)", 100 * (l3 > A_PRIM).mean(), R4[f"op_{c}_{tag}_share_above_alpha_pct"])
        if f"op_{c}_{tag}_share_above_alpha_modelnull_pct" in R4:
            P.check(f"F6 {c} {v} share above α (model null)", 100 * (l0 > A_PRIM).mean(), R4[f"op_{c}_{tag}_share_above_alpha_modelnull_pct"])
        if f"op_{c}_{tag}_corr" in R4 and R4[f"op_{c}_{tag}_corr"] != "—":
            P.check(f"F6 {c} {v} corr", float(np.corrcoef(l3, pi)[0, 1]), R4[f"op_{c}_{tag}_corr"])
        P.register_value(f"f6_{c}_{tag}_share_corpus_pct", f"{100 * (l3 > A_PRIM).mean():.0f}"); P.register_value(f"f6_{c}_{tag}_share_modelnull_pct", f"{100 * (l0 > A_PRIM).mean():.0f}")
        P.register_value(f"f6_{c}_{tag}_power_mean_pp", f"{100 * pi.mean():.1f}")

fig, axes = plt.subplots(2, len(CELLS), figsize=(6.8, 4.0), sharey=True)
for j, cell in enumerate(CELLS):
    for i, (ylab_key, xlab) in enumerate(((1, "stored corpus null level of the key, Study 3 (pp)"), (2, "model-null level of the key on unwatermarked generations (pp)"))):
        ax = axes[i, j]
        for v in METHODS:
            col, mk, lab = STYLE[v]; pi, l3, l0 = OP[(cell, v)]; x = l3 if ylab_key == 1 else l0
            ax.scatter(100 * x, 100 * pi, s=11, color=col, marker=mk, alpha=0.85 if col != P.MUTED else 0.6, lw=0, label=lab if (i == 0 and j == 0) else None, zorder=3 if col != P.MUTED else 2)
        ax.axvline(100 * A_PRIM, color=P.INK2, lw=0.8, ls="--", zorder=1, label="α = 1%" if (i == 0 and j == 0) else None)
        if i == 0:
            ax.set_title(P.CELL_LABEL[cell], loc="left")
        if j == 1:
            ax.set_xlabel(xlab)
        if j == 0:
            ax.set_ylabel("realised power of the key (pp)")
        ax.set_xlim(left=-0.3)
h_, l_ = axes[0, 0].get_legend_handles_labels(); fig.legend(h_, l_, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.01))
fig.tight_layout(rect=(0, 0.07, 1, 1))
P.save(fig, "fig6_operating_points")
P.register_value("f6_K4", len(g4["keys"]["power_keys"])); P.register_value("f6_n_tx", N_TX); P.register_value("f6_N0", N0)
P.flush_values("f6")
P.finish_checks("fig6_operating_points")
