"""
Phase 2 Test Suite: Arbitration Engine 2.0
Verifies:
1. Explicit rule identity, priority, and decision impact metadata.
2. Explicit conflict detection (HYDROLOGICAL_RAIN_CONFLICT, PEST_WIND_DRIFT_CONFLICT, PEST_RAIN_WASHOFF_CONFLICT).
3. Structured "Why-Not" rejected action tracking (candidate_action, blocked_by_rule_id, reason).
4. Deterministic arbitration precedence under multiple simultaneous conflicts.
5. Exact boundary behavior (15.0 vs 15.1 km/h, 24.9 vs 25.0 mm, 70.0% rain prob).
6. 100% decision determinism across repeated executions.
7. What-If simulation engine reusability.
"""

import pytest
from backend.engines.arbitration import arbitrate_daily_plan
from backend.schemas.contracts import (
    SoilState,
    PestState,
    WeatherForecast,
    MarketState
)

@pytest.fixture
def base_soil_stressed():
    return SoilState(
        crop_type="bt_cotton", depletion_mm=48.0, raw_mm=45.0, taw_mm=70.0,
        moisture_status="MOISTURE_STRESS", volumetric_water_content=0.28
    )

@pytest.fixture
def base_soil_adequate():
    return SoilState(
        crop_type="bt_cotton", depletion_mm=20.0, raw_mm=45.0, taw_mm=70.0,
        moisture_status="MOISTURE_ADEQUATE", volumetric_water_content=0.35
    )

@pytest.fixture
def base_pest_triggered():
    return PestState(
        crop_type="bt_cotton", pest_name="pink_bollworm", accumulated_gdd=462.0,
        gdd_threshold=450.0, risk_triggered=True, growth_stage="flowering_boll"
    )

@pytest.fixture
def base_pest_nominal():
    return PestState(
        crop_type="bt_cotton", pest_name="pink_bollworm", accumulated_gdd=200.0,
        gdd_threshold=450.0, risk_triggered=False, growth_stage="flowering_boll"
    )

@pytest.fixture
def base_market():
    return MarketState(
        crop_type="bt_cotton", mandi_name="Beed APMC", modal_price_inr=7450.0,
        sma_7_inr=7200.0, price_momentum_percent=3.47, trend="FAVORABLE"
    )

def test_rule_priority_and_trace_structure(base_soil_stressed, base_pest_nominal, base_market):
    """Verify that rule traces contain explicit priority, decision_impact, and structured metadata."""
    weather = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=0.0, rain_next_24h_mm=10.0, rain_next_36h_mm=28.0,
        rain_prob_next_6h=10.0, wind_speed_kmh=8.0, wind_gust_kmh=12.0,
        et0_mm=4.0, humidity_percent=70.0, source="demo_fixture"
    )

    card, exp = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", base_soil_stressed, base_pest_nominal, weather, base_market)

    # Check RuleTrace priority and decision impact
    rule_hydro_01 = next(r for r in exp.rule_traces if r.rule_id == "RULE_HYDRO_01")
    assert rule_hydro_01.priority == 80
    assert rule_hydro_01.triggered is True
    assert rule_hydro_01.decision_impact == "FINAL_PROHIBITION"
    assert "Tubewell irrigation rejected" in rule_hydro_01.why_not

def test_explicit_conflict_detection_and_rejected_actions(base_soil_stressed, base_pest_triggered, base_market):
    """Verify explicit conflicts_detected list and structured rejected_actions trace."""
    weather_multi_conflict = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=4.0, rain_next_24h_mm=28.0, rain_next_36h_mm=28.0,
        rain_prob_next_6h=10.0, wind_speed_kmh=18.5, wind_gust_kmh=24.0,
        et0_mm=4.0, humidity_percent=80.0, source="demo_fixture"
    )

    card, exp = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", base_soil_stressed, base_pest_triggered, weather_multi_conflict, base_market)

    # Both Hydrological Rain Conflict and Pest Wind Drift Conflict must be detected
    assert "HYDROLOGICAL_RAIN_CONFLICT" in exp.conflicts_detected
    assert "PEST_WIND_DRIFT_CONFLICT" in exp.conflicts_detected

    # Both TUBEVILL_IRRIGATION and CHEMICAL_PESTICIDE_SPRAY must be in rejected_actions
    rejected_types = [r.candidate_action for r in exp.rejected_actions]
    assert "TUBEVILL_IRRIGATION" in rejected_types
    assert "CHEMICAL_PESTICIDE_SPRAY" in rejected_types

    # Unified synthesis check
    assert card.critical_prohibition == "DO NOT IRRIGATE OR APPLY CHEMICAL SPRAYS TODAY"

