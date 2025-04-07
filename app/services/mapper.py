import json
import os
from rapidfuzz import process, fuzz

MAPPING_DIR = os.path.join(os.path.dirname(__file__), "mappings")

# Load market map for a specific bookie
def load_market_map(bookie):
    path = os.path.join(MAPPING_DIR, f"markets_{bookie}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Market map for '{bookie}' not found.")
    with open(path, "r") as f:
        return json.load(f)

# Load universal selection map
def load_selection_map():
    path = os.path.join(MAPPING_DIR, "selection_map.json")
    with open(path, "r") as f:
        return json.load(f)

# Simulated match fixtures — this would be scraped or fetched live in production
MOCK_FIXTURES = [
    # Commonly used names
    "Royal Antwerp FC vs Club Brugge",
    "Go Ahead Eagles vs FC Utrecht",
    "Baez, Sebastian vs Cobolli, Flavio",
    "Wawrinka, Stan vs Tabilo, Alejandro",
    "Monfils, Gael vs Marozsan, Fabian",
    "Medvedev, Daniil vs Khachanov, Karen",

    # Bookie-specific name formats
    "Royal Antwerp vs Club Brugge KV",                 # SportyBet
    "Antwerp FC vs Brugge",                            # Football.com.ng
    "G.A. Eagles vs Utrecht",                          # SportyBet variant
    "GS Warriors vs Houston",                          # SportyBet NBA
    "Golden State vs Houston Rockets",                 # Football.com.ng variant
]

def find_closest_match(input_match, fixtures):
    match, score, _ = process.extractOne(
        input_match, fixtures, scorer=fuzz.token_sort_ratio
    )
    return match if score >= 80 else None

def map_to_bookie(bet, bookie):
    try:
        market_map = load_market_map(bookie)
        selection_map = load_selection_map()
    except Exception as e:
        return {"error": str(e)}

    mapped = {"bookie": bookie}

    # Validate and normalize match
    match = bet.get("match")
    if not match:
        return {"error": "Missing match in bet"}

    matched_fixture = find_closest_match(match, MOCK_FIXTURES)
    if not matched_fixture:
        return {"error": f"Match '{match}' not found on target bookie"}
    mapped["match"] = matched_fixture

    # Validate and map market
    market = bet.get("market")
    if not market:
        return {"error": "Missing market in bet"}

    market_key = market_map.get(market)
    if not market_key:
        return {"error": f"Market '{market}' not supported by {bookie}"}
    mapped["market"] = market_key

    # Validate and map selection
    selection = bet.get("selection")
    if not selection:
        return {"error": "Missing selection in bet"}

    clean_selection = " ".join(selection.split()).strip()
    selection_options = selection_map.get(clean_selection)
    if not selection_options:
        return {"error": f"Selection '{clean_selection}' not found in selection map"}
    mapped["selection"] = selection_options.get(bookie)
    if not mapped["selection"]:
        return {"error": f"Selection not supported by {bookie}"}

    # Pass through odds
    mapped["odd"] = bet.get("odd")

    return mapped
