from fastapi import APIRouter

router = APIRouter(tags=["flows"])


@router.get("/flows")
async def get_flows():
    return []


@router.get("/flows/top")
async def get_top_flows():
    return []


@router.get("/flows/sankey")
async def get_sankey():
    return {"nodes": [], "links": []}


@router.get("/flows/timeseries")
async def get_timeseries():
    return []
