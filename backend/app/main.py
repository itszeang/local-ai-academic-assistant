"""FastAPI application entry point."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import create_api_router
from app.common.config import Settings, load_settings
from app.common.errors import AppError, error_payload
from app.common.logging import configure_logging
from app.storage.paths import ensure_local_directories
from app.storage.sqlite import SQLiteDatabase


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or load_settings()
    configure_logging()
    ensure_local_directories(app_settings.local_directories)

    database = SQLiteDatabase(app_settings.sqlite_path)
    database.initialize()

    app = FastAPI(
        title="Local AI Academic Assistant API",
        version="0.1.0",
        description="Local-only API for document-grounded academic assistance.",
    )
    app.state.settings = app_settings
    app.state.database = database

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=error_payload(exc))

    @app.get("/health")
    async def health() -> dict[str, Any]:
        missing_local_resources: list[str] = []
        for path in app_settings.local_directories:
            if not path.exists():
                missing_local_resources.append(str(path))

        return {
            "status": "ready" if not missing_local_resources else "degraded",
            "offline_ready": not missing_local_resources,
            "missing_local_resources": missing_local_resources,
        }

    app.include_router(create_api_router())
    return app


app = create_app()
