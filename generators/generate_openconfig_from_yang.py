#!/usr/bin/env python3
"""OpenConfig YANG -> OpenAPI 3.0, from the pyang-resolved schema (augments + Cisco deviations).

One spec per OpenConfig module that defines top-level data (openconfig-interfaces,
openconfig-system, openconfig-network-instance, ...). Grouping/augment-only modules such as
openconfig-bgp or openconfig-if-ethernet get no spec of their own: their nodes appear under
the root they augment, with RFC 8040 module-qualified path segments
(/data/openconfig-interfaces:interfaces/interface={name}/openconfig-if-ethernet:ethernet).

Every container and list becomes a path (lists: a collection path plus an item path with
all keys as path parameters). Config nodes get GET/PUT/PATCH/DELETE; config-false (state)
nodes are GET-only. Bodies are wrapped with the RFC 7951 member name, like the cfg/oper
tree generators.

    python generators/generate_openconfig_from_yang.py --version 26.2.1
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _openconfig_schema import data_children, data_modules, load_context, top_nodes  # noqa: E402
from _version_args import resolve_paths  # noqa: E402
from generate_cfg_from_tree import COMMON_COMPONENTS, example_for_type, yang_type_to_schema  # noqa: E402

SCHEMA_DEPTH = 4
EXAMPLE_DEPTH = 3
SPEC_SIZE_LIMIT = 12 * 1024 * 1024  # shrink schema/example depth for a module above this


def _module_name(node) -> str:
    return node.i_module.i_modulename


def _description(node) -> str:
    stmt = node.search_one("description")
    return " ".join(stmt.arg.split()) if stmt is not None and stmt.arg else ""


def _base_type(leaf):
    """(base type name, enum values) following typedefs."""
    type_stmt = leaf.search_one("type")
    while type_stmt is not None and getattr(type_stmt, "i_typedef", None) is not None:
        type_stmt = type_stmt.i_typedef.search_one("type")
    if type_stmt is None:
        return "string", []
    name = type_stmt.arg.split(":")[-1]
    enums = [e.arg for e in type_stmt.search("enum")] if name == "enumeration" else []
    return name, enums


def _member(child, parent_module: str) -> str:
    """RFC 7951: a member is module-qualified when its module differs from its parent's."""
    module = _module_name(child)
    return child.arg if module == parent_module else f"{module}:{child.arg}"


def leaf_schema(leaf) -> dict:
    base, enums = _base_type(leaf)
    schema = yang_type_to_schema(base, leaf.arg)
    if enums:
        schema["enum"] = enums
    description = _description(leaf)
    if description:
        schema["description"] = description[:300]
    return schema


def leaf_example(leaf):
    base, enums = _base_type(leaf)
    return enums[0] if enums else example_for_type(base, leaf.arg)


def build_schema(node, depth=0, max_depth=SCHEMA_DEPTH) -> dict:
    if node.keyword in ("leaf", "leaf-list"):
        schema = leaf_schema(node)
        return {"type": "array", "items": schema} if node.keyword == "leaf-list" else schema
    obj = {"type": "object"}
    if depth < max_depth:
        properties = {}
        for child in data_children(node):
            properties[_member(child, _module_name(node))] = build_schema(child, depth + 1, max_depth)
        if properties:
            obj["properties"] = properties
        keys = node.search_one("key")
        if node.keyword == "list" and keys is not None:
            obj["required"] = keys.arg.split()
    return {"type": "array", "items": obj} if node.keyword == "list" else obj


def build_example(node, depth=0, max_depth=EXAMPLE_DEPTH):
    if node.keyword == "leaf":
        return leaf_example(node)
    if node.keyword == "leaf-list":
        return [leaf_example(node)]
    obj = {}
    if depth < max_depth:
        for child in data_children(node):
            if child.keyword == "leaf" and leaf_example(child) is None:
                continue
            obj[_member(child, _module_name(node))] = build_example(child, depth + 1, max_depth)
    return [obj] if node.keyword == "list" else obj


def _segment(node, parent_module: str | None) -> str:
    return f"{_module_name(node)}:{node.arg}" if _module_name(node) != parent_module else node.arg


def _key_names(node) -> list[str]:
    keys = node.search_one("key")
    return keys.arg.split() if keys is not None else []


