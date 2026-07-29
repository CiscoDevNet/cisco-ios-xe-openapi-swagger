#!/usr/bin/env python3
"""Render CHANGELOG.md into the strict-CSP static page `changelog.html`.

Reuses the dependency-free Markdown renderer + CSS from
`build_app_map_html.py`, so the two generated docs stay visually and
structurally consistent (same headings, tables, lists, code blocks, and
strict-CSP page shell with no inline `<script>`).

Re-run after editing CHANGELOG.md:

    python -X utf8 scripts/build_changelog_html.py
"""
from __future__ import annotations

import html
import sys
from datetime import datetime, timezone
from pathlib import Path

# build_app_map_html lives next to this script; reuse its Markdown renderer
# and stylesheet rather than duplicating ~400 lines of parser.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_app_map_html import CSS, render  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "CHANGELOG.md"
TARGET = ROOT / "changelog.html"

PAGE_TITLE = "Changelog \u2014 Cisco IOS XE OpenAPI Documentation Hub"
PAGE_DESC = (
    "Detailed development history and release notes for the Cisco IOS XE "
    "OpenAPI documentation hub \u2014 every round of features, security "
    "hardening, and per-release artefacts, generated from the canonical "
    "CHANGELOG.md source."
)

HEADER_NAV = [
    ("Home", "index.html"),
    ("App Map", "app-map.html"),
    ("About", "about.html"),
    ("Versioning", "VERSIONING.md"),
    (
        "Edit on GitHub",
        "https://github.com/CiscoDevNet/cisco-ios-xe-openapi-swagger/blob/main/CHANGELOG.md",
    ),
]


def build_page(body_html: str, source_rel: str) -> str:
    nav_html = "".join(
        f'<a href="{html.escape(href, quote=True)}">{label}</a>'
        for label, href in HEADER_NAV
    )
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(PAGE_TITLE)}</title>
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' https://*.clarity.ms https://*.posthog.com https://*.i.posthog.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://*.clarity.ms https://*.posthog.com https://*.i.posthog.com;">
    <meta name="description" content="{html.escape(PAGE_DESC, quote=True)}">
    <meta name="keywords" content="Cisco IOS XE, YANG, OpenAPI, RESTCONF, NETCONF, changelog, release notes, development history, network automation, swagger">
    <meta name="author" content="Cisco DevNet">
    <meta name="theme-color" content="#1565c0" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#0a0d12" media="(prefers-color-scheme: dark)">
    <link rel="canonical" href="https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/changelog.html">
    <link rel="icon" type="image/svg+xml" href="assets/icons/favicon.svg">
    <link rel="alternate icon" type="image/x-icon" href="assets/icons/favicon.ico">
    <link rel="apple-touch-icon" sizes="180x180" href="assets/icons/apple-touch-icon.png">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Cisco IOS XE OpenAPI &amp; YANG Docs">
    <meta property="og:title" content="{html.escape(PAGE_TITLE)}">
    <meta property="og:description" content="{html.escape(PAGE_DESC, quote=True)}">
    <meta property="og:url" content="https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/changelog.html">
    <meta property="og:image" content="https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/assets/icons/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{html.escape(PAGE_TITLE)}">
    <meta name="twitter:description" content="{html.escape(PAGE_DESC, quote=True)}">
    <meta name="twitter:image" content="https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/assets/icons/og-image.png">
    <style>{CSS}</style>
</head>
<body>
    <header class="header">
        <div class="inner">
            <h1>Changelog</h1>
            <p>Detailed development history and release notes for the Cisco IOS XE OpenAPI documentation hub.</p>
            <nav>{nav_html}</nav>
        </div>
    </header>
    <main class="container">
        <div class="toolbar">
            <div class="links">
                <a href="{html.escape(source_rel)}">View source (Markdown)</a>
                <a href="https://github.com/CiscoDevNet/cisco-ios-xe-openapi-swagger/blob/main/{html.escape(source_rel)}">Edit on GitHub</a>
            </div>
            <div>Generated {generated_at} from <code>{html.escape(source_rel)}</code></div>
        </div>
        <article class="content">
{body_html}
        </article>
    </main>
    <footer class="footer">
        <p>Auto-generated by <code>scripts/build_changelog_html.py</code>. To update, edit
        <code>{html.escape(source_rel)}</code> and re-run the script.</p>
    </footer>
    <script src="assets/js/analytics-config.js"></script>
    <script src="assets/js/sw-register.js" defer></script>
    <script src="assets/js/analytics.js" defer></script>
</body>
</html>
"""


def main() -> int:
    if not SOURCE.is_file():
        sys.stderr.write(f"[changelog] source not found: {SOURCE}\n")
        return 1
    md_text = SOURCE.read_text(encoding="utf-8")
    body = render(md_text)
    html_out = build_page(body, SOURCE.name)
    TARGET.write_text(html_out, encoding="utf-8")
    size_kb = TARGET.stat().st_size / 1024
    print(f"[changelog] wrote {TARGET.relative_to(ROOT)} ({size_kb:.1f} KB) "
          f"from {SOURCE.relative_to(ROOT)} ({SOURCE.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
