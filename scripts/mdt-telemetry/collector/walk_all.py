#!/usr/bin/env python3
"""
walk_all.py — collect ALL model flavors on ONE device, sequentially & resumably.

Runs walk_xpaths.py for each flavor (small -> big, native-config last) plus the
MIB catalog, each with its own checkpoint (walk-<device>-<flavor>.json). One
xpath at a time, all nested containers/lists, keyed values captured. Re-running
resumes every flavor where it left off; `--loop` keeps re-checking so newly
configured features get picked up on later passes.

Run one per device (they share the single Telegraf receiver; each writes its own
mdt-<device>.json via tagpass):

  nohup .venv-harness/bin/python scripts/mdt-telemetry/collector/walk_all.py \
        --device C9300 --mib > output/walk-all-C9300.log 2>&1 &
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WALK = HERE / "walk_xpaths.py"
OUT = HERE / "output"
MIB_CATALOG = OUT / "mib-nodes.json"
PY = sys.executable

# (flavor label, catalog override or None). Small -> big; native-config last.
STEPS = [
    ("openconfig", None),
    ("ietf", None),
    ("other", None),
    ("cfg", None),
    ("mib", MIB_CATALOG),
    ("oper", None),
    ("native-config", None),
]
COMMON = ["--window", "10", "--idle", "3", "--pace", "0", "--apply"]


def run_step(device: str, flavor: str, catalog, capture: Path) -> int:
    state = OUT / f"walk-{device}-{flavor}.json"
    cmd = [PY, str(WALK), "--device", device,
           "--capture-file", str(capture), "--state", str(state)]
    if catalog is not None:
        cmd += ["--catalog", str(catalog)]        # MIB: walk whole catalog
    else:
        cmd += ["--category", flavor]              # normal flavor filter
    cmd += COMMON
    print(f"\n>>> {device} :: {flavor}", flush=True)
    return subprocess.call(cmd)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--device", required=True)
    ap.add_argument("--flavors", nargs="+",
                    help="Subset of flavor labels (default: all incl. mib/native-config).")
    ap.add_argument("--mib", action="store_true", help="Include the MIB catalog step.")
    ap.add_argument("--loop", action="store_true", help="Keep re-passing (picks up new features).")
    args = ap.parse_args()

    capture = OUT / f"mdt-{args.device}.json"
    steps = STEPS
    if args.flavors:
        want = set(args.flavors)
        steps = [s for s in STEPS if s[0] in want]
    if not args.mib:
        steps = [s for s in steps if s[0] != "mib"]

    while True:
        for flavor, catalog in steps:
            run_step(args.device, flavor, catalog, capture)
        print(f"\n=== {args.device}: full pass complete ===", flush=True)
        if not args.loop:
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
