from app.storage.repositories import CitationRepository


def test_citation_source_validation_rejects_unretrieved_segment() -> None:
    assert CitationRepository.is_retrieved_source(
        source_segment_id="seg_missing",
        allowed_source_segment_ids={"seg_1"},
    ) is False


def test_citation_source_validation_accepts_retrieved_segment() -> None:
    assert CitationRepository.is_retrieved_source(
        source_segment_id="seg_1",
        allowed_source_segment_ids={"seg_1"},
    ) is True
