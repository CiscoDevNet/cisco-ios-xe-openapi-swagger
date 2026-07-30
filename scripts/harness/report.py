"""Render captured RESTCONF responses into one offline HTML for easy review.

Part of the Track B GET harness (DEVICE_DATA_COLLECTION.md §11.A.1). Walks every
capture under scripts/harness/captures/ and emits a single self-contained
scripts/harness/capture-report.html grouped device -> category -> module ->
path, with an HTTP-status badge and the verbatim (already light-redacted)
response body in a collapsible block. A text box filters by module/path.

Local review only: the report embeds device-real data, so it is GITIGNORED and
must never be committed. It is a static file (native <details> collapsing +
one tiny inline filter script); open it straight from disk.

Run:  python -X utf8 -m scripts.harness.report
      python -X utf8 -m scripts.harness.report --open      # also open in a browser
"""
from __future__ import annotations

import argparse
import html
import json
import sys
import webbrowser
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

HARNESS_DIR = Path(__file__).resolve().parent
CAPTURES_DIR = HARNESS_DIR / "captures"
REPORT_PATH = HARNESS_DIR / "capture-report.html"

# Cap each rendered response so a few huge subtrees don't produce an unusably
# large HTML file. --full disables the cap.
DEFAULT_MAX_CHARS = 100_000


def _status_class(status) -> str:
    if status == 200:
        return "ok"
    if status == 404:
        return "missing"
    if isinstance(status, int) and 500 <= status < 600:
        return "err"
    return "other"


