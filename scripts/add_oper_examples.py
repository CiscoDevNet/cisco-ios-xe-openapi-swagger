#!/usr/bin/env python3
"""
Add production-realistic examples to Operational Data Model OpenAPI specs

This script enhances the consolidated oper-*.json files with realistic
operational data examples. Examples are based on actual Cisco device outputs
and provide meaningful, production-like values.

Phase 5 Week 2: Production Examples
"""

import json
from pathlib import Path
import re

def get_example_for_field(field_name, category):
    """
    Generate production-realistic example values based on field name and category
    
    Returns example values that match what you'd see on real Cisco IOS-XE devices
    """
    
    field_lower = field_name.lower()
    
    # CPU and Performance
    if 'cpu' in field_lower and ('usage' in field_lower or 'utilization' in field_lower or 'percent' in field_lower):
        return 5
    if 'cpu' in field_lower and 'load' in field_lower:
        return 0.05
    if 'cpu-time' in field_lower or 'cputime' in field_lower:
        return 45123456
    
    # Memory
    if 'memory' in field_lower:
        if 'total' in field_lower or 'size' in field_lower:
            return 2048000000  # 2GB in bytes
        if 'used' in field_lower:
            return 921600000   # ~900MB
        if 'free' in field_lower:
            return 1126400000  # ~1.1GB
        if 'percent' in field_lower or 'usage' in field_lower:
            return 45
    
    # Temperature
    if 'temperature' in field_lower or 'temp' in field_lower:
        return 45
    if 'thermal' in field_lower:
        return "Normal"
    
    # Power
    if 'power' in field_lower:
        if 'status' in field_lower or 'state' in field_lower:
            return "Normal"
        if 'watts' in field_lower or 'consumption' in field_lower:
            return 125.5
        if 'voltage' in field_lower:
            return 12.1
        if 'current' in field_lower:
            return 10.4
    
    # Fan
    if 'fan' in field_lower:
        if 'rpm' in field_lower or 'speed' in field_lower:
            return 3200
        if 'status' in field_lower or 'state' in field_lower:
            return "Normal"
    
    # Uptime
    if 'uptime' in field_lower or 'up-time' in field_lower:
        if 'second' in field_lower:
            return 651780  # 7d 14h 23m
        return "7d 14h 23m"
    
    # Interface Status
    if 'oper-status' in field_lower or 'status' in field_lower:
        if category == 'interfaces':
            return "up"
    if 'admin' in field_lower and 'status' in field_lower:
        return "up"
    if 'link-state' in field_lower or 'link-status' in field_lower:
        return "up"
    
    # Speed and Duplex
    if 'speed' in field_lower and not 'fan' in field_lower:
        if 'mbps' in field_lower.replace('-', ''):
            return 1000
        return "1000Mbps"
    if 'duplex' in field_lower:
        return "full"
    if 'bandwidth' in field_lower:
        return 1000000000  # 1Gbps in bps
    
    # Counters
    if 'packet' in field_lower and ('in' in field_lower or 'rx' in field_lower or 'receive' in field_lower):
        return 12845632
    if 'packet' in field_lower and ('out' in field_lower or 'tx' in field_lower or 'transmit' in field_lower):
        return 10234567
    if 'byte' in field_lower and ('in' in field_lower or 'rx' in field_lower):
        return 1284563200
    if 'byte' in field_lower and ('out' in field_lower or 'tx' in field_lower):
        return 1023456700
    if 'error' in field_lower and ('in' in field_lower or 'input' in field_lower):
        return 0
    if 'error' in field_lower and ('out' in field_lower or 'output' in field_lower):
        return 0
    if 'drop' in field_lower:
        return 0
    if 'crc' in field_lower:
        return 0
    if 'collision' in field_lower:
        return 0
    
    # BGP
    if 'bgp' in field_lower:
        if 'state' in field_lower:
            return "Established"
        if 'session-state' in field_lower:
            return "Established"
        if 'neighbor' in field_lower and 'id' in field_lower:
            return "192.168.1.1"
        if 'as' in field_lower or 'asn' in field_lower:
            return 65001
        if 'prefix' in field_lower:
            return 1250
    
    # OSPF
    if 'ospf' in field_lower:
        if 'state' in field_lower:
            return "Full"
        if 'neighbor' in field_lower and 'id' in field_lower:
            return "1.1.1.1"
        if 'area' in field_lower:
            return "0.0.0.0"
    
    # IP Addresses
    if 'ip-address' in field_lower or 'ipaddress' in field_lower or field_lower == 'ip':
        return "10.0.0.1"
    if 'ipv6-address' in field_lower or 'ipv6address' in field_lower:
        return "2001:db8::1"
    if 'mac-address' in field_lower or 'macaddress' in field_lower:
        return "00:1A:2B:3C:4D:5E"
    if 'subnet' in field_lower or 'netmask' in field_lower:
        return "255.255.255.0"
    if 'prefix-length' in field_lower:
        return 24
    
    # Interface Names
    if 'interface' in field_lower and 'name' in field_lower:
        return "GigabitEthernet1/0/1"
    if 'port' in field_lower and 'name' in field_lower:
        return "Gi1/0/1"
    
    # Serial Numbers and IDs
    if 'serial' in field_lower and 'number' in field_lower:
        return "FOC2145L0QS"
    if 'pid' in field_lower or 'product-id' in field_lower:
        return "C9300-48P"
    if 'vid' in field_lower or 'version-id' in field_lower:
        return "V01"
    
    # Software Versions
    if 'version' in field_lower and 'software' in field_lower:
        return "17.18.1"
    if 'ios' in field_lower and 'version' in field_lower:
        return "17.18.1"
    
    # VLAN
    if 'vlan' in field_lower and 'id' in field_lower:
        return 100
    if 'vlan' in field_lower and 'name' in field_lower:
        return "DATA_VLAN"
    
    # Wireless
    if 'ssid' in field_lower:
        return "Corporate-WiFi"
    if 'channel' in field_lower and category == 'wireless':
        return 36
    if 'client' in field_lower and 'count' in field_lower:
        return 45
    if 'rssi' in field_lower:
        return -55
    if 'snr' in field_lower:
        return 35
    
    # Generic States
    if 'status' in field_lower or 'state' in field_lower:
        return "Normal"
    if 'enabled' in field_lower or 'enable' in field_lower:
        return True
    if 'disabled' in field_lower or 'disable' in field_lower:
        return False
    
    # Timestamps
    if 'timestamp' in field_lower or 'time' in field_lower:
        return "2024-02-22T10:30:45Z"
    if 'date' in field_lower:
        return "2024-02-22"
    
    # Generic Strings
    if 'name' in field_lower:
        return "example-name"
    if 'description' in field_lower or 'desc' in field_lower:
        return "Sample description"
    
    # Generic Numbers
    if 'count' in field_lower or 'number' in field_lower:
        return 10
    if 'index' in field_lower or 'id' in field_lower:
        return 1
    
    # Default fallback
    return "example-value"


