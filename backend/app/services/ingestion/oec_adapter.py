"""Fallback adapter for the OEC (Observatory of Economic Complexity) API.

Provides the same public interface as ``ComtradeAdapter`` so the ingestion
pipeline can transparently switch between data sources.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

OEC_BASE_URL = "https://oec.world/olap-proxy/data.jsonrecords"


@dataclass
class OECAdapter:
    """Async adapter for the OEC data API (fallback source)."""

    _last_request_time: float = field(default=0.0, init=False, repr=False)

    async def fetch_flows(
        self,
        commodity_code: str,
        hs_codes: list[str],
        year: int,
        reporter_iso3: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch trade flows from OEC for the given HS codes and year.

        Args:
            commodity_code: Internal commodity identifier (e.g. ``"lithium"``).
            hs_codes: List of HS-6 codes to query.
            year: Reporting year.
            reporter_iso3: If provided, restrict to a single reporter.

        Returns:
            A list of normalised flow dictionaries.
        """
        all_flows: list[dict[str, Any]] = []

        for hs6 in hs_codes:
            for flow_type_label, oec_flow in [("export", "Export"), ("import", "Import")]:
                raw_rows = await self._request(hs6, year, oec_flow, reporter_iso3)
                for row in raw_rows:
                    normalised = self._normalise_row(row, commodity_code, flow_type_label)
                    if normalised is not None:
                        all_flows.append(normalised)

        logger.info(
            "OEC: fetched %d flows for %s / year=%d (%d HS codes)",
            len(all_flows),
            commodity_code,
            year,
            len(hs_codes),
        )
        return all_flows

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _enforce_rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TransportError)),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _request(
        self,
        hs6: str,
        year: int,
        flow: str,
        reporter_iso3: str | None,
    ) -> list[dict[str, Any]]:
        await self._enforce_rate_limit()

        # OEC uses HS product codes prefixed with section identifiers.
        # The cube name and drilldown depend on the OEC schema version.
        params: dict[str, str] = {
            "cube": "trade_i_baci_a_92",
            "drilldowns": "Year,Exporter Country,Importer Country,HS6",
            "measures": "Trade Value",
            "Year": str(year),
            "HS6": hs6,
            "flow": flow,
        }
        if reporter_iso3:
            if flow == "Export":
                params["Exporter Country"] = reporter_iso3
            else:
                params["Importer Country"] = reporter_iso3

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(OEC_BASE_URL, params=params)
            self._last_request_time = time.monotonic()
            response.raise_for_status()
            payload = response.json()

        return payload.get("data", payload) if isinstance(payload, dict) else payload

    @staticmethod
    def _normalise_row(
        row: dict[str, Any],
        commodity_code: str,
        flow_type: str,
    ) -> dict[str, Any] | None:
        """Convert a single OEC row to internal format."""
        # OEC uses ISO-3 alpha-3 directly in most cube schemas.
        reporter_iso3 = row.get("Exporter Country") if flow_type == "export" else row.get("Importer Country")
        partner_iso3 = row.get("Importer Country") if flow_type == "export" else row.get("Exporter Country")

        if not reporter_iso3 or not partner_iso3:
            return None

        value = row.get("Trade Value")
        if value is None or value <= 0:
            return None

        return {
            "reporter_iso3": str(reporter_iso3)[:3].upper(),
            "partner_iso3": str(partner_iso3)[:3].upper(),
            "commodity_code": commodity_code,
            "year": int(row.get("Year", 0)),
            "flow_type": flow_type,
            "value_usd": int(value),
            "weight_kg": None,  # OEC does not reliably provide weight
        }
