# app/services/generators/sportybet_gen.py

import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)
BASE_URL = "https://www.sportybet.com/ng/m/sport/event/"

async def generate_sportybet_code(selections) -> str:
    if not selections:
        return "ERROR: No selections provided"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 375, "height": 812},
                user_agent="Mozilla/5.0 (Linux; Android 10; Mobile; rv:109.0) Gecko/109.0 Firefox/109.0",
                java_script_enabled=True,
                device_scale_factor=2
            )
            page = await context.new_page()

            for selection in selections:
                event_id = selection["event_id"]
                outcome_id = selection["outcome_id"]
                event_url = f"{BASE_URL}{event_id}"

                print(f"\n🌍 Visiting {event_url}")
                await page.goto(event_url, timeout=60000)

                try:
                    # Force scroll down so outcome blocks load
                    await page.mouse.wheel(0, 2000)
                    await page.wait_for_timeout(1500)

                    selector = f".m-outcome-odds[data-id='{outcome_id}']"
                    await page.wait_for_selector(selector, timeout=15000)
                    await page.locator(selector).click()
                    await page.wait_for_timeout(1000)

                    print(f"✅ Clicked outcome {outcome_id} for event {event_id}")
                except Exception as e:
                    print(f"⚠️ Error loading outcome {outcome_id} for event {event_id}: {e}")
                    continue

            # Open floating betslip modal
            try:
                await page.wait_for_selector("div[data-op='fast-betslip-wrap']", timeout=10000)
                await page.click("div[data-op='fast-betslip-wrap']")
                await page.wait_for_timeout(1500)
            except Exception as e:
                print(f"⚠️ Failed to activate floating betslip: {e}")

            # Grab booking code
            try:
                await page.wait_for_selector("span[data-cms-key='book_bet']", timeout=10000)
                code_span = await page.query_selector("span[data-cms-key='book_bet']")
                if code_span:
                    code = await code_span.inner_text()
                    return code.strip()
            except Exception as e:
                print(f"❌ Failed to generate SportyBet code: {e}")

            return "ERROR"

    except Exception as e:
        print(f"Unexpected failure: {e}")
        return "ERROR"
