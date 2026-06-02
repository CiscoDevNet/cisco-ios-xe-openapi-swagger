#!/usr/bin/env python3
"""
Generate releases/<ver>/platform-support.json from YangModels yang-set files
(NETCONF yang-library <modules-state> dumps).  Falls back to capability-*.xml
parsing when a yang-set file is missing.

Inputs:  references/yang/vendor/cisco/xe/<token>/yang-set-<platform>.xml
         references/yang/vendor/cisco/xe/<token>/capability-<platform>.xml (fallback)
         releases/index.json (for ver -> yangmodels_path mapping)

Output:  releases/<ver>/platform-support.json
         {
           "release": "26.1.1",
           "platforms": [{"id":"cat9k","label":"...","family":"switching"}, ...],
           "modules": { "<module-name>": { "platforms": [...], "revision": "YYYY-MM-DD" }, ... },
           "generated_from": ["yang-set-cat9k.xml", ...]
         }

Also produces top-level platform-support-index.json:
         { "releases": ["26.1.1", "17.18.1", ...], "default": "26.1.1" }
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(ROOT, "references", "yang")
RELEASES = os.path.join(ROOT, "releases")
INDEX_PATH = os.path.join(RELEASES, "index.json")

# id -> (display label, family)
PLATFORM_META = {
    # Switching
    "cat9k":    ("Catalyst 9300/9400/9500/9600", "switching"),
    "cat9200":  ("Catalyst 9200",                "switching"),
    "cat9300":  ("Catalyst 9300",                "switching"),
    "cat9400":  ("Catalyst 9400",                "switching"),
    "cat9500":  ("Catalyst 9500",                "switching"),
    "cat9600":  ("Catalyst 9600",                "switching"),
    # Routing
    "asr1k":    ("ASR 1000",                     "routing"),
    "asr900":   ("ASR 900",                      "routing"),
    "c8000v":   ("Catalyst 8000V",               "routing"),
    "c8200":    ("Catalyst 8200",                "routing"),
    "c8300":    ("Catalyst 8300",                "routing"),
    "c8500":    ("Catalyst 8500",                "routing"),
    "isr1k":    ("ISR 1000",                     "routing"),
    "isr4k":    ("ISR 4000",                     "routing"),
    # IoT / Industrial / Edge
    "ir1101":   ("IR 1101",                      "iot"),
    "ess3x00":  ("ESS 3300",                     "iot"),
    "ie3x00":   ("IE 3x00",                      "iot"),
    # Wireless
    "wireless": ("Catalyst 9800 WLC",            "wireless"),
}

# Filename: capability-<id>.xml  or  yang-set-<id>.xml
CAP_RE = re.compile(r"^capability-(.+)\.xml$", re.IGNORECASE)
SET_RE = re.compile(r"^yang-set-(.+)\.xml$", re.IGNORECASE)

# yang-set entry: <module><name>X</name><revision>YYYY-MM-DD</revision>...
MODULE_BLOCK_RE = re.compile(
    r"<module>\s*<name>([^<]+)</name>\s*(?:<revision>([^<]*)</revision>)?",
    re.IGNORECASE,
)


def parse_yang_set_file(path):
    """Return list of (module_name, revision_or_None) from a yang-set XML."""
    out = []
    seen = set()
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return out
    for m in MODULE_BLOCK_RE.finditer(text):
        name = m.group(1).strip()
        rev = (m.group(2) or "").strip() or None
        if not name or name in seen:
            continue
        seen.add(name)
        out.append((name, rev))
    return out


# Capability URL: ...?module=<name>[&revision=YYYY-MM-DD][...]
def parse_capability_file(path):
    """Return list of (module_name, revision_or_None) tuples found in a capability XML.
    Used only as a fallback when yang-set-<id>.xml is unavailable."""
    out = []
    seen = set()
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return out
    text = text.replace("&amp;", "&")
    for m in re.finditer(r"\?([^<>\"' \t\r\n]+)", text):
        qs = m.group(1)
        params = {}
        for part in qs.split("&"):
            if "=" not in part:
                continue
            k, v = part.split("=", 1)
            params[k] = v
        mod = params.get("module")
        if not mod or mod in seen:
            continue
        seen.add(mod)
        rev = params.get("revision")
        out.append((mod, rev))
    return out


def load_release_index():
    with open(INDEX_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def build_for_release(rel):
    ver = rel["ver"]
    ym_path = rel.get("yangmodels_path")
    if not ym_path:
        print(f"  SKIP {ver}: no yangmodels_path")
        return None
    cap_dir = os.path.join(REFS, ym_path)
    if not os.path.isdir(cap_dir):
        print(f"  SKIP {ver}: missing {cap_dir}")
        return None

    # Prefer yang-set-*.xml (full yang-library module list).
    # Fall back to capability-*.xml only for platforms with no yang-set file.
    set_files = sorted(glob.glob(os.path.join(cap_dir, "yang-set-*.xml")))
    cap_files = sorted(glob.glob(os.path.join(cap_dir, "capability-*.xml")))
    if not set_files and not cap_files:
        print(f"  SKIP {ver}: no yang-set-*.xml or capability-*.xml in {cap_dir}")
        return None

    # Build platform -> source-file map: yang-set wins, capability fills gaps.
    sources = {}  # pid -> (path, kind)  kind in {"yang-set", "capability"}
    for sf in set_files:
        m = SET_RE.match(os.path.basename(sf))
        if not m:
            continue
        pid = m.group(1).lower()
        if os.path.getsize(sf) == 0:
            continue
        sources[pid] = (sf, "yang-set")
    for cf in cap_files:
        m = CAP_RE.match(os.path.basename(cf))
        if not m:
            continue
        pid = m.group(1).lower()
        if pid in sources:
            continue
        if os.path.getsize(cf) == 0:
            continue
        sources[pid] = (cf, "capability")

    modules = defaultdict(lambda: {"platforms": set(), "revision": None})
    platforms_seen = []
    files_used = []

    for pid in sorted(sources):
        path, kind = sources[pid]
        name = os.path.basename(path)
        if pid not in PLATFORM_META:
            print(f"  {ver}: WARN unknown platform id '{pid}' in {name} — add to PLATFORM_META")
            PLATFORM_META[pid] = (pid, "other")
        platforms_seen.append(pid)
        files_used.append(name)
        entries = (parse_yang_set_file(path) if kind == "yang-set"
                   else parse_capability_file(path))
        for mod, rev in entries:
            modules[mod]["platforms"].add(pid)
            if rev and not modules[mod]["revision"]:
                modules[mod]["revision"] = rev

    # Sort + serialize
    platforms_out = []
    for pid in sorted(platforms_seen, key=lambda p: (PLATFORM_META[p][1], p)):
        label, family = PLATFORM_META[pid]
        platforms_out.append({"id": pid, "label": label, "family": family})

    modules_out = {}
    for mod in sorted(modules):
        info = modules[mod]
        modules_out[mod] = {
            "platforms": sorted(info["platforms"]),
            "revision": info["revision"],
        }

    doc = {
        "release": ver,
        "platforms": platforms_out,
        "modules": modules_out,
        "generated_from": files_used,
    }
    return doc


def main():
    idx = load_release_index()
    out_releases = []
    for rel in idx.get("releases", []):
        ver = rel["ver"]
        doc = build_for_release(rel)
        if doc is None:
            continue
        out_dir = os.path.join(RELEASES, ver)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "platform-support.json")
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, sort_keys=False)
        print(f"  {ver}: {len(doc['platforms'])} platforms, {len(doc['modules'])} modules -> {os.path.relpath(out_path, ROOT)}")
        out_releases.append(ver)

    # Tiny top-level index so the UI can know which releases have data without probing.
    top = {
        "default": idx.get("default"),
        "releases": out_releases,
    }
    top_path = os.path.join(ROOT, "platform-support-index.json")
    with open(top_path, "w", encoding="utf-8") as fh:
        json.dump(top, fh, indent=2)
    print(f"top-level index: {os.path.relpath(top_path, ROOT)}  ({len(out_releases)} releases)")


if __name__ == "__main__":
    main()
