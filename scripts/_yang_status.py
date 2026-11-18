"""Parser-independent scan of YANG ``status`` statements.

Shared by build_deprecations.py (as the independent cross-check of pyang's
parser) and enrich_mib_metadata.py (per-MIB deprecated / obsolete counts).
Handles comments, single- and double-quoted strings (so ``status deprecated``
inside a description is not counted) and ``+`` string concatenation.
"""
from __future__ import annotations

from collections import Counter


def lex_status_statements(text: str) -> list[tuple[int, str]]:
    """Return (line, argument) for every ``status`` statement in a YANG module."""
    tokens: list[tuple[str, str, int]] = []  # (kind, value, line); kind in word|str|sep
    i, n, line = 0, len(text), 1
    while i < n:
        c = text[i]
        if c == "\n":
            line += 1
            i += 1
        elif c in " \t\r\f\v":
            i += 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            line += text.count("\n", i, j)
            i = j
        elif c in ";{}":
            tokens.append(("sep", c, line))
            i += 1
        elif c == '"':
            start_line, j, buf = line, i + 1, []
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j:j + 2])
                    j += 2
                    continue
                buf.append(text[j])
                j += 1
            seg = "".join(buf)
            line += seg.count("\n")
            tokens.append(("str", seg, start_line))
            i = j + 1
        elif c == "'":
            j = text.find("'", i + 1)
            j = n if j < 0 else j
            seg = text[i + 1:j]
            tokens.append(("str", seg, line))
            line += seg.count("\n")
            i = j + 1
        else:
            j = i
            while j < n and text[j] not in " \t\r\n\f\v;{}\"'":
                if text.startswith("//", j) or text.startswith("/*", j):
                    break
                j += 1
            tokens.append(("word", text[i:j], line))
            i = j

    found: list[tuple[int, str]] = []
    at_start = True
    k = 0
    while k < len(tokens):
        kind, val, ln = tokens[k]
        if kind == "sep":
            at_start = True
            k += 1
            continue
        if at_start and kind == "word" and val == "status":
            # Argument: a word, or one or more strings joined by '+'.
            parts: list[str] = []
            k += 1
            while k < len(tokens) and tokens[k][0] != "sep":
                if not (tokens[k][0] == "word" and tokens[k][1] == "+"):
                    parts.append(tokens[k][1])
                k += 1
            found.append((ln, "".join(parts).strip()))
            at_start = False
            continue
        at_start = False
        k += 1
    return found


def status_counts(text: str) -> Counter:
    """Count of each status value (``deprecated``, ``obsolete``, ``current``) in a module."""
    return Counter(value for _, value in lex_status_statements(text))
