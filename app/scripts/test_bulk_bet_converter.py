from datetime import datetime
import json
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code
import asyncio

sample_bets = [
    {
        "match": "Vaasan Palloseura vs FC Haka Valkeakoski",
        "market": "Match Result",
        "selection": "Vaasan Palloseura",
        "odd": 1.91,
        "kickoff": int(datetime(2025, 7, 2, 16, 0).timestamp() * 1000)   # Wed, Jul 02 4:00PM
    },
    {
        "match": "Oulun Luistinseura vs KPV Kokkola",
        "market": "Match Result",
        "selection": "Oulun Luistinseura",
        "odd": 1.60,
        "kickoff": int(datetime(2025, 7, 2, 16, 30).timestamp() * 1000)  # Wed, Jul 02 4:30PM
    },
    {
        "match": "FC Dila Gori vs FC Spaeri",
        "market": "Match Result",
        "selection": "FC Dila Gori",
        "odd": 1.62,
        "kickoff": int(datetime(2025, 7, 2, 17, 0).timestamp() * 1000)   # Wed, Jul 02 5:00PM
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

            # This uses the mapped fixture teams, not OCR values
            home, away = mapped["match"].split(" vs ")
            stake_sel = bet["selection"].strip().lower()

            if stake_sel == home.lower():
                selection_for_site = home
            elif stake_sel == away.lower():
                selection_for_site = away
            elif "draw" in stake_sel:
                selection_for_site = "Draw"
            else:
                selection_for_site = bet["selection"]

            mapped_selections.append({
                "teams": [home, away],
                "market": bet["market"],
                "selection": selection_for_site,  # This matches exactly what is on the site!
                "event_id": mapped["event_id"]
            })
        
        print("-" * 50)

    print("DEBUG: mapped_selections =", mapped_selections)  # <-- ADD THIS LINE
    
    if not mapped_selections:
        print("⚠️ No valid selections were mapped, skipping code generation.")
        return

    print("🎟️ Generating multi-selection betslip code...\n")
    code = await generate_sportybet_code(mapped_selections)
    print(f"✅ Bet Code: {code}")
    print(f"📎 Copy and paste it into SportyBet to preview the multibet.")

if __name__ == "__main__":
    asyncio.run(run())
