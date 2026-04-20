"""Document ingestion orchestration for local PDF processing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from app.common.errors import AppError, ErrorCode
from app.common.types import ExtractionMethod
from app.ingestion.chunker import Chunker, ChunkerPage, TextChunk
from app.ingestion.embedding_service import EmbeddingService
from app.ingestion.ocr_service import OCRService
from app.ingestion.pdf_extractor import PdfExtractionResult, PdfTextExtractor


class PdfExtractor(Protocol):
    def extract(self, pdf_path: Path) -> PdfExtractionResult:
        ...


class SegmentRepository(Protocol):
    def create(self, **kwargs: Any) -> object:
        ...


@dataclass(frozen=True, slots=True)
class DocumentIngestionResult:
    document_id: str
    source_label: str
    page_count: int
    extraction_method: ExtractionMethod
    chunks: list[TextChunk]
    embeddings: list[list[float]]
    persisted_segments: list[object]

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)


class DocumentProcessor:
    def __init__(
        self,
        *,
        pdf_extractor: PdfExtractor | None = None,
        segment_repository: SegmentRepository | None = None,
        embedding_service: EmbeddingService | None = None,
        chunk_size: int = 1100,
        chunk_overlap: int = 200,
    ) -> None:
        self.pdf_extractor = pdf_extractor or PdfTextExtractor(ocr_service=OCRService())
        self.segment_repository = segment_repository
        self.embedding_service = embedding_service or EmbeddingService()
        self.chunker = Chunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def process(
        self,
        *,
        document_id: str,
        pdf_path: Path,
        source_label: str | None = None,
    ) -> DocumentIngestionResult:
        label = source_label or Path(pdf_path).name
        try:
            extraction = self.pdf_extractor.extract(Path(pdf_path))
            chunks = self.chunker.chunk_pages(
                [
                    ChunkerPage(
                        page_number=page.page_number,
                        text=page.text,
                        extraction_method=page.extraction_method,
                    )
                    for page in extraction.pages
                ],
                document_id=document_id,
                source_label=label,
            )
            embeddings = self.embedding_service.embed_texts([chunk.text for chunk in chunks])
            persisted_segments = self._persist_chunks(document_id=document_id, chunks=chunks)
        except AppError:
            raise
        except Exception as exc:
            raise AppError(
                code=ErrorCode.INGESTION_FAILED,
                message="Document ingestion failed.",
                status_code=422,
                details={"filename": Path(pdf_path).name, "reason": str(exc)},
            ) from exc

        return DocumentIngestionResult(
            document_id=document_id,
            source_label=label,
            page_count=extraction.page_count,
            extraction_method=extraction.extraction_method,
            chunks=chunks,
            embeddings=embeddings,
            persisted_segments=persisted_segments,
        )

    def _persist_chunks(self, *, document_id: str, chunks: list[TextChunk]) -> list[object]:
        if self.segment_repository is None:
            return []

        persisted: list[object] = []
        for chunk in chunks:
            persisted.append(
                self.segment_repository.create(
                    document_id=document_id,
                    chunk_index=chunk.chunk_index,
                    text=chunk.text,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    source_label=chunk.source_label,
                    extraction_method=chunk.extraction_method,
                    metadata=chunk.metadata,
                )
            )
        return persisted
