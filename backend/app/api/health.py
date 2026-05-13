from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.db.health import DatabaseHealthError, check_database

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}


@router.get("/health/db", response_model=None)
def database_health():
    try:
        check_database()
    except DatabaseHealthError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "database": "unavailable"},
        )
    return {"status": "ok", "database": "available"}
