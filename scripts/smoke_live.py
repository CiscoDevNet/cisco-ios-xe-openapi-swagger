#!/usr/bin/env python3
"""Headless smoke test for the version-aware MIB viewer.

Loads the MIB viewer once per active IOS-XE release and reports module count,
the resolved __apiBase(), and any console / page errors. Useful both against
the live GitHub Pages deployment and a local static server.

Usage:
    python -X utf8 scripts/smoke_live.py
    python -X utf8 scripts/smoke_live.py --base-url http://localhost:8000
"""
from __future__ import annotations
import argparse
import asyncio
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright

DEFAULT_BASE_URL = "https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger"
ROOT = Path(__file__).resolve().parent.parent


def load_versions() -> tuple[str, list[str]]:
    cfg = json.loads((ROOT / "releases" / "index.json").read_text(encoding="utf-8"))
    default = cfg.get("default") or "17.18.1"
    versions = [r["ver"] for r in cfg.get("releases", []) if r.get("status") == "active"]
    if default not in versions:
        versions.append(default)
    return default, versions


async def run(base_url: str) -> int:
    default_ver, versions = load_versions()
    failures = 0
    print(f"[smoke] base_url={base_url}")
    print(f"[smoke] default={default_ver} active={versions}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        for ver in versions:
            page = await ctx.new_page()
            errors: list[str] = []
            page.on(
                "console",
                lambda m: errors.append(f"{m.type}: {m.text}") if m.type == "error" else None,
            )
            page.on("pageerror", lambda e: errors.append(f"PAGEERROR: {e}"))
            url = f"{base_url}/swagger-mib-model/index.html?ver={ver}"
            try:
                await page.goto(url, wait_until="networkidle", timeout=30_000)
                await asyncio.sleep(2)
                cnt = await page.evaluate("document.querySelectorAll('#moduleList li').length")
                api_base = await page.evaluate(
                    "typeof __apiBase === 'function' ? __apiBase() : 'undef'"
                )
            except Exception as e:
                cnt, api_base = 0, f"NAV-ERROR: {e}"
            real_errors = [e for e in errors if "503" not in e]  # ignore transient CDN
            ok = cnt > 0 and not real_errors
            status = "PASS" if ok else "FAIL"
            print(f"  [{status}] {ver:10} modules={cnt:4d} apiBase={api_base} errors={len(errors)}")
            for e in errors[:3]:
                print(f"    ! {e}")
            if not ok:
                failures += 1
            await page.close()
        await browser.close()
    print(f"\n[smoke] failures={failures}/{len(versions)}")
    return 0 if failures == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL of the deployed site (default: {DEFAULT_BASE_URL}).",
    )
    args = ap.parse_args()
    return asyncio.run(run(args.base_url.rstrip("/")))


if __name__ == "__main__":
    sys.exit(main())
