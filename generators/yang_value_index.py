#!/usr/bin/env python3
"""
Lightweight YANG source scanner to extract leaf defaults and first enum values
for use as realistic example values in generated OpenAPI specs.

Parses YANG modules with simple regex (no full pyang dependency) and produces a
flat lookup keyed by leaf name. Same-name collisions across containers prefer
the first occurrence with a default; otherwise first occurrence with enums.

Public API:
    build_index(yang_dir: Path) -> dict[str, dict]
        Returns: { leaf_name: { 'default': str|None, 'enum_first': str|None,
                                'enums': list[str], 'type': str|None } }

This is best-effort. It is intentionally name-keyed (not path-keyed) to match
the existing example-value heuristic in the from_tree generators.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

# Match `leaf <name> {` ... contents ... `}` (non-greedy, single leaf body)
_LEAF_RE = re.compile(r'\bleaf\s+([A-Za-z0-9_\-]+)\s*\{', re.MULTILINE)
_TYPEDEF_RE = re.compile(r'\btypedef\s+([A-Za-z0-9_\-]+)\s*\{', re.MULTILINE)
_DEFAULT_RE = re.compile(r'\bdefault\s+"?([^";]+?)"?\s*;')
_TYPE_RE = re.compile(r'\btype\s+([A-Za-z0-9_:\-]+)')
_ENUM_RE = re.compile(r'\benum\s+"?([A-Za-z0-9_\-\.\+ ]+?)"?\s*[;{]')


def _find_matching_brace(text: str, open_idx: int) -> int:
    depth = 0
    i = open_idx
    n = len(text)
    while i < n:
        c = text[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _scan_body(body: str) -> Dict[str, Optional[object]]:
    """Extract default, type, and enum list from a leaf/typedef body."""
    default = None
    m = _DEFAULT_RE.search(body)
    if m:
        default = m.group(1).strip()

    yang_type = None
    tm = _TYPE_RE.search(body)
    if tm:
        yang_type = tm.group(1)

    enums: List[str] = []
    for em in _ENUM_RE.finditer(body):
        enums.append(em.group(1).strip())

    return {
        'default': default,
        'type': yang_type,
        'enums': enums,
        'enum_first': enums[0] if enums else None,
    }


def _scan_module(text: str, leaves: Dict[str, dict], typedefs: Dict[str, dict]) -> None:
    # Typedefs first so leaves can resolve symbolic types
    for tm in _TYPEDEF_RE.finditer(text):
        name = tm.group(1)
        brace = text.find('{', tm.end() - 1)
        if brace < 0:
            continue
        close = _find_matching_brace(text, brace)
        if close < 0:
            continue
        body = text[brace + 1:close]
        info = _scan_body(body)
        # Keep first occurrence with usable info
        prev = typedefs.get(name)
        if not prev or (not prev.get('default') and info.get('default')):
            typedefs[name] = info

    for lm in _LEAF_RE.finditer(text):
        name = lm.group(1)
        brace = text.find('{', lm.end() - 1)
        if brace < 0:
            continue
        close = _find_matching_brace(text, brace)
        if close < 0:
            continue
        body = text[brace + 1:close]
        info = _scan_body(body)
        # Accumulate observations per leaf name so we can detect conflicts
        bucket = leaves.setdefault(name, {
            'defaults': set(), 'enum_firsts': set(), 'types': set()
        })
        if info.get('default') is not None:
            bucket['defaults'].add(info['default'])
        if info.get('enum_first') is not None:
            bucket['enum_firsts'].add(info['enum_first'])
        if info.get('type'):
            bucket['types'].add(info['type'])


def build_index(yang_dir: Path, module_glob: str = '*.yang') -> Dict[str, dict]:
    """Build a {leaf_name -> info} index from YANG sources in yang_dir.

    Resolves leaves whose type is a local typedef to inherit the typedef's
    default/enum_first values.
    """
    leaves: Dict[str, dict] = {}
    typedefs: Dict[str, dict] = {}

    for path in sorted(Path(yang_dir).glob(module_glob)):
        try:
            text = path.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        _scan_module(text, leaves, typedefs)

    # Resolve buckets into a single info per name. Only return a value when
    # the YANG sources agree (unanimous default or unanimous first enum) so
    # we never put a wrong default into an unrelated leaf's example body.
    resolved: Dict[str, dict] = {}
    for name, bucket in leaves.items():
        if isinstance(bucket, dict) and 'defaults' in bucket:
            defaults = bucket['defaults']
            enums = bucket['enum_firsts']
            types = bucket['types']
            info = {
                'default': next(iter(defaults)) if len(defaults) == 1 else None,
                'enum_first': next(iter(enums)) if len(enums) == 1 else None,
                'enums': list(enums),
                'type': next(iter(types)) if len(types) == 1 else None,
            }
            resolved[name] = info
        else:
            resolved[name] = bucket  # already-resolved (from earlier code paths)
    leaves = resolved

    # Resolve leaves whose type is a typedef and whose own scan came back empty
    for name, info in leaves.items():
        yt = info.get('type') or ''
        # Strip module prefix (e.g. ios-types:foo -> foo)
        base = yt.split(':')[-1] if ':' in yt else yt
        if base in typedefs:
            td = typedefs[base]
            if not info.get('default') and td.get('default'):
                info['default'] = td['default']
            if not info.get('enum_first') and td.get('enum_first'):
                info['enum_first'] = td['enum_first']
                info['enums'] = td.get('enums') or []

    return leaves


def example_from_index(index: Dict[str, dict], leaf_name: str) -> Optional[object]:
    """Return a realistic example value for a leaf, or None if unknown.

    Preference order: YANG default -> first enum value -> None.
    Booleans and numerics are returned in their native JSON type when possible.
    """
    info = index.get(leaf_name)
    if not info:
        return None
    val = info.get('default') or info.get('enum_first')
    if val is None:
        return None
    if val in ('true', 'false'):
        return val == 'true'
    try:
        if val.lstrip('-').isdigit():
            return int(val)
    except AttributeError:
        pass
    return val


# ---------------------------------------------------------------------------
# Module-level lazy singleton (used by the from_tree generators)
# ---------------------------------------------------------------------------

_DEFAULT_YANG_DIR = Path(__file__).resolve().parent.parent / 'references' / '17181-YANG-modules'
_INDEX_CACHE: Optional[Dict[str, dict]] = None


def get_index(yang_dir: Optional[Path] = None) -> Dict[str, dict]:
    global _INDEX_CACHE
    if _INDEX_CACHE is None:
        d = yang_dir or _DEFAULT_YANG_DIR
        _INDEX_CACHE = build_index(d) if d.exists() else {}
    return _INDEX_CACHE


def lookup_example(leaf_name: str) -> Optional[object]:
    """Convenience: look up a realistic example value for a leaf by name."""
    return example_from_index(get_index(), leaf_name)


if __name__ == '__main__':
    import sys
    import json
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('references/17181-YANG-modules')
    idx = build_index(d)
    print(f'Indexed {len(idx)} leaves from {d}')
    with_default = sum(1 for v in idx.values() if v.get('default'))
    with_enum = sum(1 for v in idx.values() if v.get('enum_first'))
    print(f'  with default: {with_default}')
    print(f'  with enum:    {with_enum}')
    # Print a few samples
    samples = ['hostname', 'mtu', 'shutdown', 'mode', 'speed', 'duplex', 'enable']
    for s in samples:
        if s in idx:
            print(f'  {s}: {json.dumps(idx[s])}')
