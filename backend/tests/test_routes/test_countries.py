import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_country_profile(client: AsyncClient):
    resp = await client.get(
        "/api/v1/countries/AUS/profile", params={"year": 2022, "commodity": "lithium"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["iso3"] == "AUS"
    assert data["name"] == "Australia"
    assert "total_exports" in data
    assert "total_imports" in data
    assert "top_export_partners" in data
    assert "top_import_partners" in data
    assert "top_commodities" in data


@pytest.mark.asyncio
async def test_get_country_profile_totals(client: AsyncClient):
    resp = await client.get(
        "/api/v1/countries/AUS/profile", params={"year": 2022, "commodity": "lithium"}
    )
    data = resp.json()
    # AUS exports lithium to CHN (5M) and USA (3M) in 2022
    assert data["total_exports"] == 8_000_000
    assert data["total_imports"] == 0


@pytest.mark.asyncio
async def test_get_country_profile_without_filters(client: AsyncClient):
    resp = await client.get("/api/v1/countries/AUS/profile")
    assert resp.status_code == 200
    data = resp.json()
    assert data["iso3"] == "AUS"
    assert data["total_exports"] > 0


@pytest.mark.asyncio
async def test_get_country_profile_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/countries/ZZZ/profile")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_country_partners(client: AsyncClient):
    resp = await client.get(
        "/api/v1/countries/AUS/partners",
        params={"year": 2022, "flow_type": "export"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # All partners should have the correct flow_type
    assert all(p["flow_type"] == "export" for p in data)


@pytest.mark.asyncio
async def test_get_country_partners_sorted_by_value(client: AsyncClient):
    resp = await client.get(
        "/api/v1/countries/AUS/partners",
        params={"year": 2022, "flow_type": "export"},
    )
    data = resp.json()
    values = [p["value_usd"] for p in data]
    assert values == sorted(values, reverse=True)


@pytest.mark.asyncio
async def test_get_country_partners_requires_year(client: AsyncClient):
    resp = await client.get("/api/v1/countries/AUS/partners")
    assert resp.status_code == 422
