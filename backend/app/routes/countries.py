from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.country import CountryPartner, CountryProfile
from app.services.aggregation_service import AggregationService, CountryNotFoundError

router = APIRouter(tags=["countries"])


@router.get("/countries/{iso3}/profile", response_model=CountryProfile)
async def get_country_profile(
    iso3: str,
    year: int | None = None,
    commodity: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> CountryProfile:
    """Return a full trade profile for a country."""
    service = AggregationService(db)
    try:
        return await service.get_country_profile(iso3, year, commodity)
    except CountryNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country not found: {iso3}")


@router.get("/countries/{iso3}/partners", response_model=list[CountryPartner])
async def get_country_partners(
    iso3: str,
    year: int = Query(...),
    commodity: str | None = None,
    flow_type: str = Query(default="export"),
    db: AsyncSession = Depends(get_db),
) -> list[CountryPartner]:
    """Return trade partners for a country in a given year."""
    service = AggregationService(db)
    try:
        return await service.get_country_partners(iso3, year, commodity, flow_type)
    except CountryNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country not found: {iso3}")
