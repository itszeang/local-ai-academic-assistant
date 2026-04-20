from pathlib import Path

from app.common.types import DocumentStatus, ExtractionMethod, GenerationMode
from app.llm.generator import GroundedGenerator
from app.llm.prompt_manager import PromptManager
from app.retrieval.bm25_store import BM25Store
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.vector_store import VectorStore
from app.storage.repositories import RepositoryRegistry
from app.storage.sqlite import SQLiteDatabase


async def test_grounded_qa_pipeline_returns_cited_answer(tmp_path: Path) -> None:
    db = SQLiteDatabase(tmp_path / "academic_assistant.sqlite")
    db.initialize()
    repos = RepositoryRegistry(db)
    workspace = repos.workspaces.create(name="Default", root_path=tmp_path)
    document = repos.documents.create(
        workspace_id=workspace.id,
        filename="paper.pdf",
        stored_path=tmp_path / "paper.pdf",
        status=DocumentStatus.READY,
        authors=("Aksoy",),
        year=2024,
    )
    repos.source_segments.create(
        document_id=document.id,
        chunk_index=0,
        text="Motivation improves persistence in learning tasks.",
        page_start=5,
        source_label="paper.pdf",
        extraction_method=ExtractionMethod.TEXT,
        metadata={"authors": ["Aksoy"], "year": 2024},
    )

    retriever = HybridRetriever(
        bm25_store=BM25Store(repos.source_segments),
        vector_store=VectorStore(repos.source_segments),
        reranker=CrossEncoderReranker(),
    )
    results = retriever.retrieve(
        query="What improves persistence?",
        active_document_ids=[document.id],
        top_k=3,
    )
    answer = await GroundedGenerator(prompt_manager=PromptManager()).generate(
        mode=GenerationMode.QA,
        query="What improves persistence?",
        retrieval_results=results,
    )

    assert answer.fallback_used is False
    assert answer.citations[0].source_segment_id == results[0].source_segment.id
    assert "(Aksoy, 2024)" in answer.sections[0].blocks[0]
