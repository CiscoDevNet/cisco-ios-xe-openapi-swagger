#!/usr/bin/env python3
"""
refresh_live_data.py — one command to rebuild the Live Data artifacts.

Chains the deterministic, offline steps:

  1. build the gitignored sidecar from the local captures
     (references/live-examples-<ver>.json), and
  2. regenerate releases/<ver>/live-examples-index.json + the per-path
     live-data/ files (with publish-time redaction).

Optionally re-captures from the devices first (needs inventory + creds).

Usage:
    python scripts/refresh_live_data.py --version 26.1.1
    python scripts/refresh_live_data.py --version 26.1.1 --capture   # device I/O first
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import build_live_examples_index
from scripts.harness import build_observed_examples
from scripts.harness.collector import CAPTURES_DIR


def refresh(version: str, capture: bool) -> int:
    if capture:
        # Full device capture (all categories, all devices). Read-only GETs.
        from scripts.harness import collector

        print("[refresh] capturing from devices …")
        rc = collector.main([])
        if rc != 0:
            print(f"[refresh] collector exited {rc}; aborting.", file=sys.stderr)
            return rc

    if not CAPTURES_DIR.is_dir():
        print(f"[refresh] no captures at {CAPTURES_DIR}; run with --capture first.", file=sys.stderr)
        return 2

    sidecar_path = PROJECT_ROOT / "references" / f"live-examples-{version}.json"
    print(f"[refresh] building sidecar → {sidecar_path}")
    sidecar, stats = build_observed_examples.build_sidecar(CAPTURES_DIR)
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    import json

    sidecar_path.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")
    print(f"[refresh]   {sidecar['entry_count']} path entries "
          f"(skipped too_large={stats['skipped_too_large']} secret={stats['skipped_secret']})")

    print(f"[refresh] regenerating releases/{version} live-data …")
    index = build_live_examples_index.build(version)
    if index is None:
        print("[refresh] index build was a no-op (no sidecar).", file=sys.stderr)
        return 2
    t = index["totals"]
    print(f"[refresh] done: {t['modules_with_data']} modules, {t['captured_paths']} paths, "
          f"{t['devices']} devices.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--version", required=True)
    ap.add_argument("--capture", action="store_true",
                    help="Re-capture from the devices first (needs inventory + IOSXE_USER/IOSXE_PASS)")
    args = ap.parse_args()
    return refresh(args.version, args.capture)


if __name__ == "__main__":
    raise SystemExit(main())
