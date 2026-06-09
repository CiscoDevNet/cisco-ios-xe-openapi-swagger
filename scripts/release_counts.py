#!/usr/bin/env python3
"""Compute and snapshot API/operation/module counts per release.

Produces a deterministic JSON baseline (`release_counts.json` at repo root)
that subsequent test runs compare against. The point is to catch **silent
disappearance of APIs** — if a regen accidentally drops `swagger-oper-model`
from 215 modules to 180, `tests/test_release_counts.py` fails the build.

Counted per release × category:
  - specs       : count of *.json files under api/ (excluding manifest.json
                  and `_*.json` index files)
  - paths       : sum of len(spec["paths"]) across every spec
  - operations  : sum of HTTP-method operations under each path
  - modules     : sorted list of spec stems (catches **renames** with same count)

Also tracked at release level:
  - search_index.modules / categories
  - platform_support.modules / platforms

Usage:
    python -X utf8 scripts/release_counts.py            # print snapshot
    python -X utf8 scripts/release_counts.py --write    # rewrite baseline
    python -X utf8 scripts/release_counts.py --check    # exit 1 if drift vs baseline
    python -X utf8 scripts/release_counts.py --release 26.1.1
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = PROJECT_ROOT / "release_counts.json"
SCHEMA_VERSION = 1

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def is_spec_file(name: str) -> bool:
    return name != "manifest.json" and not name.startswith("_")


def _discover_releases() -> list[str]:
    rels: list[str] = []
    rel_root = PROJECT_ROOT / "releases"
    if not rel_root.is_dir():
        return rels
    for child in sorted(rel_root.iterdir()):
        if child.is_dir() and any(child.glob("swagger-*-model")):
            rels.append(child.name)
    return rels


def _count_category(api_dir: Path) -> dict:
    specs = 0
    paths = 0
    operations = 0
    modules: list[str] = []
    for f in sorted(api_dir.glob("*.json")):
        if not is_spec_file(f.name):
            continue
        specs += 1
        modules.append(f.stem)
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            # gate 1 of validate_release will catch this; for counts we skip.
            continue
        for _path, methods in (data.get("paths") or {}).items():
            paths += 1
            if not isinstance(methods, dict):
                continue
            for method_name, op in methods.items():
                if not isinstance(op, dict):
                    continue
                if method_name.lower() in HTTP_METHODS:
                    operations += 1
    return {
        "specs": specs,
        "paths": paths,
        "operations": operations,
        "modules": sorted(modules),
    }


def _count_search_index(rel_root: Path) -> dict[str, int]:
    idx = rel_root / "search-index.json"
    if not idx.is_file():
        idx = PROJECT_ROOT / "search-index.json"
        if not idx.is_file():
            return {}
    try:
        data = json.loads(idx.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {
        "modules": len(data.get("modules", [])),
        "categories": len(data.get("categories", []) or data.get("categories", {})),
    }


def _count_platform_support(rel_root: Path) -> dict[str, int]:
    p = rel_root / "platform-support.json"
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {
        "modules": len(data.get("modules", {})),
        "platforms": len(data.get("platforms", [])),
    }


def compute_release(version: str) -> dict:
    """Return the count snapshot for a single release."""
    rel_root = PROJECT_ROOT / "releases" / version
    if not rel_root.is_dir():
        raise FileNotFoundError(f"release directory not found: {rel_root}")

    categories: dict[str, dict[str, int]] = {}
    for cat_dir in sorted(rel_root.glob("swagger-*-model")):
        api_dir = cat_dir / "api"
        if not api_dir.is_dir():
            continue
        categories[cat_dir.name] = _count_category(api_dir)

    totals = {
        "specs": sum(c["specs"] for c in categories.values()),
        "paths": sum(c["paths"] for c in categories.values()),
        "operations": sum(c["operations"] for c in categories.values()),
    }
    return {
        "release": version,
        "categories": categories,
        "totals": totals,
        "search_index": _count_search_index(rel_root),
        "platform_support": _count_platform_support(rel_root),
    }


def compute_all(releases: list[str] | None = None) -> dict:
    if releases is None:
        releases = _discover_releases()
    return {
        "schema_version": SCHEMA_VERSION,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "releases": {v: compute_release(v) for v in releases},
    }


def _format_snapshot(snap: dict) -> str:
    out = []
    for ver, rel in snap["releases"].items():
        out.append(f"\n=== {ver} ===")
        out.append(f"  totals: specs={rel['totals']['specs']:>4} "
                   f"paths={rel['totals']['paths']:>6} "
                   f"operations={rel['totals']['operations']:>6}")
        si = rel.get("search_index") or {}
        ps = rel.get("platform_support") or {}
        out.append(f"  search-index: modules={si.get('modules','?')}")
        out.append(f"  platform-support: modules={ps.get('modules','?')} "
                   f"platforms={ps.get('platforms','?')}")
        for cat, c in rel["categories"].items():
            out.append(f"    {cat:<32} specs={c['specs']:>4} "
                       f"paths={c['paths']:>6} operations={c['operations']:>6}")
    return "\n".join(out)


def diff_snapshots(current: dict, baseline: dict) -> list[str]:
    """Return list of regression messages. Empty list = no regressions.

    A regression is any **strict decrease** in:
      - per-category specs/paths/operations
      - per-release search_index.modules or platform_support.modules
      - a release present in baseline but missing in current
      - a category present in baseline but missing in current
      - a **named module** present in baseline but missing in current
        (catches renames where counts stay the same)
    Growth is allowed and silent.
    """
    issues: list[str] = []
    base_releases = baseline.get("releases", {})
    cur_releases = current.get("releases", {})

    for ver, base_rel in base_releases.items():
        if ver not in cur_releases:
            issues.append(f"[{ver}] release disappeared from snapshot")
            continue
        cur_rel = cur_releases[ver]

        base_cats = base_rel.get("categories", {})
        cur_cats = cur_rel.get("categories", {})
        for cat, base_c in base_cats.items():
            if cat not in cur_cats:
                issues.append(f"[{ver}] category {cat} disappeared")
                continue
            cur_c = cur_cats[cat]
            for field in ("specs", "paths", "operations"):
                b = int(base_c.get(field, 0))
                c = int(cur_c.get(field, 0))
                if c < b:
                    issues.append(
                        f"[{ver}/{cat}] {field} dropped {b} -> {c} (-{b - c})"
                    )
            # Named-module disappearance (catches renames where the total
            # count is preserved by an unrelated addition).
            base_mods = set(base_c.get("modules") or [])
            cur_mods = set(cur_c.get("modules") or [])
            gone = sorted(base_mods - cur_mods)
            if gone:
                preview = ", ".join(gone[:5]) + ("..." if len(gone) > 5 else "")
                issues.append(
                    f"[{ver}/{cat}] {len(gone)} module(s) disappeared: {preview}"
                )

        for key, label in (("search_index", "modules"),
                           ("platform_support", "modules"),
                           ("platform_support", "platforms")):
            b = int((base_rel.get(key) or {}).get(label, 0) or 0)
            c = int((cur_rel.get(key) or {}).get(label, 0) or 0)
            if b and c < b:
                issues.append(
                    f"[{ver}/{key}.{label}] dropped {b} -> {c} (-{b - c})"
                )
    return issues


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--release", action="append", default=None,
                   help="Limit to specific release(s); default: all under releases/")
    p.add_argument("--write", action="store_true",
                   help=f"Write {BASELINE_PATH.relative_to(PROJECT_ROOT)} as new baseline")
    p.add_argument("--check", action="store_true",
                   help="Exit 1 if current snapshot has regressions vs the checked-in baseline")
    p.add_argument("--json", action="store_true",
                   help="Print snapshot as JSON instead of summary table")
    args = p.parse_args()

    snap = compute_all(args.release)

    if args.write:
        BASELINE_PATH.write_text(
            json.dumps(snap, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"[counts] wrote {BASELINE_PATH.relative_to(PROJECT_ROOT)} "
              f"({len(snap['releases'])} releases)")
        print(_format_snapshot(snap))
        return 0

    if args.check:
        if not BASELINE_PATH.is_file():
            sys.stderr.write(
                f"[counts] no baseline at {BASELINE_PATH.relative_to(PROJECT_ROOT)}; "
                f"run --write first.\n"
            )
            return 1
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        issues = diff_snapshots(snap, baseline)
        if issues:
            print(f"[counts] REGRESSION — {len(issues)} drop(s) vs baseline:")
            for msg in issues:
                print(f"  - {msg}")
            print(f"\nIf this is intentional (e.g. legitimate module deprecation), "
                  f"refresh the baseline:\n"
                  f"  python -X utf8 scripts/release_counts.py --write")
            return 1
        print(f"[counts] OK — no regressions across {len(snap['releases'])} releases.")
        return 0

    if args.json:
        print(json.dumps(snap, indent=2, sort_keys=True))
    else:
        print(_format_snapshot(snap))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
