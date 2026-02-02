#!/usr/bin/env python3
"""
Consolidate Events Model into category-based files

Consolidates 39 individual Cisco-IOS-XE-*-events.json files into logical
event category groupings.

Phase 6: Events Model Enhancement
"""

import json
from pathlib import Path
from collections import defaultdict

# Event category mappings based on module names
CATEGORY_KEYWORDS = {
    'interfaces': [
        'interface', 'ethernet', 'port', 'lacp', 'lldp', 'cdp',
        'vlan', 'switchport', 'efp', 'port-bounce'
    ],
    'routing': [
        'bgp', 'ospf', 'eigrp', 'rip', 'isis', 'fib', 'pim',
        'mroute', 'msdp', 'perf-measure'
    ],
    'security': [
        'aaa', 'crypto', 'pki', 'ipsec', 'ikev2', 'trustsec',
        'firewall', 'ngfw', 'zbfw'
    ],
    'platform': [
        'platform', 'environment', 'power', 'fan', 'temperature',
        'chassis', 'stack', 'boot', 'install', 'controller'
    ],
    'wireless': [
        'wireless', 'wlan', 'dot11', 'ap-', 'mesh', 'rrm', 'rfid'
    ],
    'vpn': [
        'tunnel', 'gre', 'vpn', 'dmvpn', 'ipsla', 'lisp', 'geo'
    ],
    'sdwan': [
        'sdwan', 'viptela', 'appqoe', 'waas', 'dca'
    ],
    'services': [
        'dhcp', 'nat', 'hsrp', 'vrrp', 'arp', 'nd', 'ntp',
        'endpoint-tracker'
    ],
    'system': [
        'ios-', 'sm-', 'process', 'memory', 'cpu', 'syslog',
        'im-'
    ],
    'qos': [
        'qfp', 'qos', 'diffserv', 'policy', 'red-app'
    ]
}

def get_category(module_name):
    """
    Determine category for a module based on keywords
    
    Args:
        module_name: Module name (e.g., 'aaa', 'bgp', 'interface')
    
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
        'interfaces': 'Events - Interface & Port Events',
        'routing': 'Events - Routing Protocol Events',
        'security': 'Events - Security & Authentication Events',
        'platform': 'Events - Platform & Hardware Events',
        'wireless': 'Events - Wireless Events',
        'vpn': 'Events - VPN & Tunnel Events',
        'sdwan': 'Events - SD-WAN Events',
        'services': 'Events - Network Services Events',
        'system': 'Events - System Events',
        'qos': 'Events - QoS & Performance Events',
        'other': 'Events - Miscellaneous Events'
    }
    
    # Build description with module list
    modules = sorted(set(p['source_module'] for p in paths_data))
    description = f"""Cisco IOS-XE Event Notifications - {category.title()}

**Category:** {category.title()}
**Modules:** {len(modules)}
**Notification Endpoints:** {len(paths_data)}

**HTTP Methods:**
- POST: Subscribe to event notifications (YANG notification streams)
- GET: Query notification stream metadata

**Modules Included:**
{chr(10).join(f'- {m}' for m in modules)}

**Event Notification Pattern:**
Events are delivered via YANG notification streams. Subscribe using RESTCONF or NETCONF 
to receive real-time notifications when events occur.

**Example Subscription:**
```bash
POST /restconf/operations/ietf-subscribed-notifications:establish-subscription
Content-Type: application/yang-data+json

{{
  "input": {{
    "stream": "NETCONF",
    "encoding": "encode-json",
    "filter": {{
      "stream-subtree-filter": {{
        "notification-name": "{paths_data[0]['path'].split('/')[-1] if paths_data else 'event-name'}"
      }}
    }}
  }}
}}
```

**Example Notification:**
```json
{{
  "ietf-restconf:notification": {{
    "eventTime": "2024-02-01T10:30:45.123Z",
    "event": {{
      "severity": "critical",
      "message": "Interface GigabitEthernet1/0/1 changed state to down"
    }}
  }}
}}
```
"""
    
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": titles.get(category, f"Events - {category.title()}"),
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
    print("PHASE 6: CONSOLIDATE EVENTS MODEL")
    print("=" * 70)
    
    # Find swagger-events-model/api directory
    api_dir = Path(__file__).parent.parent / 'swagger-events-model' / 'api'
    output_dir = api_dir
    
    if not api_dir.exists():
        print(f"ERROR: Directory not found: {api_dir}")
        return
    
    # Find all Cisco-IOS-XE-*-events.json files
    json_files = sorted([f for f in api_dir.glob('Cisco-IOS-XE-*.json')])
    
    print(f"\nFound {len(json_files)} event module files to consolidate\n")
    
    # Group paths by category
    categorized_paths = defaultdict(list)
    module_stats = {}
    
    for json_file in json_files:
        # Extract module name
        module_name = json_file.stem.replace('Cisco-IOS-XE-', '').replace('-events', '').replace('-oper', '')
        
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
    print("Generating consolidated event category files...\n")
    
    manifest = {
        "title": "Events Model Manifest",
        "description": "Consolidated event notification categories",
        "total_modules": len(json_files),
        "total_paths": sum(len(paths) for paths in categorized_paths.values()),
        "categories": {}
    }
    
    for category, paths_data in sorted(categorized_paths.items()):
        # Create consolidated spec
        spec = create_consolidated_spec(category, paths_data)
        
        # Write to file
        output_file = output_dir / f"events-{category}.json"
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
    manifest_file = output_dir / 'events-manifest.json'
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n{'='*70}")
    print("CONSOLIDATION COMPLETE")
    print("="*70)
    print(f"""
Summary:
  {len(json_files)} module files -> {len(categorized_paths)} category files
  Total paths: {manifest['total_paths']}
  
  Manifest: {manifest_file.name}
  
Category Distribution:
""")
    
    for cat, info in sorted(manifest['categories'].items(), key=lambda x: x[1]['paths'], reverse=True):
        print(f"  {cat:<15} {info['paths']:>3} paths from {info['modules']:>2} modules")
    
    print(f"\n{'='*70}")
    print("Next: Delete old 39 individual files")
    print("Command: Remove-Item 'swagger-events-model/api/Cisco-IOS-XE-*-events*.json'")
    print("="*70)


if __name__ == '__main__':
    main()
