#!/usr/bin/env python3
"""Audit YANG module coverage across all swagger generators"""

import re
from pathlib import Path

yang_dir = Path(__file__).parent.parent / 'references' / '17181-YANG-modules'

# =========================================================================
# PART 1: Check if 'uncategorized' Cisco-IOS-XE-*.yang files are submodules
# =========================================================================

print('='*80)
print('PART 1: Classifying uncategorized Cisco-IOS-XE-*.yang files')
print('='*80)

# Read native module to find includes
native_file = yang_dir / 'Cisco-IOS-XE-native.yang'
native_content = native_file.read_text(encoding='utf-8', errors='ignore')
native_includes = set()
for m in re.finditer(r'include\s+(\S+);', native_content):
    native_includes.add(m.group(1))

print(f"\nNative module includes {len(native_includes)} submodules")

# Uncategorized Cisco-IOS-XE files
uncategorized_cisco = []
for f in sorted(yang_dir.glob('Cisco-IOS-XE-*.yang')):
    stem = f.stem
    if any(k in stem.lower() for k in ['-oper', '-cfg', '-rpc', '-actions', '-events', '-types', '-common', '-deviation', '-obsolete']):
        continue
    if stem == 'Cisco-IOS-XE-native':
        continue
    uncategorized_cisco.append(stem)

submodules = []
augmenters = []
standalone = []

for mod in uncategorized_cisco:
    yang_file = yang_dir / f'{mod}.yang'
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    
    is_submodule = bool(re.search(r'^\s*submodule\s+', content, re.MULTILINE))
    augments_native = 'augment' in content and '/ios:' in content
    has_container = bool(re.search(r'^\s*container\s+', content, re.MULTILINE))
    has_rpc = bool(re.search(r'^\s*rpc\s+', content, re.MULTILINE))
    
    if is_submodule or mod in native_includes:
        submodules.append(mod)
    elif augments_native:
        augmenters.append(mod)
    else:
        standalone.append(mod)

print(f'\nSubmodules of native ({len(submodules)}): Covered by native generator')
for s in submodules[:10]:
    print(f'  - {s}')
if len(submodules) > 10:
    print(f'  ... and {len(submodules) - 10} more')

print(f'\nAugment /native ({len(augmenters)}): Loaded by native generator via augmentation')
for a in augmenters[:10]:
    print(f'  - {a}')
if len(augmenters) > 10:
    print(f'  ... and {len(augmenters) - 10} more')

print(f'\nStandalone modules ({len(standalone)}): May need separate specs')
for s in standalone:
    yang_file = yang_dir / f'{s}.yang'
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    has_container = bool(re.search(r'^\s*container\s+', content, re.MULTILINE))
    has_rpc = bool(re.search(r'^\s*rpc\s+', content, re.MULTILINE))
    has_notification = bool(re.search(r'^\s*notification\s+', content, re.MULTILINE))
    print(f'  - {s} (container={has_container}, rpc={has_rpc}, notification={has_notification})')

# =========================================================================
# PART 2: Verify RPC files - which ones matched the filter but have no spec?
# =========================================================================

print()
print('='*80)
print('PART 2: RPC files that SHOULD have specs but are MISSING')
print('='*80)

rpc_keywords = ['rpc', 'cmd', 'actions']
rpc_additional = ['cisco-smart-license', 'cisco-bridge-domain', 'cisco-ia']
all_yang = sorted([f.stem for f in yang_dir.glob('*.yang')])
rpc_matched = [f for f in all_yang if any(kw in f.lower() for kw in rpc_keywords)]
rpc_matched += [f for f in rpc_additional if f in all_yang and f not in rpc_matched]
rpc_matched = sorted(set(rpc_matched))

rpc_api_dir = Path(__file__).parent.parent / 'swagger-rpc-model' / 'api'
rpc_specs = set(f.stem for f in rpc_api_dir.glob('*.json') if f.stem != 'manifest')

rpc_missing = sorted(set(rpc_matched) - rpc_specs)

