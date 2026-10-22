#!/usr/bin/env python3
"""Build the public snapshot repository of this project (Stage 9; decision P1, 2026-10-21).

Copies every git-tracked file at HEAD except the session briefing (`RESEARCH_HANDOFF.md`), the model instructions for
the two sessions (`AGENTS.md`), the project's Claude skills (`.claude/`) and the registry pointers, generalises the local
paths of this machine (the working folder, the home folder, the skill file) to placeholders, scans for secret-like strings,
adds LICENSE (MIT, code), LICENSE-TEXT (CC BY 4.0, text and figures), README.md and CITATION.cff, copies the paper page
(`docs/`, built by `tools/make_site.py` in the working repository) and writes SNAPSHOT_MANIFEST.json (source commit, file
count, SHA-256 of every file). Git-ignored data, model weights, corpora, literature PDFs and the render are never in the
tree, so they cannot be copied.

Run: python3 tools/make_public_snapshot.py DEST [--git [--fresh]] [--check-only]
  --git initialises a repository in DEST with one commit, or adds a commit to an existing one (an update never rewrites
  history); --fresh starts a new history instead (the old one is bundled to DEST's parent folder first, then removed), for
  a publication history that must hold only approved content (R13 F9). After every --git run, and alone with --check-only,
  the history check walks every commit reachable from every ref of DEST and refuses any excluded path, raw capture,
  git-ignored material, third-party page or projected-away bibliography field, and requires every ref of the configured
  remote to point into that history; when a remote is configured and cannot be read, the check fails (R13 F14), and only a
  repository with no remote passes on its local refs alone. --selftest runs the check with an injected remote-read error
  and an injected timeout and requires each to be reported as a problem.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = Path(sys.argv[1]).resolve()
EXCLUDE = ("RESEARCH_HANDOFF.md", "AGENTS.md", ".claude/", "research/claim_gate/raw_A/", "research/claim_gate/raw_B/", "research/claim_gate/raw_C/",   # the raw captures of third-party pages stay private (R13 F4)
           "research/paper/bib_sources/raw_responses/")   # the full API responses behind the bibliography stay private; the distributed records are projections (R13 F10)
IGNORED_MATERIAL = ("/data/", "/raw/", "/pdfs/", "/txt/")   # git-ignored folders that must never appear
WEIGHT_EXT = (".safetensors", ".bin", ".pt", ".npy", ".parquet")
GENERALISE = [  # (literal, replacement): the working folder first, then its parent and the home folder, then the skill
    (str(ROOT), "<repository>"),
    (str(ROOT.parent), "<projects>"),
    (str(Path.home()) + "/.claude/skills/research-project-guide/SKILL.md", "<the research-project-guide skill, not included>"),
    ("<the research-project-guide skill, not included>", "<the research-project-guide skill, not included>"),
    ("<the research-project-guide skill, not included>", "<the research-project-guide skill, not included>"),
    ("<repository>", "<repository>"),
    ("<projects>", "<projects>"),
    (str(Path.home()), "<home>"),
]
SECRET = re.compile(r"hf_[A-Za-z0-9]{25,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH) PRIVATE KEY")
PUBLIC_URL = "https://github.com/SHENSHENZYC/watermark-key-validity"
SITE_URL = "https://shenshenzyc.github.io/watermark-key-validity/"
TITLE = "Key-conditional false-positive rates of LLM watermark detectors: dispersion identities, a systematic measurement on open corpora, per-key calibration and its power cost"

README = f"""# {TITLE}

