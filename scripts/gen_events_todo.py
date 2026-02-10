"""Generate TODO_EVENTS.md accountability tracker."""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE, 'scripts', 'events_audit.json')) as f:
    results = json.load(f)

lines = []
lines.append('# Event Notifications Enhancement TODO')
lines.append('')
lines.append('**Goal**: Add YANG-derived schemas with typed properties and realistic example values')
lines.append('to all 128 event notification specs in `swagger-events-model/api/`.')
lines.append('')
lines.append('## Summary')
lines.append('| Metric | Before | Target |')
lines.append('|--------|--------|--------|')
lines.append('| Specs with schemas | 5/128 | 128/128 |')
lines.append('| Specs with examples | 0/128 | 128/128 |')
lines.append('| Total notification schemas | ~9 | ~492 |')
lines.append('')
lines.append('## Legend')
lines.append('- [ ] Not started')
lines.append('- [x] Complete')
lines.append('')

# Group them
xe = []
mib = []
other = []
for r in results:
    fn = r['file']
    if fn.startswith('Cisco-IOS-XE-'):
        xe.append(r)
    elif fn[0].isupper() and '-MIB' in fn:
        mib.append(r)
    else:
        other.append(r)

for label, group in [
    ('XE Event Notifications (39)', xe),
    ('MIB SNMP Trap Notifications (80)', mib),
    ('Other Event Notifications (9)', other),
]:
    lines.append(f'## {label}')
    lines.append('')
    lines.append('| # | File | Paths | Notifs | Has Schema | Has Examples | Status |')
    lines.append('|---|------|-------|--------|------------|--------------|--------|')
    for i, r in enumerate(sorted(group, key=lambda x: x['file']), 1):
        fn = r['file']
        sch = 'Yes' if r['schemas'] > 0 else 'No'
        ex = 'Yes' if r['has_examples'] or r['has_inline_examples'] else 'No'
        notif_list = r['notif_names']
        if len(notif_list) <= 3:
            notifs = ', '.join(notif_list)
        else:
            notifs = ', '.join(notif_list[:3]) + f' +{len(notif_list)-3} more'
        lines.append(f'| {i} | {fn} | {r["paths"]} | {r["notif_count"]} ({notifs}) | {sch} | {ex} | [ ] |')
    lines.append('')

with open(os.path.join(BASE, 'TODO_EVENTS.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Created TODO_EVENTS.md with {len(lines)} lines')
