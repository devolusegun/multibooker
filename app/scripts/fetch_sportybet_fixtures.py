# app/scripts/fetch_sportybet_fixtures.py

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

FIXTURE_OUTPUT_PATH = Path("sportybet_fixtures.json")
TARGET_FRAGMENT = "wapConfigurableEventsByOrder"
SPORTYBET_URL = "https://www.sportybet.com/ng/m/sport/football?time=all&source=sport_menu&sort=0"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 10; Mobile; rv:109.0) Gecko/109.0 Firefox/109.0",
            viewport={"width": 375, "height": 800},
            java_script_enabled=True,
            device_scale_factor=2
        )
        page = await context.new_page()

        captured = False

        async def handle_response(response):
            nonlocal captured
            url = response.url

            if "api" in url and response.status == 200:
                print(f" {url}")

            if TARGET_FRAGMENT in url and response.status == 200 and not captured:
                try:
                    json_data = await response.json()
                    FIXTURE_OUTPUT_PATH.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
                    print(f" Captured and saved fixture data to {FIXTURE_OUTPUT_PATH.resolve()}")
                    captured = True
                except Exception as e:
                    print(f" Error capturing JSON response: {e}")

        # Attach before navigation
        page.on("response", handle_response)

        print("Navigating to all-football-fixtures page (mobile)...")
        await page.goto(SPORTYBET_URL, timeout=60000)

        print(" Scrolling to trigger XHRs...")
        for _ in range(4):
            await page.mouse.wheel(0, 4000)
            await page.wait_for_timeout(2000)

        print(" Waiting up to 20s for any final XHRs...")
        await page.wait_for_timeout(20000)

        if not captured:
            print(" Fixture response not captured.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
