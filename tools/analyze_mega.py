#!/usr/bin/env python3
"""Analyze mega containers and interface type features for the container-based swagger strategy."""
import re, os, json

yang_dir = 'references/17181-YANG-modules'

# 1. Router augmenters
print("=" * 60)
print("ROUTER: augmenting modules")
print("=" * 60)
router_mods = []
for yf in sorted(os.listdir(yang_dir)):
    if not yf.endswith('.yang'):
        continue
    path = os.path.join(yang_dir, yf)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        txt = f.read()
    if 'ios:router' in txt:
        router_mods.append(yf.replace('.yang', ''))
print(f"Count: {len(router_mods)}")
for r in router_mods:
    print(f"  {r}")

# 2. Crypto augmenters
print("\n" + "=" * 60)
print("CRYPTO: augmenting modules")
print("=" * 60)
crypto_mods = []
for yf in sorted(os.listdir(yang_dir)):
    if not yf.endswith('.yang'):
        continue
    path = os.path.join(yang_dir, yf)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        txt = f.read()
    if 'ios:crypto' in txt:
        crypto_mods.append(yf.replace('.yang', ''))
print(f"Count: {len(crypto_mods)}")
for r in crypto_mods:
    print(f"  {r}")

# 3. Interface type feature comparison
print("\n" + "=" * 60)
print("INTERFACE: feature comparison across types")
print("=" * 60)

# Group interface types by category
intf_categories = {
    'Physical Ethernet': ['GigabitEthernet', 'TenGigabitEthernet', 'TwentyFiveGigE', 
                          'FortyGigabitEthernet', 'HundredGigE', 'TwoHundredGigE', 'FourHundredGigE',
                          'FiveGigabitEthernet', 'TwoGigabitEthernet', 'AppGigabitEthernet',
                          'FiftyGigabitEthernet', 'FastEthernet', 'Ethernet'],
    'Virtual/Logical': ['Loopback', 'Tunnel', 'Virtual-Template', 'VirtualPortGroup', 
                        'Virtual-PPP', 'nve', 'overlay', 'Vif'],
    'VLAN/L2': ['Vlan', 'BDI', 'BD-VIF', 'Port-channel'],
    'WAN/Legacy': ['Serial', 'Dialer', 'ATM', 'Multilink', 'Cellular', 'MFR'],
    'Service/Special': ['Embedded-Service-Engine', 'Service-Engine', 'ucse', 
                        'pseudowire', 'SM', 'GMPLS', 'Bundle'],
    'IoT': ['LORAWAN', 'WPAN', 'Virtual-WPAN'],
    'LISP/Overlay': ['LISP', 'L2LISP', 'vasileft', 'vasiright']
}

type_mod_count = {}
for yf in sorted(os.listdir(yang_dir)):
    if not yf.endswith('.yang'):
        continue
    path = os.path.join(yang_dir, yf)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        txt = f.read()
    for cat, types in intf_categories.items():
        for t in types:
            if f'ios:{t}' in txt:
                type_mod_count.setdefault(t, set()).add(yf.replace('.yang', ''))

print("\nInterface types by augmenting module count:")
for cat, types in intf_categories.items():
    print(f"\n  {cat}:")
    for t in types:
        count = len(type_mod_count.get(t, set()))
        bar = '#' * (count // 2)
        print(f"    {t:<30} {count:>3} modules  {bar}")

# Show that physical ethernets are nearly identical
print("\n" + "=" * 60)
print("PHYSICAL ETHERNET: shared vs unique modules")
print("=" * 60)
eth_types = ['GigabitEthernet', 'TenGigabitEthernet', 'FiveGigabitEthernet', 
             'TwentyFiveGigE', 'HundredGigE']
if all(t in type_mod_count for t in eth_types):
    common = type_mod_count[eth_types[0]].copy()
    for t in eth_types[1:]:
        common &= type_mod_count[t]
    print(f"\nCommon to all physical Ethernet types: {len(common)} modules")
    
    for t in eth_types:
        unique = type_mod_count[t] - common
        if unique:
            print(f"  {t} unique: {sorted(unique)}")
        else:
            print(f"  {t} unique: (none - identical to common set)")
