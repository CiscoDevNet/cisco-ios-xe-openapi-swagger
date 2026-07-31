"""depth_probe.py — does GETting a deeper path return MORE data than the parent?

Some IOS XE oper subtrees are NOT populated in a shallow/root GET: the parent
returns the container skeleton but a nested list comes back empty, and the real
data only appears when you GET the keyed deeper path directly (e.g.
platform-oper components/component=<key>/platform-properties/platform-property).
Other deeper paths are redundant (identical to the parent slice).

This probe answers "gives more data or not" empirically: it reads a captured
parent list, builds the concrete keyed child paths (percent-encoding key values
per RFC 8040), GETs each directly on ONE device, and classifies the result vs.
the parent slice: ADDS_DATA / REDUNDANT / EMPTY / ERROR.

Strictly READ-ONLY (GET only). Usage:
    python -X utf8 -m scripts.harness.depth_probe \
        --device C9600 \
        --parent-path /data/Cisco-IOS-XE-platform-oper:components/component \
        --key-leaf cname \
        --child platform-properties/platform-property \
        --child platform-subcomponents/platform-subcomponent
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
from pathlib import Path

import requests

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.harness import inventory as inv
    from scripts.harness import redact as redaction
    from scripts.harness.request import RESTCONF_HEADERS
else:  # pragma: no cover
    from . import inventory as inv
    from . import redact as redaction
    from .request import RESTCONF_HEADERS

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Leaf names to try as a list key when none is given (data-driven inference).
_KEY_HINTS = ("name", "cname", "id", "index", "number", "if-name", "interface-name")


def _encode_key(value) -> str:
    """Percent-encode a single list-key value (RFC 8040): '/', ':', space, etc.
    must be escaped so they are not read as path separators."""
    return urllib.parse.quote(str(value), safe="")


def _deep_url(host, port, deep_path) -> str:
    """Absolute RESTCONF URL for an already-key-encoded deep path.

    The key value is pre-encoded by ``_encode_key``; we must NOT re-quote it (that
    would turn ``%2F`` into ``%252F`` and the device would 404). Structural
    segments here contain only URL-safe characters, so append verbatim.
    """
    return f"https://{host.strip()}:{int(port)}/restconf{deep_path}"


def _unwrap(body):
    """Strip a single top-level module-prefixed wrapper key if present, so two
    responses can be compared on their content, not their envelope."""
    if isinstance(body, dict) and len(body) == 1:
        return next(iter(body.values()))
    return body


def _load_parent(version: str, parent_path: str, pid: str):
    """Return the captured parent list entries for ``pid`` from the sidecar."""
    sidecar = PROJECT_ROOT / "references" / f"live-examples-{version}.json"
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    for e in data.get("entries", []):
        if e.get("path") == parent_path and pid in (e.get("pids") or {}):
            val = _unwrap(e["pids"][pid]["value"])
            # val is the list (array) or a dict wrapping the list
            if isinstance(val, list):
                return val
            if isinstance(val, dict):
                for v in val.values():
                    if isinstance(v, list):
                        return v
    return []


def _pick_key_leaf(entries, override):
    if override:
        return override
    if entries and isinstance(entries[0], dict):
        for hint in _KEY_HINTS:
            if hint in entries[0]:
                return hint
    return None


def _slice(entry, child):
    """The parent's view of ``child`` (dotted/slashed) for this entry."""
    cur = entry
    for seg in child.split("/"):
        if isinstance(cur, dict) and seg in cur:
            cur = cur[seg]
        else:
            return None
    return cur


def _key_structure(node, prefix=""):
    """Recursive SET of key-paths (structure only, ignoring scalar values), so two
    oper responses can be compared without volatile counters causing false diffs."""
    keys = set()
    if isinstance(node, dict):
        for k, v in node.items():
            kp = f"{prefix}/{k}"
            keys.add(kp)
            keys |= _key_structure(v, kp)
    elif isinstance(node, list):
        for item in node:
            keys |= _key_structure(item, prefix + "[]")
    return keys


