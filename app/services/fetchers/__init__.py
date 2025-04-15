from .sportybet import fetch_sportybet_odds
from .bet9ja import fetch_bet9ja_odds

BOOKIE_FETCHERS = {
    "sportybet": fetch_sportybet_odds,
    "bet9ja": fetch_bet9ja_odds,
}


async def fetch_odds(bookie: str, event_id: str):
    """
    Dynamically fetch odds from a specified bookie.

    Args:
        bookie (str): Name of the bookie, e.g., "sportybet" or "bet9ja".
        event_id (str): ID of the event on that platform.

    Returns:
        dict or None: Normalized odds data or None if failed.
    """
    fetcher = BOOKIE_FETCHERS.get(bookie.lower())
    if not fetcher:
        raise ValueError(f"Unsupported bookie: {bookie}")
    
    try:
        return await fetcher(event_id)
    except Exception as e:
        # You can log errors here
        print(f"[{bookie.upper()}] Error fetching odds for event {event_id}: {e}")
        return None
