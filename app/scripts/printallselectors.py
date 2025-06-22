import asyncio
from playwright.async_api import async_playwright

async def main():
    url = "https://www.sportybet.com/ng/m/sport/football/today?source=sport_menu&sort=0"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            device_scale_factor=2,
            has_touch=True,
        )
        page = await context.new_page()
        await page.goto(url, timeout=60000)
        await page.wait_for_load_state('networkidle')

        divs = await page.query_selector_all("div")
        print("\n=== All divs with class and text (first 60 chars) ===")
        for div in divs:
            cls = await div.get_attribute("class")
            txt = await div.inner_text()
            txt = txt.replace("\n", " ").strip()
            if cls and txt:
                print(f"CLASS: {cls}\nTEXT: {txt[:60]}\n----")

        await browser.close()

asyncio.run(main())