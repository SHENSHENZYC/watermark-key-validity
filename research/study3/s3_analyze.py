"""Study 3 analyzer (v1): the inventory gate, the body contract, the pre-registered rules T1, T2 and REP, and the descriptive blocks.
Study mode requires the verified lock before any unit is read; pilot mode reads a validation directory (synthetic cells, validation keys)
with a pilot INPUTS file and is not a study outcome.
- Inventory (R07 F1): exactly the expected pass-1 (cal) and pass-2 (eval) units; every unit's provenance equal, field by field, to the
  provenance derived from the verified lock, the canonical grid, the pinned code and the manifests; every eval unit's counts file at its
  digest, its threshold map covering exactly the registered sources with digests equal to the pass-1 records' (and equal between the
  record and its provenance copy); every cal unit's committed thresholds file at its digest and its body under the calibration contract.
- Body contracts (R07 F1-F2): see `validate_cal_body` and `validate_eval_body` (N_E bound to the registered size; exact axis metadata;
  exactly the expected arrays with the registered shapes and dtype; counts in [0, N_E] and nested across alpha; finite values in range
  for every bootstrap summary and screening constant; the calibration thresholds finite in [0, 1], nested across alpha, with the
  abstention convention and the scheme summaries equal to the arrays).
- T1 (adequacy of the calibrated-threshold predictor; pass/fail): over the eligible primary pairs (KGW; raw and distinct; h in {1, 2};
  both tokenizers; every ordered (calibration cell, evaluation cell) pair within a tokenizer, the diagonal included; per-key conformal;
  N_cal in {1,000, 5,000}; alpha = 0.01; eligible when the predicted theory share is >= 0.75 and the prediction carries no flag), the
  ratio SD_obs / SD_pred with its key-bootstrap 95% interval: consistent inside [2/3, 3/2], inconsistent when disjoint from it,
  unresolved otherwise; pass iff >= 30 resolved and >= 80% of the resolved consistent.
- T2 (does per-key calibration change the dispersion as predicted?; pass/fail): over the same block, the pairs whose predicted ratio
  R_pred = SD_pred(conformal) / SD_pred(nominal on the evaluation set) lies outside [2/3, 3/2] (material); the observed ratio
  R_obs = SD_obs(conformal) / SD_obs(nominal) (the same keys and texts) with its paired key-bootstrap 95% interval: agree when the
  interval excludes 1 on the predicted side, disagree when it excludes 1 on the other side, unresolved when it contains 1; pass iff
  >= 30 resolved and >= 90% of the resolved agree.
- REP (integrity): for every (tokenizer, evaluation cell except Gutenberg, h, rule) of the KGW family at alpha = 0.01, the nominal
  across-key SD with Study 3's keys against Study 2's observed SD on the same texts with Study 2's keys (Study 2's record, its
  inventory digest checked against its pinned run manifest): a gross failure when |SD3 - SD2| > 6 sqrt(se3^2 + se2^2) + 1e-12; REP
  passes iff no gross failure (a failure is an implementation audit, not a result).
Usage: .venv/bin/python -u research/study3/s3_analyze.py --grid research/study3/grid_v0.1.json --lock outputs/study3_v0.1/PRE_RUN_LOCK.json
       .venv/bin/python -u research/study3/s3_analyze.py --grid research/study3/grid_v0.1.json --pilot <validation dir> --pilot-inputs <file>
"""
import hashlib, json, pathlib, sys
import numpy as np
from scipy.stats import binom, norm
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study2")); sys.path.insert(0, str(ROOT / "research/study1"))
import s3_core as T
import s3_run as R
import s3_data as SD

FAMILIES = R.FAMILIES
REP_TOL = 1e-12


class InventoryError(RuntimeError):
    pass


class BodyError(RuntimeError):
    pass


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def rng_for(name, salt=20261016):
    return np.random.default_rng([int(hashlib.sha256(name.encode()).hexdigest()[:8], 16), salt])


# ---------------- inventory and body contract ----------------
def _is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x)


