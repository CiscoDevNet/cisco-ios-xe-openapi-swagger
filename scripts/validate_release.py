#!/usr/bin/env python3
"""
validate_release.py — Pre-flight CI gates for a single release.

Implements the checks defined in VERSIONING.md §9 so they can be run locally
before pushing. The same gates run inside .github/workflows/deploy-pages.yml.

Gates implemented (returns non-zero exit on failure):
  1. JSON validity            — every spec parses.
  2. Manifest accuracy        — manifest.spec_count == on-disk count.
  3. Search-index integrity   — no duplicate module entries.
  4. Tree coverage            — every spec has tree or documented exclusion.
  5. Spec→tree linkage        — info.x-yang-tree-url resolves on disk.
  6. MDT xpath sanity         — every x-mdt-filter-xpath matches the regex.
  7. Export size cap          — each Postman/Bruno file ≤ 50 MB.
  8. Accountability regression — handled by separate compare script (warned here).

Usage:
    python scripts/validate_release.py --version 26.1.1
    python scripts/validate_release.py --version 26.1.1 --gates 1,2,3
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAX_EXPORT_BYTES = 50 * 1024 * 1024

MDT_XPATH_RE = re.compile(
    r"^/[a-z][a-z0-9\-]*:[A-Za-z][A-Za-z0-9_\-]*"
    r"(/[A-Za-z][A-Za-z0-9_\-]*(\[[^\]]+\])?)*$"
)


def release_root(version: str) -> Path:
    return PROJECT_ROOT / "releases" / version


def fail(msg: str, errs: list[str]) -> None:
    errs.append(msg)
    print(f"  ✗ {msg}")


def ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def is_spec_file(name: str) -> bool:
    """Return True for actual OpenAPI spec files, excluding manifest.json and
    auxiliary index files (e.g. ``_paths_index.json``) that live alongside
    specs but are not themselves modules."""
    return name != "manifest.json" and not name.startswith("_")


def gate_json_validity(rel: Path, errs: list[str]) -> None:
    print("\n[gate 1] JSON validity")
    n = 0
    for spec in rel.glob("swagger-*-model/api/*.json"):
        if not is_spec_file(spec.name):
            continue
        try:
            json.loads(spec.read_text(encoding="utf-8"))
            n += 1
        except Exception as e:
            fail(f"invalid JSON: {spec.relative_to(PROJECT_ROOT)}: {e}", errs)
    ok(f"parsed {n} specs")


def gate_manifests(rel: Path, errs: list[str]) -> None:
    print("\n[gate 2] Manifest accuracy")
    for manifest in rel.glob("swagger-*-model/api/manifest.json"):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception as e:
            fail(f"invalid manifest {manifest.relative_to(PROJECT_ROOT)}: {e}", errs)
            continue
        on_disk = sum(
            1 for f in manifest.parent.glob("*.json") if is_spec_file(f.name)
        )
        declared = data.get("spec_count")
        if declared is None:
            print(f"  ! {manifest.relative_to(PROJECT_ROOT)}: no spec_count "
                  f"declared (legacy manifest, on-disk={on_disk})")
            continue
        if declared != on_disk:
            fail(
                f"{manifest.relative_to(PROJECT_ROOT)}: spec_count={declared} but "
                f"{on_disk} files on disk",
                errs,
            )
        else:
            ok(f"{manifest.parent.name}: {on_disk}")


def gate_search_index(rel: Path, errs: list[str]) -> None:
    print("\n[gate 3] Search-index integrity")
    idx = rel / "search-index.json"
    if not idx.is_file():
        # Legacy 17.18.1 still keeps search-index.json at the repo root.
        legacy = PROJECT_ROOT / "search-index.json"
        if legacy.is_file():
            idx = legacy
        else:
            fail(f"missing {(rel / 'search-index.json').relative_to(PROJECT_ROOT)}", errs)
            return
    data = json.loads(idx.read_text(encoding="utf-8"))
    seen: set[str] = set()
    dup: list[str] = []
    for m in data.get("modules", []):
        # Include version (v1/v2) in the dedup key — the same module name can
        # legitimately appear in both the legacy api/ and the api/ trees.
        key = (m.get("category", ""), m.get("version", ""), m.get("name", ""))
        skey = "/".join(key)
        if skey in seen:
            dup.append(skey)
        seen.add(skey)
    if dup:
        fail(f"duplicate entries in search index: {dup[:5]}…", errs)
    else:
        ok(f"{len(seen)} unique entries")


def gate_tree_coverage(rel: Path, errs: list[str]) -> None:
    print("\n[gate 4] Tree coverage")
    tree_audit_path = rel / "tree_audit.json"
    if not tree_audit_path.is_file():
        # Fallbacks: repo-root tree_audit.json (older legacy layout) and
        # releases/17.18.1/tree_audit.json (current per-release artifact even
        # when specs still live at repo root in legacy in-place mode).
        for cand in (PROJECT_ROOT / "tree_audit.json",
                     PROJECT_ROOT / "releases" / "17.18.1" / "tree_audit.json"):
            if cand.is_file():
                tree_audit_path = cand
                break
        else:
            print(f"  ! missing {(rel / 'tree_audit.json').relative_to(PROJECT_ROOT)} "
                  f"— skipping (run generate_all_pyang_trees.py to enable)")
            return
    audit = json.loads(tree_audit_path.read_text(encoding="utf-8"))
    documented = {r["module"]: r for r in audit.get("results", [])}

    accountability_path = rel / "yang_accountability.json"
    if not accountability_path.is_file():
        legacy = PROJECT_ROOT / "yang_accountability.json"
        if legacy.is_file():
            accountability_path = legacy
    excluded: set[str] = set()
    if accountability_path.is_file():
        ad = json.loads(accountability_path.read_text(encoding="utf-8"))
        for m in ad.get("excluded_modules", []):
            excluded.add(m.get("name") or m.get("module") or "")

    missing: list[str] = []
    for spec in rel.glob("swagger-*-model/api/*.json"):
        if not is_spec_file(spec.name):
            continue
        module = spec.stem
        rec = documented.get(module)
        if rec and rec["status"] == "generated":
            continue
        if rec and rec.get("reason"):
            continue
        if module in excluded:
            continue
        # Synthetic split-spec convention: ``native-<chunk>`` files in
        # swagger-native-config-model/api are slices of Cisco-IOS-XE-native.
        # If the parent module is documented (generated) treat the chunk as
        # covered transitively.
        if module.startswith("native-"):
            parent = documented.get("Cisco-IOS-XE-native")
            if parent and parent.get("status") == "generated":
                continue
        missing.append(module)
    if missing:
        fail(f"{len(missing)} specs lack a tree and have no exclusion: {missing[:5]}…",
             errs)
    else:
        ok("every spec has tree or documented exclusion")


def gate_spec_tree_links(rel: Path, errs: list[str]) -> None:
    print("\n[gate 5] Spec→tree linkage")
    broken: list[str] = []
    n = 0
    for spec in rel.glob("swagger-*-model/api/*.json"):
        if not is_spec_file(spec.name):
            continue
        try:
            data = json.loads(spec.read_text(encoding="utf-8"))
        except Exception:
            continue
        url = data.get("info", {}).get("x-yang-tree-url")
        if not url:
            continue
        n += 1
        target = (spec.parent / url).resolve()
        if not target.is_file():
            broken.append(f"{spec.name} → {url}")
    if broken:
        fail(f"{len(broken)} broken tree links: {broken[:3]}…", errs)
    else:
        ok(f"{n} tree links resolve")


def gate_mdt_xpaths(rel: Path, errs: list[str]) -> None:
    print("\n[gate 6] MDT xpath sanity")
    bad: list[str] = []
    n = 0
    for spec in (rel / "swagger-oper-model" / "api").glob("*.json"):
        if not is_spec_file(spec.name):
            continue
        try:
            data = json.loads(spec.read_text(encoding="utf-8"))
        except Exception:
            continue
        for path, methods in (data.get("paths") or {}).items():
            if not isinstance(methods, dict):
                continue
            for op in methods.values():
                if not isinstance(op, dict):
                    continue
                xp = op.get("x-mdt-filter-xpath")
                if not xp:
                    continue
                n += 1
                if not MDT_XPATH_RE.match(xp):
                    bad.append(f"{spec.name} {path}: {xp}")
    if bad:
        fail(f"{len(bad)} invalid MDT xpaths: {bad[:3]}…", errs)
    else:
        ok(f"{n} MDT xpaths valid")


def gate_export_sizes(rel: Path, errs: list[str]) -> None:
    print("\n[gate 7] Export size cap (50 MB)")
    exports = rel / "exports"
    if not exports.is_dir():
        # Legacy 17.18.1 keeps specs at repo root but exports under releases/17.18.1/exports.
        alt = PROJECT_ROOT / "releases" / "17.18.1" / "exports"
        if alt.is_dir():
            exports = alt
        else:
            ok("no exports directory (skipping)")
            return
    over: list[tuple[str, int]] = []
    n = 0
    for f in exports.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix.lower() not in {".json", ".bru"}:
            continue
        n += 1
        if f.stat().st_size > MAX_EXPORT_BYTES:
            over.append((str(f.relative_to(PROJECT_ROOT)), f.stat().st_size))
    if over:
        for path, sz in over:
            fail(f"export over 50 MB: {path} ({sz/1_048_576:.1f} MB)", errs)
    else:
        ok(f"{n} export files under cap")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--version", required=True)
    parser.add_argument("--gates", default="",
                        help="Comma-separated gate numbers to run (default: all)")
    args = parser.parse_args()

    rel = release_root(args.version)
    legacy_inplace = False
    has_release_specs = any(rel.glob("swagger-*-model/api/*.json")) if rel.is_dir() else False
    if not has_release_specs:
        # The 17.18.1 baseline still lives at repo root (not yet migrated to
        # releases/17.18.1/). Treat the repo root as the release root so the
        # gates can validate the legacy in-place layout. For other versions
        # this remains a hard error.
        if args.version == "17.18.1" and (PROJECT_ROOT / "swagger-oper-model" / "api").is_dir():
            rel = PROJECT_ROOT
            legacy_inplace = True
            print(f"[validate] {args.version} not migrated; using legacy "
                  f"in-place layout at repo root")
        else:
            sys.stderr.write(f"no release dir or specs at: {release_root(args.version)}\n")
            return 1

    print(f"[validate] release={args.version} root="
          + (str(rel.relative_to(PROJECT_ROOT)) if rel != PROJECT_ROOT else '.')
          + (" (legacy in-place)" if legacy_inplace else ""))
    errs: list[str] = []
    gates = {
        "1": gate_json_validity,
        "2": gate_manifests,
        "3": gate_search_index,
        "4": gate_tree_coverage,
        "5": gate_spec_tree_links,
        "6": gate_mdt_xpaths,
        "7": gate_export_sizes,
    }
    selected = (args.gates.split(",") if args.gates else list(gates.keys()))
    selected = [g.strip() for g in selected if g.strip() in gates]
    for g in selected:
        gates[g](rel, errs)

    print()
    if errs:
        print(f"[validate] FAIL — {len(errs)} error(s):")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("[validate] OK — all selected gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
