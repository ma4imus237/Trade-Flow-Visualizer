"""Seed the commodities and hs_code_mappings tables from data/static/hs_mappings.json.

Run standalone:
    python -m data.scripts.seed_hs_mappings
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.config import settings  # noqa: E402
from app.models.commodity import Commodity, HSCodeMapping  # noqa: E402

logger = logging.getLogger(__name__)

STATIC_DIR = PROJECT_ROOT / "data" / "static"


async def seed_hs_mappings(session: AsyncSession) -> tuple[int, int]:
    """Load commodity and HS-code mapping data from JSON and upsert.

    Returns (commodities_upserted, mappings_upserted).
    """
    json_path = STATIC_DIR / "hs_mappings.json"
    with open(json_path, "r", encoding="utf-8") as fh:
        commodities_data: list[dict] = json.load(fh)

    commodities_count = 0
    mappings_count = 0

    for entry in commodities_data:
        code = entry["code"]
        result = await session.execute(select(Commodity).where(Commodity.code == code))
        commodity: Commodity | None = result.scalar_one_or_none()

        if commodity is not None:
            commodity.name = entry["name"]
            commodity.color = entry.get("color")
        else:
            commodity = Commodity(
                code=code,
                name=entry["name"],
                color=entry.get("color"),
            )
            session.add(commodity)
            await session.flush()  # ensure commodity.id is available
        commodities_count += 1

        # Upsert each HS code mapping for this commodity
        for hs_entry in entry.get("hs_codes", []):
            hs6 = hs_entry["hs6"]
            result = await session.execute(
                select(HSCodeMapping).where(
                    HSCodeMapping.commodity_id == commodity.id,
                    HSCodeMapping.hs6 == hs6,
                )
            )
            existing_mapping: HSCodeMapping | None = result.scalar_one_or_none()

            if existing_mapping is not None:
                existing_mapping.description = hs_entry.get("description")
            else:
                session.add(
                    HSCodeMapping(
                        commodity_id=commodity.id,
                        hs6=hs6,
                        description=hs_entry.get("description"),
                    )
                )
            mappings_count += 1

    await session.commit()
    return commodities_count, mappings_count


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    engine = create_async_engine(settings.database_url, echo=False)
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_factory() as session:
        c_count, m_count = await seed_hs_mappings(session)
        logger.info("Upserted %d commodities and %d HS-code mappings.", c_count, m_count)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
