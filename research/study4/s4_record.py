"""Study 4's binding to Study 3's committed record (v1): the only path through which Study 4 reads a threshold or a stored null level.

It refuses before it returns anything unless: the run manifest's inventory is complete (240 files) and every file's SHA-256 equals the
manifest's digest and the inventory digest recomputed with the manifest's own formula equals the recorded one; the lock file's digest
equals the manifest's; each unit record is a STUDY record of study3_v0.1 (no FIXTURE marker, mode 'study', the lock's digest) whose
array file matches both the record's digest and the manifest's; every per-key array has exactly K = 1,000 entries; and the key binding
is the grid's (index i <-> evaluation key key_eval_start + i, the runner's write order). A threshold is never recomputed or repaired:
a zero threshold is returned as it is and `abstaining` marks it (R07/R08 carried forward)."""
import hashlib, json, pathlib, sys
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/study3"))
from s3_keys import STUDY3_EVAL  # noqa: E402  (the pinned key range; the module is imported, not edited)

STUDY = "study3_v0.1"
CELLS_DIR = ROOT / "outputs/study3_v0.1/cells"
MANIFEST = ROOT / "outputs/study3_v0.1/RUN_MANIFEST.json"
LOCK = ROOT / "outputs/study3_v0.1/PRE_RUN_LOCK.json"
GRID = ROOT / "research/study3/grid_v0.1.json"
N_FILES = 240


class RecordError(RuntimeError):
    pass


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def _inventory_digest(digests):
    return hashlib.sha256("".join(f"{k}:{v}\n" for k, v in sorted(digests.items())).encode()).hexdigest()


class Record:
    """The verified record. Construct once; every load goes through it."""
    def __init__(self, cells_dir=CELLS_DIR, manifest=MANIFEST, lock=LOCK, grid=GRID, verify_files=True):
        self.cells_dir = pathlib.Path(cells_dir); self.man = json.loads(pathlib.Path(manifest).read_text()); self.grid = json.loads(pathlib.Path(grid).read_text())
        if self.man.get("study") != STUDY or self.man.get("label") != "STUDY":
            raise RecordError(f"manifest is not the {STUDY} STUDY manifest (study={self.man.get('study')!r}, label={self.man.get('label')!r})")
        inv = self.man["inventory"]
        if not inv.get("complete") or inv.get("n_files") != N_FILES or len(inv["file_digests"]) != N_FILES or inv.get("n_fixture_marked", 1) != 0:
            raise RecordError("manifest inventory incomplete, of the wrong size or fixture-marked")
        if _inventory_digest(inv["file_digests"]) != inv["inventory_sha256"]:
            raise RecordError("the manifest's inventory digest does not equal the digest of its own file list")
        self.lock_sha = sha(lock)
        if self.lock_sha != self.man["lock"]["sha256"]:
            raise RecordError("the lock file's digest differs from the manifest's")
        self.lock = json.loads(pathlib.Path(lock).read_text())
        ks = self.lock["keys"]
        if (ks["eval_start"], ks["K"]) != (self.grid["key_eval_start"], self.grid["K"]) or (ks["eval_start"], ks["eval_start"] + ks["K"] - 1) != STUDY3_EVAL:
            raise RecordError("the lock's key record, the grid and s3_keys disagree")
        self.key_eval_start = int(ks["eval_start"]); self.K = int(ks["K"]); self.keys = self.key_eval_start + np.arange(self.K)
        self.beta = float(self.grid["beta"]); self.alphas = [float(a) for a in self.grid["alpha"]]; self.N_cal = [int(n) for n in self.grid["N_cal"]]
        self.file_digests = inv["file_digests"]
        if verify_files:
            self.verify_files()

    def verify_files(self):
        present = {p.name for p in self.cells_dir.iterdir() if p.is_file()}
        if present != set(self.file_digests):
            raise RecordError(f"cells directory differs from the manifest: missing {sorted(set(self.file_digests) - present)[:5]}, extra {sorted(present - set(self.file_digests))[:5]}")
        bad = [n for n, d in self.file_digests.items() if sha(self.cells_dir / n) != d]
        if bad:
            raise RecordError(f"{len(bad)} record files differ from their manifest digests, e.g. {bad[:3]}")
        self.verified = True
        return {"n_files": len(self.file_digests), "inventory_sha256": self.man["inventory"]["inventory_sha256"], "lock_sha256": self.lock_sha}

    def _record(self, kind, tok, tag, h):
        name = f"{kind}__{tok}__{tag}__h{h}"; jp = self.cells_dir / f"{name}.json"
        if jp.name not in self.file_digests or sha(jp) != self.file_digests[jp.name]:
            raise RecordError(f"{jp.name} missing from the manifest or differs from its digest")
        rec = json.loads(jp.read_text())
        if "FIXTURE" in rec or rec["provenance"].get("mode") != "study" or rec["provenance"].get("study") != STUDY or rec["provenance"].get("lock_sha256") != self.lock_sha:
            raise RecordError(f"{name}: not a STUDY record of {STUDY} under the lock {self.lock_sha[:12]}")
        if rec["unit"] != {"kind": kind, "tokenizer": tok, "tag": tag, "h": h}:
            raise RecordError(f"{name}: the record's unit field {rec['unit']} is not the requested unit")
        if int(rec["provenance"]["key_eval_start"]) != self.key_eval_start or int(rec["provenance"]["K"]) != self.K:
            raise RecordError(f"{name}: key provenance differs from the lock's")
        return name, rec

    def cal(self, tok, tag, h):
        name, rec = self._record("cal", tok, tag, h); fn = pathlib.Path(rec["thresholds_file"]).name; fp = self.cells_dir / fn
        d = sha(fp)
        if d != rec["thresholds_sha256"] or d != self.file_digests.get(fn):
            raise RecordError(f"{fn}: the thresholds array differs from the record's or the manifest's digest")
        z = np.load(fp); arrays = {k: np.array(z[k]) for k in z.files}
        for k, a in arrays.items():
            parts = k.split("|")
            want = (1,) if parts[2] in ("empirical", "pooled") else (self.K,)
            if a.shape != want or not np.all(np.isfinite(a)) or (a < 0).any():
                raise RecordError(f"{fn}: array {k} has shape {a.shape} (expected {want}) or a non-finite or negative entry")
        return CalUnit(self, name, rec, arrays)

    def eval(self, tok, tag, h):
        name, rec = self._record("eval", tok, tag, h); fn = f"{name}.npz"; fp = self.cells_dir / fn
        d = sha(fp)
        if d != rec["npz_sha256"] or d != self.file_digests.get(fn):
            raise RecordError(f"{fn}: the counts array differs from the record's or the manifest's digest")
        z = np.load(fp); arrays = {k: np.array(z[k]) for k in z.files}
        nA = len(rec["alphas"]); nS = len(rec["cal_sources"]); nV = len(rec["variants_same"]); N_E = int(rec["N_E"])
        for k, a in arrays.items():
            kind = k.split("|")[-1]
            want = {"fixed": (2, nA, self.K), "same": (nS, nV, nA, self.K), "cross": (len(rec["cross_tokenizers"]), nS, len(rec["variants_cross"]), self.K)}.get(kind)
            if want is None or a.shape != want or a.dtype != np.uint16 or int(a.max(initial=0)) > N_E:
                raise RecordError(f"{fn}: array {k} has shape {a.shape}, dtype {a.dtype} or a count above N_E = {N_E} (expected {want}, uint16)")
        return EvalUnit(self, name, rec, arrays)


