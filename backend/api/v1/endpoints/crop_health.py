"""
Crop Health Endpoint:
GET /api/v1/crop-health/{plot_id}
Exposes dynamic crop health, phenological growth stage, days after sowing,
and thermal degree-day (GDD) pest emergence risk derived from plot profile
and weather forecast. Reuses Member 1 engines.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.database import get_db
from backend.models.db_models import DBPlot
from backend.schemas.contracts import CropHealthResponse
from backend.services.weather_service import fetch_weather_forecast
from backend.api.v1.endpoints.decision import compute_agronomic_states
from backend.services.fallback_fixture import get_tukaram_plot_profile

router = APIRouter(prefix="/crop-health", tags=["Crop Health"])

@router.get("/{plot_id}", response_model=CropHealthResponse)
def get_crop_health(plot_id: str, db: Session = Depends(get_db)):
    """
    Returns dynamic crop health details for a specified plot_id.
    """
    db_plot = db.query(DBPlot).filter(DBPlot.plot_id == plot_id).first()
    if not db_plot:
        if plot_id == "tukaram_beed_01":
            tukaram = get_tukaram_plot_profile()
            db_plot = DBPlot(
                plot_id=tukaram.plot_id,
                farmer_name=tukaram.farmer_name,
                district=tukaram.location.district,
                latitude=tukaram.location.latitude,
                longitude=tukaram.location.longitude,
                crop_type=tukaram.crop_type,
                sowing_date=tukaram.sowing_date,
                soil_type=tukaram.soil_type,
                plot_area_ha=tukaram.plot_area_ha
            )
            db.add(db_plot)
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot '{plot_id}' not found."
            )

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    weather_forecast = fetch_weather_forecast(
        plot_id=db_plot.plot_id,
        lat=db_plot.latitude,
        lon=db_plot.longitude,
        date_str=date_str,
        db=db
    )

    soil_state, pest_state = compute_agronomic_states(db_plot, weather_forecast)

    today_date = datetime.now(timezone.utc).date()
    try:
        sow_date = datetime.strptime(db_plot.sowing_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        sow_date = today_date

    days_elapsed = max(0, (today_date - sow_date).days)

    crop_label = "Bt Cotton" if db_plot.crop_type == "bt_cotton" else ("Soybean" if db_plot.crop_type == "soybean" else db_plot.crop_type.title())

    # Phenological stage description
    if days_elapsed < 20:
        crop_stage = "Vegetative / Seedling Emergence"
    elif days_elapsed < 45:
        crop_stage = "Early Vegetative & Branching"
    elif days_elapsed < 80:
        crop_stage = "Flowering & Square Formation" if db_plot.crop_type == "bt_cotton" else "Pod Initiation & Flowering"
    elif days_elapsed < 120:
        crop_stage = "Boll Development & Maturation" if db_plot.crop_type == "bt_cotton" else "Pod Filling & Maturation"
    else:
        crop_stage = "Late Harvest / Maturation"

    return CropHealthResponse(
        plot_id=db_plot.plot_id,
        crop=crop_label,
        crop_stage=crop_stage,
        days_after_sowing=days_elapsed,
        pest=pest_state.pest_name.replace("_", " ").title(),
        accumulated_gdd=round(pest_state.accumulated_gdd, 1),
        threshold_gdd=round(pest_state.gdd_threshold, 1),
        pest_risk_high=pest_state.risk_triggered,
        model_version=pest_state.model_version.get("pest", "Thermal-GDD-v1.0"),
        provenance=f"Member 1 Thermal GDD + Member 2 Engine ({weather_forecast.source})",
        sowing_date=db_plot.sowing_date,
        weather_source=weather_forecast.source,
        calculation_period_days=days_elapsed
    )
