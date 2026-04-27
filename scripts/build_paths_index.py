#!/usr/bin/env python3
"""Build per-category _paths_index.json files for the cross-chunk operation
search feature in the Swagger viewers.

Runs for every active release. Each viewer's paths-search.js IIFE is gated
on __IOSXE_ACTIVE_VERSION__ so users see the wider search surface on the
release they are currently browsing.

Output schema (one file per category, written next to the v2 specs).
Entries are deduplicated to one row per (spec, path); HTTP methods and the
operationId for each method are kept as parallel arrays. Short keys are
used to keep the JSON small enough to fetch on viewer load.

    {
      "v": "26.1.1",
      "c": "native-config",
      "n": 4900,
      "ops": [
        {"s": "native-interfaces",
         "p": "/data/Cisco-IOS-XE-native:native/vlan",
         "t": "vlan",
         "sm": "Get vlan",
         "ms": ["get","put","patch","delete"],
         "ids": ["get-native-vlan","put-native-vlan",
                 "patch-native-vlan","delete-native-vlan"]},
        ...
      ]
    }
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CATEGORIES = (
    "cfg",
    "events",
    "ietf",
    "mib",
    "native-config",
    "openconfig",
    "oper",
    "other",
    "rpc",
)
HTTP_METHODS = ("get", "put", "post", "patch", "delete", "head", "options")


def build_one(api_dir: Path, version: str, category: str) -> int:
    rows: list[dict] = []
    for spec_path in sorted(api_dir.glob("*.json")):
        if spec_path.name in ("manifest.json", "_paths_index.json"):
            continue
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            print(f"  ! skip {spec_path.name}: {exc}", file=sys.stderr)
            continue
        spec_name = spec_path.stem
        paths = spec.get("paths") or {}
        for raw_path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            ms: list[str] = []
            ids: list[str] = []
            tag = ""
            summary = ""
            for method, op in methods.items():
                m = method.lower()
                if m not in HTTP_METHODS or not isinstance(op, dict):
                    continue
                ms.append(m)
                ids.append(op.get("operationId") or "")
                if not tag:
                    tags = op.get("tags") or []
                    if tags and isinstance(tags, list):
                        tag = str(tags[0])
                if not summary:
                    summary = op.get("summary") or ""
            if not ms:
                continue
            rows.append({
                "s": spec_name,
                "p": raw_path,
                "t": tag,
                "sm": summary,
                "ms": ms,
                "ids": ids,
            })

    out = {
        "v": version,
        "c": category,
        "n": len(rows),
        "ops": rows,
    }
    out_path = api_dir / "_paths_index.json"
    out_path.write_text(
        json.dumps(out, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    return len(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", default="26.1.1",
                    help="Release version to index.")
    ap.add_argument("--root", default=".",
                    help="Repo root containing the releases/ directory.")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    base = root / "releases" / args.version
    if not base.is_dir():
        print(f"[build_paths_index] ERROR: {base} not found", file=sys.stderr)
        return 1

    print(f"[build_paths_index] {args.version}")
    grand_total = 0
    for cat in CATEGORIES:
        api_dir = base / f"swagger-{cat}-model" / "api-v2"
        if not api_dir.is_dir():
            print(f"  - {cat:14s}  MISSING ({api_dir.relative_to(root)})")
            continue
        n = build_one(api_dir, args.version, cat)
        grand_total += n
        print(f"  + {cat:14s}  {n:>6d} paths        -> {api_dir.relative_to(root)}/_paths_index.json")
    print(f"[build_paths_index] DONE  total paths indexed: {grand_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
