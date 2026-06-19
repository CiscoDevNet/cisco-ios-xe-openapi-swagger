#!/usr/bin/env python3
"""
build_version_stats.py — Per-release rollup of API path/operation/spec counts.

Walks every release's swagger-*-model/api/*.json files and writes
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
          "telemetry_xpaths": int,   # unique derivable MDT filter xpaths
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
import re
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

# Telemetry filter xpaths derive from every category except RPC (RPCs are
# actions, not subscribable). Mirrors the deriveXpath rule in telemetry.js.
TELEMETRY_CATEGORIES = tuple(c for c in MODEL_CATEGORIES if c != "swagger-rpc-model")
_KEY_TAIL = re.compile(r"=[^/]*$")
_KEY_MID = re.compile(r"=[^/]*(?=/|$)")
_ENTRY_SUFFIX = re.compile(r"Entry$")


def _scan_category(spec_dir: Path) -> dict:
    """Return {specs, paths, operations} for one swagger-<cat>-model/api dir."""
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


def _derive_xpath(op_path: str, prefixes: dict, is_mib: bool):
    """Port of telemetry.js deriveXpath: turn an OpenAPI path into its MDT
    filter xpath, or None when it can't be normalised."""
    if not op_path:
        return None
    p = op_path
    if p.startswith("/data/"):
        p = p[len("/data/"):]
    elif p.startswith("/restconf/data/"):
        p = p[len("/restconf/data/"):]
    elif p.startswith("/"):
        p = p[1:]
    fs = p.find("/")
    first = p if fs == -1 else p[:fs]
    rest = "" if fs == -1 else p[fs:]
    colon = first.find(":")
    if colon == -1:
        return None
    module_name = first[:colon]
    head = _KEY_TAIL.sub("", first[colon + 1:])
    tail = _KEY_MID.sub("", rest)
    if is_mib:
        if _ENTRY_SUFFIX.search(head):
            return None
        return "/" + module_name + ":" + module_name + "/" + head + tail
    prefix = prefixes.get(module_name)
    if not prefix:
        return None
    return "/" + prefix + ":" + head + tail


def _prefix_map(rp: ReleasePaths) -> dict:
    candidates = [rp.release_root / "yang-prefix-map.json"]
    if rp.legacy:
        candidates.append(PROJECT_ROOT / "yang-prefix-map.json")
    for c in candidates:
        if c.is_file():
            try:
                return (json.loads(c.read_text(encoding="utf-8")) or {}).get("modules", {})
            except Exception:
                return {}
    return {}


def _telemetry_xpaths(rp: ReleasePaths) -> int:
    """Count the unique derived MDT filter xpaths across all telemetry
    categories (everything except RPC) — the true subscribable surface."""
    prefixes = _prefix_map(rp)
    uniq: set[str] = set()
    for cat in TELEMETRY_CATEGORIES:
        spec_dir = rp.spec_dir(cat)
        if not spec_dir.is_dir():
            continue
        is_mib = (cat == "swagger-mib-model")
        for f in sorted(spec_dir.glob("*.json")):
            if f.name == "manifest.json":
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            for ap in (data.get("paths") or {}):
                xp = _derive_xpath(ap, prefixes, is_mib)
                if xp:
                    uniq.add(xp)
    return len(uniq)


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
            "telemetry_xpaths": _telemetry_xpaths(rp),
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
    print(f"{'version':<12} {'specs':>6} {'paths':>8} {'ops':>8} {'xpaths':>8}  modules: total/specs/trees")
    print("-" * 78)
    for v in versions:
        t = totals[v]
        mc = f"{t['modules_total']}/{t['modules_with_specs']}/{t['modules_with_trees']}"
        print(f"{v:<12} {t['specs']:>6} {t['paths']:>8} {t['operations']:>8} {t['telemetry_xpaths']:>8}  {mc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
