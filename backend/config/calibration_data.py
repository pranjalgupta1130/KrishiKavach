"""Centralized calibration data configuration module for KrishiKavach.

This module stores global constants, thresholds, and environmental baseline values
for pest development models (Growing Degree Days / GDD) and soil moisture calibrations.
"""

# -----------------------------------------------------------------------------
# Pest Engine Calibration Parameters (Growing Degree Days - GDD)
# -----------------------------------------------------------------------------

# Base temperature (°C) below which Pink Bollworm development halts
PINK_BOLLWORM_TBASE = 12

# Accumulated Growing Degree Days (GDD) threshold for Pink Bollworm lifecycle risk
PINK_BOLLWORM_THRESHOLD_GDD = 450

# Base temperature (°C) below which Tobacco Caterpillar development halts
TOBACCO_CATERPILLAR_TBASE = 10

# Accumulated Growing Degree Days (GDD) threshold for Tobacco Caterpillar lifecycle risk
TOBACCO_CATERPILLAR_THRESHOLD_GDD = 380


# -----------------------------------------------------------------------------
# Soil Moisture & Irrigation Calibration Parameters
# -----------------------------------------------------------------------------

# Default Readily Available Water (RAW) depletion factor for crop stress thresholding
DEFAULT_RAW_FACTOR = 0.65

# Volumetric water content ratio at field capacity (maximum water held after free drainage)
FIELD_CAPACITY = 0.35

# Volumetric water content ratio at permanent wilting point (minimum soil moisture for plant extraction)
WILTING_POINT = 0.15
