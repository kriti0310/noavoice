# Run this once in a standalone script
# app/scripts/run_seed.py

import asyncio
from app.config.database import AsyncSessionLocal
from app.config.seed_template import seed_default_template

async def main():
    async with AsyncSessionLocal() as db:
        await seed_default_template(db)

asyncio.run(main())