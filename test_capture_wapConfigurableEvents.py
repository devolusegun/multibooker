import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("🌐 Navigating to SportyBet football page (mobile)...")
        await page.goto("https://www.sportybet.com/ng/m/sport/football", timeout=60000)

        print("⏳ Interacting with the page to trigger network requests...")
        await page.mouse.wheel(0, 5000)
        await page.wait_for_timeout(5000)

        print("📡 Waiting for fixture response...")

        def is_target_response(response):
            return (
                "wapConfigurableEventsByOrder" in response.url
                and response.status == 200
            )

        try:
            response = await context.wait_for_event("response", predicate=is_target_response, timeout=15000)
            json_data = await response.json()

            print("✅ Captured Fixture Data, saving to file...")
            with open("sportybet_fixtures.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            print("📁 Data saved to sportybet_fixtures.json")

        except Exception as e:
            print(f"❌ Failed to capture fixture data: {e}")

        await browser.close()

asyncio.run(run())
