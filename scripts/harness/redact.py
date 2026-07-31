"""Light redaction for captured RESTCONF responses (DEVICE_DATA_COLLECTION.md §6).

Redaction level = LIGHT: strip obvious secrets only (passwords, community
strings, certificates, private keys, tokens/keys). IPs / serials / MACs /
hostnames are KEPT (lab data) unless a stricter classification is chosen later.

Raw captures stay LOCAL + gitignored regardless; this scrubber exists so that
IF a capture is ever staged for commit it can be run first, and so the
in-memory response written to disk never carries a plaintext secret.
"""
from __future__ import annotations

import re
from typing import Any

REDACTED = "***REDACTED***"

# Leaf-name substrings whose *values* are secrets and must be masked.
_SECRET_KEY_PATTERNS = re.compile(
    r"(password|passwd|secret|pre-?shared-?key|psk|community|"
    r"auth-?key|priv-?key|private-?key|priv-?password|auth-?password|"
    r"token|api-?key|shared-?secret|encryption-?key|wpa-?key|"
    r"credential)",
    re.IGNORECASE,
)

# Ambiguous short leaf names that hold a secret only as an exact match, so we
# don't over-redact names like "key-id", "primary-key", "public-key",
# "keychain-name". These cover radius/tacacs server ``key``, routing-auth
# ``md5`` / ``message-digest-key`` / ``authentication-key``, and key chains.
_EXACT_SECRET_KEYS = {
    "key", "md5", "key-string", "message-digest-key",
    "authentication-key", "hello-authentication-key",
}


def _is_secret_key(key: str) -> bool:
    # RESTCONF keys are often module-qualified (e.g. "Cisco-IOS-XE-aaa:key");
    # match against the local leaf name too so a prefix can't dodge redaction.
    local = key.rsplit(":", 1)[-1]
    return (
        bool(_SECRET_KEY_PATTERNS.search(key))
        or key.lower() in _EXACT_SECRET_KEYS
        or local.lower() in _EXACT_SECRET_KEYS
    )

# Multiline blobs to mask by value pattern (PEM keys/certs) regardless of key.
_PEM_BLOCK = re.compile(
    r"-----BEGIN [^-]+-----.*?-----END [^-]+-----",
    re.DOTALL,
)


def _redact_string(value: str) -> str:
    if _PEM_BLOCK.search(value):
        return _PEM_BLOCK.sub(REDACTED, value)
    return value


def redact(obj: Any) -> Any:
    """Return a deep-copied, light-redacted version of ``obj``.

    - dict values whose key matches a secret pattern -> REDACTED
    - any string containing a PEM block -> REDACTED
    - recurses through dicts and lists
    """
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, val in obj.items():
            if isinstance(key, str) and _is_secret_key(key):
                out[key] = REDACTED
            else:
                out[key] = redact(val)
        return out
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    if isinstance(obj, str):
        return _redact_string(obj)
    return obj
