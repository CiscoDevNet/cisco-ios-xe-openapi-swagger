#!/usr/bin/env python3
"""
Add pyang tree links to all OpenAPI specifications
"""

import json
from pathlib import Path

def get_tree_link(module_name: str) -> str:
    """Generate link to pyang tree HTML file"""
    base_url = "https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/yang-trees"
    return f"{base_url}/{module_name}.html"

def tree_file_exists(module_name: str, trees_dir: Path) -> bool:
    """Check if tree HTML file exists for this module"""
    tree_file = trees_dir / f"{module_name}.html"
    return tree_file.exists()

def add_tree_link_to_spec(spec_file: Path, trees_dir: Path) -> bool:
    """Add pyang tree link to a single OpenAPI spec"""
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        
        # Extract module name from title or filename
        title = spec['info']['title']
        
        # Try to extract module name from filename first (most reliable)
        # Remove .json extension
        filename_base = spec_file.stem
        
        # Try multiple strategies to find the tree file
        possible_names = [
            filename_base,  # Exact filename match (e.g., Cisco-IOS-XE-aaa-events)
            title.split(' - ')[0].strip(),  # Title before first dash
            title,  # Full title
        ]
        
        # Find which tree file exists
        module_name = None
        for name in possible_names:
            if tree_file_exists(name, trees_dir):
                module_name = name
                break
        
        # Check if tree exists
        if not module_name:
            return False
        
        # Skip if already has tree link
        if 'yang-trees' in spec['info'].get('description', ''):
            print(f"  ⏭️  Skipping {module_name} (already has tree link)")
            return False
        
        # Get current description
        current_desc = spec['info'].get('description', '')
        
        # Generate tree link
        tree_url = get_tree_link(module_name)
        tree_link = f"\n\n**📊 YANG Tree:** [View {module_name} structure]({tree_url})"
        
        # Add tree link to description
        spec['info']['description'] = current_desc + tree_link
        
        # Write back
        with open(spec_file, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2)
        
        print(f"  ✅ Added tree link to {module_name}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {spec_file.name}: {e}")
        return False

def process_model_folder(folder_path: Path, model_name: str, trees_dir: Path):
    """Process all specs in a model folder"""
    api_dir = folder_path / 'api'
    if not api_dir.exists():
        print(f"⚠️  No api/ directory in {folder_path}")
        return 0
    
    print(f"\n{'='*70}")
    print(f"Processing {model_name}")
    print(f"{'='*70}")
    
    # Find all JSON files except manifest
    spec_files = [f for f in api_dir.glob('*.json') if f.name != 'manifest.json' and 'rpc-manifest' not in f.name]
    
    if not spec_files:
        print(f"No spec files found in {api_dir}")
        return 0
    
    print(f"Found {len(spec_files)} specs\n")
    
    updated_count = 0
    for spec_file in sorted(spec_files):
        if add_tree_link_to_spec(spec_file, trees_dir):
            updated_count += 1
    
    print(f"\nUpdated {updated_count}/{len(spec_files)} specs")
    return updated_count

def main():
    """Main entry point"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    trees_dir = project_root / 'yang-trees'
    
    if not trees_dir.exists():
        print(f"❌ Error: Trees directory not found: {trees_dir}")
        print("Run generate_pyang_trees.py first!")
        return
    
    print("\n" + "="*70)
    print("Add pyang Tree Links to OpenAPI Specs")
    print("="*70)
    
    # Count available trees
    tree_files = list(trees_dir.glob('*.html'))
    tree_files = [f for f in tree_files if f.name != 'index.html']
    print(f"\nFound {len(tree_files)} pyang tree files\n")
    
    # Model folders to process
    model_folders = [
        ('swagger-oper-model', 'Operational'),
        ('swagger-rpc-model', 'RPC'),
        ('swagger-events-model', 'Events'),
        ('swagger-native-config-model', 'Native Config'),
        ('swagger-cfg-model', 'Configuration'),
        ('swagger-ietf-model', 'IETF'),
        ('swagger-openconfig-model', 'OpenConfig'),
        ('swagger-mib-model', 'MIB'),
        ('swagger-other-model', 'Other')
    ]
    
    total_updated = 0
    for folder_name, display_name in model_folders:
        folder_path = project_root / folder_name
        if folder_path.exists():
            total_updated += process_model_folder(folder_path, display_name, trees_dir)
        else:
            print(f"⚠️  Folder not found: {folder_path}")
    
    print(f"\n{'='*70}")
    print(f"COMPLETE: Updated {total_updated} total specs with tree links")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
