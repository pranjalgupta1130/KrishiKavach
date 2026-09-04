"""Unit tests for the Soil Engine module.
"""

import sys
from pathlib import Path
import pytest

# Ensure repository root is on sys.path for direct pytest discovery
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.engines.soil_engine import (
    calculate_soil_moisture_status,
    calculate_root_depth,
    get_crop_stage_parameters,
    validate_soil_moisture,
)


def test_soil_moisture_low():
    """Test 1: Low moisture case below wilting point (Critical status)."""
    result = calculate_soil_moisture_status(soil_moisture=0.10)

    assert result["soil_moisture"] == 0.10
    assert result["status"] == "Critical"
    assert result["field_capacity"] == 0.35
    assert result["wilting_point"] == 0.15


def test_soil_moisture_moderate():
    """Test 2: Moderate moisture case between wilting point and field capacity (Moderate status)."""
    result = calculate_soil_moisture_status(soil_moisture=0.20)

    assert result["soil_moisture"] == 0.20
    assert result["status"] == "Moderate"
    assert result["field_capacity"] == 0.35
    assert result["wilting_point"] == 0.15


def test_soil_moisture_high():
    """Test 3: High moisture case at or above field capacity (Optimal status)."""
    result = calculate_soil_moisture_status(soil_moisture=0.40)

    assert result["soil_moisture"] == 0.40
    assert result["status"] == "Optimal"
    assert result["field_capacity"] == 0.35
    assert result["wilting_point"] == 0.15


def test_calculate_root_depth_seedling():
    """Test 4: Seedling stage rooting depth (0.2m)."""
    assert calculate_root_depth("Seedling") == 0.2


def test_calculate_root_depth_vegetative():
    """Test 5: Vegetative stage rooting depth (0.5m)."""
    assert calculate_root_depth("Vegetative") == 0.5


def test_calculate_root_depth_flowering():
    """Test 6: Flowering stage rooting depth (0.8m)."""
    assert calculate_root_depth("Flowering") == 0.8


def test_calculate_root_depth_maturity():
    """Test 7: Maturity stage rooting depth (1.2m)."""
    assert calculate_root_depth("Maturity") == 1.2


def test_calculate_root_depth_invalid_stage():
    """Test 8: Invalid stage raises ValueError."""
    with pytest.raises(ValueError, match=r"Invalid crop stage .* Valid stages are:"):
        calculate_root_depth("Harvesting")


def test_crop_stage_parameters_germination():
    """Test 9: Parameter lookup for germination stage."""
    params = get_crop_stage_parameters("germination")
    assert params["water_requirement"] == "Low"
    assert params["recommended_soil_moisture"] == 0.20


def test_crop_stage_parameters_vegetative():
    """Test 10: Parameter lookup for vegetative stage."""
    params = get_crop_stage_parameters("vegetative")
    assert params["water_requirement"] == "Medium"
    assert params["recommended_soil_moisture"] == 0.35


def test_crop_stage_parameters_flowering():
    """Test 11: Parameter lookup for flowering stage."""
    params = get_crop_stage_parameters("flowering")
    assert params["water_requirement"] == "High"
    assert params["recommended_soil_moisture"] == 0.45


def test_crop_stage_parameters_fruiting():
    """Test 12: Parameter lookup for fruiting stage."""
    params = get_crop_stage_parameters("fruiting")
    assert params["water_requirement"] == "Medium"
    assert params["recommended_soil_moisture"] == 0.35


def test_crop_stage_parameters_invalid_stage():
    """Test 13: Invalid stage parameter lookup raises ValueError."""
    with pytest.raises(ValueError, match=r"Invalid crop stage .* Valid stages are:"):
        get_crop_stage_parameters("dormant")


def test_validate_soil_moisture_valid_low():
    """Test 14: Valid low soil moisture boundary (0.0)."""
    assert validate_soil_moisture(0.0) == 0.0
    assert validate_soil_moisture(0.05) == 0.05


def test_validate_soil_moisture_valid_high():
    """Test 15: Valid high soil moisture boundary (1.0)."""
    assert validate_soil_moisture(1.0) == 1.0
    assert validate_soil_moisture(0.95) == 0.95


def test_validate_soil_moisture_below_minimum():
    """Test 16: Soil moisture below minimum (0.0) raises ValueError."""
    with pytest.raises(ValueError, match=r"outside the valid range of \[0.0, 1.0\]"):
        validate_soil_moisture(-0.05)


def test_validate_soil_moisture_above_maximum():
    """Test 17: Soil moisture above maximum (1.0) raises ValueError."""
    with pytest.raises(ValueError, match=r"outside the valid range of \[0.0, 1.0\]"):
        validate_soil_moisture(1.05)


def test_soil_moisture_exactly_at_wilting_point():
    """Test 18: Soil moisture exactly at wilting point (0.15 -> Moderate status)."""
    result = calculate_soil_moisture_status(soil_moisture=0.15)
    assert result["soil_moisture"] == 0.15
    assert result["status"] == "Moderate"
    assert result["wilting_point"] == 0.15


def test_soil_moisture_exactly_at_field_capacity():
    """Test 19: Soil moisture exactly at field capacity (0.35 -> Optimal status)."""
    result = calculate_soil_moisture_status(soil_moisture=0.35)
    assert result["soil_moisture"] == 0.35
    assert result["status"] == "Optimal"
    assert result["field_capacity"] == 0.35


def test_soil_moisture_below_minimum_threshold():
    """Test 20: Soil moisture below minimum threshold (< 0.0) raises ValueError."""
    with pytest.raises(ValueError, match=r"outside the valid range of \[0.0, 1.0\]"):
        calculate_soil_moisture_status(-0.01)


def test_soil_moisture_above_maximum_threshold():
    """Test 21: Soil moisture above maximum threshold (> 1.0) raises ValueError."""
    with pytest.raises(ValueError, match=r"outside the valid range of \[0.0, 1.0\]"):
        calculate_soil_moisture_status(1.01)


def test_soil_moisture_invalid_negative_values():
    """Test 22: Negative values raise ValueError across status calculation and validation."""
    with pytest.raises(ValueError, match=r"outside the valid range of \[0.0, 1.0\]"):
        calculate_soil_moisture_status(-0.5)
    with pytest.raises(ValueError, match=r"outside the valid range of \[0.0, 1.0\]"):
        validate_soil_moisture(-1.0)


def test_soil_moisture_invalid_values_greater_than_one():
    """Test 23: Values > 1.0 raise ValueError across status calculation and validation."""
    with pytest.raises(ValueError, match=r"outside the valid range of \[0.0, 1.0\]"):
        calculate_soil_moisture_status(1.5)
    with pytest.raises(ValueError, match=r"outside the valid range of \[0.0, 1.0\]"):
        validate_soil_moisture(2.5)
