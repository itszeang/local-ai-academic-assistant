export type HealthResponse = {
  status: "ready" | "degraded";
  offline_ready: boolean;
  missing_local_resources: string[];
};

export type GenerateMode = "qa" | "summarization" | "argument_builder" | "literature_review";

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

export type ApiClientOptions = {
  baseUrl?: string;
  fetchImpl?: typeof fetch;
};

export class ApiClient {
  private readonly baseUrl: string;
  private readonly fetchImpl: typeof fetch;

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl = options.baseUrl ?? "http://127.0.0.1:8765";
    this.fetchImpl = options.fetchImpl ?? fetch;
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
      throw new Error(`Generation failed with status ${response.status}`);
    }
    return response.json() as Promise<AcademicOutputResponse>;
  }
}

export const apiClient = new ApiClient();
