import json
import os

total = 0
category_counts = {}

for filename in os.listdir('swagger-native-config-model/api'):
    if not filename.endswith('.json') or filename == 'manifest.json':
        continue
    
    filepath = f'swagger-native-config-model/api/{filename}'
    with open(filepath, 'r') as f:
        spec = json.load(f)
    
    count = len(spec['paths'])
    category_counts[filename] = count
    total += count
    print(f"{filename:30} {count:5} paths")

print(f"\n{'TOTAL':30} {total:5} paths")
print(f"\nComparison:")
print(f"  Phase 1 (top-level only): 242 paths")
print(f"  Phase 3 (recursive):     {total} paths")
print(f"  Increase:                {total - 242} paths ({((total - 242) / 242 * 100):.1f}% more)")
