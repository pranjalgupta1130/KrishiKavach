from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime, timezone

class Location(BaseModel):
    district: str = Field(default="Beed", description="District name in Maharashtra")
    latitude: float = Field(default=18.99, description="Decimal latitude")
    longitude: float = Field(default=75.76, description="Decimal longitude")

class PlotProfile(BaseModel):
    plot_id: str = Field(..., description="Unique plot identifier e.g. tukaram_beed_01")
    farmer_name: str = Field(default="Tukaram", description="Farmer name")
    location: Location = Field(default_factory=Location)
    crop_type: str = Field(default="bt_cotton", description="Crop identifier: bt_cotton or soybean")
    sowing_date: str = Field(default="2026-06-25", description="Sowing date YYYY-MM-DD")
    soil_type: str = Field(default="medium_black_vertisol", description="Soil classification")
    plot_area_ha: float = Field(default=1.5, ge=0.1, description="Plot area in hectares")

class SoilState(BaseModel):
    crop_type: str = Field(..., description="Crop identifier")
    depletion_mm: float = Field(..., ge=0.0, description="Current root-zone soil water depletion in mm (Dr,i)")
    raw_mm: float = Field(..., ge=0.0, description="Readily Available Water limit in mm")
    taw_mm: float = Field(..., ge=0.0, description="Total Available Water capacity in mm")
    moisture_status: str = Field(..., description="MOISTURE_STRESS or MOISTURE_ADEQUATE")
    volumetric_water_content: float = Field(..., ge=0.0, le=1.0, description="Current volumetric soil moisture fraction")

class PestState(BaseModel):
    crop_type: str = Field(..., description="Crop identifier")
    pest_name: str = Field(..., description="Target pest: pink_bollworm or tobacco_caterpillar")
    accumulated_gdd: float = Field(..., ge=0.0, description="Cumulative Growing Degree Days")
    gdd_threshold: float = Field(..., ge=0.0, description="Emergence threshold degree days")
    risk_triggered: bool = Field(..., description="True if GDD >= threshold")
    growth_stage: str = Field(default="flowering_boll", description="Current crop growth stage")

class WeatherForecast(BaseModel):
    date: str = Field(..., description="Forecast date YYYY-MM-DD")
    temp_max: float = Field(..., description="Maximum temperature in deg C")
    temp_min: float = Field(..., description="Minimum temperature in deg C")
    temp_mean: float = Field(..., description="Mean temperature in deg C")
    rain_next_12h_mm: float = Field(..., ge=0.0, description="Expected rainfall next 12 hours in mm")
    rain_next_24h_mm: float = Field(..., ge=0.0, description="Expected rainfall next 24 hours in mm")
    rain_next_36h_mm: float = Field(..., ge=0.0, description="Expected rainfall next 36 hours in mm")
    rain_prob_next_6h: float = Field(..., ge=0.0, le=100.0, description="Rainfall probability in next 6 hours (0-100%)")
    wind_speed_kmh: float = Field(..., ge=0.0, description="Sustained wind speed in km/h")
    wind_gust_kmh: float = Field(..., ge=0.0, description="Peak wind gust speed in km/h")
    et0_mm: float = Field(..., ge=0.0, description="Reference Evapotranspiration in mm/day")
    humidity_percent: float = Field(..., ge=0.0, le=100.0, description="Relative humidity percentage")
    source: str = Field(..., description="Data provenance: live_api, cached, or demo_fixture")

class MarketState(BaseModel):
    crop_type: str = Field(..., description="Crop identifier")
    mandi_name: str = Field(..., description="APMC Mandi name e.g. Beed APMC")
    modal_price_inr: float = Field(..., ge=0.0, description="Daily modal price per quintal in INR")
    sma_7_inr: float = Field(..., ge=0.0, description="7-day Simple Moving Average in INR")
    price_momentum_percent: float = Field(..., description="Percentage difference from SMA7")
    trend: str = Field(..., description="FAVORABLE, NEUTRAL, or UNFAVORABLE")

class DecisionCard(BaseModel):
    decision_id: str = Field(..., description="Unique decision UUID")
    plot_id: str = Field(..., description="Plot identifier")
    date: str = Field(..., description="Decision date YYYY-MM-DD")
    primary_action: str = Field(..., description="Single unequivocal primary directive")
    critical_prohibition: str = Field(..., description="Single unequivocal critical prohibition")
    scientific_rationale: str = Field(..., description="Plain language numeric agronomic explanation")
    confidence_indicator: str = Field(..., description="Data freshness indicator e.g. Live Open-Meteo, SQLite Cache, Demo Fixture")
    explainability_id: str = Field(..., description="ID to fetch deep explainability drawer details")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    translations: Dict[str, Dict[str, str]] = Field(default_factory=dict, description="Vernacular translations (mr, hi)")

