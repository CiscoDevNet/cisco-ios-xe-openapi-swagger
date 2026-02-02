#!/usr/bin/env python3
"""
Add YANG tree visualization links to MIB swagger specifications.
Links point to pyang tree HTML files in yang-trees directory.
"""

import json
from pathlib import Path

def add_tree_link_to_mib_spec(spec_file: Path, tree_base_url: str) -> bool:
    """Add tree visualization link to a MIB swagger spec"""
    try:
        # Read the spec
        with open(spec_file, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        
        # Extract module name from filename
        module_name = spec_file.stem
        
        # Check if tree link already exists
        if 'description' in spec.get('info', {}) and '📊 YANG Tree:' in spec['info']['description']:
            return False
        
        # Construct tree link
        tree_url = f"{tree_base_url}/{module_name}.html"
        tree_link = f"\n\n**📊 YANG Tree:** [View {module_name} structure]({tree_url})"
        
        # Add tree link to description
        if 'info' in spec and 'description' in spec['info']:
            spec['info']['description'] += tree_link
        else:
            return False
        
        # Write updated spec
        with open(spec_file, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Error processing {spec_file.name}: {e}")
        return False


def main():
    """Main entry point"""
    script_dir = Path(__file__).parent
    swagger_dir = script_dir.parent / 'swagger-mib-model' / 'api'
    tree_base_url = "https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/yang-trees"
    
    print("Adding YANG tree links to MIB swagger specifications...\n")
    
    # Get all JSON specs (exclude manifests)
    spec_files = [f for f in swagger_dir.glob('*.json') 
                  if f.stem not in ['manifest', 'mib-manifest']]
    
    total_specs = len(spec_files)
    updated = 0
    skipped = 0
    
    for i, spec_file in enumerate(sorted(spec_files), 1):
        print(f"[{i}/{total_specs}] Processing {spec_file.stem}...")
        
        if add_tree_link_to_mib_spec(spec_file, tree_base_url):
            updated += 1
            print(f"  ✓ Added tree link")
        else:
            skipped += 1
            print(f"  - Already has tree link or no description")
    
    print(f"\n{'='*60}")
    print(f"✓ COMPLETE: Updated {updated} MIB specs with tree links")
    print(f"{'='*60}")
    print(f"  Updated:  {updated} specs")
    print(f"  Skipped:  {skipped} specs")
    print(f"  Total:    {total_specs} specs")


if __name__ == "__main__":
    main()
