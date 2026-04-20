# Research: Local-First AI Academic Assistant

**Date**: 2026-04-20  
**Feature**: Local-First AI Academic Assistant

## Decision: Tauri + React desktop UI with FastAPI sidecar

**Rationale**: Tauri gives a native desktop container and a polished web UI surface for the requested sidebar, document-style workspace, and citation panel. FastAPI keeps the academic RAG core in Python, where PDF extraction, OCR, embeddings, FAISS, BM25, reranking, Ollama integration, and DOCX export are strongest.

**Alternatives considered**:

- PyQt-only application: simpler packaging in one language, but weaker fit for the requested componentized frontend structure and modern document workspace UI.
- Browser-only local web app: easier development, but weaker desktop identity and local app lifecycle.
- Electron: mature, but heavier than needed for a local-first academic workspace.

## Decision: pdfplumber primary extraction with pytesseract OCR fallback

**Rationale**: Academic PDFs often contain selectable text, where direct extraction is faster and more faithful. Scanned PDFs need OCR fallback. The pipeline must record whether pages used direct extraction or OCR so citation confidence and processing errors are explainable.

**Alternatives considered**:

- OCR every page: slower and can degrade text quality for digital PDFs.
- Direct extraction only: fails on scanned academic material.
- Cloud OCR: conflicts with local-first privacy constraints.

## Decision: Recursive chunking at 1000-1200 characters with 200-character overlap

**Rationale**: This chunk size balances context completeness, citation granularity, and retrieval performance. Overlap preserves academic sentence continuity across chunk boundaries. Every chunk carries document ID, source file, page number, extraction method, and chunk index.

**Alternatives considered**:

- Very small chunks: precise citations but weak synthesis context.
- Very large chunks: better context but weaker retrieval precision and citation mapping.
- Page-only chunks: simple but inconsistent across dense papers and slides.

## Decision: BGE-M3 embeddings with FAISS vector search

**Rationale**: BGE-M3 is suitable for multilingual academic retrieval and works locally. FAISS provides fast local vector search without requiring a hosted vector database.

**Alternatives considered**:

- Hosted vector database: violates local-first design.
- Smaller local embedding model: lighter but lower multilingual and academic retrieval quality.
- Full-text search only: misses semantically related academic phrasing.

## Decision: BM25 plus vector hybrid retrieval

**Rationale**: Academic questions often include exact terms, abbreviations, author names, and concepts. BM25 preserves exact lexical matching while vector retrieval captures semantic matches. Merging both improves recall before reranking.

**Alternatives considered**:

- Vector-only retrieval: risks missing exact terminology.
- BM25-only retrieval: risks missing paraphrased concepts.
- Manual keyword filters only: too brittle for student and thesis workflows.

## Decision: Cross-encoder reranking before context selection

**Rationale**: Hybrid retrieval may return noisy candidates. A cross-encoder reranker improves final evidence precision and supports stronger citation mapping for academic answers.

**Alternatives considered**:

- Use raw vector/BM25 scores: faster but less reliable.
- Let the generator choose evidence: increases hallucination risk.

## Decision: Ollama-only local LLM adapter with separable roles

**Rationale**: The core product must run offline and keep user data on device. A thin Ollama adapter isolates local model calls. Classification, generation, and formatting roles are separated so each can have dedicated prompts, validation, and model configuration while initially using the same installed model if needed.

**Alternatives considered**:

- Cloud LLM APIs: conflict with local-first and privacy requirements.
- One prompt for every task: simpler, but harder to validate and maintain.
- Hard-coded model names: less portable across user machines.

## Decision: SQLite, local filesystem, FAISS indexes, and persisted BM25 state

**Rationale**: SQLite is reliable for local metadata and generated outputs. Filesystem storage is natural for PDFs and exports. FAISS and BM25 artifacts can be stored per workspace and rebuilt when needed.

**Alternatives considered**:

- JSON-only metadata: simple but weaker for querying jobs, documents, outputs, and citations.
- Client-server database: unnecessary for single-user local v1.
- In-memory indexes only: loses offline readiness after restart.

## Decision: Evidence-first generation guard

**Rationale**: The system is not a chatbot. If no selected document segment supports the request, generation should not run or should be forced to return exactly `Bilgi bulunamadı`. For partial support, unsupported sections must explicitly say `Bilgi bulunamadı`.

**Alternatives considered**:

- Ask the LLM to answer from memory: violates the zero-hallucination requirement.
- Generate a best-effort answer with caveats: still risks unsupported academic claims.
- Hide missing sections: less transparent for users preparing academic work.

## Decision: python-docx export from structured output

**Rationale**: Users need editable academic documents. Exporting from a structured output model preserves headings, paragraphs, citations, and references.

**Alternatives considered**:

- PDF export: less editable for thesis and assignment workflows.
- Plain text or Markdown only: loses academic document formatting expectations.
- UI screenshot export: not suitable for academic editing.
