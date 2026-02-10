#!/usr/bin/env python3
"""Fix GET operations that use $ref to NotificationResponse by inlining the response.

This resolves 5 GET operations in 3 event spec files where the 200 response
is a $ref to components/responses/NotificationResponse instead of inline content.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES = [
    'swagger-events-model/api/CISCO-LICENSE-MGMT-MIB.json',
    'swagger-events-model/api/CISCO-OSPF-TRAP-MIB.json',
    'swagger-events-model/api/OSPF-TRAP-MIB.json',
]


def main():
    total_fixed = 0
    for relpath in FILES:
        filepath = os.path.join(ROOT, relpath)
        with open(filepath, encoding='utf-8') as f:
            spec = json.load(f)

        nr = spec.get('components', {}).get('responses', {}).get('NotificationResponse', {})
        if not nr:
            print('WARNING: no NotificationResponse in %s' % relpath)
            continue

        fixed = 0
        for pk, pv in spec.get('paths', {}).items():
            op = pv.get('get')
            if not op or not isinstance(op, dict):
                continue
            r200 = op.get('responses', {}).get('200', {})
            if r200.get('$ref') == '#/components/responses/NotificationResponse':
                # Extract trap name from path
                trap_name = pk.split('/')[-1]
                if ':' in trap_name:
                    trap_name = trap_name.split(':', 1)[1]

                # Inline the NotificationResponse content
                op['responses']['200'] = {
                    'description': '%s notification data' % trap_name,
                    'content': nr.get('content', {})
                }
                fixed += 1

        if fixed > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(spec, f, indent=2, ensure_ascii=False)
                f.write('\n')
            print('  %s: inlined %d GET response(s)' % (relpath, fixed))
            total_fixed += fixed

    print('\nTotal: fixed %d GET responses' % total_fixed)


if __name__ == '__main__':
    main()
