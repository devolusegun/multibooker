import asyncio
from app.services.generators.sportybet_gen import generate_sportybet_code

async def run():
    print("🚀 Testing automatic SportyBet code generation...")
    code = await generate_sportybet_code()
    print("🏁 Booking Code:", code)

asyncio.run(run())
