"""Enumerate GET paths from the OpenAPI specs for the GET-phase categories.

Per DEVICE_DATA_COLLECTION.md §3/§4 the harness collects GET paths from four model
categories (oper + mib + cfg + native-config). Each category ships an
``api/manifest.json`` (a JSON array of module names) alongside one
``api/<module>.json`` OpenAPI 3.0 spec per module.

The default specs root is ``releases/26.1.1/`` (the versioned layout). If that
is absent (e.g. a stripped export), pass ``--specs-root`` to point at any
directory that contains ``swagger-<cat>-model/api/*.json`` (for offline
validation a flat pre-versioning copy works too).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

# Categories captured in the GET phase. rpc is POST-only (skipped); the rest are
# read-safe (cfg/native/openconfig/ietf/other are CRUD but GET returns config/state).
GET_CATEGORIES = ("oper", "mib", "cfg", "native-config", "openconfig", "ietf", "other")

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPECS_ROOT = REPO_ROOT / "releases" / "26.1.1"


@dataclass(frozen=True)
class GetPath:
    category: str
    module: str
    path: str  # OpenAPI/RESTCONF path string


class SpecsNotFoundError(RuntimeError):
    pass


def category_api_dir(specs_root: Path, category: str) -> Path:
    return Path(specs_root) / f"swagger-{category}-model" / "api"


def _module_names(api_dir: Path) -> list[str]:
    """Module list for a category: prefer manifest.json, else glob *.json."""
    manifest = api_dir / "manifest.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = None
        # Manifest may be a bare list of names, or {"modules": [...]}.
        if isinstance(data, dict):
            data = data.get("modules")
        if isinstance(data, list) and data:
            return [str(m) for m in data]
    # Fallback: every spec file except the manifest itself.
    return sorted(
        p.stem for p in api_dir.glob("*.json") if p.name != "manifest.json"
    )


def _is_capturable(path: str, method_map: dict) -> bool:
    """A path is GET-capturable if it declares a ``get`` operation and has no
    unresolved list-key placeholder (``={...}``) that we cannot fill blindly."""
    if not isinstance(method_map, dict):
        return False
    if "get" not in {k.lower() for k in method_map.keys()}:
        return False
    if "={" in path:
        # Keyed list entry — requires concrete key values we don't have.
        return False
    return True


def enumerate_category(
    specs_root: Path,
    category: str,
    roots_only: bool = False,
    modules: Optional[Iterable[str]] = None,
) -> list[GetPath]:
    """Return all capturable GET paths for one category.

    ``roots_only`` keeps only the shortest (root container) path per module —
    the fast mode from §4 where the subtree comes back in one GET.
    ``modules`` optionally restricts to a subset (used by the pilot).
    """
    api_dir = category_api_dir(specs_root, category)
    if not api_dir.is_dir():
        raise SpecsNotFoundError(
            f"Specs dir not found for category {category!r}: {api_dir}\n"
            f"Pass --specs-root to a directory containing swagger-{category}-model/api/."
        )

    wanted = set(modules) if modules else None

    # MIB special case: IOS XE mounts each MIB at /data/<module-name> and does NOT
    # serve the spec's /data/<MIB>:<table> paths (they return "uri keypath not
    # found"). One GET on /data/<module> returns the whole MIB, so emit exactly
    # that per module regardless of roots_only.
    if category == "mib":
        return [
            GetPath(category="mib", module=module, path=f"/data/{module}")
            for module in _module_names(api_dir)
            if wanted is None or module in wanted
        ]

    results: list[GetPath] = []
    for module in _module_names(api_dir):
        if wanted is not None and module not in wanted:
            continue
        spec_file = api_dir / f"{module}.json"
        if not spec_file.exists():
            continue
        try:
            spec = json.loads(spec_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        paths = spec.get("paths", {})
        if not isinstance(paths, dict):
            continue
        capturable = [p for p, m in paths.items() if _is_capturable(p, m)]
        if not capturable:
            continue
        if roots_only:
            # Shortest path = module root container.
            capturable = [min(capturable, key=len)]
        for p in capturable:
            results.append(GetPath(category=category, module=module, path=p))
    return results


def enumerate_get_paths(
    specs_root: Path,
    categories: Iterable[str] = GET_CATEGORIES,
    roots_only: bool = False,
    modules: Optional[Iterable[str]] = None,
) -> list[GetPath]:
    """Enumerate GET paths across all requested categories."""
    out: list[GetPath] = []
    for category in categories:
        out.extend(
            enumerate_category(
                specs_root, category, roots_only=roots_only, modules=modules
            )
        )
    return out


def resolve_specs_root(specs_root: Optional[str]) -> Path:
    """Resolve/validate the specs root, defaulting to releases/26.1.1/."""
    root = Path(specs_root) if specs_root else DEFAULT_SPECS_ROOT
    if not root.is_dir():
        raise SpecsNotFoundError(
            f"Specs root not found: {root}\n"
            "This export may be stripped. Point --specs-root at a directory that "
            "contains swagger-<cat>-model/api/*.json (e.g. releases/26.1.1 or a "
            "full repo copy)."
        )
    return root
