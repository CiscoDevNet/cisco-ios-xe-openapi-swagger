#!/usr/bin/env python3
"""generate_native_augment_specs.py

Resolve sibling-module augments that fill in Cisco-IOS-XE-native's empty
placeholder containers (router, xconnect, route-tag, l2vpn-config) and emit
one swagger spec per placeholder.

Background:
    In `Cisco-IOS-XE-native.yang`, several top-level containers are declared
    as bodyless placeholders, e.g.

        container router;

    Their real content lives in augment statements inside sibling modules
    (Cisco-IOS-XE-bgp.yang, -ospf.yang, -eigrp.yang, -isis.yang, -nhrp.yang,
    -lisp.yang, -l2vpn.yang, ...). The main native-spec generator
    (`generate_native_openapi_v2.py`) only parses `Cisco-IOS-XE-native.yang`,
    so it silently drops these placeholders — leaving entire feature areas
    (BGP, OSPF, EIGRP, ISIS, RIP, static, xconnect, etc.) absent from the
    swagger-native-config-model viewer.

What this script does:
    1. Scan `references/<ver>/*.yang` for modules that import
       Cisco-IOS-XE-native.
    2. For each augment statement targeting `/<prefix>:native/<prefix>:<P>`
       where <P> is one of the four placeholders, parse the augment body
       into container/list/leaf nodes (recursively).
    3. Merge all augments for the same placeholder into a single path tree
       rooted at `/data/Cisco-IOS-XE-native:native/<P>`.
    4. Emit one OpenAPI 3.0 spec per placeholder, matching the format of
       the existing `native-*.json` files under swagger-native-config-model.
    5. Patch `manifest.json` so the viewer picks the new specs up.

Idempotent. Safe to re-run. Run after `generate_native_openapi_v2.py` and
before `wrap_body_schemas.py` so the post-processor normalises shared
invariants (server default, hostname examples, body wrappers).

Usage:
    python scripts/generate_native_augment_specs.py --version 26.1.1
    python scripts/generate_native_augment_specs.py --all
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
RELEASES = ["17.9.x", "17.12.x", "17.15.x", "17.18.1", "26.1.1"]
_REF_DIR_OVERRIDES = {"17.18.1": "17181-YANG-modules"}

PLACEHOLDERS: Tuple[str, ...] = ("router", "xconnect", "route-tag", "l2vpn-config")

# Per-protocol bucket map for splitting the (very large) /native/router
# augment tree across multiple spec files so no single spec exceeds the
# legacy ~6 MB ceiling. Unmapped children fall into the 'other' bucket.
_ROUTER_BUCKETS: Dict[str, str] = {
    "bgp": "bgp",
    "ospf": "ospf",
    "ospfv3": "ospf",
    "router-ospf": "ospf",
    "eigrp": "eigrp",
    "router-eigrp": "eigrp",
    "isis": "isis",
    "isis-container": "isis",
    "rip": "rip",
    "lisp": "lisp",
    "lisp-list": "lisp-list",
    "nhrp": "nhrp",
}

MAX_TREE_DEPTH = 5  # cap recursion so emitted path counts stay sane

# --- shared helpers -------------------------------------------------------

_IMPORT_NATIVE_RE = re.compile(
    r"import\s+Cisco-IOS-XE-native\s*\{\s*prefix\s+(\S+)\s*;"
)
_AUGMENT_RE = re.compile(r"augment\s+\"([^\"]+)\"\s*\{")
_GROUPING_RE = re.compile(r"\bgrouping\s+([A-Za-z0-9_\-:]+)\s*\{")
_USES_RE = re.compile(r"\buses\s+([A-Za-z0-9_\-:]+)\s*[;{]")
_CONTAINER_RE = re.compile(r"\bcontainer\s+([A-Za-z0-9_\-]+)\s*[;{]")
_LIST_RE = re.compile(r"\blist\s+([A-Za-z0-9_\-]+)\s*\{")
_LEAF_RE = re.compile(r"\bleaf\s+([A-Za-z0-9_\-]+)\s*\{")
_LEAFLIST_RE = re.compile(r"\bleaf-list\s+([A-Za-z0-9_\-]+)\s*\{")
_KEY_RE = re.compile(r"\bkey\s+\"([^\"]+)\"")
_TYPE_RE = re.compile(r"\btype\s+([A-Za-z0-9_:\-]+)")
_DESC_RE = re.compile(r"\bdescription\s+\"([^\"]+)\"")


def _ref_dir(version: str) -> Path:
    sub = _REF_DIR_OVERRIDES.get(version, version)
    return ROOT / "references" / sub


def _release_api_dir(version: str) -> Path:
    return ROOT / "releases" / version / "swagger-native-config-model" / "api"


def _strip_comments(text: str) -> str:
    # YANG allows // line comments and /* block */ comments. The augment
    # bodies in Cisco modules sometimes contain them; strip to simplify
    # regex-based parsing.
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def _find_balanced(text: str, open_brace_pos: int) -> int:
    """Return the index of the matching '}' for the '{' at open_brace_pos."""
    depth = 1
    i = open_brace_pos + 1
    while i < len(text) and depth > 0:
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


# --- augment discovery ----------------------------------------------------

def _collect_module_groupings(text: str) -> Dict[str, str]:
    """Return {grouping_name: body_text} for every top-level grouping in this
    module. Handles comment-stripping at the call site.
    """
    out: Dict[str, str] = {}
    for gm in _GROUPING_RE.finditer(text):
        end = _find_balanced(text, gm.end() - 1)
        if end == -1:
            continue
        out[gm.group(1)] = text[gm.end(): end]
    return out


# Cross-module grouping index. Built lazily per reference directory so a
# single augment body that calls `uses pref:foo` can resolve `foo` from the
# imported module. Cleared between releases.
_GROUPING_INDEX: Dict[str, Tuple[Dict[str, str], Dict[str, str]]] = {}
# value = (groupings_in_module, import_prefix_map)


def _build_module_index(ref_dir: Path) -> Dict[str, Tuple[Dict[str, str], Dict[str, str]]]:
    """For every .yang in ref_dir, capture (groupings, import_prefix_map).
    import_prefix_map maps local prefix -> imported module name.
    """
    idx: Dict[str, Tuple[Dict[str, str], Dict[str, str]]] = {}
    for fp in ref_dir.glob("*.yang"):
        try:
            text = _strip_comments(fp.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        # module/submodule name as filename stem
        mod_name = fp.stem
        groupings = _collect_module_groupings(text)
        imports: Dict[str, str] = {}
        for im in re.finditer(r"\bimport\s+(\S+)\s*\{\s*prefix\s+(\S+)\s*;", text):
            imports[im.group(2)] = im.group(1)
        idx[mod_name] = (groupings, imports)
    return idx


def _resolve_grouping(
    name: str, owner_module: str, idx: Dict[str, Tuple[Dict[str, str], Dict[str, str]]]
) -> Optional[str]:
    """Resolve a `uses` target (which may be 'foo' or 'pref:foo') to a
    grouping body. Returns None if unresolvable.
    """
    if ":" in name:
        pref, local = name.split(":", 1)
        imports = idx.get(owner_module, ({}, {}))[1]
        target_mod = imports.get(pref)
        if not target_mod:
            return None
        groupings = idx.get(target_mod, ({}, {}))[0]
        return groupings.get(local)
    # Unqualified: look in owner's own groupings, else any module.
    own = idx.get(owner_module, ({}, {}))[0]
    if name in own:
        return own[name]
    for _mn, (gs, _imp) in idx.items():
        if name in gs:
            return gs[name]
    return None


def find_native_augments(
    yang_path: Path,
) -> Tuple[str, List[Tuple[str, List[str], str]]]:
    """Return (module_name, [(placeholder, segments, body), ...])."""
    try:
        text = yang_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return yang_path.stem, []
    m = _IMPORT_NATIVE_RE.search(text)
    if not m:
        return yang_path.stem, []
    prefix = m.group(1)
    text = _strip_comments(text)

    out: List[Tuple[str, List[str], str]] = []
    target_re = re.compile(
        r"augment\s+\"(" + re.escape("/" + prefix + ":native/") + r"[^\"]*)\"\s*\{"
    )
    for am in target_re.finditer(text):
        target = am.group(1)
        brace_pos = am.end() - 1
        end = _find_balanced(text, brace_pos)
        if end == -1:
            continue
        body = text[brace_pos + 1 : end]
        rest = target[len(f"/{prefix}:native/"):]
        segments: List[str] = []
        for seg in rest.split("/"):
            if not seg:
                continue
            seg_main = re.sub(r"\[[^\]]*\]", "", seg)
            if ":" in seg_main:
                seg_main = seg_main.split(":", 1)[1]
            segments.append(seg_main)
        if not segments:
            continue
        placeholder = segments[0]
        if placeholder not in PLACEHOLDERS:
            continue
        out.append((placeholder, segments, body))
    return yang_path.stem, out


def find_native_root_augments(yang_path: Path) -> Tuple[str, List[str]]:
    """Return (module_name, [body, ...]) for augments targeting `/native`
    itself (no child path) — i.e. modules that add brand-new top-level
    children to /native via `augment "/ios:native" { uses ...; }` or inline
    container/list declarations.
    """
    try:
        text = yang_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return yang_path.stem, []
    m = _IMPORT_NATIVE_RE.search(text)
    if not m:
        return yang_path.stem, []
    prefix = m.group(1)
    text = _strip_comments(text)

    bodies: List[str] = []
    # Match augment "/pref:native" exactly (no trailing /...)
    root_target_re = re.compile(
        r"augment\s+\"/" + re.escape(prefix) + r":native\"\s*\{"
    )
    for am in root_target_re.finditer(text):
        brace_pos = am.end() - 1
        end = _find_balanced(text, brace_pos)
        if end == -1:
            continue
        bodies.append(text[brace_pos + 1 : end])
    return yang_path.stem, bodies


# --- body -> path tree ----------------------------------------------------

def _walk_body(
    body: str,
    parent_segments: List[str],
    depth: int,
    paths: Dict[str, Dict],
    owner_module: str,
    idx: Dict[str, Tuple[Dict[str, str], Dict[str, str]]],
    visited_groupings: Optional[set] = None,
) -> None:
    """Recursively walk a YANG block body, emitting one paths[<path>] entry
    per container/list. Expands `uses <grouping>` references inline.
    """
    if depth > MAX_TREE_DEPTH:
        return
    if visited_groupings is None:
        visited_groupings = set()

    pos = 0
    depth_cursor = 0
    while pos < len(body):
        # Find the earliest container/list/uses at this depth.
        c_match = _find_next_top_level(body, pos, _CONTAINER_RE)
        l_match = _find_next_top_level(body, pos, _LIST_RE)
        u_match = _find_next_top_level(body, pos, _USES_RE)
        candidates: List[Tuple[int, str, str, re.Match]] = []
        if c_match:
            candidates.append((c_match.start(), "container", c_match.group(1), c_match))
        if l_match:
            candidates.append((l_match.start(), "list", l_match.group(1), l_match))
        if u_match:
            candidates.append((u_match.start(), "uses", u_match.group(1), u_match))
        if not candidates:
            return
        candidates.sort(key=lambda x: x[0])
        start, kind, name, match = candidates[0]

        if kind == "uses":
            if name in visited_groupings:
                pos = match.end()
                # If uses has a refinement block `uses NAME { ... }`, the
                # `{` is captured as the last char of the match — skip
                # past the matching `}` so subsequent statements at the
                # same depth remain visible.
                if body[match.end() - 1] == "{":
                    close = _find_balanced(body, match.end() - 1)
                    if close != -1:
                        pos = close + 1
                continue
            grouping_body = _resolve_grouping(name, owner_module, idx)
            if grouping_body is not None:
                # Expand the grouping inline at the current depth — the
                # grouping's top-level data nodes are children of
                # parent_segments, just like containers declared inline.
                _walk_body(
                    grouping_body,
                    parent_segments,
                    depth,
                    paths,
                    owner_module,
                    idx,
                    visited_groupings | {name},
                )
            pos = match.end()
            if body[match.end() - 1] == "{":
                close = _find_balanced(body, match.end() - 1)
                if close != -1:
                    pos = close + 1
            continue

        after = body[match.end() - 1]
        if kind == "container" and after == ";":
            full_segments = parent_segments + [name]
            _record_path(full_segments, depth, kind, "", paths)
            pos = match.end()
            continue
        if after != "{":
            pos = match.end()
            continue
        end = _find_balanced(body, match.end() - 1)
        if end == -1:
            return
        inner = body[match.end(): end]
        full_segments = parent_segments + [name]
        key_match = _KEY_RE.search(inner) if kind == "list" else None
        key = key_match.group(1).split()[0] if key_match else ""
        _record_path(full_segments, depth, kind, key, paths)
        _walk_body(inner, full_segments, depth + 1, paths, owner_module, idx, visited_groupings)
        pos = end + 1


def _find_next_top_level(body: str, start: int, regex: re.Pattern) -> Optional[re.Match]:
    """Find the next regex match in body[start:] that is NOT nested inside a
    deeper { } block. We walk and track depth as we go.
    """
    depth = 0
    i = start
    while i < len(body):
        c = body[i]
        if c == "{":
            depth += 1
            i += 1
            continue
        if c == "}":
            depth -= 1
            i += 1
            continue
        if depth == 0:
            m = regex.match(body, i)
            if m:
                return m
        i += 1
    return None


def _record_path(
    segments: List[str], depth: int, kind: str, key: str, paths: Dict[str, Dict]
) -> None:
    base = "/data/Cisco-IOS-XE-native:native/" + "/".join(segments)
    paths[base] = {"kind": kind, "key": key, "name": segments[-1], "depth": depth}
    if kind == "list" and key:
        item = f"{base}={{{key}}}"
        paths[item] = {"kind": "list-item", "key": key, "name": segments[-1], "depth": depth}


# --- OpenAPI spec emission ------------------------------------------------

_TOP_DATA_RE = re.compile(
    r"\b(container|list|leaf|leaf-list|choice|anyxml)\s+([A-Za-z0-9_\-]+)\b"
)


def _top_level_data_names(
    body: str,
    owner_module: str,
    idx: Dict[str, Tuple[Dict[str, str], Dict[str, str]]],
    visited_groupings: Optional[set] = None,
) -> set:
    """Return the set of data-node names declared at depth 0 of `body`,
    expanding `uses <grouping>` references recursively (so a body of
    `uses some-grouping;` yields the grouping's top-level data names).
    """
    if visited_groupings is None:
        visited_groupings = set()
    names: set = set()
    depth = 0
    i = 0
    while i < len(body):
        c = body[i]
        if c == "{":
            depth += 1
            i += 1
            continue
        if c == "}":
            depth -= 1
            i += 1
            continue
        if depth == 0:
            dm = _TOP_DATA_RE.match(body, i)
            if dm:
                names.add(dm.group(2))
                i = dm.end()
                continue
            um = _USES_RE.match(body, i)
            if um:
                g = um.group(1)
                local = g.split(":")[-1]
                if local not in visited_groupings:
                    gbody = _resolve_grouping(g, owner_module, idx)
                    if gbody is not None:
                        names |= _top_level_data_names(
                            gbody, owner_module, idx, visited_groupings | {local}
                        )
                i = um.end()
                if body[um.end() - 1] == "{":
                    close = _find_balanced(body, um.end() - 1)
                    if close != -1:
                        i = close + 1
                continue
        i += 1
    return names


def _parse_native_top_children(yang_path: Path) -> Dict[str, str]:
    """Return {child_name: body_text} for every top-level container/list
    declared directly in `container native { ... }` in Cisco-IOS-XE-native.yang.
    Bodyless containers map to ''. Used as a safety-net sweep so any
    container the v2 generator skipped still gets a spec.
    """
    try:
        text = yang_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    text = _strip_comments(text)
    m = re.search(r"\bcontainer\s+native\s*\{", text)
    if not m:
        return {}
    end = _find_balanced(text, m.end() - 1)
    if end == -1:
        return {}
    nbody = text[m.end() : end]
    out: Dict[str, str] = {}
    depth = 0
    i = 0
    while i < len(nbody):
        c = nbody[i]
        if c == "{":
            depth += 1
            i += 1
            continue
        if c == "}":
            depth -= 1
            i += 1
            continue
        if depth == 0:
            mm = re.match(r"(container|list)\s+([A-Za-z0-9_\-]+)\s*([;{])", nbody[i:])
            if mm:
                name = mm.group(2)
                term = mm.group(3)
                if term == ";":
                    out.setdefault(name, "")
                    i += mm.end()
                else:
                    brace = i + mm.end() - 1
                    cend = _find_balanced(nbody, brace)
                    if cend == -1:
                        break
                    out.setdefault(name, nbody[brace + 1 : cend])
                    i = cend + 1
                continue
        i += 1
    return out


def _covered_top_names(api_dir: Path) -> set:
    """Top-level /native/<name> segments present in any existing native-*.json."""
    covered: set = set()
    top_re = re.compile(r"^/data/Cisco-IOS-XE-native:native/([^/?=]+)")
    for fp in sorted(api_dir.glob("native-*.json")):
        try:
            spec = json.loads(fp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for p in spec.get("paths", {}).keys():
            mm = top_re.match(p)
            if mm:
                covered.add(mm.group(1))
    return covered



def _path_entry(name: str, kind: str, tag: str, is_list_item: bool) -> Dict:
    summary_kind = {"container": "container", "list": "list", "list-item": "list entry"}[kind]
    methods = ["get", "put", "patch", "delete"]
    body_schema = {
        "type": "object",
        "properties": {
            f"Cisco-IOS-XE-native:{name}": {"type": "object"},
        },
    }
    example = {f"Cisco-IOS-XE-native:{name}": {}}
    entry: Dict[str, Dict] = {}
    for m in methods:
        op_id = f"{m}-{name}"
        if is_list_item:
            op_id += "-item"
        op: Dict = {
            "summary": f"{m.upper()} {summary_kind} '{name}'",
            "operationId": op_id,
            "tags": [tag],
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/yang-data+json": {
                            "schema": body_schema,
                            "example": example,
                        }
                    },
                },
                "204": {"description": "No content (success, no body)"},
                "401": {"description": "Unauthorized"},
                "404": {"description": "Not found"},
            },
        }
        if m in ("put", "patch"):
            op["requestBody"] = {
                "required": True,
                "content": {
                    "application/yang-data+json": {
                        "schema": body_schema,
                        "example": example,
                    }
                },
            }
        entry[m] = op
    return entry


def _list_key_param(key: str) -> Dict:
    return {
        "name": key,
        "in": "path",
        "required": True,
        "description": f"Key '{key}' of the list entry",
        "schema": {"type": "string"},
    }


def build_spec(
    spec_name: str,
    title_subject: str,
    placeholder: str,
    paths_map: Dict[str, Dict],
    version: str,
) -> Dict:
    """spec_name is the file stem (e.g. 'native-router-bgp'). placeholder
    is the top-level native child (router/xconnect/route-tag/l2vpn-config)
    so the description and tag stay grouped.
    """
    tag = spec_name
    title = f"Native - {title_subject} (augmented)"
    description = (
        f"Cisco IOS-XE Native Configuration — `/native/{placeholder}` subtree, "
        f"resolved from augment statements in sibling YANG modules "
        f"(e.g. Cisco-IOS-XE-bgp, -ospf, -eigrp, -isis, -lisp, -nhrp, -l2vpn).\n\n"
        f"**Paths:** {len(paths_map)}\n"
        f"**HTTP methods:** GET / PUT / PATCH / DELETE"
    )
    out_paths: Dict[str, Dict] = {}
    for path in sorted(paths_map.keys()):
        info = paths_map[path]
        entry = _path_entry(info["name"], info["kind"], tag, info["kind"] == "list-item")
        if info["kind"] == "list-item":
            entry["parameters"] = [_list_key_param(info["key"])]
        out_paths[path] = entry
    return {
        "openapi": "3.0.0",
        "info": {
            "title": title,
            "description": description,
            "version": version,
            "contact": {
                "name": "Cisco IOS-XE RESTCONF API",
                "url": "https://developer.cisco.com/iosxe/",
            },
            "x-yang-module": "Cisco-IOS-XE-native",
            "x-model-type": "native",
            "x-augment-resolved": True,
        },
        "servers": [
            {
                "url": "https://{device}/restconf",
                "variables": {
                    "device": {
                        "default": "devnetsandboxiosxec9k.cisco.com",
                        "description": "Device IP or hostname",
                    }
                },
            }
        ],
        "paths": out_paths,
        "components": {
            "securitySchemes": {
                "BasicAuth": {"type": "http", "scheme": "basic"},
            }
        },
        "security": [{"BasicAuth": []}],
        "tags": [{"name": tag, "description": f"/native/{placeholder} (augment-resolved)"}],
    }


# --- manifest patching ----------------------------------------------------

def _patch_manifest(api_dir: Path, new_modules: List[str]) -> None:
    mp = api_dir / "manifest.json"
    if not mp.is_file():
        return
    manifest = json.loads(mp.read_text(encoding="utf-8"))
    modules = set(manifest.get("modules", []))
    modules.update(new_modules)
    manifest["modules"] = sorted(modules)
    # Recompute totals from disk.
    total_paths = 0
    total_ops = 0
    for spec_file in sorted(api_dir.glob("*.json")):
        if spec_file.name == "manifest.json" or spec_file.name.startswith("_"):
            continue
        try:
            spec = json.loads(spec_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        paths = spec.get("paths") or {}
        total_paths += len(paths)
        for ops in paths.values():
            total_ops += sum(
                1 for k in ops if k.lower() in {"get", "put", "post", "patch", "delete"}
            )
    manifest["total_modules"] = len(manifest["modules"])
    manifest["spec_count"] = len(manifest["modules"])
    manifest["total_paths"] = total_paths
    manifest["total_operations"] = total_ops
    mp.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


# --- main per-release driver ---------------------------------------------

def process_release(version: str) -> int:
    rd = _ref_dir(version)
    ad = _release_api_dir(version)
    if not rd.is_dir():
        sys.stderr.write(f"[{version}] missing reference dir: {rd}\n")
        return 2
    if not ad.is_dir():
        sys.stderr.write(f"[{version}] missing api dir: {ad}\n")
        return 2

    # Build the cross-module index once for this release.
    idx = _build_module_index(rd)

    # Collect augments per placeholder.
    aggregated: Dict[str, Dict[str, Dict]] = {p: {} for p in PLACEHOLDERS}
    module_counts: Dict[str, int] = {p: 0 for p in PLACEHOLDERS}

    # Collect native-root augments (modules that add NEW top-level children
    # to /native via `augment "/<pref>:native"`). Each discovered child
    # name becomes its own spec — same pattern as the placeholders, but the
    # name set is discovered dynamically rather than fixed.
    root_aggregated: Dict[str, Dict[str, Dict]] = {}
    root_origins: Dict[str, set] = {}

    for fp in sorted(rd.glob("*.yang")):
        owner, augments = find_native_augments(fp)
        if augments:
            for placeholder, segments, body in augments:
                module_counts[placeholder] += 1
                _record_path([placeholder], 0, "container", "", aggregated[placeholder])
                _walk_body(
                    body, segments, len(segments), aggregated[placeholder], owner, idx
                )
        _owner2, root_bodies = find_native_root_augments(fp)
        for rbody in root_bodies:
            # First, discover ALL top-level data-node names this augment adds
            # (containers, lists, AND leaf/leaf-list). _walk_body below only
            # emits container/list paths, so we need this separate sweep to
            # avoid silently dropping leaf-only additions (e.g. Cisco-IOS-XE-pae
            # adds `leaf pae;`).
            top_names = _top_level_data_names(rbody, owner, idx)
            for nm in top_names:
                root_aggregated.setdefault(nm, {})
                if not root_aggregated[nm]:
                    _record_path([nm], 0, "container", "", root_aggregated[nm])
                root_origins.setdefault(nm, set()).add(owner)
            # Then expand container/list bodies via _walk_body.
            tmp: Dict[str, Dict] = {}
            _walk_body(rbody, [], 0, tmp, owner, idx)
            for path, info in tmp.items():
                rest = path[len("/data/Cisco-IOS-XE-native:native/"):]
                if not rest:
                    continue
                child = rest.lstrip("/").split("/")[0].split("=")[0]
                root_aggregated.setdefault(child, {})
                if not root_aggregated[child]:
                    _record_path([child], 0, "container", "", root_aggregated[child])
                root_aggregated[child][path] = info
                root_origins.setdefault(child, set()).add(owner)

    written: List[str] = []
    for p in PLACEHOLDERS:
        if not aggregated[p]:
            sys.stderr.write(
                f"[{version}] {p}: no augment content found — skipping (will leave gap)\n"
            )
            continue

        if p == "router":
            # Split router into per-protocol spec files so no single spec
            # exceeds the legacy ~6 MB ceiling.
            buckets: Dict[str, Dict[str, Dict]] = {}
            root_only: Dict[str, Dict] = {}
            for path, info in aggregated[p].items():
                # path = /data/Cisco-IOS-XE-native:native/router[/...]
                rest = path[len("/data/Cisco-IOS-XE-native:native/router"):]
                if not rest:
                    root_only[path] = info
                    continue
                # rest starts with '/' then the immediate child name.
                first = rest.lstrip("/").split("/")[0].split("=")[0]
                bucket = _ROUTER_BUCKETS.get(first, "other")
                buckets.setdefault(bucket, {})[path] = info
            # Always emit a slim native-router.json (placeholder root only)
            # so the accountability guard sees /native/router covered even
            # if the protocol buckets are renamed in the future.
            if not root_only:
                _record_path(["router"], 0, "container", "", root_only)
            slim = build_spec(
                "native-router", "Router", "router", root_only, version
            )
            (ad / "native-router.json").write_text(
                json.dumps(slim, indent=2) + "\n", encoding="utf-8"
            )
            written.append("native-router")
            print(
                f"[{version}] wrote native-router.json: {len(root_only)} path "
                f"(index / placeholder root)"
            )
            for bucket_name in sorted(buckets):
                bp = buckets[bucket_name]
                # Include the router root path in each bucket so users can
                # navigate up from any protocol view.
                bp.update(root_only)
                spec_name = f"native-router-{bucket_name}"
                title_subject = f"Router {bucket_name.upper()}"
                spec = build_spec(spec_name, title_subject, "router", bp, version)
                out = ad / f"{spec_name}.json"
                out.write_text(
                    json.dumps(spec, indent=2) + "\n", encoding="utf-8"
                )
                written.append(spec_name)
                print(
                    f"[{version}] wrote {out.name}: {len(bp)} paths "
                    f"(bucket={bucket_name})"
                )
            continue

        spec_name = f"native-{p}"
        title_subject = p.replace("-", " ").title()
        spec = build_spec(spec_name, title_subject, p, aggregated[p], version)
        out = ad / f"{spec_name}.json"
        out.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
        written.append(spec_name)
        print(
            f"[{version}] wrote {out.name}: {len(aggregated[p])} paths "
            f"from {module_counts[p]} augment(s)"
        )

    # Root-augment specs (one per discovered child).
    for child in sorted(root_aggregated):
        paths_map = root_aggregated[child]
        spec_name = f"native-{child}"
        title_subject = child.replace("-", " ").title()
        # Re-use build_spec but pass the child as "placeholder" so tags /
        # descriptions are consistent with the placeholder-augment specs.
        spec = build_spec(spec_name, title_subject, child, paths_map, version)
        # Override description so it's clear this is a root-augment child.
        origins = sorted(root_origins.get(child, set()))
        spec["info"]["description"] = (
            f"Cisco IOS-XE Native Configuration — `/native/{child}` subtree, "
            f"added to the /native root by sibling YANG module(s) via "
            f"`augment \"/ios:native\"`. Origin module(s): "
            f"{', '.join(origins) if origins else 'unknown'}.\n\n"
            f"**Paths:** {len(paths_map)}\n"
            f"**HTTP methods:** GET / PUT / PATCH / DELETE"
        )
        spec["info"]["x-augment-resolved"] = True
        spec["info"]["x-augment-target"] = "/native (root)"
        out = ad / f"{spec_name}.json"
        out.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
        written.append(spec_name)
        print(
            f"[{version}] wrote {out.name}: {len(paths_map)} paths "
            f"(root augment from {', '.join(origins)})"
        )

    # Completeness sweep: any top-level container/list declared in
    # Cisco-IOS-XE-native.yang that no existing spec covers gets its own
    # spec. Catches gaps where the v2 native generator silently dropped a
    # container (historical: dot1x, login, password, object-group, zone,
    # zone-pair, identity, scada-gw all fell into this bucket).
    native_yang = rd / "Cisco-IOS-XE-native.yang"
    if native_yang.is_file():
        native_children = _parse_native_top_children(native_yang)
        covered_now = _covered_top_names(ad)
        for child in sorted(native_children):
            if child in covered_now or child in PLACEHOLDERS:
                continue
            body = native_children[child]
            paths_map: Dict[str, Dict] = {}
            _record_path([child], 0, "container", "", paths_map)
            if body:
                _walk_body(
                    body, [child], 1, paths_map, "Cisco-IOS-XE-native", idx
                )
            spec_name = f"native-{child}"
            # Avoid clobbering an existing file written earlier this run.
            if (ad / f"{spec_name}.json").exists():
                continue
            title_subject = child.replace("-", " ").title()
            spec = build_spec(spec_name, title_subject, child, paths_map, version)
            spec["info"]["description"] = (
                f"Cisco IOS-XE Native Configuration — `/native/{child}` subtree, "
                f"emitted by the completeness sweep because the primary native "
                f"generator did not produce a spec for this top-level container.\n\n"
                f"**Paths:** {len(paths_map)}\n"
                f"**HTTP methods:** GET / PUT / PATCH / DELETE"
            )
            (ad / f"{spec_name}.json").write_text(
                json.dumps(spec, indent=2) + "\n", encoding="utf-8"
            )
            written.append(spec_name)
            print(
                f"[{version}] wrote {spec_name}.json: {len(paths_map)} paths "
                f"(completeness sweep)"
            )

    if written:
        _patch_manifest(ad, written)
        print(f"[{version}] patched manifest with: {sorted(written)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", help="release version (e.g. 26.1.1)")
    ap.add_argument("--all", action="store_true", help="process all known releases")
    args = ap.parse_args()
    if not args.version and not args.all:
        ap.error("specify --version <ver> or --all")
    versions = RELEASES if args.all else [args.version]
    rc = 0
    for v in versions:
        rc = max(rc, process_release(v))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
