#!/usr/bin/env python3
"""Add readOnly: true to all schema properties in oper (operational state) specs.

Oper specs are GET-only (read-only state data). Adding readOnly: true to every
property signals to Postman/Bruno/code generators that these fields are not writable.
Skips the restconf-error schema (shared utility, not YANG state data).
"""
import json
import glob
import os

os.chdir(os.path.join(os.path.dirname(__file__), '..'))

SKIP_SCHEMAS = {'restconf-error'}


def add_readonly_to_properties(obj):
    """Recursively add readOnly: true to all properties in a schema object."""
    count = 0
    if not isinstance(obj, dict):
        return count

    # If this object has "properties", mark each property readOnly
    props = obj.get('properties')
    if isinstance(props, dict):
        for prop_name, prop_val in props.items():
            if isinstance(prop_val, dict):
                if 'readOnly' not in prop_val:
                    prop_val['readOnly'] = True
                    count += 1
                # Recurse into nested objects
                count += add_readonly_to_properties(prop_val)

    # Handle array items
    items = obj.get('items')
    if isinstance(items, dict):
        count += add_readonly_to_properties(items)

    # Handle allOf, oneOf, anyOf
    for keyword in ('allOf', 'oneOf', 'anyOf'):
        combo = obj.get(keyword)
        if isinstance(combo, list):
            for sub in combo:
                count += add_readonly_to_properties(sub)

    return count


def process_spec(filepath):
    """Add readOnly: true to all schema properties in an oper spec."""
    with open(filepath, encoding='utf-8') as f:
        spec = json.load(f)

    schemas = spec.get('components', {}).get('schemas', {})
    total_props = 0

    for name, schema in schemas.items():
        if name in SKIP_SCHEMAS:
            continue
        total_props += add_readonly_to_properties(schema)

    if total_props > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
            f.write('\n')

    return total_props


def main():
    oper_specs = sorted(glob.glob('swagger-oper-model/api/*.json'))
    oper_specs = [f for f in oper_specs if 'manifest' not in os.path.basename(f)]

    total_specs = 0
    total_props = 0
    modified_specs = 0

    for filepath in oper_specs:
        try:
            props_added = process_spec(filepath)
            total_specs += 1
            total_props += props_added
            if props_added > 0:
                modified_specs += 1
        except Exception as e:
            print(f"  ERROR: {filepath}: {e}")

    print(f"Oper specs processed: {total_specs}")
    print(f"Specs modified:       {modified_specs}")
    print(f"Properties marked:    {total_props}")

    # Also mark MIB specs (all GET-only, read-only state data)
    mib_specs = sorted(glob.glob('swagger-mib-model/api/*.json'))
    mib_specs = [f for f in mib_specs if 'manifest' not in os.path.basename(f)]

    mib_total = 0
    mib_props = 0
    mib_modified = 0

    for filepath in mib_specs:
        try:
            props_added = process_spec(filepath)
            mib_total += 1
            mib_props += props_added
            if props_added > 0:
                mib_modified += 1
        except Exception as e:
            print(f"  ERROR: {filepath}: {e}")

    print(f"\nMIB specs processed:  {mib_total}")
    print(f"Specs modified:       {mib_modified}")
    print(f"Properties marked:    {mib_props}")

    print(f"\n{'='*50}")
    print(f"TOTAL specs modified: {modified_specs + mib_modified}")
    print(f"TOTAL readOnly props: {total_props + mib_props}")


if __name__ == '__main__':
    main()
