#!/usr/bin/env python3
"""
Update all manifest.json files with current path/operation counts.

Usage:
    python scripts/update_manifests.py --version 26.2.1   # releases/<ver>/swagger-*-model/api
    python scripts/update_manifests.py                    # legacy root swagger-*-model/api
"""
import argparse
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT  # set from --version in main()

FOLDERS = [
    'swagger-oper-model', 'swagger-rpc-model', 'swagger-cfg-model',
    'swagger-openconfig-model', 'swagger-ietf-model', 'swagger-mib-model',
    'swagger-events-model', 'swagger-native-config-model', 'swagger-other-model'
]

EXCLUDE = {
    'manifest.json', 'all-operations.json', 'all-rpc-operations.json',
    'all-config.json', 'all-ietf.json', 'all-openconfig.json',
    'all-mib.json', 'all-events.json', 'all-other.json',
    '_paths_index.json',
}


def count_folder(folder_name):
    """Count specs, paths, and ops in a folder."""
    api_dir = BASE / folder_name / 'api'
    if not api_dir.is_dir():
        return 0, 0, 0, []

    specs = []
    total_paths = 0
    total_ops = 0

    for fn in sorted(os.listdir(api_dir)):
        if fn in EXCLUDE or not fn.endswith('.json'):
            continue
        fp = api_dir / fn
        try:
            with open(fp, 'r', encoding='utf-8-sig') as fh:
                spec = json.load(fh)
            paths = spec.get('paths', {})
            p = len(paths)
            o = sum(1 for pk in paths for m in ['get', 'put', 'patch', 'delete', 'post'] if m in paths[pk])
            total_paths += p
            total_ops += o
            specs.append(fn.replace('.json', ''))
        except Exception as e:
            print(f"  WARNING: Error reading {fn}: {e}")

    specs.sort()  # by module name; filename order puts "x-v2.json" before "x.json"
    return len(specs), total_paths, total_ops, specs


def update_manifest(folder_name, spec_count, total_paths, total_ops, modules):
    """Update counts in a folder's manifest.json, keeping generator-written keys."""
    api_dir = BASE / folder_name / 'api'
    mf_path = api_dir / 'manifest.json'

    manifest = {}
    if mf_path.is_file():
        manifest = json.loads(mf_path.read_text(encoding='utf-8-sig'))
    existing = manifest.get("modules")
    if isinstance(existing, list) and sorted(map(str, existing)) == sorted(modules):
        modules = existing  # generators choose their own order; keep it
    manifest.update({
        "total_modules": spec_count,
        "total_paths": total_paths,
        "total_operations": total_ops,
        "modules": modules,
    })

    with open(mf_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')

    return manifest


def main():
    global BASE
    parser = argparse.ArgumentParser(description="Update manifest.json counts")
    parser.add_argument("--version", help="Release under releases/<ver>/ (default: legacy root layout)")
    args = parser.parse_args()
    if args.version:
        BASE = ROOT / "releases" / args.version
        if not BASE.is_dir():
            raise SystemExit(f"release not found: {BASE}")

    print("=" * 70)
    print(f"  Updating all manifests ({BASE.relative_to(ROOT) if BASE != ROOT else 'root'})")
    print("=" * 70)

    grand_specs = 0
    grand_paths = 0
    grand_ops = 0
    folder_stats = {}

    for folder in FOLDERS:
        if not (BASE / folder / 'api').is_dir():
            continue  # e.g. the retired swagger-events-model
        count, paths, ops, modules = count_folder(folder)
        folder_stats[folder] = (count, paths, ops)
        grand_specs += count
        grand_paths += paths
        grand_ops += ops

        update_manifest(folder, count, paths, ops, modules)
        print(f"  {folder}: {count} specs, {paths} paths, {ops} ops")

    print(f"\n  GRAND TOTALS: {grand_specs} specs, {grand_paths} paths, {grand_ops} ops")
    print("\n  All manifests updated.")

    return grand_specs, grand_paths, grand_ops, folder_stats


if __name__ == "__main__":
    main()
