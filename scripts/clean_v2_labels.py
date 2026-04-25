#!/usr/bin/env python3
"""Remove v2/v1 labels from all index-v2.html pages to make them the default."""
import re
from pathlib import Path

base = Path(__file__).parent.parent

models = [
    ('swagger-oper-model', 'Operational'),
    ('swagger-rpc-model', 'RPC'),
    ('swagger-cfg-model', 'Configuration'),
    ('swagger-native-config-model', 'Native Config'),
    ('swagger-openconfig-model', 'OpenConfig'),
    ('swagger-ietf-model', 'IETF'),
    ('swagger-mib-model', 'MIB'),
    ('swagger-events-model', 'Events'),
    ('swagger-other-model', 'Other'),
]

def main():
    for folder, label in models:
        path = base / folder / 'index-v2.html'
        if not path.exists():
            print(f'{folder} - NOT FOUND')
            continue

        content = path.read_text(encoding='utf-8')
        original = content

        # 1. Clean title: remove (v2 Deep Paths) suffix
        content = re.sub(
            r'<title>(.*?) \(v2 Deep Paths\)</title>',
            r'<title>\1</title>',
            content
        )

        # 2. Remove <span class="badge">v2 — Deep Paths</span> from h1
        content = re.sub(
            r'\s*<span class="badge">v2 — Deep Paths</span>',
            '',
            content
        )

        # 3. Clean nav bar labels: "Oper (v2)" -> "Oper", "Config (v2)" -> "Config" etc.
        content = re.sub(r'>Oper \(v2\)<', '>Operational<', content)
        content = re.sub(r'>Config \(v2\)<', '>Config<', content)
        content = re.sub(r'>Native \(v2\)<', '>Native<', content)
        content = re.sub(r'>OpenConfig \(v2\)<', '>OpenConfig<', content)
        content = re.sub(r'>RPC \(v2\)<', '>RPC<', content)
        content = re.sub(r'>IETF \(v2\)<', '>IETF<', content)
        content = re.sub(r'>MIB \(v2\)<', '>MIB<', content)
        content = re.sub(r'>Events \(v2\)<', '>Events<', content)
        content = re.sub(r'>Other \(v2\)<', '>Other<', content)

        # 4. Clean sidebar header: "Operational Specs (v2)" -> "Operational Specs"
        content = re.sub(r'Specs \(v2\)', 'Specs', content)

        # 5. Clean welcome content: "— v2 Deep Paths" -> ""
        content = re.sub(r' — v2 Deep Paths', '', content)

        if content != original:
            path.write_text(content, encoding='utf-8')
            changes = len(original) - len(content)
            print(f'{folder} - cleaned ({changes} chars removed)')
        else:
            print(f'{folder} - no changes needed')


if __name__ == '__main__':
    main()
