"""Cross-encoder reranking boundary with deterministic lexical fallback."""

from __future__ import annotations

import re

from app.common.types import RetrievalResult


TOKEN_RE = re.compile(r"[\wçğıöşüÇĞİÖŞÜ]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


class CrossEncoderReranker:
    def rerank(self, *, query: str, results: list[RetrievalResult]) -> list[RetrievalResult]:
        query_tokens = set(tokenize(query))
        reranked: list[RetrievalResult] = []
        for result in results:
            segment_tokens = set(tokenize(result.source_segment.text))
            overlap = len(query_tokens & segment_tokens)
            denominator = max(len(query_tokens), 1)
            rerank_score = overlap / denominator
            reranked.append(
                RetrievalResult(
                    source_segment=result.source_segment,
                    score=result.score + rerank_score,
                    rank=result.rank,
                    bm25_score=result.bm25_score,
                    vector_score=result.vector_score,
                    rerank_score=rerank_score,
                )
            )

        sorted_results = sorted(reranked, key=lambda item: item.score, reverse=True)
        return [
            RetrievalResult(
                source_segment=result.source_segment,
                score=result.score,
                rank=index + 1,
                bm25_score=result.bm25_score,
                vector_score=result.vector_score,
                rerank_score=result.rerank_score,
            )
            for index, result in enumerate(sorted_results)
        ]
