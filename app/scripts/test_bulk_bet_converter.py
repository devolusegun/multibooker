import json
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code
import asyncio

sample_bets = [
    {
        "match": "FC Lausanne-Sport vs FC Basel 1893",
        "market": "Double Chance",
        "selection": "Draw or FC Basel 1893",
        "odd": 1.63,
        "kickoff": 1747246200000  # May 14, 2025 7:30 PM WAT
    },
    {
        "match": "Glasgow Rangers vs Dundee United",
        "market": "Match Result",
        "selection": "Glasgow Rangers",
        "odd": 1.40,
        "kickoff": 1747247100000  # May 14, 2025 7:45 PM WAT
    },
    {
        "match": "Heart of Midlothian FC vs St Johnstone FC",
        "market": "Double Chance",
        "selection": "Heart of Midlothian FC or Draw",
        "odd": 1.18,
        "kickoff": 1747247100000
    },
    {
        "match": "Bologna FC vs AC Milan",
        "market": "Which Team Will Win The Final",
        "selection": "AC Milan",
        "odd": 1.76,
        "kickoff": 1747248000000  # May 14, 2025 8:00 PM WAT
    },
    {
        "match": "Aberdeen FC vs Celtic Glasgow",
        "market": "Match Result",
        "selection": "Celtic Glasgow",
        "odd": 1.64,
        "kickoff": 1747248000000
    }
]

BOOKIE = "sportybet"

async def run():
    print(f"🎯 Converting OCR-style bets to multibet code for {BOOKIE}...\n")
    mapped_selections = []

    for idx, bet in enumerate(sample_bets, 1):
        print(f"📌 Bet #{idx}: {bet['match']} | {bet['market']} | {bet['selection']} @ {bet['odd']}")
        mapped = map_to_bookie(bet, BOOKIE)

        if "error" in mapped:
            print(f"❌ Error: {mapped['error']}")
        else:
            print("✅ Mapped:", json.dumps(mapped, indent=2))
            mapped_selections.append({
                "event_id": mapped.get("event_id", mapped.get("match")),
                "market_id": mapped["market"],
                "outcome_id": mapped["selection"]
            })
        print("-" * 50)

    if not mapped_selections:
        print("⚠️ No valid selections were mapped, skipping code generation.")
        return

    print("🎟️ Generating multi-selection betslip code...\n")
    code = await generate_sportybet_code(mapped_selections)
    print(f"✅ Bet Code: {code}")
    print(f"📎 Copy and paste it into SportyBet to preview the multibet.")

if __name__ == "__main__":
    asyncio.run(run())
