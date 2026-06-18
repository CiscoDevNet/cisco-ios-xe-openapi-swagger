"""Guard test: keep the UI free of decorative emoji.

This is a developer-facing technical reference; emoji glyphs render as mojibake
on plenty of consoles and look like AI slop. The agreed convention is to keep
*functional* monochrome glyphs (favorites star, copy check, close X) and ban
everything else. See `AGENTS.md` -> "No emoji in UI or docs".
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# Code-point ranges considered "decorative emoji" for this repo.
BANNED_RE = re.compile(
    "[\U0001F000-\U0001FAFF\u2600-\u27BF\u2300-\u23FF\u2B00-\u2BFF]"
)

# Functional monochrome glyphs the UI relies on.
KEEP = {
    "\u2605",  # ★ BLACK STAR (favorites on)
    "\u2606",  # ☆ WHITE STAR (favorites off)
    "\u2713",  # ✓ CHECK MARK (copy confirmation)
    "\u2715",  # ✕ MULTIPLICATION X (close)
}

UI_FILES = [
    "index.html",
    "code-generator.html",
    "tree-compare.html",
    "yang-accountability.html",
    "yang-accountability-compare.html",
    "exports.html",
    "telemetry.html",
    "about.html",
    "404.html",
    "index-app.js",
    "code-generator.js",
    "search.js",
    "tree-compare.js",
    "yang-accountability.js",
    "recent-favorites.js",
    "hub-search-ops.js",
    "notifications.js",
]


def _viewer_files():
    out = []
    for d in REPO.glob("swagger-*-model"):
        out.extend(d.glob("*.html"))
        out.extend(d.glob("*.js"))
    return sorted(out)


def _all_targets():
    files = [REPO / p for p in UI_FILES if (REPO / p).is_file()]
    files.extend(_viewer_files())
    return files


@pytest.mark.parametrize("path", _all_targets(), ids=lambda p: str(p.relative_to(REPO)))
def test_no_decorative_emoji(path: Path):
    text = path.read_text(encoding="utf-8")
    bad = [c for c in text if BANNED_RE.match(c) and c not in KEEP]
    if bad:
        unique = sorted(set(bad))
        pytest.fail(
            f"{path.relative_to(REPO)}: {len(bad)} decorative emoji "
            f"({unique}). Run `python -X utf8 scripts/strip_emoji.py .` "
            f"or remove them by hand. See AGENTS.md."
        )


# Common mojibake fingerprints: UTF-8 bytes re-decoded as cp1252/Latin-1.
# Each entry is the literal characters that appear when this happens.
MOJIBAKE_NEEDLES = [
    "\u00E2\u2013\u00BC",   # ▼ written as UTF-8 then read as cp1252
    "\u00E2\u2013\u00BA",   # ►
    "\u00E2\u20AC\u0099",   # ’
    "\u00E2\u20AC\u009C",   # “
    "\u00E2\u20AC\u009D",   # ”
    "\u00E2\u20AC\u201C",   # –
    "\u00E2\u20AC\u201D",   # —
    "\u2261\u0192",          # cp437 misread of 4-byte emoji lead
]


@pytest.mark.parametrize("path", _all_targets(), ids=lambda p: str(p.relative_to(REPO)))
def test_no_mojibake(path: Path):
    text = path.read_text(encoding="utf-8")
    found = [n for n in MOJIBAKE_NEEDLES if n in text]
    if found:
        pytest.fail(
            f"{path.relative_to(REPO)}: mojibake sequence(s) present "
            f"{[ [hex(ord(c)) for c in n] for n in found ]}. "
            f"This usually means a file was written via PowerShell "
            f"`Set-Content -Encoding utf8` (which double-encodes). "
            f"Use Python `Path.write_text(..., encoding='utf-8', newline='\\n')` instead."
        )
