import json
from collections import defaultdict

with open('scripts/audit_results.json') as f:
    data = json.load(f)

buckets = defaultdict(lambda: {'critical':0,'high':0,'medium':0,'low':0,'good':0,'total':0})
for r in data['results']:
    s = r['gap_score'] or 0
    folder = r['folder']
    buckets[folder]['total'] += 1
    if s >= 70: buckets[folder]['critical'] += 1
    elif s >= 50: buckets[folder]['high'] += 1
    elif s >= 30: buckets[folder]['medium'] += 1
    elif s >= 10: buckets[folder]['low'] += 1
    else: buckets[folder]['good'] += 1

header = f"{'Folder':<35} {'CRIT':>5} {'HIGH':>5} {'MED':>5} {'LOW':>5} {'GOOD':>5} {'TOTAL':>6}"
print(header)
print('-' * 72)
for folder in sorted(buckets.keys()):
    b = buckets[folder]
    print(f"{folder:<35} {b['critical']:>5} {b['high']:>5} {b['medium']:>5} {b['low']:>5} {b['good']:>5} {b['total']:>6}")

# Top 10 CRITICAL per category  
print("\n=== CRITICAL BREAKDOWN BY CATEGORY ===")
for folder in sorted(buckets.keys()):
    crits = [r for r in data['results'] if r['folder'] == folder and (r['gap_score'] or 0) >= 70]
    if crits:
        print(f"\n{folder}: {len(crits)} critical")
        for r in crits[:5]:
            print(f"  {r['name']}: score={r['gap_score']}, paths={r['spec_paths']}/{r['tree_addressable']}, props={r['spec_schema_props']}/{r['tree_leaves']}")
        if len(crits) > 5:
            print(f"  ... and {len(crits)-5} more")

# No-tree  
print(f"\nNo-tree specs: {len(data['no_tree'])}")
nt = defaultdict(int)
for r in data['no_tree']:
    nt[r['folder']] += 1
for f, c in sorted(nt.items()):
    print(f"  {f}: {c}")

# Focus on non-MIB criticals
print("\n=== NON-MIB CRITICAL SPECS (focus area) ===")
non_mib = [r for r in data['results'] if r['folder'] != 'swagger-mib-model' and (r['gap_score'] or 0) >= 70]
print(f"Count: {len(non_mib)}")
for r in sorted(non_mib, key=lambda x: -x['gap_score']):
    print(f"  {r['name']} ({r['folder']}): score={r['gap_score']}, paths={r['spec_paths']}/{r['tree_addressable']}, leaves={r['spec_schema_props']}/{r['tree_leaves']}")
