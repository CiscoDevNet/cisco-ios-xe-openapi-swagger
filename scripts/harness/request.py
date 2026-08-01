"""GET-only RESTCONF client for the Track B capture harness.

Safety core of the whole GET phase. This module can ONLY issue HTTP GET
requests against a device's RESTCONF root. Any attempt to route a non-GET
method (PUT/PATCH/POST/DELETE/HEAD/OPTIONS) through here raises immediately,
BEFORE any socket is opened. The collector never passes a method; it calls
``restconf_get`` exclusively, which makes accidental writes structurally
impossible during the GET phase.

Request pattern (HTTP Basic + verify=False + yang-data+json headers +
bounded timeout) mirrors the repo's scripts/validate_examples_c9kv.py
``restconf_request`` helper referenced in DEVICE_DATA_COLLECTION.md §3.

CRUD (Phase 5, §7) is intentionally NOT implemented here. A write path must
live in a separate, explicitly-gated module — never by relaxing this one.
"""
from __future__ import annotations

import random
import time
import urllib.parse
from dataclasses import dataclass
from typing import Any, Optional

import requests
import urllib3

# The device presents a self-signed cert in the lab; we knowingly disable
# verification (same as validate_examples_c9kv.py) and silence the warning
# so it does not drown the per-request summary output.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}

# The ONLY method this module will ever send. Do not add to this.
_ALLOWED_METHOD = "GET"


class WriteAttemptError(PermissionError):
    """Raised when any non-GET method is routed through the GET-only client."""


def assert_get_only(method: str) -> None:
    """Hard guard: raise unless ``method`` is exactly GET (case-insensitive).

    Kept as a standalone function so tests and any future caller can assert the
    invariant directly.
    """
    if method is None or method.strip().upper() != _ALLOWED_METHOD:
        raise WriteAttemptError(
            f"GET-only harness refused non-GET method {method!r}. "
            "Writes are gated behind the separate CRUD phase (DEVICE_DATA_COLLECTION.md §7)."
        )


@dataclass
class GetResult:
    """Outcome of a single RESTCONF GET."""

    ok: bool
    http_status: Optional[int]
    body: Any  # parsed JSON, raw text, or None (204/empty)
    is_json: bool
    empty: bool
    error: Optional[str]
    elapsed_ms: int
    url: str
    # Crash instrumentation: reset=True means the device dropped the connection
    # mid-exchange (ConnectionError / ChunkedEncodingError “Response ended
    # prematurely”) at least once — a strong device-crash signature that is
    # recorded even when a later retry succeeds (so retries can't mask it).
    reset: bool = False
    attempts: int = 1


def build_restconf_url(host: str, port: int, openapi_path: str) -> str:
    """Compose the absolute RESTCONF URL.

    ``openapi_path`` is a spec path such as
    ``/data/Cisco-IOS-XE-native:native/hostname``. The RESTCONF root is
    ``https://<host>:<port>/restconf``. The path is appended verbatim (already
    percent-safe as emitted by the generators) with only spaces encoded.
    """
    host = host.strip()
    root = f"https://{host}:{int(port)}/restconf"
    if not openapi_path.startswith("/"):
        openapi_path = "/" + openapi_path
    # Encode spaces (list-key placeholders may contain them) but keep the
    # RESTCONF-significant characters (:/=,) intact. ``%`` is kept safe so a
    # caller that already percent-encoded a key value (e.g. ``%2F`` for a '/'
    # inside a key) is not double-encoded into ``%252F``.
    safe_path = urllib.parse.quote(openapi_path, safe="/:=,{}[]-.~%")
    return root + safe_path


