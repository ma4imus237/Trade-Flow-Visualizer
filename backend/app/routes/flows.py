from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.flow import FlowFilters, FlowRecord, SankeyData, TimeSeriesPoint
from app.services.flow_service import FlowService

router = APIRouter(tags=["flows"])


@router.get("/flows", response_model=list[FlowRecord])
async def get_flows(
    commodity: str | None = None,
    year: int | None = None,
    flow_type: str | None = None,
    reporter: str | None = None,
    partner: str | None = None,
    min_value: int = 0,
    limit: int = Query(default=200, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> list[FlowRecord]:
    """Return trade flows matching the provided filters."""
    filters = FlowFilters(
        commodity=commodity,
        year=year,
        flow_type=flow_type,
        reporter=reporter,
        partner=partner,
        min_value=min_value,
        limit=limit,
    )
    service = FlowService(db)
    return await service.get_flows(filters)


@router.get("/flows/top", response_model=list[FlowRecord])
async def get_top_flows(
    commodity: str = Query(...),
    year: int = Query(...),
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[FlowRecord]:
    """Return top flows by value for a given commodity and year."""
    service = FlowService(db)
    return await service.get_top_flows(commodity, year, limit)


@router.get("/flows/sankey", response_model=SankeyData)
async def get_sankey(
    commodity: str = Query(...),
    year: int = Query(...),
    flow_type: str = Query(default="export"),
    limit: int = Query(default=30, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> SankeyData:
    """Return sankey diagram data for a commodity in a given year."""
    service = FlowService(db)
    return await service.get_sankey(commodity, year, flow_type, limit)


@router.get("/flows/timeseries", response_model=list[TimeSeriesPoint])
async def get_timeseries(
    reporter: str = Query(...),
    partner: str = Query(...),
    commodity: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> list[TimeSeriesPoint]:
    """Return a time series of bilateral trade for a commodity."""
    service = FlowService(db)
    return await service.get_timeseries(reporter, partner, commodity)
