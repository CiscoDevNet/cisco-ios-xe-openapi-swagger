#!/usr/bin/env python3
"""build_gnmi_dataset.py — Device Data transport datasets from the gNMI probe
files (output/gnmi-<PID>.json = Get, output/gnmi-sub-<PID>.json = Subscribe).

Emits (standard device-data shape, payload embedded, encoding json_ietf):
  - gnmi-get-live-data.json        (gNMI Get, datatype=all)
  - gnmi-getconfig-live-data.json  (gNMI Get, datatype=config)
  - gnmi-state-live-data.json      (gNMI Get, datatype=state / operational)
  - gnmi-sub-live-data.json        (gNMI Subscribe ONCE/SAMPLE/ON_CHANGE support)
"""
from __future__ import annotations

import collections
import glob
import json
from datetime import datetime, timezone
from pathlib import Path

from redact_payload import redact_payload  # mask secrets before embedding

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
REPO_ROOT = HERE.parents[2]
PAGE_PAYLOAD_CAP = 40_000


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


def build_get():
    for op, fname, label in (
            ("all", "gnmi-get-live-data.json", "gNMI Get datatype=all (:9339)"),
            ("config", "gnmi-getconfig-live-data.json", "gNMI Get datatype=config (:9339)"),
            ("state", "gnmi-state-live-data.json", "gNMI Get datatype=state / oper (:9339)")):
        paths = []
        for f in sorted(glob.glob(str(OUT / "gnmi-*.json"))):
            if "gnmi-sub-" in f:
                continue
            doc = json.loads(Path(f).read_text(encoding="utf-8"))
            for e in doc.get("entries", []):
                if e.get("op") != op or e.get("status") not in ("data", "empty"):
                    continue
                paths.append({"pid": doc["pid"], "source": doc.get("host", ""),
                              "category": e["category"], "path": e["xpath"],
                              "status": e["status"], "bytes": e.get("bytes", 0),
                              "payload": redact_payload(e.get("payload") or "")[:PAGE_PAYLOAD_CAP]})
        _write(fname, label, paths, "live device capture (gNMI Get, pygnmi)")


def build_sub():
    paths = []
    for f in sorted(glob.glob(str(OUT / "gnmi-sub-*.json"))):
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        for e in doc.get("entries", []):
            if e.get("once") not in ("streamed", "accepted-nodata"):
                continue
            paths.append({"pid": doc["pid"], "source": doc.get("host", ""),
                          "category": e["category"], "path": e["xpath"],
                          "status": "data" if e["once"] == "streamed" else "empty",
                          "once": e.get("once"), "sample": e.get("sample"),
                          "onchange": e.get("onchange"),
                          "bytes": e.get("bytes", 0), "payload": redact_payload(e.get("payload") or "")[:PAGE_PAYLOAD_CAP]})
    if paths:
        _write("gnmi-sub-live-data.json", "gNMI Subscribe ONCE/SAMPLE/ON_CHANGE (:9339)", paths,
               "live device capture (gNMI Subscribe, pygnmi)")
    else:
        print("gnmi-sub: no data yet (skipped)")


def main() -> int:
    build_get()
    build_sub()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
