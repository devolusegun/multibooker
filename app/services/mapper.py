import json
import os
from rapidfuzz import process, fuzz
from datetime import datetime, timedelta

MAPPING_DIR = os.path.join(os.path.dirname(__file__), "mappings")

# === Loaders ===
def load_market_map(bookie):
    path = os.path.join(MAPPING_DIR, f"markets_{bookie}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Market map for '{bookie}' not found.")
    with open(path, "r") as f:
        return json.load(f)

def load_selection_map():
    path = os.path.join(MAPPING_DIR, "selection_map.json")
    with open(path, "r") as f:
        return json.load(f)

def load_fixtures():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "normalized_outcomes_fixtures.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# === Helpers ===
def normalize_name(name):
    name = name.lower()
    name = name.replace(" fc", "").replace(" sc", "").replace(" ac", "").replace(" cf", "")
    name = name.replace(".", "").replace(",", "").strip()
    return name

def fuzzy_match(query, choices, threshold=70):
    query_norm = normalize_name(query)
    choices_norm = [normalize_name(c) for c in choices]
    match, score, idx = process.extractOne(query_norm, choices_norm, scorer=fuzz.token_sort_ratio)
    return choices[idx] if score >= threshold else None

# === Smart Fixture Matcher (Name + Kickoff Time) ===
def match_fixture(input_match, input_time, fixtures, threshold=75):
    input_norm = normalize_name(input_match)
    input_dt = datetime.fromtimestamp(input_time / 1000) if input_time else None

    candidates = []
    for fx in fixtures:
        fx_name = fx["match"]
        fx_norm = normalize_name(fx_name)
        fx_time = fx.get("start_time")

        if fx_time and input_dt:
            fx_dt = datetime.fromtimestamp(fx_time / 1000)
            time_diff = abs((fx_dt - input_dt).total_seconds())
        else:
            time_diff = float("inf")

        score = fuzz.token_sort_ratio(input_norm, fx_norm)
        if score >= threshold and time_diff <= 1800:  # 30 minutes margin
            candidates.append((fx, score, time_diff))

    # Prefer best fuzzy + closest time
    if candidates:
        candidates.sort(key=lambda x: (-x[1], x[2]))  # highest score, closest time
        return candidates[0][0]
    return None

# === Main Mapping Engine ===
def map_to_bookie(bet, bookie):
    try:
        market_map = load_market_map(bookie)
        selection_map = load_selection_map()
        fixtures = load_fixtures()
    except Exception as e:
        return {"error": str(e)}

    mapped = {"bookie": bookie}

    # Step 1: Match fixture by name + time
    input_match = bet.get("match")
    input_time = bet.get("kickoff")  # UNIX ms if available
    if not input_match:
        return {"error": "Missing match in bet"}

    matched_fixture = match_fixture(input_match, input_time, fixtures)
    if not matched_fixture:
        return {"error": f"Match '{input_match}' not found by name and time"}

    mapped["match"] = matched_fixture["match"]
    mapped["event_id"] = matched_fixture["event_id"]

    # Step 2: Market
    market = bet.get("market")
    if not market:
        return {"error": "Missing market in bet"}
    market_key = market_map.get(market)
    if not market_key:
        return {"error": f"Market '{market}' not supported by {bookie}"}
    mapped["market"] = market_key

    # Step 3: Selection
    raw_selection = bet.get("selection", "").strip()
    clean_selection = " ".join(raw_selection.split())

    selection_entry = selection_map.get(clean_selection)
    if selection_entry:
        mapped_selection = selection_entry.get(bookie)
        if mapped_selection:
            mapped["selection"] = mapped_selection
        else:
            return {"error": f"Selection not supported by {bookie}"}
    else:
        market_data = matched_fixture.get("markets", {}).get(market, {})
        if not market_data:
            return {"error": f"No outcomes found for market '{market}' in fixture"}

        fallback = fuzzy_match(clean_selection, list(market_data.keys()), threshold=70)
        if fallback:
            mapped["selection"] = fallback
        elif market.lower() == "match result":
            home, away = matched_fixture["match"].split(" vs ")
            norm_sel = normalize_name(clean_selection)
            if fuzz.partial_ratio(norm_sel, normalize_name(home)) > 70:
                mapped["selection"] = "1"
            elif fuzz.partial_ratio(norm_sel, normalize_name(away)) > 70:
                mapped["selection"] = "2"
            elif "draw" in norm_sel or norm_sel in ["x", "d"]:
                mapped["selection"] = "X"
            else:
                return {"error": f"Selection '{clean_selection}' not matched to team name or X"}
        else:
            return {"error": f"Selection '{clean_selection}' not found in selection map or fixture"}

    mapped["odd"] = bet.get("odd")
    return mapped
