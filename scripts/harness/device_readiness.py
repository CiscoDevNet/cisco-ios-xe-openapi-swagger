"""Read-only device readiness probe for the Track B harness.

Validates that a device is ready for a long multi-protocol collection BEFORE we
start one — especially for a WAN device where a half-provisioned interface or a
lossy path would otherwise waste a multi-hour walk.

STRICTLY READ-ONLY. It never configures anything:
  - TCP reachability + latency to 443/830/9339/22 (raw sockets, proxy-agnostic)
  - RESTCONF GET of known-good oper + config roots (via the GET-only client)
  - gNMI Capabilities + a known-good Get on :9339 (pygnmi, TLS skip-verify)
  - NETCONF hello/capabilities on :830 (ncclient)
  - Stack health: `show switch` over SSH (netmiko) -> member count + states
  - MDT dial-out (:57500) return-path readiness is REPORTED as deferred, because
    validating it end-to-end requires configuring a subscription on the device
    (a write) — out of scope for this read-only probe.

Credentials come from scripts/harness/.env via inventory.load_credentials and are
never printed. Device traffic bypasses the corp proxy (trust_env=False / raw
sockets) so a non-10.85.134.x WAN host is reached directly.

Run:
  .venv-harness/bin/python -X utf8 -m scripts.harness.device_readiness --device C9300-STACK8-WAN
  .venv-harness/bin/python -X utf8 -m scripts.harness.device_readiness --all
"""
from __future__ import annotations

import argparse
import socket
import ssl
import sys
import time
from pathlib import Path
from typing import Optional

import requests

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.harness import inventory as inv
    from scripts.harness.request import restconf_get
else:  # pragma: no cover
    from . import inventory as inv
    from .request import restconf_get

# Ports we care about for the four collection planes (+ dial-out return path).
PORTS = {
    "restconf-443": 443,
    "netconf-830": 830,
    "gnmi-9339": 9339,
    "ssh-22": 22,
}
DIALOUT_PORT = 57500

# Known-good roots that exist on any provisioned IOS XE box.
RESTCONF_OPER_PROBE = "/data/Cisco-IOS-XE-arp-oper:arp-data"
RESTCONF_CONFIG_PROBE = "/data/Cisco-IOS-XE-native:native/version"
GNMI_OPER_PROBE = "rfc7951:/Cisco-IOS-XE-arp-oper:arp-data"
GNMI_CONFIG_PROBE = "rfc7951:/Cisco-IOS-XE-native:native"

PASS, FAIL, WARN, SKIP = "PASS", "FAIL", "WARN", "SKIP"


def _mark(ok: Optional[bool]) -> str:
    return {True: PASS, False: FAIL, None: WARN}[ok]


def tcp_probe(host: str, port: int, timeout: float = 6.0, tries: int = 3) -> dict:
    """Raw TCP connect timing (proxy-agnostic). Returns min/avg ms + ok."""
    lat = []
    err = None
    for _ in range(tries):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        t0 = time.monotonic()
        try:
            s.connect((host, port))
            lat.append((time.monotonic() - t0) * 1000)
        except OSError as e:
            err = f"{type(e).__name__}: {e}"
        finally:
            s.close()
    if lat:
        return {"ok": True, "min_ms": round(min(lat), 1), "avg_ms": round(sum(lat) / len(lat), 1)}
    return {"ok": False, "error": err}


def _device_session() -> requests.Session:
    s = requests.Session()
    s.trust_env = False  # ignore corp proxy env for direct device reach
    return s


def restconf_probe(host: str, port: int, auth: tuple[str, str]) -> dict:
    sess = _device_session()
    try:
        oper = restconf_get(host, port, RESTCONF_OPER_PROBE, auth, timeout=20, session=sess, retries=1)
        cfg = restconf_get(host, port, RESTCONF_CONFIG_PROBE, auth, timeout=20, session=sess, retries=1)
    finally:
        sess.close()
    version = None
    if cfg.is_json and isinstance(cfg.body, dict):
        version = cfg.body.get("Cisco-IOS-XE-native:version")
    return {
        "ok": bool(oper.ok and cfg.ok),
        "oper_status": oper.http_status,
        "config_status": cfg.http_status,
        "oper_ms": oper.elapsed_ms,
        "version": version,
        "error": oper.error or cfg.error,
    }


def gnmi_probe(host: str, auth: tuple[str, str]) -> dict:
    try:
        from pygnmi.client import gNMIclient
    except Exception as e:  # noqa: BLE001
        return {"ok": None, "error": f"pygnmi unavailable: {e}"}
    try:
        with gNMIclient(target=(host, 9339), username=auth[0], password=auth[1],
                        insecure=False, skip_verify=True, timeout=20) as gc:
            caps = gc.capabilities()
            got = gc.get(path=[GNMI_OPER_PROBE], datatype="state", encoding="json_ietf")
            has = bool(got and got.get("notification"))
            ver = caps.get("gNMI_version") if isinstance(caps, dict) else None
            return {"ok": bool(has), "gnmi_version": ver, "oper_data": has}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e).split("Error:")[-1][:100].strip()}


