import { BookOpen, FileText, MessageSquareText, Scale } from "lucide-react";

import type { GenerateMode } from "../services/api";

type ModeOption = {
  value: GenerateMode;
  label: string;
  icon: typeof MessageSquareText;
};

const MODES: ModeOption[] = [
  { value: "qa", label: "Q&A", icon: MessageSquareText },
  { value: "summarization", label: "Summary", icon: FileText },
  { value: "argument_builder", label: "Argument", icon: Scale },
  { value: "literature_review", label: "Review", icon: BookOpen }
];

type ModeSelectorProps = {
  value: GenerateMode;
  onChange: (mode: GenerateMode) => void;
};

export function ModeSelector({ value, onChange }: ModeSelectorProps) {
  return (
    <div className="mode-selector" role="tablist" aria-label="Academic mode">
      {MODES.map((mode) => {
        const Icon = mode.icon;
        const isSelected = mode.value === value;
        return (
          <button
            key={mode.value}
            type="button"
            role="tab"
            aria-selected={isSelected}
            className={isSelected ? "selected" : undefined}
            onClick={() => onChange(mode.value)}
            title={mode.label}
          >
            <Icon aria-hidden="true" size={16} />
            <span>{mode.label}</span>
          </button>
        );
      })}
    </div>
  );
}