class CalUnit:
    def __init__(self, R, name, rec, arrays):
        self.R, self.name, self.rec, self.arrays = R, name, rec, arrays; self.keys = R.keys; self.N_C = int(rec["N_C"])
        self.j = {}
        for fr, s in rec["summary"].items():
            for v, d in s["per_key_z"].items():
                self.j[(fr, v)] = int(d["j"])

    def threshold(self, family, rule, method, alpha, N_cal=None):
        """The K-vector of thresholds on the p scale for (family, rule, method[@N_cal], alpha); fixed methods from the grid."""
        a = float(alpha); fr = f"{family}|{rule}"
        if method == "nominal":
            return np.full(self.R.K, a)
        if method == "multiplier20":
            return np.full(self.R.K, a * self.R.beta)
        if method in ("empirical", "pooled"):
            return np.broadcast_to(self.arrays[f"{fr}|{method}|{alpha}"], (self.R.K,)).copy()
        if method in ("conformal", "tolerance"):
            return self.arrays[f"{fr}|{method}@{int(N_cal)}|{alpha}"].copy()
        raise RecordError(f"unknown method {method!r}")

    def abstaining(self, family, rule, method, alpha, N_cal=None):
        return self.threshold(family, rule, method, alpha, N_cal) <= 0

    def order_index(self, family, rule, method, alpha, N_cal):
        return self.j[(f"{family}|{rule}", f"{method}@{int(N_cal)}|{alpha}")]


