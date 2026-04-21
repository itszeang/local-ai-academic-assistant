export type HealthResponse = {
  status: "ready" | "degraded";
  offline_ready: boolean;
  missing_local_resources: string[];
};

export type GenerateMode = "qa" | "summarization" | "argument_builder" | "literature_review";
export type DocumentStatus = "pending" | "processing" | "ready" | "failed";
export type JobStatus = "queued" | "running" | "succeeded" | "failed";

export type DocumentRecord = {
  id: string;
  workspace_id: string;
  filename: string;
  stored_path: string;
  status: DocumentStatus;
  fingerprint?: string | null;
  title?: string | null;
  authors: string[];
  year?: number | null;
  page_count?: number | null;
  failure_reason?: string | null;
  created_at: string;
  updated_at: string;
};

export type JobRecord = {
  id: string;
  kind: "ingestion" | "generation" | "export";
  status: JobStatus;
  document_id?: string | null;
  output_id?: string | null;
  progress?: number | null;
  error?: string | null;
  created_at: string;
  updated_at: string;
};

export type DocumentListResponse = {
  workspace_id: string;
  documents: DocumentRecord[];
  active_document_ids: string[];
};

export type DocumentUploadResponse = {
  workspace_id: string;
  document: DocumentRecord;
  job: JobRecord;
};

export type ActiveDocumentsResponse = {
  workspace_id: string;
  active_document_ids: string[];
  documents: DocumentRecord[];
};

export type GenerateRequest = {
  mode: GenerateMode;
  query: string;
  active_document_ids: string[];
  language?: "auto" | "tr" | "en";
  top_k?: number;
};

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

export type AcademicOutputResponse = {
  id: string;
  mode: GenerateMode;
  title: string;
  sections: Array<{
    heading: string;
    blocks: string[];
  }>;
  references: string[];
  citations: Citation[];
  fallback_used: boolean;
};

export type ExportJobResponse = {
  id: string;
  export_file_id: string;
  output_id: string;
  status: "queued" | "running" | "succeeded" | "failed";
  path?: string | null;
};

export type ApiClientOptions = {
  baseUrl?: string;
  fetchImpl?: typeof fetch;
};

export class ApiClient {
  private readonly baseUrl: string;
  private readonly fetchImpl: typeof fetch;

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl = options.baseUrl ?? "http://127.0.0.1:8765";
    this.fetchImpl = options.fetchImpl ?? window.fetch.bind(window);
  }

  async health(): Promise<HealthResponse> {
    const response = await this.fetchImpl(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed with status ${response.status}`);
    }
    return response.json() as Promise<HealthResponse>;
  }

  async generate(request: GenerateRequest): Promise<AcademicOutputResponse> {
    const response = await this.fetchImpl(`${this.baseUrl}/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(request)
    });
    if (!response.ok) {
      throw new Error(await this.errorMessage(response, "Generation failed"));
    }
    return response.json() as Promise<AcademicOutputResponse>;
  }

  async getOutput(outputId: string): Promise<AcademicOutputResponse> {
    const response = await this.fetchImpl(`${this.baseUrl}/outputs/${outputId}`);
    if (!response.ok) {
      throw new Error(await this.errorMessage(response, "Output lookup failed"));
    }
    return response.json() as Promise<AcademicOutputResponse>;
  }

  async getOutputCitations(outputId: string): Promise<Citation[]> {
    const response = await this.fetchImpl(`${this.baseUrl}/outputs/${outputId}/citations`);
    if (!response.ok) {
      throw new Error(await this.errorMessage(response, "Citation lookup failed"));
    }
    return response.json() as Promise<Citation[]>;
  }

  async exportOutput(outputId: string, filename?: string): Promise<ExportJobResponse> {
    const response = await this.fetchImpl(`${this.baseUrl}/outputs/${outputId}/export`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ filename })
    });
    if (!response.ok) {
      throw new Error(await this.errorMessage(response, "Export failed"));
    }
    return response.json() as Promise<ExportJobResponse>;
  }

  async listDocuments(workspaceId?: string): Promise<DocumentListResponse> {
    const url = new URL(`${this.baseUrl}/documents`);
    if (workspaceId) {
      url.searchParams.set("workspace_id", workspaceId);
    }
    const response = await this.fetchImpl(url);
    if (!response.ok) {
      throw new Error(await this.errorMessage(response, "Document list failed"));
    }
    return response.json() as Promise<DocumentListResponse>;
  }

  async uploadDocument(file: File, workspaceId?: string): Promise<DocumentUploadResponse> {
    const url = new URL(`${this.baseUrl}/documents`);
    url.searchParams.set("filename", file.name);
    if (workspaceId) {
      url.searchParams.set("workspace_id", workspaceId);
    }
    const response = await this.fetchImpl(url, {
      method: "POST",
      headers: {
        "Content-Type": file.type || "application/pdf"
      },
      body: file
    });
    if (!response.ok) {
      throw new Error(await this.errorMessage(response, "Document upload failed"));
    }
    return response.json() as Promise<DocumentUploadResponse>;
  }

  async deleteDocument(documentId: string): Promise<{ deleted: boolean; document_id: string }> {
    const response = await this.fetchImpl(`${this.baseUrl}/documents/${documentId}`, {
      method: "DELETE"
    });
    if (!response.ok) {
      throw new Error(await this.errorMessage(response, "Document delete failed"));
    }
    return response.json() as Promise<{ deleted: boolean; document_id: string }>;
  }

  async setActiveDocuments(documentIds: string[], workspaceId?: string): Promise<ActiveDocumentsResponse> {
    const response = await this.fetchImpl(`${this.baseUrl}/documents/active`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        workspace_id: workspaceId,
        document_ids: documentIds
      })
    });
    if (!response.ok) {
      throw new Error(await this.errorMessage(response, "Active document update failed"));
    }
    return response.json() as Promise<ActiveDocumentsResponse>;
  }

  async getJob(jobId: string): Promise<{ job: JobRecord }> {
    const response = await this.fetchImpl(`${this.baseUrl}/jobs/${jobId}`);
    if (!response.ok) {
      throw new Error(await this.errorMessage(response, "Job lookup failed"));
    }
    return response.json() as Promise<{ job: JobRecord }>;
  }

  private async errorMessage(response: Response, fallback: string): Promise<string> {
    try {
      const payload = (await response.json()) as { message?: string; detail?: string };
      return payload.message ?? payload.detail ?? `${fallback} with status ${response.status}`;
    } catch {
      return `${fallback} with status ${response.status}`;
    }
  }
}

export const apiClient = new ApiClient();
