#!/usr/bin/env python3
"""
onboard.py — Prepare a Cisco IOS-XE device for the data-collection harness.

Enables, idempotently and only where missing:
  aaa        local AAA (aaa new-model + default login/exec lists) and a privilege-15
             harness user — ONLY on a device with no AAA. Existing AAA (e.g. TACACS)
             is never modified; missing lists are reported for manual action.
  https      ip http secure-server (+ ip http authentication local|aaa)
  restconf   restconf
  netconf    netconf-yang
  gnmi       secure gNMI on the device's self-signed trustpoint (port 9339)
  snmp       SNMP -> RESTCONF MIB bridge (only with --snmp-community / IOSXE_SNMP_COMMUNITY)
MDT needs no device-wide config; `harness collect` adds and removes dial-out
subscriptions itself. This step only reports whether the receiver is reachable.

Safety: dry run by default (prints the plan, secrets masked). --apply backs up the
running-config first, applies step by step, verifies a fresh SSH login after any AAA
change (rolling AAA back on failure), then probes RESTCONF/NETCONF/gNMI. Nothing is
written to startup-config unless --save.

Usage:
    python -m scripts.harness.onboard --device C9300               # plan only
    python -m scripts.harness.onboard --device C9300 --apply       # configure
    python -m scripts.harness.onboard --all --apply --save --receiver-ip 10.1.1.5
"""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.harness import inventory as inv  # noqa: E402

DEFAULT_OUT = Path(__file__).resolve().parent / "onboard-output"
SECRET_RE = re.compile(r"((?:secret|password|community|snmp-community-string)\s+(?:\d+\s+)?)\S+", re.I)


def mask(line: str) -> str:
    return SECRET_RE.sub(r"\1<masked>", line)


@dataclass
class Step:
    name: str
    status: str                      # ok | todo | manual | skipped
    lines: list[str] = field(default_factory=list)
    note: str = ""


def has(config: str, pattern: str) -> bool:
    return re.search(pattern, config, re.M) is not None


def self_signed_trustpoint(config: str) -> Optional[str]:
    match = re.search(r"^crypto pki trustpoint (TP-self-signed-\d+)", config, re.M)
    return match.group(1) if match else None


def hostname(config: str) -> Optional[str]:
    match = re.search(r"^hostname (\S+)", config, re.M)
    return match.group(1) if match else None


