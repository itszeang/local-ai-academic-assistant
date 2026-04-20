"""Simple query classification for academic output modes."""

from __future__ import annotations

from app.common.types import GenerationMode


class QueryClassifier:
    def classify(self, query: str, explicit_mode: GenerationMode | None = None) -> GenerationMode:
        if explicit_mode is not None:
            return explicit_mode

        normalized = query.strip().lower()
        literature_markers = ("literature review", "literatür", "literature", "review the literature")
        argument_markers = ("argument", "argue", "thesis", "claim", "counterargument", "sav")
        summary_markers = ("summarize", "summary", "özet", "ozet")

        if any(marker in normalized for marker in literature_markers):
            return GenerationMode.LITERATURE_REVIEW
        if any(marker in normalized for marker in argument_markers):
            return GenerationMode.ARGUMENT_BUILDER
        if any(marker in normalized for marker in summary_markers):
            return GenerationMode.SUMMARIZATION
        return GenerationMode.QA
