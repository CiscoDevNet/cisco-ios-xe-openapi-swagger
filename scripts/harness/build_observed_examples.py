"""Overlay real captured GET responses into the OpenAPI specs as examples.

Part of the Track B GET harness (DEVICE_DATA_COLLECTION.md §11.A.2 / §11.B.4). Reads
the local captures under scripts/harness/captures/ and, for every successful
(HTTP 200, non-empty) GET, injects the verbatim (light-redacted) response body
into that path's ``get`` 200-response as an OpenAPI 3.0 ``examples`` entry,
keyed per device PID and tagged with machine-readable ``x-cisco-observed``
provenance so it is unmistakably real device data, not a synthetic default.

Multiple PIDs capturing the same path produce multiple example entries
(``live-<pid>``) which Swagger UI surfaces natively in its examples dropdown
(the §11.B per-PID switcher, for free).

Default is a DRY RUN (prints what would change, writes nothing). Pass --write to
apply the overlay in place to the spec files under --specs-root. Injecting
example content does NOT change path/operation/module counts, so the G-6
baseline is unaffected; bump service-worker CACHE_VERSION after applying.

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


def _example_entry(record: dict) -> tuple[str, dict, dict]:
    """Build (key, example_object, x_cisco_observed) for one capture."""
    pid = str(record.get("pid", "unknown")) or "unknown"
    device = str(record.get("device", "?"))
    os_version = str(record.get("os_version", "unknown"))
    fetched_at = str(record.get("fetched_at", ""))
    # Defensive re-redaction; captures are already light-redacted on write.
    value = redaction.redact(record.get("response"))
    key = f"live-{pid}"
    summary = f"Real device capture - {pid} - IOS XE {os_version}" + (f" - {fetched_at[:10]}" if fetched_at else "")
    example_obj = {
        "summary": summary,
        "description": (
            "Verbatim RESTCONF GET response from a real Catalyst 9000 device, "
            "lightly redacted (secrets only). Not a synthetic schema default."
        ),
        "value": value,
    }
    observed = {
        "source": "live-device",
        "device": device,
        "pid": pid,
        "os_version": os_version,
        "http_status": record.get("http_status"),
        "fetched_at": fetched_at,
        # OpenAPI path only — never the restconf_url, which carries the device IP.
        "path": record.get("path", ""),
    }
    return key, example_obj, observed


def _inject(op: dict, record: dict, max_bytes: int) -> str:
    """Inject the capture into the GET op's 200 response (idempotent).

    Returns a status: ``annotated`` on success, or ``too_large`` / ``secret``
    when a guard refuses the example (in which case the spec is left untouched).
    """
    key, example_obj, observed = _example_entry(record)
    value_text = json.dumps(example_obj["value"], ensure_ascii=False)
    # Safety valve: skip a runaway payload rather than bloat the spec.
    if max_bytes and len(value_text.encode("utf-8")) > max_bytes:
        return "too_large"
    # Basic secret gate: never commit an example that still looks secret-bearing
    # after light redaction. Reuses the existing (deliberately simple) scanner.
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
        # OpenAPI forbids singular `example` alongside `examples`; migrate it.
        examples = media.setdefault("examples", {})
        if not isinstance(examples, dict):
            examples = {}
            media["examples"] = examples
        if "example" in media:
            examples.setdefault("schema-default", {"value": media.pop("example")})
        examples[key] = example_obj
        # Provenance sits beside the example on the media-type object.
        obs = media.setdefault("x-cisco-observed", {})
        if not isinstance(obs, dict):
            obs = {}
            media["x-cisco-observed"] = obs
        obs[key] = observed
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
