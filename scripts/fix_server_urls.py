#!/usr/bin/env python3
"""Fix server URLs across all specs:
1. Replace hardcoded 10.85.134.65 with {device} variable
2. Add /restconf suffix where missing
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

FOLDERS = [
    'swagger-cfg-model','swagger-oper-model','swagger-openconfig-model',
    'swagger-ietf-model','swagger-mib-model','swagger-events-model',
    'swagger-rpc-model','swagger-other-model','swagger-native-config-model'
]

CANONICAL_SERVER = {
    "url": "https://{device}/restconf",
    "description": "RESTCONF server",
    "variables": {
        "device": {
            "default": "10.1.1.1",
            "description": "Device hostname or IP address"
        }
    }
}

fixed_hardcoded = 0
fixed_restconf = 0
fixed_files = set()

for folder in FOLDERS:
    api_dir = os.path.join(folder, 'api')
    for jf in sorted(os.listdir(api_dir)):
        if not jf.endswith('.json') or jf == 'manifest.json':
            continue
        fp = os.path.join(api_dir, jf)
        with open(fp, encoding='utf-8') as f:
            spec = json.load(f)
        
        modified = False
        servers = spec.get('servers', [])
        
        for i, s in enumerate(servers):
            url = s.get('url', '')
            
            # Fix 1: Hardcoded IP -> variable
            if '10.85.134.65' in url:
                new_url = url.replace('10.85.134.65', '{device}')
                servers[i] = dict(CANONICAL_SERVER)
                if '/restconf' in new_url:
                    servers[i]['url'] = new_url
                else:
                    servers[i]['url'] = new_url + '/restconf' if not new_url.endswith('/restconf') else new_url
                modified = True
                fixed_hardcoded += 1
            
            # Fix 2: Missing /restconf suffix
            elif url in ('https://{device}', 'https://{device}:{port}'):
                servers[i]['url'] = url + '/restconf'
                if 'description' not in servers[i]:
                    servers[i]['description'] = 'RESTCONF server'
                modified = True
                fixed_restconf += 1
        
        if modified:
            spec['servers'] = servers
            with open(fp, 'w', encoding='utf-8') as f:
                json.dump(spec, f, indent=2, ensure_ascii=False)
                f.write('\n')
            fixed_files.add(fp)

print(f"Fixed hardcoded IPs: {fixed_hardcoded}")
print(f"Fixed missing /restconf: {fixed_restconf}")
print(f"Total files modified: {len(fixed_files)}")
