"""Every generated spec states the release it belongs to in info.version.

The oper/cfg/ietf/openconfig/native generators used to stamp "17.18.1" into every
release, so the viewers showed the wrong release. RPC (YANG revision dates) and
MIB/other (1.0.0) carry their own scheme and are not checked.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CATEGORIES = ("oper", "cfg", "ietf", "openconfig", "native-config")
INFO_VERSION = re.compile(r'"info"\s*:\s*\{.*?"version"\s*:\s*"([^"]+)"', re.S)
RELEASES = [r["ver"] for r in json.loads((REPO / "releases" / "index.json").read_text(encoding="utf-8"))["releases"]]


@pytest.mark.parametrize("release", RELEASES)
def test_info_version_matches_release(release: str) -> None:
    wrong = []
    for category in CATEGORIES:
        for spec in sorted((REPO / "releases" / release / f"swagger-{category}-model" / "api").glob("*.json")):
            if spec.name in ("manifest.json", "_paths_index.json"):
                continue
            with open(spec, encoding="utf-8") as handle:
                match = INFO_VERSION.search(handle.read(20000))
            if not match or match.group(1) != release:
                wrong.append(f"{spec.relative_to(REPO).as_posix()}: {match.group(1) if match else 'no info.version'}")
    assert not wrong, f"{len(wrong)} spec(s) with the wrong info.version:\n  " + "\n  ".join(wrong[:20])
