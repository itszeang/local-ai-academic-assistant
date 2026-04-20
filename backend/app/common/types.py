"""Shared domain types used across the local academic assistant backend."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any


MISSING_INFORMATION_RESPONSE = "Bilgi bulunamadı"


class DocumentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class JobKind(StrEnum):
    INGESTION = "ingestion"
    GENERATION = "generation"
    EXPORT = "export"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class GenerationMode(StrEnum):
    QA = "qa"
    SUMMARIZATION = "summarization"
    ARGUMENT_BUILDER = "argument_builder"
    LITERATURE_REVIEW = "literature_review"


class Language(StrEnum):
    AUTO = "auto"
    TURKISH = "tr"
    ENGLISH = "en"


class ExtractionMethod(StrEnum):
    TEXT = "text"
    OCR = "ocr"
    MIXED = "mixed"


@dataclass(frozen=True, slots=True)
class OutputSection:
    heading: str
    blocks: list[str]


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    source_segment: SourceSegment
    score: float
    rank: int
    bm25_score: float = 0.0
    vector_score: float = 0.0
    rerank_score: float = 0.0


@dataclass(frozen=True, slots=True)
class GeneratedAnswer:
    title: str
    sections: list[OutputSection]
    references: list[str]
    citations: list[Citation]
    fallback_used: bool


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class Workspace:
    id: str
    name: str
    root_path: Path
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class Document:
    id: str
    workspace_id: str
    filename: str
    stored_path: Path
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime
    fingerprint: str | None = None
    title: str | None = None
    authors: tuple[str, ...] = ()
    year: int | None = None
    page_count: int | None = None
    failure_reason: str | None = None


@dataclass(frozen=True, slots=True)
class Job:
    id: str
    kind: JobKind
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    document_id: str | None = None
    output_id: str | None = None
    progress: float | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class SourceSegment:
    id: str
    document_id: str
    chunk_index: int
    text: str
    page_start: int
    page_end: int | None
    source_label: str
    extraction_method: ExtractionMethod
    metadata: dict[str, Any]
    created_at: datetime


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    query: str
    mode: GenerationMode
    active_document_ids: tuple[str, ...]
    language: Language = Language.AUTO
    top_k: int = 8


@dataclass(frozen=True, slots=True)
class AcademicOutput:
    id: str
    generation_request_id: str
    mode: GenerationMode
    title: str
    sections: list[dict[str, Any]]
    references: list[str]
    fallback_used: bool
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Citation:
    id: str
    academic_output_id: str
    source_segment_id: str
    claim_path: str
    inline_text: str
    page_start: int
    page_end: int | None
    source_snippet: str


@dataclass(frozen=True, slots=True)
class ExportFile:
    id: str
    academic_output_id: str
    format: str
    path: Path
    status: JobStatus
    created_at: datetime
    error_message: str | None = None
