"""Study 2 runner (v1): executes the pre-registered grid chain by chain (a chain = one corpus cell x tokenizer x width h over the
cached production texts), writing one JSON per cell under outputs/study2_v0.1/cells/ (statistics only; no token or text is kept
in a cell) plus one cost record per chain. Before any study cell runs it verifies the lock against the CANONICAL experiment
identity of this version (study name; protocol, grid, validation, tokens-manifest and resolution paths; checkpoint R05; an ISO
date; hex digests of exactly the pinned files; approved_by, before_outcomes, final; the key record) and raises LockError naming
the first violation; every token array is verified against the pinned manifest before use. Every cell records its provenance
(lock, grid, code and manifest digests, the cell's token digest, mode, keys) AND its slot (cell, tokenizer, family, h, L, rule,
colouring, gamma, K, N); an existing cell is reused only when provenance and slot match and its body agrees with the slot;
otherwise the run stops (ProvenanceError; nothing is overwritten).
Usage: .venv/bin/python -u research/study2/s2_run.py --grid research/study2/grid_v0.1.json [--lock outputs/study2_v0.1/PRE_RUN_LOCK.json]
       [--validation --out-dir <fresh dir>] [--only-chain <tag>__<tok>__h<h>]
--validation runs the grid's synthetic validation cells with validation keys (no lock; no real text; not study outcomes).
"""
import datetime, hashlib, json, pathlib, re, resource, sys, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study1")); sys.path.insert(0, str(ROOT / "tools"))
import s2_core as S
import s2_data as D
import s1_core as C
from s2_keys import check_keys

STUDY = "study2_v0.1"
CHECKPOINT = "R05"
GRID_CANON = "research/study2/grid_v0.1.json"
PROTOCOL = "research/STUDY2_PROTOCOL_v0.1.md"
VALIDATION = f"outputs/{STUDY}/VALIDATION.json"
INPUTS = f"outputs/{STUDY}/INPUTS.json"
TOKENS_MANIFEST = f"outputs/{STUDY}/tokens_manifest.json"
RESOLUTION = "research/reviews/R05_study2-protocol/RESOLUTION.md"
OUT = pathlib.Path("outputs") / STUDY
CODE_FILES = ("research/study2/s2_core.py", "research/study2/s2_run.py", "research/study2/s2_analyze.py", "research/study2/s2_validate.py", "research/study2/s2_data.py", "research/study2/s2_keys.py", "research/study2/s2_inputs.py",
              "research/study1/s1_core.py", "tools/key_policy.py", "tools/corpora_access.py")
PINNED = tuple(sorted(set(CODE_FILES) | {GRID_CANON, PROTOCOL, VALIDATION, INPUTS, TOKENS_MANIFEST}))
LOCK_FIELDS = ("study", "date", "approved_by", "before_outcomes", "final", "grid", "protocol", "validation", "inputs", "tokens_manifest", "hashes", "review", "keys")
PROVENANCE_FIELDS = ("study", "mode", "lock_sha256", "grid_sha256", "core_sha256", "run_sha256", "s1core_sha256", "tokens_manifest_sha256", "tokens_sha256", "key_start", "K", "N")
SLOT_FIELDS = ("tag", "tokenizer", "family", "h", "L", "rule", "colouring", "gamma", "K", "N")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class LockError(RuntimeError):
    pass


class ProvenanceError(RuntimeError):
    pass


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def utc():
    return f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}"


def cell_file(slot):
    return f"{slot['tag']}__{slot['tokenizer']}__{slot['family']}__h{slot['h']}__{slot['colouring']}__g{slot['gamma']}__L{slot['L']}__{slot['rule']}.json"


