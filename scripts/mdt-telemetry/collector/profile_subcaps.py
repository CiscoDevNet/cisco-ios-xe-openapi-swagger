#!/usr/bin/env python3
"""Profile a device's MDT subscription capabilities (read-only).

GETs Cisco-IOS-XE-mdt-capabilities-oper from a device and reports, per model
category, how many xpaths are subscribable and with which update policy
(periodic / on-change). This is the authoritative, per-device source of truth
for what we can subscribe to — used to drive scaled collection.

  .venv-harness/bin/python profile_subcaps.py --device C9300 [--dump caps.json]
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REPO = Path(__file__).resolve().parents[3]
ENV = REPO / "scripts" / "harness" / ".env"
INV = REPO / "scripts" / "harness" / "inventory.json"
CAP_PATH = ("Cisco-IOS-XE-mdt-capabilities-oper:mdt-capabilities-oper-data")


def load_env():
    env = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def pick(selector):
    for d in json.loads(INV.read_text(encoding="utf-8")):
        if selector.lower() in d["name"].lower() or selector.lower() in d.get("pid", "").lower():
            return d
    raise SystemExit(f"no device matches {selector!r}")


def prefix_of(xpath):
    xp = xpath.lstrip("/")
    return xp.split(":", 1)[0] if ":" in xp else xp.split("/", 1)[0]


def category_of(pfx):
    p = pfx.lower()
    if p.startswith("openconfig") or p.startswith("oc-"):
        return "openconfig"
    if p.startswith("ietf"):
        return "ietf"
    if "native" in p:
        return "native"
    if p.endswith("-cfg") or p.endswith("-config"):
        return "cfg"
    if "oper" in p:
        return "oper"
    return "other"


def walk_pernode(obj, out):
    """Recursively collect dicts that carry an 'xpath' + policy support."""
    if isinstance(obj, dict):
        if "xpath" in obj:
            out.append(obj)
        for v in obj.values():
            walk_pernode(v, out)
    elif isinstance(obj, list):
        for v in obj:
            walk_pernode(v, out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="C9300")
    ap.add_argument("--dump", help="Write the raw capabilities JSON here.")
    args = ap.parse_args()

    env = load_env()
    dev = pick(args.device)
    url = f"https://{dev['host']}/restconf/data/{CAP_PATH}?depth=unbounded"
    r = requests.get(url, auth=(env["IOSXE_USER"], env["IOSXE_PASS"]),
                     headers={"Accept": "application/yang-data+json"},
                     verify=False, timeout=120)
    print(f"{dev['name']} ({dev['pid']}) {dev['host']} -> HTTP {r.status_code}")
    if r.status_code != 200:
        print(r.text[:400])
        return 1
    data = r.json()
    if args.dump:
        Path(args.dump).write_text(json.dumps(data, indent=1), encoding="utf-8")

    nodes = []
    walk_pernode(data, nodes)
    print(f"per-node xpath entries: {len(nodes)}")

    by_cat = collections.Counter()
    periodic = collections.Counter()
    onchange = collections.Counter()
    samples = collections.defaultdict(list)
    for n in nodes:
        xp = n.get("xpath", "")
        if not xp:
            continue
        cat = category_of(prefix_of(xp))
        by_cat[cat] += 1
        per = str(n.get("periodic-supported", "")).lower()
        onc = str(n.get("on-change-supported", "")).lower()
        if per and per not in ("not-supported", "false", "0", "none"):
            periodic[cat] += 1
        if onc and onc not in ("not-supported", "false", "0", "none"):
            onchange[cat] += 1
        if len(samples[cat]) < 4:
            samples[cat].append(xp)

    print("\nsubscribable xpaths by category:")
    for cat in sorted(by_cat):
        print(f"  {cat:11} total={by_cat[cat]:5}  periodic={periodic[cat]:5}  on-change={onchange[cat]:5}")
    print("\nsample xpaths per category:")
    for cat in sorted(samples):
        print(f"  {cat}:")
        for xp in samples[cat]:
            print(f"     {xp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
