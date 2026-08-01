#!/usr/bin/env python3
"""
MDT Telemetry Subscription Validator

Connects to a Catalyst 9300 via RESTCONF to:
1. Push telemetry subscriptions (one at a time or all)
2. Verify subscription state via show commands
3. Pull a sample of operational data via RESTCONF GET for each XPath
4. Document what fields/keys/metrics are actually returned
5. Generate a validation report

Usage:
  python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED***
  python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED*** --sub 1001
  python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED*** --check-only
  python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED*** --sample-only

Requirements:
  pip install requests pyyaml urllib3
"""

import argparse
import json
import sys
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import urllib3
import yaml

# Suppress TLS warnings for lab environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SCRIPT_DIR = Path(__file__).parent
SUBS_FILE = SCRIPT_DIR / "subscriptions.yaml"
RESULTS_DIR = SCRIPT_DIR / "results"

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}

RESTCONF_BASE = "https://{host}/restconf/data"


def load_subscriptions(filepath=SUBS_FILE):
    """Load subscription definitions from YAML."""
    with open(filepath) as f:
        return yaml.safe_load(f)


def restconf_get(session, host, path, depth=None):
    """Perform a RESTCONF GET and return parsed JSON or error dict."""
    url = f"{RESTCONF_BASE.format(host=host)}/{path}"
    # Limit response depth to avoid truncation on large modules (e.g., LLDP)
    query_depth = depth if depth is not None else 4
    if "?" not in url:
        url += f"?depth={query_depth}"
    try:
        response = session.get(url, headers=RESTCONF_HEADERS, verify=False, timeout=60)
        if response.status_code == 200:
            return {"status": "ok", "data": response.json(), "http_code": 200}
        elif response.status_code == 204:
            return {"status": "empty", "data": None, "http_code": 204}
        elif response.status_code == 404:
            return {"status": "not_found", "data": None, "http_code": 404}
        else:
            return {
                "status": "error",
                "data": response.text[:500],
                "http_code": response.status_code,
            }
    except requests.exceptions.ConnectionError as e:
        return {"status": "connection_error", "data": str(e)[:200], "http_code": 0}
    except requests.exceptions.Timeout:
        return {"status": "timeout", "data": None, "http_code": 0}
    except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ContentDecodingError) as e:
        return {"status": "response_truncated", "data": str(e)[:200], "http_code": 200}
    except Exception as e:
        return {"status": "error", "data": str(e)[:200], "http_code": 0}


def restconf_patch(session, host, path, payload):
    """Perform a RESTCONF PATCH to configure a subscription."""
    url = f"{RESTCONF_BASE.format(host=host)}/{path}"
    try:
        response = session.patch(
            url,
            headers=RESTCONF_HEADERS,
            json=payload,
            verify=False,
            timeout=30,
        )
        return {
            "status": "ok" if response.status_code in (200, 201, 204) else "error",
            "http_code": response.status_code,
            "data": response.text[:500] if response.status_code not in (200, 201, 204) else None,
        }
    except requests.exceptions.RequestException as e:
        return {"status": "connection_error", "data": str(e)[:200], "http_code": 0}


