import { create } from "zustand";

import type { DocumentRecord, JobRecord } from "../services/api";

export type WorkspaceStatus = "idle" | "checking" | "ready" | "degraded" | "error";

export type WorkspaceState = {
  status: WorkspaceStatus;
  workspaceId?: string;
  documents: DocumentRecord[];
  activeDocumentIds: string[];
  jobsById: Record<string, JobRecord>;
  setStatus: (status: WorkspaceStatus) => void;
  setWorkspaceId: (workspaceId: string) => void;
  setDocuments: (documents: DocumentRecord[]) => void;
  upsertDocument: (document: DocumentRecord) => void;
  removeDocument: (documentId: string) => void;
  setActiveDocumentIds: (documentIds: string[]) => void;
  upsertJob: (job: JobRecord) => void;
};

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  status: "idle",
  workspaceId: undefined,
  documents: [],
  activeDocumentIds: [],
  jobsById: {},
  setStatus: (status) => set({ status }),
  setWorkspaceId: (workspaceId) => set({ workspaceId }),
  setDocuments: (documents) => set({ documents }),
  upsertDocument: (document) =>
    set((state) => ({
      documents: [
        document,
        ...state.documents.filter((existingDocument) => existingDocument.id !== document.id)
      ]
    })),
  removeDocument: (documentId) =>
    set((state) => ({
      documents: state.documents.filter((document) => document.id !== documentId),
      activeDocumentIds: state.activeDocumentIds.filter((activeDocumentId) => activeDocumentId !== documentId)
    })),
  setActiveDocumentIds: (activeDocumentIds) => set({ activeDocumentIds }),
  upsertJob: (job) =>
    set((state) => ({
      jobsById: {
        ...state.jobsById,
        [job.id]: job
      }
    }))
}));