class RuleTrace(BaseModel):
    rule_id: str = Field(..., description="Identifier of the arbitration rule")
    rule_name: str = Field(..., description="Human-readable rule name")
    triggered: bool = Field(..., description="Whether rule conditions were satisfied")
    condition_evaluated: str = Field(..., description="Numeric expression evaluated")
    effect: str = Field(..., description="Action or prohibition output applied")

class ExplainabilityDetails(BaseModel):
    decision_id: str = Field(..., description="Corresponding decision ID")
    plot_id: str = Field(..., description="Plot identifier")
    date: str = Field(..., description="Decision date YYYY-MM-DD")
    soil_metrics: Dict[str, float] = Field(..., description="Depletion, RAW, TAW, FC, WP")
    spray_window_metrics: Dict[str, float] = Field(..., description="Wind speed, Wind limit, Rain 12h, Rain 36h, Rain prob 6h")
    pest_metrics: Dict[str, float] = Field(..., description="GDD accumulated, GDD threshold, Risk status")
    market_metrics: Dict[str, float] = Field(..., description="Modal price, SMA7, Momentum %")
    confidence_indicator: str = Field(..., description="Source of data")
    rule_traces: List[RuleTrace] = Field(..., description="Auditable trace of all arbitration rules evaluated")

class OverrideParams(BaseModel):
    wind_speed_kmh: Optional[float] = Field(default=None, ge=0.0, description="Override wind speed in km/h")
    rain_next_36h_mm: Optional[float] = Field(default=None, ge=0.0, description="Override 36h rainfall in mm")
    rain_next_12h_mm: Optional[float] = Field(default=None, ge=0.0, description="Override 12h rainfall in mm")
    rain_prob_next_6h: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Override 6h rain probability %")
    soil_depletion_mm: Optional[float] = Field(default=None, ge=0.0, description="Override soil depletion in mm")
    accumulated_gdd: Optional[float] = Field(default=None, ge=0.0, description="Override accumulated pest GDD")

class SimulationRequest(BaseModel):
    plot_id: str = Field(default="tukaram_beed_01", description="Target plot identifier")
    overrides: Optional[OverrideParams] = Field(default=None, description="Nested dictionary of parameter overrides")
    # Legacy flat fields preserved for compatibility
    custom_rain_36h_mm: Optional[float] = Field(default=None, ge=0.0, description="Override 36h rainfall in mm")
    custom_rain_12h_mm: Optional[float] = Field(default=None, ge=0.0, description="Override 12h rainfall in mm")
    custom_rain_prob_6h: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Override 6h rain probability %")
    custom_wind_speed_kmh: Optional[float] = Field(default=None, ge=0.0, description="Override wind speed in km/h")
    custom_soil_depletion_mm: Optional[float] = Field(default=None, ge=0.0, description="Override soil depletion in mm")
    custom_accumulated_gdd: Optional[float] = Field(default=None, ge=0.0, description="Override accumulated pest GDD")

class SimulationResponse(BaseModel):
    plot_id: str = Field(..., description="Target plot identifier")
    original_decision: DecisionCard = Field(..., description="Baseline decision without overrides")
    simulated_decision: DecisionCard = Field(..., description="Dynamic decision card with user overrides")
    is_flipped: bool = Field(..., description="True if action or prohibition changed")
    flip_reason: str = Field(..., description="Explanation of why the decision flipped")

class TranslationRequest(BaseModel):
    decision_card: DecisionCard = Field(..., description="Finalized decision card object")
    target_language: Optional[str] = Field(default=None, description="Single target language code ('mr' or 'hi')")
    target_languages: Optional[List[str]] = Field(default=None, description="List of ISO language codes ('mr' or 'hi')")

    @field_validator("target_language")
    @classmethod
    def validate_target_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in {"mr", "hi"}:
            raise ValueError(f"Unsupported language '{v}'. Only 'mr' and 'hi' are supported.")
        return v

    @field_validator("target_languages")
    @classmethod
    def validate_target_languages(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            for lang in v:
                if lang not in {"mr", "hi"}:
                    raise ValueError(f"Unsupported language '{lang}'. Only 'mr' and 'hi' are supported.")
        return v

class TranslationResponse(BaseModel):
    decision_id: str = Field(..., description="Decision ID")
    translations: Dict[str, Dict[str, str]] = Field(..., description="Map of lang -> translated fields")
