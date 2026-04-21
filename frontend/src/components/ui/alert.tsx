import type { HTMLAttributes } from "react";

import { cn } from "../../lib/utils";

type AlertVariant = "default" | "destructive";

type AlertProps = HTMLAttributes<HTMLDivElement> & {
  variant?: AlertVariant;
};

export function Alert({ className, variant = "default", ...props }: AlertProps) {
  return <div className={cn("ui-alert", `ui-alert--${variant}`, className)} role="status" {...props} />;
}