def expected_cells(grid, validation=False):
    """The complete pre-registered inventory implied by the grid (the analyzer requires exactly this set, slot by slot)."""
    cells = []
    if validation:
        v = grid["validation"]; specs = [{"tag": v["tag"], "L": v["L"]}]; toks = {v["tokenizer_label"]: {"V": v["law"]["V"]}}; hs = v["h"]; K, Kf, N = v["K"], v["K_fixed_h0"], v["N"]
    else:
        specs = grid["cells"]; toks = grid["tokenizers"]; hs = grid["h"]; K, Kf, N = grid["K"], grid["K_fixed_h0"], grid["N"]
    fam = grid["families"]
    for spec in specs:
        for tok, tinfo in toks.items():
            V = int(tinfo["V"])
            for h in hs:
                for L in spec["L"]:
                    for rule in grid["rules"]:
                        base = {"tag": spec["tag"], "tokenizer": tok, "h": h, "L": L, "rule": rule, "N": N, "V": V}
                        for gamma in fam["kgw"]["gamma"]:
                            deg, m = C.degenerate(gamma, V)
                            for colouring in fam["kgw"]["colourings"]:
                                cells.append(dict(base, family="kgw", colouring=colouring, gamma=gamma, K=K, degenerate=deg, m=m))
                            if fam["kgw"].get("fixed_h0") and h == 0:
                                cells.append(dict(base, family="kgw", colouring="fixed", gamma=gamma, K=Kf, degenerate=deg, m=m))
                        cells.append(dict(base, family="gumbel", colouring="uniform", gamma="na", K=K, degenerate=False, m=None))
    for c in cells:
        c["file"] = cell_file(c)
    return cells


def slot_of(cell):
    return {f: cell[f] for f in SLOT_FIELDS}


def in_deployer_subset(cell, grid, spec_L):
    d = grid["deployer_subset"]
    if cell["h"] not in d["h"] or cell["rule"] not in d["rules"] or cell["family"] not in d["families"]:
        return False
    if d.get("longest_L_only") and cell["L"] != max(spec_L):
        return False
    if cell["family"] == "kgw" and (cell["colouring"] != "independent" or cell["gamma"] not in d["kgw_gamma"]):
        return False
    return True


def verify_lock(lock_path, grid_path, root="."):
    """Explicit schema and canonical-identity check; raises LockError naming the first violated requirement."""
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
        raise LockError("lock must carry before_outcomes: true and final: false (Study 2 opens no held-out text)")
    if not isinstance(lock["approved_by"], str) or lock["approved_by"].strip() != "Yichen":
        raise LockError("lock must be approved_by 'Yichen'")
    try:
        d = datetime.date.fromisoformat(str(lock["date"]))
    except ValueError:
        raise LockError(f"lock date {lock['date']!r} is not an ISO date")
    if d < datetime.date(2026, 10, 10):
        raise LockError(f"lock date {d} precedes protocol v0.1")
    if str(grid_path) != GRID_CANON:
        raise LockError(f"the grid given ({grid_path}) is not the canonical grid {GRID_CANON}")
    for field, canon in (("grid", GRID_CANON), ("protocol", PROTOCOL), ("validation", VALIDATION), ("inputs", INPUTS), ("tokens_manifest", TOKENS_MANIFEST)):
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
    if ks.get("production_start") != grid["key_seed_start"] or ks.get("K") != grid["K"] or ks.get("K_fixed_h0") != grid["K_fixed_h0"]:
        raise LockError("lock key record does not match the grid")
    check_keys(range(grid["key_seed_start"], grid["key_seed_start"] + max(grid["K"], grid["K_fixed_h0"])), "study2")
    man = json.loads((root / TOKENS_MANIFEST).read_text())
    if man.get("N", 0) < grid["N"]:
        raise LockError(f"the tokens manifest holds N = {man.get('N')} texts per cell, fewer than the grid's N = {grid['N']}")
    if man.get("seed_base") != grid["text_seed_base"]:
        raise LockError("the tokens manifest's seed base differs from the grid's text_seed_base")
    for spec in grid["cells"]:
        if spec["tag"] not in man["cells"]:
            raise LockError(f"the tokens manifest lacks the cell {spec['tag']}")
        for tok in grid["tokenizers"]:
            if tok not in man["cells"][spec["tag"]]["tokenizers"]:
                raise LockError(f"the tokens manifest lacks {spec['tag']} under {tok}")
            if man["tokenizers"][tok]["V"] != grid["tokenizers"][tok]["V"]:
                raise LockError(f"V for {tok} differs between the manifest and the grid")
    return lock


