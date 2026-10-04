"""releases/compare/ must cover every adjacent release pair and stay internally consistent.

Regenerate with:
    python scripts/build_release_compare.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPARE = REPO_ROOT / "releases" / "compare"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


VERSIONS = [r["ver"] for r in _load(REPO_ROOT / "releases" / "index.json")["releases"]]
PAIRS = [(VERSIONS[i + 1], VERSIONS[i]) for i in range(len(VERSIONS) - 1)]


def test_index_lists_every_adjacent_pair():
    listed = {(p["old"], p["new"]) for p in _load(COMPARE / "index.json")["pairs"]}
    assert set(PAIRS) <= listed


@pytest.mark.parametrize("old,new", PAIRS, ids=lambda v: v)
def test_summary_matches_modules_and_details(old, new):
    data = _load(COMPARE / f"{old}__{new}.json")
    modules = data["modules"]
    summary = data["summary"]
    for status in ("added", "removed", "changed"):
        assert summary[status] == sum(1 for m in modules if m["status"] == status)
    with_schema = [m for m in modules if m.get("schema_counts")]
    assert summary["nodes_added"] == sum(m["schema_counts"]["added"] for m in with_schema)
    detail_dir = COMPARE / f"{old}__{new}"
    expected = {f"{m['name']}.json" for m in with_schema}
    assert {p.name for p in detail_dir.glob("*.json")} == expected
    for module in with_schema:
        detail = _load(detail_dir / f"{module['name']}.json")
        assert detail["nodes_added"] == module["schema_counts"]["added"]
        assert len(detail["changed"]) == module["schema_counts"]["changed"]


def test_known_26_2_1_changes():
    """Anchors from the published 26.1.1 -> 26.2.1 overview (release-comparisons/2621)."""
    data = _load(COMPARE / "26.1.1__26.2.1.json")
    by_name = {m["name"]: m for m in data["modules"]}
    assert by_name["Cisco-IOS-XE-ngfw-oper"]["status"] == "added"
    assert by_name["Cisco-IOS-XE-wireless-rrm-emul-oper"]["status"] == "removed"
    assert data["summary"]["changed"] == 336
    platforms = {p["id"]: p for p in data["platforms"]}
    assert (len(platforms["cat9k"]["added"]), len(platforms["cat9k"]["removed"])) == (15, 1)
