from app.common.types import GenerationMode
from app.llm.prompt_manager import PromptManager

from tests.helpers import make_source_segment


def test_literature_review_prompt_requires_synthesis_sections() -> None:
    prompt = PromptManager().build_prompt(
        mode=GenerationMode.LITERATURE_REVIEW,
        query="Write a literature review about motivation.",
        context=[make_source_segment()],
    )

    assert "Themes" in prompt
    assert "Source Synthesis" in prompt
    assert "Agreements/Disagreements" in prompt
    assert "Gaps or Limitations" in prompt
    assert "source synthesis" in prompt.lower()