def expected_provenance(unit, grid, sp, mode, lock_path, man, man_sha, root=ROOT):
    """The provenance a unit of the registered execution must carry, derived from the verified lock, the canonical grid, the pinned code and
    the manifests (never from the unit itself): the runner's `provenance` with the expected token digest and size (R07 F1)."""
    tok, tag, kind = unit["tokenizer"], unit["tag"], unit["kind"]
    if mode == "study":
        if kind == "cal":
            tsha = man["cells"][tag]["tokenizers"][tok]["sha256"]; N = sp["N_cal_set"]
        else:
            tsha = R.eval_tokens_sha(SD.load_eval(tag, tok, man, root=root)); N = man["cells"][tag]["eval_n"]
    else:
        tsha = "synthetic"; N = sp["N_cal_set"] if kind == "cal" else sp["N_eval"]
    return R.provenance(mode, lock_path, root / R.GRID_CANON, tsha, grid, sp, unit, man_sha, N)


def load_inventory(cells_dir, grid, mode, lock_path=None, validation=False):
    """The inventory gate (R07 F1): exactly the expected units; every unit's provenance equal, field by field, to the provenance derived
    from the lock, grid, code and manifests; every evaluation unit's counts file at its digest, its threshold map covering exactly the
    registered sources with digests equal to the pass-1 records' (and equal between its top-level and provenance copies); every
    calibration unit's committed thresholds file at its digest and its body under the calibration contract. Returns (records, spec,
    expected provenance per unit)."""
    cells_dir = pathlib.Path(cells_dir); sp = R.spec_of(grid, validation); exp_units = R.expected_units(grid, validation)
    names = {R.unit_name(u["kind"], u["tokenizer"], u["tag"], u["h"]) for u in exp_units}
    present = {p.stem for p in cells_dir.glob("*.json")}
    if present != names:
        raise InventoryError(f"inventory mismatch: missing {sorted(names - present)[:5]}, extra {sorted(present - names)[:5]}")
    if mode == "study":
        if lock_path is None:
            raise InventoryError("study mode needs the verified lock")
        man = json.loads((ROOT / R.TOKENS_MANIFEST).read_text()); man_sha = sha(ROOT / R.TOKENS_MANIFEST)
    else:
        man = None; man_sha = None
    recs = {}; exp = {}
    for u in exp_units:
        n = R.unit_name(u["kind"], u["tokenizer"], u["tag"], u["h"]); d = json.loads((cells_dir / f"{n}.json").read_text()); pv = d.get("provenance") or {}
        e = expected_provenance(u, grid, sp, mode, lock_path, man, man_sha); exp[n] = e
        bad = [f for f in R.PROVENANCE_FIELDS if pv.get(f) != e.get(f)]
        if pv.get("unit") != u:
            bad.append("unit")
        if bad:
            raise InventoryError(f"{n}: provenance differs from the registered execution in {bad}")
        recs[n] = d
    sources = {f"{t}|{c}" for t in sp["toks"] for c in sp["cells"]}
    for u in exp_units:
        n = R.unit_name(u["kind"], u["tokenizer"], u["tag"], u["h"]); d = recs[n]
        if u["kind"] == "cal":
            if not isinstance(d.get("summary"), dict) or not isinstance(d.get("info"), dict):
                raise InventoryError(f"{n}: the calibration record lacks its summary or info")
            t = cells_dir / pathlib.Path(str(d.get("thresholds_file", ""))).name
            if not t.exists() or sha(t) != d.get("thresholds_sha256"):
                raise InventoryError(f"{n}: the committed thresholds file is missing or differs from its digest")
            z = np.load(t); validate_cal_body(d, {k: z[k] for k in z.files}, grid, sp)
        else:
            npz = cells_dir / f"{n}.npz"
            if not npz.exists() or sha(npz) != d.get("npz_sha256"):
                raise InventoryError(f"{n}: its counts file is missing or differs from the recorded digest")
            td = d.get("threshold_digests")
            if not isinstance(td, dict) or set(td) != sources:
                raise InventoryError(f"{n}: the threshold map does not cover exactly the registered sources")
            if (d.get("provenance") or {}).get("threshold_digests") != td:
                raise InventoryError(f"{n}: the threshold map differs between the record and its provenance copy")
            for src, dig in td.items():
                tok, tag = src.split("|"); c = recs[R.unit_name("cal", tok, tag, u["h"])]
                if not isinstance(dig, dict) or set(dig) != {"thresholds", "boot"} or c.get("thresholds_sha256") != dig["thresholds"] or c.get("boot_sha256") != dig["boot"]:
                    raise InventoryError(f"{n}: threshold digests of {src} differ from the pass-1 record")
    return recs, sp, exp


