"""Audit generic/placeholder values in event notification examples."""
import json, os
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
api_dir = os.path.join(BASE, 'swagger-events-model', 'api')

generic_counter = Counter()
leaf_generics = Counter()  # leaf_name -> count of generic values

GENERIC_STRINGS = {
    'example-string', 'example-value', 'value', 'value-1', 'example-name',
    'bit0', 'configuration-change',
}

def scan_examples(obj, leaf_name=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            scan_examples(v, k)
    elif isinstance(obj, list):
        for v in obj:
            scan_examples(v, leaf_name)
    elif isinstance(obj, str):
        if obj in GENERIC_STRINGS:
            generic_counter[obj] += 1
            leaf_generics[leaf_name] += 1

files = sorted(f for f in os.listdir(api_dir) if f.endswith('.json') and f != 'manifest.json')

def main():

    for fn in files:
        with open(os.path.join(api_dir, fn), encoding='utf-8') as fh:
            spec = json.load(fh)
        schemas = spec.get('components', {}).get('schemas', {})
        for name, sch in schemas.items():
            ex = sch.get('example', {})
            scan_examples(ex)

    print('Generic/placeholder VALUES in examples:')
    for val, count in generic_counter.most_common(20):
        print(f'  "{val}" => {count} occurrences')
    print(f'\nTotal generic values: {sum(generic_counter.values())}')

    print(f'\nTop LEAF NAMES with generic values:')
    for leaf, count in leaf_generics.most_common(30):
        print(f'  {leaf} => {count}')

if __name__ == '__main__':
    main()
