#!/usr/bin/env python3
"""Add top-level tags definitions to specs that are missing them.

Derives tag name and description from the operation-level tags already
present in each spec. This ensures Swagger UI properly groups operations.

Targets: swagger-events-model (90), swagger-rpc-model (58), swagger-oper-model (1)
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDERS = [
    'swagger-events-model',
    'swagger-rpc-model',
    'swagger-oper-model',
    'swagger-cfg-model',
    'swagger-openconfig-model',
    'swagger-ietf-model',
    'swagger-mib-model',
    'swagger-other-model',
    'swagger-native-config-model',
]

# Map folder to description template
FOLDER_DESC = {
    'swagger-events-model': 'SNMP notification and event subscriptions for %s',
    'swagger-rpc-model': 'RPC operations for %s',
    'swagger-oper-model': 'Operational state data for %s',
    'swagger-cfg-model': 'Configuration operations for %s',
    'swagger-openconfig-model': 'OpenConfig operations for %s',
    'swagger-ietf-model': 'IETF model operations for %s',
    'swagger-mib-model': 'MIB operations for %s',
    'swagger-other-model': 'Operations for %s',
    'swagger-native-config-model': 'Native configuration for %s',
}


def process_spec(filepath, folder):
    """Add top-level tags if missing. Returns True if modified."""
    with open(filepath, encoding='utf-8') as f:
        spec = json.load(f)

    if spec.get('tags'):
        return False

    # Collect unique tags from operations
    op_tags = set()
    for pv in spec.get('paths', {}).values():
        if not isinstance(pv, dict):
            continue
        for m in ('get', 'post', 'put', 'patch', 'delete'):
            op = pv.get(m)
            if op and isinstance(op, dict):
                for t in op.get('tags', []):
                    op_tags.add(t)

    if not op_tags:
        return False

    desc_template = FOLDER_DESC.get(folder, 'Operations for %s')
    tags = []
    for tag_name in sorted(op_tags):
        tags.append({
            'name': tag_name,
            'description': desc_template % tag_name
        })

    # Insert tags after info section
    spec['tags'] = tags

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
        f.write('\n')

    return True


def main():
    total = 0
    for folder in FOLDERS:
        api_dir = os.path.join(ROOT, folder, 'api')
        if not os.path.isdir(api_dir):
            continue
        count = 0
        for jf in sorted(os.listdir(api_dir)):
            if not jf.endswith('.json') or jf == 'manifest.json':
                continue
            filepath = os.path.join(api_dir, jf)
            if process_spec(filepath, folder):
                count += 1
        if count > 0:
            print('  %s: added tags to %d specs' % (folder, count))
            total += count

    print('\nTotal: added top-level tags to %d specs' % total)


if __name__ == '__main__':
    main()
