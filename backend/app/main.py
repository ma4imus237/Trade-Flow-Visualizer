from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


def create_app() -> FastAPI:
    application = FastAPI(title="Trade Flow Visualizer", version="0.1.0")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.routes import flows, countries, commodities, shifts

    application.include_router(flows.router, prefix="/api/v1")
    application.include_router(countries.router, prefix="/api/v1")
    application.include_router(commodities.router, prefix="/api/v1")
    application.include_router(shifts.router, prefix="/api/v1")

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    return application


app = create_app()
