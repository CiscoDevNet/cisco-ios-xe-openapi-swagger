#!/usr/bin/env python3
"""Render APP_MAP.md into the strict-CSP static page `app-map.html`.

This is **not** a general markdown renderer. It supports only the subset of
GitHub-Flavoured Markdown actually used by APP_MAP.md:

    - ATX headers (#, ##, ###, ####)
    - Paragraphs
    - Ordered + unordered lists (with nesting via indentation)
    - GitHub tables
    - Blockquotes
    - Horizontal rules (---)
    - Fenced code blocks (``` ... ```) including ```mermaid
    - Inline: backtick code, **bold**, *italic*, [text](url)

It is deterministic, dependency-free, and CSP-safe (no inline `<script>`
emitted). The mermaid block is rendered as a styled `<pre>` with a hint
that the source is the canonical artifact.

Re-run after editing APP_MAP.md:

    python -X utf8 scripts/build_app_map_html.py
"""
from __future__ import annotations

import html
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "APP_MAP.md"
TARGET = ROOT / "app-map.html"

PAGE_TITLE = "App Map \u2014 Cisco IOS-XE OpenAPI Documentation Hub"
PAGE_DESC = (
    "Architectural map of the Cisco IOS-XE OpenAPI documentation hub: every "
    "page, every data file, every user flow \u2014 generated from the canonical "
    "APP_MAP.md source."
)

CSS = """
:root {
    --bg: #f5f5f5;
    --panel: #ffffff;
    --text: #1a1a1a;
    --muted: #5f6b7a;
    --border: #e0e4e8;
    --accent: #1565C0;
    --accent-dark: #0D47A1;
    --code-bg: #f5f7fa;
    --code-fg: #2d3748;
    --table-head: #f7f7f7;
    --quote: #5f6b7a;
    --quote-bar: #1565C0;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.55;
}
.header {
    background: linear-gradient(135deg, #1565C0, #0D47A1);
    color: #ffffff;
    padding: 28px 20px 24px;
}
.header .inner { max-width: 980px; margin: 0 auto; }
.header h1 { margin: 0 0 6px; font-size: 1.7rem; font-weight: 500; }
.header p { margin: 0 0 14px; opacity: 0.92; font-size: 0.96rem; }
.header nav { display: flex; flex-wrap: wrap; gap: 8px; }
.header nav a {
    background: rgba(255, 255, 255, 0.16);
    color: #ffffff;
    padding: 5px 12px;
    text-decoration: none;
    border-radius: 16px;
    font-size: 0.85rem;
}
.header nav a:hover { background: rgba(255, 255, 255, 0.30); }
.container {
    max-width: 980px;
    margin: 0 auto;
    padding: 24px 20px 64px;
}
.toolbar {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 22px;
    font-size: 0.88rem;
    color: var(--muted);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    align-items: center;
    justify-content: space-between;
}
.toolbar .links a {
    color: var(--accent);
    text-decoration: none;
    font-weight: 500;
    margin-right: 14px;
}
.toolbar .links a:hover { text-decoration: underline; }
.content {
    background: var(--panel);
    border-radius: 8px;
    padding: 28px 36px;
    border: 1px solid var(--border);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.content h1, .content h2, .content h3, .content h4 {
    margin-top: 1.8em;
    margin-bottom: 0.55em;
    line-height: 1.25;
}
.content h1 { font-size: 1.8rem; border-bottom: 2px solid var(--border); padding-bottom: 0.3em; }
.content h2 { font-size: 1.4rem; border-bottom: 1px solid var(--border); padding-bottom: 0.25em; }
.content h3 { font-size: 1.15rem; color: var(--accent-dark); }
.content h4 { font-size: 1rem; color: var(--accent-dark); }
.content h1:first-child, .content h2:first-child { margin-top: 0; }
.content p { margin: 0.6em 0 0.9em; }
.content a { color: var(--accent); text-decoration: none; }
.content a:hover { text-decoration: underline; }
.content ul, .content ol { padding-left: 1.7em; margin: 0.5em 0 1em; }
.content li { margin-bottom: 0.25em; }
.content hr { border: 0; border-top: 1px solid var(--border); margin: 2em 0; }
.content blockquote {
    border-left: 4px solid var(--quote-bar);
    color: var(--quote);
    margin: 1em 0;
    padding: 0.4em 1em;
    background: #f7f9fc;
    border-radius: 0 6px 6px 0;
}
.content blockquote p { margin: 0.35em 0; }
.content code {
    background: var(--code-bg);
    color: var(--code-fg);
    padding: 1px 6px;
    border-radius: 4px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    font-size: 0.88em;
}
.content pre {
    background: var(--code-bg);
    color: var(--code-fg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px 18px;
    overflow-x: auto;
    font-size: 0.85rem;
    line-height: 1.45;
}
.content pre code {
    background: transparent;
    padding: 0;
    font-size: inherit;
    color: inherit;
}
/* Mindmap is rendered as a generated PNG (see scripts/build_app_map_html.py
   `_render_mindmap_png`). The source Mermaid block remains available below
   the image inside a collapsed `<details>`. */
.content .mindmap-figure {
    margin: 1.2em 0 1.4em;
    padding: 0;
    background: linear-gradient(180deg, #f7faff, #eef3fb);
    border: 1px solid var(--border);
    border-radius: 10px;
    text-align: center;
    overflow: hidden;
}
.content .mindmap-figure img {
    display: block;
    width: 100%;
    height: auto;
    max-width: 100%;
    margin: 0 auto;
}
.content .mindmap-figure figcaption {
    padding: 10px 16px 12px;
    font-size: 0.82rem;
    color: var(--muted);
    text-align: center;
    border-top: 1px solid var(--border);
    background: #ffffff;
}
.content .mindmap-source {
    margin: 0.2em 0 1.2em;
    font-size: 0.78rem;
    color: var(--muted);
}
.content .mindmap-source summary {
    cursor: pointer;
    user-select: none;
}
.content .mindmap-source pre {
    margin-top: 6px;
    font-size: 0.78rem;
}
.content table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.9rem;
    margin: 1em 0 1.4em;
    overflow-x: auto;
    display: block;
}
.content table th, .content table td {
    border: 1px solid var(--border);
    padding: 7px 10px;
    vertical-align: top;
    text-align: left;
}
.content table thead th { background: var(--table-head); font-weight: 600; }
.content table tbody tr:nth-child(even) { background: #fafbfc; }
.footer {
    max-width: 980px;
    margin: 0 auto;
    padding: 28px 20px 12px;
    color: var(--muted);
    font-size: 0.82rem;
    text-align: center;
}
"""

