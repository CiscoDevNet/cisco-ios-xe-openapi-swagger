#!/usr/bin/env python3
"""Add OpenAPI vendor extensions (x-* fields) to all specs.

Adds to every spec:
  info level:
    x-yang-module      - Primary YANG module name
    x-model-type       - cfg/oper/rpc/native/openconfig/ietf/mib/events/other

  path level:
    x-yang-path        - YANG tree path (stripped of module namespace)
    x-restconf-kind    - container/list/list-instance/rpc
    x-list-keys        - List key parameter names (when applicable)

These are pure metadata annotations per OpenAPI 3.0 §4.1 Specification Extensions.
No device-side impact — they help Postman/Bruno users understand the YANG→REST mapping.
"""
import json
import glob
import os
import re
import sys

os.chdir(os.path.join(os.path.dirname(__file__), '..'))

MODEL_FOLDERS = {
    'swagger-cfg-model/api':            'cfg',
    'swagger-oper-model/api':           'oper',
    'swagger-rpc-model/api':            'rpc',
    'swagger-native-config-model/api':  'native',
    'swagger-openconfig-model/api':     'openconfig',
    'swagger-ietf-model/api':           'ietf',
    'swagger-mib-model/api':            'mib',
    'swagger-events-model/api':         'events',
    'swagger-other-model/api':          'other',
}


def extract_yang_module(spec, filename):
    """Extract the primary YANG module name from spec info or paths."""
    info = spec.get('info', {})

    # For most specs, the title IS the module name
    title = info.get('title', '')

    # Native config: special handling
    if 'native' in filename.lower() and 'native' not in title.lower():
        pass  # fall through to path extraction

    # Try to extract from the first path's namespace
    paths = spec.get('paths', {})
    if paths:
        first_path = next(iter(paths))
        # /data/Cisco-IOS-XE-aaa-oper:aaa-data -> Cisco-IOS-XE-aaa-oper
        if '/data/' in first_path and ':' in first_path:
            ns = first_path.split('/data/')[-1].split(':')[0]
            return ns
        # /operations/aaa_actions_rpc:test-aaa-command
        if '/operations/' in first_path and ':' in first_path:
            ns = first_path.split('/operations/')[-1].split(':')[0]
            # Convert underscore RPC names back to hyphen
            return ns.replace('_', '-')

    # Fallback: use filename without extension
    base = os.path.splitext(os.path.basename(filename))[0]
    # Native specs like native-aaa -> Cisco-IOS-XE-native
    if base.startswith('native-'):
        return 'Cisco-IOS-XE-native'
    return base


def extract_yang_path(restconf_path):
    """Convert RESTCONF path to YANG tree path.
    
    /data/Cisco-IOS-XE-aaa-oper:aaa-data/aaa-users -> /aaa-data/aaa-users
    /data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={name} -> /native/interface/GigabitEthernet={name}
    /operations/aaa_actions_rpc:test-aaa-command -> /test-aaa-command
    """
    if '/data/' in restconf_path:
        after_data = restconf_path.split('/data/')[-1]
        # Remove module namespace prefix (everything before first colon)
        if ':' in after_data:
            after_ns = after_data.split(':', 1)[1]
        else:
            after_ns = after_data
        return '/' + after_ns
    elif '/operations/' in restconf_path:
        after_ops = restconf_path.split('/operations/')[-1]
        if ':' in after_ops:
            after_ns = after_ops.split(':', 1)[1]
        else:
            after_ns = after_ops
        return '/' + after_ns
    return restconf_path


def extract_list_keys(restconf_path):
    """Extract list key names from path parameters.
    
    /data/.../GigabitEthernet={name} -> ["name"]
    /data/.../protocol={identifier},{name} -> ["identifier", "name"]
    """
    keys = re.findall(r'=\{([^}]+)\}', restconf_path)
    # Split comma-separated keys: {identifier},{name} -> ["identifier", "name"]
    result = []
    for k in keys:
        result.extend(k.split(','))
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for k in result:
        kk = k.strip('{}')
        if kk not in seen:
            seen.add(kk)
            unique.append(kk)
    return unique


