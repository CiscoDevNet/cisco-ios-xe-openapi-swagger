#!/usr/bin/env python3
"""enable_secure_gnmi.py — enable secure gNMI (TLS, port 9339) via SSH CLI.

IOS XE 26.1 configures gNMI through the `gnxi` command family. Reference config
(from C9300, which already serves secure gNMI on 9339):

    gnxi secure-allow-self-signed-trustpoint
    gnxi secure-password-auth
    gnxi secure-trustpoint <device self-signed trustpoint>
    gnxi secure-server

RESTCONF/NETCONF writes to Cisco-IOS-XE-gnmi-cfg are NACM access-denied for our
account, so this uses the CLI. Idempotent: skips devices already serving secure
gNMI. Read-only unless --apply is given.

    python enable_secure_gnmi.py --all              # dry-run (show plan)
    python enable_secure_gnmi.py --all --apply      # configure + verify
"""
from __future__ import annotations

import argparse
import re
import socket

from collect_fleet import load_env, load_devices
from netmiko import ConnectHandler

SECURE_PORT = 9339


def _tcp_open(host: str, port: int, timeout: float = 4.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _self_signed_tp(conn) -> str | None:
    out = conn.send_command("show running-config | include crypto pki trustpoint TP-self-signed")
    m = re.search(r"(TP-self-signed-\d+)", out or "")
    return m.group(1) if m else None


def _secure_up(conn) -> bool:
    state = conn.send_command("show gnxi state detail")
    return "State: Provisioned" in (state or "")


def process(dev, env, apply: bool) -> dict:
    host, pid = dev["host"], dev["pid"]
    conn = ConnectHandler(device_type="cisco_ios", host=host, username=env["IOSXE_USER"],
                          password=env["IOSXE_PASS"], fast_cli=False, conn_timeout=20)
    try:
        if _secure_up(conn) and _tcp_open(host, SECURE_PORT):
            return {"pid": pid, "result": "already-secure"}
        tp = _self_signed_tp(conn)
        if not tp:
            return {"pid": pid, "result": "no-self-signed-trustpoint"}
        cmds = [
            # `service internal` unlocks secure-allow-self-signed-trustpoint; without
            # it the allow command is silently dropped and the server stays "Default".
            "service internal",
            "gnxi secure-allow-self-signed-trustpoint",
            "gnxi secure-password-auth",
            f"gnxi secure-trustpoint {tp}",
            "gnxi secure-server",
        ]
        if not apply:
            return {"pid": pid, "result": "would-configure", "tp": tp, "cmds": cmds}
        conn.send_config_set(cmds)
        # the gNMI service bounces on secure-server enable; give the listener time to bind
        ok = False
        for _ in range(10):
            if _tcp_open(host, SECURE_PORT):
                ok = True
                break
            socket_wait(3)
        return {"pid": pid, "result": "configured" if ok and _secure_up(conn) else "configured-not-up",
                "tp": tp}
    finally:
        conn.disconnect()


def socket_wait(seconds: float) -> None:
    import time
    time.sleep(seconds)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true", help="Actually configure (default is dry-run).")
    args = ap.parse_args()
    env = load_env()
    devices = load_devices([args.device] if args.device else None)
    for dev in devices:
        try:
            r = process(dev, env, args.apply)
        except Exception as e:  # noqa: BLE001
            r = {"pid": dev["pid"], "result": "error", "error": str(e)[:150]}
        line = f"  {r['pid']:12} {r['result']}"
        if r.get("tp"):
            line += f"  tp={r['tp']}"
        if r.get("error"):
            line += f"  ! {r['error']}"
        print(line, flush=True)
        if r.get("cmds"):
            for c in r["cmds"]:
                print(f"        {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
