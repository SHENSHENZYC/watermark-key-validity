#!/usr/bin/env python3
"""Build ``research/paper/references.bib`` from primary sources (guide A4.4; outline §8).

Every entry is assembled from a primary record fetched at build time and saved under ``research/paper/bib_sources/``:
the arXiv API (one ``id_list`` call for every e-print; titles, authors, dates, versions), Crossref for every DOI
(the journal, volume, issue, pages, dates), the PMLR proceedings pages (ICML 2023, ACML 2012; their ``citation_*``
meta tags), TMLR's own bib record, the GitHub API for the four repository artefacts (repository, tag or commit, date),
and the page of the one blog lecture (title and date). Venues the arXiv record does not carry were confirmed on the
proceedings' own listings before this script was written (ICLR 2024's paper list for Unigram and the reliability
paper; TMLR's paper list; the covers of the ICLR 2026 and NeurIPS 2025 PDFs) and are stated in the entry notes
with that source. Regulator and vendor documents are cited by their document identifiers and the date read
(constraint 33). Author order is taken from the arXiv record and cross-checked against the local PDF cover
(``research/literature/txt``) and Crossref; every mismatch is printed and must be resolved by hand.

The saved records are projections (R13 F10): a GitHub commit record's ``files[].patch`` diff bodies and a Crossref
record's ``message.abstract`` are third-party text the entries never use, so they are removed from the records under
``bib_sources/github/`` and ``bib_sources/crossref/`` (each carries a ``_projection`` note saying what was removed) and
the full responses are kept under ``bib_sources/raw_responses/``, which the public snapshot excludes; the fetched web
pages stay git-ignored under ``bib_sources/pages/`` with their extracted facts and read dates in ``pages/extracted.json``.

Usage:  .venv/bin/python research/paper/build_references.py [--offline]   (offline: reuse the saved responses)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SRC = HERE / "bib_sources"
TXT = ROOT / "research" / "literature" / "txt"
UA = "watermark-key-validity-lab bibliography builder (mailto:alexyczhao@gmail.com)"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d")
RAW = SRC / "raw_responses"   # the full API responses (the private record; excluded from the public snapshot, R13 F10)
PROJECTED: dict[str, list[str]] = {}   # record name -> the fields the projection removed (written to the fetch log)
FETCHED_NOW: set[Path] = set()   # the files actually downloaded in this run (the others keep their file date as the date read)
PROJECTION_NOTE = ("A projection of the API response for the public record (R13 F10): {what} removed and kept in the private "
                   "record under research/paper/bib_sources/raw_responses/, which the public snapshot excludes; every other "
                   "field is verbatim.")

# ---------------------------------------------------------------------------------------------------------------
# The entries. ``arxiv`` = the e-print read (version checked at build); ``doi`` = the published record; ``venue`` =
# the published venue with the source that confirmed it; ``pages_note`` = where the text's page references point.
# ---------------------------------------------------------------------------------------------------------------
ARXIV_ONLY = {  # key: (arxiv id, note)
    "cai2025collision": ("2510.22007", ""),
    "huang2023optimal": ("2312.07930", ""),
    "gloaguen2026unified": ("2602.06754", "The text's page reference follows this e-print."),
    "gloaguen2026automark": ("2609.37310", "The text's equation, algorithm, proposition and page references follow this e-print."),
    "fernandez2026posthoc": ("2512.16904", "The text's page reference follows this e-print."),
    "sander2026textseal": ("2605.12456", ""),
    "fu2025multiuse": ("2506.15975", ""),
    "aremu2026activation": ("2603.23171", ""),
    "delbianco2026compliance": ("2610.06317", ""),
    "nemecek2026crosslingual": ("2608.20047", ""),
    "lichen2026chainmark": ("2607.18445", ""),
    "ding2026reference": ("2609.32678", ""),
    "park2026luna": ("2606.00613", "EMNLP 2026 by the arXiv record's comment; the ACL Anthology entry was not yet available on the build date."),
    "li2026tiwm": ("2610.14378", ""),
    "wang2026bytemark": ("2610.14427", ""),
    "ma2026predictive": ("2609.15657", "The text's page reference follows this e-print."),
    "khachaturov2025repetition": ("2504.12229", ""),
    "su2026anytime": ("2602.14286", ""),
    "huang2026anytime": ("2602.17608", ""),
    "luo2026anytime": ("2607.21958", ""),
    "lihe2026saccopula": ("2608.20839", "Accepted to Findings of EMNLP 2026 by the arXiv record's comment."),
    "globalsketch2026": ("2606.04486", ""),
    "wu2024collision": ("2406.02603", "Read at abstract level at the claim gate; cited to keep the sense of 'key collision' distinct."),
    "zhou2026blade": ("2610.23601", "Read at abstract level at the final gate (2026-10-21); cited for the many-key multiplicity effect and its power price, kept apart from the fixed-key effect (constraint 3)."),
}
PUBLISHED = {  # key: dict(arxiv, type, doi | venue fields, note)
    "kirchenbauer2023watermark": dict(arxiv="2301.10226", type="inproceedings", pmlr="https://proceedings.mlr.press/v202/kirchenbauer23a.html",
                                      booktitle="Proceedings of the 40th International Conference on Machine Learning (ICML 2023)", series="Proceedings of Machine Learning Research", volume="202", publisher="PMLR", note="The PMLR proceedings page is the source of the pages and the author order."),
    "kirchenbauer2024reliability": dict(arxiv="2306.04634", type="inproceedings", booktitle="The Twelfth International Conference on Learning Representations (ICLR 2024)",
                                        iclr_bib="https://proceedings.iclr.cc/paper_files/paper/2024/file/d78e9e4316e1714fbb0f20be66f8044c-Bibtex-Conference.bib",
                                        note="Venue from the paper's cover ('Published as a conference paper at ICLR 2024') and the ICLR 2024 paper list; the pages from the proceedings' own BibTeX record; the text's page reference follows the e-print."),
    "zhao2024unigram": dict(arxiv="2306.17439", type="inproceedings", booktitle="The Twelfth International Conference on Learning Representations (ICLR 2024)",
                            iclr_bib="https://proceedings.iclr.cc/paper_files/paper/2024/file/beae9ed5316bcc48e616754c06c11875-Bibtex-Conference.bib",
                            note="Venue from the ICLR 2024 paper list (iclr.cc) and the pages from the proceedings' own BibTeX record; the text's lemma, remark and page references (Lemma C.21 pp. 31–32, Remark E.2 p. 34, Lemma F.2 p. 36) follow the e-print."),
    "fernandez2023bricks": dict(arxiv="2308.00113", type="inproceedings", doi="10.1109/WIFS58808.2023.10374576",
                                booktitle="2023 IEEE International Workshop on Information Forensics and Security (WIFS)", publisher="IEEE", note="The text's page references follow the e-print."),
    "kuditipudi2024distortion": dict(arxiv="2307.15593", type="article", journal="Transactions on Machine Learning Research", tmlr="FpaCL1MO2C", issn="2835-8856",
                                     note="TMLR's own bib record (jmlr.org/tmlr/papers/bib/FpaCL1MO2C.bib) is the source of the venue and year; the text's page reference follows the e-print."),
    "li2025framework": dict(arxiv="2404.01245", type="article", doi="10.1214/24-AOS2468", note=""),
    "li2025robust": dict(arxiv="2411.13868", type="article", doi="10.1093/jrsssb/qkaf056", note="The text's page reference follows the e-print."),
    "jovanovic2025image": dict(arxiv="2506.16349", type="inproceedings", doi="10.52202/085713-2411", booktitle="Advances in Neural Information Processing Systems 38 (NeurIPS 2025)",
                               note="Venue from the paper's cover and the proceedings record; the text's page and equation references (p. 27, Equation 9) follow the e-print."),
    "gloaguen2026diffusion": dict(arxiv="2509.24368", type="inproceedings", booktitle="The Fourteenth International Conference on Learning Representations (ICLR 2026)",
                                  iclr_bib="https://proceedings.iclr.cc/paper_files/paper/2026/file/a30d1f9de116aa3184e66a3e9d96b69d-Bibtex-Conference.bib",
                                  note="Venue from the paper's cover ('Published as a conference paper at ICLR 2026') and the pages from the proceedings' own BibTeX record; the text's page reference (p. 21, the appendix) follows the e-print."),
    "vovk2012conditional": dict(arxiv="1209.2673", type="inproceedings", pmlr="https://proceedings.mlr.press/v25/vovk12.html",
                                booktitle="Proceedings of the Asian Conference on Machine Learning (ACML 2012)", series="Proceedings of Machine Learning Research", volume="25", publisher="PMLR",
                                note="The propositions the text cites (2a, 2b) are numbered as in the e-print."),
    "bian2023training": dict(arxiv="2205.03647", type="article", doi="10.1214/23-EJS2145", note="The text's page reference (p. 2) follows the e-print."),
    "liang2025algorithmic": dict(arxiv="2311.04295", type="article", doi="10.1214/25-AOS2510", note=""),
    "ren2022derandomized": dict(arxiv="2205.15461", type="article", doi="10.1093/jrsssb/qkad085", note="The text's page reference (p. 11) follows the e-print."),
    "xie2025classroom": dict(arxiv="2507.23113", type="article", doi="10.1162/99608f92.072aebb0", note=""),
    "kandpal2025commonpile": dict(arxiv="2506.05209", type="inproceedings", doi="10.52202/085713-1918", booktitle="Advances in Neural Information Processing Systems 38 (NeurIPS 2025)", note=""),
}
DOI_ONLY = {
    "nist2024ai1004": dict(type="techreport", doi="10.6028/NIST.AI.100-4", note=""),   # rendered below from its Crossref record and the local cover
    "owen1956tables": dict(type="article", doi="10.1214/aoms/1177728074", note=""),
    "dathathri2024synthid": dict(type="article", doi="10.1038/s41586-024-08025-4", note="Cited for the paper's own words only; nothing about any deployment is claimed (constraint 6)."),
    "islam2026reliable": dict(type="article", doi="10.1016/j.cosrev.2026.101074", note="The publisher's record only (created 2026-10-05); the full text is behind the publisher and was not read."),
}
ARXIV_IDS = sorted({v[0] for v in ARXIV_ONLY.values()} | {v["arxiv"] for v in PUBLISHED.values()})


def get(url: str, pause: float = 1.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    time.sleep(pause)
    return data


def fetch(url: str, dest: Path, offline: bool, pause: float = 1.0) -> bytes:
    if offline or dest.exists():
        return dest.read_bytes()
    data = get(url, pause)
    dest.write_bytes(data); FETCHED_NOW.add(dest)
    return data


def read_date(p: Path) -> str:
    """The UTC date a saved page was read: today if it was fetched in this run, else the file's own date."""
    return NOW if p in FETCHED_NOW else datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).strftime("%Y-%m-%d")


