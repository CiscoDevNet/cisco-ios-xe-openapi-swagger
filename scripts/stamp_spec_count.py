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


def stamp(manifest: Path) -> tuple[bool, int]:
    """Add/update spec_count on a manifest. Returns (changed, on_disk_count)."""
    # Exclude bookkeeping files: manifest itself and the cross-chunk paths
    # index produced by build_paths_index.py (Round 6+). Only true OpenAPI
    # spec JSONs should count toward spec_count.
    _NON_SPECS = {"manifest.json", "_paths_index.json"}
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
    if data.get("spec_count") == on_disk:
        return False, on_disk
    data["spec_count"] = on_disk
    manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True, on_disk


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
