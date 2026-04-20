# Implementation Plan: Local-First AI Academic Assistant

**Branch**: `001-local-ai-academic-assistant` | **Date**: 2026-04-20 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-local-ai-academic-assistant/spec.md`

## Summary

Build a local-first desktop academic workspace for uploaded PDFs, grounded multi-mode academic generation, citation traceability, and `.docx` export. The implementation uses a desktop UI shell backed by a local FastAPI service, a Python academic RAG core, local embeddings and reranking, local Ollama generation, local file/vector/metadata storage, and explicit evidence gates that return `Bilgi bulunamadı` whenever selected documents do not support the request.

## Technical Context

**Language/Version**: Python 3.11+ for backend/RAG/export, TypeScript for desktop UI, Rust only for the desktop shell runtime  
**Primary Dependencies**: FastAPI, Uvicorn, Pydantic, pdfplumber, pytesseract, langchain-text-splitters, sentence-transformers (`BAAI/bge-m3` and `cross-encoder/ms-marco-MiniLM-L-6-v2`), faiss-cpu, rank_bm25, python-docx, Ollama, Tauri, React  
**Storage**: Local filesystem for PDFs/exports/models, SQLite for workspace metadata and generated outputs, FAISS indexes for vector search, persisted BM25 corpus data for keyword search  
**Testing**: pytest for backend unit/integration tests, contract tests against API schemas, UI tests with Playwright or Tauri-compatible browser automation, fixture PDFs for ingestion and grounding validation  
**Target Platform**: Local desktop application for Windows first, with architecture suitable for macOS/Linux later  
**Project Type**: Desktop app with local API sidecar and modular AI core  
**Performance Goals**: Prioritize correctness and traceability; typical readable 20-page PDF should become queryable within a practical study-session timeframe; UI should stay responsive during ingestion and generation jobs  
**Constraints**: Offline-first after local resources are installed; no cloud LLM calls in core behavior; all user data remains on device; outputs must be grounded in selected documents; missing support returns exactly `Bilgi bulunamadı`; citations must map to document/page metadata  
**Scale/Scope**: Single-user v1 workspace; multiple PDFs per workspace; initial modes are Q&A, Summarization, Argument Builder, and Literature Review; future flashcards, quizzes, knowledge maps, voice, subscriptions, and collaboration are excluded

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution file still contains template placeholders and defines no enforceable gates yet. This plan applies the active project/skill guardrails instead:

- Local-first academic RAG, not a general chatbot: PASS
- No cloud LLM calls in core behavior: PASS
- Uploaded-document-only generation with `Bilgi bulunamadı` fallback: PASS
- Source/page metadata preserved through ingestion, retrieval, generation, citations, and export: PASS
- Modular backend boundaries for ingestion, retrieval, reranking, LLM, export, and shared types: PASS
- Focused test plan for ingestion failures, empty retrieval, unsupported answers, citation mapping, and export: PASS

## Project Structure

### Documentation (this feature)

```text
specs/001-local-ai-academic-assistant/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- checklists/
|   `-- requirements.md
`-- contracts/
    `-- openapi.yaml
```

### Source Code (repository root)