def _key_schema(node, key: str) -> dict:
    leaf = node.search_one("leaf", key) or next((c for c in data_children(node) if c.arg == key), None)
    if leaf is None:
        return {"type": "string"}
    base, enums = _base_type(leaf)
    schema = yang_type_to_schema(base, key)
    if enums:
        schema["enum"] = enums
    return schema


def collect_paths(module) -> list[dict]:
    """[{path, node, params}] for every container/list under the module's top-level nodes."""
    out: list[dict] = []

    def walk(node, parent_path: str, parent_module: str | None, params: list[dict]):
        path = f"{parent_path}/{_segment(node, parent_module)}"
        if node.keyword == "container":
            out.append({"path": path, "node": node, "params": params, "collection": False})
            child_path, child_params = path, params
        else:
            out.append({"path": path, "node": node, "params": params, "collection": True})
            used = {p["name"] for p in params}
            item_params = []
            for key in _key_names(node):
                name = key if key not in used else f"{node.arg}-{key}"
                used.add(name)
                item_params.append({"name": name, "in": "path", "required": True,
                                    "description": f"Key `{key}` of list `{node.arg}`",
                                    "schema": _key_schema(node, key)})
            if not item_params:
                return  # keyless (state) list: no addressable entries
            child_path = path + "=" + ",".join("{" + p["name"] + "}" for p in item_params)
            child_params = params + item_params
            out.append({"path": child_path, "node": node, "params": child_params, "collection": False})
        for child in data_children(node):
            if child.keyword in ("container", "list"):
                walk(child, child_path, _module_name(node), child_params)

    for top in top_nodes(module):
        walk(top, "/data", None, [])
    return out


def operations(entry: dict, tag: str, schema_depth: int, example_depth: int) -> dict:
    node = entry["node"]
    member = f"{_module_name(node)}:{node.arg}"
    inner = build_schema(node, max_depth=schema_depth)
    example = build_example(node, max_depth=example_depth)
    if node.keyword == "list" and not entry["collection"]:
        inner = inner["items"]
        inner = {"type": "array", "items": inner, "maxItems": 1}
    schema = {"type": "object", "properties": {member: inner}}
    wrapped = {member: example}
    op_base = entry["path"].replace("/data/", "").replace("/", "-").replace("=", "-")
    op_base = op_base.replace("{", "").replace("}", "").replace(",", "-").replace(":", "-")
    description = _description(node)
    params = [{"$ref": "#/components/parameters/accept"}, {"$ref": "#/components/parameters/depth"}]
    ops = {"get": {
        "summary": f"Get {node.arg}" + (" (all entries)" if entry["collection"] else ""),
        "description": description or f"Retrieve {node.arg}.",
        "operationId": f"get-{op_base}",
        "tags": [tag],
        "parameters": params,
        "responses": {
            "200": {"description": "Successful response",
                    "content": {"application/yang-data+json": {"schema": schema, "example": wrapped}}},
            "401": {"description": "Unauthorized"},
            "404": {"description": "Resource not found"}}}}
    writable = bool(getattr(node, "i_config", True)) and not entry["collection"]
    if writable:
        body = {"required": True,
                "content": {"application/yang-data+json": {"schema": schema, "example": wrapped}}}
        ops["put"] = {"summary": f"Replace {node.arg}", "description": description or f"Create or replace {node.arg}.",
                      "operationId": f"put-{op_base}", "tags": [tag], "requestBody": body,
                      "responses": {"201": {"description": "Created"}, "204": {"description": "Updated"},
                                    "400": {"description": "Invalid input"}}}
        ops["patch"] = {"summary": f"Update {node.arg}", "description": description or f"Merge into {node.arg}.",
                        "operationId": f"patch-{op_base}", "tags": [tag], "requestBody": body,
                        "responses": {"204": {"description": "Updated"}, "400": {"description": "Invalid input"}}}
        ops["delete"] = {"summary": f"Delete {node.arg}", "description": description or f"Delete {node.arg}.",
                         "operationId": f"delete-{op_base}", "tags": [tag],
                         "responses": {"204": {"description": "Deleted"}, "404": {"description": "Not found"}}}
    if entry["params"]:
        for op in ops.values():
            op["parameters"] = list(entry["params"]) + op.get("parameters", [])
    return ops


