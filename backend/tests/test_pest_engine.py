"""Unit tests for the Pest Engine module.
"""

import sys
from pathlib import Path
import pytest

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.engines.pest_engine import (
    calculate_pink_bollworm_risk,
    calculate_cumulative_gdd,
    determine_pest_stage,
)


def test_calculate_pink_bollworm_risk_normal():
    """Test 1: Normal case with standard temperatures and previous GDD."""
    result = calculate_pink_bollworm_risk(tmax=35, tmin=25, previous_gdd=400)

    assert result["pest"] == "Pink Bollworm"
    assert result["daily_gdd"] == 18.0
    assert result["cumulative_gdd"] == 418.0
    assert result["pest_risk_high"] is False


def test_calculate_pink_bollworm_risk_high_risk():
    """Test 2: High risk case where cumulative GDD exceeds the threshold (450)."""
    # Mean temp = 30, daily_gdd = 18, cumulative_gdd = 440 + 18 = 458 >= 450
    result = calculate_pink_bollworm_risk(tmax=35, tmin=25, previous_gdd=440)

    assert result["pest"] == "Pink Bollworm"
    assert result["cumulative_gdd"] == 458.0
    assert result["pest_risk_high"] is True
    assert result["stage"] == "Adult Emergence / High Risk Outbreak"


def test_calculate_pink_bollworm_risk_invalid_temperature():
    """Test 3: Invalid temperature case where tmax < tmin raises ValueError."""
    with pytest.raises(ValueError, match=r"Maximum temperature .* cannot be lower than minimum temperature"):
        calculate_pink_bollworm_risk(tmax=20, tmin=25, previous_gdd=100)


def test_calculate_cumulative_gdd_normal():
    """Test 4: Normal accumulation across multiple standard days."""
    daily_temperatures = [
        {"tmax": 35, "tmin": 25},  # mean = 30, gdd = 30 - 12 = 18.0
        {"tmax": 32, "tmin": 22},  # mean = 27, gdd = 27 - 12 = 15.0
        {"tmax": 30, "tmin": 20},  # mean = 25, gdd = 25 - 12 = 13.0
    ]
    result = calculate_cumulative_gdd(daily_temperatures)

    assert result["daily_gdd"] == [18.0, 15.0, 13.0]
    assert result["cumulative_gdd"] == 46.0


def test_calculate_cumulative_gdd_zero_accumulation():
    """Test 5: Zero accumulation when temperatures are at or below base temperature (12°C)."""
    daily_temperatures = [
        {"tmax": 10, "tmin": 6},   # mean = 8.0 < 12 -> 0.0
        {"tmax": 12, "tmin": 10},  # mean = 11.0 < 12 -> 0.0
        {"tmax": 12, "tmin": 12},  # mean = 12.0 == 12 -> 0.0
    ]
    result = calculate_cumulative_gdd(daily_temperatures)

    assert result["daily_gdd"] == [0.0, 0.0, 0.0]
    assert result["cumulative_gdd"] == 0.0


def test_calculate_cumulative_gdd_multiple_days():
    """Test 6: Multi-day accumulation with mixed warm and sub-threshold cold days."""
    daily_temperatures = [
        {"tmax": 30, "tmin": 20},  # mean = 25 -> gdd = 13.0
        {"tmax": 10, "tmin": 8},   # mean = 9  -> gdd = 0.0 (ignored negative)
        {"tmax": 28, "tmin": 16},  # mean = 22 -> gdd = 10.0
        {"tmax": 34, "tmin": 24},  # mean = 29 -> gdd = 17.0
        {"tmax": 11, "tmin": 7},   # mean = 9  -> gdd = 0.0
    ]
    result = calculate_cumulative_gdd(daily_temperatures)

    assert result["daily_gdd"] == [13.0, 0.0, 10.0, 17.0, 0.0]
    assert result["cumulative_gdd"] == 40.0


def test_pest_stage_egg():
    """Test 7: Egg stage progression for cumulative GDD in 0-100 range."""
    result_0 = determine_pest_stage(0)
    result_50 = determine_pest_stage(50)
    result_100 = determine_pest_stage(100)

    assert result_0["stage"] == "Egg"
    assert result_0["cumulative_gdd"] == 0
    assert result_50["stage"] == "Egg"
    assert result_50["cumulative_gdd"] == 50
    assert result_100["stage"] == "Egg"
    assert result_100["cumulative_gdd"] == 100


def test_pest_stage_larva():
    """Test 8: Larva stage progression for cumulative GDD in 101-300 range."""
    result_101 = determine_pest_stage(101)
    result_200 = determine_pest_stage(200)
    result_300 = determine_pest_stage(300)

    assert result_101["stage"] == "Larva"
    assert result_101["cumulative_gdd"] == 101
    assert result_200["stage"] == "Larva"
    assert result_200["cumulative_gdd"] == 200
    assert result_300["stage"] == "Larva"
    assert result_300["cumulative_gdd"] == 300


def test_pest_stage_pupa():
    """Test 9: Pupa stage progression for cumulative GDD in 301-500 range."""
    result_301 = determine_pest_stage(301)
    result_400 = determine_pest_stage(400)
    result_500 = determine_pest_stage(500)

    assert result_301["stage"] == "Pupa"
    assert result_301["cumulative_gdd"] == 301
    assert result_400["stage"] == "Pupa"
    assert result_400["cumulative_gdd"] == 400
    assert result_500["stage"] == "Pupa"
    assert result_500["cumulative_gdd"] == 500


def test_pest_stage_adult():
    """Test 10: Adult stage progression for cumulative GDD 501+."""
    result_501 = determine_pest_stage(501)
    result_650 = determine_pest_stage(650)

    assert result_501["stage"] == "Adult"
    assert result_501["cumulative_gdd"] == 501
    assert result_650["stage"] == "Adult"
    assert result_650["cumulative_gdd"] == 650
