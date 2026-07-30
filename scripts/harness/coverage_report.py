"""Generate a publishable coverage report from the captures (Track B).

Reads the local captures and produces a per-category, per-module coverage
report answering "which YANG modules/paths return data on this platform, and
which return none" — the kind of platform-capability matrix intended for the
public docs site. It emits BOTH:

  * scripts/harness/coverage-report.md   (human-readable, publishable)
  * scripts/harness/coverage-report.json (structured, for the web app)

Only capability metadata is written (device PID, OS version, module/path names,
result status, response sizes) — never the device management IP/host and never
raw response bodies, so the report is safe to publish. (Raw captures stay local
and gitignored.)

Important platform note baked into the report: on IOS XE a GET of a parent
container does NOT return all descendant data — many nodes only materialize on a
direct GET of that container, and deeper still. So per-container/depth scanning
is required for true coverage; a single root GET undercounts.

Run:  python -X utf8 -m scripts.harness.coverage_report
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

HARNESS_DIR = Path(__file__).resolve().parent
CAPTURES_DIR = HARNESS_DIR / "captures"
MD_PATH = HARNESS_DIR / "coverage-report.md"
JSON_PATH = HARNESS_DIR / "coverage-report.json"
HTML_PATH = HARNESS_DIR / "coverage-report.html"
# Relative URL prefix under which the raw captures are served next to the report
# (a symlink/copy of scripts/harness/captures). Used to link each path to its
# captured API response.
CAPTURES_URL_PREFIX = "captures"

CATEGORY_ORDER = ["oper", "mib", "cfg", "native-config"]


def _classify_module(statuses: dict) -> str:
    """Bucket a module by the statuses seen across its captured paths."""
    if statuses.get(200):
        return "data"
    if statuses.get("error"):
        return "error"
    if statuses.get(204):
        return "empty"
    if statuses.get(404):
        return "not-present"
    return "other"


def collect(captures_dir: Path) -> dict:
    """Aggregate captures into a coverage structure (no raw data, no host/IP)."""
    device_meta = {}
    # category -> module -> {status_counts, data_paths, bytes}
    cats: dict = defaultdict(lambda: defaultdict(lambda: {
        "status": defaultdict(int), "data_paths": 0, "bytes": 0, "lines": 0, "paths": [],
    }))
    for cap in sorted(captures_dir.glob("*/*/*.json")):
        try:
            r = json.loads(cap.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        device_meta.setdefault("pid", r.get("pid"))
        device_meta.setdefault("os_version", r.get("os_version"))
        device_meta.setdefault("device", r.get("device"))
        cat = r.get("category", "?")
        mod = r.get("module", "?")
        st = "error" if r.get("error") else r.get("http_status")
        entry = cats[cat][mod]
        entry["status"][st] += 1
        if st == 200:
            entry["data_paths"] += 1
            resp = r.get("response")
            if resp is not None:
                b = len(json.dumps(resp))
                ln = json.dumps(resp, indent=2).count("\n") + 1
                entry["bytes"] += b
                entry["lines"] += ln  # pretty-printed JSON line count of the payload
                entry["paths"].append({"path": r.get("path"), "lines": ln, "bytes": b})
    return {"device": device_meta, "categories": cats}


def summarize(data: dict) -> dict:
    """Build a serializable summary with per-module classification."""
    out = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "device_pid": data["device"].get("pid"),
        "device_name": data["device"].get("device"),
        "os_version": data["device"].get("os_version"),
        "categories": {},
        "totals": {"modules": 0, "with_data": 0, "zero_data": 0, "data_paths": 0, "lines": 0, "bytes": 0},
    }
    cats = data["categories"]
    for cat in list(CATEGORY_ORDER) + [c for c in cats if c not in CATEGORY_ORDER]:
        if cat not in cats:
            continue
        mods = cats[cat]
        with_data, zero, dpaths, cbytes, clines = [], [], 0, 0, 0
        module_rows = []
        for mod in sorted(mods):
            e = mods[mod]
            cls = _classify_module(e["status"])
            row = {
                "module": mod, "class": cls,
                "data_paths": e["data_paths"], "lines": e["lines"], "bytes": e["bytes"],
                "paths": sorted(e["paths"], key=lambda p: -p["bytes"]),
                "status": {str(k): v for k, v in e["status"].items()},
            }
            module_rows.append(row)
            dpaths += e["data_paths"]; cbytes += e["bytes"]; clines += e["lines"]
            (with_data if cls == "data" else zero).append(mod)
        out["categories"][cat] = {
            "modules": len(mods),
            "with_data": len(with_data),
            "zero_data": len(zero),
            "data_paths": dpaths,
            "lines": clines,
            "bytes": cbytes,
            "module_rows": module_rows,
        }
        t = out["totals"]
        t["modules"] += len(mods); t["with_data"] += len(with_data)
        t["zero_data"] += len(zero); t["data_paths"] += dpaths
        t["lines"] += clines; t["bytes"] += cbytes
    return out


def render_markdown(s: dict) -> str:
    L = []
    L.append("# RESTCONF Data Coverage Report")
    L.append("")
    L.append(f"- **Device model (PID):** `{s['device_pid']}`")
    L.append(f"- **IOS XE version:** `{s['os_version']}`")
    L.append(f"- **Generated:** {s['generated_at']}")
    L.append(f"- **Transport:** RESTCONF GET (read-only)")
    L.append("")
    L.append("> **Platform note:** On IOS XE a GET of a parent container does not "
             "return all descendant data — many nodes only materialize on a direct "
             "GET of that container, and deeper still. Coverage below reflects "
             "per-container/depth scanning; a single root GET undercounts.")
    L.append("")
    t = s["totals"]
    L.append("## Summary")
    L.append("")
    L.append("| Category | Modules | With data | 0 data | Data paths | Lines | Data size |")
    L.append("|---|---:|---:|---:|---:|---:|---:|")
    for cat, c in s["categories"].items():
        L.append(f"| {cat} | {c['modules']} | {c['with_data']} | {c['zero_data']} "
                 f"| {c['data_paths']} | {c['lines']:,} | {c['bytes']/1e6:.2f} MB |")
    L.append(f"| **TOTAL** | **{t['modules']}** | **{t['with_data']}** | **{t['zero_data']}** "
             f"| **{t['data_paths']}** | **{t['lines']:,}** | **{t['bytes']/1e6:.2f} MB** |")
    L.append("")
    for cat, c in s["categories"].items():
        L.append(f"## {cat}")
        L.append("")
        L.append(f"{c['with_data']} of {c['modules']} modules returned data "
                 f"({c['data_paths']} data paths, {c['bytes']/1e6:.2f} MB).")
        L.append("")
        with_data = [r for r in c["module_rows"] if r["class"] == "data"]
        if with_data:
            L.append("### Modules WITH data")
            L.append("")
            L.append("| Module | Data paths | Lines | Size |")
            L.append("|---|---:|---:|---:|")
            for r in sorted(with_data, key=lambda r: -r["bytes"]):
                L.append(f"| `{r['module']}` | {r['data_paths']} | {r['lines']:,} | {r['bytes']:,} B |")
            L.append("")
        zero = [r for r in c["module_rows"] if r["class"] != "data"]
        if zero:
            def label(cls):
                return {"empty": "empty (204)", "not-present": "not present (404)",
                        "error": "error", "other": "other"}.get(cls, cls)
            L.append(f"### Modules with 0 data ({len(zero)})")
            L.append("")
            byclass = defaultdict(list)
            for r in zero:
                byclass[r["class"]].append(r["module"])
            for cls in ("not-present", "empty", "error", "other"):
                if byclass.get(cls):
                    names = ", ".join(f"`{m}`" for m in sorted(byclass[cls]))
                    L.append(f"- **{label(cls)}** ({len(byclass[cls])}): {names}")
            L.append("")
    return "\n".join(L) + "\n"


def render_html(s: dict, captures_dir=None, embed: bool = False) -> str:
    import html as _h

    def esc(x):
        return _h.escape(str(x))

    badge = {"data": "data", "empty": "empty", "not-present": "404",
             "error": "error", "other": "other"}
    t = s["totals"]
    dev = s.get("device_name") or ""
    parts = [_HTML_HEAD]
    parts.append("<header>")
    parts.append("<h1>RESTCONF Data Coverage</h1>")
    parts.append(
        f'<p class="meta"><b>{esc(s["device_pid"])}</b> &middot; IOS XE '
        f'{esc(s["os_version"])} &middot; generated {esc(s["generated_at"])} &middot; '
        f'RESTCONF GET (read-only)</p>'
    )
    parts.append(
        '<p class="note">On IOS XE a GET of a parent container does not return all '
        'descendant data — nodes materialize on direct GETs, and deeper still. '
        'Coverage reflects per-container/depth scanning. Expand any path to view its '
        'captured API response inline.</p>'
    )
    # Summary cards
    parts.append('<div class="cards">')
    parts.append(f'<div class="card"><b>{t["with_data"]}</b><span>modules with data</span></div>')
    parts.append(f'<div class="card"><b>{t["data_paths"]:,}</b><span>data paths</span></div>')
    parts.append(f'<div class="card"><b>{t["lines"]:,}</b><span>lines returned</span></div>')
    parts.append(f'<div class="card"><b>{t["bytes"]/1e6:.2f} MB</b><span>data captured</span></div>')
    parts.append(f'<div class="card"><b>{t["modules"]}</b><span>modules queried</span></div>')
    parts.append('</div>')
    # Controls
    parts.append('<div class="controls">')
    parts.append('<input id="filter" placeholder="Filter modules / paths…" oninput="applyFilter()">')
    parts.append('<span class="legend">show:</span>')
    for cls in ("data", "empty", "not-present", "error"):
        checked = "checked" if cls in ("data", "error") else ""
        parts.append(f'<label class="chip {cls}"><input type="checkbox" {checked} '
                     f'data-cls="{cls}" onchange="applyFilter()"> {badge[cls]}</label>')
    parts.append('</div>')
    parts.append("</header>")

    for cat, c in s["categories"].items():
        parts.append('<details class="cat" open>')
        parts.append(
            f'<summary>{esc(cat)} '
            f'<span class="cc">{c["with_data"]}/{c["modules"]} with data &middot; '
            f'{c["data_paths"]} paths &middot; {c["lines"]:,} lines &middot; '
            f'{c["bytes"]/1e6:.2f} MB</span></summary>')
        for r in sorted(c["module_rows"], key=lambda r: (r["class"] != "data", -r["bytes"], r["module"])):
            cls = r["class"]
            hay = esc(r["module"].lower())
            meta = (f'<span class="b {cls}">{badge[cls]}</span>'
                    f'<span class="n">{r["data_paths"]} paths</span>'
                    f'<span class="n">{r["lines"]:,} ln</span>'
                    f'<span class="n">{r["bytes"]:,} B</span>')
            if r.get("paths"):
                parts.append(f'<details class="mod" data-cls="{cls}" data-hay="{hay}">')
                parts.append(f'<summary><code>{esc(r["module"])}</code> {meta}</summary>')
                parts.append('<div class="paths">')
                for p in r["paths"]:
                    hh = hashlib.sha1(p["path"].encode("utf-8")).hexdigest()[:16]
                    meta_p = f'<span class="n">{p["lines"]:,} ln &middot; {p["bytes"]:,} B</span>'
                    if embed and captures_dir:
                        capf = Path(captures_dir) / dev / cat / f'{r["module"]}__{hh}.json'
                        try:
                            body = json.loads(capf.read_text(encoding="utf-8")).get("response")
                            pretty = esc(json.dumps(body, indent=2))
                        except (json.JSONDecodeError, OSError):
                            pretty = "(response unavailable)"
                        parts.append(
                            f'<details class="presp" data-loaded="1">'
                            f'<summary><code>{esc(p["path"])}</code> {meta_p}</summary>'
                            f'<pre class="respbody">{pretty}</pre></details>'
                        )
                    else:
                        link = f'{CAPTURES_URL_PREFIX}/{esc(dev)}/{esc(cat)}/{esc(r["module"])}__{hh}.json'
                        parts.append(
                            f'<details class="presp" data-src="{link}">'
                            f'<summary><code>{esc(p["path"])}</code> {meta_p}</summary>'
                            f'<pre class="respbody">Expand to load response…</pre></details>'
                        )
                parts.append('</div></details>')
            else:
                parts.append(f'<div class="mod row" data-cls="{cls}" data-hay="{hay}">'
                             f'<code>{esc(r["module"])}</code> {meta}</div>')
        parts.append('</details>')
    parts.append(_HTML_TAIL)
    return "\n".join(parts)


_HTML_HEAD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RESTCONF Data Coverage</title>
<style>
:root{color-scheme:light dark}
body{font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:0 1rem 3rem}
header{position:sticky;top:0;background:Canvas;padding:1rem 0;border-bottom:1px solid #8884;z-index:2}
h1{margin:0 0 .25rem;font-size:1.3rem}
.meta{margin:.15rem 0;color:#888}
.note{margin:.15rem 0;color:#b45309;font-size:12px;max-width:70ch}
.cards{display:flex;gap:.5rem;flex-wrap:wrap;margin:.5rem 0}
.card{background:#8881;border-radius:8px;padding:.4rem .8rem;text-align:center}
.card b{display:block;font-size:1.2rem}
.card span{font-size:11px;color:#888}
.controls{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;margin-top:.5rem}
#filter{flex:1;min-width:200px;padding:.4rem .6rem;border:1px solid #8886;border-radius:6px;background:Canvas;color:CanvasText}
.legend{font-size:12px;color:#888}
.chip{font-size:12px;border:1px solid #8884;border-radius:6px;padding:.1rem .4rem}
details.cat{margin:.6rem 0}
details.cat>summary{font-weight:700;font-size:1.05rem;cursor:pointer;padding:.3rem 0}
.cc{font-weight:400;color:#888;font-size:12px}
.mod{margin:.1rem 0 .1rem 1rem}
.mod>summary,.row{cursor:default;padding:.2rem .4rem;border-radius:6px;display:flex;gap:.5rem;align-items:center;flex-wrap:wrap}
details.mod>summary{cursor:pointer}
.mod:hover>summary,.row:hover{background:#8881}
code{font:12px/1.4 ui-monospace,Menlo,monospace}
.b{font-size:10px;font-weight:700;border-radius:4px;padding:0 .4em;min-width:2.6em;text-align:center}
.b.data{background:#16a34a22;color:#16a34a}
.b.empty{background:#f59e0b22;color:#b45309}
.b.not-present{background:#8882;color:#888}
.b.error{background:#dc262622;color:#dc2626}
.b.other{background:#8882}
.n{font-size:11px;color:#888}
.chip.data{color:#16a34a}.chip.empty{color:#b45309}.chip.not-present{color:#888}.chip.error{color:#dc2626}
table.paths{margin:.2rem 0 .4rem 1.5rem;border-collapse:collapse;font-size:12px}
table.paths th,table.paths td{text-align:left;padding:.1rem .6rem;border-bottom:1px solid #8882}
.paths{margin:.2rem 0 .4rem 1.25rem}
details.presp{margin:.1rem 0}
details.presp>summary{cursor:pointer;padding:.1rem .3rem;border-radius:4px;white-space:nowrap;overflow-x:auto}
details.presp:hover>summary{background:#8881}
details.presp .n{margin-left:.6rem;color:#888;font-size:11px}
pre.respbody{background:#8881;padding:.5rem .6rem;border-radius:6px;overflow:auto;max-height:55vh;font:12px/1.45 ui-monospace,monospace;margin:.2rem 0 .5rem 1rem}
.hidden{display:none}
</style></head><body>"""

