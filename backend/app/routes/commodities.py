from fastapi import APIRouter

router = APIRouter(tags=["commodities"])


@router.get("/commodities")
async def get_commodities():
    return []


@router.get("/years")
async def get_years():
    return []
