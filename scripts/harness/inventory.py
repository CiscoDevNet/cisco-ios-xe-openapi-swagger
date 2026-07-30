"""Inventory + credential loading for the Track B harness.

Inventory (scripts/harness/inventory.json, GITIGNORED) lists the devices to
capture. Credentials come from the environment (IOSXE_USER / IOSXE_PASS) or an
optional gitignored secrets file; they are never written into captures, logs,
or the committed inventory.example.json.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

HARNESS_DIR = Path(__file__).resolve().parent
REPO_ROOT = HARNESS_DIR.parents[1]
DEFAULT_INVENTORY = HARNESS_DIR / "inventory.json"
# Optional gitignored .env files (lab convenience); env vars still win.
DEFAULT_DOTENV_PATHS = (HARNESS_DIR / ".env", REPO_ROOT / ".env")

REQUIRED_FIELDS = ("name", "host")


@dataclass
class Device:
    name: str
    host: str
    port: int = 443
    pid: str = "unknown"
    os_version: str = "unknown"
    writable: bool = False  # GET phase ignores this; CRUD phase (§7) honors it.

    @property
    def restconf_root(self) -> str:
        return f"https://{self.host}:{self.port}/restconf"


class InventoryError(RuntimeError):
    pass


class CredentialError(RuntimeError):
    pass


def load_inventory(path: Optional[Path] = None) -> list[Device]:
    """Load and validate the device inventory.

    Raises :class:`InventoryError` with an actionable message if the file is
    missing (points at inventory.example.json) or malformed.
    """
    path = Path(path) if path else DEFAULT_INVENTORY
    if not path.exists():
        raise InventoryError(
            f"Inventory not found: {path}\n"
            f"Copy {HARNESS_DIR / 'inventory.example.json'} -> {path} "
            "and fill in the 6 devices (this file is gitignored)."
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InventoryError(f"Inventory {path} is not valid JSON: {exc}") from exc

    if not isinstance(raw, list) or not raw:
        raise InventoryError(f"Inventory {path} must be a non-empty JSON array of devices.")

    devices: list[Device] = []
    seen_names: set[str] = set()
    for i, entry in enumerate(raw):
        if not isinstance(entry, dict):
            raise InventoryError(f"Inventory entry #{i} is not an object.")
        for field in REQUIRED_FIELDS:
            if not entry.get(field):
                raise InventoryError(f"Inventory entry #{i} is missing required field '{field}'.")
        name = str(entry["name"]).strip()
        if name in seen_names:
            raise InventoryError(f"Duplicate device name in inventory: {name!r}")
        seen_names.add(name)
        devices.append(
            Device(
                name=name,
                host=str(entry["host"]).strip(),
                port=int(entry.get("port", 443)),
                pid=str(entry.get("pid", "unknown")).strip() or "unknown",
                os_version=str(entry.get("os_version", "unknown")).strip() or "unknown",
                writable=bool(entry.get("writable", False)),
            )
        )
    return devices


def _parse_dotenv(path: Path) -> dict:
    """Parse a simple ``KEY=VALUE`` .env file (ignores blanks/comments/quotes)."""
    data: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return data
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            data[key] = val
    return data


def load_credentials(
    secrets_path: Optional[Path] = None,
) -> tuple[str, str]:
    """Return ``(username, password)`` from env vars, a .env file, or a secrets file.

    Precedence: IOSXE_USER / IOSXE_PASS env vars, then a gitignored ``.env``
    (scripts/harness/.env or repo-root .env) with the same keys, then a JSON
    secrets file (default scripts/harness/secrets.json) with ``username`` /
    ``password`` keys. Raises :class:`CredentialError` if none is present.
    """
    user = os.environ.get("IOSXE_USER")
    passwd = os.environ.get("IOSXE_PASS")
    if user and passwd:
        return user, passwd

    # .env files (lab convenience). Env vars above still take precedence.
    for dotenv in DEFAULT_DOTENV_PATHS:
        if dotenv.exists():
            env = _parse_dotenv(dotenv)
            user = user or env.get("IOSXE_USER")
            passwd = passwd or env.get("IOSXE_PASS")
    if user and passwd:
        return user, passwd

    secrets_path = Path(secrets_path) if secrets_path else HARNESS_DIR / "secrets.json"
    if secrets_path.exists():
        try:
            data = json.loads(secrets_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CredentialError(f"Secrets file {secrets_path} is not valid JSON: {exc}") from exc
        user = user or data.get("username")
        passwd = passwd or data.get("password")
        if user and passwd:
            return user, passwd

    raise CredentialError(
        "Missing credentials. Set env vars IOSXE_USER and IOSXE_PASS, "
        f"or create a gitignored .env ({DEFAULT_DOTENV_PATHS[0]}) or "
        f"{secrets_path} with the credentials. "
        "Credentials are never written to captures or logs."
    )


def credentials_available() -> bool:
    """Non-raising check used by preflight to report readiness."""
    try:
        load_credentials()
        return True
    except CredentialError:
        return False
