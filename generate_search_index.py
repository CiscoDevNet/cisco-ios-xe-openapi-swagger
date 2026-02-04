#!/usr/bin/env python3
"""
Generate comprehensive search index for universal search functionality.
Includes all YANG modules from all 9 API categories plus YANG trees and MIB trees.
"""

import json
import os
from pathlib import Path

# Define API categories with metadata
CATEGORIES = {
    'swagger-oper-model': {
        'type': 'operational',
        'display_name': 'Operational Data',
        'emoji': '🔵',
        'color': 'blue',
        'description': 'Real-time device state and statistics'
    },
    'swagger-native-config-model': {
        'type': 'config',
        'display_name': 'Native Configuration',
        'emoji': '🟢',
        'color': 'green',
        'description': 'Cisco IOS-XE native configuration model'
    },
    'swagger-rpc-model': {
        'type': 'rpc',
        'display_name': 'RPC Operations',
        'emoji': '🟡',
        'color': 'yellow',
        'description': 'Remote procedure calls and device actions'
    },
    'swagger-events-model': {
        'type': 'events',
        'display_name': 'Event Notifications',
        'emoji': '🔔',
        'color': 'orange',
        'description': 'Event notifications and telemetry streams'
    },
    'swagger-cfg-model': {
        'type': 'configuration',
        'display_name': 'Configuration (CFG)',
        'emoji': '⚙️',
        'color': 'cyan',
        'description': 'Device configuration management'
    },
    'swagger-ietf-model': {
        'type': 'ietf',
        'display_name': 'IETF Standards',
        'emoji': '🟠',
        'color': 'amber',
        'description': 'RFC-compliant IETF YANG models'
    },
    'swagger-openconfig-model': {
        'type': 'openconfig',
        'display_name': 'OpenConfig',
        'emoji': '🌍',
        'color': 'teal',
        'description': 'Vendor-neutral network configuration'
    },
    'swagger-mib-model': {
        'type': 'mib',
        'display_name': 'MIB Translations',
        'emoji': '🟣',
        'color': 'purple',
        'description': 'SNMP MIB to YANG translations'
    },
    'swagger-other-model': {
        'type': 'other',
        'display_name': 'Other Models',
        'emoji': '⚫',
        'color': 'gray',
        'description': 'Miscellaneous YANG modules'
    }
}

def extract_keywords(module_name):
    """Extract searchable keywords from module name."""
    # Remove common prefixes and suffixes
    keywords = module_name.replace('Cisco-IOS-XE-', '').replace('-oper', '').replace('-rpc', '').replace('-actions-rpc', '').replace('-events', '')
    # Split on hyphens and underscores
    parts = keywords.replace('_', '-').split('-')
    # Add the full module name and parts
    return [module_name.lower()] + [p.lower() for p in parts if len(p) > 2]

def process_manifest(category_path, category_info):
    """Process a manifest.json file and return module entries."""
    manifest_path = category_path / 'api' / 'manifest.json'
    
    if not manifest_path.exists():
        print(f"Warning: Manifest not found at {manifest_path}")
        return []
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    modules = manifest.get('modules', [])
    entries = []
    
    for module in modules:
        # Handle both string and object formats
        if isinstance(module, dict):
            module_name = module.get('name', module.get('file', '').replace('.json', ''))
        else:
            module_name = module
        
        if not module_name:
            continue
            
        # Build the entry
        entry = {
            'name': module_name,
            'type': category_info['type'],
            'category': category_path.name,
            'displayCategory': category_info['display_name'],
            'emoji': category_info['emoji'],
            'color': category_info['color'],
            'description': category_info['description'],
            'swaggerUrl': f"{category_path.name}/?url=api/{module_name}.json",
            'keywords': extract_keywords(module_name)
        }
        
        # Check if YANG tree exists
        yang_tree_path = Path('yang-trees') / f"{module_name}.html"
        if yang_tree_path.exists():
            entry['yangTreeUrl'] = f"yang-trees/{module_name}.html"
        
        entries.append(entry)
    
    return entries

def process_yang_trees():
    """Process YANG tree files that might not have Swagger specs."""
    yang_trees_path = Path('yang-trees')
    entries = []
    
    if not yang_trees_path.exists():
        print("Warning: yang-trees directory not found")
        return []
    
    # Process main YANG trees
    for html_file in yang_trees_path.glob('*.html'):
        if html_file.name in ['index.html', 'mib-trees-index.html']:
            continue
        
        module_name = html_file.stem
        
        # Skip if this was already included from a manifest
        # (we'll deduplicate later)
        entry = {
            'name': module_name,
            'type': 'yang-tree',
            'category': 'yang-trees',
            'displayCategory': 'YANG Tree',
            'emoji': '🌳',
            'color': 'green',
            'description': 'YANG module tree visualization',
            'yangTreeUrl': f"yang-trees/{html_file.name}",
            'keywords': extract_keywords(module_name)
        }
        entries.append(entry)
    
    # Process MIB trees
    mib_trees_path = yang_trees_path / 'mib-trees'
    if mib_trees_path.exists():
        for html_file in mib_trees_path.glob('*.html'):
            if html_file.name == 'index.html':
                continue
            
            module_name = html_file.stem
            entry = {
                'name': module_name,
                'type': 'mib-tree',
                'category': 'yang-trees',
                'displayCategory': 'MIB Tree',
                'emoji': '🟣',
                'color': 'purple',
                'description': 'MIB module tree visualization',
                'yangTreeUrl': f"yang-trees/mib-trees/{html_file.name}",
                'keywords': extract_keywords(module_name)
            }
            entries.append(entry)
    
    return entries

def main():
    """Generate the comprehensive search index."""
    print("Generating comprehensive search index...")
    
    all_entries = []
    stats = {
        'total_modules': 0,
        'by_category': {}
    }
    
    # Process all Swagger API categories
    for category_name, category_info in CATEGORIES.items():
        category_path = Path(category_name)
        if category_path.exists():
            print(f"Processing {category_name}...")
            entries = process_manifest(category_path, category_info)
            all_entries.extend(entries)
            stats['by_category'][category_name] = len(entries)
            print(f"  Found {len(entries)} modules")
        else:
            print(f"Warning: Category directory not found: {category_name}")
    
    # Process YANG trees
    print("Processing YANG trees...")
    yang_entries = process_yang_trees()
    
    # Deduplicate: prefer Swagger entries over tree-only entries
    swagger_modules = {entry['name'] for entry in all_entries}
    unique_yang_entries = [e for e in yang_entries if e['name'] not in swagger_modules]
    
    all_entries.extend(unique_yang_entries)
    stats['by_category']['yang-trees-only'] = len(unique_yang_entries)
    print(f"  Found {len(unique_yang_entries)} tree-only modules")
    
    # Calculate totals
    stats['total_modules'] = len(all_entries)
    
    # Create the search index
    search_index = {
        'version': '1.0',
        'generated': '2026-02-03',
        'stats': stats,
        'modules': all_entries
    }
    
    # Write to file
    output_path = Path('search-index.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(search_index, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Search index generated successfully!")
    print(f"📊 Statistics:")
    print(f"   Total modules: {stats['total_modules']}")
    for category, count in stats['by_category'].items():
        print(f"   {category}: {count}")
    print(f"\n📄 Saved to: {output_path}")
    print(f"📦 File size: {output_path.stat().st_size / 1024:.2f} KB")

if __name__ == '__main__':
    main()
