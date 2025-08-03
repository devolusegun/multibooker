from datetime import datetime
import json
from app.services.mapper import map_to_bookie
from app.services.generators.sportybet_gen import generate_sportybet_code
import asyncio

sample_bets = [
    {
        "match": "Philadelphia Union vs Eintracht Frankfurt",
        "teams": ["Philadelphia Union", "Eintracht Frankfurt"],
        "market": "Match Result",
        "selection": "Eintracht Frankfurt",
        "odd": 1.93,
        "kickoff": int(datetime(2025, 8, 2, 22, 30).timestamp() * 1000),
    },
    {
        "match": "Orlando City SC vs Atlas FC",
        "teams": ["Orlando City SC", "Atlas FC"],
        "market": "Match Result",
        "selection": "Orlando City SC",
        "odd": 1.40,
        "kickoff": int(datetime(2025, 8, 2, 23, 0).timestamp() * 1000),
    },
    {
        "match": "Charlotte Independence vs Texoma FC",
        "teams": ["Charlotte Independence", "Texoma FC"],
        "market": "Match Result",
        "selection": "Charlotte Independence",
        "odd": 1.41,
        "kickoff": int(datetime(2025, 8, 3, 0, 0).timestamp() * 1000),
    },
    {
        "match": "Inter Miami CF vs Necaxa",
        "teams": ["Inter Miami CF", "Necaxa"],
        "market": "Match Result",
        "selection": "Inter Miami CF",
        "odd": 1.51,
        "kickoff": int(datetime(2025, 8, 3, 0, 0).timestamp() * 1000),
    },
    {
        "match": "Coastal Spirit FC vs Nomads United AFC",
        "teams": ["Coastal Spirit FC", "Nomads United AFC"],
        "market": "Match Result",
        "selection": "Coastal Spirit FC",
        "odd": 1.34,
        "kickoff": int(datetime(2025, 8, 3, 1, 0).timestamp() * 1000),
    },
    {
        "match": "San Martin de Tucuman vs CA River Plate (ARG)",
        "teams": ["San Martin de Tucuman", "CA River Plate (ARG)"],
        "market": "Match Result",
        "selection": "CA River Plate (ARG)",
        "odd": 1.45,
        "kickoff": int(datetime(2025, 8, 3, 1, 10).timestamp() * 1000),
    },
    {
        "match": "CF America vs Minnesota United FC",
        "teams": ["CF America", "Minnesota United FC"],
        "market": "Match Result",
        "selection": "CF America",
        "odd": 1.73,
        "kickoff": int(datetime(2025, 8, 3, 2, 0).timestamp() * 1000),
    },
    {
        "match": "Real Salt Lake vs Atletico San Luis",
        "teams": ["Real Salt Lake", "Atletico San Luis"],
        "market": "Match Result",
        "selection": "Real Salt Lake",
        "odd": 1.66,
        "kickoff": int(datetime(2025, 8, 3, 2, 30).timestamp() * 1000),
    },
    {
        "match": "Napier City Rovers AFC vs Waterside Karori",
        "teams": ["Napier City Rovers AFC", "Waterside Karori"],
        "market": "Match Result",
        "selection": "Napier City Rovers AFC",
        "odd": 1.11,
        "kickoff": int(datetime(2025, 8, 3, 3, 0).timestamp() * 1000),
    },
    {
        "match": "Portland Timbers vs Queretaro FC",
        "teams": ["Portland Timbers", "Queretaro FC"],
        "market": "Match Result",
        "selection": "Portland Timbers",
        "odd": 1.54,
        "kickoff": int(datetime(2025, 8, 3, 4, 0).timestamp() * 1000),
    },
    {
        "match": "Dalian Young Boy FC Srl vs Qingdao Hainiu FC Srl",
        "teams": ["Dalian Young Boy FC Srl", "Qingdao Hainiu FC Srl"],
        "market": "Match Result",
        "selection": "Dalian Young Boy FC Srl",
        "odd": 1.66,
        "kickoff": int(datetime(2025, 8, 3, 6, 0).timestamp() * 1000),
    },
    {
        "match": "UD Ibiza vs AL Riyadh",
        "teams": ["UD Ibiza", "AL Riyadh"],
        "market": "Match Result",
        "selection": "AL Riyadh",
        "odd": 2.32,
        "kickoff": int(datetime(2025, 8, 3, 9, 0).timestamp() * 1000),
    },
    {
        "match": "Namdhari Sports Academy vs Indian Air Force",
        "teams": ["Namdhari Sports Academy", "Indian Air Force"],
        "market": "Match Result",
        "selection": "Namdhari Sports Academy",
        "odd": 1.42,
        "kickoff": int(datetime(2025, 8, 3, 11, 30).timestamp() * 1000),
    },
    {
        "match": "Djurgardens IF vs Halmstads BK",
        "teams": ["Djurgardens IF", "Halmstads BK"],
        "market": "Match Result",
        "selection": "Djurgardens IF",
        "odd": 1.26,
        "kickoff": int(datetime(2025, 8, 3, 13, 0).timestamp() * 1000),
    },
    {
        "match": "Ajax Amsterdam vs AS Monaco FC",
        "teams": ["Ajax Amsterdam", "AS Monaco FC"],
        "market": "Match Result",
        "selection": "Ajax Amsterdam",
        "odd": 2.46,
        "kickoff": int(datetime(2025, 8, 3, 13, 0).timestamp() * 1000),
    },
    {
        "match": "Hamarkameratene vs Bodo/Glimt",
        "teams": ["Hamarkameratene", "Bodo/Glimt"],
        "market": "Match Result",
        "selection": "Bodo/Glimt",
        "odd": 1.36,
        "kickoff": int(datetime(2025, 8, 3, 13, 30).timestamp() * 1000),
    },
    {
        "match": "ADO Den Haag vs Olympiacos Piraeus",
        "teams": ["ADO Den Haag", "Olympiacos Piraeus"],
        "market": "Match Result",
        "selection": "Olympiacos Piraeus",
        "odd": 1.57,
        "kickoff": int(datetime(2025, 8, 3, 14, 0).timestamp() * 1000),
    },
    {
        "match": "AZ Alkmaar vs OFI Crete",
        "teams": ["AZ Alkmaar", "OFI Crete"],
        "market": "Match Result",
        "selection": "AZ Alkmaar",
        "odd": 1.66,
        "kickoff": int(datetime(2025, 8, 3, 14, 0).timestamp() * 1000),
    },
    {
        "match": "Assyriska FF vs Team TG FF",
        "teams": ["Assyriska FF", "Team TG FF"],
        "market": "Match Result",
        "selection": "Assyriska FF",
        "odd": 1.40,
        "kickoff": int(datetime(2025, 8, 3, 14, 0).timestamp() * 1000),
    },
    {
        "match": "Molde FK vs Bryne FK",
        "teams": ["Molde FK", "Bryne FK"],
        "market": "Match Result",
        "selection": "Molde FK",
        "odd": 1.50,
        "kickoff": int(datetime(2025, 8, 3, 16, 0).timestamp() * 1000),
    },
    {
        "match": "Morocco vs Angola",
        "teams": ["Morocco", "Angola"],
        "market": "Match Result",
        "selection": "Morocco",
        "odd": 1.73,
        "kickoff": int(datetime(2025, 8, 3, 16, 0).timestamp() * 1000),
    },
    {
        "match": "Mamelodi Sundowns vs Richards Bay FC",
        "teams": ["Mamelodi Sundowns", "Richards Bay FC"],
        "market": "Match Result",
        "selection": "Mamelodi Sundowns",
        "odd": 1.28,
        "kickoff": int(datetime(2025, 8, 3, 17, 0).timestamp() * 1000),
    },
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
