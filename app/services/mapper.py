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

# Load fresh fixtures from normalized_outcomes_fixtures.json
def load_fixtures():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "normalized_outcomes_fixtures.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Normalize name (removes suffixes and punctuation)
def normalize_name(name):
    name = name.lower()
    name = name.replace(" fc", "").replace(" sc", "").replace(" ac", "").replace(" cf", "")
    name = name.replace(".", "").replace(",", "").strip()
    return name

# Fuzzy match string against a list
def fuzzy_match(query, choices, threshold=70):
    query_norm = normalize_name(query)
    choices_norm = [normalize_name(c) for c in choices]
    match, score, idx = process.extractOne(query_norm, choices_norm, scorer=fuzz.token_sort_ratio)
    return choices[idx] if score >= threshold else None

# === MAIN Mapping Engine ===
def map_to_bookie(bet, bookie):
    try:
        market_map = load_market_map(bookie)
        selection_map = load_selection_map()
        fixtures = load_fixtures()
    except Exception as e:
        return {"error": str(e)}

    mapped = {"bookie": bookie}

    # Step 1: Match fixture
    input_match = bet.get("match")
    if not input_match:
        return {"error": "Missing match in bet"}

    fixture_names = [fx["match"] for fx in fixtures]
    matched_name = fuzzy_match(input_match, fixture_names, threshold=75)
    if not matched_name:
        return {"error": f"Match '{input_match}' not found on target bookie"}

    matched_fixture = next((fx for fx in fixtures if fx["match"] == matched_name), None)
    if not matched_fixture:
        return {"error": f"Fixture '{matched_name}' could not be loaded"}

    mapped["match"] = matched_fixture["match"]
    mapped["event_id"] = matched_fixture["event_id"]

    # Step 2: Map market
    market = bet.get("market")
    if not market:
        return {"error": "Missing market in bet"}

    market_key = market_map.get(market)
    if not market_key:
        return {"error": f"Market '{market}' not supported by {bookie}"}
    mapped["market"] = market_key

    # Step 3: Map or infer selection
    raw_selection = bet.get("selection", "").strip()
    clean_selection = " ".join(raw_selection.split())

    # 3a: Try selection map
    selection_entry = selection_map.get(clean_selection)
    if selection_entry:
        mapped_selection = selection_entry.get(bookie)
        if mapped_selection:
            mapped["selection"] = mapped_selection
        else:
            return {"error": f"Selection not supported by {bookie}"}
    else:
        # 3b: Fallback: infer from fixture market
        market_data = matched_fixture.get("markets", {}).get(market, {})
        if not market_data:
            return {"error": f"No outcomes found for market '{market}' in fixture"}

        # Try to match selection directly
        possible_outcomes = list(market_data.keys())
        fallback = fuzzy_match(clean_selection, possible_outcomes, threshold=70)
        if fallback:
            mapped["selection"] = fallback
        else:
            # 3c: Smart fallback for "Match Result" using team names
            if market.lower() == "match result":
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
