import asyncio
import sqlalchemy as sa
from app.core.database import async_engine

async def main():
    async with async_engine.begin() as conn:
        await conn.execute(sa.text("ALTER TABLE chat_narrative_states ALTER COLUMN location TYPE TEXT;"))
        await conn.execute(sa.text("ALTER TABLE chat_narrative_states ALTER COLUMN date_text TYPE TEXT;"))
        await conn.execute(sa.text("ALTER TABLE chat_narrative_states ALTER COLUMN time_text TYPE TEXT;"))
        print("MIGRATION_SUCCESS")

if __name__ == "__main__":
    asyncio.run(main())
