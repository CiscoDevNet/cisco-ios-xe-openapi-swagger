#!/usr/bin/env python3
"""Headless smoke tests S-1..S-6 from ASSURANCE_SPEC.md.

Hits the live (or local) site over plain HTTP and verifies critical hub
pages and viewer assets return 200 with expected content substrings. No
browser, no Playwright dependency — runs anywhere Python 3.8+ runs.

Run after every change and before declaring work complete:

    python -X utf8 scripts/smoke_assurance.py
    python -X utf8 scripts/smoke_assurance.py --base http://localhost:8000

Exit 0 on PASS, 1 on FAIL, 2 if any required check could not be run.

To test a local build, first run:
    cd <repo-root>; python -m http.server 8000
then in another shell:
    python -X utf8 scripts/smoke_assurance.py --base http://localhost:8000

The exact pass criteria match ASSURANCE_SPEC.md \u00a74 verbatim. Update
both files together if you change one.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from typing import Callable
from urllib import error, parse, request

DEFAULT_BASE = "https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger"
TIMEOUT = 20
USER_AGENT = "smoke_assurance.py (+repo: cisco-ios-xe-openapi-swagger)"


@dataclass
class Result:
    name: str
    status: str  # PASS, FAIL, SKIP
    detail: str = ""


@dataclass
class Check:
    id: str
    description: str
    fn: Callable[[str], Result]
    results: list[Result] = field(default_factory=list)


def fetch(url: str) -> tuple[int, str, dict[str, str]]:
    """GET url; return (status, body, headers). On network error, status=0."""
    req = request.Request(url, headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"})
    try:
        with request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read().decode("utf-8", errors="replace")
            return r.status, body, dict(r.headers)
    except error.HTTPError as e:
        return e.code, "", {}
    except (error.URLError, TimeoutError, OSError) as e:
        return 0, f"network error: {e}", {}


def require(cond: bool, detail: str) -> Result | None:
    if cond:
        return None
    return Result("", "FAIL", detail)


# --- individual checks ---------------------------------------------------

def check_homepage(base: str) -> Result:
    status, body, _ = fetch(f"{base}/index.html")
    if status == 0:
        return Result("S-0 homepage", "SKIP", body)
    if status != 200:
        return Result("S-0 homepage", "FAIL", f"HTTP {status}")
    must_contain = ["Cisco IOS-XE", "swagger-oper-model", "platform-coverage.html"]
    missing = [m for m in must_contain if m not in body]
    if missing:
        return Result("S-0 homepage", "FAIL", f"missing markers: {missing}")
    return Result("S-0 homepage", "PASS", f"{len(body)} bytes, all markers present")


def check_viewer_renders_spec(base: str) -> Result:
    # S-1: oper viewer + a known module's JSON spec.
    url = f"{base}/swagger-oper-model/index.html"
    s1, b1, _ = fetch(url)
    if s1 == 0:
        return Result("S-1 viewer renders", "SKIP", b1)
    if s1 != 200:
        return Result("S-1 viewer renders", "FAIL", f"{url} -> HTTP {s1}")
    if "Operational" not in b1:
        return Result("S-1 viewer renders", "FAIL", "viewer HTML missing 'Operational' marker")

    # Module spec must be reachable
    spec_url = f"{base}/releases/26.1.1/swagger-oper-model/api/Cisco-IOS-XE-tcam-oper.json"
    s2, b2, _ = fetch(spec_url)
    if s2 != 200:
        return Result("S-1 viewer renders", "FAIL", f"{spec_url} -> HTTP {s2}")
    try:
        doc = json.loads(b2)
        paths = doc.get("paths", {})
    except json.JSONDecodeError as e:
        return Result("S-1 viewer renders", "FAIL", f"tcam-oper spec not valid JSON: {e}")
    if len(paths) < 1:
        return Result("S-1 viewer renders", "FAIL", f"tcam-oper spec has 0 paths")

    # Platform support must list cat9k
    ps_url = f"{base}/releases/26.1.1/platform-support.json"
    s3, b3, _ = fetch(ps_url)
    if s3 != 200:
        return Result("S-1 viewer renders", "FAIL", f"{ps_url} -> HTTP {s3}")
    try:
        ps = json.loads(b3)
    except json.JSONDecodeError as e:
        return Result("S-1 viewer renders", "FAIL", f"platform-support.json invalid: {e}")
    tcam = ps.get("modules", {}).get("Cisco-IOS-XE-tcam-oper", {})
    if "cat9k" not in tcam.get("platforms", []):
        return Result("S-1 viewer renders", "FAIL",
                      f"tcam-oper platforms={tcam.get('platforms')} (expected to contain cat9k)")
    return Result("S-1 viewer renders", "PASS",
                  f"viewer 200; spec {len(paths)} paths; tcam-oper -> {tcam.get('platforms')}")


def check_deep_link_bgp(base: str) -> Result:
    # S-2: deep-link to bgp-oper — verify spec + platforms (badge data the JS uses).
    spec_url = f"{base}/releases/26.1.1/swagger-oper-model/api/Cisco-IOS-XE-bgp-oper.json"
    s, body, _ = fetch(spec_url)
    if s == 0:
        return Result("S-2 deep-link bgp-oper", "SKIP", body)
    if s != 200:
        return Result("S-2 deep-link bgp-oper", "FAIL", f"{spec_url} -> HTTP {s}")
    try:
        doc = json.loads(body)
    except json.JSONDecodeError as e:
        return Result("S-2 deep-link bgp-oper", "FAIL", f"invalid JSON: {e}")
    if not doc.get("paths"):
        return Result("S-2 deep-link bgp-oper", "FAIL", "bgp-oper spec has no paths")
    ps_url = f"{base}/releases/26.1.1/platform-support.json"
    s2, b2, _ = fetch(ps_url)
    if s2 != 200:
        return Result("S-2 deep-link bgp-oper", "FAIL", f"{ps_url} -> HTTP {s2}")
    bgp = json.loads(b2).get("modules", {}).get("Cisco-IOS-XE-bgp-oper", {})
    plats = bgp.get("platforms", [])
    if len(plats) < 6:
        return Result("S-2 deep-link bgp-oper", "FAIL",
                      f"bgp-oper platforms={plats} (expected \u22656)")
    return Result("S-2 deep-link bgp-oper", "PASS",
                  f"spec OK; bgp-oper supported on {len(plats)} platforms: {plats}")


def check_yang_accountability(base: str) -> Result:
    url = f"{base}/yang-accountability.html"
    s, body, _ = fetch(url)
    if s == 0:
        return Result("S-3 yang-accountability", "SKIP", body)
    if s != 200:
        return Result("S-3 yang-accountability", "FAIL", f"HTTP {s}")
    if "yang-accountability.js" not in body and "yang_accountability" not in body:
        return Result("S-3 yang-accountability", "FAIL",
                      "HTML missing accountability script/data reference")
    # Data file must be present
    data_url = f"{base}/yang_accountability.json"
    s2, _, _ = fetch(data_url)
    if s2 != 200:
        return Result("S-3 yang-accountability", "FAIL", f"{data_url} -> HTTP {s2}")
    return Result("S-3 yang-accountability", "PASS", "HTML 200; data file 200")


def check_platform_coverage(base: str) -> Result:
    url = f"{base}/platform-coverage.html"
    s, body, _ = fetch(url)
    if s == 0:
        return Result("S-4 platform-coverage matrix", "SKIP", body)
    if s != 200:
        return Result("S-4 platform-coverage matrix", "FAIL", f"HTTP {s}")
    # MUST reference the external JS (not inline; CSP would block inline)
    if "assets/js/platform-coverage.js" not in body:
        return Result("S-4 platform-coverage matrix", "FAIL",
                      "page does not load external assets/js/platform-coverage.js (CSP would block inline)")
    # Index + per-release data
    idx_url = f"{base}/platform-support-index.json"
    s2, b2, _ = fetch(idx_url)
    if s2 != 200:
        return Result("S-4 platform-coverage matrix", "FAIL", f"{idx_url} -> HTTP {s2}")
    try:
        idx = json.loads(b2)
    except json.JSONDecodeError as e:
        return Result("S-4 platform-coverage matrix", "FAIL", f"index JSON invalid: {e}")
    releases = idx.get("releases", [])
    if len(releases) < 5:
        return Result("S-4 platform-coverage matrix", "FAIL",
                      f"index lists {len(releases)} releases, expected \u22655")
    if idx.get("default") not in releases:
        return Result("S-4 platform-coverage matrix", "FAIL",
                      f"default={idx.get('default')} not present in releases={releases}")
    s3, b3, _ = fetch(f"{base}/releases/{idx['default']}/platform-support.json")
    if s3 != 200:
        return Result("S-4 platform-coverage matrix", "FAIL",
                      f"default release platform-support.json -> HTTP {s3}")
    mods = json.loads(b3).get("modules", {})
    if len(mods) < 800:
        return Result("S-4 platform-coverage matrix", "FAIL",
                      f"default release has {len(mods)} modules, expected \u2265800")
    return Result("S-4 platform-coverage matrix", "PASS",
                  f"page 200; index lists {len(releases)} releases; "
                  f"default {idx['default']} has {len(mods)} modules")


def check_code_generator(base: str) -> Result:
    # S-5: code-generator page exists, loads its external JS, and is CSP-strict.
    url = f"{base}/code-generator.html"
    s, body, _ = fetch(url)
    if s == 0:
        return Result("S-5 code-generator", "SKIP", body)
    if s != 200:
        return Result("S-5 code-generator", "FAIL", f"HTTP {s}")
    if "code-generator.js" not in body:
        return Result("S-5 code-generator", "FAIL", "missing reference to code-generator.js")
    s2, _, _ = fetch(f"{base}/code-generator.js")
    if s2 != 200:
        return Result("S-5 code-generator", "FAIL", f"code-generator.js -> HTTP {s2}")
    return Result("S-5 code-generator", "PASS", "HTML 200; external JS 200")


def check_telemetry(base: str) -> Result:
    # S-6: telemetry hub loads + per-release telemetry index resolves.
    url = f"{base}/telemetry.html"
    s, body, _ = fetch(url)
    if s == 0:
        return Result("S-6 telemetry", "SKIP", body)
    if s != 200:
        return Result("S-6 telemetry", "FAIL", f"HTTP {s}")
    if "telemetry.js" not in body:
        return Result("S-6 telemetry", "FAIL", "missing reference to telemetry.js")
    s2, _, _ = fetch(f"{base}/telemetry.js")
    if s2 != 200:
        return Result("S-6 telemetry", "FAIL", f"telemetry.js -> HTTP {s2}")
    # Telemetry index for default release
    s3, b3, _ = fetch(f"{base}/releases/26.1.1/telemetry-index.json")
    if s3 == 404:
        return Result("S-6 telemetry", "PASS",
                      "HTML+JS 200; telemetry-index.json not yet published for 26.1.1 (acceptable)")
    if s3 != 200:
        return Result("S-6 telemetry", "FAIL", f"telemetry-index.json -> HTTP {s3}")
    try:
        idx = json.loads(b3)
    except json.JSONDecodeError as e:
        return Result("S-6 telemetry", "FAIL", f"telemetry-index.json invalid: {e}")
    return Result("S-6 telemetry", "PASS",
                  f"HTML+JS 200; index has {len(idx) if isinstance(idx, list) else 'n/a'} entries")


CHECKS: list[tuple[str, Callable[[str], Result]]] = [
    ("S-0", check_homepage),
    ("S-1", check_viewer_renders_spec),
    ("S-2", check_deep_link_bgp),
    ("S-3", check_yang_accountability),
    ("S-4", check_platform_coverage),
    ("S-5", check_code_generator),
    ("S-6", check_telemetry),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--base", default=DEFAULT_BASE,
                    help=f"Base URL of the site (default: {DEFAULT_BASE})")
    ap.add_argument("--only", default="",
                    help="Comma-separated check IDs to run (e.g. 'S-1,S-4'). Default: all.")
    args = ap.parse_args()
    base = args.base.rstrip("/")
    only = {x.strip() for x in args.only.split(",") if x.strip()}

    print(f"[smoke] base={base}")
    print(f"[smoke] checks={','.join(c[0] for c in CHECKS if not only or c[0] in only)}")
    print()

    results: list[Result] = []
    started = time.time()
    for cid, fn in CHECKS:
        if only and cid not in only:
            continue
        t0 = time.time()
        r = fn(base)
        dt = time.time() - t0
        marker = {"PASS": "[PASS]", "FAIL": "[FAIL]", "SKIP": "[SKIP]"}[r.status]
        print(f"  {marker} {r.name:30}  {dt:5.2f}s   {r.detail}")
        results.append(r)

    elapsed = time.time() - started
    passes = sum(1 for r in results if r.status == "PASS")
    fails  = sum(1 for r in results if r.status == "FAIL")
    skips  = sum(1 for r in results if r.status == "SKIP")
    print()
    print(f"[smoke] {passes} PASS / {fails} FAIL / {skips} SKIP in {elapsed:.1f}s")

    if fails > 0:
        return 1
    if skips > 0:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
