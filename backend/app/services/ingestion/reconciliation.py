"""Reconciliation service for bilateral trade-flow data.

Compares reporter-declared exports with partner-declared imports for the same
bilateral pair and commodity/year.  When the two values disagree beyond a
configurable threshold the higher value is taken as the best estimate and the
discrepancy is flagged.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trade_flow import TradeFlow

logger = logging.getLogger(__name__)

DISCREPANCY_THRESHOLD = 0.50  # flag when values differ by more than 50 %


@dataclass
class DiscrepancyRecord:
    """Single bilateral discrepancy between export and import declarations."""

    reporter_id: int
    partner_id: int
    commodity_id: int
    year: int
    export_value: int
    import_value: int
    best_estimate: int
    discrepancy_pct: float

    @property
    def flagged(self) -> bool:
        return self.discrepancy_pct > DISCREPANCY_THRESHOLD


@dataclass
class ReconciliationReport:
    """Summary produced by the reconciliation pass."""

    total_pairs: int = 0
    reconciled: int = 0
    flagged: int = 0
    updated: int = 0
    discrepancies: list[DiscrepancyRecord] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_pairs": self.total_pairs,
            "reconciled": self.reconciled,
            "flagged": self.flagged,
            "updated": self.updated,
            "discrepancies_sample": [
                {
                    "reporter_id": d.reporter_id,
                    "partner_id": d.partner_id,
                    "commodity_id": d.commodity_id,
                    "year": d.year,
                    "export_value": d.export_value,
                    "import_value": d.import_value,
                    "best_estimate": d.best_estimate,
                    "discrepancy_pct": round(d.discrepancy_pct, 4),
                }
                for d in self.discrepancies[:50]
            ],
        }


async def reconcile_flows(
    session: AsyncSession,
    commodity_id: int | None = None,
    year: int | None = None,
) -> ReconciliationReport:
    """Run reconciliation across all bilateral pairs.

    For every (A exports to B) record, look for the mirror (B imports from A).
    Use ``max(export_value, import_value)`` as the best estimate.  Flag pairs
    whose values diverge by more than ``DISCREPANCY_THRESHOLD``.

    If ``apply=True`` (the default in this implementation), update the lower
    record with the best estimate and mark it as ``is_estimated=True``.

    Args:
        session: Active async database session.
        commodity_id: Restrict to a single commodity.
        year: Restrict to a single year.

    Returns:
        A :class:`ReconciliationReport`.
    """
    report = ReconciliationReport()

    # Fetch all export flows matching the filters
    export_query = select(TradeFlow).where(TradeFlow.flow_type == "export")
    if commodity_id is not None:
        export_query = export_query.where(TradeFlow.commodity_id == commodity_id)
    if year is not None:
        export_query = export_query.where(TradeFlow.year == year)

    result = await session.execute(export_query)
    export_flows: list[TradeFlow] = list(result.scalars().all())

    for export_flow in export_flows:
        # Find the mirror import: partner imports from reporter, same commodity/year
        import_query = select(TradeFlow).where(
            TradeFlow.reporter_id == export_flow.partner_id,
            TradeFlow.partner_id == export_flow.reporter_id,
            TradeFlow.commodity_id == export_flow.commodity_id,
            TradeFlow.year == export_flow.year,
            TradeFlow.flow_type == "import",
        )
        import_result = await session.execute(import_query)
        import_flow: TradeFlow | None = import_result.scalar_one_or_none()

        if import_flow is None:
            continue

        report.total_pairs += 1
        export_val = export_flow.value_usd
        import_val = import_flow.value_usd
        best = max(export_val, import_val)
        denominator = max(export_val, import_val, 1)
        discrepancy_pct = abs(export_val - import_val) / denominator

        record = DiscrepancyRecord(
            reporter_id=export_flow.reporter_id,
            partner_id=export_flow.partner_id,
            commodity_id=export_flow.commodity_id,
            year=export_flow.year,
            export_value=export_val,
            import_value=import_val,
            best_estimate=best,
            discrepancy_pct=discrepancy_pct,
        )

        report.reconciled += 1

        if record.flagged:
            report.flagged += 1
            report.discrepancies.append(record)

        # Update the lower-valued record to the best estimate
        updated = False
        if export_val < best:
            export_flow.value_usd = best
            export_flow.is_estimated = True
            updated = True
        if import_val < best:
            import_flow.value_usd = best
            import_flow.is_estimated = True
            updated = True

        if updated:
            report.updated += 1

    await session.commit()
    logger.info(
        "Reconciliation complete: %d pairs, %d reconciled, %d flagged, %d updated.",
        report.total_pairs,
        report.reconciled,
        report.flagged,
        report.updated,
    )
    return report
