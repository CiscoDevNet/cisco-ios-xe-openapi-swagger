#!/usr/bin/env python3
"""build_deprecations.py — census of deprecated / obsolete YANG elements for one release.

Reads every ``.yang`` file of a release (``ReleasePaths(ver).yang_source_dir()``,
recursively, so ``MIBS/`` is included) and writes ``releases/<ver>/deprecations/``:

    index.json         totals, per-category and per-module counts, validation,
                       change summary against the previous release
    modules/<M>.json   every flagged schema node that appears in module M, and
                       every flagged ``status`` statement written in M's files
    changes.json       node / statement status changes since the previous
                       release listed in releases/index.json (when its census exists)
    deprecations.csv   one row per top-most flagged node and per non-node statement

Accuracy is enforced by independent passes; the script exits non-zero if they
disagree:

1. **Lexical** — a standalone YANG tokenizer (comments, quoted strings, ``+``
   concatenation) finds every ``status`` statement.
2. **Parsed** — pyang's parser finds every ``status`` statement; the per-file
   (line, value) multiset must equal pass 1 exactly.
3. **Schema tree** — every module except deviation modules is loaded into one
   validated pyang context (groupings expanded, augments applied). Each node gets
   its own status (what ``pyang -f tree`` marks ``x`` / ``o``) and an effective
   status inherited from ancestors, the ``uses`` / grouping that instantiated it
   and the ``augment`` that added it. Every flagged source statement must land in
   exactly one bucket: schema-node, definition, extension, instantiation, or
   unreached-with-a-verified-reason. ``unexplained`` must be zero.
4. **Tree cross-check** (``--verify-trees``, slow) — runs ``pyang -f tree`` per
   module and compares the ``x`` / ``o`` marker counts with pass 3, per module.

Deviation modules are parsed (passes 1-2) but not applied: they are per-platform
and applying them all at once would prune nodes other platforms still have.

Usage:
    python scripts/build_deprecations.py                     # default release
    python scripts/build_deprecations.py --version 26.1.1 --summary
    python scripts/build_deprecations.py --version 26.2.1 --verify-trees
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _release_paths import LEGACY_VERSION, ReleasePaths, all_releases, default_release  # type: ignore  # noqa: E402
from _yang_status import lex_status_statements  # type: ignore  # noqa: E402
from analyze_yang_accountability_v2 import classify_yang_module  # type: ignore  # noqa: E402

import pyang  # noqa: E402
from pyang import context, repository, yang_parser  # noqa: E402

STATUS_NAMES = ("current", "deprecated", "obsolete")
SEVERITY = {name: i for i, name in enumerate(STATUS_NAMES)}
FLAGGED = STATUS_NAMES[1:]
DATA_KEYWORDS = {"container", "leaf", "leaf-list", "list", "anydata", "anyxml", "rpc", "action", "notification"}
NODE_KEYWORDS = DATA_KEYWORDS | {"choice", "case"}
DEFINITION_KEYWORDS = {"typedef", "identity", "feature", "extension", "grouping", "enum", "bit"}
INSTANTIATION_KEYWORDS = {"uses", "augment"}
NODE_COLUMNS = ["path", "keyword", "kind", "status", "effective", "top_most", "via", "file", "line",
                "descendants", "leaf_descendants", "top_module", "description"]
DESCRIPTION_LIMIT = 200
SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


# ------------------------------------------------- passes 1 + 2: lexer and parser

@dataclass
class SourceStatement:
    file: str
    line: int
    status: str
    keyword: str
    name: str | None
    is_extension: bool
    groupings: list[str]
    context: str
    description: str
    ordinal: int = 0

    def key(self, module: str) -> tuple:
        return statement_key(module, self.keyword, self.context, self.name, self.ordinal)


@dataclass
class ParsedSources:
    file_module: dict[str, str] = field(default_factory=dict)  # file -> main module
    submodule_files: set[str] = field(default_factory=set)
    statements: list[SourceStatement] = field(default_factory=list)
    used_groupings: set[str] = field(default_factory=set)
    keys: set[tuple] = field(default_factory=set)  # identity of every statement that can carry a status
    seen: Counter = field(default_factory=Counter)  # base key -> occurrences, for ordinals
    lexical_total: int = 0
    parsed_total: int = 0
    mismatches: list[dict] = field(default_factory=list)


def statement_key(module: str, keyword: str, context: str, name, ordinal: int = 0) -> tuple:
    """Release-independent identity of a statement (line numbers shift between releases).

    ``ordinal`` separates siblings that would otherwise share a key, e.g. two
    ``augment`` statements on the same target in a converted MIB (document order).
    """
    return (module, keyword, context or "", name or "", ordinal)


def context_of(chain: list) -> str:
    """Named ancestors below the module, e.g. ``grouping-x/container-y/leaf-z``."""
    return "/".join(a.arg for a in chain[1:] if a.arg and a.keyword != "type")


def first_sentence(stmt, limit: int = DESCRIPTION_LIMIT) -> str:
    d = stmt.search_one("description") if stmt is not None else None
    if d is None or not d.arg:
        return ""
    text = " ".join(d.arg.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def keyword_str(keyword) -> str:
    return keyword if isinstance(keyword, str) else ":".join(keyword)


def parse_sources(files: list[Path], texts: dict[Path, str]) -> ParsedSources:
    out = ParsedSources()
    scratch = context.Context(repository.FileRepository("", use_env=False))
    parser = yang_parser.YangParser()
    failures = []
    for f in files:
        text = texts[f]
        lexical = Counter(lex_status_statements(text))
        mod = parser.parse(scratch, str(f), text)
        if mod is None:
            failures.append(f.name)
            continue
        main = mod.arg
        if mod.keyword == "submodule":
            out.submodule_files.add(f.name)
            bt = mod.search_one("belongs-to")
            main = bt.arg if bt is not None else mod.arg
        out.file_module[f.name] = main

        parsed: list = []
        keyed = NODE_KEYWORDS | DEFINITION_KEYWORDS | INSTANTIATION_KEYWORDS
        stmt_ordinal: dict[int, int] = {}

        def visit(chain):
            stmt = chain[-1]
            for sub in stmt.substmts:
                if sub.keyword == "status":
                    parsed.append((sub, chain))
                    continue
                if sub.keyword == "uses" and sub.arg:
                    out.used_groupings.add(sub.arg.split(":")[-1])
                if not isinstance(sub.keyword, str) or sub.keyword in keyed:
                    base = statement_key(main, keyword_str(sub.keyword), context_of(chain), sub.arg)
                    ordinal = out.seen[base]
                    out.seen[base] += 1
                    stmt_ordinal[id(sub)] = ordinal
                    out.keys.add(base[:-1] + (ordinal,))
                visit(chain + [sub])

        visit([mod])
        parsed_counter = Counter((s.pos.line, s.arg) for s, _ in parsed)
        out.lexical_total += sum(lexical.values())
        out.parsed_total += len(parsed)
        if lexical != parsed_counter:
            out.mismatches.append({
                "file": f.name,
                "lexical_only": sorted((lexical - parsed_counter).elements()),
                "parsed_only": sorted((parsed_counter - lexical).elements()),
            })
        for st, chain in parsed:
            if st.arg not in SEVERITY:
                out.mismatches.append({"file": f.name, "line": st.pos.line, "invalid_status": st.arg})
                continue
            if st.arg == "current":
                continue
            parent = chain[-1]
            out.statements.append(SourceStatement(
                file=f.name,
                line=st.pos.line,
                status=st.arg,
                keyword=keyword_str(parent.keyword),
                name=parent.arg,
                is_extension=not isinstance(parent.keyword, str),
                groupings=[a.arg for a in chain if a.keyword == "grouping"],
                context=context_of(chain[:-1]),
                description=first_sentence(parent),
                ordinal=stmt_ordinal.get(id(parent), 0),
            ))
    if failures:
        sys.exit(f"pyang could not parse: {failures}")
    return out


# ------------------------------------------------------------ pass 3: schema tree

def status_of(stmt) -> str:
    if stmt is None:
        return "current"
    s = stmt.search_one("status")
    return s.arg if s is not None and s.arg in SEVERITY else "current"


def status_pos(stmt):
    s = stmt.search_one("status") if stmt is not None else None
    return (os.path.basename(s.pos.ref), s.pos.line) if s is not None else ("", 0)


def main_module_name(stmt) -> str:
    m = stmt.i_module
    if m.keyword == "submodule":
        return getattr(m, "i_including_modulename", None) or m.search_one("belongs-to").arg
    return m.arg


class TreeWalker:
    """Walks the resolved schema tree once, recording flagged nodes and every node's effective status."""

    def __init__(self):
        self.rows: dict[str, list[list]] = defaultdict(list)  # node module -> rows (NODE_COLUMNS)
        self.reached: Counter = Counter()  # (file, line) of own status statements found on nodes
        self.effective: Counter = Counter()  # (status, module) -> nodes
        self.effective_leaf: Counter = Counter()
        self.all_effective: dict[str, int] = {}  # path -> severity, every node
        self._seen: set[int] = set()

    @staticmethod
    def _descendants(node) -> tuple[int, int]:
        total = leafs = 0
        stack = list(getattr(node, "i_children", None) or [])
        while stack:
            c = stack.pop()
            if c.keyword in DATA_KEYWORDS:
                total += 1
                if c.keyword in ("leaf", "leaf-list"):
                    leafs += 1
            stack.extend(getattr(c, "i_children", None) or [])
        return total, leafs

    def walk_module(self, module) -> None:
        for child in getattr(module, "i_children", None) or []:
            self._walk(child, 0, "", None, module.arg, "config")

    def _walk(self, node, parent_eff: int, parent_path: str, parent_mod: str | None,
              top_module: str, kind: str) -> None:
        if id(node) in self._seen:
            return
        self._seen.add(id(node))
        mod = main_module_name(node)

        # Candidate sources of status; ties prefer the node's own statement.
        own = status_of(node)
        best = (SEVERITY[own], "", status_pos(node))
        for u in getattr(node, "i_uses", None) or []:
            grouping = getattr(u, "i_grouping", None)
            for src, label in ((u, "uses " + u.arg), (grouping, "grouping " + (grouping.arg if grouping is not None else ""))):
                sev = SEVERITY[status_of(src)]
                if sev > best[0]:
                    best = (sev, label, status_pos(src))
        aug = getattr(node, "i_augment", None)
        if aug is not None and SEVERITY[status_of(aug)] > best[0]:
            best = (SEVERITY[status_of(aug)], "augment " + aug.arg, status_pos(aug))
        eff = max(parent_eff, best[0])
        top_most = eff > parent_eff

        if node.keyword in ("rpc", "action", "notification"):
            kind = node.keyword
        elif kind not in ("rpc", "action", "notification"):
            cfg = getattr(node, "i_config", None)
            kind = "config" if cfg is True else ("state" if cfg is False else kind)

        if node.keyword in ("choice", "case"):
            segment = f"({node.arg})"
        elif node.keyword in ("input", "output"):
            segment = node.keyword
        else:
            segment = node.arg if mod == parent_mod else f"{mod}:{node.arg}"
        path = f"{parent_path}/{segment}"
        self.all_effective[path] = eff

        if node.keyword in NODE_KEYWORDS and eff:
            self.effective[(STATUS_NAMES[eff], mod)] += 1
            if node.keyword in ("leaf", "leaf-list"):
                self.effective_leaf[(STATUS_NAMES[eff], mod)] += 1

        if own != "current" or top_most:
            if own != "current":
                self.reached[status_pos(node)] += 1
            # Report the node's own statement unless a uses/augment raised it further.
            if top_most and best[1]:
                via, (ref_file, ref_line) = best[1], best[2]
            elif own != "current":
                via, (ref_file, ref_line) = "", status_pos(node)
            else:
                via, (ref_file, ref_line) = best[1], best[2]
            desc, leafs = self._descendants(node)
            self.rows[mod].append([
                path, node.keyword, kind, own, STATUS_NAMES[eff], 1 if top_most else 0, via,
                ref_file, ref_line, desc, leafs, top_module, first_sentence(node),
            ])

        for child in getattr(node, "i_children", None) or []:
            self._walk(child, eff, path, mod, top_module, kind)


