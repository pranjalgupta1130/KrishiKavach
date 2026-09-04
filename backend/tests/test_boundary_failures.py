"""
Boundary Conditions & Edge-Case Failure Path Tests
Verifies exact decision threshold boundaries, API input validation,
and crash-proof behavior under malformed external data.
"""

import pytest
from backend.engines.arbitration import arbitrate_daily_plan
from backend.schemas.contracts import (
    SoilState,
    PestState,
    WeatherForecast,
    MarketState,
    SimulationRequest
)
from backend.services.weather_service import fetch_weather_forecast

def get_base_states():
    soil_stressed = SoilState(
        crop_type="bt_cotton", depletion_mm=48.0, raw_mm=45.0, taw_mm=70.0,
        moisture_status="MOISTURE_STRESS", volumetric_water_content=0.28
    )
    pest_triggered = PestState(
        crop_type="bt_cotton", pest_name="pink_bollworm", accumulated_gdd=462.0,
        gdd_threshold=450.0, risk_triggered=True, growth_stage="flowering_boll"
    )
    market = MarketState(
        crop_type="bt_cotton", mandi_name="Beed APMC", modal_price_inr=7450.0,
        sma_7_inr=7200.0, price_momentum_percent=3.47, trend="FAVORABLE"
    )
    return soil_stressed, pest_triggered, market

def test_rain_irrigation_boundary_24_9_vs_25_0():
    soil, pest, market = get_base_states()

    # 24.9 mm -> Just below 25.0 mm threshold -> Approved irrigation
    wf_24_9 = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=0.0, rain_next_24h_mm=10.0, rain_next_36h_mm=24.9,
        rain_prob_next_6h=10.0, wind_speed_kmh=8.0, wind_gust_kmh=12.0,
        et0_mm=4.0, humidity_percent=70.0, source="demo_fixture"
    )
    card_below, exp_below = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", soil, pest, wf_24_9, market)
    assert "DO NOT IRRIGATE" not in card_below.critical_prohibition

    # 25.0 mm -> Exact threshold -> Suppress irrigation
    wf_25_0 = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=0.0, rain_next_24h_mm=10.0, rain_next_36h_mm=25.0,
        rain_prob_next_6h=10.0, wind_speed_kmh=8.0, wind_gust_kmh=12.0,
        et0_mm=4.0, humidity_percent=70.0, source="demo_fixture"
    )
    card_exact, exp_exact = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", soil, pest, wf_25_0, market)
    assert "DO NOT IRRIGATE TODAY" in card_exact.critical_prohibition

def test_wind_speed_boundary_15_0_vs_15_1():
    soil, pest, market = get_base_states()

    # 15.0 km/h -> Safe boundary -> Spray approved
    wf_15_0 = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=0.0, rain_next_24h_mm=0.0, rain_next_36h_mm=0.0,
        rain_prob_next_6h=10.0, wind_speed_kmh=15.0, wind_gust_kmh=18.0,
        et0_mm=4.0, humidity_percent=60.0, source="demo_fixture"
    )
    card_safe, _ = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", soil, pest, wf_15_0, market)
    assert "DO NOT SPRAY PESTICIDES" not in card_safe.critical_prohibition

    # 15.1 km/h -> Exceeds 15.0 km/h limit -> Spray blocked
    wf_15_1 = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=0.0, rain_next_24h_mm=0.0, rain_next_36h_mm=0.0,
        rain_prob_next_6h=10.0, wind_speed_kmh=15.1, wind_gust_kmh=18.0,
        et0_mm=4.0, humidity_percent=60.0, source="demo_fixture"
    )
    card_blocked, _ = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", soil, pest, wf_15_1, market)
    assert "DO NOT SPRAY PESTICIDES OR CHEMICALS" in card_blocked.critical_prohibition

def test_multiple_simultaneous_conflicts_synthesis():
    soil, pest, market = get_base_states()

    # Heavy rain (28mm in 36h) AND High wind (18.5 km/h) trigger simultaneously
    wf_multi = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=4.0, rain_next_24h_mm=28.0, rain_next_36h_mm=28.0,
        rain_prob_next_6h=65.0, wind_speed_kmh=18.5, wind_gust_kmh=24.0,
        et0_mm=4.0, humidity_percent=80.0, source="demo_fixture"
    )

    card, _ = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", soil, pest, wf_multi, market)

    # Must produce ONE unified prohibition and ONE unified action without naive string concatenation
    assert card.critical_prohibition == "DO NOT IRRIGATE OR APPLY CHEMICAL SPRAYS TODAY"
    assert card.primary_action == "Clear field drainage trenches immediately and deploy biological pheromone traps"

def test_api_negative_parameter_validation(client):
    # Invalid negative wind speed must trigger HTTP 422 validation error
    payload = {
        "plot_id": "tukaram_beed_01",
        "custom_wind_speed_kmh": -15.0
    }
    response = client.post("/api/v1/decision/simulate", json=payload)
    assert response.status_code == 422
