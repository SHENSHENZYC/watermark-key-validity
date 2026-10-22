#!/usr/bin/env python3
"""Run the paper's six figure scripts in order (each asserts its values against the agreed reports and registers the
values it prints), then report the checks. Usage: .venv/bin/python research/paper/figures/make_figures.py
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCRIPTS = ["fig1_deployer.py", "fig2_length.py", "fig3_domain.py", "fig4_remedies.py", "fig5_transfer.py", "fig6_operating_points.py"]
for s in SCRIPTS:
    print(f"--- {s}")
    subprocess.run([sys.executable, str(HERE / s)], check=True, cwd=ROOT)
checks = json.loads((ROOT / "research/paper/checks.json").read_text())
tot = sum(v["n"] for k, v in checks.items() if k.startswith("fig")); bad = sum(v["n_failed"] for k, v in checks.items() if k.startswith("fig"))
print(f"figures: {tot} checks against the registers, {bad} failed")
