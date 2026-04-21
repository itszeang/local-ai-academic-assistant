import type { StudyTask, TaskConfig } from "../features/tasks/taskConfig";
import { STUDY_TASKS } from "../features/tasks/taskConfig";
import type { AcademicOutput } from "./OutputViewer";
import { OutputViewer } from "./OutputViewer";
import { PromptComposer } from "./PromptComposer";
import { TaskGrid } from "./TaskGrid";

type StudyWorkspaceProps = {
  task: TaskConfig;
  selectedTaskId: StudyTask;
  query: string;
  output: AcademicOutput | null;
  activeDocumentCount: number;
  isLoading: boolean;
  onSelectTask: (task: StudyTask) => void;
  onQueryChange: (query: string) => void;
  onSubmit: () => void;
};

export function StudyWorkspace({
  task,
  selectedTaskId,
  query,
  output,
  activeDocumentCount,
  isLoading,
  onSelectTask,
  onQueryChange,
  onSubmit
}: StudyWorkspaceProps) {
  return (
    <div className="workspace-main study-workspace">
      <div className="workspace-intro">
        <p>Study Mode</p>
        <h1>Practice and understand your notes faster.</h1>
      </div>
      <TaskGrid
        title="Choose a study task"
        description="Fast workflows for lecture notes, slides, and exam prep."
        tasks={STUDY_TASKS}
        selectedTaskId={selectedTaskId}
        onSelectTask={(taskId) => onSelectTask(taskId as StudyTask)}
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
        productMode="study"
        task={task}
        output={output}
        isLoading={isLoading}
        activeDocumentCount={activeDocumentCount}
      />
    </div>
  );
}
