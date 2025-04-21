import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

SPORTYBET_BASE = "https://www.sportybet.com/ng/m"

async def generate_sportybet_code(selections=None) -> str:
    """
    Launches SportyBet (mobile site), visits each event URL, clicks the correct market + outcome,
    and retrieves a real booking code. Skips gracefully if elements fail to load.
    """
    if not selections or not isinstance(selections, list):
        return "ERROR: No selections provided"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            for idx, sel in enumerate(selections, 1):
                event_id = sel["event_id"].split(":")[-1]
                market_id = sel["market_id"]
                outcome_id = sel["outcome_id"]

                event_url = f"{SPORTYBET_BASE}/event/{event_id}"
                logger.info(f"➡️ Visiting event: {event_url}")
                await page.goto(event_url, timeout=60000)

                try:
                    await page.wait_for_selector(".m-market", timeout=15000)
                    market_selector = f"[data-id='{market_id}']"
                    odds_button = await page.query_selector(market_selector)

                    if odds_button:
                        await odds_button.click()
                    else:
                        logger.warning(f"⚠️ Market not found for event: {event_id}, skipping...")
                        continue

                except Exception as e:
                    logger.warning(f"⚠️ Error loading market for event {event_id}: {e}")
                    continue

            logger.info("✅ All selections clicked. Booking bet...")

            await page.wait_for_selector("span[data-cms-key='book_bet']", timeout=10000)
            await page.click("span[data-cms-key='book_bet']")

            await page.wait_for_selector("#copyShareCode", timeout=10000)
            code = await page.input_value("#copyShareCode")

            await browser.close()
            return code.strip() if code else "ERROR"

    except Exception as e:
        logger.error(f"❌ Failed to generate SportyBet code: {e}")
        return "ERROR"
