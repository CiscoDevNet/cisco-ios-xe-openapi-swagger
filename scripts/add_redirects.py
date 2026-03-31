#!/usr/bin/env python3
"""Add redirects from v1 index.html to index-v2.html for all model pages."""
import os
from pathlib import Path

base = Path(__file__).parent.parent

models = [
    'swagger-oper-model', 'swagger-rpc-model', 'swagger-cfg-model',
    'swagger-native-config-model', 'swagger-openconfig-model',
    'swagger-ietf-model', 'swagger-mib-model', 'swagger-events-model',
    'swagger-other-model'
]

redirect_snippet = (
    '    <meta http-equiv="refresh" content="0;url=index-v2.html">\n'
    "    <script>var t='index-v2.html';if(location.hash)t+=location.hash;"
    "if(location.search)t+=location.search;window.location.replace(t);</script>"
)

for m in models:
    path = base / m / 'index.html'
    if not path.exists():
        print(f'{m} - NOT FOUND')
        continue
    content = path.read_text(encoding='utf-8')
    if 'url=index-v2.html' in content:
        print(f'{m} - already done')
        continue
    content = content.replace('<head>', '<head>\n' + redirect_snippet, 1)
    path.write_text(content, encoding='utf-8')
    print(f'{m} - redirect added')
