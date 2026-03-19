from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.commodity import Commodity
from app.models.country import Country
from app.models.trade_flow import TradeFlow
from app.schemas.country import CountryPartner, CountryProfile


class CountryNotFoundError(Exception):
    """Raised when a country ISO3 code does not exist in the database."""

    def __init__(self, iso3: str) -> None:
        self.iso3 = iso3
        super().__init__(f"Country not found: {iso3}")


class AggregationService:
    """Service layer for aggregation queries: country profiles, partners, years."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_country_profile(
        self, iso3: str, year: int | None = None, commodity: str | None = None
    ) -> CountryProfile:
        """Full profile with totals, top partners, and top commodities."""
        # Fetch the country record
        country_stmt = select(Country).where(Country.iso3 == iso3)
        country_result = await self.session.execute(country_stmt)
        country = country_result.scalar_one_or_none()
        if country is None:
            raise CountryNotFoundError(iso3)

        # Base filter for this country as reporter
        base_filters = [TradeFlow.reporter_id == country.id]
        if year is not None:
            base_filters.append(TradeFlow.year == year)
        if commodity is not None:
            base_filters.append(Commodity.code == commodity)

        # Total exports
        export_stmt = (
            select(func.coalesce(func.sum(TradeFlow.value_usd), 0))
            .join(Commodity, TradeFlow.commodity_id == Commodity.id)
            .where(*base_filters, TradeFlow.flow_type == "export")
        )
        total_exports = (await self.session.execute(export_stmt)).scalar_one()

        # Total imports
        import_stmt = (
            select(func.coalesce(func.sum(TradeFlow.value_usd), 0))
            .join(Commodity, TradeFlow.commodity_id == Commodity.id)
            .where(*base_filters, TradeFlow.flow_type == "import")
        )
        total_imports = (await self.session.execute(import_stmt)).scalar_one()

        # Top export partners
        top_export_partners = await self._top_partners(
            country.id, "export", year, commodity, limit=5
        )

        # Top import partners
        top_import_partners = await self._top_partners(
            country.id, "import", year, commodity, limit=5
        )

        # Top commodities
        top_commodities = await self._top_commodities(country.id, year, limit=5)

        return CountryProfile(
            iso3=country.iso3,
            name=country.name,
            region=country.region,
            total_exports=total_exports,
            total_imports=total_imports,
            top_export_partners=[
                {"iso3": p.iso3, "name": p.name, "value_usd": p.value_usd}
                for p in top_export_partners
            ],
            top_import_partners=[
                {"iso3": p.iso3, "name": p.name, "value_usd": p.value_usd}
                for p in top_import_partners
            ],
            top_commodities=top_commodities,
        )

    async def _top_partners(
        self,
        country_id: int,
        flow_type: str,
        year: int | None,
        commodity: str | None,
        limit: int = 5,
    ) -> list[CountryPartner]:
        """Return top trade partners by total value for a given flow type."""
        partner = aliased(Country, name="partner")

        stmt = (
            select(
                partner.iso3,
                partner.name,
                func.sum(TradeFlow.value_usd).label("value_usd"),
            )
            .join(partner, TradeFlow.partner_id == partner.id)
            .join(Commodity, TradeFlow.commodity_id == Commodity.id)
            .where(TradeFlow.reporter_id == country_id)
            .where(TradeFlow.flow_type == flow_type)
            .group_by(partner.iso3, partner.name)
            .order_by(func.sum(TradeFlow.value_usd).desc())
            .limit(limit)
        )

        if year is not None:
            stmt = stmt.where(TradeFlow.year == year)
        if commodity is not None:
            stmt = stmt.where(Commodity.code == commodity)

        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            CountryPartner(
                iso3=r.iso3, name=r.name, value_usd=r.value_usd, flow_type=flow_type
            )
            for r in rows
        ]

    async def _top_commodities(
        self, country_id: int, year: int | None, limit: int = 5
    ) -> list[dict]:
        """Return top commodities by total trade value for a country."""
        stmt = (
            select(
                Commodity.code,
                Commodity.name,
                func.sum(TradeFlow.value_usd).label("total_value"),
            )
            .join(Commodity, TradeFlow.commodity_id == Commodity.id)
            .where(TradeFlow.reporter_id == country_id)
            .group_by(Commodity.code, Commodity.name)
            .order_by(func.sum(TradeFlow.value_usd).desc())
            .limit(limit)
        )

        if year is not None:
            stmt = stmt.where(TradeFlow.year == year)

        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            {"code": r.code, "name": r.name, "total_value": r.total_value} for r in rows
        ]

    async def get_country_partners(
        self,
        iso3: str,
        year: int,
        commodity: str | None = None,
        flow_type: str = "export",
    ) -> list[CountryPartner]:
        """Return trade partners for a country in a given year."""
        country_stmt = select(Country.id).where(Country.iso3 == iso3)
        country_result = await self.session.execute(country_stmt)
        country_id = country_result.scalar_one_or_none()
        if country_id is None:
            raise CountryNotFoundError(iso3)

        return await self._top_partners(
            country_id, flow_type, year, commodity, limit=50
        )

    async def get_available_years(self) -> list[int]:
        """Return distinct years available in trade_flows, sorted ascending."""
        stmt = select(TradeFlow.year).distinct().order_by(TradeFlow.year)
        result = await self.session.execute(stmt)
        return [r[0] for r in result.all()]
