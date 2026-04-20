"""API router registration."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.generation import router as generation_router


def create_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(generation_router)
    return router
