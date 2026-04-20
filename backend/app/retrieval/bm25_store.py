"""BM25-style keyword search over local source segments."""

from __future__ import annotations

import math
from collections import Counter
from typing import Protocol

from app.common.types import RetrievalResult, SourceSegment
from app.retrieval.reranker import tokenize


class SegmentRepository(Protocol):
    def list_by_document_ids(self, document_ids: list[str]) -> list[SourceSegment]:
        ...


class BM25Store:
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
        if not segments:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        document_tokens = [tokenize(segment.text) for segment in segments]
        document_frequency: Counter[str] = Counter()
        for tokens in document_tokens:
            document_frequency.update(set(tokens))

        results: list[RetrievalResult] = []
        total_documents = len(segments)
        for segment, tokens in zip(segments, document_tokens, strict=True):
            term_counts = Counter(tokens)
            score = 0.0
            for token in query_tokens:
                if token not in term_counts:
                    continue
                idf = math.log((total_documents + 1) / (document_frequency[token] + 0.5))
                score += term_counts[token] * max(idf, 0.01)
            if score > 0:
                results.append(
                    RetrievalResult(
                        source_segment=segment,
                        score=score,
                        rank=0,
                        bm25_score=score,
                    )
                )

        sorted_results = sorted(results, key=lambda item: item.score, reverse=True)[:top_k]
        return [
            RetrievalResult(
                source_segment=result.source_segment,
                score=result.score,
                rank=index + 1,
                bm25_score=result.bm25_score,
            )
            for index, result in enumerate(sorted_results)
        ]
