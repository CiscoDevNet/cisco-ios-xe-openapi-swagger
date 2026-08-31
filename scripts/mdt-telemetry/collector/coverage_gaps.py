#!/usr/bin/env python3
"""coverage_gaps.py — read-only coverage-gap report from protocol-matrix.json.

Reproduces the authoritative device x method data-module table plus the gap
classification (full gaps, under-collected, flavor gaps, flavor applicability)
that powers the Device Data webapp's coverage-gap panel. Read-only: consumes
protocol-matrix.json and touches no devices.

Usage:
  python coverage_gaps.py [--matrix PATH]   # default: repo-root protocol-matrix.json
"""
import argparse
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--matrix", type=Path, default=REPO_ROOT / "protocol-matrix.json",
                help="path to protocol-matrix.json (default: repo root)")
args = ap.parse_args()

m = json.loads(args.matrix.read_text(encoding="utf-8"))
methods = m["methods"]
mkeys = [x["key"] for x in methods]
mlabel = {x["key"]: x["label"] for x in methods}
devices = m["devices"]
rows = m["rows"]

# data-module counts
dc = {d: {k: 0 for k in mkeys} for d in devices}
# method -> category -> set(devices returning data for that flavor via that method)
mcatdev = collections.defaultdict(lambda: collections.defaultdict(set))
# device -> set(categories the device has ANY row for = flavor is applicable)
devcat = collections.defaultdict(set)
# all categories seen
allcats = set()

for r in rows:
    d = r["pid"]
    cat = r.get("category") or "other"
    allcats.add(cat)
    devcat[d].add(cat)
    cells = r.get("cells", {})
    for k in mkeys:
        if cells.get(k) == "data":
            dc[d][k] += 1
            mcatdev[k][cat].add(d)

cats = sorted(allcats)

print("=" * 100)
print("DATA-MODULE COUNT  (devices x methods)  — how many YANG modules returned data")
print("=" * 100)
w = max(len(d) for d in devices)
hdr = "device".ljust(w) + " | " + " ".join(l[:9].rjust(9) for l in [mlabel[k] for k in mkeys])
print(hdr)
print("-" * len(hdr))
for d in devices:
    print(d.ljust(w) + " | " + " ".join(str(dc[d][k]).rjust(9) for k in mkeys))

print()
print("=" * 100)
print("FULL GAPS — (device, method) with ZERO modules returning data")
print("=" * 100)
full = [(d, k) for d in devices for k in mkeys if dc[d][k] == 0]
if not full:
    print("  none")
for d, k in full:
    print(f"  {d:<18} {mlabel[k]}")

print()
print("=" * 100)
print("UNDER-COLLECTED — device data count < 50% of fleet MAX for that method")
print("=" * 100)
for k in mkeys:
    mx = max(dc[d][k] for d in devices)
    if mx == 0:
        continue
    low = [(d, dc[d][k]) for d in devices if 0 < dc[d][k] < 0.5 * mx]
    if low:
        print(f"  {mlabel[k]:<20} (fleet max {mx}):")
        for d, n in low:
            print(f"       {d:<18} {n}  ({100*n/mx:.0f}% of max)")

print()
print("=" * 100)
print("FLAVOR GAPS — flavor present on a device but NO data via a given method")
print("(excludes methods where the flavor never returns data on ANY device = structural)")
print("=" * 100)
for k in mkeys:
    any_flavor = mcatdev[k]
    for cat in cats:
        have = any_flavor.get(cat, set())
        if not have:
            continue  # flavor never returns data via this method anywhere -> structural, skip
        # devices where this flavor is applicable but returned no data via method k
        missing = [d for d in devices if cat in devcat[d] and d not in have]
        if missing:
            print(f"  {mlabel[k]:<20} {cat:<15} has data on {len(have)}/{len(devices)}; "
                  f"MISSING on: {', '.join(missing)}")

print()
print("=" * 100)
print("FLAVOR APPLICABILITY — which devices have ANY row for each flavor (proxy for 'model exists')")
print("=" * 100)
for cat in cats:
    present = [d for d in devices if cat in devcat[d]]
    absent = [d for d in devices if cat not in devcat[d]]
    print(f"  {cat:<15} present: {len(present)}/{len(devices)}"
          + (f"   ABSENT: {', '.join(absent)}" if absent else "   (all devices)"))
