"""One-shot patcher that strips every third-party CDN reference from the site
so a fresh clone runs with zero outbound traffic (air-gapped / high-security).

What it does:

  - Swagger UI CSS + JS:    cdn.jsdelivr.net -> ./assets/vendor/swagger-ui-5.31.0/...
  - fuse.js, chart.js:      cdn.jsdelivr.net -> ./assets/vendor/...
  - Google Fonts <link>:    removed (system font stack already in fallback chain)
  - <link rel="preconnect"> for fonts.googleapis.com / fonts.gstatic.com: removed
  - Content-Security-Policy: drops cdn.jsdelivr.net / fonts.googleapis.com /
    fonts.gstatic.com from script-src/style-src/font-src
  - Inline `font-family: 'Roboto', sans-serif` keeps Roboto first (still used when
    a customer chooses to re-enable Google Fonts) but appends a robust system
    fallback so air-gapped browsers render a high-quality sans-serif.

Idempotent: re-running on already-patched files is a no-op.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Mapping of CDN -> local path. Two contexts: top-level pages (index.html etc.)
# and the per-category viewers (swagger-*-model/index.html) which sit one
# directory deeper and therefore need ../assets/ instead of assets/.
SWAGGER_UI_FILES = [
    "swagger-ui.css",
    "swagger-ui-bundle.js",
    "swagger-ui-standalone-preset.js",
]

CDN_BASE = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.31.0/"
LOCAL_VENDOR_DIR = "assets/vendor/swagger-ui-5.31.0/"

FUSE_CDN = "https://cdn.jsdelivr.net/npm/fuse.js@7.0.0"
FUSE_LOCAL = "assets/vendor/fuse.js"

CHART_CDN = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"
CHART_LOCAL = "assets/vendor/chart.umd.js"

# Pages to patch (everything HTML at repo root + every viewer index.html one
# level deep). Released-version snapshots under releases/ are intentionally
# left untouched — they are immutable historical builds.
ROOT_HTML = sorted(ROOT.glob("*.html"))
VIEWER_HTML = sorted(p for p in ROOT.glob("swagger-*-model/index.html"))
EXTRA_HTML = [ROOT / "yang-trees" / "index.html"]
ALL_HTML = ROOT_HTML + VIEWER_HTML + [p for p in EXTRA_HTML if p.exists()]

# Regexes (all multiline-safe, no DOTALL needed — these tags are single-line).
RE_PRECONNECT = re.compile(
    r'^\s*<link\s+rel="preconnect"\s+href="https://fonts\.(?:googleapis|gstatic)\.com"[^>]*>\s*\n',
    re.MULTILINE,
)
RE_GOOGLE_FONTS_LINK = re.compile(
    r'^\s*<link\s+href="https://fonts\.googleapis\.com/css2[^"]*"\s+rel="stylesheet"[^>]*>\s*\n',
    re.MULTILINE,
)
RE_CSP = re.compile(
    r'(<meta\s+http-equiv="Content-Security-Policy"\s+content=")([^"]*)(")',
    re.IGNORECASE,
)
RE_ROBOTO_FONT = re.compile(r"font-family:\s*'Roboto',\s*sans-serif\b")
SYSTEM_FALLBACK = (
    "font-family: 'Roboto', system-ui, -apple-system, BlinkMacSystemFont, "
    "'Segoe UI', Arial, sans-serif"
)


def patch_csp(value: str) -> str:
    """Strip external hosts from a CSP value. Idempotent."""
    # Tokens to remove anywhere they appear.
    drop = ["cdn.jsdelivr.net", "fonts.googleapis.com", "fonts.gstatic.com"]
    out = value
    for tok in drop:
        # Remove preceded by space (most common) or as the first token after a directive.
        out = re.sub(rf"\s+{re.escape(tok)}", "", out)
        out = re.sub(rf"{re.escape(tok)}\s+", "", out)
    # If `font-src` is now empty (only contained gstatic), drop the whole directive.
    out = re.sub(r"font-src\s*;\s*", "", out)
    out = re.sub(r"font-src\s*$", "", out)
    # Collapse whitespace.
    out = re.sub(r"\s{2,}", " ", out).strip()
    return out


def rewrite(path: Path, text: str) -> tuple[str, int]:
    """Return (new_text, change_count) for a single file."""
    n = 0
    new = text

    # 1. Swagger UI CDN -> local vendor path. Depth-aware prefix.
    rel_prefix = "../" if path.parent.name.startswith("swagger-") or path.parent.name == "yang-trees" else ""
    local_base = rel_prefix + LOCAL_VENDOR_DIR
    for fn in SWAGGER_UI_FILES:
        url = CDN_BASE + fn
        if url in new:
            new = new.replace(url, local_base + fn)
            n += 1

    # 2. fuse.js + chart.js
    if FUSE_CDN in new:
        new = new.replace(FUSE_CDN, rel_prefix + FUSE_LOCAL)
        n += 1
    if CHART_CDN in new:
        new = new.replace(CHART_CDN, rel_prefix + CHART_LOCAL)
        n += 1

    # 3. Remove preconnect + Google Fonts <link>
    new2, c = RE_PRECONNECT.subn("", new)
    n += c
    new3, c = RE_GOOGLE_FONTS_LINK.subn("", new2)
    n += c
    new = new3

    # 4. Patch CSP
    def _csp_sub(m: re.Match[str]) -> str:
        before = m.group(2)
        after = patch_csp(before)
        return m.group(1) + after + m.group(3)

    new, c = RE_CSP.subn(_csp_sub, new)
    n += c

    # 5. Robust font fallback
    new, c = RE_ROBOTO_FONT.subn(SYSTEM_FALLBACK, new)
    n += c

    return new, n


def main() -> int:
    total_files = 0
    total_changes = 0
    for p in ALL_HTML:
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new, n = rewrite(p, text)
        if n and new != text:
            p.write_text(new, encoding="utf-8")
            rel = p.relative_to(ROOT).as_posix()
            print(f"  {n:3d}  {rel}")
            total_files += 1
            total_changes += n
    print(f"\nPatched {total_files} files, {total_changes} edits total.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
