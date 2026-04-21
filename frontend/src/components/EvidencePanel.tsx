import { Quote } from "lucide-react";

import { Badge } from "./ui/badge";
import { Card, CardContent } from "./ui/card";

export type Citation = {
  id: string;
  document_id: string;
  source_segment_id: string;
  claim_path: string;
  inline_text: string;
  source_snippet: string;
  page_start: number;
  page_end?: number | null;
};

type EvidencePanelProps = {
  citations: Citation[];
  compact?: boolean;
};

export function EvidencePanel({ citations, compact = false }: EvidencePanelProps) {
  return (
    <aside className={compact ? "evidence-panel evidence-panel--compact" : "evidence-panel"} aria-label="Evidence">
      <header className="panel-header">
        <div>
          <p>Trust layer</p>
          <h2>Evidence</h2>
        </div>
        <Badge variant={citations.length > 0 ? "success" : "secondary"}>{citations.length} sources</Badge>
      </header>
      {citations.length === 0 ? (
        <div className="evidence-empty">
          <Quote aria-hidden="true" size={24} />
          <h3>No evidence yet</h3>
          <p>Generate an academic output to inspect source snippets and page references.</p>
        </div>
      ) : (
        <ol className="evidence-list">
          {citations.map((citation) => (
            <li key={citation.id}>
              <Card className="evidence-card">
                <CardContent>
                  <div className="evidence-card__meta">
                    <strong>{citation.inline_text}</strong>
                    <Badge variant="secondary">
                      Page {citation.page_start}
                      {citation.page_end && citation.page_end !== citation.page_start ? `-${citation.page_end}` : ""}
                    </Badge>
                  </div>
                  <p>{citation.source_snippet}</p>
                </CardContent>
              </Card>
            </li>
          ))}
        </ol>
      )}
    </aside>
  );
}

export const CitationPanel = EvidencePanel;
