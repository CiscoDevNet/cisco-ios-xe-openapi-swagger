"""Generated OpenConfig specs are valid OpenAPI 3.0 and every templated path declares its parameters.

The pre-2026-11 regex generator shipped 19 of 43 specs that failed validation (path templates
without parameters). generate_openconfig_from_yang.py fixed that; this keeps it fixed.
"""
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
RELEASES = json.loads((REPO / "releases" / "index.json").read_text(encoding="utf-8"))["releases"]
SPECS = sorted(
    spec
    for release in RELEASES
    for spec in (REPO / "releases" / release["ver"] / "swagger-openconfig-model" / "api").glob("openconfig-*.json")
)


@pytest.mark.parametrize("spec", SPECS, ids=lambda p: f"{p.parts[-4]}/{p.stem}")
def test_openconfig_spec_is_valid_openapi(spec):
    validator = pytest.importorskip("openapi_spec_validator")
    validator.validate(json.loads(spec.read_text(encoding="utf-8")))


@pytest.mark.parametrize("spec", SPECS, ids=lambda p: f"{p.parts[-4]}/{p.stem}")
def test_openconfig_path_parameters_match_templates(spec):
    doc = json.loads(spec.read_text(encoding="utf-8"))
    problems = []
    for path, operations in doc["paths"].items():
        template = sorted(re.findall(r"\{([^}]+)\}", path))
        for method, operation in operations.items():
            declared = sorted(p["name"] for p in operation.get("parameters", []) if p.get("in") == "path")
            if declared != template:
                problems.append((method, path))
    assert not problems, problems[:5]


def test_every_release_has_openconfig_specs():
    assert SPECS, "no OpenConfig specs found"
    per_release = {release["ver"]: 0 for release in RELEASES}
    for spec in SPECS:
        per_release[spec.parts[-4]] += 1
    assert all(count >= 15 for count in per_release.values()), per_release
