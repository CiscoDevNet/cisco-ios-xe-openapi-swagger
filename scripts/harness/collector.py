"""GET-phase collector for the Track B C9K RESTCONF harness.

Enumerates GET paths from the OpenAPI specs and captures each device's raw
response to a local, gitignored tree. Strictly READ-ONLY: every device request
goes through ``request.restconf_get`` which hard-refuses non-GET methods.

Usage (activate the venv first: ``source .venv-harness/bin/activate``):

    python -X utf8 -m scripts.harness.collector --preflight
    python -X utf8 -m scripts.harness.collector --pilot          # 1 device, target module
    python -X utf8 -m scripts.harness.collector                  # full: all cats, all devices
    python -X utf8 -m scripts.harness.collector --roots-only     # fast mode
    python -X utf8 -m scripts.harness.collector --dry-run        # plan only, no device I/O

Nothing here is wired into build_release.py, CI, or the Pages deploy.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import sys
import threading
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

# Support both "python -m scripts.harness.collector" and direct execution.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.harness import inventory as inv
    from scripts.harness import redact as redaction
    from scripts.harness import spec_paths
    from scripts.harness.request import restconf_get
else:  # pragma: no cover - exercised via -m
    from . import inventory as inv
    from . import redact as redaction
    from . import spec_paths
    from .request import restconf_get

HARNESS_DIR = Path(__file__).resolve().parent
CAPTURES_DIR = HARNESS_DIR / "captures"
TRACE_PATH = HARNESS_DIR / "trace.jsonl"

# Canonical pilot target (DEVICE_DATA_COLLECTION.md §2).
PILOT_CATEGORY = "oper"
PILOT_MODULE = "Cisco-IOS-XE-switch-dp-punt-inject-oper"

# Modules whose GET is known to CRASH the device (firmware defects), skipped by
# default to protect the box. Override with --include-unsafe. Confirmed via the
# device-side send-log breadcrumb + on-box crash traceback.
KNOWN_UNSAFE_MODULES = {
    "Cisco-IOS-XE-lldp-oper": (
        "segfault in lldp_state_ios_oper (Process DBAL EVENTS) on GET of "
        "lldp-entries — crashes/reloads the switch (observed C9300, IOS XE 26.1.1)"
    ),
    "CISCO-RTTMON-MIB": (
        "GET of /data/CISCO-RTTMON-MIB drops the connection mid-response "
        "(ChunkedEncodingError) and stalls the RESTCONF/DMI process for minutes — "
        "device reset (observed C9300, IOS XE 26.1.1)"
    ),
}


def filter_unsafe(paths, extra_exclude=None, include_unsafe=False):
    """Drop known-unsafe and user-excluded modules. Returns (kept, skipped_modules)."""
    exclude = set(extra_exclude or ())
    if not include_unsafe:
        exclude |= set(KNOWN_UNSAFE_MODULES)
    kept = [p for p in paths if p.module not in exclude]
    skipped = sorted({p.module for p in paths if p.module in exclude})
    return kept, skipped


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _path_hash(path: str) -> str:
    return hashlib.sha1(path.encode("utf-8")).hexdigest()[:16]


def capture_file(device_name: str, category: str, module: str, path: str) -> Path:
    return CAPTURES_DIR / device_name / category / f"{module}__{_path_hash(path)}.json"


def _classify(result) -> str:
    """Bucket a GetResult for the per-module summary."""
    if result.error:
        return "error"
    if result.http_status == 404:
        return "404"
    if result.empty or result.body in (None, {}, []):
        return "empty"
    if result.ok:
        return "200"
    return f"http_{result.http_status}"


def _write_capture(
    device: "inv.Device",
    gp: "spec_paths.GetPath",
    result,
) -> None:
    record = {
        "device": device.name,
        "pid": device.pid,
        "host": device.host,
        "module": gp.module,
        "category": gp.category,
        "path": gp.path,
        "restconf_url": result.url,
        "http_status": result.http_status,
        "fetched_at": _now_iso(),
        "os_version": device.os_version,
        "error": result.error,
        # Light redaction applied before touching disk (§6). Raw is local-only.
        "response": redaction.redact(result.body) if result.is_json else result.body,
    }
    out = capture_file(device.name, gp.category, gp.module, gp.path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out)  # atomic; safe for resume/interrupt


class CircuitBreaker:
    """Abort a run when the device stops responding, to avoid crashing it.

    Counts *consecutive* connection/timeout failures (the ``error`` bucket — not
    404/empty/http_4xx, which mean the device is alive and answering). A healthy
    response resets the count. Trips once the count reaches ``threshold``;
    ``threshold=0`` disables the breaker.
    """

    def __init__(self, threshold: int) -> None:
        self.threshold = threshold
        self.consecutive = 0
        self.tripped = False
        self.reason: Optional[str] = None
        self.trip_path: Optional[str] = None

    def register(self, status: str, reset: bool = False, path: Optional[str] = None) -> bool:
        """Record one result; return True once the breaker has tripped.

        ``reset=True`` (connection dropped / chunked-encoding error \u2014 the device
        crash signature) trips IMMEDIATELY and names the culprit path, since a
        single such event means the box is going down. Otherwise a run of
        ``threshold`` consecutive errors trips it.
        """
        if not self.threshold:
            return False
        if reset:
            self.tripped = True
            self.reason = "connection reset / chunked-encoding (device crash signature)"
            self.trip_path = path
            return True
        if status == "error":
            self.consecutive += 1
        else:
            self.consecutive = 0
        if self.consecutive >= self.threshold and not self.tripped:
            self.tripped = True
            self.reason = f"{self.threshold} consecutive connection/timeout failures"
            self.trip_path = path
        return self.tripped


def capture_device(
    device: "inv.Device",
    paths: list["spec_paths.GetPath"],
    auth: tuple[str, str],
    concurrency: int,
    timeout: int,
    rate_limit: float,
    resume: bool,
    breaker_threshold: int = 8,
    conflict_retries: int = 8,
    conflict_backoff: float = 0.25,
    marker=None,
) -> Counter:
    """Capture all ``paths`` for one device. Returns a status Counter.

    ``marker`` (optional) is called with each ``GetPath`` just BEFORE its GET, so a
    device-side breadcrumb is logged first; if that GET crashes the box, the last
    breadcrumb on the device names the offending module.
    """
    summary: Counter = Counter()
    breaker = CircuitBreaker(breaker_threshold)
    lock = threading.Lock()
    # Bound concurrency; a shared Session per worker via thread-local.
    tls = threading.local()
    # Per-GET trace for crash attribution (gitignored). Records timing + reset so
    # a device crash is attributable even at high concurrency / through retries.
    trace_fh = open(TRACE_PATH, "a", encoding="utf-8")

    def worker(gp: "spec_paths.GetPath"):
        out = capture_file(device.name, gp.category, gp.module, gp.path)
        if resume and out.exists():
            # Skip only CLEAN prior captures; re-fetch anything that errored so a
            # crash-affected path is never silently left behind ("none missed").
            try:
                if not json.loads(out.read_text(encoding="utf-8")).get("error"):
                    return ("skip", False)
            except (json.JSONDecodeError, OSError):
                pass  # unreadable -> re-fetch
        if marker is not None:
            try:
                marker(gp)  # device-side breadcrumb BEFORE the GET
            except Exception:
                pass  # SSH may have dropped (device crashing) — GET reveals state
        sess = getattr(tls, "session", None)
        if sess is None:
            sess = requests.Session()
            tls.session = sess
        result = restconf_get(
            host=device.host,
            port=device.port,
            openapi_path=gp.path,
            auth=auth,
            timeout=timeout,
            session=sess,
            conflict_retries=conflict_retries,
            conflict_backoff=conflict_backoff,
        )
        _write_capture(device, gp, result)
        status = _classify(result)
        line = json.dumps({
            "t": _now_iso(), "elapsed_ms": result.elapsed_ms, "attempts": result.attempts,
            "reset": result.reset, "category": gp.category, "module": gp.module,
            "path": gp.path, "status": status, "error": result.error,
        })
        with lock:
            trace_fh.write(line + "\n")
            trace_fh.flush()
        if rate_limit:
            time.sleep(rate_limit)
        return (status, result.reset)

    total = len(paths)
    done = 0
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = {pool.submit(worker, gp): gp for gp in paths}
            for fut in concurrent.futures.as_completed(futures):
                gp = futures[fut]
                reset = False
                try:
                    status, reset = fut.result()
                except Exception as exc:  # noqa: BLE001 - keep going, record failure
                    status = "error"
                    with lock:
                        print(f"  ! {gp.module} {gp.path}: {exc}", file=sys.stderr)
                summary[status] += 1
                if reset:
                    summary["reset"] += 1
                done += 1
                culprit = f"{gp.category}/{gp.module}  {gp.path}"
                if breaker.register(status, reset=reset, path=culprit):
                    summary["breaker_tripped"] = 1
                    inflight = sorted(
                        f"{futures[f].category}/{futures[f].module}  {futures[f].path}"
                        for f in futures if not f.done()
                    )
                    with lock:
                        print(
                            f"\n  !! CIRCUIT BREAKER TRIPPED on {device.name}: {breaker.reason}",
                            file=sys.stderr, flush=True,
                        )
                        print(f"     culprit (last result): {breaker.trip_path}", file=sys.stderr)
                        print(f"     {len(inflight)} path(s) IN-FLIGHT at trip (crash suspects):", file=sys.stderr)
                        for s in inflight[:concurrency + 2]:
                            print(f"       - {s}", file=sys.stderr)
                        print(f"     captured {done}/{total} so far; trace: {TRACE_PATH}; "
                              f"resume re-runs errored+unrun paths.", file=sys.stderr, flush=True)
                    for pending in futures:
                        if not pending.done():
                            pending.cancel()
                    break
                if done % 200 == 0 or done == total:
                    print(
                        f"  [{device.name}] {done}/{total} "
                        f"(200={summary['200']} 404={summary['404']} "
                        f"empty={summary['empty']} error={summary['error']} "
                        f"reset={summary['reset']} skip={summary['skip']})",
                        flush=True,
                    )
    finally:
        trace_fh.close()
    return summary


def run_preflight(args) -> int:
    """Report readiness without contacting any device."""
    print("== Track B GET harness preflight ==")
    ok = True

    # Specs
    try:
        root = spec_paths.resolve_specs_root(args.specs_root)
        print(f"[ok]   specs root: {root}")
        for cat in spec_paths.GET_CATEGORIES:
            d = spec_paths.category_api_dir(root, cat)
            n = len(list(d.glob("*.json"))) if d.is_dir() else 0
            flag = "ok" if n else "MISSING"
            if not n:
                ok = False
            print(f"       [{flag}] {cat}: {n} spec file(s) at {d}")
    except spec_paths.SpecsNotFoundError as exc:
        ok = False
        print(f"[FAIL] {exc}")

    # Inventory
    try:
        devices = inv.load_inventory(args.inventory)
        print(f"[ok]   inventory: {len(devices)} device(s)")
        for d in devices:
            print(f"       - {d.name} ({d.pid}) {d.host}:{d.port}")
    except inv.InventoryError as exc:
        ok = False
        print(f"[FAIL] inventory: {exc}")

    # Credentials
    if inv.credentials_available():
        print("[ok]   credentials: IOSXE_USER/IOSXE_PASS present")
    else:
        ok = False
        print("[FAIL] credentials: set IOSXE_USER and IOSXE_PASS (never written to outputs)")

    print(f"\nPreflight: {'READY' if ok else 'NOT READY'} — captures dir: {CAPTURES_DIR}")
    return 0 if ok else 2


def build_plan(args) -> tuple[Path, list["spec_paths.GetPath"], list[str]]:
    """Resolve specs + build the GET path plan. Used by dry-run and real runs."""
    root = spec_paths.resolve_specs_root(args.specs_root)
    categories = args.category or list(spec_paths.GET_CATEGORIES)
    modules = None
    if args.pilot:
        categories = [PILOT_CATEGORY]
        modules = [PILOT_MODULE]
    elif args.module:
        modules = args.module
    paths = spec_paths.enumerate_get_paths(
        root, categories=categories, roots_only=args.roots_only, modules=modules
    )
    paths, skipped = filter_unsafe(
        paths, extra_exclude=args.exclude, include_unsafe=args.include_unsafe
    )
    if args.limit:
        paths = paths[: args.limit]
    return root, paths, categories, skipped


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--specs-root", help="Dir containing swagger-<cat>-model/api/*.json (default: releases/26.1.1)")
    ap.add_argument("--inventory", help="Path to inventory.json (default: scripts/harness/inventory.json)")
    ap.add_argument("--category", action="append", choices=spec_paths.GET_CATEGORIES, help="Restrict categories (repeatable)")
    ap.add_argument("--device", action="append", dest="devices", help="Restrict to device name(s) (repeatable)")
    ap.add_argument("--module", action="append", help="Restrict to module name(s) (repeatable)")
    ap.add_argument("--exclude", action="append", help="Skip module name(s) (repeatable)")
    ap.add_argument("--include-unsafe", action="store_true", help="Also query known-unsafe modules that can crash the device (default: skip them)")
    ap.add_argument("--pilot", action="store_true", help=f"Pilot: {PILOT_MODULE} on the first device only")
    ap.add_argument("--roots-only", action="store_true", help="Fast mode: GET only each module root container")
    ap.add_argument("--concurrency", type=int, default=6, help="Parallel GETs per device (4-8 recommended)")
    ap.add_argument("--timeout", type=int, default=30, help="Per-request timeout seconds")
    ap.add_argument("--rate-limit", type=float, default=0.0, help="Sleep seconds between requests per worker")
    ap.add_argument("--breaker", type=int, default=8, help="Abort a device after N consecutive connection/timeout failures (0 = disable)")
    ap.add_argument("--conflict-retries", type=int, default=8, help="Retries for a 409/429 (datastore busy) before giving up on a path")
    ap.add_argument("--conflict-backoff", type=float, default=0.25, help="Base seconds between 409/429 retries (grows per attempt, jittered)")
    ap.add_argument("--log-marker", action="store_true", help="SSH to the device and 'send log' the module/path BEFORE each GET (crash diagnosis; forces --concurrency 1)")
    ap.add_argument("--log-severity", type=int, default=6, help="Severity for the device-side 'send log' marker (default 6)")
    ap.add_argument("--ssh-port", type=int, default=22, help="SSH port for --log-marker (default 22)")
    ap.add_argument("--limit", type=int, help="Cap total paths (debug)")
    ap.add_argument("--no-resume", action="store_true", help="Re-capture even if a capture file already exists")
    ap.add_argument("--preflight", action="store_true", help="Check readiness; do NOT contact devices")
    ap.add_argument("--dry-run", action="store_true", help="Enumerate + print plan; do NOT contact devices")
    args = ap.parse_args(argv)

    if args.concurrency < 1 or args.concurrency > 8:
        ap.error("--concurrency must be between 1 and 8")
    if args.log_marker and args.concurrency != 1:
        print(f"note: --log-marker at --concurrency {args.concurrency}: marker sends are "
              "serialized (thread-safe) and each GET is still preceded by its own marker, "
              "but device-side ordering across concurrent GETs interleaves (fine for bulk; "
              "use --concurrency 1 for a clean ordered trail when crash-hunting).")

    if args.preflight:
        return run_preflight(args)

    # Build the plan (needs specs only).
    try:
        root, paths, categories, skipped = build_plan(args)
    except spec_paths.SpecsNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Specs root : {root}")
    print(f"Categories : {', '.join(categories)}")
    print(f"GET paths  : {len(paths)}"
          + (" (roots-only)" if args.roots_only else "")
          + (f" (pilot: {PILOT_MODULE})" if args.pilot else ""))
    if skipped:
        print(f"Skipped    : {len(skipped)} module(s) not queried:")
        for m in skipped:
            reason = KNOWN_UNSAFE_MODULES.get(m, "user --exclude")
            print(f"             - {m}  ({reason})")

    if args.dry_run:
        for gp in paths[:20]:
            print(f"  {gp.category:13} {gp.module}  {gp.path}")
        if len(paths) > 20:
            print(f"  ... and {len(paths) - 20} more")
        print("\nDry-run only — no device contacted.")
        return 0

    # Real capture: needs inventory + credentials.
    try:
        devices = inv.load_inventory(args.inventory)
    except inv.InventoryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.devices:
        wanted = set(args.devices)
        devices = [d for d in devices if d.name in wanted]
        if not devices:
            print(f"ERROR: no inventory devices match {sorted(wanted)}", file=sys.stderr)
            return 2
    if args.pilot:
        devices = devices[:1]

    try:
        auth = inv.load_credentials()
    except inv.CredentialError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    grand = Counter()
    for device in devices:
        print(f"\n== Device {device.name} ({device.pid}) {device.host}:{device.port} ==")
        marker = None
        dev_logger = None
        if args.log_marker:
            from scripts.harness.device_log import DeviceLogger
            dev_logger = DeviceLogger(
                host=device.host, username=auth[0], password=auth[1],
                port=args.ssh_port, severity=args.log_severity,
            )
            try:
                dev_logger.connect()
                print(f"  [log-marker] SSH connected; 'send log {args.log_severity}' before each GET")

                def marker(gp, _sev=args.log_severity, _lg=dev_logger):
                    msg = f"HARNESS GET {gp.category}/{gp.module} {gp.path}"
                    ok = _lg.mark(msg)
                    print(f"  [send log {_sev}] {msg}" + ("" if ok else "  (SSH send failed)"), flush=True)

            except Exception as exc:
                print(f"  [log-marker] SSH connect failed ({exc}); continuing without markers", file=sys.stderr)
                dev_logger = None
        summary = capture_device(
            device=device,
            paths=paths,
            auth=auth,
            concurrency=args.concurrency,
            timeout=args.timeout,
            rate_limit=args.rate_limit,
            resume=not args.no_resume,
            breaker_threshold=args.breaker,
            conflict_retries=args.conflict_retries,
            conflict_backoff=args.conflict_backoff,
            marker=marker,
        )
        if dev_logger is not None:
            dev_logger.close()
        print(f"  summary {device.name}: {dict(summary)}")
        grand.update(summary)
        if summary.get("breaker_tripped"):
            print(
                "\nStopped early: circuit breaker tripped (device stopped responding). "
                "Let it recover, then re-run — resume skips what's already captured.",
                file=sys.stderr,
            )
            break

    print(f"\nDONE. Aggregate: {dict(grand)}")
    print(f"Captures under: {CAPTURES_DIR} (gitignored)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