def provenance(mode, lock_path, grid_path, tokens_sha, key_start, K, N, slot, man_sha):
    return {"study": STUDY, "mode": mode, "lock_sha256": sha(lock_path) if lock_path else None, "grid_sha256": sha(grid_path), "core_sha256": sha(HERE / "s2_core.py"), "run_sha256": sha(HERE / "s2_run.py"),
            "s1core_sha256": sha(ROOT / "research/study1/s1_core.py"), "tokens_manifest_sha256": man_sha, "tokens_sha256": tokens_sha, "key_start": int(key_start), "K": int(K), "N": int(N), "slot": dict(slot)}


def body_matches_slot(cell, slot):
    try:
        return all(cell[f] == slot[f] for f in SLOT_FIELDS)
    except (KeyError, TypeError):
        return False


REQ_COMMON = ("N_eff", "frac_M0", "mean_M", "identity_q", "identity_z", "population", "levels", "covariance_heterogeneity", "zbar", "z_var_within_key")
REQ_KGW = REQ_COMMON + ("q_hat",); REQ_GUMBEL = REQ_COMMON + ("s_bar",)
REQ_LEVEL = ("key_mean_level", "unconditional_rate", "se_conditional_on_texts", "r2_kl_pbound", "sd_obs_conditional", "sd_obs_boot_ci95", "sd_obs_boot_se", "pred_first_order", "pred_unit_sigma",
             "pred_pairwise_gaussian", "ratio_obs_over_pred", "ratio_boot_ci95", "population_est", "quantiles", "max_key", "min_key", "share_keys_above_2alpha", "share_keys_above_5alpha", "structural_zero", "level_counts")
REQ_LEVEL_KGW_INDEP = ("pred_gaussian_shift_per_text", "pred_per_text_vs_closed_form_abs_diff_sd", "pred_simulated_shift", "ratio_obs_over_pred_simulated_shift")
REQ_CROSSED = ("q0.01", "q0.05", "q0.5", "q0.95", "q0.99", "max", "share2", "share5")
RECONCILE_TOL = 1e-9          # absolute tolerance for a stored summary against its recomputation from the integer level counts


class CellBodyError(RuntimeError):
    pass


QUANTILE_KEYS = ("0.01", "0.05", "0.5", "0.95", "0.99")
CROSSED_B = 200               # the registered crossed key-by-document resample count (s2_core.BOOT_CROSSED)


def _finite(x):
    import numpy as np
    return isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x)


def _interval(v, lo_bound=None, hi_bound=None):
    """A valid interval: a list of two finite numbers, ordered, within the bounds when given."""
    if not (isinstance(v, (list, tuple)) and len(v) == 2 and all(_finite(x) for x in v) and v[0] <= v[1]):
        return False
    if lo_bound is not None and v[0] < lo_bound - 1e-12:
        return False
    if hi_bound is not None and v[1] > hi_bound + 1e-12:
        return False
    return True


