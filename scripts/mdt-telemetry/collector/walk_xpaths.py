#!/usr/bin/env python3
"""
walk_xpaths.py — exhaustive, crash-isolating, RESUMABLE MDT discovery.

Walks the container/list catalog (subscribable-nodes.json) ONE xpath at a time
so every result is unambiguous, checkpoints after each xpath, and survives
device reloads (waits for recovery, then continues past the offending xpath).
Designed to run overnight and be stopped/resumed until complete.

Per xpath it records one of:
  streamed  — subscription valid and the device sent >=1 payload
  silent    — subscription valid but no data (feature not configured / empty)
  invalid   — device rejected the subscription (bad/again-unsupported xpath)
  crashed   — the device went unreachable right after this xpath (prime suspect)
  error     — transient issue (retried on the next run)

State is a JSON checkpoint (output/walk-<device>.json). Re-running resumes:
already-resolved xpaths are skipped; 'error' xpaths are retried; 'crashed' ones
are skipped by default (use --retry-crashers to re-test).

Usage:
  # Dry run — how many xpaths, resume status:
  .venv-harness/bin/python walk_xpaths.py --device C9300 --category oper

  # Run (overnight-safe; Ctrl-C to pause, re-run to resume):
  .venv-harness/bin/python walk_xpaths.py --device C9300 --category oper --apply
  .venv-harness/bin/python walk_xpaths.py --device C9300 --apply   # all flavors
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from collect_fleet import (  # noqa: E402  (reuse the proven helpers)
    count_lines, wait_for_idle, detect_vrf, device_cpu, sub_lines,
    load_env, load_devices, MDT_OUT, DEFAULT_RECEIVER_IP, DEFAULT_RECEIVER_PORT,
)

CATALOG = HERE / "output" / "subscribable-nodes.json"
WALK_SUB_ID = 900001            # single reused id (one-at-a-time)
TERMINAL = {"streamed", "silent", "invalid", "crashed"}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------- reachability ----------

def device_up(host, port=22, timeout=4):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def wait_reachable(host, max_wait, interval=15):
    """Block until the device's SSH is back (post-reload) or max_wait elapses."""
    deadline = time.time() + max_wait
    while time.time() < deadline:
        if device_up(host):
            time.sleep(interval)  # settle after ssh opens
            return True
        time.sleep(interval)
    return device_up(host)


# ---------- candidates / state ----------

def load_candidates(catalog_path, category, max_depth, include=None, exclude=None):
    cat = json.loads(Path(catalog_path).read_text(encoding="utf-8"))

    def catof(xp):
        p = xp.lstrip("/").split(":", 1)[0].lower()
        if p.startswith(("openconfig", "oc-")):
            return "openconfig"
        if p.startswith("ietf"):
            return "ietf"
        if "native" in p:
            return "native-config"
        if p.endswith(("-cfg", "-config")):
            return "cfg"
        if "oper" in p:
            return "oper"
        return "other"

    out = []
    for module, nodes in cat["modules"].items():
        for n in nodes:
            if max_depth and n["depth"] > max_depth:
                continue
            if category:
                # Prefer the catalog's authoritative category (from the model
                # directory); fall back to the prefix heuristic for old catalogs.
                ncat = n.get("category") or catof(n["xpath"])
                if ncat != category:
                    continue
            out.append(n["xpath"])
    if include:
        inc = [s.lower() for s in include]
        out = [x for x in out if any(s in x.lower() for s in inc)]
    if exclude:
        ex = [s.lower() for s in exclude]
        out = [x for x in out if not any(s in x.lower() for s in ex)]
    return out


def load_state(path, device, receiver):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"device": device, "receiver": receiver, "started": now(),
            "updated": now(), "results": {}, "crashers": []}


def save_state(path, state):
    state["updated"] = now()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1), encoding="utf-8")
    tmp.replace(path)


# ---------- one xpath test ----------

class Crash(Exception):
    pass


def connect(dev, env):
    from netmiko import ConnectHandler
    conn = ConnectHandler(device_type="cisco_xe", host=dev["host"], username=env["IOSXE_USER"],
                          password=env["IOSXE_PASS"], secret=env["IOSXE_PASS"], port=22,
                          fast_cli=True, conn_timeout=25)
    try:
        conn.enable()
    except Exception:
        pass
    return conn


