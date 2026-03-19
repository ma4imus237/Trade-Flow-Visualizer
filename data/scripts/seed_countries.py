"""Seed the countries table from data/static/countries.json.

Run standalone:
    python -m data.scripts.seed_countries
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure the project root is on sys.path so we can import app modules.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.config import settings  # noqa: E402
from app.models.country import Country  # noqa: E402

logger = logging.getLogger(__name__)

STATIC_DIR = PROJECT_ROOT / "data" / "static"


async def seed_countries(session: AsyncSession) -> int:
    """Load countries from JSON and upsert into the database.

    Returns the number of rows upserted.
    """
    json_path = STATIC_DIR / "countries.json"
    with open(json_path, "r", encoding="utf-8") as fh:
        countries_data: list[dict] = json.load(fh)

    upserted = 0
    for entry in countries_data:
        iso3 = entry["iso3"]
        result = await session.execute(select(Country).where(Country.iso3 == iso3))
        existing: Country | None = result.scalar_one_or_none()

        if existing is not None:
            existing.name = entry["name"]
            existing.region = entry.get("region")
            existing.latitude = entry.get("latitude")
            existing.longitude = entry.get("longitude")
        else:
            session.add(
                Country(
                    iso3=iso3,
                    name=entry["name"],
                    region=entry.get("region"),
                    latitude=entry.get("latitude"),
                    longitude=entry.get("longitude"),
                )
            )
        upserted += 1

    await session.commit()
    return upserted


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    engine = create_async_engine(settings.database_url, echo=False)
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_factory() as session:
        count = await seed_countries(session)
        logger.info("Upserted %d countries.", count)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
