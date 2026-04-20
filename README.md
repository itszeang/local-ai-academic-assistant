# Local AI Academic Assistant

Local-first desktop workspace for academic PDFs, grounded answers, structured academic writing, citation traceability, and DOCX export.

The project is intentionally built in phases. The first milestone is not a full desktop app; it is a trustworthy local RAG core that can answer only from uploaded documents and returns `Bilgi bulunamadı` when evidence is missing.

## Repository Layout

```text
backend/   Python FastAPI sidecar, ingestion, retrieval, local LLM orchestration, storage, export
frontend/  React workspace UI for documents, modes, output, and citations
desktop/   Tauri desktop shell and backend sidecar integration
specs/     Spec Kit feature specification, plan, contracts, and tasks
```

## Implementation Phases

1. Setup shared project structure and manifests.
2. Build the foundation: settings, errors, storage, app boot, health endpoint.
3. Build the MVP: grounded Q&A over prepared source segments.
4. Add PDF ingestion and active document management.
5. Add Summarization, Argument Builder, and Literature Review modes.
6. Add DOCX export.
7. Package and polish the desktop app.

Track detailed work in [tasks.md](./specs/001-local-ai-academic-assistant/tasks.md).

## Backend Development

```powershell
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
pytest
```

Run the local API after Phase 2 creates the app entry point:

```powershell
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

## Frontend Development

```powershell
cd frontend
npm install
npm run dev
npm test
```

## Desktop Development

```powershell
cd desktop
npm install
npm run dev
```

## Core Rules

- Core behavior is local-first and offline-capable after local resources are installed.
- User documents and generated content stay on the device.
- The system answers only from selected uploaded documents.
- Unsupported requests return exactly `Bilgi bulunamadı`.
- Every substantive claim must be traceable to a source document and page or equivalent source location.
- Do not add internet search, cloud LLM calls, collaboration, subscriptions, flashcards, quizzes, voice, or knowledge graphs in the initial version.