def validate_cal_body(rec, arrays, grid, sp):
    """The calibration-unit contract (R07 F1): the sizes and axes as registered; exactly the expected threshold arrays, finite in [0, 1],
    per-key arrays of length K and scheme scalars; the empirical multiplier's threshold at most alpha; every variant's threshold
    non-decreasing in alpha; the abstention convention (an order index of 0 means an all-zero threshold array) with the recorded index
    equal to its recomputation; the scheme summaries equal to the arrays."""
    K = sp["K"]
    for f, v in (("N_C", sp["N_cal_set"]), ("K", K), ("K_fit", sp["K_fit"]), ("alphas", list(grid["alpha"])), ("N_cal", list(sp["N_cal"])), ("methods_per_key", list(grid["methods_per_key"])), ("methods_scheme", list(grid["methods_scheme"]))):
        if rec.get(f) != v:
            raise BodyError(f"calibration record field {f} is {rec.get(f)!r}; expected {v!r}")
    expected = {}
    for fam in FAMILIES:
        for r in grid["rules"]:
            fr = f"{fam}|{r}"
            for a in grid["alpha"]:
                for m in grid["methods_per_key"]:
                    for n in sp["N_cal"]:
                        expected[f"{fr}|{m}@{n}|{a}"] = (K,)
                for m in grid["methods_scheme"]:
                    expected[f"{fr}|{m}|{a}"] = (1,)
    if set(arrays) != set(expected):
        raise BodyError(f"thresholds arrays differ from the expected set: missing {sorted(set(expected) - set(arrays))[:3]}, extra {sorted(set(arrays) - set(expected))[:3]}")
    for k, shape in expected.items():
        a = arrays[k]
        if a.shape != shape or not np.issubdtype(a.dtype, np.floating):
            raise BodyError(f"thresholds array {k} has shape {a.shape} dtype {a.dtype}; expected {shape} float")
        if not np.isfinite(a).all() or (a < 0).any() or (a > 1).any():
            raise BodyError(f"thresholds array {k} holds a non-finite value or one outside [0, 1]")
    alphas_sorted = sorted(grid["alpha"])
    for fam in FAMILIES:
        for r in grid["rules"]:
            fr = f"{fam}|{r}"; summ = (rec.get("summary") or {}).get(fr)
            if not isinstance(summ, dict) or not isinstance(summ.get("scheme"), dict) or not isinstance(summ.get("per_key_z"), dict):
                raise BodyError(f"calibration summary for {fr} missing or malformed")
            variants = [f"{m}@{n}" for m in grid["methods_per_key"] for n in sp["N_cal"]] + list(grid["methods_scheme"])
            for vname in variants:
                prev = None
                for a in alphas_sorted:
                    t = arrays[f"{fr}|{vname}|{a}"]
                    if prev is not None and (t + 1e-15 < prev).any():
                        raise BodyError(f"thresholds {fr} {vname} decrease from alpha {prev_a} to {a}")
                    prev, prev_a = t, a
            for a in grid["alpha"]:
                for m in grid["methods_per_key"]:
                    for n in sp["N_cal"]:
                        j = T.j_conformal(n, a) if m == "conformal" else T.j_tolerance(n, a, grid["delta"]); z = summ["per_key_z"].get(f"{m}@{n}|{a}") or {}
                        if z.get("j") != j:
                            raise BodyError(f"recorded order index for {fr} {m}@{n} alpha {a} is {z.get('j')}; expected {j}")
                        t = arrays[f"{fr}|{m}@{n}|{a}"]
                        if j == 0 and (t != 0).any():
                            raise BodyError(f"{fr} {m}@{n} alpha {a}: an abstaining method must carry an all-zero threshold")
                        # the z summary (R07 F10): every registered entry, abstaining ones included, equal to its recomputation from the committed array
                        zs = z.get("z"); ref = R.zq(t, a)
                        if not isinstance(zs, dict) or set(zs) != set(ref):
                            raise BodyError(f"{fr} {m}@{n} alpha {a}: the z summary is missing or lacks the promised fields")
                        for k_, rv in ref.items():
                            sv = zs.get(k_)
                            if rv is None:
                                ok = sv is None
                            elif isinstance(rv, int):
                                ok = isinstance(sv, int) and not isinstance(sv, bool) and sv == rv
                            else:
                                ok = _is_num(sv) and abs(sv - rv) <= 1e-12 * max(1.0, abs(rv))
                            if not ok:
                                raise BodyError(f"{fr} {m}@{n} alpha {a}: z summary field {k_} differs from its recomputation")
                sc = summ["scheme"].get(str(a)) or {}
                if not (_is_num(sc.get("t_emp")) and 0 <= sc["t_emp"] <= a + 1e-12 and _is_num(sc.get("t_pool")) and 0 <= sc["t_pool"] <= 1):
                    raise BodyError(f"{fr} alpha {a}: scheme-level thresholds missing, non-finite or out of range")
                if abs(sc["t_emp"] - float(arrays[f"{fr}|empirical|{a}"][0])) > 1e-12 or abs(sc["t_pool"] - float(arrays[f"{fr}|pooled|{a}"][0])) > 1e-12:
                    raise BodyError(f"{fr} alpha {a}: the scheme summary differs from the thresholds arrays")
                # the derived scheme fields (R07 F10): kappa = alpha/t_emp (inf at 0), the z values, and the fit detail's indices
                kap = (a / sc["t_emp"]) if sc["t_emp"] > 0 else float("inf"); sk = sc.get("kappa_emp")
                # the infinite and finite references are exclusive branches (R07 F12): at t_emp = 0 only +inf is admissible
                if kap == float("inf"):
                    ok = isinstance(sk, float) and sk == float("inf")
                else:
                    ok = _is_num(sk) and abs(sk - kap) <= 1e-9 * max(1.0, kap)
                if not ok:
                    raise BodyError(f"{fr} alpha {a}: kappa_emp differs from alpha / t_emp")
                for key_, tv in (("z_emp", sc["t_emp"]), ("z_pool", sc["t_pool"])):
                    zv = sc.get(key_); zr = float(norm.isf(tv)) if tv > 0 else None
                    if not ((zr is None and zv is None) or (zr is not None and _is_num(zv) and abs(zv - zr) <= 1e-9 * max(1.0, abs(zr)))):
                        raise BodyError(f"{fr} alpha {a}: {key_} differs from its recomputation")
                det = sc.get("emp_detail") or {}
                if det.get("m") != T.m_floor(a, rec["N_C"]) or det.get("b") != T.m_floor(grid["beta"], rec["K_fit"]) or not (_is_num(det.get("tstar_median")) and _is_num(det.get("unclipped"))):
                    raise BodyError(f"{fr} alpha {a}: the empirical multiplier's fit detail is missing or inconsistent")
    info = rec.get("info") or {}
    if not (isinstance(info.get("n_tuples"), int) and info["n_tuples"] > 0 and isinstance(info.get("nnz"), dict) and set(info["nnz"]) == set(grid["rules"]) and isinstance(info.get("mean_M"), dict)):
        raise BodyError("calibration info (n_tuples, nnz per rule, mean_M per rule) missing or malformed")
    return True


