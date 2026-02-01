#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a combined OpenAPI specification containing ALL Operational GET operations from all modules.
This creates a single unified view of all operational data endpoints.
"""

import json
from pathlib import Path
import sys

# Ensure proper console encoding
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

def generate_combined_spec():
    """Combine all operational GET operations from all modules into a single OpenAPI spec."""

    # Get script directory and construct absolute path
    script_dir = Path(__file__).parent
    api_dir = script_dir / "swagger-oper-model" / "api"

    # Read manifest to get accurate count
    manifest_file = api_dir / "manifest.json"
    total_modules = 209  # Default
    if manifest_file.exists():
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            total_modules = manifest.get('total_modules', 209)

    # Base OpenAPI structure
    combined_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Cisco IOS-XE - ALL Operational Data (Combined)",
            "version": "17.18.1",
            "description": f"**Complete collection of all {total_modules} operational GET endpoints** from all IOS-XE YANG modules in a single unified view.\n\n"
                          "This consolidated specification includes read-only operational state data from:\n"
                          "- **Interfaces & Layer 2** (14 modules): Interface stats, bridge domains, VLANs, STP\n"
                          "- **Routing Protocols** (12 modules): BGP, OSPF, EIGRP, ISIS, RIP, PIM\n"
                          "- **MPLS & TE** (4 modules): MPLS forwarding, LDP, TE tunnels\n"
                          "- **VPN & Tunnels** (6 modules): L2VPN, GRE, IPsec, VXLAN, NVE\n"
                          "- **Wireless** (37 modules): AP management, clients, RF, location services\n"
                          "- **Security & AAA** (9 modules): Authentication, crypto, trustsec, firewall\n"
                          "- **Platform & Hardware** (10 modules): Sensors, inventory, transceivers, PoE\n"
                          "- **QoS & Policy** (2 modules): Policy maps, DiffServ targets\n"
                          "- **System & Management** (6 modules): Memory, CPU, processes, environment\n"
                          "- **Network Services** (11 modules): DHCP, DNS, NAT, NTP, CDP, LLDP\n"
                          "- **Telemetry & Automation** (10 modules): Model-driven telemetry, NETCONF, streaming\n"
                          "- **SD-WAN & WAN** (8 modules): AppQoE, SDWAN, cloud services\n"
                          "- **Other Services** (80 modules): Controllers, stacking, diagnostics, and specialized features\n\n"
                          "**Authentication**: All operations require HTTP Basic Authentication.\n\n"
                          "**Base URL**: `https://{device}/restconf`\n\n"
                          "**Content-Type**: `application/yang-data+json`\n\n"
                          "**Note**: All endpoints are GET-only (read-only operational state data).",
            "contact": {
                "name": "Cisco IOS-XE RESTCONF API",
                "url": "https://developer.cisco.com/docs/ios-xe"
            }
        },
        "servers": [
            {
                "url": "https://{device}/restconf",
                "description": "IOS-XE Device RESTCONF Endpoint",
                "variables": {
                    "device": {
                        "default": "sandbox-iosxe-latest-1.cisco.com",
                        "description": "Device hostname or IP address"
                    }
                }
            }
        ],
        "paths": {},
        "components": {
            "securitySchemes": {
                "basicAuth": {
                    "type": "http",
                    "scheme": "basic",
                    "description": "HTTP Basic Authentication using device credentials"
                }
            },
            "schemas": {}
        },
        "security": [
            {
                "basicAuth": []
            }
        ],
        "tags": []
    }

    # Category mapping for better organization
    category_descriptions = {
        "Interfaces & Layer 2": "Interface statistics, bridge domains, VLANs, and Layer 2 protocols",
        "Routing Protocols": "BGP, OSPF, EIGRP, ISIS, RIP, PIM routing protocol state",
        "MPLS & TE": "MPLS forwarding, LDP sessions, and Traffic Engineering",
        "VPN & Tunnels": "L2VPN, GRE, IPsec, VXLAN tunnel operational data",
        "Wireless": "Wireless LAN controller, access points, clients, and RF management",
        "Security & AAA": "Authentication, authorization, cryptography, and security features",
        "Platform & Hardware": "Hardware sensors, inventory, transceivers, power management",
        "QoS & Policy": "Quality of Service policies and statistics",
        "System & Management": "System resources, processes, memory, and environment",
        "Network Services": "DHCP, DNS, NAT, NTP, discovery protocols",
        "Telemetry & Automation": "Model-driven telemetry, NETCONF, streaming telemetry",
        "SD-WAN & WAN": "SD-WAN, AppQoE, and WAN optimization",
        "Other Services": "Specialized features, controllers, and diagnostics"
    }

    # Track statistics
    total_operations = 0
    modules_processed = 0
    tags_by_category = {}

    # Process all JSON files
    json_files = sorted(api_dir.glob("*.json"))

    print(f"\n🔧 Combining {len(json_files)} operational modules...")

    for json_file in json_files:
        if json_file.name == "manifest.json":
            continue

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                spec = json.load(f)

            module_name = json_file.stem
            modules_processed += 1

            # Extract module info
            module_info = spec.get('info', {})
            module_title = module_info.get('title', module_name)
            module_description = module_info.get('description', f'Operational data from {module_name}')

            # Extract category from description (for internal organization only)
            category = "Other Services"
            if 'Category:' in module_description:
                category_line = module_description.split('Category:')[1].split('\n')[0].strip()
                category = category_line

            # Clean up description - remove copyright and category lines
            if 'Copyright' in module_description:
                # Keep only the text before the copyright notice
                parts = module_description.split('Copyright')
                module_description = parts[0].strip()

            # Remove category line from description
            if 'Category:' in module_description:
                parts = module_description.split('Category:')
                module_description = parts[0].strip()

            # Track tags by category
            if category not in tags_by_category:
                tags_by_category[category] = []

            # Add tag
            tag_entry = {
                "name": module_name,
                "description": module_description,
                "x-displayName": module_title
            }
            tags_by_category[category].append(tag_entry)

            # Merge paths (operations)
            if 'paths' in spec:
                for path, methods in spec['paths'].items():
                    for method, operation in methods.items():
                        # Add tag to operation
                        if 'tags' not in operation:
                            operation['tags'] = []
                        if module_name not in operation['tags']:
                            operation['tags'].append(module_name)

                        total_operations += 1

                    # Add path
                    if path in combined_spec['paths']:
                        combined_spec['paths'][path].update(methods)
                    else:
                        combined_spec['paths'][path] = methods

            # Merge schemas (optional, to keep spec size manageable we might skip this)
            # Operational modules typically have examples in responses rather than complex schemas

        except Exception as e:
            print(f"  ⚠️  Error processing {json_file.name}: {e}")
            continue

    # Build organized tag list - just modules, no category headers
    organized_tags = []
    for category in sorted(tags_by_category.keys()):
        # Add module tags (skip category headers)
        for tag in sorted(tags_by_category[category], key=lambda x: x['name']):
            organized_tags.append(tag)

    combined_spec['tags'] = organized_tags

    # Write combined specification
    output_file = api_dir / "all-operations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_spec, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Combined specification created successfully!")
    print(f"   📊 Modules processed: {modules_processed}")
    print(f"   📡 Total operations: {total_operations}")
    print(f"   🏷️  Categories: {len(tags_by_category)}")
    print(f"   📄 Output: {output_file}")
    print(f"   💾 Size: {output_file.stat().st_size / 1024:.1f} KB")

    return combined_spec

if __name__ == "__main__":
    try:
        generate_combined_spec()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
