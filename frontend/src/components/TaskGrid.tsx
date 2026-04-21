import type { TaskConfig, TaskId } from "../features/tasks/taskConfig";
import { TaskCard } from "./TaskCard";

type TaskGridProps = {
  title: string;
  description: string;
  tasks: TaskConfig[];
  selectedTaskId: TaskId;
  onSelectTask: (taskId: TaskId) => void;
};

export function TaskGrid({ title, description, tasks, selectedTaskId, onSelectTask }: TaskGridProps) {
  return (
    <section className="task-selection" aria-label={title}>
      <div className="section-heading">
        <p>{description}</p>
        <h2>{title}</h2>
      </div>
      <div className="task-grid">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            isSelected={task.id === selectedTaskId}
            onSelect={onSelectTask}
          />
        ))}
      </div>
    </section>
  );
}
