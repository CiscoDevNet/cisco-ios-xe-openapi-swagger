#!/usr/bin/env python3
"""verify_params.py - Verify all keyed paths have correct parameters."""
import json, os, re

def main():


    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TARGET = [
        "swagger-cfg-model/api",
        "swagger-oper-model/api",
        "swagger-ietf-model/api",
        "swagger-openconfig-model/api",
        "swagger-other-model/api",
    ]

    ok = bad = 0
    issues = []

    for rel in TARGET:
        d = os.path.join(BASE, rel)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json") or fn == "manifest.json":
                continue
            with open(os.path.join(d, fn), "r", encoding="utf-8") as f:
                data = json.load(f)
            for pk, pv in data.get("paths", {}).items():
                if "={" not in pk:
                    continue
                # Count expected keys from path
                expected_keys = re.findall(r"\{([^}]+)\}", pk)
                # Expand space-separated
                all_expected = []
                for k in expected_keys:
                    if " " in k:
                        all_expected.extend(k.split())
                    else:
                        all_expected.append(k)
            
                for method in ["get", "put", "patch", "delete", "post"]:
                    if method not in pv:
                        continue
                    mv = pv[method]
                    if not isinstance(mv, dict):
                        continue
                    params = mv.get("parameters", [])
                    param_names = {p.get("name") for p in params if isinstance(p, dict)}
                
                    if set(all_expected).issubset(param_names):
                        ok += 1
                    else:
                        bad += 1
                        missing = set(all_expected) - param_names
                        if len(issues) < 15:
                            issues.append(f"  {fn} {method} {pk[-80:]}")
                            issues.append(f"    expected: {all_expected}")
                            issues.append(f"    got: {sorted(param_names)}")
                            issues.append(f"    missing: {sorted(missing)}")

    print(f"Keyed methods with complete params: {ok}")
    print(f"Keyed methods with incomplete/missing params: {bad}")
    if issues:
        print("\nSample issues:")
        for line in issues:
            print(line)

if __name__ == '__main__':
    main()
