#!/usr/bin/env python3
"""
migrate_to_releases_layout.py — One-shot migration of the existing 17.18.1 artifacts
into the new ``releases/<version>/`` folder layout defined in VERSIONING.md.

This script is intentionally idempotent and verbose: it prints every move it would
make in --dry-run mode (the default) and only mutates the filesystem when invoked
with --apply. After a successful migration, the legacy paths can be removed; until
then the build keeps working from the legacy locations.

Usage:
    # see what would happen
    python scripts/migrate_to_releases_layout.py --dry-run

    # do it
    python scripts/migrate_to_releases_layout.py --apply

    # do it AND delete the legacy locations after copy
    python scripts/migrate_to_releases_layout.py --apply --remove-legacy

The migration uses *copy* by default (not move), so the legacy locations remain
intact for one rollout cycle. Use --remove-legacy after you've verified the new
layout deploys cleanly.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TARGET_VERSION = "17.18.1"

# (legacy-path, new-path-relative-to-release-root). Files only at top of legacy.
LEGACY_FILE_MAP = [
    ("search-index.json", "search-index.json"),
    ("yang_accountability.json", "yang_accountability.json"),
]

# (legacy-dir-glob, new-subdir-relative-to-release-root). Whole subtree copied.
LEGACY_DIR_MAP = [
    ("yang-trees", "yang-trees"),
    ("swagger-cfg-model/api-v2", "swagger-cfg-model/api-v2"),
    ("swagger-events-model/api-v2", "swagger-events-model/api-v2"),
    ("swagger-ietf-model/api-v2", "swagger-ietf-model/api-v2"),
    ("swagger-mib-model/api-v2", "swagger-mib-model/api-v2"),
    ("swagger-native-config-model/api-v2", "swagger-native-config-model/api-v2"),
    ("swagger-openconfig-model/api-v2", "swagger-openconfig-model/api-v2"),
    ("swagger-oper-model/api-v2", "swagger-oper-model/api-v2"),
    ("swagger-other-model/api-v2", "swagger-other-model/api-v2"),
    ("swagger-rpc-model/api-v2", "swagger-rpc-model/api-v2"),
    # Postman exports
    ("tools", "exports/postman-legacy"),
]

# References — raw YANG sources move from the old per-release folder name.
LEGACY_REFERENCES = [
    ("references/17181-YANG-modules", "references/17.18.1"),
]


def plan_copies() -> list[tuple[Path, Path, str]]:
    """Return (src, dst, kind) tuples. kind ∈ {file, dir, ref}."""
    rel_root = PROJECT_ROOT / "releases" / TARGET_VERSION
    plan: list[tuple[Path, Path, str]] = []
    for src_rel, dst_rel in LEGACY_FILE_MAP:
        s = PROJECT_ROOT / src_rel
        d = rel_root / dst_rel
        if s.is_file():
            plan.append((s, d, "file"))
    for src_rel, dst_rel in LEGACY_DIR_MAP:
        s = PROJECT_ROOT / src_rel
        d = rel_root / dst_rel
        if s.is_dir():
            plan.append((s, d, "dir"))
    for src_rel, dst_rel in LEGACY_REFERENCES:
        s = PROJECT_ROOT / src_rel
        d = PROJECT_ROOT / dst_rel
        if s.is_dir():
            plan.append((s, d, "ref"))
    return plan


def do_copy(src: Path, dst: Path, kind: str) -> None:
    if kind == "file":
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    else:
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--apply", action="store_true",
                        help="Actually perform the migration (default: dry run)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Explicitly request dry run (this is the default)")
    parser.add_argument("--remove-legacy", action="store_true",
                        help="After --apply, delete the legacy source paths")
    args = parser.parse_args()
    if args.dry_run and args.apply:
        sys.stderr.write("--dry-run and --apply are mutually exclusive\n")
        return 2

    plan = plan_copies()
    if not plan:
        print("[migrate] nothing to migrate (legacy paths not found).")
        return 0

    print(f"[migrate] target=releases/{TARGET_VERSION}/")
    print(f"[migrate] {'APPLY' if args.apply else 'DRY-RUN'}: {len(plan)} item(s)")
    for src, dst, kind in plan:
        print(f"  [{kind}] {src.relative_to(PROJECT_ROOT)} → {dst.relative_to(PROJECT_ROOT)}")

    if not args.apply:
        print("\n[migrate] dry-run only. Re-run with --apply to perform the migration.")
        return 0

    for src, dst, kind in plan:
        try:
            do_copy(src, dst, kind)
            print(f"  ✓ copied {src.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            sys.stderr.write(f"  ✗ failed {src}: {e}\n")
            return 1

    # Stub meta.json if not already present
    meta_path = PROJECT_ROOT / "releases" / TARGET_VERSION / "meta.json"
    if not meta_path.exists():
        meta_path.write_text(
            "{\n"
            f"  \"version\": \"{TARGET_VERSION}\",\n"
            f"  \"label\": \"{TARGET_VERSION}\",\n"
            "  \"yangmodels_repo\": \"https://github.com/YangModels/yang\",\n"
            "  \"yangmodels_path\": \"vendor/cisco/xe/17181\",\n"
            "  \"yangmodels_commit_sha\": \"\",\n"
            "  \"yangmodels_fetch_date\": null,\n"
            "  \"pyang_version\": \"unknown\",\n"
            "  \"build_timestamp\": null,\n"
            "  \"module_counts\": {\"total_yang\": 0, \"with_specs\": 0, \"with_trees\": 0}\n"
            "}\n",
            encoding="utf-8",
        )
        print(f"  ✓ wrote stub {meta_path.relative_to(PROJECT_ROOT)}")

    if args.remove_legacy:
        print("\n[migrate] --remove-legacy: deleting legacy source paths")
        for src, _, kind in plan:
            try:
                if kind == "file":
                    src.unlink()
                else:
                    shutil.rmtree(src)
                print(f"  ✓ removed {src.relative_to(PROJECT_ROOT)}")
            except Exception as e:
                sys.stderr.write(f"  ✗ could not remove {src}: {e}\n")

    print("\n[migrate] done. Verify with: python scripts/validate_release.py "
          f"--version {TARGET_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
