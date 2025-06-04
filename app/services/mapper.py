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
def match_fixture(
    input_match,
    input_time,
    fixtures,
    threshold=75,
    time_window_seconds=5400,     # 90 minutes for "good" match window
    max_reasonable_gap_seconds=3*3600,  # 3 hours for "safe" fallback
    debug=False,
    allow_large_gap=False         # Set to True to allow large time fallback (with warning), or False to block
):
    from datetime import datetime
    from rapidfuzz import fuzz

    input_norm = normalize_name(input_match)
    input_dt = datetime.fromtimestamp(input_time / 1000) if input_time else None

    candidates = []
    all_candidates = []  # For debug and fallback

    # First pass: collect candidates above threshold within window
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
        all_candidates.append({
            "fixture": fx_name,
            "score": score,
            "time_diff_secs": time_diff,
            "time_diff_mins": None if time_diff == float("inf") else round(time_diff / 60, 1),
            "start_time": fx_time,
            "fx_obj": fx
        })
        if score >= threshold and time_diff <= time_window_seconds:
            candidates.append((fx, score, time_diff))

    # --- Main selection: best name & closest time within normal window ---
    if candidates:
        candidates.sort(key=lambda x: (-x[1], x[2]))  # best score, then closest time
        if debug:
            print(f"\n[DEBUG] Matched '{input_match}' to fixtures within window (sorted):")
            for fx, score, time_diff in candidates:
                print(f"  - {fx['match']} | Score: {score} | Time diff (mins): {time_diff/60:.1f} | Start: {fx['start_time']}")
        # If multiple, return the closest time (first in sorted list)
        return candidates[0][0]

    # --- Debug: show top near misses ---
    if debug:
        print("\n[DEBUG] No exact match found for:", input_match, "at", input_time)
        print("[DEBUG] Top 5 close candidates (by name & time):")
        all_candidates.sort(key=lambda c: (-c["score"], c["time_diff_mins"] if c["time_diff_mins"] is not None else float("inf")))
        for cand in all_candidates[:5]:
            print(
                f"  - Fixture: {cand['fixture']} | Score: {cand['score']} | "
                f"Time diff (mins): {cand['time_diff_mins']} | Start time: {cand['start_time']}"
            )
        print("[DEBUG] ----\n")

    # --- Fallback: best name match, warn/block if gap is large ---
    # Pick the highest-scoring candidate, regardless of time gap
    if all_candidates:
        best = max(all_candidates, key=lambda c: c['score'])
        # Only accept fallback if the name is a solid match (you can adjust threshold here)
        if best["score"] >= threshold:
            if best["time_diff_secs"] is not None and best["time_diff_secs"] > max_reasonable_gap_seconds:
                warning = (
                    f"⚠️ Fallback match for '{input_match}' is over {max_reasonable_gap_seconds/3600:.1f} hours "
                    f"off ({best['time_diff_mins']} mins): {best['fixture']}"
                )
                print(warning) if debug else None
                if not allow_large_gap:
                    # Block mapping: return error, you could instead raise or prompt user in a UI
                    return {"error": warning}
            # Allow mapping (with or without warning)
            return best["fx_obj"]
    # If truly nothing found
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

    #matched_fixture = match_fixture(input_match, input_time, fixtures, time_window_seconds=5400, debug=True)
    matched_fixture = match_fixture(
        input_match, input_time, fixtures,
        time_window_seconds=5400,        # normal window: 90 min
        max_reasonable_gap_seconds=3*3600,  # large gap warning: 3 hours
        debug=True,                      # see console output
        allow_large_gap=True            # block mapping if gap is large (best for prod)
    )
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

    # First check selection map
    selection_entry = selection_map.get(clean_selection)
    if selection_entry:
        mapped_selection = selection_entry.get(bookie)
        if mapped_selection:
            mapped["selection"] = mapped_selection
        else:
            return {"error": f"Selection '{clean_selection}' not supported by {bookie}"}
    else:
        market_data = matched_fixture.get("markets", {}).get(market, {})
        if not market_data:
            return {"error": f"No outcomes found for market '{market}' in fixture"}

        # Try fallback fuzzy match on fixture outcomes
        fallback = fuzzy_match(clean_selection, list(market_data.keys()), threshold=65)
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
        elif market.lower() == "double chance":
            home, away = matched_fixture["match"].split(" vs ")
            norm_sel = normalize_name(clean_selection)
            if "draw" in norm_sel:
                if fuzz.partial_ratio(norm_sel, f"{home} or draw") > 65:
                    mapped["selection"] = "1X"
                elif fuzz.partial_ratio(norm_sel, f"draw or {home}") > 65:
                    mapped["selection"] = "1X"
                elif fuzz.partial_ratio(norm_sel, f"{away} or draw") > 65:
                    mapped["selection"] = "X2"
                elif fuzz.partial_ratio(norm_sel, f"draw or {away}") > 65:
                    mapped["selection"] = "X2"
            elif fuzz.partial_ratio(norm_sel, f"{home} or {away}") > 65:
                mapped["selection"] = "12"
            else:
                return {"error": f"Double Chance selection '{clean_selection}' not mapped"}
        else:
            return {"error": f"Selection '{clean_selection}' not found in selection map or fixture"}

    mapped["odd"] = bet.get("odd")
    return mapped
