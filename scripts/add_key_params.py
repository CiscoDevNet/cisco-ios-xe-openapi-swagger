#!/usr/bin/env python3
"""
add_key_params.py — Add OpenAPI path parameters to all keyed paths missing them.

Scans all Swagger spec folders for paths containing ={key} patterns and adds
proper "parameters" arrays to each HTTP method on those paths.

Scope: 3,293 keyed paths across cfg, oper, ietf, openconfig, and other models.
MIB model already has parameters (1,620) and is skipped.

Usage:
  python scripts/add_key_params.py           # dry-run
  python scripts/add_key_params.py --apply   # write changes
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLY = "--apply" in sys.argv

# Folders to process (skip mib/events/rpc which are already done or N/A)
TARGET_FOLDERS = [
    "swagger-cfg-model/api",
    "swagger-oper-model/api",
    "swagger-ietf-model/api",
    "swagger-openconfig-model/api",
    "swagger-other-model/api",
]

# ============================================================
# KEY NAME → TYPE + EXAMPLE MAPPING
# Based on YANG leaf types across all modules
# ============================================================

# Integer keys (counters, indexes, IDs)
INTEGER_KEYS = {
    "id", "index", "slot", "bay", "chassis", "node", "fru",
    "slot-id", "slot-num", "subslot-num", "radio-slot-id",
    "vlan-id", "wlan-id", "vc-id", "vcid", "process-id",
    "as-num", "as-number", "area-id", "table-id", "group-id",
    "key-id", "job-id", "intvl-id", "dlr-ring-id", "ha-pair-id",
    "svc-seq", "top-id", "oper-id", "trace-id", "nonce",
    "priority", "sequence", "seq", "number", "level", "instance",
    "ifIndex", "peer-as", "local-as", "remote-as",
    "sc-id-str", "mpls-label", "local-label", "remote-label",
    "session-id", "subscription-id", "filter-id",
    "lsa-type", "route-type", "metric", "tag", "cost",
    "ep-id", "endpoint-id", "request", "exp",
    "port", "peer-port", "local-port", "remote-port",
    "mcc", "mnc", "date", "spatial-stream",
    "max-bw", "min-bw", "member-id",
    "cos-min", "cos-max",
}

# MAC address keys
MAC_KEYS = {
    "wtp-mac", "ap-mac", "client-mac", "mac", "mac-address",
    "rfid-mac-addr", "eui64", "bssid",
    "src-mac", "dst-mac", "neighbor-mac", "rogue-bssid",
}

# IP address keys
IP_KEYS = {
    "ip", "addr", "address", "peer-address", "peer-ip",
    "source", "destination", "src-addr", "dst-addr",
    "source-address", "destination-address",
    "local-address", "remote-address",
    "next-hop", "gateway", "neighbor-address",
    "router-id", "neighbor-id", "adv-router",
    "source-host", "lsa-id",
}

# Prefix/CIDR keys
PREFIX_KEYS = {
    "prefix", "destination-prefix", "network",
    "route-filter", "ip-prefix",
}

# ============================================================
# TYPE INFERENCE AND EXAMPLE GENERATION
# ============================================================

def infer_type_and_example(key_name):
    """Determine OpenAPI type and example value for a key parameter."""
    kl = key_name.lower().replace("-", "").replace("_", "")
    
    # Exact match first
    if key_name in INTEGER_KEYS:
        return "integer", 1
    if key_name in MAC_KEYS:
        return "string", "00:1a:2b:3c:4d:5e"
    if key_name in IP_KEYS:
        return "string", "10.1.1.1"
    if key_name in PREFIX_KEYS:
        return "string", "10.0.0.0/24"
    
    # Pattern-based inference
    if re.search(r'(index|idx)$', kl):
        return "integer", 1
    if re.search(r'(id|num|number|count|port|level|instance|seq|label|tag|metric|cost)$', kl):
        return "integer", 1
    if re.search(r'^(slot|bay|fru|chassis|node|priority)', kl):
        return "integer", 1
    if re.search(r'(mac|bssid|eui)', kl):
        return "string", "00:1a:2b:3c:4d:5e"
    if re.search(r'(addr|address|ip$|host$|gateway|nexthop|router)', kl):
        return "string", "10.1.1.1"
    if re.search(r'(prefix|network|cidr|subnet)', kl):
        return "string", "10.0.0.0/24"
    if re.search(r'(vlan)', kl):
        return "integer", 100
    if re.search(r'(name|hostname|ifname)', kl):
        return "string", key_name_to_example(key_name)
    if re.search(r'(type|kind|mode|direction|af|afi|safi|family)', kl):
        return "string", key_name_to_example(key_name)
    if re.search(r'(vrf)', kl):
        return "string", "default"
    
    # Default: string
    return "string", key_name_to_example(key_name)


def key_name_to_example(key_name):
    """Generate a realistic example value for a key name."""
    EXAMPLES = {
        "name": "GigabitEthernet1",
        "if-name": "GigabitEthernet1/0/1",
        "interface": "GigabitEthernet1",
        "hostname": "Router1",
        "vrf-name": "default",
        "vrf": "default",
        "profile-name": "default-profile",
        "policy-name": "default-policy",
        "group-name": "group1",
        "identifier": "1",
        "af": "ipv4-unicast",
        "afi": "ipv4",
        "afi-safi": "ipv4-unicast",
        "safi": "unicast",
        "address-family": "ipv4",
        "direction": "inbound",
        "type": "default",
        "model": "C9300-24T",
        "band": "dot11-5ghz",
        "service": "default",
        "cellular-interface": "Cellular0/1/0",
        "access-control-list-name": "MY-ACL",
        "rd-value": "65000:1",
        "ni-name": "default",
        "ni-type": "default",
        "key_udi": "PID:C9300-24T,SN:FCW1234A567",
        "vpn-id": "1",
        "country-code": "US",
        "tag-name": "tag1",
        "day": "monday",
        "filter-type": "by-reference",
        "filter-logical-not": "false",
    }
    if key_name in EXAMPLES:
        return EXAMPLES[key_name]
    
    # Generate from name pattern
    if "name" in key_name:
        return key_name.replace("-name", "") + "-1"
    if "type" in key_name:
        return "default"
    if "id" in key_name.lower():
        return "1"
    
    return key_name.replace("-", "_") + "_value"


def extract_keys_from_path(path_str):
    """Extract individual key names from path like /foo={k1},{k2}/bar={k3}.
    
    Handles both:
    - Comma-separated: ={key1},{key2},{key3}
    - Space-separated: ={key1 key2}  (MIB style)
    - Mixed: /foo={k1},{k2}/bar={k3}
    """
    all_keys = []
    # Find ALL {key} groups in the path (not just after =)
    for match in re.finditer(r'\{([^}]+)\}', path_str):
        content = match.group(1)
        # Space-separated keys within a single {} like {key1 key2}
        if ' ' in content:
            all_keys.extend(content.split())
        else:
            all_keys.append(content)
    
    return all_keys


def build_parameter(key_name):
    """Build an OpenAPI parameter object for a given key name."""
    schema_type, example = infer_type_and_example(key_name)
    
    param = {
        "name": key_name,
        "in": "path",
        "required": True,
        "schema": {
            "type": schema_type
        }
    }
    
    # Add example for string types (integers are self-documenting)
    if schema_type == "string":
        param["example"] = example
    elif example != 1:
        param["example"] = example
    
    return param


def process_file(fpath, fname, stats):
    """Process a single Swagger JSON file, adding parameters to keyed paths."""
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    changed = False
    paths = data.get('paths', {})
    
    for path_key, path_val in paths.items():
        if '={' not in path_key:
            continue
        
        keys = extract_keys_from_path(path_key)
        if not keys:
            continue
        
        # Build parameters array
        params = [build_parameter(k) for k in keys]
        
        # Add/update parameters for each HTTP method
        for method in ['get', 'put', 'patch', 'delete', 'post']:
            if method not in path_val:
                continue
            mv = path_val[method]
            if not isinstance(mv, dict):
                continue
            
            existing = mv.get('parameters', [])
            existing_names = {p.get('name') for p in existing if isinstance(p, dict)}
            expected_names = {p['name'] for p in params}
            
            if expected_names.issubset(existing_names):
                # All expected keys already present — skip
                continue
            
            # Replace with correct full set of parameters
            mv['parameters'] = params
            changed = True
            stats['params_added'] += 1
    
    stats['paths_checked'] += len(paths)
    return data if changed else None


def main():
    stats = {
        'files_checked': 0,
        'files_modified': 0,
        'paths_checked': 0,
        'params_added': 0,
    }
    
    folder_stats = {}
    
    for rel_folder in TARGET_FOLDERS:
        folder = os.path.join(BASE, rel_folder)
        if not os.path.isdir(folder):
            continue
        
        label = rel_folder.split('/')[0].replace('swagger-', '').replace('-model', '')
        folder_stats[label] = {'files': 0, 'params': 0}
        
        for fname in sorted(os.listdir(folder)):
            if not fname.endswith('.json') or fname == 'manifest.json':
                continue
            
            fpath = os.path.join(folder, fname)
            stats['files_checked'] += 1
            
            before = stats['params_added']
            new_data = process_file(fpath, fname, stats)
            after = stats['params_added']
            
            folder_stats[label]['files'] += 1
            folder_stats[label]['params'] += (after - before)
            
            if new_data is not None:
                stats['files_modified'] += 1
                if APPLY:
                    with open(fpath, 'w', encoding='utf-8') as f:
                        json.dump(new_data, f, indent=2, ensure_ascii=False)
                        f.write('\n')
    
    # Summary
    mode = "APPLIED" if APPLY else "DRY-RUN"
    print(f"\n{'='*60}")
    print(f"  {mode}: Add YANG Key Parameters to Swagger Specs")
    print(f"{'='*60}")
    print(f"  Files checked:    {stats['files_checked']}")
    print(f"  Files modified:   {stats['files_modified']}")
    print(f"  Paths checked:    {stats['paths_checked']}")
    print(f"  Parameters added: {stats['params_added']}")
    print()
    print(f"  {'Folder':20s} {'Files':>6s} {'Params Added':>13s}")
    print(f"  {'-'*40}")
    for label, fs in folder_stats.items():
        print(f"  {label:20s} {fs['files']:6d} {fs['params']:13d}")
    print(f"{'='*60}")
    
    if not APPLY:
        print("\n  Run with --apply to write changes to disk.")
    
    # Verify
    if APPLY:
        print("\n  Verification...")
        remaining = 0
        for rel_folder in TARGET_FOLDERS:
            folder = os.path.join(BASE, rel_folder)
            if not os.path.isdir(folder):
                continue
            for fname in sorted(os.listdir(folder)):
                if not fname.endswith('.json') or fname == 'manifest.json':
                    continue
                with open(os.path.join(folder, fname), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for pk, pv in data.get('paths', {}).items():
                    if '={' not in pk:
                        continue
                    for method in ['get', 'put', 'patch', 'delete', 'post']:
                        mv = pv.get(method, {})
                        if isinstance(mv, dict) and 'parameters' not in mv:
                            remaining += 1
                            if remaining <= 5:
                                print(f"    STILL MISSING: {fname} {method} {pk[:80]}")
        print(f"  Remaining keyed methods without params: {remaining}")


if __name__ == '__main__':
    main()
