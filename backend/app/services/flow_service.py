from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.commodity import Commodity
from app.models.country import Country
from app.models.trade_flow import TradeFlow
from app.schemas.flow import (
    FlowFilters,
    FlowRecord,
    SankeyData,
    SankeyLink,
    SankeyNode,
    TimeSeriesPoint,
)


class FlowService:
    """Service layer for querying trade flow data."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_flows(self, filters: FlowFilters) -> list[FlowRecord]:
        """Query trade flows with joins to countries for geo data, applying all filters."""
        reporter = aliased(Country, name="reporter")
        partner = aliased(Country, name="partner")

        stmt = (
            select(
                reporter.iso3.label("reporter_iso3"),
                reporter.name.label("reporter_name"),
                reporter.latitude.label("reporter_lat"),
                reporter.longitude.label("reporter_lon"),
                partner.iso3.label("partner_iso3"),
                partner.name.label("partner_name"),
                partner.latitude.label("partner_lat"),
                partner.longitude.label("partner_lon"),
                Commodity.name.label("commodity"),
                TradeFlow.year,
                TradeFlow.flow_type,
                TradeFlow.value_usd,
                TradeFlow.weight_kg,
            )
            .join(reporter, TradeFlow.reporter_id == reporter.id)
            .join(partner, TradeFlow.partner_id == partner.id)
            .join(Commodity, TradeFlow.commodity_id == Commodity.id)
        )

        stmt = self._apply_filters(stmt, filters, reporter, partner)
        stmt = stmt.order_by(TradeFlow.value_usd.desc()).limit(filters.limit)

        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            FlowRecord(
                reporter_iso3=r.reporter_iso3,
                reporter_name=r.reporter_name,
                reporter_lat=r.reporter_lat,
                reporter_lon=r.reporter_lon,
                partner_iso3=r.partner_iso3,
                partner_name=r.partner_name,
                partner_lat=r.partner_lat,
                partner_lon=r.partner_lon,
                commodity=r.commodity,
                year=r.year,
                flow_type=r.flow_type,
                value_usd=r.value_usd,
                weight_kg=r.weight_kg,
            )
            for r in rows
        ]

    async def get_top_flows(
        self, commodity: str, year: int, limit: int = 50
    ) -> list[FlowRecord]:
        """Return the top flows by value for a given commodity and year."""
        filters = FlowFilters(commodity=commodity, year=year, limit=limit)
        return await self.get_flows(filters)

    async def get_sankey(
        self,
        commodity: str,
        year: int,
        flow_type: str = "export",
        limit: int = 30,
    ) -> SankeyData:
        """Build sankey nodes (countries) and links (flows) from top flows."""
        filters = FlowFilters(
            commodity=commodity, year=year, flow_type=flow_type, limit=limit
        )
        flows = await self.get_flows(filters)

        nodes_dict: dict[str, SankeyNode] = {}
        links: list[SankeyLink] = []

        for f in flows:
            src_id = f.reporter_iso3
            tgt_id = f.partner_iso3

            if src_id not in nodes_dict:
                nodes_dict[src_id] = SankeyNode(id=src_id, name=f.reporter_name)
            if tgt_id not in nodes_dict:
                nodes_dict[tgt_id] = SankeyNode(id=tgt_id, name=f.partner_name)

            links.append(SankeyLink(source=src_id, target=tgt_id, value=f.value_usd))

        return SankeyData(nodes=list(nodes_dict.values()), links=links)

    async def get_timeseries(
        self, reporter: str, partner: str, commodity: str
    ) -> list[TimeSeriesPoint]:
        """Time series for a bilateral flow across all available years."""
        reporter_alias = aliased(Country, name="reporter")
        partner_alias = aliased(Country, name="partner")

        stmt = (
            select(
                TradeFlow.year,
                TradeFlow.value_usd,
                TradeFlow.weight_kg,
            )
            .join(reporter_alias, TradeFlow.reporter_id == reporter_alias.id)
            .join(partner_alias, TradeFlow.partner_id == partner_alias.id)
            .join(Commodity, TradeFlow.commodity_id == Commodity.id)
            .where(reporter_alias.iso3 == reporter)
            .where(partner_alias.iso3 == partner)
            .where(Commodity.code == commodity)
            .order_by(TradeFlow.year)
        )

        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            TimeSeriesPoint(year=r.year, value_usd=r.value_usd, weight_kg=r.weight_kg)
            for r in rows
        ]

    @staticmethod
    def _apply_filters(stmt, filters: FlowFilters, reporter, partner):
        """Apply optional filters to a select statement."""
        if filters.commodity:
            stmt = stmt.where(Commodity.code == filters.commodity)
        if filters.year:
            stmt = stmt.where(TradeFlow.year == filters.year)
        if filters.flow_type and filters.flow_type != "both":
            stmt = stmt.where(TradeFlow.flow_type == filters.flow_type)
        if filters.reporter:
            stmt = stmt.where(reporter.iso3 == filters.reporter)
        if filters.partner:
            stmt = stmt.where(partner.iso3 == filters.partner)
        if filters.min_value > 0:
            stmt = stmt.where(TradeFlow.value_usd >= filters.min_value)
        return stmt
