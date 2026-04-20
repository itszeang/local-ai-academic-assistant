"""Format grounded generated text into academic output sections."""

from __future__ import annotations

from app.common.types import (
    Citation,
    MISSING_INFORMATION_RESPONSE,
    OutputSection,
    RetrievalResult,
)


class AcademicFormatter:
    def fallback_sections(self) -> list[OutputSection]:
        return [OutputSection(heading="Answer", blocks=[MISSING_INFORMATION_RESPONSE])]

    def qa_sections(self, *, answer_text: str, citation_text: str) -> list[OutputSection]:
        normalized = answer_text.strip()
        if not normalized or normalized == MISSING_INFORMATION_RESPONSE:
            return self.fallback_sections()
        if citation_text and citation_text not in normalized:
            normalized = f"{normalized} {citation_text}"
        return [
            OutputSection(heading="Answer", blocks=[normalized]),
            OutputSection(heading="Evidence", blocks=["The answer is grounded in the cited source context."]),
        ]

    def references(self, retrieval_results: list[RetrievalResult]) -> list[str]:
        references: list[str] = []
        seen: set[str] = set()
        for result in retrieval_results:
            segment = result.source_segment
            page = f"p. {segment.page_start}"
            if segment.page_end and segment.page_end != segment.page_start:
                page = f"pp. {segment.page_start}-{segment.page_end}"
            reference = f"{segment.source_label}, {page}"
            if reference not in seen:
                seen.add(reference)
                references.append(reference)
        return references

    def citation_for_result(self, result: RetrievalResult, *, output_id: str = "") -> Citation:
        segment = result.source_segment
        return Citation(
            id=f"pending_citation_{result.rank}",
            academic_output_id=output_id,
            source_segment_id=segment.id,
            claim_path="sections.0.blocks.0",
            inline_text=self.inline_citation(segment.metadata),
            page_start=segment.page_start,
            page_end=segment.page_end,
            source_snippet=segment.text[:500],
        )

    @staticmethod
    def inline_citation(metadata: dict[str, object]) -> str:
        authors_value = metadata.get("authors")
        year_value = metadata.get("year")
        year = str(year_value) if year_value else "n.d."
        if isinstance(authors_value, list) and authors_value:
            first_author = str(authors_value[0])
        elif isinstance(authors_value, str) and authors_value:
            first_author = authors_value
        else:
            first_author = "Source"
        return f"({first_author}, {year})"
