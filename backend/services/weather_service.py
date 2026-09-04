"""
Weather Data Service with 3-Tier Fallback Pipeline:
Tier 1: Live Open-Meteo REST API Ingestion
Tier 2: SQLite Local Snapshot Cache
Tier 3: Hardcoded Demo Fixture (Tukaram / Beed)
"""

import json
import logging
from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.schemas.contracts import WeatherForecast
from backend.models.db_models import DBWeatherCache
from backend.services.fallback_fixture import get_tukaram_weather_forecast

logger = logging.getLogger("krishikavach.weather")

def fetch_weather_forecast(
    plot_id: str,
    lat: float,
    lon: float,
    date_str: str = None,
    db: Session = None
) -> WeatherForecast:
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Tier 1: Try Live Open-Meteo REST Ingestion
    try:
        url = f"{settings.OPEN_METEO_BASE_URL}/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,precipitation,precipitation_probability,wind_speed_10m,wind_gusts_10m,relative_humidity_2m,et0_fao_evapotranspiration",
            "timezone": "auto",
            "forecast_days": 2
        }

        with httpx.Client(timeout=3.0) as client:
            resp = client.get(url, params=params)

        if resp.status_code == 200:
            data = resp.json()
            hourly = data.get("hourly", {})

            raw_temps = hourly.get("temperature_2m", [])
            raw_precip = hourly.get("precipitation", [])
            raw_precip_prob = hourly.get("precipitation_probability", [])
            raw_winds = hourly.get("wind_speed_10m", [])
            raw_gusts = hourly.get("wind_gusts_10m", [])
            raw_humidity = hourly.get("relative_humidity_2m", [])
            raw_et0 = hourly.get("et0_fao_evapotranspiration", [])

            valid_temps = [float(t) for t in raw_temps if isinstance(t, (int, float))]
            valid_precip = [max(0.0, float(p)) for p in raw_precip if isinstance(p, (int, float))]
            valid_precip_prob = [max(0.0, min(100.0, float(pp))) for pp in raw_precip_prob if isinstance(pp, (int, float))]
            valid_winds = [max(0.0, float(w)) for w in raw_winds if isinstance(w, (int, float))]
            valid_gusts = [max(0.0, float(g)) for g in raw_gusts if isinstance(g, (int, float))]
            valid_humidity = [max(0.0, min(100.0, float(h))) for h in raw_humidity if isinstance(h, (int, float))]
            valid_et0 = [max(0.0, float(e)) for e in raw_et0 if isinstance(e, (int, float))]

            if not (valid_temps and valid_winds and valid_precip):
                raise ValueError("Malformed or incomplete hourly payload received from Open-Meteo")

            temp_max = max(valid_temps)
            temp_min = min(valid_temps)
            temp_mean = sum(valid_temps) / len(valid_temps)

            rain_12h = sum(valid_precip[:12]) if len(valid_precip) >= 12 else sum(valid_precip)
            rain_24h = sum(valid_precip[:24]) if len(valid_precip) >= 24 else sum(valid_precip)
            rain_36h = sum(valid_precip[:36]) if len(valid_precip) >= 36 else sum(valid_precip)

            rain_prob_6h = max(valid_precip_prob[:6]) if len(valid_precip_prob) >= 6 else (valid_precip_prob[0] if valid_precip_prob else 0.0)
            wind_max = max(valid_winds[:24]) if len(valid_winds) >= 24 else valid_winds[0]
            gust_max = max(valid_gusts[:24]) if len(valid_gusts) >= 24 else (valid_gusts[0] if valid_gusts else wind_max)
            humidity_avg = sum(valid_humidity[:24]) / len(valid_humidity[:24]) if len(valid_humidity) >= 24 else 70.0
            et0_daily = sum(valid_et0[:24]) if len(valid_et0) >= 24 else 4.5

            forecast = WeatherForecast(
                date=date_str,
                temp_max=round(temp_max, 1),
                temp_min=round(temp_min, 1),
                temp_mean=round(temp_mean, 2),
                rain_next_12h_mm=round(rain_12h, 1),
                rain_next_24h_mm=round(rain_24h, 1),
                rain_next_36h_mm=round(rain_36h, 1),
                rain_prob_next_6h=round(rain_prob_6h, 1),
                wind_speed_kmh=round(wind_max, 1),
                wind_gust_kmh=round(gust_max, 1),
                et0_mm=round(et0_daily, 2),
                humidity_percent=round(humidity_avg, 1),
                source="live_api"
            )

            # Store in Tier 2 SQLite Cache
            if db:
                try:
                    cache_entry = DBWeatherCache(
                        plot_id=plot_id,
                        date=date_str,
                        payload_json=forecast.model_dump_json()
                    )
                    db.add(cache_entry)
                    db.commit()
                except Exception as db_err:
                    logger.warning(f"Failed to cache live weather to SQLite: {db_err}")
                    db.rollback()

            return forecast

    except Exception as api_err:
        logger.warning(f"Live Open-Meteo API ingestion failed ({api_err}). Trying Tier 2 SQLite Cache...")

    # Tier 2: Try SQLite Local Snapshot Cache
    if db:
        try:
            cached_record = db.query(DBWeatherCache).filter(
                DBWeatherCache.plot_id == plot_id,
                DBWeatherCache.date == date_str
            ).order_by(DBWeatherCache.fetched_at.desc()).first()

            if cached_record:
                data_dict = json.loads(cached_record.payload_json)
                data_dict["source"] = "cached"
                logger.info(f"Retrieved weather from Tier 2 SQLite Cache for plot {plot_id}")
                return WeatherForecast(**data_dict)
        except Exception as cache_err:
            logger.warning(f"Tier 2 SQLite cache retrieval failed ({cache_err}). Trying Tier 3 Fixture...")

    # Tier 3: Hardcoded Demo Fixture Fallback
    logger.info(f"Falling back to Tier 3 Demo Fixture for plot {plot_id}")
    return get_tukaram_weather_forecast(date_str)
