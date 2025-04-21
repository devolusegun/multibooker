# app/scripts/debug_fixture_endpoints.py
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        async def handle_response(response):
            url = response.url
            if "api" in url and response.status == 200:
                print(f"📡 {url}")
                try:
                    json_data = await response.json()
                    if isinstance(json_data, list) and len(json_data) > 5:
                        print(f"✅ Fixture-looking payload: {url} — {len(json_data)} items")
                except:
                    pass

        page.on("response", handle_response)

        await page.goto("https://www.sportybet.com/ng/m/sport/football?time=all", timeout=60000)
        await page.mouse.wheel(0, 8000)
        await page.wait_for_timeout(10000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
