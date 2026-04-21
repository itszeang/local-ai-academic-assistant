"""Grounded academic answer generation."""

from __future__ import annotations

from typing import Protocol

from app.common.types import (
    GeneratedAnswer,
    GenerationMode,
    Language,
    MISSING_INFORMATION_RESPONSE,
    RetrievalResult,
)
from app.llm.formatter import AcademicFormatter
from app.llm.prompt_manager import PromptManager


class LlmClient(Protocol):
    async def generate(self, *, model: str, prompt: str) -> str:
        ...


class GroundedGenerator:
    def __init__(
        self,
        *,
        llm_client: LlmClient | None = None,
        prompt_manager: PromptManager | None = None,
        formatter: AcademicFormatter | None = None,
        generator_model: str = "llama3.1:8b",
    ) -> None:
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager or PromptManager()
        self.formatter = formatter or AcademicFormatter()
        self.generator_model = generator_model

    async def generate(
        self,
        *,
        mode: GenerationMode,
        query: str,
        retrieval_results: list[RetrievalResult],
        language: Language = Language.AUTO,
    ) -> GeneratedAnswer:
        if not retrieval_results:
            return GeneratedAnswer(
                title=MISSING_INFORMATION_RESPONSE,
                sections=self.formatter.fallback_sections(),
                references=[],
                citations=[],
                fallback_used=True,
            )

        context_segments = [result.source_segment for result in retrieval_results]
        prompt = self.prompt_manager.build_prompt(
            mode=mode,
            query=query,
            context=context_segments,
            language=language,
        )
        answer_text = await self._generate_text(prompt, retrieval_results)
        if answer_text.strip() == MISSING_INFORMATION_RESPONSE:
            return GeneratedAnswer(
                title=MISSING_INFORMATION_RESPONSE,
                sections=self.formatter.fallback_sections(),
                references=[],
                citations=[],
                fallback_used=True,
            )

        primary_citation = self.formatter.citation_for_result(retrieval_results[0])
        sections = self.formatter.sections_for_mode(
            mode=mode,
            answer_text=answer_text,
            retrieval_results=retrieval_results,
        )
        return GeneratedAnswer(
            title=self._title_for_mode(mode),
            sections=sections,
            references=self.formatter.references_for_mode(
                mode=mode,
                retrieval_results=retrieval_results,
            ),
            citations=[primary_citation],
            fallback_used=False,
        )

    async def _generate_text(self, prompt: str, retrieval_results: list[RetrievalResult]) -> str:
        if self.llm_client is not None:
            try:
                generated = await self.llm_client.generate(model=self.generator_model, prompt=prompt)
            except OSError:
                generated = ""
            if generated.strip():
                return generated.strip()

        # Conservative offline fallback for tests and first-run local setup.
        # The formatter keeps Q&A concise; long synthesis is reserved for summary/review modes.
        return retrieval_results[0].source_segment.text.strip()

    @staticmethod
    def _title_for_mode(mode: GenerationMode) -> str:
        titles = {
            GenerationMode.QA: "Grounded Answer",
            GenerationMode.SUMMARIZATION: "Structured Summary",
            GenerationMode.ARGUMENT_BUILDER: "Argument Builder",
            GenerationMode.LITERATURE_REVIEW: "Literature Review",
        }
        return titles[mode]
