"""Study 1 runner (v4, after R03 round 3): executes the pre-registered grid cell by cell, writing one JSON per cell under
outputs/study1_v0.3/cells/ (statistics only; synthetic texts are not kept) plus one cost record per chain.
Before any study cell runs it verifies the lock against the CANONICAL experiment identity of this version (the study name,
the protocol, grid, validation and resolution paths, the checkpoint, an ISO date, hex digests of every pinned file,
approved_by, before_outcomes, final, the key record) and raises LockError naming the first violation. Every cell records
its provenance (lock, grid and code digests, mode, seeds, keys) AND its slot (law, h, L, rule, colouring, gamma, K,
degenerate); an existing cell is reused only when provenance and slot match and its body agrees with the slot; otherwise
the run stops (ProvenanceError; nothing is overwritten).
Usage: .venv/bin/python -u research/study1/s1_run.py --grid research/study1/grid_v0.3.json [--lock outputs/study1_v0.3/PRE_RUN_LOCK.json]
       [--validation --out-dir <fresh dir>] [--only-law <name>]
--validation runs the grid's validation laws with validation seeds and validation keys (no lock; not study outcomes).
"""
import datetime, hashlib, json, pathlib, re, sys, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "tools"))
import s1_core as C
from key_policy import check_keys

STUDY = "study1_v0.3"
CHECKPOINT = "R03"
GRID_CANON = "research/study1/grid_v0.3.json"
PROTOCOL = "research/STUDY1_PROTOCOL_v0.3.md"
VALIDATION = f"outputs/{STUDY}/VALIDATION.json"
RESOLUTION = "research/reviews/R03_study1-protocol/RESOLUTION.md"
OUT = pathlib.Path("outputs") / STUDY
CODE_FILES = ("research/study1/s1_core.py", "research/study1/s1_run.py", "research/study1/s1_analyze.py", "research/study1/s1_validate.py", "tools/key_policy.py")
PINNED = tuple(sorted(set(CODE_FILES) | {GRID_CANON, PROTOCOL, VALIDATION}))
LOCK_FIELDS = ("study", "date", "approved_by", "before_outcomes", "final", "grid", "protocol", "validation", "hashes", "review", "keys")
PROVENANCE_FIELDS = ("study", "mode", "lock_sha256", "grid_sha256", "core_sha256", "run_sha256", "text_seed_base", "text_seed", "key_start", "K")
SLOT_FIELDS = ("name", "law", "h", "L", "rule", "colouring", "gamma", "K", "degenerate")   # "law" is the full specification (kind, parameters, role): R03 round 3, F20
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class LockError(RuntimeError):
    pass


class ProvenanceError(RuntimeError):
    pass


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def utc():
    return f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}"


def law_name(spec):
    k = spec["kind"]
    if k == "zipf":
        return f"zipf_V{spec['V']}_s{spec['s']}"
    if k == "markov":
        return f"markov_V{spec['V']}_S{spec['S']}_eps{spec['eps']}_s{spec['s']}"
    if k == "twotoken":
        return f"twotoken_p{spec['p_stay']}"
    if k == "support":
        return f"support_V{spec['V']}_s{spec['s_support']}"
    raise ValueError(k)


def law_V(spec):
    return 2 if spec["kind"] == "twotoken" else int(spec["V"])


def make_law(spec):
    k = spec["kind"]
    if k == "zipf":
        return C.ZipfIID(spec["V"], spec["s"])
    if k == "markov":
        return C.MarkovZipf(spec["V"], spec["S"], spec["eps"], spec["s"])
    if k == "twotoken":
        return C.TwoToken(spec["p_stay"])
    if k == "support":
        return C.SupportUniform(spec["V"], spec["s_support"])
    raise ValueError(k)


def text_seed_for(name, seed_base):
    return int(seed_base) + int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)


