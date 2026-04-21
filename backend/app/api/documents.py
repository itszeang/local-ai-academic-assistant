"""Document workspace routes."""

from __future__ import annotations

import importlib
import inspect
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

from app.common.errors import AppError, ErrorCode
from app.common.types import Document, DocumentStatus, Job, JobKind, JobStatus, Workspace
from app.storage.repositories import RepositoryRegistry


router = APIRouter(prefix="/documents", tags=["documents"])


class ActiveDocumentsRequest(BaseModel):
    document_ids: list[str] = Field(default_factory=list)
    workspace_id: str | None = None


@router.post("", status_code=202)
async def upload_document(
    request: Request,
    filename: str | None = Query(default=None),
    workspace_id: str | None = Query(default=None),
) -> dict[str, Any]:
    repositories = RepositoryRegistry(request.app.state.database)
    workspace = _resolve_workspace(
        repositories=repositories,
        settings_data_dir=request.app.state.settings.data_dir,
        workspace_id=workspace_id,
    )
    upload = await _read_document_upload(request=request, filename=filename)
    stored_path = _stored_document_path(
        documents_dir=request.app.state.settings.documents_dir,
        workspace_id=workspace.id,
        filename=upload["filename"],
    )
    stored_path.parent.mkdir(parents=True, exist_ok=True)
    stored_path.write_bytes(upload["content"])

    document = repositories.documents.create(
        workspace_id=workspace.id,
        filename=upload["filename"],
        stored_path=stored_path,
        status=DocumentStatus.PENDING,
    )
    job = repositories.jobs.create(
        kind=JobKind.INGESTION,
        status=JobStatus.QUEUED,
        document_id=document.id,
        progress=0.0,
    )

    processor = _get_document_processor(request)
    if processor is not None:
        document, job = await _process_uploaded_document(
            processor=processor,
            document=document,
            job=job,
            repositories=repositories,
            settings=request.app.state.settings,
        )

    return {
        "workspace_id": workspace.id,
        "document": _document_payload(document),
        "job": _job_payload(job),
    }


@router.get("")
async def list_documents(
    request: Request,
    workspace_id: str | None = Query(default=None),
) -> dict[str, Any]:
    repositories = RepositoryRegistry(request.app.state.database)
    workspace = _resolve_workspace(
        repositories=repositories,
        settings_data_dir=request.app.state.settings.data_dir,
        workspace_id=workspace_id,
    )
    documents = repositories.documents.list_by_workspace(workspace.id)
    active_document_ids = repositories.documents.list_active_document_ids(workspace.id)

    return {
        "workspace_id": workspace.id,
        "documents": [_document_payload(document) for document in documents],
        "active_document_ids": active_document_ids,
    }


@router.get("/active")
async def list_active_documents(
    request: Request,
    workspace_id: str | None = Query(default=None),
) -> dict[str, Any]:
    repositories = RepositoryRegistry(request.app.state.database)
    workspace = _resolve_workspace(
        repositories=repositories,
        settings_data_dir=request.app.state.settings.data_dir,
        workspace_id=workspace_id,
    )
    active_documents = repositories.documents.list_active_documents(workspace.id)

    return {
        "workspace_id": workspace.id,
        "active_document_ids": [document.id for document in active_documents],
        "documents": [_document_payload(document) for document in active_documents],
    }


@router.put("/active")
async def set_active_documents(
    body: ActiveDocumentsRequest,
    request: Request,
) -> dict[str, Any]:
    repositories = RepositoryRegistry(request.app.state.database)
    workspace = _resolve_workspace(
        repositories=repositories,
        settings_data_dir=request.app.state.settings.data_dir,
        workspace_id=body.workspace_id,
    )
    document_ids = list(dict.fromkeys(body.document_ids))
    if not repositories.documents.all_exist_in_workspace(
        workspace_id=workspace.id,
        document_ids=document_ids,
    ):
        raise AppError(
            code=ErrorCode.INVALID_REQUEST,
            message="Active documents must belong to the selected workspace.",
            status_code=400,
            details={"workspace_id": workspace.id, "document_ids": document_ids},
        )

    active_document_ids = repositories.documents.set_active_document_ids(
        workspace_id=workspace.id,
        document_ids=document_ids,
    )
    active_documents = repositories.documents.list_active_documents(workspace.id)

    return {
        "workspace_id": workspace.id,
        "active_document_ids": active_document_ids,
        "documents": [_document_payload(document) for document in active_documents],
    }


@router.get("/{document_id}")
async def get_document(document_id: str, request: Request) -> dict[str, Any]:
    repositories = RepositoryRegistry(request.app.state.database)
    document = repositories.documents.get(document_id)
    if document is None:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message="Document was not found.",
            status_code=404,
            details={"document_id": document_id},
        )

    active_document_ids = repositories.documents.list_active_document_ids(document.workspace_id)
    return {
        "document": _document_payload(document),
        "active": document.id in active_document_ids,
    }


@router.delete("/{document_id}")
async def delete_document(document_id: str, request: Request) -> dict[str, Any]:
    repositories = RepositoryRegistry(request.app.state.database)
    document = repositories.documents.get(document_id)
    if document is None:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message="Document was not found.",
            status_code=404,
            details={"document_id": document_id},
        )

    deleted = repositories.documents.delete(document_id)
    if document.stored_path.exists():
        document.stored_path.unlink()

    return {"deleted": deleted, "document_id": document_id}


