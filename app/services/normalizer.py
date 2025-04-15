import re
from typing import Dict

def normalize_match(raw_match: str) -> str:
    match = raw_match.replace("-", "vs").replace("  ", " ").strip()
    match = re.sub(r'\s{2,}', ' ', match)
    return match

def normalize_market(raw_market: str) -> str:
    market = raw_market.lower().strip()

    # Football
    if "asian total" in market or "total" in market:
        return "Asian Total"
    if "1x2" in market or "match winner" in market or "match result" in market:
        return "Match Result"
    if "both teams to score" in market or "btts" in market:
        return "BTTS"
    if "over/under 2.5" in market or "over under 2.5" in market:
        return "Over/Under 2.5"

    return raw_market.title()

def normalize_selection(raw_selection: str) -> str:
    selection = raw_selection.strip().lower()

    if selection in {"home", "1"}:
        return "Home"
    if selection in {"draw", "x"}:
        return "Draw"
    if selection in {"away", "2"}:
        return "Away"
    if "over" in selection:
        return "Over 2.5"
    if "under" in selection:
        return "Under 2.5"

    return raw_selection.title()

def normalize_odds_payload(raw_data: Dict, source: str) -> Dict:
    """
    Normalize full odds structure from a fetcher (e.g., SportyBet or Bet9ja).
    """
    normalized = {
        "event_id": raw_data.get("event_id"),
        "match": normalize_match(
            f"{raw_data.get('home_team')} vs {raw_data.get('away_team')}"
        ),
        "start_time": raw_data.get("start_time"),
        "source": source,
        "markets": {}
    }

    odds = raw_data.get("odds", {})
    for raw_market_key, selections in odds.items():
        market_name = normalize_market(raw_market_key)
        normalized["markets"][market_name] = {}

        for sel_key, odd_val in selections.items():
            norm_sel = normalize_selection(sel_key)
            normalized["markets"][market_name][norm_sel] = odd_val

    return normalized
