import asyncio
from playwright.async_api import async_playwright

JS_INSTRUMENT = """
window.__hashLog = [];
let last = location.hash;
window.__hashLog.push(['init', last]);
const orig = history.replaceState;
history.replaceState = function(){ window.__hashLog.push(['replaceState', arguments[2], new Error().stack.split('\\n').slice(1,4).join(' | ')]); return orig.apply(this, arguments); };
const origPush = history.pushState;
history.pushState = function(){ window.__hashLog.push(['pushState', arguments[2]]); return origPush.apply(this, arguments); };
window.addEventListener('hashchange', () => window.__hashLog.push(['hashchange', location.hash]));
setInterval(() => { if (location.hash !== last) { window.__hashLog.push(['poll', location.hash]); last = location.hash; }}, 50);
"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        page.on('pageerror', lambda e: print('PAGEERR:', e))
        await page.goto('https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/swagger-mib-model/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('#moduleList li a', timeout=30000)
        await page.evaluate(JS_INSTRUMENT)
        await page.evaluate("document.querySelector(\"#moduleList li a[data-module='ATM-MIB']\").click()")
        await asyncio.sleep(3)
        log = await page.evaluate('window.__hashLog')
        for e in log:
            print(e)
        print('FINAL HASH:', await page.evaluate('location.hash'))
        await b.close()

asyncio.run(main())
