export type OutputSection = {
  heading: string;
  blocks: string[];
};

export type AcademicOutput = {
  id?: string;
  title: string;
  sections: OutputSection[];
  references: string[];
  fallback_used: boolean;
};

type WorkspaceOutputProps = {
  output: AcademicOutput | null;
  isLoading?: boolean;
};

export function WorkspaceOutput({ output, isLoading = false }: WorkspaceOutputProps) {
  if (isLoading) {
    return <main className="workspace-output" aria-busy="true">Generating...</main>;
  }

  if (!output) {
    return <main className="workspace-output empty">No academic output yet.</main>;
  }

  return (
    <main className="workspace-output">
      <article>
        <h1>{output.title}</h1>
        {output.sections.map((section) => (
          <section key={section.heading}>
            <h2>{section.heading}</h2>
            {section.blocks.map((block, index) => (
              <p key={`${section.heading}-${index}`}>{block}</p>
            ))}
          </section>
        ))}
        {output.references.length > 0 && (
          <section>
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
