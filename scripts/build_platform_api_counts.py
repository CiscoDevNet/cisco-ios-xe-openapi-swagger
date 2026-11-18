#!/usr/bin/env python3
"""build_platform_api_counts.py — API counts per platform family (cat9k, asr1k, ...).

Joins every OpenAPI spec of a release with releases/<ver>/platform-support.json
(module membership per platform yang-set) and writes
releases/<ver>/platform-api-counts.json:

    {
      "release": "26.2.1",
      "all":       {"paths": N, "operations": M, "by_category": {...}},
      "platforms": [{"id": "cat9k", "label": ..., "family": ..., "modules": n,
                     "paths": N, "operations": M, "by_category": {...}}, ...],
      "unmapped":  {"specs": [...], "paths": n, "operations": m},
      "native_attribution": {...}
    }

Counting rules
- Paths and operations are UNIQUE per category: a path shipped in several
  specs (e.g. a curated native-00-* bundle and its native-aug-* source) counts
  once. Totals are therefore lower than release_counts.json, which sums specs.
- A non-native spec counts on a platform when its YANG module (info
  x-yang-module, else the file stem) is in that platform's yang-set.
- Native-config paths all live under /Cisco-IOS-XE-native:native, but ~130
  other modules augment that tree. Each native path is attributed to the
  augmenting module(s) by longest-prefix match against the harvested augment
  targets (harvest_native_augments.py). A native path counts on a platform when
  Cisco-IOS-XE-native is supported there and, if attributed, at least one
  attributing module is too.
- Specs whose module is not in any yang-set are reported under "unmapped" and
  are not counted on any platform. Deviations are not applied.

Usage:
    python -X utf8 scripts/build_platform_api_counts.py --version 26.2.1
    python -X utf8 scripts/build_platform_api_counts.py --all
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASES = ROOT / "releases"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import harvest_native_augments as harvest  # noqa: E402

HTTP_METHODS = {"get", "put", "post", "patch", "delete"}
NATIVE_MODULE = "Cisco-IOS-XE-native"
NATIVE_DIR = "swagger-native-config-model"
NATIVE_ROOT = NATIVE_MODULE + ":native"


def category_of(model_dir: str) -> str:
    return model_dir[len("swagger-"):-len("-model")]


def iter_specs(api_dir: Path):
    for fp in sorted(api_dir.glob("*.json")):
        if fp.name == "manifest.json" or fp.name.startswith("_"):
            continue
        try:
            yield fp, json.loads(fp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"  [warn] skip {fp.name}: {exc}", file=sys.stderr)


def native_prefix_map(version: str) -> dict[str, frozenset[str]]:
    """'ip/nat' -> {'Cisco-IOS-XE-nat'}: augment target + child name -> modules."""
    gen = harvest._load_tree_gen()
    origins: list[str] = []
    augments, _ = harvest.harvest_augments(gen, version, True, origins)
    prefixes: dict[str, set[str]] = defaultdict(set)
    for (target, children), module in zip(augments, origins):
        for child in children:
            prefixes["/".join(target[1:] + (child.name,))].add(module)
    return {k: frozenset(v) for k, v in prefixes.items()}


def native_segments(path: str) -> list[str]:
    tail = path.split(NATIVE_ROOT, 1)[-1]
    return [s.split("=", 1)[0] for s in tail.strip("/").split("/") if s]


def attribute(path: str, prefixes: dict[str, frozenset[str]]) -> frozenset[str]:
    segs = native_segments(path)
    for k in range(len(segs), 0, -1):
        hit = prefixes.get("/".join(segs[:k]))
        if hit:
            return hit
    return frozenset()


def build(version: str) -> dict:
    rel = RELEASES / version
    support = json.loads((rel / "platform-support.json").read_text(encoding="utf-8"))
    platforms = support["platforms"]
    known_modules = support["modules"]
    plat_modules = {p["id"]: set() for p in platforms}
    for mod, info in known_modules.items():
        for pid in info.get("platforms", []):
            plat_modules.setdefault(pid, set()).add(mod)

    # category -> path -> {"methods": set, "modules": set of requirement sets}
    paths: dict[str, dict[str, dict]] = defaultdict(dict)
    unmapped_specs: list[str] = []
    prefixes = None
    attributed = 0

    for api_dir in sorted(rel.glob("swagger-*-model/api")):
        model_dir = api_dir.parent.name
        cat = category_of(model_dir)
        is_native = model_dir == NATIVE_DIR
        if is_native and prefixes is None:
            prefixes = native_prefix_map(version)
        for fp, spec in iter_specs(api_dir):
            module = (spec.get("info") or {}).get("x-yang-module") or fp.stem
            if is_native:
                module = NATIVE_MODULE
            elif module not in known_modules:
                unmapped_specs.append(f"{cat}/{fp.stem}")
                module = None
            for p, item in (spec.get("paths") or {}).items():
                methods = {m for m in (item or {}) if m in HTTP_METHODS}
                entry = paths[cat].setdefault(p, {"methods": set(), "module": module})
                entry["methods"] |= methods
                if entry["module"] is None and module is not None:
                    entry["module"] = module
                if is_native and "augment" not in entry:
                    entry["augment"] = attribute(p, prefixes)
                    if entry["augment"]:
                        attributed += 1

    def tally(selector) -> dict:
        out = {"paths": 0, "operations": 0, "by_category": {}}
        for cat in sorted(paths):
            cp = co = 0
            for p, entry in paths[cat].items():
                if selector(entry):
                    cp += 1
                    co += len(entry["methods"])
            if cp:
                out["by_category"][cat] = {"paths": cp, "operations": co}
            out["paths"] += cp
            out["operations"] += co
        return out

    def supported_on(pid: str):
        mods = plat_modules.get(pid, set())

        def sel(entry):
            if entry["module"] is None or entry["module"] not in mods:
                return False
            aug = entry.get("augment")
            return not aug or bool(aug & mods)
        return sel

    unmapped = tally(lambda e: e["module"] is None)
    result = {
        "release": version,
        "method": ("Unique paths/operations per category. A spec counts on a platform when its "
                   "YANG module is in that platform's yang-set; native-config paths also require "
                   "the augmenting module. Deviations not applied."),
        "all": tally(lambda e: True),
        "platforms": [],
        "unmapped": {"specs": sorted(unmapped_specs),
                     "paths": unmapped["paths"], "operations": unmapped["operations"]},
        "native_attribution": {
            "paths": len(paths.get(category_of(NATIVE_DIR), {})),
            "augment_attributed": attributed,
            "augment_prefixes": len(prefixes or {}),
        },
    }
    for p in platforms:
        counts = tally(supported_on(p["id"]))
        result["platforms"].append({
            "id": p["id"], "label": p.get("label", p["id"]), "family": p.get("family", "other"),
            "modules": len(plat_modules.get(p["id"], ())), **counts,
        })
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="append", help="release (repeatable)")
    ap.add_argument("--all", action="store_true", help="every release in releases/index.json")
    args = ap.parse_args()

    if args.all:
        index = json.loads((RELEASES / "index.json").read_text(encoding="utf-8"))
        versions = [r["ver"] for r in index["releases"]]
    elif args.version:
        versions = args.version
    else:
        ap.error("pass --version <v> or --all")

    for ver in versions:
        if not (RELEASES / ver / "platform-support.json").is_file():
            print(f"[skip] {ver}: no platform-support.json")
            continue
        data = build(ver)
        out = RELEASES / ver / "platform-api-counts.json"
        out.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
        cat9k = next((p for p in data["platforms"] if p["id"] == "cat9k"), None)
        print(f"[ok] {ver}: all {data['all']['paths']:,} paths / {data['all']['operations']:,} ops"
              + (f"; cat9k {cat9k['paths']:,} / {cat9k['operations']:,}" if cat9k else "")
              + f"; unmapped specs {len(data['unmapped']['specs'])} -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
