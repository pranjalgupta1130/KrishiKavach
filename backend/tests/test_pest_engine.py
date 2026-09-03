"""Unit tests for the Pest Engine module.
"""

import sys
from pathlib import Path
import pytest

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.engines.pest_engine import calculate_pink_bollworm_risk


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
