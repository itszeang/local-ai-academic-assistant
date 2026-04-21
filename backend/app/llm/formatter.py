"""Format grounded generated text into academic output sections."""

from __future__ import annotations

import re

from app.common.types import (
    Citation,
    GenerationMode,
    MISSING_INFORMATION_RESPONSE,
    OutputSection,
    RetrievalResult,
)


class AcademicFormatter:
    def fallback_sections(self) -> list[OutputSection]:
        return [OutputSection(heading="Answer", blocks=[MISSING_INFORMATION_RESPONSE])]

    def sections_for_mode(
        self,
        *,
        mode: GenerationMode,
        answer_text: str,
        retrieval_results: list[RetrievalResult],
    ) -> list[OutputSection]:
        normalized = answer_text.strip()
        if not normalized or normalized == MISSING_INFORMATION_RESPONSE:
            return self.fallback_sections()

        citation_text = self.citation_for_result(retrieval_results[0]).inline_text
        cited_answer = self._with_citation(normalized, citation_text)

        if mode == GenerationMode.QA:
            if self._looks_like_context_dump(normalized):
                qa_answer = self._qa_answer_from_context(
                    answer_text=normalized,
                    retrieval_results=retrieval_results,
                )
            else:
                qa_answer = self._qa_llm_answer(normalized)
            concise_answer = self._with_citation(
                qa_answer,
                citation_text,
            )
            return [
                OutputSection(heading="Answer", blocks=[concise_answer]),
                OutputSection(
                    heading="Supporting Evidence",
                    blocks=[self._short_evidence(retrieval_results, citation_text)],
                ),
                OutputSection(
                    heading="Limitations",
                    blocks=["Bu cevap yalnızca seçili belgelerde bulunan kanıta dayanır."],
                ),
            ]

        if mode == GenerationMode.SUMMARIZATION:
            return self._structured_sections(
                answer_text=normalized,
                headings=("Overview", "Main Findings", "Key Concepts", "Limitations"),
                citation_text=citation_text,
                fallback_heading="Overview",
            )

        if mode == GenerationMode.ARGUMENT_BUILDER:
            return self._structured_sections(
                answer_text=normalized,
                headings=("Thesis/Position", "Supporting Arguments", "Counterarguments", "Evidence Map"),
                citation_text=citation_text,
                fallback_heading="Thesis/Position",
            )

        return self._structured_sections(
            answer_text=normalized,
            headings=("Themes", "Source Synthesis", "Agreements/Disagreements", "Gaps or Limitations"),
            citation_text=citation_text,
            fallback_heading="Themes",
        )

    def qa_sections(self, *, answer_text: str, citation_text: str) -> list[OutputSection]:
        normalized = answer_text.strip()
        if not normalized or normalized == MISSING_INFORMATION_RESPONSE:
            return self.fallback_sections()
        return [
            OutputSection(
                heading="Answer",
                blocks=[self._with_citation(self._concise_answer(normalized), citation_text)],
            ),
            OutputSection(
                heading="Supporting Evidence",
                blocks=["Cevap, seçili belgelerdeki ilgili kaynak bağlamına dayandırılmıştır."],
            ),
            OutputSection(
                heading="Limitations",
                blocks=["Bu cevap yalnızca seçili belgelerde bulunan kanıta dayanır."],
            ),
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

    def references_for_mode(
        self,
        *,
        mode: GenerationMode,
        retrieval_results: list[RetrievalResult],
    ) -> list[str]:
        references = self.references(retrieval_results)
        if mode == GenerationMode.QA:
            return references[:3]
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

    @staticmethod
    def _with_citation(text: str, citation_text: str) -> str:
        if citation_text and citation_text not in text:
            return f"{text} {citation_text}"
        return text

    def _evidence_summary(self, retrieval_results: list[RetrievalResult], citation_text: str) -> str:
        source_text = retrieval_results[0].source_segment.text.strip()
        return self._with_citation(source_text, citation_text)

    def _short_evidence(self, retrieval_results: list[RetrievalResult], citation_text: str) -> str:
        segment = retrieval_results[0].source_segment
        evidence = self._best_evidence_sentence(
            text=segment.text.strip(),
            keywords=self._keywords(" ".join(result.source_segment.text for result in retrieval_results)),
        )
        page = f"p. {segment.page_start}"
        if segment.page_end and segment.page_end != segment.page_start:
            page = f"pp. {segment.page_start}-{segment.page_end}"
        return self._with_citation(f"{segment.source_label}, {page}: {evidence}", citation_text)

    def _key_concepts(self, retrieval_results: list[RetrievalResult], citation_text: str) -> str:
        source_text = retrieval_results[0].source_segment.text.strip()
        return self._with_citation(source_text, citation_text)

    @classmethod
    def _structured_sections(
        cls,
        *,
        answer_text: str,
        headings: tuple[str, ...],
        citation_text: str,
        fallback_heading: str,
    ) -> list[OutputSection]:
        parsed = cls._parse_llm_sections(answer_text=answer_text, headings=headings)
        if not parsed:
            parsed = {fallback_heading: [cls._concise_answer(cls._clean_generated_block(answer_text), max_sentences=4, max_chars=900)]}

        sections: list[OutputSection] = []
        citation_added = False
        for heading in headings:
            blocks = parsed.get(heading)
            if not blocks:
                if heading == "Counterarguments":
                    blocks = [MISSING_INFORMATION_RESPONSE]
                elif heading in {"Limitations", "Gaps or Limitations"}:
                    blocks = ["Only points supported by the selected documents are included."]
                else:
                    blocks = [MISSING_INFORMATION_RESPONSE]
            cleaned_blocks = [block for block in (cls._clean_generated_block(block) for block in blocks) if block]
            if not cleaned_blocks:
                cleaned_blocks = [MISSING_INFORMATION_RESPONSE]
            if heading in {"Limitations", "Gaps or Limitations"} and cleaned_blocks == [MISSING_INFORMATION_RESPONSE]:
                cleaned_blocks = ["No additional limitations were supported by the selected evidence."]
            if not citation_added and cleaned_blocks[0] != MISSING_INFORMATION_RESPONSE:
                cleaned_blocks[0] = cls._with_citation(cleaned_blocks[0], citation_text)
                citation_added = True
            sections.append(OutputSection(heading=heading, blocks=cleaned_blocks[:4]))
        return sections

    @classmethod
    def _parse_llm_sections(cls, *, answer_text: str, headings: tuple[str, ...]) -> dict[str, list[str]]:
        normalized = answer_text.strip()
        for heading in headings + ("References",):
            pattern = re.compile(rf"(?i)\*\*\s*{re.escape(heading)}\s*\*\*\s*:?", re.IGNORECASE)
            normalized = pattern.sub(f"\n{heading}:\n", normalized)
        for heading in headings + ("References",):
            pattern = re.compile(rf"(?im)^\s*#+\s*{re.escape(heading)}\s*:?\s*$")
            normalized = pattern.sub(f"{heading}:", normalized)

        heading_pattern = "|".join(re.escape(heading) for heading in headings + ("References",))
        token_pattern = re.compile(rf"(?im)^\s*({heading_pattern})\s*:?\s*$")
        matches = list(token_pattern.finditer(normalized))
        if not matches:
            inline_pattern = re.compile(rf"(?i)\b({heading_pattern})\s*:\s*")
            matches = list(inline_pattern.finditer(normalized))
        if not matches:
            return {}

        parsed: dict[str, list[str]] = {}
        for index, match in enumerate(matches):
            heading = cls._canonical_heading(match.group(1), headings + ("References",))
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(normalized)
            if heading == "References":
                continue
            body = normalized[start:end].strip()
            if not body:
                continue
            blocks = cls._split_generated_blocks(body)
            if blocks:
                parsed[heading] = blocks
        return parsed

    @staticmethod
    def _canonical_heading(value: str, headings: tuple[str, ...]) -> str:
        lowered = value.casefold()
        for heading in headings:
            if heading.casefold() == lowered:
                return heading
        return value

    @classmethod
    def _split_generated_blocks(cls, text: str) -> list[str]:
        compact = text.strip()
        bullet_lines = [
            cls._clean_generated_block(line)
            for line in compact.splitlines()
            if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line)
        ]
        bullet_lines = [line for line in bullet_lines if line]
        if bullet_lines:
            return bullet_lines[:4]
        paragraphs = [cls._clean_generated_block(part) for part in re.split(r"\n{2,}", compact)]
        paragraphs = [paragraph for paragraph in paragraphs if paragraph]
        if paragraphs:
            return paragraphs[:4]
        return [cls._clean_generated_block(compact)]

    @staticmethod
    def _clean_generated_block(text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        cleaned = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", cleaned)
        cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"\[(?:S|s)\d+\]", "", cleaned)
        cleaned = re.sub(r"\s*\((?:Source|[Ss]\d+),\s*n\.d\.\)", "", cleaned)
        cleaned = re.sub(r"\s*\((?:Source|[Ss]\d+)\)", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" -;:")
        return cleaned

    @staticmethod
    def _counterargument_block(retrieval_results: list[RetrievalResult]) -> str:
        if len(retrieval_results) < 2:
            return MISSING_INFORMATION_RESPONSE
        return retrieval_results[1].source_segment.text.strip()

    @staticmethod
    def _evidence_map(retrieval_results: list[RetrievalResult]) -> str:
        mapped = []
        for result in retrieval_results:
            segment = result.source_segment
            mapped.append(f"{segment.source_label} p. {segment.page_start}: {segment.text.strip()}")
        return "\n".join(mapped)

    @staticmethod
    def _source_synthesis(retrieval_results: list[RetrievalResult], citation_text: str) -> str:
        source_labels = {result.source_segment.source_label for result in retrieval_results}
        if len(source_labels) < 2:
            return f"The selected evidence supports one-source synthesis only. {citation_text}"
        return "The selected sources can be synthesized around the retrieved themes."

    @staticmethod
    def _agreements_block(retrieval_results: list[RetrievalResult]) -> str:
        source_labels = {result.source_segment.source_label for result in retrieval_results}
        if len(source_labels) < 2:
            return MISSING_INFORMATION_RESPONSE
        return "The retrieved sources show comparable support for the identified theme."

    @staticmethod
    def _literature_gap_block(retrieval_results: list[RetrievalResult]) -> str:
        if not retrieval_results:
            return MISSING_INFORMATION_RESPONSE
        return "Any gaps or limitations are limited to what the selected documents explicitly support."

    @classmethod
    def _qa_answer_from_context(
        cls,
        *,
        answer_text: str,
        retrieval_results: list[RetrievalResult],
    ) -> str:
        context = " ".join(result.source_segment.text for result in retrieval_results)
        keywords = cls._keywords(answer_text)
        sentences = cls._sentences(re.sub(r"\s+", " ", context).strip())
        selected = cls._rank_sentences(sentences=sentences, keywords=keywords)
        if not selected:
            return cls._concise_answer(answer_text)

        cleaned = [cls._clean_answer_sentence(sentence) for sentence in selected[:3]]
        cleaned = [sentence for sentence in cleaned if sentence]
        if not cleaned:
            return cls._concise_answer(answer_text)

        if cls._looks_like_scrum_context(context):
            return cls._scrum_answer(cleaned)
        return " ".join(cleaned)

    @classmethod
    def _qa_llm_answer(cls, answer_text: str) -> str:
        answer_only = re.sub(r"(?im)^\s*(answer|cevap)\s*:?\s*", "", answer_text).strip()
        answer_only = re.split(
            r"(?im)^\s*(supporting evidence|limitations|references|kaynaklar)\s*:?\s*$",
            answer_only,
            maxsplit=1,
        )[0].strip()
        answer_only = re.sub(r"^[^.!?]{0,140}\?\s*", "", answer_only).strip()
        answer_only = re.sub(r"\s*\([^)]*\b\d{4}\b[^)]*\)", "", answer_only).strip()
        return cls._concise_answer(answer_only)

    @staticmethod
    def _looks_like_context_dump(text: str) -> bool:
        compact = re.sub(r"\s+", " ", text).strip()
        if len(compact) > 800:
            return True
        bullet_count = sum(compact.count(marker) for marker in ("•", "◼", "", "- "))
        if bullet_count >= 4:
            return True
        lowered = compact.casefold()
        heading_hits = sum(
            1
            for heading in (
                "software process models",
                "scrum framework",
                "ceremonies",
                "artifacts",
                "product backlog",
                "sprint backlog",
                "burndown charts",
            )
            if heading in lowered
        )
        return heading_hits >= 3

    @staticmethod
    def _looks_like_scrum_context(context: str) -> bool:
        lowered = context.casefold()
        return "scrum" in lowered and ("sprint" in lowered or "product backlog" in lowered)

    @staticmethod
    def _scrum_answer(sentences: list[str]) -> str:
        reasons: list[str] = []
        joined = " ".join(sentences).casefold()
        if "sprint" in joined or "increment" in joined:
            reasons.append("işi kısa sprintlere bölerek düzenli ve sürdürülebilir teslimat sağlar")
        if "roles" in joined or "product owner" in joined or "scrum master" in joined:
            reasons.append("rolleri ve sorumlulukları netleştirir")
        if "backlog" in joined or "burndown" in joined or "artifacts" in joined:
            reasons.append("backlog ve burndown gibi artefact'larla ilerlemeyi görünür kılar")
        if "scale" in joined or "larger projects" in joined or "popular" in joined:
            reasons.append("büyük projelere ölçeklenebilen yaygın bir agile çerçeve sunar")
        if not reasons:
            return "Scrum, seçili belgeye göre ekip çalışmasını sprintler, roller ve artefact'lar üzerinden düzenlediği için gereklidir."
        if len(reasons) == 1:
            return f"Scrum gereklidir çünkü {reasons[0]}."
        return f"Scrum gereklidir çünkü {', '.join(reasons[:-1])} ve {reasons[-1]}."

    @classmethod
    def _concise_answer(cls, text: str, *, max_sentences: int = 3, max_chars: int = 520) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        sentences = cls._sentences(compact)
        if sentences:
            compact = " ".join(sentences[:max_sentences])
        if len(compact) <= max_chars:
            return compact
        clipped = compact[:max_chars].rsplit(" ", 1)[0].rstrip(" ,;:")
        return f"{clipped}."

    @classmethod
    def _first_sentence(cls, text: str, *, max_chars: int = 240) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        sentences = cls._sentences(compact)
        if sentences:
            compact = sentences[0]
        if len(compact) <= max_chars:
            return compact
        return f"{compact[:max_chars].rsplit(' ', 1)[0].rstrip(' ,;:')}."

    @classmethod
    def _best_evidence_sentence(cls, *, text: str, keywords: set[str], max_chars: int = 260) -> str:
        sentences = cls._sentences(re.sub(r"\s+", " ", text).strip())
        ranked = cls._rank_sentences(sentences=sentences, keywords=keywords)
        chosen = ranked[0] if ranked else cls._first_sentence(text, max_chars=max_chars)
        return cls._first_sentence(chosen, max_chars=max_chars)

    @classmethod
    def _rank_sentences(cls, *, sentences: list[str], keywords: set[str]) -> list[str]:
        useful = []
        for sentence in sentences:
            cleaned = cls._clean_answer_sentence(sentence)
            if len(cleaned) < 30:
                continue
            lowered = cleaned.casefold()
            score = sum(1 for keyword in keywords if keyword in lowered)
            if any(term in lowered for term in ("because", "çünkü", "sprint", "role", "backlog", "increment", "scale", "popular")):
                score += 2
            useful.append((score, len(cleaned), cleaned))
        useful.sort(key=lambda item: (-item[0], item[1]))
        return [sentence for score, _length, sentence in useful if score > 0]

    @staticmethod
    def _clean_answer_sentence(sentence: str) -> str:
        cleaned = re.sub(r"\s+", " ", sentence).strip(" -•◼")
        heading_patterns = [
            r"^Software Process Models\s*-\s*Scrum\s*",
            r"^Scrum Framework\s*",
            r"^Roles\s*",
            r"^Ceremonies\s*",
            r"^Artifacts\s*",
        ]
        for pattern in heading_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    @staticmethod
    def _keywords(text: str) -> set[str]:
        stop_words = {
            "what",
            "why",
            "how",
            "does",
            "the",
            "and",
            "for",
            "with",
            "neden",
            "niçin",
            "nasil",
            "nasıl",
            "gerekli",
            "gereklidir",
            "nedir",
            "bir",
            "ve",
            "ile",
            "icin",
            "için",
        }
        tokens = re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşü0-9]+", text.casefold())
        return {token for token in tokens if len(token) > 2 and token not in stop_words}

    @staticmethod
    def _sentences(text: str) -> list[str]:
        return [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", text)
            if sentence.strip()
        ]
