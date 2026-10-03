"""Gated CRUD/write path for the Track B harness (Phase 5, §7).

This is the ONLY module allowed to send non-GET RESTCONF methods, and it is
deliberately kept apart from ``request.py`` (whose GET-only guard is never
relaxed). Every write goes through the safety workflow:

    backup  -> dry-run (default) -> apply -> verify -> rollback

  * backup:   GET the target container(s) + the full running config to a local,
              gitignored backup dir BEFORE anything is changed.
  * dry-run:  the default. Prints the exact method + URL + payload and touches
              nothing. A real change requires the explicit ``--apply`` flag.
  * apply:    send the PATCH/PUT/POST/DELETE, then re-GET to confirm.
  * verify:   GET the container back (+ use-case specific liveness checks).
  * rollback: ``--rollback <backup.json>`` restores the saved container via PUT.

Only ever run against a device whose inventory ``writable`` flag is true.

First use case: ``gnmi-enable`` — bring up the secure gNMI server (port 9339)
by mirroring a known-good fleet config, using the device's own self-signed
trustpoint.

Run (activate venv; creds via env, never logged):
  python -X utf8 -m scripts.harness.crud --device C9300-STACK8-WAN --use-case gnmi-enable            # dry-run
  python -X utf8 -m scripts.harness.crud --device C9300-STACK8-WAN --use-case gnmi-enable --apply
  python -X utf8 -m scripts.harness.crud --device C9300-STACK8-WAN --rollback <backup.json>
"""
from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import requests

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.harness import inventory as inv
    from scripts.harness.request import (
        RESTCONF_HEADERS,
        build_restconf_url,
        restconf_get,
    )
else:  # pragma: no cover
    from . import inventory as inv
    from .request import RESTCONF_HEADERS, build_restconf_url, restconf_get

HARNESS_DIR = Path(__file__).resolve().parent
BACKUPS_DIR = HARNESS_DIR / "captures"  # gitignored; per-device subdir below

_WRITE_METHODS = {"PATCH", "PUT", "POST", "DELETE"}

# gNMI secure server (mirrors a known-good C9K fleet config).
GNMI_CONFIG_PATH = "/data/Cisco-IOS-XE-gnmi-cfg:gnmi-cfg-data/config"
NATIVE_ROOT_PATH = "/data/Cisco-IOS-XE-native:native"
# Trustpoints: prefer the operational model (it reports the auto-generated
# self-signed trustpoint created by ``ip http secure-server``, which does NOT
# appear in native running-config). Native config is a fallback for devices
# that carry an explicitly-configured trustpoint.
TRUSTPOINT_OPER_PATH = "/data/Cisco-IOS-XE-crypto-pki-oper:crypto-pki-oper-data"
TRUSTPOINT_PATH = "/data/Cisco-IOS-XE-native:native/crypto/pki/trustpoint"

# Model-Driven Telemetry (gRPC dial-out). The device dials OUT to a collector,
# so the collector must be reachable FROM the device (here: over the WAN).
MDT_CONFIG_PATH = "/data/Cisco-IOS-XE-mdt-cfg:mdt-config-data"
MDT_OPER_SUBS_PATH = "/data/Cisco-IOS-XE-mdt-oper:mdt-oper-data/mdt-subscriptions"
MDT_OPER_CONNS_PATH = "/data/Cisco-IOS-XE-mdt-oper:mdt-oper-data/mdt-connections"
# Default dial-out receiver = our VM's telegraf cisco_telemetry_mdt input (plain
# gRPC, no TLS). Override with --receiver-ip/--receiver-port to aim elsewhere.
MDT_RECEIVER_IP = "10.85.134.200"
MDT_RECEIVER_PORT = 57500
# Dial-out must egress an interface/VRF that can ROUTE BACK to the receiver. On
# these C9300s the mgmt IP is on GigabitEthernet0/0 in Mgmt-vrf (the only path
# with a default route to the collector); the global table has no such route, so
# a subscription without source-vrf silently sources from a global loopback and
# never connects. Override/disable with --source-vrf.
MDT_SOURCE_VRF = "Mgmt-vrf"
# Minimal always-present validation subscriptions (kvGPB periodic dial-out).
# ``period`` is in centiseconds (100 = 1s). Distinct IDs avoid colliding with
# any pre-existing subscriptions on the shared collector.
MDT_TEST_SUBS = [
    {"id": 98001, "name": "cpu",
     "xpath": "/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization", "period": 1000},
    {"id": 98002, "name": "interfaces",
     "xpath": "/interfaces-ios-xe-oper:interfaces/interface", "period": 3000},
]


