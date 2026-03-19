import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_shifts(client: AsyncClient):
    resp = await client.get(
        "/api/v1/shifts",
        params={
            "commodity": "lithium",
            "year_from": 2022,
            "year_to": 2023,
            "min_value": 1_000_000,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_shifts_classification(client: AsyncClient):
    # AUS->CHN: 5M in 2022, 15M in 2023 => 200% increase => surge
    resp = await client.get(
        "/api/v1/shifts",
        params={
            "commodity": "lithium",
            "year_from": 2022,
            "year_to": 2023,
            "min_value": 1_000_000,
        },
    )
    data = resp.json()
    valid_types = {"surge", "collapse", "new", "abandoned"}
    for shift in data:
        assert shift["shift_type"] in valid_types
        assert shift["commodity"] == "lithium"
        assert shift["year_from"] == 2022
        assert shift["year_to"] == 2023


@pytest.mark.asyncio
async def test_get_shifts_requires_params(client: AsyncClient):
    resp = await client.get("/api/v1/shifts")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_shifts_summary(client: AsyncClient):
    resp = await client.get(
        "/api/v1/shifts/summary",
        params={"commodity": "lithium", "year_from": 2022, "year_to": 2023},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["commodity"] == "lithium"
    assert "total_shifts" in data
    assert "surges" in data
    assert "collapses" in data
    assert "new_flows" in data
    assert "abandoned_flows" in data
    assert "top_shifts" in data
    assert isinstance(data["top_shifts"], list)


@pytest.mark.asyncio
async def test_get_shifts_summary_counts_consistent(client: AsyncClient):
    resp = await client.get(
        "/api/v1/shifts/summary",
        params={"commodity": "lithium", "year_from": 2022, "year_to": 2023},
    )
    data = resp.json()
    total = data["surges"] + data["collapses"] + data["new_flows"] + data["abandoned_flows"]
    assert total == data["total_shifts"]


@pytest.mark.asyncio
async def test_get_shifts_summary_requires_params(client: AsyncClient):
    resp = await client.get("/api/v1/shifts/summary")
    assert resp.status_code == 422