HEADER_NAV = [
    ("Home", "index.html"),
    ("Code Generator", "code-generator.html"),
    ("Compare Trees", "tree-compare.html"),
    ("YANG Report", "yang-accountability.html"),
    ("MDT Telemetry", "telemetry.html"),
    ("Platform Coverage", "platform-coverage.html"),
    ("About", "about.html"),
]

INLINE_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
INLINE_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
INLINE_CODE = re.compile(r"`([^`\n]+)`")
INLINE_BOLD = re.compile(r"\*\*([^*\n]+)\*\*")
INLINE_ITALIC = re.compile(r"(?<![*\w])\*([^*\n]+)\*(?!\w)")


def _render_inline(text: str) -> str:
    """Apply inline markdown to text that is **not** yet HTML-escaped."""
    # Extract code spans first so their contents aren't subject to bold/italic
    placeholders: list[str] = []

    def _stash_code(m: re.Match) -> str:
        placeholders.append(m.group(1))
        return f"\x00CODE{len(placeholders) - 1}\x00"

    pre = INLINE_CODE.sub(_stash_code, text)
    pre = html.escape(pre, quote=False)
    pre = INLINE_BOLD.sub(r"<strong>\1</strong>", pre)
    pre = INLINE_ITALIC.sub(r"<em>\1</em>", pre)

    def _img_repl(m: re.Match) -> str:
        alt = m.group(1)
        src = m.group(2)
        return (
            f'<img src="{html.escape(src, quote=True)}" '
            f'alt="{html.escape(alt, quote=True)}" '
            f'loading="lazy" style="max-width:100%;height:auto;border-radius:6px;">'
        )

    # Images must run before INLINE_LINK so the leading '!' isn't lost.
    pre = INLINE_IMAGE.sub(_img_repl, pre)

    def _link_repl(m: re.Match) -> str:
        label = m.group(1)
        href = m.group(2)
        # Resolve workspace-relative paths to GitHub raw view for files that
        # are not also published to the site (e.g. .py, .md). The site itself
        # only ships HTML/JS/JSON, so anything else is best-effort linked to
        # the GitHub source tree.
        return f'<a href="{html.escape(href, quote=True)}">{label}</a>'

    pre = INLINE_LINK.sub(_link_repl, pre)

    for i, raw in enumerate(placeholders):
        pre = pre.replace(
            f"\x00CODE{i}\x00",
            f"<code>{html.escape(raw, quote=False)}</code>",
        )
    return pre


