#!/usr/bin/env python3
"""
build_telemetry_dataset.py — Emit a committable dataset of REAL Model-Driven
Telemetry (MDT) captured from physical Catalyst switches for the web app's
telemetry-data page (telemetry-data.html / telemetry-data.js).

It reads the local MDT telemetry bundle (scripts/mdt-telemetry/):
  - harness/validation/subscriptions.yaml  — canonical subscription list
    (id, name, yang_module, xpath, tier, expected keys/metrics/dimensions).
  - captures/*.txt                          — grouped plain-text metric summaries
    produced by the OTel collector (per-metric name, type, cardinality, and a
    distribution of value|dimension rows).
  - captures/README.md                      — the produced/silent index and the
    reasons a subscription streamed no data.

and writes ./telemetry-data.json: one entry per subscription with its metadata
plus, for produced subscriptions, a capped sample of the streamed metrics and
values. The page uses this single file for coverage stats, tier/module browsing,
and metric drill-down — no raw captures are shipped.

Values are kept verbatim by default (the bundle's captures hold lab identifiers,
not secrets). Pass --redact to mask IPv4/IPv6 addresses, MACs, and hostnames in
sample values if the dataset ever needs to leave a trusted environment.

Usage:
  python scripts/build_telemetry_dataset.py                 # write telemetry-data.json
  python scripts/build_telemetry_dataset.py --redact        # mask IPs/MACs/hostnames
  python scripts/build_telemetry_dataset.py --dry-run       # print summary only
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_DIR = PROJECT_ROOT / "scripts" / "mdt-telemetry"
SUBS_FILE = BUNDLE_DIR / "harness" / "validation" / "subscriptions.yaml"
CAPTURES_DIR = BUNDLE_DIR / "captures"
CAPTURES_INDEX = CAPTURES_DIR / "README.md"
OUTPUT_FILE = PROJECT_ROOT / "telemetry-data.json"

# Keep the committed file small: cap how much of each capture's distribution we
# carry. The full cardinality is preserved as a number; only the sampled rows
# are truncated.
MAX_METRICS_PER_SUB = 60
MAX_SAMPLES_PER_METRIC = 6

# Static provenance describing the reference lab that produced the captures.
DEVICES = ["cat9300x-pod10a", "cat9300-pod10b"]
PLATFORM = "Catalyst 9300"
OS_VERSION = "26.1.1"
TRANSPORT = "gRPC dial-out (TCP/57500, kvGPB)"
CAPTURE_WINDOW_SEC = 120

TIER_LABELS = {"hot": "HOT", "warm": "WARM", "cool": "COOL"}

# --- capture-file parsing ----------------------------------------------------

# "  cisco.content.free-memory  (gauge, 30)"
_METRIC_HEADER = re.compile(r"^\s{2}(\S.*?)\s+\(([a-z]+),\s*([\d,]+)\)\s*$")
# "      758,651,908  |  name=Processor"   /   "                1  |  (global)"
_SAMPLE_ROW = re.compile(r"^\s*(.+?)\s+\|\s+(.*?)\s*$")
# "  180 data points from 10 telemetry messages"
_HEADER_POINTS = re.compile(r"([\d,]+)\s+data points from\s+([\d,]+)\s+telemetry messages")


def _to_int(text: str) -> int:
    return int(text.replace(",", "").strip())


def _metric_class_and_leaf(name: str) -> tuple[str, str]:
    """Split a collector metric name like ``cisco.content.isis-neighbor.holdtime``
    into its class (``content`` / ``keys``) and the remaining leaf path."""
    parts = name.split(".")
    if len(parts) >= 3 and parts[0] == "cisco":
        return parts[1], ".".join(parts[2:])
    return "", name


def parse_capture(path: Path) -> dict:
    """Parse one capture .txt into {sub_id, name, slug, data_points, messages, metrics[]}."""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    result = {
        "sub_id": None,
        "name": None,
        "slug": path.stem,
        "data_points": None,
        "telemetry_messages": None,
        "metrics": [],
    }

    # Header block: "Sub <id>: <name>" and the data-points line.
    for line in lines[:8]:
        stripped = line.strip()
        if stripped.startswith("Sub "):
            head = stripped[4:]
            sub_id, _, name = head.partition(":")
            result["sub_id"] = sub_id.strip()
            result["name"] = name.strip() or None
        points_match = _HEADER_POINTS.search(stripped)
        if points_match:
            result["data_points"] = _to_int(points_match.group(1))
            result["telemetry_messages"] = _to_int(points_match.group(2))

    current = None
    for line in lines:
        header = _METRIC_HEADER.match(line)
        if header:
            if current is not None:
                result["metrics"].append(current)
            metric_class, leaf = _metric_class_and_leaf(header.group(1))
            current = {
                "name": header.group(1),
                "class": metric_class,
                "leaf": leaf,
                "type": header.group(2),
                "cardinality": _to_int(header.group(3)),
                "samples": [],
            }
            continue
        if current is None:
            continue
        if set(line.strip()) <= {"-"} and line.strip():
            continue  # separator dashes
        row = _SAMPLE_ROW.match(line)
        if row and len(current["samples"]) < MAX_SAMPLES_PER_METRIC:
            current["samples"].append({
                "value": row.group(1).strip(),
                "label": row.group(2).strip(),
            })
    if current is not None:
        result["metrics"].append(current)

    if len(result["metrics"]) > MAX_METRICS_PER_SUB:
        result["metrics"] = result["metrics"][:MAX_METRICS_PER_SUB]
    return result


def parse_silent_reasons(index_path: Path) -> dict:
    """Read the 'Silent Subscriptions' table from captures/README.md ->
    {sub_id: reason}."""
    reasons: dict[str, str] = {}
    if not index_path.exists():
        return reasons
    in_silent = False
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if "Silent Subscriptions" in line:
            in_silent = True
            continue
        if in_silent:
            if line.startswith("## "):
                break
            if line.startswith("|") and "|" in line[1:]:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 4 and cells[0].isdigit():
                    reasons[cells[0]] = cells[3]
    return reasons


# --- redaction (opt-in) ------------------------------------------------------

_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_MAC = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:.-]){5}[0-9A-Fa-f]{2}\b")
_HOSTNAME = re.compile(r"\b[a-z0-9-]+\.cisco\.com\b|\bcat9300[a-z0-9-]*\b", re.IGNORECASE)


def redact_text(text: str) -> str:
    text = _IPV4.sub("<ip>", text)
    text = _MAC.sub("<mac>", text)
    text = _HOSTNAME.sub("<host>", text)
    return text


def redact_samples(metrics: list, enabled: bool) -> None:
    if not enabled:
        return
    for metric in metrics:
        for sample in metric["samples"]:
            sample["value"] = redact_text(sample["value"])
            sample["label"] = redact_text(sample["label"])


# --- category mapping --------------------------------------------------------

def category_for_module(module: str) -> str:
    """Map a YANG module name to the web app's spec category (for coloring and
    deep links)."""
    lowered = module.lower()
    if lowered.startswith("ietf"):
        return "ietf"
    if lowered.startswith("openconfig"):
        return "openconfig"
    return "oper"


# --- build -------------------------------------------------------------------

def build_dataset(redact: bool) -> dict:
    config = yaml.safe_load(SUBS_FILE.read_text(encoding="utf-8"))
    subscriptions = config.get("subscriptions", {})
    tiers_cfg = config.get("tiers", {})

    silent_reasons = parse_silent_reasons(CAPTURES_INDEX)

    # Index captures by subscription id.
    captures_by_id: dict[str, dict] = {}
    for capture_path in sorted(CAPTURES_DIR.glob("*.txt")):
        parsed = parse_capture(capture_path)
        if parsed["sub_id"]:
            captures_by_id[parsed["sub_id"]] = parsed

    entries = []
    total_metrics = 0
    total_data_points = 0
    produced_count = 0

    for raw_id, sub in sorted(subscriptions.items(), key=lambda kv: str(kv[0])):
        sub_id = str(raw_id)
        tier = sub.get("tier", "")
        module = sub.get("yang_module", "")
        capture = captures_by_id.get(sub_id)
        produced = capture is not None

        metrics = []
        data_points = 0
        messages = None
        if produced:
            redact_samples(capture["metrics"], redact)
            metrics = capture["metrics"]
            data_points = capture.get("data_points") or 0
            messages = capture.get("telemetry_messages")
            produced_count += 1
            total_metrics += len(metrics)
            total_data_points += data_points

        entries.append({
            "id": sub_id,
            "name": sub.get("name", ""),
            "section": sub.get("section"),
            "yang_module": module,
            "category": category_for_module(module),
            "xpath": sub.get("xpath", ""),
            "tier": tier,
            "interval_sec": tiers_cfg.get(tier, {}).get("interval_sec"),
            "produced": produced,
            "silent_reason": None if produced else silent_reasons.get(sub_id),
            "data_points": data_points,
            "telemetry_messages": messages,
            "expected_keys": sub.get("expected_keys", []) or [],
            "expected_metrics": sub.get("expected_metrics", []) or [],
            "expected_dimensions": sub.get("expected_dimensions", []) or [],
            "metrics": metrics,
        })

    tiers = {
        name: {
            "interval_sec": cfg.get("interval_sec"),
            "label": TIER_LABELS.get(name, name.upper()),
        }
        for name, cfg in tiers_cfg.items()
    }

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "scripts/mdt-telemetry",
        "platform": PLATFORM,
        "os_version": OS_VERSION,
        "devices": DEVICES,
        "transport": TRANSPORT,
        "capture_window_sec": CAPTURE_WINDOW_SEC,
        "redacted": redact,
        "tiers": tiers,
        "totals": {
            "subscriptions": len(entries),
            "produced": produced_count,
            "silent": len(entries) - produced_count,
            "metrics": total_metrics,
            "data_points": total_data_points,
        },
        "subscriptions": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--redact", action="store_true", help="Mask IPs/MACs/hostnames in sample values.")
    parser.add_argument("--dry-run", action="store_true", help="Print a summary; do not write the file.")
    parser.add_argument("--out", default=str(OUTPUT_FILE), help="Output path (default: telemetry-data.json).")
    args = parser.parse_args()

    if not SUBS_FILE.exists():
        parser.error(f"subscriptions.yaml not found at {SUBS_FILE} — is the MDT bundle placed under scripts/mdt-telemetry/?")

    dataset = build_dataset(redact=args.redact)
    totals = dataset["totals"]
    print(
        f"subscriptions={totals['subscriptions']} produced={totals['produced']} "
        f"silent={totals['silent']} metrics={totals['metrics']} "
        f"data_points={totals['data_points']:,} redacted={dataset['redacted']}"
    )

    if args.dry_run:
        print("(dry run — nothing written)")
        return 0

    out_path = Path(args.out)
    out_path.write_text(json.dumps(dataset, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    size_kb = out_path.stat().st_size / 1024
    print(f"wrote {out_path.relative_to(PROJECT_ROOT)} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
