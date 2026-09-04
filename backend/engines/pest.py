"""
Pest Phenology Engine (Thermal Degree Days Model)
Interface adapter to compute PestState consuming Member 1's scientific engine.
"""
from backend.config.settings import settings
from backend.schemas.contracts import PestState
from backend.engines.pest_engine import calculate_pink_bollworm_risk

def calculate_gdd(temp_max: float, temp_min: float, t_base: float) -> float:
    """Calculates daily Growing Degree Days: max(((Tmax + Tmin)/2) - Tbase, 0)"""
    t_avg = (temp_max + temp_min) / 2.0
    return max(0.0, t_avg - t_base)

def calculate_pest_phenology(
    crop_type: str,
    accumulated_gdd: float,
    temp_max: float = 32.0,
    temp_min: float = 24.0
) -> PestState:
    """
    Tracks thermal accumulation against emergence limits.
    Consumes Member 1 pest_engine for Pink Bollworm (Bt-Cotton) and applies
    calibrated thresholds for Tobacco Caterpillar (Soybean).
    """
    crop_cfg = settings.CROP_CONFIGS.get(crop_type, settings.CROP_CONFIGS["bt_cotton"])
    pest_name = crop_cfg.get("target_pest", "pink_bollworm")

    if crop_type == "bt_cotton" or pest_name == "pink_bollworm":
        # Delegate directly to Member 1's pest_engine
        m1_res = calculate_pink_bollworm_risk(
            tmax=temp_max,
            tmin=temp_min,
            previous_gdd=accumulated_gdd
        )
        return PestState(
            crop_type=crop_type,
            pest_name="pink_bollworm",
            accumulated_gdd=float(m1_res["cumulative_gdd"]),
            gdd_threshold=float(m1_res["threshold_gdd"]),
            risk_triggered=bool(m1_res["pest_risk_high"]),
            growth_stage="flowering_boll",
            model_version={"pest": "Member1-PinkBollworm-GDD-v1.0"}
        )
    else:
        # Soybean / Tobacco Caterpillar model using calibration settings
        t_base = crop_cfg.get("pest_tbase", 10.0)
        threshold_gdd = crop_cfg.get("pest_gdd_threshold", 380.0)
        daily_gdd = calculate_gdd(temp_max, temp_min, t_base)
        total_gdd = accumulated_gdd + daily_gdd
        risk_triggered = total_gdd >= threshold_gdd

        return PestState(
            crop_type=crop_type,
            pest_name=pest_name,
            accumulated_gdd=round(total_gdd, 1),
            gdd_threshold=threshold_gdd,
            risk_triggered=risk_triggered,
            growth_stage="vegetative_pod",
            model_version={"pest": "Member2-TobaccoCaterpillar-GDD-v1.0"}
        )
