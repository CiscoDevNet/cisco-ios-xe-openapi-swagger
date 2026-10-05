#!/usr/bin/env python3
"""
kit.py — single entry point for the portable IOS XE data-collection harness.

Runs from the repo or from an extracted kit (scripts/build_kit.py); both share the
same relative layout, so the proven collectors run unchanged.

    doctor                  check Python deps, Telegraf, inventory/credentials, data files, device ports
    onboard [...]           enable AAA/HTTPS/RESTCONF/NETCONF/gNMI(/SNMP) where missing (see onboard.py)
    facts                   record hostname, version, and YANG library modules per device (NETCONF)
    telegraf start|stop|status   local MDT gRPC dial-out receiver (bin/telegraf or telegraf on PATH)
    collect                 run every collector per device, then split MDT and score coverage
    walk                    config-driven per-xpath MDT walk: configured native/cfg xpaths until matched
    split-mdt               split output/mdt-live.json into mdt-<PID>.json by device hostname
    coverage                checklist: device-advertised data modules vs what each method returned
    bundle                  redact, secret-scan, checksum, and pack results for import_harness_bundle.py
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.harness import inventory as inv  # noqa: E402

HARNESS_DIR = Path(__file__).resolve().parent
REPO = HARNESS_DIR.parents[1]
COLLECTOR = REPO / "scripts" / "mdt-telemetry" / "collector"
OUTPUT = COLLECTOR / "output"
CAPTURES = HARNESS_DIR / "captures"
ONBOARD_OUT = HARNESS_DIR / "onboard-output"
RUN_DIR = HARNESS_DIR / "kit-run"
LOG_DIR = RUN_DIR / "logs"
KIT_INFO = REPO / "KIT.json"
MDT_LIVE = OUTPUT / "mdt-live.json"
HARNESS_SUBSCRIPTION = re.compile(r"9\d{5}")  # collect_fleet / recapture / walk ids
DEFAULT_MDT_PORT = 57500
BUNDLE_FORMAT = "iosxe-harness-bundle/1"

# Order matters: config first (what is configured); gnmi-sub reuses gnmi-<PID>.json; the long spec walk runs last.
METHODS = ["config", "restconf", "netconf", "gnmi", "gnmi-sub", "netconf-sub", "netconf-sub-config", "mdt",
           "restconf-walk"]
RAW_KINDS = ("config", "restconf", "netconf", "netconf-sub", "netconf-sub-config", "gnmi", "gnmi-sub", "mdt")
REQUIRED_MODULES = ("requests", "ncclient", "netmiko", "pygnmi", "yaml")
DEVICE_PORTS = {"ssh": 22, "restconf": 443, "netconf": 830, "gnmi": 9339}

sys.path.insert(0, str(COLLECTOR))


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def kit_info() -> dict:
    if KIT_INFO.exists():
        return json.loads(KIT_INFO.read_text(encoding="utf-8"))
    return {}


def default_release() -> str:
    """The release the devices run (kit build release, else releases/index.json device_data)."""
    release = kit_info().get("release")
    if release:
        return release
    index = REPO / "releases" / "index.json"
    if index.exists():
        data = json.loads(index.read_text(encoding="utf-8"))
        return data.get("device_data") or data.get("default") or data["releases"][0]["ver"]
    return "26.1.1"


def select_devices(selectors: Optional[list[str]]) -> list:
    devices = inv.load_inventory()
    if not selectors:
        return devices
    wanted = [s.lower() for s in selectors]
    return [d for d in devices if any(s in d.name.lower() or s in d.pid.lower() for s in wanted)]


def collector_env() -> dict:
    user, password = inv.load_credentials()
    return {"IOSXE_USER": user, "IOSXE_PASS": password}


def port_open(host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def local_ip_toward(host: str) -> str:
    """The address this host uses to reach `host` (the MDT receiver IP devices dial)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.connect((host, 9))
        return probe.getsockname()[0]


def telegraf_binary() -> Optional[str]:
    bundled = REPO / "bin" / "telegraf"
    if bundled.exists():
        return str(bundled)
    return shutil.which("telegraf")


# --------------------------------------------------------------------------- doctor

