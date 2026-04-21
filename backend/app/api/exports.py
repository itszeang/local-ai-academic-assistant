"""Academic output export routes."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.common.errors import AppError, ErrorCode
from app.common.types import ExportFile, JobKind, JobStatus
from app.export.docx_exporter import DocxExporter
from app.storage.repositories import RepositoryRegistry


router = APIRouter(tags=["exports"])


class ExportRequestBody(BaseModel):
    filename: str | None = None


@router.post("/outputs/{output_id}/export", status_code=202)
async def export_academic_output(
    output_id: str,
    request: Request,
    body: ExportRequestBody | None = None,
) -> dict[str, Any]:
    repositories = RepositoryRegistry(request.app.state.database)
    output = repositories.academic_outputs.get(output_id)
    if output is None:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message="Academic output was not found.",
            status_code=404,
            details={"output_id": output_id},
        )

    filename = _safe_filename((body.filename if body else None) or f"{output.id}.docx")
    export_path = _safe_export_path(request.app.state.settings.exports_dir, filename)
    job = repositories.jobs.create(
        kind=JobKind.EXPORT,
        status=JobStatus.RUNNING,
        output_id=output.id,
        progress=0.0,
    )

    try:
        DocxExporter().export(output=output, path=export_path)
    except Exception as exc:
        repositories.jobs.update(job.id, status=JobStatus.FAILED, progress=1.0, error=str(exc))
        export_file = repositories.export_files.create(
            academic_output_id=output.id,
            path=export_path,
            status=JobStatus.FAILED,
            error_message=str(exc),
        )
        raise AppError(
            code=ErrorCode.EXPORT_FAILED,
            message="DOCX export failed.",
            status_code=500,
            details={"export_file_id": export_file.id},
        ) from exc

    repositories.jobs.update(job.id, status=JobStatus.SUCCEEDED, progress=1.0)
    export_file = repositories.export_files.create(
        academic_output_id=output.id,
        path=export_path,
        status=JobStatus.SUCCEEDED,
    )
    return _export_payload(export_file, job_id=job.id)


def _export_payload(export_file: ExportFile, *, job_id: str) -> dict[str, Any]:
    return {
        "id": job_id,
        "export_file_id": export_file.id,
        "output_id": export_file.academic_output_id,
        "status": export_file.status.value,
        "path": str(export_file.path),
    }


def _safe_filename(filename: str) -> str:
    name = Path(filename).name.strip() or "academic-output.docx"
    name = re.sub(r"[^A-Za-z0-9._ -]+", "_", name)
    if not name.lower().endswith(".docx"):
        name = f"{name}.docx"
    return name


def _safe_export_path(exports_dir: Path, filename: str) -> Path:
    root = Path(exports_dir).resolve()
    path = (root / filename).resolve()
    if root != path and root not in path.parents:
        raise AppError(
            code=ErrorCode.INVALID_REQUEST,
            message="Export filename must resolve inside the local exports directory.",
        )
    return path
