#!/usr/bin/env python3
"""
Generate IOS XE CLI config from subscriptions.yaml

Produces a ready-to-paste IOS XE config block for all telemetry
subscriptions, using the receiver IP/port and intervals from the YAML.

Usage:
  python generate_ios_config.py                          # stdout
  python generate_ios_config.py --receiver-ip 10.1.1.3   # override receiver
  python generate_ios_config.py --out c9300-mdt.cfg       # write to file
  python generate_ios_config.py --sub 1001 1005 1007      # specific subs only
"""

import argparse
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
SUBS_FILE = SCRIPT_DIR / "subscriptions.yaml"

TIER_INTERVALS = {"hot": 3000, "warm": 6000, "cool": 30000}
TIER_LABELS = {"hot": "30s", "warm": "60s", "cool": "300s"}


def load_config(filepath=SUBS_FILE):
    with open(filepath) as f:
        return yaml.safe_load(f)


def generate(config, receiver_ip, receiver_port, sub_ids=None):
    subs = config["subscriptions"]
    if sub_ids:
        subs = {k: v for k, v in subs.items() if k in sub_ids}

    lines = []
    lines.append("! " + "=" * 60)
    lines.append("! IOS XE Model-Driven Telemetry — gRPC Dial-Out Config")
    lines.append(f"! Receiver: {receiver_ip}:{receiver_port}")
    lines.append(f"! Generated subscriptions: {len(subs)}")
    lines.append("! " + "=" * 60)
    lines.append("")

    current_tier = None
    for sub_id, sub in sorted(subs.items()):
        tier = sub["tier"]
        if tier != current_tier:
            current_tier = tier
            lines.append(f"! {'=' * 60}")
            lines.append(
                f"! {tier.upper()} TIER — {TIER_LABELS.get(tier, '?')} polling"
            )
            lines.append(f"! {'=' * 60}")
            lines.append("")

        interval = TIER_INTERVALS.get(tier, 30000)
        section = sub.get("section", "?")
        name = sub["name"]

        lines.append(f"! --- §{section}. {name} ---")
        lines.append(f"telemetry ietf subscription {sub_id}")
        lines.append(f" encoding encode-kvgpb")
        lines.append(f" filter xpath {sub['xpath']}")
        lines.append(f" stream yang-push")
        lines.append(f" update-policy periodic {interval}")
        lines.append(
            f" receiver ip address {receiver_ip} {receiver_port} protocol grpc-tcp"
        )
        lines.append("")

    lines.append("! " + "=" * 60)
    lines.append("! Verification Commands")
    lines.append("! " + "=" * 60)
    lines.append("! show telemetry ietf subscription all")
    lines.append("! show telemetry ietf subscription <id> detail")
    lines.append("! show telemetry ietf subscription <id> receiver")
    lines.append("! show telemetry internal connection")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate IOS XE MDT subscription CLI config")
    parser.add_argument("--receiver-ip", help="Override receiver IP (default from YAML)")
    parser.add_argument("--receiver-port", type=int, help="Override receiver port (default from YAML)")
    parser.add_argument("--out", help="Output file path (default: stdout)")
    parser.add_argument("--sub", nargs="+", type=int, help="Specific subscription IDs only")

    args = parser.parse_args()
    config = load_config()

    receiver_ip = args.receiver_ip or config["receiver"]["ip"]
    receiver_port = args.receiver_port or config["receiver"]["port"]

    output = generate(config, receiver_ip, receiver_port, args.sub)

    if args.out:
        with open(args.out, "w") as f:
            f.write(output)
        print(f"Config written to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
