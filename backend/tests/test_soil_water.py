from backend.engines.soil_water import calculate_soil_water_balance

def test_soil_water_balance_moisture_stress():
    # Depletion 48mm >= RAW 45.5mm (Bt-Cotton with root_depth 0.35m)
    state = calculate_soil_water_balance(
        crop_type="bt_cotton",
        depletion_mm=48.0,
        root_depth_m=0.35,
        precip_mm=0.0,
        irrigation_mm=0.0,
        et0_mm=4.5
    )
    assert state.moisture_status == "MOISTURE_STRESS"
    assert state.depletion_mm >= state.raw_mm

def test_soil_water_balance_moisture_adequate():
    # Depletion 20mm < RAW 45.5mm
    state = calculate_soil_water_balance(
        crop_type="bt_cotton",
        depletion_mm=20.0,
        root_depth_m=0.7,
        precip_mm=10.0,
        irrigation_mm=0.0,
        et0_mm=4.0
    )
    assert state.moisture_status == "MOISTURE_ADEQUATE"
