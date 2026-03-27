#!/usr/bin/env python3
"""Compare interface type features across all interface types in the YANG tree."""
import re

with open('yang-trees/Cisco-IOS-XE-native.html', 'r', encoding='utf-8') as f:
    content = f.read()

pre_matches = re.findall(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
tree_text = pre_matches[1]
tree_text = re.sub(r'<[^>]+>', '', tree_text)
tree_text = tree_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
lines = tree_text.split('\n')

def get_indent_len(line):
    """Count leading indent characters (spaces and pipes)."""
    n = 0
    for c in line:
        if c in ' |':
            n += 1
        else:
            break
    return n

def get_direct_children(lines, start_line):
    """Get direct child feature names of a list/container node."""
    parent_indent = get_indent_len(lines[start_line])
    features = []
    for j in range(start_line + 1, min(len(lines), start_line + 100000)):
        line = lines[j]
        if not line.strip():
            continue
        line_indent = get_indent_len(line)
        if line_indent == parent_indent + 3:
            m = re.search(r'[+o]--(rw|ro)\s+(\S+)', line)
            if m:
                features.append(m.group(2).rstrip('?').rstrip('!'))
        elif line_indent > parent_indent + 3:
            continue
        else:
            break
    return features


# Find all interface types - the 'interface' container is at line ~2885
# Its direct children are interface type lists at indent level 8 (5+3)
intf_line = None
for i, line in enumerate(lines):
    if re.match(r'^     \+--rw interface$', line):
        intf_line = i
        break

intf_indent = 5  # indent of 'interface'
intf_features = {}
intf_type_lines = []

for j in range(intf_line + 1, len(lines)):
    line = lines[j]
    if not line.strip():
        continue
    indent = get_indent_len(line)
    if indent == intf_indent + 3:  # direct child of interface
        m = re.search(r'[+o]--(rw|ro)\s+(\S+)', line)
        if m:
            name = m.group(2).rstrip('*')
            intf_type_lines.append((name, j))
    elif indent > intf_indent + 3:
        continue
    elif indent <= intf_indent and line.strip():
        break

for name, line_num in intf_type_lines:
    features = get_direct_children(lines, line_num)
    intf_features[name] = set(features)

# Print comparison
print(f'Interface types found: {len(intf_features)}')
print()

# Sort by feature count
print("=== INTERFACE TYPES BY FEATURE COUNT ===")
for name, features in sorted(intf_features.items(), key=lambda x: -len(x[1])):
    print(f'  {name:<30} {len(features):>4} features')

# Find common features (present in ALL physical ethernet types)
physical_types = ['GigabitEthernet', 'TenGigabitEthernet', 'FiveGigabitEthernet',
                  'TwentyFiveGigE', 'HundredGigE', 'FortyGigabitEthernet']
physical_present = [t for t in physical_types if t in intf_features]

if len(physical_present) >= 2:
    common_physical = intf_features[physical_present[0]].copy()
    for t in physical_present[1:]:
        common_physical &= intf_features[t]
    
    print(f'\n=== COMMON FEATURES ACROSS PHYSICAL ETHERNET ({len(common_physical)}) ===')
    for f in sorted(common_physical):
        print(f'  {f}')
    
    print(f'\n=== UNIQUE FEATURES PER PHYSICAL TYPE ===')
    for t in physical_present:
        unique = intf_features[t] - common_physical
        if unique:
            print(f'  {t}: +{sorted(unique)}')
        else:
            print(f'  {t}: (identical to common set)')

# Now compare ALL interface types against a universal common set
print(f'\n=== FEATURE INTERSECTION ANALYSIS ===')
all_types = list(intf_features.keys())
if len(all_types) >= 2:
    universal_common = intf_features[all_types[0]].copy()
    for t in all_types[1:]:
        universal_common &= intf_features[t]
    
    print(f'Features common to ALL {len(all_types)} interface types: {len(universal_common)}')
    for f in sorted(universal_common):
        print(f'  {f}')

# Group interface types by feature similarity
print(f'\n=== FEATURE SIMILARITY GROUPS ===')
# Use Jaccard similarity
groups = {}
assigned = set()
for t1 in sorted(intf_features.keys()):
    if t1 in assigned:
        continue
    group = [t1]
    assigned.add(t1)
    for t2 in sorted(intf_features.keys()):
        if t2 in assigned:
            continue
        f1 = intf_features[t1]
        f2 = intf_features[t2]
        if len(f1) == 0 or len(f2) == 0:
            continue
        jaccard = len(f1 & f2) / len(f1 | f2)
        if jaccard > 0.85:  # >85% similar
            group.append(t2)
            assigned.add(t2)
    groups[t1] = group

for leader, members in groups.items():
    if len(members) > 1:
        print(f'  Similar group ({len(intf_features[leader])} features): {", ".join(members)}')
    else:
        print(f'  Standalone ({len(intf_features[leader])} features): {leader}')
