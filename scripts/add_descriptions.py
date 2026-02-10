#!/usr/bin/env python3
"""Add missing descriptions to operations that have summaries but no descriptions.

Derives description from the HTTP method + summary + resource path.
Targets: native-config (579), other (394), openconfig (9)
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDERS = [
    'swagger-native-config-model',
    'swagger-other-model',
    'swagger-openconfig-model',
    'swagger-cfg-model',
    'swagger-oper-model',
    'swagger-ietf-model',
    'swagger-mib-model',
    'swagger-events-model',
    'swagger-rpc-model',
]

METHOD_TEMPLATES = {
    'get': 'Retrieve %s from the RESTCONF interface',
    'put': 'Create or replace %s via the RESTCONF interface',
    'post': 'Create %s via the RESTCONF interface',
    'patch': 'Partially update %s via the RESTCONF interface',
    'delete': 'Remove %s from the device configuration via the RESTCONF interface',
}


def extract_resource_label(path, summary):
    """Build a human-readable resource label from path or summary."""
    # Use summary if available - it's already human-friendly
    if summary:
        # Remove method-like prefixes: "Get X data", "Configure X", etc.
        cleaned = re.sub(
            r'^(Get|Retrieve|Create or replace|Create|Update|Modify|Delete|Remove|Configure|Partially modify)\s+',
            '', summary, flags=re.IGNORECASE)
        if cleaned:
            # lowercase first char
            return cleaned[0].lower() + cleaned[1:]

    # Fall back to last path segment
    segments = [s for s in path.split('/') if s and s != 'data']
    if not segments:
        return 'this resource'
    last = segments[-1]
    last = re.sub(r'=\{[^}]+\}(,\{[^}]+\})*', '', last)
    if ':' in last:
        last = last.split(':', 1)[1]
    # Convert camelCase/kebab to readable
    readable = re.sub(r'([a-z])([A-Z])', r'\1 \2', last)
    readable = readable.replace('-', ' ').replace('_', ' ').lower()
    return readable + ' data'


def process_spec(filepath):
    """Add descriptions where missing. Returns count added."""
    with open(filepath, encoding='utf-8') as f:
        spec = json.load(f)

    added = 0
    for path, pv in spec.get('paths', {}).items():
        if not isinstance(pv, dict):
            continue
        for m in ('get', 'post', 'put', 'patch', 'delete'):
            op = pv.get(m)
            if not op or not isinstance(op, dict):
                continue
            if op.get('description'):
                continue

            summary = op.get('summary', '')
            resource = extract_resource_label(path, summary)
            template = METHOD_TEMPLATES.get(m, 'Perform operation on %s')
            op['description'] = template % resource
            added += 1

    if added > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
            f.write('\n')

    return added


def main():
    total = 0
    files_modified = 0

    for folder in FOLDERS:
        api_dir = os.path.join(ROOT, folder, 'api')
        if not os.path.isdir(api_dir):
            continue
        folder_count = 0
        for jf in sorted(os.listdir(api_dir)):
            if not jf.endswith('.json') or jf == 'manifest.json':
                continue
            filepath = os.path.join(api_dir, jf)
            added = process_spec(filepath)
            if added > 0:
                files_modified += 1
                folder_count += added
        if folder_count > 0:
            print('  %s: added %d descriptions' % (folder, folder_count))
            total += folder_count

    print('\nTotal: added %d descriptions across %d files' % (total, files_modified))


if __name__ == '__main__':
    main()
