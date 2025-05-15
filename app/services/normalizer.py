import re
from typing import Dict

def normalize_match(match: str) -> str:
    """
    Normalize a match string like 'Villarreal CF vs CD Leganes'
    into 'villarreal vs leganes'
    """
    if not match or " vs " not in match.lower():
        return match.strip().lower()

    team1, team2 = map(str.strip, match.lower().split(" vs "))

    def clean(name):
        name = re.sub(r"\b(fc|cf|cd|sc|ac|afc|srl|team|club)\b", "", name)
        name = re.sub(r"[^\w\s]", "", name)
        name = re.sub(r"\s+", " ", name)
        return name.strip()

    return f"{clean(team1)} vs {clean(team2)}"

def normalize_market(raw_market: str) -> str:
    """
    Normalize market labels to standard internal keys.
    """
    market = raw_market.lower().strip()

    if "1x2" in market or "match result" in market or "match winner" in market:
        return "Match Result"
    if "both teams to score" in market or "btts" in market:
        return "BTTS"
    if "over/under 2.5" in market or "over under 2.5" in market:
        return "Over/Under 2.5"
    if "total" in market or "asian total" in market:
        return "Asian Total"
    if "double chance" in market:
        return "Double Chance"
    if "win the final" in market or "winner of the final" in market:
        return "Win The Final"
    if "handicap" in market:
        return "Handicap"

    return raw_market.title()

def normalize_selection(raw_selection: str) -> str:
    """
    Normalize selection strings like 'Over 2.5' or 'Home' to standard format.
    """
    selection = raw_selection.strip().lower()

    if selection in {"1", "home", "team 1"}:
        return "Home"
    if selection in {"x", "draw"}:
        return "Draw"
    if selection in {"2", "away", "team 2"}:
        return "Away"
    if "over" in selection and "2.5" in selection:
        return "Over 2.5"
    if "under" in selection and "2.5" in selection:
        return "Under 2.5"
    if "or" in selection and "draw" in selection:
        return selection.replace(" or ", " or ").title()
    if "handicap" in selection or "(" in selection:
        return raw_selection

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
