#!/usr/bin/env python3
"""F4 — the deployer's view by method on the diagonal (Study 3 Figure 2 re-rendered): per (tokenizer, cell) unit the
median key and the 99% key of the realised level under each method when the calibration law is the deployment law;
KGW γ = 0.25, α = 0.01, h = 1; K = 1,000 keys per unit on the unit's N_E evaluation texts. Source:
outputs/study3_v0.1/results.json (descriptive_rows), checked against the agreed report's register.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paperlib as P  # noqa: E402

plt = P.style()
res = P.results("s3"); R3 = P.register("s3"); g3 = P.grid("s3")
DR = res["descriptive_rows"]
METHODS = ["nominal", "multiplier20", "empirical", "pooled", "conformal@1000", "conformal@5000", "tolerance@1000", "tolerance@5000"]
XLAB = ["nominal", "multiplier 1/β", "empirical multiplier", "pooled", "conformal, N_cal 1,000", "conformal, N_cal 5,000", "tolerance, N_cal 1,000", "tolerance, N_cal 5,000"]
FLOOR = 100.0 / g3["N_eval"]


def units(rule, method):
    cls = "fixed" if method in ("nominal", "multiplier20") else "diagonal"
    xs = [x for x in DR if x["family"] == "kgw" and x["rule"] == rule and x["h"] == 1 and float(x["alpha"]) == 0.01 and x["variant"] == method and x["class"] == cls]
    assert len(xs) == 20, (rule, method, len(xs))
    return xs


fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.7), sharey=True)
rng = np.random.default_rng(20261019)   # a fixed jitter seed: byte-reproducible
for ax, rule in zip(axes, ("raw", "distinct")):
    for i, m in enumerate(METHODS):
        xs = units(rule, m)
        q50 = np.array([max(100 * x["quantiles"]["0.5"], FLOOR) for x in xs]); q99 = np.array([max(100 * x["quantiles"]["0.99"], FLOOR) for x in xs])
        jit = rng.uniform(-0.16, 0.16, size=20)
        ax.scatter(i - 0.08 + jit * 0.6, q50, s=9, color=P.SLOT[0], alpha=0.55, lw=0, zorder=2, label="median key, per unit" if (i == 0 and rule == "raw") else None)
        ax.scatter(i + 0.08 + jit * 0.6, q99, s=9, color=P.SLOT[1], alpha=0.55, lw=0, zorder=2, label="99% key, per unit" if (i == 0 and rule == "raw") else None)
        ax.plot([i - 0.3, i + 0.3], [np.median(q50)] * 2, color=P.SLOT[0], lw=2.2, zorder=3, label="median over the 20 units" if (i == 0 and rule == "raw") else None)
        ax.plot([i - 0.3, i + 0.3], [np.median(q99)] * 2, color=P.SLOT[1], lw=2.2, zorder=3)
        pre = f"rem_h1_{rule}_{m.replace('@', '')}"
        if f"{pre}_median_range" in R3:
            lo, hi = R3[f"{pre}_median_range"].split("–"); P.check(f"F4 {pre} median key min", min(100 * x["quantiles"]["0.5"] for x in xs), lo); P.check(f"F4 {pre} median key max", max(100 * x["quantiles"]["0.5"] for x in xs), hi)
        if f"{pre}_q99_range" in R3:
            lo, hi = R3[f"{pre}_q99_range"].split("–"); P.check(f"F4 {pre} 99% key min", min(100 * x["quantiles"]["0.99"] for x in xs), lo); P.check(f"F4 {pre} 99% key max", max(100 * x["quantiles"]["0.99"] for x in xs), hi)
        if f"{pre}_q99_median" in R3:
            P.check(f"F4 {pre} q99 median", float(np.median([100 * x["quantiles"]["0.99"] for x in xs])), R3[f"{pre}_q99_median"])
        P.register_value(f"f4_{rule}_{m.replace('@', '')}_median_key_median", f"{np.median(q50):.2f}"); P.register_value(f"f4_{rule}_{m.replace('@', '')}_q99_median", f"{np.median(q99):.2f}")
    ax.axhline(1.0, color=P.MUTED, lw=0.9, ls="--", zorder=1, label="nominal α = 1%" if rule == "raw" else None)
    ax.set_yscale("log"); P.logfmt(ax, "y", subs=(1.0, 3.0)); ax.set_ylim(0.03, 30)
    ax.set_xticks(range(len(METHODS))); ax.set_xticklabels(XLAB, fontsize=6.6, rotation=35, ha="right"); ax.grid(axis="x", visible=False)
    ax.set_title(f"{rule} rule", loc="left")
axes[0].set_ylabel("per-key level at α = 1% on the deployment law (%)")
h_, l_ = axes[0].get_legend_handles_labels(); fig.legend(h_, l_, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.06, 1, 1))
P.save(fig, "fig4_remedies")
P.register_value("f4_n_units", 20); P.register_value("f4_K", g3["K"])
P.flush_values("f4")
P.finish_checks("fig4_remedies")
