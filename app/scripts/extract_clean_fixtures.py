import json
from pathlib import Path

INPUT_PATH = Path("sportybet_fixtures.json")
OUTPUT_PATH = Path("cleaned_sportybet_fixtures.json")

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    raw = json.load(f)

fixtures = []

try:
    tournaments = raw["data"]["tournaments"]
    for t in tournaments:
        for event in t.get("events", []):
            fixtures.append(event)
except Exception as e:
    print(f" Failed to extract fixtures: {e}")
    exit(1)

print(f"Found {len(fixtures)} total fixtures.")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(fixtures, f, indent=2)

print(f" Extracted fixtures saved to {OUTPUT_PATH}")
