"""Access census of the candidate null corpora and tokenizers: metadata only, nothing is downloaded.

Reads the Hugging Face Hub API (/api/datasets/<id>, /api/models/<id>, /api/datasets/<id>/tree/<rev>/<path>) and the
datasets-server (/size for published row counts; /first-rows for feature names only, no content is stored).
Writes outputs/corpora_census_<date>.json and prints a Markdown table. Paced at one request per second.
Usage: python3 tools/census_hub.py            (system python3 is enough; stdlib only)
Terms: research/corpora/TERMS_OF_USE_CHECK.md
"""
import datetime, glob, json, os, pathlib, sys, time, urllib.parse, urllib.request

UA = "watermark-key-validity-lab census (metadata only; one request per second)"
PACE = 1.0
TODAY = datetime.date.today().isoformat()
OUT = pathlib.Path(f"outputs/corpora_census_{TODAY}.json")

DATASETS = [
    # id, configs of interest (datasets-server names), tree paths to list (sizes), first-rows (config, split)
    ("allenai/c4", ["realnewslike"], ["realnewslike"], ("realnewslike", "validation")),
    ("Salesforce/wikitext", ["wikitext-103-raw-v1"], ["wikitext-103-raw-v1"], ("wikitext-103-raw-v1", "validation")),
    ("Hello-SimpleAI/HC3", ["all", "reddit_eli5", "open_qa", "wiki_csai", "medicine", "finance"], [""], ("all", "train")),
    ("wikimedia/wikipedia", [f"20231101.{l}" for l in ["en", "de", "fr", "es", "ru", "uk", "bg", "ar", "zh", "ja", "ko", "hi"]],
     [f"20231101.{l}" for l in ["en", "de", "fr", "es", "ru", "uk", "bg", "ar", "zh", "ja", "ko", "hi"]], ("20231101.ja", "train")),
    ("donfu/oa-stackexchange", ["default"], ["", "data"], ("default", "train")),
    ("HuggingFaceH4/stack-exchange-preferences", ["default"], [], ("default", "train")),
    # Common Pile v0.1 (Kandpal et al. 2025): per-document licence in metadata.license (added 2026-10-09 after R01)
    ("common-pile/news_filtered", ["default"], ["", "data"], ("default", "train")),
    ("common-pile/news", ["default"], ["", "data"], ("default", "train")),
    ("common-pile/project_gutenberg_filtered", ["default"], ["", "data"], ("default", "train")),
    ("common-pile/stackexchange_filtered", ["default"], ["", "data"], ("default", "train")),
    ("izumi-lab/wikinews-en-20230728", ["default"], [""], ("default", "train")),
]
MODELS = ["meta-llama/Llama-3.2-1B", "Qwen/Qwen2.5-1.5B"]
CACHE = pathlib.Path(os.path.expanduser("~/.cache/huggingface/hub"))


def get(url):
    time.sleep(PACE)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8")), r.status
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}"}, e.code
    except Exception as e:  # network error: record, never retry in a loop
        return {"error": f"{type(e).__name__}: {e}"}, None


def tree(ds, rev, path):
    """List one directory (non-recursive) with sizes; paginate through Link headers if present."""
    entries, url = [], f"https://huggingface.co/api/datasets/{ds}/tree/{rev}/{urllib.parse.quote(path)}?recursive=false"
    while url:
        time.sleep(PACE)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                entries += json.loads(r.read().decode("utf-8"))
                link = r.headers.get("Link", "")
                url = None
                for part in link.split(","):
                    if 'rel="next"' in part:
                        url = part[part.find("<") + 1:part.find(">")]
        except Exception as e:
            return entries, f"{type(e).__name__}: {e}"
    return entries, None


