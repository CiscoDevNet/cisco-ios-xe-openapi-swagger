#!/usr/bin/env python3
"""build_restconf_augment.py — reconcile live-examples-index.json with restconf-live-data.json.

The self-contained RESTCONF collector (restconf_get.py) finds module ROOTS the
harness tree-walk skipped on some devices (MIB on most boxes; ietf/openconfig/
other on the .110 WAN box). Those roots were originally appended straight into
the flat browse dataset (restconf-live-data.json) as per-VALUE example files — a
layout the harness index (one per-PATH file holding every PID's value) cannot
represent, so the canonical builder scripts/build_restconf_dataset.py could not
reproduce them from the index.

This reconciler folds every (PID, path) the dataset has but the index lacks INTO
the index, materialising each body as the harness's per-path file
(releases/<ver>/live-data/<category>/<module>/<sha1(path)[:16]>.json holding every
PID's value). Values are copied verbatim from the collector's existing per-value
files, so no payload changes. After running it, regenerate the flat dataset with
the canonical builder:

    python -X utf8 scripts/mdt-telemetry/collector/build_restconf_augment.py
    python3 scripts/build_restconf_dataset.py

It is idempotent: once the dataset is regenerated from the index the gap is empty
and a re-run is a no-op. The now-orphaned per-value files are no longer referenced
by the regenerated dataset and can be deleted.
"""
from __future__ import annotations

import collections
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
RELEASE = "26.1.1"
RELEASE_DIR = REPO_ROOT / "releases" / RELEASE
INDEX = RELEASE_DIR / "live-examples-index.json"
DATASET = REPO_ROOT / "restconf-live-data.json"


def _module_of(path: str) -> str:
    """Top module name from a browse path (/data/<module>:<container>/...)."""
    s = path.lstrip("/")
    if s.startswith("data/"):
        s = s[len("data/"):]
    head = s.split("/")[0]
    return head.split(":")[0] if ":" in head else head


def _path_hash(path: str) -> str:
    return hashlib.sha1(path.encode("utf-8")).hexdigest()[:16]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _recompute_aggregates(index: dict) -> None:
    """Rebuild devices[]/categories[]/totals{} from modules[] exactly as
    scripts/build_live_examples_index.py does — preserving each category's
    manifest totals and each device's os_version already recorded in the index."""
    os_by_pid = {d["pid"]: d.get("os_version") for d in index.get("devices", [])}
    cat_meta = {c["category"]: c for c in index.get("categories", [])}
    dev: dict = {}
    cat_cap: dict = collections.defaultdict(lambda: {"modules": 0, "paths": 0})
    for m in index["modules"]:
        cat, mod = m["category"], m["module"]
        if m["paths"]:
            cat_cap[cat]["modules"] += 1
            cat_cap[cat]["paths"] += len(m["paths"])
        for p in m["paths"]:
            for pid in p["pids"]:
                d = dev.setdefault(pid, {"modules": set(), "paths": 0})
                d["modules"].add(f"{cat}/{mod}")
                d["paths"] += 1
    index["devices"] = [
        {"pid": pid, "os_version": os_by_pid.get(pid) or RELEASE,
         "modules": len(d["modules"]), "paths": d["paths"]}
        for pid, d in sorted(dev.items())
    ]
    cats = []
    for cat in sorted(cat_meta):
        meta, cap = cat_meta[cat], cat_cap.get(cat, {"modules": 0, "paths": 0})
        cats.append({
            "category": cat,
            "total_modules": meta.get("total_modules", 0),
            "total_paths": meta.get("total_paths", 0),
            "captured_modules": cap["modules"],
            "captured_paths": cap["paths"],
        })
    index["categories"] = cats
    index["totals"] = {
        "devices": len(index["devices"]),
        "total_paths": sum(c["total_paths"] for c in cats),
        "captured_paths": sum(c["captured_paths"] for c in cats),
        "modules_with_data": len(index["modules"]),
    }


def main() -> int:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    ds = json.loads(DATASET.read_text(encoding="utf-8"))

    path2entry: dict = {}          # path -> (module_entry, path_entry)
    covered: set = set()           # (pid, path) already represented in the index
    for m in index["modules"]:
        for p in m["paths"]:
            path2entry[p["path"]] = (m, p)
            for pid in p["pids"]:
                covered.add((pid, p["path"]))
    mod_by_key = {(m["category"], m["module"]): m for m in index["modules"]}

    gap = [e for e in ds["paths"] if (e["pid"], e["path"]) not in covered]
    if not gap:
        print("index already covers the dataset; nothing to do.")
        return 0

    bodies: dict = {}              # rel -> merged per-path doc (write once)
    fetched_ats: list = []
    added: collections.Counter = collections.Counter()
    for e in sorted(gap, key=lambda x: (x["path"], x["pid"])):
        pid, path = e["pid"], e["path"]
        vdoc = json.loads((REPO_ROOT / e["file"]).read_text(encoding="utf-8"))
        val = vdoc["pids"][pid]    # {os_version, fetched_at, http_status, value}

        entry = path2entry.get(path)
        if entry is not None:      # path already indexed (for other PIDs) — add this PID
            m, p = entry
            category, module, rel = m["category"], m["module"], p["file"]
        else:                      # brand-new path — create module/path entries
            category, module = e.get("category", "other"), _module_of(path)
            rel = f"live-data/{category}/{module}/{_path_hash(path)}.json"
            m = mod_by_key.get((category, module))
            if m is None:
                m = {"category": category, "module": module, "pids": [], "paths": []}
                mod_by_key[(category, module)] = m
                index["modules"].append(m)
            p = {"path": path, "file": rel, "pids": {}}
            m["paths"].append(p)
            path2entry[path] = (m, p)

        if rel in bodies:
            doc = bodies[rel]
        else:
            pf = RELEASE_DIR / rel
            doc = (json.loads(pf.read_text(encoding="utf-8")) if pf.exists()
                   else {"path": path, "category": category, "module": module, "pids": {}})
            bodies[rel] = doc
        doc["pids"][pid] = val

        nbytes = len(json.dumps(val["value"], ensure_ascii=False).encode("utf-8"))
        p["pids"][pid] = {"status": val.get("http_status"), "bytes": nbytes}
        if pid not in m["pids"]:
            m["pids"].append(pid)
        if isinstance(val.get("fetched_at"), str) and val["fetched_at"]:
            fetched_ats.append(val["fetched_at"])
        added[pid] += 1

    for rel, doc in bodies.items():
        pf = RELEASE_DIR / rel
        pf.parent.mkdir(parents=True, exist_ok=True)
        pf.write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")

    for m in index["modules"]:
        m["pids"] = sorted(m["pids"])
        m["paths"] = sorted(m["paths"], key=lambda p: p["path"])
    index["modules"] = sorted(index["modules"], key=lambda m: (m["category"], m["module"]))

    _recompute_aggregates(index)
    index["generated_at"] = _now()
    if fetched_ats:
        window = fetched_ats + [t for t in (index.get("captured_from"), index.get("captured_to")) if t]
        index["captured_from"], index["captured_to"] = min(window), max(window)

    INDEX.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"folded {sum(added.values())} (pid,path) into the index ({dict(added)}); "
          f"{len(bodies)} per-path files written/merged.")
    print("now regenerate: python3 scripts/build_restconf_dataset.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
