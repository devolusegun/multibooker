import httpx
import logging

logger = logging.getLogger(__name__)

SPORTYBET_SHARE_API = "https://www.sportybet.com/ng/sporty-api/ng/betslip/share"

# NOTE: This structure is inferred from how SportyBet share betslip requests look in browser.
# You'll need to verify exact payload keys/structure via browser DevTools.

async def generate_sportybet_bet_code(event_id: str, market: str, selection: str) -> str:
    """
    Generate a playable SportyBet betslip code for a given event, market, and selection.

    Args:
        event_id (str): SportyBet's internal event ID.
        market (str): Normalized market name (e.g., 'Match Result').
        selection (str): Normalized selection name (e.g., 'Home').

    Returns:
        str: A betslip code the user can play on SportyBet.
    """
    try:
        payload = {
            "bets": [
                {
                    "eventId": event_id,
                    "market": market,       # You might need the market ID instead of string
                    "selection": selection  # You might need selection ID (e.g., 1=home, 2=draw)
                }
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(SPORTYBET_SHARE_API, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            return data.get("betCode") or data.get("code") or "UNKNOWN"

    except Exception as e:
        logger.error(f"Failed to generate SportyBet bet code: {e}")
        return "ERROR"