def reconcile(parsed: ParsedSources, walker: TreeWalker, deviation_files: set[str]) -> dict[str, list[dict]]:
    """Place every flagged status statement in exactly one bucket, grouped by module."""
    top_instances: Counter = Counter()
    for rows in walker.rows.values():
        for r in rows:
            if r[5] and not r[6]:
                top_instances[(r[7], r[8])] += 1
    items: dict[str, list[dict]] = defaultdict(list)
    for s in parsed.statements:
        key = (s.file, s.line)
        item = {"status": s.status, "keyword": s.keyword, "name": s.name, "context": s.context,
                "file": s.file, "line": s.line, "description": s.description}
        if s.ordinal:
            item["ordinal"] = s.ordinal
        if s.is_extension:
            item["bucket"] = "extension"
        elif s.keyword in DEFINITION_KEYWORDS:
            item["bucket"] = "definition"
        elif s.keyword in INSTANTIATION_KEYWORDS:
            item["bucket"] = "instantiation"
        elif walker.reached[key]:
            item["bucket"] = "schema-node"
            item["instances"] = walker.reached[key]
            item["top_most_instances"] = top_instances[key]
        elif s.file in deviation_files:
            item["bucket"] = "unreached"
            item["reason"] = "deviation module (not applied)"
        elif s.groupings and not any(g in parsed.used_groupings for g in s.groupings):
            item["bucket"] = "unreached"
            item["reason"] = f"grouping '{s.groupings[-1]}' is never referenced by a uses statement"
        else:
            item["bucket"] = "unexplained"
        if s.groupings:
            item["in_grouping"] = s.groupings[-1]
        items[parsed.file_module[s.file]].append(item)
    return items


