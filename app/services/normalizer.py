import re

def normalize_match(raw_match: str) -> str:
    # Convert "Player A - Player B" → "Player A vs Player B"
    match = raw_match.replace("-", "vs").replace("  ", " ").strip()
    match = re.sub(r'\s{2,}', ' ', match)
    return match

def normalize_market(raw_market: str) -> str:
    # Lowercase + simplify known markets
    market = raw_market.lower().strip()

    # Football
    if "asian total" in market or "total" in market:
        return "Asian Total"
    if "1x2" in market or "match winner" in market:
        return "Match Result"
    if "both teams to score" in market or "btts" in market:
        return "BTTS"

    # Tennis
    if "to win a set" in market:
        return "To Win a Set"
    if "match winner" in market or "to win match" in market:
        return "Match Winner"
    if "total games" in market:
        return "Total Games"
    if "handicap" in market:
        return "Handicap"

    # Basketball
    if "points" in market:
        return "Total Points"
    if "spread" in market or "handicap" in market:
        return "Spread"
    if "moneyline" in market:
        return "Moneyline"

    return raw_market.title()  # fallback

def normalize_selection(raw_selection: str) -> str:
    selection = raw_selection.strip()

    # Common formatting cleanup
    selection = selection.replace("Over", "Over ").replace("Under", "Under ")
    return selection
