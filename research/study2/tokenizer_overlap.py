"""Post-hoc side computation (not pre-registered; no key or per-key level is produced; the stored per-key q-hat values are read only
for the observed correlation): what the two pinned tokenizers (Llama-3.2-1B and Qwen2.5-1.5B, the revisions of the tokens manifest)
share as HASH INPUTS, and what fraction of the production token occurrences falls on shared inputs.

The colouring hash is a deterministic function of the integer token ids alone (s1_core.context_ids / tuple_ids: a splitmix64 mix of
the ids, never of V or of the token string), so an identical integer (h+1)-tuple under the two tokenizers receives the same uniform
under every key, whatever strings the two vocabularies attach to those ids. The exact identity for the across-tokenizer covariance of
the per-key mean green fraction is therefore g(1 - g) * sum_t w_L(t) w_Q(t) over the tuples t present in both document-averaged weight
vectors (the same algebra as the within-cell identity A = sum_t w(t)^2), and the identity-predicted correlation of q-hat across the two
tokenizers is rho_pred = sum_t w_L(t) w_Q(t) / sqrt(A_L A_Q). This script computes, per corpus cell, at h = 0 and h = 1 under the raw
rule at the cell's longest length: (i) rho_pred; (ii) the share of each tokenizer's occurrence weight on tuples that also occur under
the other tokenizer; (iii) the observed correlation of the stored per-key q-hat values of the two production cells (the same 1,000
keys); (iv) the semantic-alignment diagnostic: how many ids carry the same token STRING in both vocabularies, and the share of all
occurrences on those ids (the full occurrence count is the denominator; an id outside the compared range is a non-match).
Round 1 of R06 (F1) found the first version's Qwen shares used a restricted denominator (ids below 128,256 only) and that the
same-string count is a semantic diagnostic, not the hash-overlap estimand; the superseded output is kept beside the new one.
Writes outputs/study2_v0.1/report/tokenizer_overlap.json, which the report builder reads in study mode.
Usage: .venv/bin/python research/study2/tokenizer_overlap.py
"""
import json, os, pathlib, sys
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "research/study1")); sys.path.insert(0, str(ROOT / "tools"))
import s2_data as D
import s1_core as C
from s2_run import TOKENS_MANIFEST, OUT, sha, utc

os.environ.setdefault("HF_HUB_OFFLINE", "1"); os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
from transformers import AutoTokenizer   # noqa: E402

man = json.loads((ROOT / TOKENS_MANIFEST).read_text()); grid = json.loads((ROOT / "research/study2/grid_v0.1.json").read_text())
toks = {name: AutoTokenizer.from_pretrained(spec["repo"], revision=spec["revision"]) for name, spec in man["tokenizers"].items()}
nA, nB = len(toks["llama"]), len(toks["qwen"]); n_common = min(nA, nB)
strA = toks["llama"].convert_ids_to_tokens(list(range(n_common))); strB = toks["qwen"].convert_ids_to_tokens(list(range(n_common)))
same = np.array([a == b for a, b in zip(strA, strB)], dtype=bool); first_diff = int(np.argmin(same)) if not same.all() else None


def weights(X, h):
    """Document-averaged raw-rule weights over hash tuple ids at the cell's longest length: w(t) = sum over occurrences of 1/(N M), M = L - h."""
    N, L = X.shape; ids = C.tuple_ids(C.context_ids(X, h), X)[:, h:]; M = L - h
    t, cnt = np.unique(ids.reshape(-1), return_counts=True)
    return t, cnt.astype(np.float64) / (N * M)


res = {"written_utc": utc(), "note": "post-hoc side computation; not pre-registered; no key or per-key level produced (the stored q-hat values are read for the observed correlation only)",
       "tokens_manifest_sha256": sha(ROOT / TOKENS_MANIFEST), "hash_input_note": "the colouring hash is a function of the integer ids alone (s1_core.context_ids/tuple_ids), never of V or the token string",
       "semantic": {"len_llama": nA, "len_qwen": nB, "ids_compared": n_common, "ids_same_string": int(same.sum()), "share_same_of_compared": float(same.mean()), "first_differing_id": first_diff,
                    "note": "a semantic-alignment diagnostic: ids whose token STRING is the same in both vocabularies; not the hash-overlap estimand"},
       "cells": {}}
