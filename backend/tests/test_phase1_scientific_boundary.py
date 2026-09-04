"""
Phase 1 Integration Tests: Scientific Model Integration & Contract Hardening
Verifies that:
1. Member 1's scientific engines (pest_engine.py, soil_engine.py, calibration_data.py)
   are cleanly consumed via Member 2's adapters (engines/pest.py, engines/soil_water.py).
2. The Arbitration Engine receives structured SoilState and PestState contracts
   WITHOUT recalculating GDD or soil water balance internally.
3. Model version provenance is preserved in DecisionCard and ExplainabilityDetails.
4. Existing public APIs (Daily Decision, What-If Simulation, Explainability, Translation) continue working seamlessly.
"""

import pytest
from backend.engines.pest_engine import calculate_pink_bollworm_risk, PINK_BOLLWORM_THRESHOLD_GDD
from backend.engines.soil_engine import calculate_soil_moisture_status, FIELD_CAPACITY, WILTING_POINT
from backend.engines.pest import calculate_pest_phenology
from backend.engines.soil_water import calculate_soil_water_balance
from backend.engines.arbitration import arbitrate_daily_plan
from backend.schemas.contracts import (
    SoilState,
    PestState,
    WeatherForecast,
    MarketState
)

def test_member1_pest_engine_consumed_by_adapter():
    """Verify Member 2 pest.py adapter directly consumes Member 1's pest_engine.py."""
    # Test Pink Bollworm (bt_cotton)
    pest_state = calculate_pest_phenology(
        crop_type="bt_cotton",
        accumulated_gdd=440.0,
        temp_max=34.0,
        temp_min=24.0
    )

    # Directly check against Member 1 calculation: mean (34+24)/2 = 29 -> daily GDD = 29 - 12 = 17 -> total = 457 >= 450
    assert pest_state.crop_type == "bt_cotton"
    assert pest_state.pest_name == "pink_bollworm"
    assert pest_state.accumulated_gdd == 457.0
    assert pest_state.gdd_threshold == PINK_BOLLWORM_THRESHOLD_GDD
    assert pest_state.risk_triggered is True
    assert "model_version" in pest_state.model_dump()
    assert pest_state.model_version["pest"] == "Member1-PinkBollworm-GDD-v1.0"

def test_member1_soil_engine_consumed_by_adapter():
    """Verify Member 2 soil_water.py adapter consumes Member 1's calibration & soil_engine.py."""
    # With root_depth_m = 0.35m (Bt-Cotton default), RAW = 45.5mm. Depletion = 48.0mm triggers stress.
    soil_state = calculate_soil_water_balance(
        crop_type="bt_cotton",
        depletion_mm=48.0,
        root_depth_m=0.35,
        precip_mm=0.0,
        et0_mm=4.5
    )

    assert soil_state.crop_type == "bt_cotton"
    assert soil_state.depletion_mm >= soil_state.raw_mm
    assert soil_state.moisture_status == "MOISTURE_STRESS"
    assert soil_state.depletion_exceeded is True
    assert "model_version" in soil_state.model_dump()
    assert "Member1-SoilEngine-FAO56" in soil_state.model_version["soil"]

def test_arbitration_consumes_structured_states_without_recalculation():
    """Verify Arbitration Engine relies on SoilState & PestState without recalculating GDD/depletion."""
    soil = SoilState(
        crop_type="bt_cotton", depletion_mm=48.0, raw_mm=45.0, taw_mm=70.0,
        moisture_status="MOISTURE_STRESS", volumetric_water_content=0.28
    )
    pest = PestState(
        crop_type="bt_cotton", pest_name="pink_bollworm", accumulated_gdd=462.0,
        gdd_threshold=450.0, risk_triggered=True, growth_stage="flowering_boll"
    )
    weather = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=0.0, rain_next_24h_mm=10.0, rain_next_36h_mm=28.0,
        rain_prob_next_6h=10.0, wind_speed_kmh=18.5, wind_gust_kmh=24.0,
        et0_mm=4.0, humidity_percent=70.0, source="demo_fixture"
    )
    market = MarketState(
        crop_type="bt_cotton", mandi_name="Beed APMC", modal_price_inr=7450.0,
        sma_7_inr=7200.0, price_momentum_percent=3.47, trend="FAVORABLE"
    )

    card, exp = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", soil, pest, weather, market)

    assert "DO NOT IRRIGATE OR APPLY CHEMICAL SPRAYS TODAY" in card.critical_prohibition
    assert card.model_version is not None
    assert exp.model_version is not None
    assert exp.soil_metrics["depletion_mm"] == 48.0
    assert exp.pest_metrics["accumulated_gdd"] == 462.0

