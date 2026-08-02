#!/usr/bin/env python3
"""recapture.py — FAST MDT re-capture using the known-streaming manifest.

The exhaustive walk is a one-time *discovery* cost. Once we know which xpaths
stream (build_streaming_manifest.py), refreshing the data after a config or
topology change does NOT need another walk: we simply re-subscribe each device's
known-good set in a few batches, let one snapshot stream, and tear it down.
Whole fleet ~= minutes.

Flow per device (‑‑apply):
  1. (‑‑fresh) truncate the per-device capture file + restart Telegraf so the
     new snapshot isn't mixed with stale values.
  2. Connect, auto-detect transport VRF, then push the manifest xpaths in
     CPU-gated batches (they are all known-valid, so nothing is wasted).
  3. wait_for_idle → one full snapshot streams to Telegraf → remove the subs.
Then run build_live_dataset.py to rebuild telemetry-live-data.json.

    # dry run (default) — show the plan, touch nothing:
    python3 recapture.py
    # real refresh of the whole fleet:
    python3 recapture.py --fresh --apply
    # just one device:
    python3 recapture.py --devices C9500 --fresh --apply
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

# Reuse the battle-tested helpers from the fleet collector.
from collect_fleet import (  # noqa: E402
    BASE_SUB_ID, DEFAULT_RECEIVER_IP, DEFAULT_RECEIVER_PORT, OUT_DIR,
    chunks, detect_vrf, device_cpu, load_devices, load_env, sub_lines, wait_for_idle,
)

MANIFEST = OUT_DIR / "streaming-manifest.json"
TELEGRAF_CONTAINER = "mdt-telegraf"


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def refresh_capture_file(pid: str) -> None:
    """Start the device's capture file from empty so the rebuild sees only the
    fresh snapshot (Telegraf reopens the file on restart)."""
    f = OUT_DIR / f"mdt-{pid}.json"
    try:
        f.write_text("", encoding="utf-8")
    except OSError:
        pass


def _depth(xpath: str) -> int:
    return xpath.lstrip("/").count("/") + 1


def select_xpaths(entries: list, which: str) -> list:
    """Pick the subscription subset. Subscribing a container streams its whole
    subtree, so 'roots' (no streaming parent) already yields ~100% coverage."""
    if which == "roots":
        picked = [e for e in entries if e.get("root")]
        if picked:
            return [e["xpath"] for e in picked]
        which = "phase1"  # manifest predates root flags -> fall back to top-level
    if which == "phase1":
        return [e["xpath"] for e in entries if _depth(e["xpath"]) == 1]
    if which == "phase2":
        return [e["xpath"] for e in entries if _depth(e["xpath"]) <= 2]
    return [e["xpath"] for e in entries]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=str(MANIFEST))
    ap.add_argument("--set", dest="which", choices=["roots", "phase1", "phase2", "all"], default="roots",
                    help="Subscription subset: roots (minimal, ~100%% via subtree streaming; default), "
                         "phase1 (top-level only, ~99%%), phase2 (<=2nd level), all (every streaming xpath).")
    ap.add_argument("--devices", nargs="+", help="Device name/PID substrings (default: all in manifest).")
    ap.add_argument("--receiver-ip", default=DEFAULT_RECEIVER_IP)
    ap.add_argument("--receiver-port", type=int, default=DEFAULT_RECEIVER_PORT)
    ap.add_argument("--batch-size", type=int, default=20,
                    help="Subscriptions per batch. Manifest xpaths are all known-valid, "
                         "so this can be larger than discovery's; still CPU-gated.")
    ap.add_argument("--pace", type=int, default=3, help="Seconds between batches.")
    ap.add_argument("--max-cpu", type=int, default=70, help="Back off if 1-min control-plane CPU hits this %%.")
    ap.add_argument("--period-cs", type=int, default=30000,
                    help="Periodic interval (cs). Large: IOS XE sends the first full payload immediately.")
    ap.add_argument("--idle", type=int, default=4, help="Stop a batch's capture after this many idle seconds.")
    ap.add_argument("--window", type=int, default=45, help="Max seconds to wait for a batch's snapshot.")
    ap.add_argument("--source-vrf", default="auto", help="'auto', 'global', or a VRF name.")
    ap.add_argument("--fresh", action="store_true",
                    help="Truncate per-device capture files + restart Telegraf first (recommended for a "
                         "true refresh so new values don't mix with stale ones).")
    ap.add_argument("--apply", action="store_true", help="Actually push (default: dry run).")
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    man_devs = manifest.get("devices", {})

    def manifest_key(pid: str):
        """Map an inventory PID (e.g. 'C9300-24UX') to its manifest key
        (e.g. 'C9300'), tolerating either being a substring of the other."""
        if pid in man_devs:
            return pid
        for k in man_devs:
            if k in pid or pid in k:
                return k
        return None

    devices = [d for d in load_devices(args.devices) if manifest_key(d["pid"])]

    print(f"Manifest: {sum(len(v) for v in man_devs.values()):,} streaming xpaths  |  set={args.which}")
    for d in devices:
        n = len(select_xpaths(man_devs.get(manifest_key(d['pid']), []), args.which))
        print(f"  {d['pid']:14} {n:5,} xpaths -> re-subscribe")
    print(f"Receiver: {args.receiver_ip}:{args.receiver_port}  batch={args.batch_size} "
          f"period={args.period_cs}cs window={args.window}s  fresh={args.fresh}")

    if not args.apply:
        print("\n(dry run — pass --apply to refresh; --fresh also clears stale capture first)")
        print("Then rebuild:  python3 build_live_dataset.py")
        return 0

    if args.fresh:
        for d in devices:
            refresh_capture_file(d["pid"])
        print(f"\nRestarting Telegraf ({TELEGRAF_CONTAINER}) for a clean capture...")
        subprocess.run(["docker", "restart", TELEGRAF_CONTAINER], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)

    from netmiko import ConnectHandler
    env = load_env()
    summary = []
    for dev in devices:
        pid = dev["pid"]
        xpaths = select_xpaths(man_devs.get(manifest_key(pid), []), args.which)
        print(f"\n=== {pid} ({dev['host']}) — {len(xpaths):,} xpaths ===")
        params = {
            "device_type": "cisco_xe", "host": dev["host"],
            "username": env["IOSXE_USER"], "password": env["IOSXE_PASS"],
            "secret": env["IOSXE_PASS"], "port": 22, "fast_cli": False, "conn_timeout": 25,
        }
        conn = None
        pushed = 0
        try:
            conn = ConnectHandler(**params)
            try:
                conn.enable()
            except Exception:
                pass
            if args.source_vrf == "auto":
                vrf, reachable = detect_vrf(conn, args.receiver_ip)
                if not reachable:
                    print(f"  ! {args.receiver_ip} unreachable from {pid} — skipping.")
                    summary.append((pid, 0, "unreachable"))
                    conn.disconnect()
                    continue
            elif args.source_vrf in ("global", "", "none"):
                vrf = None
            else:
                vrf = args.source_vrf
            print(f"  path: {'Mgmt-vrf' if vrf else 'global'} (source-address {dev['host']})")

            indexed = list(enumerate(xpaths))
            for batch in chunks(indexed, args.batch_size):
                cpu = device_cpu(conn)
                if cpu is None:
                    raise RuntimeError("device health check failed — aborting to protect it")
                if cpu >= args.max_cpu:
                    print(f"  ! CPU {cpu}% >= {args.max_cpu}% — waiting {args.pace * 3}s")
                    time.sleep(args.pace * 3)
                lines, ids = [], []
                for idx, xp in batch:
                    sid = BASE_SUB_ID + idx
                    lines += sub_lines(sid, xp, args.period_cs, args.receiver_ip, args.receiver_port,
                                       source_vrf=vrf, source_addr=dev["host"])
                    ids.append(sid)
                from collect_fleet import count_lines, MDT_OUT
                baseline = count_lines(MDT_OUT)
                conn.send_config_set(lines, read_timeout=60)
                pushed += len(ids)
                wait_for_idle(baseline, args.idle, args.window)
                conn.send_config_set([f"no telemetry ietf subscription {sid}" for sid in ids], read_timeout=60)
                time.sleep(args.pace)
            summary.append((pid, pushed, "ok"))
        except Exception as e:  # noqa: BLE001
            summary.append((pid, pushed, f"error: {e}"))
        finally:
            if conn is not None:
                try:
                    conn.disconnect()
                except Exception:
                    pass

    print("\n=== re-capture summary ===")
    for pid, n, st in summary:
        print(f"  {pid:14} pushed {n:5,}  {st}")
    print("\nNow rebuild:  python3 build_live_dataset.py   (then build_restconf_dataset.py + push)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
