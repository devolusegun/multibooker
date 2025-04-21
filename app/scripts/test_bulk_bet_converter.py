import json
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code
import asyncio

# === Raw OCR-style Stake bets (as seen in screenshot) ===
sample_bets = [
    {
    "match": "Real Madrid vs Athletic Bilbao",
    "market": "Double Chance",
    "selection": "Real Madrid or draw",
    "odd": 1.11,
    "kickoff": 1745181900000
    },
    {
        "match": "Girona FC vs Real Betis Balompie",
        "market": "Handicap 0:2",
        "selection": "Real Betis Balompie (0:2)",
        "odd": 1.12,
        "kickoff": 1745265600000
    },
    {
        "match": "Valencia CF vs RCD Espanyol Barcelona",
        "market": "Double Chance",
        "selection": "Valencia CF or draw",
        "odd": 1.2,
        "kickoff": 1745344800000
    },
    {
        "match": "Manchester City FC vs Aston Villa FC",
        "market": "Handicap 0:3",
        "selection": "Aston Villa FC (0:3)",
        "odd": 1.12,
        "kickoff": 1745352000000
    },
    {
        "match": "FC Barcelona vs RCD Mallorca",
        "market": "Match Result",
        "selection": "FC Barcelona",
        "odd": 1.24,
        "kickoff": 1745353800000
    },
    {
        "match": "RC Celta de Vigo vs Villarreal CF",
        "market": "Match Result",
        "selection": "RC Celta de Vigo",
        "odd": 1.0,
        "kickoff": 1745431200000
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