def module_shard(ver: str, module: str, category: str, walker: TreeWalker, items: dict[str, list[dict]]) -> dict:
    return {
        "version": ver, "module": module, "category": category,
        "node_columns": NODE_COLUMNS, "nodes": sorted(walker.rows.get(module, []), key=lambda r: r[0]),
        "items": sorted(items.get(module, []), key=lambda it: (it["file"], it["line"])),
    }

# ------------------------------------------------------------------ release data

def previous_release(ver: str) -> str | None:
    """The next-older release in releases/index.json. A release not listed yet is
    being added (VERSIONING.md §8 builds before registering), so it compares
    against the current newest."""
    vers = [r["ver"] for r in all_releases()]
    if ver not in vers:
        return vers[0] if vers else None
    i = vers.index(ver)
    return vers[i + 1] if i + 1 < len(vers) else None


def load_accountability(paths: ReleasePaths) -> dict[str, dict]:
    acc = paths.accountability_json()
    if not acc.is_file():
        return {}
    return {m["name"]: m for m in json.loads(acc.read_text(encoding="utf-8")).get("modules", [])}


def sources_digest(files: list[Path], root: Path) -> str:
    h = hashlib.sha256()
    for f in files:
        h.update(f.relative_to(root).as_posix().encode())
        h.update(hashlib.sha256(f.read_bytes().replace(b"\r\n", b"\n")).digest())
    return h.hexdigest()


