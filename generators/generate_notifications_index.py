#!/usr/bin/env python3
"""Build a cross-model YANG **notification** capability index for a release.

The hub's purpose is to document the *full* capability surface of the IOS-XE
YANG models. YANG ``notification`` nodes are a first-class construct that the
per-model OpenAPI generators do not surface (they only walk the ``data:``
section of each tree), so notifications defined by MIB translations, IETF
modules, and a handful of native modules were previously invisible even though
the resolved trees describe them.

This generator scans **every** resolved YANG tree in a release, extracts the
``notifications:`` section of each module, and emits a single
``notifications.json`` capability artifact:

    releases/<ver>/notifications.json   (+ a copy at repo root for the default
                                          release, mirroring the other indexes)

It is intentionally *additive* and read-only with respect to the existing
per-model specs — it does not modify or regenerate any ``swagger-*-model``
spec, so there is no risk of churning the 90+ committed module specs. The UI
(notifications catalog + per-module section) consumes this index directly.

Each notification is tagged with its delivery transport and an honest
``restconf_consumable`` flag, because many of these (SNMP MIB traps in
particular) cannot actually be subscribed to over RESTCONF — and that is fine:
the goal is to *catalog* the capability, not imply it is consumable.

Run:

    python -X utf8 generators/generate_notifications_index.py --version 26.1.1
    python -X utf8 generators/generate_notifications_index.py --all
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent

# Reuse the shared YANG value engine for realistic leaf example values
# (YANG default -> first enum -> None), keyed by leaf name.
sys.path.insert(0, str(ROOT / 'generators'))
try:
    from yang_value_index import lookup_example as _yang_lookup_example
except Exception:  # pragma: no cover - engine is best-effort
    def _yang_lookup_example(_name):
        return None

# Category dir -> (short type, display label). Mirrors generate_search_index.py.
CATEGORY_LABELS = {
    'swagger-oper-model': ('operational', 'Operational Data'),
    'swagger-cfg-model': ('configuration', 'Configuration'),
    'swagger-native-config-model': ('native', 'Native Configuration'),
    'swagger-openconfig-model': ('openconfig', 'OpenConfig'),
    'swagger-ietf-model': ('ietf', 'IETF Standards'),
    'swagger-mib-model': ('mib', 'MIB Translations'),
    'swagger-rpc-model': ('rpc', 'RPC Operations'),
    'swagger-events-model': ('events', 'Event Notifications'),
    'swagger-other-model': ('other', 'Other Models'),
}

# IETF modules whose notifications are NETCONF-stream rather than YANG-Push.
_NETCONF_STREAM_MODULES = {
    'ietf-netconf-notifications',
    'ietf-event-notifications',
    'ietf-restconf-monitoring',
}

# How each transport is actually consumed on a device. Deliberately honest:
# none of these are dynamic-subscription-over-RESTCONF, which IOS-XE does not
# usefully support — the catalog documents the real mechanism instead.
_CONSUMPTION = {
    'yang-push': (
        'Subscribe via NETCONF <establish-subscription> (RFC 8639/8641) or '
        'configure gRPC dial-out telemetry; events arrive as YANG-Push '
        'notifications. Not retrievable with a RESTCONF GET.'
    ),
    'snmp-trap': (
        'Delivered as an SNMP notification (trap/inform). Enable the '
        'corresponding *NotifEnable object and configure an snmp-server host. '
        'Not available over RESTCONF/NETCONF.'
    ),
    'netconf-stream': (
        'Subscribe over NETCONF (create-subscription / establish-subscription) '
        'to the relevant event stream. Not retrievable with a RESTCONF GET.'
    ),
}



def _release_dirs(version: str):
    base = ROOT / 'releases' / version
    return base, base / 'yang-trees'


def build_category_map(release_base: Path) -> Dict[str, str]:
    """Map module name -> swagger category dir by scanning each model's api dir.

    A module is attributed to the first category whose ``api/<module>.json``
    exists. This is the same notion of "category" the search index uses.
    """
    cat_map: Dict[str, str] = {}
    for cat_dir in CATEGORY_LABELS:
        api_dir = release_base / cat_dir / 'api'
        if not api_dir.is_dir():
            continue
        for spec in api_dir.glob('*.json'):
            if spec.name in ('manifest.json', 'all-events.json', '_paths_index.json'):
                continue
            cat_map.setdefault(spec.stem, cat_dir)
    return cat_map


def _classify(module: str, category_dir: Optional[str]):
    """Return (transport, restconf_consumable) for a module's notifications."""
    if category_dir == 'swagger-mib-model':
        # SNMP NOTIFICATION-TYPE traps — delivered over SNMP, not RESTCONF.
        return 'snmp-trap', False
    if module in _NETCONF_STREAM_MODULES or module.startswith('ietf-'):
        return 'netconf-stream', False
    # Native YANG-Push notification streams (events / oper / other native).
    return 'yang-push', True


# ---------------------------------------------------------------------------
# Realistic example values (RFC 7951 JSON payloads).
# ---------------------------------------------------------------------------

