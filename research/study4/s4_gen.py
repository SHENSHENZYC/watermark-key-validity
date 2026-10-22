"""Study 4 generation (v1): batched sampling from a pinned open-weight model on MPS with the watermark hooks of s4_wm (the LOCKED hash),
a manual KV-cache loop so that every step's logits are available on the CPU for the hooks and the diagnostics.

Per batch (B prompts of P tokens, one key, one mode): n_new tokens are generated; at every step the model's unshifted logits for the
last position go to the CPU as float32, the special and padding ids are excluded (set to -inf), temperature 1 (the model's own law),
then
  none:   x ~ softmax(logits)                                         (the model's null law; the key is unused)
  kgw:    x ~ softmax(logits + delta * green(key, context, .))        (Kirchenbauer et al. 2023, soft rule)
  gumbel: x = argmax_v log U_v(key, context) / p_v                    (Aaronson 2023; deterministic given key and context)
Recorded per text: the token ids (the record), the model's log-probability of the chosen token under the UNSHIFTED distribution (for
the quality diagnostic), the hook's green flag (kgw) or the chosen token's uniform (gumbel) at every generated position, and whether EOS
was wanted (its probability mass at that step, which the exclusion removed). The sampling RNG is a NumPy Generator seeded per batch
(a documented function of the batch's identity); the model's logits on MPS in bfloat16 are not guaranteed bit-reproducible across
batch compositions or runs, so the committed token arrays are the record and every downstream number is recomputed from them.
"""
import os, pathlib, sys, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study2"))
import s4_wm as W
import s2_data as D   # the pinned tokenizer specs (repo, revision, V)

MODELS = {"qwen": {"repo": "Qwen/Qwen2.5-1.5B", "revision": "8faed761d45a263340a0528343f099c05c9a4323", "tokenizer": "qwen", "license": "apache-2.0"},
          "llama": {"repo": "meta-llama/Llama-3.2-1B", "revision": "4e20de362430cd3b72f300e6b0f18e50e7166e08", "tokenizer": "llama", "license": "llama3.2"}}


def load_model(name="qwen", device="mps", dtype="bfloat16"):
    os.environ.setdefault("HF_HUB_OFFLINE", "1"); os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    spec = MODELS[name]
    tok = AutoTokenizer.from_pretrained(spec["repo"], revision=spec["revision"])
    model = AutoModelForCausalLM.from_pretrained(spec["repo"], revision=spec["revision"], dtype=getattr(torch, dtype))
    model.to(device).eval()
    V_model = int(model.config.vocab_size); V_tok = int(D.TOKENIZERS[spec["tokenizer"]]["V"])
    if V_model != V_tok:
        raise RuntimeError(f"model vocab {V_model} differs from the pinned tokenizer V {V_tok}")
    n_tok = len(tok)   # ids >= n_tok never occur in text (padding rows of the embedding)
    special = sorted(set(tok.all_special_ids) | set(range(n_tok, V_model)))
    return model, tok, {"name": name, **spec, "V": V_model, "len_tokenizer": n_tok, "n_excluded_ids": len(special), "eos_id": tok.eos_token_id, "special_ids": special[:40], "device": device, "dtype": dtype}


def _excluded_mask(V, special):
    m = np.zeros(V, dtype=bool); m[np.asarray(special, dtype=np.int64)] = True; return m


def _softmax_rows(lg):
    m = lg.max(axis=1, keepdims=True); ex = np.exp(lg - m); return ex / ex.sum(axis=1, keepdims=True)


def _sample_rows(p, rng):
    """Inverse-CDF multinomial sampling, one uniform per row (B x V probabilities). The cumulative sum is taken in float64 (a float32
    accumulation erases tail mass below the running total's resolution: R09 F9), the uniform is scaled by the row's total, and the index
    is the first entry whose cumulative mass exceeds the uniform (searchsorted, right side), which skips zero-mass plateaus; a draw of
    exactly 0 therefore lands on the first positive-mass entry."""
    c = np.cumsum(np.asarray(p, dtype=np.float64), axis=1); u = rng.random(p.shape[0]) * c[:, -1]
    idx = np.array([np.searchsorted(c[b], u[b], side="right") for b in range(p.shape[0])])
    return np.minimum(idx, p.shape[1] - 1)