# ----------------------------------------------------------------------- changes

def _ancestors_or_self(path: str):
    while path:
        yield path
        path = path.rsplit("/", 1)[0]


def compute_changes(prev_dir: Path, prev_keys: set | None, cur: ParsedSources, walker: TreeWalker,
                    items: dict[str, list[dict]], category_of) -> dict | None:
    """Status changes relative to the previous release's census.

    Statements are the unit of change: matched by (module, keyword, context, name),
    since line numbers shift between releases. ``prev_keys`` (every status-capable
    statement in the previous release's sources, when available) separates a
    statement that was newly flagged from one that was added already flagged.

    Nodes are matched by schema path; a node's previous effective status is the
    highest status of any previous top-most node at or above its path. A node that
    becomes flagged only because it is a new copy of an unchanged, already-flagged
    definition (e.g. a grouping reused under a new interface type) has
    ``cause: "new-instance"``.
    """
    modules_dir = prev_dir / "modules"
    if not modules_dir.is_dir():
        return None
    prev_top: dict[str, tuple[int, str, list]] = {}
    prev_status: dict[tuple, int] = {}
    for shard in modules_dir.glob("*.json"):
        data = json.loads(shard.read_text(encoding="utf-8"))
        cols = {c: i for i, c in enumerate(data["node_columns"])}
        for r in data["nodes"]:
            if r[cols["top_most"]]:
                prev_top[r[cols["path"]]] = (SEVERITY[r[cols["effective"]]], data["module"], r)
        for it in data["items"]:
            key = statement_key(data["module"], it["keyword"], it.get("context"), it.get("name"), it.get("ordinal", 0))
            prev_status[key] = max(prev_status.get(key, 0), SEVERITY[it["status"]])

    cur_status: dict[tuple, int] = {}
    cur_ref: dict[tuple[str, int], tuple] = {}
    for s in cur.statements:
        key = s.key(cur.file_module[s.file])
        cur_status[key] = max(cur_status.get(key, 0), SEVERITY[s.status])
        cur_ref[(s.file, s.line)] = key

    def change_type(before: int, after: int, existed: bool = True) -> str:
        if after > before:
            if before:
                return "escalated"
            return f"{'newly' if existed else 'added'}-{STATUS_NAMES[after]}"
        return "now-current" if after == 0 else "relaxed"

    entries = []
    for key in sorted(set(cur_status) | set(prev_status)):
        before, after = prev_status.get(key, 0), cur_status.get(key, 0)
        if before == after:
            continue
        mod, keyword, ctx, name, ordinal = key
        if after > before:
            kind = change_type(before, after, prev_keys is None or key in prev_keys)
        elif after == 0 and key not in cur.keys:
            kind = "removed"
        else:
            kind = change_type(before, after)
        entry = {"element": "statement", "type": kind, "module": mod, "category": category_of(mod),
                 "keyword": keyword, "context": ctx, "name": name,
                 "from": STATUS_NAMES[before], "to": STATUS_NAMES[after] if kind != "removed" else None}
        if ordinal:
            entry["ordinal"] = ordinal
        entries.append(entry)

    def prev_effective(path: str) -> int:
        return max((prev_top[p][0] for p in _ancestors_or_self(path) if p in prev_top), default=0)

    for mod, rows in walker.rows.items():
        for r in rows:
            if not r[5]:
                continue
            before, after = prev_effective(r[0]), SEVERITY[r[4]]
            if before >= after:
                continue
            key = cur_ref.get((r[7], r[8]))
            cause = "new-instance" if key is not None and prev_status.get(key, 0) >= after else "status-change"
            entries.append({"element": "node", "type": change_type(before, after), "cause": cause,
                            "module": mod, "category": category_of(mod), "path": r[0], "keyword": r[1],
                            "kind": r[2], "from": STATUS_NAMES[before], "to": r[4], "descendants": r[9]})
    for path, (before, mod, r) in prev_top.items():
        after = walker.all_effective.get(path)
        if after is not None and after >= before:
            continue
        entries.append({"element": "node", "type": "removed" if after is None else change_type(before, after),
                        "module": mod, "category": category_of(mod), "path": path, "keyword": r[1], "kind": r[2],
                        "from": STATUS_NAMES[before], "to": None if after is None else STATUS_NAMES[after],
                        "descendants": r[9]})

    entries.sort(key=lambda e: (e["element"] != "statement", e["category"], e["module"], e["type"],
                                e.get("path") or f"{e.get('context')}/{e.get('name')}"))

    def tally(rows) -> dict:
        stmts = [e for e in rows if e["element"] == "statement"]
        nodes = [e for e in rows if e["element"] == "node"]
        return {"statements": dict(Counter(e["type"] for e in stmts)),
                "nodes": dict(Counter(e["type"] for e in nodes)),
                "nodes_new_instance": sum(1 for e in nodes if e.get("cause") == "new-instance")}

    by_module: dict[str, list] = defaultdict(list)
    for e in entries:
        by_module[e["module"]].append(e)
    return {
        "previous_sources_parsed": prev_keys is not None,
        "summary": tally(entries),
        "by_category": {c: tally([e for e in entries if e["category"] == c])
                        for c in sorted({e["category"] for e in entries})},
        "by_module": {m: tally(es) for m, es in sorted(by_module.items())},
        "entries": entries,
    }