# Check each missing RPC file for actual RPC content
print(f'\nMissing RPC specs that matched keyword filter:')
for mod in rpc_missing:
    yang_file = yang_dir / f'{mod}.yang'
    if not yang_file.exists():
        print(f'  {mod}: FILE NOT FOUND')
        continue
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    rpcs = re.findall(r'^\s*rpc\s+(\S+)', content, re.MULTILINE)
    has_rpc = len(rpcs) > 0
    
    # Check if it's false positive (matched keyword but no RPCs)
    is_false_positive = not has_rpc
    
    if is_false_positive:
        print(f'  {mod}: FALSE POSITIVE - keyword match but no RPCs in file')
    else:
        print(f'  {mod}: GENUINE MISSING - has {len(rpcs)} RPCs: {rpcs[:5]}')

# =========================================================================
# PART 3: Check oper files that matched but are missing
# =========================================================================

print()
print('='*80)
print('PART 3: Oper files that matched filter but have no spec')
print('='*80)

oper_api_dir = Path(__file__).parent.parent / 'swagger-oper-model' / 'api'
oper_specs = set(f.stem for f in oper_api_dir.glob('*.json') if f.stem != 'manifest')

oper_matched = sorted([f.stem for f in yang_dir.glob('Cisco-IOS-XE-*-oper*.yang')
                        if '-oper' in f.stem.lower()])

oper_missing = sorted(set(oper_matched) - oper_specs)
print(f'\nMissing oper specs ({len(oper_missing)}):')
for mod in oper_missing:
    yang_file = yang_dir / f'{mod}.yang'
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    
    # Check if it's a types-only or common module
    has_container = bool(re.search(r'^\s*container\s+', content, re.MULTILINE))
    has_grouping = bool(re.search(r'^\s*grouping\s+', content, re.MULTILINE))
    is_submodule = bool(re.search(r'^\s*submodule\s+', content, re.MULTILINE))
    
    # Check if it defines data nodes vs just types/groupings
    containers = re.findall(r'^\s*container\s+(\S+)', content, re.MULTILINE)
    
    reason = ""
    if '-types' in mod:
        reason = "TYPES MODULE - no API paths"
    elif '-common' in mod and not has_container:
        reason = "COMMON MODULE (groupings only) - no API paths"
    elif '-events-oper' in mod:
        reason = "EVENTS-OPER module - may overlap with events generator"
    elif is_submodule:
        reason = "SUBMODULE - imported by parent"
    elif not has_container and has_grouping:
        reason = "GROUPINGS ONLY - no top-level containers"
    else:
        reason = f"GENUINE MISSING - has containers: {containers[:3]}"
    
    print(f'  {mod}: {reason}')

# =========================================================================
# PART 4: Check OpenConfig - many are sub-modules/types
# =========================================================================

print()
print('='*80)
print('PART 4: OpenConfig missing specs analysis')
print('='*80)

oc_api_dir = Path(__file__).parent.parent / 'swagger-openconfig-model' / 'api'
oc_specs = set(f.stem for f in oc_api_dir.glob('*.json') if f.stem != 'manifest')
oc_matched = sorted([f.stem for f in yang_dir.glob('openconfig-*.yang')])
oc_missing = sorted(set(oc_matched) - oc_specs)

oc_genuinely_missing = []
oc_types_or_sub = []

for mod in oc_missing:
    yang_file = yang_dir / f'{mod}.yang'
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    
    has_container = bool(re.search(r'^\s*container\s+', content, re.MULTILINE))
    is_submodule = bool(re.search(r'^\s*submodule\s+', content, re.MULTILINE))
    is_types = '-types' in mod or mod.endswith('-ext')
    has_grouping_only = bool(re.search(r'^\s*grouping\s+', content, re.MULTILINE)) and not has_container
    
    if is_types or has_grouping_only or is_submodule:
        oc_types_or_sub.append(mod)
    else:
        oc_genuinely_missing.append(mod)

print(f'\nOpenConfig types/grouping/sub-modules (no spec needed): {len(oc_types_or_sub)}')
for t in oc_types_or_sub[:10]:
    print(f'  - {t}')
if len(oc_types_or_sub) > 10:
    print(f'  ... and {len(oc_types_or_sub) - 10} more')

print(f'\nOpenConfig genuinely missing ({len(oc_genuinely_missing)}):')
for g in oc_genuinely_missing:
    yang_file = yang_dir / f'{g}.yang'
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    containers = re.findall(r'^\s*container\s+(\S+)', content, re.MULTILINE)
    print(f'  ✗ {g} (containers: {containers[:3]})')

