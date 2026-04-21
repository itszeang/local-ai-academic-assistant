import type { ReactNode } from "react";

import type { ProductMode } from "../features/tasks/taskConfig";

type WorkspaceShellProps = {
  productMode: ProductMode;
  documents: ReactNode;
  workspace: ReactNode;
  evidence: ReactNode;
};

export function WorkspaceShell({ productMode, documents, workspace, evidence }: WorkspaceShellProps) {
  return (
    <div className="app-workspace-layout" data-product-mode={productMode}>
      <div className="workspace-shell">
        {documents}
        {workspace}
        {evidence}
      </div>
    </div>
  );
}