def test_xpath(conn, host, xp, vrf, src, args):
    """Return (status, records). Raise Crash if the device dies on this xpath."""
    capture = Path(args.capture_file)
    lines = sub_lines(WALK_SUB_ID, xp, args.period_cs, args.receiver_ip, args.receiver_port,
                      source_vrf=vrf, source_addr=src)
    baseline = count_lines(capture)
    try:
        conn.send_config_set(lines, read_timeout=90)
    except Exception:
        if not device_up(host):
            raise Crash()
        raise
    # Is the subscription valid?
    try:
        st = conn.send_command(f"show telemetry ietf subscription {WALK_SUB_ID}", read_timeout=30)
    except Exception:
        if not device_up(host):
            raise Crash()
        st = ""
    if "Invalid" in st and "Valid" not in st:
        _remove(conn, host)
        return "invalid", 0
    got = wait_idle(capture, baseline, args.idle, args.window)
    _remove(conn, host)
    return ("streamed" if got > 0 else "silent"), got


def _remove(conn, host):
    try:
        conn.send_config_set([f"no telemetry ietf subscription {WALK_SUB_ID}"], read_timeout=90)
    except Exception:
        if not device_up(host):
            raise Crash()


def wait_idle(capture, baseline, idle_sec, max_sec):
    """Idle-detect against THIS device's own capture file (parallel-safe)."""
    start = time.time()
    last = count_lines(capture)
    last_change = time.time()
    while time.time() - start < max_sec:
        time.sleep(2)
        c = count_lines(capture)
        if c > last:
            last = c
            last_change = time.time()
        elif c > baseline and (time.time() - last_change) >= idle_sec:
            break
    return last - baseline


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--device", default="C9300")
    ap.add_argument("--category", default=None, help="Limit to one flavor (oper, openconfig, native-config, cfg, ietf, other).")
    ap.add_argument("--max-depth", type=int, default=0, help="Limit xpath depth (0 = all depths).")
    ap.add_argument("--catalog", default=str(CATALOG),
                    help="Node catalog JSON (default subscribable-nodes.json; use mib-nodes.json for MIBs).")
    ap.add_argument("--include", nargs="+", default=None,
                    help="Keep only xpaths containing one of these substrings (e.g. wireless).")
    ap.add_argument("--exclude", nargs="+", default=None,
                    help="Skip xpaths containing any of these substrings (e.g. known crashers appqoe lldp).")
    ap.add_argument("--receiver-ip", default=DEFAULT_RECEIVER_IP)
    ap.add_argument("--receiver-port", type=int, default=DEFAULT_RECEIVER_PORT)
    ap.add_argument("--capture-file", default=str(MDT_OUT),
                    help="Telegraf output for THIS device's receiver (isolate per device when parallel).")
    ap.add_argument("--period-cs", type=int, default=30000)
    ap.add_argument("--idle", type=int, default=4)
    ap.add_argument("--window", type=int, default=30)
    ap.add_argument("--pace", type=float, default=1.0, help="Seconds between xpaths.")
    ap.add_argument("--recover-timeout", type=int, default=900, help="Max seconds to wait for a reload to recover.")
    ap.add_argument("--max-cpu", type=int, default=85, help="Wait if 1-min control-plane CPU is at/above this.")
    ap.add_argument("--retry-crashers", action="store_true", help="Re-test xpaths previously marked crashed.")
    ap.add_argument("--limit", type=int, default=0, help="Process at most N xpaths this run (0 = no limit).")
    ap.add_argument("--state", default=None, help="Checkpoint file (default: output/walk-<device>.json).")
    ap.add_argument("--apply", action="store_true", help="Actually push (default: dry run / status only).")
    args = ap.parse_args()

    dev = load_devices([args.device])
    if not dev:
        sys.exit(f"device {args.device!r} not in inventory")
    dev = dev[0]
    receiver = f"{args.receiver_ip}:{args.receiver_port}"
    state_path = Path(args.state) if args.state else HERE / "output" / f"walk-{dev['pid']}.json"

    candidates = load_candidates(args.catalog, args.category, args.max_depth, args.include, args.exclude)
    state = load_state(state_path, dev["pid"], receiver)
    results = state["results"]

    def resolved(xp):
        r = results.get(xp)
        if not r:
            return False
        if r["status"] == "crashed" and args.retry_crashers:
            return False
        if r["status"] == "error":
            return False  # retry transient errors
        return r["status"] in TERMINAL

    pending = [x for x in candidates if not resolved(x)]
    done = len(candidates) - len(pending)
    tally = {}
    for r in results.values():
        tally[r["status"]] = tally.get(r["status"], 0) + 1
    print(f"device={dev['pid']} category={args.category or 'ALL'} max_depth={args.max_depth or 'all'}")
    print(f"catalog={len(candidates)}  resolved={done}  pending={len(pending)}  state={state_path.name}")
    print(f"so far: {tally}")
    if state.get("crashers"):
        print(f"crashers so far ({len(state['crashers'])}): {state['crashers']}")

    if not args.apply:
        print("\n(dry run — pass --apply to walk & capture; Ctrl-C to pause, re-run to resume)")
        return 0
    if not pending:
        print("\nNothing pending — walk complete for this scope.")
        return 0

    env = load_env()
    processed = 0
    conn = None
    vrf = None

    def ensure_conn():
        nonlocal conn, vrf
        if conn is not None:
            return
        if not wait_reachable(dev["host"], args.recover_timeout):
            raise SystemExit(f"device {dev['pid']} not reachable within {args.recover_timeout}s — stopping.")
        conn = connect(dev, env)
        vrf, ok = detect_vrf(conn, args.receiver_ip)
        if not ok:
            raise SystemExit(f"{args.receiver_ip} unreachable from {dev['pid']} (global/Mgmt-vrf) — stopping.")
        print(f"  [connected; path={'Mgmt-vrf' if vrf else 'global'}]")

    try:
        ensure_conn()
        for xp in pending:
            if args.limit and processed >= args.limit:
                print(f"\n--limit {args.limit} reached; re-run to continue.")
                break
            # CPU guard (best effort).
            cpu = device_cpu(conn)
            if cpu is not None and cpu >= args.max_cpu:
                print(f"  [cpu {cpu}% high; waiting]")
                time.sleep(args.pace * 5)
            try:
                status, recs = test_xpath(conn, dev["host"], xp, vrf, dev["host"], args)
                results[xp] = {"status": status, "records": recs, "cpu": cpu, "ts": now()}
                mark = {"streamed": "\u2713", "silent": "\u00b7", "invalid": "\u2717"}.get(status, "?")
                print(f"  [{done + processed + 1}/{len(candidates)}] {mark} {status:8} {recs:>4}  {xp}")
            except Crash:
                results[xp] = {"status": "crashed", "records": 0, "cpu": cpu, "ts": now()}
                if xp not in state["crashers"]:
                    state["crashers"].append(xp)
                print(f"  [{done + processed + 1}/{len(candidates)}] !!! CRASHED -> {xp}")
                save_state(state_path, state)
                # Wait for the reload to recover, then reconnect and continue.
                try:
                    conn.disconnect()
                except Exception:
                    pass
                conn = None
                print(f"  waiting up to {args.recover_timeout}s for {dev['pid']} to recover…")
                ensure_conn()
            except Exception as exc:
                results[xp] = {"status": "error", "records": 0, "ts": now(), "detail": str(exc)[:120]}
                print(f"  [{done + processed + 1}/{len(candidates)}] error {xp}: {str(exc)[:80]}")
                # Reconnect defensively.
                try:
                    conn.disconnect()
                except Exception:
                    pass
                conn = None
                ensure_conn()
            processed += 1
            save_state(state_path, state)
            time.sleep(args.pace)
    except KeyboardInterrupt:
        print("\n[paused] checkpoint saved — re-run to resume.")
    finally:
        save_state(state_path, state)
        if conn is not None:
            try:
                _remove(conn, dev["host"])
            except Exception:
                pass
            try:
                conn.disconnect()
            except Exception:
                pass

    final = {}
    for r in results.values():
        final[r["status"]] = final.get(r["status"], 0) + 1
    print(f"\nprocessed {processed} this run. totals: {final}")
    print(f"crashers ({len(state['crashers'])}): {state['crashers']}")
    print(f"state: {state_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
