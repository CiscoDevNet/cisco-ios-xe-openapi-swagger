"""Schema sanity tests for all manifest.json files.

Run with: python -X utf8 -m pytest tests/test_manifest_schema.py -v

Catches the regression we hit in this session where release manifests had a
different schema (modules-as-objects, missing total_paths) than the default
spec dirs, which crashed viewers with "Cannot read properties of undefined".
"""
from __future__ import annotations
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

MANIFESTS = sorted(
    list(ROOT.glob("releases/*/swagger-*-model/api-v2/manifest.json"))
    + list(ROOT.glob("swagger-*-model/api-v2/manifest.json"))
)

REQUIRED_INT_KEYS = ("total_modules", "total_paths", "total_operations", "spec_count")


@pytest.mark.parametrize("manifest_path", MANIFESTS, ids=lambda p: str(p.relative_to(ROOT)))
def test_manifest_schema(manifest_path: Path) -> None:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    for key in REQUIRED_INT_KEYS:
        assert key in data, f"missing key {key!r}"
        assert isinstance(data[key], int), f"{key!r} must be int, got {type(data[key]).__name__}"
        assert data[key] >= 0, f"{key!r} must be >= 0"

    assert "modules" in data, "missing key 'modules'"
    assert isinstance(data["modules"], list), "'modules' must be a list"
    for i, m in enumerate(data["modules"]):
        assert isinstance(m, str), f"modules[{i}] must be str (flat basenames), got {type(m).__name__}"

    # Counts must agree.
    assert data["spec_count"] == data["total_modules"] == len(data["modules"]), (
        f"spec_count/total_modules/len(modules) disagree: "
        f"{data['spec_count']}/{data['total_modules']}/{len(data['modules'])}"
    )

    # Every listed module must resolve to a sibling .json spec file.
    api_dir = manifest_path.parent
    for m in data["modules"]:
        spec_file = api_dir / f"{m}.json"
        assert spec_file.is_file(), f"manifest references missing spec file {spec_file.relative_to(ROOT)}"


def test_manifest_set_nonempty() -> None:
    assert MANIFESTS, "no manifest.json files discovered — repo layout changed?"