def generate_batch(model, info, prompts, n_new, mode, key=None, h=1, delta=2.0, gamma=0.25, seed=0, cache=None, temperature=1.0):
    """prompts: B x P int array (equal lengths). Returns a dict of arrays: tokens (B x n_new int32), logp (B x n_new float32: the model's
    unshifted log-probability of the chosen token over the admissible ids), flag (B x n_new float32: the green flag for kgw, the chosen
    token's uniform for gumbel, zeros for none), eos_mass (B x n_new float32: the excluded EOS's mass under the full softmax), and timing.
    Sampling (none, kgw): inverse-CDF multinomial with one uniform per row and step from a NumPy PCG64 generator seeded by (seed, 20261016)."""
    import torch
    dev = info["device"]; V = info["V"]; B, P = prompts.shape; g = W.C.green_fraction(gamma, V)
    excl = _excluded_mask(V, info["_special_all"]); eos_id = info["eos_id"]
    rng = np.random.default_rng([int(seed), 20261016]); cache = cache if cache is not None else W.HookCache(V, g=g)
    if mode == "kgw" and cache.g != g:
        raise ValueError("the hook cache was built for another green fraction")
    hist = np.ascontiguousarray(prompts, dtype=np.int64).copy()
    tokens = np.zeros((B, n_new), dtype=np.int32); logp = np.zeros((B, n_new), dtype=np.float32); flag = np.zeros((B, n_new), dtype=np.float32); eos = np.zeros((B, n_new), dtype=np.float32)
    t0 = time.time(); t_model = 0.0; t_hook = 0.0; past = None; rows = np.arange(B)
    with torch.no_grad():
        step_in = torch.as_tensor(hist, device=dev)
        for t in range(n_new):
            tm = time.time()
            out = model(input_ids=step_in, past_key_values=past, use_cache=True); past = out.past_key_values
            lg = out.logits[:, -1, :].float().cpu().numpy()        # B x V float32, the model's unshifted logits
            t_model += time.time() - tm; th = time.time()
            if temperature != 1.0:
                lg = lg / np.float32(temperature)
            m = lg.max(axis=1, keepdims=True); ex = np.exp(lg - m); z_full = ex.sum(axis=1)
            if eos_id is not None:
                eos[:, t] = ex[:, eos_id] / z_full
            ex[:, excl] = 0.0; p0 = ex / ex.sum(axis=1, keepdims=True)        # the model's law over the admissible ids
            if mode == "none":
                chosen = _sample_rows(p0, rng)
            elif mode == "kgw":
                cids = W.context_hash_batch(hist, h) if h > 0 else np.zeros(B, dtype=np.uint64)
                green = np.stack([cache.green(key, int(c)) for c in cids])                        # B x V bool, the exact detector colouring
                lgs = lg.copy(); lgs[:, excl] = -np.inf; lgs += np.float32(delta) * green
                chosen = _sample_rows(_softmax_rows(lgs), rng); flag[:, t] = green[rows, chosen]
            elif mode == "gumbel":
                cids = W.context_hash_batch(hist, h) if h > 0 else np.zeros(B, dtype=np.uint64)
                U = np.stack([cache.get(key, int(c)) for c in cids]).astype(np.float64)              # B x V
                with np.errstate(divide="ignore", invalid="ignore"):
                    sc = np.where(p0 > 0, np.log(np.maximum(U, 1e-300)) / np.where(p0 > 0, p0, 1.0), -np.inf)
                chosen = sc.argmax(axis=1); flag[:, t] = U[rows, chosen]
            else:
                raise ValueError(mode)
            logp[:, t] = np.log(np.maximum(p0[rows, chosen], 1e-45)); tokens[:, t] = chosen
            hist = np.concatenate([hist, chosen[:, None]], axis=1)
            step_in = torch.as_tensor(chosen[:, None].astype(np.int64), device=dev)
            t_hook += time.time() - th
    el = time.time() - t0
    if dev == "mps":
        del past, out; torch.mps.empty_cache()
    return {"tokens": tokens, "logp": logp, "flag": flag, "eos_mass": eos, "seconds": el, "seconds_model": t_model, "seconds_hook": t_hook, "tok_per_s": B * n_new / el,
            "cache_hits": cache.hits, "cache_misses": cache.misses}


def prepare_info(model, tok, info):
    """Fill the full exclusion list (every special id and every padding row) once."""
    import torch
    V = info["V"]; n_tok = info["len_tokenizer"]
    info["_special_all"] = sorted(set(tok.all_special_ids) | set(range(n_tok, V)))
    return info


def score_logp_of_text(model, info, X, sub=4):
    """The model's log-probability of each token of X (B x T int) given its predecessors (teacher forcing; positions 1..T-1), float32
    B x (T-1), under the SAME admissible law as the generations' `logp` (the special and padding ids excluded before the normalisation; a
    human token that is itself an excluded id gets -inf, counted by the caller). Scored in sub-batches of `sub` texts with a float32
    log-sum-exp per position and only the target's value gathered, so that no float32 full-vocabulary copy of every position is kept."""
    import torch
    excl = torch.as_tensor(np.flatnonzero(_excluded_mask(info["V"], info["_special_all"])), device=info["device"]); out = []
    with torch.no_grad():
        for i in range(0, X.shape[0], sub):
            ids = torch.as_tensor(np.ascontiguousarray(X[i:i + sub], dtype=np.int64), device=info["device"])
            lg = model(input_ids=ids).logits[:, :-1, :].float(); lg[:, :, excl] = float("-inf")
            lse = torch.logsumexp(lg, dim=-1); tgt = ids[:, 1:]; picked = torch.gather(lg, 2, tgt[:, :, None])[:, :, 0]
            out.append((picked - lse).cpu().numpy()); del lg, lse, picked, ids
            if info["device"] == "mps":
                torch.mps.empty_cache()
    return np.concatenate(out, axis=0).astype(np.float32)


def rep_n(X, n=4):
    """Share of repeated n-grams per text (1 - distinct/total), a loop diagnostic."""
    X = np.asarray(X); B, T = X.shape; out = np.zeros(B)
    for b in range(B):
        grams = [tuple(X[b, i:i + n]) for i in range(T - n + 1)]
        out[b] = 1.0 - len(set(grams)) / max(1, len(grams))
    return out
