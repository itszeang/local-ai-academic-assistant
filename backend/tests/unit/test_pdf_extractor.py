from pathlib import Path

import pytest

from app.common.errors import AppError, ErrorCode
from app.common.types import ExtractionMethod
from app.ingestion.pdf_extractor import PdfTextExtractor


class FakePage:
    def __init__(self, text: str | None) -> None:
        self.text = text

    def extract_text(self) -> str | None:
        return self.text


class FakePdf:
    def __init__(self, pages: list[FakePage]) -> None:
        self.pages = pages

    def __enter__(self) -> "FakePdf":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


class FakeOCRService:
    def __init__(self, text: str) -> None:
        self.text = text
        self.calls: list[int] = []

    def should_ocr_page(self, text: str) -> bool:
        return len(text.strip()) < 8

    def extract_page_text(self, page: object, page_number: int) -> str:
        self.calls.append(page_number)
        return self.text


def test_pdf_text_extractor_returns_page_metadata(tmp_path: Path) -> None:
    extractor = PdfTextExtractor(
        open_pdf=lambda path: FakePdf(
            [
                FakePage("First page text."),
                FakePage("Second page text."),
            ]
        )
    )

    result = extractor.extract(tmp_path / "paper.pdf")

    assert result.page_count == 2
    assert [page.page_number for page in result.pages] == [1, 2]
    assert [page.text for page in result.pages] == ["First page text.", "Second page text."]
    assert result.extraction_method is ExtractionMethod.TEXT


def test_pdf_text_extractor_uses_ocr_for_empty_pages(tmp_path: Path) -> None:
    ocr_service = FakeOCRService("Recognized scanned text.")
    extractor = PdfTextExtractor(
        open_pdf=lambda path: FakePdf([FakePage(""), FakePage("Readable text.")]),
        ocr_service=ocr_service,
    )

    result = extractor.extract(tmp_path / "scan.pdf")

    assert ocr_service.calls == [1]
    assert result.pages[0].text == "Recognized scanned text."
    assert result.pages[0].extraction_method is ExtractionMethod.OCR
    assert result.extraction_method is ExtractionMethod.MIXED


def test_pdf_text_extractor_raises_structured_error_for_corrupted_pdf(tmp_path: Path) -> None:
    def fail_open(path: Path) -> FakePdf:
        raise RuntimeError("not a pdf")

    extractor = PdfTextExtractor(open_pdf=fail_open)

    with pytest.raises(AppError) as error:
        extractor.extract(tmp_path / "corrupted.pdf")

    assert error.value.code is ErrorCode.INGESTION_FAILED
    assert error.value.details["filename"] == "corrupted.pdf"
