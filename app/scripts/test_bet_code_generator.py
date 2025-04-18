import json
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code

# ✅ Sample OCR-style bet (already confirmed to work)
sample_bet = {
    "match": "Inter vs Bayern Munich",
    "market": "Match Result",
    "selection": "Home",
    "odd": 2.1
}

BOOKIE = "sportybet"

if __name__ == "__main__":
    print(f"🎯 Generating bet code for {BOOKIE}...\n")
    mapped = map_to_bookie(sample_bet, BOOKIE)

    if "error" in mapped:
        print(f"❌ Mapping failed: {mapped['error']}")
    else:
        print("✅ Mapped Selection:")
        print(json.dumps(mapped, indent=2))

        selections = [{
            "event_id": mapped.get("event_id", mapped.get("match")),
            "market_id": mapped["market"],
            "outcome_id": mapped["selection"]
        }]

        try:
            import asyncio
            code = asyncio.run(generate_sportybet_code(selections))
            print(f"🎟️ Bet Code: {code}")
        except Exception as e:
            print(f"❌ Code generation failed: {e}")
