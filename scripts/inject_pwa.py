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
    """Manifest link + inline SW registration. asset_prefix lets viewer
    pages reach back to the site root (../) for both URLs.

    The registration also wires up an "update available" toast: when a
    new service worker reaches the `installed` state while an existing
    controller is still in charge, we surface a small bottom-right card
    with a Reload button that triggers the SKIP_WAITING handshake.
    """
    sw_url = f'{asset_prefix}service-worker.js'
    scope = asset_prefix or './'
    manifest = f'{asset_prefix}site.webmanifest'
    # Compact single-string payload. Kept inline (no extra request) and
    # without any external CSS — fail-silent on every branch so a broken
    # update path can never break the page.
    register = (
        "if('serviceWorker' in navigator && "
        "(location.protocol==='https:'||location.hostname==='localhost')){"
        "window.addEventListener('load',function(){"
        f"navigator.serviceWorker.register('{sw_url}',{{scope:'{scope}'}}).then(function(reg){{"
        "function show(w){"
        "if(document.getElementById('iosxe-sw-toast'))return;"
        "var t=document.createElement('div');t.id='iosxe-sw-toast';"
        "t.setAttribute('role','status');t.setAttribute('aria-live','polite');"
        "t.style.cssText='position:fixed;right:16px;bottom:16px;z-index:99999;"
        "background:#1565c0;color:#fff;padding:10px 14px;border-radius:8px;"
        "box-shadow:0 4px 12px rgba(0,0,0,.25);"
        "font:14px/1.4 system-ui,-apple-system,sans-serif;"
        "display:flex;gap:10px;align-items:center;max-width:90vw';"
        "var s=document.createElement('span');s.textContent='New version available.';"
        "var b=document.createElement('button');b.type='button';b.textContent='Reload';"
        "b.style.cssText='background:#fff;color:#1565c0;border:0;padding:6px 12px;"
        "border-radius:6px;font:600 13px system-ui,-apple-system,sans-serif;cursor:pointer';"
        "var x=document.createElement('button');x.type='button';x.textContent='\\u00d7';"
        "x.setAttribute('aria-label','Dismiss update notification');"
        "x.style.cssText='background:transparent;color:#fff;border:0;"
        "font:18px/1 system-ui,sans-serif;cursor:pointer;padding:0 4px';"
        "var reloaded=false;"
        "navigator.serviceWorker.addEventListener('controllerchange',function(){"
        "if(reloaded)return;reloaded=true;location.reload();});"
        "b.addEventListener('click',function(){try{w.postMessage({type:'SKIP_WAITING'});}catch(e){}});"
        "x.addEventListener('click',function(){t.remove();});"
        "t.appendChild(s);t.appendChild(b);t.appendChild(x);"
        "document.body.appendChild(t);"
        "}"
        "if(reg.waiting && navigator.serviceWorker.controller)show(reg.waiting);"
        "reg.addEventListener('updatefound',function(){"
        "var nw=reg.installing;if(!nw)return;"
        "nw.addEventListener('statechange',function(){"
        "if(nw.state==='installed' && navigator.serviceWorker.controller)show(nw);"
        "});"
        "});"
        "}).catch(function(){});"
        "});}"
    )
    return (
        f'\n<link rel="manifest" href="{manifest}">'
        f'\n<script>{register}</script>'
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