def restconf_get(
    host: str,
    port: int,
    openapi_path: str,
    auth: tuple[str, str],
    timeout: int = 30,
    session: Optional[requests.Session] = None,
    retries: int = 2,
    backoff: float = 1.5,
    conflict_retries: int = 8,
    conflict_backoff: float = 0.25,
    _method: str = "GET",
) -> GetResult:
    """Issue a single RESTCONF GET and return a normalized :class:`GetResult`.

    ``auth`` is a ``(username, password)`` tuple sourced from env/secrets by the
    caller; credentials are never logged or persisted by this module.

    Retries with exponential backoff on timeouts and 5xx responses. 204 and
    empty bodies are returned as ``empty=True`` (not errors). Non-JSON bodies
    are returned as text with ``is_json=False``.
    """
    # Structural write guard — first line of defense, before any network I/O.
    assert_get_only(_method)

    url = build_restconf_url(host, port, openapi_path)
    owns_session = session is None
    sess = session or requests.Session()
    last_error: Optional[str] = None
    attempt = 0            # transient (5xx / connection) retry counter
    conflict_tries = 0     # 409/429 "datastore busy" waits (separate budget)
    reset_seen = False
    start_all = time.monotonic()
    try:
        while True:
            start = time.monotonic()
            try:
                resp = sess.get(
                    url,
                    headers=RESTCONF_HEADERS,
                    auth=auth,
                    verify=False,
                    timeout=timeout,
                )
                elapsed_ms = int((time.monotonic() - start) * 1000)

                # Retry on transient server-side failures.
                if resp.status_code >= 500 and attempt < retries:
                    attempt += 1
                    last_error = f"HTTP {resp.status_code}"
                    time.sleep(backoff ** attempt)
                    continue

                # 409 Conflict / 429 Too Many Requests: the RESTCONF datastore
                # is busy serving a prior read (IOS XE serializes config-datastore
                # GETs, so parallel workers collide). This is NOT a real failure
                # — the request will succeed once the in-flight read completes.
                # Wait briefly and retry, with jitter so parallel workers don't
                # retry in lockstep. Uses its own budget so it never consumes the
                # 5xx / connection retry allotment. This lets the collector run
                # concurrently and self-throttle to whatever the device can serve.
                if resp.status_code in (409, 429) and conflict_tries < conflict_retries:
                    conflict_tries += 1
                    last_error = f"HTTP {resp.status_code}"
                    time.sleep(conflict_backoff * conflict_tries
                               + random.uniform(0.0, conflict_backoff))
                    continue

                text = resp.text or ""
                empty = resp.status_code == 204 or text.strip() == ""
                body: Any = None
                is_json = False
                if not empty:
                    ctype = resp.headers.get("Content-Type", "")
                    if "json" in ctype.lower():
                        try:
                            body = resp.json()
                            is_json = True
                        except ValueError:
                            body = text
                            is_json = False
                    else:
                        body = text
                        is_json = False

                return GetResult(
                    ok=200 <= resp.status_code < 300,
                    http_status=resp.status_code,
                    body=body,
                    is_json=is_json,
                    empty=empty,
                    error=None,
                    elapsed_ms=int((time.monotonic() - start_all) * 1000),
                    url=url,
                    reset=reset_seen,
                    attempts=attempt + conflict_tries + 1,
                )
            except (requests.Timeout, requests.ConnectionError,
                    requests.exceptions.ChunkedEncodingError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                # ConnectionError / ChunkedEncodingError = device dropped the
                # connection = crash signature. (A bare read Timeout is a stall,
                # not necessarily a reset.)
                if not isinstance(exc, requests.Timeout):
                    reset_seen = True
                if attempt < retries:
                    attempt += 1
                    time.sleep(backoff ** attempt)
                    continue
                break
            except requests.RequestException as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                break

        return GetResult(
            ok=False,
            http_status=None,
            body=None,
            is_json=False,
            empty=True,
            error=last_error or "unknown error",
            elapsed_ms=int((time.monotonic() - start_all) * 1000),
            url=url,
            reset=reset_seen,
            attempts=attempt + conflict_tries + 1,
        )
    finally:
        if owns_session:
            sess.close()
