#!/usr/bin/env python3
"""
generate_all_pyang_trees.py — Per-release pyang tree generator with skip audit.

Walks every YANG module under ``references/<version>/`` and produces a tree HTML
under ``releases/<version>/yang-trees/<module>.html``. Modules that legitimately
have no tree structure (types-only, deviation-only, augment-only, submodules,
framework modules) are recorded in ``releases/<version>/tree_audit.json`` with
the reason. CI uses that audit to allow tree-coverage gaps without false-failing.

Authoritative spec: VERSIONING.md §9 (CI gates), MDT_XPATH_SPEC.md (consumed by
annotate_mdt_xpaths.py to confirm prefixes from these trees).

Usage:
    python scripts/generate_all_pyang_trees.py --version 26.1.1
    python scripts/generate_all_pyang_trees.py --version 26.1.1 --include-mibs
    python scripts/generate_all_pyang_trees.py --all     # iterate releases/index.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RELEASES_INDEX = PROJECT_ROOT / "releases" / "index.json"

# Regex helpers for skip detection (parsed from raw YANG, before pyang).
RE_SUBMODULE = re.compile(r"^\s*submodule\s+", re.MULTILINE)
RE_TYPEDEF = re.compile(r"^\s*typedef\s+", re.MULTILINE)
RE_DEVIATION = re.compile(r"^\s*deviation\s+", re.MULTILINE)
RE_AUGMENT = re.compile(r"^\s*augment\s+", re.MULTILINE)
RE_DATA_NODES = re.compile(
    r"^\s*(container|list|leaf|leaf-list|choice|case|action|rpc|notification)\s+",
    re.MULTILINE,
)


def classify_skip_reason(yang_text: str, tree_output: str) -> str | None:
    """Return a documented skip reason if the module shouldn't have a tree, else None."""
    if RE_SUBMODULE.search(yang_text):
        return "submodule"
    has_data = bool(RE_DATA_NODES.search(yang_text))
    if not has_data:
        if RE_TYPEDEF.search(yang_text):
            return "types-only"
        if RE_DEVIATION.search(yang_text) and not RE_AUGMENT.search(yang_text):
            return "deviation-only"
        if RE_AUGMENT.search(yang_text):
            return "augment-only"
    if not tree_output.strip() or len(tree_output.strip()) < 50:
        return "empty-tree"
    return None


def get_swagger_category(module_name: str) -> tuple[str, str]:
    """Match the convention used by the legacy generate_pyang_trees.py."""
    n = module_name
    low = n.lower()
    if low.endswith("-oper"):
        return "swagger-oper-model", "Operational State APIs"
    if low.endswith("-rpc"):
        return "swagger-rpc-model", "RPC APIs"
    if low.endswith("-events"):
        return "swagger-events-model", "Event/Telemetry APIs"
    if low.endswith("-cfg"):
        return "swagger-cfg-model", "Configuration APIs"
    if low.startswith("ietf-"):
        return "swagger-ietf-model", "IETF Standard APIs"
    if low.startswith("openconfig-"):
        return "swagger-openconfig-model", "OpenConfig APIs"
    if n == "Cisco-IOS-XE-native":
        return "swagger-native-config-model", "Native Config APIs"
    if low.endswith("-mib") or low.startswith("cisco-") and "-mib" in low:
        return "swagger-mib-model", "MIB YANG APIs"
    return "swagger-other-model", "Other/Vendor APIs"