def xpath_to_restconf_path(xpath):
    """Convert a YANG XPath to a RESTCONF URL path.

    Telemetry XPaths use a prefix like:
      /process-cpu-ios-xe-oper:cpu-usage/cpu-utilization
    RESTCONF needs the full YANG module name:
      Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization

    Special cases for non-Cisco modules (ietf, mdt-oper, etc.)
    """
    path = xpath.lstrip("/")

    # Map of telemetry prefix → RESTCONF module name for non-standard mappings
    prefix_map = {
        "mdt-oper-v2": "Cisco-IOS-XE-mdt-oper-v2",
        "mdt-oper": "Cisco-IOS-XE-mdt-oper",
        "dp-resources-oper": "Cisco-IOS-XE-switch-dp-resources-oper",
        "switch-dp-punt-inject-oper": "Cisco-IOS-XE-switch-dp-punt-inject-oper",
        "poe-health-oper": "Cisco-IOS-XE-poe-health-oper",
        "poe-health-xe": "Cisco-IOS-XE-poe-health-oper",
        "device-hardware-xe-oper": "Cisco-IOS-XE-device-hardware-oper",
        "platform-sw-ios-xe-oper": "Cisco-IOS-XE-platform-software-oper",
        "stp-ios-xe-oper": "Cisco-IOS-XE-spanning-tree-oper",
        "xcvr-ios-xe-oper": "Cisco-IOS-XE-transceiver-oper",
        "if": "ietf-interfaces",
        "rt": "ietf-routing",
    }

    # Extract the prefix (everything before the first ':')
    if ":" in path:
        prefix, rest = path.split(":", 1)

        # Check explicit mappings first
        if prefix in prefix_map:
            return f"{prefix_map[prefix]}:{rest}"

        # IETF modules stay as-is
        if prefix.startswith("ietf-"):
            return path

        # Standard Cisco pattern: xxx-ios-xe-oper → Cisco-IOS-XE-xxx-oper
        # e.g., process-cpu-ios-xe-oper → Cisco-IOS-XE-process-cpu-oper
        if "-ios-xe-oper" in prefix:
            module_name = prefix.replace("-ios-xe-oper", "")
            return f"Cisco-IOS-XE-{module_name}-oper:{rest}"

        # Fallback: try prepending Cisco-IOS-XE-
        return f"Cisco-IOS-XE-{prefix}:{rest}"

    return path


def check_subscription_state(session, host, sub_id):
    """Check if a subscription exists and its state via RESTCONF."""
    path = f"Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data/mdt-subscription-oper={sub_id}"
    result = restconf_get(session, host, path)
    if result["status"] == "ok" and result["data"]:
        return result["data"]
    # Try the older mdt-oper path
    path = f"Cisco-IOS-XE-mdt-oper:mdt-oper-data/mdt-subscriptions={sub_id}"
    result = restconf_get(session, host, path)
    if result["status"] == "ok" and result["data"]:
        return result["data"]
    return None


def push_subscription(session, host, sub_id, sub_config, receiver_ip, receiver_port):
    """Push a single telemetry subscription via RESTCONF."""
    tiers = {"hot": 3000, "warm": 6000, "cool": 30000}
    interval = tiers.get(sub_config["tier"], 30000)

    payload = {
        "Cisco-IOS-XE-mdt-cfg:mdt-subscription": {
            "subscription-id": sub_id,
            "base": {
                "stream": "yang-push",
                "encoding": "encode-kvgpb",
                "xpath": sub_config["xpath"],
                "period": interval,
            },
            "mdt-receivers": {
                "address": receiver_ip,
                "port": receiver_port,
                "protocol": "grpc-tcp",
            },
        }
    }

    path = "Cisco-IOS-XE-mdt-cfg:mdt-config-data"
    return restconf_patch(session, host, path, payload)


def sample_operational_data(session, host, xpath):
    """Fetch a sample of operational data via RESTCONF GET.

    If the full path returns 404 (common when xpath traverses into a list
    without specifying keys), retry with progressively shorter paths until
    we reach the top-level container.
    """
    restconf_path = xpath_to_restconf_path(xpath)

    # Use shallower depth for known-large modules to prevent truncation
    depth_override = None
    if "lldp" in restconf_path.lower():
        # LLDP lldp-entries is too large — query lldp-entry sub-path instead
        restconf_path = restconf_path.replace(
            "lldp-entries", "lldp-entries/lldp-entry"
        )

    result = restconf_get(session, host, restconf_path, depth=depth_override)

    # Fallback: truncate nested path segments on 404
    # This handles xpaths like .../location/dp-feature-resource where
    # 'location' is a keyed list that RESTCONF can't traverse without keys.
    if result["status"] == "not_found":
        parts = restconf_path.split("/")
        while len(parts) > 1 and result["status"] == "not_found":
            parts = parts[:-1]
            truncated = "/".join(parts)
            result = restconf_get(session, host, truncated, depth=depth_override)

    return result


