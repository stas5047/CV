from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.jobs import router as jobs_router
from app.api.media import router as media_router
from app.api.models import router as models_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(health_router)
api_router.include_router(media_router)
api_router.include_router(models_router)
api_router.include_router(jobs_router)
