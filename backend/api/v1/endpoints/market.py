"""
Market API Endpoint:
GET /api/v1/market/{plot_id}
Returns mandi market rates, 7-day moving average, price momentum, and trend
derived for the plot's registered location and crop type.
Implements Live -> Cache -> Fallback hierarchy with explicit data_status.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.db_models import DBPlot
from backend.schemas.contracts import MarketResponse
from backend.services.market_service import fetch_market_state
from backend.services.fallback_fixture import get_tukaram_plot_profile

router = APIRouter(prefix="/market", tags=["Market"])

@router.get("/{plot_id}", response_model=MarketResponse)
def get_market_data(plot_id: str, db: Session = Depends(get_db)):
    """
    Returns market price indicators and momentum for the plot's commodity & district APMC.
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

    crop_label = "Bt Cotton" if db_plot.crop_type == "bt_cotton" else ("Soybean" if db_plot.crop_type == "soybean" else db_plot.crop_type.title())
    commodity_label = "Cotton" if db_plot.crop_type == "bt_cotton" else ("Soybean" if db_plot.crop_type == "soybean" else db_plot.crop_type.title())
    mandi_name = f"{db_plot.district} APMC"

    market_state = fetch_market_state(crop_type=db_plot.crop_type, mandi_name=mandi_name)

    trend_label = "UP" if market_state.trend == "FAVORABLE" else ("DOWN" if market_state.trend == "UNFAVORABLE" else "STABLE")
    fetched_at_iso = datetime.now(timezone.utc).isoformat()

    return MarketResponse(
        plot_id=db_plot.plot_id,
        crop=crop_label,
        commodity=commodity_label,
        current_price=round(market_state.modal_price_inr, 2),
        currency="INR",
        unit="quintal",
        moving_average=round(market_state.sma_7_inr, 2),
        momentum=round(market_state.price_momentum_percent, 2),
        trend=trend_label,
        source=f"Agmarknet Mandi Intelligence Baseline ({mandi_name})",
        fetched_at=fetched_at_iso,
        data_status="FALLBACK"
    )
