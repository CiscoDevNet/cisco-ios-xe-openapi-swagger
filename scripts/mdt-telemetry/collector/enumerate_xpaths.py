#!/usr/bin/env python3
"""Estimate the top-level (depth-1) and 2nd-level (depth-2) subscribable xpath
counts per model category from the committed release specs. Read-only, offline.

Used to size a scaled MDT collection sample. Emits the candidate xpaths grouped
by category so we can pick a bounded, high-value set to subscribe to.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

CATEGORY_DIRS = {
    "oper": "swagger-oper-model",
    "cfg": "swagger-cfg-model",
    "native-config": "swagger-native-config-model",
    "openconfig": "swagger-openconfig-model",
    "ietf": "swagger-ietf-model",
    "other": "swagger-other-model",
}


def prefix_map(version):
    f = REPO / "releases" / version / "yang-prefix-map.json"
    if not f.exists():
        f = REPO / "yang-prefix-map.json"
    data = json.loads(f.read_text(encoding="utf-8"))
    # The map is nested: {"module_count", "modules": {<module>: <prefix>}, ...}.
    # MDT filter xpaths require the YANG PREFIX, not the module name.
    return data.get("modules", data)


def xpath_from_restconf(path, pmap):
    """/data/Module:container/child -> /prefix:container/child (MDT filter form)."""
    p = path
    if p.startswith("/data/"):
        p = p[len("/data/"):]
    if not p or ":" not in p:
        return None
    mod, _, rest = p.partition(":")
    pfx = pmap.get(mod, mod)
    return "/" + pfx + ":" + rest


def depth_after_prefix(xp):
    # xp = /prefix:container/child/... ; depth = number of nodes after the prefix
    body = xp.split(":", 1)[1] if ":" in xp else xp
    return len([seg for seg in body.split("/") if seg])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="26.1.1")
    ap.add_argument("--max-depth", type=int, default=2)
    ap.add_argument("--dump", help="Write candidate xpaths per category as JSON.")
    args = ap.parse_args()

    pmap = prefix_map(args.version)
    base = REPO / "releases" / args.version
    result = {}
    candidates = {}
    for cat, d in CATEGORY_DIRS.items():
        api = base / d / "api"
        if not api.is_dir():
            continue
        by_depth = collections.Counter()
        seen = set()
        for spec in api.glob("*.json"):
            try:
                doc = json.loads(spec.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            for path in doc.get("paths", {}):
                if "{" in path:  # skip keyed list instances
                    continue
                xp = xpath_from_restconf(path, pmap)
                if not xp:
                    continue
                depth = depth_after_prefix(xp)
                if 1 <= depth <= args.max_depth and xp not in seen:
                    seen.add(xp)
                    by_depth[depth] += 1
        result[cat] = dict(sorted(by_depth.items()))
        candidates[cat] = sorted(seen)

    print(f"candidate subscribable xpaths (depth 1..{args.max_depth}) by category:")
    grand = 0
    for cat, depths in result.items():
        total = sum(depths.values())
        grand += total
        d1 = depths.get(1, 0)
        d2 = depths.get(2, 0)
        print(f"  {cat:14} depth1={d1:5}  depth2={d2:5}  total={total:5}")
    print(f"  {'TOTAL':14} {'':14}            {grand:5}")

    if args.dump:
        Path(args.dump).write_text(json.dumps(candidates, indent=1), encoding="utf-8")
        print(f"\nwrote candidate xpaths -> {args.dump}")


if __name__ == "__main__":
    raise SystemExit(main())
