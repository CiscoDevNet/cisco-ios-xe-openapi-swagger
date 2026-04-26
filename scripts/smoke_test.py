"""Quick Playwright smoke test of the live GH Pages site.

Verifies:
  - both active versions (17.18.1, 17.9.x) appear in the version dropdown
  - per version: opening the MIB viewer, clicking a module, hash becomes #spec=<m>
  - clicking an operation updates hash to include &op=<id>
  - reloading that exact URL auto-expands the operation row
  - scans rendered text for stray control bytes (e.g. U+0080-U+009F, U+FFFD)
"""
import asyncio
import re
from playwright.async_api import async_playwright

BASE = "https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/"
BAD_RE = re.compile(r"[\u0080-\u009F\uFFFD]")


async def run():
    rows = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto(BASE, wait_until="domcontentloaded")
        # version selector is populated via fetch — poll until options arrive
        for _ in range(40):
            n = await page.evaluate("document.querySelectorAll('#versionSelector option').length")
            if n >= 2:
                break
            await asyncio.sleep(0.25)

        labels = await page.eval_on_selector_all(
            "#versionSelector option",
            "els => els.map(e => ({label: e.textContent.trim(), disabled: e.disabled, value: e.value}))",
        )
        print("Dropdown:", labels)
        active = [l["value"] for l in labels if not l["disabled"]]
        rows.append(("versions visible (17.18.1, 17.9.x)",
                     ",".join(active),
                     "PASS" if {"17.18.1", "17.9.x"}.issubset(set(active)) else "FAIL"))

        all_garbled = []
        for ver in ["17.18.1", "17.9.x"]:
            page2 = await ctx.new_page()
            mib_url = BASE + "swagger-mib-model/index-v2.html#ver=" + ver
            await page2.goto(mib_url, wait_until="domcontentloaded")
            await page2.wait_for_selector("#moduleList li a", timeout=30000)
            # debug: confirm deeplink.js loaded
            has_dl = await page2.evaluate("typeof window.__DeepLink === 'object'")
            print(f"  [{ver}] __DeepLink loaded:", has_dl)
            await page2.evaluate(
                """() => {
                    const a = [...document.querySelectorAll('#moduleList li a')]
                        .find(x => x.dataset.module === 'ATM-MIB')
                        || document.querySelector('#moduleList li a');
                    a.click();
                }"""
            )
            spec_hash = ""
            for _ in range(40):
                spec_hash = await page2.evaluate("location.hash")
                if "spec=" in spec_hash:
                    break
                await asyncio.sleep(0.25)
            rows.append((f"{ver} mib spec hash", spec_hash, "PASS" if "spec=" in spec_hash else "FAIL"))

            try:
                await page2.wait_for_selector("#swagger-ui .opblock .opblock-summary", timeout=30000)
            except Exception:
                rows.append((f"{ver} swagger-ui rendered", "", "FAIL"))
                continue
            await page2.eval_on_selector("#swagger-ui .opblock .opblock-summary", "el => el.click()")
            op_hash = ""
            for _ in range(40):
                op_hash = await page2.evaluate("location.hash")
                if "op=" in op_hash and "spec=" in op_hash:
                    break
                await asyncio.sleep(0.25)
            ok_op = "op=" in op_hash and "spec=" in op_hash
            rows.append((f"{ver} click op hash", op_hash, "PASS" if ok_op else "FAIL"))

            if ok_op:
                page3 = await ctx.new_page()
                full_url = mib_url.split("#")[0] + op_hash
                await page3.goto(full_url, wait_until="domcontentloaded")
                try:
                    await page3.wait_for_selector("#swagger-ui .opblock.is-open", timeout=20000)
                    rows.append((f"{ver} reload auto-expand", "", "PASS"))
                except Exception:
                    rows.append((f"{ver} reload auto-expand", "no .is-open", "FAIL"))
                await page3.close()

            txt = await page2.evaluate("document.body.innerText")
            bad = BAD_RE.findall(txt)
            if bad:
                idx = next((i for i, c in enumerate(txt) if BAD_RE.match(c)), -1)
                snippet = txt[max(0, idx - 40):idx + 40] if idx >= 0 else ""
                all_garbled.append((ver, len(bad), repr(snippet)))
            await page2.close()

        rows.append(("garbled char count",
                     str(sum(g[1] for g in all_garbled)),
                     "PASS" if not all_garbled else "FAIL"))
        for g in all_garbled:
            print("  GARBLED:", g)

        await browser.close()

    print()
    print(f"{'TEST':<35} | {'DETAIL':<55} | RESULT")
    print("-" * 105)
    for t, d, r in rows:
        print(f"{t:<35} | {(d or '')[:55]:<55} | {r}")


if __name__ == "__main__":
    asyncio.run(run())