def plan(config: str, username: str, password: str, snmp_community: Optional[str] = None) -> list[Step]:
    """Build the onboarding plan from a running-config. Pure function (unit-tested)."""
    steps: list[Step] = []
    user_re = rf"^username {re.escape(username)} "
    aaa_on = has(config, r"^aaa new-model$")
    login_default = re.search(r"^aaa authentication login default (.+)$", config, re.M)
    exec_default = re.search(r"^aaa authorization exec default (.+)$", config, re.M)

    if not aaa_on:
        lines = [] if has(config, user_re) else [f"username {username} privilege 15 secret 0 {password}"]
        lines += ["aaa new-model", "aaa authentication login default local",
                  "aaa authorization exec default local"]
        steps.append(Step("aaa", "todo", lines, "no AAA on device: enable local AAA (lockout-checked)"))
        http_auth = "local"
    elif login_default and exec_default:
        steps.append(Step("aaa", "ok", note=f"existing AAA kept (login: {login_default.group(1)})"))
        http_auth = "local" if login_default.group(1).split()[0] == "local" else "aaa"
    else:
        missing = [n for n, m in (("aaa authentication login default", login_default),
                                  ("aaa authorization exec default", exec_default)) if not m]
        steps.append(Step("aaa", "manual", note="existing AAA left unchanged; RESTCONF/NETCONF need "
                          + " and ".join(missing) + " <method> (privilege 15 for the harness user)"))
        http_auth = "aaa"
    if aaa_on and not has(config, user_re) and http_auth == "local":
        steps.append(Step("user", "manual", note=f"local AAA but no 'username {username}' — create a privilege-15 user"))

    https = [] if has(config, r"^ip http secure-server$") else ["ip http secure-server"]
    if not has(config, r"^ip http authentication "):
        https.append(f"ip http authentication {http_auth}")
    steps.append(Step("https", "todo" if https else "ok", https))
    steps.append(Step("restconf", "ok" if has(config, r"^restconf$") else "todo",
                      [] if has(config, r"^restconf$") else ["restconf"]))
    steps.append(Step("netconf", "ok" if has(config, r"^netconf-yang$") else "todo",
                      [] if has(config, r"^netconf-yang$") else ["netconf-yang"]))

    if has(config, r"^gnxi secure-server$") and has(config, r"^gnxi secure-trustpoint "):
        steps.append(Step("gnmi", "ok"))
    else:
        trustpoint = self_signed_trustpoint(config) or "<TP-self-signed after https>"
        lines = [] if has(config, r"^gnxi$") else ["gnxi"]
        # 'service internal' unlocks secure-allow-self-signed-trustpoint on 26.1.x.
        lines += [] if has(config, r"^service internal$") else ["service internal"]
        lines += ["gnxi secure-allow-self-signed-trustpoint", "gnxi secure-password-auth",
                  f"gnxi secure-trustpoint {trustpoint}", "gnxi secure-server"]
        steps.append(Step("gnmi", "todo", lines, "secure gNMI on :9339 with the self-signed trustpoint"))

    if snmp_community:
        lines = []
        if not has(config, rf"^snmp-server community {re.escape(snmp_community)} RO"):
            lines.append(f"snmp-server community {snmp_community} RO")
        if not has(config, r"^snmp ifmib ifindex persist$"):
            lines.append("snmp ifmib ifindex persist")
        if not has(config, rf"^netconf-yang cisco-ia snmp-community-string {re.escape(snmp_community)}$"):
            lines.append(f"netconf-yang cisco-ia snmp-community-string {snmp_community}")
        steps.append(Step("snmp", "todo" if lines else "ok", lines, "SNMP -> RESTCONF/NETCONF MIB bridge"))
    else:
        steps.append(Step("snmp", "skipped", note="no --snmp-community: MIB modules will not return data"))
    return steps


def _connect(dev: "inv.Device", auth):
    from netmiko import ConnectHandler
    return ConnectHandler(device_type="cisco_xe", host=dev.host, username=auth[0], password=auth[1],
                          fast_cli=False, conn_timeout=30, banner_timeout=30, auth_timeout=30)


def _push(conn, lines: list[str]) -> str:
    output = conn.send_config_set(lines, read_timeout=120)
    if re.search(r"^% (Invalid|Incomplete|Ambiguous)", output, re.M):
        raise RuntimeError("device rejected: " + mask(output.strip().splitlines()[-1]))
    return output


def _login_ok(dev: "inv.Device", auth) -> bool:
    try:
        probe = _connect(dev, auth)
        try:
            return "15" in probe.send_command("show privilege")
        finally:
            probe.disconnect()
    except Exception:  # noqa: BLE001 - any failure means the new login path is broken
        return False


def _receiver_reachability(conn, receiver_ip: str) -> dict:
    result = {}
    for label, cmd in (("global", f"ping {receiver_ip} repeat 2 timeout 1"),
                       ("Mgmt-vrf", f"ping vrf Mgmt-vrf {receiver_ip} repeat 2 timeout 1")):
        out = conn.send_command(cmd, read_timeout=30)
        match = re.search(r"Success rate is (\d+) percent", out)
        result[label] = int(match.group(1)) if match else 0
    return result


def _wait_ready(dev: "inv.Device", seconds: int = 120) -> dict:
    def port_open(port: int) -> bool:
        try:
            with socket.create_connection((dev.host, port), timeout=4):
                return True
        except OSError:
            return False
    deadline = time.time() + seconds
    state = {}
    while time.time() < deadline:
        state = {"restconf:443": port_open(dev.port), "netconf:830": port_open(830), "gnmi:9339": port_open(9339)}
        if all(state.values()):
            break
        time.sleep(10)
    return state