def expected_cells(grid, laws=None):
    """The complete pre-registered inventory implied by the grid (the analyzer requires exactly this set, slot by slot)."""
    cells = []
    sub = grid.get("fixed_subset_core", {})
    for spec in (grid["laws"] if laws is None else laws):
        role = spec.get("role", "core"); name = law_name(spec); V = law_V(spec)
        hs = grid["h"] if role == "core" else grid["h_illustration"]
        Ls = grid["L"] if role == "core" else grid["L_illustration"]
        gammas = grid["gamma"] if (role != "core" or spec.get("gamma_extra", False)) else [grid["gamma"][0]]
        for h in hs:
            if role == "core":
                cols = [("independent", grid["K"], Ls)] + ([("fixed", grid["K_fixed_core"], sub["L"])] if sub and h in sub["h"] else [])
            else:
                cols = [(c, spec.get("K_illustration", grid["K"]), Ls) for c in grid["colourings_illustration"]]
            for colouring, K, L_list in cols:
                for gamma in gammas:
                    deg, m = C.degenerate(gamma, V)
                    for L in L_list:
                        for rule in grid["rules"]:
                            cells.append({"file": f"{name}__h{h}__{colouring}__g{gamma}__L{L}__{rule}.json", "law": spec, "name": name, "V": V, "role": role,
                                          "h": h, "colouring": colouring, "gamma": gamma, "L": L, "rule": rule, "K": K, "degenerate": deg, "m": m})
    return cells


def slot_of(cell):
    return {f: cell[f] for f in SLOT_FIELDS}


def verify_lock(lock_path, grid_path, root="."):
    """Explicit schema and canonical-identity check; raises LockError naming the first violated requirement. `root` is the directory
    against which the canonical relative paths are resolved (the repository root in production; a copy in fixtures)."""
    root = pathlib.Path(root); lock_path = pathlib.Path(lock_path)
    if not lock_path.exists():
        raise LockError(f"no lock at {lock_path}")
    try:
        lock = json.loads(lock_path.read_text())
    except Exception as e:
        raise LockError(f"lock is not valid JSON: {e}")
    for f in LOCK_FIELDS:
        if f not in lock:
            raise LockError(f"lock lacks the field {f!r}")
    if lock["study"] != STUDY:
        raise LockError(f"lock study {lock['study']!r} is not {STUDY!r}")
    if lock["before_outcomes"] is not True or lock["final"] is not False:
        raise LockError("lock must carry before_outcomes: true and final: false")
    if not isinstance(lock["approved_by"], str) or lock["approved_by"].strip() != "Yichen":
        raise LockError("lock must be approved_by 'Yichen'")
    try:
        d = datetime.date.fromisoformat(str(lock["date"]))
    except ValueError:
        raise LockError(f"lock date {lock['date']!r} is not an ISO date")
    if d < datetime.date(2026, 10, 10):
        raise LockError(f"lock date {d} precedes protocol v0.3")
    if str(grid_path) != GRID_CANON:
        raise LockError(f"the grid given ({grid_path}) is not the canonical grid {GRID_CANON}")
    for field, canon in (("grid", GRID_CANON), ("protocol", PROTOCOL), ("validation", VALIDATION)):
        if lock[field] != canon:
            raise LockError(f"lock {field} {lock[field]!r} is not the canonical {canon!r}")
    hashes = lock["hashes"]
    if not isinstance(hashes, dict) or set(hashes) != set(PINNED):
        raise LockError(f"lock hashes must pin exactly {sorted(PINNED)}; missing {sorted(set(PINNED) - set(hashes))}, extra {sorted(set(hashes) - set(PINNED))}")
    for f, h in hashes.items():
        if not isinstance(h, str) or not HEX64.match(h):
            raise LockError(f"lock digest for {f} is not a 64-hex sha256")
        if not (root / f).exists():
            raise LockError(f"locked file {f} does not exist under {root}")
        if sha(root / f) != h:
            raise LockError(f"LOCK MISMATCH: {f} differs from its locked digest")
    rv = lock["review"]
    for f in ("checkpoint", "resolution", "sha256"):
        if f not in rv:
            raise LockError(f"lock review lacks {f!r}")
    if rv["checkpoint"] != CHECKPOINT or rv["resolution"] != RESOLUTION:
        raise LockError(f"lock review must name checkpoint {CHECKPOINT} and the resolution {RESOLUTION}")
    if not isinstance(rv["sha256"], str) or not HEX64.match(rv["sha256"]):
        raise LockError("lock review digest is not a 64-hex sha256")
    if not (root / RESOLUTION).exists() or sha(root / RESOLUTION) != rv["sha256"]:
        raise LockError("the reviewer's resolution memo is missing or differs from its locked digest")
    grid = json.loads((root / GRID_CANON).read_text())
    if grid.get("study") != STUDY:
        raise LockError(f"the grid's study {grid.get('study')!r} is not {STUDY!r}")
    ks = lock["keys"]
    if ks.get("production_start") != grid["key_seed_start"] or ks.get("K") != grid["K"] or ks.get("K_fixed_core") != grid["K_fixed_core"]:
        raise LockError("lock key record does not match the grid")
    K_max = max([grid["K"], grid["K_fixed_core"]] + [l.get("K_illustration", grid["K"]) for l in grid["laws"]])
    check_keys(range(grid["key_seed_start"], grid["key_seed_start"] + K_max), "study1")
    return lock


