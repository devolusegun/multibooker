import json
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code
import asyncio

# === Raw OCR-style Stake bets (as seen in screenshot) ===
sample_bets = [
    {
        "match": "Internacional FC De Palmira vs Tigres FC",
        "market": "Match Result",
        "selection": "Internacional FC De Palmira",
        "odd": 1.79,
        "kickoff": 1745267400000  # April 21, 2025 9:30 PM WAT
    },
    {
        "match": "CS 2 de Mayo vs Sportivo Ameliano",
        "market": "Match Result",
        "selection": "CS 2 de Mayo",
        "odd": 2.21,
        "kickoff": 1745269200000  # April 21, 2025 10:00 PM WAT
    },
    {
        "match": "Amazonas FC AM vs Avai FC SC",
        "market": "Match Result",
        "selection": "Amazonas FC AM",
        "odd": 2.39,
        "kickoff": 1745269200000
    },
    {
        "match": "Gremio Novorizontino SP vs Criciuma EC SC",
        "market": "Match Result",
        "selection": "Gremio Novorizontino SP",
        "odd": 1.95,
        "kickoff": 1745272800000  # April 21, 2025 11:00 PM WAT
    },
    {
        "match": "Cavaliers FC vs Chapelton Maroons FC",
        "market": "Match Result",
        "selection": "Cavaliers FC",
        "odd": 1.59,
        "kickoff": 1745272800000
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
