import logging
from playwright.async_api import async_playwright
import time
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)

SPORT_URL = "https://www.sportybet.com/ng/m/sport/football/today?source=sport_menu&sort=0"

def teams_match_logic(row_teams, target_teams):
    # Normalize: lower, remove fc/sc/bk etc.
    def norm(t): return t.strip().lower().replace(' fc', '').replace(' sc', '').replace(' bk', '')
    row_norm = [norm(t) for t in row_teams]
    target_norm = [norm(t) for t in target_teams]
    # Both [home, away]
    score1 = fuzz.ratio(row_norm[0], target_norm[0]) + fuzz.ratio(row_norm[1], target_norm[1])
    score2 = fuzz.ratio(row_norm[0], target_norm[1]) + fuzz.ratio(row_norm[1], target_norm[0])
    return max(score1, score2) > 150  # Each must be >75; tweak as needed

#def outcome_match_logic(cell_text, target_selection):
    # Basic: does cell_text contain the selection string? (Case-insensitive)
    #return target_selection.strip().lower() in cell_text.strip().lower()

def normalize(text):
    return text.lower().strip()

def outcome_match_logic(cell_text, target_selection):
    return normalize(cell_text) == normalize(target_selection)

async def robust_scroll(page, pause=800, max_tries=40):
    last_event_count = 0
    for _ in range(max_tries):
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await page.wait_for_timeout(pause)
        event_rows = await page.query_selector_all(".m-table-row.m-sports-table")
        if len(event_rows) == last_event_count:
            break
        last_event_count = len(event_rows)

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

            async def scroll_to_bottom(page, pause=500, max_tries=25):
                # Scroll down until the page can't scroll any further
                last_height = await page.evaluate("document.body.scrollHeight")
                for _ in range(max_tries):
                    await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(pause)
                    new_height = await page.evaluate("document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
            
            await robust_scroll(page)
            event_rows = await page.query_selector_all(".m-table-row.m-sports-table")
            for i, event in enumerate(event_rows[-5:]):  # Print last 5 loaded events
                team_divs = await event.query_selector_all(".team")
                row_teams = [await t.inner_text() for t in team_divs]
                print(f"[Last Visible Row #{i}] {row_teams}")

            # Print all events scraped from the page for debugging:
            for event in event_rows:
                team_divs = await event.query_selector_all(".team")
                row_teams = [await t.inner_text() for t in team_divs]
                print(f"SportyBet event row: {row_teams}")

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
                    print(f"Row teams: {row_teams}, Target teams: {target_teams}, Match: {teams_match_logic(row_teams, target_teams)}")
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