@dataclass
class WriteResult:
    ok: bool
    http_status: Optional[int]
    body: Any
    error: Optional[str]
    elapsed_ms: int
    url: str
    method: str


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _device_session() -> requests.Session:
    s = requests.Session()
    s.trust_env = False  # bypass corp proxy for direct (incl. WAN) device reach
    return s


def restconf_write(
    method: str,
    host: str,
    port: int,
    openapi_path: str,
    payload: Optional[dict],
    auth: tuple[str, str],
    session: requests.Session,
    timeout: int = 30,
) -> WriteResult:
    """Send a single non-GET RESTCONF request. Explicitly a write path."""
    m = method.strip().upper()
    if m not in _WRITE_METHODS:
        raise ValueError(f"restconf_write only sends {_WRITE_METHODS}, got {method!r}")
    url = build_restconf_url(host, port, openapi_path)
    data = json.dumps(payload) if payload is not None else None
    start = time.monotonic()
    try:
        resp = session.request(
            m, url, headers=RESTCONF_HEADERS, auth=auth, verify=False,
            timeout=timeout, data=data,
        )
        elapsed = int((time.monotonic() - start) * 1000)
        text = resp.text or ""
        body: Any = None
        if text.strip():
            try:
                body = resp.json()
            except ValueError:
                body = text
        return WriteResult(
            ok=200 <= resp.status_code < 300,
            http_status=resp.status_code, body=body, error=None,
            elapsed_ms=elapsed, url=url, method=m,
        )
    except requests.RequestException as exc:
        return WriteResult(
            ok=False, http_status=None, body=None,
            error=f"{type(exc).__name__}: {exc}",
            elapsed_ms=int((time.monotonic() - start) * 1000), url=url, method=m,
        )


def _backup_dir(device_name: str) -> Path:
    d = BACKUPS_DIR / device_name / "crud-backups" / _ts()
    d.mkdir(parents=True, exist_ok=True)
    return d


def _get_json(dev: "inv.Device", path: str, auth, session) -> "object":
    return restconf_get(dev.host, dev.port, path, auth, timeout=30, session=session, retries=1)


