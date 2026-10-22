"""Study 3 runner (v1). For each width h, two passes over the cached texts (decisions D9-D11):
PASS 1 (calibration units: tokenizer x calibration cell P' x h): on the cell's 5,000 calibration texts, the per-text p-values of every
  evaluation key (23,000-23,999) and every fitting key (24,000-24,999) under both families (KGW gamma = 0.25, independent colouring;
  Gumbel-max) and both retention rules (raw, distinct) at L = 256; from them every threshold: per-key conformal and tolerance at every
  N_cal (prefixes of the calibration set) and alpha (evaluation keys); the empirical multiplier and the pooled threshold (fitting
  keys, the full set); the calibration-set bootstrap thresholds (B_cal resamples of the N_cal texts with replacement; alpha 0.01;
  N_cal 1,000 and 5,000; both per-key methods). Written to a local threshold file (git-ignored; its digest is recorded) and a JSON
  summary (committed: the scheme-level thresholds, the per-key thresholds' quantiles in z-units, provenance).
PASS 2 (evaluation units: tokenizer x evaluation cell P x h): on the cell's evaluation texts (Study 2's), the evaluation keys' p-values;
  for every threshold of every calibration cell under the same tokenizer (and, secondarily, under the other tokenizer), the per-key
  count of rejected evaluation texts (strict p < t); the fixed thresholds (nominal alpha; multiplier20 = alpha*beta); the crossed key-by-
  document bootstrap of the deployer's summaries on the diagonal (P' = P) for the registered variants; the calibration-set bootstrap's
  summaries for every same-tokenizer calibration cell. Counts are written as a compressed .npz (the record, committed) with a JSON
  (the bootstraps, the screening constants, provenance, the digests of every threshold file used).
Before any study unit runs the lock is verified against this version's canonical identity (as Study 2's runner: study name; protocol,
grid, validation, inputs, tokens-manifest and resolution paths; checkpoint R07; an ISO date; hex digests of exactly the pinned files;
approved_by, before_outcomes, final: false; the key record); every token array is verified against its manifest; an existing unit is
reused only when its provenance and slot match; otherwise the run stops (nothing is overwritten).
Usage: .venv/bin/python -u research/study3/s3_run.py --grid research/study3/grid_v0.1.json [--lock outputs/study3_v0.1/PRE_RUN_LOCK.json]
       [--validation --out-dir <fresh dir>]
--validation runs the grid's synthetic validation cells with validation keys (no lock; no real text; not study outcomes).
"""
import datetime, hashlib, json, pathlib, re, resource, sys, time
import numpy as np
from scipy.stats import norm
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study2")); sys.path.insert(0, str(ROOT / "research/study1")); sys.path.insert(0, str(ROOT / "tools"))
import s3_core as T
import s3_data as SD
import s2_core as S
import s1_core as C
from s3_keys import check_keys

HEX64 = re.compile(r"^[0-9a-f]{64}$")
STUDY = "study3_v0.1"
CHECKPOINT = "R07"
GRID_CANON = "research/study3/grid_v0.1.json"
PROTOCOL = "research/STUDY3_PROTOCOL_v0.1.md"
VALIDATION = f"outputs/{STUDY}/VALIDATION.json"
INPUTS = f"outputs/{STUDY}/INPUTS.json"
TOKENS_MANIFEST = f"outputs/{STUDY}/tokens_manifest.json"
S2_TOKENS_MANIFEST = "outputs/study2_v0.1/tokens_manifest.json"
S2_RUN_MANIFEST = "outputs/study2_v0.1/RUN_MANIFEST.json"
RESOLUTION = "research/reviews/R07_study3-protocol/RESOLUTION.md"
OUT = pathlib.Path("outputs") / STUDY
CODE_FILES = ("research/study3/s3_core.py", "research/study3/s3_run.py", "research/study3/s3_analyze.py", "research/study3/s3_validate.py", "research/study3/s3_data.py",
              "research/study3/s3_keys.py", "research/study3/s3_inputs.py", "research/study2/s2_core.py", "research/study2/s2_data.py", "research/study2/s2_keys.py",
              "research/study1/s1_core.py", "tools/key_policy.py", "tools/corpora_access.py")
