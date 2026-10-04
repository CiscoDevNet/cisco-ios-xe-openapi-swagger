#!/usr/bin/env python3
"""
build_release_compare.py — "What changed" data for adjacent releases.

Writes releases/compare/<old>__<new>.json for each adjacent pair in
releases/index.json (or one pair via --old/--new), plus releases/compare/index.json.

Inputs (all pinned / reproducible):
  references/<ver>/*.yang              module inventory, content hashes, revision notes
  releases/<ver>/yang-trees/*.html     pyang trees = resolved schema (uses/augment applied)
  releases/<ver>/platform-support.json per-platform module membership
  releases/<ver>/yang_accountability.json  model category per module

Schema diffs come from pyang trees rather than the generated OpenAPI specs:
the committed specs of older releases were produced by earlier generator
versions, so a spec diff would report generator drift as YANG changes.

Usage:
    python scripts/build_release_compare.py                 # all adjacent pairs
    python scripts/build_release_compare.py --old 26.1.1 --new 26.2.1
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASES = ROOT / "releases"
OUT_DIR = RELEASES / "compare"
LEGACY_YANG = {"17.18.1": ROOT / "references" / "17181-YANG-modules"}
INNOVATIONS_URL = ("https://github.com/jeremycohoe/cisco-ios-xe-yang-model-innovations/"
                   "blob/main/release-comparisons/{token}-YANG-Model-Overview.md")
# Overview docs whose "previous -> current" pair matches two releases hosted here.
OVERVIEW_PAIRS = {("17.18.1", "26.1.1"): "2611", ("26.1.1", "26.2.1"): "2621"}

RE_NODE = re.compile(
    r"^(?P<indent>[| ]*)(?P<status>[+xo])--(?P<flags>rw|ro|-x|-n|-w|-u)\s+"
    r"(?P<name>[^\s?*!]+)(?P<mark>[?*!]*)(?:\s+\[(?P<keys>[^\]]+)\])?(?P<rest>.*)$")
RE_SECTION = re.compile(r"^(module|submodule|augment|rpcs|notifications|grouping|structure)\b(.*?):?\s*$")
RE_REVISION = re.compile(r"revision\s+\"?(\d{4}-\d{2}-\d{2})\"?\s*\{(.*?)\n\s*\}", re.S)
RE_DESCRIPTION = re.compile(r"description\s+\"((?:[^\"\\]|\\.)*)\"", re.S)
STATUS = {"+": "current", "x": "deprecated", "o": "obsolete"}
KIND = {"rw": "config", "ro": "state", "-x": "rpc/action", "-n": "notification",
        "-w": "input", "-u": "uses"}


def yang_dir(version: str) -> Path:
    candidate = ROOT / "references" / version
    if candidate.is_dir():
        return candidate
    if version in LEGACY_YANG and LEGACY_YANG[version].is_dir():
        return LEGACY_YANG[version]
    raise SystemExit(f"missing YANG source for {version}: {candidate}")


def load_modules(version: str) -> dict[str, dict]:
    """Top-level YANG modules: content hash, latest revision, revision notes."""
    modules = {}
    for path in sorted(yang_dir(version).glob("*.yang")):
        text = path.read_text(encoding="utf-8", errors="replace")
        revisions = []
        for date, body in RE_REVISION.findall(text):
            match = RE_DESCRIPTION.search(body)
            note = re.sub(r"\s+", " ", match.group(1)).strip() if match else ""
            revisions.append({"date": date, "note": note})
        revisions.sort(key=lambda r: r["date"], reverse=True)
        modules[path.stem] = {
            "sha1": hashlib.sha1(text.encode("utf-8")).hexdigest(),
            "revision": revisions[0]["date"] if revisions else None,
            "revisions": revisions,
        }
    return modules


def parse_tree(tree_html: Path) -> dict[str, dict]:
    """Map schema path -> node properties from a pyang tree page."""
    match = re.search(r"<pre>(.*?)</pre>", tree_html.read_text(encoding="utf-8"), re.S)
    if not match:
        return {}
    nodes: dict[str, dict] = {}
    stack: list[tuple[int, str]] = []
    section = ""
    for line in html.unescape(match.group(1)).splitlines():
        if not line.strip():
            continue
        head = RE_SECTION.match(line.strip())
        if head and not line.startswith((" ", "|")):
            kind, arg = head.group(1), head.group(2).strip()
            section = f"augment {arg}" if kind == "augment" else ("" if kind in ("module", "submodule") else kind)
            stack = []
            continue
        node = RE_NODE.match(line)
        if not node:
            continue  # wrapped type continuation lines
        depth = len(node.group("indent"))
        while stack and stack[-1][0] >= depth:
            stack.pop()
        parent = stack[-1][1] if stack else (f"[{section}]" if section else "")
        path = f"{parent}/{node.group('name')}"
        stack.append((depth, path))
        rest = node.group("rest").strip()
        nodes[path] = {
            "kind": KIND[node.group("flags")],
            "status": STATUS[node.group("status")],
            "type": rest.split()[0] if rest and not rest.startswith(("{", "->")) else "",
            "keys": node.group("keys") or "",
            "list": "*" in node.group("mark"),
            "presence": "!" in node.group("mark"),
        }
    return nodes


def load_trees(version: str) -> dict[str, Path]:
    return {Path(p).stem: Path(p) for p in glob.glob(str(RELEASES / version / "yang-trees" / "*.html"))
            if Path(p).stem not in ("index", "mib-trees-index")}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def accountability(version: str) -> dict[str, dict]:
    data = load_json(RELEASES / version / "yang_accountability.json")
    return {m["name"]: m for m in data.get("modules", [])}


def subtree_roots(paths: list[str], nodes: dict) -> list[dict]:
    """Collapse each added/removed subtree to its root plus a descendant count."""
    path_set = set(paths)
    roots = [p for p in paths if p.rsplit("/", 1)[0] not in path_set]
    root_set = set(roots)
    descendants = dict.fromkeys(roots, 0)
    for path in paths:
        ancestor = path.rsplit("/", 1)[0]
        while ancestor:
            if ancestor in root_set:
                descendants[ancestor] += 1
                break
            ancestor = ancestor.rsplit("/", 1)[0]
    return [{"path": root, "kind": nodes[root]["kind"], "type": nodes[root]["type"],
             "status": nodes[root]["status"], "descendants": descendants[root]} for root in roots]


def diff_nodes(old: dict, new: dict) -> dict:
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = []
    for path in sorted(set(old) & set(new)):
        before, after = old[path], new[path]
        deltas = {key: [before[key], after[key]] for key in ("kind", "status", "type", "keys", "list", "presence")
                  if before[key] != after[key]}
        if deltas:
            changed.append({"path": path, "changes": deltas})
    return {
        "added": subtree_roots(added, new),
        "removed": subtree_roots(removed, old),
        "changed": changed,
        "nodes_added": len(added),
        "nodes_removed": len(removed),
    }


def compare(old: str, new: str) -> dict:
    old_mods, new_mods = load_modules(old), load_modules(new)
    old_trees, new_trees = load_trees(old), load_trees(new)
    old_acct, new_acct = accountability(old), accountability(new)
    old_plat = load_json(RELEASES / old / "platform-support.json")
    new_plat = load_json(RELEASES / new / "platform-support.json")

    modules = []
    for name in sorted(set(old_mods) | set(new_mods), key=str.lower):
        before, after = old_mods.get(name), new_mods.get(name)
        if before and after and before["sha1"] == after["sha1"]:
            continue
        status = "added" if not before else "removed" if not after else "changed"
        acct = new_acct.get(name) or old_acct.get(name) or {}
        entry = {
            "name": name,
            "status": status,
            "category": acct.get("classification", ""),
            # Spec viewer links resolve against the release that has the module.
            "specs": [{"label": c["label"], "url": c["spec_url"]} for c in acct.get("categories", [])],
            "revision_before": before and before["revision"],
            "revision_after": after and after["revision"],
        }
        if after:
            since = before["revision"] if before else ""
            entry["revision_notes"] = [r for r in after["revisions"] if r["date"] > (since or "")][:5]
        if name in old_trees or name in new_trees:
            old_nodes = parse_tree(old_trees[name]) if name in old_trees else {}
            new_nodes = parse_tree(new_trees[name]) if name in new_trees else {}
            node_diff = diff_nodes(old_nodes, new_nodes)
            entry["nodes_before"], entry["nodes_after"] = len(old_nodes), len(new_nodes)
            if any(node_diff.values()):
                entry["schema"] = node_diff
                entry["schema_counts"] = {"added": node_diff["nodes_added"],
                                          "removed": node_diff["nodes_removed"],
                                          "changed": len(node_diff["changed"])}
        entry["has_tree"] = name in (old_trees if status == "removed" else new_trees)
        modules.append(entry)

    platforms = []
    old_members = {m: set(v.get("platforms", [])) for m, v in old_plat.get("modules", {}).items()}
    new_members = {m: set(v.get("platforms", [])) for m, v in new_plat.get("modules", {}).items()}
    labels = {p["id"]: p.get("label", p["id"]) for p in old_plat.get("platforms", []) + new_plat.get("platforms", [])}
    for platform in sorted(labels):
        had = {m for m, plats in old_members.items() if platform in plats}
        has = {m for m, plats in new_members.items() if platform in plats}
        if had or has:
            platforms.append({"id": platform, "label": labels[platform], "before": len(had), "after": len(has),
                              "added": sorted(has - had, key=str.lower), "removed": sorted(had - has, key=str.lower)})

    def count(status):
        return sum(1 for m in modules if m["status"] == status)

    schema_modules = [m for m in modules if m.get("schema")]
    doc_token = OVERVIEW_PAIRS.get((old, new))
    new_meta = load_json(RELEASES / new / "meta.json")
    old_meta = load_json(RELEASES / old / "meta.json")
    # meta.json of some releases records a local temp path; index.json has the repo path.
    repo_paths = {r["ver"]: r.get("yangmodels_path") for r in load_json(RELEASES / "index.json").get("releases", [])}
    return {
        "old": old,
        "new": new,
        "sources": {
            old: {"yangmodels_path": repo_paths.get(old), "commit": old_meta.get("yangmodels_commit_sha")},
            new: {"yangmodels_path": repo_paths.get(new), "commit": new_meta.get("yangmodels_commit_sha")},
        },
        "overview_doc": INNOVATIONS_URL.format(token=doc_token) if doc_token else None,
        "summary": {
            "modules_before": len(old_mods),
            "modules_after": len(new_mods),
            "added": count("added"),
            "removed": count("removed"),
            "changed": count("changed"),
            "changed_with_schema_delta": sum(1 for m in schema_modules if m["status"] == "changed"),
            "nodes_added": sum(m["schema_counts"]["added"] for m in schema_modules),
            "nodes_removed": sum(m["schema_counts"]["removed"] for m in schema_modules),
            "nodes_changed": sum(m["schema_counts"]["changed"] for m in schema_modules),
        },
        "modules": modules,
        "platforms": platforms,
    }


def write_json(path: Path, data: dict, compact: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (json.dumps(data, separators=(",", ":"), ensure_ascii=False) if compact
            else json.dumps(data, indent=1, ensure_ascii=False))
    path.write_text(text + "\n", encoding="utf-8")


def write_pair(old: str, new: str, data: dict) -> None:
    """Summary JSON for the page, plus one on-demand schema-detail file per module."""
    detail_dir = OUT_DIR / f"{old}__{new}"
    if detail_dir.is_dir():
        for stale in detail_dir.glob("*.json"):
            stale.unlink()
    for module in data["modules"]:
        schema = module.pop("schema", None)
        if schema:
            write_json(detail_dir / f"{module['name']}.json", schema, compact=True)
    write_json(OUT_DIR / f"{old}__{new}.json", data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--old")
    parser.add_argument("--new")
    args = parser.parse_args()

    versions = [r["ver"] for r in load_json(RELEASES / "index.json").get("releases", [])]
    if args.old or args.new:
        if not (args.old and args.new):
            parser.error("--old and --new go together")
        pairs = [(args.old, args.new)]
    else:
        # index.json lists newest first; adjacent pairs run older -> newer.
        pairs = [(versions[i + 1], versions[i]) for i in range(len(versions) - 1)]

    for old, new in pairs:
        data = compare(old, new)
        write_pair(old, new, data)
        s = data["summary"]
        print(f"[compare] {old} -> {new}: +{s['added']} -{s['removed']} ~{s['changed']} modules "
              f"({s['changed_with_schema_delta']} with schema deltas); nodes +{s['nodes_added']} "
              f"-{s['nodes_removed']} ~{s['nodes_changed']}")

    existing = sorted(p.stem for p in OUT_DIR.glob("*__*.json"))
    index = {"pairs": [{"old": n.split("__")[0], "new": n.split("__")[1], "file": f"{n}.json"} for n in existing]}
    order = {v: i for i, v in enumerate(versions)}
    index["pairs"].sort(key=lambda p: order.get(p["new"], 99))
    write_json(OUT_DIR / "index.json", index)
    return 0


if __name__ == "__main__":
    sys.exit(main())
