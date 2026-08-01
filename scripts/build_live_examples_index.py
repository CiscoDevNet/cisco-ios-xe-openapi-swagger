#!/usr/bin/env python3
"""
build_live_examples_index.py — Emit the committable data the interactive Live
Data page (device-data.html / device-data.js) needs, WITHOUT putting any response
bodies into the OpenAPI specs (which keeps the specs lean and the Swagger
viewers fast).

Two outputs, both under ``releases/<ver>/``:

  * ``live-examples-index.json`` — a small index: per-category coverage, the
    device PIDs, and for every captured path which PIDs have data (http status +
    byte size) plus the relative ``file`` where the real body lives. NO bodies.

  * ``live-data/<category>/<module>/<hash>.json`` — one small file per captured
    path holding the real GET response body per PID. The page fetches only the
    single file for the path the user drills into, so nothing heavy loads up
    front and the specs stay lean.

Source of truth is the gitignored sidecar
``references/live-examples-<ver>.json`` (built by
``scripts/harness/build_observed_examples.py --sidecar`` from the local
captures). When the sidecar is absent (e.g. CI), this is a no-op and the
already-committed index + data files are used as-is.

Usage:
    python scripts/build_live_examples_index.py --version 26.1.1
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.harness.redact import redact

# harness category label -> swagger model dir (for per-category totals).
CATEGORY_MODEL = {
    "oper": "swagger-oper-model",
    "cfg": "swagger-cfg-model",
    "native-config": "swagger-native-config-model",
    "openconfig": "swagger-openconfig-model",
    "ietf": "swagger-ietf-model",
    "mib": "swagger-mib-model",
    "other": "swagger-other-model",
    "rpc": "swagger-rpc-model",
}


def _path_hash(path: str) -> str:
    return hashlib.sha1(path.encode("utf-8")).hexdigest()[:16]


def _category_totals(release_dir: Path) -> dict:
    """Per-category total module/path counts from the release manifests."""
    totals = {}
    for category, model_dir in CATEGORY_MODEL.items():
        man = release_dir / model_dir / "api" / "manifest.json"
        tm = tp = 0
        if man.is_file():
            try:
                d = json.loads(man.read_text(encoding="utf-8"))
                tm = int(d.get("total_modules") or 0)
                tp = int(d.get("total_paths") or 0)
            except (json.JSONDecodeError, ValueError):
                pass
        totals[category] = {"total_modules": tm, "total_paths": tp}
    return totals


def build(version: str):
    release_dir = PROJECT_ROOT / "releases" / version
    sidecar_path = PROJECT_ROOT / "references" / f"live-examples-{version}.json"
    if not sidecar_path.is_file():
        print(f"[live-index] no sidecar at {sidecar_path}; nothing to do.")
        return None

    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    entries = sidecar.get("entries") or []

    # Fresh live-data tree so stale per-path files are removed.
    live_dir = release_dir / "live-data"
    if live_dir.exists():
        shutil.rmtree(live_dir)

    cat_totals = _category_totals(release_dir)

    # Group entries by (category, module).
    by_module = OrderedDict()
    for e in entries:
        by_module.setdefault((e.get("category"), e.get("module")), []).append(e)

    modules_out = []
    device_stats: dict = {}
    cat_captured = {c: {"modules": 0, "paths": 0} for c in CATEGORY_MODEL}
    fetched_ats: list = []

    for (category, module), es in sorted(by_module.items()):
        paths_out = []
        module_pids: set = set()
        for e in es:
            path = e.get("path")
            pids = e.get("pids") or {}
            if not path or not pids:
                continue
            rel = f"live-data/{category}/{module}/{_path_hash(path)}.json"

            data_pids = {}
            index_pids = {}
            for pid, entry in pids.items():
                if not isinstance(entry, dict):
                    continue
                value = entry.get("value")
                # Re-scrub at publish time so the committed data files never
                # carry a secret, even if the capture predates a redaction fix.
                value = redact(value)
                nbytes = len(json.dumps(value, ensure_ascii=False).encode("utf-8"))
                data_pids[pid] = {
                    "os_version": entry.get("os_version"),
                    "fetched_at": entry.get("fetched_at"),
                    "http_status": entry.get("http_status"),
                    "value": value,
                }
                index_pids[pid] = {"status": entry.get("http_status"), "bytes": nbytes}
                module_pids.add(pid)
                fa = entry.get("fetched_at")
                if isinstance(fa, str) and fa:
                    fetched_ats.append(fa)
                ds = device_stats.setdefault(
                    pid,
                    {"pid": pid, "os_version": entry.get("os_version") or version,
                     "modules": set(), "paths": 0},
                )
                ds["modules"].add(f"{category}/{module}")
                ds["paths"] += 1
            if not index_pids:
                continue
            out_file = release_dir / rel
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(
                json.dumps({"path": path, "category": category, "module": module,
                            "pids": data_pids}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            paths_out.append({"path": path, "file": rel, "pids": index_pids})

        if paths_out:
            cat_captured[category]["modules"] += 1
            cat_captured[category]["paths"] += len(paths_out)
            modules_out.append({
                "category": category,
                "module": module,
                "pids": sorted(module_pids),
                "paths": sorted(paths_out, key=lambda p: p["path"]),
            })

    categories = []
    for category in sorted(CATEGORY_MODEL):
        tot = cat_totals.get(category, {"total_modules": 0, "total_paths": 0})
        cap = cat_captured[category]
        categories.append({
            "category": category,
            "total_modules": tot["total_modules"],
            "total_paths": tot["total_paths"],
            "captured_modules": cap["modules"],
            "captured_paths": cap["paths"],
        })

    devices = [
        {"pid": d["pid"], "os_version": d["os_version"],
         "modules": len(d["modules"]), "paths": d["paths"]}
        for d in sorted(device_stats.values(), key=lambda d: d["pid"])
    ]

    index = {
        "version": version,
        "os_version": sidecar.get("os_version") or version,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "captured_from": min(fetched_ats) if fetched_ats else None,
        "captured_to": max(fetched_ats) if fetched_ats else None,
        "devices": devices,
        "categories": categories,
        "totals": {
            "devices": len(devices),
            "total_paths": sum(c["total_paths"] for c in categories),
            "captured_paths": sum(c["captured_paths"] for c in categories),
            "modules_with_data": len(modules_out),
        },
        "modules": sorted(modules_out, key=lambda m: (m["category"], m["module"])),
    }
    (release_dir / "live-examples-index.json").write_text(
        json.dumps(index, indent=2) + "\n", encoding="utf-8")

    # Tiny per-release summary for the viewer discovery banner (module -> pids +
    # path count). Kept small so the Swagger viewers stay fast; the full index
    # and the bodies are only fetched by the Live Data page on demand.
    modules_summary = {
        m["module"]: {"category": m["category"], "pids": m["pids"], "paths": len(m["paths"])}
        for m in modules_out
    }
    (release_dir / "live-modules.json").write_text(
        json.dumps({
            "version": version,
            "os_version": index["os_version"],
            "devices": {d["pid"]: d["os_version"] for d in devices},
            "modules": modules_summary,
        }, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return index


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--version", required=True)
    args = ap.parse_args()

    release_dir = PROJECT_ROOT / "releases" / args.version
    if not release_dir.is_dir():
        print(f"[live-index] no release dir {release_dir}; nothing to do.")
        return 0

    index = build(args.version)
    if index is None:
        return 0
    t = index["totals"]
    print(f"[live-index] releases/{args.version}/live-examples-index.json "
          f"+ per-path files under releases/{args.version}/live-data/")
    print(f"  {t['modules_with_data']} modules, {t['captured_paths']} captured paths, "
          f"{t['devices']} device(s): {', '.join(d['pid'] for d in index['devices']) or '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
