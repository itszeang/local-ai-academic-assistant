from app.common.types import GenerationMode, MISSING_INFORMATION_RESPONSE
from app.llm.prompt_manager import PromptManager

from tests.helpers import make_source_segment


def test_argument_prompt_requires_argument_sections_and_missing_fallback() -> None:
    prompt = PromptManager().build_prompt(
        mode=GenerationMode.ARGUMENT_BUILDER,
        query="Build an argument for persistence.",
        context=[make_source_segment()],
    )

    assert "Thesis/Position" in prompt
    assert "Supporting Arguments" in prompt
    assert "Counterarguments" in prompt
    assert "Evidence Map" in prompt
    assert MISSING_INFORMATION_RESPONSE in prompt