def provenance(mode, lock_path, grid_path, text_seed, key_start, K, seed_base, slot):
    return {"study": STUDY, "mode": mode, "lock_sha256": sha(lock_path) if lock_path else None, "grid_sha256": sha(grid_path),
            "core_sha256": sha(HERE / "s1_core.py"), "run_sha256": sha(HERE / "s1_run.py"), "text_seed_base": int(seed_base), "text_seed": int(text_seed),
            "key_start": int(key_start), "K": int(K), "slot": dict(slot)}


def body_matches_slot(cell, slot):
    """The cell's own metadata must agree with its slot, including the FULL law specification (kind, parameters and role), so that a
    copied, renamed or role-edited cell is caught even when its provenance block matches (R03 rounds 2 and 3)."""
    try:
        return (cell["law"] == slot["law"] and law_name(cell["law"]) == slot["name"] and cell["h"] == slot["h"] and cell["L"] == slot["L"] and cell["rule"] == slot["rule"]
                and cell["colouring"] == slot["colouring"] and cell["gamma"] == slot["gamma"] and cell["K"] == slot["K"] and bool(cell.get("degenerate", False)) == bool(slot["degenerate"]))
    except (KeyError, ValueError, TypeError):
        return False


def cell_reusable(path, prov):
    """True when the cell exists with the same provenance and slot and a body that agrees with the slot; False when it does not
    exist; ProvenanceError when it exists and differs in any of these."""
    path = pathlib.Path(path)
    if not path.exists():
        return False
    try:
        cell = json.loads(path.read_text()); old = cell.get("provenance", {})
    except Exception as e:
        raise ProvenanceError(f"{path.name}: unreadable existing cell ({e})")
    diff = [f for f in PROVENANCE_FIELDS if old.get(f) != prov.get(f)]
    if old.get("slot") != prov["slot"]:
        diff.append("slot")
    if diff:
        raise ProvenanceError(f"{path.name}: existing cell has foreign provenance in {diff}; refusing to reuse or overwrite")
    if not body_matches_slot(cell, prov["slot"]):
        raise ProvenanceError(f"{path.name}: existing cell's body disagrees with its slot; refusing to reuse or overwrite")
    return True