def backup_targets(dev: "inv.Device", auth, session, paths: list[str]) -> Path:
    """GET each path (+ full native running config) and save to a backup dir."""
    bdir = _backup_dir(dev.name)
    meta = {"device": dev.name, "host": dev.host, "at": _now(), "paths": {}}
    for p in paths + [NATIVE_ROOT_PATH]:
        r = _get_json(dev, p, auth, session)
        safe = p.strip("/").replace("/", "__").replace(":", "_")
        (bdir / f"{safe}.json").write_text(
            json.dumps({"path": p, "http_status": r.http_status,
                        "body": r.body if r.is_json else None,
                        "error": r.error}, indent=2), encoding="utf-8")
        meta["paths"][p] = {"http_status": r.http_status, "error": r.error}
    (bdir / "_manifest.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return bdir


def detect_self_signed_trustpoint(dev: "inv.Device", auth, session) -> Optional[str]:
    """Return the device's self-signed trustpoint name (TP-self-signed-*), if any.

    Primary source is the crypto-pki operational model, which reports the
    auto-generated self-signed trustpoint used for HTTPS/RESTCONF even when it
    is absent from native running-config. Falls back to native config.
    """
    # 1) operational model: crypto-pki-bundle[].label
    r = _get_json(dev, TRUSTPOINT_OPER_PATH, auth, session)
    if r.is_json and isinstance(r.body, dict):
        data = r.body.get("Cisco-IOS-XE-crypto-pki-oper:crypto-pki-oper-data") or {}
        bundle = data.get("crypto-pki-bundle") or []
        if isinstance(bundle, dict):
            bundle = [bundle]
        labels = [b.get("label") for b in bundle if isinstance(b, dict) and b.get("label")]
        for lbl in labels:
            if str(lbl).startswith("TP-self-signed-"):
                return lbl
        if labels:
            return labels[0]
    # 2) fallback: explicitly-configured trustpoint in native config
    r = _get_json(dev, TRUSTPOINT_PATH, auth, session)
    if not r.is_json or not isinstance(r.body, dict):
        return None
    tps = r.body.get("Cisco-IOS-XE-native:trustpoint") or r.body.get("trustpoint") or []
    if isinstance(tps, dict):
        tps = [tps]
    names = [t.get("id") for t in tps if isinstance(t, dict) and t.get("id")]
    for n in names:
        if str(n).startswith("TP-self-signed-"):
            return n
    return names[0] if names else None


def tcp_open(host: str, port: int, timeout: float = 6.0, retries: int = 1, delay: float = 3.0) -> bool:
    """True if a TCP connect succeeds. Optionally retry (a freshly-enabled
    server can take several seconds to bind its listening socket)."""
    for attempt in range(max(1, retries)):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except OSError:
            pass
        finally:
            s.close()
        if attempt < retries - 1:
            time.sleep(delay)
    return False


def gnmi_capabilities(host: str, port: int, auth: tuple[str, str]) -> dict:
    """Best-effort functional gNMI probe (Capabilities RPC over TLS).

    Returns {"ok": True, "models": N} on success, {"ok": False, "detail": ...}
    on a gNMI/gRPC error, or {"ok": None, ...} when pygnmi is unavailable. Never
    raises and never logs credentials.
    """
    try:
        from pygnmi.client import gNMIclient
    except Exception:
        return {"ok": None, "detail": "pygnmi not installed"}
    try:
        # enable_http_proxy=0 stops gRPC from routing to a lab device via the
        # corp HTTP proxy (RESTCONF bypasses it with trust_env=False; gRPC needs
        # this channel option instead).
        with gNMIclient(target=(host, port), username=auth[0], password=auth[1],
                        insecure=False, skip_verify=True,
                        grpc_options=[("grpc.enable_http_proxy", 0)]) as c:
            caps = c.capabilities()
        return {"ok": True, "models": len(caps.get("supported_models", []) or [])}
    except Exception as exc:  # noqa: BLE001 - best-effort probe
        return {"ok": False, "detail": str(exc)[-90:]}


# ---- use case: enable secure gNMI --------------------------------------------

def plan_gnmi_enable(dev: "inv.Device", auth, session) -> tuple[str, str, dict, list[str]]:
    """Return (method, path, payload, backup_paths) for enabling secure gNMI.

    RESTCONF ``PATCH`` only merges into an existing resource; if the gNMI config
    container is absent (fresh device -> HTTP 404) it must be *created* with
    ``PUT``. When the container already exists we ``PATCH`` to merge our keys
    without clobbering any other config the device carries.
    """
    tsname = detect_self_signed_trustpoint(dev, auth, session)
    config = {
        "enable": True,
        "secure-enable": True,
        "service": True,
        "secure-password-auth": True,
    }
    if tsname:
        config["secure-tsname"] = tsname
    payload = {"Cisco-IOS-XE-gnmi-cfg:config": config}
    existing = _get_json(dev, GNMI_CONFIG_PATH, auth, session)
    method = "PATCH" if existing.http_status == 200 else "PUT"
    return method, GNMI_CONFIG_PATH, payload, [GNMI_CONFIG_PATH]


def verify_gnmi(dev: "inv.Device", auth, session, probe_rpc: bool = False) -> dict:
    r = _get_json(dev, GNMI_CONFIG_PATH, auth, session)
    cfg = {}
    if r.is_json and isinstance(r.body, dict):
        cfg = r.body.get("Cisco-IOS-XE-gnmi-cfg:config", {})
    port_open = tcp_open(dev.host, 9339, retries=6, delay=5.0) if probe_rpc else tcp_open(dev.host, 9339)
    out = {
        "config_status": r.http_status,
        "enable": cfg.get("enable"),
        "secure_enable": cfg.get("secure-enable"),
        "secure_tsname": cfg.get("secure-tsname"),
        "tcp_9339_open": port_open,
    }
    if probe_rpc and port_open:
        out["gnmi_rpc"] = gnmi_capabilities(dev.host, 9339, auth)
    return out


def _gnmi_state_field(detail_text: str) -> Optional[str]:
    """Parse the top-level gNMI `State:` value from `show gnmi-yang state detail`."""
    m = re.search(r"^\s*State:\s*(\S+)", detail_text or "", re.M)
    return m.group(1) if m else None


def provision_gnxi_self_signed(dev: "inv.Device", auth) -> dict:
    """Apply the CLI-only knob secure gNMI needs when using a SELF-SIGNED
    trustpoint: `gnxi secure-allow-self-signed-trustpoint` (under `service
    internal`). The RESTCONF gnmi-cfg model does not expose this leaf, so without
    it IOS-XE leaves the gNXI server in State: Default and every RPC returns
    "Device has not been provisioned". Idempotent: no-op once State: Provisioned.
    """
    try:
        from netmiko import ConnectHandler
    except Exception:
        return {"ok": None, "detail": "netmiko not installed"}
    try:
        conn = ConnectHandler(device_type="cisco_xe", host=dev.host,
                              username=auth[0], password=auth[1], fast_cli=False,
                              conn_timeout=30, banner_timeout=30, auth_timeout=30)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "detail": f"ssh: {str(exc)[-80:]}"}
    try:
        before = _gnmi_state_field(conn.send_command("show gnmi-yang state detail", read_timeout=60))
        if before == "Provisioned":
            return {"ok": True, "state": before, "changed": False}
        conn.send_config_set(["service internal", "gnxi secure-allow-self-signed-trustpoint"])
        time.sleep(3)  # server regenerates/rebinds the secure listener
        after = _gnmi_state_field(conn.send_command("show gnmi-yang state detail", read_timeout=60))
        return {"ok": after == "Provisioned", "state": after, "changed": True}
    finally:
        conn.disconnect()


