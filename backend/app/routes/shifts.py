from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.shift import ShiftSummary, TradeShift
from app.services.shift_detector import ShiftDetector

router = APIRouter(tags=["shifts"])


@router.get("/shifts", response_model=list[TradeShift])
async def get_shifts(
    commodity: str = Query(...),
    year_from: int = Query(...),
    year_to: int = Query(...),
    min_value: int = Query(default=1_000_000),
    db: AsyncSession = Depends(get_db),
) -> list[TradeShift]:
    """Detect trade shifts between two years for a commodity."""
    detector = ShiftDetector(db)
    return await detector.detect_shifts(commodity, year_from, year_to, min_value)


@router.get("/shifts/summary", response_model=ShiftSummary)
async def get_shifts_summary(
    commodity: str = Query(...),
    year_from: int = Query(...),
    year_to: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> ShiftSummary:
    """Return a summary of trade shifts between two years for a commodity."""
    detector = ShiftDetector(db)
    return await detector.summary_shifts(commodity, year_from, year_to)
