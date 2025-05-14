import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

BASE_URL = "https://www.sportybet.com/ng/m/sport/event"

async def generate_sportybet_code(selections=None) -> str:
    """
    Visits each SportyBet match URL, attempts to click specified outcomes.
    Falls back to clicking first available odds if targeted selector is not found.
    Then activates betslip and scrapes booking code.
    """
    if not selections or not isinstance(selections, list):
        return "ERROR: No selections provided"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            for sel in selections:
                event_id = sel.get("event_id")
                outcome_id = sel.get("outcome_id")
                if not event_id or not outcome_id:
                    logger.warning(f"Skipping invalid selection: {sel}")
                    continue

                url = f"{BASE_URL}/{event_id}"
                print(f"\n🌍 Visiting {url}")
                try:
                    await page.goto(url, timeout=60000)
                    await page.wait_for_selector(".m-outcome", timeout=15000)

                    selector = f".m-outcome-odds[data-id='{outcome_id}']"
                    try:
                        await page.wait_for_selector(selector, timeout=12000)
                        await page.click(selector)
                        print(f"✅ Clicked outcome {outcome_id} for event {event_id}")
                    except Exception:
                        print(f"⚠️ Outcome {outcome_id} not found. Clicking first odds instead...")
                        try:
                            await page.click(".m-outcome-odds")
                            print(f"✅ Fallback click for event {event_id}")
                        except Exception:
                            print(f"❌ No odds clickable for event {event_id}")
                            continue

                except Exception as e:
                    print(f"⚠️ Error loading outcome {outcome_id} for event {event_id}: {e}")
                    continue

            # Open floating betslip
            try:
                await page.wait_for_selector("div[data-op='fast-betslip-wrap']", timeout=10000)
                await page.click("div[data-op='fast-betslip-wrap']")
            except Exception:
                print("⚠️ Failed to activate floating betslip.")
                return "ERROR"

            # Click 'Book Bet' and fetch the booking code
            try:
                await page.wait_for_selector("span[data-cms-key='book_bet']", timeout=10000)
                await page.click("span[data-cms-key='book_bet']")
                await page.wait_for_selector("#copyShareCode", timeout=10000)
                code = await page.input_value("#copyShareCode")
                return code.strip() if code else "ERROR"
            except Exception:
                print("❌ Failed to generate SportyBet code.")
                return "ERROR"
            finally:
                await browser.close()

    except Exception as e:
        print(f"❌ Global failure: {e}")
        return "ERROR"
