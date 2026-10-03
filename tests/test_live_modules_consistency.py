"""live-modules.json (viewer banner summary) must match its live-examples-index.json.

Drift here hides the "Live device data" banner for whole devices/modules. Fix with:
    python scripts/build_live_examples_index.py --version <ver> --summary-only
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.build_live_examples_index import module_summary  # noqa: E402

RELEASES_WITH_INDEX = sorted(
    path.parent.name for path in (REPO_ROOT / "releases").glob("*/live-examples-index.json")
)


@pytest.mark.parametrize("version", RELEASES_WITH_INDEX)
def test_live_modules_matches_index(version):
    release_dir = REPO_ROOT / "releases" / version
    index = json.loads((release_dir / "live-examples-index.json").read_text(encoding="utf-8"))
    summary = json.loads((release_dir / "live-modules.json").read_text(encoding="utf-8"))
    assert summary == module_summary(index), (
        f"releases/{version}/live-modules.json is stale; regenerate with "
        f"build_live_examples_index.py --version {version} --summary-only"
    )
