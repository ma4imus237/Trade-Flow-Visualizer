import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.flow import FlowFilters
from app.services.flow_service import FlowService


@pytest.mark.asyncio
async def test_get_flows_unfiltered(seeded_session: AsyncSession):
    service = FlowService(seeded_session)
    flows = await service.get_flows(FlowFilters())
    assert len(flows) > 0


@pytest.mark.asyncio
async def test_get_flows_filter_commodity(seeded_session: AsyncSession):
    service = FlowService(seeded_session)
    flows = await service.get_flows(FlowFilters(commodity="lithium"))
    assert all(f.commodity == "Lithium" for f in flows)


@pytest.mark.asyncio
async def test_get_flows_filter_year(seeded_session: AsyncSession):
    service = FlowService(seeded_session)
    flows = await service.get_flows(FlowFilters(year=2020))
    assert all(f.year == 2020 for f in flows)


@pytest.mark.asyncio
async def test_get_flows_filter_reporter(seeded_session: AsyncSession):
    service = FlowService(seeded_session)
    flows = await service.get_flows(FlowFilters(reporter="AUS"))
    assert all(f.reporter_iso3 == "AUS" for f in flows)


@pytest.mark.asyncio
async def test_get_flows_ordered_desc(seeded_session: AsyncSession):
    service = FlowService(seeded_session)
    flows = await service.get_flows(FlowFilters())
    values = [f.value_usd for f in flows]
    assert values == sorted(values, reverse=True)


@pytest.mark.asyncio
async def test_get_flows_limit(seeded_session: AsyncSession):
    service = FlowService(seeded_session)
    flows = await service.get_flows(FlowFilters(limit=2))
    assert len(flows) <= 2


@pytest.mark.asyncio
async def test_get_flows_min_value(seeded_session: AsyncSession):
    service = FlowService(seeded_session)
    flows = await service.get_flows(FlowFilters(min_value=5_000_000))
    assert all(f.value_usd >= 5_000_000 for f in flows)


@pytest.mark.asyncio
async def test_get_top_flows(seeded_session: AsyncSession):
    service = FlowService(seeded_session)
    flows = await service.get_top_flows("lithium", 2020, limit=10)
    assert len(flows) > 0
    assert all(f.year == 2020 for f in flows)


@pytest.mark.asyncio
async def test_get_sankey_structure(seeded_session: AsyncSession):
    service = FlowService(seeded_session)
    sankey = await service.get_sankey("lithium", 2020, "export", limit=10)
    assert len(sankey.nodes) > 0
    assert len(sankey.links) > 0
    node_ids = {n.id for n in sankey.nodes}
    for link in sankey.links:
        assert link.source in node_ids
        assert link.target in node_ids


@pytest.mark.asyncio
async def test_get_timeseries(seeded_session: AsyncSession):
    service = FlowService(seeded_session)
    ts = await service.get_timeseries("AUS", "CHN", "lithium")
    assert len(ts) == 2
    years = [p.year for p in ts]
    assert years == sorted(years)


@pytest.mark.asyncio
async def test_get_timeseries_empty(seeded_session: AsyncSession):
    service = FlowService(seeded_session)
    ts = await service.get_timeseries("BRA", "USA", "lithium")
    assert len(ts) == 0
