"""
_version_args.py — Shared version-aware path resolver for spec generators.

Each generator's ``main()`` calls ``resolve_paths(model_category)`` to obtain the
input YANG directory and the OpenAPI output directory for the requested release.

Layout:
- 17.18.1 ("legacy"): inputs ``references/17181-YANG-modules/``, outputs
  ``swagger-<cat>-model/api/`` (preserves existing behaviour).
- Any other version: inputs ``releases/<ver>/yang-source/``, outputs
  ``releases/<ver>/swagger-<cat>-model/api-v2/``.

Backward compatible: invoked with no ``--version`` argv it returns the legacy paths
unchanged, so generators called directly (without the orchestrator) keep working.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEGACY_VERSION = "17.18.1"


def _parse_version_arg() -> str:
    """Strip ``--version <v>`` from sys.argv if present and return v.

    Returns the legacy release string when the flag is absent so existing call
    sites remain a no-op.
    """
    argv = sys.argv
    for i, tok in enumerate(argv):
        if tok == "--version" and i + 1 < len(argv):
            ver = argv[i + 1]
            del argv[i:i + 2]
            return ver
        if tok.startswith("--version="):
            ver = tok.split("=", 1)[1]
            del argv[i]
            return ver
    return LEGACY_VERSION


def resolve_paths(model_category: str, *, mib_subdir: bool = False) -> tuple[Path, Path, str]:
    """Return ``(yang_dir, output_dir, version)``.

    ``model_category`` is the bare category (e.g. ``"oper"``, ``"native-config"``);
    used to derive the output folder name ``swagger-<model_category>-model``.

    Set ``mib_subdir=True`` for the MIB generator, which sources YANG from a
    ``MIBS/`` subdirectory of the YANG tree.
    """
    version = _parse_version_arg()
    if version == LEGACY_VERSION:
        yang_dir = PROJECT_ROOT / "references" / "17181-YANG-modules"
        if mib_subdir:
            yang_dir = yang_dir / "MIBS"
        output_dir = PROJECT_ROOT / f"swagger-{model_category}-model" / "api"
    else:
        # fetch_yang_release.py drops the upstream YANG tree at
        # ``references/<ver>/`` (the same convention legacy 17.18.1 uses,
        # just under the version folder). Prefer that; fall back to the
        # alternate ``releases/<ver>/yang-source`` path if it exists for
        # back-compat with older fetch scripts.
        primary = PROJECT_ROOT / "references" / version
        alt = PROJECT_ROOT / "releases" / version / "yang-source"
        yang_dir = primary if primary.is_dir() else alt
        if mib_subdir:
            yang_dir = yang_dir / "MIBS"
        output_dir = (PROJECT_ROOT / "releases" / version
                      / f"swagger-{model_category}-model" / "api-v2")
    output_dir.mkdir(parents=True, exist_ok=True)
    return yang_dir, output_dir, version
