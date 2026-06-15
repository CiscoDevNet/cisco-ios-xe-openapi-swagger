"""Shared helpers for the v2 YANG-to-OpenAPI generators.

Two problems used to bite every generator that parses YANG with regex:

1) ``include <submodule>;`` was not resolved. Parent modules declare RPCs
   and containers that ``uses`` groupings defined in submodules
   (``belongs-to <parent>``). Without inlining, ``extract_groupings``
   returns nothing and request bodies collapse to ``{}``.

2) ``re.search`` ignored brace depth, hoisting nested leaves / containers /
   choice cases into the parent schema.

This module provides the two minimal primitives every generator needs:

* :func:`find_balanced_braces`
* :func:`iter_top_level_blocks` — yields ``(name, body)`` for every
  ``<keyword> <name> { ... }`` at brace depth 0, skipping strings and
  comments.
* :func:`iter_top_level_uses` — yields grouping names from ``uses X;`` /
  ``uses X { ... };`` at brace depth 0.
* :func:`resolve_includes` — inlines submodule bodies into the parent
  module's content so groupings declared there become visible to
  downstream extractors.
* :func:`is_submodule` — reports whether content starts with ``submodule``.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, Optional, Set, Tuple

_SUBMODULE_RE = re.compile(r'^\s*submodule\s+', re.MULTILINE)
_INCLUDE_RE = re.compile(r'\binclude\s+([\w-]+)\s*(?:\{[^}]*\})?\s*;')
_WRAPPER_RE = re.compile(r'^\s*(?:sub)?module\s+\S+\s*(?:\{|\b)')


def _unwrap_module(content: str) -> str:
    """If ``content`` starts (after whitespace and YANG header statements
    like ``yang-version``) with a ``module X { ... }`` or ``submodule X
    { ... }`` wrapper, return the wrapper body. Otherwise return the
    content unchanged.

    This lets the depth-aware scanners treat whole-file content the same
    as a container/grouping body — every interesting statement sits at
    depth 0 relative to the returned string.
    """
    m = _WRAPPER_RE.match(content)
    if not m:
        return content
    # Find the opening brace of the wrapper.
    open_brace = content.find('{', m.start())
    if open_brace == -1:
        return content
    close_brace = find_balanced_braces(content, open_brace)
    if close_brace == -1:
        return content
    return content[open_brace + 1:close_brace]



def find_balanced_braces(text: str, start_pos: int) -> int:
    """Return the index of the closing ``}`` for the ``{`` at ``start_pos``.

    Returns ``-1`` if ``text[start_pos]`` is not ``{`` or no matching brace
    is found.
    """
    if start_pos >= len(text) or text[start_pos] != '{':
        return -1
    count = 0
    for i in range(start_pos, len(text)):
        c = text[i]
        if c == '{':
            count += 1
        elif c == '}':
            count -= 1
            if count == 0:
                return i
    return -1


def _skip_string_or_comment(content: str, i: int, n: int) -> Optional[int]:
    """If ``content[i]`` opens a string or comment, return the index after
    it; otherwise return None.
    """
    c = content[i]
    if c in ('"', "'"):
        q = c
        i += 1
        while i < n:
            if content[i] == '\\' and i + 1 < n:
                i += 2
                continue
            if content[i] == q:
                return i + 1
            i += 1
        return n
    if c == '/' and i + 1 < n:
        nxt = content[i + 1]
        if nxt == '/':
            nl = content.find('\n', i)
            return n if nl < 0 else nl + 1
        if nxt == '*':
            end = content.find('*/', i + 2)
            return n if end < 0 else end + 2
    return None


def iter_top_level_blocks(content: str, keyword: str) -> Iterator[Tuple[str, str]]:
    """Yield ``(name, body)`` for each ``<keyword> <name> { ... }`` at brace
    depth 0.

    If the content begins with a ``module X { ... }`` or ``submodule X
    { ... }`` wrapper, that wrapper is automatically stripped first — so
    callers can pass either a full YANG file or an already-extracted body
    and get the same depth-0 semantics.

    Skips matches inside string literals and YANG ``//`` / ``/* */``
    comments. The keyword must be word-bounded (so ``leaf`` won't match
    ``leaf-list``).
    """
    content = _unwrap_module(content)
    n = len(content)
    i = 0
    depth = 0
    kw_re = re.compile(rf'{re.escape(keyword)}\b\s+(\S+)\s*\{{')
    while i < n:
        skipped = _skip_string_or_comment(content, i, n)
        if skipped is not None:
            i = skipped
            continue
        c = content[i]
        if c == '{':
            depth += 1
            i += 1
            continue
        if c == '}':
            depth -= 1
            i += 1
            continue
        if depth == 0:
            prev_ok = (i == 0) or not (content[i - 1].isalnum() or content[i - 1] in '_-')
            if prev_ok:
                m = kw_re.match(content, i)
                if m:
                    block_start = m.end() - 1
                    block_end = find_balanced_braces(content, block_start)
                    if block_end != -1:
                        yield m.group(1), content[block_start + 1:block_end]
                        i = block_end + 1
                        continue
        i += 1


def iter_top_level_uses(content: str) -> Iterator[str]:
    """Yield grouping names from ``uses <name>;`` and
    ``uses <name> { <refinements> };`` at brace depth 0.

    The outer ``module``/``submodule`` wrapper is auto-stripped (see
    :func:`iter_top_level_blocks`). Prefix qualifiers (``foo:bar``) are
    stripped — only the local name is returned.
    """
    content = _unwrap_module(content)
    n = len(content)
    i = 0
    depth = 0
    while i < n:
        skipped = _skip_string_or_comment(content, i, n)
        if skipped is not None:
            i = skipped
            continue
        c = content[i]
        if c == '{':
            depth += 1
            i += 1
            continue
        if c == '}':
            depth -= 1
            i += 1
            continue
        if depth == 0:
            prev_ok = (i == 0) or not (content[i - 1].isalnum() or content[i - 1] in '_-')
            if prev_ok and content.startswith('uses', i):
                # Simple form first: `uses [prefix:]name ;`
                m = re.match(r'uses\s+(?:[\w-]+:)?([\w-]+)\s*;', content[i:])
                if m:
                    yield m.group(1)
                    i += m.end()
                    continue
                # Refined form: `uses [prefix:]name { ... };`
                m = re.match(r'uses\s+(?:[\w-]+:)?([\w-]+)\s*\{', content[i:])
                if m:
                    name = m.group(1)
                    brace_pos = i + m.end() - 1
                    end = find_balanced_braces(content, brace_pos)
                    if end != -1:
                        yield name
                        i = end + 1
                        # consume optional trailing semicolon
                        while i < n and content[i] in ' \t\r\n':
                            i += 1
                        if i < n and content[i] == ';':
                            i += 1
                        continue
        i += 1


def is_submodule(content: str) -> bool:
    """Return True if ``content`` declares a YANG submodule."""
    return bool(_SUBMODULE_RE.search(content))


def resolve_includes(yang_file: Path, content: str,
                     seen: Optional[Set[str]] = None) -> str:
    """Return ``content`` with every ``include <submodule>;`` replaced by
    the body of that submodule (recursively).

    Submodule files are expected to live next to ``yang_file`` and be named
    ``<submodule>.yang``. The outer ``submodule X { ... }`` wrapper is
    stripped and the submodule body is inserted *inside* the parent
    module's own wrapper (just before its closing ``}``). That way every
    grouping ends up at the same brace depth as the parent's own
    groupings \u2014 critical for the depth-aware scanners. Missing
    submodules are silently ignored (preserves prior behaviour \u2014 a
    broken pyang lookup never blocks the pipeline).
    """
    if seen is None:
        seen = set()
    yang_dir = Path(yang_file).parent
    collected: list[str] = []
    for match in _INCLUDE_RE.finditer(content):
        submod = match.group(1)
        if submod in seen:
            continue
        seen.add(submod)
        sub_path = yang_dir / f'{submod}.yang'
        if not sub_path.is_file():
            continue
        try:
            sub_content = sub_path.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        # Recurse so a submodule that itself ``include``s another one is
        # still resolved.
        sub_content = resolve_includes(sub_path, sub_content, seen)
        # Strip outer `submodule X { ... }` wrapper and collect the body.
        wrap = re.search(r'\bsubmodule\s+\S+\s*\{', sub_content)
        if wrap:
            body_start = wrap.end() - 1
            body_end = find_balanced_braces(sub_content, body_start)
            if body_end != -1:
                collected.append(sub_content[body_start + 1:body_end])
                continue
        # Couldn't peel the wrapper \u2014 keep raw rather than skip silently.
        collected.append(sub_content)

    if not collected:
        return content

    # Insert collected submodule bodies just before the parent module's
    # closing brace, so groupings end up inside the parent wrapper.
    parent_wrap = _WRAPPER_RE.match(content)
    if parent_wrap:
        open_brace = content.find('{', parent_wrap.start())
        if open_brace != -1:
            close_brace = find_balanced_braces(content, open_brace)
            if close_brace != -1:
                injection = '\n' + '\n'.join(collected) + '\n'
                return content[:close_brace] + injection + content[close_brace:]

    # No parent wrapper detected (rare) \u2014 fall back to concatenation.
    return content + '\n' + '\n'.join(collected)
