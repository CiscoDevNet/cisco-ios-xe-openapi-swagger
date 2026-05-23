"""Inject PWA manifest link and service-worker registration into every
public HTML page in the repo.

Idempotent: the injected block is wrapped in marker comments so re-runs
replace the existing block in-place.

Usage:
    python scripts/inject_pwa.py

The registration script is conservative:
  * Only registers on https:// (or localhost) origins
  * Computes the SW URL relative to the site root, so it works on both
    Pages domains (jeremycohoe and CiscoDevNet) without rebuilds
  * Silent on failure — broken registration must never break the page
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BEGIN = "<!-- BEGIN pwa (managed by scripts/inject_pwa.py) -->"
END = "<!-- END pwa -->"

TOP_LEVEL = [
    "index.html",
    "code-generator.html",
    "tree-compare.html",
    "telemetry.html",
    "exports.html",
    "yang-accountability.html",
    "yang-accountability-compare.html",
    "404.html",
]
VIEWERS = [
    "swagger-cfg-model/index.html",
    "swagger-events-model/index.html",
    "swagger-ietf-model/index.html",
    "swagger-mib-model/index.html",
    "swagger-native-config-model/index.html",
    "swagger-openconfig-model/index.html",
    "swagger-oper-model/index.html",
    "swagger-other-model/index.html",
    "swagger-rpc-model/index.html",
]


def _block(asset_prefix: str) -> str:
    """Manifest link + external SW registration script.

    The SW registration logic and update-toast UI live in
    ``assets/js/sw-register.js`` so that pages whose CSP forbids
    ``'unsafe-inline'`` for ``script-src`` can still register the
    service worker. The external script derives its SW URL and scope
    from its own ``document.currentScript.src`` so it works the same
    from the site root and from viewer subdirectories.
    """
    manifest = f'{asset_prefix}site.webmanifest'
    sw_register = f'{asset_prefix}assets/js/sw-register.js'
    return (
        f'\n<link rel="manifest" href="{manifest}">'
        f'\n<script src="{sw_register}" defer></script>'
    )


def _inject(path: Path, block: str) -> bool:
    text = path.read_text(encoding="utf-8")
    wrapped = f"{BEGIN}{block}\n{END}"
    pattern = re.compile(rf"{re.escape(BEGIN)}.*?{re.escape(END)}", re.S)
    if pattern.search(text):
        new_text = pattern.sub(lambda _m: wrapped, text)
    else:
        if "</head>" not in text:
            print(f"  skip {path.relative_to(ROOT)}: no </head>")
            return False
        new_text = text.replace("</head>", f"{wrapped}\n</head>", 1)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for rel in TOP_LEVEL:
        p = ROOT / rel
        if not p.is_file():
            print(f"  miss {rel}")
            continue
        if _inject(p, _block(asset_prefix="")):
            print(f"  inj  {rel}")
            changed += 1
        else:
            print(f"  ok   {rel}")
    for rel in VIEWERS:
        p = ROOT / rel
        if not p.is_file():
            print(f"  miss {rel}")
            continue
        if _inject(p, _block(asset_prefix="../")):
            print(f"  inj  {rel}")
            changed += 1
        else:
            print(f"  ok   {rel}")
    print(f"\n{changed} file(s) changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