class EvalUnit:
    """Study 3's stored null outcomes for a (tokenizer, cell, h): counts of rejected evaluation texts per key under every threshold."""
    def __init__(self, R, name, rec, arrays):
        self.R, self.name, self.rec, self.arrays = R, name, rec, arrays; self.N_E = int(rec["N_E"]); self.keys = R.keys
        self.vs, self.sources, self.alphas, self.fixed = rec["variants_same"], rec["cal_sources"], [float(a) for a in rec["alphas"]], rec["fixed_variants"]

    def null_count(self, family, rule, method, alpha, N_cal=None, cal_source=None):
        fr = f"{family}|{rule}"; ia = self.alphas.index(float(alpha))
        if method in self.fixed:
            return self.arrays[f"{fr}|fixed"][self.fixed.index(method), ia].astype(np.int64)
        v = method if method in ("empirical", "pooled") else f"{method}@{int(N_cal)}"
        src = cal_source or self.rec["unit"]["tag"]
        return self.arrays[f"{fr}|same"][self.sources.index(src), self.vs.index(v), ia].astype(np.int64)

    def null_level(self, *a, **k):
        return self.null_count(*a, **k) / self.N_E


if __name__ == "__main__":
    import shutil, tempfile
    R = Record(); print("record verified:", R.verify_files())
    cu = R.cal("qwen", "news_en_256", 1); ev = R.eval("qwen", "news_en_256", 1)
    for fam, rule in (("kgw", "distinct"), ("kgw", "raw")):
        t_nom = cu.threshold(fam, rule, "nominal", 0.01); t_c = cu.threshold(fam, rule, "conformal", 0.01, 5000)
        l_nom = ev.null_level(fam, rule, "nominal", 0.01); l_c = ev.null_level(fam, rule, "conformal", 0.01, 5000)
        print(f"{fam}|{rule} h=1 qwen news: keys {cu.keys[0]}..{cu.keys[-1]}; conformal@5000 j={cu.order_index(fam, rule, 'conformal', 0.01, 5000)}; "
              f"stored null key-mean nominal {l_nom.mean():.4f} (SD {l_nom.std(ddof=1):.4f}), conformal@5000 {l_c.mean():.4f} (SD {l_c.std(ddof=1):.4f}); abstaining {int(cu.abstaining(fam, rule, 'conformal', 0.01, 5000).sum())}")
    ab = cu.abstaining("gumbel", "raw", "tolerance", 0.001, 500); print("gumbel|raw tolerance@500 alpha 0.001 abstaining (structural):", int(ab.sum()))
    # refusal fixtures on copies in a scratch directory (the record itself is never touched)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="s4_record_fixture_")); shutil.copytree(CELLS_DIR, tmp / "cells")
    cases = {}
    # (a) one threshold value changed in one array file
    f = tmp / "cells/cal__qwen__news_en_256__h1__thresholds.npz"; z = np.load(f); d = {k: np.array(z[k]) for k in z.files}; d["kgw|distinct|conformal@5000|0.01"][3] *= 1.0001; np.savez_compressed(f, **d)
    try:
        Record(cells_dir=tmp / "cells"); cases["tampered_array"] = "ACCEPTED (wrong)"
    except RecordError as e:
        cases["tampered_array"] = f"refused: {str(e)[:70]}"
    shutil.copy(CELLS_DIR / f.name, f)
    # (b) a record file with its unit field pointing at another unit
    j = tmp / "cells/cal__qwen__news_en_256__h1.json"; rec = json.loads(j.read_text()); rec["unit"]["tag"] = "wikipedia_en_256"; j.write_text(json.dumps(rec, indent=0))
    try:
        Record(cells_dir=tmp / "cells"); cases["relabelled_record"] = "ACCEPTED (wrong)"
    except RecordError as e:
        cases["relabelled_record"] = f"refused: {str(e)[:70]}"
    shutil.copy(CELLS_DIR / j.name, j)
    # (c) a missing file
    (tmp / "cells/eval__llama__news_en_256__h0.npz").unlink()
    try:
        Record(cells_dir=tmp / "cells"); cases["missing_file"] = "ACCEPTED (wrong)"
    except RecordError as e:
        cases["missing_file"] = f"refused: {str(e)[:70]}"
    # (d) a manifest whose lock digest is altered (the lock pointing elsewhere)
    man = json.loads(MANIFEST.read_text()); man["lock"]["sha256"] = "0" * 64; mp = tmp / "manifest.json"; mp.write_text(json.dumps(man))
    try:
        Record(manifest=mp, verify_files=False); cases["lock_digest_mismatch"] = "ACCEPTED (wrong)"
    except RecordError as e:
        cases["lock_digest_mismatch"] = f"refused: {str(e)[:70]}"
    shutil.rmtree(tmp)
    for k, v in cases.items():
        print(f"  fixture {k}: {v}")
    if any(v.startswith("ACCEPTED") for v in cases.values()):
        raise SystemExit("a refusal fixture was accepted")
    print("all refusal fixtures refused")
