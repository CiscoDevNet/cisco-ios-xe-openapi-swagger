import json
from collections import Counter

spec = json.load(open('swagger-native-config-model/api/native-system.json'))
paths = list(spec['paths'].keys())

# Extract top-level containers after /native/
containers = []
for path in paths:
    parts = path.split('/')[3:]  # Skip /data/Cisco-IOS-XE-native:native
    if parts:
        container = parts[0].split('=')[0].split('{')[0]
        containers.append(container)

counter = Counter(containers)
print(f'Total system paths: {len(paths)}')
print(f'\nTop 40 containers in system category:')
for name, count in counter.most_common(40):
    print(f'  {name:30} {count:4} paths')

# Suggest new categories
print('\n' + '='*70)
print('RECOMMENDED SPLIT:')
print('='*70)

aaa_keywords = ['aaa', 'radius', 'tacacs', 'authentication']
logging_keywords = ['logging', 'archive']
management_keywords = ['snmp', 'ntp', 'domain', 'hostname', 'username', 'enable', 'password']
infra_keywords = ['banner', 'clock', 'service', 'boot', 'license', 'parser']
network_keywords = ['ip', 'ipv6', 'cdp', 'lldp', 'arp']

categories = {
    'AAA & Auth': aaa_keywords,
    'Logging & Archive': logging_keywords,
    'Management': management_keywords,
    'Infrastructure': infra_keywords,
    'Network Basics': network_keywords
}

for cat, keywords in categories.items():
    count = sum(counter[c] for c in counter if any(k in c.lower() for k in keywords))
    print(f'{cat:25} ~{count:4} paths')
