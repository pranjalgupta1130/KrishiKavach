"""Soil Engine module for KrishiKavach.

Provides assessment of soil moisture status, irrigation thresholds,
and moisture stress classification.
"""

from typing import Any, Dict, Union

# Robust import strategy supporting package execution, pytest, and direct execution
try:
    from backend.config.calibration_data import (
        FIELD_CAPACITY,
        WILTING_POINT,
    )
except ImportError:
    try:
        from config.calibration_data import (
            FIELD_CAPACITY,
            WILTING_POINT,
        )
    except ImportError:
        from ..config.calibration_data import (
            FIELD_CAPACITY,
            WILTING_POINT,
        )


def calculate_soil_moisture_status(soil_moisture: Union[int, float]) -> Dict[str, Any]:
    """Evaluates the status of soil moisture relative to field capacity and wilting point.

    Args:
        soil_moisture: Volumetric soil water content ratio (m³/m³ or fraction).

    Returns:
        Dict[str, Any]: Dictionary containing:
            - 'soil_moisture' (float/int): The evaluated soil moisture value.
            - 'field_capacity' (float): Calibrated field capacity threshold.
            - 'wilting_point' (float): Calibrated permanent wilting point threshold.
            - 'status' (str): Moisture state ('Optimal', 'Moderate', or 'Critical').

    Raises:
        TypeError: If soil_moisture is not a numeric type (int or float) or is a boolean.
        ValueError: If soil_moisture is negative.
    """
    # Input validation
    if not isinstance(soil_moisture, (int, float)) or isinstance(soil_moisture, bool):
        raise TypeError(f"Parameter 'soil_moisture' must be a numeric value (int or float). Received {type(soil_moisture).__name__}.")

    if soil_moisture < 0.0:
        raise ValueError(f"soil_moisture cannot be negative. Received {soil_moisture}.")

    # Status classification
    if soil_moisture >= FIELD_CAPACITY:
        status = "Optimal"
    elif WILTING_POINT <= soil_moisture < FIELD_CAPACITY:
        status = "Moderate"
    else:
        status = "Critical"

    return {
        "soil_moisture": soil_moisture,
        "field_capacity": FIELD_CAPACITY,
        "wilting_point": WILTING_POINT,
        "status": status,
    }


if __name__ == "__main__":
    print(calculate_soil_moisture_status(0.20))