_HTML_TAIL = """<script>
function applyFilter(){
  var q=document.getElementById('filter').value.trim().toLowerCase();
  var on={};
  document.querySelectorAll('.chip input').forEach(function(c){on[c.dataset.cls]=c.checked});
  document.querySelectorAll('.mod').forEach(function(m){
    var okCls=on[m.dataset.cls]!==false;
    var okQ=!q||(m.dataset.hay||'').indexOf(q)>-1||(m.textContent||'').toLowerCase().indexOf(q)>-1;
    m.classList.toggle('hidden',!(okCls&&okQ));
  });
  document.querySelectorAll('details.cat').forEach(function(c){
    var any=c.querySelectorAll('.mod:not(.hidden)').length>0;
    c.classList.toggle('hidden',!any);
  });
}
document.addEventListener('DOMContentLoaded', applyFilter);
// Lazy-load a path's captured API response inline when its row is expanded.
document.addEventListener('toggle', function(e){
  var d=e.target;
  if(!(d.classList && d.classList.contains('presp')) || !d.open || d.dataset.loaded) return;
  d.dataset.loaded='1';
  var pre=d.querySelector('.respbody');
  pre.textContent='loading\u2026';
  fetch(d.dataset.src).then(function(r){return r.json();}).then(function(j){
    var body=(j && Object.prototype.hasOwnProperty.call(j,'response'))?j.response:j;
    pre.textContent=JSON.stringify(body,null,2);
  }).catch(function(err){ pre.textContent='error loading response: '+err; });
}, true);
</script></body></html>"""


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--captures", help="Captures dir (default scripts/harness/captures)")
    ap.add_argument("--md", help="Markdown output path (default scripts/harness/coverage-report.md)")
    ap.add_argument("--json", dest="json_out", help="JSON output path (default scripts/harness/coverage-report.json)")
    ap.add_argument("--html", help="HTML output path (default scripts/harness/coverage-report.html)")
    ap.add_argument("--embed", action="store_true", help="Embed captured responses inline — self-contained HTML (no server/captures needed; committable)")
    args = ap.parse_args(argv)

    captures_dir = Path(args.captures) if args.captures else CAPTURES_DIR
    if not captures_dir.is_dir():
        print(f"No captures dir: {captures_dir}. Run the collector first.", file=sys.stderr)
        return 2

    summary = summarize(collect(captures_dir))
    md_path = Path(args.md) if args.md else MD_PATH
    json_path = Path(args.json_out) if args.json_out else JSON_PATH
    html_path = Path(args.html) if args.html else HTML_PATH
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_html(summary, captures_dir=captures_dir, embed=args.embed), encoding="utf-8")
    t = summary["totals"]
    print(f"Coverage report written:\n  {md_path}\n  {json_path}\n  {html_path}")
    print(f"Totals: {t['with_data']}/{t['modules']} modules with data, "
          f"{t['data_paths']} data paths, {t['bytes']/1e6:.2f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
