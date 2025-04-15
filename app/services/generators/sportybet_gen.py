import httpx
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

SPORTYBET_SHARE_API = "https://www.sportybet.com/ng/sporty-api/ng/betslip/share"

async def generate_sportybet_code(selections: List[Dict[str, str]]) -> str:
    """
    Generate a playable SportyBet betslip code for multiple selections.

    Each selection should be a dict with 'event_id', 'market_id', 'outcome_id' keys.
    """
    try:
        payload = {
            "bets": [
                {
                    "eventId": sel["event_id"],
                    "market": sel["market_id"],
                    "selection": sel["outcome_id"]
                }
                for sel in selections
            ]
        }
        print("Sending to SportyBet API:", json.dumps(payload, indent=2))  # log payload

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
