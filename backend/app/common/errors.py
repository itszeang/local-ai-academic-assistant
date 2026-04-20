"""Structured application errors and API error helpers."""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    INVALID_REQUEST = "invalid_request"
    NOT_FOUND = "not_found"
    INGESTION_FAILED = "ingestion_failed"
    EXPORT_FAILED = "export_failed"
    INTERNAL_ERROR = "internal_error"


class AppError(Exception):
    """Predictable application failure with an API-safe payload."""

    def __init__(
        self,
        *,
        code: ErrorCode,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def error_payload(error: AppError) -> dict[str, Any]:
    return {
        "code": error.code.value,
        "message": error.message,
        "details": error.details,
    }
