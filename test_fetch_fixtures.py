import httpx
import asyncio

SPORTYBET_FIXTURE_URL = "https://www.sportybet.com/api/ng/factsCenter/Outcomes"

async def fetch_sportybet_fixtures():
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Origin": "https://www.sportybet.com",
        "Referer": "https://www.sportybet.com/ng/m/sport/football?time=all&source=sport_menu&sort=0",
        "Platform": "wap",
        "ClientId": "wap",
        "OperId": "2",
    }

    payload = {
        "sportId": "sr:sport:1",  # Football
        "source": "sport_menu",
        "time": "all",
        "sort": 0
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(SPORTYBET_FIXTURE_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

async def test_fetch_fixtures():
    try:
        data = await fetch_sportybet_fixtures()
        fixtures = data.get("data", [])
        for fixture in fixtures[:5]:  # preview first 5
            match = f"{fixture['homeTeamName']} vs {fixture['awayTeamName']}"
            event_id = fixture['eventId']
            markets = fixture.get('markets', [])
            for market in markets:
                market_id = market['id']
                for outcome in market.get("outcomes", []):
                    print({
                        "match": match,
                        "event_id": event_id,
                        "market_id": market_id,
                        "outcome_id": outcome["id"],
                        "selection": outcome["desc"],
                        "odds": outcome["odds"]
                    })
    except Exception as e:
        print("❌ Failed to fetch or parse fixtures:", e)

asyncio.run(test_fetch_fixtures())