def _interval_ok(iv):
    try:
        lo, hi = float(iv[0]), float(iv[1])
    except Exception:
        return False
    return np.isfinite(lo) and np.isfinite(hi) and -1e-12 <= lo <= hi <= 1 + 1e-12


def validate_eval_body(rec, arrays, grid, sp, study_mode, unit, N_E_expected):
    """The evaluation-unit contract (R07 F2): N_E bound to the registered size; the axis metadata exactly as registered (alphas, variants,
    sources, cross tokenizers, fixed variants); exactly the expected arrays with the registered shapes and dtype uint16; every count in
    [0, N_E]; counts nested across alpha for every variant; the crossed block on the diagonal with every registered variant populated
    (finite ordered bounds in [0, 1], a finite non-negative SE, B as registered); the calibration-set bootstrap with B finite values in
    range for every same-tokenizer source and registered (method, N_cal); the screening constants (c, r, b) finite and equal to their
    recomputation."""
    K = sp["K"]; N_E = rec.get("N_E"); nA = len(grid["alpha"]); ncell = len(sp["cells"]); vs = R.variant_names(sp["N_cal"]); nv = len(vs)
    if not isinstance(N_E, int) or isinstance(N_E, bool) or N_E != N_E_expected:
        raise BodyError(f"N_E is {N_E!r}; the registered evaluation size is {N_E_expected}")
    others = [t for t in sp["toks"] if t != unit["tokenizer"]] if (study_mode and grid.get("cross_tokenizer")) else []
    for f, v in (("alphas", list(grid["alpha"])), ("variants_same", vs), ("variants_cross", R.cross_variant_names(grid)), ("cal_sources", list(sp["cells"])), ("cross_tokenizers", others), ("fixed_variants", ["nominal", "multiplier20"])):
        if rec.get(f) != v:
            raise BodyError(f"evaluation record field {f} is {rec.get(f)!r}; expected {v!r}")
    expected = {}
    for fam in FAMILIES:
        for r in grid["rules"]:
            fr = f"{fam}|{r}"; expected[f"{fr}|fixed"] = (2, nA, K); expected[f"{fr}|same"] = (ncell, nv, nA, K)
            if others:
                expected[f"{fr}|cross"] = (len(others), ncell, len(R.cross_variant_names(grid)), K)
    if set(arrays) != set(expected):
        raise BodyError(f"count arrays differ from the expected set: missing {sorted(set(expected) - set(arrays))[:3]}, extra {sorted(set(arrays) - set(expected))[:3]}")
    order = np.argsort(grid["alpha"])
    for key, shape in expected.items():
        a = arrays[key]
        if a.shape != shape or a.dtype != np.uint16:
            raise BodyError(f"array {key} has shape {a.shape} dtype {a.dtype}; expected {shape} uint16")
        if (a > N_E).any():
            raise BodyError(f"array {key} holds a count above N_E")
        if not key.endswith("|cross"):
            srt = np.take(a, order, axis=-2)
            if (np.diff(srt.astype(np.int64), axis=-2) < 0).any():
                raise BodyError(f"array {key}: counts not nested across alpha")
    for fam in FAMILIES:
        for r in grid["rules"]:
            fr = f"{fam}|{r}"; cr = (rec.get("crossed") or {}).get(fr) or {}
            for v in grid["crossed_bootstrap"]["variants"]:
                if "@" in v and int(v.split("@")[-1]) not in sp["N_cal"]:
                    continue
                blk = cr.get(v)
                if blk is None or blk.get("B") != grid["crossed_bootstrap"]["B"]:
                    raise BodyError(f"crossed block {fr} {v} missing or with the wrong B")
                for st in ("q0.01", "q0.05", "q0.5", "q0.95", "q0.99", "max", "share2", "share5"):
                    if st not in blk or not _interval_ok(blk[st].get("ci95", [])) or not (_is_num(blk[st].get("boot_se")) and blk[st]["boot_se"] >= 0):
                        raise BodyError(f"crossed block {fr} {v} {st} not populated")
            cb = (rec.get("cal_boot") or {}).get(fr) or {}; B = grid["cal_bootstrap"]["B"]
            for tagc in sp["cells"]:
                for n in grid["cal_bootstrap"]["N_cal"]:
                    if n not in sp["N_cal"]:
                        continue
                    for m in grid["methods_per_key"]:
                        b = (cb.get(tagc) or {}).get(f"{m}@{n}")
                        if not isinstance(b, dict):
                            raise BodyError(f"calibration bootstrap {fr} {tagc} {m}@{n} missing")
                        for s_ in ("key_mean", "sd", "share_above_alpha", "q99"):
                            vals = b.get(s_)
                            if not isinstance(vals, list) or len(vals) != B or not all(_is_num(x) and 0 <= x <= 1 for x in vals):
                                raise BodyError(f"calibration bootstrap {fr} {tagc} {m}@{n} {s_}: not {B} finite values in [0, 1]")
    for a in grid["alpha"]:
        s = T.screening(np.zeros(1), N_E, a, grid["beta"]); st = (rec.get("screen") or {}).get(str(a)) or {}
        if st.get("c") != s["c"] or not (_is_num(st.get("r")) and abs(st["r"] - s["r"]) <= 1e-12) or not (_is_num(st.get("b")) and abs(st["b"] - s["b"]) <= 1e-12):
            raise BodyError(f"screening constants at alpha {a} differ from their recomputation")
    return True


