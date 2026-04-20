from pathlib import Path

from app.common.types import ExtractionMethod
from app.ingestion.document_processor import DocumentProcessor
from app.ingestion.pdf_extractor import ExtractedPage, PdfExtractionResult


class FakeExtractor:
    def extract(self, pdf_path: Path) -> PdfExtractionResult:
        return PdfExtractionResult(
            pages=[
                ExtractedPage(
                    page_number=1,
                    text="Motivation improves persistence in learning tasks.",
                    extraction_method=ExtractionMethod.TEXT,
                ),
                ExtractedPage(
                    page_number=2,
                    text="Feedback supports self regulation during exam preparation.",
                    extraction_method=ExtractionMethod.TEXT,
                ),
            ],
            page_count=2,
            extraction_method=ExtractionMethod.TEXT,
        )


class InMemorySegmentRepository:
    def __init__(self) -> None:
        self.created: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> object:
        self.created.append(kwargs)
        return kwargs


def test_document_processor_ingests_readable_pdf(tmp_path: Path) -> None:
    segment_repository = InMemorySegmentRepository()
    processor = DocumentProcessor(
        pdf_extractor=FakeExtractor(),
        segment_repository=segment_repository,
        chunk_size=80,
        chunk_overlap=15,
    )

    result = processor.process(
        document_id="document_1",
        pdf_path=tmp_path / "paper.pdf",
        source_label="paper.pdf",
    )

    assert result.page_count == 2
    assert result.extraction_method is ExtractionMethod.TEXT
    assert result.chunk_count >= 1
    assert len(result.embeddings) == result.chunk_count
    assert segment_repository.created[0]["document_id"] == "document_1"
    assert segment_repository.created[0]["page_start"] == 1
    assert "Motivation improves persistence" in segment_repository.created[0]["text"]


def test_document_processor_can_run_without_persistence(tmp_path: Path) -> None:
    processor = DocumentProcessor(
        pdf_extractor=FakeExtractor(),
        segment_repository=None,
        chunk_size=200,
        chunk_overlap=20,
    )

    result = processor.process(
        document_id="document_1",
        pdf_path=tmp_path / "paper.pdf",
        source_label="paper.pdf",
    )

    assert result.persisted_segments == []
    assert result.chunks[0].metadata["document_id"] == "document_1"
