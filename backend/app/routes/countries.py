from fastapi import APIRouter

router = APIRouter(tags=["countries"])


@router.get("/countries/{iso3}/profile")
async def get_country_profile(iso3: str):
    return {}


@router.get("/countries/{iso3}/partners")
async def get_country_partners(iso3: str):
    return []
