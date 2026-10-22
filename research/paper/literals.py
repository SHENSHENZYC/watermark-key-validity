#!/usr/bin/env python3
"""Scan the section drafts for numerals and counting words that are not placeholders (R12 F7, F15; guide A4.1).

``fill_paper.py --check`` proves only that every placeholder resolves; it never looked at the numbers typed around
them. This module lists the numerals and counting words its patterns recognise in a draft, in the prose and inside the
formulas, classifies each occurrence, and counts by class the spans it sets aside; it is a syntactic check (what a pattern
does not recognise, it does not see), and the manual reading of the drafts covers the rest:

  * **prose settings**: a design constant written beside its symbol (``γ = 0.25``, ``h ∈ {0, 1, 2}``,
    ``N_cal = 5,000``, ``α = 1%``), checked against the set the pinned grids and locks define for that symbol;
  * **math settings**: the same inside ``$…$`` (``$\\gamma = 0.25$``, ``$N_{\\mathrm{cal}} = 5{,}000$``), with the
    LaTeX symbols mapped to the grid symbols and checked the same way;
  * **math constants**: inside a formula the integers 0, 1 and 2, exponents and subscripts are algebraic and pass;
    any other numeral the pattern recognises in a formula (``3\\,\\mathrm{SE}``, ``10^{-9}``, ``4/25``, an example law ``(0.9, 0.1)``)
    must be allow-listed with a reason and, for a tolerance or a pinned constant, a source the scan verifies;
  * **conventions**: the quantile labels of the deployer's view (``the 99% key``, the ``5–95%`` band, a ``95%``
    interval), recognised only in their labelled form, so a measured share such as "95% keys above nominal" is not
    mistaken for one;
  * **allow-listed**: a literal that ``literals_allowed.json`` names for that file (or for every file) with a
    reason; the entry's ``context`` must contain the literal and the occurrence must lie inside that context on its
    line, so an exception vouches for one phrase and not for a line; an entry may carry a ``source`` (a file and a
    regex) that the scan verifies;
  * **unallowed**: everything else; ``fill_paper.py`` and ``assemble.py`` fail on any such literal.

Counting words: two to twenty, the tens to ninety, zero, hundred, thousand, the fractions, and "one" when it counts a
design entity that a register carries (a model, a study, a source, a language, a tokenizer, a width, a rule, a cell,
a unit, an arm, a strength, a method, a law). ``--selftest`` runs the sentences that escaped the first version (R12
F15) and fails unless every one is caught. Usage: ``.venv/bin/python research/paper/literals.py [--selftest] [files...]``.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ALLOWLIST = HERE / "literals_allowed.json"
STUDY_DIRS = {"study1": "outputs/study1_v0.3", "study2": "outputs/study2_v0.1", "study3": "outputs/study3_v0.1", "study4": "outputs/study4_v0.1"}

MATH_SPAN = re.compile(r"\$\$(.*?)\$\$|\$([^$\n]+?)\$", re.S)
# --- what is set aside before the scan, by class (each class is counted and reported; never a typed result) ----------
STRIP = [
    ("markup", re.compile(r"`[^`\n]*`")),                             # code spans (file names, digests, ids)
    ("markup", re.compile(r"\[\[[^\]]+\]\]")),                        # placeholders
    ("citation", re.compile(r"\[@[^\]]+\]")),                           # citation blocks (keys, pages, equation numbers)
    ("citation", re.compile(r"(?<![\w/@.])@[A-Za-z][A-Za-z0-9]*")),     # bare citation keys
    ("markup", re.compile(r"<<(?:TABLE|FIG):[A-Za-z0-9_]+>>")),       # float markers
    ("markup", re.compile(r"<!--.*?-->", re.S)),                      # comments
    ("reference", re.compile(r"^#+\s*(?:[A-E]\.)?\d+(?:\.\d+)?\s", re.M)),  # heading numbers
    ("identifier", re.compile(r"\b\d{4}-\d{2}-\d{2}(?:T[\d:]+Z?)?\b")),   # ISO dates
    ("identifier", re.compile(r"\b(?:Llama-3\.2(?:-1B)?|Qwen2\.5(?:-1\.5B)?|Common Pile v0\.1|Claude Fable 5\.1|Three Bricks|SHA-256|ICLR \d{4}|NeurIPS \d{4}|ICML \d{4}|NIST AI 100-4|C\(2026\) 5054 final|v0\.\d(?:\.\d)?|rep-4|UTF-8|5-gram|first-order|two-way|two-sided|one-sided|two-token|two-key|three-prefix|second-model|one-correlated-draw)\b")),
    ("reference", re.compile(r"§\s*\d+(?:\.\d+)?(?:[–-]\d+(?:\.\d+)?)?")),                                   # section references
    ("reference", re.compile(r"\b(?:Tables?|Figures?|Appendix|Appendices)\s+[A-E]?\d+[a-d]?(?:\s*(?:[–-]|and|,)\s*[A-E]?\d+[a-d]?)*")),
    ("reference", re.compile(r"\b(?:Equation|Proposition|Propositions|Algorithm|Lemma|Remark|Theorem|Measure|Sub-measure|Article|Section|Chapter|Step)s?\s+[A-Z]?\.?\d+(?:\.\d+)?[ab]?(?:\s*(?:and|,)\s*\d+[ab]?)*")),
    ("reference", re.compile(r"\b(?:pp?\.|pages?)\s*\d+(?:\s*[–-]\s*\d+)?(?:,\s*\d+)*")),                 # page references
    ("identifier", re.compile(r"\b(?:R0\d|R1\d|R\d+b?|S\d|T\d|W\d|F\d+|J\d+|O\d+|D\d+|C\d+|A\.\d|B\.\d|C\.\d|E\.\d|1G|[A-F]\d)\b")),  # rule, checkpoint, finding, claim and subsection ids
    ("identifier", re.compile(r"\b(?:Study|Studies|Milestone|round|Round|checkpoint|Checkpoint)\s+\d+(?:\s*(?:[–-]|and|,|to)\s*\d+)*")),
    ("reference", re.compile(r"\b(?:Measure|Tables?)\s+\d+\.\d+")),
    ("identifier", re.compile(r"\bdocument \d+\b")),
    ("notation", re.compile(r"\b1/β\b|\b1/C_\w+|\bnon-zero\b")),                                           # the multiplier, the collision reciprocal, a value word
    ("notation", re.compile(r"\bExp\(1\)|\bpass-1\b|\bBeta\([^)]*\)|\bGamma\([^)]*\)")),                     # named distributions and a phase label
    ("citation", re.compile(r"\b(?:Genhatharan|AutoMark|Unigram|Vovk|Owen|Hoeffding)\s+\d{4}\b")),            # a name-year citation written in prose
    # conventions: the deployer's quantile labels in their labelled form, interval labels, the percentile bands as labelled
    ("convention", re.compile(r"\b(?:the|a|its|each|every)\s+(?:1|5|50|95|99)%\s+key(?:'s|’s)?\b|\b(?:the|its)\s+5%,\s*50%\s+and\s+95%\s+keys\b|\bbands?\s+(?:cover|covers)\s+1–99%\s+and\s+5–95%\s+of\s+the\s+sampled\s+keys\b|\b5th(?:\s*[–-]\s*95th)?\s+percentiles?\b|\b95th[\s-]percentile\b|\b95%\s+(?:interval|intervals|CI)\b|\bnominal-95%|\bthe median key\b", re.I)),
]
# a design constant written beside its symbol in prose
SETTING = re.compile(r"(?P<sym>γ|α|β|δ|κ|h|L|M|N_cal|N_E|N_C|N₀|N_0|N|K_4|K₄|K_fit|K|V|n|s|B|j|m|t|z_α)\s*(?P<op>=|≤|≥|∈|<|>|≈|≠)\s*(?P<val>\{[^}]*\d[^}]*\}|\[[^\]]*\d[^\]]*\]|\d[\d,]*(?:\.\d+)?(?:\s*%|k)?(?:\s*(?:[–-]|to|and)\s*\d[\d,]*(?:\.\d+)?(?:\s*%|k)?)?)")
NUMERAL = re.compile(r"(?<![\w.])(?:±|×|−|-)?(?:\d[\d,]*(?:\.\d+)?|\.\d+)(?:\s*(?:%|pp|×|k|-fold|th|st|nd|rd))?(?!\w|\.\d)")
_TENS = r"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)"
_UNITS = r"(?:one|two|three|four|five|six|seven|eight|nine)"
WORDS = re.compile(r"\b(?:" + _TENS + "-" + _UNITS + r"|zero|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|half|third|quarter|fifth|sixth|tenth|twice|thrice|dozen)\b", re.I)
ONE_DESIGN = re.compile(r"\bone\s+(?:(?:open-weight|base|language|synthetic|real|frozen|generated|English|prompt|corpus|null|retention|context|calibration|evaluation|generation)\s+)?(?:model|models|study|studies|source|sources|language|languages|tokenizer|tokenizers|width|widths|rule|rules|cell|cells|unit|units|arm|arms|strength|strengths|method|methods|law|laws)\b", re.I)
BAND = re.compile(r"\[2/3,\s*3/2\]")
# --- inside a formula -------------------------------------------------------------------------------------------
LATEX_SYM = {r"\gamma": "γ", r"\alpha": "α", r"\beta": "β", r"\delta": "δ", r"\kappa": "κ", r"N_{\mathrm{cal}}": "N_cal", r"N_{\text{cal}}": "N_cal",
             r"N_{\mathrm{eff}}": "N_eff", "N_E": "N_E", "N_C": "N_C", "N_0": "N₀", r"K_{\mathrm{fit}}": "K_fit", "K_4": "K_4"}
MATH_SETTING = re.compile(r"(?<![\\\w_^])(?P<sym>\\gamma|\\alpha|\\beta|\\delta|\\kappa|N_\{\\mathrm\{cal\}\}|N_\{\\text\{cal\}\}|N_\{\\mathrm\{eff\}\}|N_E|N_C|N_0|K_\{\\mathrm\{fit\}\}|K_4|K|N|V|L|M|h|n|s|m|j|t|B)\s*(?P<op>=|\\le\b|\\ge\b|\\leq\b|\\geq\b|<|>|\\in\b|\\approx\b)\s*(?P<val>\\\{(?:[^{}]|\{,\})*\d(?:[^{}]|\{,\})*\\\}|10\^\{-\d+\}|\d[\d{,}]*(?:\.\d+)?(?:\\%)?(?:\s*(?:\\le|\\ge|,|\\dots|\\ldots|–|-)\s*\d[\d{,}]*(?:\.\d+)?)*)")
MATH_TOLERANCE = re.compile(r"10\^\{-\d+\}")
MATH_NUMERAL = re.compile(r"(?<![\w\\.])(?:(?:\d{1,3}(?:\{,\}\d{3})+|\d+)(?:\.\d+)?|\.\d+)(?![\d.]|\{,\})")
MATH_ALGEBRAIC = re.compile(r"(?:\^\{?-?\d+\}?|_\{?\d\}?)")            # exponents and subscripts: algebraic, never a result

_cache: dict[str, object] = {}


def _json(rel: str) -> object:
    if rel not in _cache:
        _cache[rel] = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    return _cache[rel]


def grids() -> dict[str, dict]:
    out = {}
    for s, d in STUDY_DIRS.items():
        lock = _json(f"{d}/PRE_RUN_LOCK.json")
        out[s] = _json(lock["grid"])
    return out


def _norm(x) -> str:
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, int):
        return f"{x:,}"
    if isinstance(x, float):
        return f"{x:g}" if x != int(x) else f"{int(x):,}"
    return str(x).strip()


def allowed_values() -> dict[str, set[str]]:
    """The values each setting symbol may take, from the pinned grids and locks (one set per symbol)."""
    g = grids(); g1, g2, g3, g4 = g["study1"], g["study2"], g["study3"], g["study4"]
    def nums(xs):
        return {_norm(x) for x in xs}
    for band in (g2["primary"]["band"], g3["primary"].get("band", g2["primary"]["band"]), g4["W2"]["band"], g4["W3"]["band"]):
        assert abs(band[0] - 2 / 3) < 1e-12 and band[1] == 1.5, band            # the adequacy band [2/3, 3/2] written in the prose
    V = {l["V"] for l in g1["laws"] if "V" in l} | {t["V"] for t in g2["tokenizers"].values()} | {g4["model"]["V"]}
    L = set(g1["L"]) | {c["L_cell"] for c in g2["cells"]} | {l for c in g2["cells"] for l in c["L"]} | {g3["L"]} | set(g4["lengths"]) | set(g1["L_illustration"])
    alphas = set(g1["alpha"]) | set(g2["alpha"]) | set(g3["alpha"]) | set(g4["alpha"])
    vals = {
        "γ": nums(g1["gamma"]) | nums(g2["families"]["kgw"]["gamma"]) | {_norm(g3["families"]["kgw"]["gamma"]), _norm(g4["gamma"])},
        "α": nums(alphas) | {f"{100 * a:g}%" for a in alphas},
        "β": {_norm(g3["beta"]), _norm(g4["beta"]), f"{100 * g3['beta']:g}%"},
        "δ": {_norm(a["delta"]) for a in g4["arms"]} | {_norm(g3["delta"]), f"{100 * g3['delta']:g}%", _norm(g4["delta_tol"])},
        "h": nums(g1["h"]) | nums(g2["h"]) | nums(g3["h"]) | nums(g4["W3"]["widths"]) | nums(g4["null_arm"]["widths"]) | {_norm(a["h"]) for a in g4["arms"]},
        "L": nums(L),
        "N_cal": nums(g3["N_cal"]) | {_norm(g3["N_cal_set"])} | nums(g4["N_cal"]),
        "N_E": {_norm(g3["N_eval"]), _norm(g3["N_eval_gutenberg"])},
        "N_C": {_norm(g3["N_cal_set"])},
        "N₀": {_norm(g4["null_arm"]["n_texts"])}, "N_0": {_norm(g4["null_arm"]["n_texts"])},
        "N": {_norm(g1["N"]), _norm(g2["N"]), _norm(g3["N_eval"]), _norm(g3["N_eval_gutenberg"]), _norm(g3["N_cal_set"])},
        "K": {_norm(g1["K"]), _norm(g1["K_fixed_core"]), _norm(g2["K"]), _norm(g3["K"]), _norm(g3["K_fit"]), _norm(g4["keys"]["K4"])},
        "K_4": {_norm(g4["keys"]["K4"])}, "K₄": {_norm(g4["keys"]["K4"])}, "K_fit": {_norm(g3["K_fit"])},
        "V": nums(V) | {"128k", "151k"},
        "n": {_norm(g4["prompts"]["n_watermarked"])},
        "s": {_norm(l["s"]) for l in g1["laws"] if "s" in l} | {_norm(g2["validation"]["law"]["s"])},
        "B": {_norm(g3["key_bootstrap_B"]), _norm(g3["crossed_bootstrap"]["B"]), _norm(g3["cal_bootstrap"]["B"]), _norm(g4["key_bootstrap_B"]), "100", "30", "5"},
    }
    return vals


def _split_values(val: str) -> list[str]:
    inner = val.strip().rstrip(".,;:")
    inner = inner.replace("\\{", "").replace("\\}", "").replace("{,}", ",").replace("\\%", "%").replace("\\dots", "…").replace("\\ldots", "…")
    if inner[:1] in "{[" and inner[-1:] in "}]":
        inner = inner[1:-1]
    parts = re.split(r"\s*(?:,(?!\d{3}(?!\d))|…|\.\.\.|[–-]|\\le|\\ge|\bto\b|\band\b)\s*", inner)
    return [p.strip() for p in parts if p.strip() and p.strip() not in ("…", "...")]


def _canon(v: str) -> str:
    v = v.strip().rstrip(".,;:").replace(" ", "").replace("{,}", ",")
    if v.endswith("%"):
        return f"{float(v[:-1].replace(',', '')):g}%"
    if v.endswith("k"):
        return v
    try:
        f = float(v.replace(",", ""))
        return f"{int(f):,}" if f == int(f) else f"{f:g}"
    except ValueError:
        return v


def _source_ok(rule: dict) -> bool:
    src = rule.get("source")
    if not src:
        return True
    text = (ROOT / src["file"]).read_text(encoding="utf-8", errors="replace")
    return re.search(src["regex"], text) is not None


def load_allowlist() -> dict:
    allow = json.loads(ALLOWLIST.read_text(encoding="utf-8")) if ALLOWLIST.exists() else {}
    for fname, rules in allow.items():
        for r in rules:
            assert r.get("context") and r["literal"].lower() in r["context"].lower(), f"allow-list {fname}: the context of {r['literal']!r} must contain the literal"
            assert r.get("reason"), f"allow-list {fname}: {r['literal']!r} has no reason"
    return allow


def _match_rule(rules: list[dict], line: str, start: int, end: int, tok: str) -> dict | None:
    """The first rule whose context contains this very occurrence (the occurrence lies inside the context's span on the line)."""
    low = line.lower()
    for r in rules:
        if r["literal"].lower() != tok.lower():
            continue
        ctx = r["context"].lower(); pos = low.find(ctx)
        while pos >= 0:
            if pos <= start and end <= pos + len(ctx):
                return r
            pos = low.find(ctx, pos + 1)
    return None


def scan_text(text: str, fname: str, allow: dict) -> list[dict]:
    """Classify the numerals, settings and counting words the patterns recognise in a draft, in the prose and inside the formulas, and record the spans set aside by class."""
    m = re.search(r"^##+\s*Open items\s*$", text, re.M)
    if m:
        text = text[: m.start()]
    vals = allowed_values()
    rules = allow.get(fname, []) + allow.get("*", [])
    out: list[dict] = []

    def add(lno, tok, kind, status, reason, line, start, end):
        out.append({"file": fname, "line": lno, "text": tok, "kind": kind, "status": status, "reason": reason, "context": line.strip()[:160], "span": (start, end)})

    def aside(lno, cls, tok, line, start, end):
        """A span set aside by class (a cross-reference, an identifier, a citation, a labelled convention, an exponent): counted, never a literal."""
        if re.search(r"\d|\b(?:" + _TENS + "|" + _UNITS + r"|ten|eleven|twelve|zero|hundred|thousand)\b", tok, re.I):
            out.append({"file": fname, "line": lno, "text": tok.strip(), "kind": "set aside: " + cls, "status": "excluded", "reason": cls, "context": line.strip()[:160], "span": (start, end)})

    def verdict(rule, tok, kind, lno, line, start, end, fallback_status="UNALLOWED", fallback_reason=""):
        if rule and not _source_ok(rule):
            add(lno, tok, kind, "UNALLOWED", f"allow-list source no longer matches: {rule['source']}", line, start, end)
        elif rule:
            add(lno, tok, kind, "allowlisted", rule["reason"], line, start, end)
        else:
            add(lno, tok, kind, fallback_status, fallback_reason, line, start, end)

    for lno, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("|"):
            continue
        # --- the formulas ---------------------------------------------------------------------------------------
        for mb in BAND.finditer(raw):
            aside(lno, "band", mb.group(0), raw, mb.start(), mb.end())   # the adequacy band [2/3, 3/2], asserted against the pinned grids
        line = BAND.sub(lambda mm: " " * len(mm.group(0)), raw)
        blanks = list(line)
        for ms in MATH_SPAN.finditer(line):
            body = ms.group(1) if ms.group(1) is not None else ms.group(2)
            base = ms.start(1) if ms.group(1) is not None else ms.start(2)
            work = body
            for s in MATH_SETTING.finditer(body):
                sym = LATEX_SYM.get(s.group("sym"), s.group("sym")); val = s.group("val")
                st, en = base + s.start(), base + s.end()
                rule = _match_rule(rules, line, st, en, s.group(0).strip())
                if rule:
                    verdict(rule, s.group(0).strip(), "math setting", lno, line, st, en)
                elif MATH_TOLERANCE.fullmatch(val):
                    rule2 = _match_rule(rules, line, base + s.start("val"), base + s.end("val"), val)
                    verdict(rule2, val, "math tolerance", lno, line, st, en, "UNALLOWED", "a tolerance needs an allow-list entry with its protocol or code source")
                else:
                    ok = sym in vals and all(_canon(v) in {_canon(x) for x in vals[sym]} for v in _split_values(val))
                    add(lno, s.group(0).strip(), "math setting", "grid" if ok else "UNALLOWED", "" if ok else "a value outside the grids", line, st, en)
                work = work[: s.start()] + " " * (s.end() - s.start()) + work[s.end():]
            for t in MATH_TOLERANCE.finditer(work):
                st, en = base + t.start(), base + t.end()
                verdict(_match_rule(rules, line, st, en, t.group(0)), t.group(0), "math tolerance", lno, line, st, en, "UNALLOWED", "a tolerance needs an allow-list entry with its protocol or code source")
                work = work[: t.start()] + " " * (t.end() - t.start()) + work[t.end():]
            for e in MATH_ALGEBRAIC.finditer(work):
                aside(lno, "exponent or subscript", e.group(0), line, base + e.start(), base + e.end())
            work = MATH_ALGEBRAIC.sub(lambda mm: " " * len(mm.group(0)), work)
            for n in list(WORDS.finditer(work)) + list(ONE_DESIGN.finditer(work)):   # a counting word written inside a formula (\text{…})
                st, en = base + n.start(), base + n.end()
                verdict(_match_rule(rules, line, st, en, n.group(0)), n.group(0), "math word", lno, line, st, en)
            for n in MATH_NUMERAL.finditer(work):
                tok = n.group(0).replace("{,}", ",")
                st, en = base + n.start(), base + n.end()
                if tok in ("0", "1", "2"):
                    add(lno, tok, "math constant", "algebraic", "0, 1 and 2 inside a formula are algebraic", line, st, en); continue
                verdict(_match_rule(rules, line, st, en, tok), tok, "math numeral", lno, line, st, en, "UNALLOWED", "a numeral inside a formula that is not 0, 1, 2, an exponent or a subscript needs an allow-list entry")
            for i in range(ms.start(), ms.end()):
                blanks[i] = " "
        prose = "".join(blanks)
        # --- the prose ------------------------------------------------------------------------------------------
        stripped = prose
        for cls, pat in STRIP:
            for mm in pat.finditer(stripped):
                aside(lno, cls, mm.group(0), line, mm.start(), mm.end())
            stripped = pat.sub(lambda mm: " " * len(mm.group(0)), stripped)
        work = stripped
        for s in SETTING.finditer(stripped):
            sym, val = s.group("sym"), s.group("val"); st, en = s.start(), s.end()
            rule = _match_rule(rules, line, st, en, s.group(0).rstrip(".,;:"))
            if rule:
                verdict(rule, s.group(0).rstrip(".,;:"), "setting", lno, line, st, en)
            else:
                ok = sym in vals and all(_canon(v) in {_canon(x) for x in vals[sym]} for v in _split_values(val))
                add(lno, s.group(0).rstrip(".,;:"), "setting", "grid" if ok else "UNALLOWED", "" if ok else "a value outside the grids", line, st, en)
            work = work[:st] + " " * (en - st) + work[en:]
        for n in list(NUMERAL.finditer(work)) + list(WORDS.finditer(work)) + list(ONE_DESIGN.finditer(work)):
            raw_tok = n.group(0); tok = raw_tok.strip().rstrip(".,;:")
            st = n.start() + (len(raw_tok) - len(raw_tok.lstrip())); en = st + len(tok)
            kind = "numeral" if n.re is NUMERAL else "word"
            verdict(_match_rule(rules, line, st, en, tok), tok, kind, lno, line, st, en)
    return out


def scan_files(files: list[Path]) -> list[dict]:
    allow = load_allowlist()
    out = []
    for f in files:
        out.extend(scan_text(f.read_text(encoding="utf-8"), f.name, allow))
    return out


def summary(findings: list[dict]) -> dict:
    lits = [x for x in findings if x["status"] != "excluded"]
    n = lambda **kw: sum(1 for x in lits if all(x.get(k) == v for k, v in kw.items()))
    aside = {}
    for x in findings:
        if x["status"] == "excluded":
            aside[x["reason"]] = aside.get(x["reason"], 0) + 1
    return {"n_literals": len(lits), "n_prose": sum(1 for x in lits if not x["kind"].startswith("math")), "n_math": sum(1 for x in lits if x["kind"].startswith("math")),
            "n_settings_checked_against_grids": n(status="grid"), "n_allowlisted": n(status="allowlisted"), "n_algebraic": n(status="algebraic"), "n_unallowed": n(status="UNALLOWED"),
            "n_set_aside": sum(aside.values()), "set_aside_by_class": dict(sorted(aside.items()))}


def report(findings: list[dict]) -> str:
    s = summary(findings)
    lines = ["# Literal inventory of the section drafts (numerals and counting words outside placeholders, in the prose and inside the formulas)", "",
             f"{s['n_literals']} literals ({s['n_prose']} in prose, {s['n_math']} in formulas): {s['n_settings_checked_against_grids']} settings checked against the grids, "
             f"{s['n_allowlisted']} allow-listed with a reason, {s['n_algebraic']} algebraic constants (0, 1, 2 in a formula), {s['n_unallowed']} unallowed. "
             f"Set aside by class before the scan, {s['n_set_aside']} spans that carry a digit or a counting word: {s['set_aside_by_class']}. "
             "The scan is syntactic: it classifies what its patterns recognise and lists the classes it sets aside; a numeral written in a form outside its patterns is not seen by it.", ""]
    by_file: dict[str, list[dict]] = {}
    for x in findings:
        by_file.setdefault(x["file"], []).append(x)
    for f, xs in by_file.items():
        lines += [f"## {f}", "", "| line | literal | kind | status | reason / context |", "|---|---|---|---|---|"]
        for x in [y for y in xs if y["status"] != "excluded"] + [y for y in xs if y["status"] == "excluded"]:
            lines.append(f"| {x['line']} | `{x['text']}` | {x['kind']} | {x['status']} | {(x.get('reason') or x['context']).replace('|', '\\|')} |")
        lines.append("")
    return "\n".join(lines)


def selftest() -> list[str]:
    """The escapes the reviewer demonstrated at R12 round 2 (F15), each of which must now be caught."""
    allow = load_allowlist()
    cases = [("There were zero failures.", ["zero"]), ("There were sixty keys.", ["sixty"]), ("The estimate was $0.123$.", ["0.123"]),
             ("We used $N_{\\mathrm{cal}} = 5{,}001$ null texts.", ["N_{\\mathrm{cal}} = 5{,}001"]), ("We measured 95% keys above nominal.", ["95%"]),
             ("On one model's watermarked generations the cost is large.", ["one model"]), ("The tolerance is $10^{-7}$ here.", ["10^{-7}"]),
             ("We compared two datasets and the covariance between two texts.", ["two"]),
             ("There were seventy-five keys.", ["seventy-five"]), ("We measured 5–95% of the keys above nominal.", ["5"]),
             ("The estimate was $.123$.", [".123"]), ("We measured $\\text{sixty}$ failures.", ["sixty"])]
    failures = []
    for sent, expect in cases:
        hits = [x for x in scan_text(sent, "00_abstract.md", allow) if x["status"] == "UNALLOWED"]
        got = [x["text"] for x in hits]
        for e in expect:
            if e not in got:
                failures.append(f"not caught: {e!r} in {sent!r} (flagged: {got})")
    ok = scan_text("The 99% key is high; the bands cover 1–99% and 5–95% of the sampled keys; $\\gamma = 0.25$ and $h \\in \\{0, 1, 2\\}$; $(V-1)$ and $s_0^2$; a two-way table.", "00_abstract.md", allow)
    bad = [x for x in ok if x["status"] == "UNALLOWED"]
    if bad:
        failures.append(f"a convention, a grid setting or an algebraic constant was flagged: {[x['text'] for x in bad]}")
    band = scan_text("The interval was [2/3, 3/2].", "00_abstract.md", allow)   # R12 F25: the band is inventoried as an excluded class, never silently removed
    if not any(x["status"] == "excluded" and x["reason"] == "band" for x in band):
        failures.append("the adequacy band [2/3, 3/2] was not inventoried as an excluded class")
    return failures


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--selftest":
        fails = selftest()
        print("selftest:", "ok" if not fails else "\n  ".join(["FAILED"] + fails))
        sys.exit(1 if fails else 0)
    files = [Path(a) for a in args] or sorted((HERE / "sections").glob("*.md"))
    fs = scan_files(files)
    print(report(fs))
    sys.exit(1 if any(x["status"] == "UNALLOWED" for x in fs) else 0)