# ---------------------------------------------------------- pass 4: tree markers

TREE_MARKER = re.compile(r"^[\s|]*([xo])--", re.M)


def verify_trees(files: list[Path], search_path: str, walker: TreeWalker, workers: int) -> dict:
    def run(f: Path):
        p = subprocess.run([sys.executable, "-m", "pyang", "-f", "tree", "--tree-line-length", "0",
                            "-p", search_path, str(f)], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        c = Counter(m.group(1) for m in TREE_MARKER.finditer(p.stdout))
        return f.stem, c["x"], c["o"]

    with ThreadPoolExecutor(max_workers=workers) as pool:
        trees = {name: (x, o) for name, x, o in pool.map(run, files)}
    census = {m: (sum(1 for r in rows if r[3] == "deprecated"), sum(1 for r in rows if r[3] == "obsolete"))
              for m, rows in walker.rows.items()}
    mismatched = {m: {"tree": trees.get(m, (0, 0)), "census": census.get(m, (0, 0))}
                  for m in sorted(set(trees) | set(census)) if trees.get(m, (0, 0)) != census.get(m, (0, 0))}
    return {
        "modules_checked": len(files),
        "tree_deprecated": sum(x for x, _ in trees.values()),
        "tree_obsolete": sum(o for _, o in trees.values()),
        "mismatched_modules": mismatched,
    }


# -------------------------------------------------------------------------- main

def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def build(ver: str, verify: bool, workers: int) -> tuple[dict, bool]:
    paths = ReleasePaths(ver, legacy=ver == LEGACY_VERSION)
    src = paths.yang_source_dir()
    if not src.is_dir():
        sys.exit(f"YANG sources for {ver} not found at {src} (run scripts/fetch_yang_release.py)")
    files = sorted(src.rglob("*.yang"))
    texts = {f: f.read_text(encoding="utf-8", errors="replace") for f in files}
    search_path = os.pathsep.join(sorted({str(f.parent) for f in files}))

    accountability = load_accountability(paths)
    category_cache: dict[str, str] = {}

    def category_of(module: str) -> str:
        if module not in category_cache:
            if module in accountability:
                category_cache[module] = accountability[module].get("classification") or "other"
            else:
                f = next((p for p in files if p.stem == module), None)
                category_cache[module] = classify_yang_module(f"{module}.yang", texts.get(f, "") if f else "")[0]
        return category_cache[module]

    # Passes 1 + 2
    parsed = parse_sources(files, texts)
    deviation_files = {fn for fn, m in parsed.file_module.items() if category_of(m) == "deviation"}

    # Pass 3
    ctx = context.Context(repository.FileRepository(search_path, use_env=False))
    ctx.lax_quote_checks = True
    ctx.lax_xpath_checks = True
    tree_files = [f for f in files if f.name not in deviation_files and f.name not in parsed.submodule_files]
    for f in tree_files:
        ctx.add_module(str(f), texts[f])
    ctx.validate()
    walker = TreeWalker()
    modules = sorted({id(m): m for m in ctx.modules.values() if m.keyword == "module"}.values(), key=lambda m: m.arg)
    for m in modules:
        walker.walk_module(m)

    # Rows that start a flagged subtree because of the node's own statement.
    items = reconcile(parsed, walker, deviation_files)
    unexplained = [dict(it, module=m) for m, its in items.items() for it in its if it["bucket"] == "unexplained"]

    levels = Counter("error" if pyang.error.is_error(pyang.error.err_level(e[1])) else "warning" for e in ctx.errors)

    # Per-module and per-category counts
    by_module = {}
    for m in sorted(set(walker.rows) | set(items)):
        rows, its = walker.rows.get(m, []), items.get(m, [])
        acc = accountability.get(m) or {}
        spec = next((c.get("spec_url") for c in acc.get("categories") or [] if c.get("spec_url")), None)
        entry = {"category": category_of(m), "spec_url": spec,
                 "has_tree": (paths.release_root / "yang-trees" / f"{m}.html").is_file()}
        for st in FLAGGED:
            entry[st] = {
                "statements": sum(1 for it in its if it["status"] == st),
                "explicit_nodes": sum(1 for r in rows if r[3] == st),
                "top_most_nodes": sum(1 for r in rows if r[5] and r[4] == st),
                "effective_nodes": walker.effective[(st, m)],
                "effective_leafs": walker.effective_leaf[(st, m)],
            }
        by_module[m] = entry

    def rollup(entries) -> dict:
        out = {"modules": 0}
        for st in FLAGGED:
            out[st] = {k: sum(e[st][k] for e in entries) for k in
                       ("statements", "explicit_nodes", "top_most_nodes", "effective_nodes", "effective_leafs")}
            out[st]["modules"] = sum(1 for e in entries if e[st]["statements"] or e[st]["effective_nodes"])
        out["modules"] = len(entries)
        return out

    by_category = {c: rollup([e for e in by_module.values() if e["category"] == c])
                   for c in sorted({e["category"] for e in by_module.values()})}
    totals = rollup(list(by_module.values()))
    for st in FLAGGED:
        totals[st]["by_bucket"] = dict(Counter(it["bucket"] for its in items.values() for it in its if it["status"] == st))
        totals[st]["by_keyword"] = dict(Counter(it["keyword"] for its in items.values() for it in its
                                                if it["status"] == st).most_common())

    prev = previous_release(ver)
    changes = None
    if prev:
        prev_paths = ReleasePaths(prev, legacy=prev == LEGACY_VERSION)
        prev_src = prev_paths.yang_source_dir()
        prev_keys = None
        if prev_src.is_dir():
            prev_files = sorted(prev_src.rglob("*.yang"))
            prev_keys = parse_sources(
                prev_files, {f: f.read_text(encoding="utf-8", errors="replace") for f in prev_files}).keys
        changes = compute_changes(prev_paths.release_root / "deprecations", prev_keys, parsed, walker,
                                  items, category_of)
    if changes:
        for m, c in changes["by_module"].items():
            by_module.setdefault(m, {"category": category_of(m), "spec_url": None, "has_tree": False,
                                     **{st: {k: 0 for k in ("statements", "explicit_nodes", "top_most_nodes",
                                                            "effective_nodes", "effective_leafs")} for st in FLAGGED}})
            by_module[m]["changes"] = c

    tree_check = verify_trees(tree_files, search_path, walker, workers) if verify else None

    meta_path = paths.release_root / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
    validation = {
        "lexical_status_statements": parsed.lexical_total,
        "parsed_status_statements": parsed.parsed_total,
        "lexical_vs_parsed_mismatches": parsed.mismatches,
        "flagged_statements": sum(len(v) for v in items.values()),
        "by_bucket": dict(Counter(it["bucket"] for its in items.values() for it in its)),
        "unexplained": unexplained,
        "pyang_errors": levels["error"],
        "pyang_warnings": levels["warning"],
        "tree_check": tree_check,
    }
    ok = not parsed.mismatches and not unexplained and (
        tree_check is None or not tree_check["mismatched_modules"])
    validation["passed"] = ok
    index = {
        "version": ver,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": {
            "yangmodels_path": meta.get("yangmodels_path") if not os.path.isabs(meta.get("yangmodels_path") or "")
            else None,
            "yangmodels_commit_sha": meta.get("yangmodels_commit_sha"),
            "content_sha256": sources_digest(files, src),
            "yang_files": len(files),
            "modules_in_tree": len(modules),
            "deviation_files_not_applied": len(deviation_files),
            "pyang_version": pyang.__version__,
        },
        "validation": validation,
        "totals": totals,
        "by_category": by_category,
        "by_module": by_module,
        "changes": {"from": prev, "previous_sources_parsed": changes["previous_sources_parsed"],
                    "summary": changes["summary"], "by_category": changes["by_category"]}
        if changes else ({"from": prev, "unavailable": True} if prev else None),
    }

    # Write into a scratch dir, then swap, so removed modules leave no stale shards.
    out_dir = paths.release_root / "deprecations"
    tmp = paths.release_root / f"deprecations.tmp-{os.getpid()}"
    for stale in paths.release_root.glob("deprecations.tmp*"):
        shutil.rmtree(stale, ignore_errors=True)
    (tmp / "modules").mkdir(parents=True)
    for m in by_module:
        if not SAFE_NAME.match(m):
            sys.exit(f"unsafe module name for a file path: {m!r}")
        write_json(tmp / "modules" / f"{m}.json", module_shard(ver, m, by_module[m]["category"], walker, items))

    write_json(tmp / "index.json", index)
    if changes:
        write_json(tmp / "changes.json", {"version": ver, "from": prev, **changes})
    write_csv(tmp / "deprecations.csv", ver, walker, items, category_of)
    swap_dir(tmp, out_dir)
    return index, ok