def netconf_probe(host: str, auth: tuple[str, str]) -> dict:
    try:
        from ncclient import manager
    except Exception as e:  # noqa: BLE001
        return {"ok": None, "error": f"ncclient unavailable: {e}"}
    try:
        with manager.connect(host=host, port=830, username=auth[0], password=auth[1],
                             hostkey_verify=False, look_for_keys=False, allow_agent=False,
                             timeout=20) as m:
            caps = list(m.server_capabilities)
            yp = any("yang-push" in c or "notification" in c for c in caps)
            return {"ok": True, "capabilities": len(caps), "yang_push": yp}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e).split("\n")[0][:100]}


def stack_probe(host: str, auth: tuple[str, str]) -> dict:
    """`show switch` over SSH -> stack member count + states (read-only)."""
    try:
        from netmiko import ConnectHandler
    except Exception as e:  # noqa: BLE001
        return {"ok": None, "error": f"netmiko unavailable: {e}"}
    try:
        conn = ConnectHandler(device_type="cisco_xe", host=host, username=auth[0],
                              password=auth[1], fast_cli=False, conn_timeout=20)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e).split("\n")[0][:100]}
    try:
        out = conn.send_command("show switch", read_timeout=30)
    finally:
        conn.disconnect()
    members, ready = [], 0
    for line in out.splitlines():
        parts = line.split()
        if parts and parts[0].strip("*").isdigit():
            members.append(parts[0].strip("*"))
            if "Ready" in line:
                ready += 1
    return {"ok": len(members) > 0, "members": len(members), "ready": ready, "raw_lines": out.count("\n")}


def dialout_probe() -> dict:
    """Report MDT dial-out return-path readiness (cannot fully test read-only)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("0.0.0.0", DIALOUT_PORT))
        free = True
    except OSError:
        free = False
    finally:
        s.close()
    return {"ok": None, "port_free_on_collector": free,
            "note": "device->collector:57500 dial-back requires a subscription config (write); deferred"}


def probe_device(dev: "inv.Device", auth: tuple[str, str]) -> dict:
    print(f"\n== {dev.name} ({dev.pid}) {dev.host} ==")
    results: dict = {}

    for label, port in PORTS.items():
        r = tcp_probe(dev.host, port)
        results[label] = r
        detail = f"min={r['min_ms']}ms avg={r['avg_ms']}ms" if r["ok"] else r.get("error", "")
        print(f"  [{_mark(r['ok'])}] tcp {label:14} {detail}")

    rc = restconf_probe(dev.host, dev.port, auth)
    results["restconf"] = rc
    print(f"  [{_mark(rc['ok'])}] RESTCONF   oper={rc['oper_status']} config={rc['config_status']} "
          f"rtt={rc['oper_ms']}ms ver={rc.get('version')}" + (f" err={rc['error']}" if rc.get("error") else ""))

    gn = gnmi_probe(dev.host, auth)
    results["gnmi"] = gn
    print(f"  [{_mark(gn['ok'])}] gNMI       " +
          (f"ver={gn.get('gnmi_version')} oper_data={gn.get('oper_data')}" if gn.get("ok") else gn.get("error", "")))

    nc = netconf_probe(dev.host, auth)
    results["netconf"] = nc
    print(f"  [{_mark(nc['ok'])}] NETCONF    " +
          (f"caps={nc.get('capabilities')} yang_push={nc.get('yang_push')}" if nc.get("ok") else nc.get("error", "")))

    st = stack_probe(dev.host, auth)
    results["stack"] = st
    print(f"  [{_mark(st['ok'])}] STACK      " +
          (f"members={st.get('members')} ready={st.get('ready')}" if st.get("ok") else st.get("error", "")))

    do = dialout_probe()
    results["dialout"] = do
    print(f"  [{_mark(do['ok'])}] MDT :57500 port_free={do['port_free_on_collector']} ({do['note']})")

    # Overall verdict: the forward-direction planes must pass; dial-out is informational.
    hard = [results["restconf"]["ok"], gn.get("ok"), nc.get("ok")]
    results["ready"] = all(x for x in hard if x is not None) and results["restconf"]["ok"]
    print(f"  => {'READY' if results['ready'] else 'NOT READY'} (forward planes)")
    return results


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--device", action="append", dest="devices", help="Device name(s) from inventory (repeatable)")
    ap.add_argument("--all", action="store_true", help="Probe every device in inventory")
    ap.add_argument("--inventory", help="Path to inventory.json")
    args = ap.parse_args(argv)

    try:
        devices = inv.load_inventory(args.inventory)
        auth = inv.load_credentials()
    except (inv.InventoryError, inv.CredentialError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if not args.all:
        if not args.devices:
            ap.error("specify --device NAME (repeatable) or --all")
        wanted = set(args.devices)
        devices = [d for d in devices if d.name in wanted]
        if not devices:
            print(f"ERROR: no inventory devices match {sorted(wanted)}", file=sys.stderr)
            return 2

    all_ready = True
    for dev in devices:
        res = probe_device(dev, auth)
        all_ready = all_ready and res["ready"]
    print(f"\n{'ALL READY' if all_ready else 'SOME NOT READY'}")
    return 0 if all_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
