#!/usr/bin/env python3
"""
collect_one_payload.py — end-to-end single-payload MDT capture on THIS host.

Pushes ONE telemetry subscription to ONE device over SSH (stable IOS XE CLI),
waits for the local Telegraf receiver to decode at least one payload, then
REMOVES the subscription so the device is left clean.

  device  --(gRPC dial-out :57500)-->  Telegraf (cisco_telemetry_mdt)
                                         -> collector/output/mdt-live.json

Credentials come from scripts/harness/.env (IOSXE_USER / IOSXE_PASS); device
IPs come from scripts/harness/inventory.json. Nothing secret is printed.

Safety: config push is gated behind --apply (default is a dry run that only
prints the planned CLI). The subscription is always removed in a finally block,
even on error, unless --keep is given.

Usage:
  # Dry run (print planned config, no device change):
  .venv-harness/bin/python collect_one_payload.py --device C9300

  # Actually push, capture one payload, then clean up:
  .venv-harness/bin/python collect_one_payload.py --device C9300 --apply
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPO_ROOT / "scripts" / "harness" / ".env"
INVENTORY = REPO_ROOT / "scripts" / "harness" / "inventory.json"
OUTPUT_FILE = Path(__file__).resolve().parent / "output" / "mdt-live.json"

DEFAULT_RECEIVER_IP = "10.85.134.200"
DEFAULT_RECEIVER_PORT = 57500
DEFAULT_SUB_ID = 99001
DEFAULT_XPATH = "/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization"
DEFAULT_PERIOD_CS = 30000  # centiseconds -> 300s; IOS XE sends the first full payload immediately


def load_env(path: Path) -> dict:
    creds = {}
    if not path.exists():
        sys.exit(f"Credentials file not found: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        creds[key.strip()] = val.strip().strip('"').strip("'")
    if not creds.get("IOSXE_USER") or not creds.get("IOSXE_PASS"):
        sys.exit("IOSXE_USER / IOSXE_PASS missing from .env")
    return creds


def pick_device(selector: str) -> dict:
    devices = json.loads(INVENTORY.read_text(encoding="utf-8"))
    sel = selector.lower()
    for dev in devices:
        if sel in dev["name"].lower() or sel in dev.get("pid", "").lower():
            return dev
    sys.exit(f"No device in inventory matches '{selector}'. "
             f"Options: {', '.join(d['pid'] for d in devices)}")


def enable_lines(sub_id: int, xpath: str, period_cs: int, rx_ip: str, rx_port: int,
                 source_addr: str | None = None, source_vrf: str | None = None) -> list[str]:
    lines = [
        f"telemetry ietf subscription {sub_id}",
        " encoding encode-kvgpb",
        f" filter xpath {xpath}",
        " stream yang-push",
        f" update-policy periodic {period_cs}",
    ]
    if source_vrf:
        # The collector is reachable only via the management VRF on some
        # platforms (Gi0/0 in Mgmt-vrf); without this they stick in
        # 'Transport requested'.
        lines.append(f" source-vrf {source_vrf}")
    if source_addr:
        # Source the dial-out from the device's own mgmt IP (the reachable
        # interface) — mirrors the lab's working DNAC subscriptions.
        lines.append(f" source-address {source_addr}")
    lines.append(f" receiver ip address {rx_ip} {rx_port} protocol grpc-tcp")
    return lines


def disable_lines(sub_id: int) -> list[str]:
    return [f"no telemetry ietf subscription {sub_id}"]


def count_records(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    except OSError:
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--device", default="C9300", help="Device name/PID substring (default: C9300).")
    ap.add_argument("--receiver-ip", default=DEFAULT_RECEIVER_IP, help="This host's IP the device streams to.")
    ap.add_argument("--receiver-port", type=int, default=DEFAULT_RECEIVER_PORT)
    ap.add_argument("--sub-id", type=int, default=DEFAULT_SUB_ID)
    ap.add_argument("--xpath", default=DEFAULT_XPATH)
    ap.add_argument("--period-cs", type=int, default=DEFAULT_PERIOD_CS, help="Periodic interval in centiseconds.")
    ap.add_argument("--source-address", default=None,
                    help="Subscription source-address (default: the device's own mgmt IP from inventory).")
    ap.add_argument("--source-vrf", default=None,
                    help="Subscription source-vrf (e.g. Mgmt-vrf) when the collector is only reachable via a VRF.")
    ap.add_argument("--timeout", type=int, default=90, help="Seconds to wait for a payload.")
    ap.add_argument("--keep", action="store_true", help="Do NOT remove the subscription afterwards.")
    ap.add_argument("--apply", action="store_true", help="Actually push to the device (default: dry run).")
    args = ap.parse_args()

    dev = pick_device(args.device)
    source_addr = args.source_address or dev["host"]
    lines = enable_lines(args.sub_id, args.xpath, args.period_cs, args.receiver_ip, args.receiver_port,
                         source_addr, args.source_vrf)

    print(f"Device : {dev['name']} ({dev['pid']}) {dev['host']}")
    print(f"Receiver: {args.receiver_ip}:{args.receiver_port}")
    print("Planned config:")
    for ln in lines:
        print("  " + ln)

    if not args.apply:
        print("\n(dry run — pass --apply to push, capture, and clean up)")
        return 0

    from netmiko import ConnectHandler

    creds = load_env(ENV_FILE)
    conn_params = {
        "device_type": "cisco_xe",
        "host": dev["host"],
        "username": creds["IOSXE_USER"],
        "password": creds["IOSXE_PASS"],
        "secret": creds["IOSXE_PASS"],
        "port": 22,
        "fast_cli": False,
        "conn_timeout": 20,
    }

    baseline = count_records(OUTPUT_FILE)
    captured = False
    conn = None
    try:
        print(f"\nConnecting to {dev['host']} …")
        conn = ConnectHandler(**conn_params)
        try:
            conn.enable()
        except Exception:
            pass  # already privileged or no enable secret needed

        print(f"Pushing subscription {args.sub_id} …")
        conn.send_config_set(lines)
        conn.save_config()

        state = conn.send_command(f"show telemetry ietf subscription {args.sub_id} receiver")
        print("Receiver state:\n" + "\n".join("  " + l for l in state.splitlines()[:12]))

        print(f"\nWaiting up to {args.timeout}s for a payload at {OUTPUT_FILE.name} …")
        deadline = time.time() + args.timeout
        while time.time() < deadline:
            if count_records(OUTPUT_FILE) > baseline:
                captured = True
                break
            time.sleep(3)
    finally:
        if conn is not None:
            if not args.keep:
                print(f"Removing subscription {args.sub_id} (cleanup) …")
                try:
                    conn.send_config_set(disable_lines(args.sub_id))
                    conn.save_config()
                except Exception as exc:
                    print(f"  ! cleanup failed, remove manually: no telemetry ietf subscription {args.sub_id} ({exc})")
            try:
                conn.disconnect()
            except Exception:
                pass

    total = count_records(OUTPUT_FILE)
    new = total - baseline
    if captured:
        print(f"\nCAPTURED {new} record(s). Saved to {OUTPUT_FILE}")
        return 0
    print(f"\nNo payload arrived within {args.timeout}s (new records: {new}).")
    print("Check: device->{}:{} reachability (ACL/route), subscription receiver state above.".format(
        args.receiver_ip, args.receiver_port))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
