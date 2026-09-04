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
