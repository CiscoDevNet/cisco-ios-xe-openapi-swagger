"""Overlay real captured GET responses into the OpenAPI specs (x-cisco-live-examples).

Part of the Track B GET harness (DEVICE_DATA_COLLECTION.md §11.0). Reads the local
captures under scripts/harness/captures/ and, for every successful (HTTP 200,
non-empty) GET, adds the verbatim (light-redacted) response under the
``x-cisco-live-examples`` vendor extension on that path's ``get`` 200-response,
keyed by device PID. The existing synthetic ``example`` is left UNTOUCHED — the
web app's viewer hook (assets/js/viewer-enhancements.js) renders the per-PID real
data in a "Live device sample - <PID>" panel beside it.

Shape written per media type:
    "x-cisco-live-examples": {
        "C9300-24UX": { "os_version": "26.1.1", "fetched_at": "...", "http_status": 200,
                        "path": "/data/...", "value": {<real redacted response>} }
    }
Multiple PIDs capturing the same path simply add more keys (per-PID switcher).

Default is a DRY RUN (prints what would change, writes nothing). Pass --write to
apply the overlay in place to the spec files under --specs-root. This is additive
vendor-extension content: it does NOT change path/operation/module counts, so the
G-6 baseline is unaffected; bump service-worker CACHE_VERSION after applying.

Run:
  python -X utf8 -m scripts.harness.build_observed_examples                 # dry run
  python -X utf8 -m scripts.harness.build_observed_examples --write         # apply
  python -X utf8 -m scripts.harness.build_observed_examples --specs-root releases/26.1.1 --write
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.harness import redact as redaction
    from scripts.harness import secret_scan
    from scripts.harness import spec_paths
else:  # pragma: no cover - exercised via -m
    from . import redact as redaction
    from . import secret_scan
    from . import spec_paths

HARNESS_DIR = Path(__file__).resolve().parent
CAPTURES_DIR = HARNESS_DIR / "captures"

DEFAULT_MEDIA_TYPE = "application/yang-data+json"

# Safety valve only. Real oper/mib payloads are far smaller than this; the cap
# exists so a pathological whole-config subtree can't bloat a spec unbounded.
# 0 = no cap.
DEFAULT_MAX_EXAMPLE_BYTES = 5_000_000


def _iter_captures(captures_dir: Path):
    for cap in sorted(captures_dir.glob("*/*/*.json")):
        try:
            record = json.loads(cap.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        yield record


def _is_usable(record: dict) -> bool:
    """Only successful GETs with an actual body become examples."""
    if record.get("http_status") != 200 or record.get("error"):
        return False
    body = record.get("response")
    return body not in (None, {}, [], "")


def _get_operation(spec: dict, path: str) -> Optional[dict]:
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        return None
    item = paths.get(path)
    if not isinstance(item, dict):
        return None
    for key, op in item.items():
        if key.lower() == "get" and isinstance(op, dict):
            return op
    return None


def _response_object(op: dict) -> dict:
    """Return (creating if needed) the 200/default response object for a GET op."""
    responses = op.setdefault("responses", {})
    for key in ("200", 200, "default"):
        if key in responses and isinstance(responses[key], dict):
            return responses[key]
    resp = {"description": "Successful RESTCONF GET (observed on a real device)."}
    responses["200"] = resp
    return resp


def _live_entry(record: dict) -> tuple[str, dict]:
    """Build (pid, per-PID live-example entry) for one capture.

    Per the agreed Phase 4 decision (DEVICE_DATA_COLLECTION.md §11.0) the real
    data is exposed under the ``x-cisco-live-examples`` vendor extension keyed by
    PID; the entry carries the redacted response plus minimal provenance so the
    viewer can render a "Live device sample - <PID> v<os_version>" panel. The
    device IP / restconf_url is deliberately excluded.
    """
    pid = str(record.get("pid", "unknown")) or "unknown"
    # Defensive re-redaction; captures are already light-redacted on write.
    value = redaction.redact(record.get("response"))
    entry = {
        "os_version": str(record.get("os_version", "unknown")),
        "fetched_at": str(record.get("fetched_at", "")),
        "http_status": record.get("http_status"),
        "path": record.get("path", ""),   # OpenAPI path only — never the device IP
        "value": value,
    }
    return pid, entry


def _inject(op: dict, record: dict, max_bytes: int) -> str:
    """Inject the capture into the GET op's 200 response (idempotent).

    Adds the real response under ``x-cisco-live-examples[<PID>]`` and leaves the
    existing synthetic ``example`` UNTOUCHED (agreed convention). Returns
    ``annotated`` on success, or ``too_large`` / ``secret`` when a guard refuses
    the example (spec left unchanged).
    """
    pid, entry = _live_entry(record)
    value_text = json.dumps(entry["value"], ensure_ascii=False)
    # Safety valve: skip a runaway payload rather than bloat the spec.
    if max_bytes and len(value_text.encode("utf-8")) > max_bytes:
        return "too_large"
    # Basic secret gate: never commit data that still looks secret-bearing after
    # light redaction. Reuses the existing (deliberately simple) scanner.
    if secret_scan.find_secrets(value_text):
        return "secret"

    resp = _response_object(op)
    content = resp.setdefault("content", {})
    if not isinstance(content, dict) or not content:
        content = {DEFAULT_MEDIA_TYPE: {}}
        resp["content"] = content
    for _mt, media in list(content.items()):
        if not isinstance(media, dict):
            continue
        # Synthetic `example` stays UNTOUCHED; real per-PID data goes in the
        # x-cisco-live-examples vendor extension (matches x-yang-module/x-model-type).
        live = media.setdefault("x-cisco-live-examples", {})
        if not isinstance(live, dict):
            live = {}
            media["x-cisco-live-examples"] = live
        live[pid] = entry
    return "annotated"


def apply_overlay(captures_dir: Path, specs_root: Path, write: bool,
                  max_bytes: int = DEFAULT_MAX_EXAMPLE_BYTES) -> Counter:
    """Overlay all usable captures onto the specs. Returns a stats Counter."""
    stats: Counter = Counter()
    # Group usable captures by (category, module) -> list, so each spec file is
    # read/written once even with many paths or several devices.
    by_spec: dict[tuple[str, str], list[dict]] = {}
    for record in _iter_captures(captures_dir):
        stats["captures"] += 1
        if not _is_usable(record):
            stats["skipped_not200_or_empty"] += 1
            continue
        key = (str(record.get("category")), str(record.get("module")))
        by_spec.setdefault(key, []).append(record)

    for (category, module), records in sorted(by_spec.items()):
        spec_file = spec_paths.category_api_dir(specs_root, category) / f"{module}.json"
        if not spec_file.exists():
            stats["spec_missing"] += len(records)
            print(f"  [skip] spec not found: {spec_file} ({len(records)} capture(s))")
            continue
        try:
            spec = json.loads(spec_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            stats["spec_unreadable"] += len(records)
            print(f"  [skip] spec not JSON: {spec_file}")
            continue

        touched = 0
        for record in records:
            path = str(record.get("path"))
            op = _get_operation(spec, path)
            if op is None:
                stats["path_not_in_spec"] += 1
                continue
            status = _inject(op, record, max_bytes)
            if status == "annotated":
                touched += 1
                stats["operations_annotated"] += 1
            elif status == "too_large":
                stats["skipped_too_large"] += 1
            elif status == "secret":
                stats["skipped_secret"] += 1
                print(f"  [!] secret-like content, example SKIPPED: {category}/{module} {path}")

        if touched:
            stats["specs_touched"] += 1
            action = "write" if write else "would annotate"
            print(f"  [{action}] {category}/{module}.json: {touched} operation(s)")
            if write:
                spec_file.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    return stats


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--captures", help="Captures dir (default scripts/harness/captures)")
    ap.add_argument("--specs-root", help="Specs root (default releases/26.1.1)")
    ap.add_argument("--write", action="store_true", help="Apply the overlay in place (default: dry run)")
    ap.add_argument(
        "--max-example-bytes",
        type=int,
        default=DEFAULT_MAX_EXAMPLE_BYTES,
        help=f"Skip any example larger than this (default {DEFAULT_MAX_EXAMPLE_BYTES}; 0 = no cap)",
    )
    args = ap.parse_args(argv)

    captures_dir = Path(args.captures) if args.captures else CAPTURES_DIR
    if not captures_dir.is_dir():
        print(f"No captures dir yet: {captures_dir}. Run the collector first.", file=sys.stderr)
        return 2
    try:
        specs_root = spec_paths.resolve_specs_root(args.specs_root)
    except spec_paths.SpecsNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Captures : {captures_dir}")
    print(f"Specs    : {specs_root}")
    print(f"Mode     : {'WRITE (in place)' if args.write else 'DRY RUN (no files changed)'}")
    print(f"Max bytes: {args.max_example_bytes or 'no cap'}")
    stats = apply_overlay(captures_dir, specs_root, write=args.write, max_bytes=args.max_example_bytes)

    print(
        "\nSummary: "
        f"captures={stats['captures']} "
        f"annotated_ops={stats['operations_annotated']} "
        f"specs_touched={stats['specs_touched']} "
        f"skipped(non-200/empty)={stats['skipped_not200_or_empty']} "
        f"skipped(too_large)={stats['skipped_too_large']} "
        f"skipped(secret)={stats['skipped_secret']} "
        f"path_not_in_spec={stats['path_not_in_spec']} "
        f"spec_missing={stats['spec_missing']}"
    )
    if stats["skipped_secret"]:
        print("WARNING: secret-like examples were skipped; investigate before committing.")
    if not args.write and stats["operations_annotated"]:
        print("\nDry run only. Re-run with --write to apply, then bump service-worker CACHE_VERSION.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
