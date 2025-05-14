import json
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code
import asyncio

sample_bets = [
    {
        "match": "SC Telstar vs ADO Den Haag",
        "market": "Asian Total",
        "selection": "Over 2.5",
        "odd": 1.73,
        "kickoff": 1747155900000  # May 13, 2025 5:45 PM WAT
    },
    {
        "match": "Real Valladolid vs Girona FC",
        "market": "Asian Total",
        "selection": "Over 2.5",
        "odd": 1.77,
        "kickoff": 1747156800000  # May 13, 2025 6:00 PM WAT
    },
    {
        "match": "Stade Rochelais Basket vs AS Monaco",
        "market": "1st Half - Asian Handicap",
        "selection": "AS Monaco (-10.5)",
        "odd": 1.86,
        "kickoff": 1747160400000  # May 13, 2025 7:00 PM WAT
    },
    {
        "match": "Sunderland AFC vs Coventry City",
        "market": "Match Result",
        "selection": "Coventry City",
        "odd": 2.90,
        "kickoff": 1747164000000  # May 13, 2025 8:00 PM WAT
    },
    {
        "match": "Bologna FC 1909 vs AC Milan",
        "market": "Which Team Will Win The Final",
        "selection": "AC Milan",
        "odd": 1.80,
        "kickoff": 1747243200000  # May 14, 2025 8:00 PM WAT
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
