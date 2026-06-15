#!/usr/bin/env python3
"""
stamp_spec_count.py — Stamp ``spec_count`` field on every manifest.json so
``validate_release.py`` gate 2 has a declared count to compare against the
on-disk file count.

Walks both the legacy in-place layout (``swagger-*-model/api/``) and the
per-release layout (``releases/<v>/swagger-*-model/api/``). Idempotent.

Usage:
    python scripts/stamp_spec_count.py                # stamp every manifest
    python scripts/stamp_spec_count.py --version 26.1.1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


_NON_SPECS = {"manifest.json", "_paths_index.json"}
_OP_METHODS = {"get", "put", "patch", "post", "delete", "head", "options"}


def _scan_paths_ops(api_dir: Path) -> tuple[int, int]:
    """Sum (total_paths, total_operations) across all spec JSONs in a dir."""
    total_paths = 0
    total_ops = 0
    for f in api_dir.glob("*.json"):
        if f.name in _NON_SPECS:
            continue
        try:
            spec = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        paths = spec.get("paths", {}) if isinstance(spec, dict) else {}
        if not isinstance(paths, dict):
            continue
        total_paths += len(paths)
        for item in paths.values():
            if isinstance(item, dict):
                total_ops += sum(1 for m in item if m in _OP_METHODS)
    return total_paths, total_ops


def stamp(manifest: Path) -> tuple[bool, int]:
    """Stamp spec_count and backfill total_paths/total_operations if missing.

    The category viewer pages call ``manifest.total_operations.toLocaleString()``
    and ``manifest.total_paths.toLocaleString()`` unguarded, so a manifest that
    is missing either key crashes ``init()`` and the module-list sidebar never
    renders. Regenerating a category with ``--only <cat>-specs`` rewrites the
    manifest fresh from the generator, and several generators (ietf, openconfig,
    other, mib) do not emit ``total_operations`` — so this step must restore it.
    Returns (changed, on_disk_count).
    """
    # Exclude bookkeeping files: manifest itself and the cross-chunk paths
    # index produced by build_paths_index.py (Round 6+). Only true OpenAPI
    # spec JSONs should count toward spec_count.
    on_disk = sum(
        1 for f in manifest.parent.glob("*.json") if f.name not in _NON_SPECS
    )
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception as e:  # pragma: no cover
        print(f"  ! {manifest.relative_to(PROJECT_ROOT)}: invalid JSON ({e})")
        return False, on_disk
    if not isinstance(data, dict):
        print(f"  ! {manifest.relative_to(PROJECT_ROOT)}: not an object; skipping")
        return False, on_disk

    changed = False
    if data.get("spec_count") != on_disk:
        data["spec_count"] = on_disk
        changed = True

    # Backfill the stat keys the viewer reads unguarded. Only compute (an O(N)
    # spec scan) when at least one key is actually missing, to stay cheap and
    # to avoid disturbing counts already emitted by a generator.
    if "total_paths" not in data or "total_operations" not in data:
        scanned_paths, scanned_ops = _scan_paths_ops(manifest.parent)
        if "total_paths" not in data:
            data["total_paths"] = scanned_paths
            changed = True
        if "total_operations" not in data:
            data["total_operations"] = scanned_ops
            changed = True

    if changed:
        manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return changed, on_disk


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--version", help="Limit to a single release version")
    args = p.parse_args()

    targets: list[Path] = []
    # Legacy in-place api layout
    if not args.version or args.version == "17.18.1":
        targets.extend(
            PROJECT_ROOT.glob("swagger-*-model/api/manifest.json")
        )
    # Per-release layout
    rel_root = PROJECT_ROOT / "releases"
    if rel_root.is_dir():
        if args.version:
            targets.extend(
                (rel_root / args.version).glob(
                    "swagger-*-model/api/manifest.json"
                )
            )
        else:
            targets.extend(
                rel_root.glob("*/swagger-*-model/api/manifest.json")
            )

    changed = 0
    for m in sorted(set(targets)):
        did, n = stamp(m)
        marker = "*" if did else " "
        print(f"  {marker} {m.relative_to(PROJECT_ROOT)} spec_count={n}")
        if did:
            changed += 1
    print(f"[stamp] updated {changed}/{len(targets)} manifests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
