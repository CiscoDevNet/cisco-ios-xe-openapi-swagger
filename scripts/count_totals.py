#!/usr/bin/env python3
"""Quick script to read all manifests and count totals."""
import json
import os

root = '.'
folders = [
    'swagger-oper-model', 'swagger-rpc-model', 'swagger-cfg-model',
    'swagger-openconfig-model', 'swagger-ietf-model', 'swagger-mib-model',
    'swagger-events-model', 'swagger-native-config-model', 'swagger-other-model'
]

def main():
    print("=== Current manifest values ===")
    total_mp = 0
    total_mo = 0
    for f in folders:
        mf = os.path.join(root, f, 'api', 'manifest.json')
        if os.path.exists(mf):
            try:
                with open(mf, 'r', encoding='utf-8') as fh:
                    m = json.load(fh)
                tp = m.get('total_paths', '?')
                to = m.get('total_operations', '?')
                print(f"  {f}: paths={tp}, ops={to}")
                if isinstance(tp, int):
                    total_mp += tp
                if isinstance(to, int):
                    total_mo += to
            except Exception as e:
                print(f"  {f}: ERROR reading manifest: {e}")

    print(f"\n  Manifest totals: paths={total_mp}, ops={total_mo}")

    print("\n=== Actual counted values ===")
    exclude = {'manifest.json', 'all-operations.json', 'all-rpc-operations.json',
               'all-config.json', 'all-ietf.json', 'all-openconfig.json',
               'all-mib.json', 'all-events.json', 'all-other.json'}
    grand_paths = 0
    grand_ops = 0
    for f in folders:
        api_dir = os.path.join(root, f, 'api')
        if not os.path.isdir(api_dir):
            continue
        f_paths = 0
        f_ops = 0
        for fn in sorted(os.listdir(api_dir)):
            if fn in exclude or not fn.endswith('.json'):
                continue
            fp = os.path.join(api_dir, fn)
            try:
                with open(fp, 'r', encoding='utf-8') as fh:
                    spec = json.load(fh)
                paths = spec.get('paths', {})
                p = len(paths)
                o = sum(1 for pk in paths for m in ['get', 'put', 'patch', 'delete', 'post'] if m in paths[pk])
                f_paths += p
                f_ops += o
            except (OSError, json.JSONDecodeError):
                pass
        print(f"  {f}: paths={f_paths}, ops={f_ops}")
        grand_paths += f_paths
        grand_ops += f_ops

    print(f"\n  Actual totals: paths={grand_paths}, ops={grand_ops}")
    print(f"\n  Delta: +{grand_paths - total_mp} paths, +{grand_ops - total_mo} ops")


if __name__ == '__main__':
    main()