PINNED = tuple(sorted(set(CODE_FILES) | {GRID_CANON, PROTOCOL, VALIDATION, INPUTS, TOKENS_MANIFEST, S2_TOKENS_MANIFEST, S2_RUN_MANIFEST}))
LOCK_FIELDS = ("study", "date", "approved_by", "before_outcomes", "final", "grid", "protocol", "validation", "inputs", "tokens_manifest", "hashes", "review", "keys")
PROVENANCE_FIELDS = ("study", "mode", "lock_sha256", "grid_sha256", "core_sha256", "run_sha256", "tokens_manifest_sha256", "tokens_sha256", "key_eval_start", "K", "key_fit_start", "K_fit", "N")
FAMILIES = ("kgw", "gumbel")
VARIANTS_SAME = None   # set from the grid (variant_names)


class LockError(RuntimeError):
    pass


class ProvenanceError(RuntimeError):
    pass


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def utc():
    return f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}"


# ---------------- the inventory ----------------
def variant_names(ncals):
    """The threshold variants carried per calibration source (same tokenizer), in storage order."""
    return ["empirical", "pooled"] + [f"conformal@{n}" for n in ncals] + [f"tolerance@{n}" for n in ncals]


def cross_variant_names(grid):
    sel = sorted({1000, 5000} & set(grid["N_cal"])) or [max(grid["N_cal"])]
    return ["empirical", "pooled"] + [f"conformal@{n}" for n in sel] + [f"tolerance@{n}" for n in sel]


def spec_of(grid, validation):
    if validation:
        v = grid["validation"]; cells = [f"{v['tag']}_{i}" for i in range(v["n_cells"])]; toks = {v["tokenizer_label"]: {"V": v["law"]["V"]}}
        return {"cells": cells, "toks": toks, "h": v["h"], "K": v["K"], "K_fit": v["K_fit"], "N_cal": v["N_cal"], "N_cal_set": v["N_cal_set"], "N_eval": v["N_eval"]}
    return {"cells": grid["cells"], "toks": grid["tokenizers"], "h": grid["h"], "K": grid["K"], "K_fit": grid["K_fit"], "N_cal": grid["N_cal"], "N_cal_set": grid["N_cal_set"], "N_eval": grid["N_eval"]}


def unit_name(kind, tok, tag, h):
    return f"{kind}__{tok}__{tag}__h{h}"


def expected_units(grid, validation=False):
    sp = spec_of(grid, validation)
    return [{"kind": k, "tokenizer": t, "tag": c, "h": h} for h in sp["h"] for k in ("cal", "eval") for t in sp["toks"] for c in sp["cells"]]


# ---------------- lock ----------------
def verify_lock(lock_path, grid_path, root="."):
    """Explicit schema and canonical-identity check (Study 2's, for this version); raises LockError naming the first violation."""
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
        raise LockError("lock must carry before_outcomes: true and final: false (Study 3 opens no held-out text)")
    if not isinstance(lock["approved_by"], str) or lock["approved_by"].strip() != "Yichen":
        raise LockError("lock must be approved_by 'Yichen'")
    try:
        d = datetime.date.fromisoformat(str(lock["date"]))
    except ValueError:
        raise LockError(f"lock date {lock['date']!r} is not an ISO date")
    if d < datetime.date(2026, 10, 13):
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
    if ks.get("eval_start") != grid["key_eval_start"] or ks.get("K") != grid["K"] or ks.get("fit_start") != grid["key_fit_start"] or ks.get("K_fit") != grid["K_fit"]:
        raise LockError("lock key record does not match the grid")
    check_keys(range(grid["key_eval_start"], grid["key_eval_start"] + grid["K"]), "study3_eval")
    check_keys(range(grid["key_fit_start"], grid["key_fit_start"] + grid["K_fit"]), "study3_fit")
    man = json.loads((root / TOKENS_MANIFEST).read_text())
    if man.get("N_cal") != grid["N_cal_set"] or man.get("L") != grid["L"] or man.get("N_eval") != grid["N_eval"] or man.get("N_eval_gutenberg") != grid["N_eval_gutenberg"]:
        raise LockError("the tokens manifest's sizes differ from the grid's")
    if man.get("study2_manifest") != S2_TOKENS_MANIFEST or man.get("study2_manifest_sha256") != sha(root / S2_TOKENS_MANIFEST):
        raise LockError("the tokens manifest does not bind Study 2's token manifest")
    for tag in grid["cells"]:
        if tag not in man["cells"]:
            raise LockError(f"the tokens manifest lacks the cell {tag}")
        for tok in grid["tokenizers"]:
            if tok not in man["cells"][tag]["tokenizers"]:
                raise LockError(f"the tokens manifest lacks {tag} under {tok}")
            if man["tokenizers"][tok]["V"] != grid["tokenizers"][tok]["V"]:
                raise LockError(f"V for {tok} differs between the manifest and the grid")
    return lock


