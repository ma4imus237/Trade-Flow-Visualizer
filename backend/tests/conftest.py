"""Shared test fixtures.

Provides an in-memory SQLite async database with pre-populated reference data
so that tests can run without a live PostgreSQL instance.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models.commodity import Commodity, HSCodeMapping
from app.models.country import Country
from app.models.trade_flow import TradeFlow

# Use aiosqlite for fast, in-process async testing.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

SAMPLE_COUNTRIES = [
    {"iso3": "USA", "name": "United States", "region": "Americas", "latitude": 37.09, "longitude": -95.71},
    {"iso3": "CHN", "name": "China", "region": "East Asia", "latitude": 35.86, "longitude": 104.20},
    {"iso3": "AUS", "name": "Australia", "region": "Oceania", "latitude": -25.27, "longitude": 133.78},
    {"iso3": "CHL", "name": "Chile", "region": "Americas", "latitude": -35.68, "longitude": -71.54},
    {"iso3": "COD", "name": "DR Congo", "region": "Africa", "latitude": -4.04, "longitude": 21.76},
    {"iso3": "JPN", "name": "Japan", "region": "East Asia", "latitude": 36.20, "longitude": 138.25},
    {"iso3": "KOR", "name": "South Korea", "region": "East Asia", "latitude": 35.91, "longitude": 127.77},
    {"iso3": "DEU", "name": "Germany", "region": "Europe", "latitude": 51.17, "longitude": 10.45},
    {"iso3": "CAN", "name": "Canada", "region": "Americas", "latitude": 56.13, "longitude": -106.35},
    {"iso3": "BRA", "name": "Brazil", "region": "Americas", "latitude": -14.24, "longitude": -51.93},
]

SAMPLE_COMMODITIES = [
    {"code": "lithium", "name": "Lithium", "color": "#06b6d4"},
    {"code": "copper", "name": "Copper", "color": "#ef4444"},
]

SAMPLE_HS_CODES = [
    {"commodity_code": "lithium", "hs6": "283691", "description": "Lithium carbonate"},
    {"commodity_code": "lithium", "hs6": "282520", "description": "Lithium oxide and hydroxide"},
    {"commodity_code": "copper", "hs6": "260300", "description": "Copper ores and concentrates"},
    {"commodity_code": "copper", "hs6": "740311", "description": "Refined copper cathodes"},
]


def _set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key support in SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    event.listen(engine.sync_engine, "connect", _set_sqlite_pragma)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine):
    session_factory = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def seeded_session(async_engine):
    """Session pre-loaded with sample countries, commodities, HS codes, and flows."""
    session_factory = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        # Countries
        country_objs: dict[str, Country] = {}
        for c in SAMPLE_COUNTRIES:
            obj = Country(**c)
            session.add(obj)
            country_objs[c["iso3"]] = obj
        await session.flush()

        # Commodities
        commodity_objs: dict[str, Commodity] = {}
        for cm in SAMPLE_COMMODITIES:
            obj = Commodity(**cm)
            session.add(obj)
            commodity_objs[cm["code"]] = obj
        await session.flush()

        # HS-code mappings
        for hs in SAMPLE_HS_CODES:
            session.add(
                HSCodeMapping(
                    commodity_id=commodity_objs[hs["commodity_code"]].id,
                    hs6=hs["hs6"],
                    description=hs["description"],
                )
            )
        await session.flush()

        # Sample trade flows for lithium and copper, years 2022 and 2023
        flows = [
            # Lithium: AUS exports to CHN, CHN imports from AUS
            {"reporter": "AUS", "partner": "CHN", "commodity": "lithium", "year": 2022, "flow_type": "export", "value_usd": 5_000_000_000, "weight_kg": 200_000_000},
            {"reporter": "CHN", "partner": "AUS", "commodity": "lithium", "year": 2022, "flow_type": "import", "value_usd": 4_800_000_000, "weight_kg": 195_000_000},
            # Lithium: CHL exports to USA
            {"reporter": "CHL", "partner": "USA", "commodity": "lithium", "year": 2022, "flow_type": "export", "value_usd": 3_000_000_000, "weight_kg": 150_000_000},
            {"reporter": "USA", "partner": "CHL", "commodity": "lithium", "year": 2022, "flow_type": "import", "value_usd": 3_200_000_000, "weight_kg": 155_000_000},
            # Lithium 2023
            {"reporter": "AUS", "partner": "CHN", "commodity": "lithium", "year": 2023, "flow_type": "export", "value_usd": 4_200_000_000, "weight_kg": 210_000_000},
            {"reporter": "CHN", "partner": "AUS", "commodity": "lithium", "year": 2023, "flow_type": "import", "value_usd": 4_100_000_000, "weight_kg": 205_000_000},
            # Copper: CHL exports to CHN
            {"reporter": "CHL", "partner": "CHN", "commodity": "copper", "year": 2022, "flow_type": "export", "value_usd": 12_000_000_000, "weight_kg": 1_000_000_000},
            {"reporter": "CHN", "partner": "CHL", "commodity": "copper", "year": 2022, "flow_type": "import", "value_usd": 11_500_000_000, "weight_kg": 980_000_000},
            # Copper: COD exports to CHN (large discrepancy for reconciliation testing)
            {"reporter": "COD", "partner": "CHN", "commodity": "copper", "year": 2022, "flow_type": "export", "value_usd": 2_000_000_000, "weight_kg": 100_000_000},
            {"reporter": "CHN", "partner": "COD", "commodity": "copper", "year": 2022, "flow_type": "import", "value_usd": 5_000_000_000, "weight_kg": 250_000_000},
            # Copper 2023
            {"reporter": "CHL", "partner": "CHN", "commodity": "copper", "year": 2023, "flow_type": "export", "value_usd": 13_000_000_000, "weight_kg": 1_050_000_000},
            {"reporter": "CHN", "partner": "CHL", "commodity": "copper", "year": 2023, "flow_type": "import", "value_usd": 12_800_000_000, "weight_kg": 1_040_000_000},
        ]

        for f in flows:
            session.add(
                TradeFlow(
                    reporter_id=country_objs[f["reporter"]].id,
                    partner_id=country_objs[f["partner"]].id,
                    commodity_id=commodity_objs[f["commodity"]].id,
                    year=f["year"],
                    flow_type=f["flow_type"],
                    value_usd=f["value_usd"],
                    weight_kg=f["weight_kg"],
                )
            )

        await session.commit()
        yield session