# ---------------- statistics ----------------
def key_boot_sd(levels, rng, B=T.BOOT_KEYS):
    K = len(levels); idx = rng.integers(0, K, size=(B, K)); s = levels[idx].std(axis=1, ddof=1)
    return s, float(np.quantile(s, 0.025)), float(np.quantile(s, 0.975)), float(s.std(ddof=1))


def classify_band(lo, hi, band):
    if band[0] <= lo and hi <= band[1]:
        return "consistent"
    if hi < band[0] or lo > band[1]:
        return "inconsistent"
    return "unresolved"


def classify_sign(lo, hi, predicted_above_one):
    if lo > 1 or hi < 1:
        above = lo > 1
        return "agree" if above == predicted_above_one else "disagree"
    return "unresolved"


def pair_class(tagC, tagE, grid, tokC=None, tokE=None):
    if tokC is not None and tokE is not None and tokC != tokE:
        return "cross_tokenizer"
    if tagC == tagE:
        return "diagonal"
    if set([tagC, tagE]) == set(grid.get("near_identical_pair", [])):
        return "near_identical"
    en = set(grid.get("english_cells", []))
    if tagC in en and tagE in en:
        return "within_english"
    if tagC in en or tagE in en:
        return "english_other"
    return "other_other"


def analyze(grid, cells_dir, inputs, mode, lock_path=None, validation=False, s2_cells=None):
    recs, sp, exp = load_inventory(cells_dir, grid, mode, lock_path, validation); cells_dir = pathlib.Path(cells_dir)
    pr = grid["primary"]; vs = R.variant_names(sp["N_cal"]); alphas = grid["alpha"]; ia01 = alphas.index(float(pr["alpha"]))
    # in pilot mode the primary block iterates over the pilot's own tokenizers and widths (a pilot that never enters a rule tests nothing)
    pr_toks = pr["tokenizers"] if not validation else list(sp["toks"]); pr_h = pr["h"] if not validation else [h for h in sp["h"] if h > 0]
    t1, t2, rep, desc = [], [], [], []
    for u in R.expected_units(grid, validation):
        if u["kind"] != "eval":
            continue
        n = R.unit_name("eval", u["tokenizer"], u["tag"], u["h"]); rec = recs[n]; z = np.load(cells_dir / f"{n}.npz"); arr = {k: z[k] for k in z.files}
        validate_eval_body(rec, arr, grid, sp, mode == "study", u, exp[n]["N"]); N_E = rec["N_E"]; tokE, tagE, h = u["tokenizer"], u["tag"], u["h"]
        for f in FAMILIES:
            for r in grid["rules"]:
                fr = f"{f}|{r}"; blk = inputs["blocks"].get(f"h{h}|{r}")
                nomE = arr[f"{fr}|fixed"][0] / N_E                                        # (nA, K) nominal levels
                for ia, a in enumerate(alphas):
                    for iv, vname in enumerate(("nominal", "multiplier20")):
                        lv = arr[f"{fr}|fixed"][iv, ia]; s = T.level_summary(lv, N_E, a); sc = T.screening(lv, N_E, a, grid["beta"])
                        pred = blk["sets"][f"{tokE}|{tagE}|E"]["pred_fixed"][str(a)][vname] if blk else None
                        desc.append({"family": f, "rule": r, "h": h, "tokE": tokE, "tagE": tagE, "tokC": None, "tagC": None, "class": "fixed", "variant": vname, "alpha": a, **s,
                                     "screen_B": sc["B"], "screen_b": sc["b"], "pred_sd": pred["sd_cond"] if pred else None, "pred_mean": pred["mean_level"] if pred else None, **{f"pred_{k}": (pred.get(k) if pred else None) for k in T._share_names()}})
                for ic, tagC in enumerate(sp["cells"]):
                    cls = pair_class(tagC, tagE, grid)
                    pk = blk["pairs"].get(f"{tokE}|{tagC}->{tokE}|{tagE}") if blk else None
                    for ia, a in enumerate(alphas):
                        for iv, vname in enumerate(vs):
                            lv = arr[f"{fr}|same"][ic, iv, ia]; s = T.level_summary(lv, N_E, a); sc = T.screening(lv, N_E, a, grid["beta"])
                            meth = vname.split("@")[0]; pred = None
                            if pk is not None:
                                pred = pk["per_key"][vname.split("@")[1]][str(a)][meth] if "@" in vname else pk["fixed"][str(a)][meth]
                            desc.append({"family": f, "rule": r, "h": h, "tokE": tokE, "tagE": tagE, "tokC": tokE, "tagC": tagC, "class": cls, "variant": vname, "alpha": a, **s,
                                         "screen_B": sc["B"], "screen_b": sc["b"], "pred_sd": pred["sd_cond"] if pred else None, "pred_mean": pred["mean_level"] if pred else None,
                                         **{f"pred_{k}": (pred.get(k) if pred else None) for k in T._share_names()}, "pred_theory_share": pred.get("theory_share") if pred else None})
                    # the primary rules
                    if f == pr["family"] and r in pr["rules"] and h in pr_h and tokE in pr_toks and pk is not None:
                        for nc in pr["N_cal"]:
                            if nc not in sp["N_cal"]:
                                continue
                            iv = vs.index(f"{pr['method']}@{nc}"); lv = arr[f"{fr}|same"][ic, iv, ia01] / N_E; lvn = nomE[ia01]
                            pred = pk["per_key"][str(nc)][pr["alpha"]][pr["method"]]; pnom = blk["sets"][f"{tokE}|{tagE}|E"]["pred_fixed"][pr["alpha"]]["nominal"]
                            name = f"{tokE}|{tagC}->{tagE}|h{h}|{r}|{nc}"; rng = rng_for(name)
                            K = len(lv); idx = rng.integers(0, K, size=(T.BOOT_KEYS, K))
                            sd_b = lv[idx].std(axis=1, ddof=1); sdn_b = lvn[idx].std(axis=1, ddof=1)
                            sd = float(lv.std(ddof=1)); sdn = float(lvn.std(ddof=1))
                            eligible = (pred["theory_share"] >= pr["min_theory_share"]) and not pred["flags"] and pred["sd_cond"] > 0
                            mC = blk["sets"][f"{tokE}|{tagC}|C{nc}"]; mE = blk["sets"][f"{tokE}|{tagE}|E"]
                            row = {"pair": name, "class": cls, "tok": tokE, "tagC": tagC, "tagE": tagE, "h": h, "rule": r, "N_cal": nc, "N_E": int(N_E), "K": int(K), "j": pred.get("j"), "sd_obs": sd, "sd_pred": pred["sd_cond"], "theory_share": pred["theory_share"],
                                   "flags": pred["flags"], "eligible": bool(eligible), "key_mean_obs": float(lv.mean()), "key_mean_pred": pred["mean_level"],
                                   "v": pred.get("v"), "v_raw": pred.get("v_raw"), "tau_v": pred.get("tau_v"), "rho_C": mC["rho"], "rho_E": mE["rho"], "rho_CE": pk["cross"][str(nc)]["rho_CE"], "sigma2_C": mC["sigma2"], "sigma2_E": mE["sigma2"]}
                            if eligible:
                                lo, hi = np.quantile(sd_b, 0.025) / pred["sd_cond"], np.quantile(sd_b, 0.975) / pred["sd_cond"]
                                row.update({"ratio": sd / pred["sd_cond"], "ratio_ci95": [float(lo), float(hi)], "class_T1": classify_band(lo, hi, pr["band"])})
                            t1.append(row)
                            Rp = pred["sd_cond"] / pnom["sd_cond"] if pnom["sd_cond"] > 0 else float("nan")
                            mb = pr["T2_material_band"]; material = np.isfinite(Rp) and (Rp < mb[0] or Rp > mb[1])
                            rr = sd_b / np.where(sdn_b > 0, sdn_b, np.nan); lo2, hi2 = np.nanquantile(rr, 0.025), np.nanquantile(rr, 0.975)
                            row2 = {"pair": name, "class": cls, "tok": tokE, "tagC": tagC, "tagE": tagE, "h": h, "rule": r, "N_cal": nc, "N_E": int(N_E), "K": int(K), "R_pred": Rp, "R_obs": sd / sdn if sdn > 0 else float("nan"),
                                    "R_obs_ci95": [float(lo2), float(hi2)], "material": bool(material), "sd_nominal_obs": sdn, "sd_nominal_pred": pnom["sd_cond"]}
                            if material:
                                row2["class_T2"] = classify_sign(lo2, hi2, Rp > 1)
                            t2.append(row2)
                # cross-tokenizer (secondary, descriptive)
                for io, ot in enumerate(rec.get("cross_tokenizers") or []):
                    for ic, tagC in enumerate(sp["cells"]):
                        pk = blk["pairs"].get(f"{ot}|{tagC}->{tokE}|{tagE}") if blk else None
                        for iv, vname in enumerate(R.cross_variant_names(grid)):
                            a = grid["cal_bootstrap"]["alpha"]; lv = arr[f"{fr}|cross"][io, ic, iv]; s = T.level_summary(lv, N_E, a); sc = T.screening(lv, N_E, a, grid["beta"])
                            meth = vname.split("@")[0]; pred = (pk["per_key"][vname.split("@")[1]][str(a)][meth] if "@" in vname else pk["fixed"][str(a)][meth]) if pk else None
                            desc.append({"family": f, "rule": r, "h": h, "tokE": tokE, "tagE": tagE, "tokC": ot, "tagC": tagC, "class": "cross_tokenizer", "variant": vname, "alpha": a, **s,
                                         "screen_B": sc["B"], "screen_b": sc["b"], "pred_sd": pred["sd_cond"] if pred else None, "pred_mean": pred["mean_level"] if pred else None, **{f"pred_{k}": (pred.get(k) if pred else None) for k in T._share_names()}})
                # REP (study mode only; KGW; Gutenberg excluded)
                if s2_cells is not None and f == "kgw" and tagE not in grid["rep"]["exclude"]:
                    p2 = pathlib.Path(s2_cells) / f"{tagE}__{tokE}__kgw__h{h}__independent__g0.25__L256__{r}.json"; d2 = json.loads(p2.read_text())
                    l2 = d2["levels"][str(grid["rep"]["alpha"])]; lvn = nomE[alphas.index(grid["rep"]["alpha"])]
                    _, _, _, se3 = key_boot_sd(lvn, rng_for(f"rep|{tokE}|{tagE}|{h}|{r}")); sd3 = float(lvn.std(ddof=1))
                    d = abs(sd3 - l2["sd_obs_conditional"]); thr = grid["rep"]["gross_se"] * np.sqrt(se3 ** 2 + l2["sd_obs_boot_se"] ** 2) + REP_TOL
                    rep.append({"tok": tokE, "tag": tagE, "h": h, "rule": r, "sd_s3": sd3, "se_s3": se3, "sd_s2": l2["sd_obs_conditional"], "se_s2": l2["sd_obs_boot_se"], "z": d / (thr - REP_TOL) if thr > REP_TOL else float("inf"), "gross": bool(d > thr)})
    def rule_summary(rows, key, ok, pass_share):
        res = [x for x in rows if key in x]; n_ok = sum(x[key] == ok for x in res); n_res = sum(x[key] != "unresolved" for x in res)
        return {"n_rows": len(rows), "n_eligible": len(res), "n_resolved": n_res, f"n_{ok}": n_ok, "n_unresolved": len(res) - n_res, "share": (n_ok / n_res) if n_res else None,
                "pass": bool(n_res >= pr["min_resolved"] and n_ok / max(n_res, 1) >= pass_share)}
    out = {"study": R.STUDY, "mode": mode, "T1": rule_summary(t1, "class_T1", "consistent", pr["T1_pass_share"]), "T2": rule_summary(t2, "class_T2", "agree", pr["T2_pass_share"]),
           "REP": {"n_checks": len(rep), "n_gross": sum(x["gross"] for x in rep), "pass": bool(rep) and not any(x["gross"] for x in rep)} if s2_cells is not None else None,
           "t1_rows": t1, "t2_rows": t2, "rep_rows": rep, "descriptive_rows": desc,
           "pass1": {n: {"summary": d["summary"], "info": d["info"]} for n, d in recs.items() if n.startswith("cal__")},
           "crossed": {n: d["crossed"] for n, d in recs.items() if n.startswith("eval__")}, "cal_boot": {n: d["cal_boot"] for n, d in recs.items() if n.startswith("eval__")}}
    return out


