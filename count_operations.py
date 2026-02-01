#!/usr/bin/env python3
"""Count API operations and XPath coverage in Native Config."""

import json
from pathlib import Path

# Count API operations in generated specs
api_dir = Path("swagger-native-config-model/api")
json_files = sorted(api_dir.glob("native-*.json"))

total_paths = 0
total_operations = 0
categories = {}

print("Native Config Model - Coverage Analysis")
print("="*70)
print("\nAPI Operations by Category:")
print("-"*70)

for json_file in json_files:
    with open(json_file, 'r') as f:
        spec = json.load(f)
    
    if 'paths' in spec:
        path_count = len(spec['paths'])
        operation_count = 0
        
        # Count operations (GET, PUT, POST, DELETE, PATCH)
        for path, methods in spec['paths'].items():
            operation_count += len(methods)
        
        category = json_file.stem.replace('native-', '')
        categories[category] = {
            'paths': path_count,
            'operations': operation_count
        }
        
        total_paths += path_count
        total_operations += operation_count
        
        print(f"{category:20s}: {path_count:4d} paths, {operation_count:5d} operations")

print("-"*70)
print(f"{'TOTAL':20s}: {total_paths:4d} paths, {total_operations:5d} operations")

# Count XPaths in YANG tree
print("\n" + "="*70)
print("YANG Model XPath Analysis:")
print("-"*70)

tree_file = Path("docs/native-yang-tree-depth6.txt")
if tree_file.exists():
    try:
        with open(tree_file, 'r', encoding='utf-8', errors='ignore') as f:
            tree_lines = f.readlines()
    except:
        with open(tree_file, 'r', encoding='latin-1') as f:
            tree_lines = f.readlines()
    
    # Count different types of nodes
    containers = sum(1 for line in tree_lines if '+--rw' in line and 'container' not in line and '{' not in line)
    lists = sum(1 for line in tree_lines if '+--rw' in line and '*' in line)
    leaves = sum(1 for line in tree_lines if '+--rw' in line and '?' in line)
    
    total_tree_lines = len(tree_lines)
    
    print(f"Tree file (depth 6): {total_tree_lines:,} lines")
    print(f"Estimated containers: ~{containers:,}")
    print(f"Estimated lists: ~{lists:,}")
    print(f"Estimated leaves: ~{leaves:,}")

print("\n" + "="*70)
print("Coverage Summary:")
print("-"*70)
print(f"Generated API Paths:     {total_paths:,}")
print(f"Generated Operations:    {total_operations:,}")
print(f"YANG Tree Lines (d=6):   {total_tree_lines:,}")
print(f"Estimated Coverage:      {(total_paths/total_tree_lines*100):.1f}%")
print("="*70)