def _parse_table(lines: list[str], idx: int) -> tuple[str, int]:
    """Parse a GitHub-style table starting at lines[idx]. Returns (html, next_idx)."""
    header = lines[idx]
    sep = lines[idx + 1]
    cells = [c.strip() for c in header.strip().strip("|").split("|")]
    rows_html: list[str] = []
    j = idx + 2
    while j < len(lines) and lines[j].lstrip().startswith("|"):
        row_cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
        rows_html.append(
            "<tr>"
            + "".join(f"<td>{_render_inline(c)}</td>" for c in row_cells)
            + "</tr>"
        )
        j += 1
    head_html = (
        "<thead><tr>"
        + "".join(f"<th>{_render_inline(c)}</th>" for c in cells)
        + "</tr></thead>"
    )
    body_html = "<tbody>" + "".join(rows_html) + "</tbody>"
    return f"<table>{head_html}{body_html}</table>", j


def _is_table_row(line: str) -> bool:
    return line.lstrip().startswith("|") and line.count("|") >= 2


def _is_table_sep(line: str) -> bool:
    stripped = line.strip().strip("|")
    if not stripped:
        return False
    cells = [c.strip() for c in stripped.split("|")]
    return all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c)


def _parse_list(lines: list[str], idx: int) -> tuple[str, int]:
    """Parse a list (possibly nested) starting at lines[idx]. Returns (html, next_idx).

    Indent unit is detected from the first sub-item; sibling items share
    indentation. Supports `- `, `* `, `1.` style markers.
    """
    items: list[tuple[int, str, str]] = []  # (indent, marker_kind, content)
    j = idx
    while j < len(lines):
        raw = lines[j]
        if not raw.strip():
            # Blank line terminates list only if not followed by another list
            # item; we treat any blank as terminator for simplicity.
            break
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", raw)
        if not m:
            # Continuation line: append to previous item's content.
            if items and raw.startswith(" "):
                indent_prev, kind_prev, content_prev = items[-1]
                items[-1] = (indent_prev, kind_prev, content_prev + " " + raw.strip())
                j += 1
                continue
            break
        indent = len(m.group(1))
        kind = "ol" if m.group(2).endswith(".") else "ul"
        content = m.group(3)
        items.append((indent, kind, content))
        j += 1

    # Build nested structure
    def _emit(items_slice: list[tuple[int, str, str]], base_indent: int) -> str:
        out: list[str] = []
        k = 0
        kind_at_level: str | None = None
        while k < len(items_slice):
            indent, kind, content = items_slice[k]
            if indent != base_indent:
                k += 1
                continue
            if kind_at_level is None:
                kind_at_level = kind
                out.append(f"<{kind_at_level}>")
            # find children of this item
            child_start = k + 1
            child_end = child_start
            while (child_end < len(items_slice)
                   and items_slice[child_end][0] > base_indent):
                child_end += 1
            li_inner = _render_inline(content)
            if child_end > child_start:
                child_indent = items_slice[child_start][0]
                li_inner += _emit(items_slice[child_start:child_end], child_indent)
            out.append(f"<li>{li_inner}</li>")
            k = child_end
        if kind_at_level:
            out.append(f"</{kind_at_level}>")
        return "".join(out)

    base = items[0][0] if items else 0
    return _emit(items, base), j


def _parse_blockquote(lines: list[str], idx: int) -> tuple[str, int]:
    j = idx
    parts: list[str] = []
    while j < len(lines) and lines[j].lstrip().startswith(">"):
        parts.append(re.sub(r"^\s*>\s?", "", lines[j]))
        j += 1
    inner = "<br>".join(_render_inline(p) for p in parts if p.strip())
    return f"<blockquote><p>{inner}</p></blockquote>", j


