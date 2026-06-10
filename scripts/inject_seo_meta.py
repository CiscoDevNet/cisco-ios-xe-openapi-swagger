"""Inject SEO meta, favicon, Open Graph, Twitter Card, and JSON-LD into
every public HTML page in the repo.

Idempotent: the injected block is wrapped in marker comments so re-runs
replace the existing block in-place.

Usage:
    python scripts/inject_seo_meta.py [--site-url https://...]

Defaults to the production site URL.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SITE = "https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger"

BEGIN = "<!-- BEGIN seo-meta (managed by scripts/inject_seo_meta.py) -->"
END = "<!-- END seo-meta -->"

# Per-page metadata. Keys = repo-relative HTML paths.
# Each value = (title-suffix-or-None, description). If title-suffix is None,
# the page's existing <title> is preserved verbatim.
TOP_LEVEL: dict[str, tuple[str | None, str]] = {
    "index.html": (
        None,
        "Browse and search 608 Cisco IOS XE OpenAPI specs across 5 releases. "
        "Deep-link to any RESTCONF endpoint, generate client code, and "
        "download Postman or Bruno collections.",
    ),
    "code-generator.html": (
        None,
        "Generate ready-to-run Python, curl, Ansible, and RESTCONF code "
        "snippets for any Cisco IOS XE YANG model.",
    ),
    "tree-compare.html": (
        None,
        "Compare YANG trees across Cisco IOS XE releases — see exactly which "
        "nodes were added, removed, or renamed between versions.",
    ),
    "telemetry.html": (
        None,
        "Browse model-driven telemetry (MDT) xpaths and subscription "
        "examples for Cisco IOS XE devices.",
    ),
    "exports.html": (
        None,
        "Download Postman and Bruno collections, OpenAPI spec bundles, and "
        "per-release artifacts for Cisco IOS XE programmability.",
    ),
    "yang-accountability.html": (
        None,
        "Coverage report mapping every Cisco IOS XE YANG module to its "
        "OpenAPI spec and rendered tree.",
    ),
    "yang-accountability-compare.html": (
        None,
        "Compare YANG module coverage between Cisco IOS XE releases.",
    ),
    # app-map.html intentionally omitted: its full SEO block is baked by
    # scripts/build_app_map_html.py (the page is regenerated from APP_MAP.md
    # every time, so injecting external markers would be clobbered).
}

VIEWER_DESCRIPTIONS: dict[str, str] = {
    "cfg": "Browse RESTCONF configuration APIs",
    "events": "Browse YANG event notification streams",
    "ietf": "Browse IETF-standard YANG OpenAPI specs",
    "mib": "Browse SNMP MIB-derived OpenAPI specs",
    "native-config": "Browse the Cisco-IOS-XE-native configuration tree",
    "openconfig": "Browse OpenConfig YANG OpenAPI specs",
    "oper": "Browse operational-state and telemetry APIs",
    "other": "Browse auxiliary YANG OpenAPI specs",
    "rpc": "Browse RPC and action OpenAPI specs",
}


def _title_for(path: Path) -> str:
    """Extract the existing <title> text for canonical reuse."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"<title>([^<]+)</title>", text, re.I)
    return m.group(1).strip() if m else "Cisco IOS XE OpenAPI & YANG Docs"


