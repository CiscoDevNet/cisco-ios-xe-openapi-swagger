#!/usr/bin/env python3
"""
build_accountability_compare.py — Cross-release accountability comparison matrix.

Reads each release's ``yang_accountability.json`` and produces a unified comparison
view at ``cisco-ios-xe-openapi-swagger/accountability_compare.json`` consumed by
``yang-accountability-compare.html``.

Per VERSIONING.md §9 gate 8 and PROJECT_REQUIREMENTS.md §16.3.

Usage:
    python scripts/build_accountability_compare.py
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _release_paths import PROJECT_ROOT, ReleasePaths, all_releases  # type: ignore  # noqa: E402


def load_accountability(version: str) -> dict | None:
    rp = ReleasePaths(version=version, legacy=True)
    p = rp.accountability_json()
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def normalize_modules(data: dict) -> dict[str, dict]:
    """Produce module_name → {has_spec, has_tree, category, status}."""
    out: dict[str, dict] = {}
    for entry in data.get("modules", []) or []:
        name = entry.get("name") or entry.get("module")
        if not name:
            continue
        out[name] = {
            "has_spec": bool(entry.get("swaggerUrl") or entry.get("has_spec")),
            "has_tree": bool(entry.get("yangTreeUrl") or entry.get("has_tree")),
            "category": entry.get("category") or entry.get("displayCategory") or "",
            "status": entry.get("status", "documented"),
        }
    for entry in data.get("excluded_modules", []) or []:
        name = entry.get("name") or entry.get("module")
        if not name:
            continue
        out.setdefault(name, {})
        out[name].update({
            "has_spec": False,
            "status": "excluded",
            "exclusion_reason": entry.get("reason", "excluded"),
        })
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--versions", default="",
                   help="Comma-separated list of versions to include (default: all "
                        "from releases/index.json)")
    args = p.parse_args()

    if args.versions:
        versions = [v.strip() for v in args.versions.split(",") if v.strip()]
    else:
        versions = [r["ver"] for r in all_releases()]

    per_version: dict[str, dict] = {}
    summary: dict[str, dict] = {}
    all_modules: set[str] = set()

    for v in versions:
        data = load_accountability(v)
        if not data:
            print(f"[compare] {v}: no accountability data, skipping.")
            continue
        norm = normalize_modules(data)
        per_version[v] = norm
        all_modules.update(norm.keys())
        summary[v] = {
            "total_modules": data.get("total_modules", len(norm)),
            "with_specs": data.get("modules_with_specs",
                                   sum(1 for m in norm.values() if m.get("has_spec"))),
            "with_trees": data.get("modules_with_trees",
                                   sum(1 for m in norm.values() if m.get("has_tree"))),
            "ios_xe_version": data.get("ios_xe_version") or v,
            "generated": data.get("generated"),
        }

    matrix: list[dict] = []
    for module in sorted(all_modules):
        row = {"module": module, "by_version": {}}
        for v in per_version:
            entry = per_version[v].get(module)
            if not entry:
                row["by_version"][v] = {"present": False}
            else:
                row["by_version"][v] = {
                    "present": True,
                    "has_spec": entry.get("has_spec", False),
                    "has_tree": entry.get("has_tree", False),
                    "status": entry.get("status", ""),
                    "category": entry.get("category", ""),
                }
        matrix.append(row)

    # Compute deltas (added/removed between consecutive versions in input order)
    deltas: list[dict] = []
    ordered = list(per_version.keys())
    for i in range(1, len(ordered)):
        prev, cur = ordered[i - 1], ordered[i]
        added = sorted(set(per_version[cur]) - set(per_version[prev]))
        removed = sorted(set(per_version[prev]) - set(per_version[cur]))
        deltas.append({"from": prev, "to": cur,
                       "added": added, "added_count": len(added),
                       "removed": removed, "removed_count": len(removed)})

    out = {
        "generated": datetime.now(timezone.utc).replace(microsecond=0)
            .isoformat().replace("+00:00", "Z"),
        "versions": list(per_version.keys()),
        "summary": summary,
        "deltas": deltas,
        "matrix": matrix,
    }
    target = PROJECT_ROOT / "accountability_compare.json"
    target.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"[compare] wrote {target.relative_to(PROJECT_ROOT)}")
    print(f"[compare] versions={len(per_version)} modules-tracked={len(all_modules)}")
    for v, s in summary.items():
        print(f"           {v}: total={s['total_modules']} specs={s['with_specs']} "
              f"trees={s['with_trees']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
