"""Paced download of arXiv PDFs for a gate, with a hashed manifest, then text extraction (pdftotext, reading order).

Terms: research/literature/TERMS_OF_USE_CHECK.md (one request per >= 4 s, single connection, personal research use,
no redistribution; PDFs and text are git-ignored, the manifest is tracked).
Usage: python3 tools/fetch_arxiv_pdfs.py <gate-tag> <arxiv-id> [<arxiv-id> ...]
"""
import datetime, hashlib, json, pathlib, subprocess, sys, time, urllib.request

PDF_DIR = pathlib.Path("research/literature/pdfs")
TXT_DIR = pathlib.Path("research/literature/txt")
MANIFEST = pathlib.Path("research/literature/pdf_manifest.json")
PACE_S = 4.0
UA = "watermark-key-validity-lab research reader (paced: one request per 4 s, single connection)"


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(tag, ids):
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    man = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"terms": "research/literature/TERMS_OF_USE_CHECK.md", "entries": {}}
    for aid in ids:
        out = PDF_DIR / f"{aid}.pdf"
        entry = man["entries"].get(aid)
        if out.exists() and entry and "sha256" in entry:
            if hashlib.sha256(out.read_bytes()).hexdigest() != entry["sha256"]:
                print("HASH MISMATCH", aid, flush=True)
            else:
                print("skip (cached)", aid, flush=True)
        else:
            url = f"https://arxiv.org/pdf/{aid}"
            t0 = time.time()
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=180) as r:
                    data, final, status = r.read(), r.geturl(), r.status
            except Exception as e:  # network or HTTP error: record the gap, never retry in a loop
                man["entries"][aid] = {"gate": tag, "url": url, "retrieved_utc": now(), "error": f"{type(e).__name__}: {e}"}
                MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=True))
                print("FAIL", aid, type(e).__name__, e, flush=True)
                time.sleep(max(0.0, PACE_S - (time.time() - t0)))
                continue
            if not data.startswith(b"%PDF"):
                man["entries"][aid] = {"gate": tag, "url": url, "final_url": final, "retrieved_utc": now(), "error": f"not a PDF (status {status}, {len(data)} bytes)"}
                MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=True))
                print("NOT PDF", aid, status, data[:80], flush=True)
                time.sleep(max(0.0, PACE_S - (time.time() - t0)))
                continue
            out.write_bytes(data)
            man["entries"][aid] = {"gate": tag, "url": url, "final_url": final, "retrieved_utc": now(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=True))
            print("ok", aid, len(data), "bytes", flush=True)
            time.sleep(max(0.0, PACE_S - (time.time() - t0)))
        txt = TXT_DIR / f"{aid}.txt"
        if out.exists() and not txt.exists():
            subprocess.run(["pdftotext", str(out), str(txt)], check=False)
            if txt.exists():
                pages = txt.read_text(errors="replace").count("\f") + 1
                man["entries"][aid]["pdftotext_pages"] = pages
                MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=True))
                print("   text:", pages, "pages", flush=True)
    print("DONE", tag, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
