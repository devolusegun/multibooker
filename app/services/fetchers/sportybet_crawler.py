import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

SPORTYBET_SPORT_URLS = [
    "https://www.sportybet.com/ng/sport/football",
    "https://www.sportybet.com/ng/sport/basketball",
    "https://www.sportybet.com/ng/sport/tennis"
]

async def crawl_sportybet_fixtures() -> list:
    """
    Crawls SportyBet for links to individual match fixtures across football, basketball, and tennis.
    Returns a list of match URLs.
    """
    fixture_links = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            for url in SPORTYBET_SPORT_URLS:
                logger.info(f"🌐 Visiting {url}")
                await page.goto(url, timeout=60000)

                await page.wait_for_selector("a[href*='/sporty/']", timeout=15000)

                elements = await page.locator("a[href*='/sporty/']").all()
                for el in elements:
                    href = await el.get_attribute("href")
                    if href and "/sporty/" in href and href not in fixture_links:
                        fixture_links.append(f"https://www.sportybet.com{href}")

            await browser.close()
            return fixture_links

    except Exception as e:
        logger.error(f"❌ Failed to crawl SportyBet fixtures: {e}")
        return []
