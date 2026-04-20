"""Recursive-ish text chunking with source and page metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.common.types import ExtractionMethod
from app.ingestion.cleaner import clean_text


@dataclass(frozen=True, slots=True)
class ChunkerPage:
    page_number: int
    text: str
    extraction_method: ExtractionMethod


@dataclass(frozen=True, slots=True)
class TextChunk:
    chunk_index: int
    text: str
    page_start: int
    page_end: int
    source_label: str
    extraction_method: ExtractionMethod
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class _PageSpan:
    page_number: int
    start: int
    end: int
    extraction_method: ExtractionMethod


class Chunker:
    def __init__(self, *, chunk_size: int = 1100, chunk_overlap: int = 200) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(
        self,
        pages: list[ChunkerPage],
        *,
        document_id: str,
        source_label: str,
    ) -> list[TextChunk]:
        document_text, spans = self._join_pages(pages)
        if not document_text:
            return []

        ranges = self._chunk_ranges(document_text)
        chunks: list[TextChunk] = []
        for index, (start, end) in enumerate(ranges):
            chunk_text = document_text[start:end].strip()
            if not chunk_text:
                continue
            page_numbers = self._page_numbers_for_range(spans, start, end)
            methods = self._methods_for_range(spans, start, end)
            page_start = min(page_numbers)
            page_end = max(page_numbers)
            extraction_method = self._merge_methods(methods)
            chunks.append(
                TextChunk(
                    chunk_index=len(chunks),
                    text=chunk_text,
                    page_start=page_start,
                    page_end=page_end,
                    source_label=source_label,
                    extraction_method=extraction_method,
                    metadata={
                        "document_id": document_id,
                        "source": source_label,
                        "page_start": page_start,
                        "page_end": page_end,
                        "extraction_method": extraction_method.value,
                    },
                )
            )
        return chunks

    @staticmethod
    def _join_pages(pages: list[ChunkerPage]) -> tuple[str, list[_PageSpan]]:
        parts: list[str] = []
        spans: list[_PageSpan] = []
        cursor = 0
        for page in pages:
            text = clean_text(page.text)
            if not text:
                continue
            if parts:
                parts.append("\n\n")
                cursor += 2
            start = cursor
            parts.append(text)
            cursor += len(text)
            spans.append(
                _PageSpan(
                    page_number=page.page_number,
                    start=start,
                    end=cursor,
                    extraction_method=page.extraction_method,
                )
            )
        return "".join(parts), spans

    def _chunk_ranges(self, text: str) -> list[tuple[int, int]]:
        ranges: list[tuple[int, int]] = []
        start = 0
        text_length = len(text)
        while start < text_length:
            hard_end = min(start + self.chunk_size, text_length)
            end = self._best_break(text, start, hard_end)
            if end <= start:
                end = hard_end
            ranges.append((start, end))
            if end >= text_length:
                break
            start = max(0, end - self.chunk_overlap)
            while start < text_length and text[start].isspace():
                start += 1
        return ranges

    @staticmethod
    def _best_break(text: str, start: int, hard_end: int) -> int:
        if hard_end >= len(text):
            return len(text)
        window = text[start:hard_end]
        for separator in ("\n\n", ". ", "; ", ", ", " "):
            index = window.rfind(separator)
            if index >= max(1, len(window) // 2):
                return start + index + len(separator)
        return hard_end

    @staticmethod
    def _page_numbers_for_range(spans: list[_PageSpan], start: int, end: int) -> list[int]:
        return [
            span.page_number
            for span in spans
            if span.start < end and span.end > start
        ]

    @staticmethod
    def _methods_for_range(
        spans: list[_PageSpan],
        start: int,
        end: int,
    ) -> set[ExtractionMethod]:
        return {
            span.extraction_method
            for span in spans
            if span.start < end and span.end > start
        }

    @staticmethod
    def _merge_methods(methods: set[ExtractionMethod]) -> ExtractionMethod:
        if methods == {ExtractionMethod.TEXT}:
            return ExtractionMethod.TEXT
        if methods == {ExtractionMethod.OCR}:
            return ExtractionMethod.OCR
        return ExtractionMethod.MIXED
