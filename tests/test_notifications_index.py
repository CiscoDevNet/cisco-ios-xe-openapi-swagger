"""Guards for the cross-model notification capability index.

`generators/generate_notifications_index.py` scans every resolved YANG tree in
a release and catalogs each module's `notification` nodes into
`releases/<ver>/notifications.json` (with a root copy for the default release).

These tests verify the default-release index exists, is internally consistent,
and still captures known notification-bearing modules — in particular the
CISCO-CEF-MIB SNMP traps that motivated the feature, which must never silently
disappear again.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def _default_version() -> str:
    idx = json.loads((REPO / "releases" / "index.json").read_text(encoding="utf-8"))
    return idx["default"]


@pytest.fixture(scope="module")
def index() -> dict:
    ver = _default_version()
    path = REPO / "releases" / ver / "notifications.json"
    assert path.is_file(), (
        f"missing {path}. Generate it with: "
        f"python -X utf8 generators/generate_notifications_index.py --version {ver}"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def test_root_copy_matches_default_release(index):
    root = REPO / "notifications.json"
    assert root.is_file(), "root notifications.json (default-release copy) missing"
    root_data = json.loads(root.read_text(encoding="utf-8"))
    assert root_data["version"] == index["version"]
    assert root_data["totals"] == index["totals"]


def test_totals_are_consistent(index):
    modules = index["modules"]
    totals = index["totals"]
    assert totals["modules_with_notifications"] == len(modules)
    assert totals["total_notifications"] == sum(
        m["notification_count"] for m in modules
    )
    assert totals["total_notifications"] == sum(
        len(m["notifications"]) for m in modules
    )
    # Per-module count must match its notification list length.
    for m in modules:
        assert m["notification_count"] == len(m["notifications"]), m["module"]


def test_has_meaningful_coverage(index):
    # The feature is only worthwhile if it catalogs a substantial surface.
    assert index["totals"]["modules_with_notifications"] >= 100
    assert index["totals"]["total_notifications"] >= 400


def test_cef_mib_traps_present(index):
    cef = next((m for m in index["modules"] if m["module"] == "CISCO-CEF-MIB"), None)
    assert cef is not None, "CISCO-CEF-MIB notifications missing from index"
    assert cef["transport"] == "snmp-trap"
    assert cef["restconf_consumable"] is False
    names = {n["name"] for n in cef["notifications"]}
    # The four SNMP traps defined by CISCO-CEF-MIB.
    assert {
        "cefResourceFailure",
        "cefPeerStateChange",
        "cefPeerFIBStateChange",
        "cefInconsistencyDetection",
    } <= names


def test_transport_classification(index):
    for m in index["modules"]:
        assert m["transport"] in ("snmp-trap", "yang-push", "netconf-stream")
        if m["transport"] == "snmp-trap":
            # SNMP traps are not RESTCONF-subscribable.
            assert m["restconf_consumable"] is False
        # MIB modules must classify as SNMP traps.
        if m["category"] == "mib":
            assert m["transport"] == "snmp-trap"