# =========================================================================
# PART 5: IETF missing specs analysis
# =========================================================================

print()
print('='*80)
print('PART 5: IETF missing specs analysis')
print('='*80)

ietf_api_dir = Path(__file__).parent.parent / 'swagger-ietf-model' / 'api'
ietf_specs = set(f.stem for f in ietf_api_dir.glob('*.json') if f.stem != 'manifest')
ietf_matched = sorted([f.stem for f in yang_dir.glob('ietf-*.yang')])
ietf_missing = sorted(set(ietf_matched) - ietf_specs)

for mod in ietf_missing:
    yang_file = yang_dir / f'{mod}.yang'
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    
    has_container = bool(re.search(r'^\s*container\s+', content, re.MULTILINE))
    is_types = '-types' in mod
    has_grouping_only = bool(re.search(r'^\s*grouping\s+', content, re.MULTILINE)) and not has_container
    
    if is_types or has_grouping_only:
        label = "TYPES/GROUPINGS ONLY"
    elif has_container:
        label = "GENUINE MISSING - has containers"
    else:
        label = "NO DATA NODES"
    print(f'  {mod}: {label}')

# =========================================================================
# PART 6: Check cfg module that's missing
# =========================================================================

print()
print('='*80)
print('PART 6: Config missing spec')
print('='*80)

cfg_api_dir = Path(__file__).parent.parent / 'swagger-cfg-model' / 'api'
cfg_specs = set(f.stem for f in cfg_api_dir.glob('*.json') if f.stem != 'manifest')
cfg_matched = sorted([f.stem for f in yang_dir.glob('*-cfg.yang')])
cfg_missing = sorted(set(cfg_matched) - cfg_specs)

for mod in cfg_missing:
    yang_file = yang_dir / f'{mod}.yang'
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    containers = re.findall(r'^\s*container\s+(\S+)', content, re.MULTILINE)
    print(f'  {mod}: containers={containers[:5]}')

# =========================================================================
# FINAL SUMMARY
# =========================================================================

print()
print('='*80)
print('FINAL SUMMARY: Genuinely Missing Swagger Specs')
print('='*80)

print('\n1. RPC SPECS GENUINELY MISSING:')
for mod in rpc_missing:
    yang_file = yang_dir / f'{mod}.yang'
    if not yang_file.exists():
        continue
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    rpcs = re.findall(r'^\s*rpc\s+(\S+)', content, re.MULTILINE)
    if rpcs:
        print(f'   ✗ {mod} ({len(rpcs)} RPCs)')

print('\n2. OPER SPECS GENUINELY MISSING:')
for mod in oper_missing:
    yang_file = yang_dir / f'{mod}.yang'
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    has_container = bool(re.search(r'^\s*container\s+', content, re.MULTILINE))
    if has_container and '-types' not in mod:
        print(f'   ✗ {mod}')

print('\n3. CONFIG SPECS GENUINELY MISSING:')
for mod in cfg_missing:
    print(f'   ✗ {mod}')

print('\n4. OPENCONFIG SPECS GENUINELY MISSING:')
for g in oc_genuinely_missing:
    print(f'   ✗ {g}')

print('\n5. IETF SPECS GENUINELY MISSING:')
for mod in ietf_missing:
    yang_file = yang_dir / f'{mod}.yang'
    content = yang_file.read_text(encoding='utf-8', errors='ignore')
    has_container = bool(re.search(r'^\s*container\s+', content, re.MULTILINE))
    is_types = '-types' in mod
    if has_container and not is_types:
        print(f'   ✗ {mod}')

print('\n6. OTHER SPECS GENUINELY MISSING:')
other_list = ['cisco-ospf', 'cisco-policy', 'cisco-storm-control']
for mod in other_list:
    yang_file = yang_dir / f'{mod}.yang'
    if yang_file.exists():
        content = yang_file.read_text(encoding='utf-8', errors='ignore')
        has_container = bool(re.search(r'^\s*container\s+', content, re.MULTILINE))
        print(f'   ✗ {mod} (has containers: {has_container})')
