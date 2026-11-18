#!/usr/bin/env python3
"""Build the nested OpenConfig node catalog for gNMI (output/openconfig-nodes.json).

The spec-derived catalogs are thin for OpenConfig (openconfig-interfaces has 14
spec paths and no augments: no ethernet, subinterfaces, ipv4). This walks the real
YANG schema with pyang, including augments and the Cisco IOS XE deviations, and
emits every container and list as an unprefixed gNMI path, which is the only form
IOS XE accepts (openconfig:/interfaces/interface/ethernet/state).

    .venv-harness/bin/python gnmi_oc_catalog.py            # device_data release
    .venv-harness/bin/python gnmi_oc_catalog.py --version 26.2.1
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "generators"))
from _release_paths import device_data_release  # noqa: E402
from _openconfig_schema import data_children, data_modules, load_context, top_nodes  # noqa: E402

OUT = Path(__file__).resolve().parent / "output" / "openconfig-nodes.json"


def _walk(node, parent_path, root_module, depth, out):
    for child in data_children(node):
        if child.keyword not in ("container", "list"):
            continue
        path = f"{parent_path}/{child.arg}"
        out.append({
            "path": path,
            "module": root_module,
            "node_module": child.i_module.i_modulename,
            "kind": child.keyword,
            "depth": depth,
            "config": bool(getattr(child, "i_config", True)),
        })
        _walk(child, path, root_module, depth + 1, out)


def build_catalog(yang_dir: Path) -> dict:
    ctx = load_context(yang_dir)
    nodes: list[dict] = []
    for module in data_modules(ctx):
        for top in top_nodes(module):
            nodes.append({"path": f"/{top.arg}", "module": module.arg, "node_module": module.arg,
                          "kind": top.keyword, "depth": 1,
                          "config": bool(getattr(top, "i_config", True))})
            _walk(top, f"/{top.arg}", module.arg, 2, nodes)
    unique = {}
    for node in nodes:
        unique.setdefault(node["path"], node)
    ordered = sorted(unique.values(), key=lambda n: (n["module"], n["path"]))
    by_module = collections.Counter(n["module"] for n in ordered)
    return {"source": str(yang_dir.relative_to(REPO)), "total": len(ordered),
            "by_module": dict(sorted(by_module.items())), "nodes": ordered}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", default=device_data_release())
    args = parser.parse_args()
    catalog = build_catalog(REPO / "references" / args.version)
    catalog["version"] = args.version
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(catalog, indent=1) + "\n", encoding="utf-8")
    print(f"{OUT.name}: {catalog['total']} nodes in {len(catalog['by_module'])} modules")
    for module, count in catalog["by_module"].items():
        print(f"  {count:>5}  {module}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
