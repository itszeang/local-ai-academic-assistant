from app.common.types import GenerationMode, MISSING_INFORMATION_RESPONSE
from app.llm.formatter import AcademicFormatter

from tests.helpers import make_retrieval_result


def test_formatter_returns_distinct_sections_for_each_mode() -> None:
    formatter = AcademicFormatter()
    result = make_retrieval_result()

    expected_headings = {
        GenerationMode.QA: ["Answer", "Supporting Evidence", "Limitations"],
        GenerationMode.SUMMARIZATION: ["Overview", "Main Findings", "Key Concepts", "Limitations"],
        GenerationMode.ARGUMENT_BUILDER: [
            "Thesis/Position",
            "Supporting Arguments",
            "Counterarguments",
            "Evidence Map",
        ],
        GenerationMode.LITERATURE_REVIEW: [
            "Themes",
            "Source Synthesis",
            "Agreements/Disagreements",
            "Gaps or Limitations",
        ],
    }

    for mode, headings in expected_headings.items():
        sections = formatter.sections_for_mode(
            mode=mode,
            answer_text="Motivation improves persistence in learning tasks.",
            retrieval_results=[result],
        )

        assert [section.heading for section in sections] == headings
        assert any("(Aksoy, 2024)" in block for section in sections for block in section.blocks)


def test_formatter_uses_partial_fallback_for_unsupported_mode_sections() -> None:
    formatter = AcademicFormatter()
    result = make_retrieval_result()

    sections = formatter.sections_for_mode(
        mode=GenerationMode.ARGUMENT_BUILDER,
        answer_text="Motivation improves persistence in learning tasks.",
        retrieval_results=[result],
    )

    counterarguments = next(section for section in sections if section.heading == "Counterarguments")
    assert counterarguments.blocks == [MISSING_INFORMATION_RESPONSE]


def test_qa_output_is_concise_even_when_retrieved_context_is_long() -> None:
    formatter = AcademicFormatter()
    result = make_retrieval_result(
        text=(
            "Scrum is useful because teams work in short sprints that create a sustainable "
            "cadence for delivering small valuable increments. It also clarifies roles, "
            "meetings, and artifacts. Product backlogs and sprint backlogs help teams keep "
            "work visible. Burndown charts help monitor progress. This extra sentence should "
            "not make the Q&A answer feel like a summary."
        )
    )

    sections = formatter.sections_for_mode(
        mode=GenerationMode.QA,
        answer_text=result.source_segment.text,
        retrieval_results=[result],
    )

    answer = sections[0].blocks[0]
    assert len(answer) < 620
    assert "This extra sentence" not in answer
    assert sections[1].blocks[0].startswith("motivation.pdf, p. 5:")


def test_qa_scrum_answer_synthesizes_instead_of_dumping_slide_text() -> None:
    formatter = AcademicFormatter()
    result = make_retrieval_result(
        text=(
            "Software Process Models - Scrum Scrum Framework Roles • Product owner • Scrum Master "
            "Ceremonies Team • Sprint planning • Sprint review • Sprint retrospective • Daily scrum meeting "
            "Artifacts • Product backlog • Sprint backlog • Burndown charts • Increment Scrum is used "
            "to scale up for larger projects. Teams work in cycles called Sprints that create a sustainable "
            "cadence of releasing small, valuable increments of work regularly."
        )
    )

    sections = formatter.sections_for_mode(
        mode=GenerationMode.QA,
        answer_text=result.source_segment.text,
        retrieval_results=[result],
    )

    answer = sections[0].blocks[0]
    assert answer.startswith("Scrum gereklidir çünkü")
    assert "Software Process Models" not in answer
    assert "Product owner • Scrum Master" not in answer
    assert "sprint" in answer.casefold()


def test_summary_output_parses_llm_sections_instead_of_dumping_context() -> None:
    formatter = AcademicFormatter()
    result = make_retrieval_result(
        text=(
            "Product Backlog Management Prioritising the backlog. The backlog itself should always "
            "be in priority order. Team members inform colleagues about new backlog items."
        )
    )
    answer_text = (
        "**Overview** This summary compares Scrum backlog management and software requirements.\n\n"
        "**Main Findings**\n"
        "* Backlog items should be prioritized by value and urgency.\n"
        "* Requirements should remain complete and consistent.\n\n"
        "**Key Concepts**\n"
        "* Product backlog management\n"
        "* Requirements consistency\n\n"
        "**Limitations** The selected documents do not fully describe implementation at scale.\n\n"
        "**References** [S1] 2-scrum.pdf"
    )

    sections = formatter.sections_for_mode(
        mode=GenerationMode.SUMMARIZATION,
        answer_text=answer_text,
        retrieval_results=[result],
    )

    overview = sections[0].blocks[0]
    main_findings = " ".join(sections[1].blocks)
    key_concepts = " ".join(sections[2].blocks)
    all_blocks = " ".join(block for section in sections for block in section.blocks)

    assert [section.heading for section in sections] == ["Overview", "Main Findings", "Key Concepts", "Limitations"]
    assert "Main Findings" not in overview
    assert "References" not in all_blocks
    assert "Product Backlog Management Prioritising" not in main_findings
    assert "Backlog items should be prioritized" in main_findings
    assert "Product backlog management" in key_concepts
