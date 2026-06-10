#!/usr/bin/env python3
"""
fetch_yang_release.py — Fetch a Cisco IOS XE YANG release from YangModels/yang.

Pulls the YANG modules for a single IOS XE release (e.g. 17.9.x → vendor/cisco/xe/1791/)
into ``references/<version>/`` using ``git`` so the upstream commit SHA can be pinned in
``releases/<version>/meta.json``.

Usage:
    python scripts/fetch_yang_release.py --version 26.1.1 --yangmodels-path vendor/cisco/xe/2611
    python scripts/fetch_yang_release.py --version 17.9.x --yangmodels-path vendor/cisco/xe/1791

This script is idempotent: re-running updates the local copy and re-pins the commit SHA.

Authoritative spec: VERSIONING.md §5 (meta.json schema) and §8 (release runbook).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

YANGMODELS_REPO = "https://github.com/YangModels/yang.git"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path | None = None) -> str:
    """Run a subprocess, return stdout (text). Raise on non-zero exit."""
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(cmd)}")
    return result.stdout


def detect_pyang_version() -> str:
    try:
        out = run(["pyang", "--version"]).strip()
        # pyang prints e.g. "pyang 2.6.1"
        return out.split()[-1] if out else "unknown"
    except (FileNotFoundError, SystemExit):
        return "not-installed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument(
        "--version", required=True,
        help="Release tag used in folder names (e.g. 26.1.1, 17.9.x)",
    )
    parser.add_argument(
        "--yangmodels-path", required=True,
        help="Path within YangModels/yang (e.g. vendor/cisco/xe/2611)",
    )
    parser.add_argument(
        "--repo", default=YANGMODELS_REPO,
        help=f"Source git repo URL (default: {YANGMODELS_REPO})",
    )
    parser.add_argument(
        "--ref", default="main",
        help="Git ref/branch to fetch (default: main)",
    )
    args = parser.parse_args()

    version = args.version
    yang_path = args.yangmodels_path.strip("/")
    dest_yang = PROJECT_ROOT / "references" / version
    dest_release = PROJECT_ROOT / "releases" / version
    dest_release.mkdir(parents=True, exist_ok=True)

    print(f"[fetch] release={version} yangmodels_path={yang_path} ref={args.ref}")

    with tempfile.TemporaryDirectory(prefix=f"yang-{version}-") as tmp:
        tmp_path = Path(tmp)
        # Sparse, shallow clone of just the needed sub-tree
        run(["git", "clone", "--depth", "1", "--filter=blob:none",
             "--sparse", "--branch", args.ref, args.repo, str(tmp_path / "yang")])
        run(["git", "sparse-checkout", "set", yang_path],
            cwd=tmp_path / "yang")
        commit_sha = run(["git", "rev-parse", "HEAD"], cwd=tmp_path / "yang").strip()

        src = tmp_path / "yang" / yang_path
        if not src.is_dir():
            raise SystemExit(f"path not found in upstream repo: {yang_path}")

        # Replace destination contents
        if dest_yang.exists():
            shutil.rmtree(dest_yang)
        dest_yang.mkdir(parents=True)
        yang_files = sorted(src.glob("*.yang"))
        for f in yang_files:
            shutil.copy2(f, dest_yang / f.name)
        print(f"[fetch] copied {len(yang_files)} *.yang files → {dest_yang}")
        # Also copy known MIB / BIC subdirectories so the MIB generator and
        # enricher can find SMIv2-derived YANG modules. The upstream
        # YangModels/yang tree publishes MIB conversions under
        # ``vendor/cisco/xe/<id>/MIBS/`` and per-platform MIBs under
        # ``vendor/cisco/xe/<id>/BIC/``.
        for sub in ("MIBS", "BIC"):
            sub_src = src / sub
            if sub_src.is_dir():
                sub_dest = dest_yang / sub
                shutil.copytree(sub_src, sub_dest)
                sub_files = list(sub_dest.rglob("*.yang"))
                print(f"[fetch] copied {len(sub_files)} *.yang files â†’ {sub_dest}")
                yang_files.extend(sub_files)
    # Write/update meta.json
    meta_path = dest_release / "meta.json"
    existing: dict = {}
    if meta_path.exists():
        try:
            existing = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}

    meta = {
        "version": version,
        "label": existing.get("label", version),
        "yangmodels_repo": args.repo,
        "yangmodels_path": yang_path,
        "yangmodels_commit_sha": commit_sha,
        "yangmodels_fetch_date": datetime.now(timezone.utc)
            .replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "pyang_version": detect_pyang_version(),
        "build_timestamp": existing.get("build_timestamp"),
        "module_counts": existing.get("module_counts", {
            "total_yang": len(yang_files),
            "with_specs": 0,
            "with_trees": 0,
        }),
    }
    meta["module_counts"]["total_yang"] = len(yang_files)
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"[fetch] wrote meta.json (commit_sha={commit_sha[:12]}…)")
    print(f"[fetch] done. Next: python scripts/build_release.py --version {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