def cmd_doctor(args) -> int:
    problems = 0

    def report(ok: bool, label: str, detail: str = "", blocking: bool = True) -> None:
        nonlocal problems
        mark = "ok " if ok else ("FAIL" if blocking else "warn")
        print(f"  [{mark}] {label}{': ' + detail if detail else ''}")
        if not ok and blocking:
            problems += 1

    print("Python / packages")
    report(sys.version_info >= (3, 9), "python", sys.version.split()[0])
    for module in REQUIRED_MODULES:
        try:
            __import__(module)
            report(True, module)
        except ImportError as exc:
            report(False, module, str(exc))

    print("Telegraf (MDT receiver)")
    binary = telegraf_binary()
    if binary:
        version = subprocess.run([binary, "--version"], capture_output=True, text=True, check=False)
        report(version.returncode == 0, "telegraf", f"{binary} {version.stdout.strip()}")
    else:
        report(False, "telegraf", "not found (bin/telegraf or PATH); MDT collection unavailable", blocking=False)

    release = args.release or default_release()
    print(f"Data files (release {release})")
    for path in (OUTPUT / "subscribable-nodes.json", OUTPUT / "mib-nodes.json", REPO / "yang-prefix-map.json"):
        report(path.exists(), str(path.relative_to(REPO)))
    specs = REPO / "releases" / release
    spec_count = len(list(specs.glob("swagger-*-model/api/*.json"))) if specs.is_dir() else 0
    report(spec_count > 0, f"releases/{release} specs", f"{spec_count} files")

    print("Inventory / credentials")
    try:
        devices = select_devices(args.devices)
        report(bool(devices), "inventory", f"{len(devices)} device(s)")
    except inv.InventoryError as exc:
        report(False, "inventory", str(exc).splitlines()[0])
        devices = []
    try:
        inv.load_credentials()
        report(True, "credentials (IOSXE_USER / IOSXE_PASS)")
    except inv.CredentialError as exc:
        report(False, "credentials", str(exc).splitlines()[0])
    dotenv = HARNESS_DIR / ".env"
    report(dotenv.exists(), "scripts/harness/.env", "read by the protocol collectors")
    unknown_pid = [d.name for d in devices if d.pid in ("", "unknown")]
    report(not unknown_pid, "every device has a pid", ", ".join(unknown_pid))

    print("Devices")
    for device in devices:
        state = {name: port_open(device.host, port) for name, port in DEVICE_PORTS.items()}
        closed = [name for name, is_open in state.items() if not is_open]
        detail = "all ports open" if not closed else f"closed: {', '.join(closed)} (run onboard)"
        report(state["ssh"], f"{device.name} ({device.host})", detail, blocking=False)
        if not state["ssh"]:
            problems += 1
        else:
            print(f"         receiver IP toward device: {local_ip_toward(device.host)}")

    print("\nREADY" if not problems else f"\nNOT READY: {problems} blocking problem(s)")
    return 0 if not problems else 1


# --------------------------------------------------------------------------- facts

NATIVE_FILTER = ('<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">'
                 '<hostname/><version/></native>')
HARDWARE_FILTER = ('<device-hardware-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-device-hardware-oper">'
                   '<device-hardware><device-system-data><software-version/></device-system-data>'
                   '</device-hardware></device-hardware-data>')


def _xml_text(xml: str, tag: str) -> Optional[str]:
    match = re.search(rf"<{tag}>([^<]+)</{tag}>", xml)
    return match.group(1).strip() if match else None


def gather_facts(device, env: dict) -> dict:
    from netconf_get import _connect, build_ns_map, yang_library_ns

    connection = _connect({"host": device.host}, env)
    try:
        modules = yang_library_ns(connection) or build_ns_map(connection.server_capabilities)
        native = connection.get_config(source="running", filter=("subtree", NATIVE_FILTER)).data_xml
        try:
            hardware = connection.get(filter=("subtree", HARDWARE_FILTER)).data_xml
        except Exception:  # noqa: BLE001 - optional detail; some platforms omit it
            hardware = ""
    finally:
        connection.close_session()
    return {
        "pid": device.pid, "name": device.name, "host": device.host,
        "hostname": _xml_text(native, "hostname"), "version": _xml_text(native, "version"),
        "software_version": _xml_text(hardware, "software-version"),
        "modules": sorted(modules), "collected": utc_now(),
    }


def facts_path(pid: str) -> Path:
    return OUTPUT / f"facts-{pid}.json"


