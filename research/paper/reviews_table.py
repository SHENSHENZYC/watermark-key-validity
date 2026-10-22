#!/usr/bin/env python3
"""The independent-review record for the paper (the AI-use statement and Appendix E), generated, never typed.

Scans ``research/reviews/R<NN>_<slug>/``: the rounds are the ``REVIEW_<reviewer>_r<k>.md`` memos, each with its
``VERDICT:`` line; the findings of a checkpoint are the numbered findings its memos define (``### F<n>``, ``**F<n>**``,
``- F<n>`` or ``| F<n> |`` at the start of a line; a memo's references to another checkpoint's findings are not
definitions and do not count); a checkpoint is agreed when ``RESOLUTION.md`` exists and the last round's verdict is
AGREE; the agreed baseline is the commit in the AGREE row of the resolution's rounds table. Writes
``research/paper/tables/tableE_reviews.md`` and registers the counts in ``paper_values.json`` under the prefix ``r``
(``[[paper:r_...]]``), with the check counts of the paper's own table and figure scripts from ``checks.json``.

Usage:  .venv/bin/python research/paper/reviews_table.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paperlib as P  # noqa: E402

REVIEWS = P.ROOT / "research" / "reviews"
DEFS = [re.compile(r"^#{1,5}\s*\**F(\d+)\b"), re.compile(r"^\**F(\d+)\**\s*[—–\-:.(]"),
        re.compile(r"^[-*]\s*\**F(\d+)\**\s*[—–\-:.(]"), re.compile(r"^\|\s*\**F(\d+)\**\s*\|")]
NAMES = {"topic-lock-and-data-plan": "the topic lock, brief, screen and source gate; the data plan",
         "data-verdict": "the data verdict (terms, census, freeze, audit, holdout)",
         "study1-protocol": "the Study 1 protocol before its lock", "study1-report": "the Study 1 report",
         "study2-protocol": "the Study 2 protocol before its lock", "study2-report": "the Study 2 report",
         "study3-protocol": "the Study 3 protocol before its lock", "study3-report": "the Study 3 report",
         "study4-protocol": "the Study 4 protocol before its lock", "study4-report": "the Study 4 report",
         "claim-gate": "the claim gate (what the paper may claim)", "assembled-draft": "the assembled draft of this paper",
         "pre-publication": "the final paper before publication"}


def scan() -> list[dict]:
    rows = []
    for d in sorted(REVIEWS.glob("R[0-9][0-9]_*/")):
        m = re.match(r"R(\d\d)_(.+)", d.name)
        num, slug = int(m.group(1)), m.group(2)
        memos = sorted(d.glob("REVIEW_*_r*.md"), key=lambda f: int(re.search(r"_r(\d+)\.md$", f.name).group(1)))
        verdicts, findings, reviewer = [], set(), None
        for f in memos:
            reviewer = re.match(r"REVIEW_([A-Za-z0-9]+)_r", f.name).group(1)
            text = f.read_text(encoding="utf-8")
            v = re.findall(r"^\**VERDICT:\s*(AGREE|REVISE)", text, re.M)
            verdicts.append(v[-1] if v else "?")
            for line in text.splitlines():
                s = line.strip()
                for p in DEFS:
                    mm = p.match(s)
                    if mm:
                        findings.add(int(mm.group(1)))
        res = d / "RESOLUTION.md"
        agreed = res.exists() and bool(verdicts) and verdicts[-1] == "AGREE"
        baseline, date = "", ""
        if res.exists():
            for line in res.read_text(encoding="utf-8").splitlines():
                if re.match(r"^\|\s*\d+\s*\|", line) and "AGREE" in line:
                    c = re.search(r"`([0-9a-f]{7,40})`", line); baseline = c.group(1)[:7] if c else ""
                    dt = re.search(r"(20\d\d-\d\d-\d\d)", line); date = dt.group(1) if dt else ""
            rt = res.read_text(encoding="utf-8")
            if not baseline:  # the older resolutions name the agreed baseline in their header line
                c = re.search(r"baseline `([0-9a-f]{7,40})`", rt); baseline = c.group(1)[:7] if c else ""
            if not date:
                dt = re.search(r"(20\d\d-\d\d-\d\d)", rt); date = dt.group(1) if dt else ""
        rows.append({"num": num, "id": f"R{num:02d}", "slug": slug, "name": NAMES.get(slug, slug.replace("-", " ")),
                     "reviewer": reviewer or "", "rounds": len(memos), "findings": len(findings),
                     "verdicts": verdicts, "agreed": agreed, "baseline": baseline, "date": date,
                     "open": (d / "PROMPT.md").exists() and not agreed})
    return rows


def main() -> int:
    rows = scan()
    agreed = [r for r in rows if r["agreed"]]
    open_ = [r for r in rows if r["open"]]
    assert agreed, "no agreed checkpoint found"
    assert all(r["findings"] > 0 and r["rounds"] > 0 for r in agreed), rows
    n_rounds = sum(r["rounds"] for r in agreed); n_findings = sum(r["findings"] for r in agreed)
    reviewers = sorted({r["reviewer"] for r in agreed}); assert reviewers == ["codex"], reviewers
    first, last = agreed[0]["id"], agreed[-1]["id"]
    P.register_value("r_n_checkpoints_agreed", len(agreed))
    P.register_value("r_checkpoint_range", f"{first}–{last}")
    P.register_value("r_n_rounds", n_rounds)
    P.register_value("r_n_findings", n_findings)
    P.register_value("r_rounds_min", min(r["rounds"] for r in agreed)); P.register_value("r_rounds_max", max(r["rounds"] for r in agreed))
    P.register_value("r_n_first_round_agree", sum(1 for r in agreed if r["verdicts"][0] == "AGREE"))
    if open_:
        ids = ", ".join(f"{r['id']} ({r['name']})" for r in open_)
        P.register_value("r_open_sentence", f"Checkpoint {ids} is in progress at the time of this build and is added here when agreed.")
    else:
        P.register_value("r_open_sentence", "")
    checks = json.loads(P.CHECKS_FILE.read_text()) if P.CHECKS_FILE.exists() else {}
    # the placeholder and literal counts the reproducibility paragraph states (R12 F7): from the fill script and the literal scan
    import fill_paper, literals
    section_files = sorted((P.PAPER / "sections").glob("*.md"))
    n_ph = sum(len(fill_paper.PLACEHOLDER.findall(f.read_text(encoding="utf-8"))) for f in section_files)
    lit = literals.summary(literals.scan_files(section_files))
    P.register_value("r_n_placeholders", n_ph); P.register_value("r_n_section_files", len(section_files))
    P.register_value("r_n_literals", lit["n_literals"]); P.register_value("r_n_literals_grid", lit["n_settings_checked_against_grids"])
    P.register_value("r_n_literals_allowlisted", lit["n_allowlisted"]); P.register_value("r_n_literals_unallowed", lit["n_unallowed"])
    P.register_value("r_n_literals_algebraic", lit["n_algebraic"]); P.register_value("r_n_literals_prose", lit["n_prose"]); P.register_value("r_n_literals_math", lit["n_math"])
    P.register_value("r_n_literals_set_aside", lit["n_set_aside"])
    for cls, n in lit["set_aside_by_class"].items():
        P.register_value("r_n_set_aside_" + cls.replace(" or ", "_").replace(" ", "_"), n)
    P.register_value("r_n_table_checks", checks.get("tables", {}).get("n", 0))
    P.register_value("r_n_figure_checks", sum(v["n"] for k, v in checks.items() if k.startswith("fig")))
    P.register_value("r_n_table_checks_failed", checks.get("tables", {}).get("n_failed", 0))
    P.register_value("r_n_figure_checks_failed", sum(v["n_failed"] for k, v in checks.items() if k.startswith("fig")))
    P.flush_values("r")
    trs = [[r["id"], r["name"], str(r["rounds"]), str(r["findings"]), " / ".join(r["verdicts"]), f"`{r['baseline']}`" if r["baseline"] else "—", r["date"] or "—"] for r in rows]
    cap = (f"The independent second-model review (rule A7 of the project's guide): every major checkpoint was reviewed by Codex before the project "
           f"proceeded, and none proceeded without its AGREE with no open dispute. Rounds and findings are counted from the memos in "
           f"`research/reviews/`; a finding is a numbered item of a memo (F1, F2, …), each verified by the conductor against the primary evidence "
           f"before any change and answered in a response memo; the agreed baseline is the commit the reviewer read at the agreeing round. "
           f"{len(agreed)} checkpoints ({first}–{last}), {n_rounds} rounds, {n_findings} findings; {len(open_)} in progress.")
    out = P.PAPER / "tables" / "tableE_reviews.md"
    out.write_text(f"**Table E1.** {cap}\n\n" + P.md_table(["Checkpoint", "What was reviewed", "Rounds", "Findings", "Verdicts by round", "Agreed at", "Date"], trs), encoding="utf-8")
    print(f"wrote {out.relative_to(P.ROOT)}: {len(rows)} checkpoints ({len(agreed)} agreed, {len(open_)} open), {n_rounds} rounds, {n_findings} findings")
    for r in rows:
        print(f"  {r['id']} {r['slug']:<28} rounds {r['rounds']} findings {r['findings']:>2} {'/'.join(r['verdicts'])} {r['baseline']} {r['date']} {'OPEN' if r['open'] else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
