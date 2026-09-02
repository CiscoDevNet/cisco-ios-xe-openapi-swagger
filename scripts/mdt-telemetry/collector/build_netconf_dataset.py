#!/usr/bin/env python3
"""build_netconf_dataset.py — assemble Device Data transport datasets from the
NETCONF probe files (output/netconf-<PID>.json produced by netconf_get.py).

Emits datasets in the standard Device Data shape (device -> category -> path ->
payload), so each becomes a transport button:
  - netconf-get-live-data.json         (<get>: oper + config merged)
  - netconf-getconfig-live-data.json   (<get-config>: running config only)
  - netconf-sub-live-data.json         (establish-subscription periodic, all roots)
  - netconf-sub-config-live-data.json  (config-root subscription: periodic + on-change)

Payloads (XML) are embedded (truncated) so the page can show them inline.
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
                "payload": redact_payload(e.get("payload") or "")[:PAGE_PAYLOAD_CAP],
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
        if "netconf-sub-config-" in f:  # config-subscription files have their own dataset
            continue
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        pid = doc["pid"]
        for e in doc.get("entries", []):
            if e.get("status") not in ("streamed", "accepted-nodata"):
                continue
            paths.append({
                "pid": pid, "source": doc.get("host", ""), "category": e["category"],
                "path": e["xpath"], "status": "data" if e["status"] == "streamed" else "empty",
                "bytes": e.get("bytes", 0), "payload": redact_payload(e.get("payload") or "")[:PAGE_PAYLOAD_CAP],
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


def build_sub_config() -> dict:
    """netconf-sub-config-<PID>.json: config roots probed with BOTH periodic and
    on-change triggers, pivoted to one path per root carrying the per-mode status
    (mirrors the gNMI ONCE/SAMPLE/ON_CHANGE shape so the page can badge them)."""
    by_key: dict = {}
    order = []
    for f in sorted(glob.glob(str(OUT / "netconf-sub-config-*.json"))):
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        pid = doc["pid"]
        for e in doc.get("entries", []):
            key = (pid, e["xpath"])
            rec = by_key.get(key)
            if rec is None:
                rec = {"pid": pid, "source": doc.get("host", ""), "category": e["category"],
                       "path": e["xpath"], "periodic": None, "onchange": None,
                       "bytes": 0, "payload": ""}
                by_key[key] = rec
                order.append(key)
            st = e.get("status")
            if e.get("mode") == "on-change":
                rec["onchange"] = st
            else:
                rec["periodic"] = st
            if st == "streamed" and (e.get("bytes", 0) or 0) > rec["bytes"]:  # keep richest snapshot
                rec["bytes"] = e.get("bytes", 0)
                rec["payload"] = redact_payload(e.get("payload") or "")[:PAGE_PAYLOAD_CAP]
    paths = []
    for key in order:
        rec = by_key[key]
        if not any(m in ("streamed", "accepted-nodata") for m in (rec["periodic"], rec["onchange"])):
            continue  # both triggers rejected -> not subscribable, drop
        rec["status"] = "data" if "streamed" in (rec["periodic"], rec["onchange"]) else "empty"
        paths.append(rec)
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
        "transport": "NETCONF establish-subscription config — periodic + on-change (SSH/830)",
        "source": "live device capture (NETCONF yang-push config, ncclient)", "encoding": "XML",
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
    periodic = [f for f in glob.glob(str(OUT / "netconf-sub-*.json")) if "netconf-sub-config-" not in f]
    if periodic:
        ds = build_sub()
        out = REPO_ROOT / "netconf-sub-live-data.json"
        out.write_text(json.dumps(ds, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"netconf-sub-live-data.json: {ds['totals']['devices']} devices, {ds['totals']['paths']} paths "
              f"({out.stat().st_size/1024:.0f} KB)")
    if list(glob.glob(str(OUT / "netconf-sub-config-*.json"))):
        ds = build_sub_config()
        out = REPO_ROOT / "netconf-sub-config-live-data.json"
        out.write_text(json.dumps(ds, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"netconf-sub-config-live-data.json: {ds['totals']['devices']} devices, {ds['totals']['paths']} paths "
              f"({out.stat().st_size/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
