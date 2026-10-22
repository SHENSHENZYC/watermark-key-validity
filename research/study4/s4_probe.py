"""Study 4 timing probe (validation on inputs; validation keys only): generation throughput of the pinned model on MPS with and without
the hooks, by batch size, with peak RSS and MPS memory. Writes outputs/study4_v0.1/probe_<utc>.json. Keys >= 1,000,000 (the validation
namespace); the prompts are the pilot prompts (never production prompts); nothing here reads a committed threshold."""
import datetime, json, pathlib, resource, sys, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "tools"))
import s4_gen as G, s4_data as SD
from key_policy import check_keys

VAL_KEY = 1_000_301


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


def main(model_name="qwen", batches=(8, 16, 32), n_new_scan=64, n_new_full=256, cell="news_en_256"):
    import torch
    check_keys([VAL_KEY], "validation")
    man = json.loads((ROOT / "outputs/study4_v0.1/pilot/prompts_manifest.json").read_text())
    X = SD.load_prompts(man, cell, "pilot"); P = man["P"]
    t0 = time.time(); model, tok, info = G.load_model(model_name); info = G.prepare_info(model, tok, info); t_load = time.time() - t0
    rec = {"utc": f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}", "model": {k: v for k, v in info.items() if not k.startswith("_")}, "load_seconds": round(t_load, 1), "torch": torch.__version__,
           "prompt_cell": cell, "P": P, "runs": []}
    # warm-up
    G.generate_batch(model, info, X[:4, :P], 8, "none", seed=1)
    for B in batches:
        for mode, h, delta in (("none", 0, 0.0), ("kgw", 1, 2.0), ("kgw", 2, 2.0), ("gumbel", 2, 0.0)):
            pr = X[:B, :P]
            r = G.generate_batch(model, info, pr, n_new_scan, mode, key=VAL_KEY, h=h, delta=delta, seed=B * 10 + h)
            run = {"B": B, "mode": mode, "h": h, "delta": delta, "n_new": n_new_scan, "seconds": round(r["seconds"], 2), "seconds_model": round(r["seconds_model"], 2), "seconds_hook": round(r["seconds_hook"], 2),
                   "tok_per_s": round(r["tok_per_s"], 1), "cache_hits": r["cache_hits"], "cache_misses": r["cache_misses"], "rss_gb": round(rss_gb(), 2),
                   "mps_alloc_gb": round(torch.mps.current_allocated_memory() / 1e9, 2), "mps_driver_gb": round(torch.mps.driver_allocated_memory() / 1e9, 2),
                   "green_share": float(r["flag"].mean()) if mode == "kgw" else None, "mean_logp": float(r["logp"].mean()), "eos_mass_mean": float(r["eos_mass"].mean())}
            rec["runs"].append(run); print(json.dumps(run), flush=True)
    # one full-length run at the largest batch, each mode
    B = max(batches)
    for mode, h, delta in (("none", 0, 0.0), ("kgw", 1, 2.0), ("gumbel", 2, 0.0)):
        r = G.generate_batch(model, info, X[:B, :P], n_new_full, mode, key=VAL_KEY, h=h, delta=delta, seed=900 + h)
        run = {"B": B, "mode": mode, "h": h, "delta": delta, "n_new": n_new_full, "seconds": round(r["seconds"], 2), "seconds_model": round(r["seconds_model"], 2), "seconds_hook": round(r["seconds_hook"], 2),
               "tok_per_s": round(r["tok_per_s"], 1), "cache_hits": r["cache_hits"], "cache_misses": r["cache_misses"], "rss_gb": round(rss_gb(), 2),
               "mps_alloc_gb": round(torch.mps.current_allocated_memory() / 1e9, 2), "mps_driver_gb": round(torch.mps.driver_allocated_memory() / 1e9, 2),
               "green_share": float(r["flag"].mean()) if mode == "kgw" else None, "mean_logp": float(r["logp"].mean()), "eos_mass_mean": float(r["eos_mass"].mean()),
               "rep4_mean": float(G.rep_n(r["tokens"]).mean()), "sample_text": tok.decode(r["tokens"][0][:120])}
        rec["runs"].append(run); print(json.dumps(run, ensure_ascii=False), flush=True)
    out = ROOT / f"outputs/study4_v0.1/probe_{rec['utc'].replace(':', '').replace('-', '')}.json"; out.write_text(json.dumps(rec, indent=1, ensure_ascii=False)); print("wrote", out)


if __name__ == "__main__":
    main()
