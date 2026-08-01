#!/usr/bin/env python3
"""Diagnose a device's path to the telemetry collector (read-only).

Runs routing/VRF/ping checks toward the collector IP so we can tell whether a
'Transport requested' subscription is failing on routing, VRF, or an ACL.

  .venv-harness/bin/python diag_reachability.py --device C9400 --target 10.85.134.200
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from netmiko import ConnectHandler

REPO = Path(__file__).resolve().parents[3]
ENV = REPO / "scripts" / "harness" / ".env"
INV = REPO / "scripts" / "harness" / "inventory.json"


def load_env():
    env = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def pick(sel):
    for d in json.loads(INV.read_text(encoding="utf-8")):
        if sel.lower() in d["name"].lower() or sel.lower() in d.get("pid", "").lower():
            return d
    raise SystemExit(f"no device matches {sel!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", required=True)
    ap.add_argument("--target", default="10.85.134.200")
    args = ap.parse_args()
    env = load_env()
    dev = pick(args.device)
    t = args.target
    conn = ConnectHandler(device_type="cisco_xe", host=dev["host"], username=env["IOSXE_USER"],
                          password=env["IOSXE_PASS"], secret=env["IOSXE_PASS"], port=22,
                          fast_cli=False, conn_timeout=25)
    try:
        conn.enable()
    except Exception:
        pass
    cmds = [
        "show vrf",
        f"show ip interface brief | include {dev['host']}",
        f"show ip route {t}",
        f"ping {t} repeat 2 timeout 1",
        f"show ip route vrf Mgmt-vrf {t}",
        f"ping vrf Mgmt-vrf {t} repeat 2 timeout 1",
    ]
    for cmd in cmds:
        print("\n" + "-" * 66 + f"\n# {cmd}\n" + "-" * 66)
        try:
            print(conn.send_command(cmd, read_timeout=40))
        except Exception as exc:
            print(f"(error: {exc})")
    conn.disconnect()


if __name__ == "__main__":
    raise SystemExit(main())
