"""Tests for the ingestion pipeline and reconciliation logic."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commodity import Commodity
from app.models.country import Country
from app.models.trade_flow import TradeFlow
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.reconciliation import reconcile_flows


class FakeAdapter:
    """In-memory adapter that returns pre-configured flows."""

    def __init__(self, flows: list[dict[str, Any]] | None = None) -> None:
        self._flows = flows or []

    async def fetch_flows(
        self,
        commodity_code: str,
        hs_codes: list[str],
        year: int,
        reporter_iso3: str | None = None,
    ) -> list[dict[str, Any]]:
        return [
            f
            for f in self._flows
            if f["commodity_code"] == commodity_code and f["year"] == year
        ]


class TestIngestionPipelineUpsert:
    """Test pipeline insert and update behaviour."""

    @pytest.mark.asyncio
    async def test_insert_new_flows(self, seeded_session: AsyncSession):
        """Pipeline should insert new flows that do not yet exist."""
        adapter = FakeAdapter(
            flows=[
                {
                    "reporter_iso3": "BRA",
                    "partner_iso3": "CHN",
                    "commodity_code": "lithium",
                    "year": 2023,
                    "flow_type": "export",
                    "value_usd": 500_000_000,
                    "weight_kg": 25_000_000,
                },
            ]
        )
        pipeline = IngestionPipeline(seeded_session, adapter)

        # Patch the materialized view refresh (SQLite does not support it)
        with patch.object(pipeline, "_refresh_materialized_view", new_callable=AsyncMock):
            summary = await pipeline.run(commodities=["lithium"], years=[2023])

        assert summary["lithium/2023"]["status"] == "ok"
        assert summary["lithium/2023"]["rows"] == 1

        # Verify the row landed in the database
        result = await seeded_session.execute(
            select(TradeFlow).where(
                TradeFlow.flow_type == "export",
                TradeFlow.year == 2023,
            )
        )
        exports_2023 = list(result.scalars().all())
        bra_exports = [f for f in exports_2023 if f.value_usd == 500_000_000]
        assert len(bra_exports) == 1

    @pytest.mark.asyncio
    async def test_upsert_updates_existing(self, seeded_session: AsyncSession):
        """When a flow already exists, pipeline should update its value."""
        # Look up the AUS->CHN lithium 2023 export already in the seed data
        result = await seeded_session.execute(select(Country).where(Country.iso3 == "AUS"))
        aus = result.scalar_one()
        result = await seeded_session.execute(select(Country).where(Country.iso3 == "CHN"))
        chn = result.scalar_one()
        result = await seeded_session.execute(select(Commodity).where(Commodity.code == "lithium"))
        lithium = result.scalar_one()

        # Verify the existing value
        result = await seeded_session.execute(
            select(TradeFlow).where(
                TradeFlow.reporter_id == aus.id,
                TradeFlow.partner_id == chn.id,
                TradeFlow.commodity_id == lithium.id,
                TradeFlow.year == 2023,
                TradeFlow.flow_type == "export",
            )
        )
        existing = result.scalar_one()
        assert existing.value_usd == 4_200_000_000

        # Run pipeline with updated value
        adapter = FakeAdapter(
            flows=[
                {
                    "reporter_iso3": "AUS",
                    "partner_iso3": "CHN",
                    "commodity_code": "lithium",
                    "year": 2023,
                    "flow_type": "export",
                    "value_usd": 4_500_000_000,
                    "weight_kg": 220_000_000,
                },
            ]
        )
        pipeline = IngestionPipeline(seeded_session, adapter)
        with patch.object(pipeline, "_refresh_materialized_view", new_callable=AsyncMock):
            summary = await pipeline.run(commodities=["lithium"], years=[2023])

        assert summary["lithium/2023"]["rows"] == 1

        # Value should be updated
        await seeded_session.refresh(existing)
        assert existing.value_usd == 4_500_000_000

    @pytest.mark.asyncio
    async def test_skips_unknown_countries(self, seeded_session: AsyncSession):
        """Flows with country codes not in the DB should be silently skipped."""
        adapter = FakeAdapter(
            flows=[
                {
                    "reporter_iso3": "ZZZ",  # non-existent
                    "partner_iso3": "CHN",
                    "commodity_code": "lithium",
                    "year": 2023,
                    "flow_type": "export",
                    "value_usd": 100,
                    "weight_kg": None,
                },
            ]
        )
        pipeline = IngestionPipeline(seeded_session, adapter)
        with patch.object(pipeline, "_refresh_materialized_view", new_callable=AsyncMock):
            summary = await pipeline.run(commodities=["lithium"], years=[2023])

        # The row should have been skipped (0 successful inserts)
        assert summary["lithium/2023"]["rows"] == 0

    @pytest.mark.asyncio
    async def test_run_with_no_commodities_defaults_to_all(self, seeded_session: AsyncSession):
        """When commodities=None, the pipeline should process all known commodities."""
        adapter = FakeAdapter(flows=[])
        pipeline = IngestionPipeline(seeded_session, adapter)
        with patch.object(pipeline, "_refresh_materialized_view", new_callable=AsyncMock):
            summary = await pipeline.run(commodities=None, years=[2022])

        # Both lithium and copper should appear in the summary
        assert "lithium/2022" in summary
        assert "copper/2022" in summary


class TestReconciliation:
    """Test bilateral reconciliation logic."""

    @pytest.mark.asyncio
    async def test_reconciliation_updates_lower_values(self, seeded_session: AsyncSession):
        """The reconciliation should set both sides of a pair to max(export, import)."""
        # Seed data has AUS exports lithium to CHN at 5B, CHN imports at 4.8B
        result = await seeded_session.execute(select(Commodity).where(Commodity.code == "lithium"))
        lithium = result.scalar_one()

        report = await reconcile_flows(seeded_session, commodity_id=lithium.id, year=2022)

        # Should have found pairs (AUS->CHN, CHL->USA)
        assert report.total_pairs >= 2
        assert report.reconciled >= 2

        # The import value (4.8B) should now be updated to 5B
        result = await seeded_session.execute(select(Country).where(Country.iso3 == "CHN"))
        chn = result.scalar_one()
        result = await seeded_session.execute(select(Country).where(Country.iso3 == "AUS"))
        aus = result.scalar_one()

        result = await seeded_session.execute(
            select(TradeFlow).where(
                TradeFlow.reporter_id == chn.id,
                TradeFlow.partner_id == aus.id,
                TradeFlow.commodity_id == lithium.id,
                TradeFlow.year == 2022,
                TradeFlow.flow_type == "import",
            )
        )
        import_flow = result.scalar_one()
        assert import_flow.value_usd == 5_000_000_000
        assert import_flow.is_estimated is True

    @pytest.mark.asyncio
    async def test_reconciliation_flags_large_discrepancies(self, seeded_session: AsyncSession):
        """Pairs with >50% discrepancy should be flagged."""
        result = await seeded_session.execute(select(Commodity).where(Commodity.code == "copper"))
        copper = result.scalar_one()

        report = await reconcile_flows(seeded_session, commodity_id=copper.id, year=2022)

        # COD exports 2B, CHN imports 5B -- discrepancy = 3B/5B = 60% > 50%
        assert report.flagged >= 1
        flagged_pairs = [
            d for d in report.discrepancies
            if d.export_value == 2_000_000_000 and d.import_value == 5_000_000_000
        ]
        assert len(flagged_pairs) == 1
        assert flagged_pairs[0].best_estimate == 5_000_000_000
        assert flagged_pairs[0].discrepancy_pct > 0.50

    @pytest.mark.asyncio
    async def test_reconciliation_report_serialisable(self, seeded_session: AsyncSession):
        """The report as_dict() method should return a JSON-serialisable dict."""
        report = await reconcile_flows(seeded_session)
        report_dict = report.as_dict()
        assert isinstance(report_dict, dict)
        assert "total_pairs" in report_dict
        assert "discrepancies_sample" in report_dict
        assert isinstance(report_dict["discrepancies_sample"], list)
