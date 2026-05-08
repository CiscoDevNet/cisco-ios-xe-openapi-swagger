import asyncio, json
from playwright.async_api import async_playwright

URL = 'https://ciscodevnet.github.io/cisco-ios-xe-openapi-swagger/swagger-mib-model/index.html#spec=ATM-MIB&op=get-ATM-MIB%5C%3AATM-MIB'

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        page.on('console', lambda m: print('LOG', m.type, m.text[:200]))
        await page.goto(URL, wait_until='domcontentloaded')
        await page.wait_for_selector('.opblock', timeout=30000)
        await asyncio.sleep(6)
        info = await page.evaluate("""
            () => {
                const all = [...document.querySelectorAll('.opblock')];
                const targetId = 'operations-ATM-MIB-get-ATM-MIB\\\\:ATM-MIB';
                const targetNode = all.find(o => o.id === targetId.replace(/\\\\\\\\:/g, ':'));
                return {
                    total: all.length,
                    openIds: all.filter(o=>o.classList.contains('is-open')).map(o=>o.id),
                    hash: location.hash,
                    parsed: window.__DeepLink ? window.__DeepLink.parseHash() : null,
                    sampleIds: all.slice(0, 3).map(o => o.id),
                    tryExpandResult: window.__DeepLink ? window.__DeepLink.tryExpandOp(window.__DeepLink.parseHash().op) : null
                };
            }
        """)
        print(json.dumps(info, indent=2))
        await b.close()
asyncio.run(main())
