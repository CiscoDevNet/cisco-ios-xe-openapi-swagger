"""Shared ``releases/<ver>/...`` path resolution for the version-aware scripts.

Imported (with this directory on ``sys.path``) by the export generators, MDT
annotator, MIB/native enrichers and version-stats builders.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RELEASES_DIR = PROJECT_ROOT / "releases"
RELEASE_INDEX = RELEASES_DIR / "index.json"

# The first multi-release version; its artifacts also existed at the repo root
# (swagger-*-model/api, references/17181-YANG-modules) before the migration.
LEGACY_VERSION = "17.18.1"
LEGACY_YANG_DIR = PROJECT_ROOT / "references" / "17181-YANG-modules"

MODEL_CATEGORIES = (
    "swagger-oper-model",
    "swagger-cfg-model",
    "swagger-native-config-model",
    "swagger-openconfig-model",
    "swagger-ietf-model",
    "swagger-mib-model",
    "swagger-other-model",
    "swagger-rpc-model",
)


@dataclass(frozen=True)
class ReleasePaths:
    version: str
    legacy: bool = False  # allow falling back to the pre-releases/ root layout

    @property
    def release_root(self) -> Path:
        return RELEASES_DIR / self.version

    def _is_legacy_release(self) -> bool:
        return self.legacy and self.version == LEGACY_VERSION

    def spec_dir(self, category: str) -> Path:
        scoped = self.release_root / category / "api"
        root_level = PROJECT_ROOT / category / "api"
        if not scoped.is_dir() and self._is_legacy_release() and root_level.is_dir():
            return root_level
        return scoped

    def exports_dir(self, kind: str | None = None) -> Path:
        base = self.release_root / "exports"
        return base / kind if kind else base

    def yang_source_dir(self) -> Path:
        candidates = [self.release_root / "yang-source", PROJECT_ROOT / "references" / self.version]
        if self.legacy:
            candidates.append(LEGACY_YANG_DIR)
        return next((c for c in candidates if c.is_dir()), candidates[0])

    def accountability_json(self) -> Path:
        scoped = self.release_root / "yang_accountability.json"
        root_level = PROJECT_ROOT / "yang_accountability.json"
        if not scoped.is_file() and self._is_legacy_release() and root_level.is_file():
            return root_level
        return scoped

    def telemetry_index(self) -> Path:
        return self.release_root / "telemetry-index.json"

    def telemetry_skipped(self) -> Path:
        return self.release_root / "telemetry-skipped.json"

    def native_capabilities(self) -> Path:
        return self.release_root / "native-capabilities.json"

    def mib_metadata(self) -> Path:
        return self.release_root / "mib-metadata.json"


def all_releases() -> list[dict]:
    """Every entry in releases/index.json (newest first, as listed)."""
    if not RELEASE_INDEX.is_file():
        return []
    return list(json.loads(RELEASE_INDEX.read_text(encoding="utf-8")).get("releases") or [])


def list_active_releases() -> list[str]:
    return [r["ver"] for r in all_releases() if r.get("status", "active") == "active"]