def render_tree_html(module: str, version: str, tree_text: str) -> str:
    """Render a single tree HTML page. Pages live at releases/<ver>/yang-trees/."""
    swagger_dir, swagger_label = get_swagger_category(module)
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"UTF-8\">
<title>{module} — YANG Tree ({version})</title>
<style>
body {{ font-family: 'Courier New', monospace; background:#f5f5f5; padding:20px; margin:0; }}
.header {{ background:linear-gradient(135deg,#049fd9,#0070c9); color:#fff; padding:20px; border-radius:8px; margin-bottom:20px; }}
.header h1 {{ margin:0 0 6px 0; font-size:22px; }}
.header p {{ margin:0; opacity:.9; font-size:13px; }}
.header a {{ color:#fff; }}
.nav {{ background:#e3f2fd; padding:14px; border-radius:8px; border-left:4px solid #0070c9; margin-bottom:20px; display:flex; gap:10px; flex-wrap:wrap; }}
.nav a {{ background:#0070c9; color:#fff; padding:6px 12px; border-radius:4px; text-decoration:none; font-size:13px; }}
.nav a.alt {{ background:#fff; color:#0070c9; border:1px solid #cfd8dc; }}
.tree {{ background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,.08); overflow-x:auto; }}
pre {{ font-size:13px; line-height:1.4; margin:0; color:#333; }}
.footer {{ margin-top:18px; padding:12px; background:#fff; border-radius:8px; text-align:center; font-size:12px; color:#666; }}
</style>
</head>
<body>
<div class=\"header\">
  <h1>{module}</h1>
  <p>YANG tree — IOS-XE {version}</p>
</div>
<div class=\"nav\">
  <a href=\"../{swagger_dir}/index-v2.html#ver={version}&amp;spec={swagger_dir}/{module}\">📄 OpenAPI Spec</a>
  <a class=\"alt\" href=\"../{swagger_dir}/index-v2.html#ver={version}\">📂 {swagger_label}</a>
  <a class=\"alt\" href=\"index.html\">🌳 All Trees ({version})</a>
  <a class=\"alt\" href=\"../../index.html\">🏠 Hub</a>
</div>
<div class=\"tree\"><pre>{tree_text}</pre></div>
<div class=\"footer\">Generated with pyang · IOS-XE {version}</div>
</body>
</html>
"""


def render_index_html(version: str, modules: list[str]) -> str:
    cards = "\n".join(
        f'<div class="card"><a href="{m}.html">{m}</a></div>' for m in sorted(modules)
    )
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"UTF-8\">
<title>YANG Tree Browser — IOS-XE {version}</title>
<style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#f5f5f5;padding:20px;margin:0;}}
.header{{background:linear-gradient(135deg,#049fd9,#0070c9);color:#fff;padding:24px;border-radius:8px;margin-bottom:20px;}}
.header h1{{margin:0 0 8px 0}}
.search{{padding:10px 14px;border-radius:6px;border:none;width:100%;max-width:520px;margin-top:12px;font-size:15px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}}
.card{{background:#fff;padding:12px;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.card a{{color:#0070c9;text-decoration:none;font-size:13px}}
</style>
</head>
<body>
<div class=\"header\">
  <h1>📊 YANG Tree Browser</h1>
  <p>IOS-XE {version} — {len(modules)} modules with tree structure</p>
  <input class=\"search\" id=\"q\" placeholder=\"Filter modules…\" oninput=\"f()\">
</div>
<div class=\"grid\" id=\"g\">
{cards}
</div>
<script>
function f(){{
  const q=document.getElementById('q').value.toLowerCase();
  document.querySelectorAll('.card').forEach(c=>{{
    c.style.display=c.textContent.toLowerCase().includes(q)?'block':'none';
  }});
}}
</script>
</body>
</html>
"""


def generate_one(yang_file: Path, out_dir: Path, version: str) -> dict:
    module = yang_file.stem
    yang_text = yang_file.read_text(encoding="utf-8", errors="replace")
    try:
        proc = subprocess.run(
            ["pyang", "-f", "tree", str(yang_file)],
            cwd=yang_file.parent,
            capture_output=True, text=True, encoding="utf-8",
        )
    except FileNotFoundError:
        return {"module": module, "status": "skipped", "reason": "pyang-not-installed"}

    tree = proc.stdout or ""
    skip = classify_skip_reason(yang_text, tree)
    if skip:
        return {"module": module, "status": "skipped", "reason": skip}

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{module}.html").write_text(
        render_tree_html(module, version, tree),
        encoding="utf-8",
    )
    return {"module": module, "status": "generated", "reason": None}


def generate_for_version(version: str) -> int:
    src_dir = PROJECT_ROOT / "references" / version
    if not src_dir.is_dir():
        # Fall back to legacy 17.18.1 layout if user hasn't migrated yet.
        legacy = PROJECT_ROOT / "references" / "17181-YANG-modules"
        if version == "17.18.1" and legacy.is_dir():
            src_dir = legacy
        else:
            sys.stderr.write(
                f"[trees] no YANG sources for {version} — expected {src_dir}.\n"
                f"        run scripts/fetch_yang_release.py --version {version} first\n"
            )
            return 1

    out_dir = PROJECT_ROOT / "releases" / version / "yang-trees"
    audit = {
        "version": version,
        "generated": datetime.now(timezone.utc).replace(microsecond=0)
            .isoformat().replace("+00:00", "Z"),
        "results": [],
    }

    yang_files = sorted(src_dir.glob("*.yang"))
    print(f"[trees] {version}: {len(yang_files)} YANG files → {out_dir}")
    generated: list[str] = []
    for f in yang_files:
        r = generate_one(f, out_dir, version)
        audit["results"].append(r)
        if r["status"] == "generated":
            generated.append(r["module"])
        elif r["reason"] == "pyang-not-installed":
            sys.stderr.write("[trees] pyang not installed; aborting.\n")
            return 2

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(
        render_index_html(version, generated), encoding="utf-8"
    )

    audit_path = PROJECT_ROOT / "releases" / version / "tree_audit.json"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    skipped = [r for r in audit["results"] if r["status"] == "skipped"]
    print(f"[trees] {version}: generated={len(generated)} skipped={len(skipped)}")
    by_reason: dict[str, int] = {}
    for r in skipped:
        by_reason[r["reason"]] = by_reason.get(r["reason"], 0) + 1
    for reason, n in sorted(by_reason.items()):
        print(f"        ↳ {reason}: {n}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--version", help="Single release to process (e.g. 26.1.1)")
    g.add_argument("--all", action="store_true",
                   help="Process every release listed in releases/index.json")
    args = parser.parse_args()

    if args.version:
        return generate_for_version(args.version)

    if not RELEASES_INDEX.is_file():
        sys.stderr.write(f"[trees] missing {RELEASES_INDEX}\n")
        return 1
    idx = json.loads(RELEASES_INDEX.read_text(encoding="utf-8"))
    rc = 0
    for entry in idx.get("releases", []):
        ver = entry["ver"]
        if entry.get("status") not in ("active", None):
            print(f"[trees] {ver}: status={entry.get('status')}, skipping.")
            continue
        rc = generate_for_version(ver) or rc
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
