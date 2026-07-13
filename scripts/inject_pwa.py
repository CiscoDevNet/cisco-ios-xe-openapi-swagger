"""Inject the PWA manifest link, service-worker registration, and the shared
analytics scripts into every public HTML page in the repo, and allowlist the
analytics hosts (Microsoft Clarity + PostHog) in each page's CSP.

Idempotent: the injected block is wrapped in marker comments so re-runs
replace the existing block in-place; the CSP patch is a no-op once PostHog is
already present.

Usage:
    python scripts/inject_pwa.py

The registration script is conservative:
  * Only registers on https:// (or localhost) origins
  * Computes the SW URL relative to the site root, so it works on both
    Pages domains (jeremycohoe and CiscoDevNet) without rebuilds
  * Silent on failure — broken registration must never break the page

Script load order (all external; strict-CSP pages forbid inline exec):
  1. analytics-config.js  (sync)  — sets window.__ANALYTICS_CONFIG__
  2. sw-register.js       (defer) — SW + Microsoft Clarity bootstrap
  3. analytics.js         (defer) — unified wrapper (window.analytics); loads
                                    PostHog and re-points window.__iosxeTrack
                                    so legacy calls also reach PostHog.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BEGIN = "<!-- BEGIN pwa (managed by scripts/inject_pwa.py) -->"
END = "<!-- END pwa -->"

# Analytics host allowlisting for the page CSP.
CLARITY_HOST = "https://*.clarity.ms"
POSTHOG_HOSTS = "https://*.posthog.com https://*.i.posthog.com"

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
    """Manifest link + external analytics/SW scripts.

    The SW registration + Clarity bootstrap live in
    ``assets/js/sw-register.js`` and the unified analytics wrapper in
    ``assets/js/analytics.js`` so that pages whose CSP forbids
    ``'unsafe-inline'`` for ``script-src`` can still load them. Both derive
    any relative URLs from their own location, so the same files work from
    the site root and from viewer subdirectories.
    """
    manifest = f'{asset_prefix}site.webmanifest'
    analytics_cfg = f'{asset_prefix}assets/js/analytics-config.js'
    sw_register = f'{asset_prefix}assets/js/sw-register.js'
    analytics = f'{asset_prefix}assets/js/analytics.js'
    return (
        f'\n<link rel="manifest" href="{manifest}">'
        f'\n<script src="{analytics_cfg}"></script>'
        f'\n<script src="{sw_register}" defer></script>'
        f'\n<script src="{analytics}" defer></script>'
    )


def _patch_csp(text: str) -> str:
    """Allowlist the PostHog hosts next to Clarity in the page CSP. Idempotent:
    a no-op once PostHog is already present, or when the page has no CSP with
    the Clarity token."""
    if "posthog.com" in text:
        return text
    if CLARITY_HOST not in text:
        return text
    return text.replace(CLARITY_HOST, f"{CLARITY_HOST} {POSTHOG_HOSTS}")


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
    new_text = _patch_csp(new_text)
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