def extract_fields_from_json(data, prefix="", max_depth=5):
    """Recursively extract all field paths from a JSON response."""
    fields = []
    if max_depth <= 0:
        return fields

    if isinstance(data, dict):
        for key, value in data.items():
            full_path = f"{prefix}/{key}" if prefix else key
            if isinstance(value, dict):
                fields.append({"path": full_path, "type": "container"})
                fields.extend(extract_fields_from_json(value, full_path, max_depth - 1))
            elif isinstance(value, list):
                fields.append({"path": full_path, "type": "list", "count": len(value)})
                if value and isinstance(value[0], dict):
                    fields.extend(
                        extract_fields_from_json(value[0], full_path + "[0]", max_depth - 1)
                    )
            else:
                leaf_type = type(value).__name__
                fields.append({"path": full_path, "type": leaf_type, "sample": str(value)[:100]})
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        fields.extend(extract_fields_from_json(data[0], prefix + "[0]", max_depth - 1))

    return fields


def run_validation(args):
    """Main validation workflow."""
    config = load_subscriptions()
    subscriptions = config["subscriptions"]
    receiver_ip = args.receiver_ip or config["receiver"]["ip"]
    receiver_port = args.receiver_port or config["receiver"]["port"]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_file = RESULTS_DIR / f"validation-{args.host}-{timestamp}.json"

    session = requests.Session()
    session.auth = (args.user, args.password)

    # Filter subscriptions if specific ones requested
    if args.sub:
        sub_ids = [int(s) for s in args.sub]
        subscriptions = {k: v for k, v in subscriptions.items() if k in sub_ids}
        if not subscriptions:
            print(f"No matching subscription IDs found: {args.sub}")
            sys.exit(1)

    report = {
        "host": args.host,
        "timestamp": timestamp,
        "total_subscriptions": len(subscriptions),
        "results": {},
    }

    print(f"\n{'='*70}")
    print(f"MDT Subscription Validation — {args.host}")
    print(f"{'='*70}")
    print(f"Subscriptions to validate: {len(subscriptions)}")
    print(f"Receiver: {receiver_ip}:{receiver_port}")
    print(f"{'='*70}\n")

    for sub_id, sub_config in sorted(subscriptions.items()):
        section = sub_config.get("section", "?")
        name = sub_config["name"]
        xpath = sub_config["xpath"]

        print(f"[§{section}] Sub {sub_id}: {name}")
        print(f"  XPath: {xpath}")

        result = {
            "sub_id": sub_id,
            "section": section,
            "name": name,
            "xpath": xpath,
            "tier": sub_config["tier"],
            "yang_module": sub_config["yang_module"],
        }

        # Step 1: Push subscription (unless check-only or sample-only)
        if not args.check_only and not args.sample_only:
            push_result = push_subscription(
                session, args.host, sub_id, sub_config, receiver_ip, receiver_port
            )
            result["push"] = push_result
            status_icon = "OK" if push_result["status"] == "ok" else "FAIL"
            print(f"  Push: {status_icon} (HTTP {push_result['http_code']})")
            if push_result["status"] != "ok":
                print(f"    Error: {push_result.get('data', 'unknown')}")

        # Step 2: Check subscription state
        if not args.sample_only:
            sub_state = check_subscription_state(session, args.host, sub_id)
            if sub_state:
                result["state"] = "exists"
                result["state_detail"] = sub_state
                print(f"  State: EXISTS")
            else:
                result["state"] = "not_found"
                print(f"  State: NOT FOUND")

        # Step 3: Sample operational data via RESTCONF
        if not args.check_only:
            sample = sample_operational_data(session, args.host, xpath)
            result["sample"] = {
                "status": sample["status"],
                "http_code": sample["http_code"],
            }
            if sample["status"] == "ok" and sample["data"]:
                fields = extract_fields_from_json(sample["data"])
                result["sample"]["field_count"] = len(fields)
                result["sample"]["fields"] = fields[:50]  # Cap at 50 fields per sub

                # Compare expected vs actual fields
                expected_keys = sub_config.get("expected_keys", [])
                expected_metrics = sub_config.get("expected_metrics", [])
                actual_paths = {f["path"] for f in fields}

                found_keys = [k for k in expected_keys if any(k in p for p in actual_paths)]
                missing_keys = [k for k in expected_keys if k not in found_keys]
                found_metrics = [m for m in expected_metrics if any(m in p for p in actual_paths)]
                missing_metrics = [m for m in expected_metrics if m not in found_metrics]

                result["validation"] = {
                    "expected_keys": expected_keys,
                    "found_keys": found_keys,
                    "missing_keys": missing_keys,
                    "expected_metrics": expected_metrics,
                    "found_metrics": found_metrics,
                    "missing_metrics": missing_metrics,
                    "pass": len(missing_keys) == 0,
                }

                print(f"  Sample: OK ({len(fields)} fields)")
                if missing_keys:
                    print(f"  WARN: Missing expected keys: {missing_keys}")
                if missing_metrics:
                    print(f"  WARN: Missing expected metrics: {missing_metrics}")
            elif sample["status"] == "empty":
                result["sample"]["field_count"] = 0
                print(f"  Sample: EMPTY (204 — feature may not be configured)")
            elif sample["status"] == "not_found":
                print(f"  Sample: NOT FOUND (404 — YANG module may not be supported)")
            elif sample["status"] == "response_truncated":
                result["sample"]["field_count"] = 0
                print(f"  Sample: TRUNCATED (response too large, but module exists)")
            else:
                print(f"  Sample: {sample['status']} (HTTP {sample['http_code']})")

        report["results"][str(sub_id)] = result
        print()

    # Summary
    total = len(report["results"])
    if not args.check_only:
        sampled_ok = sum(
            1 for r in report["results"].values()
            if r.get("sample", {}).get("status") == "ok"
        )
        sampled_empty = sum(
            1 for r in report["results"].values()
            if r.get("sample", {}).get("status") == "empty"
        )
        sampled_fail = total - sampled_ok - sampled_empty
    else:
        sampled_ok = sampled_empty = sampled_fail = 0
        state_exists = sum(
            1 for r in report["results"].values() if r.get("state") == "exists"
        )

    print(f"{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Total subscriptions tested: {total}")
    if not args.check_only:
        print(f"  Data returned:     {sampled_ok}")
        print(f"  Empty (no config): {sampled_empty}")
        print(f"  Failed/404:        {sampled_fail}")
    if not args.sample_only:
        if args.check_only:
            print(f"  State exists:      {state_exists}")
            print(f"  State not found:   {total - state_exists}")

    # Write report
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nFull report: {report_file}")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="MDT Telemetry Subscription Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all subscriptions (push + check + sample)
  python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED***

  # Validate specific subscriptions only
  python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED*** --sub 1001 1007 1005

  # Only check subscription state (no push, no data sample)
  python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED*** --check-only

  # Only sample operational data (no push, no state check)
  python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED*** --sample-only

  # Override receiver IP/port
  python validate.py --host 10.1.1.1 --user admin --pass ***REDACTED*** --receiver-ip 10.1.1.3 --receiver-port 57500
        """,
    )
    parser.add_argument("--host", required=True, help="Switch IP or hostname")
    parser.add_argument("--user", required=True, help="RESTCONF username")
    parser.add_argument("--pass", dest="password", required=True, help="RESTCONF password")
    parser.add_argument(
        "--sub", nargs="+", help="Specific subscription IDs to validate (e.g., 1001 1007)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check subscription state, do not push or sample data",
    )
    parser.add_argument(
        "--sample-only",
        action="store_true",
        help="Only sample operational data via RESTCONF GET, do not push subscriptions",
    )
    parser.add_argument("--receiver-ip", help="Override receiver IP from subscriptions.yaml")
    parser.add_argument("--receiver-port", type=int, help="Override receiver port")

    args = parser.parse_args()
    run_validation(args)


if __name__ == "__main__":
    main()