```text
backend/
|-- app/
|   |-- main.py
|   |-- api/
|   |   |-- documents.py
|   |   |-- generation.py
|   |   |-- exports.py
|   |   `-- jobs.py
|   |-- common/
|   |   |-- config.py
|   |   |-- errors.py
|   |   |-- logging.py
|   |   `-- types.py
|   |-- ingestion/
|   |   |-- document_processor.py
|   |   |-- pdf_extractor.py
|   |   |-- ocr_service.py
|   |   |-- cleaner.py
|   |   |-- chunker.py
|   |   `-- embedding_service.py
|   |-- retrieval/
|   |   |-- bm25_store.py
|   |   |-- vector_store.py
|   |   |-- hybrid_retriever.py
|   |   `-- reranker.py
|   |-- llm/
|   |   |-- ollama_client.py
|   |   |-- query_classifier.py
|   |   |-- prompt_manager.py
|   |   |-- generator.py
|   |   `-- formatter.py
|   |-- export/
|   |   `-- docx_exporter.py
|   `-- storage/
|       |-- sqlite.py
|       |-- repositories.py
|       `-- paths.py
|-- tests/
|   |-- unit/
|   |-- integration/
|   |-- contract/
|   `-- fixtures/
`-- pyproject.toml

frontend/
|-- src/
|   |-- components/
|   |   |-- DocumentList.tsx
|   |   |-- ModeSelector.tsx
|   |   |-- WorkspaceOutput.tsx
|   |   `-- CitationPanel.tsx
|   |-- layouts/
|   |   `-- AcademicWorkspaceLayout.tsx
|   |-- pages/
|   |   `-- WorkspacePage.tsx
|   |-- services/
|   |   `-- api.ts
|   |-- state/
|   |   `-- workspaceStore.ts
|   `-- styles/
|       `-- academic-workspace.css
|-- tests/
`-- package.json

desktop/
|-- src-tauri/
|   |-- tauri.conf.json
|   |-- src/
|   `-- sidecars/
`-- README.md

data/
|-- documents/
|-- indexes/
|-- exports/
`-- academic_assistant.sqlite
```

**Structure Decision**: Use a Tauri desktop shell and React UI for the workspace experience, with a Python FastAPI sidecar owning all AI, ingestion, retrieval, export, and storage behavior. This keeps the local academic RAG system testable and modular while preserving a desktop application boundary for the user.

## Architecture

### Layer Responsibilities

- **UI Layer**: Desktop sidebar for document management and modes, main document-style output workspace, right citation panel, job progress states, export actions.
- **API Layer**: Local FastAPI service that validates requests, coordinates async ingestion/generation/export jobs, exposes source-grounded results, and never calls external services for core behavior.
- **Ingestion Pipeline**: PDF extraction, OCR fallback, cleaning, chunking, metadata attachment, embedding, FAISS indexing, BM25 corpus persistence.
- **Query Pipeline**: Query classification, query rewrite, document-scope filtering, hybrid retrieval, result merge, reranking, context building, source coverage validation, answer generation, academic formatting.
- **LLM Layer**: Local Ollama adapter with separate classification, generation, and formatting roles. Roles may use the same local model initially but remain independently configurable.
- **Storage Layer**: SQLite metadata, local file storage, FAISS vector indexes, BM25 keyword state, generated output records, citation mappings.
- **Export System**: Converts structured academic output and references into editable `.docx` files.

### Core Data Flow

```text
PDF upload -> ingestion job -> extraction/OCR -> chunks + metadata -> embeddings -> FAISS/BM25 -> ready document

User request -> active documents + mode -> classify/rewrite -> hybrid retrieval -> rerank -> context validation -> local LLM -> formatted academic output -> citations -> optional DOCX export
```

### Grounding Rules

- Retrieval is always filtered to active document IDs.
- Generation receives only retrieved context and citation metadata.
- If retrieval returns no relevant chunks, return exactly `Bilgi bulunamadı`.
- If a required section of a mode has insufficient evidence, that section must say `Bilgi bulunamadı` rather than infer.
- Formatting must not introduce new claims; it can only restructure generated, cited content.
- Citation engine validates that cited source IDs exist in the selected context before storing or exporting output.

### Mode Output Contracts

- **Q&A Mode**: Answer, supporting evidence, limitations, references.
- **Summarization Mode**: Overview, main findings, key concepts, limitations, references.
- **Argument Builder Mode**: Thesis/position, supporting arguments, counterarguments if supported, evidence map, references.
- **Literature Review Mode**: Themes, source synthesis, agreements/disagreements, gaps or limitations supported by documents, references.

## Phase 0: Research

Research decisions are captured in [research.md](./research.md). All technical unknowns from the plan were resolved with local-first defaults:

- Tauri + React UI with FastAPI sidecar
- pdfplumber first, pytesseract fallback
- Recursive character chunking with page/source metadata
- BGE-M3 embeddings, FAISS vector search, BM25 keyword search, cross-encoder reranking
- Ollama-only local LLM adapter with separable model roles
- SQLite + filesystem + FAISS/BM25 local persistence
- python-docx export

## Phase 1: Design & Contracts

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/openapi.yaml](./contracts/openapi.yaml)
- [quickstart.md](./quickstart.md)

## Post-Design Constitution Check

The design still passes the active local-first academic assistant guardrails:

- No cloud AI dependency is introduced.
- All generation paths require selected uploaded documents.
- Empty or unsupported retrieval paths return `Bilgi bulunamadı`.
- Every chunk, retrieval result, citation, and export reference carries source traceability.
- Backend modules follow single-responsibility boundaries.
- Planned tests cover failure paths and no-context behavior.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Desktop shell plus local API sidecar | The system needs a responsive desktop workspace and a Python-native AI/RAG backend | A single-process UI-only app would make PDF/OCR/vector/LLM/export concerns harder to isolate and test |
| Hybrid retrieval plus reranking | Academic answers require strong recall and citation precision | Vector-only or keyword-only retrieval increases the risk of missed evidence or weak citation mapping |
| Separate LLM roles | Classification, generation, and formatting have different prompts and validation gates | A single undifferentiated prompt path makes hallucination controls and mode-specific formatting harder to test |
