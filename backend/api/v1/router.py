from fastapi import APIRouter
from backend.api.v1.endpoints import decision, plots, explainability, translation

api_router = APIRouter()
api_router.include_router(plots.router)
api_router.include_router(decision.router)
api_router.include_router(explainability.router)
api_router.include_router(translation.router)
