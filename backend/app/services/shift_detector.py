from sqlalchemy import func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.commodity import Commodity
from app.models.country import Country
from app.models.trade_flow import TradeFlow
from app.schemas.shift import ShiftSummary, TradeShift


class ShiftDetector:
    """Detects significant shifts in bilateral trade flows between two years."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def detect_shifts(
        self,
        commodity: str,
        year_from: int,
        year_to: int,
        min_value: int = 1_000_000,
    ) -> list[TradeShift]:
        """Compare bilateral values between two years and classify shifts.

        Shift classification:
        - surge: increase > 100%
        - collapse: decrease > 50%
        - new: value_from == 0 but value_to > min_value
        - abandoned: value_from > min_value but value_to == 0
        """
        reporter = aliased(Country, name="reporter")
        partner = aliased(Country, name="partner")

        # Subquery for year_from values
        from_sub = (
            select(
                TradeFlow.reporter_id,
                TradeFlow.partner_id,
                func.sum(TradeFlow.value_usd).label("value_from"),
            )
            .join(Commodity, TradeFlow.commodity_id == Commodity.id)
            .where(Commodity.code == commodity)
            .where(TradeFlow.year == year_from)
            .group_by(TradeFlow.reporter_id, TradeFlow.partner_id)
            .subquery("from_sub")
        )

        # Subquery for year_to values
        to_sub = (
            select(
                TradeFlow.reporter_id,
                TradeFlow.partner_id,
                func.sum(TradeFlow.value_usd).label("value_to"),
            )
            .join(Commodity, TradeFlow.commodity_id == Commodity.id)
            .where(Commodity.code == commodity)
            .where(TradeFlow.year == year_to)
            .group_by(TradeFlow.reporter_id, TradeFlow.partner_id)
            .subquery("to_sub")
        )

        # Full outer join via union of left joins
        # Left join: from_sub LEFT JOIN to_sub
        left_stmt = (
            select(
                from_sub.c.reporter_id,
                from_sub.c.partner_id,
                from_sub.c.value_from,
                func.coalesce(to_sub.c.value_to, literal(0)).label("value_to"),
            )
            .outerjoin(
                to_sub,
                (from_sub.c.reporter_id == to_sub.c.reporter_id)
                & (from_sub.c.partner_id == to_sub.c.partner_id),
            )
        )

        # Right-only: to_sub rows not in from_sub
        right_only_stmt = (
            select(
                to_sub.c.reporter_id,
                to_sub.c.partner_id,
                literal(0).label("value_from"),
                to_sub.c.value_to,
            )
            .outerjoin(
                from_sub,
                (to_sub.c.reporter_id == from_sub.c.reporter_id)
                & (to_sub.c.partner_id == from_sub.c.partner_id),
            )
            .where(from_sub.c.reporter_id.is_(None))
        )

        combined = left_stmt.union_all(right_only_stmt).subquery("combined")

        # Main query joining back to country names
        stmt = (
            select(
                reporter.iso3.label("reporter_iso3"),
                reporter.name.label("reporter_name"),
                partner.iso3.label("partner_iso3"),
                partner.name.label("partner_name"),
                combined.c.value_from,
                combined.c.value_to,
            )
            .join(reporter, combined.c.reporter_id == reporter.id)
            .join(partner, combined.c.partner_id == partner.id)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        shifts: list[TradeShift] = []
        for r in rows:
            val_from = int(r.value_from)
            val_to = int(r.value_to)
            change_abs = val_to - val_from

            # Classify shift
            shift_type = self._classify(val_from, val_to, min_value)
            if shift_type is None:
                continue

            if val_from > 0:
                change_pct = round((change_abs / val_from) * 100, 2)
            else:
                change_pct = 100.0 if val_to > 0 else 0.0

            shifts.append(
                TradeShift(
                    reporter_iso3=r.reporter_iso3,
                    reporter_name=r.reporter_name,
                    partner_iso3=r.partner_iso3,
                    partner_name=r.partner_name,
                    commodity=commodity,
                    year_from=year_from,
                    year_to=year_to,
                    value_from=val_from,
                    value_to=val_to,
                    change_pct=change_pct,
                    change_abs=change_abs,
                    shift_type=shift_type,
                )
            )

        # Sort by absolute change descending
        shifts.sort(key=lambda s: abs(s.change_abs), reverse=True)
        return shifts

    @staticmethod
    def _classify(val_from: int, val_to: int, min_value: int) -> str | None:
        """Classify a bilateral flow change into a shift type or None."""
        if val_from == 0 and val_to >= min_value:
            return "new"
        if val_from >= min_value and val_to == 0:
            return "abandoned"
        if val_from > 0 and val_to > 0:
            change_pct = ((val_to - val_from) / val_from) * 100
            if change_pct > 100:
                return "surge"
            if change_pct < -50:
                return "collapse"
        return None

    async def summary_shifts(
        self, commodity: str, year_from: int, year_to: int
    ) -> ShiftSummary:
        """Generate a summary of all detected shifts for a commodity pair of years."""
        shifts = await self.detect_shifts(commodity, year_from, year_to)

        surges = [s for s in shifts if s.shift_type == "surge"]
        collapses = [s for s in shifts if s.shift_type == "collapse"]
        new_flows = [s for s in shifts if s.shift_type == "new"]
        abandoned = [s for s in shifts if s.shift_type == "abandoned"]

        return ShiftSummary(
            commodity=commodity,
            total_shifts=len(shifts),
            surges=len(surges),
            collapses=len(collapses),
            new_flows=len(new_flows),
            abandoned_flows=len(abandoned),
            top_shifts=shifts[:20],
        )