def provenance(mode, lock_path, grid_path, tokens_sha, grid, sp, unit, man_sha, N):
    return {"study": STUDY, "mode": mode, "lock_sha256": sha(lock_path) if lock_path else None, "grid_sha256": sha(grid_path), "core_sha256": sha(HERE / "s3_core.py"), "run_sha256": sha(HERE / "s3_run.py"),
            "tokens_manifest_sha256": man_sha, "tokens_sha256": tokens_sha, "key_eval_start": int(grid["validation_key_seed_start"] if mode == "validation" else grid["key_eval_start"]), "K": int(sp["K"]),
            "key_fit_start": int(grid["validation_key_seed_start"] + 500000 if mode == "validation" else grid["key_fit_start"]), "K_fit": int(sp["K_fit"]), "N": int(N), "unit": dict(unit)}


def unit_reusable(json_path, prov):
    json_path = pathlib.Path(json_path)
    if not json_path.exists():
        return False
    try:
        d = json.loads(json_path.read_text()); old = d.get("provenance", {})
    except Exception as e:
        raise ProvenanceError(f"{json_path.name}: unreadable existing unit ({e})")
    diff = [f for f in PROVENANCE_FIELDS if old.get(f) != prov.get(f)]
    if old.get("unit") != prov["unit"]:
        diff.append("unit")
    if "threshold_digests" in prov and old.get("threshold_digests") != prov["threshold_digests"]:
        diff.append("threshold_digests")
    if diff:
        raise ProvenanceError(f"{json_path.name}: existing unit has foreign provenance in {diff}; refusing to reuse or overwrite")
    if prov["unit"]["kind"] == "eval":
        files = [(json_path.with_suffix(".npz"), d.get("npz_sha256"))]
    else:
        t, b = _cal_files(d, json_path.parent); files = [(t, d.get("thresholds_sha256")), (b, d.get("boot_sha256"))]
    for f, dig in files:
        if not f.exists() or sha(f) != dig:
            raise ProvenanceError(f"{json_path.name}: its array file {f.name} is missing or differs from the recorded digest; refusing to reuse or overwrite")
    return True


# ---------------- scoring ----------------
def unit_pvalues(X, V, h, keys, grid, chunk):
    """Per-text p-values (N x len(keys) float64) for every (family, rule) at the full window length; every text must retain a tuple."""
    chain = S.build_chain(X, V, "unit", h); L = X.shape[1]; gamma = grid["families"]["kgw"]["gamma"]
    g = C.green_fraction(gamma, V)
    if g != gamma:
        raise RuntimeError(f"g = {g} differs from gamma = {gamma} at V = {V} (gamma V must be an integer)")
    inc = {r: chain.incidence(L, r) for r in grid["rules"]}; M = {r: np.asarray(inc[r].sum(axis=1)).ravel() for r in grid["rules"]}
    for r in grid["rules"]:
        if (M[r] <= 0).any():
            raise RuntimeError(f"a text retains no tuple under rule {r}")
    N = X.shape[0]; K = len(keys); P = {(f, r): np.empty((N, K), dtype=np.float64) for f in FAMILIES for r in grid["rules"]}
    for c0 in range(0, K, chunk):
        U = S.uniforms_chunk(keys[c0:c0 + chunk], chain.D); col = (U < g).astype(np.float64); Sg = S.gumbel_scores(U); del U
        for r in grid["rules"]:
            P[("kgw", r)][:, c0:c0 + chunk] = T.pvalues_kgw(np.asarray(inc[r] @ col), M[r], gamma)
            P[("gumbel", r)][:, c0:c0 + chunk] = T.pvalues_gumbel(np.asarray(inc[r] @ Sg), M[r])
    info = {"n_tuples": int(len(chain.D)), "nnz": {r: int(inc[r].nnz) for r in grid["rules"]}, "mean_M": {r: float(M[r].mean()) for r in grid["rules"]}}
    return P, info