def _resolve_workspace(
    *,
    repositories: RepositoryRegistry,
    settings_data_dir: Path,
    workspace_id: str | None,
) -> Workspace:
    if workspace_id is None:
        return repositories.workspaces.get_or_create_default(root_path=settings_data_dir)

    workspace = repositories.workspaces.get(workspace_id)
    if workspace is None:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message="Workspace was not found.",
            status_code=404,
            details={"workspace_id": workspace_id},
        )
    return workspace


async def _read_document_upload(request: Request, filename: str | None) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        try:
            form = await request.form()
        except Exception as exc:
            raise AppError(
                code=ErrorCode.INVALID_REQUEST,
                message="Multipart uploads require a valid file field.",
                details={"error": str(exc)},
            ) from exc
        file_value = form.get("file")
        if file_value is None or not hasattr(file_value, "read"):
            raise AppError(
                code=ErrorCode.INVALID_REQUEST,
                message="Multipart uploads must include a file field.",
            )
        content = await file_value.read()
        upload_filename = filename or getattr(file_value, "filename", None)
    else:
        content = await request.body()
        upload_filename = filename or request.headers.get("x-filename")

    safe_filename = Path(upload_filename or "document.pdf").name
    if not safe_filename.lower().endswith(".pdf"):
        raise AppError(
            code=ErrorCode.INVALID_REQUEST,
            message="Only PDF documents are supported.",
            details={"filename": safe_filename},
        )
    if not content:
        raise AppError(
            code=ErrorCode.INVALID_REQUEST,
            message="Uploaded document is empty.",
        )

    return {"filename": safe_filename, "content": content}


def _stored_document_path(*, documents_dir: Path, workspace_id: str, filename: str) -> Path:
    suffix = Path(filename).suffix or ".pdf"
    stem = Path(filename).stem[:80] or "document"
    return documents_dir / workspace_id / f"{stem}-{uuid.uuid4().hex}{suffix.lower()}"


def _get_document_processor(request: Request) -> Any | None:
    state_processor = getattr(request.app.state, "document_processor", None)
    if state_processor is not None:
        return state_processor

    try:
        module = importlib.import_module("app.ingestion.document_processor")
    except ModuleNotFoundError as exc:
        if exc.name != "app.ingestion.document_processor":
            raise
        return None

    process_document = getattr(module, "process_document", None)
    if process_document is not None:
        return process_document

    processor_cls = getattr(module, "DocumentProcessor", None)
    if processor_cls is None:
        return None

    def default_processor(
        *,
        document: Document,
        repositories: RepositoryRegistry,
        settings: Any,
    ) -> dict[str, Any]:
        processor = processor_cls(
            segment_repository=repositories.source_segments,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        result = processor.process(
            document_id=document.id,
            pdf_path=document.stored_path,
            source_label=document.filename,
        )
        return {
            "title": document.title,
            "authors": list(document.authors),
            "year": document.year,
            "page_count": result.page_count,
        }

    return default_processor


async def _process_uploaded_document(
    *,
    processor: Any,
    document: Document,
    job: Job,
    repositories: RepositoryRegistry,
    settings: Any,
) -> tuple[Document, Job]:
    running_document = repositories.documents.update(
        document.id,
        status=DocumentStatus.PROCESSING,
        failure_reason=None,
    )
    running_job = repositories.jobs.update(job.id, status=JobStatus.RUNNING, progress=0.1)
    document = running_document or document
    job = running_job or job

    try:
        result = _call_processor(
            processor=processor,
            document=document,
            repositories=repositories,
            settings=settings,
        )
        if inspect.isawaitable(result):
            result = await result
    except Exception as exc:
        failed_document = repositories.documents.update(
            document.id,
            status=DocumentStatus.FAILED,
            failure_reason=str(exc),
        )
        failed_job = repositories.jobs.update(
            job.id,
            status=JobStatus.FAILED,
            progress=1.0,
            error=str(exc),
        )
        return failed_document or document, failed_job or job

    metadata = result if isinstance(result, dict) else {}
    updated_document = repositories.documents.update(
        document.id,
        status=DocumentStatus.READY,
        title=_optional_str(metadata.get("title")),
        authors=tuple(str(author) for author in metadata.get("authors", ())),
        year=_optional_int(metadata.get("year")),
        page_count=_optional_int(metadata.get("page_count")),
        failure_reason=None,
    )
    updated_job = repositories.jobs.update(job.id, status=JobStatus.SUCCEEDED, progress=1.0)
    return updated_document or document, updated_job or job


def _call_processor(
    *,
    processor: Any,
    document: Document,
    repositories: RepositoryRegistry,
    settings: Any,
) -> Any:
    target = getattr(processor, "process_document", None) or getattr(processor, "process", None)
    if target is None and callable(processor):
        target = processor
    if target is None:
        raise TypeError("Document processor must be callable or expose process_document/process.")

    try:
        return target(document=document, repositories=repositories, settings=settings)
    except TypeError:
        return target(document, repositories, settings)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _document_payload(document: Document) -> dict[str, Any]:
    return {
        "id": document.id,
        "workspace_id": document.workspace_id,
        "filename": document.filename,
        "stored_path": str(document.stored_path),
        "status": document.status.value,
        "fingerprint": document.fingerprint,
        "title": document.title,
        "authors": list(document.authors),
        "year": document.year,
        "page_count": document.page_count,
        "failure_reason": document.failure_reason,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat(),
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
