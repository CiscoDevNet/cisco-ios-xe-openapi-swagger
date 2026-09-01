#!/usr/bin/env python3
"""build_restconf_augment.py — fill missing module roots in restconf-live-data.json.

The RESTCONF browse dataset (restconf-live-data.json) is produced by the harness
tree-walk, which on several devices skipped whole flavors (MIB on most boxes;
ietf/openconfig/other on the .110 WAN box). This augments that browse dataset
with the depth-1 module ROOTS that the self-contained collector
(output/restconf-<PID>.json, written by restconf_get.py) found and the walk
missed, so every RESTCONF-served module appears in the browse tab.

Only modules ENTIRELY ABSENT from a device's browse paths are added (existing
deep paths are preserved), so re-running is idempotent. Payload values are
redacted (redact_payload) and written as per-path example files matching the
harness layout: releases/<ver>/live-data/<category>/<module>/<sha1[:16]>.json
shaped {path, category, module, pids:{PID:{os_version,fetched_at,http_status,value}}}.

    python -X utf8 build_restconf_augment.py
"""
from __future__ import annotations

import collections
import glob
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from redact_payload import redact_obj, redact_payload

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
REPO_ROOT = HERE.parents[2]
DATASET = REPO_ROOT / "restconf-live-data.json"
RELEASE = "26.1.1"
LIVE_DATA = REPO_ROOT / "releases" / RELEASE / "live-data"
BASE = f"releases/{RELEASE}/"
OS_VERSION = RELEASE


def _module_of(path: str) -> str:
    """Top module name from a browse path (/data/<module>:<container>/...)."""
    s = path.lstrip("/")
    if s.startswith("data/"):
        s = s[len("data/"):]
    head = s.split("/")[0]
    return head.split(":")[0] if ":" in head else head


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _redacted_value(payload: str):
    """Parsed + redacted JSON value; falls back to a redacted string if the
    stored payload was truncated (restconf_get caps at 200K) and won't parse."""
    try:
        return redact_obj(json.loads(payload))
    except (json.JSONDecodeError, TypeError):
        return redact_payload(payload)


def _write_example(pid: str, category: str, module: str, browse_path: str, value) -> str:
    """Write/merge a per-path example file; return its repo-relative path."""
    canon = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    sha = hashlib.sha1(canon.encode("utf-8")).hexdigest()[:16]
    rel = f"{BASE}live-data/{category}/{module}/{sha}.json"
    fpath = REPO_ROOT / rel
    if fpath.exists():  # identical value already captured (possibly for another PID) — merge
        doc = json.loads(fpath.read_text(encoding="utf-8"))
    else:
        fpath.parent.mkdir(parents=True, exist_ok=True)
        doc = {"path": browse_path, "category": category, "module": module, "pids": {}}
    doc["pids"][pid] = {"os_version": OS_VERSION, "fetched_at": _now(),
                        "http_status": 200, "value": value}
    fpath.write_text(json.dumps(doc, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    return rel


def main() -> int:
    ds = json.loads(DATASET.read_text(encoding="utf-8"))
    paths = ds.get("paths", [])

    present = collections.defaultdict(set)  # pid -> {module}
    for p in paths:
        present[p["pid"]].add(_module_of(p["path"]))

    added = 0
    by_dev = collections.Counter()
    for f in sorted(glob.glob(str(OUT / "restconf-*.json"))):
        doc = json.loads(Path(f).read_text(encoding="utf-8"))
        pid = doc["pid"]
        for e in doc.get("entries", []):
            if e.get("status") != "data":
                continue
            module = e.get("module") or ""
            if not module or module in present[pid]:
                continue  # already in browse dataset (as a root or deeper path)
            present[pid].add(module)  # de-dupe within this run too
            category = e.get("category", "other")
            browse_path = "/data" + e["rc_path"]
            value = _redacted_value(e.get("payload") or "")
            rel = _write_example(pid, category, module, browse_path, value)
            paths.append({"pid": pid, "category": category, "path": browse_path,
                          "status": 200, "bytes": e.get("bytes", 0), "file": rel})
            added += 1
            by_dev[pid] += 1

    paths.sort(key=lambda e: (e["pid"], e["category"], e["path"]))

    dev_paths = collections.Counter()
    dev_bytes = collections.Counter()
    dev_cat = collections.defaultdict(collections.Counter)
    cat_paths = collections.Counter()
    for e in paths:
        dev_paths[e["pid"]] += 1
        dev_bytes[e["pid"]] += e.get("bytes", 0) or 0
        dev_cat[e["pid"]][e["category"]] += 1
        cat_paths[e["category"]] += 1

    ds["generated"] = _now()
    ds["devices"] = [{"pid": pid, "source": "", "paths": dev_paths[pid],
                      "records": dev_paths[pid], "bytes": dev_bytes[pid],
                      "by_category": dict(dev_cat[pid])} for pid in sorted(dev_paths)]
    ds["categories"] = [{"category": c, "paths": cat_paths[c]} for c in sorted(cat_paths)]
    ds["totals"] = {"devices": len(ds["devices"]), "paths": len(paths), "records": len(paths)}
    ds["paths"] = paths

    DATASET.write_text(json.dumps(ds, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"restconf-live-data.json: +{added} module roots ({dict(by_dev)}) -> {len(paths)} paths "
          f"({DATASET.stat().st_size/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
