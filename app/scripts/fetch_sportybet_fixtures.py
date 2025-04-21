# app/scripts/fetch_sportybet_fixtures.py

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_FILE = Path("sportybet_fixtures.json")
TARGET_FRAGMENT = "wapConfigurableEventsByOrder"
TIME_FILTERS = ["today", "tomorrow", "all"]
BASE_URL = "https://www.sportybet.com/ng/m/sport/football?time={}&source=sport_menu&sort=0"

async def capture_fixtures(page, filter_type, all_fixtures):
    captured = False

    async def handle_response(response):
        nonlocal captured
        url = response.url
        if TARGET_FRAGMENT in url and response.status == 200 and not captured:
            try:
                data = await response.json()
                all_fixtures.extend(data.get("events", []))
                captured = True
                print(f" ✅ Captured {len(data.get('events', []))} from {filter_type}")
            except Exception as e:
                print(f" ❌ Error parsing {filter_type}: {e}")

    page.on("response", handle_response)

    url = BASE_URL.format(filter_type)
    print(f"\n🌐 Navigating to {url}")
    await page.goto(url, timeout=60000)

    print(" 🔄 Scrolling to trigger fixture load...")
    for _ in range(3):
        await page.mouse.wheel(0, 4000)
        await page.wait_for_timeout(1500)

    await page.wait_for_timeout(3000)
    page.off("response", handle_response)

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 10; Mobile)",
            viewport={"width": 375, "height": 800},
        )
        page = await context.new_page()

        all_fixtures = []

        for filter_type in TIME_FILTERS:
            await capture_fixtures(page, filter_type, all_fixtures)

        await browser.close()

        # Deduplicate based on eventId
        seen = set()
        unique_fixtures = []
        for fixture in all_fixtures:
            eid = fixture.get("eventId")
            if eid and eid not in seen:
                seen.add(eid)
                unique_fixtures.append(fixture)

        print(f"\n📦 Merging and saving {len(unique_fixtures)} fixtures...")
        OUTPUT_FILE.write_text(json.dumps(unique_fixtures, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✅ Saved {len(unique_fixtures)} unique fixtures to {OUTPUT_FILE.resolve()}")

if __name__ == "__main__":
    asyncio.run(run())
