"""
Soil Water Engine (FAO-56 Penman-Monteith Water Balance Model)
Interface adapter to compute SoilState consuming Member 1's scientific engine & calibration.
"""
from typing import Optional
from backend.config.settings import settings
from backend.schemas.contracts import SoilState
from backend.engines.soil_engine import calculate_soil_moisture_status, FIELD_CAPACITY, WILTING_POINT

def calculate_soil_water_balance(
    crop_type: str,
    depletion_mm: float,
    root_depth_m: Optional[float] = None,
    precip_mm: float = 0.0,
    irrigation_mm: float = 0.0,
    et0_mm: float = 4.5
) -> SoilState:
    """
    Calculates root-zone soil water depletion (Dr,i) following FAO-56.
    Dr,i = Dr,i-1 - (P_i - RO_i) - I_i + ETc,i + DP_i
    Consumes Member 1's FIELD_CAPACITY, WILTING_POINT, and soil_engine status classifier.
    """
    crop_cfg = settings.CROP_CONFIGS.get(crop_type, settings.CROP_CONFIGS["bt_cotton"])
    if root_depth_m is None:
        root_depth_m = crop_cfg.get("default_root_depth_m", 0.6)

    kc = crop_cfg.get("kc_flowering", crop_cfg.get("kc_midstage", 1.15))
    p_raw = crop_cfg.get("p_raw_fraction", 0.65)

    fc = FIELD_CAPACITY
    wp = WILTING_POINT

    # Total Available Water (TAW) in mm = 1000 * (FC - WP) * Zr
    taw_mm = 1000.0 * (fc - wp) * root_depth_m
    # Readily Available Water (RAW) in mm = p * TAW
    raw_mm = p_raw * taw_mm

    # Daily crop ET (ETc = Kc * ET0)
    etc_mm = kc * et0_mm

    # Updated depletion: Dr,i = Dr,i-1 - P + ETc - Irrigation
    new_depletion = max(0.0, min(taw_mm, depletion_mm - precip_mm + etc_mm - irrigation_mm))

    moisture_status = "MOISTURE_STRESS" if new_depletion >= raw_mm else "MOISTURE_ADEQUATE"

    # Volumetric water content estimation
    vwc = fc - (new_depletion / (1000.0 * root_depth_m)) if root_depth_m > 0 else fc
    vwc = max(wp, min(fc, vwc))

    # Evaluate status using Member 1's soil engine
    m1_eval = calculate_soil_moisture_status(vwc)

    return SoilState(
        crop_type=crop_type,
        depletion_mm=round(new_depletion, 2),
        raw_mm=round(raw_mm, 2),
        taw_mm=round(taw_mm, 2),
        moisture_status=moisture_status,
        volumetric_water_content=round(vwc, 4),
        model_version={"soil": f"Member1-SoilEngine-FAO56-{m1_eval['status']}-v1.0"}
    )
