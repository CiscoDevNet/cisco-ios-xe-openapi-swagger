#!/usr/bin/env python3
"""harvest_native_augments.py

Build the *fully augmented* Cisco-IOS-XE-native tree by merging:

  1. The native module's own resolved tree (releases/<v>/yang-trees/
     Cisco-IOS-XE-native.html) — this already resolves the module's internal
     `uses <grouping>` so containers like ip/line/ipv6 are expanded.
  2. Every `augment /ios:native/...:` subtree contributed by the ~130 external
     Cisco-IOS-XE-*.yang modules. Each augmenting module's own tree HTML
     (releases/<v>/yang-trees/<Module>.html) renders its native-targeting
     augments as `augment /ios:native/ios:<path>:` blocks followed by an
     indented subtree. pyang renders these in the *augmenting* module's tree,
     never inside the native module tree — which is why the shipped native
     specs (and a naive native-tree-only audit) miss them (snmp-server, the
     nat/multicast/igmp/... content under ip, isis/eigrp/ospfv3 under router,
     etc.).

The result is a single TreeNode rooted at `native` whose structure matches the
true RESTCONF surface of the Native datastore.

This module is import-friendly:

    from harvest_native_augments import build_merged_native_tree
    root, stats = build_merged_native_tree("26.1.1")

CLI (diagnostic):

    python -X utf8 scripts/harvest_native_augments.py --version 26.1.1
    python -X utf8 scripts/harvest_native_augments.py --version 26.1.1 \
        --show /native/snmp-server
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import re
import sys
import tempfile
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
RELEASES = ["17.9.x", "17.12.x", "17.15.x", "17.18.1", "26.1.1"]


def _load_tree_gen():
    """Reuse TreeNode + parse_yang_tree_html from the tree generator so the
    native module tree is interpreted identically everywhere."""
    gen_path = ROOT / "generators" / "generate_native_from_tree.py"
    spec = importlib.util.spec_from_file_location("_native_tree_gen", gen_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {gen_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _native_root(gen, html_path: Path):
    """Parse the native module tree, tolerating both the original two-<pre>
    layout the generator expects and the published single-<pre> release layout
    (the tree is always the LAST <pre>). Normalize to two-<pre> via a temp file."""
    content = html_path.read_text(encoding="utf-8", errors="replace")
    pre_blocks = re.findall(r"<pre[^>]*>(.*?)</pre>", content, re.DOTALL)
    if not pre_blocks:
        raise ValueError(f"no <pre> tree block in {html_path}")
    if len(pre_blocks) >= 2:
        return gen.parse_yang_tree_html(str(html_path))
    normalized = f"<pre>legend</pre>\n<pre>{pre_blocks[-1]}</pre>\n"
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
# Generic indented-tree parser (a slice of pyang tree text -> TreeNode list).
# Mirrors the per-line logic in generate_native_from_tree.parse_yang_tree_html
# but operates on an arbitrary block so it can parse augment subtrees whose
# root is the augment target (not the `native` container).
# ---------------------------------------------------------------------------
def _strip_html(pre_block: str) -> list[str]:
    txt = re.sub(r"<[^>]+>", "", pre_block)
    txt = txt.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return txt.split("\n")


def _parse_line(TreeNode, line: str):
    """Return (col, TreeNode) for a single tree line, or None if not a node."""
    case_match = re.search(r"[+o]--:\((\S+)\)", line)
    if case_match:
        col = case_match.start()
        node = TreeNode(case_match.group(1), "rw", "case", depth=0)
        node.raw_name = f":({case_match.group(1)})"
        return col, node

    m = re.search(r"[+o]-+(rw|ro|x)\s+(\S+)(.*)", line)
    if not m:
        return None
    col = m.start()
    rw = m.group(1)
    raw_name = m.group(2)
    rest = m.group(3).strip()

    name = raw_name.rstrip("?").rstrip("!").rstrip("*")
    has_key = bool(re.search(r"\[(\S+)\]", rest))
    is_list = raw_name.rstrip("?").rstrip("!").endswith("*") and has_key

    if is_list:
        node_type, yang_type = "list", ""
    elif raw_name.startswith("(") and (raw_name.endswith(")") or raw_name.endswith(")?")):
        node_type = "choice"
        name = raw_name.strip("()?")
        yang_type = ""
    elif rest and not rest.startswith("[") and not rest.startswith("{"):
        yang_type = rest.split()[0] if rest.split() else "string"
        if raw_name.rstrip("?").rstrip("!").endswith("*") and not has_key:
            node_type = "leaf-list"
        else:
            node_type = "leaf"
    else:
        node_type, yang_type = "container", ""

    node = TreeNode(name, rw, node_type, yang_type, depth=0)
    node.raw_name = raw_name
    return col, node


def _parse_block(TreeNode, lines: list[str], start: int, end: int):
    """Parse lines[start:end] into a synthetic root's children using the
    column-stack algorithm. Returns the synthetic root TreeNode."""
    root = TreeNode("__block__", "rw", "container", depth=0)
    stack: list[tuple[int, object]] = [(-1, root)]
    for i in range(start, end):
        line = lines[i]
        if not line.strip():
            continue
        parsed = _parse_line(TreeNode, line)
        if parsed is None:
            continue
        col, node = parsed
        while len(stack) > 1 and stack[-1][0] >= col:
            stack.pop()
        _, parent = stack[-1]
        parent.children.append(node)
        node.depth = parent.depth + 1
        stack.append((col, node))
    return root


# ---------------------------------------------------------------------------
# Augment harvesting
# ---------------------------------------------------------------------------
_AUG_RE = re.compile(r"augment\s+(/\S*native\S*):")


def _norm_target(raw: str) -> tuple[str, ...]:
    """'/ios:native/ios:ip/ios:multicast' -> ('native','ip','multicast')."""
    segs = []
    for s in raw.split("/"):
        if not s:
            continue
        s = s.split(":", 1)[-1]          # drop module prefix
        s = s.split("=", 1)[0]            # drop any predicate
        segs.append(s)
    return tuple(segs)


def _marker_col(line: str) -> Optional[int]:
    m = re.search(r"[+o]--", line)
    return m.start() if m else None


def harvest_augments(gen, version: str, include_interface: bool):
    """Return list of (target_tuple, [child TreeNode,...]) for every native
    augment across all module tree HTMLs in the release."""
    TreeNode = gen.TreeNode
    tree_dir = ROOT / "releases" / version / "yang-trees"
    results: list[tuple[tuple[str, ...], list]] = []
    files_scanned = 0
    for fp in sorted(glob.glob(str(tree_dir / "Cisco-IOS-XE-*.html"))):
        name = Path(fp).stem
        if name == "Cisco-IOS-XE-native":
            continue  # base tree handled separately
        content = Path(fp).read_text(encoding="utf-8", errors="replace")
        pres = re.findall(r"<pre[^>]*>(.*?)</pre>", content, re.DOTALL)
        if not pres:
            continue
        lines = _strip_html(pres[-1])
        files_scanned += 1
        i = 0
        n = len(lines)
        while i < n:
            am = _AUG_RE.search(lines[i])
            if not am:
                i += 1
                continue
            target = _norm_target(am.group(1))
            header_indent = len(lines[i]) - len(lines[i].lstrip())
            # collect the following indented block until indentation returns to
            # <= header indent on a non-blank, non-tree continuation line.
            j = i + 1
            while j < n:
                ln = lines[j]
                if not ln.strip():
                    j += 1
                    continue
                if _AUG_RE.search(ln):
                    break
                col = _marker_col(ln)
                if col is None:
                    # a non-tree line (e.g. another 'module:'/'submodule' header)
                    if len(ln) - len(ln.lstrip()) <= header_indent:
                        break
                    j += 1
                    continue
                if col <= header_indent:
                    break
                j += 1
            block_root = _parse_block(TreeNode, lines, i + 1, j)
            if block_root.children:
                if not include_interface and len(target) >= 2 and target[1] == "interface":
                    pass  # skip interface-targeting augments
                else:
                    results.append((target, block_root.children))
            i = j
    return results, files_scanned


# ---------------------------------------------------------------------------
# Merge: graft augment children onto the native tree at their target path.
# ---------------------------------------------------------------------------
def _find_path(root, target: tuple[str, ...]):
    """Descend from native root following target[1:] (target[0]=='native').
    Returns the node, or None if the path doesn't exist yet."""
    node = root
    for seg in target[1:]:
        nxt = node.find_child(seg)
        if nxt is None:
            return None
        node = nxt
    return node


