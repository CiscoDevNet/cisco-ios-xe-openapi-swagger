#!/usr/bin/env python3
"""Add missing v2 RPC entries to search-index.json."""

import json
import os
from pathlib import Path

base = Path(__file__).parent.parent

def main():
    with open(base / 'search-index.json', encoding='utf-8') as f:
        data = json.load(f)

    with open(base / 'swagger-rpc-model' / 'api' / 'manifest.json') as f:
        manifest = json.load(f)

    v2_modules = set(manifest['modules'])
    existing_v2 = {e['name'] for e in data['modules'] if e.get('type') == 'rpc-v2'}
    missing = v2_modules - existing_v2

    added = 0
    for mod_name in sorted(missing):
        spec_path = base / 'swagger-rpc-model' / 'api' / f'{mod_name}.json'
        if not spec_path.exists():
            continue
        with open(spec_path, encoding='utf-8') as f:
            spec = json.load(f)

        desc = spec.get('info', {}).get('description', f'RPC operations from {mod_name}')
        paths = spec.get('paths', {})
        path_count = len(paths)

        keywords = set()
        for p, ops in paths.items():
            rpc_name = p.split(':')[-1] if ':' in p else p.split('/')[-1]
            keywords.add(rpc_name.lower())
            for method_data in ops.values():
                if isinstance(method_data, dict):
                    summary = method_data.get('summary', '')
                    for word in summary.lower().split():
                        if len(word) > 3:
                            keywords.add(word)

        entry = {
            'name': mod_name,
            'type': 'rpc-v2',
            'category': 'swagger-rpc-model',
            'displayCategory': 'RPC v2 (Deep)',
            'emoji': '\U0001f527',
            'description': desc[:200],
            'swaggerUrl': f'swagger-rpc-model/index.html#spec={mod_name}',
            'keywords': sorted(list(keywords))[:30],
            'pathCount': path_count,
            'version': 'v2'
        }
        data['modules'].append(entry)
        added += 1
        print(f'Added: {mod_name} ({path_count} RPCs)')

    data['stats']['totalModules'] = len(data['modules'])
    total_v2_rpc = sum(1 for e in data['modules'] if e.get('type') == 'rpc-v2')
    print(f"\nTotal modules in search index: {len(data['modules'])}")
    print(f"v2 RPC entries now: {total_v2_rpc}")

    with open(base / 'search-index.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\nAdded {added} v2 RPC entries to search-index.json")

if __name__ == '__main__':
    main()
