#!/usr/bin/env python3
"""
collect_fleet.py — batched, self-cleaning MDT collection across the fleet.

Enumerates subscribable xpaths from the committed release specs (all model
categories), then for each device: pushes them in small batches over SSH as
periodic telemetry subscriptions pointed at the local Telegraf receiver, waits a
short capture window so a payload streams, then REMOVES the batch. Invalid
xpaths simply never stream (self-pruning). Telegraf tags every payload with the
device `source` + `path`, so build_live_dataset.py can assemble a per-device,
per-category dataset afterwards.

Safety
------
Config changes are gated behind --apply (default: dry run — prints the plan).
Every subscription this tool adds is removed again: after each batch's capture
window, and in a finally block per device if anything goes wrong. Subscription
IDs live in a high range (900000+) so they never collide with existing subs, and
nothing is written to startup-config (running-config only; a reload would clear
any stragglers).

Usage
-----
  # Dry run — show what Phase 1 (top level, all categories) would push:
  .venv-harness/bin/python collect_fleet.py --depth 1

  # Phase 1 live, capped sample, all six devices:
  .venv-harness/bin/python collect_fleet.py --depth 1 --per-cat-cap 8 --apply

  # Phase 2 (add 2nd level), specific devices:
  .venv-harness/bin/python collect_fleet.py --depth 2 --devices C9300 C9800 --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import yaml

# Reuse the spec enumeration from the sibling module.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from enumerate_xpaths import (  # noqa: E402
    CATEGORY_DIRS, prefix_map, xpath_from_restconf, depth_after_prefix,
)

REPO = Path(__file__).resolve().parents[3]
ENV = REPO / "scripts" / "harness" / ".env"
INV = REPO / "scripts" / "harness" / "inventory.json"
OUT_DIR = Path(__file__).resolve().parent / "output"

BASE_SUB_ID = 900000
DEFAULT_RECEIVER_IP = "10.85.134.200"
DEFAULT_RECEIVER_PORT = 57500
MDT_OUT = OUT_DIR / "mdt-live.json"


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return sum(1 for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip())
    except OSError:
        return 0


def wait_for_idle(baseline: int, idle_sec: int, max_sec: int) -> int:
    """Wait until the receiver stops writing new records for `idle_sec` seconds
    (the periodic snapshot has fully streamed), capped at `max_sec`. IOS XE emits
    the first full payload immediately on subscription establishment, so a large
    period means one complete snapshot then silence — we only wait for it to go
    quiet, not for the whole period. Returns records captured since baseline."""
    start = time.time()
    last_count = count_lines(MDT_OUT)
    last_change = time.time()
    while time.time() - start < max_sec:
        time.sleep(2)
        c = count_lines(MDT_OUT)
        if c > last_count:
            last_count = c
            last_change = time.time()
        elif c > baseline and (time.time() - last_change) >= idle_sec:
            break
    return last_count - baseline


def load_env():
    env = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def load_devices(selectors):
    devs = json.loads(INV.read_text(encoding="utf-8"))
    if not selectors:
        return devs
    out = []
    for sel in selectors:
        for d in devs:
            if sel.lower() in d["name"].lower() or sel.lower() in d.get("pid", "").lower():
                if d not in out:
                    out.append(d)
    return out


def enumerate_candidates(version, categories, depth_min, depth_max, per_cat_cap):
    """Return ordered [(index, category, xpath)] with a stable global index."""
    pmap = prefix_map(version)
    base = REPO / "releases" / version
    ordered = []
    for cat in categories:
        d = CATEGORY_DIRS.get(cat)
        if not d:
            continue
        api = base / d / "api"
        if not api.is_dir():
            continue
        seen = set()
        for spec in sorted(api.glob("*.json")):
            try:
                doc = json.loads(spec.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            for path in doc.get("paths", {}):
                if "{" in path:
                    continue
                xp = xpath_from_restconf(path, pmap)
                if not xp:
                    continue
                depth = depth_after_prefix(xp)
                if depth_min <= depth <= depth_max and xp not in seen:
                    seen.add(xp)
        cat_xpaths = sorted(seen)
        if per_cat_cap:
            cat_xpaths = cat_xpaths[:per_cat_cap]
        for xp in cat_xpaths:
            ordered.append((len(ordered), cat, xp))
    return ordered


def sub_lines(sub_id, xpath, period_cs, rx_ip, rx_port, source_vrf=None, source_addr=None):
    lines = [
        f"telemetry ietf subscription {sub_id}",
        " encoding encode-kvgpb",
        f" filter xpath {xpath}",
        " stream yang-push",
        f" update-policy periodic {period_cs}",
    ]
    if source_vrf:
        lines.append(f" source-vrf {source_vrf}")
    if source_addr:
        lines.append(f" source-address {source_addr}")
    lines.append(f" receiver ip address {rx_ip} {rx_port} protocol grpc-tcp")
    return lines


def _ping_ok(conn, target, vrf=None):
    cmd = f"ping vrf {vrf} {target} repeat 2 timeout 1" if vrf else f"ping {target} repeat 2 timeout 1"
    try:
        out = conn.send_command(cmd, read_timeout=20)
    except Exception:
        return False
    return ("Success rate is" in out) and ("Success rate is 0 percent" not in out)


def detect_vrf(conn, target):
    """Return (vrf_or_None, reachable). Global first (None), then Mgmt-vrf."""
    if _ping_ok(conn, target, None):
        return None, True
    if _ping_ok(conn, target, "Mgmt-vrf"):
        return "Mgmt-vrf", True
    return None, False


def device_cpu(conn):
    """1-minute control-plane CPU %, or None if the device is unresponsive.
    A burst of large streaming snapshots can spike CPU and starve the mgmt
    plane, so we gate each batch on this."""
    try:
        out = conn.send_command("show processes cpu | include one minute", read_timeout=20)
    except Exception:
        return None
    m = re.search(r"one minute:\s*(\d+)%", out)
    return int(m.group(1)) if m else 0


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def category_from_xpath(xpath: str) -> str:
    pfx = xpath.lstrip("/").split(":", 1)[0].lower()
    if pfx.startswith("openconfig") or pfx.startswith("oc-"):
        return "openconfig"
    if pfx.startswith("ietf"):
        return "ietf"
    if "native" in pfx:
        return "native-config"
    if pfx.endswith("-cfg") or pfx.endswith("-config"):
        return "cfg"
    if "oper" in pfx:
        return "oper"
    return "other"


def load_bundle_xpaths():
    """Proven-streaming xpaths from the bundle's canonical subscription sets."""
    out = []
    for name in ("subscriptions.yaml", "subscriptions-wlc.yaml"):
        f = REPO / "scripts" / "mdt-telemetry" / "harness" / "validation" / name
        if not f.exists():
            continue
        doc = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        for sub in (doc.get("subscriptions") or {}).values():
            xp = sub.get("xpath")
            if xp:
                out.append((category_from_xpath(xp), xp))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="26.1.1")
    ap.add_argument("--depth", type=int, default=1, help="Max xpath depth (1=top level, 2=+2nd level).")
    ap.add_argument("--depth-min", type=int, default=1)
    ap.add_argument("--categories", nargs="+",
                    default=["oper", "openconfig", "native-config", "cfg", "ietf", "other"])
    ap.add_argument("--per-cat-cap", type=int, default=0, help="Cap xpaths per category (0 = no cap).")
    ap.add_argument("--include-bundle", action="store_true",
                    help="Seed with the bundle's proven-streaming xpaths (subscriptions*.yaml) first.")
    ap.add_argument("--exclude", nargs="+", default=None,
                    help="Skip xpaths containing any of these substrings (e.g. appqoe app-hosting).")
    ap.add_argument("--devices", nargs="+", help="Device name/PID substrings (default: all in inventory).")
    ap.add_argument("--receiver-ip", default=DEFAULT_RECEIVER_IP)
    ap.add_argument("--receiver-port", type=int, default=DEFAULT_RECEIVER_PORT)
    ap.add_argument("--batch-size", type=int, default=5,
                    help="Subscriptions per batch. Keep SMALL: large bursts of streaming "
                         "snapshots can overwhelm a device's control plane.")
    ap.add_argument("--pace", type=int, default=4, help="Seconds to pause between batches.")
    ap.add_argument("--max-cpu", type=int, default=70,
                    help="Back off/abort if the device's 1-minute control-plane CPU reaches this %%.")
    ap.add_argument("--period-cs", type=int, default=30000,
                    help="Periodic interval (centiseconds). Large by default: IOS XE sends the "
                         "first full payload immediately, so one clean snapshot then silence.")
    ap.add_argument("--idle", type=int, default=4,
                    help="Stop a batch's capture after this many seconds with no new records.")
    ap.add_argument("--window", type=int, default=45,
                    help="Max seconds to wait for a batch's snapshot before removing it.")
    ap.add_argument("--source-vrf", default="auto",
                    help="'auto' (ping-detect global vs Mgmt-vrf), 'global', or a VRF name.")
    ap.add_argument("--apply", action="store_true", help="Actually push (default: dry run).")
    args = ap.parse_args()

    candidates = enumerate_candidates(args.version, args.categories, args.depth_min, args.depth, args.per_cat_cap)
    # Optionally seed with proven-good bundle xpaths, but only within the
    # selected categories (keeps a single-category run strictly that category).
    if args.include_bundle:
        cats = set(args.categories)
        seen = set()
        pairs = []
        for cat, xp in load_bundle_xpaths():
            if cat in cats and xp not in seen:
                seen.add(xp)
                pairs.append((cat, xp))
        for _, cat, xp in candidates:
            if xp not in seen:
                seen.add(xp)
                pairs.append((cat, xp))
    else:
        pairs = [(cat, xp) for _, cat, xp in candidates]
    # Quarantine known crashers / anything the caller wants to skip.
    if args.exclude:
        ex = [s.lower() for s in args.exclude]
        pairs = [(c, x) for c, x in pairs if not any(s in x.lower() for s in ex)]
    candidates = [(i, c, x) for i, (c, x) in enumerate(pairs)]
    devices = load_devices(args.devices)

    by_cat = {}
    for _, cat, _ in candidates:
        by_cat[cat] = by_cat.get(cat, 0) + 1
    print(f"Candidates: {len(candidates)} xpaths (depth {args.depth_min}..{args.depth}) "
          f"across {len(args.categories)} categories -> {by_cat}")
    print(f"Devices: {', '.join(d['pid'] for d in devices)}")
    print(f"Receiver: {args.receiver_ip}:{args.receiver_port}  batch={args.batch_size} "
          f"period={args.period_cs}cs window={args.window}s")

    # Persist the sub-id -> xpath plan so the dataset builder can map/verify.
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plan = {
        "receiver": f"{args.receiver_ip}:{args.receiver_port}",
        "period_cs": args.period_cs,
        "depth": args.depth,
        "categories": args.categories,
        "xpaths": [{"sub_id": BASE_SUB_ID + idx, "category": cat, "xpath": xp}
                   for idx, cat, xp in candidates],
        "source_pid": {d["name"]: d["pid"] for d in devices},
    }
    (OUT_DIR / "fleet-plan.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")

    if not args.apply:
        print("\n(dry run — pass --apply to push, capture, and clean up)")
        print("Example batch for first device:")
        for idx, cat, xp in candidates[:3]:
            for ln in sub_lines(BASE_SUB_ID + idx, xp, args.period_cs, args.receiver_ip, args.receiver_port):
                print("  " + ln)
        return 0

    from netmiko import ConnectHandler
    env = load_env()
    summary = []

    for dev in devices:
        print(f"\n=== {dev['pid']} ({dev['host']}) ===")
        params = {
            "device_type": "cisco_xe", "host": dev["host"],
            "username": env["IOSXE_USER"], "password": env["IOSXE_PASS"],
            "secret": env["IOSXE_PASS"], "port": 22, "fast_cli": False, "conn_timeout": 25,
        }
        added_ids = []
        pushed = 0
        conn = None
        try:
            conn = ConnectHandler(**params)
            try:
                conn.enable()
            except Exception:
                pass
            # Decide how this device must reach the collector.
            if args.source_vrf == "auto":
                vrf, reachable = detect_vrf(conn, args.receiver_ip)
                if not reachable:
                    print(f"  ! {args.receiver_ip} unreachable from {dev['pid']} (global or Mgmt-vrf) — skipping.")
                    summary.append((dev["pid"], 0, "unreachable"))
                    conn.disconnect()
                    continue
            elif args.source_vrf in ("global", "", "none"):
                vrf = None
            else:
                vrf = args.source_vrf
            src_addr = dev["host"]
            print(f"  path: {'Mgmt-vrf' if vrf else 'global'} (source-address {src_addr})")
            for batch in chunks(candidates, args.batch_size):
                # Health gate: never push into a device whose control plane is
                # already loaded (this is what protects the mgmt plane).
                cpu = device_cpu(conn)
                if cpu is None:
                    raise RuntimeError("device health check failed (unresponsive) — aborting to protect it")
                if cpu >= args.max_cpu:
                    print(f"  ! control-plane CPU {cpu}% >= {args.max_cpu}% — waiting {args.pace * 3}s")
                    time.sleep(args.pace * 3)
                    if (device_cpu(conn) or 100) >= args.max_cpu:
                        raise RuntimeError(f"control-plane CPU stayed high — aborting to protect {dev['pid']}")
                lines, batch_ids = [], []
                for idx, cat, xp in batch:
                    sid = BASE_SUB_ID + idx
                    lines += sub_lines(sid, xp, args.period_cs, args.receiver_ip, args.receiver_port,
                                       source_vrf=vrf, source_addr=src_addr)
                    batch_ids.append(sid)
                conn.send_config_set(lines, read_timeout=90)
                added_ids.extend(batch_ids)
                pushed += len(batch_ids)
                baseline = count_lines(MDT_OUT)
                got = wait_for_idle(baseline, args.idle, args.window)
                print(f"  pushed {len(batch_ids)} subs (total {pushed}/{len(candidates)}); "
                      f"captured {got} record(s) then idle [cpu {cpu}%].")
                # Remove this batch before the next one, then pace.
                remove = [f"no telemetry ietf subscription {sid}" for sid in batch_ids]
                conn.send_config_set(remove, read_timeout=90)
                for sid in batch_ids:
                    if sid in added_ids:
                        added_ids.remove(sid)
                time.sleep(args.pace)
            print(f"  done: pushed {pushed} subscriptions, all removed.")
            summary.append((dev["pid"], pushed, "ok"))
        except Exception as exc:
            summary.append((dev["pid"], pushed, f"ERROR: {exc}"))
            print(f"  ! {exc}")
        finally:
            if conn is not None:
                if added_ids:  # cleanup any stragglers from a mid-batch failure
                    try:
                        conn.send_config_set([f"no telemetry ietf subscription {sid}" for sid in added_ids],
                                             read_timeout=90)
                        print(f"  cleaned up {len(added_ids)} straggler sub(s).")
                    except Exception as exc:
                        print(f"  ! straggler cleanup failed: {exc}")
                try:
                    conn.disconnect()
                except Exception:
                    pass

    print("\n" + "=" * 50)
    for pid, n, res in summary:
        print(f"  {pid:12} pushed={n:5}  {res}")
    print("Now build the dataset:  build_live_dataset.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
