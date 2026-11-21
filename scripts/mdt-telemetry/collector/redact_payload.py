#!/usr/bin/env python3
"""redact_payload.py — the single set of secret-redaction rules for published device data.

Used by every Device Data dataset builder, by scripts/harness/redact.py (capture
time and publish-time re-scrub), by kit.py, and by the CI secret gate
(tests/test_dataset_secrets.py, tests/test_repo_secrets.py). A value is masked
with the fixed token ``***REDACTED***`` (nothing derived from the secret) when:

  * its leaf name is a secret: names are normalised first (split on ``/`` and
    ``:`` so module prefixes and telemetry path-joined keys can't hide a leaf;
    ``_`` -> ``-``), then matched by substring (password, secret, psk, ...),
    by exact short name (key, md5, pwd, ...), or structurally: any non-type leaf
    directly inside a secret container (``password/text``, ``key/key``,
    ``user-mgmt/*``), so ``{"password": {"enctype": "7", "text": "..."}}`` is
    masked while ``enctype`` is kept;
  * its leaf name is a username tied to credentials (username, user-name,
    ``username/name`` list keys, AP management users, SNMPv3 users);
  * its value is a Cisco crypt hash ($1$, $5$, $6$, $8$, $9$, $14$) or a PEM block;
  * it is the secret / username argument of an IOS XE CLI line (type 0/5/6/7/8/9
    passwords and secrets, keys, NTP / SNMPv3 / WPA / IKE / type-6 master keys,
    SNMP communities and hosts) — inside CLI text blobs anywhere.

  * redact_payload(str) -> str      NETCONF XML / gNMI json_ietf payload strings
  * redact_obj(obj)     -> obj      parsed RESTCONF / telemetry values (deep)
  * redact_value(v)     -> v        dispatch on type
  * mask_cli(str)       -> str      CLI config text
  * scan_text(str)      -> [(label, location)]  values redaction would still change (gate)

Standalone (reproducibility): rewrite the payloads inside collector/dataset files.

    redact_payload.py --entries output/netconf-*.json      # entries[].payload
    redact_payload.py --dataset ../../../netconf-get-live-data.json  # whole dataset
"""
from __future__ import annotations

import argparse
import glob
import html
import json
import re
from typing import Any

REDACTED = "***REDACTED***"
_NOT_REDACTED = r"(?!\*\*\*REDACTED\*\*\*)(?!\d+\s)"

# ------------------------------------------------------------------ leaf names
SECRET = re.compile(
    r"(password|passwd|secret|pre-?shared-?key|psk|community|"
    r"auth-?key|priv-?key|private-?key|priv-?password|auth-?password|"
    r"token|api-?key|shared-?secret|encryption-?key|wpa-?key|credential|"
    r"key-string|message-digest-key|authentication-key|hello-authentication-key|"
    r"hex-string|auth-string|authpass|privpass|key-clear-text|clear-key|server-key|unc-pwd)",
    re.IGNORECASE,
)
# Short leaves that are secrets only as an exact name (substring matching would
# mask key-id, keyword, public-key, keychain-name ...).
SECRET_EXACT = {"key", "md5", "pwd", "key-0", "key-6", "key-7", "ak-0", "ak-6", "ak-7"}
# Containers whose leaf children are all secret material, except the type leaves.
SECRET_CONTAINERS = {
    "password", "secret", "key", "md5", "key-string", "authentication-key", "message-digest-key",
    "pre-shared-key", "psk", "wpa-psk", "auth-key", "user-mgmt", "mgmtuser", "encrypted-password",
}
# Metadata leaves kept inside secret containers ("encryption": "7" says nothing secret).
TYPE_LEAVES = {
    "encryption", "enctype", "enc-type", "encryption-type", "type", "password-type", "key-type",
    "secret-type", "algorithm", "crypto-algorithm", "auth-type", "auth-algorithm", "hash-type",
    "password-encryption", "privilege", "id", "key-id", "index",
}
# Usernames tied to credentials (user asked for these to be published as REDACTED too).
USERNAME_LEAVES = {"username", "user-name", "login-name", "mgmt-user", "ap-mgmt-user", "dot1x-username"}
USERNAME_LISTS = {"username", "user", "users", "mgmtuser", "user-mgmt", "local-user"}

