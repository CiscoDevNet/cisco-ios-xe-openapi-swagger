"""The service worker must precache every published top-level page and only real files.

A precache URL that 404s makes the whole SW install fail (cache.addAll is
atomic), and an un-precached page silently loses offline support.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _precache_urls() -> list[str]:
    source = (REPO / "service-worker.js").read_text(encoding="utf-8")
    block = source.split("PRECACHE_URLS = [", 1)[1].split("].map", 1)[0]
    return re.findall(r"^\s*'([^']*)',", block, re.MULTILINE)


def test_every_precache_url_exists():
    missing = [url for url in _precache_urls() if url and not (REPO / url).is_file()]
    assert not missing, f"service-worker.js precaches files that do not exist: {missing}"


def test_every_published_top_level_page_is_precached():
    pages = subprocess.check_output(
        [sys.executable, str(REPO / "scripts" / "generate_sitemap.py"), "--list-pages"], text=True,
    ).split()
    not_cached = [page for page in pages if "/" not in page and page not in _precache_urls()]
    assert not not_cached, f"published pages missing from PRECACHE_URLS: {not_cached}"
