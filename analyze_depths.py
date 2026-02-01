import json
import os
from collections import Counter

all_paths = []
depths = []

for filename in os.listdir('swagger-native-config-model/api'):
    if not filename.endswith('.json') or filename == 'manifest.json':
        continue
    
    filepath = f'swagger-native-config-model/api/{filename}'
    with open(filepath, 'r') as f:
        spec = json.load(f)
    
    for path in spec['paths'].keys():
        # Count depth (path segments after /data/Cisco-IOS-XE-native:native)
        depth = path.count('/') - 2
        depths.append(depth)
        all_paths.append((depth, path))

print(f'Total paths: {len(depths)}')
print(f'Max depth: {max(depths)}')
print(f'Min depth: {min(depths)}')
print(f'Average depth: {sum(depths)/len(depths):.2f}')

print(f'\nDepth distribution:')
counter = Counter(depths)
for d in sorted(counter.keys()):
    percentage = (counter[d] / len(depths)) * 100
    print(f'  Depth {d}: {counter[d]:4} paths ({percentage:.1f}%)')

print(f'\nSample deepest paths (top 15):')
deep = sorted(all_paths, key=lambda x: x[0], reverse=True)[:15]
for d, path in deep:
    print(f'  Depth {d}: {path}')

print(f'\nPaths by depth level:')
for depth_limit in [3, 4, 5, 6, 7, 8, 10]:
    count = sum(1 for d in depths if d <= depth_limit)
    percentage = (count / len(depths)) * 100
    print(f'  Depth <= {depth_limit}: {count:4} paths ({percentage:.1f}%)')
