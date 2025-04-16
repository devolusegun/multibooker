import json
import os
from typing import List, Dict
from pathlib import Path

from app.services.normalizer import (
    normalize_match,
    normalize_market,
    normalize_selection,
)

INPUT_FILE = "cleaned_sportybet_fixtures.json"
OUTPUT_FILE = "normalized_outcomes_fixtures.json"


def normalize_fixture_data(raw_data: Dict) -> Dict:
    """
    Converts a raw fixture dict from SportyBet into Multibooker’s internal format.
    Only normalizes markets with outcome-based odds.
    """
    try:
        event_id = raw_data.get("eventId")
        match = normalize_match(
            f"{raw_data.get('homeTeamName')} vs {raw_data.get('awayTeamName')}"
        )
        start_time = raw_data.get("estimateStartTime")
        markets = raw_data.get("markets", [])

        normalized = {
            "event_id": event_id,
            "match": match,
            "start_time": start_time,
            "source": "SportyBet",
            "markets": {},
        }

        for market in markets:
            raw_market_name = market.get("desc", "Unknown Market")
            norm_market = normalize_market(raw_market_name)
            outcomes = market.get("outcomes", [])

            if not outcomes:
                continue

            normalized["markets"][norm_market] = {}
            for outcome in outcomes:
                raw_sel = outcome.get("desc", "")
                odds = outcome.get("odds", "0")
                norm_sel = normalize_selection(raw_sel)
                normalized["markets"][norm_market][norm_sel] = odds

        return normalized

    except Exception as e:
        print(f"Error normalizing fixture: {e}")
        return None


def load_raw_fixtures(filepath: str) -> List[Dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_fixtures = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                item = item.strip()
                if not item:
                    continue
                try:
                    item = json.loads(item)
                except json.JSONDecodeError:
                    print(" Skipping malformed string:", item[:30], "...")
                    continue
            if isinstance(item, dict):
                raw_fixtures.append(item)
    elif isinstance(data, dict):
        raw_fixtures.append(data)

    return raw_fixtures


if __name__ == "__main__":
    print("Loading fixture data...")

    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_FILE)

    if not input_path.exists():
        print(f"Input file not found: {INPUT_FILE}")
        exit(1)

    raw_fixtures = load_raw_fixtures(INPUT_FILE)
    print(f"Found {len(raw_fixtures)} raw fixtures")

    normalized = []
    for fixture in raw_fixtures:
        if fixture.get("markets"):
            norm = normalize_fixture_data(fixture)
            if norm:
                normalized.append(norm)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=2)

    print(f" Normalized {len(normalized)} fixtures and saved to {output_path.resolve()}")
