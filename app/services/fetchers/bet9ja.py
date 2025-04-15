# app/services/fetchers/bet9ja.py

async def fetch_bet9ja_odds(event_id: str):
    """
    Simulated odds fetcher for Bet9ja — returns static data for now.
    Replace with real scraper later.
    """
    return {
        "event_id": event_id,
        "home_team": "Placeholder Home",
        "away_team": "Placeholder Away",
        "start_time": "2025-04-15T15:00:00Z",
        "odds": {
            "match_result": {
                "home": 2.1,
                "draw": 3.5,
                "away": 3.0
            },
            "over_under_2_5_goals": {
                "over_2_5": 1.85,
                "under_2_5": 2.00
            }
        }
    }
