import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_flows_returns_list(client: AsyncClient):
    resp = await client.get("/api/v1/flows")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_flows_filter_by_commodity(client: AsyncClient):
    resp = await client.get("/api/v1/flows", params={"commodity": "lithium"})
    assert resp.status_code == 200
    data = resp.json()
    assert all(f["commodity"] == "Lithium" for f in data)


@pytest.mark.asyncio
async def test_get_flows_filter_by_year(client: AsyncClient):
    resp = await client.get("/api/v1/flows", params={"year": 2022})
    assert resp.status_code == 200
    data = resp.json()
    assert all(f["year"] == 2022 for f in data)


@pytest.mark.asyncio
async def test_get_flows_filter_by_reporter(client: AsyncClient):
    resp = await client.get("/api/v1/flows", params={"reporter": "AUS"})
    assert resp.status_code == 200
    data = resp.json()
    assert all(f["reporter_iso3"] == "AUS" for f in data)


@pytest.mark.asyncio
async def test_get_flows_min_value(client: AsyncClient):
    resp = await client.get("/api/v1/flows", params={"min_value": 4_000_000})
    assert resp.status_code == 200
    data = resp.json()
    assert all(f["value_usd"] >= 4_000_000 for f in data)


@pytest.mark.asyncio
async def test_get_flows_limit(client: AsyncClient):
    resp = await client.get("/api/v1/flows", params={"limit": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) <= 2


@pytest.mark.asyncio
async def test_get_flows_ordered_by_value_desc(client: AsyncClient):
    resp = await client.get("/api/v1/flows")
    assert resp.status_code == 200
    data = resp.json()
    values = [f["value_usd"] for f in data]
    assert values == sorted(values, reverse=True)


@pytest.mark.asyncio
async def test_get_top_flows(client: AsyncClient):
    resp = await client.get(
        "/api/v1/flows/top", params={"commodity": "lithium", "year": 2022, "limit": 10}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(f["year"] == 2022 for f in data)


@pytest.mark.asyncio
async def test_get_top_flows_requires_params(client: AsyncClient):
    resp = await client.get("/api/v1/flows/top")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_sankey(client: AsyncClient):
    resp = await client.get(
        "/api/v1/flows/sankey",
        params={"commodity": "lithium", "year": 2022, "flow_type": "export"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "links" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["links"], list)


@pytest.mark.asyncio
async def test_get_sankey_nodes_have_id_and_name(client: AsyncClient):
    resp = await client.get(
        "/api/v1/flows/sankey",
        params={"commodity": "lithium", "year": 2022, "flow_type": "export"},
    )
    data = resp.json()
    for node in data["nodes"]:
        assert "id" in node
        assert "name" in node


@pytest.mark.asyncio
async def test_get_sankey_links_have_source_target_value(client: AsyncClient):
    resp = await client.get(
        "/api/v1/flows/sankey",
        params={"commodity": "lithium", "year": 2022, "flow_type": "export"},
    )
    data = resp.json()
    for link in data["links"]:
        assert "source" in link
        assert "target" in link
        assert "value" in link


@pytest.mark.asyncio
async def test_get_timeseries(client: AsyncClient):
    resp = await client.get(
        "/api/v1/flows/timeseries",
        params={"reporter": "AUS", "partner": "CHN", "commodity": "lithium"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    years = [p["year"] for p in data]
    assert years == sorted(years)


@pytest.mark.asyncio
async def test_get_timeseries_requires_params(client: AsyncClient):
    resp = await client.get("/api/v1/flows/timeseries")
    assert resp.status_code == 422