def main():
    census = {"date_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "user_agent": UA,
              "note": "metadata only; nothing downloaded; row counts are the datasets-server's viewer numbers, which are PARTIAL for large configs (see estimated_num_rows and viewer_count_is_partial); the dataset card is the published count", "datasets": {}, "models": {}}
    for ds, configs, paths, first in DATASETS:
        meta, st = get(f"https://huggingface.co/api/datasets/{ds}")
        cd = (meta.get("cardData") or {}) if isinstance(meta, dict) else {}
        rec = {"api_status": st, "sha": meta.get("sha"), "lastModified": meta.get("lastModified"), "gated": meta.get("gated"),
               "private": meta.get("private"), "card_license": cd.get("license"), "license_tags": [t for t in meta.get("tags", []) if t.startswith("license:")],
               "n_siblings": len(meta.get("siblings", [])), "configs": {}, "files": {}, "features": None}
        size, st2 = get(f"https://datasets-server.huggingface.co/size?dataset={urllib.parse.quote(ds)}")
        rec["size_api_status"] = st2
        if isinstance(size, dict) and "size" in size:
            rec["size_partial"] = size.get("partial")
            for c in size["size"].get("configs", []):
                if c.get("config") in configs:
                    rec["configs"][c["config"]] = {"num_rows": c.get("num_rows"), "estimated_num_rows": c.get("estimated_num_rows"),
                                                   "viewer_count_is_partial": bool(c.get("estimated_num_rows")) and c.get("estimated_num_rows") != c.get("num_rows"),
                                                   "parquet_bytes": c.get("num_bytes_parquet_files"), "original_bytes": c.get("num_bytes_original_files"), "splits": {}}
            for s in size["size"].get("splits", []):
                if s.get("config") in rec["configs"]:
                    rec["configs"][s["config"]]["splits"][s["split"]] = {"num_rows": s.get("num_rows"), "estimated_num_rows": s.get("estimated_num_rows"), "parquet_bytes": s.get("num_bytes_parquet_files")}
        else:
            rec["size_error"] = size.get("error") if isinstance(size, dict) else str(size)
        for p in paths:
            ents, err = tree(ds, rec["sha"] or "main", p)
            files = [e for e in ents if e.get("type") == "file"]
            rec["files"][p or "."] = {"n_files": len(files), "total_bytes": sum((e.get("lfs") or {}).get("size", e.get("size", 0)) or 0 for e in files),
                                      "examples": [e["path"] for e in files[:3]], "error": err,
                                      "n_dirs": len([e for e in ents if e.get("type") == "directory"])}
        fr, st3 = get(f"https://datasets-server.huggingface.co/first-rows?dataset={urllib.parse.quote(ds)}&config={urllib.parse.quote(first[0])}&split={first[1]}")
        if isinstance(fr, dict) and "features" in fr:
            rec["features"] = {"config": first[0], "split": first[1], "names": [f["name"] for f in fr["features"]]}
        else:
            rec["features"] = {"config": first[0], "split": first[1], "error": fr.get("error") if isinstance(fr, dict) else str(fr)}
        census["datasets"][ds] = rec
        print("censused", ds, flush=True)
    for m in MODELS:
        meta, st = get(f"https://huggingface.co/api/models/{m}")
        cd = (meta.get("cardData") or {}) if isinstance(meta, dict) else {}
        snaps = sorted(glob.glob(str(CACHE / f"models--{m.replace('/', '--')}" / "snapshots" / "*")))
        rec = {"api_status": st, "sha": meta.get("sha"), "lastModified": meta.get("lastModified"), "gated": meta.get("gated"), "card_license": cd.get("license"),
               "local_snapshots": [os.path.basename(s) for s in snaps], "local_tokenizer": None}
        for s in snaps:
            tj = pathlib.Path(s) / "tokenizer.json"
            if tj.exists():
                j = json.loads(tj.read_text())
                rec["local_tokenizer"] = {"snapshot": os.path.basename(s), "vocab": len(j["model"]["vocab"]), "added_tokens": len(j.get("added_tokens", [])),
                                          "type": j["model"]["type"], "matches_hub_sha": os.path.basename(s) == meta.get("sha")}
        census["models"][m] = rec
        print("censused", m, flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(census, indent=1, sort_keys=True))
    print("wrote", OUT)
    # Markdown table
    print("\n| Source | Revision (sha) | Licence (card) | Gated | Config: rows (published) | Files listed (bytes) |")
    print("|---|---|---|---|---|---|")
    for ds, rec in census["datasets"].items():
        rows = "; ".join((f"{c}: {v['num_rows']:,}" + (f" (viewer partial; est. {v['estimated_num_rows']:,})" if v.get("viewer_count_is_partial") else "")) if v.get("num_rows") else f"{c}: ?" for c, v in rec["configs"].items())
        files = "; ".join(f"{p}: {v['n_files']} files, {v['total_bytes']/1e9:.2f} GB" for p, v in rec["files"].items())
        print(f"| {ds} | {str(rec['sha'])[:12]} | {rec['card_license']} | {rec['gated']} | {rows} | {files} |")
    for m, rec in census["models"].items():
        lt = rec["local_tokenizer"] or {}
        print(f"| {m} (tokenizer) | {str(rec['sha'])[:12]} | {rec['card_license']} | {rec['gated']} | vocab {lt.get('vocab')} + {lt.get('added_tokens')} added; cached snapshot matches hub: {lt.get('matches_hub_sha')} | — |")


if __name__ == "__main__":
    main()