Public snapshot of the research repository behind the paper (Yichen Zhao, independent researcher, 2026). It holds the
four pre-registered protocols with their lock files, the validation records, run manifests and the locked analysers'
results, the per-text records of every study, every script that generated a number, table or figure in the paper, the
paper's sources, the review prompts, memos and resolutions of the thirteen independent-review checkpoints, the source and
claim gates, and the decision log that records each decision in order. It holds **no corpus text, no model weights, no
literature PDFs and none of the third-party pages, READMEs or extracted texts the literature screens captured**: the first
three were git-ignored throughout and the captures stay in the private record (the screens' memos list every query and
quotation); the bibliography's records under `research/paper/bib_sources/` are the arXiv API's metadata (CC0) and
projections of the Crossref and GitHub API responses to their provenance fields (no diff body of a cited commit, no
publisher's abstract; the full responses stay in the private record), and the hashed manifests let a rebuild be checked.

**Paper page:** {SITE_URL} (the PDF, an HTML version and this repository; served from `docs/`).

## What is where
| Path | Contents |
|---|---|
| `research/STUDY<n>_PROTOCOL_v*.md` | The four pre-registered protocols (locked by hash before any outcome; `LOCKED` in their status line) |
| `outputs/study<n>_v*/` | `PRE_RUN_LOCK.json` (the hashes of the protocol, the pinned code and the inputs, the commit, the "no outcomes" statement), `VALIDATION.json`, `INPUTS.json`, `RUN_MANIFEST.json`, `results.json` (Study 3's as `results.json.gz`), the record `cells/`, the run logs, `report/` (the generated tables, figures and checks) |
| `research/study<n>/` | The locked code (runner, analyser, validator, core; the runners refuse to start without the lock), the grid, the report builder and its prose source, the fixture generator, the pre-lock re-screen |
| `research/STUDY<n>_REPORT_v0.1.md` | The generated reports (never edited by hand) |
| `research/corpora/`, `outputs/corpora_*`, `DATA_LAYOUT.md`, `tools/` | The terms-of-use check, the data audit (v0.3 current), the freeze and build scripts, the hashed manifests (counts, digests, the holdout identifiers; no text), the sealed access layer |
| `research/paper/` | The paper: `sections/` (one file per section, every number a placeholder), `tables/` and `figures/` (one script each, reading the locked outputs and asserting against the reports), `fill_paper.py`, `literals.py`, `assemble.py`, `make_latex.py`, `latex/` (the LaTeX source and the PDF), `references.bib` with `bib_sources/`, `PAPER_DRAFT_v0.1.md` |
| `research/reviews/` | The orientation for the reviewer and, per checkpoint R01–R13, the prompt, the reviewer's memos, the conductor's responses and the resolution |
| `research/KEYCOND_GATE_v*.md`, `research/CLAIM_GATE_v0.1.md`, `research/FINAL_GATE_v0.1.md`, `research/TOPIC_SCREEN_v0.1.md`, `research/PROJECT_BRIEF.md` | The source gates, the claim gate, the final gate, the topic screen and the brief |
| `research/DECISION_LOG.md` | Every decision, result and correction, dated, in order |
| `docs/` | The paper page (built by `tools/make_site.py`: `index.html`, `paper.pdf`, `paper.html` with `figures/`) |

## Rebuilding
1. Python 3.12 (`requirements-lock.txt`) with PyTorch (MPS or CUDA) and `transformers`; the pinned model revisions are in the token and model manifests under `outputs/` (Llama 3.2 is gated on Hugging Face; accept its licence there).
2. The corpora: `tools/freeze_corpora.py` downloads the pinned Hub files named in `outputs/corpora_manifest_v0.1.json` and checks their SHA-256 against the manifest; `tools/corpora_build.py` rebuilds the units; the holdout stays sealed (`tools/corpora_access.py`; no lock in the paper is final).
3. A study: its runner under `research/study<n>/` verifies every hash in its `PRE_RUN_LOCK.json` first. Run times on one Apple M5 laptop are in the run manifests (1 to 12 hours).
4. The paper: the scripts under `research/paper/tables/` and `research/paper/figures/`, then `fill_paper.py --check`, `assemble.py --render` (pandoc and headless Chrome) and `make_latex.py` (pandoc and Tectonic).

## Licences
Code (every `.py` file and the scripts) is under the MIT licence (`LICENSE`). The text of the protocols, reports, gates, the
decision log and the paper, and the figures, are under CC BY 4.0 (`LICENSE-TEXT`). Third-party materials are not
included: the models are used under their own licences (Qwen2.5 Apache-2.0; Llama 3.2 Community Licence, tokenizer only),
the null corpora are the Common Pile v0.1 subsets (per-document licence strings recorded per unit) and the Wikimedia dumps
of 2023-11-01 (CC BY-SA 3.0 / GFDL), neither redistributed here, and the papers read are listed with their licences in
`research/FINAL_GATE_v0.1.md` (§7), whose rights table also covers the bibliography's primary records under
`research/paper/bib_sources/` (arXiv API metadata under CC0; the Crossref and GitHub API records projected to their
provenance fields, without the diff bodies of the cited commits and the publishers' abstracts).

## Use of AI tools
The prose and the code were drafted by Claude (Anthropic) in Claude Code under the author's instruction and section-level
review, and every major checkpoint was reviewed by an independent second model, Codex (OpenAI), before the project proceeded
(the memos are under `research/reviews/`); the author took every design, lock, wording and publication decision, read every
word, and takes full responsibility. No AI system is an author.

## Citing
See `CITATION.cff`. The paper is published at {SITE_URL} (a self-published preprint); cite it by that URL and this repository.

## About this snapshot
Built by `tools/make_public_snapshot.py` from the working repository at the commit named in `SNAPSHOT_MANIFEST.json`
(every file's SHA-256 is listed there). The session briefing, the model instructions and the project's Claude skills are
not included, nor are the claim gate's raw captures of third-party pages (`research/claim_gate/raw_*`) or the full API
responses behind the bibliography (`research/paper/bib_sources/raw_responses/`, of which the distributed records are
projections, each with a `_projection` note); the local paths of
the working machine were generalised to `<repository>`, `<projects>` and `<home>` in every file except the records whose
SHA-256 a lock or run manifest pins, which are byte-identical to the working repository's and so carry the working
folder's path verbatim (both lists are in `SNAPSHOT_MANIFEST.json`); nothing else was edited.
"""

MIT = """MIT License

Copyright (c) 2026 Yichen Zhao

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

CCBY = """The text of this repository (the protocols, reports, gates, the decision log, the review memos and the paper's sources)
and its figures are licensed under the Creative Commons Attribution 4.0 International licence (CC BY 4.0):
https://creativecommons.org/licenses/by/4.0/

Copyright (c) 2026 Yichen Zhao. Attribution: cite the paper (CITATION.cff) and link to this repository.
The code is under the MIT licence (LICENSE). Third-party materials are not included (the bibliography's records are API
metadata projected to their provenance fields); see README.md.
"""

CFF = f"""cff-version: 1.2.0
message: "If you use this repository, please cite the paper."
title: "{TITLE}"
authors:
  - family-names: Zhao
    given-names: Yichen
    affiliation: Independent researcher
    email: alexyczhao@gmail.com
year: 2026
type: software
repository-code: "{PUBLIC_URL}"
license: MIT
preferred-citation:
  type: generic
  title: "{TITLE}"
  authors:
    - family-names: Zhao
      given-names: Yichen
  year: 2026
  url: "{SITE_URL}"
  notes: "Self-published preprint; the GitHub Pages site is the publication of record."
"""


def check_history(dest: Path, ls_remote=None, raise_on_problem: bool = True) -> dict:
    """Walk every commit reachable from every ref of the snapshot repository (R13 F9): no commit may hold an excluded path,
    a raw capture, git-ignored material or a third-party page, and no bibliography record may carry a field the projection
    removes (R13 F10); every ref of the configured remote must point into that history, and a configured remote that
    cannot be read is a problem, never a pass (R13 F14); a repository with no remote is checked on its local refs alone and
    says so. Prints and returns the record; raises on any problem unless ``raise_on_problem`` is false (the self-test).
    ``ls_remote`` is the function that lists the remote's refs (injected by the self-test with failures)."""
    def git(*a: str) -> str:
        return subprocess.run(["git", "-C", str(dest), *a], capture_output=True, text=True, check=True).stdout
    if ls_remote is None:
        def ls_remote() -> str:
            return subprocess.run(["git", "-C", str(dest), "ls-remote", "origin"], capture_output=True, text=True, check=True, timeout=90).stdout
    commits = git("rev-list", "--all").split()
    roots = git("rev-list", "--max-parents=0", "--all").split()
    refs = {ref: sha for sha, ref in (l.split(" ", 1) for l in git("for-each-ref", "--format=%(objectname) %(refname)").splitlines())}
    problems: list[str] = []
    for c in commits:
        for f in git("ls-tree", "-r", "--name-only", c).splitlines():
            page = f.endswith((".html", ".htm", ".xml")) and not f.startswith("docs/") and f != "research/paper/bib_sources/arxiv_entries.xml"
            if f.startswith(EXCLUDE) or any(s in f for s in IGNORED_MATERIAL) or f.endswith(WEIGHT_EXT) or page:
                problems.append(f"{c[:7]}: {f}")
            elif f.startswith(("research/paper/bib_sources/github/", "research/paper/bib_sources/crossref/")):
                blob = git("show", f"{c}:{f}")
                if '"patch":' in blob or '"abstract":' in blob:
                    problems.append(f"{c[:7]}: {f} carries a field the projection removes")
    remote: dict[str, str] = {}
    configured = subprocess.run(["git", "-C", str(dest), "remote", "get-url", "origin"], capture_output=True, text=True).returncode == 0
    if not configured:
        remote = {"(no remote configured)": "the local refs alone were checked; configure and push the remote, then run --check-only again"}
    else:
        try:
            lines = ls_remote().splitlines()
            if not lines:
                problems.append("the configured remote origin lists no ref")
            listed = dict(l.split("\t")[::-1] for l in lines)   # ref -> object id; an annotated tag lists its tag object and, as ref^{}, the commit it points to
            for ref, sha in listed.items():
                if ref.endswith("^{}"):
                    continue
                commit = listed.get(ref + "^{}", sha)   # the peeled commit of an annotated tag, else the object itself
                remote[ref] = commit if commit == sha else f"{commit} (tag object {sha[:7]})"
                if commit not in commits:
                    problems.append(f"remote {ref} at {commit[:7]} is outside the local history")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            remote = {"(not read)": str(e)[:120]}
            problems.append(f"the configured remote origin could not be read ({type(e).__name__}): the remote's refs are unverified")
    man = dest / "SNAPSHOT_MANIFEST.json"
    if man.exists():   # the HEAD tree must hold every manifest entry (a dropped folder is invisible to on-disk digest checks)
        expected = set(json.loads(man.read_text(encoding="utf-8"))["sha256"]) | {"SNAPSHOT_MANIFEST.json"}
        head_tree = set(git("ls-tree", "-r", "--name-only", "HEAD").splitlines())
        if head_tree != expected:
            problems.append(f"the HEAD tree differs from the manifest: missing {sorted(expected - head_tree)[:5]}, extra {sorted(head_tree - expected)[:5]}")
    rec = {"commits": len(commits), "roots": roots, "refs": refs, "remote_configured": configured, "remote_refs": remote, "problems": problems}
    print("history check:", json.dumps(rec))
    if raise_on_problem:
        assert not problems, f"the snapshot history holds excluded material, an unknown remote ref or an unread remote: {problems[:5]}"
    return rec


def selftest_history_check(dest: Path) -> None:
    """R13 F14: a remote-read error and a timeout must each be reported as a problem (the remote must be configured)."""
    def failing() -> str:
        raise subprocess.CalledProcessError(128, ["git", "ls-remote", "origin"], stderr="fatal: could not read from remote repository")
    def timing_out() -> str:
        raise subprocess.TimeoutExpired(["git", "ls-remote", "origin"], 90)
    assert subprocess.run(["git", "-C", str(dest), "remote", "get-url", "origin"], capture_output=True).returncode == 0, "the self-test needs a configured remote"
    for name, fn in (("CalledProcessError", failing), ("TimeoutExpired", timing_out)):
        rec = check_history(dest, ls_remote=fn, raise_on_problem=False)
        assert any("could not be read" in p and name in p for p in rec["problems"]), (name, rec["problems"])
    rec = check_history(dest, raise_on_problem=False)   # the real remote: every ref inside the local history
    assert not rec["problems"] and rec["remote_refs"], rec
    print("selftest ok: an unread remote is a problem (error and timeout); the real remote's refs verified")


def main() -> int:
    use_git = "--git" in sys.argv; fresh = "--fresh" in sys.argv
    if "--selftest" in sys.argv:
        selftest_history_check(DEST); return 0
    if "--check-only" in sys.argv:
        check_history(DEST); return 0
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    files = [f for f in subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\0") if f]
    keep_git = use_git and (DEST / ".git").is_dir() and not fresh
    if fresh and (DEST / ".git").is_dir():   # a new history (R13 F9): bundle every ref of the old one beside DEST, then let the rebuild remove it
        old = subprocess.run(["git", "-C", str(DEST), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        bundle = DEST.parent / f"{DEST.name}.history-until-{old}.bundle"
        subprocess.run(["git", "-C", str(DEST), "bundle", "create", str(bundle), "--all"], check=True, capture_output=True)
        print(f"superseded history bundled to {bundle} (SHA-256 {hashlib.sha256(bundle.read_bytes()).hexdigest()}, {bundle.stat().st_size / 1e6:.1f} MB)")
    if DEST.exists():
        for child in DEST.iterdir():   # update mode keeps the snapshot repository's history; everything else is rebuilt
            if child.name == ".git" and keep_git:
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    DEST.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, str] = {}; generalised: list[str] = []; excluded: list[str] = []; pinned_verbatim: list[str] = []
    # the digests a lock or manifest pins: a record whose own SHA-256 is among them stays byte-identical (R13 F7)
    pinned_digests: set[str] = set()
    for f in files:
        if f.startswith("outputs/") and f.endswith(".json") and ("LOCK" in f or "MANIFEST" in f or "manifest" in f):
            pinned_digests |= set(re.findall(r"\b[0-9a-f]{64}\b", (ROOT / f).read_text(encoding="utf-8", errors="ignore")))
    for f in files:
        if f.startswith(EXCLUDE):
            excluded.append(f); continue
        src, dst = ROOT / f, DEST / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = None
        if text is not None:
            new = text
            if hashlib.sha256(data).hexdigest() in pinned_digests:   # a lock or manifest pins this file: byte-identical
                if any(lit in text for lit, _ in GENERALISE):
                    pinned_verbatim.append(f)
            else:
                for lit, rep in GENERALISE:
                    new = new.replace(lit, rep)
            if new != text:
                generalised.append(f); data = new.encode("utf-8")
            m = SECRET.search(new)
            assert not m, f"secret-like string in {f}: {m.group(0)[:12]}…"
        dst.write_bytes(data)
        manifest[f] = hashlib.sha256(data).hexdigest()
    for name, content in [("LICENSE", MIT), ("LICENSE-TEXT", CCBY), ("README.md", README), ("CITATION.cff", CFF)]:
        (DEST / name).write_text(content, encoding="utf-8"); manifest[name] = hashlib.sha256(content.encode("utf-8")).hexdigest()
    # the working repository's ignore rules, minus the rule that ignores the paper page there: in the snapshot `docs/` is
    # the GitHub Pages site and must be tracked (the first release build dropped it silently: the site was on disk and in
    # the manifest but not in the commit, and Pages found no /docs)
    gi_lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert any(l.strip().rstrip("/") == "docs" for l in gi_lines), "the working repository's .gitignore no longer ignores docs/: review this filter"
    gi = "\n".join(l for l in gi_lines if l.strip().rstrip("/") != "docs") + "\n# docs/ (the paper page) is tracked in this snapshot: GitHub Pages serves it from main /docs\n"
    (DEST / ".gitignore").write_text(gi, encoding="utf-8"); manifest[".gitignore"] = hashlib.sha256(gi.encode("utf-8")).hexdigest()
    docs = ROOT / "docs"
    if docs.is_dir():   # the paper page built by tools/make_site.py (git-ignored in the working repository)
        for p in sorted(docs.rglob("*")):
            if p.is_file():
                rel = p.relative_to(ROOT); (DEST / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(p, DEST / rel); manifest[str(rel)] = hashlib.sha256(p.read_bytes()).hexdigest()
    assert not any(any(s in f for s in IGNORED_MATERIAL) or f.endswith(WEIGHT_EXT) for f in manifest), "ignored material in snapshot"
    for f in manifest:   # the distributed bibliography records are projections (R13 F10)
        if f.startswith(("research/paper/bib_sources/github/", "research/paper/bib_sources/crossref/")):
            blob = (DEST / f).read_text(encoding="utf-8")
            assert '"patch":' not in blob and '"abstract":' not in blob, f"{f} carries a field the projection removes"
    leftover = sorted(f for f in manifest if f not in pinned_verbatim and str(Path.home()).encode() in (DEST / f).read_bytes())
    assert not leftover, f"a local path survived in {leftover[:5]}"
    out = {"source_commit": head, "source_dirty": bool(dirty), "built_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "files": len(manifest), "excluded": excluded, "generalised_local_path_in": generalised,
           "history": "a fresh root (the superseded history bundled beside the snapshot)" if fresh else "an added commit" if keep_git else "a new repository" if use_git else "no repository",
           "pinned_records_kept_verbatim_with_the_working_folder_path": sorted(pinned_verbatim), "sha256": manifest}
    (DEST / "SNAPSHOT_MANIFEST.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    size_mb = sum((DEST / f).stat().st_size for f in manifest) / 1e6
    print(f"snapshot at {DEST}: {len(manifest)} files, {size_mb:.1f} MB, from {head[:7]}{' (DIRTY TREE)' if dirty else ''}; excluded {len(excluded)}; generalised paths in {len(generalised)} files")
    if use_git:
        if not keep_git:
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=DEST, check=True)
        subprocess.run(["git", "add", "-A", "-f"], cwd=DEST, check=True)   # -f: every copied file is meant to be tracked, whatever the ignore rules say
        r = subprocess.run(["git", "commit", "-q", "-m", f"Public snapshot of the research repository at {head[:7]} ({out['built_utc']})"], cwd=DEST, capture_output=True, text=True)
        print("committed" if r.returncode == 0 else f"nothing to commit ({r.stdout.strip()[:80]})")
        tracked = set(subprocess.run(["git", "ls-files", "-z"], cwd=DEST, capture_output=True, text=True, check=True).stdout.split("\0")) - {""}
        expected = set(manifest) | {"SNAPSHOT_MANIFEST.json"}
        assert tracked == expected, f"the committed tree differs from the manifest: missing {sorted(expected - tracked)[:5]}, extra {sorted(tracked - expected)[:5]}"
        print(f"the committed tree equals the manifest: {len(tracked)} files (docs/ among them: {any(f.startswith('docs/') for f in tracked)})")
        check_history(DEST)
        print(f"push with: git -C {DEST} remote add origin {PUBLIC_URL}.git && git -C {DEST} push -u origin main")
    return 0


if __name__ == "__main__":
    sys.exit(main())
