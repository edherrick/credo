"""Seed politician entities into the database.

Usage (from backend/ directory):
    python scripts/seed_politicians.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

POLITICIANS = [
    {
        "name": "Brandon Johnson",
        "slug": "brandon-johnson",
        "type": "politician",
        "wikidata_id": "Q73917865",
        "description": (
            "57th Mayor of Chicago (2023–). Former educator and Chicago Teachers Union organizer. "
            "Progressive Democrat representing Chicago's West Side."
        ),
    },
]


async def main() -> None:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        for p in POLITICIANS:
            await session.execute(
                text("""
                    INSERT INTO entities (name, slug, type, wikidata_id, description)
                    VALUES (:name, :slug, :type, :wikidata_id, :description)
                    ON CONFLICT (slug) DO UPDATE SET
                        name        = EXCLUDED.name,
                        wikidata_id = EXCLUDED.wikidata_id,
                        description = EXCLUDED.description
                """),
                p,
            )
        await session.commit()

    print(f"Seeded {len(POLITICIANS)} politician(s).")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
