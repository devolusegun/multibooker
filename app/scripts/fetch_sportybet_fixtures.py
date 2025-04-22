# app/scripts/fetch_sportybet_fixtures.py

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_FILE = Path("sportybet_fixtures.json")
TARGET_URL = "https://www.sportybet.com/ng/m/sport/football?time=all&source=sport_menu&sort=0"
TARGET_FRAGMENT = "wapConfigurableEventsByOrder"

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

        captured_payloads = []

        async def handle_response(response):
            url = response.url
            if TARGET_FRAGMENT in url and response.status == 200:
                try:
                    json_data = await response.json()
                    if "data" in json_data and "tournaments" in json_data["data"]:
                        captured_payloads.append(json_data)
                        print(f"📦 Captured fixture page → {url}")
                except Exception as e:
                    print(f"❌ Failed parsing response from {url}: {e}")

        page.on("response", handle_response)

        print("🌐 Navigating to SportyBet mobile football fixtures...")
        await page.goto(TARGET_URL, timeout=60000)

        print("🔄 Scrolling to trigger all fixture pages...")
        for _ in range(15):
            await page.mouse.wheel(0, 4000)
            await page.wait_for_timeout(2000)

        await page.wait_for_timeout(5000)
        await browser.close()

        # Merge all tournaments and events
        all_events = []
        for payload in captured_payloads:
            tournaments = payload.get("data", {}).get("tournaments", [])
            for t in tournaments:
                events = t.get("events", [])
                if events:
                    for e in events:
                        all_events.append(e)

        print(f"\n✅ Captured total {len(all_events)} events")
        OUTPUT_FILE.write_text(json.dumps(all_events, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✅ Saved fixtures to {OUTPUT_FILE.resolve()}")

if __name__ == "__main__":
    asyncio.run(run())
