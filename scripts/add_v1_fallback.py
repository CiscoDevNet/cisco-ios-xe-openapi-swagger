#!/usr/bin/env python3
"""Add v1 API fallback support to all index.html files.

When a spec is requested via #spec=X but doesn't exist in api/,
falls back to loading from api/ instead. This supports 125 v1-only
modules that were linked from the search index.
"""
import os
import re
import glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = 0

    # 1. Add getSpecFolder helper right before loadSpec function
    if 'function getSpecFolder' not in content:
        old = '    function loadSpec(fname, el) {'
        new = """    function getSpecFolder(fname) {
        return allModules.find(m => m.fname === fname) ? 'api' : 'api';
    }

    function loadSpec(fname, el) {"""
        if old in content:
            content = content.replace(old, new, 1)
            changes += 1

    # 2. Update SwaggerUIBundle url in loadSpec to use getSpecFolder
    # Handle both single-line and multi-line patterns
    # Pattern 1: single line SwaggerUIBundle({ url: `api/...
    content_new = re.sub(
        r"SwaggerUIBundle\(\{\s*url:\s*`api/\$\{fname\}\.json`",
        "SwaggerUIBundle({ url: `${getSpecFolder(fname)}/${fname}.json`",
        content
    )
    if content_new != content:
        changes += 1
        content = content_new

    # Pattern 2: multi-line with url: `api/${fname}.json`,
    content_new = re.sub(
        r"url:\s*`api/\$\{fname\}\.json`",
        "url: `${getSpecFolder(fname)}/${fname}.json`",
        content
    )
    if content_new != content:
        changes += 1
        content = content_new

    # 3. Update downloadSpec to use getSpecFolder
    old_download = "a.href = `api/${currentModule}.json`;"
    new_download = "a.href = `${getSpecFolder(currentModule)}/${currentModule}.json`;"
    if old_download in content:
        content = content.replace(old_download, new_download, 1)
        changes += 1

    # 4. Update checkHash to allow specs not in manifest (v1 fallback)
    old_check = """    function checkHash() {
        const hash = decodeURIComponent(window.location.hash);
        if (hash.startsWith('#spec=')) {
            const fname = hash.replace('#spec=', '');
            if (allModules.find(m => m.fname === fname))
                loadSpec(fname, document.querySelector(`[data-module="${fname}"]`));
        }
    }"""
    new_check = """    function checkHash() {
        const hash = decodeURIComponent(window.location.hash);
        if (hash.startsWith('#spec=')) {
            const fname = hash.replace('#spec=', '');
            const el = document.querySelector(`[data-module="${fname}"]`);
            if (el) {
                loadSpec(fname, el);
            } else if (fname) {
                loadSpec(fname, null);
            }
        }
    }"""
    if old_check in content:
        content = content.replace(old_check, new_check, 1)
        changes += 1

    if changes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Patched {os.path.basename(os.path.dirname(filepath))}: {changes} changes")
    else:
        print(f"  Skipped {os.path.basename(os.path.dirname(filepath))}: already patched or pattern mismatch")

    return changes

def main():
    pattern = os.path.join(BASE, 'swagger-*-model', 'index.html')
    files = sorted(glob.glob(pattern))
    print(f"Found {len(files)} index.html files")
    
    total = 0
    for f in files:
        total += patch_file(f)
    
    print(f"\nTotal changes: {total}")

if __name__ == '__main__':
    main()
