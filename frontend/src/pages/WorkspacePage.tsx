import { useMemo, useState } from "react";

import { AcademicWorkspace } from "../components/AcademicWorkspace";
import { DocumentSidebar } from "../components/DocumentSidebar";
import { EvidencePanel, type Citation } from "../components/EvidencePanel";
import { ModeSwitcher } from "../components/ModeSwitcher";
import type { AcademicOutput } from "../components/OutputViewer";
import { StudyWorkspace } from "../components/StudyWorkspace";
import { taskById, type AcademicTask, type StudyTask } from "../features/tasks/taskConfig";
import { WorkspaceShell } from "../layouts/WorkspaceShell";
import { apiClient, type GenerateRequest } from "../services/api";
import { useWorkspaceStore } from "../state/workspaceStore";

export function WorkspacePage() {
  const activeDocumentIds = useWorkspaceStore((state) => state.activeDocumentIds);
  const productMode = useWorkspaceStore((state) => state.productMode);
  const setProductMode = useWorkspaceStore((state) => state.setProductMode);
  const studyTask = useWorkspaceStore((state) => state.studyTask);
  const academicTask = useWorkspaceStore((state) => state.academicTask);
  const setStudyTask = useWorkspaceStore((state) => state.setStudyTask);
  const setAcademicTask = useWorkspaceStore((state) => state.setAcademicTask);
  const [query, setQuery] = useState("");
  const [output, setOutput] = useState<AcademicOutput | null>(null);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<string | null>(null);

  const currentTask = useMemo(
    () => taskById(productMode === "study" ? studyTask : academicTask),
    [academicTask, productMode, studyTask]
  );

  function resetOutputForTaskChange() {
    setOutput(null);
    setCitations([]);
    setExportStatus(null);
  }

  function selectStudyTask(task: StudyTask) {
    setStudyTask(task);
    resetOutputForTaskChange();
  }

  function selectAcademicTask(task: AcademicTask) {
    setAcademicTask(task);
    resetOutputForTaskChange();
  }

  async function submitTask() {
    if (!currentTask.backendMode || !currentTask.isImplemented) {
      return;
    }
    const request: GenerateRequest = {
      mode: currentTask.backendMode,
      query,
      active_document_ids: activeDocumentIds,
      language: "auto"
    };
    setIsLoading(true);
    try {
      const response = await apiClient.generate(request);
      setOutput(response);
      setCitations(response.citations);
      setExportStatus(null);
    } finally {
      setIsLoading(false);
    }
  }

  async function exportOutput(currentOutput: AcademicOutput) {
    if (!currentOutput.id) {
      return;
    }
    setIsExporting(true);
    setExportStatus(null);
    try {
      const response = await apiClient.exportOutput(currentOutput.id);
      setExportStatus(response.path ? `Exported: ${response.path}` : `Export ${response.status}`);
    } finally {
      setIsExporting(false);
    }
  }

  const workspace =
    productMode === "study" ? (
      <StudyWorkspace
        task={currentTask}
        selectedTaskId={studyTask}
        query={query}
        output={output}
        activeDocumentCount={activeDocumentIds.length}
        isLoading={isLoading}
        onSelectTask={selectStudyTask}
        onQueryChange={setQuery}
        onSubmit={submitTask}
      />
    ) : (
      <AcademicWorkspace
        task={currentTask}
        selectedTaskId={academicTask}
        query={query}
        output={output}
        activeDocumentCount={activeDocumentIds.length}
        isLoading={isLoading}
        isExporting={isExporting}
        exportStatus={exportStatus}
        onSelectTask={selectAcademicTask}
        onQueryChange={setQuery}
        onSubmit={submitTask}
        onExport={exportOutput}
      />
    );

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p>Local-first AI</p>
          <h1>Academic Assistant</h1>
        </div>
        <ModeSwitcher
          value={productMode}
          onChange={(mode) => {
            setProductMode(mode);
            resetOutputForTaskChange();
          }}
        />
      </header>
      <WorkspaceShell
        productMode={productMode}
        documents={<DocumentSidebar />}
        workspace={workspace}
        evidence={<EvidencePanel citations={productMode === "academic" ? citations : []} compact={productMode === "study"} />}
      />
    </div>
  );
}
