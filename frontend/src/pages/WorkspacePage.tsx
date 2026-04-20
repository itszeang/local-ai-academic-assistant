import { useState } from "react";

import { CitationPanel, type Citation } from "../components/CitationPanel";
import { WorkspaceOutput, type AcademicOutput } from "../components/WorkspaceOutput";
import { apiClient, type GenerateRequest } from "../services/api";
import { useWorkspaceStore } from "../state/workspaceStore";

export function WorkspacePage() {
  const activeDocumentIds = useWorkspaceStore((state) => state.activeDocumentIds);
  const [query, setQuery] = useState("");
  const [output, setOutput] = useState<AcademicOutput | null>(null);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  async function submitQuestion() {
    const request: GenerateRequest = {
      mode: "qa",
      query,
      active_document_ids: activeDocumentIds,
      language: "auto"
    };
    setIsLoading(true);
    try {
      const response = await apiClient.generate(request);
      setOutput(response);
      setCitations(response.citations);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="workspace-page">
      <section className="question-panel">
        <textarea
          aria-label="Academic question"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <button type="button" disabled={!query.trim() || activeDocumentIds.length === 0} onClick={submitQuestion}>
          Ask
        </button>
      </section>
      <WorkspaceOutput output={output} isLoading={isLoading} />
      <CitationPanel citations={citations} />
    </div>
  );
}
