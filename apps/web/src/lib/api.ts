/** API client for the Heatwave Platform. */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: unknown;
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = 'GET', headers = {}, body } = options;

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // Health
  health: () => fetchApi('/api/v1/health'),

  // Forecasts
  listForecasts: (params?: Record<string, string>) =>
    fetchApi(`/api/v1/forecasts${params ? '?' + new URLSearchParams(params) : ''}`),
  getForecast: (id: string) => fetchApi(`/api/v1/forecasts/${id}`),
  listForecastRuns: () => fetchApi('/api/v1/forecasts/runs/'),

  // Hazards
  listHazards: (params?: Record<string, string>) =>
    fetchApi(`/api/v1/hazards${params ? '?' + new URLSearchParams(params) : ''}`),
  getHazard: (id: string) => fetchApi(`/api/v1/hazards/${id}`),

  // Vulnerability
  listVulnerability: (params?: Record<string, string>) =>
    fetchApi(`/api/v1/vulnerability${params ? '?' + new URLSearchParams(params) : ''}`),
  getVulnerability: (id: string) => fetchApi(`/api/v1/vulnerability/${id}`),

  // Exposure
  listExposure: (params?: Record<string, string>) =>
    fetchApi(`/api/v1/exposure${params ? '?' + new URLSearchParams(params) : ''}`),
  getExposure: (id: string) => fetchApi(`/api/v1/exposure/${id}`),

  // Risk
  listRisk: (params?: Record<string, string>) =>
    fetchApi(`/api/v1/risk${params ? '?' + new URLSearchParams(params) : ''}`),
  getRisk: (id: string) => fetchApi(`/api/v1/risk/${id}`),
  explainRisk: (id: string) => fetchApi(`/api/v1/risk/${id}/explain`),
  getWardRiskSummary: (wardId: string) =>
    fetchApi(`/api/v1/risk/summary/ward/${wardId}`),

  // Wards
  listWards: (params?: Record<string, string>) =>
    fetchApi(`/api/v1/wards${params ? '?' + new URLSearchParams(params) : ''}`),
  getWard: (id: string) => fetchApi(`/api/v1/wards/${id}`),
  getWardRisk: (id: string) => fetchApi(`/api/v1/wards/${id}/risk`),
  listStates: () => fetchApi('/api/v1/wards/states/'),
  listCities: (stateId?: string) =>
    fetchApi(`/api/v1/wards/cities/${stateId ? '?' + new URLSearchParams({ state_id: stateId }) : ''}`),

  // Alerts
  listAlerts: (params?: Record<string, string>) =>
    fetchApi(`/api/v1/alerts${params ? '?' + new URLSearchParams(params) : ''}`),
  getActiveAlerts: () => fetchApi('/api/v1/alerts/active'),
  getAlert: (id: string) => fetchApi(`/api/v1/alerts/${id}`),

  // Models
  listModels: () => fetchApi('/api/v1/models'),
  getModel: (id: string) => fetchApi(`/api/v1/models/${id}`),
  getModelRuns: (id: string) => fetchApi(`/api/v1/models/${id}/runs`),
};
