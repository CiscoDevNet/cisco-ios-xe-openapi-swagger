#!/usr/bin/env python3
"""Remove any leftover temp MDT subscriptions (ID >= 900000) from the fleet.

Safety net for an interrupted collect_fleet run. Never touches the pre-existing
DNAC assurance subs (500-504, 750/751, 8882) or anything below 900000.

  .venv-harness/bin/python cleanup_stragglers.py            # all devices
  .venv-harness/bin/python cleanup_stragglers.py --device C9300
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from netmiko import ConnectHandler

REPO = Path(__file__).resolve().parents[3]
ENV = REPO / "scripts" / "harness" / ".env"
INV = REPO / "scripts" / "harness" / "inventory.json"
MIN_TEMP_ID = 900000


def load_env():
    env = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def devices(selector):
    devs = json.loads(INV.read_text(encoding="utf-8"))
    if not selector:
        return devs
    return [d for d in devs if selector.lower() in d["name"].lower() or selector.lower() in d.get("pid", "").lower()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default=None)
    args = ap.parse_args()
    env = load_env()
    for dev in devices(args.device):
        try:
            conn = ConnectHandler(device_type="cisco_xe", host=dev["host"], username=env["IOSXE_USER"],
                                  password=env["IOSXE_PASS"], secret=env["IOSXE_PASS"], port=22,
                                  fast_cli=False, conn_timeout=25)
        except Exception as exc:
            print(f"{dev['pid']:12} connect failed: {exc}")
            continue
        try:
            conn.enable()
        except Exception:
            pass
        run = conn.send_command("show running-config | include ^telemetry ietf subscription", read_timeout=60)
        ids = sorted({int(m) for m in re.findall(r"telemetry ietf subscription (\d+)", run) if int(m) >= MIN_TEMP_ID})
        if ids:
            conn.send_config_set([f"no telemetry ietf subscription {i}" for i in ids], read_timeout=90)
            print(f"{dev['pid']:12} removed {len(ids)} straggler(s): {ids}")
        else:
            print(f"{dev['pid']:12} clean (no temp subs >= {MIN_TEMP_ID})")
        conn.disconnect()


if __name__ == "__main__":
    raise SystemExit(main())