# ------------------------------------------------------------------ value patterns
PEM = re.compile(r"-----BEGIN [^-]+-----.*?-----END [^-]+-----", re.DOTALL)
CRYPT = re.compile(r"\$(?:1|5|6|8|9|14)\$[./A-Za-z0-9]{4,}(?:\$[./A-Za-z0-9]+)*")

# SNMP communities as data: CLI text and community-config list keys.
CLI_COMMUNITY = re.compile(
    r"(?P<pre>\b(?:snmp-server community|snmp-community-string)\s+)" + _NOT_REDACTED + r"(?P<val>[^\s\"'<\\]+)", re.I)
XML_COMMUNITY_NAME = re.compile(
    r"(?P<pre><community-config\b[^>]*>\s*<name>)" + _NOT_REDACTED + r"(?P<val>[^<]+)(?=</name>)")
JSON_COMMUNITY_NAME = re.compile(
    r'(?P<pre>\\?"(?:[A-Za-z0-9-]+:)?community-config\\?"\s*:\s*\[(?:[^\]\[]*?\{[^{}]*?)??\\?"name\\?"\s*:\s*\\?")'
    + _NOT_REDACTED + r'(?P<val>[^"\\]+)')
COMMUNITY_LISTS = {"community-config", "community"}

# CLI: specific forms first (their secret is not the token right after the keyword).
_V = _NOT_REDACTED + r"(\S+)"
CLI_SPECIFIC = [
    re.compile(r"\bntp authentication-key\s+\d+\s+\S+\s+" + _V, re.I),
    re.compile(r"\bsnmp-server user\s+" + _V, re.I),
    re.compile(r"\bsnmp-server user\s.*?\bauth\s+\S+\s+" + _V, re.I),
    re.compile(r"\bsnmp-server user\s.*?\bpriv\s+\S+(?:\s+\d+)?\s+" + _V, re.I),
    re.compile(r"\bsnmp-server host\s+\S+(?:\s+vrf\s+\S+)?(?:\s+(?:traps|informs))?(?:\s+version\s+(?:1|2c|3\s+(?:auth|noauth|priv)))?\s+"
               r"(?!version\b|traps\b|informs\b|vrf\b)" + _V, re.I),
    re.compile(r"\b(?:set-key|psk)\s+(?:ascii|hex)\s+\d\s+" + _V, re.I),
    re.compile(r"\bkey config-key password-encrypt\s+" + _V, re.I),
    re.compile(r"\bpre-shared-key\s+(?:local|remote)\s+(?:\d\s+)?" + _V, re.I),
    re.compile(r"\bauthentication\s+text\s+" + _V, re.I),
    re.compile(r"\b(?:username|mgmtuser username)\s+" + _V, re.I),
]
# Generic: the token after a secret keyword and an optional encryption-type digit.
CLI_SECRET = re.compile(
    r"(?P<pre>\b(?:secret|password|key-string|pre-shared-key|authentication-key|message-digest-key"
    r"(?:\s+\d+\s+md5)?|key|md5|community)\s+(?:[0-9]\s+)?)" + _NOT_REDACTED + r"(?P<val>\S+)", re.I)
# Qualifiers that follow a secret keyword without being the secret (handled above).
_CLI_QUALIFIERS = {
    "md5", "sha", "sha1", "sha256", "sha512", "ascii", "hex", "local", "remote", "address", "config-key",
    "chain", "encryption", "encrypted", "unencrypted", "clear", "aes", "des", "3des", "algorithm-type",
    "password-encrypt", "auth", "priv", "string", "text", "hidden", "scrypt", "sha256-secret", "level",
}


def _cli_line(line: str) -> str:
    for rx in CLI_SPECIFIC:
        line = rx.sub(lambda m: m.group(0)[: m.start(1) - m.start(0)] + REDACTED, line)

    def generic(m: re.Match) -> str:
        if m.group("val").lower() in _CLI_QUALIFIERS:
            return m.group(0)
        return m.group("pre") + REDACTED

    return CLI_SECRET.sub(generic, line)


def mask_cli(text: str) -> str:
    """Mask secrets and credential usernames in IOS XE CLI config text."""
    text = _mask_text(text)
    return "\n".join(_cli_line(line) for line in text.split("\n"))