def _render_mindmap(code: str) -> str:
    """Render a Mermaid `mindmap` block.

    The hierarchy is parsed from the indentation-driven Mermaid syntax, then
    drawn as a horizontal mindmap PNG (root on the left, color-coded L1
    branches fanning right, L2 leaves listed beside each branch). The PNG
    is written once per build to ``docs/app_mindmap.png`` and embedded via
    ``<img>``. The original Mermaid source remains available below the
    image inside a collapsed ``<details>`` for accessibility / portability.

    If Pillow is unavailable the renderer falls back to a plain ``<pre>``
    of the Mermaid source so the page still builds.
    """
    raw_lines = code.splitlines()
    # Drop the leading `mindmap` directive
    if raw_lines and raw_lines[0].strip().lower().startswith("mindmap"):
        raw_lines = raw_lines[1:]

    nodes: list[tuple[int, str]] = []  # (indent, label)
    SHAPE_RE = re.compile(
        r"""^[\w\-]*       # optional node id
            \s*
            (?: \(\((?P<a>[^)]+)\)\)      # ((cloud))
              | \[\[(?P<b>[^\]]+)\]\]      # [[subroutine]]
              | \(\[(?P<c>[^\]]+)\]\)      # ([rounded])
              | \[(?P<d>[^\]]+)\]          # [box]
              | \((?P<e>[^)]+)\)            # (pill)
              | \{\{(?P<f>[^}]+)\}\}        # {{hex}}
              | \{(?P<g>[^}]+)\}            # {rhombus}
              | \"(?P<h>[^"]+)\"            # "quoted"
            )\s*$""",
        re.VERBOSE,
    )
    for ln in raw_lines:
        if not ln.strip():
            continue
        indent = len(ln) - len(ln.lstrip(" "))
        text = ln.strip()
        if text.startswith("::"):
            continue
        m = SHAPE_RE.match(text)
        if m:
            text = next(g for g in m.groupdict().values() if g is not None)
        nodes.append((indent, text))

    if not nodes:
        return "<pre><code>(empty mindmap)</code></pre>"

    # Build the tree.
    roots: list[tuple[str, list]] = []
    stack: list[tuple[int, list]] = []
    for indent, label in nodes:
        while stack and stack[-1][0] >= indent:
            stack.pop()
        node = (label, [])
        if stack:
            stack[-1][1].append(node)
        else:
            roots.append(node)
        stack.append((indent, node[1]))

    img_rel = "docs/app_mindmap.png"
    img_path = ROOT / img_rel
    # Try to regenerate the PNG from the current source; if Pillow isn't
    # available (common on a barebones CI runner) we still emit the figure
    # when a previously-committed PNG exists on disk.
    _render_mindmap_png(roots, img_path)
    has_png = img_path.is_file() and img_path.stat().st_size > 0

    source_escaped = html.escape(code, quote=False)
    if has_png:
        figure = (
            '<figure class="mindmap-figure">'
            f'<img src="{img_rel}" alt="Cisco IOS-XE Documentation Hub — app mindmap"'
            ' loading="lazy">'
            '<figcaption>App-map overview &mdash; root node, color-coded category'
            ' branches, and second-level features. See the source below for the full'
            ' hierarchy including third-level details.</figcaption>'
            '</figure>'
        )
    else:
        # Neither Pillow nor a committed PNG — fall back to raw Mermaid source
        # so the page still builds and the data is preserved.
        figure = (
            "<pre><code class=\"language-mermaid\">"
            f"{source_escaped}"
            "</code></pre>"
        )

    return (
        figure
        + '<details class="mindmap-source">'
        + "<summary>Show Mermaid source</summary>"
        + f"<pre><code>{source_escaped}</code></pre>"
        + "</details>"
    )


