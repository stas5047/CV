from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.cors import configure_cors
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.sensitive_log_values())

    app = FastAPI(title="AeroVision Backend")
    configure_cors(app, settings)
    app.include_router(api_router)
    return app
