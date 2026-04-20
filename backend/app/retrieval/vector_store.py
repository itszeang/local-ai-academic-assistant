"""Semantic vector search boundary with lexical fallback for the MVP."""

from __future__ import annotations

from typing import Protocol

from app.common.types import RetrievalResult, SourceSegment
from app.retrieval.reranker import tokenize


class SegmentRepository(Protocol):
    def list_by_document_ids(self, document_ids: list[str]) -> list[SourceSegment]:
        ...


class VectorStore:
    def __init__(self, segment_repository: SegmentRepository) -> None:
        self.segment_repository = segment_repository

    def search(
        self,
        *,
        query: str,
        active_document_ids: list[str],
        top_k: int = 8,
    ) -> list[RetrievalResult]:
        segments = self.segment_repository.list_by_document_ids(active_document_ids)
        query_tokens = set(tokenize(query))
        if not segments or not query_tokens:
            return []

        results: list[RetrievalResult] = []
        for segment in segments:
            segment_tokens = set(tokenize(segment.text))
            union = query_tokens | segment_tokens
            if not union:
                continue
            score = len(query_tokens & segment_tokens) / len(union)
            if score > 0:
                results.append(
                    RetrievalResult(
                        source_segment=segment,
                        score=score,
                        rank=0,
                        vector_score=score,
                    )
                )

        sorted_results = sorted(results, key=lambda item: item.score, reverse=True)[:top_k]
        return [
            RetrievalResult(
                source_segment=result.source_segment,
                score=result.score,
                rank=index + 1,
                vector_score=result.vector_score,
            )
            for index, result in enumerate(sorted_results)
        ]
