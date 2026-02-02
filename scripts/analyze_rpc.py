#!/usr/bin/env python3
"""Analyze RPC model structure"""

import json
from pathlib import Path

api_dir = Path('swagger-rpc-model/api')
files = sorted(api_dir.glob('*.json'))

print("\n" + "="*70)
print("PHASE 6: RPC MODEL ANALYSIS")
print("="*70)
print(f"\nTotal Files: {len(files)}\n")

data = []
total_paths = 0

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        spec = json.load(file)
    
    path_count = len(spec.get('paths', {}))
    total_paths += path_count
    
    data.append({
        'file': f.name,
        'paths': path_count,
        'size_kb': f.stat().st_size / 1024
    })

data.sort(key=lambda x: x['paths'], reverse=True)

print("Top 20 Files by Path Count:\n")
for d in data[:20]:
    print(f"  {d['file']:<50} {d['paths']:>3} paths  {d['size_kb']:>6.1f} KB")

print(f"\n{'='*70}")
print(f"Total Paths: {total_paths}")
print(f"Avg Paths/File: {total_paths/len(files):.1f}")
print("="*70)
