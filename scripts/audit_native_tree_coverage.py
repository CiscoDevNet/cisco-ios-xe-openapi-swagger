#!/usr/bin/env python3
"""audit_native_tree_coverage.py

Deep coverage audit: compare the *resolved* Cisco-IOS-XE-native YANG tree
against the RESTCONF paths actually emitted by the split
swagger-native-config-model specs.

Unlike scripts/check_native_coverage.py (which only checks the 264 top-level
/native children), this walks the ENTIRE tree at full depth and asserts that
every addressable **container** and **list** node maps to at least one API
path. This quantifies exactly what the generator's depth cap omits.

Method (apples-to-apples):
  * Reuse the generator's own parser (generators/generate_native_from_tree.py
    :: parse_yang_tree_html) so the tree is interpreted identically.
  * Tree side: walk every node; collect the name-path of each container/list.
    choice/case nodes are structural (not addressable) and are flattened —
    their children attach to the nearest real ancestor, mirroring the
    generator.
  * API side: load every native-*.json, take each path key, strip the
    /data/Cisco-IOS-XE-native:native/ prefix, drop ={key} predicates and
    Module:prefixes, and record the segment tuple plus every prefix (an
    ancestor segment is "covered" if it appears on the way to a deeper path).
  * A tree container/list is COVERED iff its segment tuple is an API path or a
    prefix of one. Everything else is a GAP.

Exit codes:
    0  no gaps (or --warn-only)
    1  gaps found — report printed
    2  input files missing

Usage:
    # Default: full depth, interface excluded by design.
    python -X utf8 scripts/audit_native_tree_coverage.py --version 26.1.1
    # Low-noise regression view: only nodes the generator emits as standalone
    # paths (depth <= 5), interface excluded.
    python -X utf8 scripts/audit_native_tree_coverage.py --version 26.1.1 --max-depth 5
    python -X utf8 scripts/audit_native_tree_coverage.py --all
    python -X utf8 scripts/audit_native_tree_coverage.py --version 26.1.1 \
        --json releases/26.1.1/native_tree_coverage.json

The `interface` mega-container expands every interface TYPE (GigabitEthernet,
TenGigabitEthernet, Loopback, ...) into ~37k nodes. Modelling each as its own
API is an intentional design decision NOT to do, so `interface` is excluded by
default (override with --exclude).
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
RELEASES = ["17.9.x", "17.12.x", "17.15.x", "17.18.1", "26.1.1"]
NATIVE_PREFIX = "/data/Cisco-IOS-XE-native:native"


def _load_generator():
    """Import parse_yang_tree_html from the native tree generator without
    triggering its __main__ side effects."""
    gen_path = ROOT / "generators" / "generate_native_from_tree.py"
    spec = importlib.util.spec_from_file_location("_native_tree_gen", gen_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {gen_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tree_root_from_html(gen, html_path: Path):
    """Return the parsed root TreeNode for a native tree HTML, tolerating both
    the original two-<pre> layout the generator consumed and the published
    single-<pre> release layout (header/nav wrapper). The YANG tree is always
    the LAST <pre> block; normalize to the two-<pre> form the generator parser
    expects and parse via a temp file."""
    content = html_path.read_text(encoding="utf-8", errors="replace")
    pre_blocks = re.findall(r"<pre[^>]*>(.*?)</pre>", content, re.DOTALL)
    if not pre_blocks:
        raise ValueError(f"no <pre> tree block in {html_path}")
    tree_block = pre_blocks[-1]
    normalized = f"<pre>legend</pre>\n<pre>{tree_block}</pre>\n"
    tmp_dir = ROOT / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", suffix=".html", dir=str(tmp_dir), delete=False
    ) as tf:
        tf.write(normalized)
        tmp_path = tf.name
    try:
        return gen.parse_yang_tree_html(tmp_path)
    finally:
        try:
            Path(tmp_path).unlink()
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Tree side: every container/list node as a segment tuple from /native down.
# ---------------------------------------------------------------------------
def collect_tree_nodes(node, prefix: tuple[str, ...], out: dict[tuple, str]) -> None:
    """Populate ``out`` mapping segment-tuple -> node_type for every
    container/list descendant. choice/case are flattened (no segment added)."""
    for child in node.children:
        nt = child.node_type
        if nt in ("choice", "case"):
            # Structural: descend without adding a path segment.
            collect_tree_nodes(child, prefix, out)
            continue
        seg = prefix + (child.name,)
        if nt in ("container", "list"):
            # First writer wins, but prefer 'list' label if seen both.
            if seg not in out or nt == "list":
                out[seg] = nt
            collect_tree_nodes(child, seg, out)
        else:
            # leaf / leaf-list: not a standalone resource for this audit, but
            # descend anyway in case the parser nested anything under it.
            collect_tree_nodes(child, seg, out)


# ---------------------------------------------------------------------------
# API side: every native-*.json path -> segment tuple + all prefixes.
# ---------------------------------------------------------------------------
def _norm_segment(seg: str) -> str:
    # Drop list key predicate: "GigabitEthernet={name}" -> "GigabitEthernet".
    if "=" in seg:
        seg = seg.split("=", 1)[0]
    # Drop module prefix: "Cisco-IOS-XE-foo:bar" -> "bar".
    if ":" in seg:
        seg = seg.split(":", 1)[-1]
    return seg


def collect_api_prefixes(api_dir: Path) -> set[tuple[str, ...]]:
    covered: set[tuple[str, ...]] = set()
    for fp in sorted(glob.glob(str(api_dir / "native-*.json"))):
        try:
            spec = json.loads(Path(fp).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for p in spec.get("paths", {}).keys():
            if not p.startswith(NATIVE_PREFIX):
                continue
            tail = p[len(NATIVE_PREFIX):].lstrip("/")
            if not tail:
                continue
            segs = tuple(_norm_segment(s) for s in tail.split("/") if s)
            # Record the full segment tuple and every ancestor prefix.
            for i in range(1, len(segs) + 1):
                covered.add(segs[:i])
    return covered


def audit_release(version: str, gen, max_depth: Optional[int],
                  exclude: set[str]) -> tuple[int, dict]:
    tree_html = ROOT / "releases" / version / "yang-trees" / "Cisco-IOS-XE-native.html"
    api_dir = ROOT / "releases" / version / "swagger-native-config-model" / "api"
    if not tree_html.is_file():
        sys.stderr.write(f"[{version}] missing tree HTML: {tree_html}\n")
        return 2, {}
    if not api_dir.is_dir():
        sys.stderr.write(f"[{version}] missing api dir: {api_dir}\n")
        return 2, {}

    root = _tree_root_from_html(gen, tree_html)
    all_tree_nodes: dict[tuple, str] = {}
    collect_tree_nodes(root, (), all_tree_nodes)

    # Apply scope filters:
    #  * exclude: top-level containers intentionally not modelled as their own
    #    APIs (default {"interface"} — the per-type interface explosion of
    #    ~37k nodes is excluded by design, not a generator bug).
    #  * max_depth: count only nodes at or above this tree depth, matching the
    #    generator's standalone-path depth cap (collect_deep_paths max_depth=5).
    #    Deeper nodes still live inside a parent path's body schema, so they are
    #    addressable, just not standalone paths. Use this for the low-noise,
    #    regression-catching view.
    tree_nodes = {
        seg: nt for seg, nt in all_tree_nodes.items()
        if seg[0] not in exclude
        and (max_depth is None or len(seg) <= max_depth)
    }

    api_prefixes = collect_api_prefixes(api_dir)

    missing = sorted(seg for seg in tree_nodes if seg not in api_prefixes)
    covered_n = len(tree_nodes) - len(missing)
    total = len(tree_nodes)
    pct = (covered_n / total * 100.0) if total else 100.0

    # Group missing by top-level container for a readable report.
    by_top: dict[str, int] = {}
    for seg in missing:
        by_top[seg[0]] = by_top.get(seg[0], 0) + 1

    result = {
        "version": version,
        "max_depth": max_depth,
        "excluded_top_level": sorted(exclude),
        "tree_container_list_nodes": total,
        "covered": covered_n,
        "missing": len(missing),
        "coverage_pct": round(pct, 2),
        "missing_by_top_level": dict(sorted(by_top.items(), key=lambda kv: -kv[1])),
        "missing_paths": ["/".join(seg) for seg in missing],
    }
    return (1 if missing else 0), result


def _print_report(res: dict, sample: int) -> None:
    v = res["version"]
    scope = []
    if res.get("excluded_top_level"):
        scope.append("excl " + ",".join(res["excluded_top_level"]))
    scope.append(f"max_depth={res.get('max_depth') or 'full'}")
    print(f"\n[{v}] Native tree -> API deep coverage  ({'; '.join(scope)})")
    print(f"  container/list nodes in tree : {res['tree_container_list_nodes']}")
    print(f"  covered by an API path       : {res['covered']}")
    print(f"  missing (no API path)        : {res['missing']}")
    print(f"  coverage                     : {res['coverage_pct']}%")
    if res["missing"]:
        print(f"  missing by top-level container (top 15):")
        for name, n in list(res["missing_by_top_level"].items())[:15]:
            print(f"    {name:<28} {n}")
        if sample > 0:
            print(f"  sample missing paths (first {sample}):")
            for mp in res["missing_paths"][:sample]:
                print(f"    /native/{mp}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", help="single release, e.g. 26.1.1")
    ap.add_argument("--all", action="store_true", help="audit every release")
    ap.add_argument("--json", help="write full JSON result to this path (single --version only)")
    ap.add_argument("--sample", type=int, default=25, help="how many missing paths to print")
    ap.add_argument("--max-depth", type=int, default=None,
                    help="only count tree nodes at or above this depth (matches the "
                         "generator's standalone-path cap, e.g. 5 for the low-noise "
                         "regression view). Default: full depth.")
    ap.add_argument("--exclude", default="interface",
                    help="comma-separated top-level /native containers to exclude as "
                         "intentionally-not-modelled (default: interface). Pass '' to "
                         "exclude nothing.")
    ap.add_argument("--warn-only", action="store_true", help="report gaps but exit 0")
    args = ap.parse_args()

    versions = RELEASES if args.all else [args.version or "26.1.1"]
    exclude = {s.strip() for s in args.exclude.split(",") if s.strip()}
    gen = _load_generator()

    worst_rc = 0
    last_result: Optional[dict] = None
    for v in versions:
        rc, res = audit_release(v, gen, args.max_depth, exclude)
        if rc == 2:
            worst_rc = max(worst_rc, 2)
            continue
        last_result = res
        _print_report(res, args.sample)
        worst_rc = max(worst_rc, rc)

    if args.json and last_result is not None and not args.all:
        out = Path(args.json).resolve()
        out.write_text(json.dumps(last_result, indent=2) + "\n", encoding="utf-8")
        try:
            shown = out.relative_to(ROOT)
        except ValueError:
            shown = out
        print(f"\n  wrote {shown}")

    if args.warn_only and worst_rc == 1:
        sys.stderr.write("[audit_native_tree_coverage] --warn-only: gaps present but exit 0\n")
        return 0
    return worst_rc


if __name__ == "__main__":
    raise SystemExit(main())
