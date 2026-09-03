"""Pest Engine module for KrishiKavach.

Provides predictive modeling for agricultural pests based on
Growing Degree Days (GDD) and environmental thermal thresholds.
"""

from typing import Any, Dict, Union

# Robust import strategy supporting direct execution, package imports, and pytest
try:
    from backend.config.calibration_data import (
        PINK_BOLLWORM_TBASE,
        PINK_BOLLWORM_THRESHOLD_GDD,
    )
except ImportError:
    try:
        from config.calibration_data import (
            PINK_BOLLWORM_TBASE,
            PINK_BOLLWORM_THRESHOLD_GDD,
        )
    except ImportError:
        from ..config.calibration_data import (
            PINK_BOLLWORM_TBASE,
            PINK_BOLLWORM_THRESHOLD_GDD,
        )


def calculate_pink_bollworm_risk(
    tmax: Union[int, float],
    tmin: Union[int, float],
    previous_gdd: Union[int, float] = 0.0,
) -> Dict[str, Any]:
    """Calculates daily and cumulative Growing Degree Days (GDD) for Pink Bollworm

    and assesses the infestation risk level and current developmental stage.

    Args:
        tmax: Maximum daily temperature in degrees Celsius (°C).
        tmin: Minimum daily temperature in degrees Celsius (°C).
        previous_gdd: Accumulated GDD from preceding days (default: 0.0).

    Returns:
        Dict[str, Any]: Assessment summary containing:
            - 'pest' (str): Name of the pest ("Pink Bollworm").
            - 'daily_gdd' (float): GDD accumulated during the day.
            - 'cumulative_gdd' (float): Total accumulated GDD including current day.
            - 'threshold_gdd' (int/float): Calibrated GDD threshold for high risk.
            - 'pest_risk_high' (bool): True if cumulative_gdd >= threshold_gdd.
            - 'stage' (str): Estimated biological developmental stage.

    Raises:
        TypeError: If any input is not an int or float (or is a boolean).
        ValueError: If tmax < tmin or previous_gdd < 0.
    """
    # ---------------------------------------------------------
    # 1. Input Validation
    # ---------------------------------------------------------
    # Ensure inputs are numeric and not boolean instances
    for param_name, val in [("tmax", tmax), ("tmin", tmin), ("previous_gdd", previous_gdd)]:
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            raise TypeError(f"Parameter '{param_name}' must be a numeric value (int or float). Received {type(val).__name__}.")

    if tmax < tmin:
        raise ValueError(f"Maximum temperature (tmax={tmax}) cannot be lower than minimum temperature (tmin={tmin}).")

    if previous_gdd < 0:
        raise ValueError(f"previous_gdd cannot be negative. Received {previous_gdd}.")

    # ---------------------------------------------------------
    # 2. GDD Calculation
    # ---------------------------------------------------------
    # Formula: daily_gdd = max(((tmax + tmin) / 2) - PINK_BOLLWORM_TBASE, 0)
    mean_temp = (float(tmax) + float(tmin)) / 2.0
    daily_gdd = max(mean_temp - PINK_BOLLWORM_TBASE, 0.0)
    cumulative_gdd = float(previous_gdd) + daily_gdd

    # ---------------------------------------------------------
    # 3. Risk and Developmental Stage Determination
    # ---------------------------------------------------------
    is_high_risk = cumulative_gdd >= PINK_BOLLWORM_THRESHOLD_GDD

    if cumulative_gdd >= PINK_BOLLWORM_THRESHOLD_GDD:
        stage = "Adult Emergence / High Risk Outbreak"
    elif cumulative_gdd >= 250.0:
        stage = "Pupal Stage"
    elif cumulative_gdd >= 100.0:
        stage = "Larval Stage"
    else:
        stage = "Egg / Early Stage"

    return {
        "pest": "Pink Bollworm",
        "daily_gdd": round(daily_gdd, 2),
        "cumulative_gdd": round(cumulative_gdd, 2),
        "threshold_gdd": PINK_BOLLWORM_THRESHOLD_GDD,
        "pest_risk_high": is_high_risk,
        "stage": stage,
    }


if __name__ == "__main__":
    result = calculate_pink_bollworm_risk(35, 25, 400)
    print("Test Result:")
    print(result)

