import json
from pathlib import Path
from typing import List, Dict
from app.services.normalizer import (
    normalize_match,
    normalize_market,
    normalize_selection,
)

INPUT_FILE = "cleaned_sportybet_fixtures.json"
OUTPUT_FILE = "normalized_outcomes_fixtures.json"

def normalize_fixture_data(raw_data: Dict) -> Dict:
    try:
        event_id = raw_data.get("eventId")
        home = raw_data.get("homeTeamName", "")
        away = raw_data.get("awayTeamName", "")
        start_time = raw_data.get("estimateStartTime")
        markets = raw_data.get("markets", [])

        if not home or not away or not event_id:
            raise ValueError("Missing essential match data")

        normalized = {
            "event_id": event_id,
            "match": normalize_match(f"{home} vs {away}"),
            "start_time": start_time,
            "source": "SportyBet",
            "markets": {},
        }

        for market in markets:
            market_name = market.get("desc") or market.get("name") or "Unknown Market"
            norm_market = normalize_market(market_name)
            outcomes = market.get("outcomes", [])

            if not outcomes:
                continue

            normalized["markets"][norm_market] = {}
            for outcome in outcomes:
                raw_sel = outcome.get("desc", "") or outcome.get("name", "")
                odds = outcome.get("odds", "0")
                if not raw_sel:
                    continue
                norm_sel = normalize_selection(raw_sel)
                normalized["markets"][norm_market][norm_sel] = odds

        return normalized

    except Exception as e:
        print(f"⚠️ Error normalizing fixture: {e}")
        return None

def load_fixtures(path: Path) -> List[Dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [fx for fx in data if isinstance(fx, dict)]
    except Exception as e:
        print(f"❌ Failed to load fixtures: {e}")
        return []

if __name__ == "__main__":
    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_FILE)

    print("📥 Loading fixture data...")
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path.resolve()}")
        exit(1)

    raw_fixtures = load_fixtures(input_path)
    print(f"🔍 Found {len(raw_fixtures)} raw fixtures")

    normalized = []
    for fx in raw_fixtures:
        norm = normalize_fixture_data(fx)
        if norm:
            normalized.append(norm)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=2)

    print(f"✅ Normalized {len(normalized)} fixtures saved to {output_path.resolve()}")
