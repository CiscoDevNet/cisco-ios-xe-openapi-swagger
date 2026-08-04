#!/usr/bin/env python3
"""netconf_get.py — NETCONF <get> / <get-config> of all-flavor root containers.

Probes each device over NETCONF (SSH :830) for the top-level container of every
YANG module across all flavors (oper, cfg, native-config, openconfig, ietf,
other, mib). Subscribing/getting a top container returns its whole subtree, so
these roots cover everything underneath. NETCONF identifies nodes by XML
NAMESPACE (learned from the device's <hello> capabilities), so no YANG-prefix
translation is needed.

For each root:
  - <get>            -> oper + config merged (content presence)
  - <get-config>     -> running config only (for config-capable flavors)
Results (status/bytes/payload) are written to output/netconf-<PID>.json for the
dataset builder + comparison matrix.

    .venv-harness/bin/python netconf_get.py --device C9300 --limit 5   # smoke
    .venv-harness/bin/python netconf_get.py --device C9300             # full
    .venv-harness/bin/python netconf_get.py --all
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
from pathlib import Path

from collect_fleet import load_env, load_devices  # reuse proven inventory/env helpers

from ncclient import manager
from ncclient.operations import RPCError

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
REPO_ROOT = HERE.parents[2]  # .../cisco-ios-xe-openapi-swagger
CATALOG = OUT / "subscribable-nodes.json"
MIB_CATALOG = OUT / "mib-nodes.json"
PREFIX_MAP = REPO_ROOT / "yang-prefix-map.json"


def load_prefix_to_module() -> dict:
    """YANG prefix -> module name (inverted from yang-prefix-map.json)."""
    try:
        data = json.loads(PREFIX_MAP.read_text(encoding="utf-8"))
        return {prefix: module for module, prefix in (data.get("modules") or {}).items()}
    except (json.JSONDecodeError, OSError):
        return {}

# Flavors whose top container is (also) config -> worth a <get-config>.
CONFIG_FLAVORS = {"cfg", "native-config", "openconfig"}
MAX_PAYLOAD = 200_000  # cap stored payload per path (chars) to keep files sane


def load_roots() -> list[dict]:
    """Depth-1 container of every module, all flavors (+ MIB)."""
    roots: dict[str, dict] = {}
    for path, forced_cat in ((CATALOG, None), (MIB_CATALOG, "mib")):
        if not path.exists():
            continue
        cat = json.loads(path.read_text(encoding="utf-8"))
        for module, nodes in cat.get("modules", {}).items():
            for n in nodes:
                if n.get("depth") != 1:
                    continue
                body = n["xpath"].lstrip("/")
                prefix, _, rest = body.partition(":")
                container = rest.split("/")[0]
                if not container:
                    continue
                roots["/" + body] = {
                    "prefix": prefix, "container": container,
                    "category": forced_cat or n.get("category", "other"),
                    "xpath": "/" + body,
                }
    return list(roots.values())


def build_ns_map(server_capabilities) -> dict:
    """module name -> XML namespace, parsed from the NETCONF <hello>."""
    ns = {}
    for cap in server_capabilities:
        if "?module=" not in cap:
            continue
        base, query = cap.split("?", 1)
        mod = urllib.parse.parse_qs(query).get("module", [None])[0]
        if mod and mod not in ns:
            ns[mod] = base
    return ns


def yang_library_ns(conn) -> dict:
    """module name -> namespace from ietf-yang-library (the complete list; the
    <hello> only advertises a subset)."""
    out = {}
    for container, nsuri in (("modules-state", "urn:ietf:params:xml:ns:yang:ietf-yang-library"),
                             ("yang-library", "urn:ietf:params:xml:ns:yang:ietf-yang-library")):
        try:
            xml = str(conn.get(filter=("subtree", f'<{container} xmlns="{nsuri}"/>')))
        except Exception:  # noqa: BLE001
            continue
        for block in re.findall(r"<module>.*?</module>", xml, re.S):
            name = re.search(r"<name>([^<]+)</name>", block)
            uri = re.search(r"<namespace>([^<]+)</namespace>", block)
            if name and uri:
                out.setdefault(name.group(1), uri.group(1))
        if out:
            break
    return out


def do_filtered(conn, op, container, ns):
    flt = ("subtree", f'<{container} xmlns="{ns}"/>')
    reply = conn.get(filter=flt) if op == "get" else conn.get_config(source="running", filter=flt)
    return str(reply)


def classify(op, container, ns, conn):
    try:
        xml = do_filtered(conn, op, container, ns)
    except RPCError as e:  # device-level per-path error (e.g. unsupported) — not a session drop
        return {"op": op, "status": "rpc-error", "bytes": 0, "error": str(e)[:200], "payload": ""}
    # Transport/session errors propagate to the caller's reconnect handler.
    has_data = f"<{container}" in xml
    return {
        "op": op,
        "status": "data" if has_data else "empty",
        "bytes": len(xml),
        "payload": xml[:MAX_PAYLOAD],
    }


def _connect(dev, env):
    m = manager.connect(host=dev["host"], port=830, username=env["IOSXE_USER"],
                        password=env["IOSXE_PASS"], hostkey_verify=False, allow_agent=False,
                        look_for_keys=False, device_params={"name": "iosxe"}, timeout=30)
    m.timeout = 30  # per-RPC timeout so a hanging get fails fast instead of stalling
    return m


def collect_device(dev, env, roots, limit, out_path=None) -> dict:
    prefix2module = load_prefix_to_module()
    conn = _connect(dev, env)
    nsmap = build_ns_map(conn.server_capabilities)
    nsmap.update(yang_library_ns(conn))  # complete module list (hello advertises only a subset)
    ns_by_prefix = {}
    for prefix, module in prefix2module.items():
        if module in nsmap:
            ns_by_prefix[prefix] = nsmap[module]
        elif module.startswith("Cisco-IOS-XE-"):
            ns_by_prefix[prefix] = f"http://cisco.com/ns/yang/{module}"  # Cisco convention fallback
    for module, ns in nsmap.items():
        ns_by_prefix.setdefault(module, ns)  # some catalog xpaths use module-name form

    todo = roots[:limit] if limit else roots
    resolved = sum(1 for r in todo if ns_by_prefix.get(r["prefix"]))
    print(f"  {dev['pid']}: {len(todo)} roots, {len(nsmap)} module namespaces, {resolved} resolvable")

    entries = []
    ops = []  # flatten to (root, op) so reconnect can resume mid-root
    for r in todo:
        ops.append((r, "get"))
        if r["category"] in CONFIG_FLAVORS:
            ops.append((r, "get-config"))

    i = 0
    reconnects = 0
    cur_fails = 0

    def _save():
        if out_path:
            Path(out_path).write_text(json.dumps(
                {"pid": dev["pid"], "host": dev["host"], "entries": entries},
                ensure_ascii=False), encoding="utf-8")

    while i < len(ops):
        r, op = ops[i]
        keys = {k: r[k] for k in ("xpath", "prefix", "container", "category")}
        ns = ns_by_prefix.get(r["prefix"])
        if not ns:
            entries.append({**keys, "op": op, "status": "no-namespace", "bytes": 0, "payload": ""})
            i += 1
            continue
        try:
            entries.append({**keys, **classify(op, r["container"], ns, conn)})
            i += 1
            cur_fails = 0
            if i % 40 == 0:
                _save()
                print(f"    ...{i}/{len(ops)} ({sum(1 for e in entries if e['status']=='data')} data)", flush=True)
        except Exception as ex:  # noqa: BLE001 — session drop OR a hanging get
            cur_fails += 1
            try:
                conn.close_session()
            except Exception:
                pass
            if cur_fails >= 3:  # poison root: record + skip so we don't loop forever
                entries.append({**keys, "op": op, "status": "timeout", "bytes": 0,
                                "error": str(ex)[:150], "payload": ""})
                i += 1
                cur_fails = 0
            reconnects += 1
            if reconnects >= 120:
                print(f"    too many reconnects ({reconnects}); saving partial at {i}")
                break
            time.sleep(2)
            try:
                conn = _connect(dev, env)
            except Exception as e:  # noqa: BLE001
                print(f"    reconnect failed: {e}; saving partial")
                break
    try:
        conn.close_session()
    except Exception:
        pass
    _save()
    return {"pid": dev["pid"], "host": dev["host"], "entries": entries}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", help="Device name/PID substring.")
    ap.add_argument("--all", action="store_true", help="All devices in inventory.")
    ap.add_argument("--limit", type=int, default=0, help="Only probe the first N roots (smoke test).")
    args = ap.parse_args()

    env = load_env()
    roots = load_roots()
    by_cat = {}
    for r in roots:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    print(f"Root probe set: {len(roots)} containers across flavors {by_cat}")

    devices = load_devices([args.device] if args.device else None)
    if not args.all and args.device is None:
        raise SystemExit("Specify --device <pid> or --all")

    for dev in devices:
        print(f"\n=== NETCONF {dev['pid']} ({dev['host']}) ===")
        out = OUT / f"netconf-{dev['pid']}.json"
        try:
            result = collect_device(dev, env, roots, args.limit, out_path=out)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {dev['pid']} failed: {e}")
            continue
        got = sum(1 for e in result["entries"] if e["status"] == "data")
        print(f"  wrote {out.name}: {len(result['entries'])} probes, {got} returned data "
              f"({out.stat().st_size/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