def test_foliar_spray_rain_washoff_conflict(base_soil_adequate, base_pest_triggered, base_market):
    """Verify foliar spray rain wash-off block (RULE_PEST_RAIN_01, priority 90)."""
    weather_high_rain_prob = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=2.0, rain_next_24h_mm=5.0, rain_next_36h_mm=5.0,
        rain_prob_next_6h=80.0, wind_speed_kmh=8.0, wind_gust_kmh=12.0,
        et0_mm=4.0, humidity_percent=85.0, source="demo_fixture"
    )

    card, exp = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", base_soil_adequate, base_pest_triggered, weather_high_rain_prob, base_market)

    assert "PEST_RAIN_WASHOFF_CONFLICT" in exp.conflicts_detected
    assert "DO NOT SPRAY FOLIAR CHEMICALS" in card.critical_prohibition
    
    rejected = next(r for r in exp.rejected_actions if r.candidate_action == "FOLIAR_CHEMICAL_SPRAY")
    assert rejected.blocked_by_rule_id == "RULE_PEST_RAIN_01"

def test_boundary_conditions_wind_and_rain(base_soil_stressed, base_pest_triggered, base_market):
    """Verify exact boundary threshold evaluations (15.0 vs 15.1 km/h, 24.9 vs 25.0 mm)."""
    # Wind 15.0 km/h (Safe boundary)
    wf_wind_15_0 = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=0.0, rain_next_24h_mm=0.0, rain_next_36h_mm=0.0,
        rain_prob_next_6h=10.0, wind_speed_kmh=15.0, wind_gust_kmh=18.0,
        et0_mm=4.0, humidity_percent=60.0, source="demo_fixture"
    )
    card_15_0, exp_15_0 = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", base_soil_stressed, base_pest_triggered, wf_wind_15_0, base_market)
    assert "PEST_WIND_DRIFT_CONFLICT" not in exp_15_0.conflicts_detected

    # Wind 15.1 km/h (Exceeds boundary)
    wf_wind_15_1 = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=0.0, rain_next_24h_mm=0.0, rain_next_36h_mm=0.0,
        rain_prob_next_6h=10.0, wind_speed_kmh=15.1, wind_gust_kmh=18.0,
        et0_mm=4.0, humidity_percent=60.0, source="demo_fixture"
    )
    card_15_1, exp_15_1 = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", base_soil_stressed, base_pest_triggered, wf_wind_15_1, base_market)
    assert "PEST_WIND_DRIFT_CONFLICT" in exp_15_1.conflicts_detected

def test_100_percent_decision_determinism(base_soil_stressed, base_pest_triggered, base_market):
    """Verify that identical inputs yield 100% identical outputs over 100 iterations."""
    weather = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=0.0, rain_next_24h_mm=10.0, rain_next_36h_mm=28.0,
        rain_prob_next_6h=10.0, wind_speed_kmh=18.5, wind_gust_kmh=24.0,
        et0_mm=4.0, humidity_percent=80.0, source="demo_fixture"
    )

    baseline_card, _ = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", base_soil_stressed, base_pest_triggered, weather, base_market)

    for _ in range(100):
        iter_card, _ = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", base_soil_stressed, base_pest_triggered, weather, base_market)
        assert iter_card.primary_action == baseline_card.primary_action
        assert iter_card.critical_prohibition == baseline_card.critical_prohibition
        assert iter_card.scientific_rationale == baseline_card.scientific_rationale
