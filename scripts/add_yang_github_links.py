#!/usr/bin/env python3
"""
Add GitHub YANG model links to all OpenAPI specifications
"""

import json
from pathlib import Path
import re

def get_github_yang_url(module_name: str) -> str:
    """Generate GitHub URL for YANG module"""
    # Base URL for IOS-XE 17.18.1 YANG models
    base_url = "https://github.com/YangModels/yang/blob/main/vendor/cisco/xe/17181"
    yang_file = f"{module_name}.yang"
    return f"{base_url}/{yang_file}"

def add_github_link_to_spec(spec_file: Path) -> bool:
    """Add GitHub link to a single OpenAPI spec"""
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        
        # Extract module name from title
        module_name = spec['info']['title']
        
        # Skip if already has GitHub link
        if 'github.com' in spec['info'].get('description', ''):
            print(f"  ⏭️  Skipping {module_name} (already has GitHub link)")
            return False
        
        # Get current description
        current_desc = spec['info'].get('description', '')
        
        # Generate GitHub URL
        github_url = get_github_yang_url(module_name)
        
        # Add GitHub link to description
        github_link = f"\n\n**YANG Model:** [{module_name}.yang]({github_url})"
        spec['info']['description'] = current_desc + github_link
        
        # Write back
        with open(spec_file, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2)
        
        print(f"  ✅ Added GitHub link to {module_name}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {spec_file.name}: {e}")
        return False

def process_model_folder(folder_path: Path, model_name: str):
    """Process all specs in a model folder"""
    api_dir = folder_path / 'api'
    if not api_dir.exists():
        print(f"⚠️  No api/ directory in {folder_path}")
        return 0
    
    print(f"\n{'='*70}")
    print(f"Processing {model_name}")
    print(f"{'='*70}")
    
    # Find all JSON files except manifest
    spec_files = [f for f in api_dir.glob('*.json') if f.name != 'manifest.json']
    
    if not spec_files:
        print(f"No spec files found in {api_dir}")
        return 0
    
    print(f"Found {len(spec_files)} specs\n")
    
    updated_count = 0
    for spec_file in sorted(spec_files):
        if add_github_link_to_spec(spec_file):
            updated_count += 1
    
    print(f"\nUpdated {updated_count}/{len(spec_files)} specs")
    return updated_count

def main():
    """Main entry point"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print("\n" + "="*70)
    print("Add GitHub YANG Model Links to OpenAPI Specs")
    print("="*70)
    
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
            total_updated += process_model_folder(folder_path, display_name)
        else:
            print(f"⚠️  Folder not found: {folder_path}")
    
    print(f"\n{'='*70}")
    print(f"COMPLETE: Updated {total_updated} total specs with GitHub links")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
