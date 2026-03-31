#!/usr/bin/env python3
"""
Add a 'View YANG Tree' link button to the download bar of all 9 index-v2.html files.
The button dynamically links to ../yang-trees/{moduleName}.html and only shows when the tree exists.
"""

import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES = [
    os.path.join(BASE, "swagger-oper-model", "index-v2.html"),
    os.path.join(BASE, "swagger-cfg-model", "index-v2.html"),
    os.path.join(BASE, "swagger-native-config-model", "index-v2.html"),
    os.path.join(BASE, "swagger-openconfig-model", "index-v2.html"),
    os.path.join(BASE, "swagger-ietf-model", "index-v2.html"),
    os.path.join(BASE, "swagger-mib-model", "index-v2.html"),
    os.path.join(BASE, "swagger-rpc-model", "index-v2.html"),
    os.path.join(BASE, "swagger-events-model", "index-v2.html"),
    os.path.join(BASE, "swagger-other-model", "index-v2.html"),
]

# The tree link HTML to add in the download bar
TREE_LINK_HTML = '<a id="treeLink" href="#" target="_blank" style="display:none; padding: 6px 14px; border-radius: 4px; font-size: 12px; background: #4CAF50; color: white; text-decoration: none; font-weight: 500;">🌳 View YANG Tree</a>'

# The JS code to add at the end of loadSpec() to update the tree link
TREE_JS = """
        // Update YANG tree link
        const treeLink = document.getElementById('treeLink');
        if (treeLink) {
            const treeUrl = '../yang-trees/' + fname + '.html';
            treeLink.href = treeUrl;
            treeLink.style.display = 'none';
            fetch(treeUrl, { method: 'HEAD' }).then(r => {
                treeLink.style.display = r.ok ? 'inline-block' : 'none';
            }).catch(() => { treeLink.style.display = 'none'; });
        }"""

for filepath in FILES:
    if not os.path.isfile(filepath):
        print(f"  SKIP: {filepath} not found")
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    # 1. Add the tree link button in the download bar (after the downloadLabel span)
    if 'id="treeLink"' not in content:
        # Find the downloadLabel span and add the tree link after it
        pattern = r'(<span id="downloadLabel"[^>]*></span>)'
        replacement = r'\1\n                ' + TREE_LINK_HTML
        new_content = re.sub(pattern, replacement, content, count=1)
        if new_content != content:
            content = new_content
            modified = True
            print(f"  Added tree link button to download bar: {os.path.basename(os.path.dirname(filepath))}")
        else:
            print(f"  WARNING: Could not find downloadLabel span in {filepath}")

    # 2. Add the tree link JS code to loadSpec()
    if "// Update YANG tree link" not in content:
        # Find the SwaggerUIBundle call (multi-line) and add tree code after it
        # Pattern: the }); that ends the SwaggerUIBundle call, followed by the } closing loadSpec
        # Look for the closing of SwaggerUIBundle: "        });\n    }\n"
        pattern = r"(layout: 'StandaloneLayout'[^\n]*\n\s*\}\);)"
        match = re.search(pattern, content)
        if match:
            content = content.replace(match.group(0), match.group(0) + TREE_JS)
            modified = True
            print(f"  Added tree link JS to loadSpec(): {os.path.basename(os.path.dirname(filepath))}")
        else:
            print(f"  WARNING: Could not find SwaggerUIBundle closing in {filepath}")

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(f"  No changes needed: {os.path.basename(os.path.dirname(filepath))}")

print("\nDone! Tree link buttons added to all index-v2.html files.")
