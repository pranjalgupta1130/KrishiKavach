"""
Pest Phenology Engine (Thermal Degree Days Model)
Interface to compute PestState for Member 1 integration.
"""
from backend.config.settings import settings
from backend.schemas.contracts import PestState

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
    Pink Bollworm: Tbase = 12°C, emergence threshold = 450 GDD.
    Tobacco Caterpillar: Tbase = 10°C, emergence threshold = 380 GDD.
    """
    crop_cfg = settings.CROP_CONFIGS.get(crop_type, settings.CROP_CONFIGS["bt_cotton"])
    pest_name = crop_cfg["target_pest"]
    t_base = crop_cfg["pest_tbase"]
    threshold_gdd = crop_cfg["pest_gdd_threshold"]

    daily_gdd = calculate_gdd(temp_max, temp_min, t_base)
    total_gdd = accumulated_gdd + daily_gdd

    risk_triggered = total_gdd >= threshold_gdd
    growth_stage = "flowering_boll" if crop_type == "bt_cotton" else "vegetative_pod"

    return PestState(
        crop_type=crop_type,
        pest_name=pest_name,
        accumulated_gdd=round(total_gdd, 1),
        gdd_threshold=threshold_gdd,
        risk_triggered=risk_triggered,
        growth_stage=growth_stage
    )
