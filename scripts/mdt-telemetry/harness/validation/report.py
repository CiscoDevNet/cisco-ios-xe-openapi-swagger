#!/usr/bin/env python3
"""
Generate a validation summary report from validation JSON results.

Reads the latest (or specified) validation result JSON and produces
a markdown summary showing which subscriptions passed, which returned
empty data, and which failed — with field details.

Usage:
  python report.py                              # latest result
  python report.py --file results/validation-10.1.1.1-20260412T...json
  python report.py --out results/summary.md     # write to file
"""

import argparse
import json
import sys
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"


def find_latest_report():
    """Find the most recent validation JSON in results/."""
    files = sorted(RESULTS_DIR.glob("validation-*.json"))
    if not files:
        print("No validation results found in results/")
        sys.exit(1)
    return files[-1]


def generate_report(report_data):
    """Generate markdown summary from validation JSON."""
    lines = []
    host = report_data.get("host", "unknown")
    timestamp = report_data.get("timestamp", "unknown")
    results = report_data.get("results", {})

    lines.append(f"# MDT Validation Report — {host}")
    lines.append(f"")
    lines.append(f"**Timestamp:** {timestamp}")
    lines.append(f"**Total subscriptions:** {len(results)}")
    lines.append("")

    # Categorize results
    data_ok = []
    data_empty = []
    data_fail = []
    data_not_found = []

    for sub_id, result in sorted(results.items(), key=lambda x: int(x[0])):
        sample_status = result.get("sample", {}).get("status", "unknown")
        if sample_status == "ok":
            data_ok.append((sub_id, result))
        elif sample_status == "empty":
            data_empty.append((sub_id, result))
        elif sample_status == "not_found":
            data_not_found.append((sub_id, result))
        else:
            data_fail.append((sub_id, result))

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Status | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Data returned | {len(data_ok)} |")
    lines.append(f"| Empty (feature not configured) | {len(data_empty)} |")
    lines.append(f"| Not found (404 — unsupported) | {len(data_not_found)} |")
    lines.append(f"| Error | {len(data_fail)} |")
    lines.append("")

    # Detailed results: OK
    if data_ok:
        lines.append("## Subscriptions with Data")
        lines.append("")
        lines.append("| Sub ID | § | Name | Fields | Missing Keys | Missing Metrics |")
        lines.append("|--------|---|------|--------|-------------|----------------|")
        for sub_id, result in data_ok:
            section = result.get("section", "?")
            name = result.get("name", "?")
            field_count = result.get("sample", {}).get("field_count", 0)
            validation = result.get("validation", {})
            missing_keys = ", ".join(validation.get("missing_keys", [])) or "—"
            missing_metrics = ", ".join(validation.get("missing_metrics", [])) or "—"
            lines.append(
                f"| {sub_id} | {section} | {name} | {field_count} | {missing_keys} | {missing_metrics} |"
            )
        lines.append("")

    # Detailed results: Empty
    if data_empty:
        lines.append("## Empty Data (Feature Not Configured)")
        lines.append("")
        lines.append("These subscriptions returned HTTP 204 — the YANG module exists but no data is populated. "
                     "This is expected if the feature is not configured on the device.")
        lines.append("")
        lines.append("| Sub ID | § | Name | YANG Module |")
        lines.append("|--------|---|------|------------|")
        for sub_id, result in data_empty:
            section = result.get("section", "?")
            name = result.get("name", "?")
            yang = result.get("yang_module", "?")
            lines.append(f"| {sub_id} | {section} | {name} | {yang} |")
        lines.append("")

    # Detailed results: Not Found
    if data_not_found:
        lines.append("## Not Found (YANG Module Not Supported)")
        lines.append("")
        lines.append("These subscriptions returned HTTP 404 — the YANG module may not be available on this platform/version. "
                     "Remove these from the subscription config.")
        lines.append("")
        lines.append("| Sub ID | § | Name | YANG Module | XPath |")
        lines.append("|--------|---|------|------------|-------|")
        for sub_id, result in data_not_found:
            section = result.get("section", "?")
            name = result.get("name", "?")
            yang = result.get("yang_module", "?")
            xpath = result.get("xpath", "?")
            lines.append(f"| {sub_id} | {section} | {name} | {yang} | `{xpath}` |")
        lines.append("")

    # Detailed results: Errors
    if data_fail:
        lines.append("## Errors")
        lines.append("")
        lines.append("| Sub ID | § | Name | Status | HTTP Code |")
        lines.append("|--------|---|------|--------|-----------|")
        for sub_id, result in data_fail:
            section = result.get("section", "?")
            name = result.get("name", "?")
            status = result.get("sample", {}).get("status", "?")
            http = result.get("sample", {}).get("http_code", "?")
            lines.append(f"| {sub_id} | {section} | {name} | {status} | {http} |")
        lines.append("")

    # Field inventory for OK subscriptions
    if data_ok:
        lines.append("## Field Inventory (first 20 fields per subscription)")
        lines.append("")
        for sub_id, result in data_ok:
            name = result.get("name", "?")
            section = result.get("section", "?")
            fields = result.get("sample", {}).get("fields", [])
            if not fields:
                continue
            lines.append(f"### §{section} — {name} (Sub {sub_id})")
            lines.append("")
            lines.append("| Field Path | Type | Sample Value |")
            lines.append("|-----------|------|-------------|")
            for field in fields[:20]:
                path = field.get("path", "?")
                ftype = field.get("type", "?")
                sample = field.get("sample", field.get("count", ""))
                lines.append(f"| `{path}` | {ftype} | {sample} |")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate validation summary report")
    parser.add_argument("--file", help="Specific validation JSON to summarize")
    parser.add_argument("--out", help="Output markdown file (default: stdout)")

    args = parser.parse_args()

    if args.file:
        report_path = Path(args.file)
    else:
        report_path = find_latest_report()

    with open(report_path) as f:
        report_data = json.load(f)

    markdown = generate_report(report_data)

    if args.out:
        with open(args.out, "w") as f:
            f.write(markdown)
        print(f"Report written to {args.out}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
