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
