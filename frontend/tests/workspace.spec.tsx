import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

beforeEach(() => {
  vi.resetModules();
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => {
      return new Response(
        JSON.stringify({
          workspace_id: "workspace_1",
          documents: [
            {
              id: "document_1",
              workspace_id: "workspace_1",
              filename: "paper.pdf",
              stored_path: "paper.pdf",
              status: "ready",
              authors: ["Aksoy"],
              page_count: 5,
              created_at: "2026-04-20T00:00:00Z",
              updated_at: "2026-04-20T00:00:00Z"
            }
          ],
          active_document_ids: ["document_1"]
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" }
        }
      );
    })
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});

test("renders dual-mode workspace, document, task, output, and evidence regions", async () => {
  const { WorkspacePage } = await import("../src/pages/WorkspacePage");

  render(<WorkspacePage />);

  expect(screen.getByRole("complementary", { name: "Documents" })).toBeTruthy();
  expect(screen.getByRole("tablist", { name: "Product mode" })).toBeTruthy();
  expect(screen.getByRole("complementary", { name: "Evidence" })).toBeTruthy();
  expect(screen.getByLabelText("Academic question")).toBeTruthy();
  expect(screen.getByRole("tab", { name: /Study/i })).toBeTruthy();
  expect(screen.getByRole("tab", { name: /Academic/i })).toBeTruthy();
  expect(screen.getByRole("button", { name: /Answer a Question/i })).toBeTruthy();
  expect(screen.getByRole("button", { name: /Summarize Document/i })).toBeTruthy();
  expect(screen.getByRole("button", { name: /Build an Argument/i })).toBeTruthy();
  expect(screen.getByRole("button", { name: /Literature Review/i })).toBeTruthy();

  await waitFor(() => {
    expect(screen.getByText("paper.pdf")).toBeTruthy();
  });

  fireEvent.click(screen.getByRole("tab", { name: /Study/i }));

  expect(screen.getByText("Practice and understand your notes faster.")).toBeTruthy();
  expect(screen.getByRole("button", { name: /Quick Q&A/i })).toBeTruthy();
  expect(screen.getByRole("button", { name: /Generate Flashcards/i })).toBeTruthy();
  expect(screen.getByRole("button", { name: /Generate Quiz/i })).toBeTruthy();
});