def validate_cell_body(d, c, grid, alphas=None):
    """The content contract of a live cell (R05 F1, F2, F4, F9, F10): N_eff equals N (every production window has L > h and every rule
    retains at least one tuple per text, so no text is lost); every required field is present; the stored deployer flag equals the
    grid-derived membership; every alpha's level counts are K integers in [0, N_eff] whose key mean, sample SD (ddof 1), the five
    registered quantiles, extrema, exceedance shares and KL bound reproduce the stored summaries within RECONCILE_TOL; the exact
    reference mean and the KL bound are finite and in [0, 1]; the structural-zero flag equals its derivation from the exact mean and
    the counts; the SD bootstrap SE is finite and non-negative and the SD and ratio intervals are finite, ordered and consistent
    (the ratio interval is the SD interval divided by the prediction when the prediction is positive; when it is not, the ratio and its
    interval are the registered non-finite exception); the counts are nested across alpha; a deployer-subset cell carries the crossed
    block with every promised statistic as a populated record (two finite ordered bounds in [0, 1], a finite non-negative SE, B = 200).
    Raises CellBodyError naming the first violation. Markers (degenerate slots) are not expected in this grid and are refused at a live slot."""
    import numpy as np
    import s1_core as C
    alphas = alphas or grid["alpha"]
    if c["degenerate"]:
        raise CellBodyError("a degenerate slot is not expected in this grid")
    if "levels" not in d or d.get("degenerate") is True or "flag" in d:
        raise CellBodyError("marker or flagged cell at a live slot")
    if not isinstance(d.get("N_eff"), int) or isinstance(d.get("N_eff"), bool) or d["N_eff"] != c["N"]:
        raise CellBodyError(f"N_eff {d.get('N_eff')!r} is not N = {c['N']}")
    for f in (REQ_KGW if c["family"] == "kgw" else REQ_GUMBEL):
        if f not in d:
            raise CellBodyError(f"lacks the required field {f!r}")
    if "L_list" not in c:
        raise CellBodyError("the expected cell carries no L_list (deployer membership cannot be derived)")
    dep = in_deployer_subset(c, grid, c["L_list"])
    if d.get("deployer_subset") is not dep:
        raise CellBodyError(f"stored deployer_subset {d.get('deployer_subset')!r} differs from the grid-derived membership {dep}")
    counts_by_alpha = {}
    for a in alphas:
        lv = d["levels"].get(str(a))
        if lv is None:
            raise CellBodyError(f"lacks alpha {a}")
        for f in REQ_LEVEL + (REQ_LEVEL_KGW_INDEP if (c["family"] == "kgw" and c["colouring"] == "independent") else ()):
            if f not in lv:
                raise CellBodyError(f"alpha {a} lacks {f!r}")
        k = lv["level_counts"]
        if len(k) != c["K"]:
            raise CellBodyError(f"alpha {a}: {len(k)} level counts, not K = {c['K']}")
        if not all(isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= d["N_eff"] for x in k):
            raise CellBodyError(f"alpha {a}: a level count is not an integer in [0, N_eff]")
        lev = np.asarray(k, dtype=np.float64) / d["N_eff"]
        recon = {"key_mean_level": float(lev.mean()), "sd_obs_conditional": float(lev.std(ddof=1)), "max_key": float(lev.max()), "min_key": float(lev.min()),
                 "share_keys_above_2alpha": float(np.mean(lev > 2 * a)), "share_keys_above_5alpha": float(np.mean(lev > 5 * a)), "se_conditional_on_texts": float(lev.std(ddof=1) / np.sqrt(c["K"]))}
        for f, v in recon.items():
            if not _finite(lv[f]) or abs(float(lv[f]) - v) > RECONCILE_TOL:
                raise CellBodyError(f"alpha {a}: stored {f} {lv[f]!r} differs from its recomputation {v} from the level counts")
        q = lv["quantiles"]
        if not isinstance(q, dict) or set(q) != set(QUANTILE_KEYS):
            raise CellBodyError(f"alpha {a}: the quantiles are not exactly the registered {QUANTILE_KEYS}")
        for qk, v in q.items():
            if not _finite(v) or abs(float(v) - float(np.quantile(lev, float(qk)))) > RECONCILE_TOL:
                raise CellBodyError(f"alpha {a}: stored quantile {qk} is not finite or differs from its recomputation")
        ex = lv.get("exact_marginal_if_indep_distinct", lv.get("exact_marginal_if_distinct"))
        if not _finite(ex) or not (0.0 <= ex <= 1.0):
            raise CellBodyError(f"alpha {a}: the exact reference mean {ex!r} is not a finite number in [0, 1]")
        kl = C.kl_chernoff_pbound(float(lev.mean()), float(ex), c["K"])
        if not _finite(lv["r2_kl_pbound"]) or not (0.0 <= lv["r2_kl_pbound"] <= 1.0) or abs(float(lv["r2_kl_pbound"]) - kl) > RECONCILE_TOL:
            raise CellBodyError(f"alpha {a}: stored KL bound {lv['r2_kl_pbound']!r} is not finite in [0, 1] or differs from its recomputation {kl}")
        sz = bool(lev.max() == 0.0 and ex == 0.0)
        if lv["structural_zero"] is not sz:
            raise CellBodyError(f"alpha {a}: stored structural_zero {lv['structural_zero']!r} differs from its derivation {sz} (exact mean {ex}, largest level {lev.max()})")
        if not _finite(lv["sd_obs_boot_se"]) or lv["sd_obs_boot_se"] < 0:
            raise CellBodyError(f"alpha {a}: the SD bootstrap SE {lv['sd_obs_boot_se']!r} is not finite and non-negative")
        if not _interval(lv["sd_obs_boot_ci95"], 0.0, 1.0):
            raise CellBodyError(f"alpha {a}: the SD interval {lv['sd_obs_boot_ci95']!r} is not a finite ordered interval in [0, 1]")
        sd_pred = lv["pred_first_order"].get("sd_cond")
        if not _finite(sd_pred) or sd_pred < 0:
            raise CellBodyError(f"alpha {a}: the predicted SD {sd_pred!r} is not finite and non-negative")
        if sd_pred > 0:
            if not _finite(lv["ratio_obs_over_pred"]) or abs(float(lv["ratio_obs_over_pred"]) - recon["sd_obs_conditional"] / sd_pred) > RECONCILE_TOL * max(1.0, 1.0 / sd_pred):
                raise CellBodyError(f"alpha {a}: the ratio {lv['ratio_obs_over_pred']!r} is not finite or differs from sd_obs / sd_pred")
            if not _interval(lv["ratio_boot_ci95"], 0.0, None) or any(abs(float(r_) - b_ / sd_pred) > RECONCILE_TOL * max(1.0, 1.0 / sd_pred) for r_, b_ in zip(lv["ratio_boot_ci95"], lv["sd_obs_boot_ci95"])):
                raise CellBodyError(f"alpha {a}: the ratio interval {lv['ratio_boot_ci95']!r} is not finite, ordered and equal to the SD interval divided by the prediction")
        else:
            if any(_finite(x) for x in list(lv["ratio_boot_ci95"]) + [lv["ratio_obs_over_pred"]]):
                raise CellBodyError(f"alpha {a}: a zero prediction must carry the registered non-finite ratio and interval")
        if dep:
            cr = lv.get("deployer_crossed")
            if not isinstance(cr, dict) or any(kk not in cr for kk in REQ_CROSSED):
                raise CellBodyError(f"alpha {a}: a deployer-subset cell lacks the crossed block or one of its promised keys")
            if cr.get("B") != CROSSED_B:
                raise CellBodyError(f"alpha {a}: the crossed block's B {cr.get('B')!r} is not the registered {CROSSED_B}")
            for kk in REQ_CROSSED:
                rec = cr[kk]
                if not isinstance(rec, dict) or not _interval(rec.get("ci95"), 0.0, 1.0) or not _finite(rec.get("boot_se")) or rec["boot_se"] < 0:
                    raise CellBodyError(f"alpha {a}: crossed statistic {kk} is not a populated record with a finite ordered interval in [0, 1] and a finite non-negative SE")
        counts_by_alpha[float(a)] = np.asarray(k)
    al = sorted(counts_by_alpha)                                        # nesting: counts non-decreasing in alpha for every key
    for lo, hi in zip(al, al[1:]):
        if np.any(counts_by_alpha[hi] < counts_by_alpha[lo]):
            raise CellBodyError(f"level counts at alpha {hi} fall below those at alpha {lo} for some key (the thresholds are nested)")
    return True


