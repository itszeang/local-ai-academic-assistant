"""Background job status routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query, Request

from app.common.errors import AppError, ErrorCode
from app.common.types import Job
from app.storage.repositories import RepositoryRegistry


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}")
async def get_job(job_id: str, request: Request) -> dict[str, Any]:
    repositories = RepositoryRegistry(request.app.state.database)
    job = repositories.jobs.get(job_id)
    if job is None:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message="Job was not found.",
            status_code=404,
            details={"job_id": job_id},
        )

    return {"job": _job_payload(job)}


@router.get("")
async def list_jobs(
    request: Request,
    document_id: str | None = Query(default=None),
) -> dict[str, Any]:
    repositories = RepositoryRegistry(request.app.state.database)
    if document_id is None:
        raise AppError(
            code=ErrorCode.INVALID_REQUEST,
            message="document_id is required when listing jobs.",
        )

    jobs = repositories.jobs.list_by_document(document_id)
    return {
        "document_id": document_id,
        "jobs": [_job_payload(job) for job in jobs],
    }


def _job_payload(job: Job) -> dict[str, Any]:
    return {
        "id": job.id,
        "kind": job.kind.value,
        "status": job.status.value,
        "document_id": job.document_id,
        "output_id": job.output_id,
        "progress": job.progress,
        "error": job.error,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }
