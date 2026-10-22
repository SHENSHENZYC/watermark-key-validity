"""Study 4 data layer (v1): prompts for the model's generations. Nothing here touches a key or a model.

Prompt cells: corpus cells of Study 2/3 (no Gutenberg: its pool was consumed by the Study 2 and 3 sets). A prompt is the first P tokens
(under the generating model's tokenizer) of a FRESH open-partition unit of the cell: an id that lies in no cell's evaluation set and in no
cell's calibration set (the Study 3 plan, reproduced from the metadata and checked against Study 3's manifest).
- PRODUCTION prompts: the continuation of the cell's Study 2 permutation scan past the calibration block (the same conditional uniform
  scan as Study 3's calibration sets: every admissible id in permutation order; the pilot ids below are also skipped).
- PILOT prompts (validation on inputs; never a production prompt): the first n admissible ids of a SEPARATE permutation of the cell's pool
  seeded from the validation namespace, skipping every evaluation, calibration and production-reserved id.
The human continuation (the next L tokens after the prompt) is kept beside each prompt as a reference text for the quality diagnostics
(the model's log-probability of human text from the same prompt); it is never a null evaluation text of this study.
"""
import datetime, hashlib, json, pathlib, sys
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/study2")); sys.path.insert(0, str(ROOT / "research/study3"))
import s2_data as D      # Study 2's locked data layer, unchanged
import s3_data as D3     # Study 3's locked data layer, unchanged (plan_sets reproduces every Study 2 and 3 draw from the metadata)

PILOT_SEED_BASE = 99261015          # validation namespace (seeds, not keys): the pilot permutation per cell
S3_MANIFEST = "outputs/study3_v0.1/tokens_manifest.json"
PROMPT_CELLS_ALL = [c for c in D.CELLS if c[0] != "gutenberg"]


def consumed_ids(plan):
    """Every id in any cell's evaluation set or calibration set (Study 2 and 3)."""
    s = set()
    for t, p in plan.items():
        s |= set(p["eval_ids"]); s |= set(p["cal_ids"])
    return s


def pilot_ids(pool, cell, taken, n):
    seed = PILOT_SEED_BASE + int(hashlib.sha256(D.cell_str(cell).encode()).hexdigest()[:8], 16)
    perm = D.draw(pool, len(pool), seed); out = []
    for cid in perm:
        if cid in taken:
            continue
        out.append(cid)
        if len(out) == n:
            break
    if len(out) != n:
        raise RuntimeError(f"{D.cell_tag(cell)}: only {len(out)} pilot ids available")
    return out, seed


def production_ids(perm, cal_end, taken, n):
    """The next n admissible ids of the cell's Study 2 permutation after the calibration block (positions > cal_end)."""
    out, pos = [], []
    for p in range(cal_end + 1, len(perm)):
        cid = perm[p]
        if cid in taken:
            continue
        out.append(cid); pos.append(p)
        if len(out) == n:
            break
    if len(out) != n:
        raise RuntimeError(f"only {len(out)} production prompt ids available after position {cal_end}")
    return out, (pos[0], pos[-1]) if pos else (None, None)


def plan_prompts(cells, n_prod, n_pilot, df=None):
    """Metadata only. Returns {tag: {...}} with the pilot and production ids of every prompt cell, disjoint from every Study 2/3 set and
    from each other; asserts the Study 3 plan is reproduced (D3.plan_sets does). The PILOT ids come first (a separate validation-seeded
    permutation, skipping only the consumed sets, so they equal the ids of the pilot cache built before the production plan existed) and
    the PRODUCTION scan skips the consumed sets and the pilot ids."""
    df = D.load_units_meta() if df is None else df
    s3m = json.loads((ROOT / S3_MANIFEST).read_text()); s2m = json.loads((ROOT / D3.S2_MANIFEST).read_text())
    plan3 = D3.plan_sets(s2m, df); taken = consumed_ids(plan3)
    for tag, p in plan3.items():
        if p["cal_ids_sha256"] != s3m["cells"][tag]["cal_ids_sha256"] or p["eval_ids_sha256"] != s3m["cells"][tag]["eval_ids_sha256"]:
            raise RuntimeError(f"{tag}: the reproduced Study 3 sets differ from Study 3's manifest")
    out = {}
    for cell in cells:
        tag = D.cell_tag(cell); pool, counts = D.eligible_pool(df, cell); perm, seed = D3.permutation(pool, cell, int(s2m["seed_base"]))
        if D.ids_digest(pool) != plan3[tag]["pool_sha256"]:
            raise RuntimeError(f"{tag}: pool digest differs from the Study 3 plan")
        cal_end = plan3[tag]["cal_positions"][1]
        pil, pseed = pilot_ids(pool, cell, taken, n_pilot) if n_pilot else ([], None)
        prod, prod_pos = production_ids(perm, cal_end, taken | set(pil), n_prod) if n_prod else ([], (None, None))
        if set(prod) & set(pil) or (set(prod) | set(pil)) & taken:
            raise RuntimeError(f"{tag}: prompt ids collide with a consumed set")
        out[tag] = {"cell": cell, "pool_size": len(pool), "pool_sha256": plan3[tag]["pool_sha256"], "perm_seed": seed, "cal_end_position": int(cal_end),
                    "n_consumed_global": len(taken), "prod_ids": prod, "prod_positions": [int(x) if x is not None else None for x in prod_pos], "prod_ids_sha256": D.ids_digest(prod) if prod else None,
                    "pilot_seed": pseed, "pilot_ids": pil, "pilot_ids_sha256": D.ids_digest(pil) if pil else None}
    return out


