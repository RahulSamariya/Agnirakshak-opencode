/** TypeScript domain types for the Heatwave Platform. */

export interface State {
  id: string;
  name: string;
  code: string;
  created_at: string;
  updated_at: string;
}

export interface City {
  id: string;
  name: string;
  state_id: string;
  population: number | null;
  created_at: string;
  updated_at: string;
}

export interface Ward {
  id: string;
  name: string;
  city_id: string;
  ward_code: string | null;
  population: number | null;
  created_at: string;
  updated_at: string;
}

export interface WardWithRisk extends Ward {
  current_risk_category: string | null;
  current_hsri: number | null;
}

export interface GridCell {
  id: string;
  cell_code: string;
  ward_id: string | null;
  latitude: number;
  longitude: number;
  created_at: string;
  updated_at: string;
}

export interface WeatherStation {
  id: string;
  name: string;
  station_code: string;
  latitude: number;
  longitude: number;
  elevation: number | null;
  created_at: string;
  updated_at: string;
}

export interface WeatherForecast {
  id: string;
  run_id: string;
  grid_cell_id: string;
  valid_time: string;
  lead_time_hours: number;
  air_temperature: number | null;
  relative_humidity: number | null;
  wind_speed: number | null;
  wind_direction: number | null;
  mean_radiant_temperature: number | null;
  pressure: number | null;
  precipitation_probability: number | null;
  created_at: string;
  updated_at: string;
}

export interface HazardAssessment {
  id: string;
  model_run_id: string;
  grid_cell_id: string;
  valid_time: string;
  utci_value: number;
  hazard_index: number;
  hazard_category: string;
  air_temperature: number | null;
  relative_humidity: number | null;
  wind_speed: number | null;
  mean_radiant_temperature: number | null;
  created_at: string;
  updated_at: string;
}

export interface VulnerabilityProfile {
  id: string;
  ward_id: string;
  model_run_id: string | null;
  vulnerability_index: number;
  score_details: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ExposureProfile {
  id: string;
  ward_id: string;
  model_run_id: string | null;
  exposure_index: number;
  score_details: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface RiskAssessment {
  id: string;
  risk_run_id: string;
  grid_cell_id: string;
  hazard_assessment_id: string;
  vulnerability_profile_id: string;
  exposure_profile_id: string;
  valid_time: string;
  hazard: number;
  vulnerability: number;
  exposure: number;
  hsri: number;
  risk_category: string;
  created_at: string;
  updated_at: string;
}

export interface WardRiskSummary {
  id: string;
  risk_run_id: string;
  ward_id: string;
  valid_time: string;
  mean_hazard: number;
  mean_vulnerability: number;
  mean_exposure: number;
  mean_hsri: number;
  max_hsri: number;
  min_hsri: number;
  risk_category: string;
  cell_count: number;
  high_risk_cell_count: number | null;
  created_at: string;
  updated_at: string;
}

export interface Alert {
  id: string;
  risk_run_id: string | null;
  ward_id: string | null;
  alert_level: string;
  alert_type: string;
  title: string;
  message: string;
  valid_from: string;
  valid_until: string;
  issued_at: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ActionRecommendation {
  id: string;
  alert_id: string;
  category: string;
  priority: string;
  title: string;
  description: string;
  target_audience: string | null;
  is_acknowledged: boolean;
  created_at: string;
  updated_at: string;
}

export interface ScientificModel {
  id: string;
  name: string;
  model_type: string;
  version: string;
  description: string | null;
  status: string;
  parameters: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ModelRun {
  id: string;
  model_id: string;
  run_start: string;
  run_end: string | null;
  status: string;
  input_parameters: Record<string, unknown> | null;
  output_summary: Record<string, unknown> | null;
  error_message: string | null;
  execution_time_ms: number | null;
  created_at: string;
  updated_at: string;
}

export type RiskCategory = 'low' | 'medium' | 'high';

export type AlertLevel = 'info' | 'warning' | 'critical' | 'emergency';
