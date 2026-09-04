def test_root_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] in ["healthy", "online"]

def test_get_tukaram_plot(client):
    res = client.get("/api/v1/plots/tukaram_beed_01")
    assert res.status_code == 200
    data = res.json()
    assert data["farmer_name"] == "Tukaram"
    assert data["location"]["district"] == "Beed"

def test_create_custom_plot(client):
    payload = {
        "plot_id": "jalna_soybean_02",
        "farmer_name": "Ramesh",
        "location": {"district": "Jalna", "latitude": 19.84, "longitude": 75.88},
        "crop_type": "soybean",
        "sowing_date": "2026-06-30",
        "soil_type": "medium_black_vertisol",
        "plot_area_ha": 2.0
    }
    res = client.post("/api/v1/plots", json=payload)
    assert res.status_code == 201
    assert res.json()["plot_id"] == "jalna_soybean_02"

def test_get_daily_decision_card(client):
    res = client.get("/api/v1/decision/daily/tukaram_beed_01")
    assert res.status_code == 200
    card = res.json()
    assert card["plot_id"] == "tukaram_beed_01"
    assert card["primary_action"] is not None
    assert card["critical_prohibition"] is not None
    assert card["scientific_rationale"] is not None
    assert "mr" in card["translations"]
    assert "hi" in card["translations"]

def test_explainability_endpoint(client):
    # First generate daily decision to populate DB record
    dec_res = client.get("/api/v1/decision/daily/tukaram_beed_01")
    card = dec_res.json()
    decision_id = card["decision_id"]

    exp_res = client.get(f"/api/v1/explainability/{decision_id}")
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert exp_data["decision_id"] == decision_id
    assert "soil_metrics" in exp_data
    assert "spray_window_metrics" in exp_data
    assert "pest_metrics" in exp_data
    assert len(exp_data["rule_traces"]) > 0

def test_translation_endpoint(client):
    dec_res = client.get("/api/v1/decision/daily/tukaram_beed_01")
    card = dec_res.json()

    trans_payload = {
        "decision_card": card,
        "target_languages": ["mr", "hi"]
    }
    res = client.post("/api/v1/translate", json=trans_payload)
    assert res.status_code == 200
    data = res.json()
    assert "mr" in data["translations"]
    assert "hi" in data["translations"]
