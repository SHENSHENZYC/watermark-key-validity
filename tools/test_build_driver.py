"""Regression fixtures for the build driver's control flow (R02 F11/F16), with command capture and no subprocess: (a) an
audit with P5 false stops the build before expansion or finalisation; (b) an existing final version is refused before any
command; (c) a non-PASS final audit raises; (d) a book-cell count failure followed by passing counts issues exactly one
freeze step and one loader step into the selected units directory before finalisation. Exits non-zero on failure.
Usage: .venv/bin/python tools/test_build_driver.py
"""
import json, pathlib, sys, tempfile, types
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import corpora_build as B

def audit(p5=True, fail_cells=False, verdict="PASS"):
    cells = {"gutenberg/en@1024": 2000 if fail_cells else 3000}
    return {"verdict": verdict, "rules": {"P1": {"pass": True}, "P5": {"pass": p5}, "P6": {"pass": True},
            "P2": {"open_eligible_256": {"news/en@256": 20000}, "sites_with_>=200": 25}, "P3": {"open_eligible_256": {}}, "P4": {"open_eligible_1024": {"gutenberg/en@1024": 6000}},
            "P7": {"failed_excluded_cells": [k for k, v in cells.items() if v < 2500]}}, "partition": {"finalised": verdict == "PASS"}, "partition_summary": {"rejected_files": {}}}

def harness(audits, manifest_states):
    """Replace subprocess execution and file reads; record the commands the driver would run."""
    cmds, state = [], {"audit_i": 0, "man_i": 0}
    def fake_run(cmd, log, env=None):
        cmds.append((" ".join(str(x) for x in cmd), env.get("CORPORA_UNITS_DIR") if env else None))
        return ""
    real_read = pathlib.Path.read_text
    def fake_read(self, *a, **k):
        if self.name.startswith("corpora_audit_v"):
            a_ = audits[min(state["audit_i"], len(audits) - 1)]; state["audit_i"] += 1; return json.dumps(a_)
        if self.name == "corpora_manifest_v0.1.json":
            m = manifest_states[min(state["man_i"], len(manifest_states) - 1)]; state["man_i"] += 1; return json.dumps(m)
        return real_read(self, *a, **k)
    return cmds, fake_run, fake_read

def main():
    ok = True
    real_run, real_read, real_exists = B.run, pathlib.Path.read_text, pathlib.Path.exists
    try:
        # (a) P5 false stops before expansion/finalisation
        cmds, fr, frd = harness([audit(p5=False)], [{"entries": {}}]); B.run, pathlib.Path.read_text = fr, frd; pathlib.Path.exists = lambda self: False
        try:
            B.main("9.9", 32, 4, 0.65, 4, False); res = "no exit"
        except SystemExit as e:
            res = str(e)
        names = [c.split("/")[-1].split(" ")[0] for c, _ in cmds]
        good = "integrity" in res and len(cmds) == 2 and not any("--final" in c for c, _ in cmds); ok &= good; print(f"  {'ok ' if good else 'FAIL'} P5 failure: {res[:60]} | commands {names}")
        # (b) existing final version refused before any command
        cmds, fr, frd = harness([audit()], [{"entries": {}}]); B.run, pathlib.Path.read_text = fr, frd; pathlib.Path.exists = lambda self: self.name == "partition_v9.9.parquet"
        try:
            B.main("9.9", 32, 4, 0.65, 4, False); res = "no exit"
        except SystemExit as e:
            res = str(e)
        good = "REFUSED" in res and len(cmds) == 0; ok &= good; print(f"  {'ok ' if good else 'FAIL'} existing version: {res[:50]} | commands {len(cmds)}")
        # (c) non-PASS final audit raises
        cmds, fr, frd = harness([audit(), audit(verdict="PARTIAL")], [{"entries": {}}]); B.run, pathlib.Path.read_text = fr, frd; pathlib.Path.exists = lambda self: False
        try:
            B.main("9.9", 32, 4, 0.65, 4, False); res = "no exit"
        except SystemExit as e:
            res = str(e)
        good = "did not pass" in res; ok &= good; print(f"  {'ok ' if good else 'FAIL'} non-PASS final audit: {res[:60]}")
        # (d) one book-cell failure -> one freeze + one loader step into the selected directory, then finalise
        man0 = {"entries": {"a": {"path": "x", "status": "OK"}}}; man1 = {"entries": {"a": {"path": "x", "status": "OK"}, "b": {"path": "project_gutenberg-dolma-0001.json.gz", "status": "OK"}}}
        cmds, fr, frd = harness([audit(fail_cells=True), audit(), audit()], [man0, man1, man1]); B.run, pathlib.Path.read_text = fr, frd; pathlib.Path.exists = lambda self: False
        try:
            B.main("9.9", 32, 4, 0.65, 4, False); res = "completed"
        except SystemExit as e:
            res = str(e)
        names = [c.split("/")[-1].split(" ")[0] for c, _ in cmds]; envs = [e for c, e in cmds if "corpora_loader" in c]
        good = res == "completed" and names.count("freeze_corpora.py") == 1 and names.count("corpora_loader.py") == 1 and envs == ["outputs/corpora_units_v9.9"] and any("--final" in c for c, _ in cmds)
        ok &= good; print(f"  {'ok ' if good else 'FAIL'} expansion then finalise: {res} | {names} | loader dir {envs}")
    finally:
        B.run, pathlib.Path.read_text, pathlib.Path.exists = real_run, real_read, real_exists
    print("DRIVER TESTS", "PASS" if ok else "FAIL")
    return ok

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
