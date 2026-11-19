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
import os
import sys
import threading
import time
from pathlib import Path

from collect_fleet import load_env, load_devices
from netconf_get import load_roots
from gnmi_get import GNMI_PORT, MAX_PAYLOAD, UNSAFE_PATHS, _is_empty_value, build_targets, load_openconfig_nodes

from pygnmi.client import gNMIclient

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
SAMPLE_NS = 60_000_000_000  # 60s sample interval (dial-out style: first update is immediate)
# Large subtrees (openconfig interfaces/components) take well over 4 s to build the first sample.
SAMPLE_WINDOW = 60


def _client(dev, env):
    gc = gNMIclient(target=(dev["host"], GNMI_PORT), username=env["IOSXE_USER"],
                    password=env["IOSXE_PASS"], insecure=False, skip_verify=True,
                    timeout=25, no_qos_marking=True)
    gc.connect()
    return gc


def _once_has_data(messages) -> bool:
    """An accepted ONCE on an unpopulated node still sends update messages, with no or {} values."""
    for message in messages:
        notification = message.get("update") if isinstance(message, dict) else None
        if not isinstance(notification, dict):
            continue
        if any(not _is_empty_value(update.get("val")) for update in notification.get("update") or []):
            return True
    return False


def probe_once(gc, path):
    sub = {"subscription": [{"path": path}], "mode": "once", "encoding": "json_ietf"}
    try:
        ups = list(gc.subscribe2(subscribe=sub))  # collect all once-updates (bg channel-close is harmless)
    except Exception:  # noqa: BLE001
        return "rejected", 0, ""
    body = json.dumps(ups, default=str, ensure_ascii=False) if ups else ""
    return ("streamed" if _once_has_data(ups) else "accepted-nodata"), len(body), body[:MAX_PAYLOAD]


def probe_stream(gc, path, mode, window=4):
    """Probe a STREAM subscription (sample or on_change) with a hard time bound:
    a supported path emits its first update immediately; if nothing arrives within
    the window the reader is abandoned (daemon) and we report accepted-nodata so an
    empty path can't block. sample_interval only applies to sample mode."""
    subscription = {"path": path, "mode": mode}
    if mode == "sample":
        subscription["sample_interval"] = SAMPLE_NS
    sub = {"subscription": [subscription], "mode": "stream", "encoding": "json_ietf"}
    out = {"st": "accepted-nodata"}

    def read():
        try:
            for resp in gc.subscribe_stream(subscribe=sub):
                r = resp if isinstance(resp, dict) else dict(resp)
                if _once_has_data([r]):
                    out["st"] = "streamed"
                    return
        except Exception:  # noqa: BLE001
            out["st"] = "rejected"

    t = threading.Thread(target=read, daemon=True)
    t.start()
    t.join(window)
    return out["st"]


def _probe_root(gc, path, timeout=SAMPLE_WINDOW + 40):
    """Run ONCE, then SAMPLE + ON_CHANGE (only where ONCE streamed data) in a worker
    thread with a hard timeout so one unresponsive path can't stall the fleet.
    Returns a dict, or None on timeout (caller must reset the client)."""
    result = {}

    def work():
        try:
            once_st, nbytes, payload = probe_once(gc, path)
            result.update(once=once_st, bytes=nbytes, payload=payload)
            if once_st == "streamed":
                result["sample"] = probe_stream(gc, path, "sample", window=SAMPLE_WINDOW)
                result["onchange"] = probe_stream(gc, path, "on_change")
            else:  # empty/rejected/unsupported -> the stream modes match ONCE
                result["sample"] = once_st
                result["onchange"] = once_st
        except Exception as e:  # noqa: BLE001
            result.update(error=str(e).split("details =")[-1][:120].strip())

    t = threading.Thread(target=work, daemon=True)
    t.start()
    t.join(timeout)
    return None if t.is_alive() else result


def get_supported_paths(pid):
    """gNMI paths worth subscribing to, from the gNMI Get baseline. Subscribe uses identical
    path validation, so anything Get rejects Subscribe will reject too; probing only these
    avoids pygnmi background-thread crashes on rejected paths. Module roots count when Get
    accepted them (data or empty); nested OpenConfig nodes only when Get returned data."""
    f = OUT / f"gnmi-{pid}.json"
    if not f.exists():
        return None  # no Get baseline -> probe everything (small/limited runs)
    try:
        doc = json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return {e.get("gnmi_path") for e in doc.get("entries", [])
            if e.get("op") == "all" and e.get("gnmi_path")
            and (e.get("status") == "data" or (e.get("status") == "empty" and not e.get("parent")))}