def _retry(action, attempts: int = 20, delay: float = 1.5):
    """Run a filesystem action, retrying transient Windows locks (OneDrive sync, antivirus)."""
    for i in range(attempts):
        try:
            return action()
        except PermissionError:
            if i == attempts - 1:
                raise
            time.sleep(delay)


def swap_dir(new: Path, target: Path) -> None:
    """Replace ``target`` with ``new``; the old copy is only deleted once the new one is in place."""
    old = target.with_name(target.name + ".old")
    shutil.rmtree(old, ignore_errors=True)
    if target.exists():
        _retry(lambda: target.rename(old))
    try:
        _retry(lambda: new.rename(target))
    except PermissionError:
        if old.exists() and not target.exists():
            old.rename(target)
        raise
    _retry(lambda: shutil.rmtree(old) if old.exists() else None)


def write_csv(path: Path, ver: str, walker: TreeWalker, items, category_of) -> None:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["release", "status", "element", "category", "module", "keyword", "path_or_name", "kind",
                "affected_data_nodes", "source", "defined_in", "description"])
    rows = []
    for m, node_rows in walker.rows.items():
        for r in node_rows:
            if r[5]:
                rows.append([ver, r[4], "schema node", category_of(m), m, r[1], r[0], r[2],
                             r[9] + (1 if r[1] in DATA_KEYWORDS else 0), r[6] or "own status",
                             f"{r[7]}:{r[8]}", r[12]])
    for m, its in items.items():
        for it in its:
            if it["bucket"] != "schema-node":
                name = f"{it['context']}/{it['name']}" if it.get("context") else (it.get("name") or "")
                rows.append([ver, it["status"], it["bucket"], category_of(m), m, it["keyword"], name, "",
                             "", it.get("reason", ""), f"{it['file']}:{it['line']}", it["description"]])
    rows.sort(key=lambda r: (r[3], r[4], r[6]))
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8")