# ---- use case: enable gRPC MDT dial-out --------------------------------------

def _netmiko_connect(dev: "inv.Device", auth):
    """Open a netmiko SSH session (raises on failure). Caller disconnects."""
    from netmiko import ConnectHandler
    return ConnectHandler(device_type="cisco_xe", host=dev.host,
                          username=auth[0], password=auth[1], fast_cli=False,
                          conn_timeout=30, banner_timeout=30, auth_timeout=30)


def build_mdt_cli(receiver_ip: str, receiver_port: int, subs: list[dict],
                  source_vrf: Optional[str] = None,
                  source_address: Optional[str] = None) -> tuple[list[str], list[str]]:
    """Return (add_lines, remove_lines) for kvGPB periodic gRPC dial-out subs.

    Mirrors the validated ``telemetry ietf subscription`` CLI form (the RESTCONF
    ``mdt-receivers`` leaf is deprecated on this release, so the write is driven
    over SSH). ``source_vrf``/``source_address`` pin the egress to a path that can
    route back to the receiver. ``remove_lines`` deletes exactly what was added.
    """
    add: list[str] = []
    remove: list[str] = []
    for s in subs:
        lines = [
            f"telemetry ietf subscription {s['id']}",
            " encoding encode-kvgpb",
            " stream yang-push",
        ]
        if source_vrf:
            lines.append(f" source-vrf {source_vrf}")
        if source_address:
            lines.append(f" source-address {source_address}")
        lines += [
            f" update-policy periodic {s['period']}",
            f" filter xpath {s['xpath']}",
            f" receiver ip address {receiver_ip} {receiver_port} protocol grpc-tcp",
        ]
        add += lines
        remove.append(f"no telemetry ietf subscription {s['id']}")
    return add, remove


def cli_send_config(dev: "inv.Device", auth, lines: list[str]) -> str:
    conn = _netmiko_connect(dev, auth)
    try:
        return conn.send_config_set(lines, read_timeout=90)
    finally:
        conn.disconnect()


def cli_show(dev: "inv.Device", auth, cmds: list[str]) -> dict:
    conn = _netmiko_connect(dev, auth)
    try:
        return {c: conn.send_command(c, read_timeout=60) for c in cmds}
    finally:
        conn.disconnect()


def _receiver_connected(state: object) -> bool:
    s = str(state or "")
    return s == "connected" or s.endswith("-connected")


def _connection_active(state: object) -> bool:
    s = str(state or "")
    return s == "active" or s.endswith("-active")