def collect_device(dev, env, targets, limit, out_path=None, supported=None):
    todo = targets[:limit] if limit else targets
    entries = []

    def _save():
        if out_path:
            Path(out_path).write_text(json.dumps(
                {"pid": dev["pid"], "host": dev["host"], "entries": entries},
                ensure_ascii=False), encoding="utf-8")

    gc = _client(dev, env)
    print(f"  {dev['pid']}: {len(todo)} paths -> ONCE (support signal)")

    def _reconnect():
        """Best-effort reconnect; returns a live client or None if the server is down."""
        nonlocal gc
        try:
            gc.close()
        except Exception:
            pass
        for _ in range(3):
            try:
                gc = _client(dev, env)
                return gc
            except Exception:  # noqa: BLE001
                time.sleep(3)
        return None

    for i, target in enumerate(todo, 1):
        path = target["gnmi_path"]
        keys = {k: target[k] for k in ("xpath", "prefix", "container", "category", "module")}
        if target["depth"] > 1:
            keys.update(depth=target["depth"], parent=target["parent"])
        if path is None:
            entries.append({**keys, "gnmi_path": "", "once": "unsupported", "sample": "unsupported",
                            "onchange": "unsupported", "bytes": 0, "payload": ""})
            continue
        if target["xpath"] in UNSAFE_PATHS:
            continue
        if supported is not None and path not in supported:
            if target["depth"] > 1:
                continue  # nested node without Get data: nothing to subscribe to
            # gNMI Get rejected this path -> Subscribe rejects it too; record without probing
            entries.append({**keys, "gnmi_path": path, "once": "rejected", "sample": "rejected",
                            "onchange": "rejected", "bytes": 0, "payload": ""})
            continue
        res = _probe_root(gc, path)
        if res is None:  # hung path -> reset client and move on
            entries.append({**keys, "gnmi_path": path, "once": "timeout", "sample": "timeout",
                            "onchange": "timeout", "bytes": 0, "payload": ""})
            if _reconnect() is None:
                print(f"    server unreachable after {i} roots; saving partial", flush=True)
                break
        elif "error" in res:
            # A rejected subscription does not close the shared channel; keep the
            # client (reconnecting on every reject exhausts the gNMI server).
            err = res["error"]
            entries.append({**keys, "gnmi_path": path, "once": "rejected", "sample": "rejected",
                            "onchange": "rejected", "bytes": 0, "error": err, "payload": ""})
            if "Channel closed" in err or "Stream removed" in err or "UNAVAILABLE" in err:
                if _reconnect() is None:
                    print(f"    server unreachable after {i} roots; saving partial", flush=True)
                    break
        else:
            entries.append({**keys, "gnmi_path": path, "once": res["once"], "sample": res["sample"],
                            "onchange": res.get("onchange", "skipped"),
                            "bytes": res["bytes"], "payload": res["payload"]})
        if i % 10 == 0:
            _save()
            print(f"    ...{i}/{len(todo)} (once ok={sum(1 for e in entries if e['once']=='streamed')})", flush=True)
        if i % 40 == 0:  # recycle the client to release abandoned stream subscriptions
            _reconnect()
    try:
        gc.close()
    except Exception:
        pass
    _save()
    return {"pid": dev["pid"], "host": dev["host"], "entries": entries}


def resample_device(dev, env, window):
    """Re-probe SAMPLE, independent of ONCE, on every path where gNMI Get returned data but SAMPLE
    did not stream (the 4 s window is too short for large subtrees). Updates gnmi-sub-<PID>.json."""
    sub_file = OUT / f"gnmi-sub-{dev['pid']}.json"
    get_doc = json.loads((OUT / f"gnmi-{dev['pid']}.json").read_text(encoding="utf-8"))
    get_data = {e["gnmi_path"] for e in get_doc["entries"] if e.get("op") == "all" and e.get("status") == "data"}
    doc = json.loads(sub_file.read_text(encoding="utf-8"))
    todo = [e for e in doc["entries"] if e.get("gnmi_path") in get_data and e.get("sample") != "streamed"]
    print(f"  {dev['pid']}: re-probing SAMPLE on {len(todo)} paths ({window}s window)", flush=True)
    gc = _client(dev, env)
    changed = 0
    for i, entry in enumerate(todo, 1):
        status = probe_stream(gc, entry["gnmi_path"], "sample", window=window)
        if status != entry.get("sample"):
            changed += 1
        entry["sample"] = status
        if i % 5 == 0 or status == "rejected":
            try:
                gc.close()  # releases abandoned stream subscriptions
            except Exception:  # noqa: BLE001
                pass
            gc = _client(dev, env)
            sub_file.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
            print(f"    ...{i}/{len(todo)} ({changed} changed)", flush=True)
    try:
        gc.close()
    except Exception:  # noqa: BLE001
        pass
    sub_file.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    streamed = sum(1 for e in todo if e["sample"] == "streamed")
    print(f"  {dev['pid']}: SAMPLE now streams on {streamed}/{len(todo)} re-probed paths", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--resample", action="store_true",
                    help="only re-probe SAMPLE where Get has data but SAMPLE did not stream")
    ap.add_argument("--window", type=int, default=SAMPLE_WINDOW, help="SAMPLE wait in seconds for --resample")
    args = ap.parse_args()
    env = load_env()
    if not args.all and not args.device:
        raise SystemExit("Specify --device <pid> or --all")
    if args.resample:
        for dev in load_devices([args.device] if args.device else None):
            resample_device(dev, env, args.window)
        return 0
    targets = build_targets(load_roots(), load_openconfig_nodes())  # same set as gNMI Get so gaps are visible
    for dev in load_devices([args.device] if args.device else None):
        print(f"\n=== gNMI Subscribe {dev['pid']} ({dev['host']}) ===")
        supported = get_supported_paths(dev["pid"])  # network-probe only Get-supported paths
        out = OUT / f"gnmi-sub-{dev['pid']}.json"
        try:
            result = collect_device(dev, env, targets, args.limit, out_path=out, supported=supported)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {dev['pid']} failed: {e}")
            continue
        onces = sum(1 for e in result["entries"] if e["once"] == "streamed")
        samples = sum(1 for e in result["entries"] if e["sample"] == "streamed")
        print(f"  wrote {out.name}: {len(result['entries'])} roots, ONCE={onces} SAMPLE={samples}")
    return 0


if __name__ == "__main__":
    rc = main()
    # Files are already saved; skip interpreter teardown to avoid a gRPC C++ abort
    # from lingering pygnmi daemon threads (harmless but leaves core dumps).
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(rc)
