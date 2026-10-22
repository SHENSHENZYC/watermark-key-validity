"""Study 4 watermark hooks (v1): the generation side of the two detectors Study 3 calibrated, built on the LOCKED hash of Study 1
(research/study1/s1_core.py: splitmix64 `mix64`, `uniforms(key, ids)`, the context ids and tuple ids) so that a token chosen green by
the generator is exactly the token the detector colours green for the same key and context. Pure NumPy; no model here.

Detector conventions reproduced (s1_core.context_ids / tuple_ids, pinned by the Study 1-3 locks):
  cid_0 = 0;  for j = 1..h:  cid_j = mix64(cid_{j-1} * C1 + (x[t-j] + 1) * C2 + j)      (the h previous tokens, nearest last)
  tuple id of candidate v at that position:  mix64(cid_h * C2 + (v + 1) * C1)
  KGW: green iff uniforms(key, tuple id) < g, g = floor(gamma V)/V  (independent colouring; gamma = 0.25 gives g = gamma at both V)
  Gumbel-max: score s = -ln(1 - U) summed over retained positions; U = uniforms(key, tuple id)

Generation rules:
  KGW (Kirchenbauer et al. 2023, the soft rule): add delta to the logits of the green candidates, then sample from the shifted softmax.
  Gumbel-max (Aaronson 2023; Kuditipudi et al. 2024's EXP rule with context hashing): choose argmax_v log(U_v) / p_v over the
    candidates with p_v > 0 (equivalently argmax U_v^{1/p_v}); a deterministic function of (key, context, p).
The generator's context for the first h generated tokens lies in the prompt; the detector, which sees the generated text alone, never
scores those positions (they are invalid under its rules), so the two agree on every scored position (checked by `check_against_detector`).
"""
import pathlib, sys
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/study1")); sys.path.insert(0, str(ROOT / "research/study2"))
import s1_core as C   # Study 1's locked core, unchanged
import s2_core as S   # Study 2's locked core, unchanged

C1, C2, C3 = C.C1, C.C2, C.C3


def context_hash(history, h):
    """cid at the next position given the full history (a 1-D int array of every token so far: prompt then generated), as the
    detector computes it for a position whose h predecessors all lie inside the text it sees. Returns a Python int (uint64)."""
    cid = np.uint64(0)
    with np.errstate(over="ignore"):
        for j in range(1, h + 1):
            tok = np.uint64(int(history[-j]) + 1) if len(history) >= j else np.uint64(0)
            cid = C.mix64(cid * C1 + tok * C2 + np.uint64(j))
    return int(cid)


def context_hash_batch(hist, h):
    """cid for a batch: hist is B x T int array (the last h columns are the context). Returns B uint64."""
    B, T = hist.shape; cid = np.zeros(B, dtype=np.uint64)
    with np.errstate(over="ignore"):
        for j in range(1, h + 1):
            tok = (hist[:, T - j].astype(np.uint64) + np.uint64(1)) if T >= j else np.zeros(B, dtype=np.uint64)
            cid = C.mix64(cid * C1 + tok * C2 + np.uint64(j))
    return cid


def tuple_ids_all(cid, V):
    """The tuple ids of every candidate token v in [0, V) at a context cid (uint64 V-vector)."""
    with np.errstate(over="ignore"):
        return C.mix64(np.uint64(cid) * C2 + (np.arange(V, dtype=np.uint64) + np.uint64(1)) * C1)


def uniforms_all(key, cid, V):
    return C.uniforms(key, tuple_ids_all(cid, V))


class HookCache:
    """Per-key cache by context id, with two stores: the exact green mask (the boolean comparison U < g made on the float64 uniforms of
    the locked hash; a float32 copy of U would round a uniform such as 0.2499999939965537 to 0.25 and flip the colour: R09 F2) and the
    float64 uniforms themselves (the Gumbel rule; the validation checks). Each store is a bounded dict (first-in, first-out); a new key
    empties both."""
    def __init__(self, V, max_entries=512, g=None):
        self.V = int(V); self.max = int(max_entries); self.g = g; self.key = None; self.dm = {}; self.du = {}; self.hits = 0; self.misses = 0
    def _get(self, store, key, cid, make):
        if key != self.key:
            self.key = key; self.dm = {}; self.du = {}
        store = self.dm if make == self._mk_green else self.du
        v = store.get(cid)
        if v is None:
            self.misses += 1; v = make(key, cid)
            if len(store) >= self.max:
                store.pop(next(iter(store)))
            store[cid] = v
        else:
            self.hits += 1
        return v
    def _mk_green(self, key, cid):
        return uniforms_all(key, cid, self.V) < self.g
    def _mk_u(self, key, cid):
        return uniforms_all(key, cid, self.V)
    def green(self, key, cid):
        """The exact green mask (bool V-vector) of the detector's colouring at this key and context."""
        if self.g is None:
            raise ValueError("HookCache.green needs g")
        return self._get(self.dm, key, cid, self._mk_green)
    def get(self, key, cid):
        """The float64 uniforms (Gumbel rule; validation checks)."""
        return self._get(self.du, key, cid, self._mk_u)
    @property
    def d(self):
        return self.dm if self.dm else self.du


def kgw_green(U, g):
    """The green indicator of every candidate (bool V-vector) from float64 uniforms; the same strict comparison as s1_core.colour_independent."""
    U = np.asarray(U)
    if U.dtype != np.float64:
        raise TypeError("kgw_green takes float64 uniforms (a float32 copy rounds at the boundary)")
    return U < g


