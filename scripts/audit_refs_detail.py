#!/usr/bin/env python3
"""Detailed audit of broken $refs and server URL issues."""
import json, os
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

FOLDERS = [
    'swagger-cfg-model','swagger-oper-model','swagger-openconfig-model',
    'swagger-ietf-model','swagger-mib-model','swagger-events-model',
    'swagger-rpc-model','swagger-other-model','swagger-native-config-model'
]

# --- Broken refs by folder ---

def main():

    ref_by_folder = Counter()
    ref_by_file = Counter()
    server_issues = []

    for folder in FOLDERS:
        api_dir = os.path.join(folder, 'api')
        for jf in sorted(os.listdir(api_dir)):
            if not jf.endswith('.json') or jf == 'manifest.json':
                continue
            with open(os.path.join(api_dir, jf), encoding='utf-8') as f:
                spec = json.load(f)
        
            schemas = spec.get('components', {}).get('schemas', {})
        
            broken = set()
            def check_refs(obj):
                if isinstance(obj, dict):
                    if '$ref' in obj:
                        ref = obj['$ref']
                        if ref.startswith('#/components/schemas/'):
                            schema_name = ref.split('/')[-1]
                            if schema_name not in schemas:
                                broken.add(schema_name)
                    for v in obj.values():
                        check_refs(v)
                elif isinstance(obj, list):
                    for v in obj:
                        check_refs(v)
            check_refs(spec)
        
            if broken:
                ref_by_folder[folder] += len(broken)
                ref_by_file[f'{folder}/api/{jf}'] = len(broken)
        
            # Server URL check
            for s in spec.get('servers', []):
                url = s.get('url', '')
                if '10.85.134.65' in url:
                    server_issues.append(('HARDCODED_IP', f'{folder}/api/{jf}', url))
                elif url == 'https://{device}' or url == 'https://{device}:{port}':
                    server_issues.append(('MISSING_RESTCONF', f'{folder}/api/{jf}', url))

    print("=== BROKEN $ref BY FOLDER ===")
    for folder, count in sorted(ref_by_folder.items(), key=lambda x: -x[1]):
        print(f"  {count:4d} unique broken schemas in {folder}")

    print(f"\n=== TOP 20 FILES WITH MOST BROKEN REFS ===")
    for fp, count in sorted(ref_by_file.items(), key=lambda x: -x[1])[:20]:
        print(f"  {count:3d} broken in {fp}")

    print(f"\n=== SERVER URL ISSUES ({len(server_issues)} total) ===")
    by_type = Counter(s[0] for s in server_issues)
    for t, c in by_type.items():
        print(f"  {t}: {c} specs")
        for _, fp, url in [s for s in server_issues if s[0] == t][:5]:
            print(f"    e.g. {fp} -> {url}")

    # Show one sample broken ref file to understand the pattern
    print("\n=== SAMPLE: First file with broken refs ===")
    sample = sorted(ref_by_file.keys())[0] if ref_by_file else None
    if sample:
        with open(sample, encoding='utf-8') as f:
            spec = json.load(f)
        schemas = spec.get('components', {}).get('schemas', {})
        print(f"  File: {sample}")
        print(f"  Existing schemas: {list(schemas.keys())[:5]}...")
    
        broken = set()
        def check_refs2(obj):
            if isinstance(obj, dict):
                if '$ref' in obj:
                    ref = obj['$ref']
                    if ref.startswith('#/components/schemas/'):
                        schema_name = ref.split('/')[-1]
                        if schema_name not in schemas:
                            broken.add(schema_name)
                for v in obj.values():
                    check_refs2(v)
            elif isinstance(obj, list):
                for v in obj:
                    check_refs2(v)
        check_refs2(spec)
        print(f"  Broken refs: {sorted(broken)[:10]}")

if __name__ == '__main__':
    main()
