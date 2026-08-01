#!/usr/bin/env python3
"""Print a one-shot progress summary for a walk_xpaths run.

Real-time monitor:  watch -n 5 .venv-harness/bin/python scripts/mdt-telemetry/collector/walk_status.py
"""
from __future__ import annotations

import datetime
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "output" / "subscribable-nodes.json"


def catof(xp: str) -> str:
    p = xp.lstrip("/").split(":", 1)[0].lower()
    if p.startswith(("openconfig", "oc-")):
        return "openconfig"
    if p.startswith("ietf"):
        return "ietf"
    if "native" in p:
        return "native-config"
    if p.endswith(("-cfg", "-config")):
        return "cfg"
    if "oper" in p:
        return "oper"
    return "other"


def main():
    device = sys.argv[1] if len(sys.argv) > 1 else "C9300-24UX"
    state_path = HERE / "output" / f"walk-{device}.json"
    if not state_path.exists():
        print(f"no state file yet: {state_path.name}")
        return 0
    d = json.loads(state_path.read_text())
    r = d["results"]
    tally = Counter(v["status"] for v in r.values())

    # Scope total by the categories present in results (usually one flavor).
    cats_seen = {catof(x) for x in r} or {"oper"}
    cat = json.loads(CATALOG.read_text())
    total = sum(1 for m in cat["modules"].values() for n in m if catof(n["xpath"]) in cats_seen)

    start = datetime.datetime.fromisoformat(d["started"].replace("Z", "+00:00"))
    upd = datetime.datetime.fromisoformat(d["updated"].replace("Z", "+00:00"))
    el = max((upd - start).total_seconds(), 1)
    rate = len(r) / el
    rem = max(total - len(r), 0)
    eta_h = rem / rate / 3600 if rate > 0 else 0
    age = (datetime.datetime.now(datetime.timezone.utc) - upd).total_seconds()

    print(f"device {device}   scope {sorted(cats_seen)}")
    print(f"progress {len(r)}/{total}  ({100*len(r)/total:.1f}%)   last update {age:.0f}s ago")
    print(f"  streamed {tally.get('streamed',0)}   silent {tally.get('silent',0)}   "
          f"invalid {tally.get('invalid',0)}   crashed {tally.get('crashed',0)}   error {tally.get('error',0)}")
    print(f"  rate {rate*60:.1f}/min   ETA {eta_h:.1f} h")
    crashers = d.get("crashers", [])
    print(f"  crashers ({len(crashers)}):")
    for c in crashers:
        print(f"     !!! {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
