import httpx
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

SPORTYBET_BASE_URL = "https://www.sportybet.com/api/ng/fetch"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Example supported market IDs. You can expand this.
SUPPORTED_MARKETS = {
    "1X2": "full_time_result",
    "OVER_UNDER_2.5": "over_under_2_5_goals"
}


async def fetch_sportybet_odds(event_id: str) -> Optional[Dict]:
    """
    Fetches odds for a single SportyBet event using their public endpoint.
    """
    url = f"{SPORTYBET_BASE_URL}/event?eventId={event_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            return parse_sportybet_odds(data)
    except Exception as e:
        logger.error(f"[SportyBet] Failed to fetch odds for {event_id}: {e}")
        return None


def parse_sportybet_odds(data: dict) -> Dict:
    """
    Parses SportyBet response to extract market odds in a normalized format.
    """
    event = data.get("data", {}).get("event", {})
    markets = event.get("markets", [])

    normalized_odds = {}
    for market in markets:
        market_name = market.get("name")
        if market_name == "1X2":
            odds = {
                "home": market.get("selections", [])[0]["odds"],
                "draw": market.get("selections", [])[1]["odds"],
                "away": market.get("selections", [])[2]["odds"]
            }
            normalized_odds["full_time_result"] = odds

        elif market_name == "Over/Under 2.5":
            odds = {
                "over_2_5": market.get("selections", [])[0]["odds"],
                "under_2_5": market.get("selections", [])[1]["odds"]
            }
            normalized_odds["over_under_2_5_goals"] = odds

    return {
        "event_id": event.get("id"),
        "home_team": event.get("homeTeam", {}).get("name"),
        "away_team": event.get("awayTeam", {}).get("name"),
        "start_time": event.get("startTime"),
        "odds": normalized_odds
    }
