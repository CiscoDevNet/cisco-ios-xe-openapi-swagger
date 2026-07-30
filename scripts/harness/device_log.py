"""Optional device-side breadcrumb logger for crash diagnosis (Track B).

Opens an SSH session to the switch and, before each RESTCONF GET, runs an IOS XE
``send log`` exec command so the DEVICE's own console/syslog records exactly which
YANG module/path the harness is about to query. If a particular full-subtree GET
crashes the DMI/confd process, the last ``send log`` line on the device pinpoints
the offending module (the RESTCONF side just sees a timeout).

Uses netmiko (lightweight) rather than pyATS: this task is only "open SSH, send an
exec command", for which netmiko is sufficient and far lighter to install.

Intended to run at concurrency 1 so the device-side markers stay ordered with the
GETs. Credentials are the same IOSXE_USER/IOSXE_PASS used for RESTCONF.
"""
from __future__ import annotations

import re
import threading
from typing import Optional

# IOS XE `send log` syntax varies slightly by release; we auto-detect on connect.
_CANDIDATE_TEMPLATES = (
    "send log {sev} {msg}",
    "send log severity {sev} {msg}",
)
_ERROR_MARKERS = ("% Invalid input", "% Incomplete", "% Ambiguous", "% Unrecognized")
_MAX_MSG = 180


def sanitize_message(text: str) -> str:
    """Make a marker safe for one IOS command line (no quotes/newlines; bounded)."""
    text = re.sub(r"[\r\n\"']+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:_MAX_MSG]


class DeviceLogger:
    """SSH breadcrumb logger. Best-effort: never raises out of :meth:`mark`."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 22,
        severity: int = 6,
        device_type: str = "cisco_xe",
    ) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.severity = severity
        self.device_type = device_type
        self._conn = None
        self._template = _CANDIDATE_TEMPLATES[0]
        # Single SSH session is not thread-safe; serialize sends so the logger
        # can be shared across concurrent capture workers.
        self._lock = threading.Lock()

    def connect(self) -> None:
        from netmiko import ConnectHandler

        self._conn = ConnectHandler(
            device_type=self.device_type,
            host=self.host,
            username=self.username,
            password=self.password,
            port=self.port,
            fast_cli=False,
        )
        self._detect_template()

    def _detect_template(self) -> None:
        """Pick the ``send log`` form this release accepts (probe once)."""
        for tmpl in _CANDIDATE_TEMPLATES:
            cmd = tmpl.format(sev=self.severity, msg="HARNESS marker syntax probe")
            out = self._conn.send_command_timing(cmd) or ""
            if not any(m in out for m in _ERROR_MARKERS):
                self._template = tmpl
                return
        # None validated cleanly; keep the first and let the caller see failures.
        self._template = _CANDIDATE_TEMPLATES[0]

    def mark(self, message: str) -> bool:
        """Send one breadcrumb. Returns True on apparent success, False otherwise."""
        if self._conn is None:
            return False
        cmd = self._template.format(sev=self.severity, msg=sanitize_message(message))
        try:
            with self._lock:
                out = self._conn.send_command_timing(cmd) or ""
        except Exception:
            return False  # SSH likely dropped (device crashing) — caller continues
        return not any(m in out for m in _ERROR_MARKERS)

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.disconnect()
            except Exception:
                pass
            self._conn = None

    def __enter__(self) -> "DeviceLogger":
        self.connect()
        return self

    def __exit__(self, *exc) -> None:
        self.close()