def _graft(parent, new_children) -> tuple[int, int]:
    """Merge new_children into parent.children by name. Returns (added,
    merged_existing)."""
    added = merged = 0
    index = {c.name: c for c in parent.children}
    for nc in new_children:
        if nc.name in index:
            # Recursively merge grandchildren into the existing node.
            a, m = _graft(index[nc.name], nc.children)
            added += a
            merged += m + 1
        else:
            parent.children.append(nc)
            index[nc.name] = nc
            added += 1
    return added, merged


def build_merged_native_tree(version: str, include_interface: bool = True):
    """Return (root TreeNode, stats dict) for the fully augmented native tree."""
    gen = _load_tree_gen()
    native_html = ROOT / "releases" / version / "yang-trees" / "Cisco-IOS-XE-native.html"
    if not native_html.is_file():
        raise FileNotFoundError(native_html)
    root = _native_root(gen, native_html)

    augments, files_scanned = harvest_augments(gen, version, include_interface)

    grafted = 0
    unresolved: list[str] = []
    total_added = 0
    for target, children in augments:
        anchor = _find_path(root, target)
        if anchor is None:
            # Target path not present in the native tree yet — create the
            # missing intermediate containers so the augment still lands.
            anchor = root
            for seg in target[1:]:
                nxt = anchor.find_child(seg)
                if nxt is None:
                    nxt = gen.TreeNode(seg, "rw", "container", depth=anchor.depth + 1)
                    anchor.children.append(nxt)
                anchor = nxt
            unresolved.append("/".join(target))
        a, _ = _graft(anchor, children)
        total_added += a
        grafted += 1

    stats = {
        "version": version,
        "include_interface": include_interface,
        "module_trees_scanned": files_scanned,
        "augments_grafted": grafted,
        "augment_targets_created": len(unresolved),
        "nodes_added": total_added,
        "total_descendants": root.descendant_count(),
    }
    return root, stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="26.1.1")
    ap.add_argument("--no-interface", action="store_true",
                    help="skip augments targeting /native/interface/*")
    ap.add_argument("--show", help="print the subtree at this /native/... path")
    args = ap.parse_args()

    root, stats = build_merged_native_tree(
        args.version, include_interface=not args.no_interface)
    print("merged native tree stats:")
    for k, v in stats.items():
        print(f"  {k:<26} {v}")

    if args.show:
        segs = tuple(s for s in args.show.split("/") if s)
        if segs and segs[0] == "native":
            segs = segs
        else:
            segs = ("native",) + segs
        node = _find_path(root, segs)
        if node is None:
            print(f"\n[{args.show}] NOT FOUND")
            return 1
        print(f"\n[{args.show}] node_type={node.node_type} "
              f"children={len(node.children)} descendants={node.descendant_count()}")

        def dump(n, depth=0, maxdepth=3):
            if depth > maxdepth:
                return
            for c in n.children:
                print("  " * (depth + 1) + f"{c.node_type:<10} {c.name}")
                dump(c, depth + 1, maxdepth)
        dump(node)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
