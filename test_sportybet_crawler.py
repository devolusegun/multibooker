import asyncio
from app.services.fetchers.sportybet_crawler import crawl_sportybet_fixtures

async def run():
    print("🔍 Crawling SportyBet for fixture links...")
    links = await crawl_sportybet_fixtures()
    if not links:
        print("❌ No fixture links found.")
    else:
        print(f"✅ Found {len(links)} fixture links:")
        for link in links[:10]:
            print("🔗", link)

if __name__ == "__main__":
    asyncio.run(run())