def load_facts() -> dict:
    facts = {}
    for path in sorted(OUTPUT.glob("facts-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        facts[data["pid"]] = data
    return facts


def cmd_facts(args) -> int:
    env = collector_env()
    failures = 0
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for device in select_devices(args.devices):
        try:
            facts = gather_facts(device, env)
        except Exception as exc:  # noqa: BLE001 - report per device, keep going
            print(f"  ! {device.name}: facts failed: {exc}")
            failures += 1
            continue
        facts_path(device.pid).write_text(json.dumps(facts, indent=1), encoding="utf-8")
        print(f"  {device.pid}: hostname={facts['hostname']} version={facts['version']} "
              f"modules={len(facts['modules'])}")
    return 1 if failures else 0


# --------------------------------------------------------------------------- telegraf

def telegraf_config(port: int, output_file: Path) -> str:
    return f"""# Generated by kit.py — Cisco MDT gRPC dial-out receiver (plaintext grpc-tcp).
[agent]
  interval = "10s"
  flush_interval = "2s"
  omit_hostname = true

[[inputs.cisco_telemetry_mdt]]
  transport = "grpc"
  service_address = ":{port}"

[[outputs.file]]
  files = [{json.dumps(str(output_file))}]
  data_format = "json"
  json_timestamp_units = "1ms"
  # Harness subscription ids only; devices' own standing subscriptions are dropped.
  [outputs.file.tagpass]
    subscription = ["9?????"]
"""


def telegraf_pid() -> Optional[int]:
    pidfile = RUN_DIR / "telegraf.pid"
    if not pidfile.exists():
        return None
    try:
        pid = int(pidfile.read_text().strip())
        os.kill(pid, 0)
        return pid
    except (ValueError, OSError):
        return None


def cmd_telegraf(args) -> int:
    pidfile = RUN_DIR / "telegraf.pid"
    running = telegraf_pid()
    if args.action == "status":
        print(f"telegraf: {'running pid ' + str(running) if running else 'stopped'}; output {MDT_LIVE}")
        return 0 if running else 1
    if args.action == "stop":
        if running:
            os.kill(running, signal.SIGTERM)
            print(f"stopped telegraf pid {running}")
        pidfile.unlink(missing_ok=True)
        return 0
    if running:
        print(f"telegraf already running (pid {running})")
        return 0
    binary = telegraf_binary()
    if not binary:
        print("ERROR: telegraf not found (bin/telegraf or PATH)", file=sys.stderr)
        return 2
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    config = RUN_DIR / "telegraf.conf"
    config.write_text(telegraf_config(args.port, MDT_LIVE), encoding="utf-8")
    log = open(RUN_DIR / "telegraf.log", "ab")
    process = subprocess.Popen([binary, "--config", str(config)], stdout=log, stderr=subprocess.STDOUT,
                               start_new_session=True)
    pidfile.write_text(str(process.pid))
    time.sleep(3)
    if process.poll() is not None:
        print(f"ERROR: telegraf exited ({process.returncode}); see {RUN_DIR / 'telegraf.log'}", file=sys.stderr)
        pidfile.unlink(missing_ok=True)
        return 1
    print(f"telegraf running pid {process.pid}, listening :{args.port} -> {MDT_LIVE}")
    return 0


# --------------------------------------------------------------------------- collect

def method_command(method: str, device, args, receiver_ip: Optional[str]) -> list[str]:
    limit = ["--limit", str(args.limit)] if args.limit else []
    scripts = {
        "config": ["config_get.py"],
        "restconf": ["restconf_get.py"], "netconf": ["netconf_get.py"], "gnmi": ["gnmi_get.py"],
        "gnmi-sub": ["gnmi_subscribe.py"], "netconf-sub": ["netconf_subscribe.py"],
        "netconf-sub-config": ["netconf_subscribe.py", "--config-roots", "--both"],
    }
    if method in scripts:
        script, *extra = scripts[method]
        if method == "restconf" and args.timeout:
            extra += ["--timeout", str(args.timeout)]
        if method.startswith("netconf-sub") and args.window:
            extra += ["--window", str(args.window)]
        return [sys.executable, str(COLLECTOR / script), "--device", device.name, *extra, *limit]
    if method == "mdt":
        command = [sys.executable, str(COLLECTOR / "collect_fleet.py"), "--apply", "--devices", device.name,
                   "--version", args.release, "--receiver-ip", receiver_ip,
                   "--receiver-port", str(args.receiver_port)]
        if args.limit:
            command += ["--per-cat-cap", str(args.limit)]
        return command
    if method == "restconf-walk":
        command = [sys.executable, str(HARNESS_DIR / "collector.py"), "--device", device.name,
                   "--specs-root", str(REPO / "releases" / args.release)]
        if args.timeout:
            command += ["--timeout", str(args.timeout)]
        return command + (["--roots-only"] if args.walk_roots_only else [])
    raise ValueError(method)


def run_logged(command: list[str], log_path: Path, cwd: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", encoding="utf-8", buffering=1) as log:
        process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding="utf-8", errors="replace",
                                   env={**os.environ, "PYTHONUNBUFFERED": "1"})
        for line in process.stdout:
            log.write(line)
            print("    " + line.rstrip())
        return process.wait()


def cmd_collect(args) -> int:
    args.release = args.release or default_release()
    methods = [m for m in METHODS if m in (args.methods or METHODS) and m not in (args.skip or [])]
    devices = select_devices(args.devices)
    if not devices:
        print("ERROR: no matching devices in inventory", file=sys.stderr)
        return 2
    if "mdt" in methods and not telegraf_pid():
        print("  ! telegraf is not running (kit.py telegraf start) — skipping MDT")
        methods.remove("mdt")
    env = collector_env()
    results = []
    for device in devices:
        print(f"\n######## {device.name} ({device.pid}, {device.host})")
        try:
            facts = gather_facts(device, env)
            facts_path(device.pid).write_text(json.dumps(facts, indent=1), encoding="utf-8")
            print(f"  facts: hostname={facts['hostname']} modules={len(facts['modules'])}")
        except Exception as exc:  # noqa: BLE001
            print(f"  ! facts failed ({exc}); MDT split and coverage need them")
        receiver_ip = args.receiver_ip or local_ip_toward(device.host)
        for method in methods:
            print(f"  --- {method}")
            log_path = LOG_DIR / f"{method}-{device.pid}.log"
            command = method_command(method, device, args, receiver_ip)
            started = time.time()
            code = run_logged(command, log_path, COLLECTOR if method != "restconf-walk" else REPO)
            results.append((device.pid, method, code, round(time.time() - started)))
    if "mdt" in methods:
        split_mdt()
    print("\nmethod results (exit code, seconds):")
    for pid, method, code, seconds in results:
        print(f"  {pid:20} {method:20} {'ok' if code == 0 else 'exit ' + str(code):8} {seconds}s")
    cmd_coverage(argparse.Namespace(devices=args.devices, release=args.release))
    return 0 if all(code == 0 for _, _, code, _ in results) else 1


# --------------------------------------------------------------------------- split-mdt

def source_map(facts: dict) -> dict:
    """MDT `source` tag (device hostname) -> PID, plus inventory names as a fallback."""
    mapping = {f["hostname"]: pid for pid, f in facts.items() if f.get("hostname")}
    try:
        for device in inv.load_inventory():
            mapping.setdefault(device.name, device.pid)
    except inv.InventoryError:
        pass
    return mapping


def resolve_source(source: str, mapping: dict) -> Optional[str]:
    if source in mapping:
        return mapping[source]
    for name, pid in mapping.items():
        if source and (source in name or name in source):
            return pid
    return None


def split_mdt(live: Path = MDT_LIVE, out_dir: Path = OUTPUT, facts: Optional[dict] = None) -> dict:
    """Merge the receiver stream into mdt-<PID>.json, appending only new records (idempotent)."""
    if not live.exists():
        print("  no MDT stream captured yet")
        return {}
    mapping = source_map(load_facts() if facts is None else facts)
    per_pid: dict[str, list[str]] = {}
    unknown: dict[str, int] = {}
    foreign = 0
    for line in live.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            tags = json.loads(line).get("tags", {})
        except json.JSONDecodeError:
            continue
        if not HARNESS_SUBSCRIPTION.fullmatch(str(tags.get("subscription", ""))):
            foreign += 1  # the device's own standing subscriptions, not harness data
            continue
        source = tags.get("source", "")
        pid = resolve_source(source, mapping)
        if pid is None:
            unknown[source] = unknown.get(source, 0) + 1
            continue
        per_pid.setdefault(pid, []).append(line)
    for pid, lines in per_pid.items():
        # Merge, never overwrite: earlier runs (e.g. a deep walk) may have written records the stream lacks.
        target = out_dir / f"mdt-{pid}.json"
        existing = set(target.read_text(encoding="utf-8").splitlines()) if target.exists() else set()
        new_lines = [line for line in dict.fromkeys(lines) if line not in existing]
        if new_lines:
            with open(target, "a", encoding="utf-8") as handle:
                handle.write("\n".join(new_lines) + "\n")
        print(f"  mdt-{pid}.json: {len(new_lines)} new of {len(lines)} records")
    for source, count in unknown.items():
        print(f"  ! {count} records from unknown source {source!r} (run facts for that device)")
    if foreign:
        print(f"  ignored {foreign} records from non-harness subscriptions")
    return {pid: len(lines) for pid, lines in per_pid.items()}


def cmd_split_mdt(args) -> int:
    split_mdt()
    return 0


# --------------------------------------------------------------------------- walk

def walk_state_path(pid: str, flavor: str, retry: bool = False) -> Path:
    return OUTPUT / f"walk-{pid}-{flavor}{'-retry' if retry else ''}.json"


def walk_results(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["results"] if path.exists() else {}


def walk_command(device, flavor: str, catalog: Path, state: Path, window: int, args, receiver_ip: str) -> list[str]:
    return [sys.executable, str(COLLECTOR / "walk_xpaths.py"), "--device", device.name, "--category", flavor,
            "--catalog", str(catalog), "--state", str(state), "--capture-file", str(MDT_LIVE),
            "--receiver-ip", receiver_ip, "--receiver-port", str(args.receiver_port),
            "--window", str(window), "--idle", "3", "--pace", "0", "--apply"]


def config_match(configured: list[str], results: dict, retry: dict) -> dict:
    """Configured xpaths by walk outcome; a retry result replaces the first one.

    `invalid` means the device rejects the subscription, so the xpath is resolved (it cannot
    stream); `silent` and `unresolved` (crashed, error, not walked yet) are the gaps.
    """
    buckets: dict[str, list[str]] = {"streamed": [], "invalid": [], "silent": [], "unresolved": []}
    for xpath in configured:
        status = (retry.get(xpath) or results.get(xpath) or {}).get("status")
        buckets[status if status in ("streamed", "invalid", "silent") else "unresolved"].append(xpath)
    resolved = len(buckets["streamed"]) + len(buckets["invalid"])
    return {"configured": len(configured), "resolved": resolved,
            "matched_pct": round(100 * resolved / len(configured), 1) if configured else 100.0, **buckets}


def walk_flavor(device, flavor: str, args, receiver_ip: str) -> Optional[dict]:
    """Walk one flavor's pruned catalog; for config flavors, retry silent configured xpaths and
    return the config match."""
    import prune_walk_catalog as prune

    nodes = prune.keep(flavor, device.pid, prune.catalog_nodes(flavor), set())
    catalog = RUN_DIR / f"catalog-{device.pid}-{flavor}.json"
    prune.write_catalog(nodes, catalog)
    state = walk_state_path(device.pid, flavor)
    print(f"  --- walk {flavor}: {len(nodes)} xpaths (pruned catalog {catalog.name})")
    run_logged(walk_command(device, flavor, catalog, state, args.window, args, receiver_ip),
               LOG_DIR / f"walk-{flavor}-{device.pid}.log", COLLECTOR)
    if flavor not in prune.CONFIG_FLAVORS:
        return None

    tree = prune.config_root(device.pid)
    configured = [node["xpath"] for node in nodes if prune.configured(tree, node["xpath"])]
    results = walk_results(state)
    retry_state = walk_state_path(device.pid, flavor, retry=True)
    silent = {xpath for xpath in configured if results.get(xpath, {}).get("status") == "silent"}
    if silent and args.retry_window:
        retry_catalog = RUN_DIR / f"catalog-{device.pid}-{flavor}-retry.json"
        prune.write_catalog([node for node in nodes if node["xpath"] in silent], retry_catalog)
        print(f"  --- retry {len(silent)} configured-but-silent {flavor} xpaths, window {args.retry_window}s")
        run_logged(walk_command(device, flavor, retry_catalog, retry_state, args.retry_window, args, receiver_ip),
                   LOG_DIR / f"walk-{flavor}-retry-{device.pid}.log", COLLECTOR)
    return config_match(configured, results, walk_results(retry_state))


def cmd_walk(args) -> int:
    devices = select_devices(args.devices)
    if not devices:
        print("ERROR: no matching devices in inventory", file=sys.stderr)
        return 2
    if not telegraf_pid():
        print("ERROR: telegraf is not running (kit.py telegraf start)", file=sys.stderr)
        return 2
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    gaps = 0
    for device in devices:
        print(f"\n######## {device.name} ({device.pid}, {device.host})")
        if args.refresh_config or not (OUTPUT / f"config-{device.pid}.json").exists():
            command = [sys.executable, str(COLLECTOR / "config_get.py"), "--device", device.name]
            if run_logged(command, LOG_DIR / f"config-{device.pid}.log", COLLECTOR):
                print("  ! running-config capture failed; skipping this device")
                gaps += 1
                continue
        receiver_ip = args.receiver_ip or local_ip_toward(device.host)
        report = {"pid": device.pid, "name": device.name, "generated": utc_now(), "flavors": {}}
        for flavor in args.flavors:
            match = walk_flavor(device, flavor, args, receiver_ip)
            if match is None:
                continue
            report["flavors"][flavor] = match
            print(f"  {flavor} config match: {match['resolved']}/{match['configured']} ({match['matched_pct']}%) "
                  f"streamed={len(match['streamed'])} invalid={len(match['invalid'])} "
                  f"silent={len(match['silent'])} unresolved={len(match['unresolved'])}")
            gaps += 1 if match["silent"] or match["unresolved"] else 0
        (OUTPUT / f"match-{device.pid}.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    split_mdt()
    return 0 if not gaps else 1


# --------------------------------------------------------------------------- coverage

def mdt_files_for(pid: str) -> list[Path]:
    """Per-device MDT captures for `pid`, including legacy short names (mdt-C9300.json)."""
    from build_live_dataset import pid_from_file

    try:
        inventory_pids = [d.pid for d in inv.load_inventory()]
    except inv.InventoryError:
        inventory_pids = []
    return [f for f in sorted(OUTPUT.glob("mdt-*.json"))
            if f.name != MDT_LIVE.name and ".prev" not in f.name and pid_from_file(f.name, inventory_pids) == pid]


def method_cells(pid: str) -> dict:
    """module -> {method: data|ok|no} for one device, from the raw collector files."""
    import build_protocol_matrix as matrix

    p2m, m2p = matrix.prefix_to_module(), matrix.module_to_prefix()
    grid, _ = matrix.collect()
    cells = {row["module"]: dict(row["cells"]) for (row_pid, _), row in grid.items() if row_pid == pid}
    for mdt_file in mdt_files_for(pid):
        for line in mdt_file.read_text(encoding="utf-8").splitlines():
            try:
                path = json.loads(line).get("tags", {}).get("path", "")
            except json.JSONDecodeError:
                continue
            if path:
                cells.setdefault(matrix.to_module(path, p2m, m2p), {})["mdt"] = "data"
    return cells


def capture_files(device_name: str) -> list[Path]:
    """RESTCONF walk captures (GET categories only; skips crud-backups etc.)."""
    from scripts.harness.spec_paths import GET_CATEGORIES

    device_dir = CAPTURES / device_name
    return [path for category in GET_CATEGORIES for path in sorted((device_dir / category).glob("*.json"))]


def walk_cells(device_name: str) -> dict:
    """module -> data|ok|no from the RESTCONF spec-walk captures (best status per module)."""
    rank = {"data": 3, "ok": 2, "no": 1}
    result: dict[str, str] = {}
    for path in capture_files(device_name):
        module = path.name.split("__", 1)[0]
        try:
            status = json.loads(path.read_text(encoding="utf-8")).get("http_status")
        except (json.JSONDecodeError, OSError):
            continue
        state = {200: "data", 204: "ok"}.get(status, "no")
        if rank[state] > rank.get(result.get(module, ""), 0):
            result[module] = state
    return result


def score_module(cells: dict) -> str:
    states = set(cells.values())
    if "data" in states:
        return "data"
    if "ok" in states:
        return "empty"
    if "no" in states:
        return "unsupported"
    return "not-attempted"


def coverage_for(device, facts: dict, catalog: dict, cells: dict, walk: dict) -> dict:
    advertised = set(facts.get("modules") or [])
    checklist = sorted(m for m in advertised if m in catalog)
    rows = []
    for module in checklist:
        module_cells = dict(cells.get(module, {}))
        if module in walk:
            module_cells["restconf-walk"] = walk[module]
        rows.append({"module": module, "category": catalog[module], "status": score_module(module_cells),
                     "cells": module_cells})
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    present = {kind for kind in RAW_KINDS if kind != "mdt" and (OUTPUT / f"{kind}-{device.pid}.json").exists()}
    if mdt_files_for(device.pid):
        present.add("mdt")
    if walk:
        present.add("restconf-walk")
    missing_methods = [m for m in METHODS if m not in present]
    return {
        "pid": device.pid, "name": device.name, "hostname": facts.get("hostname"), "generated": utc_now(),
        "advertised_modules": len(advertised), "checklist_modules": len(rows),
        "excluded_no_data_nodes": sorted(advertised - set(checklist)),
        "counts": counts, "missing_methods": missing_methods,
        "complete": not missing_methods and counts.get("not-attempted", 0) == 0,
        "rows": rows,
    }


def data_module_catalog(release: str) -> dict:
    """module -> category for every module that holds data: the depth-1 root catalog
    plus each non-RPC release spec (some spec'd modules have no catalog root and
    are reached only by the RESTCONF walk)."""
    from netconf_get import load_roots

    catalog = {}
    for root in load_roots():
        catalog.setdefault(root["module"], root["category"])
    for spec in sorted((REPO / "releases" / release).glob("swagger-*-model/api/*.json")):
        category = spec.parts[-3][len("swagger-"):-len("-model")]
        if category != "rpc" and spec.stem != "manifest" and not spec.stem.startswith("_"):
            catalog.setdefault(spec.stem, category)
    return catalog


def cmd_coverage(args) -> int:
    catalog = data_module_catalog(args.release or default_release())
    facts = load_facts()
    incomplete = 0
    for device in select_devices(args.devices):
        device_facts = facts.get(device.pid)
        if not device_facts:
            print(f"  {device.pid}: no facts yet (kit.py facts)")
            incomplete += 1
            continue
        report = coverage_for(device, device_facts, catalog, method_cells(device.pid), walk_cells(device.name))
        (OUTPUT / f"coverage-{device.pid}.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
        counts = " ".join(f"{k}={v}" for k, v in sorted(report["counts"].items()))
        print(f"  {device.pid:20} {'COMPLETE' if report['complete'] else 'INCOMPLETE':10} "
              f"advertised={report['advertised_modules']} checklist={report['checklist_modules']} {counts}")
        if report["missing_methods"]:
            print(f"  {'':20} missing methods: {', '.join(report['missing_methods'])}")
        incomplete += 0 if report["complete"] else 1
    return 0 if not incomplete else 1


# --------------------------------------------------------------------------- bundle

MDT_FILE_RE = re.compile(r"/output/mdt-[^/]+\.json$")


def device_record(device, facts: dict) -> dict:
    device_facts = facts.get(device.pid, {})
    return {"pid": device.pid, "name": device.name, "hostname": device_facts.get("hostname"),
            "version": device_facts.get("version"), "software_version": device_facts.get("software_version")}


def redact_document(relative: str, text: str) -> str:
    """Mask secret values in raw payloads (collector files keep them unmasked)."""
    from redact_payload import mask_cli, redact_obj, redact_value

    if MDT_FILE_RE.search(relative):
        lines = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue  # truncated write (receiver restart); the dataset builder skips these too
            record["fields"] = redact_obj(record.get("fields") or {})
            lines.append(json.dumps(record, ensure_ascii=False))
        return "\n".join(lines) + "\n"
    document = json.loads(text)
    if isinstance(document, dict):
        for entry in document.get("entries", []) or []:
            for field in ("payload", "sample", "error"):
                if field in entry:
                    entry[field] = redact_value(entry[field])
        if "response" in document:
            document["response"] = redact_obj(document["response"])
        if "show_run" in document:  # config-<PID>.json (config_get.py masks too; this is the backstop)
            document["show_run"] = mask_cli(document["show_run"])
            document["restconf_json"] = redact_obj(document.get("restconf_json") or {})
    return json.dumps(document, ensure_ascii=False)


def bundle_sources(devices: list) -> list[Path]:
    pids = {d.pid for d in devices}
    names = {d.name for d in devices}
    files = []
    for kind in RAW_KINDS + ("facts", "coverage"):
        files += [OUTPUT / f"{kind}-{pid}.json" for pid in sorted(pids)]
    files = [f for f in files if f.exists()]
    for name in sorted(names):
        files += capture_files(name)
        report = ONBOARD_OUT / f"{name}-onboard.json"
        if report.exists():
            files.append(report)
    return files


def literal_secrets() -> list[str]:
    secrets = []
    try:
        secrets.append(inv.load_credentials()[1])
    except inv.CredentialError:
        pass
    community = os.environ.get("IOSXE_SNMP_COMMUNITY")
    if community:
        secrets.append(community)
    return [s for s in secrets if len(s) >= 4]


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def deep_scan(text: str) -> list[tuple[str, str]]:
    """scan_text over the raw file AND every decoded JSON string in it: embedded
    payloads are JSON-escaped, so their secrets are invisible to a raw-text scan."""
    from redact_payload import scan_text

    hits = scan_text(text)
    try:
        documents = [json.loads(text)]
    except json.JSONDecodeError:
        documents = []
        for line in text.splitlines():
            try:
                documents.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    for document in documents:
        for value in _strings(document):
            if '"' in value or "<" in value or "-----BEGIN" in value:
                hits += scan_text(value)
    return hits


def scan_for_secrets(relative: str, text: str, literals: list[str]) -> list[str]:
    hits = [f"{relative}: {label}" for label, _ in deep_scan(text)]
    hits += [f"{relative}: literal credential value" for s in literals if s in text]
    return hits


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _add_member(archive: tarfile.TarFile, relative: str, data: bytes) -> None:
    info = tarfile.TarInfo(f"harness-bundle/{relative}")
    info.size = len(data)
    info.mtime = int(time.time())
    info.mode = 0o644
    archive.addfile(info, io.BytesIO(data))


def build_bundle(devices: list, out_path: Path) -> dict:
    """Stream redacted files into the archive; the manifest is written last. Any
    secret-scan hit deletes the partial archive so nothing unsafe is left behind."""
    literals = literal_secrets()
    entries, hits = {}, []
    out_path.parent.mkdir(parents=True, exist_ok=True)
    partial = out_path.with_name(out_path.name + ".partial")
    logs = sorted(LOG_DIR.glob("*.log")) if LOG_DIR.is_dir() else []
    try:
        with tarfile.open(partial, "w:gz") as archive:
            for source in bundle_sources(devices):
                relative = source.relative_to(REPO).as_posix()
                text = redact_document(relative, source.read_text(encoding="utf-8"))
                hits += scan_for_secrets(relative, text, literals)
                data = text.encode("utf-8")
                entries[relative] = {"sha256": sha256_bytes(data), "bytes": len(data)}
                _add_member(archive, relative, data)
            for log in logs:
                relative = "logs/" + log.name
                data = log.read_bytes()
                hits += [f"{relative}: literal credential value" for s in literals if s.encode() in data]
                entries[relative] = {"sha256": sha256_bytes(data), "bytes": len(data)}
                _add_member(archive, relative, data)
            if hits:
                raise RuntimeError("secret scan failed; no bundle written:\n  " + "\n  ".join(hits[:50]))
            facts = load_facts()
            manifest = {
                "format": BUNDLE_FORMAT, "created": utc_now(), "release": default_release(), "kit": kit_info(),
                "devices": [device_record(d, facts) for d in devices],
                "files": entries,
            }
            _add_member(archive, "manifest.json", json.dumps(manifest, indent=1).encode("utf-8"))
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    partial.replace(out_path)
    return manifest


def cmd_bundle(args) -> int:
    devices = select_devices(args.devices)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = Path(args.out) if args.out else REPO / "dist" / f"harness-bundle-{stamp}.tar.gz"
    try:
        manifest = build_bundle(devices, out_path)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    digest = hashlib.sha256()
    with open(out_path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    print(f"bundle: {out_path} ({out_path.stat().st_size / 1e6:.1f} MB, {len(manifest['files'])} files)")
    print(f"sha256: {digest.hexdigest()}")
    print("Import on the webapp repo: python scripts/import_harness_bundle.py <bundle> [--apply]")
    return 0


# --------------------------------------------------------------------------- main

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    def with_devices(p):
        p.add_argument("--device", action="append", dest="devices", help="Name/PID substring (repeatable)")
        return p

    doctor = with_devices(sub.add_parser("doctor"))
    doctor.add_argument("--release")
    doctor.set_defaults(func=cmd_doctor)

    sub.add_parser("onboard", help="Enable the device APIs; all flags go to onboard.py (onboard --help)")

    with_devices(sub.add_parser("facts")).set_defaults(func=cmd_facts)

    telegraf = sub.add_parser("telegraf")
    telegraf.add_argument("action", choices=["start", "stop", "status"])
    telegraf.add_argument("--port", type=int, default=DEFAULT_MDT_PORT)
    telegraf.set_defaults(func=cmd_telegraf)

    collect = with_devices(sub.add_parser("collect"))
    collect.add_argument("--methods", nargs="+", choices=METHODS, help="Default: all")
    collect.add_argument("--skip", nargs="+", choices=METHODS)
    collect.add_argument("--limit", type=int, default=0, help="Smoke test: first N roots (MDT: per category)")
    collect.add_argument("--release")
    collect.add_argument("--receiver-ip", help="IP devices dial for MDT (default: this host's IP toward each)")
    collect.add_argument("--receiver-port", type=int, default=DEFAULT_MDT_PORT)
    collect.add_argument("--walk-roots-only", action="store_true", help="RESTCONF walk: root containers only")
    collect.add_argument("--timeout", type=int, default=0, help="RESTCONF per-GET timeout (s); e.g. 90 over WAN")
    collect.add_argument("--window", type=int, default=0,
                         help="NETCONF subscribe wait (s) for the first update; e.g. 35 over WAN")
    collect.set_defaults(func=cmd_collect)

    sub.add_parser("split-mdt").set_defaults(func=cmd_split_mdt)

    walk = with_devices(sub.add_parser("walk", help="Config-driven per-xpath MDT walk (resumable)"))
    walk.add_argument("--flavors", nargs="+", choices=["native-config", "cfg", "oper"],
                      default=["native-config", "cfg", "oper"])
    walk.add_argument("--window", type=int, default=10, help="Seconds to wait for data per xpath")
    walk.add_argument("--retry-window", type=int, default=60,
                      help="Longer wait for configured xpaths that stayed silent (0 = no retry)")
    walk.add_argument("--refresh-config", action="store_true", help="Re-capture the running config first")
    walk.add_argument("--receiver-ip", help="IP devices dial for MDT (default: this host's IP toward each)")
    walk.add_argument("--receiver-port", type=int, default=DEFAULT_MDT_PORT)
    walk.set_defaults(func=cmd_walk)

    coverage = with_devices(sub.add_parser("coverage"))
    coverage.add_argument("--release")
    coverage.set_defaults(func=cmd_coverage)

    bundle = with_devices(sub.add_parser("bundle"))
    bundle.add_argument("--out", help="Default: dist/harness-bundle-<UTC>.tar.gz")
    bundle.set_defaults(func=cmd_bundle)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["onboard"]:
        # Hand every flag to onboard.py untouched (argparse REMAINDER drops leading options).
        from scripts.harness import onboard

        return onboard.main(argv[1:])
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (inv.InventoryError, inv.CredentialError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
