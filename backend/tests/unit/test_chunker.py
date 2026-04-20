from app.common.types import ExtractionMethod
from app.ingestion.chunker import Chunker, ChunkerPage
from app.ingestion.cleaner import clean_text


def test_clean_text_normalizes_pdf_artifacts() -> None:
    raw = "This is hyphen-\nated text.\r\n\r\n  Extra\tspaces."

    assert clean_text(raw) == "This is hyphenated text.\n\nExtra spaces."


def test_chunker_preserves_page_metadata_and_overlap() -> None:
    pages = [
        ChunkerPage(
            page_number=1,
            text="Alpha beta gamma delta. Epsilon zeta eta theta.",
            extraction_method=ExtractionMethod.TEXT,
        ),
        ChunkerPage(
            page_number=2,
            text="Iota kappa lambda mu. Nu xi omicron pi.",
            extraction_method=ExtractionMethod.OCR,
        ),
    ]
    chunker = Chunker(chunk_size=55, chunk_overlap=10)

    chunks = chunker.chunk_pages(
        pages,
        document_id="document_1",
        source_label="paper.pdf",
    )

    assert len(chunks) >= 2
    assert chunks[0].chunk_index == 0
    assert chunks[0].page_start == 1
    assert chunks[-1].page_end == 2
    assert chunks[-1].metadata["source"] == "paper.pdf"
    assert chunks[-1].metadata["document_id"] == "document_1"
    assert {chunk.extraction_method for chunk in chunks} == {ExtractionMethod.TEXT, ExtractionMethod.MIXED}


def test_chunker_rejects_invalid_overlap() -> None:
    try:
        Chunker(chunk_size=100, chunk_overlap=100)
    except ValueError as error:
        assert "chunk_overlap" in str(error)
    else:
        raise AssertionError("Expected invalid overlap to raise")
