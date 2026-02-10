#!/usr/bin/env python3
"""Audit server URLs, $ref integrity, and externalDocs across all specs."""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

issues = []
server_url_count = {}
ext_docs_count = {}

FOLDERS = [
    'swagger-cfg-model','swagger-oper-model','swagger-openconfig-model',
    'swagger-ietf-model','swagger-mib-model','swagger-events-model',
    'swagger-rpc-model','swagger-other-model','swagger-native-config-model'
]

for folder in FOLDERS:
    api_dir = os.path.join(folder, 'api')
    for jf in sorted(os.listdir(api_dir)):
        if not jf.endswith('.json') or jf == 'manifest.json':
            continue
        with open(os.path.join(api_dir, jf), encoding='utf-8') as f:
            spec = json.load(f)
        
        # Collect server URL patterns
        for s in spec.get('servers', []):
            url = s.get('url', '')
            server_url_count[url] = server_url_count.get(url, 0) + 1
        
        # Collect externalDocs
        ext = spec.get('externalDocs', {})
        if ext:
            eurl = ext.get('url', 'NO_URL')
            ext_docs_count[eurl] = ext_docs_count.get(eurl, 0) + 1
        
        # Check ref integrity
        schemas = spec.get('components', {}).get('schemas', {})
        def check_refs(obj):
            if isinstance(obj, dict):
                if '$ref' in obj:
                    ref = obj['$ref']
                    if ref.startswith('#/components/schemas/'):
                        schema_name = ref.split('/')[-1]
                        if schema_name not in schemas:
                            issues.append(f'BROKEN_REF: {folder}/api/{jf} -> {ref}')
                for v in obj.values():
                    check_refs(v)
            elif isinstance(obj, list):
                for v in obj:
                    check_refs(v)
        check_refs(spec)
        
        # Check for paths with parameters in URL but no parameters array
        paths = spec.get('paths', {})
        for path_key, path_val in paths.items():
            if not isinstance(path_val, dict):
                continue
            # Check for duplicate operationIds within this spec
            for method in ('get','post','put','patch','delete'):
                op = path_val.get(method)
                if not op or not isinstance(op, dict):
                    continue

print("=== Server URLs ===")
for url, count in sorted(server_url_count.items(), key=lambda x: -x[1]):
    print(f"  {count:3d}x  {url}")

print(f"\n=== ExternalDocs URLs (top 10) ===")
for url, count in sorted(ext_docs_count.items(), key=lambda x: -x[1])[:10]:
    print(f"  {count:3d}x  {url[:100]}")

print(f"\n=== Broken schema refs: {len(issues)} ===")
for i in issues[:20]:
    print(f"  {i}")
if len(issues) > 20:
    print(f"  ... and {len(issues)-20} more")
