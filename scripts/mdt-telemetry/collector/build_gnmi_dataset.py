#!/usr/bin/env python3
"""build_gnmi_dataset.py — Device Data transport datasets from the gNMI probe
files (output/gnmi-<PID>.json = Get, output/gnmi-sub-<PID>.json = Subscribe).

Emits (standard device-data shape, encoding json_ietf):
  - gnmi-get-live-data.json        (gNMI Get, datatype=all)
  - gnmi-getconfig-live-data.json  (gNMI Get, datatype=config)
  - gnmi-state-live-data.json      (gNMI Get, datatype=state / operational)
  - gnmi-sub-live-data.json        (gNMI Subscribe ONCE/SAMPLE/ON_CHANGE support)

The datasets are an index: each path with data points at
releases/<device_data>/gnmi-data/<method>/<sha1(path)[:16]>.json, which holds the
full redacted response for every device ({path, ..., pids: {PID: {value}}}, the
same shape as RESTCONF live-data), fetched by the page on selection.
"""
from __future__ import annotations

import collections
import glob
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from redact_payload import redact_payload  # mask secrets before publishing

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
REPO_ROOT = HERE.parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from _release_paths import device_data_release  # noqa: E402

DATA_DIR_NAME = "gnmi-data"


def _rollup(paths):
    dev_paths = collections.Counter(); dev_bytes = collections.Counter()
    dev_cat = collections.defaultdict(collections.Counter); cat_paths = collections.Counter()
    sources = {}
    for e in paths:
        dev_paths[e["pid"]] += 1
        dev_bytes[e["pid"]] += e.get("bytes", 0) or 0
        dev_cat[e["pid"]][e["category"]] += 1
        cat_paths[e["category"]] += 1
        sources[e["pid"]] = e.get("source", "")
    devices = [{"pid": p, "source": sources.get(p, ""), "paths": dev_paths[p],
                "records": dev_paths[p], "bytes": dev_bytes[p], "by_category": dict(dev_cat[p])}
               for p in sorted(dev_paths)]
    categories = [{"category": c, "paths": cat_paths[c]} for c in sorted(cat_paths)]
    return devices, categories


