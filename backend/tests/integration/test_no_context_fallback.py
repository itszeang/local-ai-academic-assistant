from app.common.types import GenerationMode, MISSING_INFORMATION_RESPONSE
from app.llm.generator import GroundedGenerator
from app.retrieval.bm25_store import BM25Store
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.vector_store import VectorStore


class EmptySegmentRepository:
    def list_by_document_ids(self, document_ids: list[str]):
        return []


async def test_no_context_pipeline_returns_exact_fallback() -> None:
    repository = EmptySegmentRepository()
    retriever = HybridRetriever(
        bm25_store=BM25Store(repository),
        vector_store=VectorStore(repository),
        reranker=CrossEncoderReranker(),
    )
    results = retriever.retrieve(
        query="What does the document say about motivation?",
        active_document_ids=["doc_missing"],
    )

    answer = await GroundedGenerator().generate(
        mode=GenerationMode.QA,
        query="What does the document say about motivation?",
        retrieval_results=results,
    )

    assert answer.title == MISSING_INFORMATION_RESPONSE
    assert answer.sections[0].blocks == [MISSING_INFORMATION_RESPONSE]
    assert answer.fallback_used is True
