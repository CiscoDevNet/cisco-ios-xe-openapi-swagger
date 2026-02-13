#!/usr/bin/env python3
"""Fix duplicate path keys in openconfig-network-instance.json.

The file has 3 pairs of paths that collide due to case-only differences:
  subtlvs (from router-capabilities) vs subTLVs (from extended-is-reachability)

Fix: Rename lowercase 'subtlvs' paths to 'router-capability-subtlvs' to disambiguate.
"""
import re
import os

os.chdir(os.path.join(os.path.dirname(__file__), '..'))

filepath = 'swagger-openconfig-model/api/openconfig-network-instance.json'

with open(filepath, encoding='utf-8') as f:
    content = f.read()

# Find all path keys with subtlvs or subTLVs
path_re = re.compile(r'^\s+"(/data/[^"]*(?:subtlvs|subTLVs)[^"]*)"', re.MULTILINE)
matches = path_re.findall(content)
print("Found paths with subtlvs/subTLVs:")
for m in matches:
    print(f"  {m}")

# Strategy: Rename the lowercase 'subtlvs' variants to include parent context
# These are the router-capability subtlvs
# The camelCase 'subTLVs' (extended-is-reachability) keep their original name

replacements = [
    # Path key replacements (in path dictionary)
    ('protocol={identifier},{name}/subtlvs"', 'protocol={identifier},{name}/router-capability-subtlvs"'),
    ('protocol={identifier},{name}/subtlvs={subtlv-type}"', 'protocol={identifier},{name}/router-capability-subtlvs={subtlv-type}"'),
    ('protocol/subtlvs"', 'protocol/router-capability-subtlvs"'),
    # operationId replacements
    ('"get-subtlvs-2202"', '"get-router-capability-subtlvs-2202"'),
    ('"put-subtlvs-2202"', '"put-router-capability-subtlvs-2202"'),
    ('"patch-subtlvs-2202"', '"patch-router-capability-subtlvs-2202"'),
    ('"delete-subtlvs-2202"', '"delete-router-capability-subtlvs-2202"'),
    ('"get-subtlvs-item-2203"', '"get-router-capability-subtlvs-item-2203"'),
    ('"put-subtlvs-item-2203"', '"put-router-capability-subtlvs-item-2203"'),
    ('"patch-subtlvs-item-2203"', '"patch-router-capability-subtlvs-item-2203"'),
    ('"delete-subtlvs-item-2203"', '"delete-router-capability-subtlvs-item-2203"'),
    ('"get-subtlvs-2204"', '"get-router-capability-subtlvs-2204"'),
    ('"post-subtlvs-2204"', '"post-router-capability-subtlvs-2204"'),
    # Summary/description text
    ('"Get subtlvs"', '"Get router-capability subtlvs"'),
    ('"Create or replace subtlvs"', '"Create or replace router-capability subtlvs"'),
    ('"Modify subtlvs"', '"Modify router-capability subtlvs"'),
    ('"Delete subtlvs"', '"Delete router-capability subtlvs"'),
    ('"Get subtlvs-item"', '"Get router-capability subtlvs-item"'),
    ('"Create or replace subtlvs-item"', '"Create or replace router-capability subtlvs-item"'),
    ('"Modify subtlvs-item"', '"Modify router-capability subtlvs-item"'),
    ('"Delete subtlvs-item"', '"Delete router-capability subtlvs-item"'),
    ('"Get subtlvs list"', '"Get router-capability subtlvs list"'),
    ('"Create subtlvs"', '"Create router-capability subtlvs"'),
    # Partial modify descriptions (with capital S)
    ('"Partially modify Subtlvs"', '"Partially modify router-capability Subtlvs"'),
]

count = 0
for old, new in replacements:
    if old in content:
        n = content.count(old)
        content = content.replace(old, new)
        print(f"  Replaced {n}x: {old} -> {new}")
        count += n

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal replacements: {count}")

# Verify: check for remaining duplicates
path_re2 = re.compile(r'^\s+"(/data/[^"]*(?:subtlvs|subTLVs|router-capability-subtlvs)[^"]*)"', re.MULTILINE)
final_matches = path_re2.findall(content)
print(f"\nFinal paths with subtlvs/subTLVs:")
seen = set()
dupes = False
for m in final_matches:
    if m in seen:
        print(f"  DUPLICATE: {m}")
        dupes = True
    else:
        print(f"  OK: {m}")
        seen.add(m)

if not dupes:
    print("\n✅ No more duplicate path keys!")
else:
    print("\n❌ Duplicates still exist!")
