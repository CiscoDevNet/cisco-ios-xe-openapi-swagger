#!/usr/bin/env python3
"""Dump a device's existing telemetry config + subscription/receiver state (read-only).

Reveals how the working subscriptions reach their collector (source-address /
source-vrf / named receiver), so scaled collection can replicate it on devices
whose default-routed receiver stays in 'Transport requested'.

  .venv-harness/bin/python show_device_telemetry.py --device C9400
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
    args = ap.parse_args()
    env = load_env()
    dev = pick(args.device)
    conn = ConnectHandler(device_type="cisco_xe", host=dev["host"], username=env["IOSXE_USER"],
                          password=env["IOSXE_PASS"], secret=env["IOSXE_PASS"], port=22,
                          fast_cli=False, conn_timeout=25)
    try:
        conn.enable()
    except Exception:
        pass
    for cmd in [
        "show running-config | section telemetry",
        "show telemetry receiver all",
        "show telemetry ietf subscription all",
    ]:
        print("\n" + "=" * 70)
        print("# " + cmd)
        print("=" * 70)
        print(conn.send_command(cmd, read_timeout=60))
    conn.disconnect()


if __name__ == "__main__":
    raise SystemExit(main())