def _block(*, title: str, description: str, page_url: str,
           asset_prefix: str, site_url: str, include_json_ld: bool) -> str:
    """Return the managed SEO block (without surrounding markers)."""
    og_image = f"{site_url}/assets/icons/og-image.png"
    json_ld = ""
    if include_json_ld:
        json_ld = (
            '\n<script type="application/ld+json">'
            '{"@context":"https://schema.org",'
            '"@type":"WebSite",'
            f'"name":"Cisco IOS XE OpenAPI & YANG Docs",'
            f'"url":"{site_url}/",'
            '"description":"Multi-version OpenAPI 2.0 and YANG tree '
            'documentation for the Cisco IOS XE programmability stack."'
            "}</script>"
        )
    return (
        f'\n<meta name="description" content="{description}">'
        '\n<meta name="keywords" content="Cisco IOS XE, YANG, OpenAPI, '
        'RESTCONF, NETCONF, network automation, model-driven telemetry, '
        'programmability, swagger">'
        '\n<meta name="author" content="Cisco DevNet">'
        '\n<meta name="theme-color" content="#1565c0" '
        'media="(prefers-color-scheme: light)">'
        '\n<meta name="theme-color" content="#0a0d12" '
        'media="(prefers-color-scheme: dark)">'
        f'\n<link rel="canonical" href="{page_url}">'
        # Favicons
        f'\n<link rel="icon" type="image/svg+xml" '
        f'href="{asset_prefix}assets/icons/favicon.svg">'
        f'\n<link rel="alternate icon" type="image/x-icon" '
        f'href="{asset_prefix}assets/icons/favicon.ico">'
        f'\n<link rel="apple-touch-icon" sizes="180x180" '
        f'href="{asset_prefix}assets/icons/apple-touch-icon.png">'
        # Open Graph
        '\n<meta property="og:type" content="website">'
        f'\n<meta property="og:site_name" content="Cisco IOS XE OpenAPI '
        '&amp; YANG Docs">'
        f'\n<meta property="og:title" content="{title}">'
        f'\n<meta property="og:description" content="{description}">'
        f'\n<meta property="og:url" content="{page_url}">'
        f'\n<meta property="og:image" content="{og_image}">'
        '\n<meta property="og:image:width" content="1200">'
        '\n<meta property="og:image:height" content="630">'
        # Twitter
        '\n<meta name="twitter:card" content="summary_large_image">'
        f'\n<meta name="twitter:title" content="{title}">'
        f'\n<meta name="twitter:description" content="{description}">'
        f'\n<meta name="twitter:image" content="{og_image}">'
        + json_ld
    )


def _inject(path: Path, block: str) -> bool:
    """Insert/replace the SEO block before </head>. Returns True if changed."""
    text = path.read_text(encoding="utf-8")
    wrapped = f"{BEGIN}{block}\n{END}"
    pattern = re.compile(
        rf"{re.escape(BEGIN)}.*?{re.escape(END)}", re.S
    )
    if pattern.search(text):
        new_text = pattern.sub(wrapped, text)
    else:
        if "</head>" not in text:
            print(f"  skip {path.relative_to(ROOT)}: no </head>")
            return False
        new_text = text.replace("</head>", f"{wrapped}\n</head>", 1)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--site-url", default=DEFAULT_SITE,
                   help="Canonical site URL (no trailing slash).")
    args = p.parse_args()
    site = args.site_url.rstrip("/")

    changed = 0

    # Top-level pages
    for rel, (title_suffix, desc) in TOP_LEVEL.items():
        path = ROOT / rel
        if not path.is_file():
            print(f"  miss {rel}: file not found")
            continue
        existing_title = _title_for(path)
        title = title_suffix or existing_title
        block = _block(
            title=title,
            description=desc,
            page_url=f"{site}/{rel}" if rel != "index.html"
            else f"{site}/",
            asset_prefix="",
            site_url=site,
            include_json_ld=(rel == "index.html"),
        )
        if _inject(path, block):
            print(f"  inj  {rel}")
            changed += 1
        else:
            print(f"  ok   {rel}")

    # Viewer pages
    for key, blurb in VIEWER_DESCRIPTIONS.items():
        rel = f"swagger-{key}-model/index.html"
        path = ROOT / rel
        if not path.is_file():
            print(f"  miss {rel}: file not found")
            continue
        existing_title = _title_for(path)
        description = (
            f"{blurb} for Cisco IOS XE. Browse, search, and deep-link "
            "to any RESTCONF endpoint."
        )
        # Canonical/og:url use the directory form (Pages auto-resolves to
        # index.html); avoids duplicate-content split between /dir/ and
        # /dir/index.html.
        canonical_url = f"{site}/swagger-{key}-model/"
        block = _block(
            title=existing_title,
            description=description,
            page_url=canonical_url,
            asset_prefix="../",
            site_url=site,
            include_json_ld=False,
        )
        if _inject(path, block):
            print(f"  inj  {rel}")
            changed += 1
        else:
            print(f"  ok   {rel}")

    print(f"\n{changed} file(s) changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
