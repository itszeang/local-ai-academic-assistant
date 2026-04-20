import { create } from "zustand";

export type WorkspaceStatus = "idle" | "checking" | "ready" | "degraded" | "error";

export type WorkspaceState = {
  status: WorkspaceStatus;
  activeDocumentIds: string[];
  setStatus: (status: WorkspaceStatus) => void;
  setActiveDocumentIds: (documentIds: string[]) => void;
};

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  status: "idle",
  activeDocumentIds: [],
  setStatus: (status) => set({ status }),
  setActiveDocumentIds: (activeDocumentIds) => set({ activeDocumentIds })
}));
