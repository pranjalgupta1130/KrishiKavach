from fastapi import APIRouter
from backend.api.v1.endpoints import decision, plots, explainability, translation, crop_health, market, scan

api_router = APIRouter()
api_router.include_router(plots.router)
api_router.include_router(decision.router)
api_router.include_router(explainability.router)
api_router.include_router(translation.router)
api_router.include_router(crop_health.router)
api_router.include_router(market.router)
api_router.include_router(scan.router)

