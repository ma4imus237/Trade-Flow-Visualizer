from fastapi import APIRouter

router = APIRouter(tags=["shifts"])


@router.get("/shifts")
async def get_shifts():
    return []


@router.get("/shifts/summary")
async def get_shifts_summary():
    return {}