def zq(t, alpha):
    """Threshold summaries across keys in z-units: z(t) = Phi_bar^-1(t) over the keys with a positive threshold (n_positive; the never-reject
    thresholds are counted as n_abstain and excluded from the quantiles), and the null-side cost z(t) - z_alpha with the same denominator."""
    t = np.asarray(t, dtype=np.float64); n_abs = int((t <= 0).sum()); t = t[t > 0]; za = float(norm.isf(alpha))
    out = {"n_positive": int(len(t)), "n_abstain": n_abs, "z_alpha": za}
    if not len(t):
        return out | {k: None for k in ("q05", "q50", "q95", "mean", "cost_q05", "cost_q50", "cost_q95", "cost_mean")}
    z = norm.isf(t); q = {"q05": float(np.quantile(z, 0.05)), "q50": float(np.quantile(z, 0.5)), "q95": float(np.quantile(z, 0.95)), "mean": float(z.mean())}
    return out | q | {f"cost_{k}": v - za for k, v in q.items()}


def eval_tokens_sha(X):
    """The digest of an evaluation array as the runner records it (the cut window, contiguous int32 bytes)."""
    return hashlib.sha256(np.ascontiguousarray(X).tobytes()).hexdigest()


# ---------------- pass 1 ----------------
def run_cal_unit(X, V, h, tok, tag, grid, sp, mode, out_dir, local_dir, keys_e, keys_f, prov, t_log):
    t0 = time.time(); Ncal = sp["N_cal"]
    if X.shape[0] != sp["N_cal_set"]:
        raise RuntimeError(f"{tag}: calibration set has {X.shape[0]} texts, not {sp['N_cal_set']}")
    Pe, info = unit_pvalues(X, V, h, keys_e, grid, grid["key_chunk"]); Pf, _ = unit_pvalues(X, V, h, keys_f, grid, grid["key_chunk"])
    arrays = {}; summ = {}
    rng = np.random.default_rng([int(hashlib.sha256(unit_name("cal", tok, tag, h).encode()).hexdigest()[:8], 16), 20261014])
    cb = grid["cal_bootstrap"]
    for f in FAMILIES:
        for r in grid["rules"]:
            fr = f"{f}|{r}"; summ[fr] = {"scheme": {}, "per_key_z": {}}
            for a in grid["alpha"]:
                thr = T.per_key_thresholds(Pe[(f, r)], a, Ncal, grid["delta"])
                for (meth, n), (t, j) in thr.items():
                    arrays[f"{fr}|{meth}@{n}|{a}"] = t; summ[fr]["per_key_z"][f"{meth}@{n}|{a}"] = {"j": j, "z": zq(t, a)}
                t_emp, kap, det = T.empirical_multiplier_threshold(Pf[(f, r)], a, grid["beta"]); t_pool = T.pooled_threshold(Pf[(f, r)], a)
                arrays[f"{fr}|empirical|{a}"] = np.array([t_emp]); arrays[f"{fr}|pooled|{a}"] = np.array([t_pool])
                summ[fr]["scheme"][str(a)] = {"t_emp": t_emp, "kappa_emp": kap, "emp_detail": det, "t_pool": t_pool, "z_emp": float(norm.isf(t_emp)) if t_emp > 0 else None, "z_pool": float(norm.isf(t_pool)) if t_pool > 0 else None}
            # the calibration-set bootstrap (per-key methods; alpha and N_cal from the grid)
            a = cb["alpha"]
            for n in [m for m in cb["N_cal"] if m in Ncal]:
                jc, jt = T.j_conformal(n, a), T.j_tolerance(n, a, grid["delta"]); bc = np.empty((cb["B"], len(keys_e))); bt = np.empty_like(bc)
                for b in range(cb["B"]):
                    sub = Pe[(f, r)][rng.integers(0, n, size=n)]
                    bc[b] = T.kth_smallest(sub, jc); bt[b] = T.kth_smallest(sub, jt)
                arrays[f"{fr}|boot|conformal@{n}|{a}"] = bc; arrays[f"{fr}|boot|tolerance@{n}|{a}"] = bt
    del Pe, Pf
    # the thresholds (per-key and scheme-level; the record Study 4 takes) are written beside the unit record and committed; the calibration-set
    # bootstrap's thresholds (used only for the summaries the evaluation units store) stay local, with their digest recorded
    thr = {k: v for k, v in arrays.items() if "|boot|" not in k}; boot = {k: v for k, v in arrays.items() if "|boot|" in k}
    name = unit_name('cal', tok, tag, h); tnpz = out_dir / f"{name}__thresholds.npz"; bnpz = local_dir / f"{name}__boot.npz"
    np.savez_compressed(tnpz, **thr); np.savez_compressed(bnpz, **boot)
    rec = {"unit": prov["unit"], "info": info, "summary": summ, "N_C": int(X.shape[0]), "K": int(len(keys_e)), "K_fit": int(len(keys_f)), "alphas": list(grid["alpha"]), "N_cal": list(Ncal),
           "methods_per_key": list(grid["methods_per_key"]), "methods_scheme": list(grid["methods_scheme"]),
           "thresholds_file": str(tnpz.relative_to(ROOT)) if tnpz.is_relative_to(ROOT) else str(tnpz), "thresholds_sha256": sha(tnpz),
           "boot_file": str(bnpz), "boot_sha256": sha(bnpz), "seconds": round(time.time() - t0, 1), "provenance": dict(prov, written_utc=utc())}
    (out_dir / f"{name}.json").write_text(json.dumps(rec, indent=0, default=float))
    t_log.write(f"{utc()}   pass 1 {name} ({rec['seconds']}s)\n"); t_log.flush()
    return arrays


