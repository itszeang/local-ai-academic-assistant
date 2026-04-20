from app.common.types import (
    ExtractionMethod,
    GenerationMode,
    Language,
    MISSING_INFORMATION_RESPONSE,
    RetrievalResult,
    SourceSegment,
    utc_now,
)
from app.llm.generator import GroundedGenerator


class FakeLlmClient:
    async def generate(self, *, model: str, prompt: str) -> str:
        assert "Document Context" in prompt
        return "The document states that motivation improves persistence."


def make_result() -> RetrievalResult:
    segment = SourceSegment(
        id="seg_1",
        document_id="doc_1",
        chunk_index=0,
        text="Motivation improves persistence in learning tasks.",
        page_start=5,
        page_end=None,
        source_label="motivation.pdf",
        extraction_method=ExtractionMethod.TEXT,
        metadata={"authors": ["Aksoy"], "year": 2024},
        created_at=utc_now(),
    )
    return RetrievalResult(source_segment=segment, score=1.0, rank=1, rerank_score=1.0)


async def test_generator_returns_exact_fallback_without_context() -> None:
    answer = await GroundedGenerator().generate(
        mode=GenerationMode.QA,
        query="What is motivation?",
        retrieval_results=[],
        language=Language.ENGLISH,
    )

    assert answer.fallback_used is True
    assert answer.title == MISSING_INFORMATION_RESPONSE
    assert answer.sections[0].blocks == [MISSING_INFORMATION_RESPONSE]
    assert answer.references == []
    assert answer.citations == []


async def test_generator_uses_context_and_creates_citation() -> None:
    answer = await GroundedGenerator(llm_client=FakeLlmClient(), generator_model="test").generate(
        mode=GenerationMode.QA,
        query="What improves persistence?",
        retrieval_results=[make_result()],
        language=Language.ENGLISH,
    )

    assert answer.fallback_used is False
    assert answer.references == ["motivation.pdf, p. 5"]
    assert answer.citations[0].source_segment_id == "seg_1"
    assert "(Aksoy, 2024)" in answer.sections[0].blocks[0]
