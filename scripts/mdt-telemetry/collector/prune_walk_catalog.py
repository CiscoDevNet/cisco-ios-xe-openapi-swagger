#!/usr/bin/env python3
"""Build a pruned MDT walk catalog for one device from the fleet's walk results and its own config.

A full per-xpath walk tests ~18,000 catalog xpaths; on a WAN device that takes days, and almost all
of them are invalid or silent on every device. For native-config and cfg this keeps every xpath whose
container is in the device's running config (`config_get.py`: `show running-config | format
restconf-json`, so nothing unconfigured is walked), plus xpaths that streamed on another walked
device. Oper data depends on runtime state, not config, so oper keeps only what streamed elsewhere.

Leave-one-out check (six walked devices): native-config keeps 192-270 of 14,659 xpaths and 299/300
of the xpaths that streamed; cfg keeps 77-127 of 522 and 101/101 (including the C9800's wireless
models); oper keeps ~820 of 3,198 and 94-100% on switches (C9800 39%: wireless-only modules). Run the
full walk later to test the rest: state files resume, so already-walked xpaths are not repeated.

  config_get.py --device C9300-STACK8-WAN
  prune_walk_catalog.py --device C9300-STACK8-WAN --flavor oper \
      --out output/catalog-pruned-C9300-STACK8-WAN-oper.json
  walk_xpaths.py --device C9300-STACK8-WAN --catalog output/catalog-pruned-C9300-STACK8-WAN-oper.json \
      --state output/walk-C9300-STACK8-WAN-oper.json --capture-file output/mdt-C9300-STACK8-WAN.json \
      --window 10 --idle 3 --pace 0 --apply
  prune_walk_catalog.py --device C9300-24UX --flavor oper --validate C9300   # recall check

`kit.py walk` runs all of this per device.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "output"
CONFIG_FLAVORS = ("native-config", "cfg")
FLAVORS = (*CONFIG_FLAVORS, "oper")


def strip(name: str) -> str:
    return name.split(":", 1)[-1]


def config_root(device: str) -> dict:
    """Every configured YANG model on the device, keyed by container name without module prefix.

    Prefers config_get.py's ``show running-config | format restconf-json`` capture (native and every
    *-cfg model); falls back to the RESTCONF ``/ios:native`` GET in restconf-<device>.json.
    """
    config = OUT / f"config-{device}.json"
    if config.is_file():
        models = json.loads(config.read_text(encoding="utf-8"))["restconf_json"]
        return {strip(key): value for key, value in models.items()}
    path = OUT / f"restconf-{device}.json"
    entries = json.loads(path.read_text(encoding="utf-8")).get("entries", []) if path.is_file() else []
    for entry in entries:
        if entry.get("xpath") == "/ios:native" and entry.get("payload"):
            return {"native": json.loads(entry["payload"])["Cisco-IOS-XE-native:native"]}
    raise SystemExit(f"no config capture for {device}: run config_get.py (or restconf_get.py) first")


def configured(root: dict, xpath: str) -> bool:
    return present(root, [s for s in xpath.split("/") if s])


def present(tree, segments: list[str]) -> bool:
    if not segments:
        return True
    if isinstance(tree, list):
        return any(present(item, segments) for item in tree)
    if not isinstance(tree, dict):
        return False
    want = strip(segments[0])
    return any(strip(key) == want and present(value, segments[1:]) for key, value in tree.items())


def fleet_results(flavor: str, exclude: set[str]) -> list[dict]:
    """Walk results of the other walked devices: local walk-<device>-<flavor>.json states, plus the
    compact fleet-walk-<flavor>.json history a harness kit ships (build_kit.py)."""
    per_device = {}
    history = OUT / f"fleet-walk-{flavor}.json"
    if history.is_file():
        per_device.update(json.loads(history.read_text(encoding="utf-8"))["devices"])
    for path in sorted(OUT.glob(f"walk-*-{flavor}.json")):
        device = path.name[len("walk-"):-len(f"-{flavor}.json")]
        per_device[device] = json.loads(path.read_text(encoding="utf-8"))["results"]
    return [results for device, results in per_device.items() if device not in exclude]


def fleet_history(flavor: str) -> dict:
    """Compact fleet history for a kit: only the statuses pruning reads (streamed / invalid)."""
    devices = {}
    for path in sorted(OUT.glob(f"walk-*-{flavor}.json")):
        device = path.name[len("walk-"):-len(f"-{flavor}.json")]
        results = json.loads(path.read_text(encoding="utf-8"))["results"]
        devices[device] = {xpath: {"status": value["status"]} for xpath, value in results.items()
                           if value["status"] in ("streamed", "invalid")}
    return {"flavor": flavor, "devices": devices}


def keep(flavor: str, device: str, nodes: list[dict], exclude: set[str]) -> list[dict]:
    results = fleet_results(flavor, exclude | {device})
    xpaths = set().union(*[set(r) for r in results]) if results else set()
    invalid = {x for x in xpaths if all(r.get(x, {}).get("status") == "invalid" for r in results)}
    streamed = {x for x in xpaths if any(r.get(x, {}).get("status") == "streamed" for r in results)}
    tree = config_root(device) if flavor in CONFIG_FLAVORS else None
    kept = []
    for node in nodes:
        xp = node["xpath"]
        # Configured wins: a model other devices lack (e.g. wireless on a WLC) is invalid everywhere else.
        if tree is not None and configured(tree, xp):
            kept.append(node)
        elif xp in streamed and xp not in invalid:
            kept.append(node)
    return kept


def catalog_nodes(flavor: str) -> list[dict]:
    catalog = json.loads((OUT / "subscribable-nodes.json").read_text(encoding="utf-8"))
    return [{**entry, "module": module}
            for module, entries in catalog["modules"].items()
            for entry in entries if entry.get("category") == flavor]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--device", required=True, help="device PID whose config capture is used (config-<PID>.json)")
    ap.add_argument("--flavor", required=True, choices=FLAVORS)
    ap.add_argument("--out", help="write the pruned catalog (walk_xpaths.py --catalog format)")
    ap.add_argument("--validate", help="walked device to leave out: report how many of its streamed xpaths are kept")
    args = ap.parse_args()

    nodes = catalog_nodes(args.flavor)
    kept = keep(args.flavor, args.device, nodes, exclude={args.validate} if args.validate else set())
    print(f"{args.flavor}: {len(nodes)} catalog xpaths -> {len(kept)} kept")
    if args.validate:
        walked = json.loads((OUT / f"walk-{args.validate}-{args.flavor}.json").read_text(encoding="utf-8"))["results"]
        streamed = {x for x, v in walked.items() if v["status"] == "streamed"}
        missed = sorted(streamed - {n["xpath"] for n in kept})
        print(f"recall: {len(streamed) - len(missed)}/{len(streamed)} streamed xpaths kept; missed: {missed[:10]}")
    if args.out:
        write_catalog(kept, Path(args.out))
    return 0


def write_catalog(nodes: list[dict], path: Path) -> None:
    """Write nodes in walk_xpaths.py --catalog format."""
    modules: dict[str, list] = {}
    for node in nodes:
        modules.setdefault(node["module"], []).append({k: v for k, v in node.items() if k != "module"})
    path.write_text(json.dumps({"version": "pruned", "modules": modules}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
