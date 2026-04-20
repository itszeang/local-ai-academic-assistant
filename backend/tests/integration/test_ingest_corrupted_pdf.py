from pathlib import Path

import pytest

from app.common.errors import AppError, ErrorCode
from app.ingestion.document_processor import DocumentProcessor


class CorruptedExtractor:
    def extract(self, pdf_path: Path) -> object:
        raise AppError(
            code=ErrorCode.INGESTION_FAILED,
            message="PDF could not be read.",
            status_code=422,
            details={"filename": pdf_path.name},
        )


def test_document_processor_preserves_corrupted_pdf_structured_error(tmp_path: Path) -> None:
    processor = DocumentProcessor(pdf_extractor=CorruptedExtractor())

    with pytest.raises(AppError) as error:
        processor.process(
            document_id="document_1",
            pdf_path=tmp_path / "broken.pdf",
            source_label="broken.pdf",
        )

    assert error.value.code is ErrorCode.INGESTION_FAILED
    assert error.value.status_code == 422
    assert error.value.details["filename"] == "broken.pdf"
