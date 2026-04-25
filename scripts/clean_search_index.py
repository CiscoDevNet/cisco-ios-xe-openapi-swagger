#!/usr/bin/env python3
"""
Clean search-index.json:
- Remove v1 entries that have a v2 equivalent (prefer v2)
- Rename v2 types to plain types (rpc-v2 -> rpc, oper-v2 -> operational, etc.)
- Clean displayCategory labels
- Update swaggerUrl to use index-v2.html
- Keep v1-only entries (no v2 equivalent) but point them to redirecting index.html
"""
import json
from pathlib import Path
from collections import defaultdict

base = Path(__file__).parent.parent

# Map v2 type back to plain type
v2_to_plain = {
    'oper-v2': 'operational',
    'cfg-v2': 'configuration',
    'native-v2': 'native',
    'openconfig-v2': 'openconfig',
    'ietf-v2': 'ietf',
    'mib-v2': 'mib',
    'rpc-v2': 'rpc',
    'events-v2': 'events',
    'other-v2': 'other',
}

# v1 types
v1_types = {'operational', 'configuration', 'native', 'openconfig', 'ietf', 'mib', 'rpc', 'events', 'other'}

# Clean displayCategory labels
display_clean = {
    'Operational v2 (Deep)': 'Operational',
    'Config v2 (Deep)': 'Configuration',
    'Native v2 (Deep)': 'Native Config',
    'OpenConfig v2 (Deep)': 'OpenConfig',
    'IETF v2 (Deep)': 'IETF',
    'MIB v2 (Deep)': 'MIB',
    'RPC v2 (Deep)': 'RPC Operations',
    'Events v2 (Deep)': 'Events',
    'Other v2 (Deep)': 'Other',
}


def main():
    index_path = base / 'search-index.json'

    with open(index_path, encoding='utf-8') as f:
        data = json.load(f)

    modules = data['modules']

    # Build set of modules that have v2 entries
    v2_modules = set()
    for m in modules:
        if m.get('type', '').endswith('-v2'):
            v2_modules.add((m['name'], m.get('category', '')))

    new_modules = []
    removed_v1 = 0
    converted_v2 = 0
    kept_v1_only = 0

    for m in modules:
        mtype = m.get('type', '')
        name = m.get('name', '')
        category = m.get('category', '')

        if mtype in v1_types:
            # This is a v1 entry - check if v2 exists
            if (name, category) in v2_modules:
                # v2 exists, skip this v1 entry
                removed_v1 += 1
                continue
            else:
                # v1-only module - keep it, URL will redirect
                kept_v1_only += 1
                new_modules.append(m)
        elif mtype in v2_to_plain:
            # v2 entry - convert to plain type
            m['type'] = v2_to_plain[mtype]
            converted_v2 += 1

            # Clean displayCategory
            dc = m.get('displayCategory', '')
            if dc in display_clean:
                m['displayCategory'] = display_clean[dc]

            # Clean version field
            if 'version' in m and m['version'] == 'v2':
                del m['version']

            new_modules.append(m)
        else:
            # Other types (shouldn't exist but keep them)
            new_modules.append(m)

    data['modules'] = new_modules

    # Update stats
    data['stats']['totalModules'] = len(new_modules)

    # Recount by category
    by_cat = defaultdict(int)
    for m in new_modules:
        cat = m.get('category', 'unknown')
        by_cat[cat] += 1

    data['stats']['by_category'] = dict(by_cat)

    # Count total endpoints
    total_endpoints = sum(m.get('pathCount', 0) for m in new_modules)
    if 'totalEndpoints' in data['stats']:
        data['stats']['totalEndpoints'] = total_endpoints

    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Removed {removed_v1} v1 entries (had v2 equivalent)")
    print(f"Converted {converted_v2} v2 entries to plain type")
    print(f"Kept {kept_v1_only} v1-only entries (no v2 equivalent)")
    print(f"Total modules now: {len(new_modules)}")


if __name__ == '__main__':
    main()
