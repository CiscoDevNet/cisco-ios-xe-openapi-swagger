"""Regression guard against silent disappearance of APIs/operations/modules.

The repo ships [`release_counts.json`](../release_counts.json) — a deterministic
per-release / per-category snapshot of:

  - specs       (count of OpenAPI spec files under api/)
  - paths       (sum of len(spec["paths"]) across specs)
  - operations  (sum of HTTP-method operations under each path)
  - search_index.modules / categories
  - platform_support.modules / platforms

This test recomputes those counts live and **fails** if any of them dropped
since the baseline was captured. Growth is allowed and silent.

To refresh the baseline after a legitimate change (new release, intentional
deprecation), run:

    python -X utf8 scripts/release_counts.py --write

and commit the resulting release_counts.json change.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
BASELINE = REPO / "release_counts.json"

sys.path.insert(0, str(REPO / "scripts"))
from release_counts import compute_all, diff_snapshots  # noqa: E402


@pytest.fixture(scope="module")
def baseline() -> dict:
    assert BASELINE.is_file(), (
        f"missing baseline {BASELINE}. Generate it with: "
        f"python -X utf8 scripts/release_counts.py --write"
    )
    return json.loads(BASELINE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def current() -> dict:
    return compute_all()


def test_baseline_covers_all_known_releases(baseline: dict, current: dict) -> None:
    base_ids = set(baseline["releases"].keys())
    cur_ids = set(current["releases"].keys())
    missing_from_baseline = cur_ids - base_ids
    assert not missing_from_baseline, (
        f"Releases exist on disk but are not in release_counts.json baseline: "
        f"{sorted(missing_from_baseline)}. Run "
        f"`python -X utf8 scripts/release_counts.py --write` and commit."
    )


def test_no_release_disappeared(baseline: dict, current: dict) -> None:
    base_ids = set(baseline["releases"].keys())
    cur_ids = set(current["releases"].keys())
    gone = sorted(base_ids - cur_ids)
    assert not gone, (
        f"Release(s) in baseline are missing from releases/: {gone}. "
        f"Restore them or remove from baseline if intentional."
    )


def test_no_category_disappeared(baseline: dict, current: dict) -> None:
    losses: list[str] = []
    for ver, base_rel in baseline["releases"].items():
        if ver not in current["releases"]:
            continue
        cur_cats = set(current["releases"][ver]["categories"].keys())
        for cat in base_rel["categories"].keys():
            if cat not in cur_cats:
                losses.append(f"{ver}/{cat}")
    assert not losses, f"Category folder(s) disappeared: {losses}"


def test_no_spec_path_or_operation_count_dropped(baseline: dict, current: dict) -> None:
    issues = diff_snapshots(current, baseline)
    assert not issues, (
        f"{len(issues)} count regression(s) detected vs release_counts.json:\n  - "
        + "\n  - ".join(issues)
        + "\n\nIf this drop is intentional (e.g. deprecated module), refresh "
        "the baseline:\n  python -X utf8 scripts/release_counts.py --write"
    )


def test_default_release_has_minimum_coverage(current: dict) -> None:
    """Sanity floor for the default (latest) release. Hard minimums catch
    catastrophic regressions even if the baseline was accidentally refreshed
    after a bad regen."""
    idx_path = REPO / "releases" / "index.json"
    assert idx_path.is_file(), "releases/index.json missing"
    idx = json.loads(idx_path.read_text(encoding="utf-8"))
    default = idx.get("default")
    assert default in current["releases"], f"default release {default} not snapshotted"
    rel = current["releases"][default]
    assert rel["totals"]["specs"] >= 700, f"default release has {rel['totals']['specs']} specs (<700)"
    assert rel["totals"]["operations"] >= 80000, f"default release has {rel['totals']['operations']} operations (<80000)"
    assert rel["categories"].get("swagger-oper-model", {}).get("specs", 0) >= 200, (
        "swagger-oper-model lost specs in the default release"
    )
    ps_mods = (rel.get("platform_support") or {}).get("modules", 0)
    assert ps_mods >= 800, f"platform-support has {ps_mods} modules (<800)"
