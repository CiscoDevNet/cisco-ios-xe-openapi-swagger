#!/usr/bin/env python3
"""build_netconf_dataset.py — assemble Device Data transport datasets from the
NETCONF probe files (output/netconf-<PID>.json produced by netconf_get.py).

Emits two datasets in the standard Device Data shape (device -> category ->
path -> payload), one per operation, so each becomes a transport button:
  - netconf-get-live-data.json        (<get>: oper + config merged)
  - netconf-getconfig-live-data.json  (<get-config>: running config only)

Payloads (XML) are embedded (truncated) so the page can show them inline.
"""
from __future__ import annotations

import collections
import glob
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
REPO_ROOT = HERE.parents[2]

PAGE_PAYLOAD_CAP = 40_000  # chars embedded for the in-page viewer

OPS = {
    "get": ("netconf-get-live-data.json", "NETCONF <get> (SSH/830)"),
    "get-config": ("netconf-getconfig-live-data.json", "NETCONF <get-config> running (SSH/830)"),
}


def build(op: str) -> dict:
    paths = []
    for f in sorted(glob.glob(str(OUT / "netconf-*.json"))):
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        pid = doc["pid"]
        for e in doc.get("entries", []):
            if e.get("op") != op or e.get("status") not in ("data", "empty"):
                continue
            paths.append({
                "pid": pid,
                "source": doc.get("host", ""),
                "category": e["category"],
                "path": e["xpath"],
                "status": e["status"],
                "bytes": e.get("bytes", 0),
                "payload": (e.get("payload") or "")[:PAGE_PAYLOAD_CAP],
            })
    paths.sort(key=lambda e: (e["pid"], e["category"], e["path"]))

    dev_paths = collections.Counter()
    dev_bytes = collections.Counter()
    dev_cat = collections.defaultdict(collections.Counter)
    cat_paths = collections.Counter()
    sources = {}
    for e in paths:
        dev_paths[e["pid"]] += 1
        dev_bytes[e["pid"]] += e["bytes"] or 0
        dev_cat[e["pid"]][e["category"]] += 1
        cat_paths[e["category"]] += 1
        sources[e["pid"]] = e["source"]

    devices = [{
        "pid": pid, "source": sources.get(pid, ""),
        "paths": dev_paths[pid], "records": dev_paths[pid], "bytes": dev_bytes[pid],
        "by_category": dict(dev_cat[pid]),
    } for pid in sorted(dev_paths)]
    categories = [{"category": c, "paths": cat_paths[c]} for c in sorted(cat_paths)]

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "transport": OPS[op][1],
        "source": "live device capture (NETCONF, ncclient)",
        "encoding": "XML",
        "totals": {"devices": len(devices), "paths": len(paths),
                   "records": sum(dev_paths.values())},
        "devices": devices, "categories": categories, "paths": paths,
    }


def build_sub() -> dict:
    """netconf-sub-<PID>.json (establish-subscription, draft yang-push)."""
    paths = []
    for f in sorted(glob.glob(str(OUT / "netconf-sub-*.json"))):
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        pid = doc["pid"]
        for e in doc.get("entries", []):
            if e.get("status") not in ("streamed", "accepted-nodata"):
                continue
            paths.append({
                "pid": pid, "source": doc.get("host", ""), "category": e["category"],
                "path": e["xpath"], "status": "data" if e["status"] == "streamed" else "empty",
                "bytes": e.get("bytes", 0), "payload": (e.get("payload") or "")[:PAGE_PAYLOAD_CAP],
            })
    paths.sort(key=lambda e: (e["pid"], e["category"], e["path"]))
    dev_paths = collections.Counter(); dev_bytes = collections.Counter()
    dev_cat = collections.defaultdict(collections.Counter); cat_paths = collections.Counter()
    sources = {}
    for e in paths:
        dev_paths[e["pid"]] += 1; dev_bytes[e["pid"]] += e["bytes"] or 0
        dev_cat[e["pid"]][e["category"]] += 1; cat_paths[e["category"]] += 1
        sources[e["pid"]] = e["source"]
    devices = [{"pid": p, "source": sources.get(p, ""), "paths": dev_paths[p],
                "records": dev_paths[p], "bytes": dev_bytes[p], "by_category": dict(dev_cat[p])}
               for p in sorted(dev_paths)]
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "transport": "NETCONF establish-subscription periodic (SSH/830)",
        "source": "live device capture (NETCONF yang-push, ncclient)", "encoding": "XML",
        "totals": {"devices": len(devices), "paths": len(paths), "records": sum(dev_paths.values())},
        "devices": devices, "categories": [{"category": c, "paths": cat_paths[c]} for c in sorted(cat_paths)],
        "paths": paths,
    }


def main() -> int:
    for op, (fname, label) in OPS.items():
        ds = build(op)
        out = REPO_ROOT / fname
        out.write_text(json.dumps(ds, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{fname}: {ds['totals']['devices']} devices, {ds['totals']['paths']} paths "
              f"({out.stat().st_size/1024:.0f} KB)  [{label}]")
    if list(glob.glob(str(OUT / "netconf-sub-*.json"))):
        ds = build_sub()
        out = REPO_ROOT / "netconf-sub-live-data.json"
        out.write_text(json.dumps(ds, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"netconf-sub-live-data.json: {ds['totals']['devices']} devices, {ds['totals']['paths']} paths "
              f"({out.stat().st_size/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
