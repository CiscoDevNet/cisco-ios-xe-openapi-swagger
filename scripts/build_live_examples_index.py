#!/usr/bin/env python3
"""
build_live_examples_index.py — Emit a lightweight, committable index of the
real captured device responses (``x-cisco-live-examples``) for one release.

The interactive Live Data page (live-data.html / live-data.js) uses this index
for coverage stats and navigation WITHOUT downloading every spec: it lists each
captured module/path and which device PIDs have data (plus http status + byte
size), but NOT the response bodies. The page fetches the single per-module spec
on demand when the user drills into a path, so this index stays small.

Reads the committed release specs
(``releases/<ver>/swagger-<cat>-model/api/*.json``) and their manifests, then
writes ``releases/<ver>/live-examples-index.json``.

Additive build artifact; does not change any spec or affect API counts.

Usage:
    python scripts/build_live_examples_index.py --version 26.1.1
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# swagger model dir -> short category label used by the harness / UI.
MODEL_CATEGORY = {
    "swagger-oper-model": "oper",
    "swagger-cfg-model": "cfg",
    "swagger-native-config-model": "native-config",
    "swagger-openconfig-model": "openconfig",
    "swagger-ietf-model": "ietf",
    "swagger-mib-model": "mib",
    "swagger-other-model": "other",
    "swagger-rpc-model": "rpc",
}
LIVE_KEY = "x-cisco-live-examples"


def _iter_spec_files(api_dir: Path):
    for f in sorted(api_dir.glob("*.json")):
        name = f.name
        if name == "manifest.json" or name.startswith("_"):
            continue
        yield f


def _live_on_operation(op: dict):
    """Return the x-cisco-live-examples dict on a GET 200 media type, or None."""
    if not isinstance(op, dict):
        return None
    responses = op.get("responses") or {}
    resp = responses.get("200") or responses.get("default")
    if not isinstance(resp, dict):
        return None
    content = resp.get("content")
    if not isinstance(content, dict):
        return None
    for media in content.values():
        if isinstance(media, dict) and isinstance(media.get(LIVE_KEY), dict):
            return media[LIVE_KEY]
    return None


def build_index(version: str) -> dict:
    release_dir = PROJECT_ROOT / "releases" / version
    categories = []
    modules_out = []
    device_stats: dict[str, dict] = {}
    os_version = version

    for model_dir, category in MODEL_CATEGORY.items():
        api_dir = release_dir / model_dir / "api"
        if not api_dir.is_dir():
            continue
        manifest_path = api_dir / "manifest.json"
        total_modules = total_paths = 0
        if manifest_path.is_file():
            try:
                man = json.loads(manifest_path.read_text(encoding="utf-8"))
                total_modules = int(man.get("total_modules") or 0)
                total_paths = int(man.get("total_paths") or 0)
            except (json.JSONDecodeError, ValueError):
                pass

        cat_captured_modules = 0
        cat_captured_paths = 0
        for spec_file in _iter_spec_files(api_dir):
            try:
                spec = json.loads(spec_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            module = spec_file.stem
            paths_out = []
            module_pids: set[str] = set()
            for path, item in (spec.get("paths") or {}).items():
                if not isinstance(item, dict):
                    continue
                live = _live_on_operation(item.get("get"))
                if not live:
                    continue
                pid_map = {}
                for pid, entry in live.items():
                    if not isinstance(entry, dict):
                        continue
                    value_bytes = len(
                        json.dumps(entry.get("value"), ensure_ascii=False).encode("utf-8")
                    )
                    pid_map[pid] = {
                        "status": entry.get("http_status"),
                        "bytes": value_bytes,
                    }
                    module_pids.add(pid)
                    ds = device_stats.setdefault(
                        pid,
                        {"pid": pid, "os_version": entry.get("os_version") or version,
                         "modules": set(), "paths": 0},
                    )
                    ds["modules"].add(f"{category}/{module}")
                    ds["paths"] += 1
                if pid_map:
                    paths_out.append({"path": path, "pids": pid_map})
            if paths_out:
                cat_captured_modules += 1
                cat_captured_paths += len(paths_out)
                modules_out.append({
                    "category": category,
                    "module": module,
                    "pids": sorted(module_pids),
                    "paths": sorted(paths_out, key=lambda p: p["path"]),
                })

        categories.append({
            "category": category,
            "total_modules": total_modules,
            "total_paths": total_paths,
            "captured_modules": cat_captured_modules,
            "captured_paths": cat_captured_paths,
        })

    devices = [
        {
            "pid": d["pid"],
            "os_version": d["os_version"],
            "modules": len(d["modules"]),
            "paths": d["paths"],
        }
        for d in sorted(device_stats.values(), key=lambda d: d["pid"])
    ]

    total_paths = sum(c["total_paths"] for c in categories)
    captured_paths = sum(c["captured_paths"] for c in categories)
    return {
        "version": version,
        "os_version": os_version,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "devices": devices,
        "categories": sorted(categories, key=lambda c: c["category"]),
        "totals": {
            "devices": len(devices),
            "total_paths": total_paths,
            "captured_paths": captured_paths,
            "modules_with_data": len(modules_out),
        },
        "modules": sorted(modules_out, key=lambda m: (m["category"], m["module"])),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--version", required=True)
    ap.add_argument("--out", help="Output path (default releases/<ver>/live-examples-index.json)")
    args = ap.parse_args()

    release_dir = PROJECT_ROOT / "releases" / args.version
    if not release_dir.is_dir():
        print(f"[live-index] no release dir {release_dir}; nothing to do.")
        return 0

    index = build_index(args.version)
    out = Path(args.out) if args.out else (release_dir / "live-examples-index.json")
    out.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    t = index["totals"]
    print(f"[live-index] {out}")
    print(f"  {t['modules_with_data']} modules, {t['captured_paths']} captured paths, "
          f"{t['devices']} device(s): {', '.join(d['pid'] for d in index['devices']) or '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
