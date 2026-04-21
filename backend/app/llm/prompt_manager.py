"""Academic prompt construction with explicit grounding rules."""

from __future__ import annotations

from app.common.types import GenerationMode, Language, MISSING_INFORMATION_RESPONSE, SourceSegment


MODE_INSTRUCTIONS: dict[GenerationMode, tuple[str, tuple[str, ...]]] = {
    GenerationMode.QA: (
        "Answer the question directly in 2-4 sentences. Do not copy long source passages or output a slide-style summary.",
        ("Answer", "Supporting Evidence", "Limitations", "References"),
    ),
    GenerationMode.SUMMARIZATION: (
        "Produce a structured academic summary of the cited context.",
        ("Overview", "Main Findings", "Key Concepts", "Limitations", "References"),
    ),
    GenerationMode.ARGUMENT_BUILDER: (
        "Build an argument only from supported evidence in the context.",
        ("Thesis/Position", "Supporting Arguments", "Counterarguments", "Evidence Map", "References"),
    ),
    GenerationMode.LITERATURE_REVIEW: (
        "Write source synthesis for a literature review using only the cited context.",
        ("Themes", "Source Synthesis", "Agreements/Disagreements", "Gaps or Limitations", "References"),
    ),
}


class PromptManager:
    def build_prompt(
        self,
        *,
        mode: GenerationMode,
        query: str,
        context: list[SourceSegment],
        language: Language = Language.AUTO,
    ) -> str:
        task_instruction, required_sections = MODE_INSTRUCTIONS[mode]
        context_block = "\n\n".join(
            self._format_source(index=index + 1, segment=segment)
            for index, segment in enumerate(context)
        )
        section_block = "\n".join(f"- {heading}" for heading in required_sections)
        response_format = "Required Sections:\n" f"{section_block}\n"
        section_gap_rule = (
            f"If a required section lacks enough evidence, write exactly {MISSING_INFORMATION_RESPONSE} "
            "for that section instead of inferring.\n"
        )
        citation_rule = "Paraphrase academically and include APA-style citations for substantive claims.\n"
        if mode == GenerationMode.QA:
            response_format = (
                "Response Format:\n"
                "- Write only the final Answer paragraph.\n"
                "- Do not include headings, bullets, references, or supporting evidence sections.\n"
                "- Do not repeat raw source text or slide headings.\n"
                "- Do not repeat the user's question.\n"
                "- If the selected language is Turkish, write in fluent natural Turkish.\n"
            )
            section_gap_rule = ""
            citation_rule = "Do not add citations, authors, years, or references; the app will attach source citations.\n"
        else:
            response_format = (
                "Response Format:\n"
                f"{section_block}\n"
                "- Use exactly these section headings and no other headings.\n"
                "- Keep each section concise: 1 short paragraph or up to 3 short bullets.\n"
                "- Do not include a References section; the app will attach references.\n"
                "- Do not paste raw slide text or long source passages.\n"
            )
            citation_rule = "Do not add citations, authors, years, or references; the app will attach source citations.\n"
        return (
            "You are a local-first academic assistant, not a chatbot.\n"
            "Use only the provided document context.\n"
            "Do not use outside knowledge.\n"
            f"If the context does not support the answer, return exactly: {MISSING_INFORMATION_RESPONSE}\n"
            f"{section_gap_rule}"
            f"{citation_rule}\n"
            f"Mode: {mode.value}\n"
            f"Language: {language.value}\n"
            f"Task: {task_instruction}\n"
            f"{response_format}"
            f"User Query: {query}\n\n"
            "Document Context:\n"
            f"{context_block}"
        )

    @staticmethod
    def _format_source(*, index: int, segment: SourceSegment) -> str:
        page_label = f"p.{segment.page_start}"
        if segment.page_end and segment.page_end != segment.page_start:
            page_label = f"pp.{segment.page_start}-{segment.page_end}"
        return f"[S{index}] {segment.source_label} {page_label}\n{segment.text}"
