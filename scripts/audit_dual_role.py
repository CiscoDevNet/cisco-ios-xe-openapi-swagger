#!/usr/bin/env python3
"""Find YANG modules with multiple roles (config + notifications, config + rpcs)
and check if they have specs for each role."""
import os, re


def main():
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yang_dir = os.path.join(BASE, "references", "17181-YANG-modules")
    dual_modules = []

    for fn in sorted(os.listdir(yang_dir)):
        if not fn.endswith('.yang'):
            continue
        name = fn.replace('.yang', '')
        name = re.sub(r'@\d{4}-\d{2}-\d{2}$', '', name)
        try:
            with open(os.path.join(yang_dir, fn), encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except OSError:
            continue

        has_container = bool(re.search(r'^\s+container\s+\w+', content, re.MULTILINE))
        has_list = bool(re.search(r'^\s+list\s+\w+', content, re.MULTILINE))
        has_notification = bool(re.search(r'^\s+notification\s+\w+', content, re.MULTILINE))
        has_rpc = bool(re.search(r'^\s+rpc\s+\w+', content, re.MULTILINE))
        has_augment_native = bool(re.search(r'augment\s+"/ios:', content))
        has_augment_rpc = bool(re.search(r'augment\s+"/ios-xe-rpc:', content))

        # Skip pure augmentation modules
        if has_augment_native and not has_container:
            continue
        if has_augment_rpc and not has_container:
            continue

        has_data = has_container or has_list

        roles = []
        if has_data:
            roles.append('config/data')
        if has_notification:
            roles.append('notification')
        if has_rpc:
            roles.append('rpc')

        if len(roles) > 1:
            spec_locs = []
            folders = {
                'oper': 'swagger-oper-model',
                'cfg': 'swagger-cfg-model',
                'native': 'swagger-native-config-model',
                'openconfig': 'swagger-openconfig-model',
                'ietf': 'swagger-ietf-model',
                'mib': 'swagger-mib-model',
                'rpc': 'swagger-rpc-model',
                'events': 'swagger-events-model',
                'other': 'swagger-other-model',
            }
            for label, folder in folders.items():
                for api in ['api-v2', 'api']:
                    p = os.path.join(BASE, folder, api, name + '.json')
                    if os.path.exists(p):
                        spec_locs.append(label)
                        break  # Don't double-count api + api-v2
            dual_modules.append((name, roles, spec_locs))

    print(f"Modules with MULTIPLE roles: {len(dual_modules)}")
    print()
    print(f"{'Module':<50s} {'Roles':<35s} {'Specs In':<30s} {'Status'}")
    print("-" * 130)
    for name, roles, specs in dual_modules:
        missing = []
        if 'config/data' in roles and not any(s in ('cfg','other','native','oper','ietf','openconfig','mib') for s in specs):
            missing.append('config spec')
        if 'notification' in roles and 'events' not in specs:
            missing.append('events spec')
        if 'rpc' in roles and 'rpc' not in specs:
            missing.append('rpc spec')

        status = 'MISSING: ' + ', '.join(missing) if missing else 'OK'
        print(f"  {name:<48s} {str(roles):<35s} {str(specs):<30s} {status}")


if __name__ == '__main__':
    main()
