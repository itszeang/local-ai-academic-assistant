# Quickstart: Local-First AI Academic Assistant

This quickstart describes the expected developer workflow for the first implementation phase.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Rust toolchain for Tauri
- Tesseract OCR installed locally and available on PATH
- Ollama installed locally
- Local Ollama models pulled before offline use

Example local model setup:

```powershell
ollama pull llama3.1:8b
```

## Backend Setup

```powershell
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
```

Run the local API:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

## Desktop Shell

```powershell
cd desktop
npm install
npm run tauri dev
```

The desktop shell starts the React workspace and connects to the local FastAPI sidecar.

## Manual Acceptance Flow

1. Start Ollama locally.
2. Start the backend service.
3. Start the desktop UI.
4. Upload at least one readable academic PDF.
5. Confirm the document reaches `ready` status.
6. Select the document as active.
7. Ask a question whose answer exists in the document.
8. Confirm the output has headings, paragraphs, citations, and references.
9. Open the citation panel and verify each citation maps to the source document and page.
10. Ask a question not supported by the active document.
11. Confirm the output is exactly `Bilgi bulunamadı`.
12. Export the supported output as `.docx`.
13. Open the exported document and verify headings, paragraph order, citations, and references.

## Test Commands

Backend:

```powershell
cd backend
pytest
```

Frontend:

```powershell
cd frontend
npm test
```

Contract checks:

```powershell
cd backend
pytest tests/contract
```

## Required Test Fixtures

- Readable academic PDF with known answerable facts.
- Scanned academic PDF page for OCR fallback.
- Corrupted PDF file.
- PDF with incomplete bibliographic metadata.
- Multi-document set with overlapping concepts.
- Query set with supported, unsupported, and partially supported prompts.

## Offline Validation

After dependencies and local models are installed:

1. Disconnect from the internet.
2. Start Ollama, backend, and desktop UI.
3. Run upload, query, citation review, and export flows.
4. Confirm no core feature requires a network request.
