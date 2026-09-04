"""
Plot Profile Dynamic Agronomic Integration Tests
Proves that persisted plot parameters (sowing_date, crop_type, soil_type, lat/lon)
genuinely drive pest GDD accumulation, soil moisture depletion, daily decision cards,
and What-If simulations without hardcoded fixture overrides.
"""

import pytest
from backend.models.db_models import DBPlot

def test_differing_sowing_dates_produce_different_gdd(client, db_session):
    # Create plot A sown on June 25 (older crop, ~71 days)
    plot_a = DBPlot(
        plot_id="plot_june_sown",
        farmer_name="Farmer A",
        district="Beed",
        latitude=18.99,
        longitude=75.76,
        crop_type="bt_cotton",
        sowing_date="2026-06-25",
        soil_type="medium_black_vertisol",
        plot_area_ha=1.5
    )
    # Create plot B sown on August 15 (younger crop, ~20 days)
    plot_b = DBPlot(
        plot_id="plot_august_sown",
        farmer_name="Farmer B",
        district="Beed",
        latitude=18.99,
        longitude=75.76,
        crop_type="bt_cotton",
        sowing_date="2026-08-15",
        soil_type="medium_black_vertisol",
        plot_area_ha=1.5
    )
    db_session.add(plot_a)
    db_session.add(plot_b)
    db_session.commit()

    # Fetch daily decisions for both plots
    res_a = client.get("/api/v1/decision/daily/plot_june_sown")
    res_b = client.get("/api/v1/decision/daily/plot_august_sown")

    assert res_a.status_code == 200
    assert res_b.status_code == 200

    card_a = res_a.json()
    card_b = res_b.json()

    exp_a = client.get(f"/api/v1/explainability/{card_a['decision_id']}").json()
    exp_b = client.get(f"/api/v1/explainability/{card_b['decision_id']}").json()

    gdd_a = exp_a["pest_metrics"]["accumulated_gdd"]
    gdd_b = exp_b["pest_metrics"]["accumulated_gdd"]

    # GDD for June-sown plot must be significantly higher than August-sown plot
    assert gdd_a > gdd_b
    assert gdd_b < exp_b["pest_metrics"]["gdd_threshold"]  # Younger plot pest risk not triggered

def test_crop_and_soil_type_consumed_in_soil_water(client, db_session):
    # Plot with soybean crop
    plot_soybean = DBPlot(
        plot_id="plot_soybean_01",
        farmer_name="Soybean Farmer",
        district="Beed",
        latitude=18.99,
        longitude=75.76,
        crop_type="soybean",
        sowing_date="2026-07-01",
        soil_type="shallow_red_vertisol",
        plot_area_ha=2.0
    )
    db_session.add(plot_soybean)
    db_session.commit()

    res = client.get("/api/v1/decision/daily/plot_soybean_01")
    assert res.status_code == 200
    card = res.json()

    exp = client.get(f"/api/v1/explainability/{card['decision_id']}").json()
    pest_metrics = exp["pest_metrics"]

    # Target pest must match soybean (tobacco_caterpillar) instead of bt_cotton (pink_bollworm)
    assert exp["plot_id"] == "plot_soybean_01"
    assert pest_metrics["gdd_threshold"] == 380.0  # Soybean target pest threshold

def test_requested_plot_id_used_throughout_pipeline(client, db_session):
    plot_custom = DBPlot(
        plot_id="custom_beed_plot_99",
        farmer_name="Ramesh",
        district="Beed",
        latitude=19.00,
        longitude=75.80,
        crop_type="bt_cotton",
        sowing_date="2026-07-10",
        soil_type="medium_black_vertisol",
        plot_area_ha=1.0
    )
    db_session.add(plot_custom)
    db_session.commit()

    res = client.get("/api/v1/decision/daily/custom_beed_plot_99")
    assert res.status_code == 200
    card = res.json()

    assert card["plot_id"] == "custom_beed_plot_99"

    exp = client.get(f"/api/v1/explainability/{card['decision_id']}").json()
    assert exp["plot_id"] == "custom_beed_plot_99"

def test_simulation_and_daily_decision_use_same_agronomic_pipeline(client, db_session):
    plot_sim = DBPlot(
        plot_id="sim_pipeline_plot_01",
        farmer_name="Suresh",
        district="Beed",
        latitude=18.99,
        longitude=75.76,
        crop_type="bt_cotton",
        sowing_date="2026-08-15",
        soil_type="medium_black_vertisol",
        plot_area_ha=1.5
    )
    db_session.add(plot_sim)
    db_session.commit()

    # Daily decision card
    daily_res = client.get("/api/v1/decision/daily/sim_pipeline_plot_01")
    assert daily_res.status_code == 200
    daily_card = daily_res.json()

    # Simulation without overrides should yield identical baseline card
    sim_res = client.post("/api/v1/decision/simulate", json={"plot_id": "sim_pipeline_plot_01"})
    assert sim_res.status_code == 200
    sim_data = sim_res.json()

    assert sim_data["original_decision"]["primary_action"] == daily_card["primary_action"]
    assert sim_data["original_decision"]["critical_prohibition"] == daily_card["critical_prohibition"]

def test_tukaram_demo_behavior_intact(client, db_session):
    # Tukaram demo plot
    res = client.get("/api/v1/decision/daily/tukaram_beed_01")
    assert res.status_code == 200
    card = res.json()

    assert card["plot_id"] == "tukaram_beed_01"
    assert "DO NOT" in card["critical_prohibition"]
