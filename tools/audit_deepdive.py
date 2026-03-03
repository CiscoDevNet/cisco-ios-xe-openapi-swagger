#!/usr/bin/env python3
"""Deep dive audit of missing YANG module swagger specs"""

import re
from pathlib import Path

base = Path(__file__).parent.parent
yang_dir = base / 'references' / '17181-YANG-modules'

# Check RPC files with no top-level rpc statements
print('='*80)
print('DEEP DIVE: RPC files with no top-level rpc statements')
print('='*80)

rpc_check = ['Cisco-IOS-XE-aaa-rpc', 'Cisco-IOS-XE-arp-rpc', 'Cisco-IOS-XE-bgp-rpc',
             'Cisco-IOS-XE-crypto-rpc', 'Cisco-IOS-XE-dhcp-rpc', 'Cisco-IOS-XE-flow-rpc',
             'Cisco-IOS-XE-multicast-rpc', 'Cisco-IOS-XE-ospf-rpc', 'Cisco-IOS-XE-platform-rpc',
             'Cisco-IOS-XE-umbrella-rpc', 'Cisco-IOS-XE-zone-rpc', 'Cisco-IOS-XE-factory-reset-secure-rpc',
             'Cisco-IOS-XE-cable-diag-rpc']

for mod in rpc_check:
    yang_file = yang_dir / f'{mod}.yang'
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    
    is_submodule = bool(re.search(r'^\s*submodule\s+', content, re.MULTILINE))
    groupings = re.findall(r'^\s*grouping\s+(\S+)', content, re.MULTILINE)
    belongs = re.search(r'belongs-to\s+(\S+)', content)
    augments = re.findall(r'^\s*augment\s', content, re.MULTILINE)
    
    module_type = 'submodule' if is_submodule else 'module'
    belongs_to = belongs.group(1) if belongs else 'N/A'
    
    print(f'\n  {mod}:')
    print(f'    Type: {module_type}')
    if is_submodule:
        print(f'    Belongs-to: {belongs_to}')
    print(f'    Groupings: {groupings[:5]}')
    print(f'    Augments: {len(augments)}')
    print(f'    File size: {len(content)} chars')

# Events-oper overlap check
print()
print('='*80)
print('EVENTS-OPER modules: checking if covered')
print('='*80)

events_api = base / 'swagger-events-model' / 'api'
events_specs = set(f.stem for f in events_api.glob('*.json') if f.stem != 'manifest')

oper_api = base / 'swagger-oper-model' / 'api'

oper_events = ['Cisco-IOS-XE-im-events-oper', 'Cisco-IOS-XE-ios-events-oper', 
               'Cisco-IOS-XE-platform-events-oper', 'Cisco-IOS-XE-sm-events-oper',
               'Cisco-IOS-XE-stack-mgr-events-oper', 'Cisco-IOS-XE-wireless-events-oper']

for mod in oper_events:
    in_events = mod in events_specs
    in_oper = (oper_api / f'{mod}.json').exists()
    yang_file = yang_dir / f'{mod}.yang'
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    containers = re.findall(r'^\s*container\s+(\S+)', content, re.MULTILINE)
    notifications = re.findall(r'^\s*notification\s+(\S+)', content, re.MULTILINE)
    print(f'  {mod}:')
    print(f'    In events dir: {in_events}')
    print(f'    In oper dir:   {in_oper}')
    print(f'    Containers: {containers[:3]}')
    print(f'    Notifications: {notifications[:3]}')

# bgp-route-oper detail
print()
print('='*80)
print('DEEP DIVE: Cisco-IOS-XE-bgp-route-oper')
print('='*80)
content = (yang_dir / 'Cisco-IOS-XE-bgp-route-oper.yang').read_text(encoding='utf-8', errors='ignore')
containers = re.findall(r'^\s*container\s+(\S+)', content, re.MULTILINE)
is_submodule = bool(re.search(r'^\s*submodule\s+', content, re.MULTILINE))
belongs = re.search(r'belongs-to\s+(\S+)', content)
print(f'  Is submodule: {is_submodule}')
if belongs:
    print(f'  Belongs-to: {belongs.group(1)}')
print(f'  Containers: {containers}')

# Standalone modules
print()
print('='*80)
print('Standalone Cisco-IOS-XE modules not in any generator:')
print('='*80)

for mod in ['Cisco-IOS-XE-qfp-stats', 'Cisco-IOS-XE-sisf']:
    yang_file = yang_dir / f'{mod}.yang'
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    is_submodule = bool(re.search(r'^\s*submodule\s+', content, re.MULTILINE))
    belongs = re.search(r'belongs-to\s+(\S+)', content)
    containers = re.findall(r'^\s*container\s+(\S+)', content, re.MULTILINE)
    augments = re.findall(r'^\s*augment\s', content, re.MULTILINE)
    print(f'  {mod}:')
    print(f'    Is submodule: {is_submodule}')
    if belongs:
        print(f'    Belongs-to: {belongs.group(1)}')
    print(f'    Containers: {containers[:5]}')
    print(f'    Augment stmts: {len(augments)}')
    has_oper_spec = (oper_api / f'{mod}.json').exists()
    print(f'    Has oper spec: {has_oper_spec}')

# Check how Cisco-IOS-XE-rpc.yang was handled
print()
print('='*80)
print('Cisco-IOS-XE-rpc.yang verification')
print('='*80)
rpc_file = yang_dir / 'Cisco-IOS-XE-rpc.yang'
content = rpc_file.read_text(encoding='utf-8', errors='ignore')
rpcs = re.findall(r'^\s*rpc\s+(\S+)', content, re.MULTILINE)
print(f'  Has RPCs: {len(rpcs) > 0} ({len(rpcs)} RPCs)')
print(f'  RPCs: {rpcs[:10]}')
rpc_spec_exists = (base / 'swagger-rpc-model' / 'api' / 'Cisco-IOS-XE-rpc.json').exists()
print(f'  Spec exists: {rpc_spec_exists}')

# Check the RPC submodule structure
print()
print('='*80)
print('RPC SUBMODULE ANALYSIS: Which -rpc.yang are submodules of Cisco-IOS-XE-rpc?')
print('='*80)
rpc_main = yang_dir / 'Cisco-IOS-XE-rpc.yang'
rpc_content = rpc_main.read_text(encoding='utf-8', errors='ignore')
rpc_includes = re.findall(r'include\s+(\S+);', rpc_content)
print(f'  Cisco-IOS-XE-rpc includes: {rpc_includes}')

# Check each -rpc.yang file for belongs-to
all_rpc_files = sorted(yang_dir.glob('*-rpc.yang'))
submodule_of_rpc = []
standalone_rpc = []
for f in all_rpc_files:
    c = f.read_text(encoding='utf-8', errors='ignore')
    is_sub = bool(re.search(r'^\s*submodule\s+', c, re.MULTILINE))
    bt = re.search(r'belongs-to\s+(\S+)', c)
    if is_sub and bt:
        submodule_of_rpc.append((f.stem, bt.group(1)))
    else:
        standalone_rpc.append(f.stem)

print(f'\n  Submodule -rpc files ({len(submodule_of_rpc)}):')
for name, parent in submodule_of_rpc:
    print(f'    {name} -> belongs-to {parent}')

print(f'\n  Standalone -rpc modules ({len(standalone_rpc)}):')
for name in standalone_rpc:
    print(f'    {name}')