def _iter_captures(captures_dir: Path):
    for cap in sorted(captures_dir.glob("*/*/*.json")):
        try:
            record = json.loads(cap.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        yield cap, record


def _render_response(response, max_chars: Optional[int]) -> tuple[str, bool]:
    """Return (escaped_pretty_text, truncated)."""
    if response is None:
        return "(no body)", False
    try:
        text = json.dumps(response, indent=2, ensure_ascii=False)
    except (TypeError, ValueError):
        text = str(response)
    truncated = False
    if max_chars is not None and len(text) > max_chars:
        text = text[:max_chars]
        truncated = True
    return html.escape(text), truncated


def build_report(captures_dir: Path, max_chars: Optional[int]) -> tuple[str, Counter, int]:
    """Return (html_string, status_counter, capture_count)."""
    # device -> category -> module -> list of path entries
    tree: dict[str, dict[str, dict[str, list[dict]]]] = {}
    status_counts: Counter = Counter()
    devices_meta: dict[str, dict] = {}
    total = 0

    for _cap, record in _iter_captures(captures_dir):
        total += 1
        device = str(record.get("device", "?"))
        category = str(record.get("category", "?"))
        module = str(record.get("module", "?"))
        status = record.get("http_status")
        status_counts[_status_class(status)] += 1
        devices_meta.setdefault(
            device,
            {
                "pid": record.get("pid", "unknown"),
                "os_version": record.get("os_version", "unknown"),
                "host": record.get("host", "?"),
            },
        )
        body, truncated = _render_response(record.get("response"), max_chars)
        tree.setdefault(device, {}).setdefault(category, {}).setdefault(module, []).append(
            {
                "path": str(record.get("path", "?")),
                "status": status,
                "status_class": _status_class(status),
                "fetched_at": str(record.get("fetched_at", "")),
                "restconf_url": str(record.get("restconf_url", "")),
                "error": record.get("error"),
                "body": body,
                "truncated": truncated,
            }
        )

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    parts: list[str] = []
    parts.append(_HTML_HEAD)
    parts.append("<header>")
    parts.append("<h1>RESTCONF capture report</h1>")
    parts.append(
        f'<p class="meta">Generated {html.escape(generated)} &middot; '
        f"{total} capture(s) &middot; "
        f'<span class="badge ok">200: {status_counts["ok"]}</span> '
        f'<span class="badge missing">404: {status_counts["missing"]}</span> '
        f'<span class="badge err">5xx: {status_counts["err"]}</span> '
        f'<span class="badge other">other: {status_counts["other"]}</span></p>'
    )
    parts.append(
        '<p class="warn">Local review only &mdash; contains device-real data. '
        "Gitignored; do not commit.</p>"
    )
    parts.append(
        '<input id="filter" type="text" placeholder="Filter by module or path\u2026" '
        'oninput="applyFilter()" autocomplete="off">'
    )
    parts.append("</header>")

    for device in sorted(tree):
        meta = devices_meta.get(device, {})
        parts.append('<details class="device" open>')
        parts.append(
            f"<summary><b>{html.escape(device)}</b> "
            f'<span class="tag">{html.escape(str(meta.get("pid", "")))}</span> '
            f'<span class="tag">IOS XE {html.escape(str(meta.get("os_version", "")))}</span> '
            f'<span class="tag">{html.escape(str(meta.get("host", "")))}</span></summary>'
        )
        for category in sorted(tree[device]):
            parts.append('<details class="category" open>')
            parts.append(f"<summary>{html.escape(category)}</summary>")
            for module in sorted(tree[device][category]):
                entries = sorted(tree[device][category][module], key=lambda e: e["path"])
                parts.append('<details class="module">')
                parts.append(
                    f'<summary class="row" data-search="{html.escape(module.lower())}">'
                    f"{html.escape(module)} "
                    f'<span class="count">({len(entries)})</span></summary>'
                )
                for e in entries:
                    hay = f'{module} {e["path"]}'.lower()
                    parts.append(f'<details class="path" data-search="{html.escape(hay)}">')
                    badge = f'<span class="badge {e["status_class"]}">{html.escape(str(e["status"]))}</span>'
                    trunc = ' <span class="tag">truncated</span>' if e["truncated"] else ""
                    parts.append(
                        f'<summary class="row">{badge} <code>{html.escape(e["path"])}</code>{trunc}</summary>'
                    )
                    parts.append('<div class="detail">')
                    if e["restconf_url"]:
                        parts.append(f'<div class="url">{html.escape(e["restconf_url"])}</div>')
                    if e["fetched_at"]:
                        parts.append(f'<div class="when">fetched {html.escape(e["fetched_at"])}</div>')
                    if e["error"]:
                        parts.append(f'<div class="error">error: {html.escape(str(e["error"]))}</div>')
                    parts.append(f"<pre>{e['body']}</pre>")
                    parts.append("</div></details>")
                parts.append("</details>")
            parts.append("</details>")
        parts.append("</details>")

    parts.append(_HTML_TAIL)
    return "\n".join(parts), status_counts, total


_HTML_HEAD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RESTCONF capture report</title>
<style>
:root { color-scheme: light dark; }
body { font: 14px/1.5 -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; padding: 0 1rem 3rem; }
header { position: sticky; top: 0; background: Canvas; padding: 1rem 0; border-bottom: 1px solid #8884; z-index: 1; }
h1 { margin: 0 0 .25rem; font-size: 1.3rem; }
.meta { margin: .25rem 0; color: #6667; }
.warn { margin: .25rem 0; color: #b45309; font-weight: 600; }
#filter { width: 100%; box-sizing: border-box; padding: .5rem .6rem; margin-top: .5rem;
          border: 1px solid #8886; border-radius: 6px; background: Canvas; color: CanvasText; }
details { margin-left: .5rem; }
details.device { margin: .75rem 0 0; }
summary { cursor: pointer; padding: .2rem 0; }
summary.row { white-space: nowrap; overflow-x: auto; }
code { font: 12px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace; }
.detail { margin: .25rem 0 .5rem 1.25rem; }
.url { font: 11px/1.3 ui-monospace, monospace; color: #6a7; word-break: break-all; }
.when { font-size: 11px; color: #6667; }
.error { color: #dc2626; font-size: 12px; }
pre { background: #8881; padding: .5rem .6rem; border-radius: 6px; overflow-x: auto;
      font: 12px/1.45 ui-monospace, monospace; max-height: 60vh; }
.badge { display: inline-block; min-width: 2.4em; text-align: center; padding: 0 .4em;
         border-radius: 4px; font-size: 11px; font-weight: 700; }
.badge.ok { background: #16a34a22; color: #16a34a; }
.badge.missing { background: #f59e0b22; color: #b45309; }
.badge.err { background: #dc262622; color: #dc2626; }
.badge.other { background: #8882; color: inherit; }
.tag { display: inline-block; background: #8882; border-radius: 4px; padding: 0 .4em;
       font-size: 11px; margin-left: .25rem; }
.count { color: #6667; font-size: 12px; }
.hidden { display: none; }
</style></head><body>"""

_HTML_TAIL = """<script>
function applyFilter() {
  var q = document.getElementById('filter').value.trim().toLowerCase();
  var paths = document.querySelectorAll('details.path');
  paths.forEach(function (p) {
    var hay = p.getAttribute('data-search') || '';
    p.classList.toggle('hidden', q && hay.indexOf(q) === -1);
  });
  // Hide modules/categories/devices with no visible paths.
  document.querySelectorAll('details.module').forEach(function (m) {
    var any = m.querySelectorAll('details.path:not(.hidden)').length > 0;
    m.classList.toggle('hidden', !!q && !any);
    if (q && any) m.open = true;
  });
  ['category', 'device'].forEach(function (cls) {
    document.querySelectorAll('details.' + cls).forEach(function (c) {
      var any = c.querySelectorAll('details.path:not(.hidden)').length > 0;
      c.classList.toggle('hidden', !!q && !any);
    });
  });
}
</script></body></html>"""


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--captures", help="Captures dir (default scripts/harness/captures)")
    ap.add_argument("--out", help="Output HTML path (default scripts/harness/capture-report.html)")
    ap.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"Cap chars per response body (default {DEFAULT_MAX_CHARS}; 0 = no cap)",
    )
    ap.add_argument("--full", action="store_true", help="No per-response size cap (alias for --max-chars 0)")
    ap.add_argument("--open", dest="open_browser", action="store_true", help="Open the report after writing")
    args = ap.parse_args(argv)

    captures_dir = Path(args.captures) if args.captures else CAPTURES_DIR
    out_path = Path(args.out) if args.out else REPORT_PATH
    max_chars: Optional[int] = None if (args.full or args.max_chars == 0) else args.max_chars

    if not captures_dir.is_dir():
        print(f"No captures dir yet: {captures_dir}. Run the collector first.", file=sys.stderr)
        return 2

    html_str, status_counts, total = build_report(captures_dir, max_chars)
    if total == 0:
        print(f"No captures found under {captures_dir}. Run the collector first.", file=sys.stderr)
        return 2

    out_path.write_text(html_str, encoding="utf-8")
    print(
        f"Wrote {out_path} ({total} capture(s): "
        f"200={status_counts['ok']} 404={status_counts['missing']} "
        f"5xx={status_counts['err']} other={status_counts['other']})"
    )
    if args.open_browser:
        webbrowser.open(out_path.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