for tag, cell in man["cells"].items():
    rec = {}
    X = {t: D.load_tokens(man, tag, t, N=man["N"], root=ROOT) for t in ("llama", "qwen")}
    for t in ("llama", "qwen"):
        ids = X[t].reshape(-1); inrange = ids < n_common; onsame = np.zeros(ids.shape, dtype=bool); onsame[inrange] = same[ids[inrange]]
        if onsame.size != X[t].size:
            raise SystemExit("denominator must be every position")
        rec[f"semantic_share_{t}"] = {"share_occurrences_on_same_string_ids": float(onsame.mean()), "n_positions": int(X[t].size), "n_positions_outside_compared_range": int((~inrange).sum())}
    for h in (0, 1):
        tL, wL = weights(X["llama"], h); tQ, wQ = weights(X["qwen"], h); AL = float((wL ** 2).sum()); AQ = float((wQ ** 2).sum())
        common, iL, iQ = np.intersect1d(tL, tQ, assume_unique=True, return_indices=True); cross = float((wL[iL] * wQ[iQ]).sum())
        L = X["llama"].shape[1]
        cells_ = {t: json.loads((ROOT / OUT / "cells" / f"{tag}__{t}__kgw__h{h}__independent__g0.25__L{L}__raw.json").read_text()) for t in ("llama", "qwen")}
        for t in ("llama", "qwen"):
            if abs(cells_[t]["identity_q"]["A"] - (AL if t == "llama" else AQ)) > 1e-9 * max(1.0, cells_[t]["identity_q"]["A"]):
                raise SystemExit(f"{tag} {t} h{h}: recomputed A {AL if t == 'llama' else AQ} differs from the cell's identity A {cells_[t]['identity_q']['A']}")
        qL = np.asarray(cells_["llama"]["q_hat"]["values"]); qQ = np.asarray(cells_["qwen"]["q_hat"]["values"])
        rec[f"h{h}"] = {"L": int(L), "n_tuples_llama": int(len(tL)), "n_tuples_qwen": int(len(tQ)), "n_tuples_shared": int(len(common)), "A_llama": AL, "A_qwen": AQ, "cross": cross,
                        "rho_pred_qhat": cross / float(np.sqrt(AL * AQ)), "weight_share_on_shared_tuples_llama": float(wL[iL].sum()), "weight_share_on_shared_tuples_qwen": float(wQ[iQ].sum()),
                        "rho_obs_qhat_stored_values": float(np.corrcoef(qL, qQ)[0, 1]), "A_check_against_cells": "equal within an absolute 1e-9 * max(1, A)"}
    res["cells"][tag] = rec
out = ROOT / OUT / "report" / "tokenizer_overlap.json"
if out.exists() and "semantic" not in json.loads(out.read_text()):
    out.rename(out.with_name("tokenizer_overlap_superseded_r1.json"))     # the first version's output (the restricted-denominator shares), kept as the record of the correction
out.write_text(json.dumps(res, indent=1))
print(json.dumps(res["semantic"], indent=1))
for tag, r in res["cells"].items():
    print(f"{tag:22s} same-string share L/Q {100*r['semantic_share_llama']['share_occurrences_on_same_string_ids']:.1f}% / {100*r['semantic_share_qwen']['share_occurrences_on_same_string_ids']:.1f}% | "
          + " | ".join(f"h{h}: rho_pred {r[f'h{h}']['rho_pred_qhat']:.3f} rho_obs(q) {r[f'h{h}']['rho_obs_qhat_stored_values']:.3f} wshare L/Q {100*r[f'h{h}']['weight_share_on_shared_tuples_llama']:.1f}%/{100*r[f'h{h}']['weight_share_on_shared_tuples_qwen']:.1f}%" for h in (0, 1)))