def build_spec(module, version: str, schema_depth=SCHEMA_DEPTH, example_depth=EXAMPLE_DEPTH) -> dict:
    entries = collect_paths(module)
    tops = top_nodes(module)
    paths = {}
    for entry in entries:
        tag = entry["path"].split("/")[2].split(":")[-1].split("=")[0]
        paths[entry["path"]] = operations(entry, tag, schema_depth, example_depth)
    augmenting = sorted({_module_name(e["node"]) for e in entries} - {module.arg})
    op_count = sum(len(ops) for ops in paths.values())
    description = _description(module) or "OpenConfig data model"
    summary = (f"{description}\n\n**Module:** `{module.arg}`\n"
               f"**Root nodes:** {', '.join(t.arg for t in tops)}\n"
               f"**Paths:** {len(paths)} | **Operations:** {op_count}\n\n"
               "GET/PUT/PATCH/DELETE for config nodes, GET-only for state (config false) nodes.")
    if augmenting:
        summary += f"\n\n**Includes augments from:** {', '.join(f'`{m}`' for m in augmenting)}"
    return {
        "openapi": "3.0.0",
        "info": {"title": module.arg, "description": summary, "version": version,
                 "contact": {"name": "Cisco IOS-XE RESTCONF API", "url": "https://developer.cisco.com/iosxe/"},
                 "x-yang-module": module.arg, "x-model-type": "openconfig",
                 "x-augmented-by": augmenting},
        "servers": [{"url": "https://{device}:{port}/restconf", "description": "IOS-XE Device RESTCONF API",
                     "variables": {"device": {"default": "devnetsandboxiosxec9k.cisco.com"},
                                   "port": {"default": "443"}}}],
        "paths": paths,
        "components": COMMON_COMPONENTS,
        "security": [{"basicAuth": []}],
        "tags": [{"name": t.arg, "description": _description(t)[:300]} for t in tops],
    }


def augment_only_modules(ctx, spec_modules: list[str]) -> dict[str, list[str]]:
    """OpenConfig modules without a spec of their own -> the specs whose paths carry their nodes."""
    hosts: dict[str, set[str]] = {}

    def walk(node, root_module: str):
        for child in data_children(node):
            hosts.setdefault(_module_name(child), set()).add(root_module)
            # Nodes expanded from a grouping belong to the using module; credit the grouping's module too.
            for uses in getattr(child, "i_uses", None) or []:
                grouping = getattr(uses, "i_grouping", None)
                if grouping is not None:
                    hosts.setdefault(grouping.i_module.i_modulename, set()).add(root_module)
            walk(child, root_module)

    for module in data_modules(ctx):
        for top in top_nodes(module):
            walk(top, module.arg)
    module_names = sorted({m.arg for m in ctx.modules.values() if m.arg.startswith("openconfig-")})
    return {name: sorted(hosts[name]) for name in module_names
            if name not in spec_modules and hosts.get(name)}


def generate_all(yang_dir: Path, output_dir: Path, version: str) -> dict:
    ctx = load_context(yang_dir)
    for stale in output_dir.glob("openconfig-*.json"):
        stale.unlink()
    written, total_paths, total_ops = [], 0, 0
    for module in data_modules(ctx):
        schema_depth, example_depth = SCHEMA_DEPTH, EXAMPLE_DEPTH
        spec = build_spec(module, version, schema_depth, example_depth)
        text = json.dumps(spec, indent=2)
        while len(text) > SPEC_SIZE_LIMIT and schema_depth > 1:
            schema_depth, example_depth = schema_depth - 1, max(1, example_depth - 1)
            spec = build_spec(module, version, schema_depth, example_depth)
            text = json.dumps(spec, indent=2)
        (output_dir / f"{module.arg}.json").write_text(text, encoding="utf-8")
        ops = sum(len(o) for o in spec["paths"].values())
        written.append(module.arg)
        total_paths += len(spec["paths"])
        total_ops += ops
        print(f"  {module.arg}: {len(spec['paths'])} paths, {ops} ops, {len(text)/1048576:.1f} MB"
              + (f" (schema depth {schema_depth})" if schema_depth != SCHEMA_DEPTH else ""))
    manifest = {"total_modules": len(written), "total_paths": total_paths, "total_operations": total_ops,
                "modules": written, "generator": "generate_openconfig_from_yang.py", "version": version,
                "augment_only_modules": augment_only_modules(ctx, written)}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Done: {len(written)} specs, {total_paths} paths, {total_ops} operations -> {output_dir}")
    return manifest


def main() -> int:
    yang_dir, output_dir, version = resolve_paths("openconfig")
    generate_all(yang_dir, output_dir, version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