def add_examples_to_schema(schema, category, path=""):
    """
    Recursively add examples to schema properties
    
    Args:
        schema: Schema object to enhance
        category: Category name (interfaces, routing, etc.)
        path: Current path in schema for context
    """
    
    if not isinstance(schema, dict):
        return
    
    # Add example to leaf properties
    if 'type' in schema and 'example' not in schema:
        field_name = path.split('/')[-1] if path else ""
        
        if schema['type'] == 'string':
            schema['example'] = str(get_example_for_field(field_name, category))
        elif schema['type'] == 'integer':
            example = get_example_for_field(field_name, category)
            schema['example'] = int(example) if isinstance(example, (int, float, str)) and str(example).replace('-', '').isdigit() else 1
        elif schema['type'] == 'number':
            example = get_example_for_field(field_name, category)
            schema['example'] = float(example) if isinstance(example, (int, float)) else 1.0
        elif schema['type'] == 'boolean':
            example = get_example_for_field(field_name, category)
            schema['example'] = bool(example) if isinstance(example, bool) else True
        elif schema['type'] == 'array' and 'items' in schema:
            add_examples_to_schema(schema['items'], category, path + '/items')
    
    # Recurse into properties
    if 'properties' in schema:
        for prop_name, prop_schema in schema['properties'].items():
            add_examples_to_schema(prop_schema, category, f"{path}/{prop_name}")
    
    # Recurse into allOf/anyOf/oneOf
    for key in ['allOf', 'anyOf', 'oneOf']:
        if key in schema:
            for i, sub_schema in enumerate(schema[key]):
                add_examples_to_schema(sub_schema, category, f"{path}/{key}[{i}]")


def process_oper_file(file_path):
    """
    Process a single consolidated oper-*.json file to add examples
    
    Args:
        file_path: Path to the OpenAPI JSON file
    """
    
    print(f"\nProcessing: {file_path.name}")
    
    # Read JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    # Extract category from filename (e.g., oper-interfaces.json -> interfaces)
    category = file_path.stem.replace('oper-', '')
    
    # Process all schemas
    if 'components' in spec and 'schemas' in spec['components']:
        schemas = spec['components']['schemas']
        print(f"  Enhancing {len(schemas)} schemas with production examples...")
        
        for schema_name, schema_def in schemas.items():
            add_examples_to_schema(schema_def, category, schema_name)
    
    # Write enhanced JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)
    
    print(f"  ✓ Enhanced with realistic operational data examples")


def main():
    """Main execution"""
    
    print("=" * 70)
    print("PHASE 5 WEEK 2: Add Production-Realistic Examples to Oper Model")
    print("=" * 70)
    
    # Find swagger-oper-model/api directory
    api_dir = Path(__file__).parent.parent / 'swagger-oper-model' / 'api'
    
    if not api_dir.exists():
        print(f"ERROR: Directory not found: {api_dir}")
        return
    
    # Process all oper-*.json files (excluding manifest)
    oper_files = sorted([f for f in api_dir.glob('oper-*.json') if f.name != 'manifest.json'])
    
    print(f"\nFound {len(oper_files)} consolidated Oper files to enhance\n")
    
    for file_path in oper_files:
        process_oper_file(file_path)
    
    print("\n" + "=" * 70)
    print("COMPLETE: All Oper files enhanced with production examples")
    print("=" * 70)
    print(f"\nEnhanced files:")
    for f in oper_files:
        print(f"  - {f.name}")


if __name__ == '__main__':
    main()
