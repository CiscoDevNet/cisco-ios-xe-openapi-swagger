#!/usr/bin/env python3
"""restconf_get.py — RESTCONF GET of all-flavor root containers (matrix coverage).

The RESTCONF browse dataset (restconf-live-data.json) is built by the capture
harness from a full-tree walk. This collector is the self-contained companion to
netconf_get.py / gnmi_get.py: it probes the SAME depth-1 module root containers
(oper, cfg, native-config, openconfig, ietf, other, MIB) over RESTCONF and writes
output/restconf-<PID>.json so build_protocol_matrix.py can score RESTCONF the same
way it scores NETCONF/gNMI (from the raw collector output).

GET /restconf/data/<module>:<container> returns the whole subtree, so a depth-1
probe of every module tells us which modules a device actually serves over
RESTCONF — exactly the gap signal the comparison matrix needs.

Self-contained: uses requests with trust_env=False so the corp proxy env vars are
ignored (devices are direct-reach, incl. the .110 WAN box on 10.195.120.0/24).

    python -X utf8 restconf_get.py --device C9200 --limit 5   # smoke
    python -X utf8 restconf_get.py --device C9200             # full
    python -X utf8 restconf_get.py --device C9300-STACK8-WAN  # .110 WAN
    python -X utf8 restconf_get.py --all
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests
import urllib3
from requests.auth import HTTPBasicAuth

from collect_fleet import load_env, load_devices  # reuse proven inventory/env helpers
from netconf_get import load_roots  # same depth-1 root set across every flavor + MIB

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # self-signed device certs

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
MAX_PAYLOAD = 200_000  # cap stored payload per path (chars) to keep files sane
TIMEOUT = 30


def _session(env) -> requests.Session:
    s = requests.Session()
    s.trust_env = False  # ignore http(s)_proxy / no_proxy; devices are direct-reach
    s.verify = False     # device certs are self-signed
    s.auth = HTTPBasicAuth(env["IOSXE_USER"], env["IOSXE_PASS"])
    s.headers.update({"Accept": "application/yang-data+json"})
    return s


def classify(sess, host, rc_path, timeout=TIMEOUT) -> dict:
    """One RESTCONF GET. 200 => served data, 204 => supported-but-empty, else gap."""
    url = f"https://{host}:443/restconf/data{rc_path}"
    try:
        r = sess.get(url, timeout=timeout)
    except requests.RequestException as e:  # transport error (timeout, refused, reset)
        return {"status": "error", "http": 0, "bytes": 0, "error": str(e)[:150], "payload": ""}
    body = r.text or ""
    if r.status_code == 200:
        return {"status": "data", "http": 200, "bytes": len(body), "payload": body[:MAX_PAYLOAD]}
    if r.status_code == 204:
        return {"status": "empty", "http": 204, "bytes": 0, "payload": ""}
    return {"status": "no", "http": r.status_code, "bytes": len(body), "error": body[:150], "payload": ""}


def collect_device(dev, env, roots, limit, out_path=None, timeout=TIMEOUT) -> dict:
    sess = _session(env)
    todo = roots[:limit] if limit else roots
    print(f"  {dev['pid']}: {len(todo)} RESTCONF roots @ {dev['host']}")

    entries = []

    def _save():
        if out_path:
            Path(out_path).write_text(json.dumps(
                {"pid": dev["pid"], "host": dev["host"], "entries": entries},
                ensure_ascii=False), encoding="utf-8")

    for i, r in enumerate(todo, 1):
        keys = {k: r[k] for k in ("xpath", "prefix", "container", "category")}
        keys["module"] = r.get("module")
        # RESTCONF qualifies the top node by MODULE name, not the YANG prefix the
        # catalog stores for ietf/openconfig roots (e.g. /if:interfaces must be
        # requested as /ietf-interfaces:interfaces). MIB/oper roots already use the
        # module name, so this is a no-op for them.
        rc_path = f"/{r.get('module') or r['prefix']}:{r['container']}"
        entries.append({**keys, "op": "get", "rc_path": rc_path,
                        **classify(sess, dev["host"], rc_path, timeout)})
        if i % 40 == 0:
            _save()
            print(f"    ...{i}/{len(todo)} "
                  f"({sum(1 for e in entries if e['status'] == 'data')} data)", flush=True)
    _save()
    return {"pid": dev["pid"], "host": dev["host"], "entries": entries}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", help="Device name/PID substring.")
    ap.add_argument("--all", action="store_true", help="All devices in inventory.")
    ap.add_argument("--limit", type=int, default=0, help="Only probe the first N roots (smoke test).")
    ap.add_argument("--timeout", type=int, default=TIMEOUT, help="Per-GET timeout (s); raise for WAN/large payloads.")
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
        print(f"\n=== RESTCONF {dev['pid']} ({dev['host']}) ===")
        out = OUT / f"restconf-{dev['pid']}.json"
        try:
            result = collect_device(dev, env, roots, args.limit, out_path=out, timeout=args.timeout)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {dev['pid']} failed: {e}")
            continue
        got = sum(1 for e in result["entries"] if e["status"] == "data")
        print(f"  wrote {out.name}: {len(result['entries'])} probes, {got} returned data "
              f"({out.stat().st_size/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
