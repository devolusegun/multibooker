import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("🌐 Navigating to SportyBet football page...")
        await page.goto("https://www.sportybet.com/ng/m/sport/football?time=all&source=sport_menu&sort=0", timeout=60000)

        await page.wait_for_timeout(5000)  # Let scripts load & cookies set

        print("📡 Fetching fixture data from within browser context...")

        response_data = await page.evaluate("""async () => {
            const res = await fetch("https://www.sportybet.com/api/ng/factsCenter/Outcomes", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "clientid": "wap",
                    "platform": "wap"
                },
                body: JSON.stringify({})
            });
            return await res.json();
        }""")

        if "data" in response_data:
            print(f"✅ Captured {len(response_data['data'])} fixtures!")
            for fix in response_data["data"][:5]:
                print(f"📌 {fix['homeTeamName']} vs {fix['awayTeamName']} — Event ID: {fix['eventId']}")
        else:
            print("❌ Unexpected structure:", response_data)

        await browser.close()

asyncio.run(run())