def _render_mindmap_png(
    roots: list[tuple[str, list]], out_path: Path
) -> bool:
    """Draw the parsed mindmap as ``out_path`` (PNG). Returns True on success.

    Radial "bubble" layout that mirrors Mermaid's native mindmap renderer:
    a central root, six color-coded category bubbles arranged around it,
    and every second-level (and third-level when present) leaf shown as a
    smaller tinted bubble fanning outward along its branch axis. Connectors
    are cubic Bezier curves in the branch color so the eye can trace any
    leaf back to its category at a glance.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False

    if not roots:
        return False

    import math

    root_label, root_children = roots[0]

    # Parse: each branch keeps its leaves AND each leaf keeps its sub-leaves.
    # The Mermaid source uses "::sub" markers for an inline group; those are
    # flattened into the parent branch (sub-leaves attach to the previous
    # real leaf so the radial picture stays balanced).
    branches: list[tuple[str, list[tuple[str, list[str]]]]] = []
    for l1_label, l1_children in root_children:
        leaves: list[tuple[str, list[str]]] = []
        pending_sub: list[str] = []
        for child_label, child_grand in l1_children:
            if child_label.startswith("::"):
                # collect grandchildren of this marker as sub-leaves
                for g_label, _ in child_grand:
                    pending_sub.append(g_label)
                continue
            sub = [g_label for g_label, _ in child_grand
                   if not g_label.startswith("::")]
            leaves.append((child_label, sub))
        if pending_sub and leaves:
            # attach the trailing "::sub" group to the last real leaf
            tail_label, tail_sub = leaves[-1]
            leaves[-1] = (tail_label, list(tail_sub) + pending_sub)
        branches.append((l1_label, leaves))

    if not branches:
        return False

    # --- palette ---------------------------------------------------------
    PALETTE = [
        (21, 101, 192),    # blue
        (123, 31, 162),    # purple
        (46, 125, 50),     # green
        (239, 108, 0),     # orange
        (0, 131, 143),     # teal
        (84, 110, 122),    # slate
        (194, 24, 91),     # pink
        (191, 54, 12),     # deep orange
    ]
    BG_TOP = (244, 248, 254)
    BG_BOT = (228, 237, 249)
    TEXT = (24, 32, 48)
    MUTED = (96, 110, 130)
    SHADOW = (180, 196, 218)
    HEADER_BLUE = (13, 71, 161)
    ROOT_DARK = (10, 56, 130)
    ROOT_LIGHT = (33, 105, 200)

    def _tint(rgb, amount=0.82):
        return tuple(int(c + (255 - c) * amount) for c in rgb)

    def _darken(rgb, amount=0.25):
        return tuple(int(c * (1 - amount)) for c in rgb)

    # --- canvas ----------------------------------------------------------
    W, H = 2600, 1900
    img = Image.new("RGB", (W, H), BG_TOP)
    draw = ImageDraw.Draw(img)
    # vertical gradient
    for y in range(H):
        t = y / max(1, H - 1)
        r = int(BG_TOP[0] * (1 - t) + BG_BOT[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOT[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOT[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    def _font(size: int, bold: bool = False):
        for name in (
            "seguisb.ttf" if bold else "segoeui.ttf",
            "arialbd.ttf" if bold else "arial.ttf",
            "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        ):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    f_title = _font(30, bold=True)
    f_subtitle = _font(16)
    f_root = _font(34, bold=True)
    f_branch = _font(22, bold=True)
    f_leaf = _font(17, bold=True)
    f_sub = _font(13)
    f_footer = _font(13)

    # --- title strip -----------------------------------------------------
    draw.text((56, 32), "Cisco IOS-XE Documentation Hub  —  Application Mind Map",
              font=f_title, fill=HEADER_BLUE)
    draw.text((58, 72),
              "Generated from APP_MAP.md  ·  Radial view: root → categories → features (full hierarchy in the source below).",
              font=f_subtitle, fill=MUTED)
    draw.rectangle((56, 102, 320, 106), fill=HEADER_BLUE)

    # --- helpers ---------------------------------------------------------
    def cubic_bezier(p0, p1, p2, p3, steps=48):
        pts = []
        for s in range(steps + 1):
            t = s / steps
            u = 1 - t
            x = (u * u * u * p0[0]
                 + 3 * u * u * t * p1[0]
                 + 3 * u * t * t * p2[0]
                 + t * t * t * p3[0])
            y = (u * u * u * p0[1]
                 + 3 * u * u * t * p1[1]
                 + 3 * u * t * t * p2[1]
                 + t * t * t * p3[1])
            pts.append((x, y))
        return pts

    def text_size(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def draw_bubble(cx, cy, text, font, fill, text_color=(255, 255, 255),
                    pad_x=18, pad_y=10, radius_extra=0, outline=None):
        tw, th = text_size(text, font)
        w = tw + pad_x * 2
        h = th + pad_y * 2
        x1, y1 = int(cx - w / 2), int(cy - h / 2)
        x2, y2 = int(cx + w / 2), int(cy + h / 2)
        rad = h // 2 + radius_extra
        # shadow
        draw.rounded_rectangle((x1 + 3, y1 + 5, x2 + 3, y2 + 5),
                               radius=rad, fill=SHADOW)
        draw.rounded_rectangle((x1, y1, x2, y2), radius=rad, fill=fill,
                               outline=outline, width=2 if outline else 0)
        draw.text((cx - tw / 2, cy - th / 2 - 1), text, font=font,
                  fill=text_color)
        return (x1, y1, x2, y2)

    # --- radial layout ---------------------------------------------------
    # Plot area sits below the title strip
    plot_top = 140
    cx0 = W / 2
    cy0 = (plot_top + H) / 2 - 30

    n = len(branches)
    # Proportional arc allocation: each branch gets angular space scaled
    # to its number of leaves, with a minimum so sparse branches still
    # read clearly. A fixed gap separates adjacent branches.
    leaf_counts = [max(1, len(b[1])) for b in branches]
    total_leaves = sum(leaf_counts)
    GAP_DEG = 10
    available = 360 - n * GAP_DEG
    MIN_ARC = 38
    raw_arcs = [available * c / total_leaves for c in leaf_counts]
    arcs = [max(MIN_ARC, a) for a in raw_arcs]
    # Renormalize so total = available
    scale = available / sum(arcs)
    arcs = [a * scale for a in arcs]

    # Start at the top (-90°) and walk clockwise
    start_angles: list[float] = []
    centers: list[float] = []
    cursor = -90 - GAP_DEG / 2
    for arc in arcs:
        cursor += GAP_DEG
        start_angles.append(cursor)
        centers.append(cursor + arc / 2)
        cursor += arc

    # Branch ring (distance from root to category bubble centre)
    R_BRANCH = 360
    # Leaf ring (distance from root to leaf bubble centre); push dense
    # branches a bit further so chord-length per leaf stays comfortable.
    LEAF_RING_BASE = 720

    branch_pos: list[tuple[float, float, float]] = []
    for c_deg in centers:
        ang = math.radians(c_deg)
        bx = cx0 + R_BRANCH * math.cos(ang)
        by = cy0 + R_BRANCH * math.sin(ang)
        branch_pos.append((bx, by, ang))

    # --- draw connectors: root → branches --------------------------------
    for i, (label, leaves) in enumerate(branches):
        color = PALETTE[i % len(PALETTE)]
        bx, by, ang = branch_pos[i]
        sx = cx0 + 108 * math.cos(ang)
        sy = cy0 + 108 * math.sin(ang)
        c1 = (cx0 + 220 * math.cos(ang), cy0 + 220 * math.sin(ang))
        c2 = (bx - 110 * math.cos(ang), by - 110 * math.sin(ang))
        pts = cubic_bezier((sx, sy), c1, c2, (bx, by), steps=44)
        draw.line(pts, fill=_tint(color, 0.75), width=14)
        draw.line(pts, fill=color, width=7)

    # --- compute leaf positions and draw connectors: branch → leaves ----
    leaf_positions: list[list[tuple[float, float]]] = []
    for i, (label, leaves) in enumerate(branches):
        color = PALETTE[i % len(PALETTE)]
        bx, by, ang_center = branch_pos[i]
        nl = len(leaves)
        positions: list[tuple[float, float]] = []
        if nl == 0:
            leaf_positions.append(positions)
            continue
        # Spread leaves across the full allocated arc (minus a small inset
        # so they sit inside the branch's slice).
        arc = arcs[i]
        inner = arc - 6  # degrees actually used by leaves
        if nl == 1:
            offsets = [0.0]
        else:
            offsets = [-inner / 2 + (inner * j / (nl - 1)) for j in range(nl)]
        # leaf ring: bump radius slightly for very dense branches so
        # leaf bubbles do not crowd each other.
        leaf_ring = LEAF_RING_BASE + max(0, (nl - 5) * 25)
        for j, (leaf_label, _sub) in enumerate(leaves):
            leaf_ang = math.radians(centers[i] + offsets[j])
            lx = cx0 + leaf_ring * math.cos(leaf_ang)
            ly = cy0 + leaf_ring * math.sin(leaf_ang)
            positions.append((lx, ly))
            # connector branch → leaf: simple curve from branch toward leaf
            cmx = (bx + lx) / 2
            cmy = (by + ly) / 2
            pts = cubic_bezier((bx, by), (cmx, by), (cmx, ly), (lx, ly),
                               steps=24)
            draw.line(pts, fill=color, width=3)
        leaf_positions.append(positions)

    # --- draw leaf bubbles ---------------------------------------------
    # (Sub-leaves are intentionally NOT rendered in the picture; they live
    # in the collapsible Mermaid source block under the figure so the
    # visual stays clean and uncluttered.)
    for i, (label, leaves) in enumerate(branches):
        color = PALETTE[i % len(PALETTE)]
        tint = _tint(color, 0.84)
        for (leaf_label, _sub), (lx, ly) in zip(leaves, leaf_positions[i]):
            draw_bubble(lx, ly, leaf_label, f_leaf, fill=tint,
                        text_color=_darken(color, 0.45),
                        pad_x=14, pad_y=8, outline=color)

    # --- draw branch bubbles (above connectors) -------------------------
    for i, (label, leaves) in enumerate(branches):
        color = PALETTE[i % len(PALETTE)]
        bx, by, _ = branch_pos[i]
        full = f"{label}  ({len(leaves)})"
        draw_bubble(bx, by, full, f_branch, fill=color,
                    text_color=(255, 255, 255), pad_x=22, pad_y=14)

    # --- draw root bubble (on top of everything) ------------------------
    # circular root
    root_r = 110
    # outer shadow
    draw.ellipse((cx0 - root_r + 6, cy0 - root_r + 10,
                  cx0 + root_r + 6, cy0 + root_r + 10), fill=SHADOW)
    # main dark circle
    draw.ellipse((cx0 - root_r, cy0 - root_r,
                  cx0 + root_r, cy0 + root_r), fill=ROOT_DARK)
    # highlight (lighter top half)
    draw.pieslice((cx0 - root_r, cy0 - root_r,
                   cx0 + root_r, cy0 + root_r),
                  start=180, end=360, fill=ROOT_LIGHT)
    # inner ring
    draw.ellipse((cx0 - root_r + 8, cy0 - root_r + 8,
                  cx0 + root_r - 8, cy0 + root_r - 8),
                 outline=(255, 255, 255), width=3)
    # root label (wrap on whitespace if needed)
    root_words = root_label.split()
    if len(root_words) >= 3:
        line1 = " ".join(root_words[:-1])
        line2 = root_words[-1]
    else:
        line1, line2 = root_label, ""
    t1w, t1h = text_size(line1, f_root)
    if line2:
        t2w, t2h = text_size(line2, f_root)
        draw.text((cx0 - t1w / 2, cy0 - t1h - 2), line1,
                  font=f_root, fill=(255, 255, 255))
        draw.text((cx0 - t2w / 2, cy0 + 4), line2,
                  font=f_root, fill=(255, 255, 255))
    else:
        draw.text((cx0 - t1w / 2, cy0 - t1h / 2), line1,
                  font=f_root, fill=(255, 255, 255))

    # --- footer ----------------------------------------------------------
    draw.text((56, H - 36),
              "Cisco IOS-XE Documentation Hub  ·  cs.co/xeswagger",
              font=f_footer, fill=MUTED)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG", optimize=True)
    return True


def _iter_blocks(text: str) -> Iterator[str]:
    """Yield HTML for each block in `text`."""
    lines = text.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # Blank
        if not line.strip():
            i += 1
            continue

        # Fenced code block
        m = re.match(r"^```(\w*)\s*$", line)
        if m:
            lang = m.group(1).strip().lower()
            j = i + 1
            buf: list[str] = []
            while j < len(lines) and not re.match(r"^```\s*$", lines[j]):
                buf.append(lines[j])
                j += 1
            code = "\n".join(buf)
            if lang == "mermaid" and code.lstrip().startswith("mindmap"):
                yield _render_mindmap(code)
            else:
                yield (
                    f"<pre><code>"
                    f"{html.escape(code, quote=False)}"
                    f"</code></pre>"
                )
            i = j + 1
            continue

        # Headers
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            txt = m.group(2).strip()
            slug = re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")
            yield f'<h{level} id="{slug}">{_render_inline(txt)}</h{level}>'
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^\s*-{3,}\s*$", line):
            yield "<hr>"
            i += 1
            continue

        # Tables
        if (_is_table_row(line)
                and i + 1 < len(lines)
                and _is_table_sep(lines[i + 1])):
            html_table, i = _parse_table(lines, i)
            yield html_table
            continue

        # Blockquote
        if line.lstrip().startswith(">"):
            block, i = _parse_blockquote(lines, i)
            yield block
            continue

        # Lists
        if re.match(r"^(\s*)([-*]|\d+\.)\s+", line):
            block, i = _parse_list(lines, i)
            yield block
            continue

        # Paragraph: collect until blank / block boundary
        para: list[str] = [line]
        i += 1
        while (i < len(lines)
               and lines[i].strip()
               and not re.match(r"^(#{1,6}\s|```|>\s|\s*[-*]\s|\s*\d+\.\s|\s*-{3,}\s*$)", lines[i])
               and not (_is_table_row(lines[i])
                        and i + 1 < len(lines)
                        and _is_table_sep(lines[i + 1]))):
            para.append(lines[i])
            i += 1
        yield f"<p>{_render_inline(' '.join(s.strip() for s in para))}</p>"


def render(markdown: str) -> str:
    return "\n".join(_iter_blocks(markdown))


def build_page(body_html: str, source_rel: str) -> str:
    nav_html = "".join(
        f'<a href="{html.escape(href, quote=True)}">{label}</a>'
        for label, href in HEADER_NAV
    )
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(PAGE_TITLE)}</title>
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src fonts.gstatic.com; img-src 'self' data:; connect-src 'self';">
    <meta name="description" content="{html.escape(PAGE_DESC, quote=True)}">
    <meta name="keywords" content="Cisco IOS-XE, YANG, OpenAPI, RESTCONF, NETCONF, network automation, model-driven telemetry, programmability, swagger, architecture, site map">
    <meta name="author" content="Cisco DevNet">
    <meta name="theme-color" content="#1565c0" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#0a0d12" media="(prefers-color-scheme: dark)">
    <link rel="canonical" href="https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/app-map.html">
    <link rel="icon" type="image/svg+xml" href="assets/icons/favicon.svg">
    <link rel="alternate icon" type="image/x-icon" href="assets/icons/favicon.ico">
    <link rel="apple-touch-icon" sizes="180x180" href="assets/icons/apple-touch-icon.png">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Cisco IOS-XE OpenAPI &amp; YANG Docs">
    <meta property="og:title" content="{html.escape(PAGE_TITLE)}">
    <meta property="og:description" content="{html.escape(PAGE_DESC, quote=True)}">
    <meta property="og:url" content="https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/app-map.html">
    <meta property="og:image" content="https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/assets/icons/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{html.escape(PAGE_TITLE)}">
    <meta name="twitter:description" content="{html.escape(PAGE_DESC, quote=True)}">
    <meta name="twitter:image" content="https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/assets/icons/og-image.png">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>{CSS}</style>
</head>
<body>
    <header class="header">
        <div class="inner">
            <h1>App Map</h1>
            <p>Architectural map of every page, data file, and user flow in the Cisco IOS-XE OpenAPI documentation hub.</p>
            <nav>{nav_html}</nav>
        </div>
    </header>
    <main class="container">
        <div class="toolbar">
            <div class="links">
                <a href="{html.escape(source_rel)}">View source (Markdown)</a>
                <a href="https://github.com/CiscoDevNet/cisco-ios-xe-openapi-swagger/blob/main/{html.escape(source_rel)}">Edit on GitHub</a>
            </div>
            <div>Generated {generated_at} from <code>{html.escape(source_rel)}</code></div>
        </div>
        <article class="content">
{body_html}
        </article>
    </main>
    <footer class="footer">
        <p>Auto-generated by <code>scripts/build_app_map_html.py</code>. To update, edit
        <code>{html.escape(source_rel)}</code> and re-run the script.</p>
    </footer>
    <script src="assets/js/sw-register.js"></script>
</body>
</html>
"""


def main() -> int:
    if not SOURCE.is_file():
        sys.stderr.write(f"[app-map] source not found: {SOURCE}\n")
        return 1
    md_text = SOURCE.read_text(encoding="utf-8")
    body = render(md_text)
    html_out = build_page(body, SOURCE.name)
    TARGET.write_text(html_out, encoding="utf-8")
    size_kb = TARGET.stat().st_size / 1024
    print(f"[app-map] wrote {TARGET.relative_to(ROOT)} ({size_kb:.1f} KB) "
          f"from {SOURCE.relative_to(ROOT)} ({SOURCE.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