# Name-substring heuristics for leafs the YANG value engine doesn't cover.
# Checked in order; first hit wins. Keeps examples aligned to what a real
# notification payload looks like rather than the literal string "example".
_NAME_HINTS = [
    (re.compile(r'(address[-_ ]?family|^af$|af[-_]?type)', re.I), 'ipv4'),
    (re.compile(r'(^|[-_])(oper)?state$|status$|state$', re.I), 'up'),
    (re.compile(r'reason', re.I), 'none'),
    (re.compile(r'(host[-_]?name)', re.I), 'router1'),
    (re.compile(r'(vrf|vpn)[-_]?name|^vrf', re.I), 'default'),
    (re.compile(r'(if[-_]?name|interface)', re.I), 'GigabitEthernet1'),
    (re.compile(r'(severity|level)', re.I), 'major'),
    (re.compile(r'(index|number|num|count|id$|ifindex)', re.I), 1),
    (re.compile(r'(time|timestamp)', re.I), '2026-06-18T15:30:00.000Z'),
    (re.compile(r'(addr|address|ip)$|ipv4|ipv6', re.I), '192.0.2.1'),
    (re.compile(r'version', re.I), 'ipv4'),
    (re.compile(r'class', re.I), 'module'),
    (re.compile(r'name$', re.I), 'example-name'),
    (re.compile(r'type$', re.I), 'example-type'),
]

# Concrete (non-string) type defaults applied before name heuristics. 'string'
# is deliberately excluded so descriptive leaf names get a realistic value from
# the heuristics instead of the bare literal "example".
_TYPE_DEFAULTS = {
    'boolean': True, 'empty': None,
    'uint8': 1, 'uint16': 1, 'uint32': 1, 'uint64': 1,
    'int8': 1, 'int16': 1, 'int32': 1, 'int64': 1,
    'counter32': 0, 'counter64': 0, 'gauge32': 0, 'gauge64': 0,
    'decimal64': 1.0, 'timestamp': '2026-06-18T15:30:00.000Z',
    'timeticks': 0,
}


def _leaf_basename(obj: dict) -> str:
    """For a leafref, the meaningful name is the target's last path segment
    (e.g. cefPeerOperState), which the value engine / hints understand better
    than a generic 'object-1' wrapper."""
    if obj.get('target'):
        tail = obj['target'].rstrip('/').split('/')[-1]
        return tail.split(':')[-1] or obj.get('name', '')
    return obj.get('name', '')


def example_value(obj: dict):
    """Best-effort realistic value for one carried notification object."""
    name = _leaf_basename(obj)
    # 1. YANG default / first-enum from the source modules.
    v = _yang_lookup_example(name)
    if v is not None:
        return v
    # 2. Concrete (non-string) type default.
    ytype = (obj.get('type') or '').split(':')[-1].lower()
    if ytype in _TYPE_DEFAULTS:
        return _TYPE_DEFAULTS[ytype]
    # 3. Name-substring heuristics (covers most leafref-carried objects and
    #    descriptive string leafs).
    for rx, val in _NAME_HINTS:
        if rx.search(name):
            return val
    return 'example'


def build_example(module: str, notif: dict) -> dict:
    """Build an RFC 7951 namespace-qualified example payload for a notification:

        { "<module>:<notification>": { "<obj>": <value>, ... } }
    """
    body = {}
    for obj in notif.get('objects', []):
        body[obj['name']] = example_value(obj)
    return {module + ':' + notif['name']: body}


# ---------------------------------------------------------------------------
# Lightweight tree parser focused on the notifications: section.
# ---------------------------------------------------------------------------

_MODULE_RE = re.compile(r'module:\s+(\S+)')
_NODE_RE = re.compile(r'([+o]-+)(rw|ro|x|n|w|mp)\s+(\S+)(.*)')


