import { create } from "zustand";

import type { AcademicTask, ProductMode, StudyTask } from "../features/tasks/taskConfig";
import type { DocumentRecord, GenerateMode, JobRecord } from "../services/api";

export type WorkspaceStatus = "idle" | "checking" | "ready" | "degraded" | "error";

export type WorkspaceState = {
  status: WorkspaceStatus;
  workspaceId?: string;
  productMode: ProductMode;
  studyTask: StudyTask;
  academicTask: AcademicTask;
  mode: GenerateMode;
  documents: DocumentRecord[];
  activeDocumentIds: string[];
  jobsById: Record<string, JobRecord>;
  setStatus: (status: WorkspaceStatus) => void;
  setWorkspaceId: (workspaceId: string) => void;
  setProductMode: (productMode: ProductMode) => void;
  setStudyTask: (studyTask: StudyTask) => void;
  setAcademicTask: (academicTask: AcademicTask) => void;
  setMode: (mode: GenerateMode) => void;
  setDocuments: (documents: DocumentRecord[]) => void;
  upsertDocument: (document: DocumentRecord) => void;
  removeDocument: (documentId: string) => void;
  setActiveDocumentIds: (documentIds: string[]) => void;
  upsertJob: (job: JobRecord) => void;
};

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  status: "idle",
  workspaceId: undefined,
  productMode: "academic",
  studyTask: "quick_qa",
  academicTask: "academic_qa",
  mode: "qa",
  documents: [],
  activeDocumentIds: [],
  jobsById: {},
  setStatus: (status) => set({ status }),
  setWorkspaceId: (workspaceId) => set({ workspaceId }),
  setProductMode: (productMode) => set({ productMode }),
  setStudyTask: (studyTask) => set({ studyTask }),
  setAcademicTask: (academicTask) => set({ academicTask }),
  setMode: (mode) => set({ mode }),
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