def run_law(spec, cells, grid, out_dir, seed_base, mode, lock_path, grid_path, key_start, t_log):
    """All chains (one per h) of one law; texts are shared across h (the same seed)."""
    law = make_law(spec); N, L_max = grid["N"], max(grid["L"] if spec.get("role", "core") == "core" else grid["L_illustration"])
    text_seed = text_seed_for(law.name, seed_base)
    by_h = {}
    for c in cells:
        by_h.setdefault(c["h"], []).append(c)
    for h, hcells in sorted(by_h.items()):
        tag = f"{law.name}__h{h}"
        todo = []
        for c in hcells:
            prov = provenance(mode, lock_path, grid_path, text_seed, key_start, c["K"], seed_base, slot_of(c))
            if not cell_reusable(out_dir / c["file"], prov):
                todo.append((c, prov))
        if not todo:
            t_log.write(f"{utc()} chain {tag}: every cell present with matching provenance and slot; skipped\n"); t_log.flush(); continue
        t0 = time.time()
        chain = C.Chain(law, h, N, L_max, seed=text_seed)
        cost = {"tag": tag, "n_tuples": int(len(chain.D)), "n_contexts": int(chain.n_ctx), "N": N, "L_max": L_max, "build_seconds": round(time.time() - t0, 1), "colourings": [], "cells": []}
        t_log.write(f"{utc()} chain {tag} built: |D|={len(chain.D)} contexts={chain.n_ctx} ({cost['build_seconds']}s)\n"); t_log.flush()
        groups = {}
        for c, prov in todo:
            groups.setdefault((c["colouring"], c["gamma"], c["K"]), []).append((c, prov))
        for (colouring, gamma, K), items in groups.items():
            keys = list(range(key_start, key_start + K)); check_keys(keys, "study1" if mode == "study" else "validation")
            if items[0][0]["degenerate"]:
                for c, prov in items:
                    (out_dir / c["file"]).write_text(json.dumps({"degenerate": True, "reason": f"m = floor(gamma V) = {c['m']} with V = {c['V']}: no dispersion across keys (every key colours alike)",
                                                                 "law": spec, "h": h, "L": c["L"], "rule": c["rule"], "colouring": colouring, "gamma": gamma, "N": N, "K": K, "provenance": dict(prov, written_utc=utc())}, indent=1))
                t_log.write(f"{utc()}   {tag} {colouring} g{gamma}: degenerate (m={items[0][0]['m']}); {len(items)} marker cells written\n"); t_log.flush(); continue
            t2 = time.time()
            packed = C.PackedColours(chain, keys, gamma, colouring, law.V, chunk=grid["key_chunk"])
            cost["colourings"].append({"colouring": colouring, "gamma": gamma, "K": K, "seconds": round(time.time() - t2, 1)})
            t_log.write(f"{utc()}   colours {tag} {colouring} g{gamma} K={K}: {time.time()-t2:.0f}s\n"); t_log.flush()
            for c, prov in items:
                t1 = time.time(); inc = chain.incidence(c["L"], c["rule"])
                counts = np.zeros((N, K), dtype=np.float64)
                for c0 in range(0, K, grid["key_chunk"]):
                    cols = packed.chunk_cols(c0); counts[:, c0:c0 + cols.shape[1]] = np.asarray(inc @ cols.astype(np.float64))
                rng = np.random.default_rng([int(hashlib.sha256(c["file"].encode()).hexdigest()[:8], 16), 20261011])   # bootstrap and subsample stream, per cell
                stats = C.cell_statistics(inc, counts, chain, gamma, grid["alpha"], law.V, colouring, rng)
                stats.update({"law": spec, "h": h, "L": c["L"], "rule": c["rule"], "colouring": colouring, "gamma": gamma, "N": N, "K": K, "n_tuples_dict": int(len(chain.D)), "n_contexts": int(chain.n_ctx),
                              "nnz": int(inc.nnz), "seconds": round(time.time() - t1, 1), "provenance": dict(prov, written_utc=utc())})
                (out_dir / c["file"]).write_text(json.dumps(stats, indent=1, default=float))
                cost["cells"].append({"file": c["file"], "L": c["L"], "rule": c["rule"], "colouring": colouring, "gamma": gamma, "K": K, "nnz": int(inc.nnz), "seconds": stats["seconds"]})
                t_log.write(f"{utc()}   cell {c['file']} ({stats['seconds']}s)\n"); t_log.flush()
        cost["chain_seconds"] = round(time.time() - t0, 1)
        (out_dir / f"costs__{tag}.json").write_text(json.dumps(cost, indent=1))
        t_log.write(f"{utc()} chain {tag} done ({cost['chain_seconds']}s)\n"); t_log.flush()
        del chain


def main(grid_path, lock_path, validation, only_law=None, out_dir=None):
    grid = json.loads(pathlib.Path(grid_path).read_text())
    if validation:
        mode = "validation"; lock_path = None; seed_base = grid["validation_seed_base"]; laws = grid["validation_laws"]; key_start = grid["validation_key_seed_start"]
        out_dir = pathlib.Path(out_dir) if out_dir else OUT / "validation"
    else:
        verify_lock(lock_path, grid_path)
        mode = "study"; seed_base = grid["text_seed_base"]; laws = grid["laws"]; key_start = grid["key_seed_start"]
        out_dir = OUT / "cells"
    out_dir.mkdir(parents=True, exist_ok=True)
    cells = expected_cells(grid, laws)
    with (out_dir.parent / ("validation_run.log" if validation else "run.log")).open("a") as t_log:
        t_log.write(f"start {mode} run {utc()} grid={grid_path} sha={sha(grid_path)} out={out_dir} lock={lock_path} core={sha(HERE / 's1_core.py')[:12]}\n")
        for spec in laws:
            if only_law and law_name(spec) != only_law:
                continue
            run_law(spec, [c for c in cells if c["name"] == law_name(spec)], grid, out_dir, seed_base, mode, lock_path, grid_path, key_start, t_log)
        t_log.write(f"DONE {utc()}\n")
    print("DONE", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[a.index("--grid") + 1], a[a.index("--lock") + 1] if "--lock" in a else str(OUT / "PRE_RUN_LOCK.json"), "--validation" in a,
         a[a.index("--only-law") + 1] if "--only-law" in a else None, a[a.index("--out-dir") + 1] if "--out-dir" in a else None)
