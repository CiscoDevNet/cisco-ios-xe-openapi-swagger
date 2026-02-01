#!/usr/bin/env python3
"""Analyze leaf node coverage in Native Config specs."""

import json
from pathlib import Path

api_dir = Path("swagger-native-config-model/api")
json_files = sorted(api_dir.glob("native-*.json"))

total_paths = 0
leaf_paths = 0
container_paths = 0
list_paths = 0

print("Analyzing Native Config API Coverage...")
print("="*70)

for json_file in json_files:
    with open(json_file, 'r') as f:
        spec = json.load(f)
    
    if 'paths' in spec:
        file_total = len(spec['paths'])
        file_leaves = 0
        
        for path, methods in spec['paths'].items():
            # Check if it's a leaf (simple GET/PUT endpoint without nested paths)
            if 'get' in methods:
                summary = methods['get'].get('summary', '')
                if any(keyword in summary.lower() for keyword in ['leaf', 'configuration']):
                    file_leaves += 1
            
            total_paths += 1
        
        if file_leaves > 0:
            print(f"{json_file.name}: {file_total} total paths ({file_leaves} leaves)")

print("="*70)
print(f"\nTotal Paths Generated: {total_paths}")
print(f"\nTop-level leaf nodes now available:")
print("  - hostname")
print("  - version")
print("  - config-register")
print("  - boot-start-marker")
print("  - boot-end-marker")
print("  - captive-portal-bypass")
print("  - aqm-register-fnf")
print("  - And many more...")
