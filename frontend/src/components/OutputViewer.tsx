import { Download, FileSearch, Sparkles } from "lucide-react";

import type { ProductMode, TaskConfig } from "../features/tasks/taskConfig";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";

export type OutputSection = {
  heading: string;
  blocks: string[];
};

export type AcademicOutput = {
  id?: string;
  mode?: string;
  title: string;
  sections: OutputSection[];
  references: string[];
  fallback_used: boolean;
};

type OutputViewerProps = {
  productMode: ProductMode;
  task: TaskConfig;
  output: AcademicOutput | null;
  isLoading?: boolean;
  isExporting?: boolean;
  exportStatus?: string | null;
  activeDocumentCount: number;
  onExport?: (output: AcademicOutput) => void;
};

function EmptyStatePanel({ productMode, task, activeDocumentCount }: Pick<OutputViewerProps, "productMode" | "task" | "activeDocumentCount">) {
  if (activeDocumentCount === 0) {
    return (
      <Card className="empty-state-panel">
        <CardContent>
          <FileSearch aria-hidden="true" size={28} />
          <h2>Select a source to continue</h2>
          <p>Choose at least one ready document from the sidebar before generating an output.</p>
        </CardContent>
      </Card>
    );
  }

  if (!task.isImplemented) {
    return (
      <Card className="empty-state-panel">
        <CardContent>
          <Sparkles aria-hidden="true" size={28} />
          <h2>{task.label} is planned</h2>
          <p>This task is part of the Study Mode structure and can stay as a placeholder until its backend prompt is added.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="empty-state-panel">
      <CardContent>
        <Sparkles aria-hidden="true" size={28} />
        <h2>{productMode === "study" ? "Start studying from your notes" : "Start an academic task"}</h2>
        <p>{task.description}</p>
        <ul>
          {task.examplePrompts.slice(0, 3).map((prompt) => (
            <li key={prompt}>{prompt}</li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

export function OutputViewer({
  productMode,
  task,
  output,
  isLoading = false,
  isExporting = false,
  exportStatus = null,
  activeDocumentCount,
  onExport
}: OutputViewerProps) {
  if (isLoading) {
    return (
      <main className="output-viewer" aria-busy="true">
        <Card className="loading-panel">
          <CardContent>
            <span className="loading-dot" />
            <h2>{productMode === "study" ? "Studying your selected notes..." : "Finding relevant evidence..."}</h2>
            <p>{productMode === "study" ? "Generating a focused response." : "Generating a grounded academic output."}</p>
          </CardContent>
        </Card>
      </main>
    );
  }

  if (!output) {
    return (
      <main className="output-viewer empty">
        <EmptyStatePanel productMode={productMode} task={task} activeDocumentCount={activeDocumentCount} />
      </main>
    );
  }

  return (
    <main className="output-viewer">
      <article className="output-article">
        <header className="output-header">
          <div>
            <p>{task.label}</p>
            <h1>{output.title}</h1>
          </div>
          {productMode === "academic" && onExport && output.id && (
            <Button type="button" disabled={isExporting} variant="secondary" onClick={() => onExport(output)}>
              <Download aria-hidden="true" size={16} />
              {isExporting ? "Exporting..." : "Export DOCX"}
            </Button>
          )}
        </header>
        {exportStatus && <p className="status-text" role="status">{exportStatus}</p>}
        {output.fallback_used && (
          <Card className="unsupported-panel">
            <CardContent>
              <h2>Not enough evidence found</h2>
              <p>The selected documents do not contain enough support for this request.</p>
            </CardContent>
          </Card>
        )}
        {output.sections.map((section) => (
          <section className="output-section" key={section.heading}>
            <h2>{section.heading}</h2>
            {section.blocks.map((block, index) => (
              <p key={`${section.heading}-${index}`}>{block}</p>
            ))}
          </section>
        ))}
        {productMode === "academic" && output.references.length > 0 && (
          <section className="output-section references-list">
            <h2>References</h2>
            <ul>
              {output.references.map((reference) => (
                <li key={reference}>{reference}</li>
              ))}
            </ul>
          </section>
        )}
      </article>
    </main>
  );
}

export const WorkspaceOutput = OutputViewer;