def verify_mdt(dev: "inv.Device", auth, session, sub_ids: list[int],
               receiver_ip: str, receiver_port: int,
               retries: int = 1, delay: float = 5.0) -> dict:
    """Poll the MDT oper model for our subscriptions and the dial-out connection.

    The ``receiver ip address`` config form reports liveness via the
    ``mdt-connections`` list (``con-state-active`` once the device has an
    established TCP session to the collector); the deprecated ``mdt-receivers``
    list stays empty. Either signal counts as connected.
    """
    wanted = {int(x) for x in sub_ids}
    out: dict = {"connected": False, "subs": {}, "connection": None}
    for attempt in range(max(1, retries)):
        r = _get_json(dev, MDT_OPER_SUBS_PATH, auth, session)
        found: dict = {}
        if r.is_json and isinstance(r.body, dict):
            subs = r.body.get("Cisco-IOS-XE-mdt-oper:mdt-subscriptions") or []
            if isinstance(subs, dict):
                subs = [subs]
            for sub in subs:
                try:
                    sid = int(sub.get("subscription-id"))
                except (TypeError, ValueError):
                    continue
                if sid not in wanted:
                    continue
                recvs = sub.get("mdt-receivers") or []
                if isinstance(recvs, dict):
                    recvs = [recvs]
                found[sid] = {
                    "sub_state": sub.get("state"),
                    "receivers": [{"address": rc.get("address"), "port": rc.get("port"),
                                   "state": rc.get("state")} for rc in recvs],
                }
        out["subs"] = found

        conn = None
        rc = _get_json(dev, MDT_OPER_CONNS_PATH, auth, session)
        if rc.is_json and isinstance(rc.body, dict):
            conns = rc.body.get("Cisco-IOS-XE-mdt-oper:mdt-connections") or []
            if isinstance(conns, dict):
                conns = [conns]
            for c in conns:
                if str(c.get("address")) == str(receiver_ip) and int(c.get("port") or 0) == int(receiver_port):
                    conn = {"state": c.get("state"), "source-address": c.get("source-address"),
                            "transport": c.get("transport")}
                    break
        out["connection"] = conn

        recv_ok = any(_receiver_connected(rc2["state"]) for v in found.values() for rc2 in v["receivers"])
        conn_ok = bool(conn) and _connection_active(conn.get("state"))
        out["connected"] = recv_ok or conn_ok
        if out["connected"]:
            break
        if attempt < retries - 1:
            time.sleep(delay)
    return out


