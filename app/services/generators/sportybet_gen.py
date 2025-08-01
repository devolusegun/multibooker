import logging
from playwright.async_api import async_playwright
import time
from rapidfuzz import fuzz
import unicodedata

logger = logging.getLogger(__name__)

SPORT_URL = "https://www.sportybet.com/ng/m/sport/football?time=all&sort=1"

def normalize_team_name(name):
    # Lowercase, strip, remove accents, and strip out standard suffixes and punctuation
    name = name.lower().strip()
    name = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
    for w in [" fc", " sc", " club", "college", ".", ",", "-", "  "]:
        name = name.replace(w, " ")
    return " ".join(name.split()).strip()

def teams_match_logic(row_teams, target_teams):
    row_set = set(normalize_team_name(t) for t in row_teams)
    target_set = set(normalize_team_name(t) for t in target_teams)
    return row_set == target_set

def normalize(text):
    return text.lower().strip()

def outcome_match_logic(cell_text, target_selection):
    return normalize(cell_text) == normalize(target_selection)

async def collect_all_event_rows(page, pause=800, max_tries=40):
    """
    Scrolls the page, accumulating all unique event rows (even those that disappear from DOM after scrolling).
    Returns a list of dicts: {teams: [...], row: element_handle}
    """
    all_fixtures = []
    seen_keys = set()  # to avoid duplicates, e.g. ("team1", "team2")

    for i in range(max_tries):
        event_rows = await page.query_selector_all(".m-table-row.m-sports-table")
        for row in event_rows:
            team_divs = await row.query_selector_all('.team')
            row_teams = [await t.inner_text() for t in team_divs]
            # Key by normalized tuple for uniqueness
            key = tuple(sorted(normalize_team_name(t) for t in row_teams))
            if key and key not in seen_keys and len(key) == 2:
                all_fixtures.append({'teams': row_teams, 'row': row})
                seen_keys.add(key)
        # Scroll and wait
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await page.wait_for_timeout(pause)
        # Stop early if no new fixtures seen
        if i > 2 and len(seen_keys) == len(all_fixtures):
            break

    print(f"[DEBUG] Finished scrolling. Total unique events loaded: {len(all_fixtures)}")
    for i, f in enumerate(all_fixtures):
        print(f"[#{i}] {f['teams']}")
    return all_fixtures

async def generate_sportybet_code(selections=None) -> str:
    """
    Searches for matches and books odds using visible event list and selectors.
    """
    if not selections or not isinstance(selections, list):
        return "ERROR: No selections provided"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False
            )  # For debug, set to True for production
            context = await browser.new_context(
                viewport={"width": 375, "height": 4000},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X)...",
                is_mobile=True,
                device_scale_factor=2,
                has_touch=True,
            )
            page = await context.new_page()
            await page.goto(SPORT_URL, timeout=60000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_selector(".m-table-row.m-sports-table", timeout=20000)

            all_events = await collect_all_event_rows(page)

            for sel in selections:
                target_teams = sel.get("teams")  # Must be ["Home", "Away"]
                target_market = sel.get("market")
                target_selection = sel.get("selection")

                print(
                    f"\n🔍 Searching for match: {target_teams} | Market: {target_market} | Selection: {target_selection}"
                )

                match_found = False
                for f in all_events:
                    row_teams = f['teams']
                    row = f['row']
                    # Print debug info
                    print(f"Row teams: {row_teams} | Norm: {set(normalize_team_name(t) for t in row_teams)} | Target: {set(normalize_team_name(t) for t in target_teams)} | Match: {teams_match_logic(row_teams, target_teams)}")
                    if teams_match_logic(row_teams, target_teams):
                        await row.click()
                        print(f"✅ Found and clicked event: {row_teams}")
                        match_found = True
                        break
                if not match_found:
                    print(f"❌ Could not find event for {target_teams}")
                    return "ERROR: Match not found"

                await page.wait_for_selector(".m-market", timeout=10000)
                market_blocks = await page.query_selector_all(".m-market")
                outcome_clicked = False
                for block in market_blocks:
                    title = await block.query_selector(".m-market-title")
                    if title:
                        title_text = await title.inner_text()
                        if target_market.lower() in title_text.lower():
                            outcome_cells = await block.query_selector_all(
                                ".m-table-cell.m-outcome"
                            )
                            for oc in outcome_cells:
                                txt = await oc.inner_text()
                                if normalize(txt) == normalize(target_selection):
                                    await oc.click()
                                    print(
                                        f"✅ Clicked selection '{target_selection}' in market '{title_text}'"
                                    )
                                    outcome_clicked = True
                                    break
                        if outcome_clicked:
                            break
                if not outcome_clicked:
                    print(
                        f"❌ Could not find outcome '{target_selection}' in market '{target_market}'"
                    )
                    continue

                await page.go_back()  # Go back to event list for next bet

            # After all selections, open betslip and get booking code as before
            try:
                await page.wait_for_selector(
                    "div[data-op='fast-betslip-wrap']", timeout=10000
                )
                await page.click("div[data-op='fast-betslip-wrap']")
                await page.wait_for_selector(
                    "span[data-cms-key='book_bet']", timeout=10000
                )
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