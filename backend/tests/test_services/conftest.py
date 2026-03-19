import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models.commodity import Commodity
from app.models.country import Country
from app.models.trade_flow import TradeFlow


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def svc_engine():
    return create_async_engine("sqlite+aiosqlite:///:memory:")


@pytest.fixture(scope="session")
def svc_session_factory(svc_engine):
    return async_sessionmaker(svc_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
async def svc_setup_and_seed(svc_engine, svc_session_factory):
    """Create tables and seed data once for the entire test session."""
    async with svc_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with svc_session_factory() as session:
        aus = Country(id=1, iso3="AUS", name="Australia", region="Oceania", latitude=-25.0, longitude=133.0)
        chn = Country(id=2, iso3="CHN", name="China", region="Asia", latitude=35.0, longitude=105.0)
        usa = Country(id=3, iso3="USA", name="United States", region="Americas", latitude=38.0, longitude=-97.0)
        bra = Country(id=4, iso3="BRA", name="Brazil", region="Americas", latitude=-14.0, longitude=-51.0)

        lithium = Commodity(id=1, code="lithium", name="Lithium", color="#4CAF50")

        session.add_all([aus, chn, usa, bra, lithium])
        await session.flush()

        flows = [
            TradeFlow(
                reporter_id=1, partner_id=2, commodity_id=1, year=2020,
                flow_type="export", value_usd=5_000_000, weight_kg=100_000,
            ),
            TradeFlow(
                reporter_id=1, partner_id=2, commodity_id=1, year=2023,
                flow_type="export", value_usd=15_000_000, weight_kg=300_000,
            ),
            TradeFlow(
                reporter_id=1, partner_id=3, commodity_id=1, year=2020,
                flow_type="export", value_usd=3_000_000, weight_kg=60_000,
            ),
            TradeFlow(
                reporter_id=1, partner_id=3, commodity_id=1, year=2023,
                flow_type="export", value_usd=1_000_000, weight_kg=20_000,
            ),
            # New flow: BRA->CHN did not exist in 2020
            TradeFlow(
                reporter_id=4, partner_id=2, commodity_id=1, year=2023,
                flow_type="export", value_usd=8_000_000, weight_kg=160_000,
            ),
            # Abandoned flow: CHN->USA existed in 2020 but not 2023
            TradeFlow(
                reporter_id=2, partner_id=3, commodity_id=1, year=2020,
                flow_type="export", value_usd=2_000_000, weight_kg=40_000,
            ),
        ]
        session.add_all(flows)
        await session.commit()

    yield

    async with svc_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def seeded_session(svc_session_factory, svc_setup_and_seed):
    async with svc_session_factory() as session:
        yield session
