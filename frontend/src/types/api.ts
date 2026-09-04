export interface Location {
  district: string;
  latitude: number;
  longitude: number;
}

export interface PlotProfile {
  plot_id: string;
  farmer_name: string;
  location: Location;
  crop_type: string;
  sowing_date: string;
  soil_type: string;
  plot_area_ha: number;
}

export interface DecisionCardTranslation {
  primary_action: string;
  critical_prohibition: string;
  scientific_rationale: string;
}

export interface DecisionCard {
  decision_id: string;
  plot_id: string;
  date: string;
  primary_action: string;
  critical_prohibition: string;
  scientific_rationale: string;
  confidence_indicator: string;
  explainability_id: string;
  created_at: string;
  translations?: Record<string, DecisionCardTranslation>;
}

export interface RuleTrace {
  rule_id: string;
  rule_name: string;
  triggered: boolean;
  condition_evaluated: string;
  effect: string;
}

export interface ExplainabilityDetails {
  decision_id: string;
  plot_id: string;
  date: string;
  soil_metrics: Record<string, number>;
  spray_window_metrics: Record<string, number>;
  pest_metrics: Record<string, number>;
  market_metrics: Record<string, number>;
  confidence_indicator: string;
  rule_traces: RuleTrace[];
}

export interface OverrideParams {
  wind_speed_kmh?: number;
  rain_next_36h_mm?: number;
  rain_next_12h_mm?: number;
  rain_prob_next_6h?: number;
  soil_depletion_mm?: number;
  accumulated_gdd?: number;
}

export interface SimulationRequest {
  plot_id: string;
  overrides?: OverrideParams;
}

export interface SimulationResponse {
  plot_id: string;
  original_decision: DecisionCard;
  simulated_decision: DecisionCard;
  is_flipped: boolean;
  flip_reason: string;
}

export interface DecisionHistoryItem {
  decision_id: string;
  plot_id: string;
  date: string;
  primary_action: string;
  critical_prohibition: string;
  scientific_rationale: string;
  confidence_indicator: string;
  explainability_id: string;
  created_at: string;
  rule_traces?: RuleTrace[];
  model_version?: Record<string, string>;
}

export interface CropHealthResponse {
  plot_id: string;
  crop: string;
  crop_stage: string;
  days_after_sowing: number;
  pest: string;
  accumulated_gdd: number;
  threshold_gdd: number;
  pest_risk_high: boolean;
  model_version: string;
  provenance: string;
}

export interface MarketResponse {
  plot_id: string;
  crop: string;
  commodity: string;
  current_price: number;
  currency: string;
  unit: string;
  moving_average: number;
  momentum: number;
  trend: 'UP' | 'DOWN' | 'STABLE';
  source: string;
  fetched_at: string;
  data_status: 'LIVE' | 'CACHED' | 'FALLBACK';
}

export interface ScanResponse {
  observation: string;
  defect_type: string;
  severity: 'NOMINAL' | 'LOW' | 'MODERATE' | 'HIGH';
  confidence: number;
  affected_area_pct: number;
  analysis_method: string;
  observations: string[];
  possible_issue: string;
  needs_field_scouting: boolean;
  recommendation_note: string;
}

export interface CropScanResult extends ScanResponse {}

