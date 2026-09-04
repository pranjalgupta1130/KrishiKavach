import {
  PlotProfile,
  DecisionCard,
  SimulationRequest,
  SimulationResponse,
  ExplainabilityDetails
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status} ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson.detail) {
          errorDetail = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        }
      } catch {
        // Fallback to HTTP status text
      }
      throw new ApiError(errorDetail, response.status);
    }

    return (await response.json()) as T;
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError('Unable to connect to KrishiKavach server. Please check your network connection.', 0);
  }
}

// 1. Create Plot Profile
export async function createPlot(plot: PlotProfile): Promise<PlotProfile> {
  return request<PlotProfile>('/api/v1/plots', {
    method: 'POST',
    body: JSON.stringify(plot),
  });
}

// 2. Fetch Plot Profile
export async function getPlot(plotId: string): Promise<PlotProfile> {
  return request<PlotProfile>(`/api/v1/plots/${encodeURIComponent(plotId)}`);
}

// 3. List Registered Plots
export async function listPlots(): Promise<PlotProfile[]> {
  return request<PlotProfile[]>('/api/v1/plots');
}

// 4. Fetch Daily Decision Card
export async function getDailyDecision(plotId: string): Promise<DecisionCard> {
  return request<DecisionCard>(`/api/v1/decision/daily/${encodeURIComponent(plotId)}`);
}

// 5. Simulate What-If Override
export async function simulateDecision(req: SimulationRequest): Promise<SimulationResponse> {
  return request<SimulationResponse>('/api/v1/decision/simulate', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

// 6. Fetch Explainability Audit Details
export async function getExplainability(decisionId: string): Promise<ExplainabilityDetails> {
  return request<ExplainabilityDetails>(`/api/v1/explainability/${encodeURIComponent(decisionId)}`);
}
