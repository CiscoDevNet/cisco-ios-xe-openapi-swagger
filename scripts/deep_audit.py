#!/usr/bin/env python3
"""Deep audit of example values across all 128 event specs for quality issues."""
import json, os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(BASE, "swagger-events-model", "api")

def audit():
    fs = sorted([f for f in os.listdir(API_DIR) if f.endswith('.json') and f != 'manifest.json'])
    issues = []

    for fname in fs:
        with open(os.path.join(API_DIR, fname), 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        schemas = data.get('components', {}).get('schemas', {})
        for sname, sval in schemas.items():
            ex = sval.get('example', {})
            walk(ex, '', fname, sname, issues)

        # Also check path-level examples
        for p, pv in data.get('paths', {}).items():
            for method, mv in pv.items():
                if not isinstance(mv, dict):
                    continue
                for code, rv in mv.get('responses', {}).items():
                    content = rv.get('content', {})
                    for ct, cv in content.items():
                        ex = cv.get('example', {})
                        if ex:
                            walk(ex, '', fname, f"path:{p}", issues)

    print(f"Issues found: {len(issues)}")
    for item in issues:
        print(f"  [{item[4]}] {item[0]} -> {item[1]} -> {item[2]} = \"{item[3]}\"")
    return issues

def walk(obj, path, fname, sname, issues):
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, f"{path}.{k}" if path else k, fname, sname, issues)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, f"{path}[{i}]", fname, sname, issues)
    elif isinstance(obj, str):
        leaf = path.rsplit('.', 1)[-1] if '.' in path else path
        leaf = re.sub(r'\[\d+\]$', '', leaf)  # strip array index
        val = obj

        # 1. Self-referential: value == leaf name
        if val == leaf or val == leaf.replace('-', '_'):
            issues.append((fname, sname, leaf, val, 'self-ref'))

        # 2. IP address in a MAC field
        if 'mac' in leaf.lower() and re.match(r'^\d+\.\d+\.\d+\.\d+$', val):
            issues.append((fname, sname, leaf, val, 'IP-in-mac'))

        # 3. MAC address in a non-MAC addr field
        if 'addr' in leaf.lower() and 'mac' not in leaf.lower() and re.match(r'^[0-9a-f]{2}:[0-9a-f]{2}:', val, re.I):
            issues.append((fname, sname, leaf, val, 'MAC-in-addr'))

        # 4. ifOperStatus='up' in a linkDown trap
        if 'down' in sname.lower() and 'oper' in leaf.lower() and 'status' in leaf.lower() and val == 'up':
            issues.append((fname, sname, leaf, val, 'oper-up-in-down'))

        # 5. Wrong domain value (link-flap in license context)
        if val == 'link-flap-detected' and ('license' in fname.lower() or 'license' in sname.lower()):
            issues.append((fname, sname, leaf, val, 'wrong-domain'))

        # 6. Known bad/truncated values
        if val in ('event-type', 'ospfv3-address', 'wsa-clien', 'wsa-client-event'):            issues.append((fname, sname, leaf, val, 'bad-enum-value'))

        # 7. "reporting-ap" as a value (self-referential but also generic)
        if val == 'reporting-ap' and leaf == 'reporting-ap':
            issues.append((fname, sname, leaf, val, 'self-ref'))

        # 8. Generic patterns still present
        if val in ('value', 'string', 'name', 'type', 'status', 'state', 'mode', 'address'):
            issues.append((fname, sname, leaf, val, 'too-generic'))

        # 9. Leaf-value pattern: common pattern where value looks like a field name
        if re.match(r'^[a-z]+-[a-z]+-[a-z]+$', val) and val not in (
            'link-flap-detected', 'oper-status-change', 'policy-map-1',
            'date-time', 'point-to-point', 'non-broadcast',
        ) and not re.match(r'^\d', val):
            # Could be a generic compound name
            pass  # Don't flag, too many false positives

if __name__ == '__main__':
    audit()
