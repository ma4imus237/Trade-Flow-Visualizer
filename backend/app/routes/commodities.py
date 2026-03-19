from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.commodity import Commodity
from app.schemas.commodity import CommodityOut
from app.services.aggregation_service import AggregationService

router = APIRouter(tags=["commodities"])


@router.get("/commodities", response_model=list[CommodityOut])
async def get_commodities(
    db: AsyncSession = Depends(get_db),
) -> list[CommodityOut]:
    """Return all available commodities."""
    stmt = select(Commodity).order_by(Commodity.name)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [CommodityOut(code=r.code, name=r.name, color=r.color) for r in rows]


@router.get("/years", response_model=list[int])
async def get_years(
    db: AsyncSession = Depends(get_db),
) -> list[int]:
    """Return all available years in the trade flow data."""
    service = AggregationService(db)
    return await service.get_available_years()
