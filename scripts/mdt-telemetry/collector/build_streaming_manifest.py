#!/usr/bin/env python3
"""build_streaming_manifest.py — distil the one-time exhaustive walk into a
fast re-capture manifest.

The exhaustive walk (walk_all.py) is a *discovery* pass: it tries every
subscribable node one-at-a-time to learn which ones actually stream. That is
slow (~day/device) but only needs to happen once. This script reads the walk
state files (output/walk-<PID>-<flavor>.json) and emits, per device, the list
of xpaths that were observed to STREAM — the known-good set to re-subscribe when
config/topology changes, so a re-capture takes minutes instead of days.

    python3 build_streaming_manifest.py
    -> output/streaming-manifest.json
"""
from __future__ import annotations

import collections
import glob
import json
import os
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
MANIFEST = OUT / "streaming-manifest.json"


def flavor_of(fname: str) -> tuple[str, str]:
    """Return (pid, flavor) from a walk-<pid>-<flavor>.json filename."""
    base = os.path.basename(fname)[len("walk-"):-len(".json")]
    if base.endswith("native-config"):
        return base[:-len("-native-config")], "native-config"
    pid, _, flavor = base.rpartition("-")
    return pid, flavor


def proper_ancestors(xpath: str) -> set[str]:
    """Ancestor xpaths of `xpath` (excluding itself)."""
    parts = xpath.lstrip("/").split("/")
    return {"/" + "/".join(parts[:i]) for i in range(1, len(parts))}


def main() -> int:
    devices: dict[str, dict[str, dict]] = collections.defaultdict(dict)
    for f in sorted(glob.glob(str(OUT / "walk-*-*.json"))):
        pid, flavor = flavor_of(f)
        try:
            state = json.loads(Path(f).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for xpath, info in (state.get("results") or {}).items():
            status = info.get("status") if isinstance(info, dict) else info
            if status == "streamed":
                # first-seen category wins; a path only belongs to one flavor
                devices[pid].setdefault(xpath, flavor)

    dev_entries: dict[str, list] = {}
    roots_total: dict[str, int] = {}
    for pid, paths in sorted(devices.items()):
        streaming = set(paths)
        entries = []
        nroots = 0
        for xp, cat in sorted(paths.items()):
            is_root = not (proper_ancestors(xp) & streaming)  # no streaming parent
            nroots += is_root
            entries.append({"xpath": xp, "category": cat, "root": is_root})
        dev_entries[pid] = entries
        roots_total[pid] = nroots

    manifest = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "exhaustive walk state files (status=streamed)",
        "note": ("known-good streaming xpaths per device; 'root'=True marks the minimal set "
                 "(no streaming parent) that alone yields ~100% subtree coverage for fast re-capture"),
        "devices": dev_entries,
        "totals": {pid: len(dev_entries[pid]) for pid in dev_entries},
        "roots": roots_total,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    total = sum(manifest["totals"].values())
    total_roots = sum(roots_total.values())
    print(f"wrote {MANIFEST.name}: {total:,} streaming xpaths "
          f"({total_roots:,} roots = the fast re-capture set) across {len(devices)} devices")
    for pid in manifest["devices"]:
        by = collections.Counter(e["category"] for e in manifest["devices"][pid])
        print(f"  {pid:14} {manifest['totals'][pid]:5,} streaming  {roots_total[pid]:5,} roots  {dict(by)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
