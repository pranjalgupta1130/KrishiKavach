"""
Conflict Arbitration Engine 2.0 - Core Deterministic Decision Layer

Central authority for resolving operational contradictions between agronomic needs
and forecast environmental risks. Used by both the Daily Decision endpoint and
What-If simulation endpoint.

All rules and thresholds are strictly imported from backend.config.settings.
Generative AI is strictly excluded from this module.
"""

import uuid
from datetime import datetime, timezone
from typing import Tuple, List

from backend.config.settings import settings
from backend.schemas.contracts import (
    SoilState,
    PestState,
    WeatherForecast,
    MarketState,
    DecisionCard,
    ExplainabilityDetails,
    RuleTrace,
    RejectedAction,
    DecisionSummary,
    WhySection,
    WhyNotItem,
    ConflictExplanation
)

def arbitrate_daily_plan(
    plot_id: str,
    date_str: str,
    soil_state: SoilState,
    pest_state: PestState,
    weather_forecast: WeatherForecast,
    market_state: MarketState
) -> Tuple[DecisionCard, ExplainabilityDetails]:
    """
    Executes deterministic conflict arbitration logic over environmental and crop states.
    Returns finalized DecisionCard and ExplainabilityDetails.
    """
    rationales: List[str] = []
    rule_traces: List[RuleTrace] = []
    conflicts_detected: List[str] = []
    rejected_actions: List[RejectedAction] = []

    # Decision flags
    hydro_state = "NOMINAL"  # PROHIBITED, APPROVED, NOMINAL
    spray_state = "NOMINAL"  # WIND_BLOCKED, RAIN_BLOCKED, APPROVED, NOMINAL

    # -------------------------------------------------------------------------
    # 1. Hydrological Conflict Arbitration (Irrigation vs. Precipitation)
    # -------------------------------------------------------------------------
    is_moisture_stressed = soil_state.depletion_mm >= soil_state.raw_mm
    rain_36h = weather_forecast.rain_next_36h_mm
    rain_suppress_limit = settings.RAIN_IRRIGATION_SUPPRESS_MM_36H

    if is_moisture_stressed:
        if rain_36h >= rain_suppress_limit:
            # Conflict Detected: Moisture stressed, but heavy rain forecast in 36h!
            hydro_state = "PROHIBITED"
            conflicts_detected.append("HYDROLOGICAL_RAIN_CONFLICT")
            reject_reason = (
                f"Soil depletion is {soil_state.depletion_mm:.1f}mm (RAW threshold: {soil_state.raw_mm:.1f}mm), "
                f"but {rain_36h:.1f}mm precipitation is forecast within 36 hours (threshold: {rain_suppress_limit:.1f}mm). "
                f"Irrigation will induce severe waterlogging and root rot in medium black vertisol."
            )
            rationales.append(reject_reason)
            rejected_actions.append(RejectedAction(
                candidate_action="TUBEVILL_IRRIGATION",
                blocked_by_rule_id="RULE_HYDRO_01",
                reason=reject_reason
            ))
            rule_traces.append(RuleTrace(
                rule_id="RULE_HYDRO_01",
                rule_name="Hydrological Rain Conflict Arbitration",
                priority=80,
                triggered=True,
                condition_evaluated=f"depletion ({soil_state.depletion_mm:.1f}mm) >= RAW ({soil_state.raw_mm:.1f}mm) AND rain_36h ({rain_36h:.1f}mm) >= threshold ({rain_suppress_limit:.1f}mm)",
                effect="Suppressed irrigation; mandated drainage trench clearing.",
                decision_impact="FINAL_PROHIBITION",
                why_not="Tubewell irrigation rejected because heavy rain is forecast within 36 hours."
            ))
        else:
            # Moisture stressed & skies clear/low rain -> Apply controlled irrigation
            hydro_state = "APPROVED"
            rationales.append(
                f"Soil water depletion has reached {soil_state.depletion_mm:.1f}mm, crossing RAW threshold ({soil_state.raw_mm:.1f}mm) "
                f"with clear skies forecast ({rain_36h:.1f}mm rain in 36h)."
            )
            rule_traces.append(RuleTrace(
                rule_id="RULE_HYDRO_02",
                rule_name="Irrigation Approval",
                priority=60,
                triggered=True,
                condition_evaluated=f"depletion ({soil_state.depletion_mm:.1f}mm) >= RAW ({soil_state.raw_mm:.1f}mm) AND rain_36h ({rain_36h:.1f}mm) < threshold ({rain_suppress_limit:.1f}mm)",
                effect="Approved controlled irrigation.",
                decision_impact="FINAL_ACTION"
            ))
    else:
        hydro_state = "NOMINAL"
        rationales.append(
            f"Soil moisture is adequate (depletion {soil_state.depletion_mm:.1f}mm < RAW limit {soil_state.raw_mm:.1f}mm). "
            f"No tubewell pumping required today."
        )
        rule_traces.append(RuleTrace(
            rule_id="RULE_HYDRO_03",
            rule_name="Moisture Adequacy",
            priority=40,
            triggered=False,
            condition_evaluated=f"depletion ({soil_state.depletion_mm:.1f}mm) < RAW ({soil_state.raw_mm:.1f}mm)",
            effect="No irrigation required.",
            decision_impact="NOMINAL"
        ))

    # -------------------------------------------------------------------------
    # 2. Biochemical Drift & Wash-off Arbitration (Pest Emergence vs. Spray Safety)
    # -------------------------------------------------------------------------
    pest_triggered = pest_state.risk_triggered
    wind_speed = weather_forecast.wind_speed_kmh
    wind_limit = settings.WIND_SAFE_LIMIT_KMH
    rain_prob_6h = weather_forecast.rain_prob_next_6h
    rain_prob_limit = settings.RAIN_PROB_SPRAY_BLOCK_PCT_6H
    rain_12h = weather_forecast.rain_next_12h_mm
    rain_12h_limit = settings.RAIN_WASH_OFF_MM_12H
    pest_display_name = pest_state.pest_name.replace("_", " ").title()

    if pest_triggered:
        if wind_speed > wind_limit:
            # Conflict Detected: Pest threshold crossed, but wind speed > limit!
            spray_state = "WIND_BLOCKED"
            conflicts_detected.append("PEST_WIND_DRIFT_CONFLICT")
            reject_reason = (
                f"{pest_display_name} emergence threshold reached ({pest_state.accumulated_gdd:.0f} GDD >= {pest_state.gdd_threshold:.0f} GDD), "
                f"but sustained wind speed ({wind_speed:.1f} km/h) exceeds safe spraying limit ({wind_limit:.1f} km/h). "
                f"Chemical spraying will cause severe drift off-target."
            )
            rationales.append(reject_reason)
            rejected_actions.append(RejectedAction(
                candidate_action="CHEMICAL_PESTICIDE_SPRAY",
                blocked_by_rule_id="RULE_PEST_WIND_01",
                reason=reject_reason
            ))
            rule_traces.append(RuleTrace(
                rule_id="RULE_PEST_WIND_01",
                rule_name="Biochemical Drift Spray Block",
                priority=100,
                triggered=True,
                condition_evaluated=f"pest_gdd ({pest_state.accumulated_gdd:.0f}) >= threshold ({pest_state.gdd_threshold:.0f}) AND wind ({wind_speed:.1f} km/h) > limit ({wind_limit:.1f} km/h)",
                effect="Blocked chemical spraying; mandated pheromone traps.",
                decision_impact="FINAL_PROHIBITION",
                why_not="Chemical spraying rejected because wind speed exceeds the safe threshold limit."
            ))
        elif rain_prob_6h > rain_prob_limit or rain_12h >= rain_12h_limit:
            # Conflict Detected: Pest threshold crossed, but rain probability/rain in 12h will wash off spray!
            spray_state = "RAIN_BLOCKED"
            conflicts_detected.append("PEST_RAIN_WASHOFF_CONFLICT")
            reject_reason = (
                f"{pest_display_name} emergence threshold reached ({pest_state.accumulated_gdd:.0f} GDD), "
                f"but imminent rain forecast (probability {rain_prob_6h:.0f}% in 6h / {rain_12h:.1f}mm in 12h) "
                f"will wash off foliar treatments, wasting chemical investment."
            )
            rationales.append(reject_reason)
            rejected_actions.append(RejectedAction(
                candidate_action="FOLIAR_CHEMICAL_SPRAY",
                blocked_by_rule_id="RULE_PEST_RAIN_01",
                reason=reject_reason
            ))
            rule_traces.append(RuleTrace(
                rule_id="RULE_PEST_RAIN_01",
                rule_name="Foliar Spray Rain Wash-Off Block",
                priority=90,
                triggered=True,
                condition_evaluated=f"rain_prob_6h ({rain_prob_6h:.0f}%) > limit ({rain_prob_limit:.0f}%) OR rain_12h ({rain_12h:.1f}mm) >= limit ({rain_12h_limit:.1f}mm)",
                effect="Blocked foliar spray due to rain wash-off risk.",
                decision_impact="FINAL_PROHIBITION",
                why_not="Foliar spraying rejected because imminent rain will cause wash-off."
            ))
        else:
            # Atmospheric conditions safe -> Apply recommended biopesticide/spray
            spray_state = "APPROVED"
            rationales.append(
                f"{pest_display_name} emergence threshold crossed ({pest_state.accumulated_gdd:.0f} GDD >= {pest_state.gdd_threshold:.0f} GDD) "
                f"under safe atmospheric conditions (wind {wind_speed:.1f} km/h <= {wind_limit:.1f} km/h, dry skies)."
            )
            rule_traces.append(RuleTrace(
                rule_id="RULE_PEST_SPRAY_OK",
                rule_name="Pest Spray Approval",
                priority=70,
                triggered=True,
                condition_evaluated=f"pest_gdd ({pest_state.accumulated_gdd:.0f}) >= threshold ({pest_state.gdd_threshold:.0f}) AND atmospheric conditions safe",
                effect="Approved targeted chemical/bio-pesticide spray.",
                decision_impact="FINAL_ACTION"
            ))
    else:
        spray_state = "NOMINAL"
        rationales.append(
            f"Pest emergence degree-days ({pest_state.accumulated_gdd:.0f} GDD) remain below intervention threshold ({pest_state.gdd_threshold:.0f} GDD). "
            f"Routine field monitoring recommended."
        )
        rule_traces.append(RuleTrace(
            rule_id="RULE_PEST_NO_RISK",
            rule_name="Pest Threshold Nominal",
            priority=30,
            triggered=False,
            condition_evaluated=f"pest_gdd ({pest_state.accumulated_gdd:.0f}) < threshold ({pest_state.gdd_threshold:.0f})",
            effect="No chemical spray required.",
            decision_impact="NOMINAL"
        ))

    # -------------------------------------------------------------------------
    # 3. Market Signal Support (Secondary - NEVER OVERRIDES AGRONOMIC RULES)
    # -------------------------------------------------------------------------
    if market_state.trend == "FAVORABLE" and market_state.price_momentum_percent >= getattr(settings, "MARKET_FAVORABLE_MOMENTUM_PCT", 2.0):
        rationales.append(
            f"Market price for {market_state.crop_type} at {market_state.mandi_name} is favorable "
            f"({market_state.modal_price_inr:.0f} INR/q, +{market_state.price_momentum_percent:.1f}% vs 7-day average)."
        )
        rule_traces.append(RuleTrace(
            rule_id="RULE_MARKET_01",
            rule_name="Market Price Momentum Support",
            priority=20,
            triggered=True,
            condition_evaluated=f"trend ({market_state.trend}) == FAVORABLE AND momentum ({market_state.price_momentum_percent:.1f}%) >= 2.0%",
            effect="Added market momentum rationale.",
            decision_impact="MARKET_CONTEXT"
        ))

    # -------------------------------------------------------------------------
    # 4. Synthesize ONE Primary Action & ONE Critical Prohibition
    # -------------------------------------------------------------------------
    # Critical Prohibition Synthesis
    if hydro_state == "PROHIBITED" and spray_state in ["WIND_BLOCKED", "RAIN_BLOCKED"]:
        critical_prohibition_str = "DO NOT IRRIGATE OR APPLY CHEMICAL SPRAYS TODAY"
    elif hydro_state == "PROHIBITED":
        critical_prohibition_str = "DO NOT IRRIGATE TODAY"
    elif spray_state == "WIND_BLOCKED":
        critical_prohibition_str = "DO NOT SPRAY PESTICIDES OR CHEMICALS"
    elif spray_state == "RAIN_BLOCKED":
        critical_prohibition_str = "DO NOT SPRAY FOLIAR CHEMICALS"
    else:
        critical_prohibition_str = "NO CRITICAL PROHIBITIONS TODAY — Standard field operations permitted"

    # Primary Action Synthesis
    if hydro_state == "PROHIBITED" and spray_state == "WIND_BLOCKED":
        primary_action_str = "Clear field drainage trenches immediately and deploy biological pheromone traps"
    elif hydro_state == "PROHIBITED" and spray_state == "RAIN_BLOCKED":
        primary_action_str = "Clear field drainage trenches immediately; postpone chemical spraying until rain clears"
    elif hydro_state == "PROHIBITED" and spray_state == "APPROVED":
        primary_action_str = "Clear field drainage trenches immediately; apply targeted bio-pesticide spray with PPE"
    elif hydro_state == "PROHIBITED":
        primary_action_str = "Clear field drainage trenches immediately"
    elif hydro_state == "APPROVED" and spray_state == "WIND_BLOCKED":
        primary_action_str = "Apply controlled drip/tubewell irrigation; deploy biological pheromone traps for pest monitoring"
    elif hydro_state == "APPROVED" and spray_state == "RAIN_BLOCKED":
        primary_action_str = "Apply controlled drip/tubewell irrigation; postpone chemical spraying until rain clears"
    elif hydro_state == "APPROVED" and spray_state == "APPROVED":
        primary_action_str = "Apply controlled irrigation; spraying is not blocked by current wind conditions. Follow approved local pest-management guidance."
    elif hydro_state == "APPROVED":
        primary_action_str = "Apply controlled irrigation (tubewell/drip)"
    elif spray_state == "WIND_BLOCKED":
        primary_action_str = "Deploy pheromone traps and monitor field boundaries manually"
    elif spray_state == "RAIN_BLOCKED":
        primary_action_str = "Postpone chemical spraying until rain clears"
    elif spray_state == "APPROVED":
        primary_action_str = "Apply recommended bio-pesticide or targeted chemical spray with PPE"
    else:
        primary_action_str = "Perform routine field inspection and soil maintenance"
        rule_traces.append(RuleTrace(
            rule_id="RULE_ROUTINE_01",
            rule_name="Routine Field Operation Fallback",
            priority=10,
            triggered=True,
            condition_evaluated="hydro_state == NOMINAL AND spray_state == NOMINAL",
            effect="Perform routine field inspection.",
            decision_impact="FINAL_ACTION"
        ))

    scientific_rationale_str = " ".join(rationales)

    decision_uuid = f"dec_{uuid.uuid4().hex[:12]}"
    explainability_uuid = f"exp_{uuid.uuid4().hex[:12]}"

    model_provenance = {
        **getattr(soil_state, "model_version", {}),
        **getattr(pest_state, "model_version", {}),
        "arbitration_engine": "Arbitration-Engine-v2.0"
    }

    confidence_text = f"Data Freshness: {weather_forecast.source.replace('_', ' ').title()}"

    decision_card = DecisionCard(
        decision_id=decision_uuid,
        plot_id=plot_id,
        date=date_str,
        primary_action=primary_action_str,
        critical_prohibition=critical_prohibition_str,
        scientific_rationale=scientific_rationale_str,
        confidence_indicator=confidence_text,
        explainability_id=explainability_uuid,
        created_at=datetime.now(timezone.utc).isoformat(),
        model_version=model_provenance
    )

    soil_metrics_dict = {
        "depletion_mm": soil_state.depletion_mm,
        "raw_mm": soil_state.raw_mm,
        "taw_mm": soil_state.taw_mm,
        "is_moisture_stressed": 1.0 if is_moisture_stressed else 0.0
    }
    spray_window_metrics_dict = {
        "wind_speed_kmh": weather_forecast.wind_speed_kmh,
        "wind_safe_limit_kmh": settings.WIND_SAFE_LIMIT_KMH,
        "rain_next_12h_mm": weather_forecast.rain_next_12h_mm,
        "rain_next_36h_mm": weather_forecast.rain_next_36h_mm,
        "rain_prob_next_6h": weather_forecast.rain_prob_next_6h,
        "rain_irrigation_suppress_threshold_mm": settings.RAIN_IRRIGATION_SUPPRESS_MM_36H,
        "rain_prob_spray_block_threshold": settings.RAIN_PROB_SPRAY_BLOCK_PCT_6H
    }
    pest_metrics_dict = {
        "accumulated_gdd": pest_state.accumulated_gdd,
        "gdd_threshold": pest_state.gdd_threshold,
        "risk_triggered": 1.0 if pest_state.risk_triggered else 0.0
    }
    market_metrics_dict = {
        "modal_price_inr": market_state.modal_price_inr,
        "sma_7_inr": market_state.sma_7_inr,
        "price_momentum_percent": market_state.price_momentum_percent
    }

    # Build Phase 3 presentation-ready facts
    summary = DecisionSummary(
        primary_action=primary_action_str,
        critical_prohibition=critical_prohibition_str,
        plain_language_reason=scientific_rationale_str,
        decision_status=confidence_text
    )

    triggered_traces = [t for t in rule_traces if t.triggered]
    why = WhySection(
        selected_rules=[t.rule_id for t in triggered_traces],
        triggered_conditions=[t.condition_evaluated for t in triggered_traces],
        priority_reason="Rules evaluated strictly in priority order from highest safety constraint (100) down to routine operations (10)."
    )

    why_not_list = [
        WhyNotItem(
            action=ra.candidate_action,
            reason=ra.reason,
            blocking_rule=ra.blocked_by_rule_id,
            priority=next((t.priority for t in rule_traces if t.rule_id == ra.blocked_by_rule_id), 100)
        )
        for ra in rejected_actions
    ]

    conflicts_explained: List[ConflictExplanation] = []
    for c_id in conflicts_detected:
        if c_id == "PEST_WIND_DRIFT_CONFLICT":
            conflicts_explained.append(ConflictExplanation(
                conflict_id="PEST_WIND_DRIFT_CONFLICT",
                description="Pest treatment indicated but wind speed exceeds safe limit.",
                winning_rule="RULE_PEST_WIND_01",
                winning_priority=100,
                rejected_action="CHEMICAL_PESTICIDE_SPRAY",
                resolution="Block chemical spraying and deploy biological pheromone traps."
            ))
        elif c_id == "PEST_RAIN_WASHOFF_CONFLICT":
            conflicts_explained.append(ConflictExplanation(
                conflict_id="PEST_RAIN_WASHOFF_CONFLICT",
                description="Pest treatment indicated but imminent rainfall will cause spray wash-off.",
                winning_rule="RULE_PEST_RAIN_01",
                winning_priority=90,
                rejected_action="FOLIAR_CHEMICAL_SPRAY",
                resolution="Block foliar spray until rain clears."
            ))
        elif c_id == "HYDROLOGICAL_RAIN_CONFLICT":
            conflicts_explained.append(ConflictExplanation(
                conflict_id="HYDROLOGICAL_RAIN_CONFLICT",
                description="Soil water depletion triggers irrigation need, but heavy rain forecast within 36 hours.",
                winning_rule="RULE_HYDRO_01",
                winning_priority=80,
                rejected_action="TUBEVILL_IRRIGATION",
                resolution="Suppress irrigation and clear field drainage trenches."
            ))

    inputs = {
        "soil": soil_metrics_dict,
        "weather": spray_window_metrics_dict,
        "pest": pest_metrics_dict,
        "market": market_metrics_dict
    }

    explainability_details = ExplainabilityDetails(
        decision_id=decision_uuid,
        plot_id=plot_id,
        date=date_str,
        soil_metrics=soil_metrics_dict,
        spray_window_metrics=spray_window_metrics_dict,
        pest_metrics=pest_metrics_dict,
        market_metrics=market_metrics_dict,
        confidence_indicator=weather_forecast.source,
        rule_traces=rule_traces,
        conflicts_detected=conflicts_detected,
        rejected_actions=rejected_actions,
        model_version=model_provenance,
        summary=summary,
        why=why,
        why_not=why_not_list,
        conflicts=conflicts_explained,
        inputs=inputs,
        model_provenance=model_provenance
    )

    return decision_card, explainability_details
