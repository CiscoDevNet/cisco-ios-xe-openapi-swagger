#!/usr/bin/env python3
"""Patch swagger-<cat>-model/index-v2.html files to be version-aware.

Replaces hardcoded `api-v2/...` fetches with a base computed from the active
version (read from `window.parent.__IOSXE_ACTIVE_VERSION__`). The default
version (17.18.1) keeps the legacy relative `api-v2/` path; any other version
fetches from `../releases/<ver>/swagger-<cat>-model/api-v2/`.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VER = "17.18.1"

HELPER = """
    // === version-aware api base (added by patch_viewers_version_aware.py) ===
    function __activeVer() {
        // Priority: ?ver= query param > #ver= hash > localStorage > parent window
        try {
            const qs = new URLSearchParams(location.search);
            if (qs.get('ver')) return qs.get('ver');
            const hm = location.hash.match(/[#&]ver=([^&]+)/);
            if (hm) return decodeURIComponent(hm[1]);
            const ls = localStorage.getItem('iosxe-active-version');
            if (ls) return ls;
        } catch (_) {}
        if (window.parent && window.parent !== window && window.parent.__IOSXE_ACTIVE_VERSION__) {
            return window.parent.__IOSXE_ACTIVE_VERSION__;
        }
        return window.__IOSXE_ACTIVE_VERSION__ || null;
    }
    function __apiBase() {
        const ver = __activeVer();
        if (!ver || ver === '%DEFAULT%') return 'api-v2';
        const m = location.pathname.match(/\\/(swagger-[^/]+-model)\\//);
        const cat = m ? m[1] : '';
        return '../releases/' + encodeURIComponent(ver) + '/' + cat + '/api-v2';
    }
    function __treeBase() {
        const ver = __activeVer();
        if (!ver || ver === '%DEFAULT%') return '../yang-trees';
        return '../releases/' + encodeURIComponent(ver) + '/yang-trees';
    }
    // Expose for mib-metadata side card and other consumers.
    window.__IOSXE_ACTIVE_VERSION__ = __activeVer();
""".replace("%DEFAULT%", DEFAULT_VER)


def patch(p: Path) -> bool:
    src = p.read_text(encoding="utf-8")
    orig = src
    if "version-aware api base" not in src:
        # Insert helper right after the opening of the main <script> block that
        # begins after the swagger-ui standalone preset import. We anchor on
        # the allModules declaration which exists in all 9 files (form varies).
        anchors = [
            "let allModules = [];",
            "let allModules = [], currentModule = null;",
        ]
        for anchor in anchors:
            if anchor in src:
                src = src.replace(
                    anchor,
                    HELPER.rstrip() + "\n    " + anchor,
                    1,
                )
                break

    # Replace fetch calls
    src = src.replace("fetch('api-v2/manifest.json')",
                      "fetch(__apiBase() + '/manifest.json')")
    src = src.replace("fetch(`api-v2/${fname}.json`)",
                      "fetch(`${__apiBase()}/${fname}.json`)")

    # Replace SwaggerUIBundle URLs that go through getSpecFolder
    src = src.replace(
        "url: `${getSpecFolder(fname)}/${fname}.json`",
        "url: `${__apiBase()}/${fname}.json`",
    )
    src = src.replace(
        "a.href = `${getSpecFolder(currentModule)}/${currentModule}.json`",
        "a.href = `${__apiBase()}/${currentModule}.json`",
    )

    # Replace tree links (../yang-trees/<fname>.html)
    src = re.sub(
        r"const treeUrl = '\.\./yang-trees/' \+ fname \+ '\.html';",
        "const treeUrl = __treeBase() + '/' + fname + '.html';",
        src,
    )

    if src != orig:
        p.write_text(src, encoding="utf-8")
        return True
    return False


def main() -> int:
    files = sorted(ROOT.glob("swagger-*-model/index-v2.html"))
    changed = 0
    for f in files:
        if patch(f):
            print(f"patched {f.relative_to(ROOT)}")
            changed += 1
        else:
            print(f"unchanged {f.relative_to(ROOT)}")
    print(f"\n[patch] {changed}/{len(files)} files updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
