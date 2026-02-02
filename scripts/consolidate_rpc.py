#!/usr/bin/env python3
"""
Consolidate RPC Model into category-based files

Consolidates 54 individual RPC/actions files into logical operation category groupings.

Phase 6: RPC Model Enhancement
"""

import json
from pathlib import Path
from collections import defaultdict

# RPC category mappings based on module names and action types
CATEGORY_KEYWORDS = {
    'network-ops': [
        'ping', 'traceroute', 'arp', 'nd', 'diagnostic', 'livetools',
        'tunnel', 'vpn', 'bridge'
    ],
    'wireless-ops': [
        'wireless', 'wlan', 'ap-', 'mesh', 'rrm', 'ble', 'client',
        'rogue', 'radio'
    ],
    'system-ops': [
        'reload', 'shutdown', 'boot', 'install', 'upgrade', 'rescue',
        'checkpoint', 'verify', 'cli'
    ],
    'security-ops': [
        'crypto', 'certificate', 'pki', 'license', 'smart-license',
        'firewall', 'utd', 'sslproxy', 'ngfw'
    ],
    'config-ops': [
        'copy', 'write', 'save', 'rollback', 'commit', 'transaction',
        'validate', 'ia'
    ],
    'debug-ops': [
        'trace', 'debug', 'monitor', 'capture', 'tech-support',
        'troubleshoot', 'log'
    ],
    'platform-ops': [
        'stack', 'power', 'redundancy', 'hardware', 'transceiver'
    ],
    'cloud-ops': [
        'cloud', 'aws', 's3', 'azure', 'gcp', 'meraki'
    ]
}

def get_category(module_name):
    """
    Determine category for an RPC module based on keywords
    
    Args:
        module_name: Module name (e.g., 'wireless-access-point-cmd', 'install')
    
    Returns:
        Category name
    """
    module_lower = module_name.lower()
    
    # Check each category's keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in module_lower:
                return category
    
    # Default to 'other' if no match
    return 'other'


def create_consolidated_spec(category, paths_data):
    """
    Create a consolidated OpenAPI spec for a category
    
    Args:
        category: Category name
        paths_data: List of {'path': ..., 'operations': ..., 'source_module': ...}
    
    Returns:
        OpenAPI spec dict
    """
    
    # Determine category title
    titles = {
        'network-ops': 'RPC - Network Operations',
        'wireless-ops': 'RPC - Wireless Operations',
        'system-ops': 'RPC - System Operations',
        'security-ops': 'RPC - Security Operations',
        'config-ops': 'RPC - Configuration Management',
        'debug-ops': 'RPC - Debug & Troubleshooting',
        'platform-ops': 'RPC - Platform Operations',
        'cloud-ops': 'RPC - Cloud Operations',
        'other': 'RPC - Other Operations'
    }
    
    # Build description with module list
    modules = sorted(set(p['source_module'] for p in paths_data))
    description = f"""Cisco IOS-XE RPC Operations - {category.replace('-ops', '').title()}

**Category:** {category.replace('-ops', '').title()} Operations
**Modules:** {len(modules)}
**RPC Actions:** {len(paths_data)}

**HTTP Methods:**
- POST: Execute RPC action/operation

**Modules Included:**
{chr(10).join(f'- {m}' for m in modules)}

**RPC Operation Pattern:**
RPC operations are executed via RESTCONF POST to `/operations/` endpoints.
Each RPC accepts input parameters and returns output results.

**Example RPC Execution:**
```bash
POST /restconf/operations/Cisco-IOS-XE-rpc:ping
Content-Type: application/yang-data+json

{{
  "input": {{
    "ping-request": {{
      "destination": "10.0.0.1",
      "repeat-count": 5,
      "size": 100
    }}
  }}
}}
```

**Example Response:**
```json
{{
  "output": {{
    "ping-reply": {{
      "destination": "10.0.0.1",
      "request-count": 5,
      "reply-count": 5,
      "success-rate": 100,
      "minimum-rtt": 1,
      "average-rtt": 2,
      "maximum-rtt": 3
    }}
  }}
}}
```

**Common Operations:**
{chr(10).join(f"- {p['path'].split('/')[-1]}" for p in paths_data[:5])}
{'...' if len(paths_data) > 5 else ''}
"""
    
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": titles.get(category, f"RPC - {category.title()}"),
            "description": description,
            "version": "17.18.1"
        },
        "servers": [
            {
                "url": "https://{device}/restconf",
                "variables": {
                    "device": {
                        "default": "router.example.com",
                        "description": "Device IP or hostname"
                    }
                }
            }
        ],
        "paths": {}
    }
    
    # Add all paths
    for path_data in paths_data:
        path_key = path_data['path']
        operations = path_data['operations']
        
        # Enhance description with source module info
        for method, method_spec in operations.items():
            if 'description' in method_spec:
                method_spec['description'] = f"**Source Module:** {path_data['source_module']}\n\n{method_spec['description']}"
        
        spec['paths'][path_key] = operations
    
    return spec


