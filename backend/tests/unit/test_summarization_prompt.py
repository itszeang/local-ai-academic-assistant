from app.common.types import GenerationMode
from app.llm.prompt_manager import PromptManager

from tests.helpers import make_source_segment


def test_summarization_prompt_requires_mode_specific_sections() -> None:
    prompt = PromptManager().build_prompt(
        mode=GenerationMode.SUMMARIZATION,
        query="Summarize the active documents.",
        context=[make_source_segment()],
    )

    assert "Overview" in prompt
    assert "Main Findings" in prompt
    assert "Key Concepts" in prompt
    assert "Limitations" in prompt
    assert "References" in prompt
