#!/usr/bin/env python3
"""Add missing operationIds to all OpenAPI specs that lack them.

Pattern: {method}-{lastSegment}-{index}
  - method: get, put, post, patch, delete
  - lastSegment: last path segment (cleaned of keys/colons)
  - index: counter to ensure uniqueness within spec

Targets: swagger-mib-model (4,272), swagger-other-model (1,534), swagger-events-model (133)
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDERS = [
    'swagger-mib-model',
    'swagger-other-model',
    'swagger-events-model',
    'swagger-cfg-model',
    'swagger-oper-model',
    'swagger-openconfig-model',
    'swagger-ietf-model',
    'swagger-rpc-model',
    'swagger-native-config-model',
]

def make_operation_id(method, path, used_ids):
    """Generate a unique operationId from HTTP method + path."""
    # Extract last meaningful segment from path
    segments = [s for s in path.split('/') if s and s != 'data']
    if not segments:
        base = 'root'
    else:
        last = segments[-1]
        # Remove key parameters like ={foo} or ={foo},{bar}
        last = re.sub(r'=\{[^}]+\}(,\{[^}]+\})*', '', last)
        # Remove module prefix (e.g., ATM-MIB: or Cisco-IOS-XE-native:)
        if ':' in last:
            last = last.split(':', 1)[1]
        # Clean to valid identifier chars
        base = re.sub(r'[^a-zA-Z0-9_-]', '', last)
        if not base:
            base = 'resource'

    candidate = '%s-%s' % (method, base)
    if candidate not in used_ids:
        used_ids.add(candidate)
        return candidate

    # Add numeric suffix for uniqueness
    i = 2
    while True:
        suffixed = '%s-%s-%d' % (method, base, i)
        if suffixed not in used_ids:
            used_ids.add(suffixed)
            return suffixed
        i += 1

def process_spec(filepath):
    """Add operationIds to a spec. Returns (added_count, already_had)."""
    with open(filepath, encoding='utf-8') as f:
        spec = json.load(f)

    # Collect existing operationIds
    used_ids = set()
    for pv in spec.get('paths', {}).values():
        if not isinstance(pv, dict):
            continue
        for m in ('get', 'post', 'put', 'patch', 'delete'):
            op = pv.get(m)
            if op and isinstance(op, dict) and op.get('operationId'):
                used_ids.add(op['operationId'])

    added = 0
    already = 0
    for path, pv in spec.get('paths', {}).items():
        if not isinstance(pv, dict):
            continue
        for m in ('get', 'post', 'put', 'patch', 'delete'):
            op = pv.get(m)
            if not op or not isinstance(op, dict):
                continue
            if op.get('operationId'):
                already += 1
                continue
            op['operationId'] = make_operation_id(m, path, used_ids)
            added += 1

    if added > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
            f.write('\n')

    return added, already

def main():
    total_added = 0
    total_already = 0
    files_modified = 0

    for folder in FOLDERS:
        api_dir = os.path.join(ROOT, folder, 'api')
        if not os.path.isdir(api_dir):
            continue
        folder_added = 0
        for jf in sorted(os.listdir(api_dir)):
            if not jf.endswith('.json') or jf == 'manifest.json':
                continue
            filepath = os.path.join(api_dir, jf)
            added, already = process_spec(filepath)
            if added > 0:
                files_modified += 1
                folder_added += added
            total_added += added
            total_already += already
        if folder_added > 0:
            print('  %s: added %d operationIds' % (folder, folder_added))

    print('\nTotal: added %d operationIds across %d files (%d already had them)' % (
        total_added, files_modified, total_already))

if __name__ == '__main__':
    main()