def _mask_text(s: str) -> str:
    """Value patterns that are secrets wherever they appear."""
    s = PEM.sub(REDACTED, s)
    s = CRYPT.sub(REDACTED, s)
    s = CLI_COMMUNITY.sub(lambda m: m.group("pre") + REDACTED, s)
    s = XML_COMMUNITY_NAME.sub(lambda m: m.group("pre") + REDACTED, s)
    return re.sub(r'\\?"(?:[A-Za-z0-9-]+:)?community-config\\?"\s*:\s*\[[^\]]*\]',
                  lambda m: re.sub(r'(\\?"name\\?"\s*:\s*\\?")[^"\\]+', r'\g<1>' + REDACTED, m.group(0)), s)


def _segments(name: str) -> list[str]:
    return [p.lower().replace("_", "-") for p in re.split(r"[/:]", name or "") if p]


def _leaf(name: str) -> str:
    """Normalised local leaf name (module prefix and telemetry path stripped)."""
    segs = _segments(name)
    return segs[-1] if segs else ""


def _split(name: str, parent: str) -> tuple[str, str]:
    segs = _segments(name)
    leaf = segs[-1] if segs else ""
    up = segs[-2] if len(segs) > 1 else _leaf(parent)
    return leaf, up


def _is_secret_name(name: str, exact: bool = True, parent: str = "") -> bool:
    """Secret leaf test on a (possibly module-qualified or path-joined) name."""
    leaf, up = _split(name, parent)
    if not leaf or leaf in TYPE_LEAVES:
        return False
    if SECRET.search(leaf) or (exact and leaf in SECRET_EXACT):
        return True
    return _secret_container(up)


def _secret_container(name: str) -> bool:
    """Containers whose non-type children are secret (``password/text``, ``credential/value``)."""
    return name in SECRET_CONTAINERS or (bool(SECRET.search(name)) and "community" not in name)


def _is_username(name: str, parent: str, value: Any) -> bool:
    if not isinstance(value, str) or not re.search(r"[A-Za-z]", value) or value == REDACTED:
        return False
    leaf, up = _split(name, parent)
    return leaf in USERNAME_LEAVES or (leaf == "name" and up in USERNAME_LISTS)


# ------------------------------------------------------------------ structured data

_COUNTER_HINT = re.compile(r"(bad|unknown|invalid|fail|count|uses|names|err|attempts|expir|lifetime|"
                           r"length|history|age|max|min|retries|drops|total|wrong|mismatch|missing|busy|"
                           r"limit|reached|exclude|reason|inuse|index|prov-mode|buf)", re.I)


def _counter_value(name: str, v: Any) -> bool:
    """Numeric counters/settings whose names merely mention a secret (snmpInBadCommunityNames)."""
    numeric = isinstance(v, (int, float)) and not isinstance(v, bool) or (isinstance(v, str) and v.isdigit())
    return numeric and bool(_COUNTER_HINT.search(_leaf(name)))


def _community_container(name: str) -> bool:
    """SNMP community lists: only each entry's name is secret, not view / permission / host."""
    return "community" in _leaf(name)


def _mask_member(key: str, parent: str, v: Any) -> bool:
    """Should ``key: v`` (inside an object owned by ``parent``) be published as REDACTED?"""
    if not key or v in (None, "", [], {}) or v == REDACTED or isinstance(v, bool) or _counter_value(key, v):
        return False
    if isinstance(v, dict) or (isinstance(v, list) and any(isinstance(x, (dict, list)) for x in v)):
        return False  # recurse: secret leaves inside are masked by name or by their secret container
    if isinstance(v, (dict, list)) and _community_container(key) and not all(isinstance(x, str) for x in
                                                                               (v if isinstance(v, list) else [v])):
        return False
    if _is_secret_name(key, parent=parent) and not _exact_identifier(key, v):
        return True
    if _is_username(key, parent, v):
        return True
    return key == "name" and _leaf(parent) in COMMUNITY_LISTS and isinstance(v, str)


def redact_obj(obj: Any, _parent: str = "") -> Any:
    """Deep-mask a parsed RESTCONF / telemetry value; strings are scrubbed by content."""
    if isinstance(obj, dict):
        return {k: (REDACTED if _mask_member(k if isinstance(k, str) else "", _parent, v)
                    else redact_obj(v, k if isinstance(k, str) else ""))
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact_obj(v, _parent) for v in obj]
    if isinstance(obj, str):
        return redact_payload(obj)
    return obj


