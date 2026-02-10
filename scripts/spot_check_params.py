#!/usr/bin/env python3
"""Spot-check parameter quality in representative specs."""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

samples = [
    ("swagger-oper-model/api", "Cisco-IOS-XE-bgp-oper.json"),
    ("swagger-oper-model/api", "Cisco-IOS-XE-interfaces-oper.json"),
    ("swagger-cfg-model/api", "Cisco-IOS-XE-wireless-wlan-cfg.json"),
    ("swagger-ietf-model/api", "ietf-interfaces.json"),
    ("swagger-openconfig-model/api", "openconfig-interfaces.json"),
    ("swagger-other-model/api", "nvo.json"),
]

for rel, fn in samples:
    fpath = os.path.join(BASE, rel, fn)
    if not os.path.exists(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n=== {fn} ===")
    shown = 0
    for pk, pv in data.get("paths", {}).items():
        if "={" not in pk:
            continue
        for method in ["get", "put", "patch", "delete"]:
            mv = pv.get(method, {})
            if isinstance(mv, dict) and "parameters" in mv:
                params = mv["parameters"]
                parts = []
                for p in params:
                    s = f'{p["name"]}({p["schema"]["type"]})'
                    if "example" in p:
                        s += f'="{p["example"]}"'
                    parts.append(s)
                short_path = pk if len(pk) < 90 else "..." + pk[-85:]
                print(f"  {method.upper()} {short_path}")
                print(f"    params: [{', '.join(parts)}]")
                break
        shown += 1
        if shown >= 3:
            break


if __name__ == "__main__":
    main = None  # just run at module level
