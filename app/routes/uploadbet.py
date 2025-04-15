from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import JSONResponse
from app.services.ocr_parser import extract_text_from_image, parse_bet_text
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code
from app.services.generators.bet9ja_gen import generate_bet9ja_bet_code
import shutil
import os

router = APIRouter()

@router.post("/upload-bet")
async def upload_bet(
    screenshot: UploadFile,
    betUrl: str = Form(None),
    bookie: str = Form("bet9ja")  # default to bet9ja, but accept sportybet or football.com
):
    file_path = f"static/{screenshot.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(screenshot.file, buffer)

    # Extract text and parse bets
    raw_text = extract_text_from_image(file_path)
    parsed_bets = parse_bet_text(raw_text)

    # Prepare mapped and mapped_selections for code generation
    mapped_bets = []
    mapped_selections = []

    for bet in parsed_bets:
        mapped = map_to_bookie(bet, bookie=bookie.lower())
        mapped_bets.append(mapped)

        if "error" not in mapped:
            mapped_selections.append({
                "event_id": mapped.get("event_id", mapped.get("match")),
                "market_id": mapped["market"],
                "outcome_id": mapped["selection"]
            })

    # Generate bet code
    code = ""
    if bookie.lower() == "sportybet":
        code = await generate_sportybet_code(mapped_selections)
    elif bookie.lower() == "bet9ja":
        code = generate_bet9ja_bet_code("multi", "accumulator", "combo")

    return {
        "bet_url": betUrl,
        "parsed_bets": parsed_bets,
        "mapped_bets": mapped_bets,
        "code": code,
        "copiable": code
    }