def _cal_files(rec, out_dir):
    t = pathlib.Path(rec["thresholds_file"]); t = t if t.is_absolute() else (ROOT / t)
    if not t.exists():
        t = out_dir / pathlib.Path(rec["thresholds_file"]).name
    return t, pathlib.Path(rec["boot_file"])


def load_thresholds(out_dir, tok, tag, h):
    rec = json.loads((out_dir / f"{unit_name('cal', tok, tag, h)}.json").read_text()); t, b = _cal_files(rec, out_dir)
    if not t.exists() or sha(t) != rec["thresholds_sha256"]:
        raise ProvenanceError(f"thresholds file {t} is missing or differs from its recorded digest")
    if not b.exists() or sha(b) != rec["boot_sha256"]:
        raise ProvenanceError(f"bootstrap thresholds file {b} is missing or differs from its recorded digest")
    out = {}
    for f in (t, b):
        z = np.load(f); out.update({k: z[k] for k in z.files})
    return out, {"thresholds": rec["thresholds_sha256"], "boot": rec["boot_sha256"]}


# ---------------- pass 2 ----------------
def run_eval_unit(X, V, h, tok, tag, grid, sp, mode, out_dir, thr_all, keys_e, prov, t_log):
    t0 = time.time(); N_E = X.shape[0]; K = len(keys_e); alphas = grid["alpha"]
    Pe, info = unit_pvalues(X, V, h, keys_e, grid, grid["key_chunk"])
    vs, vx = variant_names(sp["N_cal"]), cross_variant_names(grid); toks = list(sp["toks"])
    other = [t for t in toks if t != tok] if (grid.get("cross_tokenizer") and mode in ("study", "probe")) else []
    arrays = {}; js = {"crossed": {}, "cal_boot": {}, "screen": {}, "N_E": int(N_E)}
    rng = np.random.default_rng([int(hashlib.sha256(unit_name("eval", tok, tag, h).encode()).hexdigest()[:8], 16), 20261015])
    for a in alphas:
        js["screen"][str(a)] = {k: v for k, v in T.screening(np.zeros(1), N_E, a, grid["beta"]).items() if k in ("c", "r", "b")}
    cbg = grid["crossed_bootstrap"]; cb = grid["cal_bootstrap"]
    for f in FAMILIES:
        for r in grid["rules"]:
            fr = f"{f}|{r}"; P = Pe[(f, r)]; Ps = T.sort_columns(P)
            fixed = np.empty((2, len(alphas), K), dtype=np.uint16)
            for ia, a in enumerate(alphas):
                fixed[:, ia, :] = T.counts_below(Ps, np.array([[a], [a * grid["beta"]]]))
            arrays[f"{fr}|fixed"] = fixed
            same = np.empty((len(sp["cells"]), len(vs), len(alphas), K), dtype=np.uint16)
            for ic, tagc in enumerate(sp["cells"]):
                th = thr_all[(tok, tagc)]
                for ia, a in enumerate(alphas):
                    Tm = np.stack([np.broadcast_to(th[f"{fr}|{v}|{a}"], (K,)) for v in vs])
                    same[ic, :, ia, :] = T.counts_below(Ps, Tm)
            arrays[f"{fr}|same"] = same
            if other:
                a = cb["alpha"]; cross = np.empty((len(other), len(sp["cells"]), len(vx), K), dtype=np.uint16)
                for io, ot in enumerate(other):
                    for ic, tagc in enumerate(sp["cells"]):
                        th = thr_all[(ot, tagc)]
                        Tm = np.stack([np.broadcast_to(th[f"{fr}|{v}|{a}"], (K,)) for v in vx]); cross[io, ic] = T.counts_below(Ps, Tm)
                arrays[f"{fr}|cross"] = cross
            # crossed key-by-document bootstrap on the diagonal (P' = P), registered variants, alpha from the grid
            a = cbg["alpha"]; th = thr_all[(tok, tag)]; js["crossed"][fr] = {}
            for v in cbg["variants"]:
                if "@" in v and int(v.split("@")[-1]) not in sp["N_cal"]:
                    continue
                if v == "nominal":
                    t = np.full(K, a)
                elif v == "multiplier20":
                    t = np.full(K, a * grid["beta"])
                else:
                    t = np.broadcast_to(th[f"{fr}|{v}|{a}"], (K,))
                js["crossed"][fr][v] = S.crossed_bootstrap(P < t[None, :], a, rng, B=cbg["B"])
            # calibration-set bootstrap summaries for every same-tokenizer calibration cell
            a = cb["alpha"]; js["cal_boot"][fr] = {}
            for tagc in sp["cells"]:
                th = thr_all[(tok, tagc)]; js["cal_boot"][fr][tagc] = {}
                for n in cb["N_cal"]:
                    if n not in sp["N_cal"]:
                        continue
                    for meth in grid["methods_per_key"]:
                        cnt = T.counts_below(Ps, th[f"{fr}|boot|{meth}@{n}|{a}"]) / N_E           # B x K levels
                        js["cal_boot"][fr][tagc][f"{meth}@{n}"] = {"key_mean": cnt.mean(axis=1).tolist(), "sd": cnt.std(axis=1, ddof=1).tolist(),
                                                                    "share_above_alpha": (cnt > a).mean(axis=1).tolist(), "q99": np.quantile(cnt, 0.99, axis=1).tolist()}
            del Ps
    del Pe
    npz = out_dir / f"{unit_name('eval', tok, tag, h)}.npz"; np.savez_compressed(npz, **arrays)
    rec = {"unit": prov["unit"], "info": info, "variants_same": vs, "variants_cross": vx, "cross_tokenizers": other, "cal_sources": list(sp["cells"]), "alphas": alphas, "fixed_variants": ["nominal", "multiplier20"],
           "npz_sha256": sha(npz), "threshold_digests": prov.get("threshold_digests"), **js, "seconds": round(time.time() - t0, 1), "provenance": dict(prov, written_utc=utc())}
    (out_dir / f"{unit_name('eval', tok, tag, h)}.json").write_text(json.dumps(rec, indent=0, default=float))
    t_log.write(f"{utc()}   pass 2 {unit_name('eval', tok, tag, h)} ({rec['seconds']}s)\n"); t_log.flush()


