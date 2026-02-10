#!/usr/bin/env python3
"""audit_keys.py - Audit keyed paths and missing parameters across all Swagger specs."""
import json, os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FOLDERS = [
    ("swagger-cfg-model/api", "cfg"),
    ("swagger-oper-model/api", "oper"),
    ("swagger-ietf-model/api", "ietf"),
    ("swagger-openconfig-model/api", "openconfig"),
    ("swagger-mib-model/api", "mib"),
    ("swagger-other-model/api", "other"),
    ("swagger-native-config-model/api", "native"),
    ("swagger-rpc-model/api", "rpc"),
    ("swagger-events-model/api", "events"),
]

def extract_keys_from_path(path_str):
    """Extract key names from a RESTCONF path like /foo/bar={k1},{k2}/baz={k3}."""
    keys = []
    # Find all ={...} segments
    for match in re.finditer(r'=\{([^}]+)\}', path_str):
        key_str = match.group(1)
        keys.append(key_str)
    # Also handle space-separated keys within a single {} like ={k1 k2}
    # Split by comma for comma-separated, or by space for space-separated
    all_keys = []
    for k in keys:
        if ',' in path_str[path_str.index(k)-1:path_str.index(k)] if k in path_str else False:
            all_keys.append(k)
        else:
            all_keys.append(k)
    return keys

def audit():
    print(f"{'Folder':15s} {'Paths':>6s} {'Keyed':>6s} {'HasParams':>10s} {'Missing':>8s}")
    print("-" * 50)
    
    grand_total = grand_keyed = grand_has = grand_missing = 0
    
    for rel_folder, label in FOLDERS:
        folder = os.path.join(BASE, rel_folder)
        if not os.path.isdir(folder):
            continue
        
        tp = kp = mp = hp = 0
        
        for fname in sorted(os.listdir(folder)):
            if not fname.endswith('.json') or fname == 'manifest.json':
                continue
            with open(os.path.join(folder, fname), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for path_key, path_val in data.get('paths', {}).items():
                tp += 1
                if '={' in path_key:
                    kp += 1
                    found_param = False
                    for method in ['get', 'put', 'patch', 'delete', 'post']:
                        mv = path_val.get(method, {})
                        if isinstance(mv, dict) and 'parameters' in mv:
                            found_param = True
                            break
                    if found_param:
                        hp += 1
                    else:
                        mp += 1
        
        print(f"{label:15s} {tp:6d} {kp:6d} {hp:10d} {mp:8d}")
        grand_total += tp
        grand_keyed += kp
        grand_has += hp
        grand_missing += mp
    
    print("-" * 50)
    print(f"{'TOTAL':15s} {grand_total:6d} {grand_keyed:6d} {grand_has:10d} {grand_missing:8d}")
    print(f"\nKeyed paths needing parameters: {grand_missing}")

if __name__ == '__main__':
    audit()
