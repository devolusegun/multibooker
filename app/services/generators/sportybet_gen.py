import logging
from playwright.async_api import async_playwright
import time
from rapidfuzz import fuzz
import unicodedata
import re

logger = logging.getLogger(__name__)

SPORT_URL = "https://www.sportybet.com/ng/m/sport/football?time=all&sort=1"

def normalize_team_name(name):
    name = name.lower()
    name = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
    # Remove punctuation and common soccer suffixes/prefixes
    name = re.sub(r'\b(fc|sc|cf|cd|ac|afc|srl|sr|deportivo|club|sporting|united|city|team|impact|nwsl|ec|es|pr|sr|sd|ca|atlético|atletico|toronto|national|college|collegiate)\b', '', name)
    name = re.sub(r'[^\w\s]', ' ', name)  # Remove any remaining non-word chars
    name = re.sub(r'\s+', ' ', name)  # Collapse whitespace
    return name.strip()

def teams_match_logic(row_teams, target_teams, threshold=80):
    row_norm = [normalize_team_name(t) for t in row_teams]
    target_norm = [normalize_team_name(t) for t in target_teams]
    # Home/Away and swapped order
    score1 = fuzz.ratio(row_norm[0], target_norm[0]) + fuzz.ratio(row_norm[1], target_norm[1])
    score2 = fuzz.ratio(row_norm[0], target_norm[1]) + fuzz.ratio(row_norm[1], target_norm[0])
    print(f"[DEBUG] Matching: {row_norm} <-> {target_norm} | {score1}/{score2}")
    return max(score1, score2) >= threshold * 2

def normalize(text):
    return text.lower().strip()

def outcome_match_logic(cell_text, target_selection):
    return normalize(cell_text) == normalize(target_selection)

async def collect_all_event_rows(page, pause=800, max_tries=40):
    """
    Scrolls the page, accumulating all unique event rows (even those that disappear from DOM after scrolling).
    Returns a list of dicts: {raw: [original teams], norm: [normalized teams]}
    """
    all_fixtures = []
    seen_keys = set()

    for i in range(max_tries):
        event_rows = await page.query_selector_all(".m-table-row.m-sports-table")
        for row in event_rows:
            team_divs = await row.query_selector_all('.team')
            row_teams = [await t.inner_text() for t in team_divs]
            norm_list = [normalize_team_name(t) for t in row_teams]
            key = tuple(norm_list)
            if key and key not in seen_keys and len(norm_list) == 2:
                all_fixtures.append({'raw': row_teams, 'norm': norm_list})
                seen_keys.add(key)
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await page.wait_for_timeout(pause)
        if i > 2 and len(seen_keys) == len(all_fixtures):
            break

    print(f"[DEBUG] Finished scrolling. Total unique events loaded: {len(all_fixtures)}")
    for i, f in enumerate(all_fixtures):
        print(f"[#{i}] {f['raw']}")
    return all_fixtures

async def generate_sportybet_code(selections=None) -> str:
    """
    Searches for matches and books odds using visible event list and selectors.
    SKIPS any bets not found, does not halt on errors.
    """
    if not selections or not isinstance(selections, list):
        return "ERROR: No selections provided"

    found_count = 0
    failed_matches = []
    success_bets = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # True for production
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
                target_teams = sel.get("teams")
                target_norm = [normalize_team_name(t) for t in target_teams]
                target_market = sel.get("market")
                target_selection = sel.get("selection")

                print(f"\n🔍 Searching for match: {target_teams} | Market: {target_market} | Selection: {target_selection}")

                match_found = False
                for fixture in all_events:
                    row_teams = fixture['raw']
                    row_norm = fixture['norm']
                    if teams_match_logic(row_teams, target_teams):
                        event_rows = await page.query_selector_all(".m-table-row.m-sports-table")
                        for event in event_rows:
                            tds = await event.query_selector_all('.team')
                            teams = [await t.inner_text() for t in tds]
                            if [normalize_team_name(x) for x in teams] == row_norm:
                                await event.click()
                                print(f"✅ Found and clicked event: {teams}")
                                match_found = True
                                break
                        if match_found:
                            break

                if not match_found:
                    print(f"❌ Skipping: Could not find event for {target_teams}")
                    failed_matches.append(sel)
                    continue

                await page.wait_for_selector(".m-market", timeout=10000)
                market_blocks = await page.query_selector_all(".m-market")
                outcome_clicked = False
                for block in market_blocks:
                    title = await block.query_selector(".m-market-title")
                    if title:
                        title_text = await title.inner_text()
                        if target_market.lower() in title_text.lower():
                            outcome_cells = await block.query_selector_all(".m-table-cell.m-outcome")
                            for oc in outcome_cells:
                                txt = await oc.inner_text()
                                if normalize(txt) == normalize(target_selection):
                                    await oc.click()
                                    print(f"✅ Clicked selection '{target_selection}' in market '{title_text}'")
                                    outcome_clicked = True
                                    break
                        if outcome_clicked:
                            break
                if not outcome_clicked:
                    print(f"❌ Skipping: Could not find outcome '{target_selection}' in market '{target_market}'")
                    failed_matches.append(sel)
                    await page.go_back()
                    continue

                # Only count as success if both match and outcome found
                found_count += 1
                success_bets.append(sel)
                await page.go_back()

            # --- Book only if at least one selection succeeded ---
            if found_count > 0:
                try:
                    await page.wait_for_selector("div[data-op='fast-betslip-wrap']", timeout=10000)
                    await page.click("div[data-op='fast-betslip-wrap']")
                    await page.wait_for_selector("span[data-cms-key='book_bet']", timeout=10000)
                    await page.click("span[data-cms-key='book_bet']")
                    await page.wait_for_selector("#copyShareCode", timeout=10000)
                    code = await page.input_value("#copyShareCode")
                    await browser.close()
                    print(f"\n✅ BOOKED {found_count} bets. Skipped {len(failed_matches)} bets.")
                    if failed_matches:
                        print("❗ Skipped:")
                        for f in failed_matches:
                            print(f"  - {f.get('teams')} ({f.get('market')}, {f.get('selection')})")
                    return code.strip() if code else "ERROR"
                except Exception:
                    print("❌ Failed to generate SportyBet code.")
                    await browser.close()
                    return "ERROR"
            else:
                await browser.close()
                print(f"❌ No valid bets to book. Skipped {len(failed_matches)} bets.")
                return "ERROR: No valid bets booked."

    except Exception as e:
        print(f"❌ Global failure: {e}")
        return "ERROR"