def test_changing_scientific_state_flips_decision_without_changing_arbitration_code():
    """Verify that mutating input SoilState/PestState flips arbitration output dynamically."""
    weather_heavy_rain = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=0.0, rain_next_24h_mm=10.0, rain_next_36h_mm=28.0,
        rain_prob_next_6h=10.0, wind_speed_kmh=18.5, wind_gust_kmh=24.0,
        et0_mm=4.0, humidity_percent=70.0, source="demo_fixture"
    )
    weather_clear = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=0.0, rain_next_24h_mm=0.0, rain_next_36h_mm=0.0,
        rain_prob_next_6h=10.0, wind_speed_kmh=8.0, wind_gust_kmh=12.0,
        et0_mm=4.0, humidity_percent=70.0, source="demo_fixture"
    )
    market = MarketState(
        crop_type="bt_cotton", mandi_name="Beed APMC", modal_price_inr=7450.0,
        sma_7_inr=7200.0, price_momentum_percent=3.47, trend="FAVORABLE"
    )

    # State A: High Pest Risk + High Soil Stress + Rain/Wind Conflict -> Prohibitions
    soil_a = SoilState(
        crop_type="bt_cotton", depletion_mm=48.0, raw_mm=45.0, taw_mm=70.0,
        moisture_status="MOISTURE_STRESS", volumetric_water_content=0.28
    )
    pest_a = PestState(
        crop_type="bt_cotton", pest_name="pink_bollworm", accumulated_gdd=462.0,
        gdd_threshold=450.0, risk_triggered=True, growth_stage="flowering_boll"
    )
    card_a, _ = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", soil_a, pest_a, weather_heavy_rain, market)

    # State B: Nominal Pest Risk + Adequate Soil Moisture + Clear Weather -> No Prohibitions
    soil_b = SoilState(
        crop_type="bt_cotton", depletion_mm=20.0, raw_mm=45.0, taw_mm=70.0,
        moisture_status="MOISTURE_ADEQUATE", volumetric_water_content=0.35
    )
    pest_b = PestState(
        crop_type="bt_cotton", pest_name="pink_bollworm", accumulated_gdd=200.0,
        gdd_threshold=450.0, risk_triggered=False, growth_stage="flowering_boll"
    )
    card_b, _ = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", soil_b, pest_b, weather_clear, market)

    assert card_a.primary_action != card_b.primary_action
    assert card_a.critical_prohibition != card_b.critical_prohibition
    assert "DO NOT IRRIGATE" in card_a.critical_prohibition
    assert "NO CRITICAL PROHIBITIONS" in card_b.critical_prohibition

def test_daily_decision_api_returns_model_version_provenance(client):
    """Verify GET /api/v1/decision/daily/tukaram_beed_01 contains model provenance."""
    res = client.get("/api/v1/decision/daily/tukaram_beed_01")
    assert res.status_code == 200
    card = res.json()
    assert "model_version" in card
    assert card["model_version"] is not None
    assert "pest" in card["model_version"]
    assert "soil" in card["model_version"]

def test_whatif_simulate_api_preserves_nested_overrides(client):
    """Verify POST /api/v1/decision/simulate works with nested overrides and model provenance."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "rain_next_36h_mm": 0.0
        }
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_flipped"] is True
    assert data["simulated_decision"]["model_version"] is not None
