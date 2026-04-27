"""Strip decorative emoji from UI files.

Removes characters in U+1F000-U+1FAFF and U+2600-U+27BF (Misc Symbols, Dingbats,
Misc Symbols & Pictographs) plus U+FE0F variation selectors, with these
EXCEPTIONS kept (functional monochrome glyphs used by the UI):
  - U+2605 BLACK STAR (favorites on)
  - U+2606 WHITE STAR (favorites off)
  - U+2713 CHECK MARK (copy confirmation)
  - U+2715 MULTIPLICATION X (close button)

Also collapses the whitespace artifacts (double spaces, leading-space inside
tags) created by stripping prefixes like "[emoji] Search".
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

KEEP = {"\u2605", "\u2606", "\u2713", "\u2715"}

# Build a regex matching any code point we want to drop.
def _ranges():
    out = []
    # Misc Symbols + Dingbats + Misc Symbols & Arrows
    for cp in range(0x2600, 0x27C0):
        ch = chr(cp)
        if ch in KEEP:
            continue
        out.append(ch)
    # SMP emoji blocks
    for cp in range(0x1F000, 0x1FB00):
        out.append(chr(cp))
    return "".join(out)

EMOJI_CHARS = _ranges()
# Also strip variation selectors that immediately follow emoji
EMOJI_RE = re.compile(f"[{re.escape(EMOJI_CHARS)}]\uFE0F?")

# After removal: collapse runs of whitespace to single space, but preserve
# newlines.  Trim space immediately inside opening/closing tags or quotes.
COLLAPSE_RE = re.compile(r"[ \t]{2,}")

def strip(text: str) -> str:
    new = EMOJI_RE.sub("", text)
    if new == text:
        return text  # no emoji removed → leave file untouched
    # Only post-process lines that actually changed (had an emoji on them)
    old_lines = text.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    if len(old_lines) != len(new_lines):
        # Should not happen since EMOJI_RE preserves newlines, but be safe.
        return new
    out_lines = []
    for old, line in zip(old_lines, new_lines):
        if old == line:
            out_lines.append(line)
            continue
        m = re.match(r"^([ \t]*)(.*?)(\r?\n?)$", line, re.DOTALL)
        if not m:
            out_lines.append(line)
            continue
        lead, body, nl = m.group(1), m.group(2), m.group(3)
        body = COLLAPSE_RE.sub(" ", body)
        # On changed lines, strip the orphan space the prefix-emoji left behind
        # in patterns like `>EMOJI Word` -> `> Word` -> `>Word`. We deliberately
        # do NOT touch quoted regions because that would collapse legitimate
        # whitespace between HTML attributes (e.g. `href="..." style="..."`).
        body = re.sub(r">\s+(?=\S)", ">", body)
        body = body.rstrip(" \t")
        out_lines.append(lead + body + nl)
    return "".join(out_lines)


TARGETS = [
    "index.html", "code-generator.html", "tree-compare.html",
    "yang-accountability.html", "yang-accountability-compare.html",
    "exports.html", "telemetry.html", "404.html",
    "index-app.js", "code-generator.js", "search.js", "tree-compare.js",
    "yang-accountability.js", "recent-favorites.js", "hub-search-ops.js",
]

def main(root: Path) -> int:
    changed = 0
    files = list((root / p) for p in TARGETS if (root / p).is_file())
    for d in root.glob("swagger-*-model"):
        for ext in ("*.html", "*.js"):
            files.extend(d.glob(ext))

    for fp in files:
        try:
            old = fp.read_text(encoding="utf-8")
        except Exception as e:
            print(f"skip {fp}: {e}")
            continue
        new = strip(old)
        if new != old:
            fp.write_text(new, encoding="utf-8", newline="\n")
            removed = sum(1 for ch in old if ch in EMOJI_CHARS)
            print(f"stripped {removed:4d} emoji from {fp.relative_to(root)}")
            changed += 1
    print(f"\n{changed} file(s) modified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1] if len(sys.argv) > 1 else ".")))
