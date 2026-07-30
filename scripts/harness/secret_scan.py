"""Secret-scan guard for the harness (DEVICE_DATA_COLLECTION.md §6).

Regex-based detector for obvious secrets that must never be committed. Used by
the test suite over anything that could be staged (scrubbed captures, example
files) and reusable as a pre-commit check.
"""
from __future__ import annotations

import re
from pathlib import Path

# (label, pattern) pairs. Patterns intentionally target real secret material,
# not lab identifiers (IPs/MACs/serials/hostnames are allowed per §6).
_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("certificate_block", re.compile(r"-----BEGIN CERTIFICATE-----")),
    ("password_field", re.compile(r'"[^"]*pass(word|wd)?"\s*:\s*"(?!\*\*\*REDACTED\*\*\*)[^"]+"', re.IGNORECASE)),
    ("secret_field", re.compile(r'"[^"]*secret"\s*:\s*"(?!\*\*\*REDACTED\*\*\*)[^"]+"', re.IGNORECASE)),
    ("snmp_community", re.compile(r'"[^"]*community[^"]*"\s*:\s*"(?!\*\*\*REDACTED\*\*\*)[^"]+"', re.IGNORECASE)),
    ("preshared_key", re.compile(r'"[^"]*(pre-?shared-?key|psk)"\s*:\s*"(?!\*\*\*REDACTED\*\*\*)[^"]+"', re.IGNORECASE)),
]


def find_secrets(text: str) -> list[tuple[str, str]]:
    """Return a list of (label, matched_snippet) for any secret found in ``text``."""
    hits: list[tuple[str, str]] = []
    for label, pat in _PATTERNS:
        for m in pat.finditer(text):
            hits.append((label, m.group(0)[:80]))
    return hits


def scan_file(path: Path) -> list[tuple[str, str]]:
    try:
        return find_secrets(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return []
