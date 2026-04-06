export interface ApiWineResult {
  id?: number | null;
  name: string;
  producer?: string | null;
  country?: string | null;
  region?: string | null;
  appellation?: string | null;
  varietal?: string | null;
  color?: string | null;
  vintage?: string | null;
  price?: number | null;
  rating?: number | null;
  rating_count?: number | null;
  abv?: number | null;
  volume_ml?: number | null;
  reference_url?: string | null;
  image_url?: string | null;
  summary_note?: string | null;
  match_reason?: string | null;
}

export interface AskApiResponse {
  success: boolean;
  question: string;
  intent: string;
  answer_text: string;
  results: ApiWineResult[];
  meta: {
    grounded: boolean;
    clarification_needed: boolean;
    unsupported: boolean;
    reason?: string | null;
    result_count: number;
    source_row_count?: number | null;
    loaded_from?: string | null;
  };
}

export interface HealthApiResponse {
  status: string;
  dataset_loaded: boolean;
  row_count: number;
  loaded_from?: string | null;
  loaded_at?: string | null;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function getHealth(): Promise<HealthApiResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error("Backend health check failed.");
  }
  return response.json();
}

export async function askWineQuestion(question: string): Promise<AskApiResponse> {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error("Backend request failed.");
  }

  return response.json();
}
