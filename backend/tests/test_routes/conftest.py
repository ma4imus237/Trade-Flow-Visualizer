import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models.commodity import Commodity
from app.models.country import Country
from app.models.trade_flow import TradeFlow


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def test_engine():
    return create_async_engine("sqlite+aiosqlite:///:memory:")


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
async def setup_and_seed(test_engine, test_session_factory):
    """Create tables and seed data once for the entire test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_factory() as session:
        aus = Country(id=1, iso3="AUS", name="Australia", region="Oceania", latitude=-25.0, longitude=133.0)
        chn = Country(id=2, iso3="CHN", name="China", region="Asia", latitude=35.0, longitude=105.0)
        usa = Country(id=3, iso3="USA", name="United States", region="Americas", latitude=38.0, longitude=-97.0)

        lithium = Commodity(id=1, code="lithium", name="Lithium", color="#4CAF50")
        cobalt = Commodity(id=2, code="cobalt", name="Cobalt", color="#2196F3")

        session.add_all([aus, chn, usa, lithium, cobalt])
        await session.flush()

        flows = [
            TradeFlow(
                reporter_id=1, partner_id=2, commodity_id=1, year=2022,
                flow_type="export", value_usd=5_000_000, weight_kg=100_000,
            ),
            TradeFlow(
                reporter_id=1, partner_id=3, commodity_id=1, year=2022,
                flow_type="export", value_usd=3_000_000, weight_kg=60_000,
            ),
            TradeFlow(
                reporter_id=2, partner_id=3, commodity_id=1, year=2022,
                flow_type="export", value_usd=2_000_000, weight_kg=40_000,
            ),
            TradeFlow(
                reporter_id=1, partner_id=2, commodity_id=1, year=2023,
                flow_type="export", value_usd=15_000_000, weight_kg=300_000,
            ),
            TradeFlow(
                reporter_id=2, partner_id=1, commodity_id=1, year=2022,
                flow_type="import", value_usd=4_000_000, weight_kg=80_000,
            ),
        ]
        session.add_all(flows)
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_session_factory, setup_and_seed):
    async with test_session_factory() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession):
    """Create an httpx AsyncClient with the FastAPI app, overriding the DB dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
