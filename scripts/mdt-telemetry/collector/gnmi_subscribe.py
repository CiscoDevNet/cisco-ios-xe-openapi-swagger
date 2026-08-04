#!/usr/bin/env python3
"""gnmi_subscribe.py — gNMI Subscribe ONCE + SAMPLE over the all-flavor roots.

Content note: a ONCE subscription, the first SAMPLE update, and a Get all return
the SAME snapshot of current state. So this collector's value is the SUPPORT
signal — which xpaths ACCEPT a ONCE / SAMPLE subscription (accept vs reject) —
plus the first payload for reference. IOS XE rejects the pygnmi default QoS
marking, so we pass no_qos_marking=True (that was the only thing blocking ONCE).

    .venv-harness/bin/python gnmi_subscribe.py --device C9300 --limit 8
    .venv-harness/bin/python gnmi_subscribe.py --all
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from collect_fleet import load_env, load_devices
from netconf_get import load_prefix_to_module
from netconf_subscribe import manifest_roots
from gnmi_get import gnmi_path, GNMI_PORT

from pygnmi.client import gNMIclient

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
MAX_PAYLOAD = 40_000
SAMPLE_NS = 10_000_000_000  # 10s


def _client(dev, env):
    gc = gNMIclient(target=(dev["host"], GNMI_PORT), username=env["IOSXE_USER"],
                    password=env["IOSXE_PASS"], insecure=True, timeout=25, no_qos_marking=True)
    gc.connect()
    return gc


def probe_once(gc, path):
    sub = {"subscription": [{"path": path}], "mode": "once", "encoding": "json_ietf"}
    try:
        first = next(iter(gc.subscribe2(subscribe=sub)), None)  # first update only; avoids close hang
    except StopIteration:
        first = None
    except Exception:  # noqa: BLE001
        return "rejected", 0, ""
    body = json.dumps(first, default=str, ensure_ascii=False) if first else ""
    return ("streamed" if first else "accepted-nodata"), len(body), body[:MAX_PAYLOAD]


def probe_sample(gc, path, window=5):
    sub = {"subscription": [{"path": path, "mode": "sample", "sample_interval": SAMPLE_NS}],
           "mode": "stream", "encoding": "json_ietf"}
    t0 = time.time()
    try:
        for resp in gc.subscribe(subscribe=sub):
            r = resp if isinstance(resp, dict) else dict(resp)
            if "update" in r:
                return "streamed"
            if time.time() - t0 > window:
                break
    except Exception:  # noqa: BLE001
        return "rejected"
    return "accepted-nodata"


def collect_device(dev, env, roots, limit, out_path=None):
    p2m = load_prefix_to_module()
    todo = roots[:limit] if limit else roots
    entries = []

    def _save():
        if out_path:
            Path(out_path).write_text(json.dumps(
                {"pid": dev["pid"], "host": dev["host"], "entries": entries},
                ensure_ascii=False), encoding="utf-8")

    gc = _client(dev, env)
    print(f"  {dev['pid']}: {len(todo)} roots -> ONCE + SAMPLE")
    for i, r in enumerate(todo, 1):
        module = p2m.get(r["prefix"], r["prefix"])
        path = gnmi_path(r["prefix"], module, r["container"], r["category"])
        keys = {k: r[k] for k in ("xpath", "prefix", "container", "category")}
        if path is None:
            entries.append({**keys, "gnmi_path": "", "once": "unsupported", "sample": "unsupported",
                            "bytes": 0, "payload": ""})
            continue
        try:
            once_st, nbytes, payload = probe_once(gc, path)
            sample_st = probe_sample(gc, path)
            entries.append({**keys, "gnmi_path": path, "once": once_st, "sample": sample_st,
                            "bytes": nbytes, "payload": payload})
        except Exception as e:  # noqa: BLE001 — likely a rejected path or transport blip
            msg = str(e).split("details =")[-1][:120].strip()
            entries.append({**keys, "gnmi_path": path, "once": "rejected", "sample": "rejected",
                            "bytes": 0, "error": msg, "payload": ""})
            try:
                gc.close()
            except Exception:
                pass
            gc = _client(dev, env)
        if i % 10 == 0:
            _save()
            print(f"    ...{i}/{len(todo)} (once ok={sum(1 for e in entries if e['once']=='streamed')})", flush=True)
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
    if not args.all and not args.device:
        raise SystemExit("Specify --device <pid> or --all")
    for dev in load_devices([args.device] if args.device else None):
        print(f"\n=== gNMI Subscribe {dev['pid']} ({dev['host']}) ===")
        roots = manifest_roots(dev["pid"])  # streamable roots, oper-first
        out = OUT / f"gnmi-sub-{dev['pid']}.json"
        try:
            result = collect_device(dev, env, roots, args.limit, out_path=out)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {dev['pid']} failed: {e}")
            continue
        onces = sum(1 for e in result["entries"] if e["once"] == "streamed")
        samples = sum(1 for e in result["entries"] if e["sample"] == "streamed")
        print(f"  wrote {out.name}: {len(result['entries'])} roots, ONCE={onces} SAMPLE={samples}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
