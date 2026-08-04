#!/usr/bin/env python3
"""gnmi_get.py — gNMI Get of the all-flavor root containers (insecure :50052).

gNMI needs an explicit origin (per the IOS XE config guide):
  - Cisco IOS-XE YANG (oper/native/cfg/ietf/other):  rfc7951:/<module-name>:<container>
  - OpenConfig:                                        openconfig:/<container>
  - MIB (SNMP): not served over gNMI -> recorded as 'unsupported'.

Captures two datatypes per root so config vs state can be compared like NETCONF
<get> vs <get-config>:
  - all     (config + state)
  - config  (config only)

Writes output/gnmi-<PID>.json for the dataset builder + comparison matrix.

    .venv-harness/bin/python gnmi_get.py --device C9300 --limit 5
    .venv-harness/bin/python gnmi_get.py --all
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from collect_fleet import load_env, load_devices
from netconf_get import load_roots, load_prefix_to_module

from pygnmi.client import gNMIclient

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
GNMI_PORT = 50052
MAX_PAYLOAD = 40_000
DATATYPES = ("all", "config")


def gnmi_path(prefix, module, container, category):
    if category == "mib":
        return None  # gNMI does not serve SNMP MIBs
    if category == "openconfig":
        return f"openconfig:/{container}"
    return f"rfc7951:/{module}:{container}"


def collect_device(dev, env, roots, limit, out_path=None):
    p2m = load_prefix_to_module()
    todo = roots[:limit] if limit else roots
    entries = []

    def _save():
        if out_path:
            Path(out_path).write_text(json.dumps(
                {"pid": dev["pid"], "host": dev["host"], "entries": entries},
                ensure_ascii=False), encoding="utf-8")

    def _connect():
        gc = gNMIclient(target=(dev["host"], GNMI_PORT), username=env["IOSXE_USER"],
                        password=env["IOSXE_PASS"], insecure=True, timeout=30)
        gc.connect()
        return gc

    gc = _connect()
    print(f"  {dev['pid']}: {len(todo)} roots x {len(DATATYPES)} datatypes")
    i = 0
    fails = 0
    while i < len(todo):
        r = todo[i]
        module = p2m.get(r["prefix"], r["prefix"])
        path = gnmi_path(r["prefix"], module, r["container"], r["category"])
        keys = {k: r[k] for k in ("xpath", "prefix", "container", "category")}
        if path is None:
            entries.append({**keys, "op": "all", "gnmi_path": "", "status": "unsupported", "bytes": 0, "payload": ""})
            i += 1
            continue
        try:
            for dt in DATATYPES:
                try:
                    resp = gc.get(path=[path], datatype=dt, encoding="json_ietf")
                    body = json.dumps(resp, ensure_ascii=False)
                    has = bool(resp.get("notification") and any(
                        n.get("update") for n in resp["notification"]))
                    entries.append({**keys, "op": dt, "gnmi_path": path,
                                    "status": "data" if has else "empty",
                                    "bytes": len(body), "payload": body[:MAX_PAYLOAD]})
                except Exception as ge:  # noqa: BLE001 — per-path gNMI error (unsupported path etc.)
                    msg = str(ge).split("Error:")[-1][:150].strip()
                    entries.append({**keys, "op": dt, "gnmi_path": path,
                                    "status": "error", "bytes": 0, "error": msg, "payload": ""})
            i += 1
            fails = 0
            if i % 40 == 0:
                _save()
                print(f"    ...{i}/{len(todo)} ({sum(1 for e in entries if e['status']=='data')} data)", flush=True)
        except Exception:  # noqa: BLE001 — transport drop; reconnect
            fails += 1
            try:
                gc.close()
            except Exception:
                pass
            if fails >= 3:
                entries.append({**keys, "op": "all", "gnmi_path": path, "status": "timeout", "bytes": 0, "payload": ""})
                i += 1
                fails = 0
            time.sleep(2)
            try:
                gc = _connect()
            except Exception as e:  # noqa: BLE001
                print(f"    reconnect failed: {e}; saving partial")
                break
    try:
        gc.close()
    except Exception:
        pass
    _save()
    return {"pid": dev["pid"], "host": dev["host"], "entries": entries}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    env = load_env()
    roots = load_roots()
    if not args.all and not args.device:
        raise SystemExit("Specify --device <pid> or --all")
    for dev in load_devices([args.device] if args.device else None):
        print(f"\n=== gNMI Get {dev['pid']} ({dev['host']}) ===")
        out = OUT / f"gnmi-{dev['pid']}.json"
        try:
            result = collect_device(dev, env, roots, args.limit, out_path=out)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {dev['pid']} failed: {e}")
            continue
        got = sum(1 for e in result["entries"] if e["status"] == "data")
        print(f"  wrote {out.name}: {len(result['entries'])} probes, {got} data ({out.stat().st_size/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
