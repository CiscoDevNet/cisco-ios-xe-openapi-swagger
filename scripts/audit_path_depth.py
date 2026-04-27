#!/usr/bin/env python3
"""Audit RESTCONF path-depth distribution per category for a release.

"Depth" is the count of node segments after `/data/<module>:<root>` —
roughly how many YANG containers/lists are nested under the top-level
container. A depth-3 path looks like:
    /data/Cisco-IOS-XE-native:native/interface/Vlan={name}/ip/address

The output JSON is consumed by validate_release.py to gate releases on a
per-category minimum max-depth and writes a small summary the project
wiki / CHANGELOG can reference.

Targets (configurable via CLI / config below) — these are the depths the
viewer needs to be useful for real network engineering. Categories where
the underlying YANG is intentionally flat (mib, rpc, events) get lower
floors.

    cfg            d3   (today: d2  – needs tree-based generator)
    events         d2   (today: d1  – RPC-shaped, modest target)
    ietf           d4   (today: d6  – OK)
    mib            d2   (today: d2  – OK; YANG is flat)
    native-config  d6   (today: d8  – OK)
    openconfig     d4   (today: d7  – OK)
    oper           d3   (today: d3  – marginal; only 2 paths reach d3)
    other          d3   (today: d6  – OK)
    rpc            d1   (today: d1  – OK; RPCs are inherently shallow)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

CATEGORIES = (
    "cfg", "events", "ietf", "mib", "native-config",
    "openconfig", "oper", "other", "rpc",
)

# Per-category minimum max-depth required for a release to pass the audit.
# These are floors, not goals — bumping them tightens the gate.
MIN_MAX_DEPTH = {
    "cfg":           5,
    "events":        2,
    "ietf":          3,
    "mib":           2,
    "native-config": 6,
    "openconfig":    3,
    "oper":          5,
    "other":         3,
    "rpc":           1,
}


def path_depth(p: str) -> int:
    """Number of node segments under the module root.

    /data/Cisco-IOS-XE-native:native           -> 0
    /data/Cisco-IOS-XE-native:native/vlan      -> 1
    /data/Cisco-IOS-XE-native:native/vlan/list -> 2
    """
    s = p.split("/data/", 1)[-1]
    segs = [x for x in s.split("/") if x]
    return max(0, len(segs) - 1)


def audit_category(api_dir: Path) -> dict:
    dist: Counter[int] = Counter()
    total = 0
    for spec in sorted(api_dir.glob("*.json")):
        if spec.name in ("manifest.json", "_paths_index.json"):
            continue
        try:
            data = json.loads(spec.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            print(f"  ! skip {spec.name}: {exc}", file=sys.stderr)
            continue
        for p in (data.get("paths") or {}):
            dist[path_depth(p)] += 1
            total += 1
    max_d = max(dist) if dist else -1
    return {
        "path_count": total,
        "max_depth": max_d,
        "distribution": {str(k): dist[k] for k in sorted(dist)},
    }


def fmt_dist(dist: dict[str, int]) -> str:
    return " ".join(f"d{k}={v}" for k, v in sorted(dist.items(), key=lambda kv: int(kv[0])))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true",
                    help="Exit non-zero if any category is below MIN_MAX_DEPTH.")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    base = root / "releases" / args.version
    if not base.is_dir():
        print(f"[audit_path_depth] ERROR: {base} not found", file=sys.stderr)
        return 1

    print(f"[audit_path_depth] {args.version}")
    print(f"  {'category':14s} {'paths':>6s}  {'max':>4s}  min  status  distribution")
    print(f"  {'-'*14} {'-'*6}  {'-'*4}  ---  ------  {'-'*40}")

    summary = {"version": args.version, "min_max_depth": MIN_MAX_DEPTH, "categories": {}}
    failures: list[str] = []
    for cat in CATEGORIES:
        api_dir = base / f"swagger-{cat}-model" / "api-v2"
        if not api_dir.is_dir():
            print(f"  {cat:14s} {'-':>6s}  {'-':>4s}  -    SKIP    (no api-v2 dir)")
            summary["categories"][cat] = {"missing": True}
            continue
        stat = audit_category(api_dir)
        floor = MIN_MAX_DEPTH.get(cat, 0)
        ok = stat["max_depth"] >= floor
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures.append(cat)
        print(f"  {cat:14s} {stat['path_count']:>6d}  d{stat['max_depth']:<3d}  d{floor}    {status:>6s}  {fmt_dist(stat['distribution'])}")
        stat["min_required"] = floor
        stat["pass"] = ok
        summary["categories"][cat] = stat

    summary["failures"] = failures
    summary["pass"] = not failures

    out = base / "path_depth_audit.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n  wrote {out.relative_to(root)}")

    if failures:
        print(f"\n[audit_path_depth] {len(failures)} categor{'y' if len(failures)==1 else 'ies'} below floor: {', '.join(failures)}")
        if args.strict:
            return 2
    else:
        print("\n[audit_path_depth] all categories meet minimum max-depth floor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
