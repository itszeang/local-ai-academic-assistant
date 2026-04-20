# Data Model: Local-First AI Academic Assistant

**Date**: 2026-04-20  
**Feature**: Local-First AI Academic Assistant

## Entity: Workspace

Represents the local academic workspace for one user.

**Fields**:

- `id`: Stable local identifier.
- `name`: User-facing workspace name.
- `root_path`: Local storage root for PDFs, indexes, exports, and metadata.
- `created_at`, `updated_at`: Local timestamps.
- `settings_id`: Link to local model and processing settings.

**Relationships**:

- Has many Documents.
- Has many Generation Requests.
- Has many Academic Outputs.

**Validation Rules**:

- Workspace paths must resolve inside the configured local data directory.
- Workspace deletion must not remove external files unless they were imported into the workspace.

## Entity: Document

Represents an uploaded PDF.

**Fields**:

- `id`: Stable local identifier.
- `workspace_id`: Owning workspace.
- `filename`: Original file name.
- `stored_path`: Local imported PDF path.
- `fingerprint`: Content hash for duplicate detection.
- `title`, `authors`, `year`: Best-effort bibliographic metadata.
- `page_count`: Number of pages detected.
- `status`: `pending`, `processing`, `ready`, `failed`.
- `failure_reason`: Structured error when status is `failed`.
- `created_at`, `updated_at`: Local timestamps.

**Relationships**:

- Has many Source Segments.
- Has many Ingestion Jobs.
- May appear in many active document selections and generation requests.

**Validation Rules**:

- File must be a readable PDF before processing starts.
- Failed documents cannot be selected as active evidence.

**State Transitions**:

```text
pending -> processing -> ready
pending -> processing -> failed
failed -> processing -> ready
```

## Entity: Ingestion Job

Tracks PDF processing.

**Fields**:

- `id`: Stable local identifier.
- `document_id`: Document being processed.
- `status`: `queued`, `running`, `succeeded`, `failed`.
- `started_at`, `completed_at`: Local timestamps.
- `pages_processed`: Count of processed pages.
- `error_code`, `error_message`: Structured failure data.

**Relationships**:

- Belongs to one Document.

**Validation Rules**:

- A document may have only one running ingestion job at a time.
- Job completion must update document status.

## Entity: Source Segment

Represents a retrieved evidence unit derived from a document.

**Fields**:

- `id`: Stable local identifier.
- `document_id`: Source document.
- `chunk_index`: Ordered chunk number within document.
- `text`: Cleaned segment text.
- `page_start`, `page_end`: Page range used for citation mapping.
- `source_label`: Human-readable source label.
- `extraction_method`: `text`, `ocr`, or `mixed`.
- `embedding_ref`: Pointer to vector index entry.
- `bm25_ref`: Pointer to keyword corpus entry.
- `created_at`: Local timestamp.

**Relationships**:

- Belongs to one Document.
- May support many Citations.

**Validation Rules**:

- `text` must be non-empty after cleaning.
- Source metadata must include document identity and at least one page or equivalent location.

## Entity: Generation Request

Represents a user academic task.

**Fields**:

- `id`: Stable local identifier.
- `workspace_id`: Owning workspace.
- `mode`: `qa`, `summarization`, `argument_builder`, `literature_review`.
- `query`: User prompt or task.
- `language`: `tr`, `en`, or `auto`.
- `active_document_ids`: Ordered list of selected documents.
- `top_k`: Requested evidence count.
- `status`: `queued`, `retrieving`, `generating`, `formatting`, `succeeded`, `failed`.
- `created_at`, `completed_at`: Local timestamps.

**Relationships**:

- Belongs to one Workspace.
- Uses many Documents.
- Produces zero or one Academic Output.

**Validation Rules**:

- Must include at least one active ready document.
- Mode must be one of the supported v1 modes.
- Query must be non-empty except for full-document summarization, where the mode itself supplies the task.

## Entity: Retrieval Result

Represents an evidence candidate selected for a request.

**Fields**:

- `id`: Stable local identifier.
- `generation_request_id`: Request that produced it.
- `source_segment_id`: Source evidence segment.
- `bm25_score`: Keyword retrieval score.
- `vector_score`: Semantic retrieval score.
- `merged_score`: Combined retrieval score.
- `rerank_score`: Cross-encoder score.
- `rank`: Final rank.

**Relationships**:

- Belongs to one Generation Request.
- References one Source Segment.

**Validation Rules**:

- Source Segment document must be included in active document IDs.
- Final selected results must be sorted by rerank score and rank.

## Entity: Academic Output

Represents generated academic content.

**Fields**:

- `id`: Stable local identifier.
- `generation_request_id`: Request that produced it.
- `mode`: Copied from request for display/export.
- `title`: Output title.
- `sections`: Ordered structured sections with headings and body blocks.
- `references`: Ordered references used in the output.
- `fallback_used`: Boolean indicating whether `Bilgi bulunamadı` was returned.
- `created_at`: Local timestamp.

**Relationships**:

- Belongs to one Generation Request.
- Has many Citations.
- May have many Export Files.

**Validation Rules**:

- If `fallback_used` is true, output body must not include unsupported generated claims.
- Every substantive claim must map to at least one Citation unless the section explicitly reports missing information.

## Entity: Citation

Maps an output claim or paragraph to evidence.

**Fields**:

- `id`: Stable local identifier.
- `academic_output_id`: Output containing the claim.
- `source_segment_id`: Supporting source segment.
- `claim_path`: Section/block/claim identifier in the structured output.
- `inline_text`: Citation label shown to the user.
- `source_snippet`: Short supporting excerpt for review.
- `page_start`, `page_end`: Source page range.

**Relationships**:

- Belongs to one Academic Output.
- References one Source Segment.

**Validation Rules**:

- Citation source must come from a retrieval result for the same generation request.
- Citation label must be generated from available bibliographic metadata or a document fallback label.

## Entity: Export File

Represents a generated `.docx` export.

**Fields**:

- `id`: Stable local identifier.
- `academic_output_id`: Source output.
- `format`: `docx`.
- `path`: Local export path.
- `status`: `queued`, `running`, `succeeded`, `failed`.
- `created_at`: Local timestamp.
- `error_message`: Structured failure detail.

**Relationships**:

- Belongs to one Academic Output.

**Validation Rules**:

- Export path must resolve inside the workspace export directory.
- Export must preserve headings, paragraphs, inline citations, and references from the structured output.

## Entity: Local Settings

Stores configurable local resources.

**Fields**:

- `id`: Stable local identifier.
- `embedding_model`: Local embedding model name/path.
- `reranker_model`: Local reranker model name/path.
- `classifier_model`: Local LLM role model.
- `generator_model`: Local LLM role model.
- `formatter_model`: Local LLM role model.
- `ollama_base_url`: Local Ollama endpoint.
- `ocr_enabled`: Boolean.
- `chunk_size`, `chunk_overlap`: Chunking controls.

**Validation Rules**:

- Model settings must be local names or local paths.
- Cloud API keys are not part of core settings.
