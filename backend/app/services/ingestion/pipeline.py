"""Ingestion pipeline that fetches trade-flow data from external APIs, normalises
it, and upserts into the ``trade_flows`` table.

After a complete run the ``aggregated_flows`` materialized view is refreshed.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Protocol

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commodity import Commodity, HSCodeMapping
from app.models.country import Country
from app.models.trade_flow import TradeFlow

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parents[4] / "data" / "static"


class FlowAdapter(Protocol):
    """Protocol that both ComtradeAdapter and OECAdapter satisfy."""

    async def fetch_flows(
        self,
        commodity_code: str,
        hs_codes: list[str],
        year: int,
        reporter_iso3: str | None = None,
    ) -> list[dict[str, Any]]: ...


class IngestionPipeline:
    """Orchestrates data fetching, normalisation and persistence."""

    def __init__(self, session: AsyncSession, adapter: FlowAdapter) -> None:
        self.session = session
        self.adapter = adapter
        self._country_cache: dict[str, int] = {}
        self._commodity_cache: dict[str, int] = {}

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    async def run(
        self,
        commodities: list[str] | None = None,
        years: list[int] | None = None,
    ) -> dict[str, Any]:
        """Execute a full ingestion run.

        Args:
            commodities: List of commodity codes to ingest.  ``None`` means all.
            years: List of years to ingest.  ``None`` defaults to ``[2022, 2023]``.

        Returns:
            Summary dict with counts per commodity/year.
        """
        await self._warm_caches()

        commodity_hs_map = await self._load_commodity_hs_map(commodities)
        if years is None:
            years = [2022, 2023]

        summary: dict[str, Any] = {}

        for code, hs_codes in commodity_hs_map.items():
            for year in years:
                key = f"{code}/{year}"
                try:
                    count = await self.ingest_commodity_year(code, hs_codes, year)
                    summary[key] = {"status": "ok", "rows": count}
                    logger.info("Ingested %d rows for %s", count, key)
                except Exception:
                    logger.exception("Failed to ingest %s", key)
                    summary[key] = {"status": "error"}

        await self._refresh_materialized_view()
        return summary

    async def ingest_commodity_year(
        self,
        commodity_code: str,
        hs_codes: list[str],
        year: int,
    ) -> int:
        """Fetch and upsert flows for a single commodity/year pair.

        Returns the number of rows upserted.
        """
        flows = await self.adapter.fetch_flows(commodity_code, hs_codes, year)
        upserted = 0

        for flow in flows:
            reporter_id = self._country_cache.get(flow["reporter_iso3"])
            partner_id = self._country_cache.get(flow["partner_iso3"])
            commodity_id = self._commodity_cache.get(flow["commodity_code"])

            if reporter_id is None or partner_id is None or commodity_id is None:
                continue

            result = await self.session.execute(
                select(TradeFlow).where(
                    TradeFlow.reporter_id == reporter_id,
                    TradeFlow.partner_id == partner_id,
                    TradeFlow.commodity_id == commodity_id,
                    TradeFlow.year == flow["year"],
                    TradeFlow.flow_type == flow["flow_type"],
                )
            )
            existing: TradeFlow | None = result.scalar_one_or_none()

            if existing is not None:
                existing.value_usd = flow["value_usd"]
                existing.weight_kg = flow.get("weight_kg")
                existing.is_estimated = False
            else:
                self.session.add(
                    TradeFlow(
                        reporter_id=reporter_id,
                        partner_id=partner_id,
                        commodity_id=commodity_id,
                        year=flow["year"],
                        flow_type=flow["flow_type"],
                        value_usd=flow["value_usd"],
                        weight_kg=flow.get("weight_kg"),
                        is_estimated=False,
                    )
                )
            upserted += 1

        await self.session.commit()
        return upserted

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _warm_caches(self) -> None:
        """Pre-load country and commodity lookups."""
        result = await self.session.execute(select(Country))
        for country in result.scalars():
            self._country_cache[country.iso3] = country.id

        result = await self.session.execute(select(Commodity))
        for commodity in result.scalars():
            self._commodity_cache[commodity.code] = commodity.id

    async def _load_commodity_hs_map(
        self,
        filter_codes: list[str] | None,
    ) -> dict[str, list[str]]:
        """Return a mapping of commodity_code -> [hs6, ...] from the database."""
        query = select(Commodity)
        if filter_codes:
            query = query.where(Commodity.code.in_(filter_codes))

        result = await self.session.execute(query)
        commodity_hs: dict[str, list[str]] = {}

        for commodity in result.scalars():
            hs_result = await self.session.execute(
                select(HSCodeMapping.hs6).where(HSCodeMapping.commodity_id == commodity.id)
            )
            hs_codes = [row[0] for row in hs_result.all()]
            if hs_codes:
                commodity_hs[commodity.code] = hs_codes

        if not commodity_hs:
            # Fallback to static file if DB is empty
            logger.warning("No HS mappings found in DB; falling back to static JSON.")
            commodity_hs = self._load_hs_from_json(filter_codes)

        return commodity_hs

    @staticmethod
    def _load_hs_from_json(filter_codes: list[str] | None) -> dict[str, list[str]]:
        json_path = STATIC_DIR / "hs_mappings.json"
        with open(json_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        result: dict[str, list[str]] = {}
        for entry in data:
            code = entry["code"]
            if filter_codes and code not in filter_codes:
                continue
            result[code] = [h["hs6"] for h in entry.get("hs_codes", [])]
        return result

    async def _refresh_materialized_view(self) -> None:
        logger.info("Refreshing aggregated_flows materialized view...")
        try:
            await self.session.execute(
                text("REFRESH MATERIALIZED VIEW CONCURRENTLY aggregated_flows")
            )
            await self.session.commit()
            logger.info("Materialized view refreshed successfully.")
        except Exception:
            logger.exception("Failed to refresh materialized view.")
            await self.session.rollback()
