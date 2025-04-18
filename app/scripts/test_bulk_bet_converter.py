import json
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code
import asyncio

# === Raw OCR-style Stake bets (as seen in screenshot) ===
sample_bets = [
    {
        "match": "West Ham vs Southampton",
        "market": "Match Result",
        "selection": "West Ham United FC",
        "odd": 1.50
    },
    {
        "match": "Brentford FC vs Brighton & Hove Albion FC",
        "market": "Draw No Bet",
        "selection": "Brighton & Hove Albion FC",
        "odd": 1.99
    },
    {
        "match": "Crystal Palace vs Bournemouth",
        "market": "Both Teams to Score",
        "selection": "Yes",
        "odd": 1.62
    },
    {
        "match": "Everton FC vs Manchester City FC",
        "market": "Match Result",
        "selection": "Manchester City FC",
        "odd": 1.96
    },
    {
        "match": "Aston Villa vs Newcastle",
        "market": "Both Teams to Score",
        "selection": "Yes",
        "odd": 1.53
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
