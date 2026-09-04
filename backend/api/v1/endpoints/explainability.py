from typing import List, Dict, Any
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.db_models import DBDecisionRecord
from backend.schemas.contracts import ExplainabilityDetails, WhatChangedItem

router = APIRouter(prefix="/explainability", tags=["Explainability Drawer"])

@router.get("/{decision_id}", response_model=ExplainabilityDetails)
def get_explainability_details(decision_id: str, db: Session = Depends(get_db)):
    """
    Retrieves rule traces, threshold evaluations, exact input metrics, and historical diffs
    used during deterministic arbitration for a specific decision_id.
    Consumes ONLY persisted DBDecisionRecord data.
    """
    record = db.query(DBDecisionRecord).filter(
        (DBDecisionRecord.decision_id == decision_id) | (DBDecisionRecord.explainability_id == decision_id)
    ).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Explainability record for decision ID / explainability ID '{decision_id}' not found."
        )

    try:
        details_dict: Dict[str, Any] = json.loads(record.explainability_json)

        # Look up previous decision for the SAME plot
        prev_record = db.query(DBDecisionRecord).filter(
            DBDecisionRecord.plot_id == record.plot_id,
            DBDecisionRecord.created_at < record.created_at
        ).order_by(DBDecisionRecord.created_at.desc()).first()

        if prev_record:
            prev_details_dict: Dict[str, Any] = {}
            if prev_record.explainability_json:
                try:
                    prev_details_dict = json.loads(prev_record.explainability_json)
                except Exception:
                    prev_details_dict = {}

            details_dict["previous_decision"] = {
                "decision_id": prev_record.decision_id,
                "date": prev_record.date,
                "primary_action": prev_record.primary_action,
                "critical_prohibition": prev_record.critical_prohibition
            }

            what_changed: List[Dict[str, Any]] = []

            # 1. Primary Action
            if record.primary_action != prev_record.primary_action:
                what_changed.append({
                    "field": "primary_action",
                    "previous": prev_record.primary_action,
                    "current": record.primary_action,
                    "change": f"Primary action updated from '{prev_record.primary_action}' to '{record.primary_action}'"
                })

            # 2. Critical Prohibition
            if record.critical_prohibition != prev_record.critical_prohibition:
                what_changed.append({
                    "field": "critical_prohibition",
                    "previous": prev_record.critical_prohibition,
                    "current": record.critical_prohibition,
                    "change": f"Critical prohibition updated from '{prev_record.critical_prohibition}' to '{record.critical_prohibition}'"
                })

            # 3. Wind Speed
            curr_wind = details_dict.get("spray_window_metrics", {}).get("wind_speed_kmh")
            prev_wind = prev_details_dict.get("spray_window_metrics", {}).get("wind_speed_kmh")
            if curr_wind is not None and prev_wind is not None and curr_wind != prev_wind:
                diff = curr_wind - prev_wind
                what_changed.append({
                    "field": "wind_speed_kmh",
                    "previous": prev_wind,
                    "current": curr_wind,
                    "change": f"Wind speed changed by {diff:+.1f} km/h (from {prev_wind:.1f} to {curr_wind:.1f} km/h)"
                })

            # 4. Rain Next 36h
            curr_rain = details_dict.get("spray_window_metrics", {}).get("rain_next_36h_mm")
            prev_rain = prev_details_dict.get("spray_window_metrics", {}).get("rain_next_36h_mm")
            if curr_rain is not None and prev_rain is not None and curr_rain != prev_rain:
                diff = curr_rain - prev_rain
                what_changed.append({
                    "field": "rain_next_36h_mm",
                    "previous": prev_rain,
                    "current": curr_rain,
                    "change": f"36-hour rain forecast changed by {diff:+.1f} mm (from {prev_rain:.1f} to {curr_rain:.1f} mm)"
                })

            # 5. Soil Depletion
            curr_dep = details_dict.get("soil_metrics", {}).get("depletion_mm")
            prev_dep = prev_details_dict.get("soil_metrics", {}).get("depletion_mm")
            if curr_dep is not None and prev_dep is not None and curr_dep != prev_dep:
                diff = curr_dep - prev_dep
                what_changed.append({
                    "field": "soil_depletion_mm",
                    "previous": prev_dep,
                    "current": curr_dep,
                    "change": f"Soil depletion changed by {diff:+.1f} mm (from {prev_dep:.1f} to {curr_dep:.1f} mm)"
                })

            # 6. Accumulated GDD
            curr_gdd = details_dict.get("pest_metrics", {}).get("accumulated_gdd")
            prev_gdd = prev_details_dict.get("pest_metrics", {}).get("accumulated_gdd")
            if curr_gdd is not None and prev_gdd is not None and curr_gdd != prev_gdd:
                diff = curr_gdd - prev_gdd
                what_changed.append({
                    "field": "accumulated_gdd",
                    "previous": prev_gdd,
                    "current": curr_gdd,
                    "change": f"Pest accumulated GDD changed by {diff:+.0f} (from {prev_gdd:.0f} to {curr_gdd:.0f})"
                })

            # 7. Triggered Rules Comparison
            curr_rules = [t["rule_id"] for t in details_dict.get("rule_traces", []) if t.get("triggered")]
            prev_rules = [t["rule_id"] for t in prev_details_dict.get("rule_traces", []) if t.get("triggered")]
            if curr_rules != prev_rules:
                what_changed.append({
                    "field": "triggered_rules",
                    "previous": prev_rules,
                    "current": curr_rules,
                    "change": f"Triggered rules changed from {prev_rules} to {curr_rules}"
                })

            details_dict["what_changed"] = what_changed
        else:
            details_dict["previous_decision"] = None
            details_dict["what_changed"] = []

        return ExplainabilityDetails(**details_dict)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Corrupted explainability record payload: {err}"
        )
