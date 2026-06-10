#!/usr/bin/env python3
"""Add externalDocs to all OpenAPI specs linking to relevant Cisco DevNet docs.

Maps each model folder to the appropriate external documentation:
- Cisco IOS XE models → Cisco DevNet IOS XE Programmability guide
- OpenConfig models → openconfig GitHub repo
- IETF models → IETF YANG GitHub repo
- MIB models → Cisco SNMP Object Navigator
- Native config → Cisco IOS XE native YANG guide
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ExternalDocs mapping by folder
EXTERNAL_DOCS = {
    'swagger-cfg-model': {
        'description': 'Cisco IOS XE YANG Configuration Models - Cisco DevNet',
        'url': 'https://developer.cisco.com/iosxe/'
    },
    'swagger-oper-model': {
        'description': 'Cisco IOS XE YANG Operational Models - Cisco DevNet',
        'url': 'https://developer.cisco.com/iosxe/'
    },
    'swagger-openconfig-model': {
        'description': 'OpenConfig YANG Models - GitHub',
        'url': 'https://github.com/openconfig/public/tree/master/release/models'
    },
    'swagger-ietf-model': {
        'description': 'IETF YANG Models - GitHub',
        'url': 'https://github.com/YangModels/yang/tree/main/standard/ietf'
    },
    'swagger-mib-model': {
        'description': 'Cisco SNMP Object Navigator',
        'url': 'https://snmp.cloudapps.cisco.com/Support/IOS/do/BrowseMIB.do'
    },
    'swagger-events-model': {
        'description': 'Cisco IOS XE NETCONF/YANG Event Notifications - Cisco DevNet',
        'url': 'https://developer.cisco.com/iosxe/'
    },
    'swagger-rpc-model': {
        'description': 'Cisco IOS XE YANG RPC Operations - Cisco DevNet',
        'url': 'https://developer.cisco.com/iosxe/'
    },
    'swagger-other-model': {
        'description': 'Cisco IOS XE YANG Models - Cisco DevNet',
        'url': 'https://developer.cisco.com/iosxe/'
    },
    'swagger-native-config-model': {
        'description': 'Cisco IOS XE Native YANG Configuration Guide - Cisco DevNet',
        'url': 'https://developer.cisco.com/iosxe/'
    },
}

FOLDERS = list(EXTERNAL_DOCS.keys())


def process_spec(filepath, folder):
    """Add externalDocs if missing. Returns True if modified."""
    with open(filepath, encoding='utf-8') as f:
        spec = json.load(f)

    if spec.get('externalDocs'):
        return False

    spec['externalDocs'] = EXTERNAL_DOCS[folder].copy()

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
        f.write('\n')

    return True


def main():
    total = 0
    for folder in FOLDERS:
        api_dir = os.path.join(ROOT, folder, 'api')
        if not os.path.isdir(api_dir):
            continue
        count = 0
        for jf in sorted(os.listdir(api_dir)):
            if not jf.endswith('.json') or jf == 'manifest.json':
                continue
            filepath = os.path.join(api_dir, jf)
            if process_spec(filepath, folder):
                count += 1
        if count > 0:
            print('  %s: added externalDocs to %d specs' % (folder, count))
            total += count

    print('\nTotal: added externalDocs to %d specs' % total)


if __name__ == '__main__':
    main()
