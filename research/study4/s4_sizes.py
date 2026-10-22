"""Design arithmetic for D14 (sizes): prices candidate Study 4 designs in generation hours at the pilot's measured rates (read from the
latest pilot summary; never typed) and states the nominal precision of the main estimands. Not pinned; a planning aid for the decision."""
import glob, json, pathlib, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[2]
L_GEN = 256


def rates(summary):
    """Median tok/s per (generation mode, h) over the pilot's settings (KGW pooled over delta); 'none' has no width."""
    r = {}
    for c in summary["configs"]:
        r.setdefault((c["mode"], c["h"] if c["mode"] != "none" else None), []).append(c["tok_per_s"])
    return {m: float(np.median(v)) for m, v in r.items()}


def price(option, rates):
    """option: dict(name, cells, K4, n, runs=[(mode, h, delta)], n0 (null texts per cell)). Returns texts, tokens, hours."""
    n_cells = len(option["cells"]); n_wm = n_cells * option["K4"] * option["n"] * len(option["runs"]); n_null = n_cells * option["n0"]
    hours = sum(n_cells * option["K4"] * option["n"] * L_GEN / rates[(m, h)] for (m, h, d) in option["runs"]) / 3600 + n_null * L_GEN / rates[("none", None)] / 3600
    return {"texts_watermarked": n_wm, "texts_null": n_null, "tokens_M": round((n_wm + n_null) * L_GEN / 1e6, 2), "hours": round(hours, 1)}


def precision(K4, n, p=0.7, sd_between=0.05):
    """Nominal figures: the per-key binomial SE at power p; the SE of a key-mean (independent keys); the relative SE of a between-key SD
    estimated by the known-noise form (observed variance minus the mean binomial variance) when the true between-key SD is sd_between."""
    se_key = np.sqrt(p * (1 - p) / n); se_mean = np.sqrt(sd_between ** 2 + p * (1 - p) / n) / np.sqrt(K4)
    var_obs = sd_between ** 2 + p * (1 - p) / n; rel_se_var = np.sqrt(2.0 / (K4 - 1)) * var_obs / sd_between ** 2   # normal-theory, noise-inflated
    return {"se_per_key_power": round(float(se_key), 3), "se_key_mean_power": round(float(se_mean), 4), "rel_se_between_key_sd": round(float(rel_se_var / 2), 3)}


OPTIONS = [
    {"name": "M- (lean, within D12's scope): 3 English cells; 60 keys x 50 prompts; KGW h = 1 at delta 0.5 and 2.0, h = 2 at 0.5; 5,000 null texts per cell", "cells": ["news_en_256", "wikipedia_en_256", "stackexchange_en_256"], "K4": 60, "n": 50, "runs": [("kgw", 1, 0.5), ("kgw", 1, 2.0), ("kgw", 2, 0.5)], "n0": 5000},
    {"name": "M (recommended): 3 English cells; 100 keys x 50 prompts; KGW h = 1 at delta 0.5 and 2.0, h = 2 at 0.5; 5,000 null texts per cell", "cells": ["news_en_256", "wikipedia_en_256", "stackexchange_en_256"], "K4": 100, "n": 50, "runs": [("kgw", 1, 0.5), ("kgw", 1, 2.0), ("kgw", 2, 0.5)], "n0": 5000},
    {"name": "M+ : M with 100 prompts per key (the per-key binomial variance halved)", "cells": ["news_en_256", "wikipedia_en_256", "stackexchange_en_256"], "K4": 100, "n": 100, "runs": [("kgw", 1, 0.5), ("kgw", 1, 2.0), ("kgw", 2, 0.5)], "n0": 5000},
    {"name": "L (large): M+ with 200 keys and the Chinese Wikipedia cell added", "cells": ["news_en_256", "wikipedia_en_256", "stackexchange_en_256", "wikipedia_zh_256"], "K4": 200, "n": 100, "runs": [("kgw", 1, 0.5), ("kgw", 1, 2.0), ("kgw", 2, 0.5)], "n0": 5000},
]

if __name__ == "__main__":
    files = sorted(glob.glob(str(ROOT / "outputs/study4_v0.1/pilot/pilot_summary_*.json")))
    if not files:
        sys.exit("no pilot summary yet")
    S = json.loads(pathlib.Path(files[-1]).read_text()); r = rates(S); print("rates (median tok/s by mode):", {k: round(v) for k, v in r.items()}, "from", pathlib.Path(files[-1]).name)
    print("| Option | watermarked texts | null texts | tokens (M) | hours at the measured rates |")
    print("|---|---|---|---|---|")
    for o in OPTIONS:
        pr = price(o, r); print(f"| {o['name']} | {pr['texts_watermarked']:,} | {pr['texts_null']:,} | {pr['tokens_M']} | {pr['hours']} |")
    print("\nprecision (nominal; power 0.7; between-key SD 0.05):")
    for K4, n in ((60, 50), (100, 50), (100, 100)):
        print(f"  K4={K4}, n={n}: {precision(K4, n)}  | at between-key SD 0.12 (the pilot's two-key gap suggests a large dispersion at delta 0.5): {precision(K4, n, sd_between=0.12)}")
