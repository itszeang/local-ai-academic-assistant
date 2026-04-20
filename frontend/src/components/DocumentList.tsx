import { RefreshCw, Trash2, Upload } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { apiClient, type DocumentRecord } from "../services/api";
import { useWorkspaceStore } from "../state/workspaceStore";

function statusLabel(document: DocumentRecord): string {
  if (document.status === "failed") {
    return document.failure_reason ? `failed: ${document.failure_reason}` : "failed";
  }
  if (document.status === "ready" && document.page_count) {
    return `ready - ${document.page_count} pages`;
  }
  return document.status;
}

export function DocumentList() {
  const workspaceId = useWorkspaceStore((state) => state.workspaceId);
  const documents = useWorkspaceStore((state) => state.documents);
  const activeDocumentIds = useWorkspaceStore((state) => state.activeDocumentIds);
  const setWorkspaceId = useWorkspaceStore((state) => state.setWorkspaceId);
  const setDocuments = useWorkspaceStore((state) => state.setDocuments);
  const upsertDocument = useWorkspaceStore((state) => state.upsertDocument);
  const removeDocument = useWorkspaceStore((state) => state.removeDocument);
  const setActiveDocumentIds = useWorkspaceStore((state) => state.setActiveDocumentIds);
  const upsertJob = useWorkspaceStore((state) => state.upsertJob);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activeDocumentSet = useMemo(() => new Set(activeDocumentIds), [activeDocumentIds]);

  async function refreshDocuments() {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.listDocuments(workspaceId);
      setWorkspaceId(response.workspace_id);
      setDocuments(response.documents);
      setActiveDocumentIds(response.active_document_ids);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Document list failed.");
    } finally {
      setIsLoading(false);
    }
  }

  async function uploadDocument(file: File) {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.uploadDocument(file, workspaceId);
      setWorkspaceId(response.workspace_id);
      upsertDocument(response.document);
      upsertJob(response.job);
      await refreshDocuments();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Document upload failed.");
    } finally {
      setIsLoading(false);
    }
  }

  async function toggleActiveDocument(documentId: string) {
    const nextDocumentIds = activeDocumentSet.has(documentId)
      ? activeDocumentIds.filter((activeDocumentId) => activeDocumentId !== documentId)
      : [...activeDocumentIds, documentId];

    setActiveDocumentIds(nextDocumentIds);
    try {
      const response = await apiClient.setActiveDocuments(nextDocumentIds, workspaceId);
      setWorkspaceId(response.workspace_id);
      setActiveDocumentIds(response.active_document_ids);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Active document update failed.");
      await refreshDocuments();
    }
  }

  async function deleteDocument(documentId: string) {
    setError(null);
    try {
      await apiClient.deleteDocument(documentId);
      removeDocument(documentId);
      if (activeDocumentSet.has(documentId)) {
        const nextDocumentIds = activeDocumentIds.filter((activeDocumentId) => activeDocumentId !== documentId);
        const response = await apiClient.setActiveDocuments(nextDocumentIds, workspaceId);
        setActiveDocumentIds(response.active_document_ids);
      }
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Document delete failed.");
    }
  }

  useEffect(() => {
    void refreshDocuments();
  }, []);

  return (
    <aside className="document-list" aria-label="Documents">
      <header>
        <h2>Documents</h2>
        <button type="button" aria-label="Refresh documents" disabled={isLoading} onClick={refreshDocuments}>
          <RefreshCw aria-hidden="true" size={16} />
        </button>
      </header>

      <label className="document-upload">
        <Upload aria-hidden="true" size={16} />
        <span>Upload PDF</span>
        <input
          type="file"
          accept="application/pdf,.pdf"
          disabled={isLoading}
          onChange={(event) => {
            const file = event.target.files?.[0];
            event.currentTarget.value = "";
            if (file) {
              void uploadDocument(file);
            }
          }}
        />
      </label>

      {error && <p role="alert">{error}</p>}

      {documents.length === 0 ? (
        <p>No documents uploaded.</p>
      ) : (
        <ul>
          {documents.map((document) => (
            <li key={document.id}>
              <label>
                <input
                  type="checkbox"
                  checked={activeDocumentSet.has(document.id)}
                  onChange={() => void toggleActiveDocument(document.id)}
                />
                <span>{document.title || document.filename}</span>
              </label>
              <small>{statusLabel(document)}</small>
              <button
                type="button"
                aria-label={`Delete ${document.filename}`}
                onClick={() => void deleteDocument(document.id)}
              >
                <Trash2 aria-hidden="true" size={16} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
