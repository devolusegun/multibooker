# app/scripts/refresh_fixtures.py

import asyncio
import subprocess

async def run_all_steps():
    print("🔁 Step 1: Fetching raw fixtures from SportyBet...")
    result = subprocess.run(
        ["python", "-m", "app.scripts.fetch_sportybet_fixtures"],
        capture_output=True, text=True
    )
    print(result.stdout)

    print("🔁 Step 2: Extracting and cleaning raw fixtures...")
    result = subprocess.run(
        ["python", "-m", "app.scripts.extract_clean_fixtures"],
        capture_output=True, text=True
    )
    print(result.stdout)

    print("🔁 Step 3: Normalizing cleaned fixtures...")
    result = subprocess.run(
        ["python", "-m", "app.scripts.normalize_clean_fixtures"],
        capture_output=True, text=True
    )
    print(result.stdout)

    print("✅ Fixture refresh complete.")

if __name__ == "__main__":
    asyncio.run(run_all_steps())
