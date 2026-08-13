#!/usr/bin/env python3
"""validate_gnmi.py — pre-flight check that every device serves correct secure gNMI.

Before walking all 538 roots, confirm each device: (1) accepts a secure TLS gNMI
session on 9339, (2) returns data for a known-good oper root, and (3) returns
data for a known-good config root. Prints a per-device PASS/FAIL so we don't burn
a long walk against a half-provisioned device.

    python validate_gnmi.py --all
"""
from __future__ import annotations

import argparse

from collect_fleet import load_env, load_devices
from gnmi_get import GNMI_PORT
from pygnmi.client import gNMIclient

OPER_PROBE = "rfc7951:/Cisco-IOS-XE-arp-oper:arp-data"      # oper: always present
CONFIG_PROBE = "rfc7951:/Cisco-IOS-XE-native:native"        # config: always present


def _has_data(resp) -> bool:
    return bool(resp and resp.get("notification") and
                any(n.get("update") for n in resp["notification"]))


def check(dev, env) -> dict:
    try:
        gc = gNMIclient(target=(dev["host"], GNMI_PORT), username=env["IOSXE_USER"],
                        password=env["IOSXE_PASS"], insecure=False, skip_verify=True, timeout=15)
        gc.connect()
    except Exception as e:  # noqa: BLE001
        return {"pid": dev["pid"], "tls": False, "error": str(e).split("Error:")[-1][:80].strip()}
    result = {"pid": dev["pid"], "tls": True}
    for label, path, dt in (("oper", OPER_PROBE, "state"), ("config", CONFIG_PROBE, "config")):
        try:
            result[label] = _has_data(gc.get(path=[path], datatype=dt, encoding="json_ietf"))
        except Exception as e:  # noqa: BLE001
            result[label] = False
            result[label + "_err"] = str(e).split("Error:")[-1][:60].strip()
    try:
        gc.close()
    except Exception:
        pass
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    env = load_env()
    all_ok = True
    for dev in load_devices([args.device] if args.device else None):
        r = check(dev, env)
        ok = r.get("tls") and r.get("oper") and r.get("config")
        all_ok = all_ok and ok
        tag = "PASS" if ok else "FAIL"
        detail = f"tls={r.get('tls')} oper={r.get('oper')} config={r.get('config')}"
        if r.get("error"):
            detail += f"  ! {r['error']}"
        print(f"  {tag}  {r['pid']:12} {detail}", flush=True)
    print("\nALL DEVICES READY" if all_ok else "\nSOME DEVICES NOT READY — fix before walking")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
