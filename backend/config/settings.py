import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Import Member 1's authoritative calibration constants from calibration_data.py
try:
    from backend.config.calibration_data import (
        PINK_BOLLWORM_TBASE,
        PINK_BOLLWORM_THRESHOLD_GDD,
        TOBACCO_CATERPILLAR_TBASE,
        TOBACCO_CATERPILLAR_THRESHOLD_GDD,
        FIELD_CAPACITY,
        WILTING_POINT,
        DEFAULT_RAW_FACTOR
    )
except ImportError:
    from config.calibration_data import (
        PINK_BOLLWORM_TBASE,
        PINK_BOLLWORM_THRESHOLD_GDD,
        TOBACCO_CATERPILLAR_TBASE,
        TOBACCO_CATERPILLAR_THRESHOLD_GDD,
        FIELD_CAPACITY,
        WILTING_POINT,
        DEFAULT_RAW_FACTOR
    )

class Settings(BaseSettings):
    PROJECT_NAME: str = "KrishiKavach - Farmer Decision Support Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # SQLite Persistence & Cache DB
    DATABASE_URL: str = Field(default="sqlite:///./krishikavach.db")

    # External APIs
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    AGMARKNET_API_URL: str = "https://api.agmarknet.gov.in/v1"
    AGMARKNET_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Centralized Arbitration Threshold Rules (Single Source of Truth)
    # Rule 1: Hydrological Arbitration Threshold (Rain in 36h to suppress irrigation)
    RAIN_IRRIGATION_SUPPRESS_MM_36H: float = 25.0

    # Rule 2: Biochemical Drift Threshold (Wind speed to block chemical spraying)
    WIND_SAFE_LIMIT_KMH: float = 15.0

    # Rule 3: Foliar Spray Rain Wash-Off Thresholds
    RAIN_PROB_SPRAY_BLOCK_PCT_6H: float = 60.0
    RAIN_WASH_OFF_MM_12H: float = 10.0

    # Soil Constants - Medium Black Vertisol (Consuming Member 1's calibration parameters)
    VERTISOL_FC: float = FIELD_CAPACITY
    VERTISOL_WP: float = WILTING_POINT
    VERTISOL_BULK_DENSITY: float = 1.35  # g/cm3

    # Crop Parameters Dictionary (Consuming Member 1's calibration thresholds)
    CROP_CONFIGS: dict = {
        "bt_cotton": {
            "name": "Bt-Cotton",
            "default_root_depth_m": 0.6,
            "p_raw_fraction": DEFAULT_RAW_FACTOR,
            "kc_flowering": 1.15,
            "target_pest": "pink_bollworm",
            "pest_tbase": float(PINK_BOLLWORM_TBASE),
            "pest_gdd_threshold": float(PINK_BOLLWORM_THRESHOLD_GDD)
        },
        "soybean": {
            "name": "Soybean",
            "default_root_depth_m": 0.5,
            "p_raw_fraction": 0.50,
            "kc_midstage": 1.05,
            "target_pest": "tobacco_caterpillar",
            "pest_tbase": float(TOBACCO_CATERPILLAR_TBASE),
            "pest_gdd_threshold": float(TOBACCO_CATERPILLAR_THRESHOLD_GDD)
        }
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
