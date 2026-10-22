#!/usr/bin/env python3
"""F1 — the deployer's view on real null text (Study 2 Figure 4 re-rendered for the paper).

Per corpus cell and tokenizer at h = 1 and the cell's longest length: the spread of the per-key level over the
K = 1,000 sampled keys at α = 1% (the 1–99% and 5–95% bands of the sampled keys, the median key, the worst sampled
key with its crossed key-by-document 95% interval), for KGW γ = 0.25 under the raw and distinct rules and for
Gumbel-max under the distinct rule. Source: outputs/study2_v0.1/results.json (descriptive.deployer_view), the
locked analyser's output; the quantile ranges are checked against the agreed report's register.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paperlib as P  # noqa: E402

plt = P.style()
res = P.results("s2"); R2 = P.register("s2"); g2 = P.grid("s2")
DV = res["descriptive"]["deployer_view"]
K, N = g2["K"], g2["N"]
TOKS = ("llama", "qwen"); COL = {"llama": P.SLOT[0], "qwen": P.SLOT[1]}; MK = {"llama": "o", "qwen": "s"}
FLOOR = 100.0 / N
PANELS_MAIN = (("kgw", "raw", "KGW, γ = 0.25, raw rule"), ("kgw", "distinct", "KGW, γ = 0.25, distinct rule"))
PANELS_APP = (("gumbel", "distinct", "Gumbel-max, distinct rule"),)   # Appendix D figure (decision O5, 2026-10-19)


def entry(tag, tok, fam, rule):
    xs = [x for x in DV if x["tag"] == tag and x["tokenizer"] == tok and x["family"] == fam and x["h"] == 1 and x["rule"] == rule
          and float(x["alpha"]) == 0.01 and x["L"] == P.LMAX[tag] and (fam != "kgw" or float(x["gamma"]) == 0.25)]
    assert len(xs) == 1, (tag, tok, fam, rule, len(xs))
    return xs[0]


agg = {}


def draw(panels, name, height):
  fig, axes = plt.subplots(len(panels), 1, figsize=(6.8, height), sharex=True, squeeze=False); axes = axes[:, 0]
  for ax, (fam, rule, title) in zip(axes, panels):
      for i, tag in enumerate(P.CELL_ORDER):
          for tok in TOKS:
              r = entry(tag, tok, fam, rule); q = {k: max(100 * v, FLOOR) for k, v in r["quantiles"].items()}; mx = max(100 * r["max_key"], FLOOR)
              agg.setdefault((fam, rule, "q0.99"), []).append(r["quantiles"]["0.99"]); agg.setdefault((fam, rule, "max"), []).append(r["max_key"]); agg.setdefault((fam, rule, "q0.5"), []).append(r["quantiles"]["0.5"])
              x = i + (-0.19 if tok == "llama" else 0.19); c = COL[tok]
              first = (i == 0 and ax is axes[0] and name == "fig1_deployer")
              ax.plot([x, x], [q["0.01"], q["0.99"]], color=c, lw=1.4, alpha=0.55, solid_capstyle="butt", zorder=2, label="1%–99% of the sampled keys" if (first and tok == "llama") else None)
              ax.plot([x, x], [q["0.05"], q["0.95"]], color=c, lw=4.2, alpha=0.9, solid_capstyle="butt", zorder=3, label="5%–95% of the sampled keys" if (first and tok == "llama") else None)
              ax.scatter([x], [q["0.5"]], facecolor=P.SURFACE, edgecolor=P.INK, s=20, lw=0.8, zorder=5, marker=MK[tok], label=f"median key, {P.TOK_LABEL[tok]}" if first else None)
              lo, hi = [max(100 * v, FLOOR) for v in r["crossed"]["max"]["ci95"]]
              ax.plot([x, x], [lo, hi], color=P.INK, lw=0.7, zorder=4, label="crossed 95% CI of the worst key" if (first and tok == "llama") else None)
              ax.scatter([x], [mx], color=P.INK, s=12, zorder=6, marker=MK[tok], label=f"worst sampled key, {P.TOK_LABEL[tok]}" if first else None)
      ax.axhline(1.0, color=P.MUTED, lw=0.9, ls="--", zorder=1, label="nominal α = 1%" if (ax is axes[0] and name == "fig1_deployer") else None)
      ax.set_yscale("log"); P.logfmt(ax, "y", subs=(1.0, 3.0)); ax.set_ylim(0.15, 120)
      ax.set_title(title, loc="left"); ax.set_ylabel("per-key level at α = 1% (%)")
      ax.grid(axis="x", visible=False)
  axes[-1].set_xticks(range(len(P.CELL_ORDER))); axes[-1].set_xticklabels([P.CELL_LABEL[t] for t in P.CELL_ORDER], rotation=30, ha="right")
  axes[-1].set_xlabel(f"corpus cell (K = {K:,} keys on the N = {N:,} realised texts of each cell; Llama-3.2 left, Qwen2.5 right)")
  if name == "fig1_deployer":
      h_, l_ = axes[0].get_legend_handles_labels(); fig.legend(h_, l_, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.01))
      fig.tight_layout(rect=(0, 0.05, 1, 1))
  else:
      fig.tight_layout()
  P.save(fig, name)


draw(PANELS_MAIN, "fig1_deployer", 5.4)
draw(PANELS_APP, "figD6_deployer_gumbel", 3.4)

# checks against the register (the ranges in Study 2 §5 are over both tokenizers at h = 1)
for (fam, rule, key), nm in ((("kgw", "raw", "q0.99"), "dep_raw_h1_q99_range"), (("kgw", "raw", "max"), "dep_raw_h1_worst_range"), (("kgw", "raw", "q0.5"), "dep_raw_h1_median_range"),
                             (("kgw", "distinct", "q0.99"), "dep_distinct_h1_q99_range"), (("kgw", "distinct", "max"), "dep_distinct_h1_worst_range"), (("kgw", "distinct", "q0.5"), "dep_distinct_h1_median_range"),
                             (("gumbel", "distinct", "q0.99"), "depg_distinct_h1_q99_range"), (("gumbel", "distinct", "max"), "depg_distinct_h1_worst_range")):
    if nm in R2:
        lo, hi = R2[nm].split("–"); v = agg[(fam, rule, key)]
        P.check(f"F1 {nm} min", 100 * min(v), lo); P.check(f"F1 {nm} max", 100 * max(v), hi)
    P.register_value(f"f1_{fam}_{rule}_{key.replace('.', '')}_min", f"{100 * min(agg[(fam, rule, key)]):.1f}"); P.register_value(f"f1_{fam}_{rule}_{key.replace('.', '')}_max", f"{100 * max(agg[(fam, rule, key)]):.1f}")
P.register_value("f1_K", K); P.register_value("f1_N", N)
P.flush_values("f1")
P.finish_checks("fig1_deployer")
