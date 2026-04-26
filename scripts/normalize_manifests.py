#!/usr/bin/env python3
"""Normalize manifest.json across all releases to the schema viewers expect.

Adds total_modules / total_paths / total_operations to every manifest under
releases/<ver>/swagger-*-model/api-v2/ (and the default sibling dirs) so the
version-aware viewers don't crash on missing keys.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fix_manifest(mf_path: Path) -> bool:
    if not mf_path.is_file():
        return False
    api_dir = mf_path.parent
    spec_files = sorted(p for p in api_dir.glob("*.json") if p.name != "manifest.json")
    total_paths = 0
    total_ops = 0
    module_names = []
    for f in spec_files:
        try:
            spec = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        paths = spec.get("paths", {}) or {}
        total_paths += len(paths)
        for pk, pv in paths.items():
            if isinstance(pv, dict):
                total_ops += sum(1 for m in ("get", "put", "patch", "delete", "post") if m in pv)
        module_names.append(f.stem)
    try:
        existing = json.loads(mf_path.read_text(encoding="utf-8"))
    except Exception:
        existing = {}
    existing["total_modules"] = len(spec_files)
    existing["total_paths"] = total_paths
    existing["total_operations"] = total_ops
    if "modules" not in existing or not existing["modules"]:
        existing["modules"] = module_names
    existing["spec_count"] = len(spec_files)
    mf_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    return True


def main() -> int:
    targets = []
    targets.extend(sorted(ROOT.glob("releases/*/swagger-*-model/api-v2/manifest.json")))
    targets.extend(sorted(ROOT.glob("swagger-*-model/api-v2/manifest.json")))
    fixed = 0
    for mf in targets:
        if fix_manifest(mf):
            rel = mf.relative_to(ROOT)
            d = json.loads(mf.read_text(encoding="utf-8"))
            print(f"  {rel}: modules={d['total_modules']} paths={d['total_paths']} ops={d['total_operations']}")
            fixed += 1
    print(f"\n[normalize] {fixed}/{len(targets)} manifests updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
