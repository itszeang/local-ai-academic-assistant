import { GraduationCap, LibraryBig } from "lucide-react";

import type { ProductMode } from "../features/tasks/taskConfig";
import { Button } from "./ui/button";

type ModeSwitcherProps = {
  value: ProductMode;
  onChange: (mode: ProductMode) => void;
};

const OPTIONS = [
  {
    value: "study" as const,
    label: "Study",
    description: "Fast practice from notes",
    icon: GraduationCap
  },
  {
    value: "academic" as const,
    label: "Academic",
    description: "Research and evidence",
    icon: LibraryBig
  }
];

export function ModeSwitcher({ value, onChange }: ModeSwitcherProps) {
  return (
    <div className="mode-switcher" role="tablist" aria-label="Product mode">
      {OPTIONS.map((option) => {
        const Icon = option.icon;
        const isSelected = option.value === value;
        return (
          <Button
            key={option.value}
            aria-selected={isSelected}
            className={isSelected ? "is-selected" : undefined}
            role="tab"
            variant={isSelected ? "default" : "ghost"}
            onClick={() => onChange(option.value)}
          >
            <Icon aria-hidden="true" size={18} />
            <span>
              <strong>{option.label}</strong>
              <small>{option.description}</small>
            </span>
          </Button>
        );
      })}
    </div>
  );
}
