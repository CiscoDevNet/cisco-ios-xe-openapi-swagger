"""Guard test: hand-authored JavaScript must have balanced brackets.

A single missing brace ships a completely dead page (see the July 2026
`_renderPagerControls` regression that broke the YANG Accountability report:
the syntax error aborted the whole script and the page hung on "Loading...").

There is no Node toolchain in CI, so this is a lightweight, dependency-free
bracket-balance scanner rather than a full parser. It is deliberately
conservative: it understands line/block comments, single/double/template
strings (including `${...}` expression nesting), and regex literals, then
verifies that (), [], and {} are balanced and correctly nested. It will not
catch every syntax error, but it reliably catches the unbalanced-bracket class
that takes a page down.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# Hand-authored site scripts. Vendored/minified bundles (assets/vendor/**) are
# excluded — we neither author nor lint those.
_ROOT_JS = sorted(p for p in REPO.glob("*.js"))
_ASSET_JS = sorted(p for p in (REPO / "assets" / "js").glob("*.js"))
JS_FILES = _ROOT_JS + _ASSET_JS

_PAIRS = {")": "(", "]": "[", "}": "{"}
# After one of these punctuation tokens a `/` starts a regex literal (operand
# position); elsewhere `/` is division. Single-char heuristic.
_REGEX_PUNCT = set("(,=:[!&|?{;}") | {None, "regex", "tmpl"}
# Keywords that also put `/` in operand position, e.g. `return /re/.test(x)`.
_REGEX_KEYWORDS = {
    "return", "typeof", "instanceof", "in", "of", "new", "delete",
    "void", "throw", "do", "else", "yield", "case",
}


def _regex_allowed(src: str, i: int, prev) -> bool:
    if prev in _REGEX_PUNCT:
        return True
    # Keyword operand position: scan the word immediately before the `/`.
    j = i - 1
    while j >= 0 and src[j].isspace():
        j -= 1
    end = j + 1
    while j >= 0 and (src[j].isalnum() or src[j] in "_$"):
        j -= 1
    return src[j + 1:end] in _REGEX_KEYWORDS


def find_bracket_error(src: str):
    """Return a human-readable description of the first bracket problem, or
    None when brackets are balanced and correctly nested."""
    n = len(src)
    stack = []          # (char, line)
    tmpl_expr_depth = []  # stack depth captured when a `${` expression opened
    prev = None         # previous significant token/char (for regex detection)
    mode = "code"
    i = 0

    def line_of(idx: int) -> int:
        return src.count("\n", 0, idx) + 1

    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if mode == "code":
            if c == "/" and nxt == "/":
                j = src.find("\n", i)
                i = n if j == -1 else j
                continue
            if c == "/" and nxt == "*":
                j = src.find("*/", i + 2)
                i = n if j == -1 else j + 2
                continue
            if c == '"' or c == "'":
                i = _skip_string(src, i, c)
                prev = "str"
                continue
            if c == "`":
                mode = "template"
                i += 1
                continue
            if c == "/" and _regex_allowed(src, i, prev):
                i = _skip_regex(src, i)
                prev = "regex"
                continue
            if c in "([{":
                stack.append((c, line_of(i)))
                prev = c
                i += 1
                continue
            if c in ")]}":
                if not stack:
                    return f"line {line_of(i)}: unmatched '{c}'"
                op, ol = stack.pop()
                if _PAIRS[c] != op:
                    return (f"line {line_of(i)}: '{c}' does not close '{op}' "
                            f"opened at line {ol}")
                if c == "}" and tmpl_expr_depth and tmpl_expr_depth[-1] == len(stack):
                    tmpl_expr_depth.pop()
                    mode = "template"
                prev = c
                i += 1
                continue
            if not c.isspace():
                prev = c
            i += 1
        else:  # inside a template literal
            if c == "\\":
                i += 2
                continue
            if c == "`":
                mode = "code"
                prev = "tmpl"
                i += 1
                continue
            if c == "$" and nxt == "{":
                tmpl_expr_depth.append(len(stack))
                stack.append(("{", line_of(i)))
                mode = "code"
                i += 2
                continue
            i += 1

    if stack:
        op, ol = stack[0]
        return f"unclosed '{op}' opened at line {ol} (still {len(stack)} open at EOF)"
    return None


def _skip_string(src: str, i: int, quote: str) -> int:
    n = len(src)
    i += 1
    while i < n:
        if src[i] == "\\":
            i += 2
            continue
        if src[i] == quote:
            return i + 1
        i += 1
    return n


def _skip_regex(src: str, i: int) -> int:
    n = len(src)
    i += 1  # past opening /
    in_class = False
    while i < n:
        c = src[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":
            in_class = True
        elif c == "]":
            in_class = False
        elif c == "/" and not in_class:
            i += 1
            break
        elif c == "\n":
            break  # unterminated regex; stop
        i += 1
    while i < n and src[i].isalpha():  # flags
        i += 1
    return i


@pytest.mark.parametrize("path", JS_FILES, ids=lambda p: str(p.relative_to(REPO)))
def test_js_brackets_balanced(path: Path):
    src = path.read_text(encoding="utf-8")
    err = find_bracket_error(src)
    if err:
        pytest.fail(f"{path.relative_to(REPO)}: {err}")
