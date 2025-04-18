
import json
from app.services.mapper import map_to_bookie

# === Sample OCR-style bets (using live fixtures) ===
sample_bets = [
    {
        "match": "Inter vs Bayern Munich",
        "market": "Match Result",
        "selection": "Home",
        "odd": 2.10
    },
    {
        "match": "Real Madrid vs Arsenal",
        "market": "Over/Under 2.5",
        "selection": "Over 2.5",
        "odd": 1.85
    }
]

BOOKIE = "sportybet"

if __name__ == "__main__":
    print(f"🔍 Mapping sample bets to {BOOKIE} format...\n")

    for idx, bet in enumerate(sample_bets, 1):
        print(f"📌 Bet #{idx}: {bet['match']} | {bet['market']} | {bet['selection']} @ {bet['odd']}")
        mapped = map_to_bookie(bet, BOOKIE)

        if "error" in mapped:
            print(f"❌ Error: {mapped['error']}")
        else:
            print("✅ Mapped:", json.dumps(mapped, indent=2))

        print("-" * 50)
