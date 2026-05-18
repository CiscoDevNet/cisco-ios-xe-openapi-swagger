"""Upgrade `<div class="header|container|footer">` wrappers on the seven
top-level HTML pages to their semantic-landmark equivalents
(<header> / <main> / <footer>). Preserves the original class attribute so
existing CSS keeps working.

Idempotent: skips elements that are already a semantic landmark.

Usage:
    python scripts/upgrade_landmarks.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    "index.html",
    "code-generator.html",
    "tree-compare.html",
    "telemetry.html",
    "exports.html",
    "yang-accountability.html",
    "yang-accountability-compare.html",
    "404.html",
]

# Map class name → semantic tag name to wrap it as.
CLASS_TO_TAG = {
    "header": "header",
    "container": "main",   # the page's content wrapper
    "footer": "footer",
}


class _Finder(HTMLParser):
    """Locate the byte-offset of the matching close tag for a given
    opening div, accounting for nested divs along the way."""

    def __init__(self, target_start: int) -> None:
        super().__init__(convert_charrefs=False)
        self.target_start = target_start
        self.match_close_offset: int | None = None
        self._depth = 0
        self._started = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "div":
            return
        pos = self.getpos()
        # The opening div we care about
        if not self._started:
            self._started = True
            self._depth = 1
            return
        self._depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag != "div" or not self._started:
            return
        self._depth -= 1
        if self._depth == 0 and self.match_close_offset is None:
            # getpos() returns (line, col), 1-based
            self.match_close_offset = -1  # sentinel; we resolve via search


def _find_open_div(text: str, class_value: str, start: int = 0) -> int:
    """Return the byte index of the first `<div class="...{class_value}..."`
    occurrence (where class_value is a whole word in the class attribute)."""
    pattern = re.compile(
        r'<div\b[^>]*\bclass=(["\'])([^"\']*?\b'
        + re.escape(class_value)
        + r'\b[^"\']*?)\1[^>]*>'
    )
    m = pattern.search(text, start)
    return m.start() if m else -1


def _find_matching_close(text: str, open_idx: int) -> int:
    """Return the byte index of the `</div>` that closes the div whose
    `<` is at `open_idx`. Returns -1 if not found."""
    # Skip past the opening tag's '>'
    open_end = text.index(">", open_idx) + 1
    depth = 1
    pos = open_end
    open_re = re.compile(r"<div\b", re.I)
    close_re = re.compile(r"</div>", re.I)
    while True:
        next_open = open_re.search(text, pos)
        next_close = close_re.search(text, pos)
        if not next_close:
            return -1
        if next_open and next_open.start() < next_close.start():
            depth += 1
            pos = next_open.end()
        else:
            depth -= 1
            if depth == 0:
                return next_close.start()
            pos = next_close.end()


def _upgrade_one(text: str, class_value: str, semantic_tag: str) -> tuple[str, bool]:
    """Replace the first matching `<div class="...class_value...">` /
    matching `</div>` with `<semantic_tag class="...">` / `</semantic_tag>`.

    Skips silently if the page already uses the semantic tag with the same
    class (idempotency)."""
    # Idempotency check: already semantic?
    existing = re.search(
        rf'<{semantic_tag}\b[^>]*\bclass=(["\'])[^"\']*?\b'
        + re.escape(class_value)
        + r'\b[^"\']*?\1',
        text,
    )
    if existing:
        return text, False

    open_idx = _find_open_div(text, class_value)
    if open_idx < 0:
        return text, False
    open_end = text.index(">", open_idx) + 1
    close_idx = _find_matching_close(text, open_idx)
    if close_idx < 0:
        return text, False

    # Build new strings
    open_tag = text[open_idx:open_end]
    new_open = "<" + semantic_tag + open_tag[len("<div"):]
    new_close = f"</{semantic_tag}>"

    new_text = (
        text[:open_idx]
        + new_open
        + text[open_end:close_idx]
        + new_close
        + text[close_idx + len("</div>"):]
    )
    return new_text, True


def upgrade(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    changes: list[str] = []
    for cls, tag in CLASS_TO_TAG.items():
        new_text, changed = _upgrade_one(text, cls, tag)
        if changed:
            changes.append(f"{cls}->{tag}")
            text = new_text
    if changes:
        path.write_text(text, encoding="utf-8")
    return changes


def main() -> int:
    total = 0
    for rel in PAGES:
        path = ROOT / rel
        if not path.is_file():
            print(f"  miss {rel}")
            continue
        changes = upgrade(path)
        if changes:
            print(f"  upd  {rel}  ({', '.join(changes)})")
            total += 1
        else:
            print(f"  ok   {rel}")
    print(f"\n{total} file(s) changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
