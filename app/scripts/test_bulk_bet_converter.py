from datetime import datetime
import json
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code
import asyncio

sample_bets = [
    {
        "match": "Deportivo Toluca FC vs Montreal Impact",
        "teams": ["Deportivo Toluca FC", "Montreal Impact"],
        "market": "Match Result",
        "selection": "Deportivo Toluca FC",
        "odd": 1.54,
        "kickoff": int(datetime(2025, 8, 2, 2, 0).timestamp() * 1000),
    },
    {
        "match": "Colorado Springs Switchbacks FC vs Lexington SC",
        "teams": ["Colorado Springs Switchbacks FC", "Lexington SC"],
        "market": "Match Result",
        "selection": "Colorado Springs Switchbacks FC",
        "odd": 1.77,
        "kickoff": int(datetime(2025, 8, 2, 2, 0).timestamp() * 1000),
    }
]

# ADD THIS BLOCK RIGHT HERE:
for bet in sample_bets:
    if "match" not in bet and "teams" in bet:
        bet["match"] = " vs ".join(bet["teams"])

BOOKIE = "sportybet"

async def run():
    print(f"🎯 Converting OCR-style bets to multibet code for {BOOKIE}...\n")
    mapped_selections = []

    for idx, bet in enumerate(sample_bets, 1):
        print(f"📌 Bet #{idx}: {' vs '.join(bet['teams'])} | {bet['market']} | {bet['selection']} @ {bet['odd']}")
        mapped = map_to_bookie(bet, BOOKIE)

        if "error" in mapped:
            print(f"❌ Error: {mapped['error']}")
        else:
            print("✅ Mapped:", json.dumps(mapped, indent=2))

            # This uses the mapped fixture teams, not OCR values
            home, away = mapped["match"].split(" vs ")
            stake_sel = bet["selection"].strip().lower()

            if stake_sel == home.lower():
                selection_for_site = "Home"
            elif stake_sel == away.lower():
                selection_for_site = "Away"
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
