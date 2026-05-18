"""Validate Open Graph + Twitter Card metadata across all live prod pages.

Hits the live URL, parses meta tags, and reports any missing/malformed
fields plus a content-type+dimensions check on og:image.

Usage:
    python scripts/validate_og.py [--base-url https://...]
"""

from __future__ import annotations

import argparse
import io
import re
import sys
import urllib.request
from urllib.parse import urljoin
from typing import Iterable

from PIL import Image

DEFAULT_BASE = "https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/"

PAGES = [
    "",  # index
    "code-generator.html",
    "tree-compare.html",
    "telemetry.html",
    "exports.html",
    "yang-accountability.html",
    "yang-accountability-compare.html",
    "swagger-cfg-model/",
    "swagger-events-model/",
    "swagger-ietf-model/",
    "swagger-mib-model/",
    "swagger-native-config-model/",
    "swagger-openconfig-model/",
    "swagger-oper-model/",
    "swagger-other-model/",
    "swagger-rpc-model/",
]

REQUIRED_OG = ("og:type", "og:title", "og:description", "og:url",
               "og:image", "og:site_name")
REQUIRED_TWITTER = ("twitter:card", "twitter:title", "twitter:description",
                    "twitter:image")
REQUIRED_OTHER = ("description", "canonical", "favicon-svg",
                  "apple-touch-icon")


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "og-validator/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _extract_meta(html: str) -> dict[str, str]:
    out: dict[str, str] = {}
    # property="og:foo" content="bar"
    for m in re.finditer(
        r'<meta\s+(?:property|name)=["\']([^"\']+)["\']\s+content=["\']([^"\']*)["\']',
        html, re.I
    ):
        out[m.group(1).lower()] = m.group(2)
    # rel="canonical" href="..."
    m = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
                  html, re.I)
    if m:
        out["canonical"] = m.group(1)
    m = re.search(
        r'<link\s+rel=["\']icon["\']\s+type=["\']image/svg\+xml["\']\s+'
        r'href=["\']([^"\']+)["\']', html, re.I)
    if m:
        out["favicon-svg"] = m.group(1)
    m = re.search(r'<link\s+rel=["\']apple-touch-icon["\'][^>]*href=["\']([^"\']+)["\']',
                  html, re.I)
    if m:
        out["apple-touch-icon"] = m.group(1)
    m = re.search(r'<title>([^<]+)</title>', html, re.I)
    if m:
        out["title"] = m.group(1).strip()
    return out


def _check(page: str, tags: dict[str, str], required: Iterable[str]) -> list[str]:
    errs = []
    for k in required:
        if not tags.get(k):
            errs.append(f"missing {k}")
    return errs


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default=DEFAULT_BASE)
    args = p.parse_args()
    base = args.base_url if args.base_url.endswith("/") else args.base_url + "/"

    total_errs = 0
    image_cache: dict[str, str] = {}

    print(f"Validating OG/Twitter metadata against {base}\n")
    for page in PAGES:
        url = urljoin(base, page)
        try:
            html = _get(url).decode("utf-8", errors="replace")
        except Exception as e:
            print(f"  FAIL {page or '<root>'}: fetch error {e}")
            total_errs += 1
            continue
        tags = _extract_meta(html)
        errs = (_check(page, tags, REQUIRED_OG)
                + _check(page, tags, REQUIRED_TWITTER)
                + _check(page, tags, REQUIRED_OTHER))

        # Twitter card must be summary_large_image (for 1200x630 art)
        tc = tags.get("twitter:card")
        if tc and tc != "summary_large_image":
            errs.append(f"twitter:card={tc!r} (expected summary_large_image)")

        # og:image URL must be absolute and resolve to a 1200×630 PNG
        img_url = tags.get("og:image", "")
        if img_url:
            if img_url not in image_cache:
                try:
                    raw = _get(img_url)
                    im = Image.open(io.BytesIO(raw))
                    image_cache[img_url] = f"{im.format} {im.size[0]}x{im.size[1]} ({len(raw)} B)"
                except Exception as e:
                    image_cache[img_url] = f"FETCH FAIL: {e}"
            info = image_cache[img_url]
            if "FAIL" in info:
                errs.append(f"og:image unreachable: {info}")
            elif "PNG 1200x630" not in info:
                errs.append(f"og:image wrong dims/format: {info}")

        # canonical must equal page url
        canon = tags.get("canonical", "")
        if canon and not (canon == url or canon == url.rstrip("/")
                          or canon + "/" == url):
            errs.append(f"canonical mismatch: {canon!r} vs requested {url!r}")

        status = "OK  " if not errs else "FAIL"
        label = page or "<root>"
        print(f"  [{status}] {label}")
        if errs:
            for e in errs:
                print(f"           - {e}")
            total_errs += len(errs)

    if image_cache:
        print("\nOG image:")
        for k, v in image_cache.items():
            print(f"  {k}\n    {v}")

    print(f"\n{total_errs} issue(s) across {len(PAGES)} page(s).")
    return 0 if total_errs == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
