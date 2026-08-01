#!/usr/bin/env python3
"""Count subscribable nodes (containers + lists) per model flavor, all depths.

For MDT yang-push you subscribe to container/list nodes, not leaves. A node is a
container/list iff it has at least one child path in the specs. This counts
every such node per category (the theoretical maximum subscription set), plus
the leaf total for context.

  .venv-harness/bin/python count_subscribable.py [--version 26.1.1]
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from enumerate_xpaths import CATEGORY_DIRS, prefix_map, xpath_from_restconf  # noqa: E402

REPO = Path(__file__).resolve().parents[3]


def category_of(xpath: str) -> str:
    pfx = xpath.lstrip("/").split(":", 1)[0].lower()
    if pfx.startswith("openconfig") or pfx.startswith("oc-"):
        return "openconfig"
    if pfx.startswith("ietf"):
        return "ietf"
    if "native" in pfx:
        return "native-config"
    if pfx.endswith("-cfg") or pfx.endswith("-config"):
        return "cfg"
    if "oper" in pfx:
        return "oper"
    return "other"


def parent(xpath: str):
    """/prefix:a/b/c -> /prefix:a/b ; None if the parent is just the module root."""
    if "/" not in xpath.split(":", 1)[1]:
        return None  # depth-1: parent is the bare module, not a subscribable path here
    return xpath.rsplit("/", 1)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="26.1.1")
    ap.add_argument("--dump", help="Write the full container/list node catalog (JSON) here.")
    args = ap.parse_args()
    pmap = prefix_map(args.version)
    base = REPO / "releases" / args.version

    all_nodes = set()
    non_leaf = set()      # any node that has >=1 child = container or list
    module_roots = set()  # bare module top containers implied by depth-1 children
    node_cat = {}         # xpath -> authoritative category (from the model directory)

    for cat, d in CATEGORY_DIRS.items():
        api = base / d / "api"
        if not api.is_dir():
            continue
        for spec in api.glob("*.json"):
            try:
                doc = json.loads(spec.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            for path in doc.get("paths", {}):
                if "{" in path:
                    continue
                xp = xpath_from_restconf(path, pmap)
                if not xp:
                    continue
                all_nodes.add(xp)
                node_cat[xp] = cat
                p = parent(xp)
                if p:
                    non_leaf.add(p)
                    node_cat.setdefault(p, cat)
                else:
                    # depth-1 node: its module root is an implied container
                    module_roots.add(xp.split(":", 1)[0] + ":" + xp.split(":", 1)[1].split("/", 1)[0])

    # Any node that is itself a parent is a container/list; everything else is a leaf.
    containers_lists = non_leaf
    leaves = all_nodes - non_leaf

    by_cat_cl = collections.Counter(node_cat.get(x, category_of(x)) for x in containers_lists)
    by_cat_leaf = collections.Counter(node_cat.get(x, category_of(x)) for x in leaves)

    print("subscribable nodes (containers + lists) vs leaves, ALL depths:")
    print(f"  {'flavor':14}{'containers+lists':>18}{'leaves':>10}")
    cats = sorted(set(by_cat_cl) | set(by_cat_leaf))
    tot_cl = tot_leaf = 0
    for c in cats:
        cl = by_cat_cl[c]
        lf = by_cat_leaf[c]
        tot_cl += cl
        tot_leaf += lf
        print(f"  {c:14}{cl:>18}{lf:>10}")
    print(f"  {'TOTAL':14}{tot_cl:>18}{tot_leaf:>10}")
    print(f"\nTotal distinct nodes: {len(all_nodes):,}  |  "
          f"containers+lists: {len(containers_lists):,}  |  leaves: {len(leaves):,}")

    if args.dump:
        catalog = collections.defaultdict(list)
        for xp in sorted(containers_lists):
            depth = xp.split(":", 1)[1].count("/") + 1
            module = xp.lstrip("/").split(":", 1)[0]
            catalog[module].append({"xpath": xp, "depth": depth,
                                    "category": node_cat.get(xp, category_of(xp))})
        out = {
            "version": args.version,
            "total_containers_lists": len(containers_lists),
            "by_category": dict(by_cat_cl),
            "modules": {m: nodes for m, nodes in sorted(catalog.items())},
        }
        Path(args.dump).write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(f"wrote container/list catalog ({len(catalog)} modules) -> {args.dump}")


if __name__ == "__main__":
    raise SystemExit(main())