def _extract_tree_text(html_path: Path) -> Optional[str]:
    content = html_path.read_text(encoding='utf-8', errors='replace')
    pre_matches = re.findall(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
    if not pre_matches:
        return None
    for pre in reversed(pre_matches):
        cleaned = re.sub(r'<[^>]+>', '', pre)
        if re.search(r'[+o]-+(rw|ro|x|n)\s', cleaned):
            return (cleaned.replace('&amp;', '&')
                           .replace('&lt;', '<')
                           .replace('&gt;', '>'))
    return None


def extract_notifications(html_path: Path) -> List[dict]:
    """Return a list of {name, objects:[{name,type,target}]} for every
    notification node defined in the module's ``notifications:`` section."""
    tree = _extract_tree_text(html_path)
    if not tree:
        return []
    lines = tree.split('\n')

    # Locate the notifications: section boundaries (column 0 keyword lines).
    notif_start = None
    for i, line in enumerate(lines):
        if line.strip() == 'notifications:':
            notif_start = i + 1
            break
    if notif_start is None:
        return []
    notif_end = len(lines)
    for i in range(notif_start, len(lines)):
        if lines[i].strip() in ('rpcs:', 'data:'):
            notif_end = i
            break

    section = lines[notif_start:notif_end]
    if not section:
        return []

    # The top-level notification nodes are the '+---n' markers at the minimum
    # indentation column within the section.
    parsed = []  # (col, kind, name, rest)
    for line in section:
        m = _NODE_RE.search(line)
        if not m:
            continue
        parsed.append((m.start(), m.group(2), m.group(3), m.group(4).strip()))
    if not parsed:
        return []
    min_col = min(col for col, *_ in parsed)

    notifications: List[dict] = []
    current: Optional[dict] = None
    for col, kind, raw, rest in parsed:
        name = raw.rstrip('?').rstrip('!').rstrip('*')
        if col == min_col and kind == 'n':
            current = {'name': name, 'objects': []}
            notifications.append(current)
            continue
        if current is None:
            continue
        # A carried data leaf inside the notification. Skip pure container
        # wrappers (e.g. MIB "object-1"); record leafs and their leafref target.
        is_leaf = bool(rest) and not rest.startswith('[') and not rest.startswith('{')
        if not is_leaf:
            continue
        target = None
        ytype = rest.split()[0] if rest.split() else ''
        arrow = re.search(r'->\s*(\S+)', rest)
        if arrow:
            ytype = 'leafref'
            target = arrow.group(1)
        current['objects'].append({
            'name': name,
            'type': ytype,
            **({'target': target} if target else {}),
        })
    # Keep only notifications that actually carry a name.
    return [n for n in notifications if n['name']]


def build_index(version: str) -> dict:
    release_base, tree_dir = _release_dirs(version)
    if not tree_dir.is_dir():
        raise SystemExit(f"tree dir not found: {tree_dir}")

    cat_map = build_category_map(release_base)

    modules_out: List[dict] = []
    by_transport: Dict[str, int] = {}
    by_category: Dict[str, int] = {}
    total_notifs = 0

    for tree_file in sorted(tree_dir.glob('*.html')):
        if tree_file.name in ('index.html', 'mib-trees-index.html'):
            continue
        notifs = extract_notifications(tree_file)
        if not notifs:
            continue
        module = tree_file.stem
        category_dir = cat_map.get(module)
        short_cat, display_cat = CATEGORY_LABELS.get(
            category_dir, ('unknown', 'Uncategorized'))
        transport, consumable = _classify(module, category_dir)

        # Attach a realistic RFC 7951 example payload to each notification.
        for n in notifs:
            n['example'] = build_example(module, n)

        entry = {
            'module': module,
            'category': short_cat,
            'category_dir': category_dir,
            'display_category': display_cat,
            'transport': transport,
            'restconf_consumable': consumable,
            'consumption': _CONSUMPTION.get(transport, ''),
            'notification_count': len(notifs),
            'tree_url': f"yang-trees/{module}.html",
            'notifications': notifs,
        }
        if category_dir:
            entry['spec_url'] = f"{category_dir}/index.html#spec={module}"
        modules_out.append(entry)

        total_notifs += len(notifs)
        by_transport[transport] = by_transport.get(transport, 0) + len(notifs)
        by_category[short_cat] = by_category.get(short_cat, 0) + len(notifs)

    modules_out.sort(key=lambda e: (-e['notification_count'], e['module'].lower()))

    return {
        'version': version,
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'generator': 'generators/generate_notifications_index.py',
        'totals': {
            'modules_with_notifications': len(modules_out),
            'total_notifications': total_notifs,
            'by_transport': dict(sorted(by_transport.items())),
            'by_category': dict(sorted(by_category.items())),
        },
        'modules': modules_out,
    }


def write_index(version: str, default_version: Optional[str] = None) -> dict:
    index = build_index(version)
    release_base, _ = _release_dirs(version)
    out_path = release_base / 'notifications.json'
    out_path.write_text(json.dumps(index, indent=2) + '\n', encoding='utf-8')
    print(f"[notifications] {version}: "
          f"{index['totals']['modules_with_notifications']} modules, "
          f"{index['totals']['total_notifications']} notifications -> {out_path}")

    # Mirror to repo root for the default release (other indexes do this so
    # standalone pages resolve without a release path).
    if default_version and version == default_version:
        root_copy = ROOT / 'notifications.json'
        root_copy.write_text(json.dumps(index, indent=2) + '\n', encoding='utf-8')
        print(f"[notifications] copied default release index -> {root_copy}")
    return index


def _default_version() -> Optional[str]:
    idx = ROOT / 'releases' / 'index.json'
    if idx.is_file():
        try:
            return json.loads(idx.read_text(encoding='utf-8')).get('default')
        except Exception:
            return None
    return None


def _all_versions() -> List[str]:
    rel = ROOT / 'releases'
    return sorted(d.name for d in rel.iterdir()
                  if d.is_dir() and (d / 'yang-trees').is_dir())


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--version', help='release version, e.g. 26.1.1')
    ap.add_argument('--all', action='store_true',
                    help='process every release under releases/')
    args = ap.parse_args()

    default_ver = _default_version()
    if args.all:
        versions = _all_versions()
    elif args.version:
        versions = [args.version]
    else:
        versions = [default_ver] if default_ver else []
        if not versions:
            ap.error('specify --version or --all (no default release found)')

    for ver in versions:
        write_index(ver, default_ver)