def _classify(parent_slice, got_body):
    got = _unwrap(got_body)
    got_empty = got in (None, {}, [], "")
    par_empty = parent_slice in (None, {}, [], "")
    if got_empty:
        return "EMPTY"
    if par_empty and not got_empty:
        return "ADDS_DATA"
    # Compare STRUCTURE, not values: volatile oper counters differ between
    # capture time and probe time, but that is not "more data".
    extra = _key_structure(got) - _key_structure(parent_slice)
    if extra:
        return "ADDS_DATA"
    return "REDUNDANT"


def probe(device, auth, parent_path, key_leaf, children, limit):
    entries = _load_parent(args_version, parent_path, device.pid)
    key_leaf = _pick_key_leaf(entries, key_leaf)
    if not key_leaf:
        print(f"[probe] could not determine key leaf for {parent_path}", file=sys.stderr)
        return {}
    print(f"[probe] {device.pid} {parent_path} — {len(entries)} parent entries, key leaf '{key_leaf}'")

    sess = requests.Session()
    sess.trust_env = False  # ignore the corp http proxy; devices are reachable directly

    results = []
    tally = {"ADDS_DATA": 0, "REDUNDANT": 0, "EMPTY": 0, "ERROR": 0}
    probed = 0
    for entry in entries:
        key_val = entry.get(key_leaf)
        if key_val is None:
            continue
        for child in children:
            deep_path = f"{parent_path}={_encode_key(key_val)}/{child}"
            url = _deep_url(device.host, device.port, deep_path)
            status = None
            try:
                r = sess.get(url, headers=RESTCONF_HEADERS, auth=auth, verify=False, timeout=30)
                status = r.status_code
                if r.status_code == 404:
                    cls = "EMPTY"
                    body = None
                elif r.status_code >= 400:
                    cls = "ERROR"
                    body = None
                else:
                    body = r.json() if r.text.strip() else None
                    cls = _classify(_slice(entry, child), body)
            except (requests.RequestException, ValueError) as exc:
                cls = "ERROR"
                body = None
                print(f"  ! {key_val} /{child}: {exc}", file=sys.stderr)
            tally[cls] += 1
            probed += 1
            results.append({
                "key": key_val, "child": child, "path": deep_path,
                "status": status,
                "class": cls,
                "sample": redaction.redact(_unwrap(body)) if cls == "ADDS_DATA" else None,
            })
        if limit and probed >= limit:
            break
    return {"key_leaf": key_leaf, "tally": tally, "results": results}


# --------------------------------------------------------------------------- #
# Discovery: which captured modules HIDE data behind keyed lists?
# For every captured value we find nodes that are EMPTY at parent depth (empty
# list `[]` or empty container `{}`), build their fully key-qualified RESTCONF
# path, GET it directly, and see whether the device returns data there. Modules
# with any such "hidden" data are the ones that "act this way".
# --------------------------------------------------------------------------- #

