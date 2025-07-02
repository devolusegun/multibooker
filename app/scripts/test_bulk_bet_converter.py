import json
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code
import asyncio

sample_bets = [
    {
        "match": "Sogndal IL vs Lyn 1896 FK",
        "market": "Both Teams to Score",
        "selection": "Yes",
        "odd": 1.37,
        "kickoff": 1719076800000  # Sun, Jun 22, 2025 4:00 PM WAT
    },
    {
        "match": "Kalmar FF vs Orgryte IS",
        "market": "Double Chance",
        "selection": "Kalmar FF or Draw",
        "odd": 1.14,
        "kickoff": 1719076800000
    },
    {
        "match": "Hamarkameratene vs Tromsoe IL",
        "market": "Tromsoe IL Total",
        "selection": "Over 0.5",
        "odd": 1.20,
        "kickoff": 1719076800000
    },
    {
        "match": "Kristiansund BK vs Rosenborg BK",
        "market": "Both Teams to Score",
        "selection": "Yes",
        "odd": 1.53,
        "kickoff": 1719076800000
    },
    {
        "match": "Denmark vs France",
        "market": "Both Teams to Score",
        "selection": "Yes",
        "odd": 1.53,
        "kickoff": 1719080400000  # Sun, Jun 22, 2025 5:00 PM WAT
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
