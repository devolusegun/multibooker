import json

# Load your normalized outcomes file
with open("normalized_outcomes_fixtures.json", "r", encoding="utf-8") as f:
    fixtures = json.load(f)

market_selections = {}

for fixture in fixtures:
    markets = fixture.get("markets", {})
    for market, selections in markets.items():
        # Selections can be a dict mapping (label: odd)
        if isinstance(selections, dict):
            for sel in selections:
                # Clean up the market and selection for consistency
                market_key = market.strip()
                sel_key = sel.strip()
                if market_key not in market_selections:
                    market_selections[market_key] = set()
                market_selections[market_key].add(sel_key)

# Now build the selection_map in desired format
selection_map = {}

for market, sels in market_selections.items():
    for sel in sels:
        # Only add if not already present
        if sel not in selection_map:
            selection_map[sel] = {"sportybet": sel}

# Write to JSON
with open("selection_map_complete.json", "w", encoding="utf-8") as f:
    json.dump(selection_map, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(selection_map)} unique selection options!")
