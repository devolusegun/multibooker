import logging
from playwright.async_api import async_playwright
import time

logger = logging.getLogger(__name__)

SPORT_URL = "https://www.sportybet.com/ng/m/sport/football/today?source=sport_menu&sort=0"

def teams_match_logic(row_teams, target_teams):
    # Basic lower/strip match, you can replace with your fuzzy/normalize logic!
    row_teams_set = set(t.strip().lower() for t in row_teams)
    target_teams_set = set(t.strip().lower() for t in target_teams)
    return row_teams_set == target_teams_set

def outcome_match_logic(cell_text, target_selection):
    # Basic: does cell_text contain the selection string? (Case-insensitive)
    return target_selection.strip().lower() in cell_text.strip().lower()

async def generate_sportybet_code(selections=None) -> str:
    """
    Searches for matches and books odds using visible event list and selectors.
    """
    if not selections or not isinstance(selections, list):
        return "ERROR: No selections provided"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # For debug, set to True for production
            context = await browser.new_context(
                viewport={"width": 375, "height": 812},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X)...",
                is_mobile=True,
                device_scale_factor=2,
                has_touch=True,
            )
            page = await context.new_page()
            await page.goto(SPORT_URL, timeout=60000)
            await page.wait_for_load_state('networkidle')
            await page.wait_for_selector(".m-table-row.m-sports-table", timeout=20000)

            for sel in selections:
                target_teams = sel.get("teams")  # This must be a 2-item list ["Home", "Away"] (adjust if needed)
                target_market = sel.get("market")  # E.g. "Double Chance", "Match Result"
                target_selection = sel.get("selection")  # E.g. "Draw or Home", "2", etc.

                print(f"\n🔍 Searching for match: {target_teams} | Market: {target_market} | Selection: {target_selection}")

                # 1. Find and click the event row
                match_found = False
                event_rows = await page.query_selector_all(".m-table-row.m-sports-table")
                for event in event_rows:
                    team_divs = await event.query_selector_all(".team")
                    row_teams = [await t.inner_text() for t in team_divs]
                    if teams_match_logic(row_teams, target_teams):
                        await event.click()  # open match detail
                        match_found = True
                        break
                if not match_found:
                    print(f"❌ Could not find event for {target_teams}")
                    continue

                await page.wait_for_selector(".m-market", timeout=10000)
                market_blocks = await page.query_selector_all(".m-market")
                outcome_clicked = False
                for block in market_blocks:
                    title = await block.query_selector(".m-market-title")
                    if title:
                        title_text = await title.inner_text()
                        if target_market.lower() in title_text.lower():
                            # Found desired market block
                            outcome_cells = await block.query_selector_all(".m-table-cell.m-outcome")
                            for oc in outcome_cells:
                                txt = await oc.inner_text()
                                if outcome_match_logic(txt, target_selection):
                                    await oc.click()
                                    print(f"✅ Clicked selection '{target_selection}' in market '{title_text}'")
                                    outcome_clicked = True
                                    break
                        if outcome_clicked:
                            break
                if not outcome_clicked:
                    print(f"❌ Could not find outcome '{target_selection}' in market '{target_market}'")
                    continue

                await page.go_back()  # Go back to event list for next bet

            # After all selections, open betslip and get booking code as before
            try:
                await page.wait_for_selector("div[data-op='fast-betslip-wrap']", timeout=10000)
                await page.click("div[data-op='fast-betslip-wrap']")
                await page.wait_for_selector("span[data-cms-key='book_bet']", timeout=10000)
                await page.click("span[data-cms-key='book_bet']")
                await page.wait_for_selector("#copyShareCode", timeout=10000)
                code = await page.input_value("#copyShareCode")
                await browser.close()
                return code.strip() if code else "ERROR"
            except Exception:
                print("❌ Failed to generate SportyBet code.")
                await browser.close()
                return "ERROR"

    except Exception as e:
        print(f"❌ Global failure: {e}")
        return "ERROR"