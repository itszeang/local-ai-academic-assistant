"""Hybrid retrieval that merges keyword and semantic candidates."""

from __future__ import annotations

from app.common.types import RetrievalResult
from app.retrieval.bm25_store import BM25Store
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.vector_store import VectorStore


class HybridRetriever:
    def __init__(
        self,
        *,
        bm25_store: BM25Store,
        vector_store: VectorStore,
        reranker: CrossEncoderReranker,
    ) -> None:
        self.bm25_store = bm25_store
        self.vector_store = vector_store
        self.reranker = reranker

    def retrieve(
        self,
        *,
        query: str,
        active_document_ids: list[str],
        top_k: int = 8,
    ) -> list[RetrievalResult]:
        if not active_document_ids:
            return []

        keyword_results = self.bm25_store.search(
            query=query,
            active_document_ids=active_document_ids,
            top_k=top_k * 2,
        )
        vector_results = self.vector_store.search(
            query=query,
            active_document_ids=active_document_ids,
            top_k=top_k * 2,
        )
        merged = self._merge(keyword_results, vector_results)
        reranked = self.reranker.rerank(query=query, results=merged)
        return reranked[:top_k]

    @staticmethod
    def _merge(
        keyword_results: list[RetrievalResult],
        vector_results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        by_segment_id: dict[str, RetrievalResult] = {}
        for result in [*keyword_results, *vector_results]:
            current = by_segment_id.get(result.source_segment.id)
            if current is None:
                by_segment_id[result.source_segment.id] = result
                continue
            by_segment_id[result.source_segment.id] = RetrievalResult(
                source_segment=result.source_segment,
                score=current.score + result.score,
                rank=0,
                bm25_score=max(current.bm25_score, result.bm25_score),
                vector_score=max(current.vector_score, result.vector_score),
            )

        sorted_results = sorted(by_segment_id.values(), key=lambda item: item.score, reverse=True)
        return [
            RetrievalResult(
                source_segment=result.source_segment,
                score=result.score,
                rank=index + 1,
                bm25_score=result.bm25_score,
                vector_score=result.vector_score,
            )
            for index, result in enumerate(sorted_results)
        ]
