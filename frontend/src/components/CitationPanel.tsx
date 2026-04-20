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

type CitationPanelProps = {
  citations: Citation[];
};

export function CitationPanel({ citations }: CitationPanelProps) {
  return (
    <aside className="citation-panel" aria-label="Citations">
      <h2>Citations</h2>
      {citations.length === 0 ? (
        <p>No citations for this output.</p>
      ) : (
        <ol>
          {citations.map((citation) => (
            <li key={citation.id}>
              <strong>{citation.inline_text}</strong>
              <span>
                Page {citation.page_start}
                {citation.page_end && citation.page_end !== citation.page_start
                  ? `-${citation.page_end}`
                  : ""}
              </span>
              <p>{citation.source_snippet}</p>
            </li>
          ))}
        </ol>
      )}
    </aside>
  );
}