def determine_kind(restconf_path, model_type):
    """Determine the RESTCONF resource kind."""
    if model_type == 'rpc' or '/operations/' in restconf_path:
        return 'rpc'
    if model_type == 'events':
        return 'notification'

    # Check if this is a list instance (has key parameters)
    if '={' in restconf_path:
        # Check if the final segment has keys
        segments = restconf_path.rstrip('/').split('/')
        last_seg = segments[-1] if segments else ''
        if '={' in last_seg:
            return 'list-instance'
        else:
            # Keys are in a parent segment, this is a child container/list
            return 'container'
    else:
        return 'container'


def process_spec(filepath, model_type):
    """Add vendor extensions to a single spec file."""
    with open(filepath, encoding='utf-8') as f:
        spec = json.load(f)

    filename = os.path.basename(filepath)
    modified = False

    # --- Info-level extensions ---
    info = spec.get('info', {})

    # x-yang-module
    if 'x-yang-module' not in info:
        yang_module = extract_yang_module(spec, filename)
        info['x-yang-module'] = yang_module
        modified = True

    # x-model-type
    if 'x-model-type' not in info:
        info['x-model-type'] = model_type
        modified = True

    spec['info'] = info

    # --- Path-level extensions ---
    paths = spec.get('paths', {})
    for path_key, path_obj in paths.items():
        if not isinstance(path_obj, dict):
            continue

        # x-yang-path
        if 'x-yang-path' not in path_obj:
            yang_path = extract_yang_path(path_key)
            path_obj['x-yang-path'] = yang_path
            modified = True

        # x-restconf-kind
        if 'x-restconf-kind' not in path_obj:
            kind = determine_kind(path_key, model_type)
            path_obj['x-restconf-kind'] = kind
            modified = True

        # x-list-keys (only for paths with key parameters)
        if 'x-list-keys' not in path_obj:
            keys = extract_list_keys(path_key)
            if keys:
                path_obj['x-list-keys'] = keys
                modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
            f.write('\n')

    return modified


def main():
    total_specs = 0
    total_modified = 0
    info_extensions = 0
    path_extensions = 0

    for folder, model_type in MODEL_FOLDERS.items():
        pattern = os.path.join(folder, '*.json')
        files = sorted(glob.glob(pattern))
        # Skip non-spec files
        files = [f for f in files if 'manifest' not in os.path.basename(f)]

        folder_modified = 0
        for filepath in files:
            try:
                was_modified = process_spec(filepath, model_type)
                total_specs += 1
                if was_modified:
                    total_modified += 1
                    folder_modified += 1
            except Exception as e:
                print(f"  ERROR: {filepath}: {e}")

        print(f"  {model_type:12s}: {len(files):>4} specs, {folder_modified:>4} modified")

    print(f"\n{'='*50}")
    print(f"Total specs processed: {total_specs}")
    print(f"Total specs modified:  {total_modified}")

    # Verification: spot-check a few specs
    print(f"\n--- Spot Check ---")
    check_files = [
        'swagger-cfg-model/api/Cisco-IOS-XE-app-hosting-cfg.json',
        'swagger-oper-model/api/Cisco-IOS-XE-aaa-oper.json',
        'swagger-native-config-model/api/native-aaa.json',
        'swagger-openconfig-model/api/openconfig-interfaces.json',
    ]
    for cf in check_files:
        if os.path.exists(cf):
            with open(cf, encoding='utf-8') as f:
                d = json.load(f)
            info = d.get('info', {})
            first_path_key = next(iter(d.get('paths', {})), None)
            first_path = d['paths'][first_path_key] if first_path_key else {}
            print(f"\n  {os.path.basename(cf)}:")
            print(f"    x-yang-module: {info.get('x-yang-module', 'MISSING')}")
            print(f"    x-model-type:  {info.get('x-model-type', 'MISSING')}")
            if first_path_key:
                print(f"    path: {first_path_key[:80]}...")
                print(f"      x-yang-path:     {first_path.get('x-yang-path', 'MISSING')}")
                print(f"      x-restconf-kind: {first_path.get('x-restconf-kind', 'MISSING')}")
                keys = first_path.get('x-list-keys')
                if keys:
                    print(f"      x-list-keys:     {keys}")


if __name__ == '__main__':
    main()