def s2_inventory_ok(root=ROOT):
    m = json.loads((root / R.S2_RUN_MANIFEST).read_text()); cells = root / m["inventory"]["cells_dir"]
    files = sorted(f for f in cells.glob("*.json") if not f.name.startswith("costs__"))
    dig = hashlib.sha256("".join(f"{f.name}:{sha(f)}\n" for f in files).encode()).hexdigest()
    if dig != m["inventory"]["inventory_sha256"]:
        raise InventoryError("Study 2's cell inventory differs from its pinned run manifest")
    return cells


def main(a):
    grid_path = a[a.index("--grid") + 1]; grid = json.loads(pathlib.Path(grid_path).read_text())
    if "--pilot" in a:
        cells = pathlib.Path(a[a.index("--pilot") + 1]); inputs = json.loads(pathlib.Path(a[a.index("--pilot-inputs") + 1]).read_text())
        out = analyze(grid, cells, inputs, "validation", validation=True); dest = cells.parent / "pilot_results.json"
    else:
        lock = a[a.index("--lock") + 1]; R.verify_lock(lock, grid_path); inputs = json.loads((ROOT / R.INPUTS).read_text())
        out = analyze(grid, ROOT / R.OUT / "cells", inputs, "study", lock_path=lock, s2_cells=s2_inventory_ok()); dest = ROOT / R.OUT / "results.json"
    dest.write_text(json.dumps(out, default=float, separators=(",", ":")))
    print("T1", {k: out["T1"][k] for k in ("n_eligible", "n_resolved", "pass")}, "T2", {k: out["T2"][k] for k in ("n_eligible", "n_resolved", "pass")}, "REP", out["REP"], flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
