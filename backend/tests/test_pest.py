from backend.engines.pest import calculate_pest_phenology, calculate_gdd

def test_gdd_calculation():
    # Tmax = 32, Tmin = 24, Tbase = 12 -> Tavg = 28 -> GDD = 16
    gdd = calculate_gdd(temp_max=32.0, temp_min=24.0, t_base=12.0)
    assert gdd == 16.0

def test_pest_phenology_triggered():
    # Pink Bollworm threshold 450 GDD
    state = calculate_pest_phenology(
        crop_type="bt_cotton",
        accumulated_gdd=440.0,
        temp_max=34.0,
        temp_min=24.0
    )
    assert state.risk_triggered is True
    assert state.accumulated_gdd >= 450.0

def test_pest_phenology_nominal():
    state = calculate_pest_phenology(
        crop_type="bt_cotton",
        accumulated_gdd=200.0,
        temp_max=30.0,
        temp_min=20.0
    )
    assert state.risk_triggered is False
