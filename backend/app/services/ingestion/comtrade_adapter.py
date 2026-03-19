"""Adapter for the UN Comtrade API v1.

Fetches bilateral trade-flow data for specified HS6 commodity codes and
normalises the response into a list of plain dictionaries ready for database
insertion.

Reference: https://comtradeapi.un.org/data/v1/get/C/A
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

from app.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://comtradeapi.un.org/data/v1/get/C/A"
PAGE_SIZE = 250

# UN Comtrade numeric codes for aggregate / non-country partners to exclude.
_AGGREGATE_PARTNER_CODES: set[int] = {0, 97, 290, 492, 568, 577, 636, 837, 838, 839, 899}

# Mapping of UN Comtrade numeric reporter/partner codes to ISO-3166-1 alpha-3.
# This is a representative subset; the full mapping can be extended as needed.
_COMTRADE_TO_ISO3: dict[int, str] = {
    4: "AFG", 8: "ALB", 12: "DZA", 20: "AND", 24: "AGO", 28: "ATG",
    32: "ARG", 51: "ARM", 36: "AUS", 40: "AUT", 31: "AZE", 44: "BHS",
    48: "BHR", 50: "BGD", 52: "BRB", 112: "BLR", 56: "BEL", 84: "BLZ",
    204: "BEN", 64: "BTN", 68: "BOL", 70: "BIH", 72: "BWA", 76: "BRA",
    96: "BRN", 100: "BGR", 854: "BFA", 108: "BDI", 132: "CPV",
    116: "KHM", 120: "CMR", 124: "CAN", 140: "CAF", 148: "TCD",
    152: "CHL", 156: "CHN", 170: "COL", 174: "COM", 178: "COG",
    180: "COD", 188: "CRI", 384: "CIV", 191: "HRV", 192: "CUB",
    196: "CYP", 203: "CZE", 208: "DNK", 262: "DJI", 212: "DMA",
    214: "DOM", 218: "ECU", 818: "EGY", 222: "SLV", 226: "GNQ",
    232: "ERI", 233: "EST", 748: "SWZ", 231: "ETH", 242: "FJI",
    246: "FIN", 251: "FRA", 266: "GAB", 270: "GMB", 268: "GEO",
    276: "DEU", 288: "GHA", 300: "GRC", 308: "GRD", 320: "GTM",
    324: "GIN", 624: "GNB", 328: "GUY", 332: "HTI", 340: "HND",
    348: "HUN", 352: "ISL", 356: "IND", 360: "IDN", 364: "IRN",
    368: "IRQ", 372: "IRL", 376: "ISR", 380: "ITA", 388: "JAM",
    392: "JPN", 400: "JOR", 398: "KAZ", 404: "KEN", 296: "KIR",
    408: "PRK", 410: "KOR", 414: "KWT", 417: "KGZ", 418: "LAO",
    428: "LVA", 422: "LBN", 426: "LSO", 430: "LBR", 434: "LBY",
    438: "LIE", 440: "LTU", 442: "LUX", 450: "MDG", 454: "MWI",
    458: "MYS", 462: "MDV", 466: "MLI", 470: "MLT", 584: "MHL",
    478: "MRT", 480: "MUS", 484: "MEX", 583: "FSM", 498: "MDA",
    492: "MCO", 496: "MNG", 499: "MNE", 504: "MAR", 508: "MOZ",
    104: "MMR", 516: "NAM", 520: "NRU", 524: "NPL", 528: "NLD",
    554: "NZL", 558: "NIC", 562: "NER", 566: "NGA", 807: "MKD",
    578: "NOR", 512: "OMN", 586: "PAK", 585: "PLW", 275: "PSE",
    591: "PAN", 598: "PNG", 600: "PRY", 604: "PER", 608: "PHL",
    616: "POL", 620: "PRT", 634: "QAT", 642: "ROU", 643: "RUS",
    646: "RWA", 659: "KNA", 662: "LCA", 670: "VCT", 882: "WSM",
    674: "SMR", 678: "STP", 682: "SAU", 686: "SEN", 688: "SRB",
    690: "SYC", 694: "SLE", 702: "SGP", 703: "SVK", 705: "SVN",
    90: "SLB", 706: "SOM", 710: "ZAF", 728: "SSD", 724: "ESP",
    144: "LKA", 729: "SDN", 740: "SUR", 752: "SWE", 757: "CHE",
    760: "SYR", 158: "TWN", 762: "TJK", 834: "TZA", 764: "THA",
    626: "TLS", 768: "TGO", 776: "TON", 780: "TTO", 788: "TUN",
    792: "TUR", 795: "TKM", 798: "TUV", 800: "UGA", 804: "UKR",
    784: "ARE", 826: "GBR", 842: "USA", 858: "URY", 860: "UZB",
    548: "VUT", 862: "VEN", 704: "VNM", 887: "YEM", 894: "ZMB",
    716: "ZWE", 344: "HKG", 446: "MAC",
}


@dataclass
class ComtradeAdapter:
    """Async adapter for the UN Comtrade bulk-download API."""

    api_key: str = field(default_factory=lambda: settings.comtrade_api_key)
    _last_request_time: float = field(default=0.0, init=False, repr=False)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    async def fetch_flows(
        self,
        commodity_code: str,
        hs_codes: list[str],
        year: int,
        reporter_iso3: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch trade flows from Comtrade for the given HS codes and year.

        Args:
            commodity_code: Internal commodity identifier (e.g. ``"lithium"``).
            hs_codes: List of HS-6 codes to query.
            year: Reporting year.
            reporter_iso3: If provided, restrict to a single reporter.

        Returns:
            A list of normalised flow dictionaries with keys:
            ``reporter_iso3``, ``partner_iso3``, ``commodity_code``,
            ``year``, ``flow_type``, ``value_usd``, ``weight_kg``.
        """
        all_flows: list[dict[str, Any]] = []
        for hs6 in hs_codes:
            offset = 0
            while True:
                raw = await self._request(hs6, year, reporter_iso3, offset)
                data_rows = raw.get("data", [])
                if not data_rows:
                    break

                for row in data_rows:
                    normalised = self._normalise_row(row, commodity_code)
                    if normalised is not None:
                        all_flows.append(normalised)

                if len(data_rows) < PAGE_SIZE:
                    break
                offset += PAGE_SIZE

        logger.info(
            "Comtrade: fetched %d flows for %s / year=%d (%d HS codes)",
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
        """Ensure at least 1 second between consecutive requests."""
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
        reporter_iso3: str | None,
        offset: int,
    ) -> dict[str, Any]:
        await self._enforce_rate_limit()

        params: dict[str, str] = {
            "cmdCode": hs6,
            "flowCode": "M,X",
            "period": str(year),
            "maxRecords": str(PAGE_SIZE),
            "format": "JSON",
        }
        if reporter_iso3:
            params["reporterCode"] = reporter_iso3
        if offset:
            params["offset"] = str(offset)

        headers: dict[str, str] = {}
        if self.api_key:
            headers["Ocp-Apim-Subscription-Key"] = self.api_key

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(BASE_URL, params=params, headers=headers)
            self._last_request_time = time.monotonic()
            response.raise_for_status()
            return response.json()

    @staticmethod
    def _normalise_row(row: dict[str, Any], commodity_code: str) -> dict[str, Any] | None:
        """Convert a single Comtrade JSON row to internal format.

        Returns ``None`` if the partner is an aggregate entity.
        """
        partner_code = row.get("partnerCode")
        reporter_code = row.get("reporterCode")

        if partner_code in _AGGREGATE_PARTNER_CODES:
            return None

        reporter_iso3 = _COMTRADE_TO_ISO3.get(reporter_code)
        partner_iso3 = _COMTRADE_TO_ISO3.get(partner_code)

        if reporter_iso3 is None or partner_iso3 is None:
            return None

        flow_code = row.get("flowCode", "")
        if flow_code == "M":
            flow_type = "import"
        elif flow_code == "X":
            flow_type = "export"
        else:
            return None

        value = row.get("primaryValue")
        if value is None or value <= 0:
            return None

        return {
            "reporter_iso3": reporter_iso3,
            "partner_iso3": partner_iso3,
            "commodity_code": commodity_code,
            "year": row.get("period", 0),
            "flow_type": flow_type,
            "value_usd": int(value),
            "weight_kg": int(row["netWt"]) if row.get("netWt") else None,
        }
