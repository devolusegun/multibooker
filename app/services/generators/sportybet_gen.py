import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

SPORTYBET_URL = "https://www.sportybet.com/ng/sport/football"

async def generate_sportybet_code(selections=None) -> str:
    """
    Uses Playwright to simulate a real bet placement and scrape the booking code.
    If `selections` is None, it defaults to clicking the first available odds on the football page.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            logger.info("🌐 Navigating to SportyBet football page...")
            await page.goto(SPORTYBET_URL, timeout=60000)

            logger.info("⏳ Waiting for match odds to load...")
            await page.wait_for_selector(".m-outcome-odds", timeout=15000)

            logger.info("⚽ Clicking the first visible odds button...")
            await page.click(".m-outcome-odds")

            logger.info("📥 Waiting for 'Book Bet' button...")
            await page.wait_for_selector("span[data-cms-key='book_bet']", timeout=15000)
            await page.click("span[data-cms-key='book_bet']")

            logger.info("🔍 Waiting for booking code modal...")
            await page.wait_for_selector("#copyShareCode", timeout=10000)
            code = await page.input_value("#copyShareCode")

            await browser.close()

            if code:
                logger.info(f"✅ Booking code found: {code.strip()}")
                return code.strip()
            else:
                return "ERROR"

    except Exception as e:
        logger.error(f"❌ Failed to generate SportyBet code: {e}")
        return "ERROR"
