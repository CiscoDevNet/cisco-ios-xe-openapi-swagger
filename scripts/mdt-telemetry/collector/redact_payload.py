#!/usr/bin/env python3
"""redact_payload.py — payload-level secret redaction for the collector datasets.

The Device Data dataset builders embed raw device payloads: NETCONF (XML) and
gNMI (json_ietf) as inline strings, RESTCONF as a parsed JSON object. Those
strings/objects are never seen by scripts/harness/redact.py (which only masks
dict values by key at capture time), so secrets nested inside a builder's
embedded payload would ship in cleartext. This module masks the *values* of
secret-named XML elements / JSON keys inside payload strings, secret-named leaves
inside parsed objects, and PEM blocks anywhere.

  * redact_payload(str) -> str      NETCONF XML / gNMI json_ietf payload strings
  * redact_obj(obj)     -> obj      RESTCONF parsed value (deep, key-based)
  * redact_value(v)     -> v        dispatch on type
  * scan_text(str)      -> [(label, snippet)]  unmasked secret finder (gate)

Standalone (reproducibility): rewrite the payloads inside collector/dataset files.

    redact_payload.py --entries output/netconf-*.json      # entries[].payload
    redact_payload.py --dataset ../../../netconf-get-live-data.json  # paths[].payload
"""
from __future__ import annotations

import argparse
import glob
import json
import re
from typing import Any

REDACTED = "***REDACTED***"

# Secret leaf-name patterns (superset of harness/redact.py, incl. short IGP/BGP
# key leaves that appear as <module>:key-string etc.).
SECRET = re.compile(
    r"(password|passwd|secret|pre-?shared-?key|psk|community|"
    r"auth-?key|priv-?key|private-?key|priv-?password|auth-?password|"
    r"token|api-?key|shared-?secret|encryption-?key|wpa-?key|credential|"
    r"key-string|message-digest-key|authentication-key|hello-authentication-key)",
    re.IGNORECASE,
)
# Short leaves that are secrets but too generic for substring matching — matched
# exactly (after stripping any "module:" prefix) to avoid masking "keyword" etc.
SECRET_EXACT = {"key", "md5"}
PEM = re.compile(r"-----BEGIN [^-]+-----.*?-----END [^-]+-----", re.DOTALL)


def _leaf(name: str) -> str:
    """Local name: strip a leading YANG module prefix (Module:leaf -> leaf)."""
    return name.split(":")[-1]


def _is_secret_name(name: str, exact: bool = True) -> bool:
    """Secret leaf-name test. ``exact`` also matches the generic short leaves
    ({key, md5}); disable it for the gate, where bare ``key`` collides with
    structural field names (e.g. the matrix method list's "key":"mdt")."""
    local = _leaf(name)
    if SECRET.search(local):
        return True
    return exact and local.lower() in SECRET_EXACT


def _mask_xml(s: str) -> str:
    def repl(m: re.Match) -> str:
        tag, val = m.group("tag"), m.group("val")
        if val and "<" not in val and _is_secret_name(tag):
            return f"{m.group('open')}{REDACTED}</{tag}>"
        return m.group(0)

    return re.sub(
        r"(?P<open><(?P<tag>[A-Za-z0-9_.:-]+)(?:\s[^>]*)?>)(?P<val>[^<]*)</(?P=tag)>",
        repl, s)


def _mask_json(s: str) -> str:
    def repl(m: re.Match) -> str:
        if _is_secret_name(m.group("key")):
            return f'{m.group("pre")}"{REDACTED}"'
        return m.group(0)

    return re.sub(
        r'(?P<pre>"(?P<key>[A-Za-z0-9_.:\-]+)"\s*:\s*)"(?:[^"\\]|\\.)*"',
        repl, s)


def redact_payload(s: Any) -> Any:
    """Mask secrets inside an embedded payload STRING (XML or JSON)."""
    if not s or not isinstance(s, str):
        return s
    s = PEM.sub(REDACTED, s)
    s = _mask_xml(s)
    s = _mask_json(s)
    return s


def redact_obj(obj: Any) -> Any:
    """Deep-mask secrets inside a parsed RESTCONF value (key-based)."""
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            out[k] = REDACTED if isinstance(k, str) and _is_secret_name(k) else redact_obj(v)
        return out
    if isinstance(obj, list):
        return [redact_obj(v) for v in obj]
    if isinstance(obj, str):
        return PEM.sub(REDACTED, obj)
    return obj


def redact_value(v: Any) -> Any:
    return redact_payload(v) if isinstance(v, str) else redact_obj(v)


def scan_text(text: str) -> list[tuple[str, str]]:
    """Return (label, snippet) for any UNMASKED secret-named value in ``text``.

    Guards committed datasets against a re-leak — mirrors the JSON/XML shapes the
    builders emit; ``***REDACTED***`` values are ignored.
    """
    hits: list[tuple[str, str]] = []
    for m in PEM.finditer(text):
        if REDACTED not in m.group(0):
            hits.append(("pem_block", m.group(0)[:80]))
    # JSON "key": "value"
    for m in re.finditer(r'"(?P<key>[A-Za-z0-9_.:\-]+)"\s*:\s*"(?P<val>(?:[^"\\]|\\.)*)"', text):
        if _is_secret_name(m.group("key"), exact=False) and m.group("val") not in ("", REDACTED):
            hits.append(("json_secret", m.group(0)[:80]))
    # XML <tag>value</tag>
    for m in re.finditer(r"<(?P<tag>[A-Za-z0-9_.:-]+)(?:\s[^>]*)?>(?P<val>[^<]+)</(?P=tag)>", text):
        if _is_secret_name(m.group("tag"), exact=False) and m.group("val") != REDACTED:
            hits.append(("xml_secret", m.group(0)[:80]))
    return hits


def _process(path: str, field_list: str) -> None:
    doc = json.loads(open(path, encoding="utf-8").read())
    n = 0
    for e in doc.get(field_list, []):
        p = e.get("payload")
        if isinstance(p, str) and p:
            r = redact_payload(p)
            if r != p:
                n += 1
                e["payload"] = r
    if field_list == "paths":  # repo-root datasets use the builders' compact style
        text = json.dumps(doc, separators=(",", ":"), ensure_ascii=False) + "\n"
    else:
        text = json.dumps(doc, ensure_ascii=False)
    open(path, "w", encoding="utf-8").write(text)
    print(f"{path}: redacted {n} payloads")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entries", nargs="*", default=[], help="collector output/*.json (entries[].payload)")
    ap.add_argument("--dataset", nargs="*", default=[], help="repo-root *-live-data.json (paths[].payload)")
    args = ap.parse_args()
    for pat in args.entries:
        for f in glob.glob(pat):
            _process(f, "entries")
    for pat in args.dataset:
        for f in glob.glob(pat):
            _process(f, "paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
