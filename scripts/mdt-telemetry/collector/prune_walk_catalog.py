#!/usr/bin/env python3
"""Build a pruned MDT walk catalog for one device from the fleet's walk results and its own config.

A full per-xpath walk tests ~18,000 catalog xpaths; on a WAN device that takes days, and almost all
of them are invalid or silent on every device. This keeps an xpath only if it streamed on another
walked device, or (native-config) its container exists in this device's captured running config
(`output/restconf-<device>.json`, `/ios:native` payload). Xpaths invalid on every other device are
always dropped.

Leave-one-out check (2026-10-05, six walked devices): native-config keeps ~145 of 14,659 xpaths and
99-100% of the xpaths that streamed; oper keeps ~820 of 3,198 and 94-100% on switches (the C9800's
wireless-only modules are the exception). Run the full walk later to test the rest: state files
resume, so already-walked xpaths are not repeated.

  prune_walk_catalog.py --device C9300-STACK8-WAN --flavor oper \
      --out output/catalog-pruned-C9300-STACK8-WAN-oper.json
  walk_xpaths.py --device C9300-STACK8-WAN --catalog output/catalog-pruned-C9300-STACK8-WAN-oper.json \
      --state output/walk-C9300-STACK8-WAN-oper.json --capture-file output/mdt-C9300-STACK8-WAN.json \
      --window 10 --idle 3 --pace 0 --apply
  prune_walk_catalog.py --device C9300-24UX --flavor oper --validate C9300   # recall check
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "output"
WALKED = ["C9200", "C9300", "C9400", "C9500", "C9600", "C9800"]


def strip(name: str) -> str:
    return name.split(":", 1)[-1]


def native_tree(device: str):
    path = OUT / f"restconf-{device}.json"
    entries = json.loads(path.read_text(encoding="utf-8")).get("entries", []) if path.is_file() else []
    for entry in entries:
        if entry.get("xpath") == "/ios:native" and entry.get("payload"):
            return json.loads(entry["payload"])["Cisco-IOS-XE-native:native"]
    raise SystemExit(f"no /ios:native payload in {path.name}")


def present(tree, segments: list[str]) -> bool:
    if not segments:
        return True
    if isinstance(tree, list):
        return any(present(item, segments) for item in tree)
    if not isinstance(tree, dict):
        return False
    want = strip(segments[0])
    return any(strip(key) == want and present(value, segments[1:]) for key, value in tree.items())


def fleet_results(flavor: str, exclude: str | None) -> list[dict]:
    results = []
    for dev in WALKED:
        if dev == exclude:
            continue
        path = OUT / f"walk-{dev}-{flavor}.json"
        if path.is_file():
            results.append(json.loads(path.read_text(encoding="utf-8"))["results"])
    return results


def keep(flavor: str, device: str, nodes: list[dict], exclude: str | None) -> list[dict]:
    results = fleet_results(flavor, exclude)
    xpaths = set().union(*[set(r) for r in results]) if results else set()
    invalid = {x for x in xpaths if all(r.get(x, {}).get("status") == "invalid" for r in results)}
    streamed = {x for x in xpaths if any(r.get(x, {}).get("status") == "streamed" for r in results)}
    tree = native_tree(device) if flavor == "native-config" else None
    kept = []
    for node in nodes:
        xp = node["xpath"]
        if xp in invalid:
            continue
        in_config = tree is not None and present(tree, [s for s in xp.split("/")[2:] if s])
        if xp in streamed or in_config:
            kept.append(node)
    return kept


def catalog_nodes(flavor: str) -> list[dict]:
    catalog = json.loads((OUT / "subscribable-nodes.json").read_text(encoding="utf-8"))
    return [{**entry, "module": module}
            for module, entries in catalog["modules"].items()
            for entry in entries if entry.get("category") == flavor]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--device", required=True, help="device whose restconf-<device>.json is used for native-config")
    ap.add_argument("--flavor", required=True, choices=["native-config", "oper"])
    ap.add_argument("--out", help="write the pruned catalog (walk_xpaths.py --catalog format)")
    ap.add_argument("--validate", help="walked device to leave out: report how many of its streamed xpaths are kept")
    args = ap.parse_args()

    nodes = catalog_nodes(args.flavor)
    kept = keep(args.flavor, args.device, nodes, exclude=args.validate)
    print(f"{args.flavor}: {len(nodes)} catalog xpaths -> {len(kept)} kept")
    if args.validate:
        walked = json.loads((OUT / f"walk-{args.validate}-{args.flavor}.json").read_text(encoding="utf-8"))["results"]
        streamed = {x for x, v in walked.items() if v["status"] == "streamed"}
        missed = sorted(streamed - {n["xpath"] for n in kept})
        print(f"recall: {len(streamed) - len(missed)}/{len(streamed)} streamed xpaths kept; missed: {missed[:10]}")
    if args.out:
        modules: dict[str, list] = {}
        for node in kept:
            modules.setdefault(node["module"], []).append({k: v for k, v in node.items() if k != "module"})
        Path(args.out).write_text(json.dumps({"version": "pruned", "modules": modules}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
