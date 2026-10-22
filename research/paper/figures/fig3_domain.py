#!/usr/bin/env python3
"""F3 — H-domain: the between-cell Pearson correlation of the per-key levels of one key sample (Study 2 Figure 5
re-rendered): three settings, the same K = 1,000 keys in every cell, L = 256, α = 0.01. A correlation of sampled
levels at one threshold, never a transfer result (constraint 24). Source: outputs/study2_v0.1/results.json
(descriptive.correlations.between_cells), checked against the register's English–English and English–other medians.
"""
import sys
from pathlib import Path

import numpy as np
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paperlib as P  # noqa: E402

plt = P.style()
res = P.results("s2"); R2 = P.register("s2")
BC = res["descriptive"]["correlations"]["between_cells"]
SETTINGS = (("llama", 1, "distinct", "(a) Llama-3.2 tokens\nKGW, h = 1, distinct rule"), ("llama", 0, "raw", "(b) Llama-3.2 tokens\nKGW, h = 0, raw rule"), ("qwen", 1, "distinct", "(c) Qwen2.5 tokens\nKGW, h = 1, distinct rule"))
EN = ["news_en_256", "wikipedia_en_256", "stackexchange_en_256", "wikipedia_en_1024", "gutenberg_en_1024"]
OTHER = ["wikipedia_de_256", "wikipedia_ru_256", "wikipedia_ar_256", "wikipedia_zh_256", "wikipedia_ja_256"]
ORDER = EN + OTHER
cmap = LinearSegmentedColormap.from_list("div", [P.DIV_BLUE, P.DIV_MID, P.DIV_RED])

fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.95))
for ax, (tok, h, rule, title) in zip(axes, SETTINGS):
    es = [e for e in BC if e["tokenizer"] == tok and e["family"] == "kgw" and e["h"] == h and e["rule"] == rule and e["L"] == 256]
    assert len(es) == 1, (tok, h, rule, len(es))
    e = es[0]; idx = [e["tags"].index(t) for t in ORDER]; M = np.asarray(e["pearson"], float)[np.ix_(idx, idx)]
    im = ax.imshow(M, cmap=cmap, vmin=-1, vmax=1, aspect="equal")
    for i in range(10):
        for j in range(10):
            if i != j:
                ax.text(j, i, f"{M[i, j]:.2f}".replace("-0.", "−.").replace("0.", "."), ha="center", va="center", fontsize=5.2, color=P.INK if abs(M[i, j]) < 0.6 else P.SURFACE)
    ax.set_xticks(range(10)); ax.set_yticks(range(10)); ax.set_xticklabels([P.CELL_SHORT[t] for t in ORDER], rotation=90, fontsize=6); ax.set_yticklabels([P.CELL_SHORT[t] for t in ORDER] if ax is axes[0] else [], fontsize=6)
    ax.set_title(title, loc="left", fontsize=7.5); ax.grid(False)
    ax.axhline(4.5, color=P.INK2, lw=0.6); ax.axvline(4.5, color=P.INK2, lw=0.6)
    en_en = [M[i, j] for i in range(5) for j in range(i + 1, 5)]; en_ot = [M[i, j] for i in range(5) for j in range(5, 10)]; ot_ot = [M[i, j] for i in range(5, 10) for j in range(i + 1, 10)]
    for grp, vals in (("en_en", en_en), ("en_other", en_ot), ("other_other", ot_ot)):
        nm = f"corr_{tok}_kgw_h{h}_{rule}_{grp}_median"
        if nm in R2:
            P.check(f"F3 {nm}", float(np.median(vals)), R2[nm])
        P.register_value(f"f3_{tok}_h{h}_{rule}_{grp}_median", f"{np.median(vals):.3f}")
cb = fig.colorbar(im, ax=axes, fraction=0.02, pad=0.02); cb.set_label("Pearson correlation of the per-key levels", fontsize=7); cb.ax.tick_params(labelsize=6.5)
P.save(fig, "fig3_domain")
P.flush_values("f3")
P.finish_checks("fig3_domain")
