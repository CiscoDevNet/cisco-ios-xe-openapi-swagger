"""Generate sitemap.xml listing every public HTML page in the repo.

Run from repo root:
    python scripts/generate_sitemap.py [--site-url https://...]

Output: sitemap.xml at the repo root.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SITE = "https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger"
TOP_LEVEL_PAGES = [
    ("", 1.0, "weekly"),                              # index.html
    ("code-generator.html", 0.8, "monthly"),
    ("tree-compare.html", 0.8, "monthly"),
    ("telemetry.html", 0.8, "monthly"),
    ("exports.html", 0.7, "monthly"),
    ("yang-accountability.html", 0.7, "monthly"),
    ("yang-accountability-compare.html", 0.6, "monthly"),
    ("platform-coverage.html", 0.7, "monthly"),
    ("app-map.html", 0.6, "monthly"),
    ("about.html", 0.6, "monthly"),
]
VIEWER_DIRS = [
    "swagger-cfg-model", "swagger-events-model", "swagger-ietf-model",
    "swagger-mib-model", "swagger-native-config-model",
    "swagger-openconfig-model", "swagger-oper-model",
    "swagger-other-model", "swagger-rpc-model",
]


def _entry(loc: str, lastmod: str, changefreq: str, priority: float) -> str:
    return (
        "  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority:.1f}</priority>\n"
        "  </url>"
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--site-url", default=DEFAULT_SITE)
    args = p.parse_args()
    site = args.site_url.rstrip("/")
    today = dt.date.today().isoformat()

    urls: list[str] = []
    for rel, priority, freq in TOP_LEVEL_PAGES:
        if rel and not (ROOT / rel).is_file():
            continue
        loc = f"{site}/" if not rel else f"{site}/{rel}"
        urls.append(_entry(loc, today, freq, priority))

    for d in VIEWER_DIRS:
        index = ROOT / d / "index.html"
        if not index.is_file():
            continue
        urls.append(_entry(f"{site}/{d}/", today, "monthly", 0.7))

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    out = ROOT / "sitemap.xml"
    out.write_text(xml, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({len(urls)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
