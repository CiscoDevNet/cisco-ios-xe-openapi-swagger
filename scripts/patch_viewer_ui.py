#!/usr/bin/env python3
"""patch_viewer_ui.py — one-shot patcher that brings the 9
``swagger-*-model/index.html`` viewers to the same UI baseline:

1.  Replace the inline-styled "Copy Share Link" button with a shared
    ``.btn.copy-share-btn`` class from ``assets/css/components.css`` (also
    folds the native-config viewer's ``.btn-secondary`` variant into the
    same class so all 9 look identical).
2.  Add ``<link rel="stylesheet" href="../assets/css/components.css">`` if
    missing, and ``<script src="../assets/js/viewer-enhancements.js" defer>``
    if missing. The enhancements bundle adds:
       - ?ver= → hash sync (so Copy Share Link captures the active release)
       - in-header version switcher
       - global "/" key focuses the sidebar search box
       - window.__showViewerToast(msg, kind)
3.  Wrap each viewer's ``catch (e) { return { fname, title: fname, ... }; }``
    fallback to also surface a user-visible toast via the new helper.

The script is **idempotent** — re-running it on an already-patched viewer
is a no-op. Detection is via marker comments and class presence.

Run from the repo root:
    python scripts/patch_viewer_ui.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEWERS = sorted(ROOT.glob("swagger-*-model/index.html"))

# --- 1. Copy Share Link button --------------------------------------------
# Match either inline-style variant or class="btn-secondary" variant.
SHARE_BTN_RE = re.compile(
    r'<button(?P<attrs>[^>]*?)\s*onclick="window\.__DeepLink\s*&&\s*'
    r'window\.__DeepLink\.copyShareLink\(this\)"[^>]*>'
    r'Copy Share Link</button>',
    re.IGNORECASE,
)
NEW_SHARE_BTN = (
    '<button type="button" class="btn copy-share-btn" '
    'onclick="window.__DeepLink && window.__DeepLink.copyShareLink(this)" '
    'title="Copy a shareable link that opens this exact spec / operation / release">'
    'Copy Share Link</button>'
)

# --- 2. components.css + viewer-enhancements.js ---------------------------
LINK_COMPONENTS = '<link rel="stylesheet" href="../assets/css/components.css">'
SCRIPT_ENH = '<script src="../assets/js/viewer-enhancements.js" defer></script>'

# --- 3. fallback toast on spec-fetch failure ------------------------------
# The 9 viewers all have a per-module fetch with a `catch(e)` clause that
# silently substitutes a stub record. We add a toast call so the user gets
# at least one visible failure indicator instead of empty cards.
CATCH_RE = re.compile(
    r'(catch\s*\(\s*(?P<ev>e\d?|err)\s*\)\s*\{\s*)'
    r'(return\s*\{\s*fname\b)'
)
CATCH_REPLACEMENT = (
    r'\1if (typeof window.__showViewerToast === "function") { '
    r'window.__showViewerToast("Failed to load spec: " + fname + '
    r'" (" + (\g<ev> && \g<ev>.message || "network error") + ")", "warning"); } \3'
)


def patch_one(path: Path) -> dict:
    """Apply all idempotent patches to a single viewer file."""
    src = path.read_text(encoding="utf-8")
    orig = src
    changes = []

    # 1. Standardize the Copy Share Link button (inline-style or btn-secondary).
    new_src, n = SHARE_BTN_RE.subn(NEW_SHARE_BTN, src)
    if n:
        src = new_src
        changes.append(f"copy-share-btn x{n}")

    # 2a. components.css
    if "assets/css/components.css" not in src:
        anchor = '<link rel="stylesheet" href="../assets/css/viewer.css">'
        if anchor in src:
            src = src.replace(anchor, anchor + "\n" + LINK_COMPONENTS, 1)
            changes.append("components.css linked")
        else:
            # Fall back: inject just before </head>.
            src = src.replace("</head>", LINK_COMPONENTS + "\n</head>", 1)
            changes.append("components.css linked (head)")

    # 2b. viewer-enhancements.js
    if "viewer-enhancements.js" not in src:
        anchor = '<script src="../assets/js/site-chrome.js" defer></script>'
        if anchor in src:
            src = src.replace(anchor, anchor + "\n" + SCRIPT_ENH, 1)
            changes.append("viewer-enhancements.js linked")
        else:
            src = src.replace("</head>", SCRIPT_ENH + "\n</head>", 1)
            changes.append("viewer-enhancements.js linked (head)")

    # 3. Spec-load failure toast — only patch ONCE per file (the regex is
    #    intentionally narrow so we only hit the per-module fetch catch).
    if "__showViewerToast" not in src:
        new_src, n = CATCH_RE.subn(CATCH_REPLACEMENT, src, count=1)
        if n:
            src = new_src
            changes.append("spec-load toast")

    if src != orig:
        path.write_text(src, encoding="utf-8")
        return {"file": str(path.relative_to(ROOT)), "changes": changes}
    return {"file": str(path.relative_to(ROOT)), "changes": []}


def main() -> int:
    if not VIEWERS:
        print("No swagger-*-model/index.html files found")
        return 1
    n_changed = 0
    for v in VIEWERS:
        result = patch_one(v)
        if result["changes"]:
            n_changed += 1
            print(f"  patched  {result['file']:<50}  {', '.join(result['changes'])}")
        else:
            print(f"  skipped  {result['file']}  (already up-to-date)")
    print(f"\n{n_changed} of {len(VIEWERS)} viewers updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
