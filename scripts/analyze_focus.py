import json
from collections import defaultdict


def main():
    with open('scripts/audit_results.json') as f:
        data = json.load(f)

    # Focus areas - exclude events/MIB (those are notification modules, different paradigm)
    focus_cats = [
        'swagger-oper-model', 'swagger-cfg-model', 'swagger-openconfig-model',
        'swagger-ietf-model', 'swagger-rpc-model', 'swagger-other-model'
    ]

    print('=== FOCUS: Interactive Swagger specs (oper/cfg/openconfig/ietf/rpc/other) ===')
    print('(Excluding events & MIB which are notification/trap modules)\n')

    total_missing_paths = 0
    total_missing_props = 0
    all_focus = []

    for sev_name, lo, hi in [('CRITICAL', 70, 999), ('HIGH', 50, 70), ('MEDIUM', 30, 50)]:
        items = [r for r in data['results']
                 if r['folder'] in focus_cats and lo <= (r['gap_score'] or 0) < hi]
        if items:
            print(f'\n{sev_name}: {len(items)} specs')
            print(f'  {"Module":<50s} {"Paths":>10} {"Missing":>8} {"Props":>10} {"Score":>6}')
            print(f'  {"-"*50} {"-"*10} {"-"*8} {"-"*10} {"-"*6}')
            for r in sorted(items, key=lambda x: -x['gap_score']):
                missing_p = max(0, r['tree_addressable'] - r['spec_paths'])
                missing_l = max(0, r['tree_leaves'] - r['spec_schema_props'])
                total_missing_paths += missing_p
                total_missing_props += missing_l
                all_focus.append(r)
                name = r['name'][:48]
                print(f'  {name:<50s} {r["spec_paths"]:>4}/{r["tree_addressable"]:<4}  {missing_p:>6}  '
                      f'{r["spec_schema_props"]:>4}/{r["tree_leaves"]:<4}  {r["gap_score"]:>5}')

    print(f'\n{"="*80}')
    print(f'TOTAL FOCUS SPECS (score>=30, non-events/mib): {len(all_focus)}')
    print(f'TOTAL MISSING PATHS to add: {total_missing_paths}')
    print(f'TOTAL MISSING SCHEMA PROPS to add: {total_missing_props}')
    print(f'{"="*80}')

    # Category breakdown of focus specs
    print('\nBy category:')
    cat_counts = defaultdict(lambda: {'count': 0, 'missing_paths': 0})
    for r in all_focus:
        mp = max(0, r['tree_addressable'] - r['spec_paths'])
        cat_counts[r['folder']]['count'] += 1
        cat_counts[r['folder']]['missing_paths'] += mp
    for cat in sorted(cat_counts.keys()):
        c = cat_counts[cat]
        print(f'  {cat}: {c["count"]} specs, {c["missing_paths"]} missing paths')

    # The big ones
    print('\nTop 10 largest gaps (by missing path count):')
    all_focus.sort(key=lambda x: -(x['tree_addressable'] - x['spec_paths']))
    for r in all_focus[:10]:
        mp = r['tree_addressable'] - r['spec_paths']
        print(f'  {r["name"]}: {mp} missing paths ({r["spec_paths"]}/{r["tree_addressable"]})')


if __name__ == '__main__':
    main()
