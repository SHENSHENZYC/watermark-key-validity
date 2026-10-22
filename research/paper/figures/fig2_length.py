#!/usr/bin/env python3
"""F2 — the across-key SD of the level against text length under the three retention rules (Study 1 Figure 2 and
Study 2 Figure 2 re-rendered for the paper).

Panel (a): one synthetic law (i.i.d. Zipf, V = 10,000, s = 1.0) at h = 1 and γ = 0.25, the observed SD (solid) and the
first-order prediction (dashed) under the raw, distinct and first rules; panels (b)–(d): the twenty real-text chains
(ten corpus cells × two tokenizers) at h = 1, KGW γ = 0.25, α = 0.01, one panel per rule, observed solid and predicted
dashed, the four raw-rule chains on which the registered S4 fails at h = 1 marked with crosses. Sources: the locked
analysers' outputs (Study 1 descriptive.level_sd_curves_by_rule; Study 2 descriptive.cell_summaries), checked against
the Study 2 S4 rule rows and the registers.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paperlib as P  # noqa: E402

plt = P.style()
r1, r2 = P.results("s1"), P.results("s2"); R1, R2 = P.register("s1"), P.register("s2")
RULES = ("raw", "distinct", "first"); COL = dict(zip(RULES, P.SLOT[:3]))
LAW, H, G = "zipf_V10000_s1.0", "1", "0.25"

fig = plt.figure(figsize=(6.8, 4.8))
gs = fig.add_gridspec(2, 3, height_ratios=(0.9, 1.0), hspace=0.5, wspace=0.3)
ax0 = fig.add_subplot(gs[0, :])
curves = r1["descriptive"]["level_sd_curves_by_rule"]
for rule in RULES:
    es = [e for e in curves[rule] if e["chain"] == [LAW, H, G, rule]]
    assert len(es) == 1, (rule, len(es))
    e = es[0]; L = np.asarray(e["L"]); obs = np.asarray(e["level_sd_obs_pp"], float); pred = np.asarray(e["level_sd_pred_pp"], float)
    ax0.plot(L, obs, color=COL[rule], marker="o", ms=3.6, lw=1.6, label=f"{rule} rule, observed")
    ax0.plot(L, pred, color=COL[rule], ls="--", lw=1.2, label=f"{rule} rule, predicted")
    growth = e["rho_bar"][-1] / e["rho_bar"][0]
    P.register_value(f"f2_synthetic_{rule}_rho_growth", f"{growth:.1f}"); P.register_value(f"f2_synthetic_{rule}_sd_Lmax_pp", f"{obs[-1]:.2f}")
    if rule == "raw":   # the registered growth range of ρ̄ over the core laws under the raw rule contains this law's growth
        lo, hi = P.num_range(R1["rho_growth_raw_range"]); assert lo - 0.05 <= growth <= hi + 0.05, (growth, R1["rho_growth_raw_range"])
ax0.set_xscale("log", base=2); ax0.set_xticks([64, 128, 256, 512, 1024, 2048]); ax0.set_xticklabels(["64", "128", "256", "512", "1,024", "2,048"])
ax0.set_yscale("log"); P.logfmt(ax0, "y", subs=(1.0, 2.0, 5.0))
ax0.set_title(f"(a) synthetic law: i.i.d. Zipf, V = 10,000, s = 1.0; h = 1, γ = 0.25, α = 0.01; K = {R1['K']} keys, N = {R1['N']} texts", loc="left")
ax0.set_ylabel("across-key SD of the level (pp)"); ax0.set_xlabel("text length L (tokens)")
ax0.legend(ncol=2, loc="upper left")

CS = r2["descriptive"]["cell_summaries"]
S4 = r2["rules"]["S4_H_length_raw"]
fail_h1 = {(f["tag"], f["tokenizer"]) for f in S4["failing"] if f["h"] == 1}
assert len(fail_h1) == 4, fail_h1
decided = {(d["tag"], d["tokenizer"]): d for d in S4["decided"] if d["h"] == 1}   # one S4 row per chain: L and sd_obs are lists over the chain
n_chains = {}
for j, rule in enumerate(RULES):
    ax = fig.add_subplot(gs[1, j])
    for tag in P.CELL_ORDER:
        for tok in ("llama", "qwen"):
            cs = sorted([c for c in CS if c["tag"] == tag and c["tokenizer"] == tok and c["family"] == "kgw" and c["h"] == 1 and c["rule"] == rule
                         and c["colouring"] == "independent" and float(c["gamma"]) == 0.25 and float(c["alpha"]) == 0.01], key=lambda c: c["L"])
            assert len(cs) in (3, 5), (tag, tok, rule, len(cs))
            n_chains[rule] = n_chains.get(rule, 0) + 1
            L = [c["L"] for c in cs]; obs = [100 * c["sd_obs"] for c in cs]; pred = [100 * c["sd_pred"] for c in cs]
            if rule == "raw":   # the S4 rule rows hold the same observed SDs (the same locked analyser): assert equality
                d = decided[(tag, tok)]
                for c in cs:
                    k = list(d["L"]).index(c["L"]); assert abs(d["sd_obs"][k] - c["sd_obs"]) < 1e-12, (tag, tok, c["L"])
            failing = rule == "raw" and (tag, tok) in fail_h1
            ax.plot(L, obs, color=COL[rule], lw=1.0, alpha=0.85, marker="x" if failing else None, ms=5, mew=1.2, zorder=3 if failing else 2)
            ax.plot(L, pred, color=COL[rule], lw=0.8, ls="--", alpha=0.55, zorder=1)
    ax.set_xscale("log", base=2); ax.set_xticks([64, 128, 256, 512, 1024]); ax.set_xticklabels(["64", "128", "256", "512", "1,024"])
    ax.set_yscale("log"); P.logfmt(ax, "y", subs=(1.0, 2.0, 5.0)); ax.set_ylim(0.05, 20)
    ax.set_title(f"({'bcd'[j]}) real text, {rule} rule", loc="left")
    if j == 0:
        ax.set_ylabel("across-key SD of the level (pp)")
    ax.set_xlabel("text length L (tokens)")
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color=COL[rule], lw=1.0, label="observed (20 chains)"), Line2D([], [], color=COL[rule], lw=0.8, ls="--", alpha=0.6, label="predicted")]
    if rule == "raw":
        handles.append(Line2D([], [], color=COL[rule], lw=1.0, marker="x", ms=5, mew=1.2, label="S4 fails at h = 1"))
    ax.legend(handles=handles, loc="lower right", fontsize=6.5)
assert all(v == 20 for v in n_chains.values()), n_chains
P.check("F2 S4 chains", S4["n_chains"], R2["s4_chains"]); P.check("F2 S4 failing", len(S4["failing"]), R2["s4_failing_n"])
P.register_value("f2_n_real_chains_per_rule", 20); P.register_value("f2_n_s4_failing_h1", len(fail_h1)); P.register_value("f2_law_label", "i.i.d. Zipf, V = 10,000, s = 1.0")
P.save(fig, "fig2_length")
P.flush_values("f2")
P.finish_checks("fig2_length")
