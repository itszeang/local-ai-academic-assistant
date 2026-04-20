from app.common.types import GenerationMode, Language, SourceSegment, ExtractionMethod, utc_now
from app.llm.prompt_manager import PromptManager


def test_prompt_contains_grounding_and_no_external_knowledge_rule() -> None:
    prompt = PromptManager().build_prompt(
        mode=GenerationMode.QA,
        query="What does the source say?",
        context=[
            SourceSegment(
                id="seg_1",
                document_id="doc_1",
                chunk_index=0,
                text="The study reports a clear finding.",
                page_start=3,
                page_end=None,
                source_label="paper.pdf",
                extraction_method=ExtractionMethod.TEXT,
                metadata={},
                created_at=utc_now(),
            )
        ],
        language=Language.ENGLISH,
    )

    assert "Use only the provided document context" in prompt
    assert "Bilgi bulunamadı" in prompt
    assert "Do not use outside knowledge" in prompt
    assert "[S1] paper.pdf p.3" in prompt
