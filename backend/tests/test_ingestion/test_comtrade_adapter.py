"""Tests for the Comtrade adapter."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.ingestion.comtrade_adapter import (
    ComtradeAdapter,
    _COMTRADE_TO_ISO3,
)


def _make_comtrade_response(rows: list[dict]) -> dict:
    """Build a minimal Comtrade-style JSON response."""
    return {"data": rows}


def _make_row(
    reporter_code: int = 36,  # AUS
    partner_code: int = 156,  # CHN
    flow_code: str = "X",
    primary_value: int = 1_000_000,
    net_wt: int | None = 50_000,
    period: int = 2022,
) -> dict:
    return {
        "reporterCode": reporter_code,
        "partnerCode": partner_code,
        "flowCode": flow_code,
        "primaryValue": primary_value,
        "netWt": net_wt,
        "period": period,
    }


class TestComtradeAdapterNormalisation:
    """Test the static normalisation of Comtrade rows."""

    def test_normalise_export_row(self):
        row = _make_row(flow_code="X", primary_value=5_000_000)
        result = ComtradeAdapter._normalise_row(row, "lithium")
        assert result is not None
        assert result["reporter_iso3"] == "AUS"
        assert result["partner_iso3"] == "CHN"
        assert result["flow_type"] == "export"
        assert result["value_usd"] == 5_000_000
        assert result["commodity_code"] == "lithium"

    def test_normalise_import_row(self):
        row = _make_row(flow_code="M")
        result = ComtradeAdapter._normalise_row(row, "copper")
        assert result is not None
        assert result["flow_type"] == "import"

    def test_filters_aggregate_partners(self):
        row = _make_row(partner_code=0)  # "World"
        result = ComtradeAdapter._normalise_row(row, "lithium")
        assert result is None

    def test_filters_unknown_reporter(self):
        row = _make_row(reporter_code=99999)
        result = ComtradeAdapter._normalise_row(row, "lithium")
        assert result is None

    def test_filters_zero_value(self):
        row = _make_row(primary_value=0)
        result = ComtradeAdapter._normalise_row(row, "lithium")
        assert result is None

    def test_filters_negative_value(self):
        row = _make_row(primary_value=-100)
        result = ComtradeAdapter._normalise_row(row, "lithium")
        assert result is None

    def test_handles_null_weight(self):
        row = _make_row(net_wt=None)
        result = ComtradeAdapter._normalise_row(row, "lithium")
        assert result is not None
        assert result["weight_kg"] is None

    def test_unknown_flow_code_filtered(self):
        row = _make_row(flow_code="R")  # re-export
        result = ComtradeAdapter._normalise_row(row, "lithium")
        assert result is None


class TestComtradeAdapterISO3Mapping:
    """Verify key entries in the Comtrade-to-ISO3 mapping."""

    def test_major_trading_nations_present(self):
        expected = {842: "USA", 156: "CHN", 392: "JPN", 276: "DEU", 826: "GBR"}
        for code, iso3 in expected.items():
            assert _COMTRADE_TO_ISO3.get(code) == iso3


class TestComtradeAdapterFetchFlows:
    """Test the fetch_flows method with mocked HTTP."""

    @pytest.mark.asyncio
    async def test_fetch_flows_single_page(self):
        adapter = ComtradeAdapter(api_key="test-key")
        adapter._last_request_time = 0.0

        rows = [_make_row(), _make_row(partner_code=392)]  # AUS->CHN, AUS->JPN
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = _make_comtrade_response(rows)
        mock_response.raise_for_status = MagicMock()

        with patch("app.services.ingestion.comtrade_adapter.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            result = await adapter.fetch_flows("lithium", ["283691"], 2022)

        assert len(result) == 2
        assert result[0]["reporter_iso3"] == "AUS"

    @pytest.mark.asyncio
    async def test_fetch_flows_paginates(self):
        """When the first page returns PAGE_SIZE rows, a second request is made."""
        adapter = ComtradeAdapter(api_key="test-key")
        adapter._last_request_time = 0.0

        from app.services.ingestion.comtrade_adapter import PAGE_SIZE

        page1_rows = [_make_row() for _ in range(PAGE_SIZE)]
        page2_rows = [_make_row(partner_code=392)]

        call_count = 0

        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            if call_count == 1:
                mock_resp.json.return_value = _make_comtrade_response(page1_rows)
            else:
                mock_resp.json.return_value = _make_comtrade_response(page2_rows)
            return mock_resp

        with patch("app.services.ingestion.comtrade_adapter.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = mock_get
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            result = await adapter.fetch_flows("lithium", ["283691"], 2022)

        assert call_count == 2
        # PAGE_SIZE from page 1 + 1 from page 2 (but all from page 1 map to same pair, so normalised count matches)
        assert len(result) == PAGE_SIZE + 1

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Verify that consecutive requests respect the 1-second rate limit."""
        adapter = ComtradeAdapter(api_key="test-key")

        # Simulate the adapter having just made a request
        import time
        adapter._last_request_time = time.monotonic()

        # Mock the sleep so we can verify it was called
        with patch("app.services.ingestion.comtrade_adapter.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = _make_comtrade_response([])
            mock_response.raise_for_status = MagicMock()

            with patch("app.services.ingestion.comtrade_adapter.httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_client

                await adapter.fetch_flows("lithium", ["283691"], 2022)

            # Sleep should have been called since _last_request_time was just set
            mock_sleep.assert_called_once()
            sleep_duration = mock_sleep.call_args[0][0]
            assert 0.0 < sleep_duration <= 1.0
