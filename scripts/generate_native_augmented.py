#!/usr/bin/env python3
"""generate_native_augmented.py

Supplemental native-config generator that closes the augment/uses coverage gap.

The shipped native specs are produced by generate_native_openapi_v2.py, a regex
parser of Cisco-IOS-XE-native.yang that does NOT resolve external `uses` whose
grouping lives in another module, nor the 1600+ `augment /native/...` subtrees
contributed by ~130 Cisco-IOS-XE-* modules. As a result whole branches are
missing or stubbed: snmp-server, line, ipv6, large parts of ip (nat/multicast/
igmp/...), router (isis/eigrp/ospfv3), license, parser, and more.

This generator builds the *fully augmented* native tree (see
harvest_native_augments.build_merged_native_tree) and emits RESTCONF paths for
every container/list down to a depth cap, EXCLUDING paths that already exist in
the shipped specs. The output is therefore purely additive — existing specs and
their ~11k paths are untouched; we only fill the holes.

Output files are named `native-aug-<top-level>.json` (split at ~5 MB) and are
picked up into the viewer manifest by scripts/fix_manifest_schema.py on the next
build.

Usage:
    # Size the output without writing anything:
    python -X utf8 scripts/generate_native_augmented.py --version 26.1.1 --dry-run
    # Write supplemental specs into the release api dir:
    python -X utf8 scripts/generate_native_augmented.py --version 26.1.1
    python -X utf8 scripts/generate_native_augmented.py --version 26.1.1 --no-interface
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NATIVE_PREFIX = "/data/Cisco-IOS-XE-native:native"
MAX_FILE_SIZE_MB = 5.0


def _load_module(rel_path: str, mod_name: str):
    p = ROOT / rel_path
    spec = importlib.util.spec_from_file_location(mod_name, p)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {p}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _existing_exact_paths(api_dir: Path) -> set[str]:
    """Every RESTCONF path already present in the shipped native specs."""
    out: set[str] = set()
    for fp in glob.glob(str(api_dir / "*.json")):
        if Path(fp).name == "manifest.json":
            continue
        try:
            spec = json.loads(Path(fp).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        out.update(spec.get("paths", {}).keys())
    return out


def _safe_name(top: str) -> str:
    return "".join(c if (c.isalnum() or c in "-_") else "-" for c in top.lower())


def _patch_manifest(api_dir: Path, new_modules: list[str]) -> None:
    """Register newly-written specs in the viewer manifest and recompute totals
    from disk. Mirrors scripts/generate_native_augment_specs.py:_patch_manifest
    so the supplemental specs are picked up without a full manifest rescan."""
    mp = api_dir / "manifest.json"
    if not mp.is_file():
        return
    manifest = json.loads(mp.read_text(encoding="utf-8"))
    modules = set(manifest.get("modules", []))
    modules.update(new_modules)
    manifest["modules"] = sorted(modules)
    total_paths = 0
    total_ops = 0
    for spec_file in sorted(api_dir.glob("*.json")):
        if spec_file.name == "manifest.json" or spec_file.name.startswith("_"):
            continue
        try:
            spec = json.loads(spec_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        paths = spec.get("paths") or {}
        total_paths += len(paths)
        for ops in paths.values():
            total_ops += sum(
                1 for k in ops if k.lower() in {"get", "put", "post", "patch", "delete"}
            )
    manifest["total_modules"] = len(manifest["modules"])
    manifest["spec_count"] = len(manifest["modules"])
    manifest["total_paths"] = total_paths
    manifest["total_operations"] = total_ops
    mp.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


# A small set of interface types that together cover the distinct config shapes
# (L3 physical, loopback, tunnel, SVI, aggregation, WAN). Modelling these once
# captures the full interface config surface without duplicating the same
# schema across all ~58 concrete types.
REPRESENTATIVE_INTERFACE_TYPES = (
    "GigabitEthernet", "Loopback", "Tunnel", "Vlan", "Port-channel", "Serial",
)


def _restrict_interface(gen, intf_node):
    """Return a shallow copy of the interface container keeping only the
    representative interface types (and any non-list children)."""
    clone = gen.TreeNode(intf_node.name, intf_node.rw, intf_node.node_type,
                         depth=intf_node.depth)
    clone.raw_name = intf_node.raw_name
    for c in intf_node.children:
        if c.node_type == "list" and c.name not in REPRESENTATIVE_INTERFACE_TYPES:
            continue
        clone.children.append(c)
    return clone


def generate(version: str, max_depth: int, interface_mode: str,
             dry_run: bool) -> int:
    gen = _load_module("generators/generate_native_from_tree.py", "_native_tree_gen")
    harvest = _load_module("scripts/harvest_native_augments.py", "_harvest_aug")

    api_dir = ROOT / "releases" / version / "swagger-native-config-model" / "api"
    if not api_dir.is_dir():
        sys.stderr.write(f"missing api dir: {api_dir}\n")
        return 2

    # Only harvest interface-targeting augments when we actually emit interface.
    root, stats = harvest.build_merged_native_tree(
        version, include_interface=(interface_mode != "skip"))
    existing = _existing_exact_paths(api_dir)

    # Walk each top-level child of native; collect deep paths; drop dups and
    # anything already shipped.
    per_top_new: dict[str, dict[str, object]] = {}  # top -> {path: node}
    total_candidates = 0
    for child in root.children:
        if child.node_type not in ("container", "list"):
            continue
        top = child.name

        if top == "interface":
            if interface_mode == "skip":
                continue
            if interface_mode == "representative":
                # Restrict the interface container to the representative types
                # so we model the config surface once, not ~58 times.
                child = _restrict_interface(gen, child)

        base = f"{NATIVE_PREFIX}/{top}"
        collected = gen.collect_deep_paths(child, base, max_depth=max_depth)
        # collect_deep_paths also handles list keyed paths internally for
        # descendants; for the top-level list itself add the keyed instance.
        bucket = per_top_new.setdefault(top, {})
        for path, node in collected:
            total_candidates += 1
            if node.node_type not in ("container", "list", "leaf", "leaf-list"):
                continue
            if path in existing or path in bucket:
                continue
            bucket[path] = node
        if child.node_type == "list":
            key_child = child.find_child("name") or child.find_child("id")
            if key_child:
                kpath = f"{base}={{{key_child.name}}}"
                if kpath not in existing and kpath not in bucket:
                    bucket[kpath] = child

    # Drop empty tops.
    per_top_new = {t: b for t, b in per_top_new.items() if b}

    grand_new = sum(len(b) for b in per_top_new.values())

    print(f"\n[{version}] supplemental native augment generation"
          f"  (max_depth={max_depth}, interface={interface_mode})")
    print(f"  merged tree descendants : {stats['total_descendants']}")
    print(f"  augments grafted        : {stats['augments_grafted']}")
    print(f"  existing shipped paths  : {len(existing)}")
    print(f"  NEW paths to add        : {grand_new}")
    print(f"  top-level groups w/ new : {len(per_top_new)}")
    print(f"  largest groups:")
    for top, b in sorted(per_top_new.items(), key=lambda kv: -len(kv[1]))[:20]:
        print(f"    {top:<26} {len(b)}")

    if dry_run:
        return 0

    # Build & write specs per top-level group, splitting at MAX_FILE_SIZE_MB.
    written: list[str] = []
    for top, bucket in sorted(per_top_new.items()):
        tag = top
        # Build all path-operation entries first.
        path_items = []
        for path, node in bucket.items():
            ops = gen.make_path_operations(path, node, tag)
            path_items.append((path, ops))

        # Greedy size-based chunking.
        chunks: list[list] = [[]]
        cur_bytes = 0
        for path, ops in path_items:
            entry_bytes = len(json.dumps({path: ops}).encode("utf-8"))
            if cur_bytes and (cur_bytes + entry_bytes) / (1024 * 1024) > MAX_FILE_SIZE_MB:
                chunks.append([])
                cur_bytes = 0
            chunks[-1].append((path, ops))
            cur_bytes += entry_bytes

        for idx, chunk in enumerate(chunks, start=1):
            if not chunk:
                continue
            paths_obj = {p: o for p, o in chunk}
            suffix = "" if len(chunks) == 1 else f"-{idx}"
            title = (f"Native (Augmented) - {top}" +
                     ("" if len(chunks) == 1 else f" (Part {idx})"))
            desc = (f"Augment/uses-resolved Native configuration for `{top}` — "
                    f"branches contributed by external Cisco-IOS-XE-* modules "
                    f"(augments) and cross-module groupings that the base native "
                    f"generator does not resolve. Generated from the merged YANG "
                    f"tree. **Paths:** {len(paths_obj)}.")
            spec = gen.create_spec(title, desc, tag, paths_obj, version=version)
            fname = f"native-aug-{_safe_name(top)}{suffix}.json"
            out_path = api_dir / fname
            out_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
            written.append(fname)

    _patch_manifest(api_dir, [Path(f).stem for f in written])

    print(f"\n  wrote {len(written)} supplemental spec file(s):")
    for f in written:
        print(f"    {f}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="26.1.1")
    ap.add_argument("--max-depth", type=int, default=5,
                    help="standalone-path depth cap (deeper nodes live in body "
                         "schemas). Default 5, matching the base generator.")
    ap.add_argument("--interface-mode", choices=["all", "representative", "skip"],
                    default="representative",
                    help="how to model the /native/interface mega-container: "
                         "'all' = every concrete type (~58, large); "
                         "'representative' = one type per distinct config shape "
                         "(default); 'skip' = leave interface as already shipped.")
    ap.add_argument("--dry-run", action="store_true",
                    help="report counts only; write nothing")
    args = ap.parse_args()
    return generate(args.version, args.max_depth,
                    interface_mode=args.interface_mode,
                    dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