def run_mdt_enable(dev, auth, apply: bool, receiver_ip: str, receiver_port: int,
                   source_vrf: Optional[str] = None,
                   source_address: Optional[str] = None) -> int:
    subs = MDT_TEST_SUBS
    sub_ids = [s["id"] for s in subs]
    if source_vrf and source_address is None:
        source_address = dev.host  # pin to the mgmt IP on that VRF
    add_lines, remove_lines = build_mdt_cli(receiver_ip, receiver_port, subs,
                                            source_vrf, source_address)
    session = _device_session()
    try:
        via = f" via vrf {source_vrf}" if source_vrf else ""
        print(f"== CRUD use-case 'mdt-enable' on {dev.name} ({dev.host}) "
              f"-> receiver {receiver_ip}:{receiver_port} grpc-tcp{via} ==")

        print("\n-- BACKUP (pre-change) --")
        bdir = _backup_dir(dev.name)
        for p in (MDT_CONFIG_PATH, MDT_OPER_SUBS_PATH):
            r = _get_json(dev, p, auth, session)
            safe = p.strip("/").replace("/", "__").replace(":", "_")
            (bdir / f"{safe}.json").write_text(json.dumps(
                {"path": p, "http_status": r.http_status,
                 "body": r.body if r.is_json else None, "error": r.error}, indent=2),
                encoding="utf-8")
        try:
            shows = cli_show(dev, auth, ["show running-config | section telemetry"])
            (bdir / "show-run-telemetry.txt").write_text(
                shows.get("show running-config | section telemetry", ""), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001 - backup is best-effort
            print(f"  (warning: could not capture show-run telemetry: {str(exc)[-80:]})")
        rollback_file = bdir / "rollback.cli"
        rollback_file.write_text("\n".join(remove_lines) + "\n", encoding="utf-8")
        print(f"  saved: {bdir}")

        print("\n-- BEFORE --")
        print("  " + json.dumps(verify_mdt(dev, auth, session, sub_ids, receiver_ip, receiver_port, retries=1)))

        print("\n-- PLANNED CHANGE (CLI over SSH) --")
        for ln in add_lines:
            print("    " + ln)
        print(f"  rollback: --rollback {rollback_file}")

        if not apply:
            print("\nDRY-RUN: nothing was sent. Re-run with --apply to configure the subscriptions.")
            return 0

        print("\n-- APPLY --")
        out = cli_send_config(dev, auth, add_lines)
        tail = "\n".join(out.splitlines()[-6:])
        print("  " + tail.replace("\n", "\n  "))

        print("\n-- VERIFY (polling mdt-oper for receiver connection) --")
        after = verify_mdt(dev, auth, session, sub_ids, receiver_ip, receiver_port, retries=8, delay=5.0)
        print("  " + json.dumps(after))
        if after.get("connected"):
            status = ("SUCCESS: dial-out receiver CONNECTED over the WAN "
                      f"({receiver_ip}:{receiver_port}). Subscriptions streaming.")
        else:
            status = ("APPLIED but receiver not yet connected — the device cannot "
                      f"reach {receiver_ip}:{receiver_port} (WAN return path / firewall) "
                      "or is still connecting. Check `show telemetry ietf subscription "
                      "<id> receiver` on the device.")
        print(f"\n{status}")
        print(f"(not saved to startup — transient validation. rollback: --rollback {rollback_file})")
        return 0 if after.get("connected") else 1
    finally:
        session.close()


USE_CASES = {
    "gnmi-enable": {"plan": plan_gnmi_enable, "verify": verify_gnmi,
                    "post_apply": provision_gnxi_self_signed},
}
# Use cases whose apply step is CLI-driven (not RESTCONF) and have a dedicated runner.
CLI_USE_CASES = {"mdt-enable"}


def _print_plan(method, path, payload, dev):
    url = build_restconf_url(dev.host, dev.port, path)
    print("\n-- PLANNED CHANGE --")
    print(f"  method : {method}")
    print(f"  url    : {url}")
    print("  payload:")
    print("    " + json.dumps(payload, indent=2).replace("\n", "\n    "))


def run_use_case(dev, auth, name, apply: bool) -> int:
    uc = USE_CASES[name]
    session = _device_session()
    try:
        print(f"== CRUD use-case '{name}' on {dev.name} ({dev.host}) ==")
        method, path, payload, backup_paths = uc["plan"](dev, auth, session)

        print("\n-- BACKUP (pre-change) --")
        bdir = backup_targets(dev, auth, session, backup_paths)
        print(f"  saved: {bdir}")

        print("\n-- BEFORE --")
        print("  " + json.dumps(uc["verify"](dev, auth, session)))

        _print_plan(method, path, payload, dev)

        if not apply:
            print("\nDRY-RUN: nothing was sent. Re-run with --apply to make the change.")
            return 0

        print("\n-- APPLY --")
        wr = restconf_write(method, dev.host, dev.port, path, payload, auth, session)
        print(f"  {wr.method} -> HTTP {wr.http_status} ({wr.elapsed_ms} ms)"
              + (f" ERROR {wr.error}" if wr.error else ""))
        if not wr.ok:
            print("  APPLY FAILED — device unchanged (or partially). "
                  f"Rollback with: --rollback {bdir / (backup_paths[0].strip('/').replace('/', '__').replace(':', '_') + '.json')}")
            return 1

        if uc.get("post_apply"):
            print("\n-- POST-APPLY PROVISION (CLI-only step) --")
            print("  " + json.dumps(uc["post_apply"](dev, auth)))

        time.sleep(2)  # brief initial settle; verify_gnmi then polls the socket
        print("\n-- AFTER --")
        after = uc["verify"](dev, auth, session, probe_rpc=True)
        print("  " + json.dumps(after))
        applied = bool(after.get("enable")) and bool(after.get("secure_enable")) \
            and bool(after.get("tcp_9339_open"))
        rpc = after.get("gnmi_rpc") or {}
        if applied and rpc.get("ok") is True:
            status = "SUCCESS (config applied + gNMI RPC functional)"
        elif applied:
            status = ("SUCCESS: config applied and secure listener up. "
                      f"gNMI RPC not yet functional ({rpc.get('detail', 'n/a')})")
        else:
            status = "APPLIED but verification incomplete"
        print(f"\n{status} (backup at {bdir})")
        return 0 if applied else 1
    finally:
        session.close()


def run_rollback(dev, auth, backup_file: Path) -> int:
    if backup_file.suffix == ".cli":
        lines = [ln for ln in backup_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
        print(f"== ROLLBACK {dev.name}: send {len(lines)} CLI line(s) from {backup_file.name} ==")
        for ln in lines:
            print("    " + ln)
        try:
            out = cli_send_config(dev, auth, lines)
        except Exception as exc:  # noqa: BLE001
            print(f"  ROLLBACK FAILED (ssh): {str(exc)[-100:]}", file=sys.stderr)
            return 1
        print("  " + "\n  ".join(out.splitlines()[-6:]))
        return 0
    data = json.loads(backup_file.read_text(encoding="utf-8"))
    path = data.get("path")
    body = data.get("body")
    if not path:
        print(f"ERROR: backup file has no 'path': {backup_file}", file=sys.stderr)
        return 2
    session = _device_session()
    try:
        print(f"== ROLLBACK {dev.name}: restore {path} (was HTTP {data.get('http_status')}) ==")
        if body is None:
            print("  original was absent/empty — sending DELETE to remove the added config.")
            wr = restconf_write("DELETE", dev.host, dev.port, path, None, auth, session)
        else:
            wr = restconf_write("PUT", dev.host, dev.port, path, body, auth, session)
        print(f"  {wr.method} -> HTTP {wr.http_status}" + (f" ERROR {wr.error}" if wr.error else ""))
        return 0 if wr.ok else 1
    finally:
        session.close()


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--device", required=True, help="Device name from inventory (must be writable)")
    ap.add_argument("--use-case", choices=sorted(set(USE_CASES) | CLI_USE_CASES), help="Write use case to run")
    ap.add_argument("--apply", action="store_true", help="Actually send the change (default: dry-run)")
    ap.add_argument("--rollback", metavar="BACKUP_FILE", help="Restore from a backup (.json container or .cli script)")
    ap.add_argument("--receiver-ip", help=f"MDT dial-out receiver IP (default {MDT_RECEIVER_IP})")
    ap.add_argument("--receiver-port", type=int, help=f"MDT dial-out receiver port (default {MDT_RECEIVER_PORT})")
    ap.add_argument("--source-vrf", default=MDT_SOURCE_VRF,
                    help=f"MDT dial-out source VRF (default {MDT_SOURCE_VRF!r}; pass '' for global table)")
    ap.add_argument("--source-address", help="MDT dial-out source IP (default: device mgmt host when a VRF is set)")
    ap.add_argument("--inventory", help="Path to inventory.json")
    ap.add_argument("--force-writable", action="store_true", help="Override the inventory writable=false guard")
    args = ap.parse_args(argv)

    try:
        devices = inv.load_inventory(args.inventory)
        auth = inv.load_credentials()
    except (inv.InventoryError, inv.CredentialError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    dev = next((d for d in devices if d.name == args.device), None)
    if dev is None:
        print(f"ERROR: device {args.device!r} not in inventory", file=sys.stderr)
        return 2

    if not getattr(dev, "writable", False) and not args.force_writable:
        print(f"REFUSED: device {dev.name!r} is not marked writable in inventory. "
              "Set writable=true (or pass --force-writable) to allow config changes.",
              file=sys.stderr)
        return 3

    if args.rollback:
        return run_rollback(dev, auth, Path(args.rollback))
    if not args.use_case:
        ap.error("specify --use-case or --rollback")
    if args.use_case == "mdt-enable":
        return run_mdt_enable(dev, auth, apply=args.apply,
                              receiver_ip=args.receiver_ip or MDT_RECEIVER_IP,
                              receiver_port=args.receiver_port or MDT_RECEIVER_PORT,
                              source_vrf=(args.source_vrf or None),
                              source_address=args.source_address)
    return run_use_case(dev, auth, args.use_case, apply=args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
