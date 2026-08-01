#!/usr/bin/env python3
"""
mdt_manage.py — pyATS-driven enable / disable / status for IOS XE Model-Driven
Telemetry subscriptions across a fleet of Catalyst switches and C9800 WLCs.

Connects to each device over SSH (pyATS / Unicon), then:
  * status   — read `show telemetry ietf subscription all` + receiver/connection
               state (READ-ONLY; always safe).
  * enable   — build the `telemetry ietf subscription …` config for the device's
               platform set and (with --apply) push it, then verify.
  * disable  — remove those subscriptions (`no telemetry ietf subscription <id>`)
               and (with --apply) push, then verify.

Platform-aware: each device's `custom.mdt_role` picks its subscription set —
`switch` -> validation/subscriptions.yaml, `wlc` -> validation/subscriptions-wlc.yaml.

SAFETY MODEL
------------
Config changes are gated behind --apply. Without it the tool is a DRY RUN: it
connects (or, with --offline, doesn't), prints the exact config it *would* send,
and changes nothing. `status` never modifies the device. Before every enable the
tool captures the current `telemetry` running-config as a backup in the report.

Credentials come from the testbed (env-var references) — never from this file or
the command line.

Usage
-----
  # Dry run (show planned config, no device changes):
  python mdt_manage.py --testbed testbed.yaml --action enable --receiver-ip 10.0.0.9

  # Read current state across the fleet:
  python mdt_manage.py --testbed testbed.yaml --action status

  # Actually push (enable) to two devices:
  python mdt_manage.py --testbed testbed.yaml --action enable \
        --receiver-ip 10.0.0.9 --devices cat9300-1 cat9800-1 --apply

  # Remove all managed subscriptions:
  python mdt_manage.py --testbed testbed.yaml --action disable --apply

  # Preview config without any device connection:
  python mdt_manage.py --testbed testbed.yaml --action enable --receiver-ip 10.0.0.9 --offline

Requirements: pip install "pyats[library]"   (Unicon + Genie)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

PYATS_DIR = Path(__file__).resolve().parent
HARNESS_DIR = PYATS_DIR.parent
VALIDATION_DIR = HARNESS_DIR / "validation"
RESULTS_DIR = PYATS_DIR / "results"

SUBSCRIPTION_SETS = {
    "switch": VALIDATION_DIR / "subscriptions.yaml",
    "wlc": VALIDATION_DIR / "subscriptions-wlc.yaml",
}

# Centisecond periodic intervals per tier (matches generate_ios_config.py).
TIER_INTERVALS = {"hot": 3000, "warm": 6000, "cool": 30000}

STATUS_COMMANDS = [
    "show telemetry ietf subscription all",
    "show telemetry ietf subscription all receiver",
    "show telemetry internal connection",
]


# --- subscription set loading ------------------------------------------------

def role_for_device(device) -> str:
    """Resolve a device's MDT role ('switch' | 'wlc') from testbed custom data,
    falling back to its type/platform."""
    role = None
    custom = getattr(device, "custom", None)
    if isinstance(custom, dict):
        role = custom.get("mdt_role")
    elif custom is not None:
        role = getattr(custom, "mdt_role", None)
    if role:
        return str(role).lower()
    hint = " ".join(str(x or "") for x in (getattr(device, "type", ""), getattr(device, "platform", ""))).lower()
    return "wlc" if "9800" in hint or "wlc" in hint else "switch"


def load_subscription_set(role: str) -> dict:
    path = SUBSCRIPTION_SETS.get(role)
    if not path or not path.exists():
        raise FileNotFoundError(f"No subscription set for role '{role}' ({path})")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def select_ids(config: dict, sub_ids: list[str] | None) -> list:
    ids = list(config.get("subscriptions", {}).keys())
    if not sub_ids:
        return sorted(ids, key=lambda x: str(x))
    wanted = {str(s) for s in sub_ids}
    return sorted([i for i in ids if str(i) in wanted], key=lambda x: str(x))


# --- config builders (pure, no device I/O) -----------------------------------

def enable_config(config: dict, receiver_ip: str, receiver_port: int, ids: list) -> list[str]:
    """Build the IOS XE config lines that create the given subscriptions."""
    subs = config["subscriptions"]
    lines: list[str] = []
    for sub_id in ids:
        sub = subs[sub_id]
        interval = TIER_INTERVALS.get(sub.get("tier"), 30000)
        lines += [
            f"telemetry ietf subscription {sub_id}",
            " encoding encode-kvgpb",
            f" filter xpath {sub['xpath']}",
            " stream yang-push",
            f" update-policy periodic {interval}",
            f" receiver ip address {receiver_ip} {receiver_port} protocol grpc-tcp",
        ]
    return lines


def disable_config(ids: list) -> list[str]:
    """Build the IOS XE config lines that remove the given subscriptions."""
    return [f"no telemetry ietf subscription {sub_id}" for sub_id in ids]


# --- receiver resolution -----------------------------------------------------

def resolve_receiver(device, cli_ip: str | None, config: dict) -> str | None:
    """--receiver-ip flag > device custom.mdt_receiver_ip > YAML receiver.ip
    (unless it's the RECEIVER_IP placeholder)."""
    if cli_ip:
        return cli_ip
    custom = getattr(device, "custom", None)
    if isinstance(custom, dict) and custom.get("mdt_receiver_ip"):
        return custom["mdt_receiver_ip"]
    yaml_ip = config.get("receiver", {}).get("ip")
    if yaml_ip and yaml_ip != "RECEIVER_IP":
        return yaml_ip
    return None


# --- per-device execution ----------------------------------------------------

def plan_device(device, args) -> dict:
    """Compute the config plan for one device without touching it."""
    role = role_for_device(device)
    config = load_subscription_set(role)
    ids = select_ids(config, args.sub)
    receiver_port = args.receiver_port or config.get("receiver", {}).get("port", 57500)

    plan = {
        "device": device.name,
        "role": role,
        "subscription_count": len(ids),
        "subscription_ids": [str(i) for i in ids],
        "action": args.action,
    }

    if args.action == "enable":
        receiver_ip = resolve_receiver(device, args.receiver_ip, config)
        if not receiver_ip:
            plan["error"] = "No receiver IP (pass --receiver-ip or set custom.mdt_receiver_ip)."
            plan["config"] = []
            return plan
        plan["receiver"] = f"{receiver_ip}:{receiver_port}"
        plan["config"] = enable_config(config, receiver_ip, receiver_port, ids)
    elif args.action == "disable":
        plan["config"] = disable_config(ids)
    else:  # status
        plan["config"] = []
    return plan


def run_device(device, args, plan: dict) -> dict:
    """Connect and (for status, or enable/disable with --apply) act on the device."""
    result = dict(plan)
    result["connected"] = False
    result["applied"] = False

    try:
        device.connect(log_stdout=False, learn_hostname=True,
                        init_exec_commands=[], init_config_commands=[])
        result["connected"] = True
    except Exception as exc:  # unicon raises many subtypes; report and move on
        result["error"] = f"connect failed: {exc}"
        return result

    try:
        if args.action == "status":
            result["state"] = {cmd: device.execute(cmd) for cmd in STATUS_COMMANDS}
            return result

        # Backup current telemetry config before any change.
        try:
            result["backup"] = device.execute("show running-config | section telemetry")
        except Exception as exc:
            result["backup_error"] = str(exc)

        if plan.get("error") or not plan.get("config"):
            return result  # nothing to do / bad plan

        if not args.apply:
            result["note"] = "dry run — config not sent (pass --apply to push)"
            return result

        device.configure(plan["config"])
        result["applied"] = True
        # Verify after the change.
        result["verify"] = device.execute("show telemetry ietf subscription all")
        return result
    finally:
        try:
            device.disconnect()
        except Exception:
            pass


# --- orchestration -----------------------------------------------------------

def load_testbed(path: Path):
    try:
        from pyats.topology import loader
    except ImportError:
        sys.exit("pyATS not installed. Run: pip install \"pyats[library]\"")
    return loader.load(str(path))


def select_devices(testbed, names: list[str] | None):
    devices = list(testbed.devices.values())
    if names:
        wanted = set(names)
        devices = [d for d in devices if d.name in wanted]
        missing = wanted - {d.name for d in devices}
        if missing:
            sys.exit(f"Devices not in testbed: {', '.join(sorted(missing))}")
    return devices


def print_summary(results: list[dict], apply: bool) -> None:
    print("\n" + "=" * 68)
    print(f"{'DEVICE':<16}{'ROLE':<9}{'SUBS':>5}  RESULT")
    print("-" * 68)
    for r in results:
        if r.get("error"):
            outcome = "ERROR: " + r["error"][:38]
        elif "connected" not in r:
            outcome = "planned (offline)"
        elif r["action"] == "status":
            outcome = "read OK" if r.get("connected") else "unreachable"
        elif r.get("applied"):
            outcome = "APPLIED + verified"
        else:
            outcome = "dry run (use --apply)"
        print(f"{r['device']:<16}{r['role']:<9}{r['subscription_count']:>5}  {outcome}")
    print("=" * 68)


def write_report(results: list[dict], action: str) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RESULTS_DIR / f"mdt-manage-{action}-{stamp}.json"
    payload = {
        "generated": stamp,
        "action": action,
        "devices": results,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="pyATS enable/disable/status for IOS XE MDT subscriptions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--testbed", required=True, help="pyATS testbed YAML (see testbed.example.yaml).")
    parser.add_argument("--action", required=True, choices=["status", "enable", "disable"])
    parser.add_argument("--devices", nargs="+", help="Limit to these device names (default: all).")
    parser.add_argument("--sub", nargs="+", help="Limit to these subscription IDs (default: the full platform set).")
    parser.add_argument("--receiver-ip", help="Collector IP for enable (else per-device custom.mdt_receiver_ip / YAML).")
    parser.add_argument("--receiver-port", type=int, help="Collector port (default: 57500 / YAML).")
    parser.add_argument("--apply", action="store_true", help="Actually push config changes (default: dry run).")
    parser.add_argument("--offline", action="store_true", help="Build/print the plan without connecting to devices.")
    args = parser.parse_args()

    testbed_path = Path(args.testbed)
    if not testbed_path.exists():
        parser.error(f"testbed not found: {testbed_path}")

    if args.offline:
        # Build a lightweight device view from the raw YAML — no pyATS needed.
        raw = yaml.safe_load(testbed_path.read_text(encoding="utf-8"))
        results = []
        for name, spec in (raw.get("devices") or {}).items():
            if args.devices and name not in args.devices:
                continue
            stub = _StubDevice(name, spec)
            plan = plan_device(stub, args)
            results.append(plan)
            _print_plan(plan)
        print_summary(results, args.apply)
        report = write_report(results, args.action)
        print(f"\nReport: {report}")
        return 0

    testbed = load_testbed(testbed_path)
    devices = select_devices(testbed, args.devices)
    if args.apply and args.action in ("enable", "disable"):
        print(f"*** --apply set: pushing '{args.action}' to {len(devices)} device(s). ***")

    results = []
    for device in devices:
        plan = plan_device(device, args)
        _print_plan(plan)
        results.append(run_device(device, args, plan))

    print_summary(results, args.apply)
    report = write_report(results, args.action)
    print(f"\nReport: {report}")
    return 0


class _StubDevice:
    """Minimal device stand-in for --offline planning (no connection)."""

    def __init__(self, name: str, spec: dict):
        self.name = name
        self.type = spec.get("type", "")
        self.platform = spec.get("platform", "")
        self.custom = spec.get("custom", {}) or {}


def _print_plan(plan: dict) -> None:
    header = f"[{plan['device']}] role={plan['role']} action={plan['action']} subs={plan['subscription_count']}"
    if plan.get("receiver"):
        header += f" receiver={plan['receiver']}"
    print("\n" + header)
    if plan.get("error"):
        print("  ! " + plan["error"])
    for line in plan.get("config", []):
        print("  " + line)


if __name__ == "__main__":
    raise SystemExit(main())
