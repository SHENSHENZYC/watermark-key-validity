#!/usr/bin/env python3
"""F5 — transfer of a per-key conformal threshold across text laws (Study 3 Figure 3 re-rendered): a threshold set on
one cell's 5,000 calibration texts and applied to every cell's evaluation texts under the Llama-3.2 tokenizer (KGW
distinct rule, h = 1, α = 0.01, K = 1,000 keys per pair): (a) the observed across-key SD of the level, (b) the key-free
predictor's SD, (c) their ratio on a log₂ scale, (d) the observed share of keys above α. Rows are the calibration cell,
columns the evaluation cell. Source: outputs/study3_v0.1/results.json (descriptive_rows and t1_rows), the pairs'
observed SDs cross-checked between the two blocks.
"""
import sys
from pathlib import Path

import numpy as np
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paperlib as P  # noqa: E402

plt = P.style()
res = P.results("s3"); R3 = P.register("s3")
DR = res["descriptive_rows"]; T1 = res["t1_rows"]
ORDER = P.CELL_ORDER
TOK, RULE, H, A, V = "llama", "distinct", 1, 0.01, "conformal@5000"
pairs = {}
for x in DR:
    if x["family"] == "kgw" and x["rule"] == RULE and x["h"] == H and float(x["alpha"]) == A and x["variant"] == V and x["tokE"] == TOK and x["tokC"] == TOK and x["class"] != "cross_tokenizer":
        key = (x["tagC"], x["tagE"]); assert key not in pairs, key; pairs[key] = x
assert len(pairs) == 100, len(pairs)
t1 = {(x["tagC"], x["tagE"]): x for x in T1 if x["tok"] == TOK and x["rule"] == RULE and x["h"] == H and x["N_cal"] == 5000}
assert len(t1) == 100
for key, x in pairs.items():
    assert abs(t1[key]["sd_obs"] - x["sd"]) < 1e-12 and abs(t1[key]["sd_pred"] - x["pred_sd"]) < 1e-9, key   # the two blocks of the locked output agree
M_sd = np.array([[100 * pairs[(c, e)]["sd"] for e in ORDER] for c in ORDER]); M_pred = np.array([[100 * pairs[(c, e)]["pred_sd"] for e in ORDER] for c in ORDER])
M_ratio = np.log2(M_sd / M_pred); M_share = np.array([[100 * pairs[(c, e)]["share_above_alpha"] for e in ORDER] for c in ORDER])
seq = ListedColormap(P.SEQ_BLUE); div = LinearSegmentedColormap.from_list("div", [P.DIV_BLUE, P.DIV_MID, P.DIV_RED])

vmax_sd = max(M_sd.max(), M_pred.max())
MAIN = ((M_sd, "(a) observed across-key SD of the transferred level (pp)", seq, (0, vmax_sd)), (M_ratio, "(b) log₂ of observed / predicted (the band [2/3, 3/2] is ±0.58)", div, (-1, 1)))
APP = ((M_pred, "(a) predicted SD, the key-free predictor (pp)", seq, (0, vmax_sd)), (M_share, "(b) observed share of keys above α (%)", seq, (0, None)))   # Appendix D figure (decision O5, 2026-10-19)


def draw(panels, name):
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.5))
    for ax, (M, title, cm, (vmin, vmax)) in zip(axes.flat, panels):
        im = ax.imshow(M, cmap=cm, vmin=vmin, vmax=vmax, aspect="equal")
        for i in range(10):
            ax.add_patch(plt.Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=P.INK, lw=0.8))
        ax.set_xticks(range(10)); ax.set_yticks(range(10)); ax.set_xticklabels([P.CELL_SHORT[t] for t in ORDER], rotation=90, fontsize=6); ax.set_yticklabels([P.CELL_SHORT[t] for t in ORDER], fontsize=6)
        ax.set_title(title, loc="left", fontsize=7.5); ax.grid(False)
        ax.set_xlabel("evaluation cell", fontsize=7); ax.set_ylabel("calibration cell", fontsize=7)
        cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02); cb.ax.tick_params(labelsize=6.5)
    fig.tight_layout()
    P.save(fig, name)


draw(MAIN, "fig5_transfer")
draw(APP, "figD7_transfer_pred_share")

# the medians over the Llama pairs by class, registered; the T1 classes of these 100 pairs
by_class = {}
for key, x in pairs.items():
    by_class.setdefault(x["class"], []).append(x)
for cls, xs in by_class.items():
    P.register_value(f"f5_{cls}_n", len(xs)); P.register_value(f"f5_{cls}_sd_median", f"{100 * np.median([x['sd'] for x in xs]):.2f}")
    P.register_value(f"f5_{cls}_share_alpha_median", f"{100 * np.median([x['share_above_alpha'] for x in xs]):.1f}")
inside = sum(1 for key in pairs if abs(M_ratio[ORDER.index(key[0]), ORDER.index(key[1])]) <= np.log2(1.5))
cls_counts = {}
for key in pairs:
    cls_counts[t1[key].get("class_T1", "ineligible")] = cls_counts.get(t1[key].get("class_T1", "ineligible"), 0) + 1
P.register_value("f5_n_pairs", 100); P.register_value("f5_n_point_ratio_inside_band", inside)
for k, v in cls_counts.items():
    P.register_value(f"f5_t1_{k}", v)
diag_sd = np.median([pairs[(c, c)]["sd"] for c in ORDER]); eo = [pairs[(c, e)]["sd"] for (c, e) in pairs if pairs[(c, e)]["class"] == "english_other"]
P.register_value("f5_llama_english_other_over_diagonal", f"{np.median(eo) / diag_sd:.1f}")
P.flush_values("f5")
P.finish_checks("fig5_transfer")
