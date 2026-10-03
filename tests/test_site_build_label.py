"""The footer build label must name the latest CHANGELOG round.

SITE_BUILD in site-chrome.js sat at 'round 25' through rounds 26-32 because
nothing tied it to the changelog.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_footer_build_matches_latest_changelog_round():
    chrome = (REPO / "assets" / "js" / "site-chrome.js").read_text(encoding="utf-8")
    build = re.search(r"var SITE_BUILD = '[^']*\(round (\d+)\)'", chrome)
    assert build, "SITE_BUILD in site-chrome.js must end with '(round N)'"
    rounds = [int(n) for n in re.findall(r"^### .*\(round (\d+)", (REPO / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)]
    assert rounds, "no '(round N' headings found in CHANGELOG.md"
    assert int(build.group(1)) == max(rounds), (
        f"site-chrome.js SITE_BUILD says round {build.group(1)} but CHANGELOG latest is round {max(rounds)}"
    )
