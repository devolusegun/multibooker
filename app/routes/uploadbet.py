from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import JSONResponse
from app.services.ocr_parser import extract_text_from_image, parse_bet_text
from app.services.mapper import map_to_bookie
import shutil

router = APIRouter()

@router.post("/upload-bet")
async def upload_bet(
    screenshot: UploadFile,
    betUrl: str = Form(None),
    bookie: str = Form("bet9ja")  # default to bet9ja, but accept sportybet or football.com
):
    file_path = f"static/{screenshot.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(screenshot.file, buffer)

    #text = extract_text_from_image(file_path)
    raw_text = extract_text_from_image(file_path)
    parsed_bets = parse_bet_text(raw_text)

    mapped_bets = []
    for bet in parsed_bets:
        mapped = map_to_bookie(bet, bookie=bookie.lower())
        mapped_bets.append(mapped)

    return {
        "bet_url": betUrl,
        "parsed_bets": parsed_bets,
        "mapped_bets": mapped_bets
    }