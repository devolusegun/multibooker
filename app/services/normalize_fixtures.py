import json
from pathlib import Path
from typing import List, Dict
from app.services.normalizer import (
    normalize_match,
    normalize_market,
    normalize_selection
)

def normalize_fixture_data(raw_data: Dict) -> Dict:
    """
    Normalize a single fixture item into Multibooker's internal format.
    """
    normalized = {
        "event_id": raw_data.get("eventId"),
        "match": normalize_match(
            f"{raw_data.get('homeTeamName')} vs {raw_data.get('awayTeamName')}"
        ),
        "start_time": raw_data.get("estimateStartTime"),
        "source": "SportyBet",
        "markets": {}
    }

    markets = raw_data.get("markets", [])
    for market in markets:
        market_name = normalize_market(market.get("desc", "Unknown"))
        normalized["markets"][market_name] = {}

        for outcome in market.get("outcomes", []):
            selection = normalize_selection(outcome.get("desc", "Unknown"))
            odds = outcome.get("odds")
            normalized["markets"][market_name][selection] = odds

    return normalized


def normalize_all_fixtures(raw_json_path: str, output_path: str) -> None:
    """
    Load raw JSON, normalize it, and save to output file.
    """
    with open(raw_json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    fixture_list = raw.get("data", [])
    normalized_fixtures: List[Dict] = []

    for fixture in fixture_list:
        try:
            normalized = normalize_fixture_data(fixture)
            normalized_fixtures.append(normalized)
        except Exception as e:
            print(f"⚠️ Skipped a fixture due to error: {e}")

    # Save to file
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(normalized_fixtures, out, indent=2)

    print(f"✅ Normalized {len(normalized_fixtures)} fixtures saved to: {output_path}")


# Optional: enable CLI usage
if __name__ == "__main__":
    INPUT_FILE = str(Path(__file__).parent.parent.parent / "sportybet_fixtures.json")
    OUTPUT_FILE = str(Path(__file__).parent.parent.parent / "normalized_sportybet.json")
    normalize_all_fixtures(INPUT_FILE, OUTPUT_FILE)
