import asyncio
from app.services.generators.sportybet_gen import generate_sportybet_code

async def main():
    code = await generate_sportybet_code([])  # We pass [] since selections are not wired yet
    print("✅ Booking Code Found:", code)

asyncio.run(main())
