"""Redaction for captured RESTCONF responses (DEVICE_DATA_COLLECTION.md §6).

Thin wrapper over the shared rules in scripts/mdt-telemetry/collector/redact_payload.py,
so capture-time, publish-time and dataset-build redaction can never drift apart.
Secrets (passwords, keys, communities, crypt hashes, PEM blocks, CLI secrets) and
usernames tied to credentials are replaced with the fixed token ``***REDACTED***``.
IPs / serials / MACs / hostnames are kept (lab data).

Raw captures stay LOCAL + gitignored regardless; this scrubber exists so that
IF a capture is ever staged for commit it can be run first, and so the
in-memory response written to disk never carries a plaintext secret.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_COLLECTOR = Path(__file__).resolve().parents[1] / "mdt-telemetry" / "collector"
if str(_COLLECTOR) not in sys.path:
    sys.path.insert(0, str(_COLLECTOR))

import redact_payload as _rules  # noqa: E402

REDACTED = _rules.REDACTED


def _is_secret_key(key: str) -> bool:
    return _rules._is_secret_name(key)


def redact(obj: Any) -> Any:
    """Return a deep-copied, redacted version of ``obj`` (dicts, lists, strings)."""
    return _rules.redact_obj(obj)
