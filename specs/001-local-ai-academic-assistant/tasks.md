# Tasks: Local-First AI Academic Assistant

**Input**: Design documents from `/specs/001-local-ai-academic-assistant/`  
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/openapi.yaml](./contracts/openapi.yaml), [quickstart.md](./quickstart.md)

**Tests**: Include tests before implementation for grounding, citations, ingestion failures, empty retrieval, API contracts, and export because these are the core safety and quality requirements.

**Organization**: Tasks are grouped by user story so each increment can be implemented, tested, and reviewed independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other marked tasks in the same phase because it touches different files and has no dependency on incomplete tasks.
- **[Story]**: User story label used only inside user story phases.
- Every task includes the target file path for traceability.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the monorepo skeleton, dependency manifests, local runtime configuration, and basic developer commands.

- [x] T001 Create backend package structure with `__init__.py` files under `backend/app/`, `backend/app/api/`, `backend/app/common/`, `backend/app/ingestion/`, `backend/app/retrieval/`, `backend/app/llm/`, `backend/app/export/`, and `backend/app/storage/`
- [x] T002 Create backend test structure with placeholder fixture folders in `backend/tests/unit/`, `backend/tests/integration/`, `backend/tests/contract/`, and `backend/tests/fixtures/`
- [x] T003 Create frontend source structure in `frontend/src/components/`, `frontend/src/layouts/`, `frontend/src/pages/`, `frontend/src/services/`, `frontend/src/state/`, and `frontend/src/styles/`
- [x] T004 Create desktop shell structure in `desktop/src-tauri/`, `desktop/src-tauri/src/`, and `desktop/src-tauri/sidecars/`
- [x] T005 Define backend package metadata and dependencies in `backend/pyproject.toml`
- [x] T006 Define frontend package scripts and dependencies in `frontend/package.json`
- [x] T007 Define Tauri desktop package scripts in `desktop/package.json`
- [x] T008 Add Python test configuration in `backend/pytest.ini`
- [x] T009 [P] Add backend lint and type-check configuration in `backend/pyproject.toml`
- [x] T010 [P] Add frontend TypeScript configuration in `frontend/tsconfig.json`
- [x] T011 [P] Add frontend test configuration in `frontend/vitest.config.ts`
- [x] T012 [P] Add local environment example values in `.env.example`
- [x] T013 Add repository development commands and phase order to `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared types, configuration, storage, app bootstrapping, and API error behavior that every story depends on.

**Critical**: No user story implementation should begin until this phase is complete.

### Tests for Foundation

- [x] T014 [P] Add settings tests for local paths and model defaults in `backend/tests/unit/test_config.py`
- [x] T015 [P] Add error response tests for structured API errors in `backend/tests/unit/test_errors.py`
- [x] T016 [P] Add SQLite repository smoke tests in `backend/tests/unit/test_sqlite.py`
- [x] T017 [P] Add API health contract test in `backend/tests/contract/test_health_contract.py`

### Implementation for Foundation

- [x] T018 Create strongly typed shared domain objects in `backend/app/common/types.py`
- [x] T019 Implement local configuration loading in `backend/app/common/config.py`
- [x] T020 Implement structured application errors in `backend/app/common/errors.py`
- [x] T021 Implement structured logging setup without document-content leakage in `backend/app/common/logging.py`
- [x] T022 Implement safe local workspace path helpers in `backend/app/storage/paths.py`
- [x] T023 Implement SQLite connection and schema initialization in `backend/app/storage/sqlite.py`
- [x] T024 Implement repository interfaces for workspaces, documents, jobs, outputs, and citations in `backend/app/storage/repositories.py`
- [x] T025 Implement FastAPI application factory and health route in `backend/app/main.py`
- [x] T026 Add API router registration in `backend/app/api/__init__.py`
- [x] T027 Create frontend API client shell in `frontend/src/services/api.ts`
- [x] T028 Create frontend shared workspace state shell in `frontend/src/state/workspaceStore.ts`
- [x] T029 Create Tauri sidecar configuration placeholder in `desktop/src-tauri/tauri.conf.json`

**Checkpoint**: Backend boots, `/health` returns local readiness, SQLite initializes, and the frontend can import the API client.

---

## Phase 3: User Story 1 - Ask Grounded Questions (Priority: P1) MVP

**Goal**: User can ask questions about selected uploaded documents and receive structured, cited answers, or exactly `Bilgi bulunamadı` when evidence is missing.

**Independent Test**: Load fixture documents into storage, ask supported and unsupported questions through the API, verify cited academic output for supported questions and exact fallback for unsupported questions.

### Tests for User Story 1

- [x] T030 [P] [US1] Add contract test for `POST /generate` grounded response shape in `backend/tests/contract/test_generate_contract.py`
- [x] T031 [P] [US1] Add unit tests for query classification modes in `backend/tests/unit/test_query_classifier.py`
- [x] T032 [P] [US1] Add unit tests for prompt templates forbidding external knowledge in `backend/tests/unit/test_prompt_manager.py`
- [x] T033 [P] [US1] Add unit tests for context validation and exact `Bilgi bulunamadı` fallback in `backend/tests/unit/test_generator_grounding.py`
- [x] T034 [P] [US1] Add unit tests for citation mapping validation in `backend/tests/unit/test_citation_mapping.py`
- [x] T035 [P] [US1] Add integration test for supported Q&A with citations in `backend/tests/integration/test_grounded_qa.py`
- [x] T036 [P] [US1] Add integration test for unsupported Q&A fallback in `backend/tests/integration/test_no_context_fallback.py`

### Implementation for User Story 1

- [x] T037 [P] [US1] Implement Ollama local client adapter in `backend/app/llm/ollama_client.py`
- [x] T038 [P] [US1] Implement query classifier role in `backend/app/llm/query_classifier.py`
- [x] T039 [P] [US1] Implement academic prompt templates and mode routing in `backend/app/llm/prompt_manager.py`
- [x] T040 [P] [US1] Implement reranker wrapper in `backend/app/retrieval/reranker.py`
- [x] T041 [P] [US1] Implement BM25 search over stored source segments in `backend/app/retrieval/bm25_store.py`
- [x] T042 [P] [US1] Implement FAISS vector search over stored source segments in `backend/app/retrieval/vector_store.py`
- [x] T043 [US1] Implement hybrid retrieval merge and active-document filtering in `backend/app/retrieval/hybrid_retriever.py`
- [x] T044 [US1] Implement grounded answer generation and fallback enforcement in `backend/app/llm/generator.py`
- [x] T045 [US1] Implement academic output formatter that cannot add new claims in `backend/app/llm/formatter.py`
- [x] T046 [US1] Add citation persistence and source validation methods in `backend/app/storage/repositories.py`
- [x] T047 [US1] Implement generation endpoint in `backend/app/api/generation.py`
- [x] T048 [US1] Register generation routes in `backend/app/main.py`
- [x] T049 [US1] Add frontend output renderer for headings, paragraphs, bullets, and references in `frontend/src/components/WorkspaceOutput.tsx`
- [x] T050 [US1] Add frontend citation panel for source snippets and page references in `frontend/src/components/CitationPanel.tsx`
- [x] T051 [US1] Add frontend Q&A request flow in `frontend/src/pages/WorkspacePage.tsx`

**Checkpoint**: MVP works with preloaded fixture source segments: supported questions produce cited academic output, unsupported questions produce exactly `Bilgi bulunamadı`.

---

## Phase 4: User Story 2 - Build a Document Workspace (Priority: P2)

**Goal**: User can upload PDFs, process them locally, view document status, and select active documents for generation.

**Independent Test**: Upload readable, scanned, and corrupted PDFs; verify processing status, error handling, source segment creation, and active document selection.

### Tests for User Story 2

- [ ] T052 [P] [US2] Add contract tests for document upload, list, detail, delete, and active selection endpoints in `backend/tests/contract/test_documents_contract.py`
- [ ] T053 [P] [US2] Add unit tests for PDF text extraction in `backend/tests/unit/test_pdf_extractor.py`
- [ ] T054 [P] [US2] Add unit tests for OCR fallback decisions in `backend/tests/unit/test_ocr_service.py`
- [ ] T055 [P] [US2] Add unit tests for cleaning and chunk metadata in `backend/tests/unit/test_chunker.py`
- [ ] T056 [P] [US2] Add integration test for readable PDF ingestion in `backend/tests/integration/test_ingest_readable_pdf.py`
- [ ] T057 [P] [US2] Add integration test for corrupted PDF structured error handling in `backend/tests/integration/test_ingest_corrupted_pdf.py`
- [ ] T058 [P] [US2] Add integration test for active document filtering in `backend/tests/integration/test_active_documents.py`

### Implementation for User Story 2

- [ ] T059 [P] [US2] Implement PDF extraction with page metadata in `backend/app/ingestion/pdf_extractor.py`
- [ ] T060 [P] [US2] Implement OCR fallback service in `backend/app/ingestion/ocr_service.py`
- [ ] T061 [P] [US2] Implement text cleaning rules in `backend/app/ingestion/cleaner.py`
- [ ] T062 [P] [US2] Implement recursive chunking with source/page metadata in `backend/app/ingestion/chunker.py`
- [ ] T063 [P] [US2] Implement embedding service using local BGE-M3 configuration in `backend/app/ingestion/embedding_service.py`
- [ ] T064 [US2] Implement document ingestion orchestration in `backend/app/ingestion/document_processor.py`
- [ ] T065 [US2] Add document, segment, and job persistence methods in `backend/app/storage/repositories.py`
- [ ] T066 [US2] Implement document upload/list/detail/delete/active routes in `backend/app/api/documents.py`
- [ ] T067 [US2] Implement job status route in `backend/app/api/jobs.py`
- [ ] T068 [US2] Register document and job routes in `backend/app/main.py`
- [ ] T069 [US2] Add frontend document list and active selection UI in `frontend/src/components/DocumentList.tsx`
- [ ] T070 [US2] Add frontend upload and processing-status flow in `frontend/src/pages/WorkspacePage.tsx`
- [ ] T071 [US2] Wire document state updates in `frontend/src/state/workspaceStore.ts`

**Checkpoint**: Users can upload PDFs, see processing status, select active ready documents, and generation only uses those selected documents.

---

## Phase 5: User Story 3 - Generate Mode-Specific Academic Outputs (Priority: P3)

**Goal**: User can choose Q&A, Summarization, Argument Builder, or Literature Review mode and receive the correct academic output structure for that mode.

**Independent Test**: Use the same active document set in all four modes and verify each output uses the expected sections, citations, references, and missing-information behavior.

### Tests for User Story 3

- [ ] T072 [P] [US3] Add unit tests for mode-specific output schemas in `backend/tests/unit/test_output_modes.py`
- [ ] T073 [P] [US3] Add unit tests for summarization prompt requirements in `backend/tests/unit/test_summarization_prompt.py`
- [ ] T074 [P] [US3] Add unit tests for argument builder prompt requirements in `backend/tests/unit/test_argument_prompt.py`
- [ ] T075 [P] [US3] Add unit tests for literature review prompt requirements in `backend/tests/unit/test_literature_review_prompt.py`
- [ ] T076 [P] [US3] Add integration test for all mode outputs using fixture documents in `backend/tests/integration/test_mode_outputs.py`

### Implementation for User Story 3

- [ ] T077 [P] [US3] Add mode selector component in `frontend/src/components/ModeSelector.tsx`
- [ ] T078 [US3] Extend prompt manager with Q&A, Summarization, Argument Builder, and Literature Review templates in `backend/app/llm/prompt_manager.py`
- [ ] T079 [US3] Extend generator with partial-section fallback behavior in `backend/app/llm/generator.py`
- [ ] T080 [US3] Extend formatter with mode-specific section layouts in `backend/app/llm/formatter.py`
- [ ] T081 [US3] Extend generation endpoint validation for all modes in `backend/app/api/generation.py`
- [ ] T082 [US3] Wire mode selection into frontend workspace state in `frontend/src/state/workspaceStore.ts`
- [ ] T083 [US3] Render mode-specific output sections in `frontend/src/components/WorkspaceOutput.tsx`
- [ ] T084 [US3] Integrate mode selector into workspace layout in `frontend/src/pages/WorkspacePage.tsx`

**Checkpoint**: All four modes produce visibly distinct academic documents while preserving the same grounding and citation rules.

---

## Phase 6: User Story 4 - Export Academic Work (Priority: P4)

**Goal**: User can export generated academic output as editable `.docx` with headings, paragraphs, inline citations, and references preserved.

**Independent Test**: Generate a supported output and a fallback output, export both, open or inspect the `.docx`, and verify structure and references are preserved without adding unsupported content.

### Tests for User Story 4

- [ ] T085 [P] [US4] Add contract test for `POST /outputs/{outputId}/export` in `backend/tests/contract/test_exports_contract.py`
- [ ] T086 [P] [US4] Add unit tests for DOCX section and reference rendering in `backend/tests/unit/test_docx_exporter.py`
- [ ] T087 [P] [US4] Add integration test for supported output export in `backend/tests/integration/test_export_supported_output.py`
- [ ] T088 [P] [US4] Add integration test for fallback output export in `backend/tests/integration/test_export_fallback_output.py`

### Implementation for User Story 4

- [ ] T089 [US4] Implement DOCX exporter for structured academic output in `backend/app/export/docx_exporter.py`
- [ ] T090 [US4] Add export file persistence methods in `backend/app/storage/repositories.py`
- [ ] T091 [US4] Implement output retrieval and citation routes in `backend/app/api/generation.py`
- [ ] T092 [US4] Implement export route in `backend/app/api/exports.py`
- [ ] T093 [US4] Register export routes in `backend/app/main.py`
- [ ] T094 [US4] Add export action to frontend API client in `frontend/src/services/api.ts`
- [ ] T095 [US4] Add export button and export status UI in `frontend/src/components/WorkspaceOutput.tsx`
- [ ] T096 [US4] Wire export flow into workspace page in `frontend/src/pages/WorkspacePage.tsx`

**Checkpoint**: Users can export generated outputs to `.docx`; exported files preserve academic structure and references.

---

## Phase 7: Desktop Integration, Polish & Cross-Cutting Concerns

**Purpose**: Package the local desktop experience, verify offline behavior, improve UX, and harden the project.

- [ ] T097 [P] Add academic workspace layout shell with sidebar, main output area, and citation panel in `frontend/src/layouts/AcademicWorkspaceLayout.tsx`
- [ ] T098 [P] Add polished responsive workspace styling in `frontend/src/styles/academic-workspace.css`
- [ ] T099 Integrate workspace layout into `frontend/src/pages/WorkspacePage.tsx`
- [ ] T100 Configure Tauri sidecar launch behavior for the local FastAPI backend in `desktop/src-tauri/tauri.conf.json`
- [ ] T101 Add Tauri command or startup check for backend readiness in `desktop/src-tauri/src/main.rs`
- [ ] T102 [P] Add frontend smoke test for document/mode/output layout in `frontend/tests/workspace.spec.ts`
- [ ] T103 [P] Add offline validation notes and troubleshooting to `quickstart.md`
- [ ] T104 Run backend test suite and record any required fixes in `backend/tests/`
- [ ] T105 Run frontend test suite and record any required fixes in `frontend/tests/`
- [ ] T106 Validate the full quickstart flow and update `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start here.
- **Phase 2 Foundation**: Depends on Phase 1; blocks all user stories.
- **Phase 3 US1 MVP**: Depends on Phase 2; proves grounded Q&A and no-hallucination behavior.
- **Phase 4 US2 Document Workspace**: Depends on Phase 2; can be implemented after or alongside US1 if fixture data is used for US1.
- **Phase 5 US3 Modes**: Depends on Phase 3 for grounded generation and Phase 4 for real document selection.
- **Phase 6 US4 Export**: Depends on Phase 3 output structure; benefits from US3 mode structures.
- **Phase 7 Desktop/Polish**: Depends on the desired user stories being complete.