# ------------------------------------------------------------------ payload strings

_XML_TOKEN = re.compile(r"<(/?)([A-Za-z_][\w.:-]*)((?:\s[^<>]*?)?)(/?)>")


def _mask_xml(s: str) -> str:
    """Mask leaf text by element name and its parent element (works on truncated XML)."""
    out: list[str] = []
    stack: list[str] = []
    pos = 0
    for m in _XML_TOKEN.finditer(s):
        text = s[pos:m.start()]
        closing, name = m.group(1) == "/", _leaf(m.group(2))
        if text.strip() and closing and stack and stack[-1] == name and text != REDACTED:
            parent = stack[-2] if len(stack) > 1 else ""
            if _is_secret_name(name, parent=parent) or _is_username(name, parent, text.strip()):
                text = REDACTED
            elif _looks_like_cli(text):
                text = mask_cli(text)
        out.append(text)
        out.append(m.group(0))
        pos = m.end()
        if closing:
            while stack and stack.pop() != name:
                pass
        elif m.group(4) != "/":
            stack.append(name)
    out.append(s[pos:])
    return "".join(out)


_JSON_TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|[{}\[\]:,]|[^\s{}\[\]:,"]+')


def _mask_json(s: str) -> str:
    """Mask JSON values by key and parent key with a tokenizer (works on truncated JSON)."""
    tokens = list(_JSON_TOKEN.finditer(s))
    out: list[str] = []
    pos = 0
    # stack entries: [kind '{' or '[', key that opened it, secret container?]
    stack: list[list[Any]] = []
    key: str | None = None
    for i, m in enumerate(tokens):
        tok = m.group(0)
        out.append(s[pos:m.start()])
        pos = m.end()
        nxt = tokens[i + 1].group(0) if i + 1 < len(tokens) else ""
        in_obj = bool(stack) and stack[-1][0] == "{"
        if tok in "{[" and len(tok) == 1:
            owner = key if in_obj else (stack[-1][1] if stack else "")
            parent = stack[-1][1] if stack else ""
            secret = bool(owner) and _is_secret_name(owner, parent=parent) and not _community_container(owner)
            stack.append([tok, owner or "", secret or (bool(stack) and stack[-1][2])])
            key = None
            out.append(tok)
            continue
        if tok in "}]" and len(tok) == 1:
            if stack:
                stack.pop()
            key = None
            out.append(tok)
            continue
        if tok in ":," and len(tok) == 1:
            out.append(tok)
            continue
        if in_obj and tok.startswith('"') and nxt == ":" and key is None:
            key = _unquote(tok)
            out.append(tok)
            continue
        # a scalar value
        name = key if in_obj else (stack[-1][1] if stack else "")
        parent = stack[-1][1] if stack and in_obj else (stack[-2][1] if len(stack) > 1 else "")
        value = _unquote(tok) if tok.startswith('"') else tok
        container_secret = bool(stack) and stack[-1][2] and _leaf(name or "") not in TYPE_LEAVES
        if value not in ("", REDACTED, "null") and name and not _counter_value(name, value) and (
                container_secret or _is_secret_name(name, parent=parent) or _is_username(name, parent, value)
                or (name == "name" and _leaf(parent) in COMMUNITY_LISTS)):
            out.append(f'"{REDACTED}"')
        elif tok.startswith('"'):
            out.append(json.dumps(_mask_string_value(value), ensure_ascii=False) if _mask_string_value(value) != value
                       else tok)
        else:
            out.append(tok)
        key = None
    out.append(s[pos:])
    return "".join(out)


def _unquote(tok: str) -> str:
    try:
        return json.loads(tok)
    except ValueError:
        return tok.strip('"')


def _mask_string_value(v: str) -> str:
    return mask_cli(v) if _looks_like_cli(v) else _mask_text(v)


def redact_payload(s: Any) -> Any:
    """Mask secrets inside an embedded payload STRING (NETCONF XML or gNMI JSON)."""
    if not s or not isinstance(s, str):
        return s
    s = _mask_text(s)
    stripped = s.lstrip()
    if stripped[:1] in "{[":
        return _mask_json(s)
    if "<" in s and _XML_TOKEN.search(s):
        return _mask_xml(s)
    if _looks_like_cli(s):
        return mask_cli(s)
    return s


_CLI_MARKER = re.compile(r"^(?:!|hostname |interface |username |enable |snmp-server |aaa |tacacs|radius|line |"
                         r"crypto |key |ntp |router |ip |ipv6 |wireless |ap |wlan |version \d)", re.M)


def _looks_like_cli(s: str) -> bool:
    """Running-config text: several lines that start with IOS XE configuration keywords."""
    return "\n" in s and len(_CLI_MARKER.findall(s)) >= 2


def redact_value(v: Any) -> Any:
    return redact_payload(v) if isinstance(v, str) else redact_obj(v)


# ------------------------------------------------------------------ gate

def _exact_identifier(name: str, value: Any) -> bool:
    """Bare ``key`` / ``md5`` holding an identifier (protocol-matrix ``"key": "mdt"``) is not a secret."""
    return (_leaf(name) in SECRET_EXACT and isinstance(value, str)
            and re.fullmatch(r"[a-z]+(?:-[a-z]+)*", value) is not None)


def _scan_obj(orig: Any, path: str, hits: list[tuple[str, str]], parent: str = "") -> None:
    if isinstance(orig, dict):
        for k, v in orig.items():
            loc = f"{path}/{k}"
            if _mask_member(k if isinstance(k, str) else "", parent, v):
                hits.append(("secret_leaf", loc))
            else:
                _scan_obj(v, loc, hits, k if isinstance(k, str) else "")
    elif isinstance(orig, list):
        for i, v in enumerate(orig):
            _scan_obj(v, f"{path}[{i}]", hits, parent)
    elif isinstance(orig, str) and redact_payload(orig) != orig:
        hits.append(("embedded_secret", path))

def scan_text(text: str) -> list[tuple[str, str]]:
    """(label, location) for every value the redaction rules would still change.

    JSON documents are walked structurally, and string payloads (escaped NETCONF
    XML, gNMI JSON, CLI text) are decoded and checked too. Other text is HTML-unescaped
    and checked for value patterns and CLI secrets. Locations never include the value.
    """
    hits: list[tuple[str, str]] = []
    try:
        doc = json.loads(text)
    except ValueError:
        doc = None
    if doc is not None and not isinstance(doc, str):
        _scan_obj(doc, "", hits)
        return hits
    plain = html.unescape(text)
    for label, rx in (("pem_block", PEM), ("crypt_hash", CRYPT), ("snmp_community", CLI_COMMUNITY)):
        for m in rx.finditer(plain):
            if REDACTED not in m.group(0):
                hits.append((label, f"offset {m.start()}"))
    for n, line in enumerate(plain.split("\n"), 1):
        for m in _TYPED_CLI_SECRET.finditer(line):
            if not _placeholder(m.group(1)):
                hits.append(("cli_secret", f"line {n}"))
    return hits


_TYPED_CLI_SECRET = re.compile(r"\b(?:password|secret|key|key-string)\s+[05-9]\s+" + _NOT_REDACTED + r"([^\s\"'`<]+)")


def _placeholder(value: str) -> bool:
    """Documentation / fixture stand-ins, not real secrets."""
    v = value.strip("\"'`.,;:)(")
    return (not v or "fake" in v.lower() or "example" in v.lower() or "redacted" in v.lower()
            or v.startswith(("<", "$", "{", "*")) or set(v) <= set("*x.X-"))


# ------------------------------------------------------------------ CLI entry point

def _process(path: str, field_list: str) -> None:
    doc = json.loads(open(path, encoding="utf-8").read())
    if field_list == "paths":  # repo-root datasets: scrub the whole document
        new = _redact_doc(doc)
        text = json.dumps(new, separators=(",", ":"), ensure_ascii=False) + "\n"
    else:
        for e in doc.get(field_list, []):
            if isinstance(e.get("payload"), str):
                e["payload"] = redact_payload(e["payload"])
        new = doc
        text = json.dumps(doc, ensure_ascii=False)
    open(path, "w", encoding="utf-8").write(text)
    print(f"{path}: scrubbed")


def _redact_doc(obj: Any) -> Any:
    """Whole-dataset scrub: structured leaves by name, string payloads by content."""
    return redact_obj(obj)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entries", nargs="*", default=[], help="collector output/*.json (entries[].payload)")
    ap.add_argument("--dataset", nargs="*", default=[], help="repo-root *-live-data.json (whole document)")
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
