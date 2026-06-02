#!/usr/bin/env python3
"""
One-shot patch: add platform-support badge bar to all 9 swagger-*-model/index.html viewers.
Idempotent — safe to re-run.

Inserts:
  1. <div id="platformBadges"> immediately after the </div> of the download bar.
  2. <script src="../assets/js/platform-support.js"></script> before paths-search.js.
  3. A renderBadges() call at the bottom of loadSpec() (after the treeLink block).
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = [
    "swagger-cfg-model", "swagger-events-model", "swagger-ietf-model",
    "swagger-mib-model", "swagger-native-config-model", "swagger-openconfig-model",
    "swagger-oper-model", "swagger-other-model", "swagger-rpc-model",
]

BADGE_DIV = ('<div id="platformBadges" class="platform-badges" '
             'style="display:none;margin:6px 0 10px 0;padding:6px 10px;'
             'background:#fafafa;border:1px solid #e0e0e0;border-radius:4px;"></div>')

SCRIPT_TAG = '<script src="../assets/js/platform-support.js"></script>'

RENDER_CALL = ('\n        if (window.__PlatformSupport) { '
               'window.__PlatformSupport.renderBadges('
               'document.getElementById("platformBadges"), fname); }')


def patch_one(viewer_dir):
    path = os.path.join(BASE, viewer_dir, "index.html")
    if not os.path.isfile(path):
        return f"SKIP {viewer_dir}: no index.html"
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    orig = content
    changes = []

    # 1. Insert badge div after the download bar </div>. Idempotent guard.
    if 'id="platformBadges"' not in content:
        # The download bar has id="downloadBar" and closes with </div>.
        # We insert AFTER that closing </div>.
        m = re.search(r'(<div class="download-bar" id="downloadBar">.*?</div>)',
                      content, flags=re.DOTALL)
        if m:
            insert = m.group(1) + "\n            " + BADGE_DIV
            content = content[:m.start()] + insert + content[m.end():]
            changes.append("badge div")
        else:
            changes.append("WARN: download-bar not found")

    # 2. Insert script tag before paths-search.js (or before the last </script>
    #    if paths-search.js isn't there).
    if 'platform-support.js' not in content:
        if '<script src="paths-search.js"></script>' in content:
            content = content.replace(
                '<script src="paths-search.js"></script>',
                SCRIPT_TAG + '\n    <script src="paths-search.js"></script>',
                1)
            changes.append("script tag")
        else:
            changes.append("WARN: paths-search.js script tag not found")

    # 3. Add renderBadges call after the treeLink block in loadSpec().
    if 'window.__PlatformSupport.renderBadges' not in content:
        # Anchor on the unique closing block of the treeLink fetch chain.
        anchor = ".catch(() => { treeLink.style.display = 'none'; });\n        }"
        if anchor in content:
            content = content.replace(anchor, anchor + RENDER_CALL, 1)
            changes.append("renderBadges call")
        else:
            changes.append("WARN: treeLink anchor not found")

    if content == orig:
        return f"OK {viewer_dir}: already patched"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return f"PATCHED {viewer_dir}: {', '.join(changes)}"


def main():
    for v in FILES:
        print(patch_one(v))


if __name__ == "__main__":
    main()