def main():
    """Main execution"""
    
    print("=" * 70)
    print("PHASE 6: CONSOLIDATE RPC MODEL")
    print("=" * 70)
    
    # Find swagger-rpc-model/api directory
    api_dir = Path(__file__).parent.parent / 'swagger-rpc-model' / 'api'
    output_dir = api_dir
    
    if not api_dir.exists():
        print(f"ERROR: Directory not found: {api_dir}")
        return
    
    # Find all RPC/action JSON files
    json_files = sorted([f for f in api_dir.glob('*.json')])
    
    print(f"\nFound {len(json_files)} RPC module files to consolidate\n")
    
    # Group paths by category
    categorized_paths = defaultdict(list)
    module_stats = {}
    
    for json_file in json_files:
        # Extract module name
        module_name = json_file.stem.replace('Cisco-IOS-XE-', '').replace('-rpc', '').replace('-actions', '').replace('-cmd', '').replace('-cfg', '').replace('-oper', '').replace('cisco-', '').replace('tailf-netconf-', '')
        
        # Read JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        
        # Get category
        category = get_category(module_name)
        
        # Extract paths
        paths = spec.get('paths', {})
        path_count = len(paths)
        
        module_stats[module_name] = {
            'category': category,
            'paths': path_count,
            'size_kb': json_file.stat().st_size / 1024
        }
        
        # Add to category
        for path_key, path_obj in paths.items():
            categorized_paths[category].append({
                'path': path_key,
                'operations': path_obj,
                'source_module': module_name
            })
        
        print(f"  {module_name:<40} -> {category:<15} ({path_count} paths)")
    
    # Generate consolidated specs
    print(f"\n{'='*70}")
    print("Generating consolidated RPC category files...\n")
    
    manifest = {
        "title": "RPC Model Manifest",
        "description": "Consolidated RPC action categories",
        "total_modules": len(json_files),
        "total_paths": sum(len(paths) for paths in categorized_paths.values()),
        "categories": {}
    }
    
    for category, paths_data in sorted(categorized_paths.items()):
        # Create consolidated spec
        spec = create_consolidated_spec(category, paths_data)
        
        # Write to file
        output_file = output_dir / f"rpc-{category}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2)
        
        # Get module count
        modules = set(p['source_module'] for p in paths_data)
        
        # Update manifest
        manifest['categories'][category] = {
            'file': output_file.name,
            'modules': len(modules),
            'paths': len(paths_data),
            'size_kb': round(output_file.stat().st_size / 1024, 1)
        }
        
        print(f"  {category:<15} {len(paths_data):>3} paths  {len(modules):>2} modules  "
              f"{output_file.stat().st_size/1024:>6.1f} KB")
    
    # Write manifest
    manifest_file = output_dir / 'rpc-manifest.json'
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n{'='*70}")
    print("CONSOLIDATION COMPLETE")
    print("="*70)
    print(f"""
Summary:
  {len(json_files)} module files -> {len(categorized_paths)} category files
  Total RPC actions: {manifest['total_paths']}
  
  Manifest: {manifest_file.name}
  
Category Distribution:
""")
    
    for cat, info in sorted(manifest['categories'].items(), key=lambda x: x[1]['paths'], reverse=True):
        print(f"  {cat:<15} {info['paths']:>3} paths from {info['modules']:>2} modules")
    
    print(f"\n{'='*70}")
    print("Next: Delete old 54 individual files")
    print("Command: Remove-Item 'swagger-rpc-model/api/*.json' -Exclude 'rpc-*'")
    print("="*70)


if __name__ == '__main__':
    main()
