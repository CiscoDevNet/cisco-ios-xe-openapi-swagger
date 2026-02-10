"""Quick check of event spec schemas and examples."""
import json, os, glob

api_dir = os.path.join(os.path.dirname(__file__), '..', 'swagger-events-model', 'api')
os.chdir(api_dir)

files = [f for f in sorted(glob.glob('*.json')) if f != 'manifest.json']
no_schemas = 0
with_schemas = 0
with_examples = 0
total_paths = 0
sample_no_schema = []
sample_with_schema = []

for fn in files:
    with open(fn, encoding='utf-8') as fh:
        spec = json.load(fh)
    pc = len(spec.get('paths', {}))
    total_paths += pc
    schemas = spec.get('components', {}).get('schemas', {})
    if not schemas:
        no_schemas += 1
        if len(sample_no_schema) < 5:
            sample_no_schema.append(fn)
    else:
        with_schemas += 1
        has_ex = False
        for s in schemas.values():
            if s.get('example'):
                has_ex = True
                break
        if has_ex:
            with_examples += 1
        if len(sample_with_schema) < 5:
            sample_with_schema.append((fn, len(schemas), has_ex))

print(f"Total event spec files: {len(files)}")
print(f"Total paths: {total_paths}")
print(f"With schemas: {with_schemas}")
print(f"Without schemas: {no_schemas}")
print(f"With examples in schemas: {with_examples}")
print()
print("Sample specs WITHOUT schemas:")
for s in sample_no_schema:
    print(f"  {s}")
print()
print("Sample specs WITH schemas:")
for fn, sc, has_ex in sample_with_schema:
    print(f"  {fn}  schemas={sc}  has_examples={has_ex}")
