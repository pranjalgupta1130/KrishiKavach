"""Unit tests for the Soil Engine module.
"""

import sys
from pathlib import Path
import pytest

# Ensure repository root is on sys.path for direct pytest discovery
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.engines.soil_engine import calculate_soil_moisture_status


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
