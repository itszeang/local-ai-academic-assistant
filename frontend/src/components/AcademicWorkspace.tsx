import type { AcademicTask, TaskConfig } from "../features/tasks/taskConfig";
import { ACADEMIC_TASKS } from "../features/tasks/taskConfig";
import type { AcademicOutput } from "./OutputViewer";
import { OutputViewer } from "./OutputViewer";
import { PromptComposer } from "./PromptComposer";
import { TaskGrid } from "./TaskGrid";

type AcademicWorkspaceProps = {
  task: TaskConfig;
  selectedTaskId: AcademicTask;
  query: string;
  output: AcademicOutput | null;
  activeDocumentCount: number;
  isLoading: boolean;
  isExporting: boolean;
  exportStatus: string | null;
  onSelectTask: (task: AcademicTask) => void;
  onQueryChange: (query: string) => void;
  onSubmit: () => void;
  onExport: (output: AcademicOutput) => void;
};

export function AcademicWorkspace({
  task,
  selectedTaskId,
  query,
  output,
  activeDocumentCount,
  isLoading,
  isExporting,
  exportStatus,
  onSelectTask,
  onQueryChange,
  onSubmit,
  onExport
}: AcademicWorkspaceProps) {
  return (
    <div className="workspace-main academic-workspace">
      <div className="workspace-intro">
        <p>Academic Mode</p>
        <h1>Generate structured, document-grounded academic work.</h1>
      </div>
      <TaskGrid
        title="Choose an academic task"
        description="Research-oriented outputs with citations, evidence, and export."
        tasks={ACADEMIC_TASKS}
        selectedTaskId={selectedTaskId}
        onSelectTask={(taskId) => onSelectTask(taskId as AcademicTask)}
      />
      <PromptComposer
        task={task}
        value={query}
        activeDocumentCount={activeDocumentCount}
        isLoading={isLoading}
        onChange={onQueryChange}
        onSubmit={onSubmit}
      />
      <OutputViewer
        productMode="academic"
        task={task}
        output={output}
        isLoading={isLoading}
        isExporting={isExporting}
        exportStatus={exportStatus}
        activeDocumentCount={activeDocumentCount}
        onExport={onExport}
      />
    </div>
  );
}
