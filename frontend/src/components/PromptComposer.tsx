import { Sparkles } from "lucide-react";

import type { TaskConfig } from "../features/tasks/taskConfig";
import { Alert } from "./ui/alert";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";

type PromptComposerProps = {
  task: TaskConfig;
  value: string;
  activeDocumentCount: number;
  isLoading: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
};

export function PromptComposer({
  task,
  value,
  activeDocumentCount,
  isLoading,
  onChange,
  onSubmit
}: PromptComposerProps) {
  const hasDocuments = activeDocumentCount > 0;
  const canSubmit = task.isImplemented && hasDocuments && value.trim().length > 0 && !isLoading;
  const disabledReason = !task.isImplemented
    ? "This study feature is visible for product structure and will be wired in a later phase."
    : !hasDocuments
      ? "Select at least one ready document before generating."
      : null;

  return (
    <section className="prompt-composer" aria-label={`${task.label} prompt`}>
      <div className="prompt-composer__header">
        <div>
          <p>{task.shortLabel}</p>
          <h2>{task.promptLabel}</h2>
        </div>
        <span>{activeDocumentCount} selected</span>
      </div>
      {disabledReason && <Alert>{disabledReason}</Alert>}
      <Textarea
        aria-label={task.promptLabel}
        value={value}
        placeholder={task.promptPlaceholder}
        disabled={!task.isImplemented}
        onChange={(event) => onChange(event.target.value)}
      />
      <div className="prompt-composer__examples" aria-label="Example prompts">
        {task.examplePrompts.slice(0, 3).map((prompt) => (
          <Button key={prompt} variant="secondary" size="sm" onClick={() => onChange(prompt)}>
            {prompt}
          </Button>
        ))}
      </div>
      <Button className="prompt-composer__submit" disabled={!canSubmit} onClick={onSubmit}>
        <Sparkles aria-hidden="true" size={16} />
        {isLoading ? "Generating..." : task.primaryAction}
      </Button>
    </section>
  );
}