def project(data, kind: str, name: str):
    """The public projection of an API response (R13 F10). GitHub: every ``files[].patch`` (the diff bodies of the cited
    commits: third-party manuscript and code text) removed, the file list's names, statuses, sizes, digests and URLs kept.
    Crossref: ``message.abstract`` (the publisher's abstract) removed. Every other field verbatim; a ``_projection`` note
    says what was removed (a list response, such as a tag list, carries no text body and no note)."""
    out = json.loads(json.dumps(data)); removed: list[str] = []
    if kind == "github" and isinstance(out, dict):
        for f in out.get("files") or []:
            if "patch" in f:
                removed.append(f"files[].patch of {f.get('filename')} ({len(f['patch'])} characters)"); del f["patch"]
    elif kind == "crossref" and isinstance(out, dict):
        msg = out.get("message") or {}
        if "abstract" in msg:
            removed.append(f"message.abstract ({len(msg['abstract'])} characters)"); del msg["abstract"]
    if isinstance(out, dict):
        out["_projection"] = PROJECTION_NOTE.format(what="; ".join(removed) if removed else "nothing (this response carries no third-party text body)")
    PROJECTED[f"{kind}/{name}"] = removed
    return out


def saved(kind: str, name: str, offline: bool, getter) -> dict | list:
    """A JSON API response: the full response is kept under ``raw_responses/<kind>/`` (the private record) and its
    projection written under ``<kind>/`` (distributed). Offline, the full response is read if present, else the projection
    (every field the entries use is in both)."""
    raw, proj = RAW / kind / name, SRC / kind / name
    if raw.exists():
        data = json.loads(raw.read_text())
    elif offline:
        data = json.loads(proj.read_text())
    else:
        text = getter(); raw.parent.mkdir(parents=True, exist_ok=True); raw.write_text(text); FETCHED_NOW.add(raw); data = json.loads(text)
    proj.write_text(json.dumps(project(data, kind, name), indent=1, sort_keys=True) + "\n")
    return data