def print_summary(index: dict) -> None:
    t, v = index["totals"], index["validation"]
    print(f"## Deprecation census — IOS XE {index['version']}\n")
    print(f"Sources: {index['source']['yang_files']} YANG files; {v['flagged_statements']:,} flagged status "
          f"statements; buckets {v['by_bucket']}; unexplained {len(v['unexplained'])}; "
          f"lexical/parsed mismatches {len(v['lexical_vs_parsed_mismatches'])}; passed={v['passed']}\n")
    print("| Category | Modules | Dep. statements | Obs. statements | Dep. nodes top-most / all | Obs. nodes top-most / all |")
    print("|---|---:|---:|---:|---:|---:|")
    for c, e in list(index["by_category"].items()) + [("**Total**", t)]:
        d, o = e["deprecated"], e["obsolete"]
        print(f"| {c} | {e['modules']} | {d['statements']:,} | {o['statements']:,} | "
              f"{d['top_most_nodes']:,} / {d['effective_nodes']:,} | {o['top_most_nodes']:,} / {o['effective_nodes']:,} |")
    ch = index.get("changes")
    if ch and ch.get("summary") is not None:
        s = ch["summary"]
        print(f"\nChanges since {ch['from']}: statements {s['statements']}; nodes {s['nodes']} "
              f"({s['nodes_new_instance']} new copies of already-flagged definitions)")
    tc = v.get("tree_check")
    if tc:
        print(f"\nTree check: x={tc['tree_deprecated']:,} o={tc['tree_obsolete']:,}; "
              f"mismatched modules: {len(tc['mismatched_modules'])}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--version", default=None, help="release (default: releases/index.json default)")
    ap.add_argument("--summary", action="store_true", help="print a Markdown summary")
    ap.add_argument("--verify-trees", action="store_true",
                    help="cross-check x/o counts against `pyang -f tree` per module (slow)")
    ap.add_argument("--workers", type=int, default=max(2, (os.cpu_count() or 4) - 1),
                    help="parallel pyang processes for --verify-trees")
    args = ap.parse_args()
    ver = args.version or default_release()
    index, ok = build(ver, args.verify_trees, args.workers)
    if args.summary:
        print_summary(index)
    print(f"deprecations census for {ver}: {'PASSED' if ok else 'FAILED'}", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
