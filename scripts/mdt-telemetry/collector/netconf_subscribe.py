#!/usr/bin/env python3
"""netconf_subscribe.py -- NETCONF dynamic subscriptions (RFC 8639/8641 yang-push)
over the same SSH session, dial-in counterpart to MDT dial-out.

Two update triggers:
  * PERIODIC (default) -- <establish-subscription> with <yp:period> on each root;
    the device streams a snapshot every interval. Best for operational state.
  * ON-CHANGE (--on-change) -- <establish-subscription> with <yp:dampening-period>;
    the device sends an initial sync-on-start push carrying the current contents
    and thereafter a push on every change. This is how you "subscribe for config":
    pair it with --config-roots to probe the config models (native-config + cfg).

For each root it sends <establish-subscription>, waits for the first push-update
notification, records accept/reject + the pushed payload, then
<delete-subscription>. The accept/reject per path is itself a key API signal
(which paths support NETCONF dynamic subscription / on-change).

    .venv-harness/bin/python netconf_subscribe.py --device C9300 --limit 5
    .venv-harness/bin/python netconf_subscribe.py --all
    .venv-harness/bin/python netconf_subscribe.py --device C9300 --on-change --config-roots
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from collect_fleet import load_env, load_devices
from netconf_get import (
    _connect, build_ns_map, yang_library_ns, load_prefix_to_module, load_roots,
)
from ncclient.xml_ import to_ele

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
MANIFEST = OUT / "streaming-manifest.json"

# IOS XE implements the pre-standard draft: ietf-event-notifications +
# draft ietf-yang-push (NOT the final RFC 8641 ietf-subscribed-notifications).
EN_NS = "urn:ietf:params:xml:ns:yang:ietf-event-notifications"
YP_NS = "urn:ietf:params:xml:ns:yang:ietf-yang-push"
MAX_PAYLOAD = 40_000


def establish_rpc(ns: str, prefix: str, xpath: str, interval_cs: int,
                  on_change: bool = False) -> str:
    # Periodic subscriptions carry <yp:period>; on-change (config) subscriptions
    # carry <yp:dampening-period> instead -- its presence is what selects the
    # on-change update trigger in the pre-standard draft. dampening-period=0 means
    # report every change with no hold-down. On establish the device also sends an
    # initial sync-on-start push-update carrying the current (config) contents.
    trigger = (f'<yp:dampening-period>{interval_cs}</yp:dampening-period>' if on_change
               else f'<yp:period>{interval_cs}</yp:period>')
    return (
        f'<establish-subscription xmlns="{EN_NS}" xmlns:yp="{YP_NS}">'
        f'<stream>yp:yang-push</stream>'
        f'<yp:xpath-filter xmlns:{prefix}="{ns}">{xpath}</yp:xpath-filter>'
        f'{trigger}'
        f'</establish-subscription>'
    )


def _looks_like_drop(conn, exc) -> bool:
    """True when the SSH/NETCONF session is gone (reconnect needed) rather than a
    benign per-RPC reject. establish-subscription rejects come back as normal
    replies, so an *exception* here almost always means the transport died."""
    if not getattr(conn, "connected", True):
        return True
    msg = str(exc).lower()
    return any(s in msg for s in (
        "not connected", "session is closed", "session close", "socket",
        "transport", "eof occurred", "connection reset"))


def _subscribe_root(conn, r, ns, keys, period_cs, window, on_change=False):
    """Establish one yang-push subscription (periodic, or on-change when
    on_change=True), capture the first push, then delete it. A session-drop on
    <establish-subscription> propagates to the caller so it can reconnect; a
    reject reply is recorded as a normal result."""
    reply = str(conn.dispatch(to_ele(establish_rpc(ns, r["prefix"], r["xpath"], period_cs, on_change))))
    m = re.search(r"subscription-id[^>]*>(\d+)<", reply)
    sub_id = m.group(1) if m else None
    if not sub_id:
        return {**keys, "status": "rejected", "bytes": 0, "payload": reply[:2000]}
    payload, got = "", False
    try:
        note = conn.take_notification(block=True, timeout=window)
        if note is not None:
            payload = getattr(note, "notification_xml", "") or ""
            got = bool(payload)
    except Exception:  # noqa: BLE001
        pass
    entry = {**keys, "status": "streamed" if got else "accepted-nodata",
             "sub_id": sub_id, "bytes": len(payload), "payload": payload[:MAX_PAYLOAD]}
    try:
        conn.dispatch(to_ele(
            f'<delete-subscription xmlns="{EN_NS}"><subscription-id>{sub_id}</subscription-id></delete-subscription>'))
    except Exception:  # noqa: BLE001
        pass
    return entry


def collect_device(dev, env, roots, limit, period_cs, window, out_path=None, on_change=False):
    conn = _connect(dev, env)
    nsmap = build_ns_map(conn.server_capabilities)
    nsmap.update(yang_library_ns(conn))
    p2m = load_prefix_to_module()
    ns_by_prefix = {}
    for prefix, module in p2m.items():
        if module in nsmap:
            ns_by_prefix[prefix] = nsmap[module]
        elif module.startswith("Cisco-IOS-XE-"):
            ns_by_prefix[prefix] = f"http://cisco.com/ns/yang/{module}"
    for module, ns in nsmap.items():
        ns_by_prefix.setdefault(module, ns)

    todo = roots[:limit] if limit else roots
    kind = "dampening" if on_change else "period"
    print(f"  {dev['pid']}: {len(todo)} roots to subscribe ({kind} {period_cs}cs, window {window}s)")
    entries = []

    def _save():
        if out_path:
            Path(out_path).write_text(json.dumps(
                {"pid": dev["pid"], "host": dev["host"], "entries": entries},
                ensure_ascii=False), encoding="utf-8")

    i = 0
    reconnects = 0
    cur_fails = 0
    while i < len(todo):
        r = todo[i]
        module = r.get("module") or p2m.get(r["prefix"], r["prefix"])
        ns = nsmap.get(module)
        if not ns and module.startswith("Cisco-IOS-XE-"):
            ns = f"http://cisco.com/ns/yang/{module}"
        if not ns:
            ns = ns_by_prefix.get(r["prefix"])
        keys = {k: r[k] for k in ("xpath", "prefix", "container", "category")}
        keys["module"] = r.get("module")
        keys["mode"] = "on-change" if on_change else "periodic"
        if not ns:
            entries.append({**keys, "status": "no-namespace", "bytes": 0, "payload": ""})
            i += 1
            continue
        try:
            entries.append(_subscribe_root(conn, r, ns, keys, period_cs, window, on_change))
            i += 1
            cur_fails = 0
            if i % 40 == 0:
                _save()
                streamed = sum(1 for e in entries if e["status"] == "streamed")
                print(f"    ...{i}/{len(todo)} ({streamed} streamed)", flush=True)
        except Exception as ex:  # noqa: BLE001 — session drop OR a per-RPC error
            if not _looks_like_drop(conn, ex):
                entries.append({**keys, "status": "rejected", "bytes": 0,
                                "error": str(ex)[:200], "payload": ""})
                i += 1
                cur_fails = 0
                continue
            # Session dropped mid-run — reconnect and resume. RFC 8639 dynamic
            # subscriptions are session-bound, so the device tears down the
            # orphaned subs when the old session closes.
            cur_fails += 1
            try:
                conn.close_session()
            except Exception:  # noqa: BLE001
                pass
            if cur_fails >= 3:  # poison root: record + skip so we don't loop forever
                entries.append({**keys, "status": "session-drop", "bytes": 0,
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


def manifest_roots(pid: str):
    """Streaming-manifest roots for this device (fall back to catalog roots)."""
    try:
        man = json.loads(MANIFEST.read_text(encoding="utf-8"))
        key = pid if pid in man["devices"] else next((k for k in man["devices"] if k in pid or pid in k), None)
        if key:
            out = []
            for e in man["devices"][key]:
                if not e.get("root"):
                    continue
                body = e["xpath"].lstrip("/")
                prefix, _, rest = body.partition(":")
                out.append({"xpath": e["xpath"], "prefix": prefix,
                            "container": rest.split("/")[0], "category": e["category"]})
            if out:
                # streamable flavors first (MIB is SNMP-bridge, not yang-push subscribable)
                order = {"oper": 0, "openconfig": 1, "ietf": 2, "other": 3,
                         "native-config": 4, "cfg": 5, "wireless": 6, "mib": 7}
                out.sort(key=lambda r: (order.get(r["category"], 9), r["xpath"]))
                return out
    except (json.JSONDecodeError, OSError, KeyError):
        pass
    return load_roots()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--period-cs", type=int, default=1000, help="Periodic interval (centiseconds).")
    ap.add_argument("--dampening-cs", type=int, default=0,
                    help="On-change dampening period (centiseconds); 0 = report every change.")
    ap.add_argument("--window", type=int, default=15, help="Seconds to wait for the first push-update.")
    ap.add_argument("--on-change", action="store_true",
                    help="Establish on-change (config) subscriptions instead of periodic.")
    ap.add_argument("--both", action="store_true",
                    help="Probe each root with BOTH periodic and on-change (config subscription).")
    ap.add_argument("--config-roots", action="store_true",
                    help="Probe only config roots (native-config + cfg).")
    args = ap.parse_args()
    env = load_env()
    if not args.all and not args.device:
        raise SystemExit("Specify --device <pid> or --all")
    roots = load_roots()
    if args.config_roots:
        roots = [r for r in roots if r.get("category") in ("native-config", "cfg")]
    if args.both:
        modes = [False, True]
    elif args.on_change:
        modes = [True]
    else:
        modes = [False]
    # Only the plain full-catalog periodic run owns netconf-sub-<pid>.json; any
    # config-roots / on-change / both run writes the config subscription file so
    # it never clobbers the full periodic collection.
    is_config_run = args.config_roots or args.on_change or args.both
    tag = "netconf-sub-config" if is_config_run else "netconf-sub"
    for dev in load_devices([args.device] if args.device else None):
        labels = "+".join("on-change" if m else "periodic" for m in modes)
        print(f"\n=== NETCONF establish-subscription [{labels}] {dev['pid']} ({dev['host']}) ===")
        out = OUT / f"{tag}-{dev['pid']}.json"
        entries = []
        try:
            for on_change in modes:
                interval = args.dampening_cs if on_change else args.period_cs
                result = collect_device(dev, env, roots, args.limit, interval,
                                        args.window, out_path=None, on_change=on_change)
                entries.extend(result["entries"])
        except Exception as e:  # noqa: BLE001
            print(f"  ! {dev['pid']} failed: {e}")
            continue
        out.write_text(json.dumps(
            {"pid": dev["pid"], "host": dev["host"], "entries": entries},
            ensure_ascii=False), encoding="utf-8")
        streamed = sum(1 for e in entries if e["status"] == "streamed")
        print(f"  wrote {out.name}: {len(entries)} subs, {streamed} streamed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
