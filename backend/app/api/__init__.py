"""API router registration."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.documents import router as documents_router
from app.api.exports import router as exports_router
from app.api.generation import router as generation_router
from app.api.jobs import router as jobs_router


def create_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(documents_router)
    router.include_router(generation_router)
    router.include_router(exports_router)
    router.include_router(jobs_router)
    return router