### User Story Dependencies

- **US1 Ask Grounded Questions**: First MVP. Can use fixture source segments before full PDF ingestion is complete.
- **US2 Build a Document Workspace**: Independent ingestion/document-management slice; generation must respect its active document selection.
- **US3 Generate Mode-Specific Academic Outputs**: Builds on US1 generation rules and US2 active documents.
- **US4 Export Academic Work**: Builds on persisted Academic Output and Citation entities.

### Within Each User Story

- Write tests first and confirm they fail.
- Implement models/types before repositories.
- Implement services before endpoints.
- Implement endpoints before frontend wiring.
- Validate the checkpoint before starting the next priority phase.

## Parallel Opportunities

- T009-T012 can run in parallel after project folders exist.
- T014-T017 can run in parallel because they cover separate foundation concerns.
- T030-T036 can run in parallel while US1 implementation starts on separate modules.
- T037-T042 can run in parallel before T043 merges retrieval behavior.
- T052-T058 can run in parallel for ingestion/document tests.
- T059-T063 can run in parallel before T064 orchestrates ingestion.
- T072-T076 can run in parallel for mode behavior tests.
- T085-T088 can run in parallel for export behavior tests.
- Frontend layout tasks T097-T099 can run after the core workspace components exist.

## Parallel Example: User Story 1

