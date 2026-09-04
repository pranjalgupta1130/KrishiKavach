"""
Decision API Endpoints:
1. GET /api/v1/decision/daily/{plot_id} - Generates daily conflict-arbitrated decision card.
2. POST /api/v1/decision/simulate - Executes What-If decision simulation reusing arbitration.py.
"""

import json
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.database import get_db
from backend.models.db_models import DBPlot, DBDecisionRecord
from backend.schemas.contracts import (
    DecisionCard,
    SimulationRequest,
    SimulationResponse,
    SoilState,
    PestState,
    WeatherForecast,
    DecisionHistoryItem,
    RuleTrace
)
from backend.engines.arbitration import arbitrate_daily_plan
from backend.engines.pest import calculate_pest_phenology, calculate_gdd
from backend.engines.soil_water import calculate_soil_water_balance
from backend.services.weather_service import fetch_weather_forecast
from backend.services.market_service import fetch_market_state
from backend.services.llm_service import translate_decision_card
from backend.services.fallback_fixture import (
    get_tukaram_plot_profile,
    get_tukaram_soil_state,
    get_tukaram_pest_state
)

router = APIRouter(prefix="/decision", tags=["Decision"])

def compute_agronomic_states(db_plot: DBPlot, weather_forecast: WeatherForecast):
    """
    Computes SoilState and PestState dynamically from plot profile parameters
    (sowing_date, crop_type, soil_type) and current weather inputs.
    Reuses Member 1 pest phenology and soil water engines.
    """
    today_date = datetime.now(timezone.utc).date()
    try:
        sow_date = datetime.strptime(db_plot.sowing_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        sow_date = today_date

    days_elapsed = max(0, (today_date - sow_date).days)

    crop_cfg = settings.CROP_CONFIGS.get(db_plot.crop_type, settings.CROP_CONFIGS["bt_cotton"])
    t_base = crop_cfg.get("pest_tbase", 12.0)

    daily_gdd = calculate_gdd(weather_forecast.temp_max, weather_forecast.temp_min, t_base)
    if daily_gdd <= 0:
        daily_gdd = max(0.0, weather_forecast.temp_mean - t_base)

    accumulated_gdd = days_elapsed * daily_gdd

    pest_state = calculate_pest_phenology(
        crop_type=db_plot.crop_type,
        accumulated_gdd=accumulated_gdd,
        temp_max=weather_forecast.temp_max,
        temp_min=weather_forecast.temp_min
    )

    kc = crop_cfg.get("kc_flowering", 1.15)
    etc = kc * weather_forecast.et0_mm

    base_depletion = etc * days_elapsed if days_elapsed > 0 else 0.0

    soil_state = calculate_soil_water_balance(
        crop_type=db_plot.crop_type,
        depletion_mm=base_depletion,
        precip_mm=weather_forecast.rain_next_24h_mm,
        et0_mm=weather_forecast.et0_mm
    )

    return soil_state, pest_state


@router.get("/daily/{plot_id}", response_model=DecisionCard)
def get_daily_decision(plot_id: str, db: Session = Depends(get_db)):
    """
    Generates the daily conflict-arbitrated decision card for a given plot.
    Employs 3-tier fallback: Live API -> SQLite Cache -> Tukaram Fixture.
    """
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

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

    weather_forecast = fetch_weather_forecast(
        plot_id=db_plot.plot_id,
        lat=db_plot.latitude,
        lon=db_plot.longitude,
        date_str=date_str,
        db=db
    )

    soil_state, pest_state = compute_agronomic_states(db_plot, weather_forecast)

    market_state = fetch_market_state(
        crop_type=db_plot.crop_type,
        mandi_name=f"{db_plot.district} APMC"
    )

    decision_card, explainability_details = arbitrate_daily_plan(
        plot_id=plot_id,
        date_str=date_str,
        soil_state=soil_state,
        pest_state=pest_state,
        weather_forecast=weather_forecast,
        market_state=market_state
    )

    translations = translate_decision_card(decision_card, target_languages=["mr", "hi"])
    decision_card.translations = translations

    try:
        decision_rec = DBDecisionRecord(
            decision_id=decision_card.decision_id,
            plot_id=plot_id,
            date=date_str,
            primary_action=decision_card.primary_action,
            critical_prohibition=decision_card.critical_prohibition,
            scientific_rationale=decision_card.scientific_rationale,
            confidence_indicator=decision_card.confidence_indicator,
            explainability_id=decision_card.explainability_id,
            explainability_json=explainability_details.model_dump_json()
        )
        db.add(decision_rec)
        db.commit()
    except Exception:
        db.rollback()

    return decision_card


@router.post("/simulate", response_model=SimulationResponse)
def simulate_decision(req: SimulationRequest, db: Session = Depends(get_db)):
    """
    Executes What-If decision simulation with user parameter overrides.
    Reuses the EXACT SAME arbitration engine (arbitrate_daily_plan).
    """
    plot_id = req.plot_id
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

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

    base_weather = fetch_weather_forecast(plot_id, db_plot.latitude, db_plot.longitude, date_str, db)
    base_soil, base_pest = compute_agronomic_states(db_plot, base_weather)
    base_market = fetch_market_state(db_plot.crop_type, f"{db_plot.district} APMC")

    orig_card, _ = arbitrate_daily_plan(plot_id, date_str, base_soil, base_pest, base_weather, base_market)
    orig_card.translations = translate_decision_card(orig_card, ["mr", "hi"])

    sim_weather_dict = base_weather.model_dump()
    sim_soil_dict = base_soil.model_dump()
    sim_pest_dict = base_pest.model_dump()

    ov = req.overrides

    wind_override = (ov.wind_speed_kmh if ov and ov.wind_speed_kmh is not None else req.custom_wind_speed_kmh)
    rain_36h_override = (ov.rain_next_36h_mm if ov and ov.rain_next_36h_mm is not None else req.custom_rain_36h_mm)
    rain_12h_override = (ov.rain_next_12h_mm if ov and ov.rain_next_12h_mm is not None else req.custom_rain_12h_mm)
    rain_prob_override = (ov.rain_prob_next_6h if ov and ov.rain_prob_next_6h is not None else req.custom_rain_prob_6h)
    soil_depletion_override = (ov.soil_depletion_mm if ov and ov.soil_depletion_mm is not None else req.custom_soil_depletion_mm)
    gdd_override = (ov.accumulated_gdd if ov and ov.accumulated_gdd is not None else req.custom_accumulated_gdd)

    if wind_override is not None:
        sim_weather_dict["wind_speed_kmh"] = wind_override
    if rain_36h_override is not None:
        sim_weather_dict["rain_next_36h_mm"] = rain_36h_override
    if rain_12h_override is not None:
        sim_weather_dict["rain_next_12h_mm"] = rain_12h_override
    if rain_prob_override is not None:
        sim_weather_dict["rain_prob_next_6h"] = rain_prob_override

    sim_weather = WeatherForecast(**sim_weather_dict)

    if soil_depletion_override is not None:
        sim_soil_dict["depletion_mm"] = soil_depletion_override
        sim_soil_dict["moisture_status"] = "MOISTURE_STRESS" if soil_depletion_override >= sim_soil_dict["raw_mm"] else "MOISTURE_ADEQUATE"
    sim_soil = SoilState(**sim_soil_dict)

    if gdd_override is not None:
        sim_pest_dict["accumulated_gdd"] = gdd_override
        sim_pest_dict["risk_triggered"] = gdd_override >= sim_pest_dict["gdd_threshold"]
    sim_pest = PestState(**sim_pest_dict)

    sim_card, sim_exp = arbitrate_daily_plan(plot_id, date_str, sim_soil, sim_pest, sim_weather, base_market)
    sim_card.translations = translate_decision_card(sim_card, ["mr", "hi"])

    is_flipped = (
        orig_card.primary_action != sim_card.primary_action or
        orig_card.critical_prohibition != sim_card.critical_prohibition
    )

    if is_flipped:
        flip_reason = (
            f"Operational decision flipped! Primary action changed from '{orig_card.primary_action}' "
            f"to '{sim_card.primary_action}'. Critical prohibition updated from '{orig_card.critical_prohibition}' "
            f"to '{sim_card.critical_prohibition}' due to parameter overrides."
        )
    else:
        flip_reason = "No operational decision flip triggered. Advisory parameters remain unchanged."

    return SimulationResponse(
        plot_id=plot_id,
        original_decision=orig_card,
        simulated_decision=sim_card,
        is_flipped=is_flipped,
        flip_reason=flip_reason
    )


@router.get("/history/{plot_id}", response_model=List[DecisionHistoryItem])
def get_decision_history(
    plot_id: str,
    limit: int = Query(default=20, ge=1, le=100, description="Max history items to return (1-100)"),
    db: Session = Depends(get_db)
):
    """
    Retrieves historical decisions for a plot, ordered newest first (created_at DESC).
    Consumes ONLY persisted DBDecisionRecord data.
    """
    records = db.query(DBDecisionRecord).filter(
        DBDecisionRecord.plot_id == plot_id
    ).order_by(DBDecisionRecord.created_at.desc()).limit(limit).all()

    history_items: List[DecisionHistoryItem] = []
    for rec in records:
        rule_traces = []
        model_ver = None
        if rec.explainability_json:
            try:
                exp_data = json.loads(rec.explainability_json)
                rule_traces_data = exp_data.get("rule_traces", [])
                rule_traces = [RuleTrace(**t) for t in rule_traces_data]
                model_ver = exp_data.get("model_version", None)
            except Exception:
                pass

        created_str = (
            rec.created_at.isoformat()
            if isinstance(rec.created_at, datetime)
            else str(rec.created_at)
        )

        history_items.append(DecisionHistoryItem(
            decision_id=rec.decision_id,
            plot_id=rec.plot_id,
            date=rec.date,
            primary_action=rec.primary_action,
            critical_prohibition=rec.critical_prohibition,
            scientific_rationale=rec.scientific_rationale,
            confidence_indicator=rec.confidence_indicator,
            explainability_id=rec.explainability_id,
            created_at=created_str,
            rule_traces=rule_traces,
            model_version=model_ver
        ))

    return history_items
