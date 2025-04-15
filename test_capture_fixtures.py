import asyncio
from playwright.async_api import async_playwright

async def run():
    print("🌐 Navigating to SportyBet football page...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        all_urls = []

        page.on("requestfinished", lambda req: all_urls.append(req.url))

        await page.goto("https://www.sportybet.com/ng/m/sport/football?time=all&source=sport_menu&sort=0")

        print("🕵️ Interacting with the page to trigger all network calls...")
        await page.mouse.wheel(0, 10000)  # scroll to bottom
        await asyncio.sleep(30)

        await browser.close()

        fixture_like = [url for url in all_urls if "factsCenter" in url or "fixture" in url or "Outcomes" in url]

        print(f"\n📦 Captured {len(all_urls)} requests total.")
        if fixture_like:
            print("🔍 Potential fixture endpoints:")
            for url in fixture_like:
                print("👉", url)
        else:
            print("❌ Still no obvious fixture API found in traffic.")

asyncio.run(run())
