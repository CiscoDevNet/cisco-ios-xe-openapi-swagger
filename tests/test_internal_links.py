"""Every static href/src in every published HTML page must resolve on the deployed site.

Mirrors .github/workflows/deploy-pages.yml (via build_app_map_html.is_published):
links to repo files the site does not ship (scripts/*.py, most *.md) are 404s there.
Release-scoped tree pages (releases/<ver>/yang-trees/) are three levels deep, which
is where a wrong `../` depth previously broke ~4,200 links.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from build_app_map_html import is_published  # noqa: E402

LINK = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", re.I)
NOT_MARKUP = re.compile(r"<script\b[^>]*>.*?</script>|<!--.*?-->", re.S | re.I)
SKIP = re.compile(r"^([a-z][a-z0-9+.-]*:|#|//)", re.I)
CI_BUILT = re.compile(r"^releases/[^/]+/exports/(bruno|postman)/")  # built by deploy-pages.yml


def published_pages() -> list[Path]:
    pages = sorted(REPO.glob("*.html"))
    for top in sorted(REPO.iterdir()):
        if top.is_dir() and is_published(f"{top.name}/index.html"):
            pages += sorted(top.rglob("*.html"))
    return pages


def resolves(page: Path, link: str) -> bool:
    path = unquote(link.split("#", 1)[0].split("?", 1)[0])
    if not path:
        return True
    target = (page.parent / path).resolve()
    try:
        rel = target.relative_to(REPO).as_posix()
    except ValueError:
        return False
    if CI_BUILT.match(rel):
        return True
    if target.is_dir():
        target, rel = target / "index.html", f"{rel}/index.html"
    return target.is_file() and is_published(rel)


def test_no_broken_internal_links():
    broken = []
    for page in published_pages():
        markup = NOT_MARKUP.sub("", page.read_text(encoding="utf-8", errors="replace"))
        for link in LINK.findall(markup):
            link = link.strip()
            if SKIP.match(link) or "{" in link:
                continue
            if not resolves(page, link):
                broken.append(f"{page.relative_to(REPO).as_posix()} -> {link}")
    assert not broken, f"{len(broken)} broken link(s):\n  " + "\n  ".join(broken[:40])


def test_tree_pages_reach_site_root():
    page = next((REPO / "releases").glob("*/yang-trees/*-MIB.html"))
    assert resolves(page, "../../../index.html")
    assert not resolves(page, "../swagger-mib-model/index.html")
