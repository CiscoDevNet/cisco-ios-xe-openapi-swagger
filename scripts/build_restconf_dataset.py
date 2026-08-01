#!/usr/bin/env python3
"""build_restconf_dataset.py — reshape the default release's RESTCONF
live-examples index into restconf-live-data.json, matching the Device Data page
model (device -> category -> path). The actual GET payloads are fetched lazily
by the page from each per-path example file, so this index stays small.

    python3 scripts/build_restconf_dataset.py
"""
from __future__ import annotations

import collections
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RELEASES = REPO / "releases"
OUTPUT = REPO / "restconf-live-data.json"


def default_release() -> str:
    idx = json.loads((RELEASES / "index.json").read_text(encoding="utf-8"))
    return idx.get("default") or idx["releases"][0]["ver"]


def main() -> int:
    ver = default_release()
    src = json.loads((RELEASES / ver / "live-examples-index.json").read_text(encoding="utf-8"))
    base = f"releases/{ver}/"

    paths = []
    for module in src.get("modules", []):
        category = module.get("category", "other")
        for path_entry in module.get("paths", []):
            path = path_entry.get("path", "")
            example_file = path_entry.get("file", "")
            for pid, info in (path_entry.get("pids") or {}).items():
                paths.append({
                    "pid": pid,
                    "category": category,
                    "path": path,
                    "status": info.get("status"),
                    "bytes": info.get("bytes", 0),
                    "file": base + example_file,
                })

    paths.sort(key=lambda e: (e["pid"], e["category"], e["path"]))

    dev_paths = collections.Counter()
    dev_bytes = collections.Counter()
    dev_cat = collections.defaultdict(collections.Counter)
    cat_paths = collections.Counter()
    for entry in paths:
        dev_paths[entry["pid"]] += 1
        dev_bytes[entry["pid"]] += entry["bytes"] or 0
        dev_cat[entry["pid"]][entry["category"]] += 1
        cat_paths[entry["category"]] += 1

    devices = [{
        "pid": pid,
        "source": "",
        "paths": dev_paths[pid],
        "records": dev_paths[pid],
        "bytes": dev_bytes[pid],
        "by_category": dict(dev_cat[pid]),
    } for pid in sorted(dev_paths)]
    categories = [{"category": c, "paths": cat_paths[c]} for c in sorted(cat_paths)]

    dataset = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "transport": "RESTCONF GET (HTTPS)",
        "source": "live device capture (RESTCONF GET)",
        "release": ver,
        "base": base,
        "totals": {
            "devices": len(devices),
            "paths": len(paths),
            "records": len(paths),
        },
        "devices": devices,
        "categories": categories,
        "paths": paths,
    }

    OUTPUT.write_text(json.dumps(dataset, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    kb = OUTPUT.stat().st_size / 1024
    print(f"release={ver} devices={len(devices)} paths={len(paths)} -> {OUTPUT.name} ({kb:.1f} KB)")
    for d in devices:
        print(f"  {d['pid']:14} paths={d['paths']:5} {d['by_category']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