# ---------------- synthetic validation cells ----------------
def synthetic_sets(grid):
    """Validation cells: three Zipf laws at the real vocabulary size that share the vocabulary to different degrees (cell 0 the base
    law; cell 1 the same law with the ranks of the tail beyond the 200 most frequent ids permuted; cell 2 a fully permuted law), so
    that the cross-cell machinery sees a near-identical, a partly shared and a disjoint-head pair. Calibration and evaluation sets are
    independent draws (seed 99261013)."""
    v = grid["validation"]; law = v["law"]; Vv = law["V"]; rng0 = np.random.default_rng(99261013)
    base = C.ZipfIID(Vv, law["s"]); perms = [np.arange(Vv)]
    p1 = np.arange(Vv); p1[200:] = 200 + rng0.permutation(Vv - 200); perms.append(p1); perms.append(rng0.permutation(Vv))
    out = {}
    for i in range(v["n_cells"]):
        tag = f"{v['tag']}_{i}"; pm = perms[i % len(perms)]
        XE = pm[base.sample(v["N_eval"], grid["L"], np.random.default_rng([99261013, i, 1]))].astype(np.int32)
        XC = pm[base.sample(v["N_cal_set"], grid["L"], np.random.default_rng([99261013, i, 2]))].astype(np.int32)
        out[tag] = (XE, XC)
    return out


