"""PDF text extraction with page metadata and OCR fallback support."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.common.errors import AppError, ErrorCode
from app.common.types import ExtractionMethod
from app.ingestion.ocr_service import OCRService


class PdfPage(Protocol):
    def extract_text(self) -> str | None:
        ...


class PdfDocument(Protocol):
    pages: list[PdfPage]


OpenPdf = Callable[[Path], AbstractContextManager[PdfDocument]]


@dataclass(frozen=True, slots=True)
class ExtractedPage:
    page_number: int
    text: str
    extraction_method: ExtractionMethod


@dataclass(frozen=True, slots=True)
class PdfExtractionResult:
    pages: list[ExtractedPage]
    page_count: int
    extraction_method: ExtractionMethod


def _default_open_pdf(path: Path) -> AbstractContextManager[PdfDocument]:
    import pdfplumber

    return pdfplumber.open(path)


class PdfTextExtractor:
    def __init__(
        self,
        *,
        open_pdf: OpenPdf | None = None,
        ocr_service: OCRService | None = None,
    ) -> None:
        self.open_pdf = open_pdf or _default_open_pdf
        self.ocr_service = ocr_service

    def extract(self, pdf_path: Path) -> PdfExtractionResult:
        path = Path(pdf_path)
        try:
            with self.open_pdf(path) as pdf:
                pages = [self._extract_page(page, index + 1) for index, page in enumerate(pdf.pages)]
        except AppError:
            raise
        except Exception as exc:
            raise AppError(
                code=ErrorCode.INGESTION_FAILED,
                message="PDF could not be read.",
                status_code=422,
                details={"filename": path.name, "reason": str(exc)},
            ) from exc

        return PdfExtractionResult(
            pages=pages,
            page_count=len(pages),
            extraction_method=self._document_extraction_method(pages),
        )

    def _extract_page(self, page: PdfPage, page_number: int) -> ExtractedPage:
        text = (page.extract_text() or "").strip()
        method = ExtractionMethod.TEXT
        if self.ocr_service is not None and self.ocr_service.should_ocr_page(text):
            ocr_text = self.ocr_service.extract_page_text(page, page_number=page_number)
            if ocr_text.strip():
                text = ocr_text.strip()
                method = ExtractionMethod.OCR
        return ExtractedPage(page_number=page_number, text=text, extraction_method=method)

    @staticmethod
    def _document_extraction_method(pages: list[ExtractedPage]) -> ExtractionMethod:
        methods = {page.extraction_method for page in pages if page.text.strip()}
        if not methods:
            return ExtractionMethod.TEXT
        if methods == {ExtractionMethod.TEXT}:
            return ExtractionMethod.TEXT
        if methods == {ExtractionMethod.OCR}:
            return ExtractionMethod.OCR
        return ExtractionMethod.MIXED
