#!/usr/bin/env python3
"""build_protocol_matrix.py — cross-protocol comparison grid.

Reads every transport dataset and, per (device, YANG module), records which
access methods returned data (and how much). Output protocol-matrix.json powers
the Device Data comparison view: rows = modules, columns = methods, cell = bytes
(or blank if that method returned nothing / doesn't support it).

Common key = the YANG module name, mapped from each method's path form
(RESTCONF/gNMI use the module name; MDT/NETCONF catalog xpaths use the YANG
prefix -> converted via yang-prefix-map).
"""
from __future__ import annotations

import collections
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
PREFIX_MAP = REPO_ROOT / "yang-prefix-map.json"

SOURCES = [
    ("mdt", "telemetry-live-data.json", "MDT periodic"),
    ("restconf", "restconf-live-data.json", "RESTCONF GET"),
    ("netconf-get", "netconf-get-live-data.json", "NETCONF get"),
    ("netconf-getconfig", "netconf-getconfig-live-data.json", "NETCONF get-config"),
    ("netconf-sub", "netconf-sub-live-data.json", "NETCONF subscribe"),
    ("gnmi-get", "gnmi-get-live-data.json", "gNMI Get"),
    ("gnmi-getconfig", "gnmi-getconfig-live-data.json", "gNMI Get config"),
    ("gnmi-sub", "gnmi-sub-live-data.json", "gNMI Subscribe ONCE"),
]


def prefix_to_module():
    try:
        data = json.loads(PREFIX_MAP.read_text(encoding="utf-8"))
        return {p: m for m, p in (data.get("modules") or {}).items()}
    except (json.JSONDecodeError, OSError):
        return {}


def to_module(path: str, p2m: dict) -> str:
    p = path.lstrip("/")
    if p.startswith("data/"):
        p = p[len("data/"):]  # RESTCONF /data/
    seg = p.split("/")[0]
    tok = seg.split(":")[0]
    return p2m.get(tok, tok)  # prefix -> module; already-module passes through


def main() -> int:
    p2m = prefix_to_module()
    methods = []
    # cell[(pid, module)] = {"category": c, "cells": {method: bytes}}
    grid: dict[tuple, dict] = {}
    devices = set()
    for key, fname, label in SOURCES:
        f = REPO_ROOT / fname
        if not f.exists():
            continue
        methods.append({"key": key, "label": label})
        ds = json.loads(f.read_text(encoding="utf-8"))
        agg = collections.defaultdict(lambda: [0, ""])  # (pid,module) -> [bytes, category]
        for pth in ds.get("paths", []):
            pid = pth["pid"]
            devices.add(pid)
            module = to_module(pth["path"], p2m)
            b = pth.get("bytes") or pth.get("records") or 0
            agg[(pid, module)][0] += b
            agg[(pid, module)][1] = pth.get("category", "other")
        for (pid, module), (b, cat) in agg.items():
            row = grid.setdefault((pid, module), {"pid": pid, "module": module, "category": cat, "cells": {}})
            row["cells"][key] = b
            if not row["category"]:
                row["category"] = cat

    rows = sorted(grid.values(), key=lambda r: (r["pid"], r["category"], r["module"]))
    matrix = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "methods": methods,
        "devices": sorted(devices),
        "totals": {"modules": len({r["module"] for r in rows}), "rows": len(rows)},
        "rows": rows,
    }
    out = REPO_ROOT / "protocol-matrix.json"
    out.write_text(json.dumps(matrix, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"protocol-matrix.json: {len(methods)} methods, {len(devices)} devices, "
          f"{matrix['totals']['modules']} modules, {len(rows)} rows ({out.stat().st_size/1024:.0f} KB)")
    # quick method coverage summary
    for m in methods:
        n = sum(1 for r in rows if r["cells"].get(m["key"]))
        print(f"  {m['key']:20} data rows: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
