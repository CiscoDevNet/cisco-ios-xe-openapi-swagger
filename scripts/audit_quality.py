#!/usr/bin/env python3
"""Comprehensive quality audit of all Swagger specs."""
import json, os, glob, re
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

issues = []
stats = Counter()

FOLDERS = [
    'swagger-cfg-model','swagger-oper-model','swagger-openconfig-model',
    'swagger-ietf-model','swagger-mib-model','swagger-events-model',
    'swagger-rpc-model','swagger-other-model','swagger-native-config-model'
]


def main():

    for folder in FOLDERS:
        api_dir = os.path.join(folder, 'api')
        json_files = sorted([f for f in os.listdir(api_dir) if f.endswith('.json') and f != 'manifest.json'])
    
        for jf in json_files:
            fp = os.path.join(api_dir, jf)
            stats['files'] += 1
        
            try:
                with open(fp, encoding='utf-8') as f:
                    spec = json.load(f)
            except Exception as e:
                issues.append(('CRITICAL', f'{folder}/api/{jf}', f'Invalid JSON: {e}'))
                continue
        
            # Check required fields
            for field in ['openapi', 'info', 'paths']:
                if field not in spec:
                    issues.append(('HIGH', f'{folder}/api/{jf}', f'Missing required field: {field}'))
        
            info = spec.get('info', {})
        
            # Check info.description
            desc = info.get('description', '')
            if not desc:
                issues.append(('MEDIUM', f'{folder}/api/{jf}', 'No description in info'))
            elif 'TODO' in desc or 'FIXME' in desc or 'PLACEHOLDER' in desc.upper():
                issues.append(('MEDIUM', f'{folder}/api/{jf}', f'Placeholder text in description'))
        
            # Check servers
            servers = spec.get('servers', [])
            if not servers:
                issues.append(('LOW', f'{folder}/api/{jf}', 'No servers defined'))
            else:
                for s in servers:
                    url = s.get('url', '')
                    if not url or url == '/':
                        issues.append(('MEDIUM', f'{folder}/api/{jf}', f'Empty or root server URL'))
                    elif '{host}' not in url and 'CHANGEME' in url:
                        issues.append(('MEDIUM', f'{folder}/api/{jf}', f'Placeholder server URL'))
        
            # Check paths
            paths = spec.get('paths', {})
            if not paths:
                issues.append(('MEDIUM', f'{folder}/api/{jf}', 'Spec has no paths'))
        
            for path_key, path_val in paths.items():
                if not isinstance(path_val, dict):
                    continue
                methods = [m for m in path_val if m in ('get','post','put','patch','delete')]
                if not methods:
                    issues.append(('LOW', f'{folder}/api/{jf}', f'Path has no methods: {path_key[:80]}'))
            
                # Check for empty/missing operationIds  
                for method in methods:
                    op = path_val.get(method, {})
                    if not isinstance(op, dict):
                        continue
                
                    # Check for empty responses
                    responses = op.get('responses', {})
                    if not responses:
                        issues.append(('LOW', f'{folder}/api/{jf}', f'{method.upper()} {path_key[:60]} has no responses'))
                        stats['no_responses'] += 1
                
                    # Check for placeholder examples
                    if 'requestBody' in op:
                        rb = op['requestBody']
                        content = rb.get('content', {})
                        for ct, cv in content.items():
                            example = cv.get('example', {})
                            schema = cv.get('schema', {})
                            if isinstance(example, dict):
                                for k, v in example.items():
                                    if isinstance(v, str) and v in ('string', 'TODO', 'FIXME', 'CHANGEME'):
                                        issues.append(('MEDIUM', f'{folder}/api/{jf}', f'{method.upper()} {path_key[:40]} has placeholder example value "{v}" for key "{k}"'))
                                        stats['placeholder_examples'] += 1
        
            # Check externalDocs URLs
            ext_docs = spec.get('externalDocs', {})
            if ext_docs:
                url = ext_docs.get('url', '')
                if not url:
                    issues.append(('LOW', f'{folder}/api/{jf}', 'externalDocs has no URL'))
        
            # Check for duplicate paths (shouldn't happen in JSON but just in case)
            stats['specs_checked'] += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"QUALITY AUDIT RESULTS")
    print(f"{'='*60}")
    print(f"Specs checked: {stats['specs_checked']}")
    print(f"Total issues found: {len(issues)}")

    by_severity = Counter(i[0] for i in issues)
    for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        if by_severity[sev]:
            print(f"  {sev}: {by_severity[sev]}")

    print(f"\n--- Issues by type ---")
    by_msg = Counter()
    for sev, loc, msg in issues:
        # Generalize the message
        if 'placeholder example' in msg:
            by_msg['Placeholder example values'] += 1
        elif 'no responses' in msg.lower():
            by_msg['Operations with no responses'] += 1
        elif 'No description' in msg:
            by_msg['Specs with no description'] += 1
        elif 'No servers' in msg:
            by_msg['Specs with no servers'] += 1
        elif 'no methods' in msg.lower():
            by_msg['Paths with no methods'] += 1
        elif 'no paths' in msg.lower():
            by_msg['Specs with no paths'] += 1
        else:
            by_msg[msg[:50]] += 1

    for msg, count in sorted(by_msg.items(), key=lambda x: -x[1]):
        print(f"  {count:4d} x {msg}")

    # Print first 30 specific issues
    print(f"\n--- First 30 issues ---")
    for sev, loc, msg in issues[:30]:
        print(f"  [{sev}] {loc}: {msg}")

    if len(issues) > 30:
        print(f"  ... and {len(issues) - 30} more")

if __name__ == '__main__':
    main()
