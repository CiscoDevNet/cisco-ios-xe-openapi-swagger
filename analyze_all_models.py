#!/usr/bin/env python3
"""Analyze all Swagger model types - count paths, operations, and modules."""

import json
from pathlib import Path
from collections import defaultdict

def analyze_model_type(model_dir, model_name):
    """Analyze a specific model type directory."""
    api_dir = Path(model_dir) / "api"
    
    if not api_dir.exists():
        return None
    
    json_files = list(api_dir.glob("*.json"))
    if not json_files:
        return None
    
    total_paths = 0
    total_operations = 0
    module_count = len(json_files)
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8', errors='ignore') as f:
                spec = json.load(f)
            
            if 'paths' in spec:
                path_count = len(spec['paths'])
                total_paths += path_count
                
                # Count operations (GET, PUT, POST, DELETE, PATCH)
                for path, methods in spec['paths'].items():
                    total_operations += len(methods)
        except Exception as e:
            print(f"  Warning: Error reading {json_file.name}: {e}")
    
    return {
        'modules': module_count,
        'paths': total_paths,
        'operations': total_operations
    }

# Model types to analyze
model_types = [
    ('swagger-native-config-model', 'Native Config'),
    ('swagger-oper-model', 'Operational'),
    ('swagger-rpc-model', 'RPC'),
    ('swagger-cfg-model', 'Config'),
    ('swagger-ietf-model', 'IETF'),
    ('swagger-mib-model', 'MIB'),
    ('swagger-openconfig-model', 'OpenConfig'),
    ('swagger-events-model', 'Events'),
    ('swagger-other-model', 'Other'),
]

print("="*80)
print("Cisco IOS-XE 17.18.1 - Complete API Coverage Analysis")
print("="*80)
print()
print(f"{'Model Type':<20} {'Modules':<10} {'Paths':<10} {'Operations':<12}")
print("-"*80)

grand_total_modules = 0
grand_total_paths = 0
grand_total_operations = 0

results = []

for model_dir, model_name in model_types:
    result = analyze_model_type(model_dir, model_name)
    
    if result:
        results.append((model_name, result))
        print(f"{model_name:<20} {result['modules']:<10} {result['paths']:<10,} {result['operations']:<12,}")
        grand_total_modules += result['modules']
        grand_total_paths += result['paths']
        grand_total_operations += result['operations']
    else:
        print(f"{model_name:<20} {'N/A':<10} {'N/A':<10} {'N/A':<12}")

print("-"*80)
print(f"{'GRAND TOTAL':<20} {grand_total_modules:<10} {grand_total_paths:<10,} {grand_total_operations:<12,}")
print("="*80)
print()

# Show top categories
print("Top 5 Model Types by Operations:")
print("-"*80)
sorted_results = sorted(results, key=lambda x: x[1]['operations'], reverse=True)[:5]
for i, (name, data) in enumerate(sorted_results, 1):
    print(f"{i}. {name:<20} {data['operations']:,} operations ({data['paths']:,} paths)")

print()
print("Coverage by Model Type (% of total operations):")
print("-"*80)
for name, data in sorted_results:
    percentage = (data['operations'] / grand_total_operations * 100) if grand_total_operations > 0 else 0
    bar_length = int(percentage / 2)
    bar = '█' * bar_length
    print(f"{name:<20} {bar:<50} {percentage:5.1f}%")

print("="*80)
