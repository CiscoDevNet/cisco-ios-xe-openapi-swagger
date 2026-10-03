"""yang_accountability.json must not report false gaps or non-modules.

Fix drift with:
    python scripts/patch_excluded_reasons.py
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from patch_excluded_reasons import ACCOUNTABILITY_FILES, recompute_totals  # noqa: E402

FILES = [path for path in ACCOUNTABILITY_FILES if path.is_file()]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_no_helper_indexes_counted_as_modules(path):
    helper_entries = [m["name"] for m in _load(path)["modules"] if m["name"].startswith("_")]
    assert not helper_entries


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_notification_modules_point_to_catalog(path):
    unexplained = [
        m["name"] for m in _load(path)["modules"]
        if m["classification"] == "events" and not m["has_spec"] and not m["reason_excluded"]
    ]
    assert not unexplained


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_summary_totals_match_modules(path):
    data = _load(path)
    expected = copy.deepcopy(data)
    recompute_totals(expected)
    assert data == expected
