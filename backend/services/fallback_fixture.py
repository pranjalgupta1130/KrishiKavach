from datetime import datetime, timezone
from backend.schemas.contracts import (
    PlotProfile,
    Location,
    WeatherForecast,
    SoilState,
    PestState,
    MarketState
)

def get_tukaram_plot_profile() -> PlotProfile:
    """Returns canonical benchmark plot profile for farmer Tukaram (Beed district)."""
    return PlotProfile(
        plot_id="tukaram_beed_01",
        farmer_name="Tukaram",
        location=Location(district="Beed", latitude=18.99, longitude=75.76),
        crop_type="bt_cotton",
        sowing_date="2026-06-25",
        soil_type="medium_black_vertisol",
        plot_area_ha=1.5
    )

def get_tukaram_weather_forecast(date_str: str = None) -> WeatherForecast:
    """
    Tier 3 Fallback Fixture: Static forecast for Beed representing real Marathwada microclimate.
    Forecast: High wind (18.5 km/h) & significant 36h rain (28.0 mm).
    """
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return WeatherForecast(
        date=date_str,
        temp_max=33.5,
        temp_min=23.0,
        temp_mean=28.25,
        rain_next_12h_mm=4.5,
        rain_next_24h_mm=12.0,
        rain_next_36h_mm=28.0,
        rain_prob_next_6h=85.0,
        wind_speed_kmh=18.5,
        wind_gust_kmh=24.0,
        et0_mm=4.5,
        humidity_percent=78.0,
        source="demo_fixture"
    )

def get_tukaram_soil_state() -> SoilState:
    """
    Returns baseline soil water state for Tukaram's plot under moisture stress.
    Depletion (48mm) exceeds RAW threshold (45mm).
    """
    return SoilState(
        crop_type="bt_cotton",
        depletion_mm=48.0,
        raw_mm=45.0,
        taw_mm=70.0,
        moisture_status="MOISTURE_STRESS",
        volumetric_water_content=0.28
    )

def get_tukaram_pest_state() -> PestState:
    """
    Returns baseline pest emergence state for Pink Bollworm.
    Accumulated GDD (462) exceeds emergence threshold (450 GDD).
    """
    return PestState(
        crop_type="bt_cotton",
        pest_name="pink_bollworm",
        accumulated_gdd=462.0,
        gdd_threshold=450.0,
        risk_triggered=True,
        growth_stage="flowering_boll"
    )

def get_tukaram_market_state() -> MarketState:
    """Returns baseline market state for Bt-Cotton at Beed APMC."""
    return MarketState(
        crop_type="bt_cotton",
        mandi_name="Beed APMC",
        modal_price_inr=7450.0,
        sma_7_inr=7200.0,
        price_momentum_percent=3.47,
        trend="FAVORABLE"
    )
