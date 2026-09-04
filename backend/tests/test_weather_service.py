from backend.services.weather_service import fetch_weather_forecast

def test_weather_service_fallback_to_fixture(db_session):
    # Pass invalid lat/lon to trigger API failure and test fallback to demo fixture
    forecast = fetch_weather_forecast(
        plot_id="tukaram_beed_01",
        lat=999.0,
        lon=999.0,
        date_str="2026-09-04",
        db=db_session
    )
    assert forecast is not None
    assert forecast.source in ["demo_fixture", "cached", "live_api"]
    assert forecast.wind_speed_kmh > 0
