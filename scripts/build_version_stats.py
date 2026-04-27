#!/usr/bin/env python3
"""
build_version_stats.py — Per-release rollup of API path/operation/spec counts.

Walks every release's swagger-*-model/api-v2/*.json files and writes
``cisco-ios-xe-openapi-swagger/version-stats.json`` consumed by the home page
summary table and the cross-version comparison view, so users can see how
coverage has grown release-over-release.

Output schema:
    {
      "generated": "<iso8601>",
      "default_version": "26.1.1",
      "versions": ["26.1.1", "17.18.1", ...],   # in releases/index.json order
      "totals": {
        "<ver>": {
          "specs": int, "paths": int, "operations": int,
          "modules_total": int, "modules_with_specs": int,
          "modules_with_trees": int
        }, ...
      },
      "categories": {
        "<ver>": {
          "swagger-oper-model": { "specs": ..., "paths": ..., "operations": ... },
          ...
        }, ...
      }
    }

Usage:
    python scripts/build_version_stats.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _release_paths import (  # type: ignore  # noqa: E402
    PROJECT_ROOT,
    MODEL_CATEGORIES,
    ReleasePaths,
    all_releases,
)

OP_METHODS = ("get", "post", "put", "patch", "delete")


def _scan_category(spec_dir: Path) -> dict:
    """Return {specs, paths, operations} for one swagger-<cat>-model/api-v2 dir."""
    if not spec_dir.is_dir():
        return {"specs": 0, "paths": 0, "operations": 0}
    specs = paths = ops = 0
    for f in sorted(spec_dir.glob("*.json")):
        if f.name == "manifest.json":
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        specs += 1
        spec_paths = data.get("paths") or {}
        paths += len(spec_paths)
        for ops_obj in spec_paths.values():
            if not isinstance(ops_obj, dict):
                continue
            for m in OP_METHODS:
                if m in ops_obj:
                    ops += 1
    return {"specs": specs, "paths": paths, "operations": ops}


def _module_counts(version: str) -> dict:
    """Read accountability_json + tree_audit_json to recover per-version
    module totals. Returns zeros when the files don't exist (e.g. an empty
    release scaffold)."""
    rp = ReleasePaths(version=version, legacy=True)
    acc_path = rp.accountability_json()
    out = {
        "modules_total": 0, "modules_with_specs": 0, "modules_with_trees": 0,
        "yang_modules": 0, "mib_modules": 0,
        "yang_tree_files": 0, "mib_tree_files": 0, "total_tree_files": 0,
        "modules_excluded": 0, "spec_only_modules": 0,
    }
    if not acc_path.is_file():
        return out
    try:
        d = json.loads(acc_path.read_text(encoding="utf-8"))
    except Exception:
        return out
    out["modules_total"] = int(d.get("total_modules") or 0)
    out["modules_with_specs"] = int(d.get("modules_with_specs") or 0)
    out["modules_with_trees"] = int(d.get("modules_with_trees") or 0)
    mib_modules = mib_with_trees = excluded = 0
    for m in d.get("modules") or []:
        cls = (m.get("classification") or "").lower()
        has_tree = bool(m.get("tree_url"))
        if cls == "mib":
            mib_modules += 1
            if has_tree:
                mib_with_trees += 1
        if m.get("reason_excluded"):
            excluded += 1
    out["mib_modules"] = mib_modules
    out["yang_modules"] = max(out["modules_total"] - mib_modules, 0)
    out["mib_tree_files"] = mib_with_trees
    out["yang_tree_files"] = max(out["modules_with_trees"] - mib_with_trees, 0)
    out["total_tree_files"] = out["modules_with_trees"]
    out["modules_excluded"] = excluded
    out["spec_only_modules"] = max(out["modules_total"] - out["modules_with_trees"], 0)
    return out


def main() -> int:
    rels = all_releases()
    if not rels:
        print("[version-stats] releases/index.json missing or empty.", file=sys.stderr)
        return 1

    default_version = next((r["ver"] for r in rels if r.get("default")), rels[0]["ver"])
    versions = [r["ver"] for r in rels]

    totals: dict[str, dict] = {}
    categories: dict[str, dict] = {}

    for r in rels:
        v = r["ver"]
        rp = ReleasePaths(version=v, legacy=True)
        cat_stats: dict[str, dict] = {}
        sum_specs = sum_paths = sum_ops = 0
        for cat in MODEL_CATEGORIES:
            spec_dir = rp.spec_dir(cat)
            s = _scan_category(spec_dir)
            cat_stats[cat] = s
            sum_specs += s["specs"]
            sum_paths += s["paths"]
            sum_ops += s["operations"]
        totals[v] = {
            "specs": sum_specs,
            "paths": sum_paths,
            "operations": sum_ops,
            **_module_counts(v),
            "label": r.get("label") or v,
            "date": r.get("date") or "",
            "status": r.get("status") or "",
        }
        categories[v] = cat_stats

    out = {
        "generated": datetime.now(timezone.utc).replace(microsecond=0)
            .isoformat().replace("+00:00", "Z"),
        "default_version": default_version,
        "versions": versions,
        "totals": totals,
        "categories": categories,
    }
    target = PROJECT_ROOT / "version-stats.json"
    target.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"[version-stats] wrote {target.relative_to(PROJECT_ROOT)}")
    print(f"{'version':<12} {'specs':>6} {'paths':>8} {'ops':>8}  modules: total/specs/trees")
    print("-" * 78)
    for v in versions:
        t = totals[v]
        mc = f"{t['modules_total']}/{t['modules_with_specs']}/{t['modules_with_trees']}"
        print(f"{v:<12} {t['specs']:>6} {t['paths']:>8} {t['operations']:>8}  {mc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
