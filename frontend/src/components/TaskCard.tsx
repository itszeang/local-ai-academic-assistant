import { CheckCircle2 } from "lucide-react";

import type { TaskConfig, TaskId } from "../features/tasks/taskConfig";
import { cn } from "../lib/utils";
import { Badge } from "./ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";

type TaskCardProps = {
  task: TaskConfig;
  isSelected: boolean;
  onSelect: (taskId: TaskId) => void;
};

export function TaskCard({ task, isSelected, onSelect }: TaskCardProps) {
  const Icon = task.icon;
  return (
    <button
      className={cn("task-card-button", isSelected && "is-selected")}
      type="button"
      aria-pressed={isSelected}
      onClick={() => onSelect(task.id)}
    >
      <Card className="task-card">
        <CardHeader>
          <span className="task-card__icon">
            <Icon aria-hidden="true" size={18} />
          </span>
          <div>
            <CardTitle>{task.label}</CardTitle>
            <CardDescription>{task.description}</CardDescription>
          </div>
          {isSelected && <CheckCircle2 aria-hidden="true" className="task-card__check" size={18} />}
        </CardHeader>
        <CardContent>
          <Badge variant={task.isImplemented ? "success" : "secondary"}>
            {task.isImplemented ? "Ready" : "Coming soon"}
          </Badge>
        </CardContent>
      </Card>
    </button>
  );
}
