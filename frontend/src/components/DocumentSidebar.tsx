import { FileText, RefreshCw, Trash2, Upload } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { apiClient, type DocumentRecord } from "../services/api";
import { useWorkspaceStore } from "../state/workspaceStore";
import { Alert } from "./ui/alert";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";

function statusLabel(document: DocumentRecord): string {
  if (document.status === "failed") {
    return document.failure_reason ? `Failed: ${document.failure_reason}` : "Failed";
  }
  if (document.status === "ready" && document.page_count) {
    return `Ready - ${document.page_count} pages`;
  }
  return document.status;
}

function statusVariant(document: DocumentRecord): "success" | "warning" | "destructive" | "secondary" {
  if (document.status === "ready") {
    return "success";
  }
  if (document.status === "failed") {
    return "destructive";
  }
  if (document.status === "processing" || document.status === "pending") {
    return "warning";
  }
  return "secondary";
}

type DocumentCardProps = {
  document: DocumentRecord;
  isActive: boolean;
  onToggle: () => void;
  onDelete: () => void;
};

function DocumentCard({ document, isActive, onToggle, onDelete }: DocumentCardProps) {
  return (
    <Card className="document-card">
      <CardContent>
        <label className="document-card__main">
          <input type="checkbox" checked={isActive} onChange={onToggle} />
          <span className="document-card__icon">
            <FileText aria-hidden="true" size={16} />
          </span>
          <span>
            <strong>{document.title || document.filename}</strong>
            <small>{statusLabel(document)}</small>
          </span>
        </label>
        <div className="document-card__actions">
          <Badge variant={statusVariant(document)}>{document.status}</Badge>
          <Button
            type="button"
            aria-label={`Delete ${document.filename}`}
            size="icon"
            variant="ghost"
            onClick={onDelete}
          >
            <Trash2 aria-hidden="true" size={16} />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function DocumentSidebar() {
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
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const readyDocuments = documents.filter((document) => document.status === "ready");
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
    setUploadStatus(`Uploading ${file.name}...`);
    try {
      const response = await apiClient.uploadDocument(file, workspaceId);
      setWorkspaceId(response.workspace_id);
      upsertDocument(response.document);
      upsertJob(response.job);
      await refreshDocuments();
      setUploadStatus(
        response.document.status === "ready"
          ? `${response.document.filename} is ready.`
          : `${response.document.filename}: ${statusLabel(response.document)}`
      );
      setSelectedFile(null);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Document upload failed.");
      setUploadStatus(null);
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
    <aside className="document-sidebar" aria-label="Documents">
      <header className="panel-header">
        <div>
          <p>Sources</p>
          <h2>Documents</h2>
        </div>
        <Button type="button" aria-label="Refresh documents" disabled={isLoading} size="icon" variant="ghost" onClick={refreshDocuments}>
          <RefreshCw aria-hidden="true" size={16} />
        </Button>
      </header>

      <section className="document-upload" aria-label="Upload document">
        <label htmlFor="pdf-upload">
          <Upload aria-hidden="true" size={16} />
          <span>Add PDF</span>
        </label>
        <input
          id="pdf-upload"
          type="file"
          accept="application/pdf,.pdf"
          disabled={isLoading}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) {
              setSelectedFile(file);
              setUploadStatus(`Selected ${file.name}`);
              setError(null);
            }
          }}
        />
        <Button
          type="button"
          disabled={isLoading || !selectedFile}
          onClick={() => {
            if (selectedFile) {
              void uploadDocument(selectedFile);
            }
          }}
        >
          {isLoading ? "Working..." : "Upload"}
        </Button>
      </section>

      <div className="document-summary">
        <strong>{activeDocumentIds.length} selected</strong>
        <span>{readyDocuments.length} ready documents</span>
      </div>

      {uploadStatus && <p className="status-text" role="status">{uploadStatus}</p>}
      {error && <Alert variant="destructive">{error}</Alert>}

      {documents.length === 0 ? (
        <div className="document-empty">
          <h3>Add your first document</h3>
          <p>Upload lecture notes, slides, or academic papers. Answers stay grounded in selected PDFs.</p>
        </div>
      ) : (
        <div className="document-list">
          {documents.map((document) => (
            <DocumentCard
              key={document.id}
              document={document}
              isActive={activeDocumentSet.has(document.id)}
              onToggle={() => void toggleActiveDocument(document.id)}
              onDelete={() => void deleteDocument(document.id)}
            />
          ))}
        </div>
      )}
    </aside>
  );
}

export const DocumentList = DocumentSidebar;
