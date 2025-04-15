from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from app.services.ocr_parser import extract_text_from_image, parse_bet_text
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code
from app.services.generators.bet9ja_gen import generate_bet9ja_bet_code
import shutil

from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class OCRBet(BaseModel):
    match: str
    market: str
    selection: str
    odd: Optional[float] = None


@router.post("/upload-bet")
async def upload_bet(
    screenshot: UploadFile,
    betUrl: str = Form(None),
    bookie: str = Form("bet9ja")
):
    # 1. Save uploaded screenshot
    file_path = f"static/{screenshot.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(screenshot.file, buffer)

    # 2. Run OCR + parsing
    raw_text = extract_text_from_image(file_path)
    parsed_bets = parse_bet_text(raw_text)

    # 3. Map parsed bets into bookie-specific format
    mapped_selections = []
    mapped_bets = []

    for bet in parsed_bets:
        mapped = map_to_bookie(bet, bookie=bookie.lower())
        if "error" in mapped:
            return {
                "error": f"Mapping failed for bet: {mapped['error']}",
                "failed_bet": bet
            }

        mapped_bets.append(mapped)
        mapped_selections.append({
            "event_id": mapped.get("event_id", mapped.get("match")),
            "market_id": mapped["market"],
            "outcome_id": mapped["selection"]
        })

    # 4. Generate betslip code
    if bookie.lower() == "sportybet":
        code = await generate_sportybet_code(mapped_selections)
    elif bookie.lower() == "bet9ja":
        code = generate_bet9ja_bet_code("multi", "accumulator", "combo")
    else:
        raise HTTPException(status_code=400, detail="Unsupported bookie")

    # 5. Return all results
    return {
        "bookie": bookie,
        "bet_url": betUrl,
        "parsed_bets": parsed_bets,
        "mapped_bets": mapped_bets,
        "code": code,
        "copy_text": code
    }
