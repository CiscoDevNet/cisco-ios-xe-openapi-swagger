"""Each release's oper specs must carry the MDT annotations listed in telemetry-index.json.

Fix drift with:
    python scripts/annotate_mdt_xpaths.py --version <ver>
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASES = sorted(path.parent.name for path in (REPO_ROOT / "releases").glob("*/telemetry-index.json"))


@pytest.mark.parametrize("version", RELEASES)
def test_specs_match_telemetry_index(version):
    release_dir = REPO_ROOT / "releases" / version
    index = json.loads((release_dir / "telemetry-index.json").read_text(encoding="utf-8"))
    expected = {(entry["module"], entry["operation_path"], entry["filter_xpath"]) for entry in index["entries"]}

    annotated = set()
    for spec_path in (release_dir / "swagger-oper-model" / "api").glob("*.json"):
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        for path, methods in spec.get("paths", {}).items():
            for operation in methods.values():
                if isinstance(operation, dict) and "x-mdt-filter-xpath" in operation:
                    annotated.add((spec_path.stem, path, operation["x-mdt-filter-xpath"]))

    assert annotated == expected
