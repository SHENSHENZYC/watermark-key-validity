"""Render the Stage 2 score table from research/screen/SCORES_v0.1.json (ranked by novelty, then by the sum).
Usage: python3 tools/render_screen_table.py [path/to/SCORES.json]"""
import json, sys, pathlib

path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "research/screen/SCORES_v0.1.json")
data = json.loads(path.read_text())
rows = data["candidates"]
for r in rows:
    for k in ("N", "F", "M", "P"):
        assert 1 <= r[k] <= 5, (r["id"], k, r[k])
    r["sum"] = r["N"] + r["F"] + r["M"] + r["P"]
rows.sort(key=lambda r: (-r["N"], -r["sum"], r["id"]))
assert len({r["id"] for r in rows}) == len(rows) == 14, len(rows)
print("| Rank | Candidate | N | F | M | P | Sum | A6 | Nearest prior work (search-level) | Verdict |")
print("|---|---|---|---|---|---|---|---|---|---|")
for i, r in enumerate(rows, 1):
    print(f"| {i} | **{r['id']}** {r['title']} | {r['N']} | {r['F']} | {r['M']} | {r['P']} | {r['sum']} | {r['a6']} | {r['nearest']} | {r['verdict']} |")
print()
print(f"Scores: {data['scale']} Generated {data['date']} by `tools/render_screen_table.py` from `research/screen/SCORES_v0.1.json`; {len(rows)} candidates.")