def gumbel_choose(p, U):
    """Aaronson's rule: argmax over v with p_v > 0 of log(U_v) / p_v. p: V float (a probability vector); U: V uniforms. Returns int."""
    p = np.asarray(p, dtype=np.float64); U = np.asarray(U, dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        s = np.where(p > 0, np.log(np.maximum(U, 1e-300)) / np.where(p > 0, p, 1.0), -np.inf)
    return int(np.argmax(s))


def kgw_shift_logits(logits, green, delta):
    """logits + delta on the green candidates (float32 V-vector in, out)."""
    return logits + np.float32(delta) * green.astype(np.float32)


# ---------------- the detector-side check (no model needed) ----------------
def detector_green(X, V, h, key, gamma):
    """For a generated array X (N x L int32) and one key, the detector's green indicator at every position (N x L; False where invalid,
    i.e. t < h) through the LOCKED chain and colouring code (s2_core.build_chain, s1_core.colour_independent)."""
    chain = S.build_chain(np.ascontiguousarray(X, dtype=np.int32), V, "check", h)
    col = C.colour_independent(chain, [key], gamma, V)[:, 0].astype(bool)
    out = np.zeros(X.shape, dtype=bool); valid = chain.col >= 0
    out[valid] = col[chain.col[valid]]
    return out, chain


def detector_uniforms(X, V, h, key):
    """The detector's U(key, tuple id) at every valid position (N x L float64; NaN where invalid)."""
    chain = S.build_chain(np.ascontiguousarray(X, dtype=np.int32), V, "check", h)
    u = S.uniforms_chunk([key], chain.D)[:, 0]
    out = np.full(X.shape, np.nan); valid = chain.col >= 0; out[valid] = u[chain.col[valid]]
    return out


def check_against_detector(rng, V=1000, N=16, L=40, P=7, h=2, gamma=0.25, key=1_000_123):
    """Synthetic end-to-end check: 'generate' N texts of L tokens after P prompt tokens by random choice, recording the hook's green flag
    (through the cache, as the generator does) and the float64 uniform of the chosen token at every generated position (context from the
    true history, prompt included); then run the locked detector on the generated part alone and require exact equality at every position
    the detector scores (t >= h) for both quantities. Also: a key switch empties the cache and leaves the flags unchanged; the batch context
    hash equals the scalar one."""
    g = C.green_fraction(gamma, V); cache = HookCache(V, g=g)
    prompts = rng.integers(0, V, size=(N, P)); X = np.zeros((N, L), dtype=np.int32); flag = np.zeros((N, L), dtype=bool); uu = np.zeros((N, L))
    for n in range(N):
        hist = list(prompts[n])
        for t in range(L):
            cid = context_hash(np.array(hist), h); green = cache.green(key, cid); U = cache.get(key, cid)
            v = int(rng.integers(0, V)); X[n, t] = v; flag[n, t] = bool(green[v]); uu[n, t] = float(U[v]); hist.append(v)
    det, chain = detector_green(X, V, h, key, gamma); du = detector_uniforms(X, V, h, key)
    scored = np.zeros((N, L), dtype=bool); scored[:, h:] = True
    ok_green = bool(np.array_equal(det[scored], flag[scored])); ok_u = bool(np.array_equal(du[scored], uu[scored]))
    hb = context_hash_batch(np.concatenate([prompts, X], axis=1)[:, :P + 5], h); hs = np.array([context_hash(np.concatenate([prompts[n], X[n, :5]]), h) for n in range(N)], dtype=np.uint64)
    ok_batch = bool(np.array_equal(hb, hs))
    # a key switch: the cache is emptied and the other key's mask equals the detector's for that key
    other = key + 1; cache.green(other, context_hash(np.array(prompts[0]), h)); ok_switch = (cache.key == other and len(cache.dm) == 1 and len(cache.du) == 0)
    ok_other = bool(np.array_equal(cache.green(other, context_hash(np.array(prompts[0]), h)), uniforms_all(other, context_hash(np.array(prompts[0]), h), V) < g))
    return {"ok": ok_green and ok_u and ok_batch and ok_switch and ok_other, "green_equal_on_scored": ok_green, "uniforms_exactly_equal_on_scored": ok_u, "batch_hash_equal": ok_batch, "key_switch_ok": bool(ok_switch and ok_other),
            "n_scored": int(scored.sum()), "n_green_scored": int(flag[scored].sum()), "g": g, "h": h, "V": V, "cache_hits": cache.hits, "cache_misses": cache.misses}


def boundary_case(V=151936, key=1_000_123, prev_token=70, candidate=104474, g=0.25):
    """R09 F2's case: the float64 uniform 0.2499999939965537 is green for the detector; a float32 copy rounds to 0.25 and is not. The exact
    mask must agree with the detector."""
    cid = context_hash(np.array([prev_token]), 1); u = uniforms_all(key, cid, V); cache = HookCache(V, g=g)
    return {"uniform_float64": float(u[candidate]), "uniform_float32": float(np.float32(u[candidate])), "detector_green": bool(u[candidate] < g), "float32_would_say": bool(np.float32(u[candidate]) < np.float32(g)),
            "cache_green": bool(cache.green(key, cid)[candidate]), "ok": bool(cache.green(key, cid)[candidate] == (u[candidate] < g)), "n_flipped_by_float32_at_this_context": int(((u < g) != (u.astype(np.float32) < np.float32(g))).sum())}


if __name__ == "__main__":
    rng = np.random.default_rng(99261015)
    for h in (0, 1, 2):
        print(h, check_against_detector(rng, h=h))
    print("boundary", boundary_case())