def gh(path: str, name: str, offline: bool) -> dict | list:
    return saved("github", name, offline, lambda: subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True).stdout)


def gh_user(login: str, name: str, offline: bool) -> dict:
    """A user record: only the public name fields are kept on disk (no raw copy of the profile)."""
    proj = SRC / "github" / name
    if offline or proj.exists():
        return json.loads(proj.read_text())
    full = json.loads(subprocess.run(["gh", "api", f"users/{login}"], capture_output=True, text=True, check=True).stdout)
    user = {k: full.get(k) for k in ("login", "name", "type", "html_url")}
    proj.write_text(json.dumps(user, indent=1) + "\n")
    return user


def bibtex_escape(s: str) -> str:
    return s.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")


def render(key: str, etype: str, fields: dict) -> str:
    lines = [f"@{etype}{{{key},"]
    for k, v in fields.items():
        if v is None or v == "":
            continue
        lines.append(f"  {k} = {{{v}}},")
    lines[-1] = lines[-1].rstrip(",")
    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="reuse the saved responses in bib_sources/")
    args = ap.parse_args()
    SRC.mkdir(exist_ok=True); (SRC / "crossref").mkdir(exist_ok=True); (SRC / "github").mkdir(exist_ok=True); (SRC / "pages").mkdir(exist_ok=True)
    log: dict[str, dict] = {}
    warnings: list[str] = []
    resolved: list[str] = []

    # --- arXiv ---------------------------------------------------------------------------------------------------
    xml = fetch("https://export.arxiv.org/api/query?id_list=" + ",".join(ARXIV_IDS) + "&max_results=100", SRC / "arxiv_entries.xml", args.offline, pause=3.5)
    ns = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}
    arx: dict[str, dict] = {}
    for e in ET.fromstring(xml).findall("a:entry", ns):
        full = e.find("a:id", ns).text.split("/abs/")[1]
        aid, ver = re.match(r"(.+)v(\d+)$", full).groups()
        cat = e.find("ar:primary_category", ns)
        arx[aid] = {"title": " ".join(e.find("a:title", ns).text.split()), "authors": [" ".join(a.find("a:name", ns).text.split()) for a in e.findall("a:author", ns)],
                    "published": e.find("a:published", ns).text[:10], "updated": e.find("a:updated", ns).text[:10], "version": int(ver),
                    "primary": cat.get("term") if cat is not None else "", "comment": " ".join((e.find("ar:comment", ns).text or "").split()) if e.find("ar:comment", ns) is not None else ""}
    missing = [i for i in ARXIV_IDS if i not in arx]
    assert not missing, f"arXiv ids not returned: {missing}"

    # --- Crossref --------------------------------------------------------------------------------------------------
    cr: dict[str, dict] = {}
    for key, spec in list(PUBLISHED.items()) + list(DOI_ONLY.items()):
        doi = spec.get("doi")
        if doi:
            url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
            cr[key] = saved("crossref", doi.replace("/", "_") + ".json", args.offline, lambda u=url: get(u).decode("utf-8"))["message"]

    # --- PMLR pages, TMLR bib, GitHub, the lecture page ----------------------------------------------------------
    def pmlr_meta(url: str, name: str) -> dict:
        html = fetch(url, SRC / "pages" / f"{name}.html", args.offline).decode("utf-8", "replace")
        meta: dict[str, list[str]] = {}
        for m in re.finditer(r'<meta name="citation_([a-z_]+)" content="([^"]*)"', html):
            meta.setdefault(m.group(1), []).append(m.group(2))
        return meta
    pmlr = {k: pmlr_meta(v["pmlr"], k) for k, v in PUBLISHED.items() if "pmlr" in v}
    tmlr_bib = fetch("https://jmlr.org/tmlr/papers/bib/FpaCL1MO2C.bib", SRC / "pages" / "tmlr_FpaCL1MO2C.bib", args.offline).decode()
    assert "Transactions on Machine Learning Research" in tmlr_bib and "year={2024}" in tmlr_bib.replace(" ", "")
    gen_repo = gh("repos/nisaharan/when-nominal-false-positive-rates-fail", "genhatharan_repo.json", args.offline)
    gen_tags = gh("repos/nisaharan/when-nominal-false-positive-rates-fail/tags", "genhatharan_tags.json", args.offline)
    gen_v1 = next(t for t in gen_tags if t["name"] == "v1")
    gen_tag_commit = gh(f"repos/nisaharan/when-nominal-false-positive-rates-fail/commits/{gen_v1['commit']['sha']}", "genhatharan_v1_commit.json", args.offline)
    syn_repo = gh("repos/xlr8harder/synthid", "xlr8harder_synthid_repo.json", args.offline)
    syn_commit = gh("repos/xlr8harder/synthid/commits/b3adb0f13301506e6ee0f49be26e99f6abde5829", "xlr8harder_synthid_commit.json", args.offline)
    kl_repo = gh("repos/katcinskiy/keylottery", "keylottery_repo.json", args.offline)
    kl_commit = gh("repos/katcinskiy/keylottery/commits/8ebb6b4f52927d0adbe9084d53ba49f3f825d6eb", "keylottery_commit.json", args.offline)
    kl_user = gh_user("katcinskiy", "keylottery_user.json", args.offline)   # only the public name fields are kept on disk
    assert kl_user["name"] == "Alexander Yukhimchuk" == kl_commit["commit"]["author"]["name"] and kl_repo["license"] is None, (kl_user.get("name"), kl_repo.get("license"))
    lw_repo = gh("repos/HugoAlbertBonet/llmwatermark", "llmwatermark_repo.json", args.offline)
    lw_commit = gh("repos/HugoAlbertBonet/llmwatermark/commits/6261c02de24cdc3005bc6eafe2147b9405cb63a7", "llmwatermark_commit.json", args.offline)
    lw_readme = gh("repos/HugoAlbertBonet/llmwatermark/commits/e2d47aef5f18c119647c65655dae44c877813895", "llmwatermark_readme_commit.json", args.offline)   # R13 F6: the README that carries the caveat
    assert lw_repo["license"]["spdx_id"] == "MIT" and lw_commit["commit"]["author"]["date"][:10] == "2026-08-31" == lw_readme["commit"]["author"]["date"][:10], (lw_repo.get("license"), lw_commit["commit"]["author"]["date"])
    assert "Measured over 24 keys" in lw_commit["commit"]["message"], lw_commit["commit"]["message"][:80]
    lecture = fetch("https://scottaaronson.blog/?p=6823", SRC / "pages" / "aaronson_lecture.html", args.offline).decode("utf-8", "replace")
    lec_title = re.search(r"<title>(.*?)</title>", lecture, re.S).group(1)
    lec_date = re.search(r'article:published_time" content="([0-9-]+)', lecture).group(1)
    assert "My AI Safety Lecture for UT Effective Altruism" in lec_title and lec_date == "2022-11-29" and "watermark" in lecture.lower()
    # the fetched third-party pages stay local (git-ignored); the facts the entries use are recorded here with the UTC date
    # each page was read (the file's own date when it was not fetched in this run)
    read_utc = {name: read_date(SRC / "pages" / name) for name in ["aaronson_lecture.html"] + [f"{k}.html" for k in pmlr]}
    (SRC / "pages" / "extracted.json").write_text(json.dumps({"pmlr": pmlr, "lecture": {"title": lec_title, "published_time": lec_date, "mentions_watermark": True},
                                                              "read_utc": read_utc, "fetched_utc": max(read_utc.values())}, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    # --- helpers ---------------------------------------------------------------------------------------------------
    cover_log: dict[str, str] = {}
    # Author orders confirmed by eye on the local PDF cover where the extracted text's order differs from the arXiv record's
    # (R12 round 2, F16: the extraction can emit the names of one line out of order, so an automatic reorder is never applied).
    COVER_ORDER_VERIFIED = {
        "sander2026textseal": ["Tom Sander", "Hongyan Chang", "Sylvestre-Alvise Rebuffi", "Tomáš Souček", "Tuan Tran", "Valeriu Lacatusu", "Alexandre Mourachko",
                               "Surya Parimi", "Christophe Ropers", "Rashel Moritz", "Vanessa Stark", "Hady Elsahar", "Pierre Fernandez"],   # the v2 cover, viewed 2026-10-19 and 2026-10-20
    }
    COVER_ORDER_CONFIRMED_ARXIV = {"huang2026anytime": "the v1 cover viewed 2026-10-20: Huang, Xu, Ramchandran, Jiao, Jordan, the arXiv order; the extracted text emits Jordan before Jiao"}

    def cover_check(key: str, aid: str, authors: list[str]) -> list[str]:
        """Compare every author's position on the local PDF cover (the first 1,500 characters of the extracted text) with the
        arXiv record's order. Returns the authors in the cover's order when every surname is found once and the order differs
        (the cover of the cited version wins, guide A4.4), the arXiv order otherwise; records what was checked or skipped."""
        txt = TXT / f"{aid}.txt"
        if not txt.exists():
            cover_log[key] = "no local PDF text: the cover was not checked"
            return authors
        import unicodedata
        head = unicodedata.normalize("NFC", txt.read_text(errors="replace")[:1500])
        surnames = [unicodedata.normalize("NFC", a.split()[-1]) for a in authors]
        pos = {s: head.find(s) for s in surnames}
        missing = [s for s, p in pos.items() if p < 0]
        if missing:
            cover_log[key] = f"{len(authors)} authors; not found on the cover text: {missing}"
            warnings.append(f"{key}: author surname(s) {missing} not in the first 1,500 characters of the local PDF text")
            return authors
        if len(set(surnames)) != len(surnames) or any(head.count(s) != 1 for s in surnames):
            cover_log[key] = f"{len(authors)} authors; a surname repeats on the cover, order compared on the first two only"
            if len(surnames) > 1 and head.index(surnames[1]) < head.index(surnames[0]):
                warnings.append(f"{key}: the local cover lists {surnames[1]!r} before {surnames[0]!r}")
            return authors
        order = sorted(range(len(authors)), key=lambda i: pos[surnames[i]])
        if order == list(range(len(authors))):
            cover_log[key] = f"{len(authors)} authors in the arXiv order on the cover text"
            return authors
        if key in COVER_ORDER_VERIFIED:
            ver = COVER_ORDER_VERIFIED[key]
            assert sorted(ver) == sorted(authors), (key, ver, authors)
            cover_log[key] = f"{len(authors)} authors; the cover's order differs from the arXiv record's, confirmed by eye, and is used"
            resolved.append(f"{key}: the PDF cover orders the authors {ver} while the arXiv record gives {authors}; the cover order, confirmed by eye, is used and noted")
            return ver
        if key in COVER_ORDER_CONFIRMED_ARXIV:
            cover_log[key] = f"{len(authors)} authors; the extracted text's order differs from the arXiv record's; {COVER_ORDER_CONFIRMED_ARXIV[key]}; the arXiv order is used"
            return authors
        cover_log[key] = f"{len(authors)} authors; the extracted text's order differs from the arXiv record's and has not been checked by eye: the arXiv order is kept"
        warnings.append(f"{key}: the extracted cover text orders the authors {[authors[i] for i in order]} against the arXiv record's {authors}; view the PDF cover and record the verified order")
        return authors

    def cr_check(key: str, authors: list[str]) -> None:
        if key not in cr:
            return
        fam = [a.get("family", "") for a in cr[key].get("author", [])]
        mine = [a.split()[-1] for a in authors]
        if fam and [f.lower() for f in fam] != [m.lower() for m in mine]:
            resolved.append(f"{key}: the published record's author order {fam} differs from the arXiv order {mine}; the published order is used and noted")

    def arx_fields(aid: str) -> dict:
        a = arx[aid]
        return {"eprint": aid, "archiveprefix": "arXiv", "primaryclass": a["primary"], "url": f"https://arxiv.org/abs/{aid}v{a['version']}"}

    def and_join(names: list[str]) -> str:
        return " and ".join(names)

    entries: dict[str, str] = {}
    used_versions: dict[str, str] = {}

    # --- arXiv-only e-prints ---------------------------------------------------------------------------------------
    for key, (aid, note) in ARXIV_ONLY.items():
        a = arx[aid]; authors = cover_check(key, aid, a["authors"])
        order_note = "" if authors == a["authors"] else " Author order from the PDF cover of this version, which differs from the arXiv metadata's order."
        f = {"author": and_join(authors), "title": a["title"], "year": a["published"][:4], "month": a["published"][5:7],
             "howpublished": f"arXiv e-print {aid}v{a['version']}", **arx_fields(aid),
             "note": (f"arXiv:{aid}v{a['version']} ({a['updated']}). " + note + order_note).strip()}
        entries[key] = render(key, "misc", f); used_versions[key] = f"{aid}v{a['version']}"
        log[key] = {"source": f"arXiv API id {aid}", "version": a["version"], "cover": cover_log.get(key, "")}

    # --- published papers with an e-print --------------------------------------------------------------------------
    for key, spec in PUBLISHED.items():
        aid = spec["arxiv"]; a = arx[aid]; cover_authors = cover_check(key, aid, a["authors"]); cr_check(key, a["authors"])
        f: dict = {"author": and_join(cover_authors), "title": a["title"]}
        if cover_authors != a["authors"]:
            spec = dict(spec, note=spec.get("note", "") + " Author order from the PDF cover of the cited e-print version, which differs from the arXiv metadata's order.")
        src = [f"arXiv API id {aid}"]
        order_note = ""
        if key in cr:
            d = cr[key]; year = str(d["issued"]["date-parts"][0][0]); src.append(f"Crossref {spec['doi']}")
            f["year"] = year
            fam_cr = [x.get("family", "").lower() for x in d.get("author", [])]
            if fam_cr and fam_cr != [x.split()[-1].lower() for x in a["authors"]]:
                # the published record's author order wins over the e-print's (guide A4.4: the cover of the published version)
                f["author"] = and_join([f"{x.get('given', '')} {x.get('family', '')}".strip() for x in d["author"]])
                order_note = " Author order from the published record; the arXiv record lists the authors in a different order."
            if spec["type"] == "article":
                f["journal"] = d["container-title"][0]
                f["volume"] = d.get("volume"); f["number"] = d.get("issue"); f["pages"] = (d.get("page") or d.get("article-number") or "").replace("-", "--")
            else:
                f["booktitle"] = spec["booktitle"]; f["pages"] = (d.get("page") or "").replace("-", "--"); f["publisher"] = spec.get("publisher") or d.get("publisher")
            f["doi"] = spec["doi"]
        elif "pmlr" in spec:
            m = pmlr[key]; src.append(spec["pmlr"])
            assert m["title"][0].lower() == a["title"].lower(), (m["title"], a["title"])
            if [x.split()[-1] for x in m["author"]] != [x.split()[-1] for x in a["authors"]]:
                warnings.append(f"{key}: PMLR authors {m['author']} differ from arXiv {a['authors']}")
            f["author"] = and_join(m["author"]); f["booktitle"] = spec["booktitle"]; f["series"] = spec["series"]; f["volume"] = spec["volume"]
            f["pages"] = f"{m['citation_firstpage'][0] if 'citation_firstpage' in m else m['firstpage'][0]}--{m['lastpage'][0]}"
            f["publisher"] = spec["publisher"]; f["year"] = m["publication_date"][0][:4]; f["url"] = spec["pmlr"]
        elif "tmlr" in spec:
            src.append("https://jmlr.org/tmlr/papers/bib/FpaCL1MO2C.bib")
            f["journal"] = spec["journal"]; f["issn"] = spec["issn"]; f["year"] = "2024"; f["url"] = f"https://openreview.net/forum?id={spec['tmlr']}"
        else:  # ICLR papers: venue from the cover and the ICLR paper list; the pages from the proceedings' own BibTeX record (R12 F12)
            f["booktitle"] = spec["booktitle"]; f["year"] = spec["booktitle"].split("ICLR ")[1].rstrip(")")
            bib = fetch(spec["iclr_bib"], SRC / "pages" / f"iclr_{key}.bib", args.offline).decode("utf-8", "replace")
            pm = re.search(r"pages\s*=\s*\{(\d+)--(\d+)\}", bib); tm = re.search(r"(?<!book)title\s*=\s*\{(.*?)\}", bib, re.S)
            assert pm and tm, (key, bib[:200])
            assert re.sub(r"\W+", "", tm.group(1)).lower() == re.sub(r"\W+", "", a["title"]).lower(), (key, tm.group(1), a["title"])
            f["pages"] = f"{pm.group(1)}--{pm.group(2)}"; f["publisher"] = "ICLR"; src.append(spec["iclr_bib"])
        if "url" not in f:
            f["url"] = f"https://arxiv.org/abs/{aid}v{a['version']}"
        f["eprint"] = aid; f["archiveprefix"] = "arXiv"
        f["note"] = (f"arXiv:{aid}v{a['version']} ({a['updated']}). " + spec["note"] + order_note).strip()
        entries[key] = render(key, spec["type"], f); used_versions[key] = f"{aid}v{a['version']}"
        log[key] = {"source": "; ".join(src), "version": a["version"], "cover": cover_log.get(key, "")}

    # --- DOI-only ---------------------------------------------------------------------------------------------------
    for key, spec in DOI_ONLY.items():
        if key == "nist2024ai1004":
            continue   # a technical report: rendered below from its Crossref record and the local cover
        d = cr[key]
        authors = [f"{x.get('given', '')} {x.get('family', '')}".strip() for x in d.get("author", [])]
        created = d.get("created", {}).get("date-time", "")[:4]; issued = str(d["issued"]["date-parts"][0][0])
        year = created if key == "islam2026reliable" else issued
        f = {"author": and_join(authors), "title": d["title"][0], "journal": d["container-title"][0], "volume": d.get("volume"), "number": d.get("issue"),
             "pages": (d.get("page") or d.get("article-number") or "").replace("-", "--"), "year": year, "doi": spec["doi"], "note": spec["note"]}
        if key == "islam2026reliable":
            f["note"] = f"Volume {d.get('volume')} is dated {d['issued']['date-parts'][0][0]}-{d['issued']['date-parts'][0][1]:02d}; the record was created {d['created']['date-time'][:10]}. " + spec["note"]
        entries[key] = render(key, "article", f)
        log[key] = {"source": f"Crossref {spec['doi']}"}

    # --- artefacts, documentation, documents, data ---------------------------------------------------------------
    gen_date = gen_tag_commit["commit"]["author"]["date"][:10]
    entries["genhatharan2026nominal"] = render("genhatharan2026nominal", "misc", {
        "author": "Nisaharan Genhatharan", "title": "When Nominal False-Positive Rates Fail: Key- and Length-Dependent Null Behavior of Canonical LLM Text Watermarks",
        "year": "2026", "month": "09", "howpublished": "A paper released in a public GitHub repository (MIT licence)",
        "url": "https://github.com/nisaharan/when-nominal-false-positive-rates-fail/blob/v1/paper/when-nominal-false-positive-rates-fail.pdf", "note": f"Repository {gen_repo['html_url']}, created {gen_repo['created_at'][:10]}, release tag v1 at commit {gen_v1['commit']['sha'][:7]} of {gen_date}; the PDF read on 2026-10-09 was `paper/when-nominal-false-positive-rates-fail.pdf` of the repository (19 pages; its SHA-256 in the project's literature manifest); not on arXiv on the build date; cited by repository, release and date (constraint 15). The text's page references follow that PDF."})
    log["genhatharan2026nominal"] = {"source": "GitHub API: repository, tags, the v1 commit"}
    entries["xlr8harder2026synthid"] = render("xlr8harder2026synthid", "misc", {
        "author": "{xlr8harder}", "title": "Reproducible SynthID-Text implementation for vLLM, datasets, detectors, and evaluation results (GitHub repository)",
        "year": "2026", "month": "08", "howpublished": "GitHub repository (MIT licence)", "url": syn_commit["html_url"],
        "note": f"Commit {syn_commit['sha'][:7]} of {syn_commit['commit']['author']['date'][:10]} (repository created {syn_repo['created_at'][:10]}); the detector amendment `docs/DETECTOR_SCORE_FAMILY_AMENDMENT.md` read through the GitHub API at that commit on 2026-10-19; cited as prior practice by repository, commit and date (constraints 15, 32)."})
    log["xlr8harder2026synthid"] = {"source": "GitHub API: repository and commit b3adb0f"}
    entries["yukhimchuk2026keylottery"] = render("yukhimchuk2026keylottery", "misc", {
        "author": "Alexander Yukhimchuk", "title": "Key lottery: per-key false positives of LLM text watermarks (GitHub repository; with the proposal ``Audit the Deployed Key, Not the Scheme: Per-Key False-Positive Control for LLM Text Watermarks'')",
        "year": "2026", "month": "10", "howpublished": "GitHub repository (no licence file); a course project of MBZUAI's ML8502 Machine Learning Security (Fall 2026), by its README", "url": kl_commit["html_url"],
        "note": f"Commit {kl_commit['sha'][:7]} of {kl_commit['commit']['author']['date'][:10]} (repository created {kl_repo['created_at'][:10]}); its PREREGISTRATION.md self-dates the claims to 3--5 October 2026 and says the git history does not timestamp them; read through the GitHub API at that commit on 2026-10-21 (README.md, PREREGISTRATION.md, proposal/proposal.tex, report/claims.json, report/screening.json, results/window_sweep_prf.json; no PDF); independent concurrent work, cited by repository, commit and date (constraints 15, 34, 36)."})
    log["yukhimchuk2026keylottery"] = {"source": "GitHub API: repository, commit 8ebb6b4 and the user record (the author's name)"}
    entries["bonet2026llmwatermark"] = render("bonet2026llmwatermark", "misc", {
        "author": "{HugoAlbertBonet}", "title": "llmwatermark: a KGW-style text watermarking library with transformers, vLLM, llama.cpp and SGLang adapters (GitHub repository)",
        "year": "2026", "month": "08", "howpublished": "GitHub repository (MIT licence)", "url": f"https://github.com/HugoAlbertBonet/llmwatermark/blob/{lw_readme['sha']}/README.md",
        "note": f"The README at commit {lw_readme['sha'][:7]} of {lw_readme['commit']['author']['date'][:10]} (repository created {lw_repo['created_at'][:10]}), the first that carries the fixed-key caveat and the measured per-key offset; the measurement itself is commit {lw_commit['sha'][:7]} of the same day, whose message states that it was measured over 24 keys; both read through the GitHub API on 2026-10-21; cited as a practice record by repository, commit and date (constraints 15, 35)."})
    log["bonet2026llmwatermark"] = {"source": "GitHub API: repository, the measurement commit 6261c02 and the README commit e2d47ae (R13 F6)"}
    entries["openai2026textgrain"] = render("openai2026textgrain", "techreport", {
        "author": "Xiang Li and Garrett Wen and Xiaohong Chen and Qi Long and Arzav Jain and Florent Joly and Mike Lam and Qingquan Song and Weijie Su",
        "title": "textGrain: Entropy-Calibrated Watermarking for Language Model Text", "institution": "OpenAI", "type": "Technical report accompanying OpenAI's October 5th blog post",
        "year": "2026", "month": "10", "url": "https://cdn.openai.com/pdf/e9508624-d767-41b6-a26d-e34ca798ada6/textgrain-entropy-calibrated-watermarking-for-language-model-text.pdf",
        "note": "Dated October 5, 2026; the author list and order from the report's cover; read 2026-10-09 (R01) and re-read 2026-10-18; the text's page reference (\\S3.2, p. 6) follows the PDF."})
    log["openai2026textgrain"] = {"source": "the report's cover (local text); the URL from the industry screen of 2026-10-18"}
    entries["vllm2026watermarking"] = render("vllm2026watermarking", "misc", {
        "author": "{vLLM project}", "title": "Text watermarking (vLLM documentation)", "year": "2026", "month": "10",
        "howpublished": "\\url{https://docs.vllm.ai/en/latest/features/watermarking/}",
        "note": "Page dated October 15, 2026 (its footer); read 2026-10-18 at the claim gate's industry screen and cited by the date read, not by a version (constraint 33)."})
    log["vllm2026watermarking"] = {"source": "the documentation page; the screen's record of 2026-10-18"}
    entries["ec2026code"] = render("ec2026code", "misc", {
        "author": "{European Commission}", "title": "Code of Practice on Transparency of AI-Generated Content (final version)", "year": "2026", "month": "06",
        "howpublished": "\\url{https://ec.europa.eu/newsroom/dae/redirection/document/129555}",
        "note": "Commission newsroom document 129555; the final Code published on 10 June 2026 by the Commission's news page; drafted by two independent Working Groups (chairs Kalina Bontcheva and Anja Bechmann; vice-chairs Dino Pedreschi, Giovanni De Gregorio, Christian Riess and Madalina Botan, as the cover lists them); read 2026-10-18; the text's page reference (Measure 3.2, p. 17) follows the PDF. Cited for vocabulary only (constraint 33)."})
    log["ec2026code"] = {"source": "the document's cover (local text); the Commission's newsroom id"}
    entries["ec2026guidelines"] = render("ec2026guidelines", "misc", {
        "author": "{European Commission}", "title": "Guidelines on the implementation of the transparency obligations for certain AI systems under Article 50 of Regulation (EU) 2024/1689 (the AI Act): Annex to the Communication to the Commission, C(2026) 5054 final", "year": "2026", "month": "07",
        "howpublished": "\\url{https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-07/guidelines_on_the_implementation_of_the_transparency_obligations_for_certain_ai_systems_under_article_50_of_the_ai_act_bzptwqhk0ikg1dtlddap41psfy_131215.pdf}",
        "note": "Brussels, 20.7.2026; Commission newsroom document 131215; read 2026-10-18; the text's page reference (p. 26) follows the PDF. Cited for vocabulary only (constraint 33)."})
    log["ec2026guidelines"] = {"source": "the document's cover (local text); the service-desk URL from the industry screen"}
    nist_cr = cr["nist2024ai1004"]
    assert "synthetic content" in nist_cr["title"][0].lower() and nist_cr["issued"]["date-parts"][0][0] == 2024, nist_cr.get("title")
    entries["nist2024ai1004"] = render("nist2024ai1004", "techreport", {
        "author": "{National Institute of Standards and Technology}", "title": "Reducing Risks Posed by Synthetic Content: An Overview of Technical Approaches to Digital Content Transparency",
        "institution": "National Institute of Standards and Technology", "number": "NIST AI 100-4", "year": "2024", "month": "11", "doi": "10.6028/NIST.AI.100-4",
        "url": "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-4.pdf", "note": "The text's page reference (p. 12) follows the PDF; read 2026-10-08 and re-read 2026-10-18. Cited for vocabulary only (constraint 33)."})
    log["nist2024ai1004"] = {"source": "Crossref 10.6028/NIST.AI.100-4 (saved under bib_sources/crossref/); the title, institution and date confirmed against the report's cover (local text)"}
    wm = json.loads((ROOT / "outputs" / "corpora_manifest_v0.1.json").read_text())["entries"]
    wiki = next(v for v in wm.values() if v["repo_id"] == "wikimedia/wikipedia")
    entries["wikimedia2023dump"] = render("wikimedia2023dump", "misc", {
        "author": "{Wikimedia Foundation}", "title": "Wikipedia dumps of 1 November 2023 (Hugging Face dataset wikimedia/wikipedia, configurations 20231101.<lang>)", "year": "2023", "month": "11",
        "howpublished": "\\url{https://huggingface.co/datasets/wikimedia/wikipedia}",
        "note": f"Hub revision {wiki['revision']}; the six language configurations frozen on {wiki['retrieved_utc'][:10]} under the project's hashed manifest (each file's SHA-256 equal to the Hub's LFS digest); the project licence (CC BY-SA 3.0/4.0 and GFDL, inherited by the articles)."})
    log["wikimedia2023dump"] = {"source": "the freeze manifest outputs/corpora_manifest_v0.1.json (Hub revision and retrieval date)"}
    entries["aaronson2022lecture"] = render("aaronson2022lecture", "misc", {
        "author": "Scott Aaronson", "title": "My AI Safety Lecture for UT Effective Altruism", "year": "2022", "month": "11",
        "howpublished": "Shtetl-Optimized (blog), \\url{https://scottaaronson.blog/?p=6823}",
        "note": f"Posted {lec_date}; the lecture describes the pseudorandom (Gumbel-max, exponential minimum sampling) watermark for GPT outputs, whose detector the text cites through Kuditipudi et al. (2024) and Fernandez et al. (2023); read {read_utc['aaronson_lecture.html']}."})
    log["aaronson2022lecture"] = {"source": "the blog page (title and published_time meta tag)"}

    # --- write ------------------------------------------------------------------------------------------------------
    order = sorted(entries)
    header = (f"% references.bib for 'Key-conditional false-positive rates of LLM watermark detectors' (built {NOW} by research/paper/build_references.py "
              f"from the primary records saved under research/paper/bib_sources/; see bib_sources/fetch_log.json). Every arXiv entry names the version read; "
              f"every published paper carries its DOI or proceedings page; repository artefacts are cited by repository, tag or commit and date; "
              f"documentation and regulator documents by document identifier and the date read.\n\n")
    (HERE / "references.bib").write_text(header + "\n\n".join(entries[k] for k in order) + "\n", encoding="utf-8")
    projections = {"private_record": "research/paper/bib_sources/raw_responses/ (the full GitHub and Crossref responses; excluded from the public snapshot) "
                                     "and bib_sources/pages/*.html (git-ignored); the distributed records under github/ and crossref/ are projections (R13 F10)",
                   "removed": PROJECTED, "pages_read_utc": read_utc}
    (SRC / "fetch_log.json").write_text(json.dumps({"built_utc": NOW, "entries": log, "arxiv_versions": used_versions, "warnings": warnings, "resolved": resolved,
                                                    "projections": projections}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote references.bib with {len(entries)} entries; {len(warnings)} unresolved warning(s); {len(resolved)} resolved difference(s)")
    for w in warnings:
        print("  WARNING:", w)
    for w in resolved:
        print("  resolved:", w[:160])
    return 0


if __name__ == "__main__":
    sys.exit(main())
