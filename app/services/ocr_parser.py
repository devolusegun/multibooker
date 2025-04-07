import pytesseract
import cv2
import numpy as np
from PIL import Image
import os
import re
from app.services.normalizer import normalize_match, normalize_market, normalize_selection

# Set this if you're on Windows and installed Tesseract manually
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(path: str) -> np.ndarray:
    img = cv2.imread(path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize for better OCR accuracy
    resized = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)

    # Apply thresholding
    _, thresh = cv2.threshold(resized, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh

def extract_text_from_image(path: str) -> str:
    preprocessed = preprocess_image(path)
    pil_image = Image.fromarray(preprocessed)
    text = pytesseract.image_to_string(pil_image)
    return text

def parse_bet_text(raw_text: str) -> list:
    lines = raw_text.split('\n')
    bets = []
    current_bet = {}
    last_line = ""
    second_last_line = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Clean OCR noise
        line = line.replace("®", "").replace("“", "").replace("”", "").replace("|", "")
        line = line.replace("@", "").replace("‘", "").replace("’", "").replace("¢", "")
        line = re.sub(r'[^\x00-\x7F]+', '', line)

        # Check if line is a known finish symbol (standalone)
        if line.strip().lower() in ["x", "✓", "✔", "×"]:
            current_bet["is_finished"] = True

        # Or if one of the last 2 lines contained a finish symbol
        if any(sym in second_last_line.lower() for sym in ["x", "✓", "✔", "×"]) or \
           any(sym in last_line.lower() for sym in ["x", "✓", "✔", "×"]):
            current_bet["is_finished"] = True

        # Detect live clues
        if any(live_key in line.lower() for live_key in ["live", "1st half", "2nd half", "break", "quarter", "overtime", "extra time"]):
            current_bet["is_live"] = True
        if re.search(r"\d{1,2}'", line):
            current_bet["is_live"] = True

        # Detect finished match by scoreline
        if re.match(r"^\d{2,3}-\d{2,3}$", line):
            current_bet["is_finished"] = True

        # Detect upcoming match by time string
        if re.search(r"\w{3},\s\w{3}\s\d{2}\s\d{1,2}:\d{2}\s[APap][Mm]", line):
            current_bet["is_upcoming"] = True

        # Match line
        if re.match(r".+\s[-vVs]{1,2}\s.+", line):
            if current_bet:
                bets.append(current_bet)
                current_bet = {}

            cleaned_match = re.sub(r'^[^a-zA-Z0-9]*', '', line)
            cleaned_match = re.sub(r'\s[ioa]{1,3}$', '', cleaned_match)
            current_bet["match"] = normalize_match(cleaned_match)

        # Market line
        elif any(keyword in line.lower() for keyword in ["total", "set", "win", "handicap", "score", "moneyline", "spread"]):
            current_bet["market"] = normalize_market(line)

        # Selection + odds
        elif re.search(r"\d+\.\d{1,2}$", line):
            match = re.match(r"(.+?)\s(\d+\.\d{1,2})$", line)
            if match:
                current_bet["selection"] = normalize_selection(match.group(1))
                current_bet["odd"] = float(match.group(2))
            elif "selection" not in current_bet:
                current_bet["selection"] = normalize_selection(last_line)
                current_bet["odd"] = float(line)

        # Track last two lines for symbol detection
        second_last_line = last_line
        last_line = line

    # Append final bet
    if current_bet:
        if "match" in current_bet:
            current_bet["match"] = normalize_match(current_bet["match"])
        if "market" in current_bet:
            current_bet["market"] = normalize_market(current_bet["market"])
        if "selection" in current_bet:
            current_bet["selection"] = normalize_selection(current_bet["selection"])
        bets.append(current_bet)

    # Final filter: Only upcoming matches allowed
    filtered_bets = []
    for bet in bets:
        if bet.get("is_upcoming") and not bet.get("is_live") and not bet.get("is_finished"):
            filtered_bets.append(bet)
        else:
            bet["excluded"] = True  # internal use only

    return filtered_bets