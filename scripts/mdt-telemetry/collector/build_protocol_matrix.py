#!/usr/bin/env python3
"""build_protocol_matrix.py — status-aware cross-protocol gap grid.

Reads the RAW collector outputs (not just the browse datasets) so each cell
captures WHY a method did or didn't return data:
  data  = returned content
  ok    = method supported the path but returned nothing (e.g. subscribe
          accepted, empty datastore)
  no    = method rejected / doesn't support the path (the gap signal)
  (absent) = not applicable / not collected

Keyed by (device, YANG module). Output protocol-matrix.json powers the Device
Data comparison view so gaps (GET works but subscribe/gNMI doesn't) are visible.
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
PREFIX_MAP = REPO_ROOT / "yang-prefix-map.json"

METHODS = [
    ("mdt", "MDT periodic"),
    ("restconf", "RESTCONF GET"),
    ("netconf-get", "NETCONF get"),
    ("netconf-getconfig", "NETCONF get-config"),
    ("netconf-sub", "NETCONF subscribe"),
    ("gnmi-get", "gNMI Get"),
    ("gnmi-getconfig", "gNMI Get config"),
    ("gnmi-state", "gNMI Get state"),
    ("gnmi-sub", "gNMI Subscribe"),
]
RANK = {"data": 3, "ok": 2, "no": 1}


def prefix_to_module():
    try:
        data = json.loads(PREFIX_MAP.read_text(encoding="utf-8"))
        return {p: m for m, p in (data.get("modules") or {}).items()}
    except (json.JSONDecodeError, OSError):
        return {}


def module_to_prefix():
    try:
        data = json.loads(PREFIX_MAP.read_text(encoding="utf-8"))
        return dict(data.get("modules") or {})
    except (json.JSONDecodeError, OSError):
        return {}


def resolve_module(prefix, container, m2p):
    """Pick the module that defines a top container when several share a prefix
    (e.g. `ios` -> Cisco-IOS-XE-native, not an augmentation module)."""
    cands = [m for m, p in m2p.items() if p == prefix]
    if len(cands) == 1:
        return cands[0]
    if not cands:
        return prefix
    want = container.lower()
    exact = [m for m in cands if m.lower().rsplit("cisco-ios-xe-", 1)[-1] == want]
    if exact:
        return exact[0]
    ends = [m for m in cands if m.lower().endswith(want)]
    if ends:
        return min(ends, key=len)
    contains = [m for m in cands if want in m.lower()]
    if contains:
        return min(contains, key=len)
    return sorted(cands)[0]


def to_module(path, p2m, m2p=None):
    p = path.lstrip("/")
    if p.startswith("data/"):
        p = p[len("data/"):]
    head = p.split("/")[0]
    prefix = head.split(":")[0]
    container = head.split(":", 1)[1].split("/")[0] if ":" in head else ""
    if m2p is not None and container:
        return resolve_module(prefix, container, m2p)
    return p2m.get(prefix, prefix)


def entry_module(e, p2m, m2p=None):
    """Prefer the module the collector already resolved (handles shared prefixes
    like `ios` -> Cisco-IOS-XE-native); fall back to deriving it from the path."""
    return e.get("module") or to_module(e["xpath"], p2m, m2p)


def collect():
    p2m = prefix_to_module()
    m2p = module_to_prefix()
    grid = {}
    devices = set()

    def put(pid, module, cat, method, state, xpath=None):
        devices.add(pid)
        row = grid.setdefault((pid, module), {"pid": pid, "module": module,
                                              "category": cat or "other", "cells": {}})
        cur = row["cells"].get(method)
        if cur is None or RANK.get(state, 0) > RANK.get(cur, 0):
            row["cells"][method] = state
        if (not row["category"] or row["category"] == "other") and cat:
            row["category"] = cat
        # keep one representative xpath, preferring the /prefix:container root form
        if xpath and (not row.get("xpath")
                      or (row["xpath"].startswith("/data/") and not xpath.startswith("/data/"))):
            row["xpath"] = xpath

    # MDT + RESTCONF from browse datasets (data where present)
    for method, fname in (("mdt", "telemetry-live-data.json"),
                          ("restconf", "restconf-live-data.json")):
        f = REPO_ROOT / fname
        if not f.exists():
            continue
        ds = json.loads(f.read_text(encoding="utf-8"))
        for pth in ds.get("paths", []):
            put(pth["pid"], to_module(pth["path"], p2m, m2p), pth.get("category"), method, "data",
                xpath=pth.get("path"))

    # NETCONF get / get-config from raw netconf-<PID>.json
    for f in glob.glob(str(OUT / "netconf-C*.json")):
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        pid = doc["pid"]
        for e in doc.get("entries", []):
            if e.get("status") == "no-namespace":
                continue  # module not present on device -> not applicable
            method = "netconf-getconfig" if e.get("op") == "get-config" else "netconf-get"
            st = {"data": "data", "empty": "ok"}.get(e.get("status"), "no")
            put(pid, entry_module(e, p2m, m2p), e.get("category"), method, st, xpath=e.get("xpath"))

    # NETCONF subscribe from netconf-sub-<PID>.json
    for f in glob.glob(str(OUT / "netconf-sub-*.json")):
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        pid = doc["pid"]
        for e in doc.get("entries", []):
            if e.get("status") == "no-namespace":
                continue
            st = {"streamed": "data", "accepted-nodata": "ok"}.get(e.get("status"), "no")
            put(pid, entry_module(e, p2m, m2p), e.get("category"), "netconf-sub", st, xpath=e.get("xpath"))

    # gNMI get / get-config from gnmi-<PID>.json (excludes gnmi-sub-*)
    for f in glob.glob(str(OUT / "gnmi-C*.json")):
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        pid = doc["pid"]
        for e in doc.get("entries", []):
            op = e.get("op")
            method = {"config": "gnmi-getconfig", "state": "gnmi-state"}.get(op, "gnmi-get")
            st = {"data": "data", "empty": "ok"}.get(e.get("status"), "no")
            put(pid, entry_module(e, p2m, m2p), e.get("category"), method, st, xpath=e.get("xpath"))

    # gNMI subscribe from gnmi-sub-<PID>.json (once support)
    for f in glob.glob(str(OUT / "gnmi-sub-*.json")):
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        pid = doc["pid"]
        for e in doc.get("entries", []):
            st = {"streamed": "data", "accepted-nodata": "ok"}.get(e.get("once"), "no")
            put(pid, entry_module(e, p2m, m2p), e.get("category"), "gnmi-sub", st, xpath=e.get("xpath"))

    return grid, devices


def main() -> int:
    grid, devices = collect()
    rows = sorted(grid.values(), key=lambda r: (r["pid"], r["category"], r["module"]))
    matrix = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "legend": {"data": "returned data", "ok": "supported, no data",
                   "no": "rejected / unsupported"},
        "methods": [{"key": k, "label": l} for k, l in METHODS],
        "devices": sorted(devices),
        "totals": {"modules": len({r["module"] for r in rows}), "rows": len(rows)},
        "rows": rows,
    }
    out = REPO_ROOT / "protocol-matrix.json"
    out.write_text(json.dumps(matrix, separators=(",", ":"), ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"protocol-matrix.json: {len(METHODS)} methods, {len(devices)} devices, "
          f"{matrix['totals']['modules']} modules, {len(rows)} rows "
          f"({out.stat().st_size / 1024:.0f} KB)")
    for k, _ in METHODS:
        c = collections.Counter(r["cells"].get(k) for r in rows)
        print(f"  {k:20} data={c.get('data', 0):4} ok={c.get('ok', 0):4} no={c.get('no', 0):4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
