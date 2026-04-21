"""Grounded academic generation routes."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.common.errors import AppError, ErrorCode
from app.common.types import GeneratedAnswer, GenerationMode, Language, MISSING_INFORMATION_RESPONSE
from app.llm.generator import GroundedGenerator
from app.llm.ollama_client import OllamaClient
from app.retrieval.bm25_store import BM25Store
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.vector_store import VectorStore
from app.storage.repositories import RepositoryRegistry


router = APIRouter(tags=["generation"])


class GenerationRequestBody(BaseModel):
    mode: GenerationMode = GenerationMode.QA
    query: str = Field(min_length=1)
    active_document_ids: list[str] = Field(min_length=1)
    language: Language = Language.AUTO
    top_k: int = Field(default=8, ge=1, le=20)


@router.post("/generate")
async def generate_academic_output(
    body: GenerationRequestBody,
    request: Request,
) -> dict[str, Any]:
    repositories = RepositoryRegistry(request.app.state.database)
    retriever = HybridRetriever(
        bm25_store=BM25Store(repositories.source_segments),
        vector_store=VectorStore(repositories.source_segments),
        reranker=CrossEncoderReranker(),
    )
    retrieval_results = retriever.retrieve(
        query=body.query,
        active_document_ids=body.active_document_ids,
        top_k=body.top_k,
    )
    generator = GroundedGenerator(
        llm_client=OllamaClient(
            base_url=request.app.state.settings.ollama_base_url,
            timeout_seconds=request.app.state.settings.ollama_timeout_seconds,
        ),
        generator_model=request.app.state.settings.generator_model,
    )
    answer = await generator.generate(
        mode=body.mode,
        query=body.query,
        retrieval_results=retrieval_results,
        language=body.language,
    )
    output = repositories.academic_outputs.create(
        generation_request_id=f"request_{uuid.uuid4().hex}",
        mode=body.mode,
        title=answer.title,
        sections=_section_payload(answer),
        references=answer.references,
        fallback_used=answer.fallback_used,
    )

    allowed_source_segment_ids = {result.source_segment.id for result in retrieval_results}
    persisted_citations = []
    for citation in answer.citations:
        if not repositories.citations.is_retrieved_source(
            source_segment_id=citation.source_segment_id,
            allowed_source_segment_ids=allowed_source_segment_ids,
        ):
            raise AppError(
                code=ErrorCode.INTERNAL_ERROR,
                message="Generated citation did not map to retrieved context.",
                status_code=500,
            )
        persisted_citations.append(
            repositories.citations.create_for_retrieved_source(
                allowed_source_segment_ids=allowed_source_segment_ids,
                academic_output_id=output.id,
                source_segment_id=citation.source_segment_id,
                claim_path=citation.claim_path,
                inline_text=citation.inline_text,
                page_start=citation.page_start,
                source_snippet=citation.source_snippet,
                page_end=citation.page_end,
            )
        )

    return {
        "id": output.id,
        "mode": output.mode.value,
        "title": output.title,
        "sections": output.sections,
        "references": output.references,
        "citations": [
            {
                "id": citation.id,
                "document_id": _document_id_for_citation(retrieval_results, citation.source_segment_id),
                "source_segment_id": citation.source_segment_id,
                "claim_path": citation.claim_path,
                "inline_text": citation.inline_text,
                "source_snippet": citation.source_snippet,
                "page_start": citation.page_start,
                "page_end": citation.page_end,
            }
            for citation in persisted_citations
        ],
        "fallback_used": output.fallback_used,
    }


@router.get("/outputs/{output_id}")
async def get_academic_output(output_id: str, request: Request) -> dict[str, Any]:
    repositories = RepositoryRegistry(request.app.state.database)
    output = repositories.academic_outputs.get(output_id)
    if output is None:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message="Academic output was not found.",
            status_code=404,
            details={"output_id": output_id},
        )

    citations = repositories.citations.list_by_output(output.id)
    return _output_payload(output, citations, repositories)


@router.get("/outputs/{output_id}/citations")
async def get_output_citations(output_id: str, request: Request) -> list[dict[str, Any]]:
    repositories = RepositoryRegistry(request.app.state.database)
    output = repositories.academic_outputs.get(output_id)
    if output is None:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message="Academic output was not found.",
            status_code=404,
            details={"output_id": output_id},
        )
    return [
        _citation_payload(citation, repositories)
        for citation in repositories.citations.list_by_output(output.id)
    ]


def _section_payload(answer: GeneratedAnswer) -> list[dict[str, Any]]:
    if answer.fallback_used:
        return [{"heading": "Answer", "blocks": [MISSING_INFORMATION_RESPONSE]}]
    return [
        {
            "heading": section.heading,
            "blocks": section.blocks,
        }
        for section in answer.sections
    ]


def _document_id_for_citation(retrieval_results: list[Any], source_segment_id: str) -> str:
    for result in retrieval_results:
        if result.source_segment.id == source_segment_id:
            return str(result.source_segment.document_id)
    return ""


def _output_payload(output: Any, citations: list[Any], repositories: RepositoryRegistry) -> dict[str, Any]:
    return {
        "id": output.id,
        "mode": output.mode.value,
        "title": output.title,
        "sections": output.sections,
        "references": output.references,
        "citations": [_citation_payload(citation, repositories) for citation in citations],
        "fallback_used": output.fallback_used,
    }


def _citation_payload(citation: Any, repositories: RepositoryRegistry) -> dict[str, Any]:
    source_segment = repositories.source_segments.get(citation.source_segment_id)
    return {
        "id": citation.id,
        "document_id": source_segment.document_id if source_segment else "",
        "source_segment_id": citation.source_segment_id,
        "claim_path": citation.claim_path,
        "inline_text": citation.inline_text,
        "source_snippet": citation.source_snippet,
        "page_start": citation.page_start,
        "page_end": citation.page_end,
    }
