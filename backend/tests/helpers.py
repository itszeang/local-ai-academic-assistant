from app.common.types import ExtractionMethod, RetrievalResult, SourceSegment, utc_now


def make_source_segment(
    *,
    text: str = "Motivation improves persistence in learning tasks.",
) -> SourceSegment:
    return SourceSegment(
        id="seg_1",
        document_id="doc_1",
        chunk_index=0,
        text=text,
        page_start=5,
        page_end=None,
        source_label="motivation.pdf",
        extraction_method=ExtractionMethod.TEXT,
        metadata={"authors": ["Aksoy"], "year": 2024},
        created_at=utc_now(),
    )


def make_retrieval_result(
    *,
    text: str = "Motivation improves persistence in learning tasks.",
) -> RetrievalResult:
    return RetrievalResult(
        source_segment=make_source_segment(text=text),
        score=1.0,
        rank=1,
        rerank_score=1.0,
    )