def _spec_keymap(version: str, category: str, module: str) -> dict:
    """node-name -> key-leaf, parsed from the spec's ``.../<node>={param}`` paths."""
    api = PROJECT_ROOT / "releases" / version / f"swagger-{category}-model" / "api" / f"{module}.json"
    keymap: dict[str, str] = {}
    try:
        spec = json.loads(api.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return keymap
    for p in spec.get("paths", {}):
        for seg in p.split("/"):
            if "={" in seg:
                node, param = seg.split("=", 1)
                keymap.setdefault(node.split(":")[-1], param.strip("{}").split(",")[0].split("{")[-1])
    return keymap


def _schema_names(path: str) -> tuple:
    """Sequence of local node-names from a /data/ path (drop keys + module prefix)."""
    body = path[len("/data/"):] if path.startswith("/data/") else path.lstrip("/")
    names = []
    for seg in body.split("/"):
        seg = seg.split("=")[0].split(":")[-1]
        if seg:
            names.append(seg)
    return tuple(names)


def _spec_child_map(version: str, category: str, module: str) -> dict:
    """schema-path tuple -> set of immediate child node-names (containers/lists/leaves)."""
    api = PROJECT_ROOT / "releases" / version / f"swagger-{category}-model" / "api" / f"{module}.json"
    cmap: dict[tuple, set] = {}
    try:
        spec = json.loads(api.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return cmap
    for p in spec.get("paths", {}):
        if not p.startswith("/data/"):
            continue
        names = _schema_names(p)
        for i in range(1, len(names)):
            cmap.setdefault(names[:i], set()).add(names[i])
        cmap.setdefault(names, cmap.get(names, set()))
    return cmap


def _find_candidates(value, base_path, schema_path, keymap, child_map, max_entries, depth, out, cap):
    """Collect key-qualified candidate paths: EMPTY present nodes AND container/
    list children that are ABSENT from the data but defined in the spec."""
    if depth > 6 or len(out) >= cap:
        return
    node = _unwrap(value) if depth == 0 else value
    if not isinstance(node, dict):
        return
    present = {k.split(":")[-1] for k in node.keys()}
    # ABSENT container/list children (a child that itself has children in spec).
    for child in child_map.get(schema_path, set()):
        if child not in present and child_map.get(schema_path + (child,)):
            out.append({"path": f"{base_path}/{child}", "kind": "absent"})
            if len(out) >= cap:
                return
    for k, v in node.items():
        local = k.split(":")[-1]
        cpath = f"{base_path}/{local}"
        sp = schema_path + (local,)
        if isinstance(v, dict):
            if not v:
                out.append({"path": cpath, "kind": "empty"})
            else:
                _find_candidates(v, cpath, sp, keymap, child_map, max_entries, depth + 1, out, cap)
        elif isinstance(v, list):
            if not v:
                out.append({"path": cpath, "kind": "empty"})
            elif isinstance(v[0], dict):
                key_leaf = keymap.get(local) or _pick_key_leaf(v, None)
                if not key_leaf:
                    continue
                for entry in v[:max_entries]:
                    kv = entry.get(key_leaf)
                    if kv is None:
                        continue
                    kpath = f"{cpath}={_encode_key(kv)}"
                    _find_candidates(entry, kpath, sp, keymap, child_map, max_entries, depth + 1, out, cap)


def discover(device, auth, version, category, max_entries, cap_per_module, module_filter):
    sidecar = PROJECT_ROOT / "references" / f"live-examples-{version}.json"
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    # module -> module-root value for this device (shortest captured path per module)
    roots: dict = {}
    for e in data.get("entries", []):
        if category and e.get("category") != category:
            continue
        if module_filter and e.get("module") not in module_filter:
            continue
        pids = e.get("pids") or {}
        if device.pid not in pids:
            continue
        mod = e["module"]
        cur = roots.get(mod)
        if cur is None or len(e["path"]) < len(cur[0]):
            roots[mod] = (e["path"], e["category"], pids[device.pid]["value"])

    sess = requests.Session()
    sess.trust_env = False

    per_module = {}
    total_probes = 0
    for mod, (path, cat, value) in sorted(roots.items()):
        keymap = _spec_keymap(version, cat, mod)
        child_map = _spec_child_map(version, cat, mod)
        schema0 = _schema_names(path)
        cands: list = []
        _find_candidates(value, path, schema0, keymap, child_map, max_entries, 0, cands, cap_per_module)
        # dedup on path
        seen = set()
        cands = [c for c in cands if not (c["path"] in seen or seen.add(c["path"]))]
        if not cands:
            continue
        adds = 0
        adds_empty = 0
        adds_absent = 0
        samples = []
        for cand in cands:
            cpath = cand["path"]
            url = _deep_url(device.host, device.port, cpath)
            try:
                r = sess.get(url, headers=RESTCONF_HEADERS, auth=auth, verify=False, timeout=30)
                total_probes += 1
                if r.status_code == 200 and r.text.strip():
                    body = _unwrap(r.json())
                    if body not in (None, {}, [], ""):
                        adds += 1
                        adds_absent += cand["kind"] == "absent"
                        adds_empty += cand["kind"] == "empty"
                        if len(samples) < 3:
                            samples.append({"path": cpath, "kind": cand["kind"],
                                            "sample": redaction.redact(body)})
            except (requests.RequestException, ValueError):
                pass
        per_module[mod] = {"category": cat, "candidates": len(cands), "adds_data": adds,
                           "adds_empty": adds_empty, "adds_absent": adds_absent, "samples": samples}
        if adds:
            print(f"  {mod}: {len(cands)} candidate(s) probed, {adds} return data "
                  f"(absent={adds_absent} empty={adds_empty})  <== HIDES DATA")
    hiders = sum(1 for m in per_module.values() if m["adds_data"])
    print(f"\n[discover] {hiders} module(s) hide data (empty-node or absent-container) — "
          f"{total_probes} probes on {device.pid}.")
    return {"device": device.pid, "modules": per_module}


def main(argv=None) -> int:
    global args_version
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--version", default="26.1.1")
    ap.add_argument("--device", required=True, help="Device PID or name to probe (single device)")
    ap.add_argument("--discover", action="store_true",
                    help="Scan ALL captured modules for data hidden behind keyed lists (no --parent-path needed)")
    ap.add_argument("--category", help="Restrict discovery to one category (e.g. oper)")
    ap.add_argument("--module", action="append", dest="modules", help="Restrict discovery to module(s)")
    ap.add_argument("--max-entries", type=int, default=5, help="List entries sampled per list during discovery")
    ap.add_argument("--cap-per-module", type=int, default=400, help="Max candidate probes per module during discovery")
    ap.add_argument("--parent-path", help="OpenAPI path of the parent LIST (single-probe mode)")
    ap.add_argument("--key-leaf", help="List key leaf name (default: auto-detect from data)")
    ap.add_argument("--child", action="append", dest="children",
                    help="Child container/list path under each entry (repeatable), e.g. platform-properties/platform-property")
    ap.add_argument("--limit", type=int, help="Cap number of deep GETs (debug)")
    ap.add_argument("--out", help="Write full JSON result to this path")
    args = ap.parse_args(argv)
    args_version = args.version

    if not inv.credentials_available():
        print("Set IOSXE_USER and IOSXE_PASS.", file=sys.stderr)
        return 2
    devices = inv.load_inventory()
    match = [d for d in devices if args.device in (d.pid, d.name)]
    if not match:
        print(f"Device {args.device!r} not in inventory.", file=sys.stderr)
        return 2
    device = match[0]
    auth = inv.load_credentials()

    if args.discover:
        out = discover(device, auth, args.version, args.category,
                       args.max_entries, args.cap_per_module, set(args.modules or []))
        if args.out:
            Path(args.out).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
            print(f"[discover] wrote {args.out}")
        return 0

    if not args.parent_path or not args.children:
        print("Single-probe mode needs --parent-path and at least one --child (or use --discover).", file=sys.stderr)
        return 2

    out = probe(device, auth, args.parent_path, args.key_leaf, args.children, args.limit)
    if not out:
        return 1
    print(f"\n[probe] tally: {out['tally']}")
    adds = [r for r in out["results"] if r["class"] == "ADDS_DATA"]
    print(f"[probe] {len(adds)} path(s) return MORE data than the parent. Examples:")
    for r in adds[:5]:
        s = json.dumps(r["sample"])[:120]
        print(f"  + {r['child']} key={r['key']!r}: {s}")
    if not adds:
        print("  (none — every probed deeper path was redundant or empty)")
    if args.out:
        Path(args.out).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        print(f"[probe] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
