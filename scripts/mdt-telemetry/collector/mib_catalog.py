#!/usr/bin/env python3
"""Build the MIB node catalog for SNMP->MDT bridge subscriptions.

MIB MDT filter xpaths use a different rule than the prefix-map categories:
    OpenAPI  /data/IF-MIB:ifTable/ifEntry
    MDT      /IF-MIB:IF-MIB/ifTable/ifEntry     (module name repeated as prefix + root)

Emits output/mib-nodes.json in the same schema as subscribable-nodes.json so
walk_xpaths.py can walk it with --catalog. MIB subscriptions also require an SNMP
community configured on the device (SNMP->MDT bridge).
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
API = REPO / "releases" / "26.1.1" / "swagger-mib-model" / "api"
OUT = Path(__file__).resolve().parent / "output" / "mib-nodes.json"


def mdt_xpath(path: str):
    p = path[len("/data/"):] if path.startswith("/data/") else path
    if ":" not in p:
        return None
    mod, _, rest = p.partition(":")
    if not rest:
        return None
    return f"/{mod}:{mod}/{rest}"


def main():
    all_nodes = set()
    for spec in sorted(API.glob("*.json")):
        try:
            doc = json.loads(spec.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for path in doc.get("paths", {}):
            if "{" in path:
                continue
            xp = mdt_xpath(path)
            if xp:
                all_nodes.add(xp)
    # Add each module root /<MOD>:<MOD> (subscribe to the whole MIB).
    for mod in {x.lstrip("/").split(":", 1)[0] for x in all_nodes}:
        all_nodes.add(f"/{mod}:{mod}")

    # Container/list = any node that has children (tables, entries, module roots).
    parents = set()
    for x in all_nodes:
        body = x.split(":", 1)[1]
        if "/" in body:
            parents.add(x.rsplit("/", 1)[0])
    containers_lists = sorted(n for n in all_nodes if n in parents)

    catalog = defaultdict(list)
    for xp in containers_lists:
        mod = xp.lstrip("/").split(":", 1)[0]
        depth = xp.split(":", 1)[1].count("/") + 1
        catalog[mod].append({"xpath": xp, "depth": depth})

    out = {
        "version": "26.1.1",
        "total_containers_lists": len(containers_lists),
        "modules": {m: nodes for m, nodes in sorted(catalog.items())},
    }
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"MIB catalog: {len(catalog)} modules, {len(containers_lists)} container/list nodes -> {OUT.name}")


if __name__ == "__main__":
    raise SystemExit(main())
