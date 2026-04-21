from app.common.types import GenerationMode
from app.llm.generator import GroundedGenerator

from tests.helpers import make_retrieval_result


async def test_all_generation_modes_return_mode_specific_sections() -> None:
    generator = GroundedGenerator()
    result = make_retrieval_result()

    expected_first_heading = {
        GenerationMode.QA: "Answer",
        GenerationMode.SUMMARIZATION: "Overview",
        GenerationMode.ARGUMENT_BUILDER: "Thesis/Position",
        GenerationMode.LITERATURE_REVIEW: "Themes",
    }

    for mode, first_heading in expected_first_heading.items():
        answer = await generator.generate(
            mode=mode,
            query="What does the source support?",
            retrieval_results=[result],
        )

        assert answer.fallback_used is False
        assert answer.sections[0].heading == first_heading
        assert answer.references == ["motivation.pdf, p. 5"]
        assert answer.citations[0].source_segment_id == "seg_1"
