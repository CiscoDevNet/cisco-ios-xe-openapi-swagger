#!/usr/bin/env python3
"""
Update all stats references across the project.
Replaces old path/operation counts with new values in all HTML, MD, and text files.
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# New stats (actual counted values)
NEW_STATS = {
    # Grand totals
    'total_paths': 13840,
    'total_ops': 24734,
    'total_specs': 672,
    # Per-folder
    'oper_paths': 4222,
    'oper_ops': 4222,
    'rpc_paths': 290,
    'rpc_ops': 290,
    'cfg_paths': 815,
    'cfg_ops': 2722,
    'oc_paths': 2063,
    'oc_ops': 7482,
    'ietf_paths': 553,
    'ietf_ops': 1836,
    'mib_paths': 4272,
    'mib_ops': 4272,
    'events_paths': 455,
    'events_ops': 455,
    'native_paths': 328,
    'native_ops': 1307,
    'other_paths': 842,
    'other_ops': 2148,
}

# Old -> New replacements (text patterns)
REPLACEMENTS = [
    # Grand totals
    ('10,563', '13,840'),
    ('10563', '13840'),
    ('17,074', '24,734'),
    ('17074', '24734'),
    # Oper
    ('2,652 paths', '4,222 paths'),
    ('2,652 ops', '4,222 ops'),
    ('2,652 operational', '4,222 operational'),
    ('(2,652 paths)', '(4,222 paths)'),
    # Cfg
    ('612 paths', '815 paths'),
    ('612 config', '815 config'),
    ('1,992 ops', '2,722 ops'),
    ('1,992 operations', '2,722 operations'),
    # OpenConfig
    ('777 paths', '2,063 paths'),
    ('2,900 ops', '7,482 ops'),
    ('2,900 operations', '7,482 operations'),
    # IETF
    ('505 paths', '553 paths'),
    ('1,664 ops', '1,836 ops'),
    ('1,664 operations', '1,836 operations'),
    # Other
    ('672 ops', '2,148 ops'),   # Be careful - 672 is also spec count
    ('1,542 ops', '2,148 ops'),
    ('1,542 operations', '2,148 operations'),
]

# Patterns in table rows (more specific to avoid false positives)
TABLE_REPLACEMENTS = [
    # PROJECT_SUMMARY.md table rows: | Category | modules | paths | ops |
    ('| Operational | 200 | 2,652 | 2,652 |', '| Operational | 200 | 4,222 | 4,222 |'),
    ('| Configuration | 39 | 612 | 1,992 |', '| Configuration | 39 | 815 | 2,722 |'),
    ('| OpenConfig | 42 | 777 | 2,900 |', '| OpenConfig | 42 | 2,063 | 7,482 |'),
    ('| IETF | 21 | 505 | 1,664 |', '| IETF | 21 | 553 | 1,836 |'),
    ('| Other | 10 | 672 | 1,542 |', '| Other | 10 | 842 | 2,148 |'),
    ('| **Total** | **672** | **10,563** | **17,074** |', '| **Total** | **672** | **13,840** | **24,734** |'),
]

# Files to process
EXTENSIONS = {'.md', '.html'}


def update_file(filepath):
    """Update stats in a single file. Returns number of replacements made."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except Exception:
            return 0

    original = content
    count = 0

    # Apply table-specific replacements first (more specific)
    for old, new in TABLE_REPLACEMENTS:
        if old in content:
            content = content.replace(old, new)
            count += content.count(new) - original.count(new)

    # Apply general replacements
    for old, new in REPLACEMENTS:
        if old in content:
            before = content
            content = content.replace(old, new)
            if content != before:
                count += 1

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return count
    return 0


def main():
    print("=" * 70)
    print("  Updating all stat references")
    print("=" * 70)

    total_files = 0
    total_replacements = 0

    for root_dir, dirs, files in os.walk(ROOT):
        # Skip hidden dirs, node_modules, .git, yang-trees
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'yang-trees')]

        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in EXTENSIONS:
                continue

            filepath = os.path.join(root_dir, fn)
            rel_path = os.path.relpath(filepath, ROOT)
            count = update_file(filepath)
            if count > 0:
                print(f"  Updated: {rel_path} ({count} replacements)")
                total_files += 1
                total_replacements += count

    print(f"\n  Files updated: {total_files}")
    print(f"  Total replacements: {total_replacements}")


if __name__ == "__main__":
    main()
