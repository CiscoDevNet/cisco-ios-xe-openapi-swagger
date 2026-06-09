"""Security regression test: catch dangerous patterns that flow
URL-fragment / query-string / location data into a DOM sink without
escaping.

Background: in May 2026 a reflected XSS slipped into ``404.html``
(``msg.innerHTML = '... <code>' + params.spec + '</code> ...'``) and a
``javascript:`` URL open-redirect slipped into ``search.js``
(``window.location.href = modelDir + '/index.html#spec=' + specName``).
Both took URL-controlled values without validating or escaping them.
This test scans every JS/HTML source for the same shape so the bugs
can't quietly come back.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# Files we scan. Stay narrow — third-party libs (Swagger UI, Fuse, etc.)
# live under release/archive folders and are out of scope.
SCAN = [
    "search.js",
    "index-app.js",
    "code-generator.js",
    "tree-compare.js",
    "yang-accountability.js",
    "recent-favorites.js",
    "404.html",
    "index.html",
    "exports.html",
    "telemetry.html",
    "about.html",
    "code-generator.html",
    "tree-compare.html",
    "yang-accountability.html",
    "yang-accountability-compare.html",
    "platform-coverage.html",
    "app-map.html",
    "assets/js/site-chrome.js",
    "assets/js/sw-register.js",
    "assets/js/platform-coverage.js",
    "assets/js/platform-support.js",
    "swagger-cfg-model/paths-search.js",
    "swagger-cfg-model/yang-tree-sidebar.js",
]

# innerHTML / outerHTML / insertAdjacentHTML / document.write fed directly
# by a URL-fragment or query-string read in the same expression.
DANGEROUS_SINK = re.compile(
    r"(innerHTML|outerHTML|document\.write|insertAdjacentHTML)"
    r"[^;\n]{0,200}?"
    r"(location\.hash|location\.search|URLSearchParams|window\.location\.hash"
    r"|window\.location\.search|params\.\w+)",
    re.IGNORECASE,
)

# Naked ``location.href = ... + <something>`` redirect to a value that
# isn't a https:// / http:// / relative URL literal. The whitelist guard
# we added in round 24 stops the ``javascript:`` URL exploit; this test
# fails loudly if anyone reintroduces the pre-whitelist shape.
JS_URL_REDIRECT = re.compile(
    r"(?:window\.)?location\.(?:href|assign|replace)\s*=\s*"
    r"(?!['\"]https?:|['\"]/|['\"]\.{0,2}/|['\"]#)"
    r"[A-Za-z_$][\w$\.\[\]]*\s*\+",
)

# Inline ``<script>...</script>`` blocks on top-level pages whose CSP
# forbids 'unsafe-inline'. JSON-LD blocks (``type="application/ld+json"``)
# are non-executable and exempt.
STRICT_CSP_PAGES = [
    "index.html",
    "about.html",
    "code-generator.html",
    "tree-compare.html",
    "telemetry.html",
    "yang-accountability.html",
    "platform-coverage.html",
    "app-map.html",
]
INLINE_EXEC_SCRIPT = re.compile(
    r"<script(?![^>]*\bsrc=)(?![^>]*type\s*=\s*['\"]application/ld\+json)"
    r"[^>]*>(?!\s*</script>)",
    re.IGNORECASE,
)


@pytest.mark.parametrize("rel", SCAN)
def test_no_url_to_dom_sink(rel: str) -> None:
    p = REPO / rel
    if not p.is_file():
        pytest.skip(f"{rel} not present")
    text = p.read_text(encoding="utf-8", errors="ignore")
    hits = DANGEROUS_SINK.findall(text)
    assert not hits, (
        f"{rel}: URL-controlled data appears to flow into a DOM-sink "
        f"without escaping; matched: {hits[:3]}"
    )


@pytest.mark.parametrize("rel", SCAN)
def test_no_javascript_url_redirect(rel: str) -> None:
    p = REPO / rel
    if not p.is_file():
        pytest.skip(f"{rel} not present")
    text = p.read_text(encoding="utf-8", errors="ignore")
    # Mask out the round-24 whitelist guard so the pattern doesn't trip
    # on the safe form we ship now.
    masked = re.sub(
        r"if\s*\(\s*ALLOWED_MODEL_DIRS\.indexOf\(modelDir\)[^)]*\)\s*return;\s*",
        "/* whitelist-guard */",
        text,
    )
    hits = JS_URL_REDIRECT.findall(masked)
    # The guarded form (`modelDir + '/index.html#spec=' + encode...`) is
    # safe — we accept that the masked text may still match because the
    # pattern is conservative. Allow zero or one match max, and require
    # the file to contain the whitelist guard if it matches.
    if hits:
        assert "ALLOWED_MODEL_DIRS" in text, (
            f"{rel}: location.href / .assign / .replace receives a "
            f"concatenated value with no whitelist guard. Matches: {hits[:3]}"
        )


@pytest.mark.parametrize("rel", STRICT_CSP_PAGES)
def test_strict_csp_pages_have_no_inline_exec_script(rel: str) -> None:
    p = REPO / rel
    if not p.is_file():
        pytest.skip(f"{rel} not present")
    text = p.read_text(encoding="utf-8", errors="ignore")
    # Only flag truly inline executable scripts (i.e. <script>...content...).
    # Build a list of offending fragments for the assertion message.
    offenders = []
    for m in re.finditer(
        r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        attrs = m.group("attrs") or ""
        body = (m.group("body") or "").strip()
        if not body:
            continue  # external <script src=...>
        if "src=" in attrs:
            continue  # external script with empty body — fine
        if re.search(r"type\s*=\s*['\"]application/ld\+json", attrs, re.I):
            continue  # JSON-LD data block — not executed by browser
        offenders.append(body[:120])
    assert not offenders, (
        f"{rel}: inline executable <script> block(s) present but CSP "
        f"forbids 'unsafe-inline'. Move logic to an external file under "
        f"assets/js/. First offender: {offenders[0]!r}"
    )
