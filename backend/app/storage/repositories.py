"""Repository interfaces for local metadata persistence."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from app.common.types import (
    AcademicOutput,
    Citation,
    Document,
    DocumentStatus,
    ExportFile,
    ExtractionMethod,
    GenerationMode,
    Job,
    JobKind,
    JobStatus,
    SourceSegment,
    Workspace,
    utc_now,
)
from app.storage.sqlite import SQLiteDatabase


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def _serialize_dt(value: datetime) -> str:
    return value.isoformat()


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


class WorkspaceRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def create(self, *, name: str, root_path: Path) -> Workspace:
        now = utc_now()
        workspace = Workspace(
            id=_new_id("workspace"),
            name=name,
            root_path=Path(root_path),
            created_at=now,
            updated_at=now,
        )
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO workspaces (id, name, root_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    workspace.id,
                    workspace.name,
                    str(workspace.root_path),
                    _serialize_dt(workspace.created_at),
                    _serialize_dt(workspace.updated_at),
                ),
            )
        return workspace

    def get(self, workspace_id: str) -> Workspace | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT id, name, root_path, created_at, updated_at FROM workspaces WHERE id = ?",
                (workspace_id,),
            ).fetchone()

        if row is None:
            return None

        return Workspace(
            id=str(row["id"]),
            name=str(row["name"]),
            root_path=Path(str(row["root_path"])),
            created_at=_parse_dt(str(row["created_at"])),
            updated_at=_parse_dt(str(row["updated_at"])),
        )


class DocumentRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def create(
        self,
        *,
        workspace_id: str,
        filename: str,
        stored_path: Path,
        status: DocumentStatus = DocumentStatus.PENDING,
        fingerprint: str | None = None,
        title: str | None = None,
        authors: tuple[str, ...] = (),
        year: int | None = None,
        page_count: int | None = None,
        failure_reason: str | None = None,
    ) -> Document:
        now = utc_now()
        document = Document(
            id=_new_id("document"),
            workspace_id=workspace_id,
            filename=filename,
            stored_path=Path(stored_path),
            status=status,
            fingerprint=fingerprint,
            title=title,
            authors=authors,
            year=year,
            page_count=page_count,
            failure_reason=failure_reason,
            created_at=now,
            updated_at=now,
        )
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    id, workspace_id, filename, stored_path, fingerprint, title, authors_json,
                    year, page_count, status, failure_reason, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document.id,
                    document.workspace_id,
                    document.filename,
                    str(document.stored_path),
                    document.fingerprint,
                    document.title,
                    json.dumps(list(document.authors)),
                    document.year,
                    document.page_count,
                    document.status.value,
                    document.failure_reason,
                    _serialize_dt(document.created_at),
                    _serialize_dt(document.updated_at),
                ),
            )
        return document

    def get(self, document_id: str) -> Document | None:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
        if row is None:
            return None
        return Document(
            id=str(row["id"]),
            workspace_id=str(row["workspace_id"]),
            filename=str(row["filename"]),
            stored_path=Path(str(row["stored_path"])),
            fingerprint=None if row["fingerprint"] is None else str(row["fingerprint"]),
            title=None if row["title"] is None else str(row["title"]),
            authors=tuple(json.loads(str(row["authors_json"]))),
            year=None if row["year"] is None else int(row["year"]),
            page_count=None if row["page_count"] is None else int(row["page_count"]),
            status=DocumentStatus(str(row["status"])),
            failure_reason=None if row["failure_reason"] is None else str(row["failure_reason"]),
            created_at=_parse_dt(str(row["created_at"])),
            updated_at=_parse_dt(str(row["updated_at"])),
        )


class JobRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def create(
        self,
        *,
        kind: JobKind,
        status: JobStatus = JobStatus.QUEUED,
        document_id: str | None = None,
        output_id: str | None = None,
        progress: float | None = None,
        error: str | None = None,
    ) -> Job:
        now = utc_now()
        job = Job(
            id=_new_id("job"),
            kind=kind,
            status=status,
            document_id=document_id,
            output_id=output_id,
            progress=progress,
            error=error,
            created_at=now,
            updated_at=now,
        )
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO jobs (
                    id, kind, status, document_id, output_id, progress, error, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.id,
                    job.kind.value,
                    job.status.value,
                    job.document_id,
                    job.output_id,
                    job.progress,
                    job.error,
                    _serialize_dt(job.created_at),
                    _serialize_dt(job.updated_at),
                ),
            )
        return job

    def get(self, job_id: str) -> Job | None:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        return Job(
            id=str(row["id"]),
            kind=JobKind(str(row["kind"])),
            status=JobStatus(str(row["status"])),
            document_id=None if row["document_id"] is None else str(row["document_id"]),
            output_id=None if row["output_id"] is None else str(row["output_id"]),
            progress=None if row["progress"] is None else float(row["progress"]),
            error=None if row["error"] is None else str(row["error"]),
            created_at=_parse_dt(str(row["created_at"])),
            updated_at=_parse_dt(str(row["updated_at"])),
        )


class SourceSegmentRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def create(
        self,
        *,
        document_id: str,
        chunk_index: int,
        text: str,
        page_start: int,
        source_label: str,
        extraction_method: ExtractionMethod,
        page_end: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SourceSegment:
        segment = SourceSegment(
            id=_new_id("segment"),
            document_id=document_id,
            chunk_index=chunk_index,
            text=text,
            page_start=page_start,
            page_end=page_end,
            source_label=source_label,
            extraction_method=extraction_method,
            metadata=metadata or {},
            created_at=utc_now(),
        )
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO source_segments (
                    id, document_id, chunk_index, text, page_start, page_end, source_label,
                    extraction_method, metadata_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    segment.id,
                    segment.document_id,
                    segment.chunk_index,
                    segment.text,
                    segment.page_start,
                    segment.page_end,
                    segment.source_label,
                    segment.extraction_method.value,
                    json.dumps(segment.metadata),
                    _serialize_dt(segment.created_at),
                ),
            )
        return segment

    def get(self, segment_id: str) -> SourceSegment | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM source_segments WHERE id = ?", (segment_id,)
            ).fetchone()
        if row is None:
            return None
        return SourceSegment(
            id=str(row["id"]),
            document_id=str(row["document_id"]),
            chunk_index=int(row["chunk_index"]),
            text=str(row["text"]),
            page_start=int(row["page_start"]),
            page_end=None if row["page_end"] is None else int(row["page_end"]),
            source_label=str(row["source_label"]),
            extraction_method=ExtractionMethod(str(row["extraction_method"])),
            metadata=json.loads(str(row["metadata_json"])),
            created_at=_parse_dt(str(row["created_at"])),
        )

    def list_by_document_ids(self, document_ids: list[str]) -> list[SourceSegment]:
        if not document_ids:
            return []

        placeholders = ",".join("?" for _ in document_ids)
        with self.database.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM source_segments
                WHERE document_id IN ({placeholders})
                ORDER BY document_id, chunk_index
                """,
                tuple(document_ids),
            ).fetchall()

        return [
            SourceSegment(
                id=str(row["id"]),
                document_id=str(row["document_id"]),
                chunk_index=int(row["chunk_index"]),
                text=str(row["text"]),
                page_start=int(row["page_start"]),
                page_end=None if row["page_end"] is None else int(row["page_end"]),
                source_label=str(row["source_label"]),
                extraction_method=ExtractionMethod(str(row["extraction_method"])),
                metadata=json.loads(str(row["metadata_json"])),
                created_at=_parse_dt(str(row["created_at"])),
            )
            for row in rows
        ]


class AcademicOutputRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def create(
        self,
        *,
        generation_request_id: str,
        mode: GenerationMode,
        title: str,
        sections: list[dict[str, Any]],
        references: list[str],
        fallback_used: bool,
    ) -> AcademicOutput:
        output = AcademicOutput(
            id=_new_id("output"),
            generation_request_id=generation_request_id,
            mode=mode,
            title=title,
            sections=sections,
            references=references,
            fallback_used=fallback_used,
            created_at=utc_now(),
        )
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO academic_outputs (
                    id, generation_request_id, mode, title, sections_json, references_json,
                    fallback_used, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    output.id,
                    output.generation_request_id,
                    output.mode.value,
                    output.title,
                    json.dumps(output.sections),
                    json.dumps(output.references),
                    int(output.fallback_used),
                    _serialize_dt(output.created_at),
                ),
            )
        return output

    def get(self, output_id: str) -> AcademicOutput | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM academic_outputs WHERE id = ?", (output_id,)
            ).fetchone()
        if row is None:
            return None
        return AcademicOutput(
            id=str(row["id"]),
            generation_request_id=str(row["generation_request_id"]),
            mode=GenerationMode(str(row["mode"])),
            title=str(row["title"]),
            sections=json.loads(str(row["sections_json"])),
            references=json.loads(str(row["references_json"])),
            fallback_used=bool(row["fallback_used"]),
            created_at=_parse_dt(str(row["created_at"])),
        )


class CitationRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def create(
        self,
        *,
        academic_output_id: str,
        source_segment_id: str,
        claim_path: str,
        inline_text: str,
        page_start: int,
        source_snippet: str,
        page_end: int | None = None,
    ) -> Citation:
        citation = Citation(
            id=_new_id("citation"),
            academic_output_id=academic_output_id,
            source_segment_id=source_segment_id,
            claim_path=claim_path,
            inline_text=inline_text,
            page_start=page_start,
            page_end=page_end,
            source_snippet=source_snippet,
        )
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO citations (
                    id, academic_output_id, source_segment_id, claim_path, inline_text,
                    source_snippet, page_start, page_end
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    citation.id,
                    citation.academic_output_id,
                    citation.source_segment_id,
                    citation.claim_path,
                    citation.inline_text,
                    citation.source_snippet,
                    citation.page_start,
                    citation.page_end,
                ),
            )
        return citation

    @staticmethod
    def is_retrieved_source(
        *,
        source_segment_id: str,
        allowed_source_segment_ids: set[str],
    ) -> bool:
        return source_segment_id in allowed_source_segment_ids

    def create_for_retrieved_source(
        self,
        *,
        allowed_source_segment_ids: set[str],
        academic_output_id: str,
        source_segment_id: str,
        claim_path: str,
        inline_text: str,
        page_start: int,
        source_snippet: str,
        page_end: int | None = None,
    ) -> Citation:
        if not self.is_retrieved_source(
            source_segment_id=source_segment_id,
            allowed_source_segment_ids=allowed_source_segment_ids,
        ):
            raise ValueError("Citation source must come from retrieved context.")
        return self.create(
            academic_output_id=academic_output_id,
            source_segment_id=source_segment_id,
            claim_path=claim_path,
            inline_text=inline_text,
            page_start=page_start,
            source_snippet=source_snippet,
            page_end=page_end,
        )


class ExportFileRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def create(
        self,
        *,
        academic_output_id: str,
        path: Path,
        status: JobStatus,
        format: str = "docx",
        error_message: str | None = None,
    ) -> ExportFile:
        export_file = ExportFile(
            id=_new_id("export"),
            academic_output_id=academic_output_id,
            format=format,
            path=Path(path),
            status=status,
            error_message=error_message,
            created_at=utc_now(),
        )
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO export_files (
                    id, academic_output_id, format, path, status, error_message, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    export_file.id,
                    export_file.academic_output_id,
                    export_file.format,
                    str(export_file.path),
                    export_file.status.value,
                    export_file.error_message,
                    _serialize_dt(export_file.created_at),
                ),
            )
        return export_file


class RepositoryRegistry:
    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        self.workspaces = WorkspaceRepository(database)
        self.documents = DocumentRepository(database)
        self.jobs = JobRepository(database)
        self.source_segments = SourceSegmentRepository(database)
        self.academic_outputs = AcademicOutputRepository(database)
        self.citations = CitationRepository(database)
        self.export_files = ExportFileRepository(database)
