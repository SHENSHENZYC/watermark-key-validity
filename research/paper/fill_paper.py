#!/usr/bin/env python3
"""Fill the paper's section drafts from the builders' registers and the locked records (guide A4.1).

No number in a section draft is typed: every value is a placeholder ``[[namespace:name]]`` that this
script resolves from a committed, generated source, failing on any unresolved name. Namespaces:

  s1, s2, s3, s4   the report builders' registers (``outputs/<study>/report/prose_values.json``);
                   the value is the register's own formatted string;
  lock:<study>|<path>      the study's ``PRE_RUN_LOCK.json`` (study = study1 … study4);
  grid:<study>|<path>      the study's grid JSON pinned by the lock;
  manifest:<study>|<path>  the study's ``RUN_MANIFEST.json``;
  tokens:<study>|<path>    the study's token (or prompt) manifest;
  data:<path>              ``outputs/corpora_audit_v0.3.json`` (the data audit, Stage 4);
  side:<study>|<path>      the two-way SE side computation's JSON of that study (R09 F18; labelled);
  paper:<name>             ``research/paper/paper_values.json`` (values computed by the paper's own
                           committed scripts from the locked outputs and asserted against the reports).

A ``<path>`` is a ``|``-separated walk through the JSON (dict keys or list indices). An optional
``#<format>`` suffix applies a Python format spec (``#,`` thousands separators; ``#.1f``; ``#.1%``) or
spells an integer out (``#w`` → "four", ``#W`` → "Four", so that a count in words is generated too);
without it, integers are printed with thousands separators, floats with four significant digits,
strings as they are. Figure and table markers ``<<FIG:name>>`` and ``<<TABLE:name>>`` are left for
the assembly script. The filled sections go to ``research/paper/filled/``; ``--check`` resolves
everything and writes nothing. Both modes then run the literal scan of ``literals.py`` over the
sections' prose and formulas (R12 F7, F15, F22): every numeral and counting word the scan's patterns recognise
outside a placeholder must be a design constant checked against the grids, a labelled convention, an algebraic
0, 1 or 2 in a formula, or an allow-listed constant with a reason, the spans set aside are counted by class, and
the run fails otherwise (a syntactic check; the manual reading covers what the patterns do not see); the inventory is written to ``research/paper/filled/LITERALS.md``. The run lists the
register names used and writes the names registered but unused to
``research/paper/filled/UNUSED_REGISTER_NAMES.txt``.

Usage:  .venv/bin/python research/paper/fill_paper.py [--check] [--sections DIR] [files...]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SECTIONS_DIR = HERE / "sections"
FILLED_DIR = HERE / "filled"

STUDY_DIRS = {"study1": "outputs/study1_v0.3", "study2": "outputs/study2_v0.1",
              "study3": "outputs/study3_v0.1", "study4": "outputs/study4_v0.1"}
REGISTERS = {"s1": "outputs/study1_v0.3/report/prose_values.json",
             "s2": "outputs/study2_v0.1/report/prose_values.json",
             "s3": "outputs/study3_v0.1/report/prose_values.json",
             "s4": "outputs/study4_v0.1/report/prose_values.json"}
SIDE = {"study1": "outputs/study1_v0.3/report/twoway_se_check.json",
        "study2": "outputs/study2_v0.1/report/twoway_se_check.json",
        "study1_regen": "outputs/study1_v0.3/report/twoway_se_check_regen.json",
        "study1_synthetic": "outputs/study1_v0.3/report/twoway_se_check_synthetic.json"}
TOKENS = {"study2": "outputs/study2_v0.1/tokens_manifest.json",
          "study3": "outputs/study3_v0.1/tokens_manifest.json",
          "study4": "outputs/study4_v0.1/prompts_manifest.json",
          "study4_model": "outputs/study4_v0.1/model_manifest_qwen2.5-1.5b.json"}
DATA = "outputs/corpora_audit_v0.3.json"
PAPER_VALUES = HERE / "paper_values.json"

PLACEHOLDER = re.compile(r"\[\[([a-z0-9_]+):([^\]#]+?)(?:#([^\]]+))?\]\]")
NUMBER_WORDS = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
                11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
                19: "nineteen", 20: "twenty", 30: "thirty", 40: "forty", 50: "fifty", 60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety", 100: "a hundred"}


def words(value: object) -> str:
    """An integer spelled out (0–20, the tens, 100); anything else is an error, so a large count stays a numeral."""
    n = int(str(value).replace(",", ""))
    if n not in NUMBER_WORDS:
        raise ValueError(f"no word form for {n}")
    return NUMBER_WORDS[n]

_cache: dict[str, object] = {}


def load_json(rel: str) -> object:
    if rel not in _cache:
        p = ROOT / rel
        if not p.exists():
            raise FileNotFoundError(f"missing source {rel}")
        _cache[rel] = json.loads(p.read_text(encoding="utf-8"))
    return _cache[rel]


def walk(obj: object, path: str, where: str) -> object:
    cur = obj
    for part in path.split("|"):
        if isinstance(cur, dict):
            if part not in cur:
                raise KeyError(f"{where}: no key {part!r} (have {list(cur)[:12]}…)")
            cur = cur[part]
        elif isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError) as exc:
                raise KeyError(f"{where}: bad list index {part!r}") from exc
        else:
            raise KeyError(f"{where}: cannot walk into {type(cur).__name__} with {part!r}")
    return cur


def fmt(value: object, spec: str | None) -> str:
    if spec in ("w", "W"):
        w = words(value)
        return w[0].upper() + w[1:] if spec == "W" else w
    if spec:
        if spec.endswith("%") or spec.endswith("f") or spec.endswith("g") or spec.endswith("e"):
            return format(float(value), spec)
        return format(value, spec)
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:.4g}"
    if isinstance(value, (dict, list)):
        raise ValueError("a placeholder must resolve to a scalar, not a container")
    return str(value)


def resolve(ns: str, name: str, spec: str | None, used: dict[str, set[str]]) -> str:
    if ns in REGISTERS:
        reg = load_json(REGISTERS[ns])
        if name not in reg:
            raise KeyError(f"register {ns}: no name {name!r}")
        used.setdefault(ns, set()).add(name)
        return fmt(reg[name], spec) if spec else str(reg[name])
    if ns == "paper":
        if not PAPER_VALUES.exists():
            raise FileNotFoundError("paper_values.json does not exist yet")
        reg = json.loads(PAPER_VALUES.read_text(encoding="utf-8"))
        if name not in reg:
            raise KeyError(f"paper register: no name {name!r}")
        used.setdefault("paper", set()).add(name)
        return fmt(reg[name], spec)
    if ns == "data":
        return fmt(walk(load_json(DATA), name, "data"), spec)
    study, _, path = name.partition("|")
    if not path:
        raise KeyError(f"{ns}:{name}: a study and a path are needed")
    if ns == "lock":
        src = f"{STUDY_DIRS[study]}/PRE_RUN_LOCK.json"
    elif ns == "manifest":
        src = f"{STUDY_DIRS[study]}/RUN_MANIFEST.json"
    elif ns == "grid":
        src = load_json(f"{STUDY_DIRS[study]}/PRE_RUN_LOCK.json")["grid"]
    elif ns == "tokens":
        src = TOKENS[study]
    elif ns == "side":
        src = SIDE[study]
    else:
        raise KeyError(f"unknown namespace {ns!r}")
    return fmt(walk(load_json(src), path, f"{ns}:{study}"), spec)


def fill_text(text: str, used: dict[str, set[str]], errors: list[str], where: str) -> str:
    def sub(m: re.Match) -> str:
        ns, name, spec = m.group(1), m.group(2).strip(), m.group(3)
        try:
            return resolve(ns, name, spec, used)
        except Exception as exc:  # noqa: BLE001 — every failure is reported, then the run fails
            errors.append(f"{where}: [[{ns}:{name}]] → {exc}")
            return m.group(0)
    return PLACEHOLDER.sub(sub, text)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="section files (default: every *.md in --sections)")
    ap.add_argument("--sections", type=Path, default=SECTIONS_DIR)
    ap.add_argument("--out", type=Path, default=FILLED_DIR)
    ap.add_argument("--check", action="store_true", help="resolve everything, write nothing")
    args = ap.parse_args(argv)

    files = [Path(f) for f in args.files] or sorted(args.sections.glob("*.md"))
    if not files:
        print("no section files found", file=sys.stderr)
        return 2
    used: dict[str, set[str]] = {}
    errors: list[str] = []
    n_placeholders = 0
    outputs: dict[Path, str] = {}
    for f in files:
        text = f.read_text(encoding="utf-8")
        n_placeholders += len(PLACEHOLDER.findall(text))
        outputs[f] = fill_text(text, used, errors, f.name)
    if errors:
        print(f"UNRESOLVED ({len(errors)}):")
        for e in errors:
            print("  " + e)
        return 1
    print(f"resolved {n_placeholders} placeholders in {len(files)} file(s)")
    for ns in sorted(used):
        print(f"  {ns}: {len(used[ns])} distinct names used")
    # the literal scan (R12 F7): no numeral or counting word outside a placeholder without a grid check or a reason
    import literals
    fails = literals.selftest()
    if fails:
        print("LITERAL SCAN SELF-TEST FAILED:", *fails, sep="\n  "); return 1
    findings = literals.scan_files(files)
    s = literals.summary(findings)
    bad = [x for x in findings if x["status"] == "UNALLOWED"]
    print(f"literals: {s['n_literals']} outside placeholders, {s['n_prose']} in prose and {s['n_math']} in formulas ({s['n_settings_checked_against_grids']} settings checked against the grids, {s['n_allowlisted']} allow-listed, {s['n_algebraic']} algebraic, {s['n_unallowed']} unallowed; self-test ok)")
    if not args.check:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "LITERALS.md").write_text(literals.report(findings) + "\n", encoding="utf-8")
    if bad:
        print("UNALLOWED LITERALS:")
        for x in bad[:60]:
            print(f"  {x['file']}:{x['line']} `{x['text']}` {x.get('reason', '')} — {x['context'][:100]}")
        if len(bad) > 60:
            print(f"  … and {len(bad) - 60} more")
        return 1
    if not args.check:
        args.out.mkdir(parents=True, exist_ok=True)
        for f, text in outputs.items():
            (args.out / f.name).write_text(text, encoding="utf-8")
        lines = []
        for ns, rel in REGISTERS.items():
            reg = load_json(rel)
            unused = sorted(set(reg) - used.get(ns, set()))
            lines.append(f"# {ns}: {len(unused)} of {len(reg)} register names unused")
            lines.extend(f"{ns}:{k}" for k in unused)
        (args.out / "UNUSED_REGISTER_NAMES.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote {len(outputs)} filled file(s) to {args.out.relative_to(ROOT)} and UNUSED_REGISTER_NAMES.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
