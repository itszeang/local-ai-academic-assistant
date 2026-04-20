"""Academic prompt construction with explicit grounding rules."""

from __future__ import annotations

from app.common.types import GenerationMode, Language, SourceSegment


MODE_INSTRUCTIONS: dict[GenerationMode, str] = {
    GenerationMode.QA: "Produce a concise academic answer with support from the cited context.",
    GenerationMode.SUMMARIZATION: "Produce a structured academic summary of the cited context.",
    GenerationMode.ARGUMENT_BUILDER: "Build an argument only from supported evidence in the context.",
    GenerationMode.LITERATURE_REVIEW: "Synthesize themes only from the cited context.",
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
        context_block = "\n\n".join(
            self._format_source(index=index + 1, segment=segment)
            for index, segment in enumerate(context)
        )
        return (
            "You are a local-first academic assistant, not a chatbot.\n"
            "Use only the provided document context.\n"
            "Do not use outside knowledge.\n"
            "If the context does not support the answer, return exactly: Bilgi bulunamadı\n"
            "Paraphrase academically and include APA-style citations for substantive claims.\n\n"
            f"Mode: {mode.value}\n"
            f"Language: {language.value}\n"
            f"Task: {MODE_INSTRUCTIONS[mode]}\n"
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