def onboard_device(dev, auth, apply: bool, save: bool, snmp_community: Optional[str],
                   receiver_ip: Optional[str], out_dir: Path) -> dict:
    report = {"device": dev.name, "host": dev.host, "applied": [], "time": datetime.now(timezone.utc).isoformat()}
    conn = _connect(dev, auth)
    try:
        running = conn.send_command("show running-config", read_timeout=180)
        report["hostname"] = hostname(running)
        report["version"] = (re.search(r"^version (\S+)", running, re.M) or [None, None])[1]
        steps = plan(running, auth[0], auth[1], snmp_community)
        report["plan"] = [{"name": s.name, "status": s.status, "lines": [mask(l) for l in s.lines], "note": s.note}
                          for s in steps]
        if receiver_ip:
            report["receiver_reachability"] = _receiver_reachability(conn, receiver_ip)
        todo = [s for s in steps if s.status == "todo"]
        if not apply or not todo:
            return report

        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = out_dir / f"{dev.name}-{stamp}-running-config.txt"
        backup.write_text(running, encoding="utf-8")
        os.chmod(backup, 0o600)
        report["backup"] = str(backup)

        for step in todo:
            if step.name == "gnmi" and "<TP-self-signed" in " ".join(step.lines):
                running = conn.send_command("show running-config", read_timeout=180)
                trustpoint = self_signed_trustpoint(running)
                if not trustpoint:
                    report["applied"].append({"step": "gnmi", "error": "no self-signed trustpoint after https"})
                    continue
                step.lines = [l.replace("<TP-self-signed after https>", trustpoint) for l in step.lines]
            _push(conn, step.lines)
            report["applied"].append({"step": step.name, "lines": [mask(l) for l in step.lines]})
            if step.name == "aaa" and not _login_ok(dev, auth):
                rollback = ["no aaa new-model"]
                if step.lines[0].startswith("username "):
                    rollback.append(f"no username {auth[0]}")
                _push(conn, rollback)
                report["applied"].append({"step": "aaa-rollback", "lines": rollback})
                raise RuntimeError("fresh SSH login failed after enabling AAA; AAA rolled back")
        report["ready"] = _wait_ready(dev)
        if save:
            conn.save_config()
            report["saved"] = True
        return report
    finally:
        conn.disconnect()


def print_report(report: dict) -> None:
    print(f"\n=== {report['device']} ({report['host']}) hostname={report.get('hostname')} version={report.get('version')}")
    for step in report.get("plan", []):
        print(f"  [{step['status']:7}] {step['name']:9} {step['note']}")
        for line in step["lines"] if step["status"] == "todo" else []:
            print(f"              {line}")
    if "receiver_reachability" in report:
        print(f"  receiver ping success %: {report['receiver_reachability']}")
    for item in report.get("applied", []):
        print(f"  applied {item}")
    if "ready" in report:
        print(f"  ports after apply: {report['ready']}")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--device", action="append", dest="devices", help="Device name/PID substring (repeatable)")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--inventory")
    ap.add_argument("--apply", action="store_true", help="Configure the device (default: plan only)")
    ap.add_argument("--save", action="store_true", help="write memory after a successful apply")
    ap.add_argument("--snmp-community", default=os.environ.get("IOSXE_SNMP_COMMUNITY"))
    ap.add_argument("--receiver-ip", help="MDT receiver IP to test reachability from the device")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="Backups and reports (contains config: keep private)")
    args = ap.parse_args(argv)

    devices = inv.load_inventory(Path(args.inventory) if args.inventory else None)
    if not args.all:
        if not args.devices:
            ap.error("--device or --all is required")
        devices = [d for d in devices if any(s.lower() in d.name.lower() or s.lower() in d.pid.lower()
                                             for s in args.devices)]
    if not devices:
        print("ERROR: no matching devices in inventory", file=sys.stderr)
        return 2
    auth = inv.load_credentials()
    out_dir = Path(args.out)
    failures = 0
    for dev in devices:
        try:
            report = onboard_device(dev, auth, args.apply, args.save, args.snmp_community, args.receiver_ip, out_dir)
        except Exception as exc:  # noqa: BLE001 - report per device, continue with the rest
            report = {"device": dev.name, "host": dev.host, "error": mask(str(exc))}
            failures += 1
        print_report(report)
        if "error" in report:
            print(f"  ERROR: {report['error']}")
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{dev.name}-onboard.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    if not args.apply:
        print("\nDry run only. Re-run with --apply to configure.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
