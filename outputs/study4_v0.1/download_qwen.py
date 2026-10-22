"""Download Qwen/Qwen2.5-1.5B weights at the pinned revision (Apache-2.0; terms in research/corpora/TERMS_OF_USE_CHECK.md) into the
Hugging Face cache; the tokenizer files are already cached at this revision. Writes a manifest with sizes and SHA-256 digests."""
import hashlib, json, os, pathlib, time, datetime
os.environ["HF_HUB_OFFLINE"] = "0"
from huggingface_hub import snapshot_download, HfApi
REPO, REV = "Qwen/Qwen2.5-1.5B", "8faed761d45a263340a0528343f099c05c9a4323"
t0 = time.time()
p = snapshot_download(REPO, revision=REV, allow_patterns=["model.safetensors", "generation_config.json", "LICENSE", "README.md", "config.json", "tokenizer*", "vocab.json", "merges.txt"])
el = time.time() - t0
info = HfApi().model_info(REPO, revision=REV, files_metadata=True)
hub = {s.rfilename: {"size": s.size, "lfs_sha256": (s.lfs.sha256 if s.lfs else None)} for s in info.siblings}
man = {"repo": REPO, "revision": REV, "downloaded_utc": f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}", "seconds": round(el, 1), "snapshot_dir": p, "license": "apache-2.0", "files": {}}
for f in sorted(pathlib.Path(p).iterdir()):
    if f.is_file() or f.is_symlink():
        b = f.read_bytes(); d = hashlib.sha256(b).hexdigest()
        man["files"][f.name] = {"bytes": len(b), "sha256": d, "hub_size": hub.get(f.name, {}).get("size"), "hub_lfs_sha256": hub.get(f.name, {}).get("lfs_sha256"),
                                "match": (hub.get(f.name, {}).get("lfs_sha256") in (None, d)) and (hub.get(f.name, {}).get("size") == len(b))}
pathlib.Path("outputs/study4_v0.1/model_manifest_qwen2.5-1.5b.json").write_text(json.dumps(man, indent=1))
print(json.dumps({k: (v["bytes"], v["match"]) for k, v in man["files"].items()}, indent=1)); print("seconds", round(el, 1))
