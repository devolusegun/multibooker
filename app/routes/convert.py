from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from app.services.fetchers import fetch_odds
from app.services.normalizer import normalize_match, normalize_market, normalize_selection
from app.services.generators.sportybet_gen import generate_sportybet_code
from app.services.generators.bet9ja_gen import generate_bet9ja_bet_code
from app.services.generators.sportybet_gen import generate_sportybet_code

from app.services.mapper import map_to_bookie
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/convert",
    tags=["Convert Stake Bet"]
)

# === EXISTING GET endpoint ===
@router.get("/")
async def convert_to_bookie_format(
    match: str = Query(..., example="Man City vs Arsenal"),
    market: str = Query(..., example="Match Result"),
    selection: str = Query(..., example="Home"),
    bookie: str = Query(..., example="sportybet"),
    event_id: str = Query(..., example="12345678")
) -> Dict:
    """
    Convert a normalized bet (match, market, selection) into a format
    the destination bookie understands — including the real selection code.
    """
    normalized_match = normalize_match(match)
    normalized_market = normalize_market(market)
    normalized_selection = normalize_selection(selection)

    odds_data = await fetch_odds(bookie, event_id)
    if not odds_data:
        raise HTTPException(status_code=404, detail=f"No odds found for event {event_id} on {bookie}")

    bookie_market_key = normalized_market.lower().replace(" ", "_")
    bookie_selection_key = normalized_selection.lower().replace(" ", "_")

    market_data = odds_data.get("odds", {}).get(bookie_market_key)
    if not market_data:
        raise HTTPException(status_code=404, detail=f"Market '{normalized_market}' not found for {bookie}")

    selection_odds = market_data.get(bookie_selection_key)
    if not selection_odds:
        raise HTTPException(status_code=404, detail=f"Selection '{normalized_selection}' not found for {bookie}")

    return {
        "bookie": bookie,
        "event_id": odds_data.get("event_id"),
        "home_team": odds_data.get("home_team"),
        "away_team": odds_data.get("away_team"),
        "market": bookie_market_key,
        "selection": bookie_selection_key,
        "odds": selection_odds,
        "bet_format": {
            "event_id": odds_data.get("event_id"),
            "market": bookie_market_key,
            "selection": bookie_selection_key
        }
    }


# === NEW POST /convert/sportybet ===

class Selection(BaseModel):
    event_id: str
    market_id: str
    outcome_id: str

class ConvertRequest(BaseModel):
    bookie: str
    selections: List[Selection]


@router.post("/sportybet")
async def convert_to_sportybet(request: ConvertRequest):
    if request.bookie.lower() != "sportybet":
        raise HTTPException(status_code=400, detail="Only SportyBet is supported for now.")

    try:
        selections = [
            {
                "event_id": sel.event_id,
                "market_id": sel.market_id,
                "outcome_id": sel.outcome_id
            }
            for sel in request.selections
        ]

        code = await generate_sportybet_code(mapped_selections)
        return {
            "bookie": "sportybet",
            "code": code
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert to SportyBet: {e}")


@router.get("/bet9ja")
async def convert_to_bet9ja(
    match: str = Query(..., example="Man City vs Arsenal"),
    market: str = Query(..., example="Match Result"),
    selection: str = Query(..., example="Home"),
    event_id: str = Query(..., example="12345678")
) -> Dict:
    """
    Convert a normalized Stake bet into Bet9ja format and generate a simulated betslip code.
    """
    normalized_match = normalize_match(match)
    normalized_market = normalize_market(market)
    normalized_selection = normalize_selection(selection)

    odds_data = await fetch_odds("bet9ja", event_id)
    if not odds_data:
        raise HTTPException(status_code=404, detail=f"No odds found for event {event_id} on Bet9ja")

    market_key = normalized_market.lower().replace(" ", "_")
    selection_key = normalized_selection.lower().replace(" ", "_")

    market_data = odds_data.get("odds", {}).get(market_key)
    if not market_data:
        raise HTTPException(status_code=404, detail=f"Market '{normalized_market}' not found for Bet9ja")

    selection_odds = market_data.get(selection_key)
    if not selection_odds:
        raise HTTPException(status_code=404, detail=f"Selection '{normalized_selection}' not found for Bet9ja")

    # Simulated (future real) betslip code
    fake_code = generate_bet9ja_bet_code(
        event_id=event_id,
        market=market_key,
        selection=selection_key
    )

    return {
        "bookie": "bet9ja",
        "event_id": odds_data.get("event_id"),
        "home_team": odds_data.get("home_team"),
        "away_team": odds_data.get("away_team"),
        "market": market_key,
        "selection": selection_key,
        "odds": selection_odds,
        "bet_code": fake_code,
        "copy_text": fake_code
    }

# === OCR bet model ===
class OCRBet(BaseModel):
    match: str
    market: str
    selection: str
    odd: Optional[float] = None

class BulkConvertRequest(BaseModel):
    bookie: str
    bets: List[OCRBet]

@router.post("/from-ocr")
async def convert_from_ocr(request: BulkConvertRequest):
    mapped_selections = []

    for bet in request.bets:
        mapped = map_to_bookie(bet.dict(), request.bookie)
        if "error" in mapped:
            return {
                "error": f"Failed to map bet: {mapped['error']}",
                "failed_bet": bet
            }
        mapped_selections.append({
            "event_id": mapped.get("event_id", mapped.get("match")),  # fallback
            "market_id": mapped["market"],
            "outcome_id": mapped["selection"]
        })

    # === SPORTYBET handling ===
    if request.bookie.lower() == "sportybet":
        code = await generate_sportybet_code(mapped_selections)
        return {
            "bookie": "sportybet",
            "code": code,
            "copiable": code
        }

    # === BET9JA handling (simulated) ===
    elif request.bookie.lower() == "bet9ja":
        code = generate_bet9ja_bet_code("multi", "accumulator", "combo")
        return {
            "bookie": "bet9ja",
            "code": code,
            "copiable": code
        }

    return {
        "error": f"Bookie '{request.bookie}' not supported yet"
    }