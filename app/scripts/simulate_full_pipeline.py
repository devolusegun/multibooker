import json
import asyncio
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code

# === Simulated OCR-Extracted Bets ===
ocr_bets = [
    {
        "match": "Inter vs Bayern Munich",
        "market": "Match Result",
        "selection": "Home",
        "odd": 2.1
    },
    {
        "match": "Real Madrid vs Arsenal",
        "market": "Over/Under 2.5",
        "selection": "Over 2.5",
        "odd": 1.85
    }
]

BOOKIE = "sportybet"

async def run_full_pipeline():
    print("🎯 Simulating full pipeline: OCR Bet → SportyBet Code...\n")

    mapped_selections = []

    for idx, bet in enumerate(ocr_bets, 1):
        print(f"📌 Bet #{idx}: {bet['match']} | {bet['market']} | {bet['selection']} @ {bet['odd']}")
        mapped = map_to_bookie(bet, BOOKIE)

        if "error" in mapped:
            print(f"❌ Mapping Failed: {mapped['error']}\n")
        else:
            print("✅ Mapped:", json.dumps(mapped, indent=2))
            mapped_selections.append({
                "event_id": mapped.get("event_id", mapped.get("match")),
                "market_id": mapped["market"],
                "outcome_id": mapped["selection"]
            })

        print("-" * 50)

    if not mapped_selections:
        print("⚠️ No valid selections to generate a bet code.")
        return

    print("🎟️ Generating real SportyBet multibet code...\n")
    code = await generate_sportybet_code(mapped_selections)

    print(f"✅ Real Bet Code: {code}")
    print("📎 Copy and paste it into SportyBet to preview the betslip.")

if __name__ == "__main__":
    asyncio.run(run_full_pipeline())
