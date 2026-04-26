#!/usr/bin/env python3
"""Patch swagger-<cat>-model/index-v2.html files to be version-aware.

Replaces hardcoded `api-v2/...` fetches with a base computed from the active
version (read from `?ver=` query string, `#ver=` hash, localStorage, or the
parent window). The default version (read from releases/index.json) keeps the
legacy relative `api-v2/` path; any other version fetches from
`../releases/<ver>/swagger-<cat>-model/api-v2/`.

The allow-list of valid versions is also baked in at patch time so that bad
URLs (`?ver=../etc`, `?ver=v0.0.0`) silently fall back to the default instead
of producing a wave of 404s.

This script is idempotent: re-running it on already-patched files updates the
helper block in place (anchor: `// === version-aware api base`).
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_release_config() -> tuple[str, list[str]]:
    """Return (default_version, allowed_versions) from releases/index.json."""
    cfg_path = ROOT / "releases" / "index.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    default = cfg.get("default") or "17.18.1"
    allowed = [r["ver"] for r in cfg.get("releases", []) if r.get("status") == "active"]
    if default not in allowed:
        allowed.append(default)
    return default, allowed


def build_helper(default_ver: str, allowed: list[str]) -> str:
    allow_js = json.dumps(allowed)
    return f"""
    // === version-aware api base (added by patch_viewers_version_aware.py) ===
    // Default version + allow-list are baked from releases/index.json at
    // patch time. Re-run scripts/patch_viewers_version_aware.py after editing
    // releases/index.json to refresh these.
    var __IOSXE_DEFAULT_VER__ = '{default_ver}';
    var __IOSXE_ALLOWED_VERS__ = {allow_js};
    function __activeVer() {{
        // Priority: ?ver= query > #ver= hash > localStorage > parent window.
        // Always returns a valid version from the allow-list (falls back to
        // __IOSXE_DEFAULT_VER__ for unknown/missing input).
        var raw = null;
        try {{
            var qs = new URLSearchParams(location.search);
            if (qs.get('ver')) raw = qs.get('ver');
            if (!raw) {{
                var hm = location.hash.match(/[#&]ver=([^&]+)/);
                if (hm) raw = decodeURIComponent(hm[1]);
            }}
            if (!raw) raw = localStorage.getItem('iosxe-active-version');
        }} catch (_) {{}}
        if (!raw && window.parent && window.parent !== window
                 && window.parent.__IOSXE_ACTIVE_VERSION__) {{
            raw = window.parent.__IOSXE_ACTIVE_VERSION__;
        }}
        if (!raw) raw = window.__IOSXE_ACTIVE_VERSION__;
        if (raw && __IOSXE_ALLOWED_VERS__.indexOf(raw) >= 0) return raw;
        return __IOSXE_DEFAULT_VER__;
    }}
    function __apiBase() {{
        var ver = __activeVer();
        if (ver === __IOSXE_DEFAULT_VER__) return 'api-v2';
        var m = location.pathname.match(/\\/(swagger-[^/]+-model)\\//);
        var cat = m ? m[1] : '';
        return '../releases/' + encodeURIComponent(ver) + '/' + cat + '/api-v2';
    }}
    function __treeBase() {{
        var ver = __activeVer();
        if (ver === __IOSXE_DEFAULT_VER__) return '../yang-trees';
        return '../releases/' + encodeURIComponent(ver) + '/yang-trees';
    }}
    // Expose for mib-metadata side card and other consumers.
    window.__IOSXE_ACTIVE_VERSION__ = __activeVer();
    // Update any element flagged with `.header-version` so the viewer's
    // visible header reflects the active release instead of the static
    // fallback baked in at HTML build time.
    (function () {{
        function applyHeaderVersion() {{
            try {{
                var v = __activeVer();
                document.querySelectorAll('.header-version').forEach(function (el) {{
                    el.textContent = v;
                }});
            }} catch (_) {{}}
        }}
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', applyHeaderVersion);
        }} else {{
            applyHeaderVersion();
        }}
    }})();
    // === end version-aware api base ===
"""


# Matches an existing helper block so we can replace it on re-runs without
# accumulating duplicates. Newer blocks are terminated by an explicit END
# marker; older blocks (pre-header-version-rebind) ended at the
# window.__IOSXE_ACTIVE_VERSION__ assignment line.
HELPER_BLOCK_RE = re.compile(
    r"\n\s*// === version-aware api base.*?// === end version-aware api base ===\s*\n",
    re.DOTALL,
)
HELPER_BLOCK_OLD_RE = re.compile(
    r"\n\s*// === version-aware api base.*?window\.__IOSXE_ACTIVE_VERSION__ = __activeVer\(\);\s*\n",
    re.DOTALL,
)


def patch(p: Path, helper: str) -> bool:
    src = p.read_text(encoding="utf-8")
    orig = src

    if HELPER_BLOCK_RE.search(src):
        # Already on the new schema: refresh the helper in place.
        src = HELPER_BLOCK_RE.sub("\n" + helper, src, count=1)
    elif HELPER_BLOCK_OLD_RE.search(src):
        # Migrate older patched files (no END marker) to the new schema.
        src = HELPER_BLOCK_OLD_RE.sub("\n" + helper, src, count=1)
    else:
        # Insert before the first allModules declaration we recognise.
        anchors = [
            "let allModules = [];",
            "let allModules = [], currentModule = null;",
        ]
        for anchor in anchors:
            if anchor in src:
                src = src.replace(anchor, helper.rstrip() + "\n    " + anchor, 1)
                break

    # Replace fetch calls (no-op on already-patched files).
    src = src.replace("fetch('api-v2/manifest.json')",
                      "fetch(__apiBase() + '/manifest.json')")
    src = src.replace("fetch(`api-v2/${fname}.json`)",
                      "fetch(`${__apiBase()}/${fname}.json`)")
    src = src.replace(
        "url: `${getSpecFolder(fname)}/${fname}.json`",
        "url: `${__apiBase()}/${fname}.json`",
    )
    src = src.replace(
        "a.href = `${getSpecFolder(currentModule)}/${currentModule}.json`",
        "a.href = `${__apiBase()}/${currentModule}.json`",
    )
    src = re.sub(
        r"const treeUrl = '\.\./yang-trees/' \+ fname \+ '\.html';",
        "const treeUrl = __treeBase() + '/' + fname + '.html';",
        src,
    )

    # Remove the now-dead getSpecFolder() helper. After patching, all callers
    # use __apiBase() directly, so the function is unreachable. Idempotent: a
    # second run finds nothing to remove.
    src = re.sub(
        r"\n\s*function getSpecFolder\(fname\) \{[^}]*\}\n",
        "\n",
        src,
    )

    if src != orig:
        p.write_text(src, encoding="utf-8")
        return True
    return False


def main() -> int:
    default_ver, allowed = load_release_config()
    print(f"[patch] default={default_ver} allowed={allowed}")
    helper = build_helper(default_ver, allowed)
    files = sorted(ROOT.glob("swagger-*-model/index-v2.html"))
    changed = 0
    for f in files:
        if patch(f, helper):
            print(f"  patched   {f.relative_to(ROOT)}")
            changed += 1
        else:
            print(f"  unchanged {f.relative_to(ROOT)}")
    print(f"\n[patch] {changed}/{len(files)} files updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