def build_prompt_cache(cells, n_prod, n_pilot, P, L, out_dir, tok_name="qwen", kinds=("pilot", "prod"), log=print):
    """Load the prompt units through the seal, tokenise as Study 2 did (no special tokens; the capped prefix), keep the first P + L tokens
    (prompt + human continuation; every unit is eligible for 256 tokens, so P + L <= 256 is guaranteed), write
    <out_dir>/prompts/<tag>__<tok>__<kind>.npy (git-ignored; n x (P + L) int32) and <out_dir>/prompts_manifest.json (tracked)."""
    out_dir = pathlib.Path(out_dir).resolve(); pdir = out_dir / "prompts"; pdir.mkdir(parents=True, exist_ok=True)
    if P + L > 256:
        raise ValueError("P + L must not exceed the cells' eligibility length 256")
    plan = plan_prompts(cells, n_prod if "prod" in kinds else 0, n_pilot); tok = D.get_tokenizer(tok_name)   # the pilot ids are always drawn, so the production scan always skips them
    man = {"study": "study4_v0.1", "written_utc": f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}", "P": P, "L": L, "tokenizer": dict(D.TOKENIZERS[tok_name], name=tok_name),
           "study3_manifest": S3_MANIFEST, "study3_manifest_sha256": D.sha_file(ROOT / S3_MANIFEST), "study2_manifest_sha256": D.sha_file(ROOT / D3.S2_MANIFEST),
           "units_dir": str(D.UNITS_DIR.relative_to(ROOT)), "units_version": D.UNITS_VERSION, "pilot_seed_base": PILOT_SEED_BASE, "add_special_tokens": False, "text_cap_chars": D.TOK_CAP_CHARS, "cells": {}}
    seal = None
    for cell in cells:
        tag = D.cell_tag(cell); p = plan[tag]; entry = {k: v for k, v in p.items() if k not in ("cell", "prod_ids", "pilot_ids")} | {"cell": D.cell_str(cell), "tag": tag, "kinds": {}}
        for kind in kinds:
            ids = p["prod_ids"] if kind == "prod" else p["pilot_ids"]
            if not ids:
                continue
            log(f"{D.cell_str(cell)} {kind}: {len(ids)} ids; loading texts through the seal")
            texts, seal = D.load_texts(ids, cap=D.TOK_CAP_CHARS[cell[0]])
            X, n_full = D.tokenise_window([texts[i] for i in ids], tok, cell, P + L)
            f = pdir / f"{tag}__{tok_name}__{kind}.npy"; np.save(f, X)
            entry["kinds"][kind] = {"file": str(f.relative_to(ROOT)), "n": len(ids), "shape": list(X.shape), "dtype": str(X.dtype), "sha256": D.sha_file(f), "ids_sha256": D.ids_digest(ids), "first_ids": ids[:3],
                                    "capped_prefix_tokens_median": int(np.median(n_full)), "capped_prefix_tokens_min": int(n_full.min())}
            log(f"  {X.shape} sha {entry['kinds'][kind]['sha256'][:12]}")
        man["cells"][tag] = entry
    man["seal"] = seal
    (out_dir / "prompts_manifest.json").write_text(json.dumps(man, indent=1))
    return man


def load_prompts(manifest, tag, kind, root=ROOT):
    e = manifest["cells"][tag]["kinds"][kind]; p = pathlib.Path(root) / e["file"]
    if not p.exists() or D.sha_file(p) != e["sha256"]:
        raise RuntimeError(f"PROMPT CACHE MISSING OR MISMATCHED: {p}")
    X = np.load(p)
    if list(X.shape) != e["shape"] or str(X.dtype) != e["dtype"]:
        raise RuntimeError(f"prompt cache {p}: shape/dtype differ from the manifest")
    return X


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--pilot" in a:
        cells = [c for c in PROMPT_CELLS_ALL if D.cell_tag(c) in ("news_en_256", "wikipedia_en_256", "stackexchange_en_256", "wikipedia_zh_256")]
        build_prompt_cache(cells, 0, 96, P=64, L=192, out_dir=ROOT / "outputs/study4_v0.1/pilot", kinds=("pilot",))
    elif "--build" in a:
        # the production cache: the pilot ids (96 per cell, as in the pilot cache) are reproduced and must equal the pilot manifest's digests
        grid = json.loads((ROOT / "research/study4/grid_v0.1.json").read_text()); cells = [c for c in PROMPT_CELLS_ALL if D.cell_tag(c) in grid["cells"]]
        pil_man = json.loads((ROOT / grid["prompts"]["pilot_manifest"]).read_text())
        plan = plan_prompts(cells, grid["prompts"]["n_prod"], 96)
        for cell in cells:
            tag = D.cell_tag(cell)
            if plan[tag]["pilot_ids_sha256"] != pil_man["cells"][tag]["kinds"]["pilot"]["ids_sha256"]:
                raise RuntimeError(f"{tag}: the reproduced pilot ids differ from the pilot cache's digest")
        man = build_prompt_cache(cells, grid["prompts"]["n_prod"], 96, P=grid["prompts"]["P"], L=grid["prompts"]["L_human"], out_dir=ROOT / "outputs/study4_v0.1", kinds=("prod",))
        print("production prompt cache written:", {t: e["kinds"]["prod"]["sha256"][:12] for t, e in man["cells"].items()})
    elif "--plan" in a:
        pl = plan_prompts(PROMPT_CELLS_ALL, 0, 0)
        for t, p in pl.items():
            print(f"{t:22s} pool {p['pool_size']:7d} cal_end {p['cal_end_position']:6d} consumed(global) {p['n_consumed_global']}")
