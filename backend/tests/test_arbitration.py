from backend.engines.arbitration import arbitrate_daily_plan
from backend.schemas.contracts import (
    SoilState,
    PestState,
    WeatherForecast,
    MarketState
)
from backend.config.settings import settings

def test_hydrological_conflict_arbitration():
    soil_stressed = SoilState(
        crop_type="bt_cotton", depletion_mm=48.0, raw_mm=45.0, taw_mm=70.0,
        moisture_status="MOISTURE_STRESS", volumetric_water_content=0.28
    )
    pest_nominal = PestState(
        crop_type="bt_cotton", pest_name="pink_bollworm", accumulated_gdd=200.0,
        gdd_threshold=450.0, risk_triggered=False, growth_stage="flowering_boll"
    )
    weather_heavy_rain = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=10.0, rain_next_24h_mm=26.0, rain_next_36h_mm=28.0, # >= 25mm threshold!
        rain_prob_next_6h=40.0, wind_speed_kmh=10.0, wind_gust_kmh=15.0,
        et0_mm=4.0, humidity_percent=80.0, source="demo_fixture"
    )
    market = MarketState(
        crop_type="bt_cotton", mandi_name="Beed APMC", modal_price_inr=7450.0,
        sma_7_inr=7200.0, price_momentum_percent=3.47, trend="FAVORABLE"
    )

    card, exp = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", soil_stressed, pest_nominal, weather_heavy_rain, market)

    assert "DO NOT IRRIGATE TODAY" in card.critical_prohibition
    assert "Clear field drainage trenches immediately" in card.primary_action
    assert any(t.rule_id == "RULE_HYDRO_01" and t.triggered for t in exp.rule_traces)

def test_spray_drift_wind_arbitration():
    soil_ok = SoilState(
        crop_type="bt_cotton", depletion_mm=20.0, raw_mm=45.0, taw_mm=70.0,
        moisture_status="MOISTURE_ADEQUATE", volumetric_water_content=0.35
    )
    pest_triggered = PestState(
        crop_type="bt_cotton", pest_name="pink_bollworm", accumulated_gdd=462.0,
        gdd_threshold=450.0, risk_triggered=True, growth_stage="flowering_boll"
    )
    weather_high_wind = WeatherForecast(
        date="2026-09-04", temp_max=32.0, temp_min=24.0, temp_mean=28.0,
        rain_next_12h_mm=0.0, rain_next_24h_mm=0.0, rain_next_36h_mm=0.0,
        rain_prob_next_6h=10.0, wind_speed_kmh=18.5, # > 15.0 km/h limit!
        wind_gust_kmh=24.0, et0_mm=4.5, humidity_percent=60.0, source="demo_fixture"
    )
    market = MarketState(
        crop_type="bt_cotton", mandi_name="Beed APMC", modal_price_inr=7450.0,
        sma_7_inr=7200.0, price_momentum_percent=3.47, trend="FAVORABLE"
    )

    card, exp = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", soil_ok, pest_triggered, weather_high_wind, market)

    assert "DO NOT SPRAY PESTICIDES OR CHEMICALS" in card.critical_prohibition
    assert "Deploy pheromone traps" in card.primary_action
    assert any(t.rule_id == "RULE_PEST_WIND_01" and t.triggered for t in exp.rule_traces)

def test_foliar_spray_rain_prob_arbitration():
    soil_ok = SoilState(
        crop_type="bt_cotton", depletion_mm=20.0, raw_mm=45.0, taw_mm=70.0,
        moisture_status="MOISTURE_ADEQUATE", volumetric_water_content=0.35
    )
    pest_triggered = PestState(
        crop_type="bt_cotton", pest_name="pink_bollworm", accumulated_gdd=462.0,
        gdd_threshold=450.0, risk_triggered=True, growth_stage="flowering_boll"
    )
    weather_high_rain_prob = WeatherForecast(
        date="2026-09-04", temp_max=30.0, temp_min=22.0, temp_mean=26.0,
        rain_next_12h_mm=2.0, rain_next_24h_mm=5.0, rain_next_36h_mm=5.0,
        rain_prob_next_6h=80.0, # > 70.0% threshold!
        wind_speed_kmh=8.0, # safe wind!
        wind_gust_kmh=12.0, et0_mm=4.0, humidity_percent=85.0, source="demo_fixture"
    )
    market = MarketState(
        crop_type="bt_cotton", mandi_name="Beed APMC", modal_price_inr=7450.0,
        sma_7_inr=7200.0, price_momentum_percent=3.47, trend="FAVORABLE"
    )

    card, exp = arbitrate_daily_plan("tukaram_beed_01", "2026-09-04", soil_ok, pest_triggered, weather_high_rain_prob, market)

    assert "DO NOT SPRAY FOLIAR CHEMICALS" in card.critical_prohibition
    assert "Postpone chemical spraying" in card.primary_action
    assert any(t.rule_id == "RULE_PEST_RAIN_01" and t.triggered for t in exp.rule_traces)
