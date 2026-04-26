#!/usr/bin/env python3
"""
build_all_releases.py — Iterate releases/index.json and build every active release.

Authoritative spec: VERSIONING.md §8.

Usage:
    python scripts/build_all_releases.py
    python scripts/build_all_releases.py --skip-exports
    python scripts/build_all_releases.py --include-planned
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RELEASES_INDEX = PROJECT_ROOT / "releases" / "index.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--include-planned", action="store_true",
                        help="Also build releases marked status=planned (default: skip)")
    parser.add_argument("--skip-exports", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    if not RELEASES_INDEX.is_file():
        sys.stderr.write(f"missing {RELEASES_INDEX}\n")
        return 1
    idx = json.loads(RELEASES_INDEX.read_text(encoding="utf-8"))

    fail = False
    for entry in idx.get("releases", []):
        ver = entry["ver"]
        status = entry.get("status", "active")
        if status == "planned" and not args.include_planned:
            print(f"[all] {ver}: status=planned, skipping (pass --include-planned to build)")
            continue
        cmd = ["python", str(PROJECT_ROOT / "scripts" / "build_release.py"),
               "--version", ver]
        if args.skip_exports:
            cmd.append("--skip-exports")
        if args.continue_on_error:
            cmd.append("--continue-on-error")
        print(f"\n[all] === {ver} ===")
        rc = subprocess.run(cmd, cwd=PROJECT_ROOT).returncode
        if rc != 0:
            fail = True
            if not args.continue_on_error:
                return rc
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