def cell_reusable(path, prov, expected_cell=None, grid=None):
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
    if expected_cell is not None and grid is not None:
        try:
            validate_cell_body(cell, expected_cell, grid)
        except CellBodyError as e:
            raise ProvenanceError(f"{path.name}: existing cell fails the body contract ({e}); refusing to reuse or overwrite")
    return True


def synthetic_tokens(grid):
    v = grid["validation"]; law = v["law"]
    X = C.ZipfIID(law["V"], law["s"]).sample(v["N"], max(v["L"]), np.random.default_rng(99261012))
    return X, {"synthetic": True, "law": law, "seed": 99261012}


def run_chain(spec, tok, V, h, cells, grid, out_dir, mode, lock_path, grid_path, key_start, t_log, man, man_sha, X):
    """One chain: the cell x tokenizer x h over the cached texts; every (family, gamma, colouring, L, rule) cell of the chain."""
    tag = f"{spec['tag']}__{tok}__h{h}"; N = X.shape[0]
    tokens_sha = man["cells"][spec["tag"]]["tokenizers"][tok]["sha256"] if man else "synthetic"
    todo = []
    for c in cells:
        prov = provenance(mode, lock_path, grid_path, tokens_sha, key_start, c["K"], N, slot_of(c), man_sha)
        if not cell_reusable(out_dir / c["file"], prov, dict(c, L_list=spec["L"]), grid):
            todo.append((c, prov))
    if not todo:
        t_log.write(f"{utc()} chain {tag}: every cell present with matching provenance and slot; skipped\n"); t_log.flush(); return
    t0 = time.time(); chain = S.build_chain(X, V, tag, h)
    cost = {"tag": tag, "N": int(N), "L_max": int(X.shape[1]), "V": V, "n_tuples": int(len(chain.D)), "n_contexts": int(chain.n_ctx), "build_seconds": round(time.time() - t0, 1), "cells": [], "key_loop": {}}
    t_log.write(f"{utc()} chain {tag} built: |D|={len(chain.D)} contexts={chain.n_ctx} ({cost['build_seconds']}s)\n"); t_log.flush()
    K = grid["validation"]["K"] if mode == "validation" else grid["K"]; Kf = grid["validation"]["K_fixed_h0"] if mode == "validation" else grid["K_fixed_h0"]
    keys = list(range(key_start, key_start + K)); check_keys(keys, "study2" if mode == "study" else "validation")
    gammas = grid["families"]["kgw"]["gamma"]
    combos = sorted({(c["rule"], c["L"]) for c, _ in todo if c["colouring"] in ("independent", "uniform")}, key=lambda x: (x[1], x[0]))
    inc = {rl: chain.incidence(rl[1], rl[0]) for rl in combos}
    counts = {rl: {g: np.zeros((N, K), dtype=np.uint16) for g in gammas} for rl in combos}; sums = {rl: np.zeros((N, K), dtype=np.float32) for rl in combos}
    t1 = time.time(); ch = grid["key_chunk"]
    for c0 in range(0, K, ch):
        U = S.uniforms_chunk(keys[c0:c0 + ch], chain.D); cols = {g: (U < C.green_fraction(g, V)).astype(np.float32) for g in gammas}; Sg = S.gumbel_scores(U).astype(np.float32); del U
        for rl in combos:
            for g in gammas:
                counts[rl][g][:, c0:c0 + ch] = np.asarray(inc[rl] @ cols[g]).astype(np.uint16)
            sums[rl][:, c0:c0 + ch] = np.asarray(inc[rl] @ Sg)
    cost["key_loop"] = {"seconds": round(time.time() - t1, 1), "K": K, "nnz_total": int(sum(m.nnz for m in inc.values())), "n_combos": len(combos)}
    t_log.write(f"{utc()}   {tag}: {K} keys scored for {len(combos)} (rule, L) combos in {cost['key_loop']['seconds']}s (nnz total {cost['key_loop']['nnz_total']})\n"); t_log.flush()
    fixed_cols = {}
    for c, prov in todo:
        t2 = time.time(); rl = (c["rule"], c["L"]); rng = np.random.default_rng([int(hashlib.sha256(c["file"].encode()).hexdigest()[:8], 16), 20261013])
        dep = in_deployer_subset(c, grid, spec["L"])
        if c["family"] == "kgw" and c["colouring"] == "independent":
            stats = S.kgw_cell_statistics(inc[rl], counts[rl][c["gamma"]].astype(np.float64), chain, c["gamma"], grid["alpha"], V, "independent", rng, deployer=dep, B_text=grid["text_bootstrap_B"])
        elif c["family"] == "kgw" and c["colouring"] == "fixed":
            if c["gamma"] not in fixed_cols:
                kf = list(range(key_start, key_start + Kf)); check_keys(kf, "study2" if mode == "study" else "validation"); fixed_cols[c["gamma"]] = C.colour_fixed(chain, kf, c["gamma"], V).astype(np.float64)
            inc_f = inc.get(rl) if rl in inc else chain.incidence(c["L"], c["rule"])
            stats = S.kgw_cell_statistics(inc_f, np.asarray(inc_f @ fixed_cols[c["gamma"]]), chain, c["gamma"], grid["alpha"], V, "fixed", rng, deployer=False, sim_shift=False, B_text=grid["text_bootstrap_B"])
        else:
            stats = S.gumbel_cell_statistics(inc[rl], sums[rl].astype(np.float64), chain, grid["alpha"], rng, deployer=dep, B_text=grid["text_bootstrap_B"])
        stats.update(slot_of(c)); stats.update({"V": V, "degenerate": bool(c["degenerate"]), "m": c["m"], "deployer_subset": bool(dep), "n_tuples_dict": int(len(chain.D)), "n_contexts": int(chain.n_ctx),
                                               "nnz": int(inc[rl].nnz) if rl in inc else None, "seconds": round(time.time() - t2, 1), "provenance": dict(prov, written_utc=utc())})
        (out_dir / c["file"]).write_text(json.dumps(stats, indent=1, default=float))
        cost["cells"].append({"file": c["file"], "L": c["L"], "rule": c["rule"], "family": c["family"], "colouring": c["colouring"], "gamma": c["gamma"], "K": c["K"], "nnz": stats["nnz"], "seconds": stats["seconds"], "deployer": dep})
        t_log.write(f"{utc()}   cell {c['file']} ({stats['seconds']}s)\n"); t_log.flush()
    cost["chain_seconds"] = round(time.time() - t0, 1); cost["peak_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30, 2)
    (out_dir / f"costs__{tag}.json").write_text(json.dumps(cost, indent=1))
    t_log.write(f"{utc()} chain {tag} done ({cost['chain_seconds']}s; peak RSS so far {cost['peak_rss_gb']} GB)\n"); t_log.flush()


def main(grid_path, lock_path, validation, only_chain=None, out_dir=None):
    grid = json.loads(pathlib.Path(grid_path).read_text())
    if validation:
        mode = "validation"; lock_path = None; key_start = grid["validation_key_seed_start"]; out_dir = pathlib.Path(out_dir) if out_dir else OUT / "validation"; man = None; man_sha = None
        cells = expected_cells(grid, validation=True); X_syn, _ = synthetic_tokens(grid)
        specs = [{"tag": grid["validation"]["tag"], "L": grid["validation"]["L"]}]; toks = {grid["validation"]["tokenizer_label"]: {"V": grid["validation"]["law"]["V"]}}; hs = grid["validation"]["h"]
    else:
        verify_lock(lock_path, grid_path); mode = "study"; key_start = grid["key_seed_start"]; out_dir = OUT / "cells"
        man = json.loads(pathlib.Path(TOKENS_MANIFEST).read_text()); man_sha = sha(TOKENS_MANIFEST); cells = expected_cells(grid)
        specs = grid["cells"]; toks = grid["tokenizers"]; hs = grid["h"]
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir.parent / ("validation_run.log" if validation else "run.log")).open("a") as t_log:
        t_log.write(f"start {mode} run {utc()} grid={grid_path} sha={sha(grid_path)} out={out_dir} lock={lock_path} core={sha(HERE / 's2_core.py')[:12]} s1core={sha(ROOT / 'research/study1/s1_core.py')[:12]}\n")
        for spec in specs:
            for tok, tinfo in toks.items():
                X = X_syn if validation else D.load_tokens(man, spec["tag"], tok, N=grid["N"], root=ROOT)
                for h in hs:
                    tag = f"{spec['tag']}__{tok}__h{h}"
                    if only_chain and tag != only_chain:
                        continue
                    run_chain(spec, tok, int(tinfo["V"]), h, [c for c in cells if c["tag"] == spec["tag"] and c["tokenizer"] == tok and c["h"] == h], grid, out_dir, mode, lock_path, grid_path, key_start, t_log, man, man_sha, X)
                del X
        t_log.write(f"DONE {utc()}\n")
    print("DONE", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[a.index("--grid") + 1], a[a.index("--lock") + 1] if "--lock" in a else str(OUT / "PRE_RUN_LOCK.json"), "--validation" in a,
         a[a.index("--only-chain") + 1] if "--only-chain" in a else None, a[a.index("--out-dir") + 1] if "--out-dir" in a else None)
