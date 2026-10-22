"""Compute check for the Stage 1 brief: load time, forward throughput and generation speed on Apple MPS.
Offline only (HF_HUB_OFFLINE=1): uses models already in the local cache."""
import os, sys, time, gc
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def bench(mid):
    print(f"=== {mid} ===", flush=True)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(mid)
    try:
        model = AutoModelForCausalLM.from_pretrained(mid, dtype=torch.bfloat16)
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(mid, torch_dtype=torch.bfloat16)
    model = model.to("mps").eval()
    print(f"load: {time.time()-t0:.1f}s; params={sum(p.numel() for p in model.parameters())/1e9:.2f}B", flush=True)
    text = "The quick brown fox jumps over the lazy dog. " * 60
    ids = tok(text, return_tensors="pt", truncation=True, max_length=256).input_ids.to("mps")
    with torch.no_grad():
        for bs in (1, 8):
            x = ids.repeat(bs, 1)
            model(x); torch.mps.synchronize()
            t = time.time()
            for _ in range(3):
                model(x); torch.mps.synchronize()
            dt = (time.time() - t) / 3
            print(f"forward bs={bs} seq=256: {dt:.3f}s/call = {bs*256/dt:.0f} tok/s (logits incl.)", flush=True)
            torch.mps.empty_cache()
        if tok.pad_token_id is None:
            tok.pad_token = tok.eos_token
        p = tok("Write a short paragraph about statistics and machine learning.", return_tensors="pt").input_ids.to("mps")
        for bs in (1, 8):
            pb = p.repeat(bs, 1)
            torch.mps.synchronize(); t = time.time()
            g = model.generate(pb, max_new_tokens=128, min_new_tokens=128, do_sample=True, top_p=0.95, temperature=1.0, pad_token_id=tok.pad_token_id)
            torch.mps.synchronize(); dt = time.time() - t
            n = (g.shape[1] - p.shape[1]) * bs
            print(f"generate bs={bs}: {n} new tokens in {dt:.1f}s = {n/dt:.1f} tok/s", flush=True)
            torch.mps.empty_cache()
    try:
        print(f"driver allocated: {torch.mps.driver_allocated_memory()/1e9:.2f} GB", flush=True)
    except Exception as e:
        print("mem n/a", e)
    del model; gc.collect(); torch.mps.empty_cache()

for mid in sys.argv[1:]:
    try:
        bench(mid)
    except Exception as e:
        print(f"FAILED {mid}: {type(e).__name__}: {e}", flush=True)
print("DONE", flush=True)
