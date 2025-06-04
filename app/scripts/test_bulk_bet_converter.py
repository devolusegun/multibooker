import json
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code
import asyncio

sample_bets = [
    {
        "match": "Spain vs France",
        "market": "Match Result",
        "selection": "Draw",
        "odd": 3.30,
        "kickoff": 1717617600000  # Thu, Jun 5, 2025 8:00 PM WAT
    },
    {
        "match": "ecuador vs brazil",
        "market": "Match Result",
        "selection": "Brazil",
        "odd": 2.10,
        "kickoff": 1749121200000  # Fri, Jun 6, 2025 12:00 AM WAT
    },
    {
        "match": "Chile vs Argentina",
        "market": "Match Result",
        "selection": "Argentina",
        "odd": 1.75,
        "kickoff": 1717639200000  # Fri, Jun 6, 2025 2:00 AM WAT
    },
    {
        "match": "Poland vs Moldova",
        "market": "Match Result",
        "selection": "Poland",
        "odd": 1.27,
        "kickoff": 1717688700000  # Fri, Jun 6, 2025 7:45 PM WAT
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
