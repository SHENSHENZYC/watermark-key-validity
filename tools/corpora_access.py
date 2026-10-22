"""The only sanctioned path to the frozen texts for scientific use (audit §5.7, the seal; v2 after R02 round 1).

Access(units_dir, version) binds to the finalised partition map partition_v<version>.parquet, whose SHA-256 must equal the
digest file written at finalisation. load_texts(canonical_ids, partition, ...) resolves every requested id against that
map (unknown ids and ids whose stored partition differs from the request are refused), validates the partition name, and
for the held-out partition requires a lock file that is registered in the allow-list and binds the corpora manifest's
digest, the partition map's digest, the units-metadata digest, a study name and a non-empty list of cells
('source/lang@L'); every requested unit must lie within those cells by its bound source, language and length eligibility
(R02 round 2, F9); every held-out opening is logged with the digest of the requested ids.
"""
import datetime, gzip, hashlib, json, pathlib
import pyarrow.parquet as pq

DEFAULTS = {"manifest": "outputs/corpora_manifest_v0.1.json", "allowlist": "outputs/corpora_seal_allowlist.json", "openings": "outputs/holdout_openings.jsonl"}
PARTITIONS = ("open", "holdout")


class SealError(PermissionError):
    pass


def _sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


class Access:
    def __init__(self, units_dir, version, manifest=None, allowlist=None, openings=None):
        self.units_dir = pathlib.Path(units_dir); self.version = version
        self.manifest = pathlib.Path(manifest or DEFAULTS["manifest"]); self.allowlist = pathlib.Path(allowlist or DEFAULTS["allowlist"]); self.openings = pathlib.Path(openings or DEFAULTS["openings"])
        fp = self.units_dir / f"partition_v{version}.parquet"; dg = self.units_dir / f"partition_v{version}.sha256"
        if not fp.exists() or not dg.exists():
            raise SealError(f"no finalised partition v{version} in {self.units_dir}")
        self.partition_sha256 = _sha(fp)
        if self.partition_sha256 != dg.read_text().strip():
            raise SealError("the partition map does not match its digest file")
        t = pq.read_table(fp, columns=["canonical_id", "file", "pos", "partition", "source", "lang"]).to_pandas()
        self.map = {c: (f, int(p), part, s, l) for c, f, p, part, s, l in zip(t["canonical_id"], t["file"], t["pos"], t["partition"], t["source"], t["lang"])}
        man = json.loads(self.manifest.read_text())
        self.paths = {e["path"]: pathlib.Path(e["local_path"]) for e in man["entries"].values() if e.get("status") == "OK"}
        # bound eligibility provenance (R02 round 2, F9): the units metadata, verified against its digest written at finalisation
        ud = self.units_dir / f"units_v{version}.sha256"
        self.units_sha256 = ud.read_text().strip() if ud.exists() else None
        self.tok = None
        cj = self.units_dir / "counts.json"
        if self.units_sha256 and cj.exists():
            meta = json.loads(cj.read_text()); h = hashlib.sha256()
            for f in meta["files"]:
                h.update((self.units_dir / f["units_file"]).read_bytes())
            h.update(cj.read_bytes())
            if h.hexdigest() != self.units_sha256:
                raise SealError("the units metadata does not match the digest written at finalisation")
            tok = {}
            for f in meta["files"]:
                u = pq.read_table(self.units_dir / f["units_file"], columns=["canonical_id", "n_tok_llama"]).to_pandas()
                tok.update(zip(u["canonical_id"], u["n_tok_llama"]))
            self.tok = tok

    @staticmethod
    def parse_cell(cell):
        """'source/lang@L' -> (source, lang, L)."""
        try:
            sl, L = cell.split("@"); src, lang = sl.split("/"); return src, lang, int(L)
        except Exception:
            raise SealError(f"malformed cell {cell!r}")

    def in_scope(self, cid, cells):
        """A unit is within the requested scope when its bound (source, lang) matches a cell and it meets that cell's length
        eligibility from the bound token counts (books: 1,000 + L); without bound counts, length cannot be checked and the
        unit is refused."""
        f, p, part, src, lang = self.map[cid]
        for cell in cells:
            s, l, Lc = self.parse_cell(cell)
            if s == src and l == lang:
                if self.tok is None:
                    raise SealError("no bound units metadata: cell length eligibility cannot be verified")
                need = Lc + (1000 if src == "gutenberg" else 0)
                if self.tok.get(cid, -1) >= need:
                    return True
        return False

    def check_seal(self, partition, final_lock, study, cells, ids):
        if partition not in PARTITIONS:
            raise SealError(f"unknown partition {partition!r}")
        if partition == "open":
            return None
        if final_lock is None:
            raise SealError("held-out partition requested without a final lock")
        lock = pathlib.Path(final_lock)
        if not lock.exists():
            raise SealError(f"lock file not found: {lock}")
        sha = _sha(lock)
        allow = json.loads(self.allowlist.read_text()).get("locks", []) if self.allowlist.exists() else []
        if sha not in allow:
            raise SealError("lock file is not registered in the seal allow-list")
        j = json.loads(lock.read_text())
        if j.get("final") is not True:
            raise SealError("lock is not final")
        if not isinstance(j.get("study"), str) or not j["study"] or j["study"] != study:
            raise SealError("lock study name missing or different from the requested study")
        if j.get("manifest_sha256") != _sha(self.manifest):
            raise SealError("lock does not bind this corpora manifest")
        if j.get("partition_sha256") != self.partition_sha256:
            raise SealError("lock does not bind this partition map")
        if not isinstance(j.get("cells"), list) or not j["cells"] or not isinstance(cells, list) or not cells or not set(cells) <= set(j["cells"]):
            raise SealError("cells missing, or the requested cells are not within the lock's cells")
        if j.get("units_sha256") != self.units_sha256 or self.units_sha256 is None:
            raise SealError("lock does not bind this units-metadata digest")
        out_of_scope = [c for c in ids if not self.in_scope(c, cells)]
        if out_of_scope:
            raise SealError(f"{len(out_of_scope)} requested units are outside the requested cells (source, language or length), e.g. {out_of_scope[0]!r}")
        ids_digest = hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()
        rec = {"opened_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "lock_sha256": sha, "study": study, "cells": cells, "n_units": len(ids), "ids_sha256": ids_digest, "partition_sha256": self.partition_sha256, "units_sha256": self.units_sha256}
        with self.openings.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        return rec

    def load_texts(self, canonical_ids, partition, final_lock=None, study=None, cells=None):
        ids = list(canonical_ids)
        if partition not in PARTITIONS:
            raise SealError(f"unknown partition {partition!r}")
        unknown = [c for c in ids if c not in self.map]
        if unknown:
            raise SealError(f"{len(unknown)} requested ids are not in the finalised partition (stale or wrong ids), e.g. {unknown[0]!r}")
        wrong = [c for c in ids if self.map[c][2] != partition]
        if wrong:
            raise SealError(f"{len(wrong)} requested ids belong to another partition than {partition!r}, e.g. {wrong[0]!r}")
        self.check_seal(partition, final_lock, study, cells, ids)
        by_file = {}
        for c in ids:
            f, p, *_ = self.map[c]; by_file.setdefault(f, {})[p] = c
        for file, wanted in by_file.items():
            local = self.paths[file]
            if local.suffix == ".parquet":
                pf = pq.ParquetFile(local); row = 0
                for rg in range(pf.metadata.num_row_groups):
                    n = pf.metadata.row_group(rg).num_rows
                    hit = [p for p in wanted if row <= p < row + n]
                    if hit:
                        col = pf.read_row_group(rg, columns=["text"]).column("text").to_pylist()
                        for p in hit:
                            yield wanted[p], col[p - row]
                    row += n
            else:
                remaining = dict(wanted)
                with gzip.open(local, "rt", encoding="utf-8") as fh:
                    for n, line in enumerate(fh, 1):
                        if n in remaining:
                            yield remaining.pop(n), json.loads(line)["text"]
                            if not remaining:
                                break
