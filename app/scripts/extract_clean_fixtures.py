import json
from pathlib import Path

INPUT_PATH = Path("sportybet_fixtures.json")
OUTPUT_PATH = Path("cleaned_sportybet_fixtures.json")

try:
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        raw_fixtures = json.load(f)

    if not isinstance(raw_fixtures, list):
        raise ValueError("Expected a list of fixture objects")

    print(f"Found {len(raw_fixtures)} total fixtures.")
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(raw_fixtures, f, indent=2)

    print(f"✅ Extracted fixtures saved to {OUTPUT_PATH.resolve()}")

except Exception as e:
    print(f"❌ Failed to extract fixtures: {e}")