def _write(fname, transport, paths, source, encoding="json_ietf"):
    paths.sort(key=lambda e: (e["pid"], e["category"], e["path"]))
    devices, categories = _rollup(paths)
    ds = {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
          "transport": transport, "source": source, "encoding": encoding,
          "totals": {"devices": len(devices), "paths": len(paths),
                     "records": sum(d["paths"] for d in devices)},
          "devices": devices, "categories": categories, "paths": paths}
    out = REPO_ROOT / fname
    out.write_text(json.dumps(ds, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{fname}: {ds['totals']['devices']} devices, {ds['totals']['paths']} paths ({out.stat().st_size/1024:.0f} KB)")


def _path_hash(path: str) -> str:
    return hashlib.sha1(path.encode("utf-8")).hexdigest()[:16]


def _without_timestamps(value):
    """Each gNMI reply carries its own notification timestamp; ignore it when comparing bodies."""
    if isinstance(value, dict):
        return {k: _without_timestamps(v) for k, v in value.items() if k != "timestamp"}
    if isinstance(value, list):
        return [_without_timestamps(v) for v in value]
    return value


# Get datatype=config / state bodies that equal the device's datatype=all body point at the get file.
DEDUPE_AGAINST_GET = {"getconfig", "state"}


class PayloadFiles:
    """Collects redacted payloads per (method, path) across devices, then writes one file each."""

    def __init__(self, release: str):
        self.release = release
        self.root = REPO_ROOT / "releases" / release / DATA_DIR_NAME
        self.docs: dict[tuple[str, str], dict] = {}
        self.deduped = 0

    def _rel(self, method: str, path: str) -> str:
        return f"releases/{self.release}/{DATA_DIR_NAME}/{method}/{_path_hash(path)}.json"

    def add(self, method: str, pid: str, entry: dict) -> tuple[str, int, bool]:
        """Register one device's payload; returns (site-relative file URL, redacted size, same-as-get)."""
        text = redact_payload(entry.get("payload") or "")
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            value = text  # keep a non-JSON body verbatim rather than drop it
        if method in DEDUPE_AGAINST_GET:
            get_doc = self.docs.get(("get", entry["xpath"]))
            get_value = get_doc["pids"].get(pid, {}).get("value") if get_doc else None
            if get_value is not None and _without_timestamps(get_value) == _without_timestamps(value):
                self.deduped += 1
                return self._rel("get", entry["xpath"]), len(text), True
        key = (method, entry["xpath"])
        doc = self.docs.setdefault(key, {
            "path": entry["xpath"], "gnmi_path": entry.get("gnmi_path", ""), "method": method,
            "category": entry["category"], "module": entry.get("module", ""), "pids": {}})
        doc["pids"][pid] = {"value": value}
        return self._rel(method, entry["xpath"]), len(text), False

    def write(self) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)  # this builder owns the folder; drop files of vanished paths
        total = 0
        for (method, path), doc in self.docs.items():
            target = self.root / method / f"{_path_hash(path)}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            doc["pids"] = dict(sorted(doc["pids"].items()))
            text = json.dumps(doc, separators=(",", ":"), ensure_ascii=False) + "\n"
            target.write_text(text, encoding="utf-8")
            total += len(text)
        print(f"{DATA_DIR_NAME}/: {len(self.docs)} files ({total/1048576:.1f} MB) under releases/{self.release}/; "
              f"{self.deduped} config/state bodies share the get file")


def _index_entry(doc: dict, entry: dict, status: str, files: PayloadFiles, method: str) -> dict:
    out = {"pid": doc["pid"], "source": doc.get("host", ""), "category": entry["category"],
           "module": entry.get("module", ""), "path": entry["xpath"], "gnmi_path": entry.get("gnmi_path", ""),
           "status": status}
    if entry.get("depth"):
        out["depth"] = entry["depth"]
    if status == "data":
        out["file"], out["bytes"], same_as_get = files.add(method, doc["pid"], entry)
        if same_as_get:
            out["same_as"] = "gnmi-get"
    else:
        out["bytes"] = 0
        out["payload"] = ""
    return out


def build_get(files: PayloadFiles):
    for op, method, fname, label in (
            ("all", "get", "gnmi-get-live-data.json", "gNMI Get datatype=all (:9339)"),
            ("config", "getconfig", "gnmi-getconfig-live-data.json", "gNMI Get datatype=config (:9339)"),
            ("state", "state", "gnmi-state-live-data.json", "gNMI Get datatype=state / oper (:9339)")):
        paths = []
        for f in sorted(glob.glob(str(OUT / "gnmi-*.json"))):
            if "gnmi-sub-" in f:
                continue
            doc = json.loads(Path(f).read_text(encoding="utf-8"))
            for e in doc.get("entries", []):
                if e.get("op") != op or e.get("status") not in ("data", "empty"):
                    continue
                if e.get("depth") and e["status"] != "data":
                    continue  # nested OpenConfig nodes are listed only when populated
                paths.append(_index_entry(doc, e, e["status"], files, method))
        _write(fname, label, paths, "live device capture (gNMI Get, pygnmi)")


def build_sub(files: PayloadFiles):
    paths = []
    for f in sorted(glob.glob(str(OUT / "gnmi-sub-*.json"))):
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        for e in doc.get("entries", []):
            if e.get("once") not in ("streamed", "accepted-nodata"):
                continue
            if e.get("depth") and e["once"] != "streamed":
                continue
            status = "data" if e["once"] == "streamed" else "empty"
            entry = _index_entry(doc, e, status, files, "sub")
            entry.update(once=e.get("once"), sample=e.get("sample"), onchange=e.get("onchange"))
            paths.append(entry)
    if paths:
        _write("gnmi-sub-live-data.json", "gNMI Subscribe ONCE/SAMPLE/ON_CHANGE (:9339)", paths,
               "live device capture (gNMI Subscribe, pygnmi)")
    else:
        print("gnmi-sub: no data yet (skipped)")


def main() -> int:
    files = PayloadFiles(device_data_release())
    build_get(files)
    build_sub(files)
    files.write()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
