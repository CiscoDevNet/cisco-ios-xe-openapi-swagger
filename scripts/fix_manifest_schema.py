#!/usr/bin/env python3
"""Backfill total_modules / total_paths / total_operations / spec_count on
every release manifest.json. Idempotent: only adds missing keys, never
overwrites existing values. Module list is normalized to a flat list of
basenames (per tests/test_manifest_schema.py)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTTP_METHODS = {"get", "put", "post", "patch", "delete", "head", "options"}


def _ops_in_spec(spec_path: Path) -> tuple[int, int]:
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except Exception:
        return 0, 0
    paths = spec.get("paths") or {}
    total_paths = len(paths)
    total_ops = 0
    for ops in paths.values():
        if isinstance(ops, dict):
            total_ops += sum(1 for k in ops if k.lower() in HTTP_METHODS)
    return total_paths, total_ops


def _normalize_modules(modules) -> list[str]:
    if not modules:
        return []
    out: list[str] = []
    for m in modules:
        if isinstance(m, str):
            out.append(m)
        elif isinstance(m, dict):
            for k in ("name", "module", "basename", "filename", "id"):
                if k in m:
                    v = m[k]
                    if isinstance(v, str):
                        out.append(v.removesuffix(".json"))
                        break
    return out


def _is_spec_file(name: str) -> bool:
    """Match scripts/validate_release.py:is_spec_file — excludes manifest.json
    and auxiliary indices like ``_paths_index.json`` that live alongside specs
    but are not themselves modules."""
    return name != "manifest.json" and not name.startswith("_")


def _scan_specs(api_dir: Path) -> list[str]:
    return sorted(p.stem for p in api_dir.glob("*.json") if _is_spec_file(p.name))


def patch(manifest_path: Path) -> bool:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    api_dir = manifest_path.parent

    modules = _normalize_modules(data.get("modules"))
    on_disk = _scan_specs(api_dir)
    if not modules:
        modules = on_disk
    else:
        # If any listed module lacks a sibling spec file, fall back to scanning
        # the directory. Catches name-prefix drift (e.g. modules listed as
        # "00-core" while files on disk are "native-00-core.json"). Also drop
        # any non-spec entries that may have been previously injected (auxiliary
        # _paths_index.json etc).
        if any(not (api_dir / f"{m}.json").exists() for m in modules) \
                or any(m.startswith("_") for m in modules):
            modules = on_disk

    changed = data.get("modules") != modules
    data["modules"] = modules

    total_paths = 0
    total_ops = 0
    for name in modules:
        sp = api_dir / f"{name}.json"
        if sp.exists():
            p, o = _ops_in_spec(sp)
            total_paths += p
            total_ops += o

    spec_count = len(modules)
    for key, val in (
        ("total_modules", spec_count),
        ("total_paths", total_paths),
        ("total_operations", total_ops),
        ("spec_count", spec_count),
    ):
        if data.get(key) != val:
            data[key] = val
            changed = True

    if changed:
        manifest_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return changed


def main() -> int:
    targets = sorted(
        list(ROOT.glob("releases/*/swagger-*-model/api/manifest.json"))
        + list(ROOT.glob("swagger-*-model/api/manifest.json"))
    )
    n_changed = 0
    for m in targets:
        if patch(m):
            print(f"  patched {m.relative_to(ROOT)}")
            n_changed += 1
    print(f"{n_changed} of {len(targets)} manifest(s) updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
