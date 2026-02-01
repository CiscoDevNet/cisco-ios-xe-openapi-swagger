import sys
from pathlib import Path
sys.path.append('generators')
from generate_native_openapi_v2 import NativeToOpenAPI

yang_dir = Path('references/17181-YANG-modules')
output_dir = Path('swagger-native-config-model/api')
gen = NativeToOpenAPI(yang_dir, output_dir)

test_paths = [
    'native/redundancy',
    'native/redundancy/application',
    'native/monitor/session',
    'native/hw-module',
    'native/switch',
    'native/mac',
    'native/session'
]

print("Testing categorization:")
for path in test_paths:
    category = gen.categorize_path(path)
    print(f"  {path:40} -> {category}")

print("\nPlatform keywords:", gen.category_keywords['platform'][:5])
print("\nMonitor keywords:", gen.category_keywords['monitor'])
