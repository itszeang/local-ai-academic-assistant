# OfflineScholar

Local-first academic assistant for working with your own PDFs.

OfflineScholar lets you upload academic PDFs, search only within your selected documents, generate grounded answers with citations, build literature-review style outputs, and export results to DOCX — all with local models.

---

## What it does

OfflineScholar is built for one core goal:

> help you read, reason over, and write from your own PDF sources without inventing information.

It is designed for academic workflows where trust matters more than fluency.

### Core capabilities

- Upload PDF documents into a local workspace
- Process documents into searchable chunks
- Ask grounded questions over selected PDFs
- Generate:
  - Q&A answers
  - Summaries
  - Argument-builder outputs
  - Literature review outputs
- Return citations tied to retrieved source segments
- Fall back to **“Bilgi bulunamadı”** when the requested information is not supported by the retrieved evidence
- Export generated outputs to `.docx`
- Run locally with Ollama-based generation models

---

## Why this project exists

Most AI writing tools are optimized for speed and smooth text generation.

Academic work needs something else:

- traceable evidence
- source-bounded answers
- explicit failure when evidence is missing
- local control over documents and models

OfflineScholar is built around those constraints.

---

## Architecture

This repository is split into three parts:

### 1. `backend/`
Local FastAPI backend that handles:

- PDF upload
- document ingestion
- OCR/text extraction
- chunking
- embeddings
- hybrid retrieval
- reranking
- grounded generation
- citation persistence
- DOCX export
- job tracking

### 2. `frontend/`
React + Vite user interface for:

- managing documents
- selecting active PDFs
- submitting academic tasks
- viewing outputs
- inspecting citations/evidence
- exporting results

### 3. `desktop/`
Tauri desktop shell that wraps the local app into a desktop experience.

---

## Tech stack

### Backend
- FastAPI
- SQLite
- pdfplumber
- pytesseract
- langchain-text-splitters
- sentence-transformers
- faiss-cpu
- rank-bm25
- python-docx
- httpx

### Frontend
- React
- Vite
- TypeScript
- Zustand
- lucide-react

### Desktop
- Tauri

### Local AI / Retrieval
- Ollama
- `BAAI/bge-m3` for embeddings
- `cross-encoder/ms-marco-MiniLM-L-6-v2` for reranking
- `llama3.1:8b` for classification / generation / formatting by default

---

## Retrieval and generation flow

The core pipeline is:

1. User uploads a PDF
2. The backend extracts text (and OCR when needed)
3. The document is cleaned and chunked
4. Chunks are embedded and indexed locally
5. Query is matched using hybrid retrieval:
   - BM25
   - vector similarity
   - reranking
6. Only retrieved evidence is sent to the local generator
7. Output is stored with citations
8. If sufficient support is not found, the system falls back instead of pretending certainty

---

## Supported generation modes

The backend currently supports these modes:

- `qa`
- `summarization`
- `argument_builder`
- `literature_review`

That means the app is not limited to simple question answering. It already has the right shape for source-grounded academic writing workflows.

---

## Local-first design

OfflineScholar is designed to keep the academic workflow on-device as much as possible.

### Local storage includes:
- uploaded PDFs
- generated indexes
- SQLite metadata
- exported DOCX files

### Default local data directory
```bash
./data