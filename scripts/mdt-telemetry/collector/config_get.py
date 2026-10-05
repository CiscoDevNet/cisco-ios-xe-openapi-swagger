#!/usr/bin/env python3
"""config_get.py — capture what is configured on a device (SSH CLI).

Writes ``output/config-<PID>.json`` with:
  * ``show_run``       — ``show running-config`` text, secrets masked (mask_cli)
  * ``sections``       — top-level CLI commands (first two words), for a quick "what is configured"
  * ``restconf_json``  — ``show running-config | format restconf-json`` parsed (every YANG config
                         model the running config populates: native, *-cfg, ...), secrets masked
  * ``models``         — the top-level ``module:container`` keys of restconf_json

prune_walk_catalog.py uses restconf_json to walk only configured native/cfg containers.

    python -X utf8 config_get.py --device C9300-24UX
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from collect_fleet import load_devices, load_env
from redact_payload import mask_cli, redact_obj

OUT = Path(__file__).resolve().parent / "output"


def sections(show_run: str) -> list[str]:
    tops = set()
    for line in show_run.splitlines():
        if line and not line[0].isspace() and not line.startswith(("!", "Building", "Current", "end")):
            tops.add(" ".join(line.split()[:2]))
    return sorted(tops)


def parse_restconf_json(text: str) -> dict:
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON in 'show running-config | format restconf-json' output")
    document = json.loads(text[start:])
    return document.get("data", document)


def build_record(device: dict, show_run: str, restconf_text: str) -> dict:
    models = parse_restconf_json(restconf_text)
    masked = mask_cli(show_run)
    return {
        "pid": device["pid"], "name": device["name"],
        "collected": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "show_run": masked,
        "show_run_lines": len(show_run.splitlines()),
        "sections": sections(masked),
        "models": sorted(models),
        "restconf_json": redact_obj(models),
    }


def capture(device: dict, env: dict, timeout: int) -> dict:
    from netmiko import ConnectHandler

    conn = ConnectHandler(device_type="cisco_xe", host=device["host"], username=env["IOSXE_USER"],
                          password=env["IOSXE_PASS"], secret=env["IOSXE_PASS"], conn_timeout=30)
    try:
        try:
            conn.enable()
        except Exception:  # noqa: BLE001 - already privileged
            pass
        conn.send_command("terminal length 0")
        show_run = conn.send_command("show running-config", read_timeout=timeout)
        restconf_text = conn.send_command("show running-config | format restconf-json", read_timeout=timeout)
    finally:
        conn.disconnect()
    return build_record(device, show_run, restconf_text)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--device", required=True, help="Device name/PID substring.")
    ap.add_argument("--timeout", type=int, default=300, help="Seconds per command (large configs over a WAN).")
    ap.add_argument("--limit", type=int, default=0, help="Accepted for kit compatibility; ignored.")
    args = ap.parse_args()

    devices = load_devices([args.device])
    if not devices:
        sys.exit(f"device {args.device!r} not in inventory")
    env = load_env()
    failures = 0
    for device in devices:
        try:
            record = capture(device, env, args.timeout)
        except Exception as exc:  # noqa: BLE001 - report per device, keep going
            print(f"  ! {device['pid']}: config capture failed: {exc}")
            failures += 1
            continue
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"config-{device['pid']}.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
        print(f"  {device['pid']}: show run {record['show_run_lines']} lines, {len(record['sections'])} sections, "
              f"models {len(record['models'])}: {', '.join(record['models'])}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
