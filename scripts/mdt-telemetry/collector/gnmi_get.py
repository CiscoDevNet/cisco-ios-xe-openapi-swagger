#!/usr/bin/env python3
"""gnmi_get.py — gNMI Get of every module root plus nested OpenConfig containers (TLS :9339).

gNMI needs an explicit origin (per the IOS XE config guide):
  - Cisco IOS-XE YANG (oper/native/cfg/ietf/other):  rfc7951:/<module-name>:<container>
  - OpenConfig:                                        openconfig:/<container>[/<child>...]
  - MIB (SNMP): not served over gNMI -> recorded as 'unsupported'.

Captures three GetRequest datatypes per path so config vs operational state are
cleanly separated (like NETCONF <get-config> vs a state read):
  - all     (config + operational state)
  - config  (configured/intended values only)
  - state   (operational state only)

OpenConfig is walked per container/list from output/openconfig-nodes.json
(gnmi_oc_catalog.py): a node is only probed when its parent returned data.

A transport failure (reset, refused) reconnects with backoff; if the server stays
down the device stops and saves, and --resume continues later. Roots that crash
gnmib are never sent (UNSAFE_PATHS). Raw payloads are kept whole (MAX_PAYLOAD guard).

Writes output/gnmi-<PID>.json for the dataset builder + comparison matrix.

    .venv-harness/bin/python gnmi_get.py --device C9300 --limit 5
    .venv-harness/bin/python gnmi_get.py --all [--resume]
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from collect_fleet import load_env, load_devices
from netconf_get import _module_to_prefix, load_prefix_to_module, load_roots

from pygnmi.client import gNMIclient

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
OC_CATALOG = OUT / "openconfig-nodes.json"
GNMI_PORT = 9339  # secure gNMI (TLS); insecure 50052 is no longer used
MAX_PAYLOAD = 5_000_000
RPC_TIMEOUT = 120
# gNMI GetRequest.type: all=config+state, config=config-only, state=oper-only.
DATATYPES = ("all", "config", "state")
# Get on these resets the connection and leaves gnmib refusing connections (26.1.1, all platforms).
UNSAFE_PATHS = {"/notif-bis:streams", "/confd_dyncfg:confdConfig"}
TRANSPORT_MARKERS = ("failed to connect", "Stream removed", "Connection reset", "Socket closed",
                     "UNAVAILABLE", "Channel closed", "Handshake")
RECONNECT_WAITS = (5, 15, 30, 60, 120)
# A resumed run re-probes only these (anything else is a final answer from the device).
RETRY_STATUSES = {"transport", "timeout"}


def gnmi_path(prefix, module, container, category):
    if category == "mib":
        return None  # gNMI does not serve SNMP MIBs
    if category == "openconfig":
        return f"openconfig:/{container}"
    return f"rfc7951:/{module}:{container}"


def is_transport_error(message: str) -> bool:
    return any(marker in message for marker in TRANSPORT_MARKERS)


def _is_empty_value(value) -> bool:
    if isinstance(value, dict):
        return all(_is_empty_value(child) for child in value.values())
    if isinstance(value, list):
        return all(_is_empty_value(child) for child in value)
    return value is None or value == ""


def response_has_data(response: dict) -> bool:
    """IOS XE answers an unpopulated node with an update whose val is {} -> that is not data."""
    return any(not _is_empty_value(update.get("val"))
               for notification in response.get("notification") or []
               for update in notification.get("update") or [])


def load_openconfig_nodes() -> list[dict]:
    if not OC_CATALOG.exists():
        raise SystemExit(f"{OC_CATALOG.name} missing: run gnmi_oc_catalog.py first")
    return json.loads(OC_CATALOG.read_text(encoding="utf-8"))["nodes"]


def build_targets(roots: list[dict], oc_nodes: list[dict]) -> list[dict]:
    """Non-OpenConfig module roots, then every OpenConfig container (parents first)."""
    p2m = load_prefix_to_module()
    m2p = _module_to_prefix()
    targets = []
    for root in roots:
        if root["category"] == "openconfig":
            continue  # the schema catalog below replaces the spec-derived OC roots
        module = root.get("module") or p2m.get(root["prefix"], root["prefix"])
        targets.append({"xpath": root["xpath"], "prefix": root["prefix"], "container": root["container"],
                        "category": root["category"], "module": module,
                        "gnmi_path": gnmi_path(root["prefix"], module, root["container"], root["category"]),
                        "depth": 1, "parent": None})
    for node in oc_nodes:
        prefix = m2p.get(node["module"], node["module"])
        container = node["path"].lstrip("/")
        parent = node["path"].rsplit("/", 1)[0] or None
        targets.append({"xpath": f"/{prefix}:{container}", "prefix": prefix, "container": container,
                        "category": "openconfig", "module": node["module"],
                        "gnmi_path": f"openconfig:{node['path']}", "depth": node["depth"],
                        "parent": f"/{prefix}:{parent.lstrip('/')}" if node["depth"] > 1 else None})
    return targets


def _load_previous(out_path: Path) -> dict:
    """(xpath, op) -> entry from an earlier run, minus retryable failures."""
    if not out_path.exists():
        return {}
    try:
        doc = json.loads(out_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    kept = {}
    for entry in doc.get("entries", []):
        if entry.get("status") in RETRY_STATUSES or is_transport_error(entry.get("error", "")):
            continue
        if entry.get("status") == "data":
            try:
                entry["status"] = "data" if response_has_data(json.loads(entry["payload"])) else "empty"
            except (json.JSONDecodeError, KeyError, TypeError):
                continue  # truncated by an older payload cap -> fetch again
        kept[(entry["xpath"], entry["op"])] = entry
    return kept


def collect_device(dev, env, targets, limit, out_path=None, resume=False, skip=frozenset()):
    todo = targets[:limit] if limit else targets
    previous = _load_previous(Path(out_path)) if (resume and out_path) else {}
    entries: list[dict] = []
    status_all: dict[str, str] = {}  # xpath -> datatype=all status (drives nested pruning)
    client = None

    def _save():
        if out_path:
            Path(out_path).write_text(json.dumps(
                {"pid": dev["pid"], "host": dev["host"], "entries": entries},
                ensure_ascii=False), encoding="utf-8")

    def _connect():
        nonlocal client
        if client is not None:
            try:
                client.close()
            except Exception:  # noqa: BLE001
                pass
        for wait in (0, *RECONNECT_WAITS):
            time.sleep(wait)
            try:
                client = gNMIclient(target=(dev["host"], GNMI_PORT), username=env["IOSXE_USER"],
                                    password=env["IOSXE_PASS"], insecure=False, skip_verify=True,
                                    timeout=RPC_TIMEOUT)
                client.connect()
                return True
            except Exception as error:  # noqa: BLE001
                print(f"    connect failed ({str(error)[-80:]}); retry in next backoff step", flush=True)
        client = None
        return False

    def _get(path, datatype):
        """One Get -> (status, bytes, payload, error). Reconnects once on a transport drop."""
        for attempt in (1, 2):
            try:
                response = client.get(path=[path], datatype=datatype, encoding="json_ietf")
                body = json.dumps(response, ensure_ascii=False)
                return ("data" if response_has_data(response) else "empty"), len(body), body[:MAX_PAYLOAD], ""
            except Exception as error:  # noqa: BLE001 — per-path gNMI error (unsupported path etc.)
                message = str(error).split("Error:")[-1][:200].strip()
                if "Deadline" in message or "DEADLINE" in message:
                    return "timeout", 0, "", message
                if not is_transport_error(message):
                    return "error", 0, "", message
                if attempt == 1 and _connect():
                    continue
                return "transport", 0, "", message
        return "transport", 0, "", "unreachable"

    if not _connect():
        print(f"  {dev['pid']}: gNMI unreachable; nothing collected", flush=True)
        return {"pid": dev["pid"], "host": dev["host"], "entries": []}
    print(f"  {dev['pid']}: {len(todo)} paths x {len(DATATYPES)} datatypes"
          + (f" (resume: {len(previous)} kept)" if previous else ""), flush=True)

    probed = 0
    for index, target in enumerate(todo, 1):
        keys = {k: target[k] for k in ("xpath", "prefix", "container", "category", "module")}
        if target["depth"] > 1:
            keys.update(depth=target["depth"], parent=target["parent"])
        path = target["gnmi_path"]
        if path is None:
            entries.append({**keys, "op": "all", "gnmi_path": "", "status": "unsupported", "bytes": 0, "payload": ""})
            continue
        if target["parent"] and status_all.get(target["parent"]) != "data":
            continue  # nothing under an empty/failed parent
        if target["xpath"] in UNSAFE_PATHS or target["xpath"] in skip:
            entries.append({**keys, "op": "all", "gnmi_path": path, "status": "skipped-unsafe",
                            "bytes": 0, "payload": ""})
            continue
        for datatype in DATATYPES:
            kept = previous.get((target["xpath"], datatype))
            if kept is not None:
                entries.append(kept)
            elif datatype != "all" and status_all.get(target["xpath"]) != "data":
                # config/state are subsets of all: nothing to read when all had nothing
                base = next(e for e in reversed(entries) if e["xpath"] == target["xpath"] and e["op"] == "all")
                entries.append({**keys, "op": datatype, "gnmi_path": path, "status": base["status"],
                                "bytes": 0, "payload": "", **({"error": base["error"]} if base.get("error") else {})})
            else:
                status, size, payload, error = _get(path, datatype)
                probed += 1
                entry = {**keys, "op": datatype, "gnmi_path": path, "status": status, "bytes": size,
                         "payload": payload}
                if error:
                    entry["error"] = error
                entries.append(entry)
                if status == "transport":
                    _save()
                    print(f"    gNMI server down at {target['xpath']} ({error[-80:]}); saved, use --resume",
                          flush=True)
                    return {"pid": dev["pid"], "host": dev["host"], "entries": entries}
            if datatype == "all":
                status_all[target["xpath"]] = entries[-1]["status"]
        if index % 40 == 0:
            _save()
            data = sum(1 for e in entries if e["op"] == "all" and e["status"] == "data")
            print(f"    ...{index}/{len(todo)} ({data} data, {probed} Gets)", flush=True)
    try:
        client.close()
    except Exception:  # noqa: BLE001
        pass
    _save()
    return {"pid": dev["pid"], "host": dev["host"], "entries": entries}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--resume", action="store_true",
                        help="keep finished paths from output/gnmi-<PID>.json; retry transport/timeouts")
    parser.add_argument("--openconfig-only", action="store_true", help="only the OpenConfig schema walk")
    parser.add_argument("--skip", action="append", default=[], metavar="XPATH",
                        help="never send this root (e.g. one that crashed gnmib on this device); repeatable")
    args = parser.parse_args()
    env = load_env()
    if not args.all and not args.device:
        raise SystemExit("Specify --device <pid> or --all")
    targets = build_targets(load_roots(), load_openconfig_nodes())
    if args.openconfig_only:
        targets = [t for t in targets if t["category"] == "openconfig"]
    for dev in load_devices([args.device] if args.device else None):
        print(f"\n=== gNMI Get {dev['pid']} ({dev['host']}) ===", flush=True)
        out = OUT / f"gnmi-{dev['pid']}.json"
        try:
            result = collect_device(dev, env, targets, args.limit, out_path=out, resume=args.resume,
                                    skip=frozenset(args.skip))
        except Exception as e:  # noqa: BLE001
            print(f"  ! {dev['pid']} failed: {e}")
            continue
        got = sum(1 for e in result["entries"] if e["op"] == "all" and e["status"] == "data")
        print(f"  wrote {out.name}: {len(result['entries'])} probes, {got} paths with data "
              f"({out.stat().st_size/1024:.0f} KB)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
