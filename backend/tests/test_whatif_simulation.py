from backend.schemas.contracts import SimulationRequest, OverrideParams

def test_whatif_simulation_legacy_flat_fields(client, db_session):
    # Default Tukaram baseline: High wind (> 15 km/h)
    req = SimulationRequest(
        plot_id="tukaram_beed_01",
        custom_wind_speed_kmh=8.0,
        custom_rain_36h_mm=0.0,
        custom_rain_12h_mm=0.0,
        custom_rain_prob_6h=10.0
    )

    response = client.post("/api/v1/decision/simulate", json=req.model_dump())
    assert response.status_code == 200
    data = response.json()

    assert data["is_flipped"] is True
    assert data["original_decision"]["critical_prohibition"] != data["simulated_decision"]["critical_prohibition"]
    assert "DO NOT" in data["original_decision"]["critical_prohibition"]
    assert "Apply controlled irrigation; spraying is not blocked" in data["simulated_decision"]["primary_action"]
    assert "Follow approved local pest-management guidance" in data["simulated_decision"]["primary_action"]

    # Verify that it does NOT prescribe a specific pesticide/product/dose
    sim_action_lower = data["simulated_decision"]["primary_action"].lower()
    for specific_term in ["bio-pesticide", "chemical spray", "spray with ppe", "dose", "ml/l", "kg/ha"]:
        assert specific_term not in sim_action_lower

def test_whatif_simulation_public_nested_overrides_json(client, db_session):
    # REGRESSION TEST: Exact public JSON payload structure sent by Swagger UI & Member 3 frontend
    public_payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "rain_next_36h_mm": 0.0
        }
    }

    response = client.post("/api/v1/decision/simulate", json=public_payload)
    assert response.status_code == 200
    data = response.json()

    # Prove that nested overrides actually reach the arbitration inputs and flip the decision
    assert data["is_flipped"] is True
    assert "DO NOT" in data["original_decision"]["critical_prohibition"]
    assert "NO CRITICAL PROHIBITIONS" in data["simulated_decision"]["critical_prohibition"]
    assert "Apply controlled irrigation; spraying is not blocked" in data["simulated_decision"]["primary_action"]
    assert "Follow approved local pest-management guidance" in data["simulated_decision"]["primary_action"]

    # Verify non-prescription of specific pesticide/product/dose
    sim_action_lower = data["simulated_decision"]["primary_action"].lower()
    for specific_term in ["bio-pesticide", "chemical spray", "spray with ppe", "dose", "ml/l", "kg/ha"]:
        assert specific_term not in sim_action_lower

def test_override_is_not_silently_ignored(client, db_session):
    # PROOF TEST: Verifies that overrides actively modify the simulated rationale text
    public_payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "rain_next_36h_mm": 0.0
        }
    }

    response = client.post("/api/v1/decision/simulate", json=public_payload)
    assert response.status_code == 200
    data = response.json()

    # Rationale must reflect overridden wind (8.0 km/h) rather than baseline wind
    sim_rationale = data["simulated_decision"]["scientific_rationale"]
    orig_rationale = data["original_decision"]["scientific_rationale"]

    assert "safe atmospheric conditions" in sim_rationale or "8.0 km/h" in sim_rationale or "8 km/h" in sim_rationale
    assert "exceeds safe spraying limit" in orig_rationale
    assert sim_rationale != orig_rationale
