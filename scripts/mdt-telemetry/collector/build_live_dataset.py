#!/usr/bin/env python3
"""
build_live_dataset.py — assemble a per-device MDT dataset from Telegraf output.

Reads the JSON-lines the Telegraf cisco_telemetry_mdt receiver wrote
(collector/output/mdt-live.json) plus the collection plan (fleet-plan.json), and
emits telemetry-live-data.json: one entry per (device PID, xpath) with the model
category and a capped sample of the fields that streamed. Device PID and model
category let the web app show real oper / OpenConfig / native-config telemetry
side by side per platform.

  .venv-harness/bin/python build_live_dataset.py
"""
from __future__ import annotations

import argparse
import collections
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DEFAULT_INPUT = HERE / "output" / "mdt-live.json"
PLAN_FILE = HERE / "output" / "fleet-plan.json"
OUTPUT_FILE = REPO / "telemetry-live-data.json"

MAX_FIELDS_PER_PATH = 24
MAX_SAMPLES = 5000  # distinct keyed instances kept per path (effectively "all";
                    # high bound guards against a single pathological path)


def category_of(path: str) -> str:
    mod = path.split(":", 1)[0].lower() if ":" in path else path.lower()
    if "wireless" in mod:
        return "wireless"
    if "-mib" in mod or mod.endswith("mib"):
        return "mib"
    if mod.startswith("openconfig") or mod.startswith("oc-"):
        return "openconfig"
    if mod.startswith("ietf"):
        return "ietf"
    if "native" in mod:
        return "native-config"
    if mod.endswith("-cfg") or mod.endswith("-config"):
        return "cfg"
    if "oper" in mod:
        return "oper"
    return "other"


def load_inv_pids() -> list:
    inv = REPO / "scripts" / "harness" / "inventory.json"
    try:
        return [d["pid"] for d in json.loads(inv.read_text(encoding="utf-8"))]
    except Exception:
        return []


def pid_from_file(fname: str, inv_pids: list) -> str:
    tok = fname[len("mdt-"):-len(".json")]  # e.g. C9300
    for p in inv_pids:
        if tok and (tok in p or p in tok):
            return p
    return tok


def source_to_pid(plan: dict) -> dict:
    """Map a Telegraf `source` hostname to a device PID using the plan's
    name->pid map (the inventory name embeds the hostname)."""
    out = {}
    for name, pid in (plan.get("source_pid") or {}).items():
        out[name] = pid
    return out


def resolve_pid(source: str, name_pid: dict) -> str:
    for name, pid in name_pid.items():
        if source and (source in name or name in source):
            return pid
    return source or "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUTPUT_FILE))
    args = ap.parse_args()

    plan = json.loads(PLAN_FILE.read_text(encoding="utf-8")) if PLAN_FILE.exists() else {}
    out_dir = HERE / "output"
    inv_pids = load_inv_pids()
    files = [f for f in sorted(out_dir.glob("mdt-*.json"))
             if f.name != "mdt-live.json" and ".prev" not in f.name]
    if not files:
        raise SystemExit("No per-device capture files (output/mdt-<PID>.json) yet.")

    # aggregate[(pid, path)] = {pid, source, category, records, fields{...}}
    aggregate: dict[tuple, dict] = {}
    sig_seen: dict[tuple, set] = {}  # (pid,path) -> set of instance signatures
    for f in files:
        pid = pid_from_file(f.name, inv_pids)
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            tags = rec.get("tags", {})
            path = tags.get("path") or rec.get("name", "")
            if not path:
                continue
            key = (pid, path)
            entry = aggregate.setdefault(key, {
                "pid": pid, "source": tags.get("source", ""), "category": category_of(path),
                "path": path, "records": 0, "instances": 0, "keys": {}, "fields": {}, "samples": [],
            })
            entry["records"] += 1

            # This record's list keys (tags) and leaf fields.
            rkeys = {tk: tv for tk, tv in tags.items()
                     if tk not in ("path", "source", "subscription")}
            rfields = dict(rec.get("fields") or {})

            # Signature identifies a distinct list instance (e.g. one interface).
            sig = (tuple(sorted(rkeys.items())) if rkeys
                   else ("_leaf_" + "|".join(sorted(rfields.keys())),))
            seen = sig_seen.setdefault(key, set())
            if sig not in seen:
                seen.add(sig)
                entry["instances"] += 1
                if len(entry["samples"]) < MAX_SAMPLES:
                    entry["samples"].append({
                        "keys": {k: v for k, v in list(rkeys.items())[:12]},
                        "fields": {k: v for k, v in list(rfields.items())[:MAX_FIELDS_PER_PATH]},
                    })

            # Backward-compatible first-instance summary.
            if not entry["keys"] and rkeys:
                entry["keys"] = {k: v for k, v in list(rkeys.items())[:12]}
            for fname, fval in rfields.items():
                if len(entry["fields"]) < MAX_FIELDS_PER_PATH and fname not in entry["fields"]:
                    entry["fields"][fname] = fval

    paths = sorted(aggregate.values(), key=lambda e: (e["pid"], e["category"], e["path"]))

    # Device + category rollups.
    dev_paths = collections.Counter()
    dev_records = collections.Counter()
    dev_cat = collections.defaultdict(lambda: collections.Counter())
    cat_paths = collections.Counter()
    sources = {}
    for e in paths:
        dev_paths[e["pid"]] += 1
        dev_records[e["pid"]] += e["records"]
        dev_cat[e["pid"]][e["category"]] += 1
        cat_paths[e["category"]] += 1
        sources[e["pid"]] = e["source"]

    devices = [{
        "pid": pid, "source": sources.get(pid, ""),
        "paths": dev_paths[pid], "records": dev_records[pid],
        "by_category": dict(dev_cat[pid]),
    } for pid in sorted(dev_paths)]
    categories = [{"category": c, "paths": cat_paths[c]} for c in sorted(cat_paths)]

    dataset = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "live fleet capture (Telegraf cisco_telemetry_mdt)",
        "receiver": plan.get("receiver", ""),
        "transport": "gRPC dial-out (TCP/57500, kvGPB)",
        "capture": "periodic yang-push",
        "totals": {
            "devices": len(devices),
            "paths": len(paths),
            "records": sum(dev_records.values()),
        },
        "devices": devices,
        "categories": categories,
        "paths": paths,
    }

    out = Path(args.out)
    out.write_text(json.dumps(dataset, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    kb = out.stat().st_size / 1024
    print(f"devices={len(devices)} paths={len(paths)} records={dataset['totals']['records']}")
    for d in devices:
        print(f"  {d['pid']:14} paths={d['paths']:4} {d['by_category']}")
    print(f"wrote {out.name} ({kb:.1f} KB)")


if __name__ == "__main__":
    raise SystemExit(main())