def main(grid_path, lock_path, validation, out_dir=None):
    grid = json.loads(pathlib.Path(grid_path).read_text()); sp = spec_of(grid, validation)
    if validation:
        mode = "validation"; lock_path = None; out_dir = pathlib.Path(out_dir) if out_dir else OUT / "validation"; man = None; man_sha = None
        syn = synthetic_sets(grid); ke = grid["validation_key_seed_start"]; kf = ke + 500000
        keys_e = list(range(ke, ke + sp["K"])); keys_f = list(range(kf, kf + sp["K_fit"])); check_keys(keys_e, "validation"); check_keys(keys_f, "validation")
    else:
        verify_lock(lock_path, grid_path); mode = "study"; out_dir = OUT / "cells"
        man = json.loads(pathlib.Path(TOKENS_MANIFEST).read_text()); man_sha = sha(TOKENS_MANIFEST)
        keys_e = list(range(grid["key_eval_start"], grid["key_eval_start"] + grid["K"])); keys_f = list(range(grid["key_fit_start"], grid["key_fit_start"] + grid["K_fit"]))
        check_keys(keys_e, "study3_eval"); check_keys(keys_f, "study3_fit")
    out_dir.mkdir(parents=True, exist_ok=True); local_dir = out_dir.parent / ("validation_thresholds" if validation else "thresholds_local"); local_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir.parent / ("validation_run.log" if validation else "run.log")).open("a") as t_log:
        t_log.write(f"start {mode} run {utc()} grid={grid_path} sha={sha(grid_path)} out={out_dir} lock={lock_path} core={sha(HERE / 's3_core.py')[:12]}\n")
        for h in sp["h"]:
            thr_all = {}; thr_dig = {}
            for tok, tinfo in sp["toks"].items():
                V = int(tinfo["V"])
                for tag in sp["cells"]:
                    unit = {"kind": "cal", "tokenizer": tok, "tag": tag, "h": h}
                    if validation:
                        X = syn[tag][1]; tsha = "synthetic"
                    else:
                        X = SD.load_cal(tag, tok, man); tsha = man["cells"][tag]["tokenizers"][tok]["sha256"]
                    prov = provenance(mode, lock_path, grid_path, tsha, grid, sp, unit, man_sha, X.shape[0])
                    js = out_dir / f"{unit_name('cal', tok, tag, h)}.json"
                    if unit_reusable(js, prov):
                        t_log.write(f"{utc()}   pass 1 {js.stem}: present with matching provenance; reused\n"); t_log.flush()
                    else:
                        run_cal_unit(X, V, h, tok, tag, grid, sp, mode, out_dir, local_dir, keys_e, keys_f, prov, t_log)
                    thr_all[(tok, tag)], thr_dig[f"{tok}|{tag}"] = load_thresholds(out_dir, tok, tag, h)
                    del X
            for tok, tinfo in sp["toks"].items():
                V = int(tinfo["V"])
                for tag in sp["cells"]:
                    unit = {"kind": "eval", "tokenizer": tok, "tag": tag, "h": h}
                    if validation:
                        X = syn[tag][0]; tsha = "synthetic"
                    else:
                        X = SD.load_eval(tag, tok, man); tsha = hashlib.sha256(np.ascontiguousarray(X).tobytes()).hexdigest()
                    prov = provenance(mode, lock_path, grid_path, tsha, grid, sp, unit, man_sha, X.shape[0]) | {"threshold_digests": thr_dig}
                    js = out_dir / f"{unit_name('eval', tok, tag, h)}.json"
                    if unit_reusable(js, prov):
                        t_log.write(f"{utc()}   pass 2 {js.stem}: present with matching provenance; reused\n"); t_log.flush()
                    else:
                        run_eval_unit(X, V, h, tok, tag, grid, sp, mode, out_dir, thr_all, keys_e, prov, t_log)
                    del X
            t_log.write(f"{utc()} h = {h} done (peak RSS so far {round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 30, 2)} GB)\n"); t_log.flush()
            del thr_all
        t_log.write(f"DONE {utc()}\n")
    print("DONE", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[a.index("--grid") + 1], a[a.index("--lock") + 1] if "--lock" in a else str(OUT / "PRE_RUN_LOCK.json"), "--validation" in a, a[a.index("--out-dir") + 1] if "--out-dir" in a else None)