```text
Task: "Add unit tests for query classification modes in backend/tests/unit/test_query_classifier.py"
Task: "Add unit tests for prompt templates forbidding external knowledge in backend/tests/unit/test_prompt_manager.py"
Task: "Add unit tests for context validation and exact Bilgi bulunamadı fallback in backend/tests/unit/test_generator_grounding.py"
Task: "Implement Ollama local client adapter in backend/app/llm/ollama_client.py"
Task: "Implement BM25 search over stored source segments in backend/app/retrieval/bm25_store.py"
Task: "Implement FAISS vector search over stored source segments in backend/app/retrieval/vector_store.py"
```

## Implementation Strategy

### Recommended Way To Code This Project

Use **Spec Kit + vertical slices + TDD for safety-critical behavior**:

1. Complete Setup and Foundation.
2. Build US1 with fixture source segments before full PDF ingestion. This proves the hardest product promise: every answer is grounded or returns `Bilgi bulunamadı`.
3. Add US2 ingestion and document selection once generation safety exists.
4. Add US3 modes after the shared grounding pipeline is stable.
5. Add US4 export after output and citation structures stop changing.
6. Package the desktop shell last.

### MVP First

1. Finish Phase 1.
2. Finish Phase 2.
3. Finish Phase 3 only.
4. Stop and validate grounded Q&A independently.

### Incremental Delivery

1. MVP grounded Q&A.
2. Real PDF ingestion and active document management.
3. Multi-mode academic writing.
4. DOCX export.
5. Desktop packaging and UX polish.

## Notes

- Commit after each phase or a small logical group of tasks.
- Do not add internet search or cloud LLM behavior to core paths.
- Keep `Bilgi bulunamadı` exact in tests and implementation.
- Every source segment, retrieval result, citation, and export reference must carry document and page metadata.
- Avoid implementing future extensions until the initial workflow is stable.
