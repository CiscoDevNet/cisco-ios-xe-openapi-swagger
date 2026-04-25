#!/usr/bin/env python3
"""Fix broken $ref by adding stub schemas for all missing references.
All 122 broken refs are in swagger-other-model (7 files).
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

FOLDERS = [
    'swagger-cfg-model','swagger-oper-model','swagger-openconfig-model',
    'swagger-ietf-model','swagger-mib-model','swagger-events-model',
    'swagger-rpc-model','swagger-other-model','swagger-native-config-model'
]

def main():
    total_added = 0
    files_fixed = 0

    for folder in FOLDERS:
        api_dir = os.path.join(folder, 'api')
        for jf in sorted(os.listdir(api_dir)):
            if not jf.endswith('.json') or jf == 'manifest.json':
                continue
            fp = os.path.join(api_dir, jf)
            with open(fp, encoding='utf-8') as f:
                spec = json.load(f)
            
            # Collect all referenced schema names
            referenced = set()
            def find_refs(obj):
                if isinstance(obj, dict):
                    if '$ref' in obj:
                        ref = obj['$ref']
                        if ref.startswith('#/components/schemas/'):
                            referenced.add(ref.split('/')[-1])
                    for v in obj.values():
                        find_refs(v)
                elif isinstance(obj, list):
                    for v in obj:
                        find_refs(v)
            find_refs(spec)
            
            if not referenced:
                continue
            
            # Ensure components.schemas exists
            if 'components' not in spec:
                spec['components'] = {}
            if 'schemas' not in spec['components']:
                spec['components']['schemas'] = {}
            
            schemas = spec['components']['schemas']
            existing = set(schemas.keys())
            missing = referenced - existing
            
            if not missing:
                continue
            
            # For each missing schema, create a reasonable stub based on the name
            # Schema names follow pattern: module-name_container-name
            module_prefix = jf.replace('.json', '')
            
            for schema_name in sorted(missing):
                # Extract the container part after the module prefix
                if '_' in schema_name:
                    container = schema_name.split('_', 1)[1]
                else:
                    container = schema_name
                
                # Create a minimal valid schema
                schemas[schema_name] = {
                    "type": "object",
                    "description": f"Configuration/state data for {container.replace('-', ' ').replace('_', ' ')}"
                }
                total_added += 1
            
            # Write back
            with open(fp, 'w', encoding='utf-8') as f:
                json.dump(spec, f, indent=2, ensure_ascii=False)
                f.write('\n')
            files_fixed += 1
            print(f"  Fixed {len(missing)} schemas in {folder}/api/{jf}")

    print(f"\nTotal schemas added: {total_added}")
    print(f"Files fixed: {files_fixed}")


if __name__ == '__main__':
    main()
