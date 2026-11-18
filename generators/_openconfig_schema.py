"""Load a release's OpenConfig YANG with pyang: augments resolved, Cisco IOS XE deviations applied.

Shared by the OpenConfig spec generator and the gNMI node catalog
(scripts/mdt-telemetry/collector/gnmi_oc_catalog.py) so both see the same schema.
"""
from __future__ import annotations

from pathlib import Path

from pyang import context, repository

# Platform-specific deviations would hide nodes other platforms serve.
EXCLUDED_DEVIATION_PREFIXES = ("cisco-xe-routing-", "cisco-xe-wireless-")
DATA_KEYWORDS = ("container", "list")
TRANSPARENT_KEYWORDS = ("choice", "case")


def yang_files(yang_dir: Path) -> tuple[list[Path], list[Path]]:
    """(modules, deviation modules): every openconfig-* file plus the generic Cisco OpenConfig ext/deviations."""
    modules, deviations = [], []
    for path in sorted(Path(yang_dir).glob("*.yang")):
        name = path.stem.split("@")[0]
        if name.startswith("openconfig-"):
            modules.append(path)
        elif name.startswith("cisco-xe-") and "openconfig" in name:
            if name.startswith(EXCLUDED_DEVIATION_PREFIXES):
                continue
            (deviations if name.endswith("-deviation") else modules).append(path)
    return modules, deviations


def load_context(yang_dir: Path):
    repo = repository.FileRepository(str(yang_dir), use_env=False)
    ctx = context.Context(repo)
    modules, deviations = yang_files(yang_dir)
    for path in modules + deviations:
        module = ctx.add_module(str(path), path.read_text(encoding="utf-8"))
        if module is not None and path in deviations:
            ctx.deviation_modules.append(module)
    ctx.validate()
    return ctx


def data_modules(ctx) -> list:
    """OpenConfig modules that define top-level data nodes (the only ones with RESTCONF/gNMI roots)."""
    found = []
    for module in sorted(ctx.modules.values(), key=lambda m: m.arg):
        if module.keyword != "module" or not module.arg.startswith("openconfig-"):
            continue
        if any(top.keyword in DATA_KEYWORDS and top.i_module.i_modulename == module.arg
               for top in getattr(module, "i_children", []) or []):
            found.append(module)
    return found


def top_nodes(module) -> list:
    return [top for top in getattr(module, "i_children", []) or []
            if top.keyword in DATA_KEYWORDS and top.i_module.i_modulename == module.arg]


def data_children(node) -> list:
    """Children with choice/case flattened (they are not data nodes)."""
    out = []
    for child in getattr(node, "i_children", []) or []:
        if child.keyword in TRANSPARENT_KEYWORDS:
            out.extend(data_children(child))
        elif child.keyword not in ("input", "output", "notification", "action", "rpc"):
            out.append(child)
    return out
