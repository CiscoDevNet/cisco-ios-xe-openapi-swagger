#!/usr/bin/env python3
"""
Phase 5: Consolidate Oper Model - Post-Processor
Consolidates 197 individual module files into 12-15 category files
"""

import json
from pathlib import Path
from collections import defaultdict

def get_category(module_name: str) -> str:
    """Categorize module based on name patterns"""
    name_lower = module_name.lower()
    
    # Wireless (18 modules)
    if any(x in name_lower for x in ['wireless', 'wifi', 'wlan', 'dot11', 'ap-', 'mesh', 'rrm', 'rogue']):
        return 'wireless'
    
    # Platform & Hardware
    if any(x in name_lower for x in ['platform', 'environment', 'power', 'fan', 'temperature', 
                                      'sensor', 'transceiver', 'stack', 'inventory', 'bbu', 'poe',
                                      'redundancy', 'entity']):
        return 'platform'
    
    # Interfaces & Layer 2
    if any(x in name_lower for x in ['interface', 'ethernet', 'vlan', 'port', 'lacp', 'lldp', 
                                      'cdp', 'switch', 'dot1x', 'bridge', 'cfm', 'stp']):
        return 'interfaces'
    
    # Routing
    if any(x in name_lower for x in ['bgp', 'ospf', 'eigrp', 'rip', 'isis', 'routing', 'route', 
                                      'rib', 'fib', 'pim', 'multicast', 'igmp', 'msdp']):
        return 'routing'
    
    # Security & AAA
    if any(x in name_lower for x in ['aaa', 'acl', 'security', 'crypto', 'ipsec', 'ikev2', 
                                      'pki', 'trustsec', 'macsec', 'zone', 'identity']):
        return 'security'
    
    # MPLS & TE
    if any(x in name_lower for x in ['mpls', 'ldp', 'rsvp', 'te-', 'segment-routing', 'sr-']):
        return 'mpls'
    
    # QoS
    if any(x in name_lower for x in ['qos', 'policy', 'class-map', 'queue', 'scheduler', 'wred']):
        return 'qos'
    
    # SD-WAN & WAN
    if any(x in name_lower for x in ['sdwan', 'sd-wan', 'appqoe', 'waas', 'cflowd', 'dre', 'wccp']):
        return 'sdwan'
    
    # VPN & Tunnels
    if any(x in name_lower for x in ['tunnel', 'gre', 'vpn', 'dmvpn', 'lisp', 'vxlan', 
                                      'evpn', 'pseudowire', 'l2vpn', 'otv']):
        return 'vpn'
    
    # Network Services
    if any(x in name_lower for x in ['dhcp', 'dns', 'nat', 'ip-sla', 'ipsla', 'track', 
                                      'hsrp', 'vrrp', 'glbp', 'arp', 'nd', 'nwpi']):
        return 'services'
    
    # System & Management
    if any(x in name_lower for x in ['system', 'process', 'memory', 'cpu', 'licensing', 'license',
                                      'logging', 'syslog', 'ntp', 'snmp', 'boot', 'software']):
        return 'system'
    
    # Telemetry & Automation
    if any(x in name_lower for x in ['netconf', 'restconf', 'gnmi', 'telemetry', 'mdt', 
                                      'streaming', 'app-hosting', 'utd']):
        return 'telemetry'
    
    # Voice
    if any(x in name_lower for x in ['voice', 'sip', 'dial-peer', 'sccp']):
        return 'voice'
    
    # Controller & Fabric
    if any(x in name_lower for x in ['controller', 'fabric', 'lisp', 'vxlan', 'sd-access']):
        return 'controller'
    
    # Cellular/WAN
    if any(x in name_lower for x in ['cellwan', 'cellular', 'lte', 'gps', 'gnss']):
        return 'cellular'
    
    return 'other'

def consolidate_specs():
    """Consolidate 197 individual specs into category files"""
    api_dir = Path('swagger-oper-model/api')
    
    # Read all module files
    category_paths = defaultdict(list)
    category_modules = defaultdict(list)
    
    print("Reading module files...")
    module_files = list(api_dir.glob('Cisco-IOS-XE-*-oper.json'))
    
    for module_file in module_files:
        module_name = module_file.stem
        with open(module_file, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        
        category = get_category(module_name)
        
        # Store paths and module name
        if 'paths' in spec:
            for path, path_obj in spec['paths'].items():
                category_paths[category].append({
                    'path': path,
                    'path_obj': path_obj,
                    'module': module_name
                })
        
        category_modules[category].append(module_name)
    
    # Create consolidated spec for each category
    print("\nGenerating consolidated specs by category:")
    total_paths_written = 0
    
    category_titles = {
        'wireless': 'Operational - Wireless',
        'platform': 'Operational - Platform & Hardware',
        'interfaces': 'Operational - Interfaces & Layer 2',
        'routing': 'Operational - Routing Protocols',
        'security': 'Operational - Security & AAA',
        'mpls': 'Operational - MPLS & TE',
        'qos': 'Operational - QoS & Policy',
        'sdwan': 'Operational - SD-WAN & WAN',
        'vpn': 'Operational - VPN & Tunnels',
        'services': 'Operational - Network Services',
        'system': 'Operational - System & Management',
        'telemetry': 'Operational - Telemetry & Automation',
        'voice': 'Operational - Voice',
        'controller': 'Operational - Controller & Fabric',
        'cellular': 'Operational - Cellular/WAN',
        'other': 'Operational - Other Services'
    }
    
    for category, paths_list in sorted(category_paths.items()):
        if not paths_list:
            continue
        
        # Create consolidated spec
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": category_titles.get(category, f"Operational - {category.title()}"),
                "description": f"Cisco IOS-XE Operational State Data - {category.title()}\n\n"
                              f"**Category:** {category.title()}\n"
                              f"**Modules:** {len(category_modules[category])}\n"
                              f"**Paths:** {len(paths_list)}\n\n"
                              f"**HTTP Methods:**\n"
                              f"- GET: Retrieve operational state data\n\n"
                              f"**Modules Included:**\n" +
                              '\n'.join([f"- {mod}" for mod in sorted(category_modules[category])[:20]]) +
                              (f"\n- ... and {len(category_modules[category]) - 20} more" if len(category_modules[category]) > 20 else ""),
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
        for path_info in paths_list:
            spec['paths'][path_info['path']] = path_info['path_obj']
        
        # Write consolidated file
        output_file = api_dir / f"oper-{category}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2)
        
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"  * {category}: {len(paths_list)} paths, {len(category_modules[category])} modules ({file_size_mb:.2f} MB) -> {output_file.name}")
        total_paths_written += len(paths_list)
    
    # Create manifest
    manifest = {
        'total_categories': len(category_paths),
        'total_paths': total_paths_written,
        'total_modules': len(module_files),
        'categories': {cat: len(paths) for cat, paths in category_paths.items()},
        'generator': 'consolidate_oper.py (Phase 5)',
        'version': '17.18.1',
        'enhancement': 'Phase 5 - Consolidated from 197 module files to category-based organization'
    }
    
    manifest_file = api_dir / 'manifest.json'
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"Consolidation Complete:")
    print(f"  197 module files -> {len(category_paths)} category files")
    print(f"  Total paths: {total_paths_written}")
    print(f"  Manifest: {manifest_file}")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    consolidate_specs()
